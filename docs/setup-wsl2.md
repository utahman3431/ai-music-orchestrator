WSL2 GPU Setup (lothor-ROG)
============================

Prereqs
-------
- Windows 11 with WSL2 installed.
- NVIDIA GPU (RTX 4090 12GB) with latest Windows driver.
- Docker Desktop with WSL integration enabled (or Docker Engine inside WSL + nvidia-container-toolkit).

One-time install (inside WSL)
-----------------------------
```bash
sudo apt-get update
sudo apt-get install -y curl git ca-certificates gnupg lsb-release

# NVIDIA container runtime
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/libnvidia-container/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | sudo tee /etc/apt/sources.list.d/libnvidia-container.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker || true

# Verify GPU from WSL
docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu24.04 nvidia-smi
```

Model stack bring-up
--------------------
```bash
cd /path/to/ai-music-orchestrator/docker
docker compose -f compose.models.yml build    # first-time model images
docker compose -f compose.models.yml up -d
```

Model pulls
-----------
Ollama models (example):
```bash
curl -X POST http://localhost:11434/api/pull -d '{"model":"llama3:8b"}'
curl -X POST http://localhost:11434/api/pull -d '{"model":"nomic-embed-text"}'
```

Health checks (inside WSL)
--------------------------
```bash
curl -s http://localhost:11434/api/tags
curl -s http://localhost:8011/health
curl -s http://localhost:8012/health
curl -s http://localhost:8013/health
curl -s http://localhost:8018/api/v1/heartbeat
```

Firewall
--------
- If ufw enabled inside WSL: `sudo ufw allow 11434 8011 8012 8013 8018/tcp && sudo ufw reload`.
- If Windows Firewall blocks inbound, add inbound rules for those ports for the WSL virtual NIC.
- Palo Alto: allow inbound to 192.168.10.133 on 11434, 8011-8013, 8018 from n8n host segment.

Logs
----
```bash
docker ps
docker compose -f docker/compose.models.yml logs -f image-gen
docker compose -f docker/compose.models.yml logs -f audio-gen
docker compose -f docker/compose.models.yml logs -f video-gen
docker compose -f docker/compose.models.yml logs -f chroma
```

Notes
-----
- Services mount `/opt/ai-music-orchestrator/orchestration` (ensure host path exists and writable).
- If ports conflict, adjust `docker/compose.models.yml` and update n8n workflow env values accordingly.
