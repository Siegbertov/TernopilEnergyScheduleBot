import re
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from pprint import pprint

def re_search_all_inlines(text:str, pattern_r:str) -> dict:
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

def re_search_day_and_month(text:str, pattern_r:str) -> tuple:
    result = (None, None)
    try:
        pattern = re.compile(pattern_r)
        match = pattern.search(text)
        result = (match.group(1), match.group(2))
    except Exception as e:
        #TODO exception handling
        pass 
    return result

async def async_requester(link:str)->str:
    async with aiohttp.ClientSession() as session:
        try:
            response = await session.get(url=link)
            return await response.text()
        except Exception as e:
            print(e)

async def get_reverse_posts(link:str)->list:
    response = await async_requester(link=link)
    soup = BeautifulSoup(response, "html.parser")
    return soup.find_all("div", {"class": "tgme_widget_message_bubble"})[::-1]

async def get_text_posts(link:str)->list:
    posts = await get_reverse_posts(link=link)
    return [post.find("div", {"class": "tgme_widget_message_text"}).text for post in posts if post.find("div", {"class": "tgme_widget_message_text"} is not None)]

async def scrap_current_day_month_group(link:str, days:list, day_month_r:str, group_r:str)->dict:
    temp_d = {}
    for day in days:
        temp_d[day] = None

    for current_post in  await get_text_posts(link=link):
        if all(temp_d.values()):
            break
        else:
            day, month = re_search_day_and_month(current_post, pattern_r=day_month_r)
            groups = re_search_all_inlines(current_post, pattern_r=group_r)
            if not(day is None or month is None or groups == {}):
                if  f"{day} {month}" in temp_d.keys():
                    if temp_d[f"{day} {month}"] is None:
                        temp_d[f"{day} {month}"] = groups
    return temp_d
        

async def test_function():
    from utils import get_tomorrow_name, get_today_name
    LINK = "https://t.me/s/ternopiloblenerho"
    DAY_MONTH_R = r", (\d+) (\w+),?"
    GROUP_R = r"(\d\d:\d\d)-(\d\d:\d\d)\s+(\d)\s+\w+"
    a_results = await scrap_current_day_month_group(
        link=LINK,
        days=[get_tomorrow_name(), get_today_name()],
        day_month_r=DAY_MONTH_R,
        group_r=GROUP_R        
    )
    pprint(a_results)


if __name__ == "__main__":
    asyncio.run(test_function())