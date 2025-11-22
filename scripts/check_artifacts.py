#!/usr/bin/env python3
import json
import sys
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else "/opt/ai-music-orchestrator/orchestration")

queue = json.loads((root / "queue.json").read_text())
state = json.loads((root / "state.json").read_text())

completed = list((root / "completed").glob("*.json"))
failures = list((root / "failures").glob("*.json"))

print("Queue pending:", len(queue.get("pending", [])))
print("Processing:", len(state.get("processing", {})))
print("Completed summaries:", len(completed))
print("Failure summaries:", len(failures))

for summary in completed[:5]:
    job = json.loads(summary.read_text())
    art = job.get("artifacts", [])
    print(f"[completed] {job.get('id')} artifacts: {art}")

if failures:
    print("Failures:")
    for summary in failures:
        job = json.loads(summary.read_text())
        print(f"- {job.get('id')} error: {job.get('error')}")
