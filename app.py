import os
from dotenv import load_dotenv
import telebot
from telebot import types
import telebot.formatting
from utils import scrapper, get_today_name, get_tomorrow_name, bold, italic, mono
from db_day_handler import DB_Days
from db_user_handler import DB_Users

# from utils import create_users_table, __is_user_id_in_database, __add_user
# from utils import create_days_table, get_all_days_from_database, get_last_day_from_database, __add_day_to_database, __get_day_from_database


def configure():
    load_dotenv()


if __name__ == "__main__":
    # ENV VARIABLES
    configure()
    TOKEN = os.getenv('TOKEN')
    MY_USER_ID = os.getenv('MY_USER_ID')
    LINK = os.getenv('LINK')

    # DATABASE CREATION
    DATABASE_FILENAME = "small_db.sql"
    db_users = DB_Users(db_filename=DATABASE_FILENAME)
    db_days = DB_Days(db_filename=DATABASE_FILENAME)
    
    # BOT CREATION
    bot = telebot.TeleBot(token=TOKEN)

    @bot.message_handler(commands=['start'])
    def start(message):
        if not db_users.is_user_id_exists(user_id=message.from_user.id): 
            db_users.add_user(user_id=message.from_user.id)
            bot.send_message(message.chat.id, f"ADDED USER <{message.from_user.id}>") # FIXME edit later
        else:
            bot.send_message(message.chat.id, f"USER <{message.from_user.id}> ALREADY EXISTS") # FIXME edit later
    
    @bot.message_handler(commands=['update'])
    def update(message):
        if str(message.from_user.id) == str(MY_USER_ID):
            DAYS = scrapper(link=LINK, day_month_r=r"(\d+) (\w+),", group_r=r"(\d\d:\d\d)-(\d\d:\d\d)\s+(\d)\s+\w+")
            for day_name, groups in DAYS.items():
                db_days.add_day(day_name=day_name, groups=groups)
                bot.send_message(message.chat.id, f"UPDATED: <{day_name}>") # FIXME edit later
        else:
            bot.send_message(message.chat.id, f"This command only for admins") # FIXME edit later

    @bot.message_handler(commands=['settings'])
    def settings(message):
        # TODO implement command /settings
        user_settings = db_users.get_user(user_id=message.from_user.id)
        _, auto_send, off_emoji, on_emoji, *groups_to_show, view, total= user_settings
        # TODO change showing of groups_to_show
        groups_to_show = [x for x in range(1, 7) if groups_to_show[x-1]]
        txt = f"""▪️Авторозсилка : {bold('ON' if auto_send else 'OFF')}
/change_auto_send

▪️Емоджі відключення : {bold(off_emoji)}
/set_emoji_off + YOUR_EMOJI

▪️Емоджі включення: {bold(on_emoji)}
/set_emoji_on + YOUR_EMOJI

▪️Мої групи : {bold('')}
/add_group + NUMBER
/remove_group + NUMBER

▪️Вигляд : {bold(view)} 
<INLINE, ON_PAIRS, OFF_PAIRS>
/set_view + VALUE

▪️Сумарний час включень/відключень : {bold(total)} 
<NONE, OFF, ON>
/set_total + VALUE"""
        txt = txt.replace("_", "\\_")
        bot.send_message(message.chat.id, txt, parse_mode='Markdown')
        bot.send_message(message.chat.id, "<b>Команди поки що не працюють!!!</b>", parse_mode="HTML")

    @bot.message_handler(commands=['get_today'])
    def get_today(message):
        # TODO implement BEAUTIFUL command /get_today 
        day_name = get_today_name()
        db_day = db_days.get_day_by_name(day_name=day_name)
        if db_day:
            d_n, *g_s = db_day
            txt = f"*Графік на {d_n}:*"
            for g in g_s:
                txt = f"{txt} {g}"
            txt = txt.replace("+", "\\+")
            txt = txt.replace("-", "\\-")
            bot.reply_to(message, txt, parse_mode='MarkdownV2') # FIXME edit later
        else:
            bot.reply_to(message, f"Графік на {day_name} відсутній! 😢") 
    
    @bot.message_handler(commands=['get_tomorrow'])
    def get_tomorrow(message):
        # TODO implement BEAUTIFUL command /get_tomorrow
        day_name = get_tomorrow_name()
        db_day = db_days.get_day_by_name(day_name=day_name)
        if db_day:
            d_n, *g_s = db_day
            txt = f"*Графік на {d_n}:*"
            for g in g_s:
                txt = f"{txt} {g}"
            txt = txt.replace("+", "\\+")
            txt = txt.replace("-", "\\-")
            bot.reply_to(message, txt, parse_mode='MarkdownV2') # FIXME edit later
        else:
            bot.reply_to(message, f"Графік на {day_name} відсутній! 😢")     

    @bot.message_handler(commands=['get_last_available'])
    def get_last_available(message):
        db_day = db_days.get_all_days_from_database()[-1]
        d_n, *g_s = db_day
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