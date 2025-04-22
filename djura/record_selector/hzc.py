from pathlib import Path
from typing import List
import json
import numpy as np

from ..utilities import get_period_im


def prepare_input_for_hzc(
    selection_dir: Path,
    psha: dict,
    poes: List[float],
    cond_imt: str,
):
    poes = np.sort(poes)[::-1]
    data = {
        "rs_imi_intensities": [],
    }
    im_stars = []
    for poe in poes:
        with open(selection_dir / f"records_{poe}.json") as f:
            records = json.load(f)
        records = records['selected_scaled_best']
        im_idxs = np.asarray(records['im_idxs']['SA'])
        scaled_ims = np.asarray(records['Scaled_IMs'])[:, im_idxs]

        idx = records['IMi']['SA'].index(
            float(cond_imt.split('(')[1].split(')')[0]))
        im_stars.append(np.asarray(records['Scaled_IMs'])[0, idx])

        if 'rs_imi_periods' not in data:
            data['rs_imi_periods'] = records['IMi']['SA']

        data['rs_imi_intensities'].append(scaled_ims.tolist())
        # data['rs_imi_intensities'].append(records['Scaled_IMs'])

    data['psha_imstar_intensities'] = psha['cond_imls'][cond_imt]
    im_stars.sort()
    data['psha_imstar_poes'] = psha['cond_poes']
    data['investigation_time'] = psha['investigation_time']

    data['psha_imi_intensities'] = {}
    data['psha_imi_poes'] = {}

    curves = psha['hazard_curves']
    for key in curves.keys():
        _, period = get_period_im(key)
        data['psha_imi_intensities'][str(period)] = curves[
            key
        ]['iml']
        data['psha_imi_poes'][str(period)] = curves[
            key
        ]['poe']

    return data
