#!/usr/bin/env python3
"""
Update OpenRouter API Key
Run this script after getting your new API key from openrouter.ai/keys
"""

import os
import sys

def update_api_key():
    print("🔑 OpenRouter API Key Updater")
    print("=" * 50)
    print()
    
    # Get new API key
    print("Please paste your new OpenRouter API key:")
    print("(Get it from: https://openrouter.ai/keys)")
    print()
    
    new_key = input("API Key: ").strip()
    
    if not new_key:
        print("❌ No key provided. Exiting.")
        return
    
    if not new_key.startswith("sk-or-v1-"):
        print("⚠️  Warning: OpenRouter keys usually start with 'sk-or-v1-'")
        proceed = input("Continue anyway? (y/n): ").strip().lower()
        if proceed != 'y':
            return
    
    # Update .env file
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    
    try:
        # Read current .env
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        # Update API key line
        updated = False
        new_lines = []
        for line in lines:
            if line.startswith("OPENROUTER_API_KEY="):
                new_lines.append(f"OPENROUTER_API_KEY={new_key}\n")
                updated = True
            else:
                new_lines.append(line)
        
        # Write back
        with open(env_path, 'w') as f:
            f.writelines(new_lines)
        
        if updated:
            print()
            print("✅ API key updated successfully!")
            print()
            print("📋 Next steps:")
            print("1. If using Docker: docker-compose restart")
            print("2. If using local: restart python app.py")
            print()
            print("🧪 Test with: curl http://localhost:5000/health")
        else:
            print("❌ Could not find OPENROUTER_API_KEY line in .env")
    
    except Exception as e:
        print(f"❌ Error updating .env: {e}")

if __name__ == "__main__":
    update_api_key()
