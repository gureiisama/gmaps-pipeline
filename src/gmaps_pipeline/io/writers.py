import json
from pathlib import Path
from time import time_ns
from typing import Any


def write_json(data: Any, path: Path | str | None = None, file_name: str | None = None) -> Path:
    """
    Serialize an object to JSON and write it to disk using pathlib.

    Parameters
    ----------
    data : Any
        The Python object to serialize as JSON.
    path : Path | str | None, optional
        Directory where the file will be saved. Defaults to the current working directory.
    file_name : str | None, optional
        Output file name. Defaults to a timestamp-based name such as
        "output_1234567890.json""

    Returns
    -------
    Path
        The full path to the written JSON file.

    Raises
    ------
    NotADirectoryError
        If "path" does not point to an existing directory.
    ValueError
        If "file_name" does not end with ".json"
    OSError
        If writing the file fails for any filesystem-related reason.
    TypeError
        If "data" is not JSON serializable.
    """
    base_path = Path(path) if path is not None else Path.cwd()

    if not base_path.is_dir():
        raise NotADirectoryError(f"Invalid directory: {base_path}")

    if file_name is None:
        file_name = f"output_{time_ns()}.json"

    if not file_name.lower().endswith(".json"):
        raise ValueError('file_name must end with ".json"')

    full_path = base_path / file_name

    with full_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

    return full_path
