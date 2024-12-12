import logging
import subprocess
import tempfile

from app.config import (
    CONF_PATH,
    DNS1,
    DNS2,
    INTERFACE,
    SERVER_CONFIG,
    SERVER_IP,
    SERVER_PUBLIC_KEY,
    TEST,
    WG_PORT,
)
from app.database.config import ConfigDatabase
from app.misc.texts import Err


def generate_wireguard_keys():
    private_key = subprocess.run(["wg", "genkey"], capture_output=True, text=True).stdout.strip()
    public_key = subprocess.run(["wg", "pubkey"], input=private_key, capture_output=True, text=True).stdout.strip()
    return private_key, public_key


def generate_wg_psk() -> str | None:
    try:
        psk = subprocess.run(["wg", "genpsk"], capture_output=True, text=True, check=True).stdout.strip()
        return psk
    except subprocess.CalledProcessError as e:
        logging.error(Err.generate_PSK.format(e))
        return None


def sync_wireguard_config() -> None:
    try:
        with tempfile.NamedTemporaryFile("w+") as temp_file:
            subprocess.run(["wg-quick", "strip", INTERFACE], stdout=temp_file, check=True)
            temp_file.seek(0)
            subprocess.run(["wg", "syncconf", INTERFACE, temp_file.name], check=True)

    except subprocess.CalledProcessError as e:
        logging.error(Err.subprocess.format(e))


def server_config(config: ConfigDatabase) -> str:
    return (
        "[Peer]\n"
        f"PublicKey = {config.public_key}\n"
        f"PresharedKey = {config.preshared_key}\n"
        f"AllowedIPs = {config.ip}/32\n\n"
    )


def client_config(config: ConfigDatabase) -> str:
    return (
        "[Interface]\n"
        f"PrivateKey = {config.private_key}\n"
        f"Address = {config.ip}/32\n"
        f"DNS = {DNS1}, {DNS2}\n\n"
        "[Peer]\n"
        f"PublicKey = {SERVER_PUBLIC_KEY}\n"
        f"PresharedKey = {config.preshared_key}\n"
        f"Endpoint = {SERVER_IP}:{WG_PORT}\n"
        "AllowedIPs = 0.0.0.0/0, ::/0\n"
    )


def peers_info():
    result = subprocess.run(["wg", "show"], capture_output=True, text=True)
    if result.returncode != 0:
        logging.error(Err.subprocess.format(result.stderr))
        return []
    output = result.stdout + "\npeer: None"
    info = []
    data = {}

    for line in output.splitlines():
        line = line.strip()
        if line.startswith("peer:"):
            if data:
                info.append(data)
            data = {"peer": line.split(":")[1].strip()}
        elif line.startswith("endpoint:"):
            data["endpoint"] = line.split(": ", 1)[1].strip()
        elif line.startswith("allowed ips:"):
            data["allowed_ips"] = line.split(": ", 1)[1].strip()
        elif line.startswith("latest handshake:"):
            data["latest_handshake"] = line.split(": ", 1)[1].strip()
        elif line.startswith("transfer:"):
            data["transfer"] = line.split(": ", 1)[1].strip()
    return info

def create_config(config: ConfigDatabase) -> None:
    private_key, public_key = generate_wireguard_keys()
    config.private_key = private_key
    config.public_key = public_key
    config.preshared_key = generate_wg_psk()

    user_path = CONF_PATH / str(config.user_id)
    user_path.mkdir(parents=True, exist_ok=True)
    with open(user_path / f"{config.ip}.conf", "w") as file:
        file.write(client_config(config) + "\n")


def append_to_server_config(config: ConfigDatabase) -> None:
    with open(SERVER_CONFIG, "a") as file:
        file.write(server_config(config))
    if not TEST:
        sync_wireguard_config()
