import os
from dotenv import load_dotenv
import telebot
from telebot import types
from utils import scrapper, get_today_date_name, get_tomorrow_date_name
from utils import create_users_table, __is_user_id_in_database, __add_user
from utils import create_days_table, get_all_days_from_database, get_last_day_from_database, __add_day_to_database


def configure():
    load_dotenv()


if __name__ == "__main__":
    configure()
    DATABASE_FILENAME = "small_db.sql"
    TOKEN = os.getenv('TOKEN')
    MY_USER_ID = os.getenv('MY_USER_ID')
    LINK = os.getenv('LINK')
    bot = telebot.TeleBot(token=TOKEN)

    @bot.message_handler(commands=['start'])
    def start(message):
        create_users_table(db_filename=DATABASE_FILENAME)
        create_days_table(db_filename=DATABASE_FILENAME)
        if not __is_user_id_in_database(db_filename=DATABASE_FILENAME, user_id=message.from_user.id):
            __add_user(db_filename=DATABASE_FILENAME, user_id=message.from_user.id)
            bot.send_message(message.chat.id, f"ADDED USER <{message.from_user.id}>") # FIXME edit later
        else:
            bot.send_message(message.chat.id, f"USER <{message.from_user.id}> ALREADY EXISTS") # FIXME edit later
    
    @bot.message_handler(commands=['update'])
    def update(message):
        if message.from_user.id == MY_USER_ID:
            DAYS = scrapper(link=LINK, day_month_r=r"(\d+) (\w+),", group_r=r"(\d\d:\d\d)-(\d\d:\d\d)\s+(\d)\s+\w+")
            for day_name, groups in DAYS.items():
                __add_day_to_database(db_filename=DATABASE_FILENAME, day_name=day_name, groups=groups)
                bot.send_message(message.chat.id, f"UPDATED: <{day_name}>") # FIXME edit later
        else:
            bot.send_message(message.chat.id, f"This command only for admins") # FIXME edit later

    @bot.message_handler(commands=['settings'])
    def settings(message):
        # TODO implement command /settings
        bot.send_message(message.chat.id, "Not Implemented....yet!")

    @bot.message_handler(commands=['get_today'])
    def get_today(message):
        # TODO implement command /get_today
        txt = get_today_date_name()
        bot.send_message(message.chat.id, txt)
        bot.send_message(message.chat.id, "Not Implemented....yet!")
    
    @bot.message_handler(commands=['get_tomorrow'])
    def get_tomorrow(message):
        # TODO implement command /get_tomorrow
        txt = get_tomorrow_date_name()
        bot.send_message(message.chat.id, txt)
        bot.send_message(message.chat.id, "Not Implemented....yet!")    

    @bot.message_handler(commands=['get_last_available'])
    def get_last_available(message):
        db_day = get_last_day_from_database(db_filename=DATABASE_FILENAME)
        d_n, g1, g2, g3, g4, g5, g6 = db_day
        g_s = [g1, g2, g3, g4, g5, g6]
        txt = f"*Графік на {d_n}:*"
        for g in g_s:
            txt = f"{txt} {g}"
        txt = txt.replace("+", "\\+")
        txt = txt.replace("-", "\\-")
        bot.send_message(message.chat.id, txt, parse_mode='MarkdownV2') # FIXME edit later

    # @bot.message_handler(commands=['get_all'])
    # def get_all(message):
    #     db_days = get_all_days_from_database(db_filename=DATABASE_FILENAME)
    #     for db_day in db_days:
    #         txt = " ".join(db_day)
    #         bot.send_message(message.chat.id, txt) # FIXME edit later

    # END
    bot.polling(non_stop=True)
    # bot.infinity_polling() # SAME