from ui import launch_ui
from config import init_config
from api import use_local_or_remote_api
from installer import check_or_install_kea

def main():
    init_config()
    api_url, mode = use_local_or_remote_api()
    if mode == "local":
        check_or_install_kea()
    launch_ui(api_url)

if __name__ == "__main__":
    main()
