# flake8: noqa
from pathlib import Path
import sys

path = Path(__file__).resolve().parent

sys.path.insert(0, str(path.parent))

from djura.utilities import to_json_serializable
from djura.record_selector.hzc import prepare_rs_for_hzc
from djura.hazard.psha import proc_oq_hazard_curve


# POEs of interest
# Those are probability of exceedances (POEs) associated with intensity levels
# used during record selection
poes = [0.4, 0.2, 0.1, 0.05, 0.02, 0.01, 0.005, 0.0025, 0.001]

# IMs of interest
imts = ["SA(0.5)"]

# Conditional IM (for visualisations)
cond_im = "SA(0.5)"

# Set the hazard-curves 
hz = proc_oq_hazard_curve(poes, path / 'data/psha',
                          out_file=path / 'data/psha/hazard.json')

curves = hz['hazard_curves']

rs = prepare_rs_for_hzc(path / f'data/records', hz["cond_poes"], imts)

# Finally prepare input that can be used inside hazard-consistency application
# at https://apps.djura.it/hazard/hazard-consistency

data = {
    "imts": imts,
    "response_spectra": rs,
    "conditional_poes": hz["cond_poes"],
    "conditional_intensities": hz["cond_imls"][cond_im],
    "investigation_time": hz["investigation_time"],
    "num_im": 500,
    "hazard_curves": curves,
}

data = to_json_serializable(data)
