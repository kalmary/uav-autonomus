from typing import Protocol, TypeVar

State = TypeVar("State", covariant=True)
Control = TypeVar("Control", contravariant=True)


class FlightDynamics(Protocol[State, Control]):
    """Interface for interchangeable flight models and control representations."""

    def reset(self, batch_size: int = 1) -> State: ...

    def step(self, control: Control) -> State: ...
