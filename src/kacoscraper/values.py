from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class InverterValue:
    name: str
    """Name of the value."""
    unit: str | None = None
    """Unit, if applicable."""
    wire_data: tuple[str, int] | None = None
    parse: Callable[[float], Any] = lambda v: v
