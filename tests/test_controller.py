import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from controller import ConveyorController, Inputs, State
from simulation import run_demo
from report import render_dashboard, write_reports


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.c = ConveyorController()
        self.i = Inputs()

    def start(self):
        self.i.start = True
        self.c.scan(self.i)
        self.i.start = False
        self.c.scan(self.i)

    def test_initial_state_motor_off(self):
        self.assertEqual(self.c.state, State.IDLE)
        self.assertFalse(self.c.outputs().motor_on)

    def test_start_turns_motor_on(self):
        self.start()
        self.assertEqual(self.c.state, State.RUNNING)
        self.assertTrue(self.c.outputs().motor_on)

    def test_start_requires_rising_edge(self):
        self.start()
        self.i.stop = True
        self.c.scan(self.i)
        self.i.stop = False
        self.c.scan(self.i, 500)
        self.assertEqual(self.c.state, State.IDLE)
        self.c.scan(self.i)
        self.assertEqual(self.c.state, State.IDLE)

    def test_normal_stop_disables_motor_immediately(self):
        self.start()
        self.i.stop = True
        self.c.scan(self.i)
        self.assertEqual(self.c.state, State.STOPPING)
        self.assertFalse(self.c.outputs().motor_on)

    def test_normal_stop_transitions_to_idle(self):
        self.start()
        self.i.stop = True
        self.c.scan(self.i)
        self.i.stop = False
        self.c.scan(self.i, 500)
        self.assertEqual(self.c.state, State.IDLE)

    def test_product_counts_only_rising_edges(self):
        self.start()
        self.i.product_detected = True
        self.c.scan(self.i)
        self.c.scan(self.i)
        self.assertEqual(self.c.products_counted, 1)
        self.i.product_detected = False
        self.c.scan(self.i)
        self.i.product_detected = True
        self.c.scan(self.i)
        self.assertEqual(self.c.products_counted, 2)

    def test_no_count_while_idle(self):
        self.i.product_detected = True
        self.c.scan(self.i)
        self.assertEqual(self.c.products_counted, 0)

    def test_estop_immediately_disables_motor(self):
        self.start()
        self.i.e_stop = True
        self.c.scan(self.i)
        self.assertEqual(self.c.state, State.ESTOP)
        self.assertFalse(self.c.outputs().motor_on)

    def test_estop_stays_latched_when_released(self):
        self.start()
        self.i.e_stop = True
        self.c.scan(self.i)
        self.i.e_stop = False
        self.c.scan(self.i)
        self.assertEqual(self.c.state, State.ESTOP)

    def test_estop_reset_requires_release_and_edge(self):
        self.start()
        self.i.e_stop = True
        self.i.reset = True
        self.c.scan(self.i)
        self.assertEqual(self.c.state, State.ESTOP)
        self.i.e_stop = False
        self.c.scan(self.i)
        self.assertEqual(self.c.state, State.ESTOP)
        self.i.reset = False
        self.c.scan(self.i)
        self.i.reset = True
        self.c.scan(self.i)
        self.assertEqual(self.c.state, State.IDLE)

    def test_reset_never_auto_restarts_motor(self):
        self.start()
        self.i.e_stop = True
        self.c.scan(self.i)
        self.i.e_stop = False
        self.i.reset = True
        self.c.scan(self.i)
        self.assertEqual(self.c.state, State.IDLE)
        self.assertFalse(self.c.outputs().motor_on)

    def test_open_guard_fault_latched(self):
        self.start()
        self.i.guard_closed = False
        self.c.scan(self.i)
        self.assertEqual(self.c.state, State.FAULT)
        self.i.guard_closed = True
        self.c.scan(self.i)
        self.assertEqual(self.c.state, State.FAULT)

    def test_jam_fault(self):
        self.start()
        self.i.jam_detected = True
        self.c.scan(self.i)
        self.assertEqual(self.c.fault_reason, "Conveyor jam")
        self.assertFalse(self.c.outputs().motor_on)

    def test_overload_fault(self):
        self.start()
        self.i.motor_overload = True
        self.c.scan(self.i)
        self.assertEqual(self.c.fault_reason, "Motor overload")

    def test_reset_blocked_until_fault_clears(self):
        self.start()
        self.i.jam_detected = True
        self.c.scan(self.i)
        self.i.reset = True
        self.c.scan(self.i)
        self.assertEqual(self.c.state, State.FAULT)
        self.i.reset = False
        self.i.jam_detected = False
        self.c.scan(self.i)
        self.i.reset = True
        self.c.scan(self.i)
        self.assertEqual(self.c.state, State.IDLE)

    def test_guard_cannot_start_motor(self):
        self.i.guard_closed = False
        self.i.start = True
        self.c.scan(self.i)
        self.assertFalse(self.c.outputs().motor_on)

    def test_negative_timing_rejected(self):
        with self.assertRaises(ValueError):
            self.c.scan(self.i, -1)

    def test_demo_reaches_expected_states(self):
        rows = run_demo()
        self.assertEqual(rows[-1]["state"], "IDLE")
        self.assertEqual(rows[-1]["products_counted"], 3)
        self.assertIn("ESTOP", [x["state"] for x in rows])
        self.assertIn("FAULT", [x["state"] for x in rows])

    def test_report_creates_files(self):
        with TemporaryDirectory() as tmp:
            json_file, html_file = write_reports(run_demo(), Path(tmp) / "reports")
            self.assertTrue(json_file.is_file())
            self.assertTrue(html_file.is_file())
            self.assertIn("Industrial Conveyor", html_file.read_text(encoding="utf-8"))

    def test_report_rejects_empty(self):
        with self.assertRaises(ValueError):
            render_dashboard([])

    def test_report_escapes_events(self):
        rows = run_demo()
        rows[0]["event"] = "<script>alert(1)</script>"
        html = render_dashboard(rows)
        self.assertNotIn("<script>", html)
        self.assertIn("&lt;script&gt;", html)


if __name__ == "__main__":
    unittest.main()
