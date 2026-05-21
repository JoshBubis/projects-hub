#!/usr/bin/env python3
"""Poll configured app health endpoints and write data/status.json."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "apps.json"
STATUS_PATH = ROOT / "data" / "status.json"


def load_config() -> dict:
    with CONFIG_PATH.open() as f:
        return json.load(f)


def check_url(url: str, timeout: int) -> dict:
    started = datetime.now(timezone.utc)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ProjectsHub/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(8192).decode("utf-8", errors="replace")
            ok = 200 <= resp.status < 300
            summary = body[:200]
            try:
                parsed = json.loads(body)
                summary = parsed.get("status") or parsed.get("overall_status") or summary
            except json.JSONDecodeError:
                pass
            return {
                "ok": ok,
                "http_status": resp.status,
                "summary": str(summary),
                "latency_ms": int((datetime.now(timezone.utc) - started).total_seconds() * 1000),
            }
    except urllib.error.HTTPError as e:
        return {
            "ok": False,
            "http_status": e.code,
            "summary": str(e.reason),
            "latency_ms": int((datetime.now(timezone.utc) - started).total_seconds() * 1000),
        }
    except Exception as e:
        return {
            "ok": False,
            "http_status": None,
            "summary": str(e),
            "latency_ms": int((datetime.now(timezone.utc) - started).total_seconds() * 1000),
        }


def main() -> int:
    config = load_config()
    timeout = int(config.get("poll_timeout_seconds", 15))
    checked_at = datetime.now(timezone.utc).isoformat()

    results = []
    for app in config["apps"]:
        result = check_url(app["url"], timeout)
        results.append({**app, **result, "checked_at": checked_at})

    relayra_token = os.environ.get("RELAYRA_DIAGNOSTICS_TOKEN")
    if relayra_token:
        deep_url = f"https://relayra.com/diagnostics.json?token={relayra_token}"
        deep = check_url(deep_url, timeout)
        results.append(
            {
                "id": "relayra-diagnostics",
                "name": "Relayra (deep)",
                "url": "https://relayra.com/diagnostics.json",
                "admin_url": "https://relayra.com/admin/system",
                **deep,
                "checked_at": checked_at,
            }
        )

    payload = {
        "checked_at": checked_at,
        "overall_ok": all(r["ok"] for r in results),
        "apps": results,
    }

    STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATUS_PATH.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"Wrote {STATUS_PATH} ({len(results)} checks, overall_ok={payload['overall_ok']})")
    return 0 if payload["overall_ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
