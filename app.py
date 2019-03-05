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
            if summoner not in blueTeam:
                print("NOT ON BLUE, add to blue")
                summoner.team = 1
                blueTeam.append(summoner)

            if summoner in redTeam:
                print("ON RED")
                redTeam.remove(summoner)

        if eventData == 'PlayerSwitchedTeamEvent' and obj['summonerId'] != None:
            if summoner not in redTeam:
                print("NOT ON RED, add to red")
                summoner.team = 2
                redTeam.append(summoner)

            #XXX: This is temporary fix, idk why the other if doesn't work.
            #XXX: It seems like a new object being created has diff signature
            blueNames = [s.name for s in blueTeam]
            if summoner.name in blueNames:
                index = blueNames.index(summoner.name)
                del blueNames[index]
                del blueTeam[index]

            #FIXME: This doesn't work for some reason
            if summoner in blueTeam:
                print("ON BLUE")
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
    if 'username' not in session:
        return "You are not logged in <br><a href = '/'></b>" + "click here to log in</b></a>"

    global tournieId
    print("Working")
    tournieId = ri.get_provider_id()
    print(tournieId)

    return render_template('index.html',tourn_id=tournieId)


@app.route('/remind/', methods=['GET','POST'])
def home():
    if 'username' not in session:
        return "You are not logged in <br><a href = '/'></b>" + "click here to log in</b></a>"

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host=host, port=port)
