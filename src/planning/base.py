"""Transport-independent contract for optional initial planning."""

from typing import Protocol

type Point = tuple[float, float]
type Route = tuple[Point, ...]


class GlobalPlanner(Protocol):
    """An initial planner bound to a world model with clearance already applied.

    Points use metres in a stable Cartesian world frame. A route includes the
    start and destination, or one point if they coincide. None means no route.
    Implementations reject invalid coordinates with ValueError. Reference routes
    must be validated against LiDAR observations before execution. Initial
    planning requires both available geometry and enabled preplanning. Without
    a reference route, local planning continues toward the mission destination.
    """

    def plan(self, start: Point, goal: Point) -> Route | None: ...
