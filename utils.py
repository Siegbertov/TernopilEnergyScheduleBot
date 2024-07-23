import sqlite3
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def __parse_date_as_ukr(date:str)->str:
    MONTH_UA_OR = {
                            "01":"січня",
                            "02": "лютого",
                            "03":"березня",
                            "04": "квітня",
                            "05":"травня",
                            "06": "червня",
                            "07":"липня",
                            "08": "серпня",
                            "09":"вересня",
                            "10": "жовтня",
                            "11":"листопада",
                            "12": "грудня"
                        }
    day, month = date.split(" ")
    return f"{day} {MONTH_UA_OR[month]}"

def get_today_date_name()->str:
    some_day = datetime.today().strftime("%d %m")
    return __parse_date_as_ukr(some_day)

def get_tomorrow_date_name()->str:
    some_day = (datetime.today() + timedelta(days=1)).strftime("%d %m")
    return __parse_date_as_ukr(some_day) 


# FUNCTIONS FOR DATABASE <USERS>
def create_users_table(db_filename:str)->None:
    connection = sqlite3.connect(db_filename)
    cursor = connection.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
                                    user_id TEXT,
                                    auto_send INTEGER DEFAULT 0,
                                    off_emoji TEXT DEFAULT '🔴',
                                    on_emoji TEXT DEFAULT '🟢',
                                    first_g INTEGER DEFAULT 1,
                                    second_g INTEGER DEFAULT 1,
                                    third_g INTEGER DEFAULT 1,
                                    fouth_g INTEGER DEFAULT 1,
                                    fifth_g INTEGER DEFAULT 1,
                                    sixth_g INTEGER DEFAULT 1,
                                    view TEXT DEFAULT 'OFF_PAIRS',
                                    total TEXT DEFAULT 'NONE'
                                )""")
    connection.commit()
    cursor.close()
    connection.close()
    
def __is_user_id_in_database(db_filename:str, user_id:str)->bool:
    result = None
    connection = sqlite3.connect(db_filename)
    cursor = connection.cursor()

    result = bool(cursor.execute(f"SELECT * FROM users WHERE user_id=:user_id", {'user_id':user_id}).fetchone())

    connection.commit()
    cursor.close()
    connection.close()

    return result

def __add_user(db_filename:str, user_id:str):
    connection = sqlite3.connect(db_filename)
    cursor = connection.cursor()

    cursor.execute(f"INSERT INTO users (user_id) VALUES ({user_id})")
    connection.commit()
    cursor.close()
    connection.close()  

# FUNCTIONS FOR DATABASE <DAYS>
def create_days_table(db_filename:str)->None:
    connection = sqlite3.connect(db_filename)
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

def get_all_days_from_database(db_filename:str) ->list:
    result = None
    connection = sqlite3.connect(db_filename)
    cursor = connection.cursor()

    result = cursor.execute(f"SELECT * FROM days").fetchall()

    connection.commit()
    cursor.close()
    connection.close()

    return result

def get_last_day_from_database(db_filename:str) ->tuple:
    return get_all_days_from_database(db_filename=db_filename)[-1]

def __get_day_from_database(db_filename:str, day_name:str) -> tuple:
    result = None
    connection = sqlite3.connect(db_filename)
    cursor = connection.cursor()

    result = cursor.execute(f"SELECT * FROM days WHERE day_name=:day_name", {'day_name':day_name}).fetchone()

    connection.commit()
    cursor.close()
    connection.close()

    return result

def __is_day_in_database(db_filename:str, day_name:str)->bool:
    return bool(__get_day_from_database(db_filename=db_filename, day_name=day_name))

def __add_day_to_database(db_filename:str, day_name:str, groups:dict) ->None:
    if __is_day_in_database(db_filename=db_filename, day_name=day_name):
        db_day_tuple = __get_day_from_database(db_filename=db_filename, day_name=day_name)
        parsed_day = [day_name]
        for group in groups.values():
            parsed_day.append(group)
        parsed_day_tuple = tuple(parsed_day)
        if not (db_day_tuple == parsed_day_tuple):
            connection = sqlite3.connect(db_filename)
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
        connection = sqlite3.connect(db_filename)
        cursor = connection.cursor()
        cursor.execute(
                    f"INSERT INTO days VALUES (:day_name, :first_g, :second_g, :third_g, :fouth_g, :fifth_g, :sixth_g)", 
                    {'day_name': day_name, 'first_g': groups['1'], 'second_g': groups['2'], 'third_g': groups['3'], 
                    'fouth_g': groups['4'], 'fifth_g': groups['5'], 'sixth_g': groups['6']}
                                    ) 
        connection.commit()
        cursor.close()
        connection.close()

# FUNCTIONS FOR SCRAPPING
def __re_search_all_off_lines(text:str, pattern_r:str) -> dict:
    result = {}
    try:
        pattern = re.compile(pattern_r)
        matches = pattern.finditer(text)
        for match in matches:
            h1, h2, group = match.group(1), match.group(2), match.group(3)
            if group not in result:
                result[group] = []
            result[group].append(f"{h1}-{h2}")
    except Exception as e:
        pass #TODO exception handling

    for pair in result.keys():
        result[pair].sort()

    result = {k: v for k, v in sorted(list(result.items()))}

    temp = {}
    for pair in result.keys():
        current_inline = "+".join(result[pair])
        if not current_inline.startswith("00:00"):
            current_inline = f"00:00+{current_inline}"
        if not current_inline.endswith("24:00"):
            current_inline = f"{current_inline}+24:00"
        temp[pair] = current_inline

    return temp

def __re_search_day_and_month(text:str, pattern_r:str) -> tuple:
    result = (None, None)
    try:
        pattern = re.compile(pattern_r)
        match = pattern.search(text)
        result = (match.group(1), match.group(2))
    except Exception as e:
        pass #TODO exception handling
    return result

def scrapper(link:str, day_month_r:str, group_r:str) -> dict:
    result_d = {}
    temp_d = {}
    try:
       r = requests.get(link)
       soup = BeautifulSoup(r.text, 'html.parser')
       posts = soup.find_all("div", {"class": "tgme_widget_message_bubble"})
       for post in posts:
            text = post.find("div", {"class": "tgme_widget_message_text"})

            if text is not None:
                day, month = __re_search_day_and_month(text=text.text, pattern_r=day_month_r)
                groups = __re_search_all_off_lines(text=text.text, pattern_r=group_r)
                if not(day is None or month is None or groups == {}):
                    temp_d[f"{day} {month}"] = groups
    except requests.ConnectionError as e:
        pass

    for reversed_key in list(temp_d.keys())[::-1]:
        if reversed_key not in result_d:
            result_d[reversed_key] = temp_d[reversed_key]
    return dict(reversed(list(result_d.items())))






