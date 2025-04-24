"""
Process Disaggregation outputs from OQ-engine
Datastore

This method is not available within the UI of Djura
But it can be used through the API.

If you are willing to utilise the API directly without the
UI, feel free to contact us!

This is an exact approach
"""

# flake8: noqa
from pathlib import Path
import sys
import json

path = Path(__file__).resolve().parent

sys.path.insert(0, str(path.parent))

from djura.hazard.dstore import get_context_from_dstore


# OQ Datastores (.hdf5) are typically located in:
# C:\Users\<your-username>\oqdata or
# C:\Users\<your-username>\Documents\oqdata

# Conditional IM, does not have to match the conditional
# IM used during conditional selection of OQ engine
im_ref = "SA(0.5)"

dstore = "85"
hdf_path = path.parents[5] / f"oqdata/calc_{dstore}.hdf5"
ctx, oq = get_context_from_dstore(hdf_path, im_ref=im_ref)

# You may choose to save the context into a pickle
# from djura.utilities import export_results

# export_results(
#     path / f"ctx_{dstore}",
#     ctx,
#     "pickle"
# )
