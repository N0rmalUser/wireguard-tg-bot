from pathlib import Path

import toml

root_path = Path(__file__).parent.parent.resolve()

config = toml.load(root_path / "config.toml")

BOT_TOKEN: str = config["bot"]["token"]
ADMIN_CHAT_ID: int = config["bot"]["admin_chat_id"]

LOG_LEVEL = config["logging"]["level"]
EVENT_LEVEL = config["logging"]["event_level"]

DATA_PATH: Path = root_path / "data"
LOG_FILE: Path = DATA_PATH / "bot.log"
USERS_DB: Path = DATA_PATH / "users.db"
CONF_PATH: Path = DATA_PATH / "conf"
SERVER_CONFIG: Path = Path(config["server"]["config"]).resolve()

TEST: bool = config["server"]["test"]
SERVER_IP: str = config["server"]["public_ip"]
SERVER_PUBLIC_KEY: str = config["server"]["public_key"]
BUSY_PORTS: list[int] = config["server"]["busy_ports"]
WG_PORT: int = config["server"]["wg_port"]
INTERFACE: str = config["server"]["interface"]

DNS1: str = config["server"]["DNS"]["1"]
DNS2: str = config["server"]["DNS"]["2"]

MAX_CONFIGS: int = config["config"]["max"]

TIMEZONE: str = config["date"]["timezone"]
TIME_FORMAT: str = config["date"]["format"]
