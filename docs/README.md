# Projects Hub Documentation

Read-only uptime dashboard for Josh's production apps.

## Monitored apps

| App | Health URL | Notes |
|-----|------------|-------|
| Catamist | `https://catamist.com/health` | Public JSON health check |
| HackyChat | `https://api.hackychat.com/health` | DB + Redis status |
| Relayra | `https://relayra.com/up` | Rails boot check (lite) |

Optional deep check: Relayra `https://relayra.com/diagnostics.json?token=…` (set `RELAYRA_DIAGNOSTICS_TOKEN` in env).

## Usage

```bash
cd /Users/jbair/Projects/projects-hub
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python poller/poll.py
python -m http.server 8090 --directory dashboard
```

Open `http://localhost:8090` — the page loads `../data/status.json` via fetch (run poller first).

## Server cron (optional)

```bash
*/5 * * * * cd ~/projects-hub && .venv/bin/python poller/poll.py >> logs/poller.log 2>&1
```

## Last updated

May 21, 2026
