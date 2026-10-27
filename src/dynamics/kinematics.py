import torch


def integrate_constant_acceleration(
    state: torch.Tensor,
    acceleration: torch.Tensor,
    dt: float,
) -> torch.Tensor:
    """Advance batched position and velocity in an inertial frame.

    State rows contain ``[x, y, z, vx, vy, vz]`` and acceleration rows
    contain ``[ax, ay, az]`` in matching units.
    """
    if state.ndim != 2 or state.shape[1] != 6:
        raise ValueError("state must have shape (num_envs, 6)")
    if acceleration.shape != (state.shape[0], 3):
        raise ValueError("acceleration must have shape (num_envs, 3)")
    if not state.is_floating_point() or not acceleration.is_floating_point():
        raise TypeError("state and acceleration must use floating-point tensors")
    if state.device != acceleration.device or state.dtype != acceleration.dtype:
        raise ValueError("state and acceleration must have the same device and dtype")
    if dt <= 0:
        raise ValueError("dt must be positive")

    position, velocity = state.split(3, dim=1)
    next_position = position + velocity * dt + acceleration * (0.5 * dt * dt)
    next_velocity = velocity + acceleration * dt
    return torch.cat((next_position, next_velocity), dim=1)
