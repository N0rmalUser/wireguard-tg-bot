import sqlite3
from datetime import datetime

from pytz import timezone as tz

from app.config import TIME_FORMAT, TIMEZONE, USERS_DB


class PortDatabase:
    def __init__(self, num: int):
        self.__conn = sqlite3.connect(USERS_DB)
        self.__cursor = self.__conn.cursor()
        self.__num = num
        self._check_and_create_record()

    @property
    def ip(self):
        self.__cursor.execute(
            """
            SELECT ip FROM port
            WHERE num = ?;
            """,
            (self.__num,),
        )
        result = self.__cursor.fetchone()
        return result[0] if result is not None else False

    @ip.setter
    def ip(self, ip: str):
        self.__cursor.execute(
            """
            UPDATE port
            SET ip = ?
            WHERE num = ?;
            """,
            (ip, self.__num),
        )
        self.__conn.commit()

    @ip.deleter
    def ip(self):
        self.__cursor.execute(
            """
            DELETE FROM port
            WHERE num = ?;
            """,
            (self.__num,),
        )
        self.__conn.commit()

    def _check_and_create_record(self):
        self.__cursor.execute(
            """
            SELECT * FROM port
            WHERE num = ?;
            """,
            (self.__num,),
        )

        if self.__cursor.fetchone() is None:
            creation_date = datetime.now(tz(TIMEZONE)).strftime(TIME_FORMAT)
            self.__cursor.execute(
                """
                INSERT INTO port(num, creation_date)
                VALUES(?, ?);
                """,
                (self.__num, creation_date),
            )
            self.__conn.commit()

    def __del__(self):
        self.__conn.commit()
        self.__conn.close()
