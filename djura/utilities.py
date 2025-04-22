from pathlib import Path
import re
import shutil
import pickle
import json
import numpy as np


def to_json_serializable(data):
    if isinstance(data, dict):
        for key, value in data.items():
            data[key] = to_json_serializable(value)
    elif isinstance(data, list):
        return [to_json_serializable(item) for item in data]
    elif isinstance(data, np.ndarray):
        return data.tolist()
    elif isinstance(data, np.float32):
        return float(data)
    elif isinstance(data, np.int32):
        return float(data)

    return data


def get_period_im(name: str):
    """Given name of intensity measure (IM)
    return IM type and associated period (if available)

    Parameters
    ----------
    name : str
        IM name

    Returns
    -------
    tuple
        A tuple containing:
        - IM type as a string (e.g., 'PGA', 'SA')
        - Period as a float if applicable, otherwise omitted
        (e.g., ('PGA', None), ('SA', 0.5))

    Usage
    ------
    >>> get_period_im('PGA')
    ('PGA',)
    >>> get_period_im('SA(0.5)')
    ('SA', 0.5)
    """
    # pattern = r"\((\d+\.\d+)\)?"
    pattern = r"\((\d+(\.\d+)?)\)?(?:\D*)?"

    if '(' in name:
        im_type = name.split('(', 1)[0].strip()
    else:
        im_type = name

    if re.search(pattern, name):
        period = float(re.search(pattern, name).group(1))
    else:
        period = None

    return im_type, period


def export_results(filepath: Path, data, filetype: str):
    """Exports results to file

    Parameters
    ----------
    filepath : Path
        Path where to export data to
    data : any
        Data to be stored
    filetype : str
        Filetype, e.g. npy, json, pkl, csv
    """
    if filetype == "json":
        data = to_json_serializable(data)

    if filetype == "npy":
        np.save(f"{filepath}.npy", data)
    elif filetype == "pkl" or filetype == "pickle":
        with open(f"{filepath}.pickle", 'wb') as handle:
            pickle.dump(data, handle)
    elif filetype == "json":
        with open(f"{filepath}.json", "w") as json_file:
            json.dump(data, json_file)
    elif filetype == "csv":
        data.to_csv(f"{filepath}.csv", index=False)


def remove_path(directory: Path):
    """Removes the directory if it exists

    Parameters
    ----------
    directory : Path
        Directory to be removed
    """
    if directory.is_dir():
        shutil.rmtree(directory)


def create_path(directory: Path):
    """Create a folder if it does not exist

    Parameters
    ----------
    directory : Path
        Directory to be created
    """
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except OSError:
        print("Error: Creating directory. ", directory)
