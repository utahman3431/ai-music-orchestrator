Architecture
============

Roles
-----
- n8n (hosted) orchestrates queue, workers, schedulers, and health probes. Filesystem path seen by n8n: `/data/orchestration`.
- GPU laptop `192.168.10.133` (`lothor-ROG`) runs model microservices via Docker/WSL2 with NVIDIA acceleration.
- Queue + state + artifacts live on the host path `/opt/ai-music-orchestrator/orchestration` (bind-mounted into n8n as `/data/orchestration`).

Folder layout (host)
--------------------
```
/opt/ai-music-orchestrator/orchestration/
  queue.json              # pending FIFO
  state.json              # processing map, heartbeats, versions
  jobs/<jobId>/job.json   # job spec + status
  jobs/<jobId>/logs/      # worker logs per job
  jobs/<jobId>/artifacts/ # generated files
  completed/              # symlinks or json summaries for done jobs
  failures/               # failed job summaries
  tmp/                    # transient scratch
```

Queue + job schema
------------------
- `queue.json`:
```json
{
  "pending": [
    {
      "id": "job-uuid",
      "type": "audio|image|video|text",
      "priority": 0,
      "submitted_at": "2025-11-21T20:00:00Z",
      "payload_path": "jobs/job-uuid/job.json"
    }
  ]
}
```
- `state.json`:
```json
{
  "processing": {
    "job-uuid": {
      "worker": "worker-1",
      "started_at": "...",
      "heartbeat_at": "...",
      "retry": 0
    }
  },
  "version": 1
}
```
- `jobs/<jobId>/job.json`:
```json
{
  "id": "job-uuid",
  "type": "audio",
  "status": "pending|processing|completed|error",
  "params": { "prompt": "...", "duration": 8, "seed": 123 },
  "artifacts": [],
  "logs": [],
  "created_at": "...",
  "updated_at": "..."
}
```

Workflow overview
-----------------
- **Queue – Add Job**: Webhook (`POST /queue/add`), validates payload, writes `job.json`, appends to `queue.json.pending`, returns job id.
- **Queue – Dequeue Job**: Webhook (`POST /queue/dequeue`), atomically pops oldest pending, updates `state.json.processing`, returns payload path.
- **Queue – Scheduler**: Cron-triggered; calls Worker – Process One Job to drain queue with backoff/parallelism control.
- **Worker – Process One Job**: Dequeues job, dispatches to model microservice based on `type`, writes artifacts, updates status, handles retries.
- **Worker – Update Job Status**: Utility webhook for explicit status changes (manual or recovery).
- **Health Check – Generator State**: Probes model service health endpoints (Ollama, SD, MusicGen, SVD, Chroma).
- **Health Check – Filesystem**: Validates readability/writability of `/data/orchestration`, existence of key files, free space.
- **Health Check – Queue Integrity**: Validates JSON structure, cross-checks `queue.json` vs `state.json` and job files.

Dispatch matrix (service URLs)
------------------------------
- LLM / control: `http://192.168.10.133:11434` (Ollama)
- Image: `http://192.168.10.133:8011`
- Audio: `http://192.168.10.133:8012`
- Video: `http://192.168.10.133:8013`
- Embeddings / Chroma: `http://192.168.10.133:8018`

Retry strategy
--------------
- Each job gets up to 3 attempts; backoff 30s, 2m, 5m.
- Worker writes failure summary to `failures/<jobId>.json` after final attempt.
- Partial artifacts retained in job folder for debugging.

Logging
-------
- Per-job logs under `jobs/<jobId>/logs/worker.log`.
- Health workflows push summaries to `jobs/health/*.json`.
- n8n execution logs remain in n8n; use tag `ai-music` for filtering (set in workflows).

Heartbeats
----------
- Worker updates `state.json.processing[jobId].heartbeat_at` every dispatch cycle.
- Health check flags stale heartbeats (>10m) and can requeue orphaned jobs via Update Job Status workflow.

Load control
------------
- Scheduler respects `MAX_CONCURRENT` (config in workflow) before invoking another Worker. Default 1. Increase after confirming GPU headroom.

Testing plan (high-level)
-------------------------
- Enqueue synthetic jobs (audio/image/video/text) with small sizes.
- Run Worker – Process One Job manually and via Scheduler.
- Validate artifacts present and job status transitions.
- Induce failure by pointing to invalid model endpoint to test retries and failure logging.
- Network reachability tests in `scripts/test_health.sh` and `docs/network.md`.***
