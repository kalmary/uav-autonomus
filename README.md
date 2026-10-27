# UAV horizontal path planning

This project uses hybrid global/local planning to produce a collision-free
horizontal route from point A to point B. With known building geometry,
`extremitypathfinder` calculates the initial geometric shortest path. During
flight, streamed LiDAR observations validate that route and trigger local
detours when observed obstacles differ from the map.

The local planner also works without an initial map or global route. Initial
planning is replaceable so another 2D planner or a future 3D planner can be
introduced without changing mission coordination.

The initial sensor model is a rotating horizontal LiDAR with one beam, a 10 Hz
scan frequency and a 10 m maximum range. These values and the minimum obstacle
distance are configurable.

The implementation will integrate with a Three.js simulation. Its message
protocol and the planner runtime will be selected after the simulator is
available.

See [`docs/PROJECT.md`](docs/PROJECT.md) for the planned behavior and
[`docs/STATUS.md`](docs/STATUS.md) for the current implementation status.
