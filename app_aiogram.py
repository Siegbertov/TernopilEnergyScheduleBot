import os
from dotenv import load_dotenv
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
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

@dp.message(CommandStart())
async def command_start(message: types.Message):
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
async def command_help(message: types.Message):
    # TODO implements help()
    content = formatting.Text(
            "<🆘Список корисних команд🆘>",
            )
    await message.answer(**content.as_kwargs())

@dp.message(Command('info'))
async def command_info(message: types.Message):
    # TODO implements info()
    content = formatting.Text(
            "<🆘Інформація про бота🆘>",
            )
    await message.answer(**content.as_kwargs())

@dp.message(Command('settings'))
async def command_settings(message: types.Message):
    user_settings_content = generate_settings_content(db=db_users, user_id=message.from_user.id)
    await message.reply(**user_settings_content.as_kwargs())

@dp.message(Command('change_auto_send'))
async def command_change_auto_send(message: types.Message):
    db_users.change_auto_send(user_id=message.from_user.id)
    status = db_users.get_auto_send_status(user_id=message.from_user.id)
    content = formatting.Text(
        formatting.Bold("📮Авторозсилка"), " : ", formatting.Code(f"{'ON' if status else 'OFF'}"), "\n",
        formatting.BotCommand("/change_auto_send"), " - ", formatting.Italic(f"{'ввімкнути' if status else 'вимкнути'} авторозсилку"), "\n",
        "\n"
    )
    await message.reply(**content.as_kwargs())

@dp.message(Command('set_emoji_off'))
async def command_set_emoji_off(message: types.Message):
    #TODO implement set_emoji_off()
    content = formatting.Text(
            "<🆘Змінити EMOJI_OFF🆘>",
            )
    await message.answer(**content.as_kwargs())

@dp.message(Command('set_emoji_on'))
async def command_set_emoji_on(message: types.Message):
    #TODO implement set_emoji_on()
    content = formatting.Text(
            "<🆘Змінити EMOJI_ON🆘>",
            )
    await message.answer(**content.as_kwargs())

@dp.message(Command('add_group'))
async def command_add_group(message: types.Message):
    groups = db_users.get_groups(user_id=message.from_user.id)
    groups_to_show_str = ", ".join([str(x) for x in range(1, 7) if groups[x-1]])
    content = formatting.Text(
                formatting.Bold("🔠Мої групи"), " : ", formatting.Code(f"[{groups_to_show_str}]"), 
                )
    kb = []
    kb.append([types.KeyboardButton(text=f"Скасувати")])
    groups = db_users.get_groups(user_id=message.from_user.id)
    for group in [str(x) for x in db_users.possible_groups if not groups[int(x)-1]]:
        kb.append([types.KeyboardButton(text=f"+{group}")])
    rkm = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="(номер групи)", one_time_keyboard=True, selective=True)
    await message.answer(**content.as_kwargs(), reply_markup=rkm)

@dp.message(Command('remove_group'))
async def command_remove_group(message: types.Message):
    content = formatting.Text(
            "<🆘Видалити групу🆘>",
            )
    kb = []
    kb.append([types.KeyboardButton(text=f"Скасувати")])
    groups = db_users.get_groups(user_id=message.from_user.id)
    for group in [str(x) for x in db_users.possible_groups if groups[int(x)-1]]:
        kb.append([types.KeyboardButton(text=f"-{group}")])
    rkm = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="(номер групи)", one_time_keyboard=True, selective=True)
    await message.answer(**content.as_kwargs(), reply_markup=rkm)

@dp.message(Command('set_view'))
async def command_set_view(message: types.Message):
    #TODO implement set_view()
    current_view = db_users.get_view(user_id=message.from_user.id)
    content = formatting.Text(
            formatting.Bold("🖼Вигляд"), " : ", formatting.Code(current_view)
            )
    kb = []
    kb.append([types.KeyboardButton(text=f"Скасувати")])
    for view in db_users.possible_views:
        if view != current_view:
            kb.append([types.KeyboardButton(text=view)])
    rkm = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="(номер групи)", one_time_keyboard=True, selective=True)
    await message.reply(**content.as_kwargs(), reply_markup=rkm)

@dp.message(Command('set_total'))
async def command_set_total(message: types.Message):
    #TODO implement set_total()
    content = formatting.Text(
            "<🆘Змінити підсумок🆘>",
            )
    await message.answer(**content.as_kwargs())

@dp.message()
async def text_message(message: types.Message):
    txt = message.text
    match txt:
        case txt if txt in ["+1", "+2", "+3", "+4", "+5", "+6"]:
            content = formatting.Text( "✅" )
            db_users.add_group(user_id=message.from_user.id, num_to_add=txt[1])
            await message.reply(**content.as_kwargs())
            await command_add_group(message=message)
        case txt if txt in ["-1", "-2", "-3", "-4", "-5", "-6"]:
            content = formatting.Text( "✅" )
            db_users.remove_group(user_id=message.from_user.id, num_to_remove=txt[1])
            await message.reply(**content.as_kwargs())
            await command_remove_group(message=message)
        case txt if txt in db_users.possible_views:
            db_users.set_new_view(user_id=message.from_user.id, new_view=txt)
            await command_set_view(message=message)
        case txt if txt in ["Скасувати"]:
            content = formatting.Text(
                    "❌",
                    )
            await message.reply(**content.as_kwargs(), reply_markup=types.ReplyKeyboardRemove())
        case _:
            pass




















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