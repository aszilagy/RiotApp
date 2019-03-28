import requests
import time
import json
import urllib
from pprint import pprint
import flask
import configparser as cf

config = cf.ConfigParser()
config.read('config.ini')

api_key = config['DEFAULT']['API_KEY']
summonerDict = {}

#TODO: Check for new versions on https://ddragon.leagueoflegends.com/api/versions.json
def main():
    start = time.time()
    #ver = get_current_version() #XXX this adds 0.2 seconds, do it once a day to see if new version?
    ver = '9.6.1'

    #XXX Make the difference in these two calls clearer
    champ = read_static_champion('Xerath', version=ver)
    zoe = get_champ_page('Xerath', version=ver)

    champ = read_static_champion('Zac', version=ver)
    zoe = get_champ_page('Zac', version=ver)

    end = time.time()
    print("MAIN TOOK %.2gs" % (end-start))

def get_current_version():
    url = "https://ddragon.leagueoflegends.com/api/versions.json"
    with urllib.request.urlopen(url) as u:
       data = json.loads(u.read().decode())

    return data[0]

def get_champ_page(championName, filename=None, version='9.6.1'):
    if filename is None:
        filename = 'static/champions/' + championName + '-' + version + '.json'

    try:
        with open(filename, encoding="utf8") as f:
            data = json.load(f)

    except: #except FileNotFounderror
        url = "http://ddragon.leagueoflegends.com/cdn/" + version + "/data/en_US/champion/"+ championName + ".json"
        with urllib.request.urlopen(url) as u:
            data = json.loads(u.read().decode())

        with open(filename, 'w+') as outf:
            json.dump(data, outf)

    return data['data'][championName]

def read_static_champion(championName, filename=None, version='9.6.1'):
    if filename is None:
        filename='static/champion-'+version+'.json'
    try:
        with open(filename, encoding="utf8") as f:
            data = json.load(f)

    except: #except FileNotFoundError
        url = "http://ddragon.leagueoflegends.com/cdn/" + version + "/data/en_US/champion.json"
        with urllib.request.urlopen(url) as u:
            data = json.loads(u.read().decode())

        with open(filename, 'w+') as outf:
            json.dump(data, outf)

    return data['data'][championName]

def get_events(tourn):
    start = time.time()
    print("Getting list of events")
    url = 'https://americas.api.riotgames.com/lol/tournament-stub/v4/lobby-events/by-code/' + tourn 
    params = {"api_key": api_key}
    myReq = requests.get(url, params=params, verify=True)
    jData = myReq.json()

    #eventTypeList = ['PracticeGameCreatedEvent', 'PlayerJoinedGameEvent', 'PlayerSwitchedTeamEvent', 'PlayerQuitGameEvent', 'ChampSelectStartedEvent', 'GameAllocationStartedEvent', 'GameAllocatedToLsmEvent']
    fakeData = [{'timestamp': '1234567890001',
                'eventType': 'PlayerJoinedGameEvent',
                'summonerId': 'dWFNLXFgPgTQr32VNmOECUUs5XONGXDZAmY_CxxFzIQL8bc'},
                {'timestamp': '1234567890002',
                'eventType': 'PlayerJoinedGameEvent',
                'summonerId': 'soFgnCpoRjrdxEwrxCexfuaCrnurJb8cI-bLY-ZIJl2nelM8'},
                {'timestamp': '1234567890003',
                'eventType': 'PlayerJoinedGameEvent',
                'summonerId': 'NWVYUL3RxgZzs_NSFz4_-AR1ka83xNUo5sS0R7YJnjPMM4I'},
                {'timestamp': '1234567890004',
                'eventType': 'PlayerJoinedGameEvent',
                'summonerId': 'sfKJB_hj5Uo7UlJwfXWOIpkDxG5GY2euTMR6kKTUsju9L6I'},
                {'timestamp': '1234567890005',
                'eventType': 'PlayerJoinedGameEvent',
                'summonerId': get_summoner_by_name('imaqtpie',justId=True)},
                {'timestamp': '1234567890006',
                'eventType': 'PlayerSwitchedTeamEvent',
                'summonerId': 'sfKJB_hj5Uo7UlJwfXWOIpkDxG5GY2euTMR6kKTUsju9L6I'},
                {'timestamp': '1234567890007',
                'eventType': 'PlayerSwitchedTeamEvent',
                'summonerId': 'sfKJB_hj5Uo7UlJwfXWOIpkDxG5GY2euTMR6kKTUsju9L6I'}]

    fakeSummoners = []
    for ddo in fakeData:
        fakeSummoners.append(ddo['summonerId'])
        jData['eventList'].append(ddo)

    for j in jData['eventList']:
        if (j['summonerId'] != None) and (j['summonerId'] in fakeSummoners):
            if j['summonerId'] in summonerDict.keys():
                j['summoner'] = summonerDict[j['summonerId']]

            else:
                summonerObj = get_summoner_by_id(j['summonerId'])
                summonerObj.rank = get_summoner_rank(j['summonerId'])
                j['summoner'] = summonerObj
                summonerDict[j['summonerId']] = summonerObj

        elif j['summonerId'] != None:
            if j['summonerId'] in summonerDict.keys():
                j['summoner'] = summonerDict[j['summonerId']]

            else:
                summonerObj = get_summoner_by_name('Decelx')
                summonerObj.rank = get_summoner_rank(summonerObj.summonerId)
                j['summoner'] = summonerObj
                summonerDict[j['summonerId']] = summonerObj

        else:
            j['summoner'] = None

    end = time.time()
    print("GET_EVENTS TOOK %.2gs" % (end-start))
    return jData

def get_provider_id():
    print("Getting provider ID")
    url = 'https://americas.api.riotgames.com/lol/tournament-stub/v4/providers?api_key='+api_key
    data = {"url": "http://54.159.86.209/", "region":"NA"}
    myReq = requests.post(url, data=json.dumps(data), verify=True)

    jsonReq = myReq.json() #158 <- PROVIDER ID

    tourn = get_tourn_id(jsonReq) #158

    return tourn

def get_tourn_id(tournId:int):
    print("Getting tournament ID")
    url = 'https://americas.api.riotgames.com/lol/tournament-stub/v4/tournaments'
    params = {"api_key": api_key}
    data = {"name":"Friends-Game-Night", "providerId":tournId}
    myReq = requests.post(url, data=json.dumps(data), params=params, verify=True)

    jsonReq = myReq.json() #3968 <- TOURNAMENT ID

    tourn = create_tourney_game(jsonReq)

    return tourn

def create_tourney_game(tournId):
    print("Creating lobby")
    url = 'https://americas.api.riotgames.com/lol/tournament-stub/v4/codes'
    params = {"api_key": api_key, "tournamentId": tournId}
    data = {"teamSize":5, "mapType":"SUMMONERS_RIFT", "pickType": "DRAFT_MODE", "spectatorType":"ALL"}

    headers = {'content-type':'application/json'}
    myReq = requests.post(url, data=json.dumps(data), params=params, verify=True)

    tourn_id = myReq.json()[0]

    return tourn_id


def jprint(jsonD):
    '''
    Parameters: Request ... myReq  [Returned from requests.get]
    '''
    jData = json.loads(jsonD.content)
    print(jData)

def get_summoner_rank(summoner_id: str):
    url = 'https://na1.api.riotgames.com/lol/league/v4/positions/by-summoner/' + summoner_id + '?api_key='+api_key
    myReq = requests.get(url, verify=True)
    if(myReq.ok):
        rankList = json_to_rank(myReq)
        if rankList != None:
            print("Getting rank for %s" % rankList[0].name)
        return rankList

    else:
        print("SUMMONER_MASTERY BAD")
        jprint(myReq)

def get_summoner_by_id(summoner_id):
    url = 'https://na1.api.riotgames.com/lol/summoner/v4/summoners/'+ summoner_id + '?api_key='+api_key
    myReq = requests.get(url, verify=True)
    if(myReq.ok):
        summonerObj = json_to_summoner(myReq)
        print("Getting summoner id for %s" % summonerObj.name)
        return summonerObj

    else:
        print("SUMMONER_INFO BAD")
        jprint(myReq)


def get_summoner_by_name(summoner_name, justId = False):
    print("Getting summoner object by name: %s" % summoner_name)
    url = 'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/'+ summoner_name + '?api_key='+api_key
    myReq = requests.get(url, verify=True)
    if(myReq.ok):
        summonerObj = json_to_summoner(myReq)
        if justId == True:
            return summonerObj.summonerId
        return summonerObj

    else:
        print("SUMMONER_INFO BAD")
        jprint(myReq)

def json_to_rank(jsonD):
    rankList = []
    rankOrder = ['IRON', 'BRONZE', 'SILVER','GOLD','PLATINUM','DIAMOND','MASTER','GRANDMASTER','CHALLENGER']
    jList = json.loads(jsonD.content)

    if len(jList) == 0:
        #They are unranked
        return None

    for jData in jList:
        if 'miniSeries' not in jData:
            jData['miniSeries'] = {}
        rankObj = Rank(jData['queueType'], 
                jData['summonerName'],
                jData['hotStreak'],
                jData['miniSeries'],
                jData['wins'],
                jData['veteran'],
                jData['losses'],
                jData['rank'],
                jData['leagueId'],
                jData['inactive'],
                jData['freshBlood'],
                jData['leagueName'],
                jData['position'],
                jData['tier'],
                jData['summonerId'],
                jData['leaguePoints'])

        rankList.append(rankObj)


    rankList = sorted(rankList, key = lambda k: rankOrder.index(k.tier))

    return rankList

def json_to_summoner(jsonD):
    jData = json.loads(jsonD.content)
    sumObj = Summoner(jData['profileIconId'], 
            jData['name'],
            jData['puuid'],
            jData['summonerLevel'],
            jData['revisionDate'],
            jData['id'],
            jData['accountId'])

    return sumObj

#TODO: Create json_to_champion

class Champion:
    def __init__(self):
        #TODO: Get it from here https://developer.riotgames.com/static-data.html
        pass

class ChampionMastery:
    def __init__(self,
            chestGranted: bool,
            championLevel: int,
            championPoints: int,
            championId: int,
            championPointsUntilNextLevel: int,
            lastPlayTime: int,
            tokensEarned: int,
            championPointsSinceLastLevel: int,
            summonerId: str):
        self.chestGranted = chestGranted
        self.championLevel = championLevel
        self.championPoints = championPoints
        self.championId = championId
        self.championPointsUntilNextLevel = championPointsUntilNextLevel
        self.lastPlayTime = lastPlayTime
        self.tokensEarned = tokensEarned
        self.championPointsSinceLastLevel = championPointsSinceLastLevel
        self.summonerId = summonerId

class Rank:
    def __init__(self,
            queueType: str,
            summonerName: str,
            hotStreak: bool,
            miniSeries,
            wins: int,
            veteran: bool,
            losses: int,
            rank: str,
            leagueId: str,
            inactive: bool,
            freshBlood: bool,
            leagueName: bool,
            position: str,
            tier: str,
            summonerId: str,
            leaguePoints: int):
        self.queueType = queueType
        self.name = summonerName
        self.hotStreak = hotStreak
        self.miniSeries = miniSeries
        self.wins = wins
        self.veteran = veteran
        self.losses = losses
        self.rank = rank
        self.leagueId = leagueId
        self.inactive = inactive
        self.freshBlood = freshBlood
        self.leagueName = leagueName
        self.position = position
        self.tier = tier
        self.summonderId = summonerId
        self.leaguePoints = leaguePoints

class Summoner:
    def __init__(self,
            profileIconId: int,
            name: str,
            puuid: str,
            summonerLevel: int,
            revisionDate: int,
            summonerId: str,
            accountId: str,
            rank = None,
            championList = None):
        self.icon = profileIconId
        self.name = name
        self.puuid = puuid
        self.level = summonerLevel
        self.revDate = revisionDate
        self.summonerId = summonerId
        self.accountId = accountId
        self.rank = rank #List of Rank objects
        self.championList = championList #List of Champion objects

if __name__ == '__main__':
    main()
