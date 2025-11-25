Testing & Validation
====================

Prereq env
----------
- `N8N_API_TOKEN` set locally (from `/opt/codex/.env` key `n8n_api`).
- n8n accessible at `https://n8n.lothortech.com`.
- Services running on `192.168.10.133` with open ports 11434, 8011, 8012, 8013, 8018.
- Worker/webhook auth: `WORKER_TOKEN` from `/opt/n8n/.env` (or `docker-compose.yml` env) passed as `?token=...` for `worker/run`/scheduler triggers.

Happy-path
----------
1) Health probes:
   - `bash scripts/test_health.sh`
2) Enqueue sample jobs:
   - `bash scripts/test_enqueue.sh`
3) Run worker cycles:
   - `bash scripts/test_worker.sh`
4) Inspect artifacts and job status:
   - `python3 scripts/check_artifacts.py /opt/ai-music-orchestrator/orchestration`

Failure simulation
------------------
- Stop a service (e.g., `docker stop ai-image`) then run `scripts/test_worker.sh`; job should retry up to 3 times and land in `failures/<jobId>.json`.
- Corrupt queue file: remove a job file and hit `GET /webhook/health/queue` to see `pendingMissing` flag it.
- Network drop: block port 8012 temporarily and confirm Health Check - Generator State reports `degraded`.

Load smoke
----------
- Enqueue multiple small jobs by looping `scripts/test_enqueue.sh` or adjusting payloads; monitor GPU with `nvidia-smi -l 2` on the GPU host.

Resets
------
- Clear queue: overwrite `queue.json` with `config/queue.sample.json`.
- Clear state: overwrite `state.json` with `config/state.sample.json`.
- Keep artifacts for postmortem; rerun enqueue afterwards.***
