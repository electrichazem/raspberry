from __future__ import annotations

import time


class PID:
    def __init__(self, kp: float, ki: float, kd: float, output_limits=(0.0, 100.0)) -> None:
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.min_output, self.max_output = output_limits
        self._integral = 0.0
        self._last_error = 0.0
        self._last_time = time.time()

    def reset(self) -> None:
        self._integral = 0.0
        self._last_error = 0.0
        self._last_time = time.time()

    def compute(self, setpoint: float, measurement: float) -> float:
        now = time.time()
        dt = max(now - self._last_time, 1e-3)
        error = setpoint - measurement
        self._integral += error * dt
        derivative = (error - self._last_error) / dt
        output = (
            self.kp * error
            + self.ki * self._integral
            + self.kd * derivative
        )
        output = max(self.min_output, min(self.max_output, output))
        self._last_error = error
        self._last_time = now
        return output

