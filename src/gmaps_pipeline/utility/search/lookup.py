from __future__ import annotations

import re
from collections.abc import Callable, Mapping, Sequence
from typing import Any, TypeAlias, List

_SENTINEL = object()

PathSegment: TypeAlias = str | int | slice | re.Pattern[str] | Callable[..., bool]


def deep_query(obj: Any, *path: PathSegment) -> list[Any]:
    """Return all terminal values reachable by following ``path`` through ``obj``.

    Traversal is recursive and depth-first. Each segment in ``path`` is interpreted
    according to the current container type:

    - Mapping: wildcard ``"*"``, exact string key, regex, or callable predicate
    - Sequence: wildcard ``"*"``, integer index, slice, or callable predicate

    Parameters
    ----------
    obj:
        Root object to traverse.
    *path:
        A sequence of matcher segments applied one by one during traversal.

    Returns
    -------
    list[Any]
        A list containing every terminal value found along matching branches.
        Returns an empty list when no branches match.
    """

    def step(current: Any, segments: list[PathSegment]) -> list[Any]:
        if not segments:
            return [current]

        seg, *rest = segments
        results: list[Any] = []

        # --- Mapping (dict-like) ---
        if isinstance(current, Mapping):
            items = current.items()

            if seg == "*":
                for _, value in items:
                    results.extend(step(value, rest))

            elif isinstance(seg, str):
                value = current.get(seg, _SENTINEL)
                if value is not _SENTINEL:
                    results.extend(step(value, rest))

            elif isinstance(seg, re.Pattern):
                for key, value in items:
                    if seg.search(str(key)):
                        results.extend(step(value, rest))

            elif callable(seg):
                for key, value in items:
                    try:
                        if seg(key, value):
                            results.extend(step(value, rest))
                    except Exception:
                        # Ignore predicate errors for individual items.
                        pass

            else:
                # Unsupported matcher for mappings.
                return []

        # --- Sequence (list/tuple), but not str/bytes ---
        elif isinstance(current, Sequence) and not isinstance(
            current, (str, bytes, bytearray)
        ):
            n = len(current)

            if seg == "*":
                for value in current:
                    results.extend(step(value, rest))

            elif isinstance(seg, int):
                if -n <= seg < n:
                    results.extend(step(current[seg], rest))

            elif isinstance(seg, slice):
                for value in current[seg]:
                    results.extend(step(value, rest))

            elif callable(seg):
                for index, value in enumerate(current):
                    try:
                        if seg(index, value):
                            results.extend(step(value, rest))
                    except Exception:
                        # Ignore predicate errors for individual items.
                        pass

            else:
                # Unsupported matcher for sequences.
                return []

        else:
            # Cannot descend further.
            return []

        return results

    return step(obj, list(path))


def deep_get(obj: Any, *path: PathSegment, default: Any = None) -> Any:
    """Return the first match found by :func:`deep_query`, or ``default``.

    Parameters
    ----------
    obj:
        Root object to traverse.
    *path:
        Same matcher syntax accepted by :func:`deep_query`.
    default:
        Value returned when no match is found. Defaults to ``None``.

    Returns
    -------
    Any
        The first matched terminal value, or ``default`` if no match exists.

    Notes
    -----
    This function cannot distinguish between:

    - no match found
    - the first match being ``None``

    unless you pass a non-``None`` default.
    """

    results = deep_query(obj, *path)
    return results[0] if results else default


def match_component(
    source_text: str,
    target_text: str,
    delimiter: str = ","
) -> List[str]:
    """
    Identify which delimited components from a source string exist within a target string.

    This function splits the source string into components using a specified delimiter,
    then performs a case-insensitive search to check which components are present
    within the target string.

    Args:
        source_text (str): The input string containing components to check (e.g., "A, B, C").
        target_text (str): The string in which to search for component matches.
        delimiter (str, optional): The delimiter used to split the source string. Defaults to ",".

    Returns:
        List[str]: A list of components from the source string that were found in the target string.
    """

    components = [part.strip()
                  for part in source_text.split(delimiter) if part.strip()]
    matches = []

    for component in components:
        pattern = re.escape(component)
        if re.search(pattern, target_text, re.IGNORECASE):
            matches.append(component)

    return matches
