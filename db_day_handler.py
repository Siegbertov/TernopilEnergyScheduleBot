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
                                    sixth_g TEXT
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

    def get_day_by_name(self, day_name:str)->tuple | None:
        result = None
        connection = sqlite3.connect(self.db_filename)
        cursor = connection.cursor()

        result = cursor.execute(f"SELECT * FROM days WHERE day_name=:day_name", {'day_name':day_name}).fetchone()

        connection.commit()
        cursor.close()
        connection.close()

        return result
    
    def is_day_exists(self, day_name:str)->bool:
        return bool(self.get_day_by_name(day_name=day_name))

    def add_day(self, day_name:str, groups:dict)->None:
        if self.is_day_exists(day_name=day_name):
            db_day_tuple = self.get_day_by_name(day_name=day_name)
            parsed_day = [day_name]
            for group in groups.values():
                parsed_day.append(group)
            parsed_day_tuple = tuple(parsed_day)
            if not (db_day_tuple == parsed_day_tuple):
                connection = sqlite3.connect(self.db_filename)
                cursor = connection.cursor()
                cursor.execute(
                        """UPDATE days SET first_g=:first_g, second_g=:second_g, third_g=:third_g,
                        fouth_g=:fouth_g, fifth_g=:fifth_g, sixth_g=:sixth_g WHERE day_name=:day_name""",
                        {'day_name': day_name, 'first_g': groups['1'], 'second_g': groups['2'], 'third_g': groups['3'], 
                        'fouth_g': groups['4'], 'fifth_g': groups['5'], 'sixth_g': groups['6']}
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





