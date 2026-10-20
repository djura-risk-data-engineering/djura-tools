"""
Readers of the PSHA model (GMM logic tree, OpenQuake source model), rupture
geometry of disaggregation bins and the djura record selection input built
from them.

A TRT_Mag_Dist bin gives the tectonic region, magnitude and rrup only. The
other GMM inputs (rake, dip, ztor, width, hypo_depth, rjb, rx, ry0, repi,
rhypo) are taken

- from the OpenQuake source model: its ruptures are put into the same bins
  and rate-weighted values are taken per style of faulting, or
- from rules per tectonic region (rake, dip, seismogenic depths,
  hypocentral depth, site side), completed with the relations in
  kaklamanos2011.py for a site perpendicular to strike, with rjb and rx
  solved from rrup.

Notes
-----
Assumptions:

- Mean disaggregation: within a tectonic region, GMMs keep their logic tree
  weights, i.e. all are taken as equally consistent with IM*. The exact
  approach weights them by their own contribution to IM*.
- A bin is represented by its centre magnitude and rrup, the distance
  OpenQuake disaggregates on.
- The GMMs of a tectonic region are used for every IM type of the target.
- Source model mode: one site, the first of the job. Parameters are
  occurrence-rate weighted means of the ruptures in a bin, and mechanisms
  share a bin by occurrence rate, not by contribution to IM*.
- Rules mode: the site is perpendicular to strike (ry0 = 0), with no
  along-strike offset from the hypocentre. Mechanisms share a bin by the
  given fractions, equally by default. Unknown values follow
  Kaklamanos et al. (2011); ztor = max(hypo_depth - 0.6 width sin(dip),
  upper_sd), and width is limited by the seismogenic thickness.
- Site parameters are those given; parameters needed by a particular GMM
  (e.g. region, backarc) must be added to them.
"""
import os
import re
import tomllib
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Union

import numpy as np
import pandas as pd

from .kaklamanos2011 import (
    hypocentral_distances, rjb_rx_from_rrup, rupture_width,
    style_of_faulting)

GEOMETRY_KEYS = ["rake", "dip", "ztor", "width", "hypo_depth", "rjb", "rx",
                 "ry0", "repi", "rhypo"]


def read_gmm_logic_tree(path: Union[str, Path]) -> Dict[str, dict]:
    """Read an OpenQuake (NRML) GMM logic tree

    Parameters
    ----------
    path : Union[str, Path]
        gmpe_logic_tree.xml

    Returns
    -------
    Dict[str, dict]
        Tectonic region -> {'names': [...], 'weights': [...],
        'kwargs': [...]}. GMMs given in TOML form, e.g.
        '[AbrahamsonEtAl2014]\\nregion = "JPN"', keep their arguments
    """
    def local(tag):
        return tag.rsplit("}", 1)[-1]

    out = {}
    for bset in ET.parse(path).iter():
        if local(bset.tag) != "logicTreeBranchSet":
            continue
        trt = bset.get("applyToTectonicRegionType")
        names, weights, kwargs = [], [], []
        for branch in bset:
            if local(branch.tag) != "logicTreeBranch":
                continue
            model = weight = None
            for child in branch:
                if local(child.tag) == "uncertaintyModel":
                    model = child.text.strip()
                elif local(child.tag) == "uncertaintyWeight":
                    weight = float(child.text)
            if model.startswith("["):
                (name, kw), = tomllib.loads(model).items()
            else:
                name, kw = model, {}
            names.append(name)
            weights.append(weight)
            kwargs.append(kw)
        out[trt] = {"names": names, "weights": weights, "kwargs": kwargs}
    return out


def geometry_from_rules(bins: pd.DataFrame,
                        rules: Dict[str, List[dict]]) -> pd.DataFrame:
    """Rupture parameters per bin from per tectonic region rules

    Parameters
    ----------
    bins : pd.DataFrame
        trt, mag, dist (rrup bin centre)
    rules : Dict[str, List[dict]]
        Tectonic region -> list of mechanisms. Each mechanism has
        'rake' and optionally 'fraction' (share of the bin, by default
        split equally), 'dip', 'upper_sd', 'lower_sd', 'hypo_depth',
        'width' and 'side' ('footwall' or 'hanging_wall'). Missing values
        follow Kaklamanos et al. (2011)

    Returns
    -------
    pd.DataFrame
        One row per bin and mechanism: trt, mag, dist, share and
        GEOMETRY_KEYS
    """
    rows = []
    for _, b in bins.iterrows():
        if b.trt not in rules:
            raise KeyError(f"No rules given for tectonic region '{b.trt}'")
        mechs = rules[b.trt]
        for mech in mechs:
            rake = float(mech["rake"])
            style = str(style_of_faulting(rake))
            dip = float(mech.get("dip", {"SS": 90, "R": 40, "N": 50}[style]))
            usd = float(mech.get("upper_sd", 0.0))
            lsd = float(mech.get("lower_sd", 500.0))
            sin_d = np.sin(np.radians(dip))
            width = float(mech.get("width", rupture_width(b.mag, style)))
            width = min(width, (lsd - usd) / sin_d)
            hypo = mech.get("hypo_depth")
            if hypo is None:
                hypo = 5.63 + 0.68 * b.mag if style == "SS" \
                    else 11.24 - 0.2 * b.mag
            hypo = float(np.clip(hypo, usd, lsd))
            ztor = max(hypo - 0.6 * width * sin_d, usd)
            ztor = min(ztor, lsd - width * sin_d)  # keep it above lsd
            rjb, rx = rjb_rx_from_rrup(b.dist, ztor, dip, width,
                                       mech.get("side", "footwall"))
            repi, rhypo = hypocentral_distances(rx, ztor, dip, hypo)
            rows.append(dict(
                trt=b.trt, mag=b.mag, dist=b.dist,
                share=float(mech.get("fraction", 1 / len(mechs))),
                rake=rake, dip=dip, ztor=ztor, width=width,
                hypo_depth=hypo, rjb=rjb, rx=rx, ry0=0.0, repi=repi,
                rhypo=rhypo))
    return pd.DataFrame(rows)


def geometry_from_source_model(job_ini: Union[str, Path], bins: pd.DataFrame,
                               mag_edges: List[float],
                               dist_edges: List[float]) -> pd.DataFrame:
    """Rupture parameters per bin from an OpenQuake source model

    The ruptures of every source are generated with hazardlib and put into
    the disaggregation bins by magnitude and rrup to the (first) site of
    the job. Within a bin, each style of faulting gets the rate-weighted
    mean of its ruptures' parameters and a share proportional to its
    occurrence rate. Rates are multiplied by the source model weights.

    Parameters
    ----------
    job_ini : Union[str, Path]
        OpenQuake job file of the PSHA (source models, logic tree, site,
        rupture discretisation)
    bins : pd.DataFrame
        trt, mag, dist; only these bins are returned
    mag_edges, dist_edges : List[float]
        Disaggregation bin edges (magnitude, rrup)

    Returns
    -------
    pd.DataFrame
        One row per bin and style of faulting: trt, mag, dist, share and
        GEOMETRY_KEYS
    """
    # sources are read in this process, which avoids spawning workers
    os.environ.setdefault("OQ_DISTRIBUTE", "no")
    from openquake.commonlib import readinput
    from openquake.hazardlib.geo.mesh import Mesh
    from openquake.hazardlib.logictree import TWO24

    oq = readinput.get_oqparam(str(job_ini))
    csm = readinput.get_composite_source_model(oq)
    sm_weights = [float(np.sum(r.weight)) for r in csm.full_lt.sm_rlzs]
    sites = readinput.get_site_collection(oq)
    site = Mesh(sites.lons[:1], sites.lats[:1], np.zeros(1))

    mag_edges, dist_edges = np.asarray(mag_edges), np.asarray(dist_edges)
    records = []
    for group in csm.src_groups:
        for src in group:
            w_sm = sum(sm_weights[t % TWO24] for t in src.trt_smrs)
            for rup in src.iter_ruptures():
                surf = rup.surface
                rrup = float(surf.get_min_distance(site)[0])
                mi = np.searchsorted(mag_edges, rup.mag, side="right") - 1
                di = np.searchsorted(dist_edges, rrup, side="right") - 1
                if not (0 <= mi < len(mag_edges) - 1
                        and 0 <= di < len(dist_edges) - 1):
                    continue
                records.append((
                    group.trt, mi, di, rup.occurrence_rate * w_sm, rup.rake,
                    surf.get_dip(), surf.get_top_edge_depth(),
                    surf.get_width(), rup.hypocenter.depth,
                    float(surf.get_joyner_boore_distance(site)[0]),
                    float(surf.get_rx_distance(site)[0]),
                    float(surf.get_ry0_distance(site)[0]),
                    float(rup.hypocenter.distance_to_mesh(
                        site, with_depths=False)[0]),
                    float(rup.hypocenter.distance_to_mesh(site)[0])))
    rups = pd.DataFrame(records, columns=["trt", "mi", "di", "w"]
                        + GEOMETRY_KEYS)
    rups["style"] = style_of_faulting(rups["rake"])

    bins = bins[["trt", "mag", "dist"]].copy()
    bins["mi"] = np.searchsorted(mag_edges, bins["mag"], side="right") - 1
    bins["di"] = np.searchsorted(dist_edges, bins["dist"], side="right") - 1

    rows = []
    for _, b in bins.iterrows():
        sel = rups[(rups.trt == b.trt) & (rups.mi == b.mi)
                   & (rups.di == b.di)]
        if sel.empty:
            raise ValueError(
                f"No ruptures of the source model fall in bin {b.trt}, "
                f"M{b.mag}, R{b.dist}: check that job_ini is the one of "
                "the disaggregation")
        total = sel.w.sum()
        for style, s in sel.groupby("style"):
            vals = {k: float(np.average(s[k], weights=s.w))
                    for k in GEOMETRY_KEYS}
            rows.append(dict(trt=b.trt, mag=b.mag, dist=b.dist,
                             share=float(s.w.sum() / total), **vals))
    return pd.DataFrame(rows)


def build_input(bins: pd.DataFrame, geometry: pd.DataFrame,
                gmm_lt: Dict[str, dict], imt: str, iml: float,
                imi: List[str], site_parameters: dict,
                template: dict = None) -> dict:
    """Assemble the djura record selection input

    Parameters
    ----------
    bins : pd.DataFrame
        trt, mag, dist, rate (from psha.proc_oq_disaggregation_trt)
    geometry : pd.DataFrame
        trt, mag, dist, share and GEOMETRY_KEYS (from geometry_from_rules
        or geometry_from_source_model)
    gmm_lt : Dict[str, dict]
        Tectonic region -> GMM names, weights (from read_gmm_logic_tree)
    imt : str
        Conditioning IM, e.g. 'SA(0.5)'
    iml : float
        IM* value
    imi : List[str]
        IMs of the target, e.g. ['SA(0.1)', 'SA(0.2)', ...]
    site_parameters : dict
        e.g. {'vs30': 600, 'z1pt0': 100, 'z2pt5': 5}
    template : dict, optional
        Other input keys (num_records, nreplicate, ...), by default None

    Returns
    -------
    dict
        Content of input.json
    """
    im_types = sorted({re.sub(r"\(.*", "", im) for im in imi + [imt]})

    gmms, gmm_id = [], {}
    for trt in sorted(bins.trt.unique()):
        if trt not in gmm_lt:
            raise KeyError(f"No GMMs for tectonic region '{trt}'")
        gmm_id[trt] = len(gmms)
        group = {"ID": gmm_id[trt]}
        for im in im_types:
            group[im] = {k: list(v) for k, v in gmm_lt[trt].items()
                         if k != "kwargs" or any(v)}
        gmms.append(group)

    merged = geometry.merge(bins[["trt", "mag", "dist", "rate"]],
                            on=["trt", "mag", "dist"])
    ruptures = []
    for _, r in merged.iterrows():
        rup = {"mag": float(r.mag), "rrup": float(r.dist)}
        rup.update({k: round(float(r[k]), 3) for k in GEOMETRY_KEYS})
        rup["weight"] = float(r.rate * r.share)
        rup["gmms"] = [gmm_id[r.trt]]
        ruptures.append(rup)
    total = sum(r["weight"] for r in ruptures)
    for r in ruptures:
        r["weight"] /= total

    data = dict(template or {})
    data.update({
        "gmms": gmms,
        "site-parameters": site_parameters,
        "ruptures": ruptures,
        "im-star": {"type": imt, "value": iml},
        "imi": list(imi),
    })
    return data
