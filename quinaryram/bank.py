from __future__ import annotations
from dataclasses import dataclass, field
from enum import IntEnum

class Control(IntEnum):
    ERASE = -2
    DECAY = -1
    BYPASS = 0
    ACCUMULATE = 1
    OVERWRITE = 2

@dataclass(frozen=True, slots=True)
class StepMetrics:
    cells: int
    changed: int
    saturated: int
    controls: dict[str, int]

@dataclass(slots=True)
class Bank:
    slots: int
    width: int
    lower: int = -(2**31)
    upper: int = 2**31 - 1
    initial: list[list[int]] | None = None
    _data: list[list[int]] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        for name, value in (
            ("slots", self.slots),
            ("width", self.width),
            ("lower", self.lower),
            ("upper", self.upper),
        ):
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"{name} must be an integer")
        if self.slots < 1 or self.width < 1:
            raise ValueError("slots and width must be positive")
        if self.lower >= self.upper:
            raise ValueError("lower must be smaller than upper")
        self._data = (
            [[0] * self.width for _ in range(self.slots)]
            if self.initial is None
            else [row.copy() for row in self.initial]
        )
        self._validate_matrix(self._data, "data", bounded=True)

    @property
    def data(self) -> tuple[tuple[int, ...], ...]:
        return tuple(tuple(row) for row in self._data)

    def _validate_matrix(self, matrix: list[list[int]], name: str, *, bounded: bool = False) -> None:
        if not isinstance(matrix, list) or len(matrix) != self.slots:
            raise ValueError(f"{name} must contain {self.slots} rows")
        for row in matrix:
            if not isinstance(row, list) or len(row) != self.width:
                raise ValueError(f"each {name} row must contain {self.width} integers")
            for value in row:
                if isinstance(value, bool) or not isinstance(value, int):
                    raise ValueError(f"{name} values must be integers")
                if bounded and not self.lower <= value <= self.upper:
                    raise ValueError(f"{name} value is outside bank bounds")

    def step(self, controls: list[list[int]], operands: list[list[int]]) -> StepMetrics:
        self._validate_matrix(controls, "controls")
        self._validate_matrix(operands, "operands")
        parsed: list[list[Control]] = []
        for row in controls:
            try:
                parsed.append([Control(value) for value in row])
            except ValueError as exc:
                raise ValueError("controls must be one of -2, -1, 0, 1, 2") from exc
        next_data = [row.copy() for row in self._data]
        changed = saturated = 0
        counts = {control.name.lower(): 0 for control in Control}
        for i in range(self.slots):
            for j in range(self.width):
                control = parsed[i][j]
                counts[control.name.lower()] += 1
                old = self._data[i][j]
                operand = operands[i][j]
                if control is Control.ERASE:
                    raw = 0
                elif control is Control.DECAY:
                    raw = old - 1 if old > 0 else old + 1 if old < 0 else 0
                elif control is Control.BYPASS:
                    raw = old
                elif control is Control.ACCUMULATE:
                    raw = old + operand
                else:
                    raw = operand
                value = min(self.upper, max(self.lower, raw))
                saturated += int(value != raw)
                changed += int(value != old)
                next_data[i][j] = value
        self._data = next_data
        return StepMetrics(self.slots * self.width, changed, saturated, counts)

    def snapshot(self) -> dict[str, object]:
        return {"format": "quinaryram-v1", "slots": self.slots, "width": self.width, "lower": self.lower, "upper": self.upper, "data": [list(row) for row in self.data]}

    @classmethod
    def from_snapshot(cls, payload: dict[str, object]) -> "Bank":
        if not isinstance(payload, dict):
            raise ValueError("snapshot must be a JSON object")
        if payload.get("format") != "quinaryram-v1":
            raise ValueError("unsupported snapshot format")
        names = ("slots", "width", "lower", "upper")
        try:
            values = tuple(payload[name] for name in names)
            data = payload["data"]
        except KeyError as exc:
            raise ValueError(f"snapshot is missing {exc.args[0]}") from exc
        for name, value in zip(names, values, strict=True):
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"snapshot {name} must be an integer")
        return cls(*values, initial=data)  # type: ignore[arg-type]
