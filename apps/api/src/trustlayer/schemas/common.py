from __future__ import annotations

from typing import TypeAlias

ScalarValue: TypeAlias = str | int | float | bool
RequestContext: TypeAlias = dict[str, ScalarValue]
