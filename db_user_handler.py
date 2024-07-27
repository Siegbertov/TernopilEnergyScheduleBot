from db import DB
import sqlite3

class DB_Users(DB):
    def __init__(self, db_filename):
        super().__init__(db_filename=db_filename)
        self.possible_groups = [str(x) for x in range(1, 7)]
        self.possible_views = ["INLINE", "OFF_PAIRS", "ON_PAIRS"]
        self.possible_totals = ["NONE", "TOTAL_ON", "TOTAL_OFF"]
        self.possible_emoji_off = [
                                '🔴', '⚫', '🌑', '🌚', 
                                '▪', '◾', '◼', '⬛',
                                '🟥', '❤', '🖤', '🍎', 
                                '🔻', '🪫', '🏴', '📕'
                                ]
        self.possible_emoji_on = [
                                '🟢', '🟡', '🌕', '🌝', 
                                '▫', '◽', '◻', '⬜', 
                                '🟩', '💚', '💛', '🍏', 
                                '⚡', '🔋', '🏳', '📗'
                                ]
        self.__create_table()
    
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
                                        fourth_g INTEGER DEFAULT 1,
                                        fifth_g INTEGER DEFAULT 1,
                                        sixth_g INTEGER DEFAULT 1,
                                        view TEXT DEFAULT 'OFF_PAIRS',
                                        total TEXT DEFAULT 'NONE'
                                    )""")
        connection.commit()
        cursor.close()
        connection.close()

    def get_all_auto_send_users(self, auto_send_value:int)->list:
        result = None
        connection = sqlite3.connect(self.db_filename)
        cursor = connection.cursor()

        result = cursor.execute(f"SELECT user_id FROM users WHERE auto_send=:auto_send", {'auto_send':auto_send_value}).fetchall()

        connection.commit()
        cursor.close()
        connection.close()

        return result

    def get_groups(self, user_id:str)->list:
        result = None
        connection = sqlite3.connect(self.db_filename)
        cursor = connection.cursor()

        result = cursor.execute(f"SELECT first_g, second_g, third_g, fourth_g, fifth_g, sixth_g FROM users WHERE user_id=:user_id", {'user_id':user_id}).fetchone()

        connection.commit()
        cursor.close()
        connection.close()

        return result

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

    def get_auto_send_status(self, user_id:str)->bool:
        result = [None]
        connection = sqlite3.connect(self.db_filename)
        cursor = connection.cursor()

        result = cursor.execute(f"SELECT auto_send FROM users WHERE user_id=:user_id", {'user_id':user_id}).fetchone()

        connection.commit()
        cursor.close()
        connection.close()

        return result[0]

    def change_auto_send(self, user_id:str)->None:
        connection = sqlite3.connect(self.db_filename)
        cursor = connection.cursor()

        current_auto_send = cursor.execute(f"SELECT auto_send FROM users WHERE user_id=:user_id", {'user_id':user_id}).fetchone()
        new_auto_send = 0 if current_auto_send[0] else 1
        cursor.execute(f"UPDATE users SET auto_send=:auto_send WHERE user_id=:user_id", {"user_id":user_id, "auto_send":new_auto_send})

        connection.commit()
        cursor.close()
        connection.close()

    def set_new_on_emoji(self, user_id:str, new_on_emoji:str)->None:
        connection = sqlite3.connect(self.db_filename)
        cursor = connection.cursor()
        cursor.execute(
                        f"UPDATE users SET on_emoji=:on_emoji WHERE user_id=:user_id",
                        {"user_id":user_id, "on_emoji":new_on_emoji}
                        )
        connection.commit()
        cursor.close()
        connection.close()
    
    def set_new_off_emoji(self, user_id:str, new_off_emoji:str)->None:
        connection = sqlite3.connect(self.db_filename)
        cursor = connection.cursor()
        cursor.execute(
                        f"UPDATE users SET off_emoji=:off_emoji WHERE user_id=:user_id",
                        {"user_id":user_id, "off_emoji":new_off_emoji}
                        )
        connection.commit()
        cursor.close()
        connection.close()

    def add_group(self, user_id:str, num_to_add:str)->None:
        group_to_add = {"1":"first_g", "2":"second_g", "3":"third_g", "4":"fourth_g", "5":"fifth_g", "6":"sixth_g"}[num_to_add]
        connection = sqlite3.connect(self.db_filename)
        cursor = connection.cursor()
        cursor.execute(
                        f"UPDATE users SET {group_to_add}=:{group_to_add} WHERE user_id=:user_id",
                        {group_to_add:1, "user_id":user_id}
                                        )
        connection.commit()
        cursor.close()
        connection.close()
    
    def remove_group(self, user_id:str, num_to_remove:str)->None:
        group_to_remove = {"1":"first_g", "2":"second_g", "3":"third_g", "4":"fourth_g", "5":"fifth_g", "6":"sixth_g"}[num_to_remove]
        connection = sqlite3.connect(self.db_filename)
        cursor = connection.cursor()
        cursor.execute(
                        f"UPDATE users SET {group_to_remove}=:{group_to_remove} WHERE user_id=:user_id",
                        {group_to_remove:0, "user_id":user_id}
                        )
        connection.commit()
        cursor.close()
        connection.close()

    def get_view(self, user_id:str)->str:
        result = [None]
        connection = sqlite3.connect(self.db_filename)
        cursor = connection.cursor()

        result = cursor.execute(f"SELECT view FROM users WHERE user_id=:user_id", {'user_id':user_id}).fetchone()

        connection.commit()
        cursor.close()
        connection.close()

        return result[0]

    def set_new_view(self, user_id:str, new_view:str)->None:
        connection = sqlite3.connect(self.db_filename)
        cursor = connection.cursor()
        cursor.execute(
                        f"UPDATE users SET view=:view WHERE user_id=:user_id",
                        {"user_id":user_id, "view":new_view}
                        )
        connection.commit()
        cursor.close()
        connection.close()

    def get_total(self, user_id:str)->str:
        result = [None]
        connection = sqlite3.connect(self.db_filename)
        cursor = connection.cursor()
        result = cursor.execute(f"SELECT total FROM users WHERE user_id=:user_id", {'user_id':user_id}).fetchone()
        connection.commit()
        cursor.close()
        connection.close()
        return result[0]

    def set_new_total(self, user_id:str, new_total:str)->None:
        connection = sqlite3.connect(self.db_filename)
        cursor = connection.cursor()
        cursor.execute(
                        f"UPDATE users SET total=:total WHERE user_id=:user_id",
                        {"user_id":user_id, "total":new_total}
                        )
        connection.commit()
        cursor.close()
        connection.close()
    

