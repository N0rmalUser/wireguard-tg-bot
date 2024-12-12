import sqlite3
from datetime import datetime

from pytz import timezone as tz

from app.config import TIME_FORMAT, TIMEZONE, USERS_DB


class ConfigDatabase:
    def __init__(self, ip: str):
        self.__conn = sqlite3.connect(USERS_DB)
        self.__cursor = self.__conn.cursor()
        self.__ip = ip
        self._check_config()

    @property
    def ip(self):
        return self.__ip

    @property
    def name(self):
        self.__cursor.execute(
            """
            SELECT name FROM config
            WHERE ip = ?;
            """,
            (self.__ip,),
        )
        result = self.__cursor.fetchone()
        return result[0] if result is not None else False

    @name.setter
    def name(self, name: str):
        self.__cursor.execute(
            """
            UPDATE config
            SET name = ?
            WHERE ip = ?;
            """,
            (name, self.__ip),
        )
        self.__conn.commit()

    @property
    def user_id(self) -> int:
        self.__cursor.execute(
            """
            SELECT user_id FROM config
            WHERE ip = ?;
            """,
            (self.__ip,),
        )
        result = self.__cursor.fetchone()
        return result[0] if result is not None else False

    @user_id.setter
    def user_id(self, user_id: int):
        self.__cursor.execute(
            """
            UPDATE config
            SET user_id = ?
            WHERE ip = ?;
            """,
            (user_id, self.__ip),
        )
        self.__conn.commit()

    @property
    def public_key(self):
        self.__cursor.execute(
            """
            SELECT public_key FROM config
            WHERE ip = ?;
            """,
            (self.__ip,),
        )
        result = self.__cursor.fetchone()
        return result[0] if result is not None else False

    @public_key.setter
    def public_key(self, public_key: str):
        self.__cursor.execute(
            """
            UPDATE config
            SET public_key = ?
            WHERE ip = ?;
            """,
            (public_key, self.__ip),
        )

    @property
    def private_key(self):
        self.__cursor.execute(
            """
            SELECT private_key FROM config
            WHERE ip = ?;
            """,
            (self.__ip,),
        )
        result = self.__cursor.fetchone()
        return result[0] if result is not None else False

    @private_key.setter
    def private_key(self, private_key: str):
        self.__cursor.execute(
            """
            UPDATE config
            SET private_key = ?
            WHERE ip = ?;
            """,
            (private_key, self.__ip),
        )

    @property
    def preshared_key(self):
        self.__cursor.execute(
            """
            SELECT preshared_key FROM config
            WHERE ip = ?;
            """,
            (self.__ip,),
        )
        result = self.__cursor.fetchone()
        return result[0] if result is not None else False

    @preshared_key.setter
    def preshared_key(self, preshared_key: str):
        self.__cursor.execute(
            """
            UPDATE config
            SET preshared_key = ?
            WHERE ip = ?;
            """,
            (preshared_key, self.__ip),
        )

    @property
    def creation_date(self):
        self.__cursor.execute(
            """
            SELECT creation_date FROM config
            WHERE ip = ?;
            """,
            (self.__ip,),
        )
        result = self.__cursor.fetchone()
        return result[0] if result is not None else False

    @creation_date.setter
    def creation_date(self, creation_date: str):
        self.__cursor.execute(
            """
            UPDATE config
            SET creation_date = ?
            WHERE ip = ?;
            """,
            (creation_date, self.__ip),
        )
        self.__conn.commit()

    @property
    def ports(self) -> dict[str, str] | None:
        self.__cursor.execute(
            """
            SELECT p.external_port, p.internal_port
            FROM ports p
            JOIN config c ON p.ip = c.ip
            WHERE c.ip = ?;
            """,
            (self.__ip,),
        )
        result = self.__cursor.fetchall()
        return {external_port: internal_port for external_port, internal_port in result} if result else None

    def _check_config(self):
        self.__cursor.execute(
            """
            SELECT * FROM config
            WHERE ip = ?;
            """,
            (self.__ip,),
        )

        if self.__cursor.fetchone() is None:
            creation_date = datetime.now(tz(TIMEZONE)).strftime(TIME_FORMAT)
            self.__cursor.execute(
                """
                INSERT INTO config(ip, creation_date)
                VALUES(?, ?);
                """,
                (self.__ip, str(creation_date)),
            )
            self.__conn.commit()

    def __del__(self):
        self.__conn.commit()
        self.__conn.close()
