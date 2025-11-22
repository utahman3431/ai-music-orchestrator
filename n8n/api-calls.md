Uploading workflows via API
===========================

Set:
- `N8N_API_TOKEN` (from /opt/codex/.env)
- `N8N_API_URL` (default `https://n8n.lothortech.com/rest`)

Create workflow (example for Queue - Add Job):
```bash
curl -sS -X POST "${N8N_API_URL:-https://n8n.lothortech.com/rest}/workflows" \
  -H "Authorization: Bearer ${N8N_API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data-binary @n8n/workflows/queue-add.json
```

Update workflow:
```bash
curl -sS -X PATCH "${N8N_API_URL}/workflows/<id>" \
  -H "Authorization: Bearer ${N8N_API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data-binary @n8n/workflows/queue-add.json
```

List workflows:
```bash
curl -sS -H "Authorization: Bearer ${N8N_API_TOKEN}" \
  "${N8N_API_URL}/workflows" | jq '.data[] | {id,name,active}'
```

Enqueue job:
```bash
curl -sS -X POST "https://n8n.lothortech.com/webhook/queue/add" \
  -H "Authorization: Bearer ${N8N_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"type":"audio","params":{"prompt":"lofi beat","duration":4}}' | jq .
```

Run worker once:
```bash
curl -sS -X POST "https://n8n.lothortech.com/webhook/worker/run" \
  -H "Authorization: Bearer ${N8N_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"worker":"gpu-worker-1"}' | jq .
```

Health probes:
```bash
curl -sS -H "Authorization: Bearer ${N8N_API_TOKEN}" https://n8n.lothortech.com/webhook/health/generator | jq .
```
