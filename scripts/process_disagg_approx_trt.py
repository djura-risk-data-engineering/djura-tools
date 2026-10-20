"""
Build a djura record selection input (input.json) from a TRT_Mag_Dist
disaggregation and the GMM logic tree.

This is an approximate approach: mean disaggregation, GMMs paired by
tectonic region with their logic tree weights.

Rupture parameters a bin does not give (rake, dip, ztor, width, hypo_depth,
rjb, rx, ry0, repi, rhypo) come from the OpenQuake source model (job_ini),
or from rules per tectonic region (rules), for PSHA done with other
software.
"""
import json
import sys
from pathlib import Path

path = Path(__file__).resolve().parent
sys.path.insert(0, str(path.parent))

from djura.hazard.psha import proc_oq_disaggregation_trt  # noqa: E402
from djura.hazard.disagg_approx import (  # noqa: E402
    build_input, geometry_from_rules, geometry_from_source_model,
    read_gmm_logic_tree)

example = path / "data" / "multi_trt"

# Mean TRT_Mag_Dist disaggregation and GMM logic tree
disagg = example / "data" / "TRT_Mag_Dist-mean-0_5.csv"
gmm_lt = example / "gmpe_logic_tree.xml"

# Conditional IM, its PoE and IMs of the target
imt = "SA(0.5)"
poe = 0.1
imi = ["SA(0.05)", "SA(0.1)", "SA(0.15)", "SA(0.2)", "SA(0.3)", "SA(0.4)",
       "SA(0.5)", "SA(0.75)", "SA(1.0)", "SA(1.5)", "SA(2.0)"]

site_parameters = {"vs30": 600, "vs30measured": True, "z1pt0": 100,
                   "z2pt5": 5}

# Rupture parameters from the OpenQuake source model, or set job_ini to None
# to use the rules per tectonic region
job_ini = example / "job_disagg.ini"
rules = {
    "Active Shallow Crust": [
        {"rake": 90, "dip": 30, "upper_sd": 8, "lower_sd": 20,
         "side": "footwall"}],
    "Stable Continental Crust": [
        {"rake": 0, "dip": 90, "upper_sd": 0, "lower_sd": 10,
         "hypo_depth": 5}],
}

# Contributions to IM occurring at IM* (Fox et al. 2016) instead of exceeding
# it; needs the disaggregation at a PoE just below poe, e.g. 0.99 * poe
occurrence = False

# Record selection settings (djura defaults if omitted)
selection = {
    "num_records": 40,
    "num-components": 2,
    "component-definition": "RotD50",
    "max_scaling_factor": 3.0,
    "correlation-models": {"SA-SA": "baker_jayaram"},
}

out_file = example / "input.json"

bins, meta = proc_oq_disaggregation_trt(
    disagg, imt, poe=poe, occurrence=occurrence)

if job_ini is not None:
    geometry = geometry_from_source_model(
        job_ini, bins, meta["mag_bin_edges"], meta["dist_bin_edges"])
else:
    geometry = geometry_from_rules(bins, rules)

data = build_input(bins, geometry, read_gmm_logic_tree(gmm_lt), imt,
                   meta["iml"], imi, site_parameters, selection)
out_file.write_text(json.dumps(data, indent=2))

print(f"{imt} = {meta['iml']:.4g} g (poe {meta['poe']}): "
      f"{len(data['ruptures'])} ruptures -> {out_file}")
