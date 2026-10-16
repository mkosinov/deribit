from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Period:
    """Start and end period unix timestamps"""

    start: int
    end: int
