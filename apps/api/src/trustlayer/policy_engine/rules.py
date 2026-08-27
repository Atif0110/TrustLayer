from __future__ import annotations

from collections.abc import Mapping


def matches_condition(
    condition: Mapping[str, object], *, action: str, context: Mapping[str, object]
) -> bool:
    if condition.get("action") != action:
        return False

    for key, expected in condition.items():
        if key == "action":
            continue
        if key.endswith("_lte"):
            actual = context.get(key[:-4])
            if not isinstance(actual, int | float) or not isinstance(expected, int | float):
                return False
            if actual > expected:
                return False
            continue
        if key.endswith("_gt"):
            actual = context.get(key[:-3])
            if not isinstance(actual, int | float) or not isinstance(expected, int | float):
                return False
            if actual <= expected:
                return False
            continue
        if context.get(key) != expected:
            return False
    return True
