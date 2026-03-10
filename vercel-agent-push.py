#!/usr/bin/env python3
"""Push agent status to Vercel-deployed Star Office UI"""

import requests
import json
import sys
import os
from datetime import datetime

def push_agent_status(vercel_url, agent_id, status, message, join_key="ocj_starteam01"):
    """
    Push agent status to Vercel instance
    
    Args:
        vercel_url: Your Vercel deployment URL (e.g., https://your-app.vercel.app)
        agent_id: Your agent ID
        status: Status (idle, working, syncing, error)
        message: Status message
        join_key: Join key for authentication
    """
    
    # Join the office
    join_url = f"{vercel_url}/agents/join"
    join_data = {
        "agentId": agent_id,
        "joinKey": join_key
    }
    
    try:
        resp = requests.post(join_url, json=join_data)
        if resp.status_code != 200:
            print(f"Failed to join: {resp.text}")
            return False
    except Exception as e:
        print(f"Error joining: {e}")
        return False
    
    # Push status
    push_url = f"{vercel_url}/agents/push"
    push_data = {
        "agentId": agent_id,
        "joinKey": join_key,
        "status": status,
        "message": message
    }
    
    try:
        resp = requests.post(push_url, json=push_data)
        if resp.status_code == 200:
            print(f"✅ Status pushed: {agent_id} -> {status}: {message}")
            return True
        else:
            print(f"❌ Failed to push: {resp.text}")
            return False
    except Exception as e:
        print(f"❌ Error pushing: {e}")
        return False

if __name__ == "__main__":
    # Example usage
    VERCEL_URL = os.environ.get("STAR_OFFICE_VERCEL_URL", "https://your-star-office.vercel.app")
    
    # You can call this from your agents
    push_agent_status(
        vercel_url=VERCEL_URL,
        agent_id="main-lobster",
        status="working",
        message="正在部署Star Office到Vercel"
    )