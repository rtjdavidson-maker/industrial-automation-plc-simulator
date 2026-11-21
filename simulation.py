"""Scripted scenario runner; deterministic repeatable PLC scan demonstrations."""
from dataclasses import asdict
from controller import ConveyorController, Inputs


def run_demo() -> list[dict]:
    plc = ConveyorController()
    i = Inputs()
    rows = []

    def cycle(note: str, milliseconds: int = 100):
        plc.scan(i, milliseconds)
        row = asdict(plc.snapshot(i))
        row["event"] = note
        rows.append(row)

    cycle("Power on: idle")
    i.start = True
    cycle("Start pressed")
    i.start = False
    cycle("Start released")
    for n in range(1, 4):
        i.product_detected = True
        cycle(f"Product {n} reached photoeye")
        i.product_detected = False
        cycle("Photoeye cleared")
    i.jam_detected = True
    cycle("Jam sensor activated: latch fault")
    i.jam_detected = False
    cycle("Jam sensor cleared; fault remains latched")
    i.reset = True
    cycle("Operator resets cleared jam")
    i.reset = False
    cycle("Reset released")
    i.start = True
    cycle("Operator restarts after fault")
    i.start = False
    cycle("Start released")
    i.e_stop = True
    cycle("Emergency stop input activated")
    i.e_stop = False
    cycle("E-stop released; remains latched")
    i.reset = True
    cycle("Operator acknowledges E-stop")
    i.reset = False
    cycle("Reset released")
    return rows
