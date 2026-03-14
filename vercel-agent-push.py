#!/usr/bin/env python3
"""
Mirror local agent activity to Vercel Star Office.

Detects agent activity by monitoring session file mtimes under
~/.openclaw/agents/*/sessions/*.jsonl — no agent cooperation needed.

Usage:
    python vercel-agent-push.py
"""

import glob
import hashlib
import json
import os
import time
from datetime import datetime, timezone

import requests

VERCEL_URL = os.environ.get("STAR_OFFICE_VERCEL_URL", "https://touchskyer-ai-office.vercel.app")
PASSWORD = os.environ.get("STAR_OFFICE_PASSWORD", "")
INTERVAL = int(os.environ.get("STAR_OFFICE_INTERVAL", "5"))
AGENTS_DIR = os.environ.get("OPENCLAW_AGENTS_DIR",
                            os.path.join(os.path.expanduser("~"), ".openclaw", "agents"))

# If a session file was modified within this many seconds, agent is "active"
ACTIVE_THRESHOLD = 30

_last_hash = None


def get_password():
    if PASSWORD:
        return PASSWORD
    env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env.local")
    if os.path.exists(env_file):
        for line in open(env_file):
            if line.startswith("ASSET_DRAWER_PASS="):
                return line.split("=", 1)[1].strip().strip('"')
    return "1234"


def detect_agents():
    """Scan ~/.openclaw/agents/ and detect activity from session file mtimes."""
    agents = []
    now = time.time()

    for agent_name in sorted(os.listdir(AGENTS_DIR)):
        sessions_dir = os.path.join(AGENTS_DIR, agent_name, "sessions")
        if not os.path.isdir(sessions_dir):
            continue

        jsonl_files = glob.glob(os.path.join(sessions_dir, "*.jsonl"))
        if not jsonl_files:
            continue

        latest = max(jsonl_files, key=os.path.getmtime)
        mtime = os.path.getmtime(latest)
        age = now - mtime
        active = age < ACTIVE_THRESHOLD

        state = "writing" if active else "idle"
        detail = "工作中" if active else "待命中"

        # Try to read last message for a better detail
        if active:
            try:
                with open(latest, "rb") as f:
                    # Read last line efficiently
                    f.seek(0, 2)
                    pos = f.tell()
                    buf = b""
                    while pos > 0:
                        pos = max(pos - 1024, 0)
                        f.seek(pos)
                        buf = f.read(f.tell() - pos if pos == 0 else 1024) + buf
                        lines = buf.split(b"\n")
                        if len(lines) > 1:
                            break
                    last_line = lines[-1] or (lines[-2] if len(lines) > 1 else b"")
                    if last_line:
                        msg = json.loads(last_line)
                        role = msg.get("message", {}).get("role", "")
                        if role == "assistant":
                            state = "writing"
                            detail = "正在回复"
                        elif role == "user":
                            state = "researching"
                            detail = "收到消息，思考中"
            except Exception:
                pass

        agents.append({
            "agentId": f"local-{agent_name}",
            "name": agent_name,
            "isMain": agent_name == "main",
            "state": state,
            "detail": detail,
            "updated_at": datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat(),
            "area": "writing" if active else "breakroom",
            "source": "local",
            "authStatus": "approved",
            "lastPushAt": datetime.now(tz=timezone.utc).isoformat(),
            "avatar": f"guest_role_{hash(agent_name) % 6 + 1}",
        })

    return agents


def build_snapshot(agents):
    """Build sync snapshot from detected agents."""
    # Main state = main agent's state, or first active agent, or idle
    main_agent = next((a for a in agents if a["isMain"]), None)
    any_active = next((a for a in agents if a["state"] != "idle"), None)
    ref = main_agent or any_active

    state = {
        "state": ref["state"] if ref else "idle",
        "detail": ref["detail"] if ref else "所有助手待命中",
        "progress": 0,
        "updated_at": datetime.now(tz=timezone.utc).isoformat(),
        "ttl_seconds": 300,
    }

    return {"state": state, "agents": agents}


def snapshot_hash(snapshot):
    # Only hash the state-relevant fields, ignore timestamps
    key_data = {
        "main_state": snapshot["state"]["state"],
        "agents": [(a["agentId"], a["state"]) for a in snapshot["agents"]],
    }
    return hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()


def sync_to_vercel(snapshot, password):
    try:
        resp = requests.post(
            f"{VERCEL_URL}/api/sync",
            json={**snapshot, "password": password},
            timeout=15,
        )
        if resp.ok:
            active = [a["name"] for a in snapshot["agents"] if a["state"] != "idle"]
            idle = [a["name"] for a in snapshot["agents"] if a["state"] == "idle"]
            print(f"✅ [{datetime.now():%H:%M:%S}] "
                  f"active=[{', '.join(active) or 'none'}] "
                  f"idle=[{', '.join(idle)}]")
            return True
        else:
            print(f"❌ [{datetime.now():%H:%M:%S}] sync failed [{resp.status_code}]: {resp.text}")
            return False
    except Exception as e:
        print(f"❌ [{datetime.now():%H:%M:%S}] sync error: {e}")
        return False


def main():
    global _last_hash
    password = get_password()

    print(f"🏢 Star Office Sync (passive detection)")
    print(f"   Agents dir: {AGENTS_DIR}")
    print(f"   Vercel:     {VERCEL_URL}")
    print(f"   Interval:   {INTERVAL}s | Active threshold: {ACTIVE_THRESHOLD}s")
    print()

    while True:
        agents = detect_agents()
        if not agents:
            print(f"⏳ [{datetime.now():%H:%M:%S}] no agents found in {AGENTS_DIR}")
            time.sleep(INTERVAL)
            continue

        snapshot = build_snapshot(agents)
        h = snapshot_hash(snapshot)
        if h != _last_hash:
            if sync_to_vercel(snapshot, password):
                _last_hash = h

        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
