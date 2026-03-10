"""Vercel serverless function entry point for Star Office UI"""

import os
import sys
import json
from pathlib import Path

# Add backend directory to Python path
current_dir = Path(__file__).parent
backend_dir = current_dir.parent / "backend"
sys.path.insert(0, str(backend_dir))

# Simple Vercel environment handling
os.environ["FLASK_ENV"] = "production"
os.environ["STAR_OFFICE_MODE"] = "vercel"

# Import and patch app
try:
    import app
    
    # Override paths for Vercel environment
    import tempfile
    temp_dir = tempfile.gettempdir()
    
    app.STATE_FILE = os.path.join(temp_dir, "state.json")
    app.AGENTS_STATE_FILE = os.path.join(temp_dir, "agents-state.json") 
    app.WORKSPACE_DIR = temp_dir
    app.MEMORY_DIR = os.path.join(temp_dir, "memory")
    app.JOIN_KEYS_FILE = os.path.join(temp_dir, "join-keys.json")
    
    # Create required directories
    os.makedirs(app.MEMORY_DIR, exist_ok=True)
    
    # Initialize default state if not exists
    if not os.path.exists(app.STATE_FILE):
        default_state = {
            "status": os.environ.get("STAR_OFFICE_STATUS", "idle"),
            "message": os.environ.get("STAR_OFFICE_MESSAGE", "AI助手办公室已上线！"),
            "timestamp": "2026-03-10T08:00:00.000Z"
        }
        with open(app.STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_state, f, ensure_ascii=False, indent=2)
    
    if not os.path.exists(app.AGENTS_STATE_FILE):
        with open(app.AGENTS_STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f)
            
    if not os.path.exists(app.JOIN_KEYS_FILE):
        # Default join keys for demo
        default_keys = {
            "ocj_vercel_demo": {
                "maxConcurrent": 3,
                "description": "Demo key for Vercel deployment"
            }
        }
        with open(app.JOIN_KEYS_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_keys, f, ensure_ascii=False, indent=2)
    
    # Export the Flask app
    handler = app.app
    
except Exception as e:
    # Fallback error handler
    from flask import Flask, jsonify
    handler = Flask(__name__)
    
    @handler.route('/', defaults={'path': ''})
    @handler.route('/<path:path>')
    def catch_all(path):
        return jsonify({
            "error": "Failed to initialize app",
            "details": str(e),
            "path": path
        }), 500