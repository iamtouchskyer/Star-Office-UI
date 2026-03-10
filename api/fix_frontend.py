#!/usr/bin/env python3
"""Fix frontend files for Vercel deployment"""

import os
import re
from pathlib import Path

def fix_version_timestamps():
    """Replace {{VERSION_TIMESTAMP}} with actual timestamp"""
    frontend_dir = Path(__file__).parent.parent / "frontend"
    timestamp = "20260310"
    
    # Process HTML files
    for html_file in frontend_dir.glob("*.html"):
        content = html_file.read_text(encoding='utf-8')
        content = content.replace('{{VERSION_TIMESTAMP}}', timestamp)
        html_file.write_text(content, encoding='utf-8')
        print(f"Fixed {html_file.name}")
    
    # Process JS files
    for js_file in frontend_dir.glob("*.js"):
        if js_file.exists():
            content = js_file.read_text(encoding='utf-8')
            content = content.replace('{{VERSION_TIMESTAMP}}', timestamp)
            js_file.write_text(content, encoding='utf-8')
            print(f"Fixed {js_file.name}")

if __name__ == "__main__":
    fix_version_timestamps()