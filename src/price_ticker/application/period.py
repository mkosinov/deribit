from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Period:
    start: int | None
    end: int | None
