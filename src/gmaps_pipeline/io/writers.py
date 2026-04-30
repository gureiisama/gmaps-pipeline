from pathlib import Path
from time import time_ns
import json
from typing import Any


def write_json(
    data: Any,
    path: Path | str | None = None,
    file_name: str | None = None,
    create_dirs: bool = False,
) -> Path:
    """
    Serialize a Python object to JSON and write it to disk.

    This function supports both directory targets and full file paths:

    - If ``path`` is a directory (or does not yet exist and is treated as one),
      the output file will be created inside it using ``file_name``.
    - If ``path`` is a file path ending in ``.json``, it is treated as the full
      destination and ``file_name`` is ignored.

    Parameters
    ----------
    data : Any
        The Python object to serialize. Must be JSON serializable.
    path : Path | str | None, optional
        Target directory or full file path. Defaults to the current working directory.
    file_name : str | None, optional
        Name of the output file when ``path`` is a directory. If not provided,
        a timestamp-based name (e.g., ``output_123456789.json``) is generated.
    create_dirs : bool, optional
        If True, non-existent directories in the target path will be created.
        If False, a missing directory raises ``FileNotFoundError``.

    Returns
    -------
    Path
        The full path to the written JSON file.

    Raises
    ------
    ValueError
        If a file path or file name does not end with ``.json``.
    FileNotFoundError
        If the target directory does not exist and ``create_dirs`` is False.
    TypeError
        If ``data`` is not JSON serializable.
    OSError
        If writing to disk fails.

    Notes
    -----
    - Parent directories are created only when ``create_dirs=True``.
    - When ``path`` is a file path, ``file_name`` is ignored.
    - Uses UTF-8 encoding with pretty-printed (indented) JSON output.
    """
    base_path = Path(path) if path is not None else Path.cwd()

    # Case 1: path explicitly looks like a JSON file
    if base_path.suffix.lower() == ".json":
        if not base_path.parent.exists():
            if create_dirs:
                base_path.parent.mkdir(parents=True, exist_ok=True)
            else:
                raise FileNotFoundError(
                    f"Directory does not exist: {base_path.parent}")

        full_path = base_path

    # Case 2: treat path as directory
    else:
        if not base_path.exists():
            if create_dirs:
                base_path.mkdir(parents=True, exist_ok=True)
            else:
                raise FileNotFoundError(
                    f"Directory does not exist: {base_path}")

        if not base_path.is_dir():
            raise NotADirectoryError(f"Expected directory, got: {base_path}")

        if file_name is None:
            file_name = f"output_{time_ns()}.json"

        if not file_name.lower().endswith(".json"):
            raise ValueError('file_name must end with ".json"')

        full_path = base_path / file_name

    with full_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return full_path
