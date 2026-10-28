# UAV horizontal path planning

This project targets hybrid global/local planning of a collision-free horizontal
route from point A to point B. With known building geometry and preplanning
enabled, the initial planner will use NetworkX A* for the shortest path on the
planning graph. During flight,
streamed LiDAR observations will validate that route and trigger local detours
when observed obstacles differ from the map.

Local planning always runs. It detours around newly observed obstacles and
tries to rejoin a safe part of the planned route. If rejoining is impossible,
or no initial route exists, it continues toward the destination using the
current world model. Unknown environments have no guarantee of a globally
shortest route; grid resolution also limits the available paths.

The initial sensor model is a rotating horizontal LiDAR with one beam, a 10 Hz
scan frequency and a 10 m maximum range. These values and the minimum obstacle
distance are configurable.

The repository currently provides the package structure, validated configuration
and an optional global-planner interface. Mapping and planning algorithms are not
implemented yet. The Three.js message protocol will be selected after the
simulator is available.

## Setup

Use Python 3.14 or newer and `uv`:

```sh
uv sync --locked --group test
uv run --locked uav-planner --config configs/planner.yaml
uv run --locked uav-planner --config configs/planner.yaml --no-preplan
uv run --locked --group test pytest
```

The `uav-planner` command validates and prints configuration; it does not start
a planning loop. `uv run --locked python -m src` validates the defaults.
Distance settings use metres. LiDAR frequency currently means complete rotations
per second; the simulator adapter must explicitly convert its sensor timing.

`--preplan` and `--no-preplan` override the YAML `preplan` setting; otherwise
YAML falls back to built-in defaults. The default is `preplan: true`, but initial
planning also requires available geometry. Missing geometry or no initial route
means dynamic planning only. These settings never disable local replanning.

## Structure

```text
src/
    config.py       # Validated planner and sensor settings
    __main__.py     # Configuration validation command
    planning/       # Optional global-planner contract; algorithms to follow
    mapping/        # Boundary reserved for LiDAR and height-grid world models
    integration/    # Boundary reserved for simulator transport and conversion
configs/planner.yaml
tests/
```

The initial global planner will use NetworkX. Local A* and mapping
will remain independent of simulator transport. Training and flight dynamics
are outside this package.

See [`docs/PROJECT.md`](docs/PROJECT.md) for the planned behavior and
[`docs/STATUS.md`](docs/STATUS.md) for the current implementation status.
