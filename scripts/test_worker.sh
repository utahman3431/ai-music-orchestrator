#!/usr/bin/env bash
set -euo pipefail

API="${N8N_API_URL:-https://n8n.lothortech.com}"
TOKEN="${N8N_API_TOKEN:?set N8N_API_TOKEN}"
WORKER_TOKEN="${WORKER_TOKEN:?set WORKER_TOKEN}"

for i in {1..3}; do
  echo "Worker cycle ${i}"
  curl -sS -X POST "${API}/webhook/worker/run" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json" \
    -d "{\"worker\":\"test-runner\",\"token\":\"${WORKER_TOKEN}\"}" | jq .
done
