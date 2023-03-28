from bs4 import BeautifulSoup
from aiohttp import ClientSession
import asyncio
import sort_data
import logging

ID_SITE = 63759
URL = f'https://betwinner-{ID_SITE}.top/ru/live/mortal-kombat/2068436-mortal-kombat-11/'

def get_url_matches(soup):
    """Получение всех юрл матчей"""
    logging.info('get url matches')
    fights_url = []
    id_matches = []
    li = soup.find_all('li', {'class' : "ui-dashboard-game dashboard-game"})
    for evety_li in li:
        matches = evety_li.find('a')
        match_url_str = matches.attrs['href']
        fight_num_and_name_fighters = match_url_str.split("/")[-1]
        fight_num_and_name_fighters_list = fight_num_and_name_fighters.split('-')
        id_match = fight_num_and_name_fighters_list[0]
        if id_match not in id_matches:
            id_matches.append(id_match)
            fights_url.append(fight_num_and_name_fighters)
    return fights_url, id_matches

async def initial_tasks(fights_urls, session):
    """Создание тасков для открытия матчей"""
    logging.info('initial tasks')
    tasks = [asyncio.create_task(open_match(fight, session)) for fight in fights_urls]
    result =  await asyncio.gather(*tasks)
    return result

async def open_match(fight_urls, session):
    """Получение данных о ходе матча"""
    logging.info('opening match')
    async with session.get(URL + fight_urls) as response:
        return await response.text()
                
async def get_coef(id_matchs): # Их не будет если матч кончился
    """Получение коэффициентов в матче"""
    logging.info('get coef in match')
    coef = []
    async with ClientSession() as session:
        for match in id_matchs:
            await asyncio.sleep(1)
            match = int(match)
            url = f'https://betwinner-{ID_SITE}.top/service-api/LiveFeed/GetGameZip?id={match}&isSubGames=true&GroupEvents=true&countevents=250&grMode=4&partner=152&topGroups=&tz=3&marketType=1'
            response = await session.get(url=url)
            response =  await response.text()
            coef.append(response)
    logging.info('%s %s', id_matchs, coef)
    return coef

async def fetch(session):
    """Получить хтмл"""
    logging.info('connecting')
    async with session.get(URL) as response:
        response = BeautifulSoup(await response.content.read(), 'lxml')
        return response

async def main():
    """Основная функция"""
    # while True:
    async with ClientSession() as session:
        html = await fetch(session)
        fights_url, id_matches = get_url_matches(html)
        tasks = await initial_tasks(fights_url, session)
        matches = await sort_data.parse_match(tasks)
        list_response_coef = await get_coef(id_matches)
        list_coef = await sort_data.coef(list_response_coef)
        await sort_data.write_stat(id_matches, matches, list_coef)
        # await asyncio.sleep(30)
        # await sort_data.write_csv()
        
if __name__ == '__main__':
    file_log = logging.FileHandler('py_log.log')
    console_out = logging.StreamHandler()
    format = " [%(threadName)s]: %(asctime)s: %(message)s"
    logging.basicConfig(handlers=(file_log, console_out),format=format, level=logging.INFO,
                        datefmt="%H:%M:%S", )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())