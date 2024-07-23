import os
from dotenv import load_dotenv
import telebot
from telebot import types
from utils import create_users_table, __is_user_id_in_database, __add_user


def configure():
    load_dotenv()


if __name__ == "__main__":
    configure()
    DATABASE_FILENAME = "small_db.sql"
    TOKEN = os.getenv('TOKEN')
    MY_USER_ID = os.getenv('MY_USER_ID')
    bot = telebot.TeleBot(token=TOKEN)

    @bot.message_handler(commands=['start'])
    def start(message):
        create_users_table(db_filename=DATABASE_FILENAME)
        if not __is_user_id_in_database(db_filename=DATABASE_FILENAME, user_id=message.from_user.id):
            __add_user(db_filename=DATABASE_FILENAME, user_id=message.from_user.id)
            bot.send_message(message.chat.id, f"ADDED USER <{message.from_user.id}>") # FIXME edit later
        else:
            bot.send_message(message.chat.id, f"USER <{message.from_user.id}> ALREADY EXISTS") # FIXME edit later
        

    # END
    bot.polling(non_stop=True)
    # bot.infinity_polling() # SAME