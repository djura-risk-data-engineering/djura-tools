"""
Process Disaggregation outputs from Oq-engine

This is an approximate approach
"""

# flake8: noqa
from pathlib import Path
import sys
import json

path = Path(__file__).resolve().parent

sys.path.insert(0, str(path.parent))

from djura.hazard.psha import proc_oq_disaggregation, proc_oq_hazard_curve


# POEs of interest
# Those are probability of exceedances (POEs) associated with intensity levels
# used during record selection
poes = [0.4, 0.2, 0.1, 0.05, 0.02, 0.01, 0.005, 0.0025, 0.001]

# Process the disaggregation excel file from OQ-Engine
disagg_all = proc_oq_disaggregation(
    path / 'data/oq', poes,
    out_file=path / 'data/psha/disaggregation.json'
)

hz = proc_oq_hazard_curve(poes, path / 'data/psha')

# SA(0.5) to be used as conditional IM
imt = "SA(0.5)"

imls = hz['cond_imls'][imt]

rs_input = json.load(open(path / "data/djura-conditional-all-input.json"))
rs_input["imi"] = [
    'SA(0.05)', 'SA(0.075)', 'SA(0.1)', 'SA(0.15)', 'SA(0.2)',
    'SA(0.25)', 'SA(0.3)', 'SA(0.4)', 'SA(0.5)', 'SA(0.6)',
    'SA(0.7)', 'SA(0.8)', 'SA(0.9)', 'SA(1.0)', 'SA(1.25)',
    'SA(1.5)', 'SA(2.0)', 'SA(2.5)', 'SA(3.0)'
]
rs_input["gmms"] = [
    {"ID": 0, "SA": {"names": ['KothaEtAl2020ESHM20'], "weights": [1]}}
]
rs_input["site-parameters"] = {
    "z2pt5": "1.38",
    "z1pt0": "391.34",
    "vs30": "370",
    "xvf": "150",
    "region": 0
}

for idx, poe in enumerate(poes):
    disagg = disagg_all["imt_disagg"][imt][
        'mag_dist_hazard_contributions'][f'poe_{poe}']
    ruptures = []
    for i in range(len(disagg['mag'])):
        ruptures.append(
            {
                "ID": i,
                "gmms": [0],
                "rjb": disagg['dist'][i],
                "mag": disagg['mag'][i],
                "rake": 0.0,
                "weight": disagg['prob_occur'][i],
                # "weight": disagg['hz_cont'][i],
            }
        )
    rs_input["ruptures"] = ruptures
    rs_input["im-star"] = {"type": imt, "value": imls[idx]}
    rs_input["im_weights"] = [1 / len(rs_input["imi"])] * len(rs_input["imi"])

    # You may save the rs_input variable to a file for each POE
    # This input then may be directly uploaded in 
    # https://apps.djura.it/hazard/record-selector/conditional

    # NOTE: however, be careful as browsers might not easily display
    # large amount of data
    # If you encounter issues, feel free to contact us for questions
    # or to help run the API without a UI
