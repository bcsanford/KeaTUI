import os
import json
from config import SETTINGS_FILE, save_settings

def use_local_or_remote_api():
    print("--- KeaTUI Mode Selection ---")
    print("1. 🌐 Connect to remote Kea server")
    print("2. 🖥️  Use local Kea server")
    mode = input("Select mode [1-2]: ")

    if mode.strip() == "1":
        url = input("Enter remote API URL (e.g., http://192.168.1.1:8000): ").strip()
        connection_mode = "remote"
    else:
        url = "http://localhost:8000"
        connection_mode = "local"

    save_settings({"api_url": url})
    return url, connection_mode
