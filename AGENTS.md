# Repository guidance

## Project purpose

This repository develops a high-performance reinforcement-learning system for autonomous control and maneuvering of a conventional drone. The intended scenarios progress from basic flight and target interception to 1v1 combat trained with transfer learning and self-play.

The core design goals are:

- vectorized simulation of many environments in one process;
- the same physics and neural-network code running on CPU or CUDA;
- a stable environment interface independent of the selected RL algorithm;
- interchangeable scripted and learned opponents;
- physical parameters, scenarios and training hyperparameters stored in YAML rather than embedded in code;
- fast headless training without a 3D engine.

Read `docs/PROJECT.md` before architectural work. It defines the intended training stages, technology choices and roadmap. Treat choices described there as the current direction, not as implemented functionality.

## Current state and intended structure

The repository contains an initialized Python scaffold. Add implementation files only when the current task needs them; do not create speculative framework code.

The target layout described in `docs/PROJECT.md` is:

```text
configs/
  dynamics/       physical parameters and model matrices
  agents/         algorithm and network hyperparameters
  train.yaml      device, training stage and checkpoint selection
src/
  dynamics/       vectorized flight dynamics
  envs/           Gymnasium environment, rewards and opponents
  agents/         policies, algorithm construction and self-play
checkpoints/      generated model weights and opponent snapshots
train.py          training entry point
inference.py      evaluation and telemetry entry point
```

Keep these responsibilities separate:

- `dynamics` updates physical state from state, controls and timestep. It must not depend on rewards, opponents or an RL framework.
- `envs` owns Gymnasium spaces, reset/step behavior, observations, rewards, termination and scenario logic.
- `agents` owns neural networks, RL algorithm integration, checkpoint loading and the self-play policy pool.
- `train.py` and `inference.py` compose modules and handle configuration; they do not reimplement physics or environment logic.
- `configs` contains tunable values. Code validates configuration at the boundary and passes typed runtime values inward.

## Before editing

- Read the affected files before editing.
- Search every caller before changing a function signature, tensor shape, return value or side effect.
- Check configuration, tests, fixtures, entry points and checkpoint compatibility affected by the change.
- Treat observation and action spaces, tensor shapes, reward definitions, episode-ending rules, YAML keys and checkpoint formats as public contracts once introduced.
- Keep the change limited to the requested outcome. Report unrelated issues instead of fixing them opportunistically.

## Implementation guidance

- Prefer the smallest implementation that completes the current milestone. Reuse existing code and installed dependencies before adding abstractions or packages.
- Use descriptive, general English names. Preserve established mathematical symbols and domain terms where they make equations easier to compare with their source.
- Keep functions focused and data flow explicit. Add a shared abstraction only when at least two real implementations need the same contract.
- Keep physics equations and their ordering recognizable. Do not change coefficients, units, integration rules, clamping, thresholds or initial conditions as part of unrelated cleanup.
- Put tunable physical values, scenario settings and RL hyperparameters in YAML. Constants that define an invariant or tensor index may stay close to the code.
- Validate external configuration, checkpoint metadata and public API inputs early. Do not hide invalid state with broad exception handling or silent defaults.
- Add comments only when a constraint, unit convention or numerical decision is not clear from the code.

## Tensor and environment rules

- Keep simulation operations batched. Avoid Python loops over individual environments in the training hot path when a PyTorch tensor operation expresses the same work.
- Use a consistent batch-first convention, normally `(num_envs, ...)`, and document the meaning and shape of public observations, actions and state.
- Preserve tensor `device` and `dtype`. Create constants and temporary tensors on the same device and with a compatible dtype as the values they interact with.
- Avoid implicit CPU transfers, `.numpy()` calls and device synchronization inside `step` or physics updates. Transfer data only at explicit logging, evaluation or I/O boundaries.
- Make reset operations work for both all environments and a selected subset without corrupting the remaining batch.
- Keep Gymnasium `terminated` and `truncated` semantics distinct. Return data in the API shape and type required by the installed Gymnasium version.
- Make seeding explicit for Python, NumPy, PyTorch, environments and opponent sampling where those components are used.
- Keep rewards and observations numerically stable: state units and coordinate frames must be explicit, angles must use one documented convention, and normalization must not divide by zero.
- Run learned opponents in evaluation mode without gradient tracking. Checkpoint loading must validate observation/action dimensions before use.

## Training and self-play

- Keep the environment independent of PPO, SAC, TRPO and any particular RL library. Framework adapters belong in `agents` or the training entry point.
- Stage I uses progressively harder deterministic opponents. Stage II starts from a compatible Stage I checkpoint and replaces the opponent with frozen policies sampled from a historical pool.
- Do not change observation or action dimensions between transfer-learning stages unless the task explicitly includes a migration strategy.
- Save enough metadata with checkpoints to reproduce the model architecture, spaces and relevant configuration.

## Dependencies and configuration

- Python must satisfy the version declared in `pyproject.toml`.
- Use `uv` for dependency and environment management, and update `uv.lock` with dependency changes. Runtime packages belong in project dependencies, visualization tools in `dev`, and test-only tools in `test`.
- PyTorch uses mutually exclusive extras: `cpu` on macOS or Linux without CUDA, and `cuda` only on Linux with a compatible NVIDIA driver. Do not silently substitute one backend for the other.
- When alternatives are listed in `docs/PROJECT.md`, add only the implementation selected for the current path.
- Never edit `.venv` or install unrecorded packages into it.
- Keep device selection and experiment settings in configuration; do not hard-code CUDA availability.
- Never store credentials, machine-specific absolute paths or private dataset locations in tracked configuration.

## Tests and verification

- For behavior changes, add or update the narrowest test that proves the contract, then implement the smallest passing change.
- Physics tests should cover tensor shapes, batched behavior, device/dtype preservation and a small known trajectory or invariant where feasible.
- Environment tests should cover reset, one step, selected-environment reset, spaces, termination versus truncation and deterministic seeding without requiring a long training run.
- Training integration tests should use tiny configurations and mocked or minimal workloads. Do not make normal tests depend on CUDA, large checkpoints, external services or hours of training.
- Run focused tests with `uv run --group test pytest <path-or-test>`. Run the full suite when shared physics, environment contracts, configuration loading or packaging changes.
- For documentation-only changes, verify referenced paths and commands; do not add tests that merely restate documentation.
- Report exactly what was run and what could not be checked because hardware, data, checkpoints or dependencies were unavailable.

## Documentation and generated files

- Keep `README.md` focused on setup, primary commands and links to detailed design documentation.
- Update `docs/PROJECT.md` when an architectural decision or roadmap assumption changes, rather than allowing code and the project description to diverge.
- Do not commit virtual environments, caches, training runs, generated telemetry or uncurated checkpoints.

## Git and user changes

- Commit changes frequently after each coherent, verified increment. Keep commits focused and use concise messages that describe the completed change.
- Local staging and commits do not require separate approval. Review the exact files being staged and never include unrelated user changes, generated artifacts or secrets.
- Do not push, pull, switch branches, merge, rebase, reset or otherwise change branches, remotes or published history without explicit user approval.
- Preserve existing user changes and do not overwrite unrelated work.
- Do not add repository traces suggesting that changes were produced by an assistant or conversation.
