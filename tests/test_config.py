from pathlib import Path

import pytest

from src.config import PlannerConfig, load_config


def test_example_matches_defaults() -> None:
    path = Path(__file__).resolve().parents[1] / "configs" / "planner.yaml"
    assert load_config(path) == PlannerConfig()


@pytest.mark.parametrize("value", [0, -1, 1.5, True, "1"])
def test_rejects_invalid_beam_count(value) -> None:
    with pytest.raises(ValueError, match="lidar_beams"):
        PlannerConfig(lidar_beams=value)


@pytest.mark.parametrize(
    "name",
    ["lidar_frequency_hz", "lidar_range_m", "grid_resolution_m", "obstacle_clearance_m"],
)
@pytest.mark.parametrize("value", [-1, float("nan"), float("inf"), True, "10", None])
def test_rejects_invalid_measurements(name, value) -> None:
    with pytest.raises(ValueError, match=name):
        PlannerConfig(**{name: value})


@pytest.mark.parametrize("name", ["lidar_frequency_hz", "lidar_range_m", "grid_resolution_m"])
def test_rejects_zero_positive_measurements(name) -> None:
    with pytest.raises(ValueError, match=name):
        PlannerConfig(**{name: 0})


def test_accepts_zero_clearance() -> None:
    assert PlannerConfig(obstacle_clearance_m=0).obstacle_clearance_m == 0


def test_loads_partial_config(tmp_path) -> None:
    path = tmp_path / "planner.yaml"
    path.write_text("lidar_beams: 4\nlidar_range_m: 20.0\n")
    assert load_config(path) == PlannerConfig(lidar_beams=4, lidar_range_m=20)


def test_rejects_unknown_settings(tmp_path) -> None:
    path = tmp_path / "planner.yaml"
    path.write_text("lidar_ragne_m: 20.0\n")
    with pytest.raises(ValueError, match="lidar_ragne_m"):
        load_config(path)


@pytest.mark.parametrize("value", [0, 1, "true", None])
def test_rejects_non_boolean_preplan(value) -> None:
    with pytest.raises(ValueError, match="preplan"):
        PlannerConfig(preplan=value)


@pytest.mark.parametrize("preplan", [True, False])
@pytest.mark.parametrize("geometry_available", [True, False])
def test_preplanning_requires_geometry_and_enabled_setting(preplan, geometry_available) -> None:
    config = PlannerConfig(preplan=preplan)
    assert config.should_preplan(geometry_available=geometry_available) is (
        preplan and geometry_available
    )


@pytest.mark.parametrize("content", ["", "null", "[]", "10", "1: true", "preplan: ["])
def test_rejects_invalid_yaml_configuration(tmp_path, content) -> None:
    path = tmp_path / "planner.yaml"
    path.write_text(content)
    with pytest.raises(ValueError):
        load_config(path)


def test_rejects_python_yaml_tags(tmp_path) -> None:
    path = tmp_path / "planner.yaml"
    path.write_text("!!python/object:builtins.object {}")
    with pytest.raises(ValueError, match="Invalid YAML"):
        load_config(path)
