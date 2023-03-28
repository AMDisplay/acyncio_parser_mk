import json
import logging
from bs4 import BeautifulSoup

async def coef(reader):
    """Сортировка коэффициентов"""
    logging.info('sorted coef')
    list_of_coef = []
    for coef_one in reader:
        coef = json.loads(coef_one)
        all_coef = {
            'win_next_round_1' : coef['Value']['GE'][0]['E'][0][0]['C'],
            'win_next_round_2' : coef['Value']['GE'][0]['E'][1][0]['C'],
            # 'time_over_first_1' : coef['Value']['GE'][1]['E'][0][0]['C'],
            # 'time_over_first_2' : coef['Value']['GE'][1]['E'][0][1]['C'],
            # 'time_over_first_3' : coef['Value']['GE'][1]['E'][0][2]['C'],
            # 'time_under_1' : coef['Value']['GE'][1]['E'][1][0]['C'],
            # 'time_under_2' : coef['Value']['GE'][1]['E'][1][1]['C'],
            # 'time_under_3' : coef['Value']['GE'][1]['E'][1][2]['C'],
            'win_match_1' : coef['Value']['GE'][2]['E'][0][0]['C'],
            'win_match_2' : coef['Value']['GE'][2]['E'][1][0]['C'],
            # 'total_all_over' : coef['Value']['GE'][3]['E'][0][0]['C'],
            # 'total_all_undef' : coef['Value']['GE'][3]['E'][1][0]['C'],
            'fat_in_next_round' : coef['Value']['GE'][4]['E'][0][0]['C'],
            'brut_in_next_round' : coef['Value']['GE'][4]['E'][0][1]['C'],
            'no_finish_next_round' : coef['Value']['GE'][4]['E'][0][2]['C'],
            'frend_in_next_round' : coef['Value']['GE'][4]['E'][0][3]['C'],
        }
        list_of_coef.append(all_coef)
    return list_of_coef

async def parse_match(tasks):
    """Получение статистики текущих матчей"""
    logging.info('parse match')
    list_of_versus = []
    for match in tasks:
        soup = BeautifulSoup(match, 'lxml')
        if soup.find('div', {'class': 'message-block game-over-panel market-grid__game-over-panel message-block--theme-gray-100 message-block--rounded'}) != None:
            script = soup.find('script')
            zxc = script.contents[0]
            first_index = zxc.find('{fightingPeriodsScores')
            seconnd_index = zxc.find(',isTimeDirectionBackward', first_index)
            fight_str = zxc[first_index:seconnd_index]
            fight = fight_str.replace('fightingPeriodsScores', '"fightingPeriodsScores"').replace('round', '"round"').replace('time', '"time"').replace('winner', '"winner"').replace('winType', '"winType"').replace('finishHim', '"finishHim"').replace(':e', ':"e"').replace(':x', ':"x"').replace(':h', ':"h"').replace(':l', ':"l"').replace(':k', ':"k"').replace(':p', ':"p"').replace(':c', ':"c"').replace(':w', ':"w"').replace(':H', ':"H"').replace(':o', ':"o"')
            finaly_fight = json.loads(fight)
            versus = {
                "fighter_1" :fighter_1, 
                "fighter_2" :fighter_2, 
                "stat_of_rounds":finaly_fight
            }
            scoreboard = soup.find('div', {'class': 'scrollbar scoreboard-section__scroll scrollbar--theme-primary--40 scrollbar--size-m'})
            team = scoreboard.find_all('div', {'class': 'scoreboard-intro__team'})
            fighter_1 = team[0].find('span', {'class': 'scoreboard-team-player-name__caption'}).text
            fighter_2 = team[1].find('span', {'class': 'scoreboard-team-player-name__caption'}).text
            list_of_versus.append(versus)
        else:
            list_of_versus.append(None)
    logging.info('%s', list_of_versus)
    return list_of_versus


async def write_stat(id_matches, matches, list_coef):
    """Запись статистики и коэфов о матчах"""
    logging.info('writing stats')
    logging.info('%s %s %s', id_matches, matches, list_coef)
    n = 0
    stats_matches=[]
    coef_matches= []
    for _ in id_matches:
        match = [id_matches[n], matches[n]]
        stats_matches.append(match)
        coef = [id_matches[n], list_coef[n]]
        coef_matches.append(coef)
        n+=1
    for match in stats_matches:
        if match[1] is not None:
            with open('stats.json', encoding='utf-8') as fp:
                listObj_stats = json.loads(fp.read())
                listObj_stats.append(stats_matches)
            with open('stats.json', 'w', encoding='utf-8') as stats_file:
                json.dump(listObj_stats, stats_file, ensure_ascii=False,
                                            indent=4, 
                                            separators=(',',': '))
    with open('coef.json', encoding='utf-8') as fp:
        listObj_coef = json.loads(fp.read())
        listObj_coef.append(coef_matches)
    with open('coef.json', 'w', encoding='utf-8') as coef_file:
        json.dump(listObj_coef, coef_file, ensure_ascii=False,
                                    indent=4,  
                                    separators=(',',': '))

# async def write_csv():
#     """Запись данных о матчах"""
#     with open('coef.json', 'r', encoding='utf-8') as coef_file:
#         all_coef = json.loads(coef_file.read())
#     with open('stats.json', 'r', encoding='utf-8') as stats_file:
#         all_stats = json.loads(stats_file.read())

    
    # with open('data.json', 'w', encoding='utf-8') as outfile:
    #     json.dump(sort_match, outfile, ensure_ascii=False,
    #                                 indent=4,  
    #                                 separators=(',',': '))

# with open('data.json') as fp:
#             listObj = json.loads(fp.read())
#             listObj.append(sort_match)

