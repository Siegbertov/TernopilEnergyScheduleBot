import os
from dotenv import load_dotenv
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.utils.formatting import Text, Bold, Italic, Code, BotCommand
from aiogram.types.error_event import ErrorEvent
from aiogram.exceptions import TelegramForbiddenError

from day import Day
from utils import edit_time_period, pretty_time
from utils import get_today_name_year, get_tomorrow_name_year

from async_scrapping import scrap_current_day_month_group
from async_day_handler import A_DB_Days
from async_user_handler import A_DB_Users

from datetime import datetime
import math
import time

# TODO LOGGING
# TODO GROUP or CHAT HANDLING
# TODO HUGE refactoring
# TODO ERROR HANDLING

# LOADING ENV
load_dotenv()

# ADMIN's stuff
ADMINS = []
MY_USER_ID = os.getenv('MY_USER_ID')
ADMINS.append(MY_USER_ID)

# DATABASE's stuff
DATABASE_FILENAME = "small_db_aiogram.sql"
# db_users = DB_Users(db_filename=DATABASE_FILENAME)
a_db_users = A_DB_Users(db_filename=DATABASE_FILENAME)
a_db_days = A_DB_Days(db_filename=DATABASE_FILENAME)
DB_UPDATE_SECONDS = 60

# BOT's stuff
TOKEN = os.getenv('TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher()

# SCRAPPING's stuff
LINK = os.getenv('LINK')
DAY_MONTH_R = r", (\d+) (\w+),?"
GROUP_R = r"(\d\d:\d\d)-(\d\d:\d\d)\s+(\d)\s+\w+"

async def generate_settings_content(db, user_id:str):
    user_settings = await db.get_user(user_id=user_id)
    _, auto_send, off_emoji, on_emoji, *groups_to_show, view, total= user_settings
    groups_to_show_str = ", ".join([str(x) for x in range(1, 7) if groups_to_show[x-1]])
    return Text(
        Bold("📮Авторозсилка"), " : ", Code(f"{'ON' if auto_send else 'OFF'}"), "\n",
        BotCommand("/change_auto_send"), " - ", Italic(f"{'вимкнути' if auto_send else 'ввімкнути'} авторозсилку"), "\n",
        "\n",
        Bold("🕯Емодзі відключення"), " : ", Code(f"{off_emoji}"), "\n",
        BotCommand("/set_emoji_off"), " - ", Italic("встановити новий emoji для відключення"), "\n",
        "\n",
        Bold("💡Емодзі включення"), " : ", Code(f"{on_emoji}"), "\n",
        BotCommand("/set_emoji_on"), " - ", Italic("встановити новий emoji для включення"), "\n",
        "\n",
        Bold("🔠Мої групи"), " : ", Code(f"[{groups_to_show_str}]"), "\n",
        BotCommand("/add_group"), " - ", Italic("добавити групу"), "\n",
        BotCommand("/remove_group"), " - ", Italic("видалити групу"), "\n",
        "\n",
        Bold("🖼Вигляд"), " : ", Code(f"{view}"), "\n",
        BotCommand("/set_view"), " - ", Italic("змінити вигляд графіку"), "\n",
        "\n",
        Bold("🧮Підсумок"), " : ", Code(f"{total}"), "\n",
        BotCommand("/set_total"), " - ", Italic("змінити показ підсумку")
        )

# DEFAULT on_startup()
async def on_startup(bot: Bot):
    await a_db_days.create_table()
    for ADMIN_ID in ADMINS:
        txt = "🔥🎉🍾*БОТ ЗАПУЩЕНИЙ*🍾🎉🔥\n\n"
        txt += "/update \\- _оновити графіки_\n"
        txt += "/notify \\- _повідомити всіх_\n"
        txt += "/my\\_test\\_command \\- _актуальна тестова команда_\n"
        await bot.send_message(chat_id=int(ADMIN_ID), text=txt, parse_mode="MarkdownV2")

dp.startup.register(on_startup)

async def scrap_and_update()->None:
    today_name, today_year = get_today_name_year()
    tomorrow_name, tomorrow_year = get_tomorrow_name_year()
    DAYS = await scrap_current_day_month_group(link=LINK, days=[tomorrow_name, today_name], day_month_r=DAY_MONTH_R, group_r=GROUP_R)
    await a_db_days.add_day(day_name=today_name, day_year=today_year, groups=DAYS[today_name])
    await a_db_days.add_day(day_name=tomorrow_name, day_year=tomorrow_year, groups=DAYS[tomorrow_name])

# COMMANDS
@dp.message(CommandStart())
async def command_start(message: types.Message):
    content = Text(  
            BotCommand("/help"), " - ", Italic("список команд"), "\n",
            )
    if not await a_db_users.exists(user_id=message.from_user.id): 
        await a_db_users.add_user(user_id=message.from_user.id)
        content = Text(
            "Привіт, ", Bold(message.from_user.full_name), "!👋\n",
            "\n",) + content
        await message.answer(**content.as_kwargs())
    else:
        content = Text(
            "Привіт, ", Bold(message.from_user.full_name), ", давно не бачились!😏", "\n") + content
        if str(message.from_user.id) in ADMINS:
            content += Text(
                "\n",
                Italic("Cпеціально для адмінів:😉"), "\n",
                BotCommand("/update"), " - ", Italic("перевірити графіки"), "\n",
                BotCommand("/notify"), " - ", Italic("повідомити всіх"), "\n",
                BotCommand("/my_test_command"), ' - ', Italic("актуальна тестова команда"), "\n",
                )
        await message.answer(**content.as_kwargs())

@dp.message(Command('my_test_command'))
async def command_my_test_command(message: types.Message):
    if str(message.from_user.id) in ADMINS:
         rest = message.text.split("my_test_command")[-1]
         await bot.send_message(chat_id=message.from_user.id, text=rest)

@dp.message(Command('notify'))
async def command_notify(message: types.Message):
    if str(message.from_user.id) in ADMINS:
        rest = message.text.split("notify")[-1]
        if rest.strip():
            for auto_send_user in await a_db_users.get_all_auto_send_users(auto_send_value=1):
                try:
                    await bot.send_message(chat_id=int(auto_send_user), text=rest.strip())
                except Exception as e:
                    if isinstance(e, TelegramForbiddenError):
                        await a_db_users.delete_user(user_id=auto_send_user)
                    else:
                        print(e)
                        print(f"Problem with: {auto_send_user}")

@dp.message(Command('update'))
async def command_update(message: types.Message):
    if str(message.from_user.id) in ADMINS:
        await scrap_and_update()
        context = Text(
                Bold("Графіки оновленні!"), "\n",
                "\n",
                Italic(f"🔄{datetime.now().strftime("%d.%m %H:%M:%S")}🔄")
            )
        await message.answer(**context.as_kwargs())
        await message.delete()

@dp.message(Command('help'))
async def command_help(message: types.Message):
    content = Text(
            Bold("Список команд:"), "\n",
            "\n",
            BotCommand("/info"), " - ", Italic("інформація про бота"), "\n",
            BotCommand("/settings"), " - ", Italic("перейти до налаштувань"), "\n",
            BotCommand("/today"), " - ", Italic("показати графік на сьогодні"), "\n",
            BotCommand("/tomorrow"), " - ", Italic("показати графік на завтра"), "\n",
            )
    await message.answer(**content.as_kwargs())

@dp.message(Command('info'))
async def command_info(message: types.Message):
    content = Text(
            Bold("<🆘#TODO інформація про бота🆘>"), "\n",
            "\n",
            Code("бла-бла-бла-бла"), "\n",
            Code("бла-бла-бла-бла"), "\n",
            Code("бла-бла-бла-бла"), "\n",
            )
    await message.answer(**content.as_kwargs())

@dp.message(Command('settings'))
async def command_settings(message: types.Message):
    user_settings_content = await generate_settings_content(db=a_db_users, user_id=message.from_user.id)
    await message.reply(**user_settings_content.as_kwargs())

@dp.message(Command('change_auto_send'))
async def command_change_auto_send(message: types.Message):
    await a_db_users.change_auto_send(user_id=message.from_user.id)
    status = await a_db_users.get_auto_send_status(user_id=message.from_user.id)
    content = Text(
        Bold("📮Авторозсилка"), " : ", Code(f"{'ON' if status else 'OFF'}"), "\n",
        BotCommand("/change_auto_send"), " - ", Italic(f"{'вимкнути' if status else  'ввімкнути'} авторозсилку"), "\n",
        "\n"
    )
    await message.reply(**content.as_kwargs())

@dp.message(Command('set_emoji_off'))
async def command_set_emoji_off(message: types.Message):
    content = Text(
            "<Вибери emoji для відключень>", "\n"
            )
    BTN_COLS = 4
    buttons = []
    OFF_EMOJIS = a_db_users.POSSIBLE_OFF_EMOJIS
    for i in range(math.ceil(len(OFF_EMOJIS)/BTN_COLS)):
        current_row = []
        for emoji in OFF_EMOJIS[i*BTN_COLS : i*BTN_COLS+BTN_COLS]:
            # await message.answer(text=f"{em}")
            current_row.append(types.InlineKeyboardButton(text=emoji, callback_data=f"cb_set_emoji_off_{emoji}"))
        buttons.append(current_row)
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.reply(**content.as_kwargs(), reply_markup=keyboard)

@dp.message(Command('set_emoji_on'))
async def command_set_emoji_on(message: types.Message):
    content = Text(
            "<Вибери emoji для включень>", "\n"
            )
    BTN_COLS = 4
    buttons = []
    ON_EMOJIS = a_db_users.POSSIBLE_ON_EMOJIS
    for i in range(math.ceil(len(ON_EMOJIS)/BTN_COLS)):
        current_row = []
        for emoji in ON_EMOJIS[i*BTN_COLS : i*BTN_COLS+BTN_COLS]:
            # await message.answer(text=f"{em}")
            current_row.append(types.InlineKeyboardButton(text=emoji, callback_data=f"cb_set_emoji_on_{emoji}"))
        buttons.append(current_row)
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons,)
    await message.reply(**content.as_kwargs(), reply_markup=keyboard)

@dp.callback_query(F.data.startswith("cb_set_emoji_"))
async def callback_set_emoji(callback: types.CallbackQuery):
    *_, action, emoji = callback.data.split("_")
    match action:
        case "on":
            await a_db_users.set_new_on_emoji(user_id=callback.from_user.id, new_on_emoji=emoji)
            content = Text(
                Bold(f"💡Емодзі включення : {emoji}")
            )
            await callback.message.edit_text(**content.as_kwargs())
        case "off":
            await a_db_users.set_new_off_emoji(user_id=callback.from_user.id, new_off_emoji=emoji)
            content = Text(
                Bold(f"🕯Емодзі відключення : {emoji}")
            )
            await callback.message.edit_text(**content.as_kwargs())

@dp.message(Command('add_group'))
async def command_add_group(message: types.Message):
    groups = await a_db_users.get_groups(user_id=message.from_user.id)
    groups_to_show_str = ", ".join([str(x) for x in range(1, 7) if groups[x-1]])
    content = Text(
                Bold("🔠Мої групи"), " : ", Code(f"[{groups_to_show_str}]"), 
                )
    kb = []
    kb.append([types.KeyboardButton(text=f"Скасувати")])
    second_row = []
    for group in [str(x) for x in a_db_users.POSSIBLE_GROUPS if not groups[int(x)-1]]:
        second_row.append(types.KeyboardButton(text=f"+{group}"))
    kb.append(second_row)
    rkm = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="(номер групи)", one_time_keyboard=True, selective=True)
    await message.answer(**content.as_kwargs(), reply_markup=rkm)

@dp.message(Command('remove_group'))
async def command_remove_group(message: types.Message):
    groups = await a_db_users.get_groups(user_id=message.from_user.id)
    groups_to_show_str = ", ".join([str(x) for x in range(1, 7) if groups[x-1]])
    content = Text(
                Bold("🔠Мої групи"), " : ", Code(f"[{groups_to_show_str}]"), 
                )
    kb = []
    kb.append([types.KeyboardButton(text=f"Скасувати")])
    second_row = []
    for group in [str(x) for x in a_db_users.POSSIBLE_GROUPS if groups[int(x)-1]]:
        second_row.append(types.KeyboardButton(text=f"-{group}"))
    kb.append(second_row)
    rkm = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="(номер групи)", one_time_keyboard=True, selective=True)
    await message.answer(**content.as_kwargs(), reply_markup=rkm)

@dp.message(Command('set_view'))
async def command_set_view(message: types.Message):
    current_view = await a_db_users.get_view(user_id=message.from_user.id)
    content = Text(
            Bold("<Вибери новий вигляд>"), "\n",
            )
    buttons = []
    for view in a_db_users.POSSIBLE_VIEWS:
        if view != current_view:
            buttons.append([types.InlineKeyboardButton(text=view, callback_data=f"cb_set_view_{view}")])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.reply(**content.as_kwargs(), reply_markup=keyboard)

@dp.callback_query(F.data.startswith("cb_set_view_"))
async def callback_set_view(callback: types.CallbackQuery):
    new_view = callback.data.split("cb_set_view_")[-1]
    await a_db_users.set_new_view(user_id=callback.from_user.id, new_view=new_view)
    content = Text(
                Bold("🖼Новий вигляд : "), Code(new_view), "\n"
            )
    await callback.message.edit_text(**content.as_kwargs())

@dp.message(Command('set_total'))
async def command_set_total(message: types.Message):
    current_total = await a_db_users.get_total(user_id=message.from_user.id)
    content = Text(
            Bold("<Вибери новий підсумок>"), "\n",
            )
    buttons = []
    for total in a_db_users.POSSIBLE_TOTALS:
        if total != current_total:
            buttons.append([types.InlineKeyboardButton(text=total, callback_data=f"cb_set_total_{total}")])
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.reply(**content.as_kwargs(), reply_markup=keyboard)

@dp.callback_query(F.data.startswith("cb_set_total_"))
async def callback_set_total(callback: types.CallbackQuery):
    new_total = callback.data.split("cb_set_total_")[-1]
    await a_db_users.set_new_total(user_id=callback.from_user.id, new_total=new_total)
    content = Text(
                Bold("🧮Новий підсумок : "), Code(new_total), "\n"
            )
    await callback.message.edit_text(**content.as_kwargs())

@dp.message(Command('today'))
async def command_today(message: types.Message):
    some_day, some_year = get_today_name_year()
    content = Text( Bold(f"Графік на {some_day}:"), "\n")
    if await a_db_days.exists(day_name=some_day, day_year=some_year):
        groups_d = await a_db_days.get_day_groups_as_dict(day_name=some_day, day_year=some_year)
        user_settings = await a_db_users.get_user(user_id=message.from_user.id)
        _, _, off_emoji, on_emoji, *groups_to_show, view, total= user_settings
        groups_to_show_l = [str(x) for x in range(1, 7) if groups_to_show[x-1]]
        day = Day(name=some_day, groups=groups_d)
        NUMS_and_VIEWS_and_TOTALS_L = day.get(groups_to_show=groups_to_show_l, view=view, total=total)
        if NUMS_and_VIEWS_and_TOTALS_L:
            for num_and_view_and_total_l in NUMS_and_VIEWS_and_TOTALS_L:
                n, v_s, t = num_and_view_and_total_l
                content += Text(
                    Bold(f"\nГрупа #{n}:",'\n')
                )
                for v in v_s:
                    if v is not None:
                        current_line = v.replace(":00", "").replace("-", off_emoji).replace("+", on_emoji)
                        content += Text(
                            Code(f"{edit_time_period(current_line)}"), "\n"
                        )
                if t is None:
                    pass
                else:
                    if t == (0, 0):
                        content += Text(Italic(f"{ '(без виключень)' if total=='TOTAL_OFF' else '(без включень)'}"), "\n")
                    else:
                        content += Text(Italic(f"{ f'🕯{pretty_time(t)}🕯' if total=='TOTAL_OFF' else f'💡{pretty_time(t)}💡'}"), "\n")
        else:
            content += Text( 
                "\n", 
                BotCommand("/add_group"), " - ", Italic("добавити групу"), "\n"
                )
        await message.answer(**content.as_kwargs())
    else:
        content += Text(  
                Italic("<графік відсутній>"), "\n"
                )
        await message.answer(**content.as_kwargs())

@dp.message(Command('tomorrow'))
async def command_tomorrow(message: types.Message):
    some_day, some_year = get_tomorrow_name_year()
    content = Text( Bold(f"Графік на {some_day}:"), "\n")
    if await a_db_days.exists(day_name=some_day, day_year=some_year):
        groups_d = await a_db_days.get_day_groups_as_dict(day_name=some_day, day_year=some_year)
        user_settings = await a_db_users.get_user(user_id=message.from_user.id)
        _, _, off_emoji, on_emoji, *groups_to_show, view, total= user_settings
        groups_to_show_l = [str(x) for x in range(1, 7) if groups_to_show[x-1]]
        day = Day(name=some_day, groups=groups_d)
        NUMS_and_VIEWS_and_TOTALS_L = day.get(groups_to_show=groups_to_show_l, view=view, total=total)
        if NUMS_and_VIEWS_and_TOTALS_L:
            for num_and_view_and_total_l in NUMS_and_VIEWS_and_TOTALS_L:
                n, v_s, t = num_and_view_and_total_l
                content += Text(
                    Bold(f"\nГрупа #{n}:",'\n')
                )
                for v in v_s:
                    if v is not None:
                        current_line = v.replace(":00", "").replace("-", off_emoji).replace("+", on_emoji)
                        content += Text(
                            Code(f"{edit_time_period(current_line)}"), "\n"
                        )
                if t is None:
                    pass
                else:
                    if t == (0, 0):
                        content += Text(Italic(f"{ '(без виключень)' if total=='TOTAL_OFF' else '(без включень)'}"), "\n")
                    else:
                        content += Text(Italic(f"{ f'🕯{pretty_time(t)}🕯' if total=='TOTAL_OFF' else f'💡{pretty_time(t)}💡'}"), "\n")
        else:
            content += Text( 
                "\n", 
                BotCommand("/add_group"), " - ", Italic("добавити групу"), "\n"
                )
        await message.answer(**content.as_kwargs())
    else:
        content += Text(  
                Italic("\n<графік відсутній>")
                )
        await message.answer(**content.as_kwargs())

@dp.message()
async def text_message(message: types.Message):
    txt = message.text
    match txt:
        case txt if txt in ["+1", "+2", "+3", "+4", "+5", "+6"]:
            content = Text( "✅" )
            await a_db_users.add_group(user_id=message.from_user.id, num_to_add=txt[1])
            await message.reply(**content.as_kwargs())
            await command_add_group(message=message)
        case txt if txt in ["-1", "-2", "-3", "-4", "-5", "-6"]:
            content = Text( "✅" )
            await a_db_users.remove_group(user_id=message.from_user.id, num_to_remove=txt[1])
            await message.reply(**content.as_kwargs())
            await command_remove_group(message=message)
        case txt if txt in ["Скасувати"]:
            content = Text(
                    "❌",
                    )
            await message.reply(**content.as_kwargs(), reply_markup=types.ReplyKeyboardRemove())
        case _:
            pass

async def my_func_1():
    while True:
        
        start = time.time()    

        # updating database
        await scrap_and_update()

        # sending # TODO make function for this
        NOT_DISTRIBUTED_DAYS = await a_db_days.get_all_not_distributed_days()
        if bool(NOT_DISTRIBUTED_DAYS):
            AUTO_SEND_USERS = await a_db_users.get_all_auto_send_users(auto_send_value=1)
            for NOT_DISTRIBUTED_DAY in NOT_DISTRIBUTED_DAYS:
                _, day_name, _,  *groups, _ = NOT_DISTRIBUTED_DAY
                for AUTO_SEND_USER in AUTO_SEND_USERS:
                    txt = f"*Графік на {day_name}:*\n"
                    user_settings = await a_db_users.get_user(user_id=int(AUTO_SEND_USER))
                    _, _, off_emoji, on_emoji, *groups_to_show, view, total= user_settings

                    groups_to_show_l = [x for x in range(1, 7) if groups_to_show[x-1]]
                    groups_d = {(k+1):v for k, v in enumerate(groups)}
                    day = Day(name=day_name, groups=groups_d)
                    NUMS_and_VIEWS_and_TOTALS_L = day.get(groups_to_show=groups_to_show_l, view=view, total=total)
                    if NUMS_and_VIEWS_and_TOTALS_L:
                        for num_and_view_and_total_l in NUMS_and_VIEWS_and_TOTALS_L:
                            n, v_s, t = num_and_view_and_total_l
                            txt += f"\n*Група \\#{n}:*\n"
                            for v in v_s:
                                if v is not None:
                                    current_line = v.replace(":00", "").replace("-", off_emoji).replace("+", on_emoji)
                                    txt += f"`{edit_time_period(current_line)}`\n"
                            if t is None:
                                pass
                            else:
                                if t == (0, 0):
                                    txt += f"_{ '(без виключень)' if total=='TOTAL_OFF' else '(без включень)'}_\n"
                                else:
                                    txt += f"_{ f'🕯{pretty_time(t)}🕯' if total=='TOTAL_OFF' else f'💡{pretty_time(t)}💡'}_\n"
                    else:
                        txt += "\n/add\\_group \\- _добавити групу_\n"
                    txt = txt.replace('(', '\\(').replace(')', '\\)')
                    try:
                        await bot.send_message(chat_id=int(AUTO_SEND_USER), text=txt.replace('.', '\\.'), parse_mode="MarkdownV2")
                    except Exception as e:
                        if isinstance(e, TelegramForbiddenError):
                            await a_db_users.delete_user(user_id=AUTO_SEND_USER)
                        else:
                            print(e)
                            print(f"Problem with: {AUTO_SEND_USER}")
                        
                        

        #     # updating 
            await a_db_days.set_all_was_distributed()

        print(f"Job was done for <{time.time() - start}>")
        await asyncio.sleep(delay=DB_UPDATE_SECONDS)
        
async def my_func_2():
    await dp.start_polling(bot)

async def main():
    await asyncio.gather(my_func_1(), my_func_2())
    

if __name__ == "__main__":

    asyncio.run(main())