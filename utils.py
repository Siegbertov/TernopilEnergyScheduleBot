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

# FUNCTIONS FOR SCRAPPING
def __re_search_all_inlines(text:str, pattern_r:str) -> dict:
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

    for x in range(1, 7):
        if str(x) not in temp.keys():
            temp[str(x)] = "00:00+24:00"
    return dict(sorted(temp.items()))

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
                groups = __re_search_all_inlines(text=text.text, pattern_r=group_r)
                if not(day is None or month is None or groups == {}):
                    temp_d[f"{day} {month}"] = groups
    except requests.ConnectionError as e:
        pass
    for reversed_key in list(temp_d.keys())[::-1]:
        if reversed_key not in result_d:
            result_d[reversed_key] = temp_d[reversed_key]
    return dict(reversed(list(result_d.items())))

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
    return f"{day} {MONTH_UA_OR[month]}"

def get_today_name()->str:
    some_day = datetime.today().strftime("%d %m")
    return __parse_date_as_ukr(some_day)

def get_tomorrow_name()->str:
    some_day = (datetime.today() + timedelta(days=1)).strftime("%d %m")
    return __parse_date_as_ukr(some_day) 

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

