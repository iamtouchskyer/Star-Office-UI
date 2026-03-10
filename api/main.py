"""Vercel serverless function entry point for Star Office UI"""

import os
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

# Apply Vercel-specific patches
from vercel_adapter import patch_backend_for_vercel
patch_backend_for_vercel()

# Import Flask app from backend
from app import app

# Export handler for Vercel
handler = app