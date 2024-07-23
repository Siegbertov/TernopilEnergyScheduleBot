from db import DB
import sqlite3

class DB_Users(DB):
    def __init__(self, db_filename):
        super().__init__(db_filename=db_filename)

    def __create_table(self)->None:
        connection = sqlite3.connect(self.db_filename)
        cursor = connection.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                                        user_id TEXT,
                                        auto_send INTEGER DEFAULT 0,
                                        off_emoji TEXT DEFAULT '🔴',
                                        on_emoji TEXT DEFAULT '🟢',
                                        first_g INTEGER DEFAULT 1,
                                        second_g INTEGER DEFAULT 1,
                                        third_g INTEGER DEFAULT 1,
                                        fouth_g INTEGER DEFAULT 1,
                                        fifth_g INTEGER DEFAULT 1,
                                        sixth_g INTEGER DEFAULT 1,
                                        view TEXT DEFAULT 'OFF_PAIRS',
                                        total TEXT DEFAULT 'NONE'
                                    )""")
        connection.commit()
        cursor.close()
        connection.close()

    def is_user_id_exists(self, user_id:str)->bool:
        result = None
        connection = sqlite3.connect(self.db_filename)
        cursor = connection.cursor()

        result = bool(self.get_user(user_id=user_id))

        connection.commit()
        cursor.close()
        connection.close()

        return result

    def get_user(self, user_id:str) -> tuple | None:
        result = None
        connection = sqlite3.connect(self.db_filename)
        cursor = connection.cursor()

        result = cursor.execute(f"SELECT * FROM users WHERE user_id=:user_id", {'user_id':user_id}).fetchone()

        connection.commit()
        cursor.close()
        connection.close()

        return result

    def add_user(self, user_id:str)->None:
        connection = sqlite3.connect(self.db_filename)
        cursor = connection.cursor()

        cursor.execute(f"INSERT INTO users (user_id) VALUES ({user_id})")
        connection.commit()
        cursor.close()
        connection.close()

    

