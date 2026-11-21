"""Offline HTML dashboard and JSON trace from simulated controller snapshots."""
from html import escape
from pathlib import Path
import json


def write_reports(records: list[dict], directory: Path) -> tuple[Path, Path]:
    if not records:
        raise ValueError("Cannot report zero controller scans")
    directory.mkdir(parents=True, exist_ok=True)
    json_path = directory / "plc_trace.json"
    html_path = directory / "dashboard.html"
    json_path.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    html_path.write_text(render_dashboard(records), encoding="utf-8")
    return json_path, html_path


def render_dashboard(records: list[dict]) -> str:
    if not records:
        raise ValueError("Cannot render zero controller scans")
    last = records[-1]
    faults = sum(r["state"] in ("FAULT", "ESTOP") for r in records)
    table_rows = []
    for row in records:
        status = escape(str(row["state"]))
        css = "bad" if row["state"] in ("FAULT", "ESTOP") else "good" if row["state"] == "RUNNING" else "muted"
        table_rows.append("<tr>"
            + f'<td>{row["time_ms"]}</td>'
            + f'<td>{escape(str(row["event"]))}</td>'
            + f'<td class="{css}">{status}</td>'
            + f'<td>{"ON" if row["motor_on"] else "OFF"}</td>'
            + f'<td>{row["products_counted"]}</td>'
            + f'<td>{escape(str(row["fault_reason"]))}</td>'
            + "</tr>")
    head = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Conveyor PLC Simulation</title>
<style>:root{font-family:system-ui,sans-serif;color:#e9f1fb;background:#0c1524}*{box-sizing:border-box}
main{max-width:1150px;margin:38px auto;padding:0 18px}h1{font-size:clamp(1.6rem,4vw,2.3rem)}
p{color:#afc0d4}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:14px;margin:24px 0}
.card,.panel{background:#1a2b43;border:1px solid #38506d;border-radius:14px;padding:20px}
.card strong{display:block;font-size:2rem;margin-top:6px}.panel{overflow:auto}table{width:100%;border-collapse:collapse;min-width:780px}
th,td{padding:11px;border-bottom:1px solid #344a66;text-align:left;font-size:.92rem}.bad{color:#ff9d9d;font-weight:700}
.good{color:#5be5b3;font-weight:700}.muted{color:#bdcfe3}</style></head><body><main>
<h1>Industrial Conveyor • PLC Logic Simulator</h1><p>Offline software demonstration — no actual PLC, relay, or motor is connected.</p>"""
    cards = [
        ("Controller scans", len(records)),
        ("Products counted", last["products_counted"]),
        ("Fault / E-stop scans", faults),
        ("Final state", last["state"]),
    ]
    card_html = "".join(f'<div class="card">{escape(label)}<strong>{escape(str(value))}</strong></div>' for label,value in cards)
    return (head + '<section class="cards">' + card_html + '</section><section class="panel"><h2>Scan event log</h2>'
            + '<table><thead><tr><th>Time (ms)</th><th>Input / event</th><th>Controller state</th><th>Motor</th><th>Product count</th><th>Fault reason</th></tr></thead><tbody>'
            + "".join(table_rows) + '</tbody></table></section>'
            + '<p>Educational logic demonstration only. Emergency stops on physical machinery require independently engineered, certified safety hardware.</p>'
            + '</main></body></html>')
