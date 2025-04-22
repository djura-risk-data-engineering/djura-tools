# flake8: noqa
from pathlib import Path
import sys

path = Path(__file__).resolve().parent

sys.path.insert(0, str(path.parent))

from djura.utilities import to_json_serializable
from djura.record_selector.rs import prepare_input_for_hzc
from djura.hazard.psha import proc_oq_hazard_curve


# POEs of interest
# Those are probability of exceedances (POEs) associated with intensity levels
# used during record selection
poes = [0.4, 0.2, 0.1, 0.05, 0.02, 0.01, 0.005, 0.0025, 0.001]

# Set the hazard-curves 
hz = proc_oq_hazard_curve(poes, path / 'data/psha',
                          out_file=path / 'data/psha/hazard.json')

curves = hz['hazard_curves']

rs = prepare_input_for_hzc(path / f'data/records', hz, poes, "SA(0.5)")

# Finally prepare input that can be used inside hazard-consistency application
# at https://apps.djura.it/hazard/hazard-consistency
data = {
    "psha_imstar_intensities": rs["psha_imstar_intensities"],
    "psha_imstar_poes": rs["psha_imstar_poes"],
    "investigation_time": rs["investigation_time"],
    "rs_imi_periods": rs['rs_imi_periods'],
    "rs_imi_intensities": rs['rs_imi_intensities'],
    "im_start": 0.01,
    "im_end": 8.0,
    "num_im": 500,
}
data = to_json_serializable(data)
