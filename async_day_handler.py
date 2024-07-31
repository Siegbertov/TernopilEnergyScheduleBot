import asyncio
import aiosqlite

class A_DB_Days:
    DEFAULT_WAS_UPDATED = False
    def __init__(self, db_filename) -> None:
        self.db_filename = db_filename
    
    async def create_table(self)->None:
        async with aiosqlite.connect(database=self.db_filename) as db:
            await db.execute(
                """CREATE TABLE 
                IF NOT EXISTS
                days(
                    was_distributed INTEGER,
                    day_name TEXT,
                    day_year INTEGER,
                    g_1 TEXT,
                    g_2 TEXT,
                    g_3 TEXT,
                    g_4 TEXT,
                    g_5 TEXT,
                    g_6 TEXT                   
                )"""
                )
            await db.commit()

    async def exists(self, day_name:str, day_year:int)->bool:
        async with aiosqlite.connect(database=self.db_filename) as db:
            row = await db.execute(
                    """SELECT * FROM days WHERE day_name=? AND day_year=?""",
                    (day_name, day_year)
                )
            await db.commit()
            return bool(await row.fetchone())

    async def insert_day(self, day_name:str, day_year:int, groups:dict)->None:
        async with aiosqlite.connect(database=self.db_filename) as db:
            await db.execute(
                """INSERT INTO days VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (0, day_name, day_year, groups["1"], groups["2"], groups["3"], groups["4"], groups["5"], groups["6"])
                )
            await db.commit()
    
    async def update_day(self, day_name:str, day_year:int, new_groups:dict)->None:
         async with aiosqlite.connect(database=self.db_filename) as db:
            await db.execute(
                """UPDATE days SET g_1=?, g_2=?, g_3=?,
                        g_4=?, g_5=?, g_6=?, was_distributed=? WHERE day_name=? AND day_year=?""",
                (new_groups["1"], new_groups["2"], new_groups["3"], new_groups["4"], new_groups["5"], new_groups["6"], 0, day_name, day_year)
                )
            await db.commit()

    async def add_day(self, day_name:str, day_year:int, groups:dict)->None:
        if groups is not None:
            if await self.exists(day_name=day_name, day_year=day_year):
                if not (groups == await self.get_day_groups_as_dict(day_name=day_name, day_year=day_year)):
                    await self.update_day(day_name=day_name, day_year=day_year, new_groups=groups)
            else:
                await self.insert_day(day_name=day_name, day_year=day_year, groups=groups)

    async def get_day_groups(self, day_name:str, day_year:int)->tuple|None:
        async with aiosqlite.connect(database=self.db_filename) as db:
            row = await db.execute(
                    """SELECT g_1, g_2, g_3, g_4, g_5, g_6 FROM days WHERE day_name=? AND day_year=?""",
                    (day_name, day_year)
                )
            await db.commit()
            return await row.fetchone()
        
    async def get_day_groups_as_dict(self, day_name:str, day_year:int)->dict:
        result_d = {}
        for num, group_data in enumerate(await self.get_day_groups(day_name=day_name, day_year=day_year), start=1): 
            result_d[str(num)] = group_data
        return result_d

    async def get_all_not_distributed_days(self)->list:
        async with aiosqlite.connect(database=self.db_filename) as db:
            rows = await db.execute(
                    """SELECT * FROM days WHERE was_distributed=?""",
                    (int(self.DEFAULT_WAS_UPDATED),)
                )
            await db.commit()
            return await rows.fetchall()

    async def set_all_was_distributed(self)->None:
        async with aiosqlite.connect(database=self.db_filename) as db:
            await db.execute(
                """UPDATE days SET was_distributed=?""",
                (int(not self.DEFAULT_WAS_UPDATED), )
                )
            await db.commit()

async def main():
    # TESTING ON EXAMPLES
    DB_FILENAME = "a_db_test.sql"
    DAY_NAME = "30 липня"
    DAY_YEAR = 2024
    GROUPS1 = {"1":"123123", "2":"56567556", "3":"qeqweqw", "4":"asdasdasd", "5":"zxczxcz", "6":"00000"}
    GROUPS2 = {"1":"1", "2":"22", "3":"333", "4":"4444", "5":"55555", "6":"666666"}

    a_db_days = A_DB_Days(db_filename=DB_FILENAME)
    await a_db_days.create_table()
    await a_db_days.insert_day(day_name=DAY_NAME, day_year=DAY_YEAR, groups=GROUPS1)
    await a_db_days.update_day(day_name=DAY_NAME, day_year=2030, new_groups=GROUPS2)
    print(await a_db_days.exists(day_name=DAY_NAME, day_year=DAY_YEAR))
    print(await a_db_days.get_day_groups(day_name=DAY_NAME, day_year=DAY_YEAR))
    print(await a_db_days.get_all_not_distributed_days())
    await a_db_days.set_all_was_distributed()
    print(await a_db_days.get_all_not_distributed_days())

if __name__ == "__main__":
    asyncio.run(main())