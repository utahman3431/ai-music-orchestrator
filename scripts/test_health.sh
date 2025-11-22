#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API="${N8N_API_URL:-https://n8n.lothortech.com}"
TOKEN="${N8N_API_TOKEN:?set N8N_API_TOKEN}"

echo "Health: generator"
curl -sS -H "Authorization: Bearer ${TOKEN}" "${API}/webhook/health/generator" | jq .

echo "Health: filesystem"
curl -sS -H "Authorization: Bearer ${TOKEN}" "${API}/webhook/health/fs" | jq .

echo "Health: queue"
curl -sS -H "Authorization: Bearer ${TOKEN}" "${API}/webhook/health/queue" | jq .
