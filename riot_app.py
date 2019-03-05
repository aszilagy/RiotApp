import requests
import json
import pprint
import flask
import configparser as cf

config = cf.ConfigParser()
config.read('config.ini')

api_key = config['DEFAULT']['API_KEY']

def main():
    #get_summoner_info('Belgian Wofls')
    tourn = get_provider_id()

    get_events(tourn)

def get_events(tourn):
    url = 'https://americas.api.riotgames.com/lol/tournament-stub/v4/lobby-events/by-code/' + tourn 
    params = {"api_key": api_key}
    myReq = requests.get(url, params=params, verify=True)
    jData = myReq.json()


    #eventTypeList = ['PracticeGameCreatedEvent', 'PlayerJoinedGameEvent', 'PlayerSwitchedTeamEvent', 'PlayerQuitGameEvent', 'ChampSelectStartedEvent', 'GameAllocationStartedEvent', 'GameAllocatedToLsmEvent']
    fakeData = {'timestamp': '1234567890001',
                'eventType': '',
                'summonerId':''}

    j['eventList'].append(fakeData)

    for j in jData['eventList']:
        print(j['timestamp'], j['summonerId'], j['eventType'])
        if j['summonerId'] != None:
            #print(j['summonerId'])
            #XXX This should be put back in once you have actual summoner Ids
            #XXX summoner = get_summoner_by_id(j['summonerId'])
            j['summoner'] = get_summoner_info('Decelx')

        else:
            j['summoner'] = None

    print(jData)

    return jData

def get_provider_id():
    url = 'https://americas.api.riotgames.com/lol/tournament-stub/v4/providers?api_key='+api_key
    data = {"url": "http://18.232.99.218/", "region":"NA"}
    myReq = requests.post(url, data=json.dumps(data), verify=True)
    jprint(myReq)

    jsonReq = myReq.json() #158 <- PROVIDER ID

    tourn = get_tourn_id(jsonReq) #158

    return tourn

def get_tourn_id(tournId:int):
    url = 'https://americas.api.riotgames.com/lol/tournament-stub/v4/tournaments'
    params = {"api_key": api_key}
    data = {"name":"Friends-Game-Night", "providerId":tournId}
    myReq = requests.post(url, data=json.dumps(data), params=params, verify=True)
    jprint(myReq)

    jsonReq = myReq.json() #3968 <- TOURNAMENT ID

    tourn = create_tourney_game(jsonReq)

    return tourn

def create_tourney_game(tournId):
    url = 'https://americas.api.riotgames.com/lol/tournament-stub/v4/codes'
    params = {"api_key": api_key, "tournamentId": tournId}
    data = {"teamSize":5, "mapType":"SUMMONERS_RIFT", "pickType": "DRAFT_MODE", "spectatorType":"ALL"}

    headers = {'content-type':'application/json'}
    print('Data object', data)
    myReq = requests.post(url, data=json.dumps(data), params=params, verify=True)

    print("Creating mock tourney")
    #jprint(myReq)
    tourn_id = myReq.json()[0]

    return tourn_id


def jprint(jsonD):
    '''
    Parameters: Request ... myReq  [Returned from requests.get]
    '''
    jData = json.loads(jsonD.content)
    print(json.dumps(jData, indent=4))

def parse_summoners(ln):
    ln = ['Decelx', 'Finland Wofls']

def get_summoner_mastery(summoner_id: str):
    pass

def get_summoner_by_id(summoner_id):
    url = 'https://na1.api.riotgames.com/lol/summoner/v4/summoners/'+ summoner_id + '?api_key='+api_key
    myReq = requests.get(url, verify=True)
    if(myReq.ok):
        jDat = json.loads(myReq.content)
        jprint(myReq)
        json_to_summoner(myReq)

    else:
        print("SUMMONER_INFO BAD")
        jprint(myReq)

    return myReq.json()

def get_summoner_info(summoner_name):
    url = 'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/'+ summoner_name + '?api_key='+api_key
    myReq = requests.get(url, verify=True)
    if(myReq.ok):
        jDat = json.loads(myReq.content)
        summonerObj = json_to_summoner(myReq)
        return summonerObj

    else:
        print("SUMMONER_INFO BAD")

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

class Summoner:
    def __init__(self,
            profileIconId: int,
            name: str,
            puuid: str,
            summonerLevel: int,
            revisionDate: int,
            summonerId: str,
            accountId: str):
        self.icon = profileIconId
        self.name = name
        self.puuid = puuid
        self.level = summonerLevel
        self.revDate = revisionDate
        self.summonerId = summonerId
        self.accountId = accountId

if __name__ == '__main__':
    main()
