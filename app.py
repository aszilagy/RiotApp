from flask import Flask, render_template, request
import riot_app as ri
from passlib.hash import sha256_crypt as sha
import configparser as cf

config = cf.ConfigParser()
config.read('config.ini')

encrypted_pass = config['DEFAULT']['PASSWORD']
encrypted_user = config['DEFAULT']['USER']
port = config['DEFAULT']['PORT']
host = config['DEFAULT']['HOST']
tournieId = ""

blueTeam = []
redTeam = []

app = Flask(__name__)

@app.route('/', methods=['GET'])
def login():

    return render_template('login.html')

@app.route('/tourney/', methods=['GET','POST'])
def verify_login():
    if 'username' in request.form and 'password' in request.form:
        checkUser = sha.verify(request.form['username'], encrypted_user)
        checkPass = sha.verify(request.form['password'], encrypted_pass)
    else:
        username = 'guest'

    if checkUser == True and checkPass == True:
        return render_template('index.html', username=request.form['username'])
    
    elif checkUser == False or checkPass == False:
        return render_template('login.html',error='Wrong Username/Password')

    else:
        return render_template('login.html')


@app.route('/refresh_tourney/', methods=['GET','POST'])
def refresh_tourney():
    global tournieId, blueTeam, redTeam;
    if tournieId == "":
        tournieId = ri.get_provider_id()

    jData = ri.get_events(tournieId)

    sortedEvents = sorted(jData['eventList'], key = lambda k: k['timestamp'])

    for obj in sortedEvents:
        summoner, eventData = obj['summoner'], obj['eventType']

        if eventData == 'PlayerJoinedGameEvent' and obj['summonerId'] != None:
            if summoner not in blueTeam:
                summoner.team = 1
                blueTeam.append(summoner)

            if summoner in redTeam:
                redTeam.remove(summoner)

        if eventData == 'PlayerSwitchedTeamEvent' and obj['summonerId'] != None:

            if summoner not in redTeam:
                summoner.team = 2
                redTeam.append(summoner)

            if summoner in blueTeam:
                blueTeam.remove(summoner)
            
        if eventData == 'PlayerQuitGameEvent' and obj['summonerId'] != None:
            if summoner in blueTeam:
                print("Found summoner on blue team that left game")
                blueTeam.remove(summoner)

            elif summoner in redTeam:
                print("Found summoner on red team that left game")
                redTeam.remove(summoner)

            else:
                print("Summoner not in game")

    return render_template('index.html', tourn_id = tournieId, eventList = jData['eventList'], blueTeam = blueTeam, redTeam = redTeam)


@app.route('/get_tourney/', methods=['GET','POST'])
def get_tourney():
    global tournieId
    print("Working")
    tournieId = ri.get_provider_id()
    print(tournieId)

    return render_template('index.html',tourn_id=tournieId)


@app.route('/remind/', methods=['GET','POST'])
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host=host, port=port)
