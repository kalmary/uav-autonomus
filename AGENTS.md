# Repository guidance

## Project purpose

This repository develops a hybrid global/local path planner for horizontal UAV
flight. When world geometry is known, an optional global planner calculates an
initial route before flight. During flight, LiDAR observations are authoritative
and a local planner validates or modifies the route before returning checkpoints.

The first milestone is independent of UAV flight dynamics. Treat the vehicle
as a point in a 2D plane and optimize geometric path length. A time-optimal
route requires motion constraints and is outside the initial scope.

Read `docs/PROJECT.md` before architectural work and `docs/STATUS.md` before
assuming that a planned component is implemented.

## Current scope

- horizontal planning only;
- one rotating LiDAR beam initially, with the number of beams configurable;
- nominal scan frequency of 10 Hz and range of 10 metres, both configurable;
- configurable minimum obstacle distance;
- an optional building-height grid may be supplied before flight;
- flight without a prior map or initial global plan must remain supported;
- global planning is replaceable so another 2D or future 3D planner can be used;
- output is an ordered sequence of 2D checkpoints.

The planner requires the UAV pose in a stable coordinate frame. Keep simulator
transport separate from mapping and route planning so the planner is not tied
to Three.js or a particular message protocol.

## Before editing

- Read the affected files before editing.
- Search every caller before changing a function signature, coordinate frame,
  data shape, return value or side effect.
- Check configuration, tests, fixtures and simulator integration affected by
  the change.
- Treat input messages, coordinates, units, occupancy values, planner status
  and checkpoint output as public contracts once introduced.
- Keep the change limited to the requested outcome. Report unrelated issues
  instead of fixing them opportunistically.

## Implementation guidance

- Prefer the smallest implementation that completes the current milestone.
- Keep sensor ingestion, world-model updates, path planning and simulator
  transport separate.
- Use descriptive, general English names.
- Put tunable values such as LiDAR range, scan frequency, grid resolution and
  obstacle clearance in configuration.
- Validate external messages and configuration at the boundary. Do not hide
  invalid state with broad exception handling or silent defaults.
- State coordinate frames, angle conventions, units and timestamp semantics
  explicitly.
- Add comments only when a constraint or numerical decision is not clear from
  the code.

## Planning rules

- Keep initial global planning optional and behind a small planner contract.
- Use NetworkX A* for shortest paths on the collision-free planning graph.
  Initial planning requires available geometry and enabled preplanning.
- The `--preplan` / `--no-preplan` CLI option overrides the YAML `preplan`
  setting. Without an override, use YAML, then built-in defaults.
- Convert a building-height grid into blocked cells for the mission altitude,
  then apply the configured clearance before global planning.
- Build a 2D occupancy representation from pose-aligned LiDAR rays.
- Mark the traversed part of a ray as free and a valid return as occupied.
- Inflate occupied space by the configured minimum obstacle distance before
  planning.
- Treat the global route as guidance, not as confirmed free space. The local
  planner must validate the route against current LiDAR observations.
- Use A* on the current local occupancy grid for the first reactive replanner;
  simplify its grid path before emitting checkpoints.
- Replan a local detour when observed geometry differs from the initial map and
  rejoin the global route when practical.
- If the global route cannot be safely rejoined, continue dynamic planning
  toward the destination. Failure to create an initial route also falls back
  to dynamic planning. Disabling preplanning never disables local planning.
- Without an initial route, use the destination as the long-term target and
  advance through locally safe checkpoints.
- Do not claim global optimality in an unknown environment. The initial target
  is the shortest collision-free path in the current world model. A grid graph
  constrains optimality to its available edges and resolution.
- Checkpoints must not cross occupied or inflated cells.

## Dependencies and configuration

- Python must satisfy the version declared in `pyproject.toml` while this
  repository remains Python-based.
- Use `uv` for dependency and environment management, and update `uv.lock`
  with dependency changes.
- Use YAML for planner configuration.
- Reuse the standard library and installed dependencies before adding a
  package.
- Never edit `.venv` or install unrecorded packages into it.
- Never store credentials or machine-specific paths in tracked configuration.

## Tests and verification

- For behavior changes, add or update the narrowest test that proves the
  contract.
- Mapping tests should cover ray endpoints, free-space updates, maximum-range
  readings and obstacle inflation.
- Planner tests should cover known-map initial planning, operation without an
  initial plan, a locally forced detour, no available route, checkpoint
  collision checks and deterministic results.
- Integration tests should use small synthetic scans and must not require a
  graphical simulator.
- Report exactly what was run and what could not be checked.

## Documentation and generated files

- Keep `README.md` focused on setup, primary commands and links to detailed
  documentation.
- Update `docs/PROJECT.md` when the planning contract or architectural
  direction changes.
- Update `docs/STATUS.md` when implementation status or a known limitation
  changes.
- Do not commit virtual environments, caches, simulator recordings or
  generated routes.

## Git and user changes

- Do not perform Git operations without explicit user approval.
- Preserve existing user changes and do not overwrite unrelated work.
- Do not add repository traces suggesting that changes were produced by an
  assistant or conversation.
