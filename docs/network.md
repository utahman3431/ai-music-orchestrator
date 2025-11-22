Network & Ports
===============

Targets
-------
- GPU host: `192.168.10.133` (`lothor-ROG`)
- n8n host: uses `/data/orchestration` bind mount; reaches GPU services over LAN

Planned ports (GPU host)
------------------------
- 11434: Ollama (LLM + embeddings)
- 8011: Image generator (Stable Diffusion)
- 8012: Audio generator (MusicGen)
- 8013: Video generator (SVD / ModelScope)
- 8018: Chroma DB (v2 API)

Check existing listeners (GPU host)
-----------------------------------
Run inside WSL2:
```
ss -tulpn
```
Adjust ports in `docker/compose.models.yml` if any conflict.

Firewall (WSL2)
---------------
WSL2 does not enforce ufw by default. If ufw is enabled inside WSL2:
```
sudo ufw allow 11434/tcp
sudo ufw allow 8011:8013/tcp
sudo ufw allow 8018/tcp
sudo ufw reload
sudo ufw status
```
If Windows Firewall blocks inbound, add rules for those ports targeting the WSL virtual NIC. Palo Alto rules can be added for 192.168.10.133 inbound on these ports if needed.

Connectivity tests (from n8n host)
----------------------------------
```
curl -I http://192.168.10.133:11434
curl -I http://192.168.10.133:8011/health
curl -I http://192.168.10.133:8012/health
curl -I http://192.168.10.133:8013/health
curl -I http://192.168.10.133:8018/api/v2/heartbeat
```

Inside GPU host to confirm services
-----------------------------------
```
curl -s http://localhost:11434/api/tags
curl -s http://localhost:8011/health
curl -s http://localhost:8012/health
curl -s http://localhost:8013/health
curl -s http://localhost:8018/api/v2/heartbeat
```

Port overrides
--------------
If conflicts arise, edit `docker/compose.models.yml` service `ports` section and mirror the change in `docs/architecture.md` and n8n workflow environment variables (service URLs).***
