"""Unique sentinel objects.

Todo:
    * Deprecate in favour of PEP 661-style sentinel objects if accepted.
"""

import enum
from typing import Final
from typing import final


@final
class _UnsetT(enum.Enum):
    UNSET = enum.auto()


Unset: Final = _UnsetT.UNSET
type UnsetT = _UnsetT
