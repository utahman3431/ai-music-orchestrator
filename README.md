AI Music Orchestrator (n8n + local GPU services)
=================================================

This package contains everything needed to stand up the AI Music Orchestrator using n8n plus local GPU-backed model services. It assumes:
- n8n reachable at `https://n8n.lothortech.com` with the provided Bearer token.
- Orchestration files mounted in n8n at `/data/orchestration` (host path `/opt/ai-music-orchestrator/orchestration`).
- GPU box `192.168.10.133` (`lothor-ROG`) running WSL2 + Docker + NVIDIA GPU (RTX 4090 12GB).

Quick start
-----------
1) Deploy GPU services on `lothor-ROG` (WSL2):
   - `cd docker && docker compose -f compose.models.yml up -d`
   - Validate GPU: `docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu24.04 nvidia-smi`
2) Load workflows via API (from this repo root):
   - `bash scripts/n8n_push_all.sh`
3) Run synthetic tests:
   - `bash scripts/test_health.sh`
   - `bash scripts/test_enqueue.sh`
   - `bash scripts/test_worker.sh`
4) Manage via n8n GUI after import; artifacts live under `/opt/ai-music-orchestrator/orchestration`.

Auth & tokens
-------------
- n8n API key lives at `/opt/codex/.env` as `n8n_api=<token>` (used for both GUI API calls and webhook bearer auth).
- Example: `curl -H "Authorization: Bearer $n8n_api" https://n8n.lothortech.com/webhook/health/generator`.
- Internal worker/webhook calls use `WORKER_TOKEN` (currently in `/opt/n8n/.env` and compose env); append `?token=$WORKER_TOKEN` or include in JSON body for `worker/run`.

Repository layout
-----------------
- `docs/architecture.md` — end-to-end design, queue/state schemas, lifecycle.
- `docs/network.md` — ports, firewall/ufw guidance, reachability checks.
- `docker/compose.models.yml` — GPU service stack (Ollama, SD, MusicGen, SVD, Chroma).
- `n8n/workflows/*.json` — workflow exports for n8n import/API.
- `scripts/` — helper CLI and test harnesses (shell + Python).
- `config/` — templates for env and queue/state defaults.

Secrets
-------
- Do NOT commit real API keys. The n8n API token is passed via env (`N8N_API_TOKEN`) or `.env.local` on your host only.
- Model downloads rely on public checkpoints; if you add licensed models, store auth tokens outside git.

Next steps
----------
- Run `docs/network.md` reachability checks.
- Hydrate memory hub with updated docs after deployment.***
