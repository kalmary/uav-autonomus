import pytest
import torch

from src.dynamics import integrate_constant_acceleration


def test_integrates_batched_constant_acceleration() -> None:
    state = torch.tensor(
        [
            [0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
            [10.0, 20.0, 30.0, 0.0, -2.0, 1.0],
        ],
        dtype=torch.float64,
    )
    acceleration = torch.tensor(
        [
            [2.0, 0.0, 0.0],
            [0.0, 4.0, -2.0],
        ],
        dtype=torch.float64,
    )

    result = integrate_constant_acceleration(state, acceleration, dt=0.5)

    expected = torch.tensor(
        [
            [0.75, 0.0, 0.0, 2.0, 0.0, 0.0],
            [10.0, 19.5, 30.25, 0.0, 0.0, 0.0],
        ],
        dtype=torch.float64,
    )
    torch.testing.assert_close(result, expected)
    assert result.device == state.device
    assert result.dtype == state.dtype


def test_rejects_mismatched_batch() -> None:
    state = torch.zeros((2, 6))
    acceleration = torch.zeros((1, 3))

    with pytest.raises(ValueError, match="acceleration must have shape"):
        integrate_constant_acceleration(state, acceleration, dt=0.1)
