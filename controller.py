"""Simulated industrial conveyor control using an explicit finite-state machine.

Educational model only: NO physical machinery or safety-rated controller.
"""
from dataclasses import asdict, dataclass
from enum import Enum


class State(str, Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"
    ESTOP = "ESTOP"
    FAULT = "FAULT"


@dataclass
class Inputs:
    start: bool = False
    stop: bool = False
    reset: bool = False
    e_stop: bool = False
    guard_closed: bool = True
    product_detected: bool = False
    jam_detected: bool = False
    motor_overload: bool = False


@dataclass
class Outputs:
    motor_on: bool
    ready_light: bool
    run_light: bool
    fault_light: bool
    alarm: bool


@dataclass
class Snapshot:
    time_ms: int
    state: str
    motor_on: bool
    guard_closed: bool
    estop_active: bool
    jam_active: bool
    overload_active: bool
    products_counted: int
    fault_reason: str


class ConveyorController:
    """Deterministic PLC-like scan logic, with explicit latching faults.

    Safety note: a software command cannot provide a real emergency stop.
    """

    def __init__(self):
        self.state = State.IDLE
        self.time_ms = 0
        self.products_counted = 0
        self.fault_reason = ""
        self._last_product = False
        self._last_start = False
        self._last_reset = False
        self._stop_elapsed = 0
        self.stop_delay_ms = 500  # Demonstrates normal controlled stop, NEVER E-stop

    def scan(self, inputs: Inputs, delta_ms: int = 100) -> Outputs:
        if delta_ms < 0:
            raise ValueError("delta_ms must be nonnegative")
        self.time_ms += delta_ms
        start_edge = inputs.start and not self._last_start
        reset_edge = inputs.reset and not self._last_reset
        product_edge = inputs.product_detected and not self._last_product
        self._last_start = inputs.start
        self._last_reset = inputs.reset
        self._last_product = inputs.product_detected

        # Highest priority: emergency stop cuts motor command immediately and latches.
        if inputs.e_stop:
            self.state = State.ESTOP
            self.fault_reason = "Emergency stop activated"
        # Faults must latch until a deliberate reset after conditions are safe.
        elif self.state == State.ESTOP:
            if reset_edge and inputs.guard_closed and not inputs.jam_detected and not inputs.motor_overload:
                self.state = State.IDLE
                self.fault_reason = ""
        elif not inputs.guard_closed or inputs.jam_detected or inputs.motor_overload:
            self.state = State.FAULT
            if not inputs.guard_closed:
                self.fault_reason = "Safety guard open"
            elif inputs.motor_overload:
                self.fault_reason = "Motor overload"
            else:
                self.fault_reason = "Conveyor jam"
        elif self.state == State.FAULT:
            if reset_edge:
                self.state = State.IDLE
                self.fault_reason = ""
        elif self.state == State.IDLE:
            if start_edge:
                self.state = State.RUNNING
        elif self.state == State.RUNNING:
            if product_edge:
                self.products_counted += 1
            if inputs.stop:
                self.state = State.STOPPING
                self._stop_elapsed = 0
        elif self.state == State.STOPPING:
            self._stop_elapsed += delta_ms
            if self._stop_elapsed >= self.stop_delay_ms:
                self.state = State.IDLE
        return self.outputs()

    def outputs(self) -> Outputs:
        # STOPPING represents a normal controlled stop; motor command is already off.
        motor_on = self.state == State.RUNNING
        return Outputs(
            motor_on=motor_on,
            ready_light=self.state == State.IDLE,
            run_light=motor_on,
            fault_light=self.state in (State.FAULT, State.ESTOP),
            alarm=self.state in (State.FAULT, State.ESTOP),
        )

    def snapshot(self, inputs: Inputs) -> Snapshot:
        return Snapshot(
            time_ms=self.time_ms,
            state=self.state.value,
            motor_on=self.outputs().motor_on,
            guard_closed=inputs.guard_closed,
            estop_active=inputs.e_stop,
            jam_active=inputs.jam_detected,
            overload_active=inputs.motor_overload,
            products_counted=self.products_counted,
            fault_reason=self.fault_reason,
        )
