import logging
import sqlite3
from functools import wraps
from pathlib import Path

from app.config import USERS_DB
from app.database.user import UserDatabase
from app.misc.texts import Err
from app.wireguard import peers_info


def sql_kit(db: Path | str = ":memory:"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            conn = sqlite3.connect(db)
            try:
                result = func(*args, **kwargs, cursor=conn.cursor())
                conn.commit()
                return result
            finally:
                conn.close()

        return wrapper

    return decorator


@sql_kit(USERS_DB)
def user_db_init(cursor: sqlite3.Cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user (
            user_id INTEGER PRIMARY KEY,
            allowed BOOLEAN DEFAULT FALSE,
            username TEXT,
            fullname TEXT,
                        
            topic_id INTEGER,
            start_date TEXT,            
            tracking BOOLEAN DEFAULT false,
            
            blocked BOOLEAN DEFAULT false,
            banned BOOLEAN DEFAULT false
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS config (
            ip TEXT PRIMARY KEY,
            user_id INTEGER,
            name TEXT,
            creation_date TEXT,
            private_key TEXT,
            public_key TEXT,
            preshared_key TEXT,
            
            FOREIGN KEY (user_id) REFERENCES user(user_id)
        );
        """
    )

    cursor.execute(
        """
            CREATE TABLE IF NOT EXISTS port (
                num INTEGER PRIMARY KEY,
                ip TEXT,
                creation_date TEXT,
                
                FOREIGN KEY (ip) REFERENCES config(ip)
            );
            """
    )


try:
    user_db_init()
    logging.info("База данных инициализирована")
except Exception as e:
    logging.error(f"Ошибка в инициализации базы данных: {e}")


async def user_info(user: UserDatabase):
    text = (
        f"Информация о пользователе:\n"
        f"<code>username:   </code> <code>{user.username}</code>\n"
        f"<code>Полное имя: </code> <code>{user.fullname}</code>\n"
        f"<code>Регистрация:</code> <code>{user.start_date}</code>\n\n"
        f"{"Заблокировал бота\n" if user.blocked else None}"
        f"{"Забанен\n" if user.banned else None}"
        f"{"Отслеживается" if user.tracking else "Не отслеживается"}\n"
        f"Конфигов: {len(user.configs)}"
    )
    peers_data = peers_info()
    for peer in peers_data:
        key = peer["peer"]
        endpoint = peer["endpoint"]
        handshake = peer["latest_handshake"]
        transfer = peer["transfer"]




@sql_kit(USERS_DB)
def all_user_ids(cursor: sqlite3.Cursor) -> list:
    cursor.execute("SELECT user_id FROM user")
    return [row[0] for row in cursor.fetchall()]


@sql_kit(USERS_DB)
def get_all_users_info(cursor: sqlite3.Cursor) -> str:
    users_count = len(all_user_ids())

    cursor.execute("SELECT COUNT(*) FROM user WHERE blocked = 1")
    blocked_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM user WHERE banned = 1")
    banned_count = cursor.fetchone()[0]

    result = (
        f"<code>Пользователей:     </code> <code>{users_count}</code>\n\n"
        f"<code>Заблокировали бота:</code> <code>{blocked_count}</code>\n"
        f"<code>Забанено:          </code> <code>{banned_count}</code>"
    )
    return result


async def tracking_manage(tracking: bool) -> None:
    for user_id in all_user_ids():
        UserDatabase(user_id).tracking = tracking


async def get_tracked_users() -> list:
    user_ids = all_user_ids()
    tracked_users = []
    for user_id in user_ids:
        if UserDatabase(user_id).tracking:
            tracked_users.append(f"`{user_id}`")
    return tracked_users


@sql_kit(USERS_DB)
def get_max_ip(cursor: sqlite3.Cursor) -> str | None:
    import ipaddress

    cursor.execute("SELECT ip FROM config")
    result = cursor.fetchall()
    return str(max([ipaddress.ip_address(ip[0]) for ip in result])) if result else None


def get_new_ip():
    max_ip = get_max_ip()
    if not max_ip:
        return "10.0.0.2"
    octets = list(map(int, max_ip.split(".")))
    if len(octets) != 4:
        raise ValueError(Err.ip_error)

    octets[3] += 1

    for i in range(3, 0, -1):
        if octets[i] > 255:
            octets[i] = 0
            octets[i - 1] += 1

    if octets[3] >= 255:
        octets[3] = 1
        octets[2] += 1

    if octets[2] >= 255:
        octets[2] = 0
        octets[1] += 1

    if octets[1] > 255:
        raise ValueError(Err.ip_range_exhausted)

    return ".".join(map(str, octets))
