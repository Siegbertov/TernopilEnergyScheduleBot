from db import DB
import sqlite3

class DB_Users(DB):
    def __init__(self, db_filename):
        super().__init__(db_filename=db_filename)
        self.possible_groups = [str(x) for x in range(1, 7)]
        self.possible_views = ["INLINE", "OFF_PAIRS", "ON_PAIRS"]
        self.possible_totals = ["NONE", "ON", "OFF"]
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

    def set_emoji_on(self, user_id:str, new_on_emoji:str)->None:
        #TODO implement set_emoji_on()
        pass

    def set_emoji_off(self, user_id:str, new_off_emoji:str)->None:
        #TODO implement set_emoji_off()
        pass

    def add_group(self, user_id:str, num_to_add:str)->None:
        group_to_add = {"1":"first_g", "2":"second_g", "3":"third_g", "4":"fourth_g", "5":"fifth_g", "6":"sixth_g"}[num_to_add]
        connection = sqlite3.connect(self.db_filename)
        cursor = connection.cursor()
        cursor.execute(
                        f"UPDATE users SET {group_to_add}=:{group_to_add}",
                        {group_to_add:1}
                                        )
        connection.commit()
        cursor.close()
        connection.close()
    
    def remove_group(self, user_id:str, num_to_remove:str)->None:
        group_to_remove = {"1":"first_g", "2":"second_g", "3":"third_g", "4":"fourth_g", "5":"fifth_g", "6":"sixth_g"}[num_to_remove]
        connection = sqlite3.connect(self.db_filename)
        cursor = connection.cursor()
        cursor.execute(
                        f"UPDATE users SET {group_to_remove}=:{group_to_remove}",
                        {group_to_remove:0}
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
                        f"UPDATE users SET view=:view",
                        {"view":new_view}
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
                        f"UPDATE users SET total=:total",
                        {"total":new_total}
                        )
        connection.commit()
        cursor.close()
        connection.close()
    

