from collections.abc import Mapping

import jsbsim
import numpy as np

from .base import FlightDynamics


class JSBSimDynamics(FlightDynamics[np.ndarray, np.ndarray]):
    """Single-aircraft JSBSim adapter with SI state and normalized controls.

    State is ``[north, east, up, v_north, v_east, v_up, roll, pitch, yaw, p, q, r]``.
    Control is ``[throttle, aileron, elevator, rudder]``.
    """

    state_size = 12
    control_size = 4
    state_properties = (
        "position/from-start-neu-n-ft",
        "position/from-start-neu-e-ft",
        "position/from-start-neu-u-ft",
        "velocities/v-north-fps",
        "velocities/v-east-fps",
        "velocities/v-down-fps",
        "attitude/phi-rad",
        "attitude/theta-rad",
        "attitude/psi-rad",
        "velocities/p-rad_sec",
        "velocities/q-rad_sec",
        "velocities/r-rad_sec",
    )
    feet_to_meters = 0.3048
    controls = (
        ("fcs/throttle-cmd-norm", 0.0, 1.0),
        ("fcs/aileron-cmd-norm", -1.0, 1.0),
        ("fcs/elevator-cmd-norm", -1.0, 1.0),
        ("fcs/rudder-cmd-norm", -1.0, 1.0),
    )

    def __init__(
        self,
        aircraft: str,
        dt: float,
        *,
        initialization: str | None = None,
        initial_conditions: Mapping[str, float] | None = None,
    ) -> None:
        if not aircraft:
            raise ValueError("aircraft must be a non-empty model name")
        if not np.isfinite(dt) or dt <= 0:
            raise ValueError("dt must be finite and positive")
        self.aircraft = aircraft
        self.dt = float(dt)
        self.initialization = initialization
        self.initial_conditions = dict(initial_conditions or {})
        self._fdm = self._create_fdm()

    def _create_fdm(self) -> jsbsim.FGFDMExec:
        fdm = jsbsim.FGFDMExec(None)
        if not fdm.load_model(self.aircraft):
            raise ValueError(f"could not load JSBSim aircraft model: {self.aircraft}")
        fdm.set_dt(self.dt)
        if self.initialization is not None and not fdm.load_ic(self.initialization, True):
            raise ValueError(f"could not load JSBSim initialization: {self.initialization}")
        for name, value in self.initial_conditions.items():
            fdm.set_property_value(name, float(value))
        if not fdm.run_ic():
            raise RuntimeError(f"could not initialize JSBSim aircraft: {self.aircraft}")
        fdm.set_property_value("propulsion/set-running", -1)
        return fdm

    def reset(self, batch_size: int = 1) -> np.ndarray:
        if batch_size != 1:
            raise ValueError("JSBSimDynamics supports one aircraft per instance")
        self._fdm = self._create_fdm()
        return self.state

    def step(self, control: np.ndarray) -> np.ndarray:
        control = np.asarray(control, dtype=np.float64)
        if control.shape != (self.control_size,):
            raise ValueError(f"control must have shape ({self.control_size},)")
        if not np.isfinite(control).all():
            raise ValueError("control values must be finite")
        for value, (name, minimum, maximum) in zip(control, self.controls, strict=True):
            if not minimum <= value <= maximum:
                raise ValueError(f"{name} must be in [{minimum}, {maximum}]")
        for value, (name, _, _) in zip(control, self.controls, strict=True):
            self._fdm.set_property_value(name, float(value))
        if not self._fdm.run():
            raise RuntimeError(f"JSBSim stopped while stepping aircraft: {self.aircraft}")
        return self.state

    @property
    def state(self) -> np.ndarray:
        values = np.array(
            [self._fdm.get_property_value(name) for name in self.state_properties],
            dtype=np.float64,
        )
        values[:6] *= self.feet_to_meters
        values[5] *= -1.0
        return values


def make_quadcopter(dt: float = 0.01) -> JSBSimDynamics:
    return JSBSimDynamics("F450", dt, initialization="initGrnd")


def make_fixed_wing(dt: float = 0.01) -> JSBSimDynamics:
    return JSBSimDynamics(
        "c172p",
        dt,
        initial_conditions={"ic/h-sl-ft": 1000.0, "ic/u-fps": 100.0},
    )
