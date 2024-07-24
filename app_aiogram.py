import os
from dotenv import load_dotenv
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.utils import formatting

from db_day_handler import DB_Days
from db_user_handler import DB_Users


def configure():
    load_dotenv()

def generate_settings_content(db, user_id:str):
    user_settings = db.get_user(user_id=user_id)
    _, auto_send, off_emoji, on_emoji, *groups_to_show, view, total= user_settings
    groups_to_show_str = ", ".join([str(x) for x in range(1, 7) if groups_to_show[x-1]])
    return formatting.Text(
        formatting.Bold("📮Авторозсилка"), " : ", formatting.Code(f"{'ON' if auto_send else 'OFF'}"), "\n",
        formatting.BotCommand("/change_auto_send"), " - ", formatting.Italic(f"{'ввімкнути' if auto_send else 'вимкнути'} авторозсилку"), "\n",
        "\n",
        formatting.Bold("🕯Емоджі відключення"), " : ", formatting.Code(f"{off_emoji}"), "\n",
        formatting.BotCommand("/set_emoji_off"), " - ", formatting.Italic("text"), "\n",
        "\n",
        formatting.Bold("💡Емоджі включення"), " : ", formatting.Code(f"{on_emoji}"), "\n",
        formatting.BotCommand("/set_emoji_on"), " - ", formatting.Italic("text"), "\n",
        "\n",
        formatting.Bold("🔠Мої групи"), " : ", formatting.Code(f"[{groups_to_show_str}]"), "\n",
        formatting.BotCommand("/add_group"), " - ", formatting.Italic("text"), "\n",
        formatting.BotCommand("/remove_group"), " - ", formatting.Italic("text"), "\n",
        "\n",
        formatting.Bold("🖼Вигляд"), " : ", formatting.Code(f"{view}"), "\n",
        formatting.BotCommand("/set_view"), " - ", formatting.Italic("text"), "\n",
        "\n",
        formatting.Bold("🧮Підсумок"), " : ", formatting.Code(f"{total}"), "\n",
        formatting.BotCommand("/set_total"), " - ", formatting.Italic("text")
        )

configure()
TOKEN = os.getenv('TOKEN')
MY_USER_ID = os.getenv('MY_USER_ID')
LINK = os.getenv('LINK')

DATABASE_FILENAME = "small_db_aiogram.sql"
db_users = DB_Users(db_filename=DATABASE_FILENAME)
db_days = DB_Days(db_filename=DATABASE_FILENAME)


bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command('start'))
async def start(message: types.Message):
    if not db_users.is_user_id_exists(user_id=message.from_user.id): 
        db_users.add_user(user_id=message.from_user.id)
        content = formatting.Text(
            "Привіт, ", formatting.Bold(message.from_user.full_name), "!👋\n",
            "\n",
            formatting.BotCommand("/help"), " - ", formatting.Italic("допомога"), "\n", 
            formatting.BotCommand("/info"), " - ", formatting.Italic("інфо"), "\n",
            formatting.BotCommand("/settings"), " - ", formatting.Italic("налаштування"), "\n",
            )
        await message.answer(**content.as_kwargs())
    else:
        content = formatting.Text(
            "Привіт, ", formatting.Bold(message.from_user.full_name), "!", " Давно не бачились!😏",
            )
        await message.answer(**content.as_kwargs())

@dp.message(Command('help'))
async def help(message: types.Message):
    # TODO implements help()
    content = formatting.Text(
            "<🆘Список корисних команд🆘>",
            )
    await message.answer(**content.as_kwargs())

@dp.message(Command('info'))
async def info(message: types.Message):
    # TODO implements info()
    content = formatting.Text(
            "<🆘Інформація про бота🆘>",
            )
    await message.answer(**content.as_kwargs())

@dp.message(Command('settings'))
async def settings(message: types.Message):
    user_settings_content = generate_settings_content(db=db_users, user_id=message.from_user.id)
    await message.reply(**user_settings_content.as_kwargs())

@dp.message(Command('change_auto_send'))
async def change_auto_send(message: types.Message):
    db_users.change_auto_send(user_id=message.from_user.id)
    user_settings_content = generate_settings_content(db=db_users, user_id=message.from_user.id)
    await message.reply(**user_settings_content.as_kwargs())

@dp.message(Command('set_emoji_off'))
async def set_emoji_off(message: types.Message):
    #TODO implement set_emoji_off()
    content = formatting.Text(
            "<🆘Змінити EMOJI_OFF🆘>",
            )
    await message.answer(**content.as_kwargs())

@dp.message(Command('set_emoji_on'))
async def set_emoji_on(message: types.Message):
    #TODO implement set_emoji_on()
    content = formatting.Text(
            "<🆘Змінити EMOJI_ON🆘>",
            )
    await message.answer(**content.as_kwargs())

@dp.message(Command('add_group'))
async def add_group(message: types.Message):
    #TODO implement add_group()
    content = formatting.Text(
            "<🆘Добавити групу🆘>",
            )

    groups_markup = types.ReplyKeyboardMarkup()
    # groups_markup.add("1").add("2").add("3").add("4").add("5").add("6")
    await message.answer(**content.as_kwargs(), reply_markup=groups_markup)

@dp.message(Command('remove_group'))
async def remove_group(message: types.Message):
    #TODO implement remove_group()
    content = formatting.Text(
            "<🆘Видалити групу🆘>",
            )
    await message.answer(**content.as_kwargs())

@dp.message(Command('set_view'))
async def set_view(message: types.Message):
    #TODO implement set_view()
    content = formatting.Text(
            "<🆘Змінити вигляд🆘>",
            )
    await message.answer(**content.as_kwargs())

@dp.message(Command('set_total'))
async def set_total(message: types.Message):
    #TODO implement set_total()
    content = formatting.Text(
            "<🆘Змінити підсумок🆘>",
            )
    await message.answer(**content.as_kwargs())






















@dp.message(Command('get_today'))
async def get_today(message: types.Message):
    #TODO implement get_today()
    content = formatting.Text(
            "<🆘Погода на сьогодні🆘>",
            )
    await message.answer(**content.as_kwargs())

@dp.message(Command('get_tomorrow'))
async def get_tomorrow(message: types.Message):
    #TODO implement get_tomorrow()
    content = formatting.Text(
            "<🆘Погода на завтра🆘>",
            )
    await message.answer(**content.as_kwargs())

@dp.message(Command('update'))
async def update(message: types.Message):
    #TODO implement update()
    content = formatting.Text(
            "<🆘Оновлення бази дани по графіках🆘>",
            )
    await message.answer(**content.as_kwargs())








async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())