# deep-query Documentation

## Created by: Gray Egaran
## Last Updated: 04/22/2026

Lightweight, flexible traversal for nested Python data structures.

```python
from gmaps_pipeline.utility.lookup import deep_query, deep_get
```

Search dict/list trees using composable path matchers: exact keys, wildcards, regex, slices, and predicates.

---

## Features

- Works on mixed `dict` / `list` / `tuple` structures
- Multiple matcher types (string, `*`, regex, slice, callable)
- Returns all matches (`deep_query`) or first match (`deep_get`)
- Safe predicate execution (errors are ignored per element)

---

## Installation

This module is part of the project structure:

```
gmaps_pipeline/
└── utility/
    └── lookup.py
```

Ensure the project is installed in editable mode or on `PYTHONPATH`:

```bash
pip install -e .
```

---

## Quick Start

```python
from gmaps_pipeline.utility.lookup import deep_query

payload = {
    "team": {
        "members": [
            {"name": "Ada"},
            {"name": "Grace"},
        ]
    }
}

print(deep_query(payload, "team", "members", "*", "name"))
# ['Ada', 'Grace']
```

---

## API Reference

### `deep_query(obj, *path)`

Return all values matching the provided path.

| Parameter | Type             | Description            |
| --------- | ---------------- | ---------------------- |
| `obj`     | Any              | Root object            |
| `*path`   | Matcher segments | Traversal instructions |

**Returns:** `list`

---

### `deep_get(obj, *path, default=None)`

Return first match or `default`.

| Parameter | Type             | Description            |
| --------- | ---------------- | ---------------------- |
| `obj`     | Any              | Root object            |
| `*path`   | Matcher segments | Traversal instructions |
| `default` | Any              | Fallback value         |

**Returns:** Any

---

## Path Syntax

### Mapping (dict-like)

| Segment          | Meaning            |
| ---------------- | ------------------ |
| `"*"`            | All values         |
| `str`            | Exact key          |
| `re.Pattern`     | Regex match on key |
| `callable(k, v)` | Predicate filter   |

### Sequence (list/tuple)

| Segment          | Meaning          |
| ---------------- | ---------------- |
| `"*"`            | All elements     |
| `int`            | Index            |
| `slice`          | Subset           |
| `callable(i, v)` | Predicate filter |

---

## Examples

### Wildcard

```python
deep_query(data, "users", "*", "name")
```

### Regex

```python
import re
deep_query(data, re.compile(r"^item_"), "value")
```

### Predicate

```python
deep_query(data, lambda k, v: v["age"] >= 18, "age")
```

### Index / Slice

```python
deep_query(data, "items", 0)
deep_query(data, "items", slice(0, 3))
```

---

## Behavior Notes

- Depth-first traversal
- Independent branch evaluation
- Unsupported matcher/container combos return no results
- Strings are NOT treated as sequences

---

## Limitations

- No object attribute traversal
- No cycle detection
- No path metadata returned
- Predicate errors are silently ignored
- Regex applies only to mapping keys
- `deep_get` cannot distinguish `None` vs missing

---

## Complexity

- Exact lookups: efficient
- Wildcards / predicates: potentially expensive
- Regex: adds per-key overhead

---

## Recommended Improvements (Optional, not included on this documentation)

- Add type hints
- Add cycle detection
- Add debug mode for predicate errors
- Add path-returning variant (e.g. `deep_query_with_path`)