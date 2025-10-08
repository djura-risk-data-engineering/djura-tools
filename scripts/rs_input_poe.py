import json
from pathlib import Path

path = Path(__file__).parent
imt = "SA(0.59)"

# Load JSON as a Python dict
with open(path / f"data/{imt}.json", "r") as f:
    data = json.load(f)

poes = data['poes']

for poe in poes:
    _data = data.copy()

    ruptures = data['poes'][str(poe)]['ruptures']
    im_star = data['poes'][str(poe)]['im-star']  # adjust if key name differs

    _data['ruptures'] = ruptures
    _data['im-star'] = im_star

    output_file = path / f"{imt}_{poe}.json"
    # with open(output_file, 'w') as f_out:
    #     json.dump(_data, f_out, indent=4)

    # print(f"Saved {output_file}")
