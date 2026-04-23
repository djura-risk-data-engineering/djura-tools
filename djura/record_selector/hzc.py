from pathlib import Path
from typing import List
import json
import numpy as np


def prepare_rs_for_hzc(
    selection_dir: Path,
    poes: List[float],
    imts: List[str],
):
    """Prepare input Record selection intensity values for
    hazard consistency checks

    Parameters
    ----------
    selection_dir : Path
        Directory of selected record json outputs following record selector of
        Djura
    poes : List[float]
        List of POEs of interest
    imts : List[str]
        List of intensity measure types of interest

    Returns
    -------
    Dict[numpy.ndarray]
        IM values of selected records
    """
    rs = {}
    for imi in imts:
        rs[imi] = get_rs_imi_intensities(
            selection_dir, poes, imi
        )
    return rs


def get_rs_imi_intensities(
    selection_dir: Path,
    poes: List[float],
    imi: str
):
    imls = []
    for poe in poes:
        with open(selection_dir / f"records_{poe}.json") as f:
            records = json.load(f)

        records = records['selected_scaled_best']
        if '(' in imi:
            im_type = imi.split('(')[0]
            period = float(imi.split('(')[1].split(')')[0])
            period_idx = records['IMi'][im_type].index(period)
            imi_idx = records['im_idxs'][im_type][period_idx]
        else:
            imi_idx = records['im_idxs'][imi]
        imls.append(np.asarray(records['Scaled_IMs'])[:, imi_idx].flatten())

    imls = np.asarray(imls)
    return imls
