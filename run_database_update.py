#!/usr/bin/env python3
"""
Simple script to update the database on Render.
Run this on the Render platform to fix the role name typo.
"""

import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Run the database update"""
    try:
        from update_database_on_render import main as update_main
        update_main()
    except Exception as e:
        print(f"❌ Error running database update: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
