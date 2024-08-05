import asyncio
import aiosqlite

class A_DB_Chats:
    POSSIBLE_GROUPS = [str(x) for x in range(1, 7)]
    POSSIBLE_VIEWS = [ "OFF_PAIRS", "ON_PAIRS", "INLINE"]
    POSSIBLE_TOTALS = ["NONE", "TOTAL_ON", "TOTAL_OFF"]
    POSSIBLE_OFF_EMOJIS = [
                                '🔴', '⚫', '🌑', '🌚', 
                                '▪', '◾', '◼', '⬛',
                                '🟥', '❤', '🖤', '🍎', 
                                '🔻', '🪫', '🏴', '📕'
                                ]
    POSSIBLE_ON_EMOJIS = [
                                '🟢', '🟡', '🌕', '🌝', 
                                '▫', '◽', '◻', '⬜', 
                                '🟩', '💚', '💛', '🍏', 
                                '⚡', '🔋', '🏳', '📗'
                                ]
    DEFAULT_AUTO_SEND = False

    def __init__(self, db_filename)->None:
        self.db_filename = db_filename

    async def create_table(self)->None:
        async with aiosqlite.connect(database=self.db_filename) as db:
            await db.execute(
                """
                CREATE TABLE
                IF NOT EXISTS
                users(
                    chat_id TEXT,
                    auto_send INTEGER,
                    off_emoji TEXT,
                    on_emoji TEXT,
                    first_g INTEGER,
                    second_g INTEGER,
                    third_g INTEGER,
                    fourth_g INTEGER,
                    fifth_g INTEGER,
                    sixth_g INTEGER,
                    view TEXT,
                    total TEXT
                )
                """
            )
            await db.commit()

    async def add_сhat(self, chat_id:str)->None:
        async with aiosqlite.connect(database=self.db_filename) as db:
            await db.execute(
                """INSERT INTO users VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (chat_id, int(self.DEFAULT_AUTO_SEND), 
                 self.POSSIBLE_OFF_EMOJIS[0], self.POSSIBLE_ON_EMOJIS[0], 
                 1, 1, 1, 1, 1, 1, self.POSSIBLE_VIEWS[0], self.POSSIBLE_TOTALS[0])
            )
            await db.commit()

    async def delete_chat(self, chat_id:str)->None:
        async with aiosqlite.connect(database=self.db_filename) as db:
            await db.execute(
                """DELETE FROM users WHERE chat_id=?""",
                (chat_id,)
            )
            await db.commit()

    async def get_chat_settings(self, chat_id:str)->tuple|None:
        async with aiosqlite.connect(database=self.db_filename) as db:
            row = await db.execute(
                """SELECT * FROM users WHERE chat_id=?""",
                (chat_id,)
            )
            await db.commit()
            return await row.fetchone()

    async def exists(self, chat_id:str)->bool:
        return bool(await self.get_chat_settings(chat_id=chat_id))

    async def get_groups(self, chat_id:str)->list:
        async with aiosqlite.connect(database=self.db_filename) as db:
            row = await db.execute(
                """SELECT 
                first_g, second_g, third_g, 
                fourth_g, fifth_g, sixth_g 
                FROM users 
                WHERE chat_id=?""",
                (chat_id,)
            )
            await db.commit()
            return await row.fetchone()

    async def get_auto_send_status(self, chat_id:str)->bool:
        async with aiosqlite.connect(database=self.db_filename) as db:
            row = await db.execute(
                """SELECT 
                auto_send
                FROM users 
                WHERE chat_id=?""",
                (chat_id,)
            )
            await db.commit()
            result = await row.fetchone()
            return bool(result[0])
        
    async def get_all_auto_send_chats_settings(self, auto_send_value:int)->list:
        async with aiosqlite.connect(database=self.db_filename) as db:
            rows = await db.execute(
                """SELECT * FROM users WHERE auto_send=?""",
                (auto_send_value, )
            )
            await db.commit()
            return await rows.fetchall()
        
    async def change_auto_send(self, chat_id:str)->None:
        async with aiosqlite.connect(database=self.db_filename) as db:
            current_status = await self.get_auto_send_status(chat_id=chat_id)
            await db.execute(
                """
                UPDATE users
                SET auto_send=?
                WHERE chat_id=?
                """,
                (int(not current_status), chat_id)
            )
            await db.commit()        

    async def set_new_on_emoji(self, chat_id:str, new_on_emoji:str)->None:
        async with aiosqlite.connect(database=self.db_filename) as db:
            await db.execute(
                """UPDATE users SET on_emoji=? WHERE chat_id=?""",
                (new_on_emoji, chat_id)
            )
            await db.commit()

    async def set_new_off_emoji(self, chat_id:str, new_off_emoji:str)->None:
        async with aiosqlite.connect(database=self.db_filename) as db:
            await db.execute(
                """UPDATE users SET off_emoji=? WHERE chat_id=?""",
                (new_off_emoji, chat_id)
            )
            await db.commit()

    async def add_group(self, chat_id:str, num_to_add:str)->None:
        group_to_add = {"1":"first_g", "2":"second_g", "3":"third_g", "4":"fourth_g", "5":"fifth_g", "6":"sixth_g"}[num_to_add]
        async with aiosqlite.connect(database=self.db_filename) as db:
            await db.execute(
                f"""UPDATE users SET {group_to_add}=? WHERE chat_id=?""",
                (1, chat_id)
            )
            await db.commit()

    async def remove_group(self, chat_id:str, num_to_remove:str)->None:
        group_to_remove = {"1":"first_g", "2":"second_g", "3":"third_g", "4":"fourth_g", "5":"fifth_g", "6":"sixth_g"}[num_to_remove]
        async with aiosqlite.connect(database=self.db_filename) as db:
            await db.execute(
                f"""UPDATE users SET {group_to_remove}=? WHERE chat_id=?""",
                (0, chat_id)
            )
            await db.commit()

    async def get_view(self, chat_id:str)->str:
        async with aiosqlite.connect(database=self.db_filename) as db:
            row = await db.execute(
                """SELECT view
                FROM users
                WHERE chat_id=?""",
                (chat_id,)
            )
            await db.commit()
            result = await row.fetchone()
            return result[0]

    async def set_new_view(self, chat_id:str, new_view:str)->None:
        async with aiosqlite.connect(database=self.db_filename) as db:
            await db.execute(
                """UPDATE users SET view=? WHERE chat_id=?""",
                (new_view, chat_id)
            )
            await db.commit()

    async def get_total(self, chat_id:str)->str:
        async with aiosqlite.connect(database=self.db_filename) as db:
            row = await db.execute(
                """SELECT total
                FROM users
                WHERE chat_id=?""",
                (chat_id,)
            )
            await db.commit()
            result = await row.fetchone()
            return result[0]

    async def set_new_total(self, chat_id:str, new_total:str)->None:
        async with aiosqlite.connect(database=self.db_filename) as db:
            await db.execute(
                """UPDATE users SET total=? WHERE chat_id=?""",
                (new_total, chat_id)
            )
            await db.commit()



async def main():
    FILENAME = 'TEST.sql'
    RED_APPLE_EMOJI = "🍎"
    GREEN_APPLE_EMOJI = "🍏"
    a_db_u = A_DB_Chats(db_filename=FILENAME)
    await a_db_u.create_table()
    # await a_db_u.add_user(chat_id="100") # WORKS
    # await a_db_u.delete_user(chat_id="100") # WORKS
    # print(await a_db_u.get_user(chat_id=r"228")) # WORKS
    # print(await a_db_u.exists(chat_id="200")) # WORKS
    # print(await a_db_u.get_groups(chat_id="100")) # WORKS
    # await a_db_u.change_auto_send(chat_id="100") # WORKS
    # print(await a_db_u.get_auto_send_status(chat_id="100")) # WORKS
    print(await a_db_u.get_all_auto_send_chats_settings()) # WORKS -------------------------------------?????
    # await a_db_u.set_new_on_emoji(chat_id="100", new_on_emoji=GREEN_APPLE_EMOJI) # WORKS
    # await a_db_u.set_new_off_emoji(chat_id="100", new_off_emoji=RED_APPLE_EMOJI) # WORKS
    # print( await a_db_u.get_view(chat_id="100") )
    # await a_db_u.set_new_view(chat_id="100", new_view="INLINE")
    # print( await a_db_u.get_view(chat_id="100") )

    # print( await a_db_u.get_total(chat_id="100") )
    # await a_db_u.set_new_total(chat_id="100", new_total="TOTAL_ON")
    # print( await a_db_u.get_total(chat_id="100") )
    # await a_db_u.remove_group(chat_id="100", num_to_remove="3")
    # await a_db_u.remove_group(chat_id="100", num_to_remove="4")
    # await a_db_u.remove_group(chat_id="100", num_to_remove="5")

    # await a_db_u.add_group(chat_id="100", num_to_add="4")





if __name__ == "__main__":
    asyncio.run(main())
    