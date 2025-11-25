#!/usr/bin/env bash
set -euo pipefail

API="${N8N_API_URL:-https://n8n.lothortech.com}"
TOKEN="${N8N_API_TOKEN:?set N8N_API_TOKEN}"

enqueue() {
  local type="$1"
  local payload="$2"
  echo "Enqueue ${type}"
  curl -sS -X POST "${API}/webhook/queue/add" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json" \
    -d "${payload}" | jq .
}

enqueue "audio" '{"type":"audio","params":{"prompt":"lofi beat with gentle piano","duration":4}}'
enqueue "image" '{"type":"image","params":{"prompt":"sunset over mountains, vibrant, 4k","height":512,"width":512}}'
enqueue "text"  '{"type":"text","params":{"prompt":"Summarize the generated track mood."}}'
