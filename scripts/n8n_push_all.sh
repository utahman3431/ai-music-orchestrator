#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API="${N8N_API_URL:-https://n8n.lothortech.com/api/v1}"
TOKEN="${N8N_API_TOKEN:?set N8N_API_TOKEN (API key from /opt/codex/.env)}"

push_workflow() {
  local file="$1"
  echo "Pushing ${file}..."
  jq 'del(.active, .tags)' "${file}" | \
  curl -sS -X POST "${API}/workflows" \
    -H "X-N8N-API-KEY: ${TOKEN}" \
    -H "Content-Type: application/json" \
    --data-binary @- | jq '{id,name,active}'
}

for wf in "${ROOT}"/n8n/workflows/*.json; do
  push_workflow "${wf}"
done

echo "Listing workflows (name, id, active):"
curl -sS -H "X-N8N-API-KEY: ${TOKEN}" "${API}/workflows" | jq '.data[] | {id,name,active}'

echo "Workflows pushed."
