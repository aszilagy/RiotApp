from flask import Flask, render_template, request, session
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
app.secret_key = b'(0a$li*&$p]/nap993-1z[1'

@app.route('/', methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/tourney/', methods=['GET','POST'])
def verify_login():
    if 'username' in request.form and 'password' in request.form:
        checkUser = sha.verify(request.form['username'], encrypted_user)
        checkPass = sha.verify(request.form['password'], encrypted_pass)

        if checkUser == True and checkPass == True:
            session['username'] = request.form['username']
            return render_template('index.html', username=request.form['username'])
    
        elif checkUser == False or checkPass == False:
            return render_template('login.html',error='Wrong Username/Password')

    return render_template('login.html')

def addToBlue(summoner):
    global blueTeam
    removeFromRed(summoner)

    blueIds = [s.summonerId for s in blueTeam]
    if summoner.summonerId not in blueIds:
        blueTeam.append(summoner)
    
def removeFromBlue(summoner):
    blueIds = [s.summonerId for s in blueTeam]
    if summoner.summonerId in blueIds:
        index = blueIds.index(summoner.summonerId)
        del blueIds[index]
        del blueTeam[index]


def addToRed(summoner):
    global redTeam
    removeFromBlue(summoner)

    redIds = [s.summonerId for s in redTeam]
    if summoner.summonerId not in redIds:
        redTeam.append(summoner)

def removeFromRed(summoner):
    redIds = [s.summonerId for s in redTeam]
    if summoner.summonerId in redIds:
        index = redIds.index(summoner.summonerId)
        del redIds[index]
        del redTeam[index]

def quitGame(summoner):
    global blueTeam, redTeam
    redIds = [s.summonerId for s in redTeam]
    blueIds = [si.summonerId for si in blueTeam]
    if summoner.summonerId in redIds:
        removeFromRed(summoner)

    if summoner.summonerId in blueIds:
        removeFromBlue(summoner)

def switchTeam(summoner):
    global blueTeam, redTeam
    redIds = [s.summonerId for s in redTeam]
    blueIds = [si.summonerId for si in blueTeam]
    if summoner.summonerId in redIds:
        addToBlue(summoner)

    if summoner.summonerId in blueIds:
        addToRed(summoner)

@app.route('/refresh_tourney/', methods=['GET','POST'])
def refresh_tourney():
    if 'username' not in session:
        return "You are not logged in <br><a href = '/'></b>" + "click here to log in</b></a>"

    global tournieId, blueTeam, redTeam;
    if tournieId == "":
        tournieId = ri.get_provider_id()

    jData = ri.get_events(tournieId)

    sortedEvents = sorted(jData['eventList'], key = lambda k: k['timestamp'])

    for obj in sortedEvents:
        summoner, eventData = obj['summoner'], obj['eventType']

        if eventData == 'PlayerJoinedGameEvent' and obj['summonerId'] != None:
            if len(redTeam) < len(blueTeam):
                if len(redTeam) != 5:
                    addToRed(summoner)

            else:
                if len(blueTeam) != 5:
                    addToBlue(summoner)

        if eventData == 'PlayerSwitchedTeamEvent' and obj['summonerId'] != None:
            switchTeam(summoner)

        if eventData == 'PlayerQuitGameEvent' and obj['summonerId'] != None:
            #XXX Removed for now, for testing purposes
            #quitGame(summoner)
            continue

    return render_template('index.html', tourn_id = tournieId, eventList = jData['eventList'], blueTeam = blueTeam, redTeam = redTeam)


@app.route('/get_tourney/', methods=['GET','POST'])
def get_tourney():
    if 'username' not in session:
        return "You are not logged in <br><a href = '/'></b>" + "click here to log in</b></a>"

    global tournieId
    print("Working")
    tournieId = ri.get_provider_id()
    print(tournieId)

    return render_template('index.html',tourn_id=tournieId)

if __name__ == '__main__':
    app.run(debug=True, host=host, port=port)
