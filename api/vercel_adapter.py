"""Vercel adapter for Star Office UI - handles serverless limitations"""

import os
import json
import tempfile
from pathlib import Path

# In Vercel, we can't write to the filesystem persistently
# So we'll use environment variables or return mock data for demo purposes

def get_temp_state_file():
    """Get a temporary state file path for this request"""
    temp_dir = tempfile.gettempdir()
    return os.path.join(temp_dir, "star-office-state.json")

def get_temp_agents_file():
    """Get a temporary agents state file path for this request"""
    temp_dir = tempfile.gettempdir()
    return os.path.join(temp_dir, "star-office-agents.json")

def init_temp_files():
    """Initialize temporary files with default or env-based state"""
    state_file = get_temp_state_file()
    agents_file = get_temp_agents_file()
    
    # Default state
    default_state = {
        "status": os.environ.get("STAR_OFFICE_STATUS", "idle"),
        "message": os.environ.get("STAR_OFFICE_MESSAGE", "Deployed on Vercel! 🚀"),
        "timestamp": "2026-03-10T08:00:00.000Z"
    }
    
    # Default agents state
    default_agents = {}
    
    # Write defaults to temp files
    with open(state_file, 'w', encoding='utf-8') as f:
        json.dump(default_state, f, ensure_ascii=False, indent=2)
        
    with open(agents_file, 'w', encoding='utf-8') as f:
        json.dump(default_agents, f, ensure_ascii=False, indent=2)
    
    return state_file, agents_file

# Monkey patch the backend paths for Vercel environment
def patch_backend_for_vercel():
    """Patch backend module to use temporary files in Vercel"""
    import backend.app as app_module
    
    state_file, agents_file = init_temp_files()
    
    # Override file paths
    app_module.STATE_FILE = state_file
    app_module.AGENTS_STATE_FILE = agents_file
    
    # Disable features that don't work in serverless
    app_module.WORKSPACE_DIR = "/tmp"
    app_module.MEMORY_DIR = "/tmp/memory"
    
    # Create temp memory dir
    os.makedirs("/tmp/memory", exist_ok=True)
    
    print(f"Patched for Vercel - State: {state_file}, Agents: {agents_file}")