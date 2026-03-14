#!/usr/bin/env python3
"""
Mirror local Star Office state to Vercel.

Polls the local Flask backend, diffs against last snapshot,
and pushes changes to Vercel's /api/sync endpoint in one request.

Usage:
    python vercel-agent-push.py

All config has sensible defaults. Override via env vars if needed:
    STAR_OFFICE_LOCAL_URL   (default: http://127.0.0.1:19000)
    STAR_OFFICE_VERCEL_URL  (default: https://touchskyer-ai-office.vercel.app)
    STAR_OFFICE_PASSWORD    (default: reads from local /assets/auth/status or "1234")
    STAR_OFFICE_INTERVAL    (default: 15)
"""

import hashlib
import json
import os
import time
from datetime import datetime

import requests

LOCAL_URL = os.environ.get("STAR_OFFICE_LOCAL_URL", "http://127.0.0.1:19000")
VERCEL_URL = os.environ.get("STAR_OFFICE_VERCEL_URL", "https://touchskyer-ai-office.vercel.app")
PASSWORD = os.environ.get("STAR_OFFICE_PASSWORD", "")
INTERVAL = int(os.environ.get("STAR_OFFICE_INTERVAL", "5"))

_last_hash = None


def get_password():
    """Try to read password from env or fall back to default"""
    if PASSWORD:
        return PASSWORD
    # Try reading from .env.local if it exists
    env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env.local")
    if os.path.exists(env_file):
        for line in open(env_file):
            if line.startswith("ASSET_DRAWER_PASS="):
                return line.split("=", 1)[1].strip().strip('"')
    return "1234"


def fetch_local():
    """Pull state + agents + memo from local Flask backend"""
    snapshot = {}
    try:
        r = requests.get(f"{LOCAL_URL}/status", timeout=5)
        if r.ok:
            snapshot["state"] = r.json()
    except Exception:
        pass

    try:
        r = requests.get(f"{LOCAL_URL}/agents", timeout=5)
        if r.ok:
            snapshot["agents"] = r.json()
    except Exception:
        pass

    try:
        r = requests.get(f"{LOCAL_URL}/yesterday-memo", timeout=5)
        if r.ok:
            data = r.json()
            if data.get("success") and data.get("memo"):
                snapshot["memo"] = data
    except Exception:
        pass

    return snapshot


def snapshot_hash(snapshot):
    """Deterministic hash of snapshot for change detection"""
    return hashlib.md5(json.dumps(snapshot, sort_keys=True, default=str).encode()).hexdigest()


def sync_to_vercel(snapshot, password):
    """Push snapshot to Vercel /api/sync"""
    try:
        resp = requests.post(
            f"{VERCEL_URL}/api/sync",
            json={**snapshot, "password": password},
            timeout=15,
        )
        if resp.ok:
            data = resp.json()
            agents_count = data.get("synced", {}).get("agents", 0)
            print(f"✅ [{datetime.now():%H:%M:%S}] synced | "
                  f"state={snapshot.get('state', {}).get('state', '?')} | "
                  f"agents={agents_count}")
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

    print(f"🏢 Star Office Sync")
    print(f"   Local:  {LOCAL_URL}")
    print(f"   Vercel: {VERCEL_URL}")
    print(f"   Interval: {INTERVAL}s")
    print()

    while True:
        snapshot = fetch_local()
        if not snapshot:
            print(f"⏳ [{datetime.now():%H:%M:%S}] local backend not reachable, retrying...")
            time.sleep(INTERVAL)
            continue

        h = snapshot_hash(snapshot)
        if h != _last_hash:
            if sync_to_vercel(snapshot, password):
                _last_hash = h
        else:
            # Silent skip — no change
            pass

        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
