# Industrial Automation & PLC Conveyor Simulator

A Python-based **software simulation of PLC-style conveyor control logic**. The project demonstrates a finite-state machine, simulated digital inputs and outputs, event-based product counting, jam and overload detection, guard interlocks, a *latched emergency-stop input*, reset/restart sequencing, structured JSON trace output, and an offline HTML monitoring dashboard.

> **SAFETY:** This is for educational simulation only. It does **not** implement a certified PLC, safety-rated relay, functional safety standard, actual emergency-stop circuit, or real industrial motor control. **Never connect this code to moving equipment or use it as a safety controller.** A physical emergency stop requires independently engineered safety hardware.

## Windows quick start

1. Download the ZIP and choose **Extract All**. Do not run programs inside the compressed ZIP.
2. Open the extracted folder containing `main.py` in File Explorer.
3. Click the File Explorer address bar, type `cmd`, and press **Enter**.
4. Run each command separately:

```cmd
python main.py
start "" "output\dashboard.html"
python -m unittest discover -s tests -v
```

The project requires **Python 3.10 or newer**, with **no third-party packages**.

## What happens during the demo?

The scripted simulation reproduces a production line:

1. Power on with conveyor idle and motor commanded OFF.
2. Operator presses START, enabling the motor command.
3. A photoelectric-style input detects three products (the counter increments on rising edges only).
4. A simulated jam causes a **latched FAULT** and motor command OFF.
5. Clearing the jam does not automatically restart the conveyor; the operator must press RESET and then START.
6. Activating a simulated emergency-stop input immediately turns the software motor command OFF and latches `ESTOP`.
7. Releasing the E-stop does not restart anything; RESET acknowledges the cleared input and returns the controller to IDLE.

The simulator outputs a CSV-like event trace on the terminal, `output/plc_trace.json`, and `output/dashboard.html`.

## Inputs, outputs, and state table

| Inputs | Meaning |
|---|---|
| `start`, `stop`, `reset` | Simulated operator controls |
| `e_stop` | Simulated emergency-stop input; latches E-stop state |
| `guard_closed` | Simulated protective-guard interlock |
| `product_detected` | Simulated photoeye; counts one product on a rising edge |
| `jam_detected` | Simulated conveyor jam |
| `motor_overload` | Simulated overload condition |

| State | Motor output | Exit condition |
|---|---|---|
| IDLE | OFF | START edge and no active fault |
| RUNNING | ON | STOP, open guard, jam, overload, or E-stop |
| STOPPING | OFF | 500 ms normal-stop demonstration |
| FAULT | OFF | Fault cleared + separate RESET edge |
| ESTOP | OFF | E-stop released + healthy inputs + separate RESET edge |

**Note:** The 500 ms STOPPING state is a **normal operational stop simulation only**, not an emergency-stop delay. Emergency stop always disables the simulated motor command immediately.

## Files

| File | Responsibility |
|---|---|
| `controller.py` | PLC-like scan cycle, states, interlocks, and safety-oriented software decisions |
| `simulation.py` | Deterministic scripted operation and fault sequence |
| `report.py` | Dashboard and JSON report creation |
| `main.py` | Console runner |
| `tests/test_controller.py` | 21 automated tests covering logic, recovery, counting, and reports |
| `.github/workflows/python-tests.yml` | Automated Python test workflow on GitHub |

## Verified software demonstration — screenshots

The screenshots below were captured while running this **educational Python simulation on Windows**. They are not photographs of a physical PLC or motor system.

### 1. Conveyor operation and fault handling

The console traces **19 simulated controller scans**, including START, three photoeye-triggered product counts, a jam fault, deliberate fault reset, restart, and a latched emergency-stop input. The motor *command* is off while faults are active.

![Windows Command Prompt tracing conveyor startup, product counts, jam fault, reset, and emergency stop](Screenshot%202026-11-21%20144946.png)

### 2. Automated unit tests

The Windows test run completed **21 tests with an OK result**. Tests exercise motor control states, product counting, fault latching, reset behavior, and report generation.

![Command Prompt showing 21 successful Python PLC logic unit tests](Screenshot%202026-11-21%20145242.png)

### 3. HTML diagnostics dashboard

The offline dashboard summarizes **19 scans, 3 counted products, 4 fault/E-stop scans**, and a final controller state of **IDLE**, then displays the event timeline.

![Industrial conveyor PLC simulation HTML dashboard summary and initial events](Screenshot%202026-11-21%20145304.png)

### 4. Fault recovery and emergency-stop input sequence

The detailed event log shows the jam fault remaining latched after the simulated jam sensor clears, followed by operator reset. Later, the simulated emergency-stop input also remains latched after release and requires a reset before returning to IDLE.

![Industrial conveyor simulation log showing jam fault, recovery, and latched emergency-stop behavior](Screenshot%202026-11-21%20145340.png)

**Scope:** These results validate the software model and its reporting. No physical machinery, certified safety controller, or electrical safety circuit was tested.

## Test it and learn

```cmd
python -m unittest discover -s tests -v
```

**Suggested learning challenges:**

- Add a simulated low-air-pressure sensor input that blocks startup.
- Add a reject gate to count defective parts separately.
- Modify the product counter to count only in RUNNING, then add a new test proving it.
- Add a configurable start-up delay before the motor command turns ON.
- Explain why releasing the emergency-stop input must **not** automatically restart the motor.

## Career relevance

PLC-style program flow, finite-state machines, discrete I/O, motor interlocks, event counting, emergency-stop input modeling, automated validation, diagnostic logging, and industrial control-system documentation. This is a useful *software* foundation for automation engineering; real PLC and electrical work require separate training and equipment.
