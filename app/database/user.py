import sqlite3

from app.config import USERS_DB


class UserDatabase:
    def __init__(self, user_id: int = None, topic_id: int = None):
        self.__conn = sqlite3.connect(USERS_DB)
        self.__cursor = self.__conn.cursor()
        if user_id is None:
            if topic_id is None:
                raise ValueError("Не передан user_id или topic_id")
            self.__user_id = self.__user_id_from_topic(topic_id)
        else:
            self.__user_id = user_id

    @property
    def username(self) -> bool:
        self.__cursor.execute(
            """
            SELECT username FROM user
            WHERE user_id = ?
            """,
            (self.__user_id,),
        )
        result = self.__cursor.fetchone()
        return result[0] if result is not None else False

    @username.setter
    def username(self, username: str) -> None:
        self.__cursor.execute(
            """
            INSERT INTO user(user_id, username)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE 
            SET username=excluded.username;
            """,
            (self.__user_id, username),
        )
        self.__conn.commit()

    @property
    def fullname(self) -> bool:
        self.__cursor.execute(
            """
            SELECT fullname FROM user
            WHERE user_id = ?
            """,
            (self.__user_id,),
        )
        result = self.__cursor.fetchone()
        return result[0] if result is not None else False

    @fullname.setter
    def fullname(self, fullname: str) -> None:
        self.__cursor.execute(
            """
            INSERT INTO user(user_id, fullname)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE 
            SET fullname=excluded.fullname;
            """,
            (self.__user_id, fullname),
        )
        self.__conn.commit()

    @property
    def blocked(self) -> bool:
        self.__cursor.execute(
            """
            SELECT blocked FROM user
            WHERE user_id = ?
            """,
            (self.__user_id,),
        )
        result = self.__cursor.fetchone()
        return bool(result[0]) if result is not None else False

    @blocked.setter
    def blocked(self, block: bool) -> None:
        self.__cursor.execute(
            """
            INSERT INTO user(user_id, blocked)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE 
            SET blocked=excluded.blocked;
            """,
            (self.__user_id, block),
        )
        self.__conn.commit()

    @property
    def banned(self) -> bool:
        self.__cursor.execute(
            """
            SELECT banned FROM user
            WHERE user_id = ?
            """,
            (self.__user_id,),
        )
        result = self.__cursor.fetchone()
        return bool(result[0]) if result is not None else False

    @banned.setter
    def banned(self, ban: bool) -> None:
        self.__cursor.execute(
            """
            INSERT INTO user(user_id, banned)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE 
            SET banned=excluded.banned;
            """,
            (self.__user_id, ban),
        )
        self.__conn.commit()

    @property
    def tracking(self) -> bool:
        self.__cursor.execute(
            """
            SELECT tracking FROM user
            WHERE user_id = ?
            """,
            (self.__user_id,),
        )
        result = self.__cursor.fetchone()
        return bool(result[0]) if result is not None else False

    @tracking.setter
    def tracking(self, tracking: bool) -> None:
        self.__cursor.execute(
            """
            INSERT INTO user(user_id, tracking)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE 
            SET tracking=excluded.tracking;
            """,
            (self.__user_id, tracking),
        )
        self.__conn.commit()

    @property
    def topic_id(self) -> int:
        self.__cursor.execute(
            """
            SELECT topic_id FROM user
            WHERE user_id = ?
            """,
            (self.__user_id,),
        )
        result = self.__cursor.fetchone()
        return result[0] if result else False

    @topic_id.setter
    def topic_id(self, topic_id: int) -> None:
        self.__cursor.execute(
            """
            INSERT INTO user(user_id, topic_id)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE
            SET topic_id=excluded.topic_id;
            """,
            (self.__user_id, topic_id),
        )
        self.__conn.commit()

    @property
    def start_date(self) -> str:
        self.__cursor.execute(
            """
            SELECT start_date FROM user
            WHERE user_id = ?
            """,
            (self.__user_id,),
        )
        result = self.__cursor.fetchone()
        return result[0] if result else None

    @start_date.setter
    def start_date(self, date: str) -> None:
        self.__cursor.execute(
            """
            INSERT INTO user(user_id, start_date)
            VALUES(?, ?) ON CONFLICT(user_id) DO UPDATE 
            SET start_date=excluded.start_date;
            """,
            (self.__user_id, str(date)),
        )
        self.__conn.commit()

    @property
    def allowed(self) -> str:
        self.__cursor.execute(
            """
            SELECT allowed FROM user
            WHERE user_id = ?
            """,
            (self.__user_id,),
        )
        result = self.__cursor.fetchone()
        return result[0] if result else None

    @allowed.setter
    def allowed(self, allowed: str) -> None:
        self.__cursor.execute(
            """
            UPDATE user
            SET allowed = ?
            WHERE user_id = ?;
            """,
            (str(allowed), self.__user_id),
        )
        self.__conn.commit()

    @property
    def configs(self) -> list[list[str]] | None:
        self.__cursor.execute(
            """
            SELECT ip, name FROM config
            WHERE user_id = ?;
            """,
            (self.__user_id,),
        )
        result = self.__cursor.fetchall()
        return result if result else None

    def tg_id(self) -> int:
        return self.__user_id

    def __user_id_from_topic(self, topic_id: int) -> int:
        self.__cursor.execute(
            """
            SELECT user_id FROM user
            WHERE topic_id = ?
            """,
            (topic_id,),
        )
        result = self.__cursor.fetchone()
        return result[0] if result else None

    def __del__(self):
        self.__conn.commit()
        self.__conn.close()
