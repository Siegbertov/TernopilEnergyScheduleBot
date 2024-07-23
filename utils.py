import sqlite3

def create_users_table(db_filename:str)->None:
    connection = sqlite3.connect(db_filename)
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
    
def __is_user_id_in_database(db_filename:str, user_id:str)->bool:
    result = None
    connection = sqlite3.connect(db_filename)
    cursor = connection.cursor()

    result = bool(cursor.execute(f"SELECT * FROM users WHERE user_id=:user_id", {'user_id':user_id}).fetchone())
    
    connection.commit()
    cursor.close()
    connection.close()

    return result

def __add_user(db_filename:str, user_id:str):
    connection = sqlite3.connect(db_filename)
    cursor = connection.cursor()

    cursor.execute(f"INSERT INTO users (user_id) VALUES ({user_id})")
    connection.commit()
    cursor.close()
    connection.close()  

def add_user_if_not_exits(db_filename:str, user_id:str)->None:
    if not __is_user_id_in_database(db_filename=db_filename, user_id=user_id):
        __add_user(db_filename=db_filename, user_id=user_id)









