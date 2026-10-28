"""Planner settings in metres and seconds; scan frequency is rotations per second."""

from dataclasses import dataclass
from math import isfinite
from pathlib import Path

import yaml


@dataclass(frozen=True)
class PlannerConfig:
    preplan: bool = True
    lidar_beams: int = 1
    lidar_frequency_hz: float = 10.0
    lidar_range_m: float = 10.0
    grid_resolution_m: float = 0.25
    obstacle_clearance_m: float = 0.5

    def __post_init__(self) -> None:
        if type(self.preplan) is not bool:
            raise ValueError("preplan must be a boolean")
        if type(self.lidar_beams) is not int or self.lidar_beams < 1:
            raise ValueError("lidar_beams must be a positive integer")
        for name in (
            "lidar_frequency_hz",
            "lidar_range_m",
            "grid_resolution_m",
            "obstacle_clearance_m",
        ):
            value = getattr(self, name)
            if type(value) not in (int, float) or not isfinite(value):
                raise ValueError(f"{name} must be a finite number")
            if value < 0 or (value == 0 and name != "obstacle_clearance_m"):
                raise ValueError(f"{name} is outside its allowed range")

    def should_preplan(self, *, geometry_available: bool) -> bool:
        return self.preplan and geometry_available


def load_config(path: str | Path) -> PlannerConfig:
    with Path(path).open(encoding="utf-8") as stream:
        try:
            values = yaml.safe_load(stream)
        except yaml.YAMLError as error:
            raise ValueError(f"Invalid YAML configuration: {error}") from error
    if not isinstance(values, dict) or any(type(key) is not str for key in values):
        raise ValueError("Configuration must be a mapping with string keys")
    unknown = values.keys() - PlannerConfig.__dataclass_fields__.keys()
    if unknown:
        raise ValueError(f"Unknown configuration settings: {', '.join(sorted(unknown))}")
    return PlannerConfig(**values)
