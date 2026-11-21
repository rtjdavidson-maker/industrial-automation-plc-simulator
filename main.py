"""Run the deterministic conveyor PLC demonstration and save reports."""
from pathlib import Path
from report import write_reports
from simulation import run_demo


def main():
    records = run_demo()
    json_path, html_path = write_reports(records, Path("output"))
    print("Mode: SIMULATED INDUSTRIAL PLC — NO PHYSICAL EQUIPMENT")
    for row in records:
        print(f'{row["time_ms"]:>5} ms | {row["state"]:<8} | '
              f'Motor {"ON" if row["motor_on"] else "OFF":<3} | '
              f'Count {row["products_counted"]} | {row["event"]}')
    print(f"\nSaved JSON: {json_path.resolve()}")
    print(f"Saved HTML: {html_path.resolve()}")
    print('On Windows, open the dashboard: start "" "output\\dashboard.html"')


if __name__ == "__main__":
    main()
