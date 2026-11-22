"""Summarize reload execution history exported to CSV."""
import argparse
import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path

def summarize(source: Path, output: Path) -> list[dict]:
    apps = defaultdict(list)
    with source.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            try:
                duration = float(row["duration_seconds"])
            except (ValueError, KeyError) as exc:
                raise ValueError(f"Invalid duration row: {row}") from exc
            if duration < 0:
                raise ValueError("Duration cannot be negative.")
            apps[row["app_name"]].append({"status": row["status"].strip().lower(), "duration": duration})
    report = []
    for app, runs in sorted(apps.items()):
        successes = sum(run["status"] == "success" for run in runs)
        report.append({"app_name": app, "runs": len(runs), "successes": successes, "failures": len(runs)-successes, "success_rate_pct": round(successes / len(runs) * 100, 1), "median_duration_seconds": round(statistics.median(run["duration"] for run in runs), 1)})
    output.mkdir(parents=True, exist_ok=True)
    (output / "reload_health.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/task_runs.csv"))
    parser.add_argument("--output", type=Path, default=Path("outputs"))
    args = parser.parse_args()
    print(json.dumps(summarize(args.input, args.output), indent=2))

if __name__ == "__main__":
    main()
