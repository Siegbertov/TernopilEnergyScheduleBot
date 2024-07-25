import os
from dotenv import load_dotenv
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.utils import formatting

from db_day_handler import DB_Days
from db_user_handler import DB_Users
from day import Day
from utils import edit_time_period, scrapper, get_today_name, get_tomorrow_name, pretty_time
from datetime import datetime

# TODO implements command /today | /tomorrow from other file
# TODO REFACTOR it

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
        formatting.BotCommand("/set_emoji_off"), " - ", formatting.Italic("встановитии новий emoji для відключення"), "\n",
        "\n",
        formatting.Bold("💡Емоджі включення"), " : ", formatting.Code(f"{on_emoji}"), "\n",
        formatting.BotCommand("/set_emoji_on"), " - ", formatting.Italic("встановитии новий emoji для включення"), "\n",
        "\n",
        formatting.Bold("🔠Мої групи"), " : ", formatting.Code(f"[{groups_to_show_str}]"), "\n",
        formatting.BotCommand("/add_group"), " - ", formatting.Italic("добавити групу"), "\n",
        formatting.BotCommand("/remove_group"), " - ", formatting.Italic("видалити групу"), "\n",
        "\n",
        formatting.Bold("🖼Вигляд"), " : ", formatting.Code(f"{view}"), "\n",
        formatting.BotCommand("/set_view"), " - ", formatting.Italic("змінити вигляд графіку"), "\n",
        "\n",
        formatting.Bold("🧮Підсумок"), " : ", formatting.Code(f"{total}"), "\n",
        formatting.BotCommand("/set_total"), " - ", formatting.Italic("змінити показ підсумку")
        )

configure()
TOKEN = os.getenv('TOKEN')
LINK = os.getenv('LINK')

ADMINS = []
MY_USER_ID = os.getenv('MY_USER_ID')
ADMINS.append(MY_USER_ID)

DATABASE_FILENAME = "small_db_aiogram.sql"
db_users = DB_Users(db_filename=DATABASE_FILENAME)
db_days = DB_Days(db_filename=DATABASE_FILENAME)


bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def command_start(message: types.Message):
    content = formatting.Text(  
            formatting.BotCommand("/help"), " - ", formatting.Italic("список команд"), "\n",
            )
    if not db_users.is_user_id_exists(user_id=message.from_user.id): 
        db_users.add_user(user_id=message.from_user.id)
        content = formatting.Text(
            "Привіт, ", formatting.Bold(message.from_user.full_name), "!👋\n",
            "\n",) + content
        await message.answer(**content.as_kwargs())
    else:
        content = formatting.Text(
            "Привіт, ", formatting.Bold(message.from_user.full_name), ", давно не бачились!😏", "\n") + content
        if str(message.from_user.id) in ADMINS:
            content += formatting.Text(
                "\n",
                formatting.Italic("Cпеціально для адмінів:😉"), "\n",
                formatting.BotCommand("/update"), " - ", formatting.Italic("перевірити графіки")
                )
        await message.answer(**content.as_kwargs())

@dp.message(Command('update'))
async def command_update(message: types.Message):
    if str(message.from_user.id) == str(MY_USER_ID):
        DAYS = scrapper(link=LINK, day_month_r=r"(\d+) (\w+),", group_r=r"(\d\d:\d\d)-(\d\d:\d\d)\s+(\d)\s+\w+")
        for day_name, groups in DAYS.items():
            db_days.add_day(day_name=day_name, groups=groups)
        now_time = datetime.now().strftime("%d.%m %H:%M:%S")
        context = formatting.Text(
                formatting.Bold("Графіки оновленні!"), "\n",
                "\n",
                formatting.Italic(f"🔄{now_time}🔄")
            )
        await message.answer(**context.as_kwargs())
        await message.delete()

@dp.message(Command('help'))
async def command_help(message: types.Message):
    content = formatting.Text(
            formatting.Bold("Список команд:"), "\n",
            "\n",
            formatting.BotCommand("/info"), " - ", formatting.Italic("інформація про бот"), "\n",
            formatting.BotCommand("/settings"), " - ", formatting.Italic("перейти до налаштувань"), "\n",
            formatting.BotCommand("/get_today"), " - ", formatting.Italic("показати графік на сьогодні"), "\n",
            formatting.BotCommand("/get_tomorrow"), " - ", formatting.Italic("показати графік на завтра"), "\n",
            )
    await message.answer(**content.as_kwargs())

@dp.message(Command('info'))
async def command_info(message: types.Message):
    content = formatting.Text(
            formatting.Bold("<🆘Інформація про бот🆘>"), "\n",
            "\n",
            formatting.Code("бла-бла-бла-бла"), "\n",
            formatting.Code("бла-бла-бла-бла"), "\n",
            formatting.Code("бла-бла-бла-бла"), "\n",
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
    groups = db_users.get_groups(user_id=message.from_user.id)
    groups_to_show_str = ", ".join([str(x) for x in range(1, 7) if groups[x-1]])
    content = formatting.Text(
                formatting.Bold("🔠Мої групи"), " : ", formatting.Code(f"[{groups_to_show_str}]"), 
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
    current_view = db_users.get_view(user_id=message.from_user.id)
    content = formatting.Text(
            formatting.Bold("🖼Вигляд"), " : ", formatting.Code(current_view)
            )
    kb = []
    kb.append([types.KeyboardButton(text=f"Скасувати")])
    for view in db_users.possible_views:
        if view != current_view:
            kb.append([types.KeyboardButton(text=view)])
    rkm = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="(вигляд)", one_time_keyboard=True, selective=True)
    await message.reply(**content.as_kwargs(), reply_markup=rkm)

@dp.message(Command('set_total'))
async def command_set_total(message: types.Message):
    current_total = db_users.get_total(user_id=message.from_user.id)
    content = formatting.Text(
            formatting.Bold("🧮Підсумок"), " : ", formatting.Code(current_total)
            )
    kb = []
    kb.append([types.KeyboardButton(text=f"Скасувати")])
    for total in db_users.possible_totals:
        if total != current_total:
            kb.append([types.KeyboardButton(text=total)])
    rkm = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="(вигляд)", one_time_keyboard=True, selective=True)
    await message.reply(**content.as_kwargs(), reply_markup=rkm)

@dp.message(Command('today'))
async def command_today(message: types.Message):
    some_day = get_today_name()
    content = formatting.Text( formatting.Bold(f"Графік на {some_day}:"), "\n")
    if db_days.exists(day_name=some_day):
        _, *some_day_groups_l = db_days.get_day(day_name=some_day)
        user_settings = db_users.get_user(user_id=message.from_user.id)
        _, auto_send, off_emoji, on_emoji, *groups_to_show, view, total= user_settings

        groups_to_show_l = [x for x in range(1, 7) if groups_to_show[x-1]]
        groups_d = {(k+1):v for k, v in enumerate(some_day_groups_l)}
        day = Day(name=some_day, groups=groups_d)
        NUMS_and_VIEWS_and_TOTALS_L = day.get(groups_to_show=groups_to_show_l, view=view, total=total)
        if NUMS_and_VIEWS_and_TOTALS_L:
            for num_and_view_and_total_l in NUMS_and_VIEWS_and_TOTALS_L:
                n, v_s, t = num_and_view_and_total_l
                content += formatting.Text(
                    formatting.Bold(f"\n#{n}:",'\n')
                )
                for v in v_s:
                    if v is not None:
                        current_line = v.replace(":00", "").replace("-", off_emoji).replace("+", on_emoji)
                        content += formatting.Text(
                            formatting.Code(f"{edit_time_period(current_line)}"), "\n"
                        )
                if t is None:
                    pass
                else:
                    if t == (0, 0):
                        content += formatting.Text(formatting.Italic(f"{ '(без виключень)' if total=='TOTAL_OFF' else '(без включень)'}"), "\n")
                    else:
                        content += formatting.Text(formatting.Italic(f"{ f'🕯{pretty_time(t)}🕯' if total=='TOTAL_OFF' else f'💡{pretty_time(t)}💡'}"), "\n")
        else:
            content += formatting.Text( 
                "\n", 
                formatting.BotCommand("/add_group"), " - ", formatting.Italic("добавити групу"), "\n"
                )
        await message.answer(**content.as_kwargs())
    else:
        content += formatting.Text(  
                formatting.Italic("<графік відсутній>"), "\n"
                )
        await message.answer(**content.as_kwargs())

@dp.message(Command('tomorrow'))
async def command_tomorrow(message: types.Message):
    some_day = get_tomorrow_name()
    content = formatting.Text( formatting.Bold(f"Графік на {some_day}:"), "\n")
    if db_days.exists(day_name=some_day):
        _, *some_day_groups_l = db_days.get_day(day_name=some_day)
        user_settings = db_users.get_user(user_id=message.from_user.id)
        _, auto_send, off_emoji, on_emoji, *groups_to_show, view, total= user_settings

        groups_to_show_l = [x for x in range(1, 7) if groups_to_show[x-1]]
        groups_d = {(k+1):v for k, v in enumerate(some_day_groups_l)}
        day = Day(name=some_day, groups=groups_d)
        NUMS_and_VIEWS_and_TOTALS_L = day.get(groups_to_show=groups_to_show_l, view=view, total=total)
        if NUMS_and_VIEWS_and_TOTALS_L:
            for num_and_view_and_total_l in NUMS_and_VIEWS_and_TOTALS_L:
                n, v_s, t = num_and_view_and_total_l
                content += formatting.Text(
                    formatting.Bold(f"\n#{n}:",'\n')
                )
                for v in v_s:
                    if v is not None:
                        current_line = v.replace(":00", "").replace("-", off_emoji).replace("+", on_emoji)
                        content += formatting.Text(
                            formatting.Code(f"{edit_time_period(current_line)}"), "\n"
                        )
                if t is None:
                    pass
                else:
                    if t == (0, 0):
                        content += formatting.Text(formatting.Italic(f"{ '(без виключень)' if total=='TOTAL_OFF' else '(без включень)'}"), "\n")
                    else:
                        content += formatting.Text(formatting.Italic(f"{ f'🕯{pretty_time(t)}🕯' if total=='TOTAL_OFF' else f'💡{pretty_time(t)}💡'}"), "\n")
        else:
            content += formatting.Text( 
                "\n", 
                formatting.BotCommand("/add_group"), " - ", formatting.Italic("добавити групу"), "\n"
                )
        await message.answer(**content.as_kwargs())
    else:
        content += formatting.Text(  
                formatting.Italic("<графік відсутній>"), "\n"
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
        case txt if txt in db_users.possible_totals:
            db_users.set_new_total(user_id=message.from_user.id, new_total=txt)
            await command_set_total(message=message)
        case txt if txt in ["Скасувати"]:
            content = formatting.Text(
                    "❌",
                    )
            await message.reply(**content.as_kwargs(), reply_markup=types.ReplyKeyboardRemove())
        case _:
            pass

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())