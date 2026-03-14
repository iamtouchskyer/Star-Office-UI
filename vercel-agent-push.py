#!/usr/bin/env python3
"""Push agent status to Vercel-deployed Star Office UI (Upstash Redis backend)"""

import requests
import json
import sys
import os
import time
from datetime import datetime

STATE_FILE_CANDIDATES = [
    os.path.join(os.path.expanduser("~"), ".openclaw", "workspace", "Star-Office-UI", "state.json"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json"),
]


def read_local_state():
    """Read state.json from local OpenClaw workspace"""
    for path in STATE_FILE_CANDIDATES:
        if os.path.exists(path):
            try:
                with open(path) as f:
                    data = json.load(f)
                return data.get("state", "idle"), data.get("detail", "待命中")
            except Exception:
                continue
    return "idle", "待命中"


def push_once(vercel_url, agent_id, join_key):
    """Read local state and push to Vercel"""
    state, detail = read_local_state()

    resp = requests.post(
        f"{vercel_url}/agent-push",
        json={
            "agentId": agent_id,
            "joinKey": join_key,
            "state": state,
            "detail": detail,
        },
        timeout=10,
    )
    if resp.status_code == 200:
        print(f"✅ [{datetime.now():%H:%M:%S}] {state}: {detail}")
        return True
    elif resp.status_code == 404:
        # Agent not registered yet, join first
        print("Agent not found, joining...")
        join_resp = requests.post(
            f"{vercel_url}/join-agent",
            json={
                "name": agent_id,
                "joinKey": join_key,
                "state": state,
                "detail": detail,
            },
            timeout=10,
        )
        if join_resp.status_code == 200:
            data = join_resp.json()
            print(f"✅ Joined as {data.get('agentId')}")
            return data.get("agentId")
        else:
            print(f"❌ Join failed: {join_resp.text}")
            return False
    else:
        print(f"❌ Push failed [{resp.status_code}]: {resp.text}")
        return False


def main():
    vercel_url = os.environ.get("STAR_OFFICE_VERCEL_URL", "https://touchskyer-ai-office.vercel.app")
    agent_id = os.environ.get("STAR_OFFICE_AGENT_ID", "main-touchskyer")
    join_key = os.environ.get("STAR_OFFICE_JOIN_KEY", "ocj_starteam01")
    interval = int(os.environ.get("STAR_OFFICE_PUSH_INTERVAL", "15"))

    print(f"🏢 Star Office Push → {vercel_url}")
    print(f"   Agent: {agent_id} | Interval: {interval}s")

    # First push might return a new agentId from join
    result = push_once(vercel_url, agent_id, join_key)
    if isinstance(result, str):
        agent_id = result  # Use the server-assigned agentId

    while True:
        time.sleep(interval)
        push_once(vercel_url, agent_id, join_key)


if __name__ == "__main__":
    main()
