from __future__ import annotations
import argparse, json
from pathlib import Path
import sys
from .bank import Bank

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Apply atomic five-state updates to bounded integer memory.")
    parser.add_argument("program", help="JSON bank definition and step list")
    parser.add_argument("--out", help="write final snapshot")
    args = parser.parse_args(argv)
    try:
        spec = json.loads(Path(args.program).read_text(encoding="utf-8"))
        bank = Bank(spec["slots"], spec["width"], spec.get("lower", -(2**31)), spec.get("upper", 2**31 - 1), spec.get("data"))
        metrics = [bank.step(item["controls"], item["operands"]) for item in spec.get("steps", [])]
        result = {"snapshot": bank.snapshot(), "steps": [metric.__dict__ if hasattr(metric, "__dict__") else {"cells": metric.cells, "changed": metric.changed, "saturated": metric.saturated, "controls": metric.controls} for metric in metrics]}
        output = json.dumps(result, indent=2, sort_keys=True)
        if args.out:
            Path(args.out).write_text(json.dumps(bank.snapshot(), indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        print(f"quinaryram: {exc}", file=sys.stderr)
        return 2
    print(output)
    return 0
