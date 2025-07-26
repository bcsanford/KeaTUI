import os
import subprocess

def is_kea_installed():
    return os.path.exists("/etc/kea/kea-dhcp4.conf")

def check_or_install_kea():
    if is_kea_installed():
        return

    print("📦 Kea DHCP not found. Do you want to install it? [y/N]")
    choice = input().lower()
    if choice == "y":
        try:
            subprocess.run([
                "apt", "install", "-y",
                "software-properties-common"
            ], check=True)
            subprocess.run([
                "add-apt-repository", "ppa:isc/kea"])
            subprocess.run(["apt", "update"], check=True)
            subprocess.run(["apt", "install", "-y",
                "kea-dhcp4-server", "kea-ctrl-agent"], check=True)
        except subprocess.CalledProcessError as e:
            print("❌ Failed to install Kea packages:", e)
