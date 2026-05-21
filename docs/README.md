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

On `projects-server`:

```bash
git clone https://github.com/JoshBubis/projects-hub.git ~/projects-hub
cd ~/projects-hub
python3 poller/poll.py
```

Cron (every 5 minutes):

```bash
*/5 * * * * cd /home/zjbird/projects-hub && /usr/bin/python3 poller/poll.py >> logs/poller.log 2>&1
```

View latest snapshot on the server:

```bash
cat ~/projects-hub/data/status.json
python3 -m http.server 8090 --directory ~/projects-hub/dashboard --bind 127.0.0.1
# then SSH tunnel: ssh -L 8090:127.0.0.1:8090 projects-tailscale
```

## Last updated

May 21, 2026
