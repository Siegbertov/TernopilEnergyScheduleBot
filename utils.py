import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

NUM_PERIOD = {
    "0":"⁰",
    "1":"¹",
    "2":"²",
    "3":"³",
    "4":"⁴",
    "5":"⁵",
    "6":"⁶",
    "7":"⁷",
    "8":"⁸",
    "9":"⁹"
}

def get_time_period(text:str, period_str=NUM_PERIOD) -> str:
    hs, ms = text.split(":")
    result = ""
    for m in ms:
        result += NUM_PERIOD[m]
    return f"{hs}{result}"

def edit_time_period(text:str) -> str:
    return re.sub(r"(\d\d:\d\d)", lambda x: get_time_period(x.group(1)), text)

def pretty_time(cur_t:tuple)->str:
    result = ""
    if cur_t != (0, 0):
        if cur_t[0] != 0:
            result += f"{cur_t[0]}год. "
        if cur_t[1] != 0:
            result += f"{cur_t[1]}хв."
    return result.strip()

# OTHER FUNCTIONS
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
    return f"{int(day)} {MONTH_UA_OR[month]}"

def get_today_name()->str:
    some_day = datetime.today().strftime("%d %m")
    return __parse_date_as_ukr(some_day)

def get_today_year()->int:
    return int(datetime.today().strftime("%Y"))

def get_today_name_year()->tuple:
    return (get_today_name(), get_today_year())

def get_tomorrow_name()->str:
    some_day = (datetime.today() + timedelta(days=1)).strftime("%d %m")
    return __parse_date_as_ukr(some_day) 

def get_tomorrow_year()->int:
    return int((datetime.today() + timedelta(days=1)).strftime("%Y"))

def get_tomorrow_name_year()->tuple:
    return (get_tomorrow_name(), get_tomorrow_year())

def difference_in_time(hour_1:list, hour_2:list) -> list:
    d_1 = timedelta(hours=int(hour_1[0]), minutes=int(hour_1[1]))
    d_2 = timedelta(hours=int(hour_2[0]), minutes=int(hour_2[1]))
    result = d_2 - d_1
    H, M, _ = str(result).split(":")
    return [H, M]

def sum_of_time(hour_1:list, hour_2:list) -> list:
    d_1 = timedelta(hours=int(hour_1[0]), minutes=int(hour_1[1]))
    d_2 = timedelta(hours=int(hour_2[0]), minutes=int(hour_2[1]))
    result = d_2 + d_1
    H, M, _ = str(result).split(":")
    return [H, M]

if __name__ == "__main__":
    print(get_today_name_year())
    print(get_tomorrow_name_year())