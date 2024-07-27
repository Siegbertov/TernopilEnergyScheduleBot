from db import DB
import sqlite3

class DB_Days(DB):
    def __init__(self, db_filename):
        super().__init__(db_filename=db_filename)
        self.__create_table()

    def __create_table(self)->None:
        connection = sqlite3.connect(self.db_filename)
        cursor = connection.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS days (
                                    day_name TEXT,
                                    first_g TEXT,
                                    second_g TEXT,
                                    third_g TEXT,
                                    fouth_g TEXT,
                                    fifth_g TEXT,
                                    sixth_g TEXT,
                                    was_distributed INTEGER DEFAULT 0
                                )""")
        connection.commit()
        cursor.close()
        connection.close()

    def get_all_days_from_database(self)->list:
        result = None
        connection = sqlite3.connect(self.db_filename)
        cursor = connection.cursor()

        result = cursor.execute(f"SELECT * FROM days").fetchall()

        connection.commit()
        cursor.close()
        connection.close()

        return result

    def get_day(self, day_name:str)->tuple | None:
        result = None
        connection = sqlite3.connect(self.db_filename)
        cursor = connection.cursor()

        result = cursor.execute(f"SELECT * FROM days WHERE day_name=:day_name", {'day_name':day_name}).fetchone()

        connection.commit()
        cursor.close()
        connection.close()

        return result
    
    def exists(self, day_name:str)->bool:
        return bool(self.get_day(day_name=day_name))

    def set_all_days_was_distributed(self)->None:
        connection = sqlite3.connect(self.db_filename)
        cursor = connection.cursor()
        cursor.execute(f"UPDATE days SET was_distributed=:was_distributed", {'was_distributed':1})
        connection.commit()
        cursor.close()
        connection.close()

    def get_all_not_distributed_days(self)->list:
        result = None
        connection = sqlite3.connect(self.db_filename)
        cursor = connection.cursor()
        result = cursor.execute(f"SELECT * FROM days WHERE was_distributed=:was_distributed", {'was_distributed':0}).fetchall()
        connection.commit()
        cursor.close()
        connection.close()
        return result

    def add_day(self, day_name:str, groups:dict)->None:
        if self.exists(day_name=day_name):
            _, *db_groups_list, _ = self.get_day(day_name=day_name)
            current_groups = groups.values()
            is_same = True
            for x, y in zip(db_groups_list, current_groups):
                if x!=y:
                    is_same = False
                    break
            if not is_same:
                connection = sqlite3.connect(self.db_filename)
                cursor = connection.cursor()
                cursor.execute(
                        """UPDATE days SET first_g=:first_g, second_g=:second_g, third_g=:third_g,
                        fouth_g=:fouth_g, fifth_g=:fifth_g, sixth_g=:sixth_g, was_distributed=:was_distributed WHERE day_name=:day_name""",
                        {'day_name': day_name, 'first_g': groups['1'], 'second_g': groups['2'], 'third_g': groups['3'], 
                        'fouth_g': groups['4'], 'fifth_g': groups['5'], 'sixth_g': groups['6'], 'was_distributed':0}
                                        )
                connection.commit()
                cursor.close()
                connection.close()
            else:
                pass
        else:
            connection = sqlite3.connect(self.db_filename)
            cursor = connection.cursor()
            cursor.execute(
                        f"INSERT INTO days VALUES (:day_name, :first_g, :second_g, :third_g, :fouth_g, :fifth_g, :sixth_g)", 
                        {'day_name': day_name, 'first_g': groups['1'], 'second_g': groups['2'], 'third_g': groups['3'], 
                        'fouth_g': groups['4'], 'fifth_g': groups['5'], 'sixth_g': groups['6']}
                                        ) 
            connection.commit()
            cursor.close()
            connection.close()



