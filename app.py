import os
import time
import json
import re
import eventlet
eventlet.monkey_patch()
import stats_obtainer as stats
from flask import Flask, render_template, redirect, url_for
from flask_socketio import SocketIO, emit
import socket
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'webiuyvoiarwueyborviuyaorievwaubyr'
socketio = SocketIO(app)
local_ip = socket.gethostbyname(socket.gethostname())
target_port = 5000



print(f"http://{local_ip}:{target_port}")

@app.route('/')
def main_page():
    return render_template('index.html')

@socketio.on("message")
def handle_msg(msg):
    emit("message", "hey")

# EVERYTHIGN ADTER THIS IS LGO CHECKER
# path_to_official_log = f"{os.getenv('APPDATA')}\\.minecraft\\logs\\latest.log"
# path_to_log = f"{os.getenv('APPDATA')}\\.minecraft\\logs\\latest.log"
path_to_log = f"{os.getenv('USERPROFILE')}\\.lunarclient\\offline\\1.8\\logs\\latest.log"
log_file = None

api_key = ""
players = []

def setup():
    global log_file
    global api_key

    if os.path.exists(path_to_log) is False:
        return {"success": False, "cause": "No Log file found"}

    with open("data.json", "r") as file:
        api_key = json.load(file)["api_key"]

    # if isinstance(api_key, str) and not stats.get_player_stats("Teky1", api_key)["success"]:
    #     api_key = None
    #     with open("data.json", "w") as file:
    #         json.dump({"api_key": None}, file)
    #     print("No API Key found, please use \"/api new\" to generate a new key")

    if api_key is not None:
        print(f"{api_key} loaded as API key.")
    else:
        print("No API Key found, please use \"/api new\" to generate a new key")
    log_file = open(path_to_log, "r")
    return {"success": True}


def process(line):
    global api_key
    global players

    updateList = True

    if line.count("[Client thread/INFO]: [CHAT]") > 0:
        line = line.strip()[40:]
    else:
        return 0
    if len(line) == 56 and line.startswith("Your new API key is ") == 1:
        api_key = line[20:]
        with open("data.json", "w") as file:
            json.dump({"api_key": api_key}, file)
        with open("data.json", "r") as file:
            print(f"{json.load(file)['api_key']} set as new api key")

        for player in players:
            player = stats.get_player_stats(player, api_key)

    elif re.match("[^:]+ has joined \(.+/.+\)!", line):
        new_player = line.split()[0]
        if not has_player(players, new_player):
            if api_key is not None:
                player_stats = stats.get_player_stats(new_player, api_key)
                players.append(player_stats)
                # print(f"added {player_stats}")
            else:
                players.append(new_player)
                # print(f"{new_player} joined, adding them to the list.")

    elif line.startswith("ONLINE: "):
        player_list = line.replace("ONLINE: ", "").split(", ")
        players = []
        if api_key is not None:
            for player in player_list:
                player_stats = stats.get_player_stats(player, api_key)
                players.append(player_stats)
                # print(player_stats)
        else:
            players = player_list

    elif re.match("[^:]+ has quit!", line):
        departed_player = line.replace(" has quit!", "")
        for i in range(len(players)):
            if (isinstance(players[i], str) and players[i] == departed_player) or players[i]["ign"]==departed_player:
                players[i] = "**GONE**"
        try:
            while True:
                players.remove("**GONE**")
        except ValueError:
            pass

        # print(f"{departed_player} has been removed from the list")
    else:
        updateList = False

    if updateList:
        data = players
        if len(data) == 0 or isinstance(data[0], str):
            data = data
        else:
            data = sorted(data, key=sortFunc, reverse=False )
        socketio.emit("player_list", data)
        print("ran", data)

    return 0


def sortFunc(player):
    try:
        return player["score"]
    except KeyError:
        return 0

def startLoop():
    # global log_file_length
    global log_file
    setup_output = setup()
    if setup_output["success"] is False:
        print(setup_output)
        return setup_output

    log_file.seek(0, 2)

    while os.path.exists(path_to_log):
        line = log_file.readline()
        if not line or len(line)<10:
            time.sleep(.1)
            pass
        process(line)
    print("Log lost")


def has_player(list, player):
    if isinstance(player, str):
        if list.count(player) > 0:
            return True
    else:
        for player in list:
            if player["ign"] == player:
                return True
    return False




if __name__ == "__main__":
    # webserver_thread = threading.Thread(target=socketio.run, args=(app, local_ip, target_port))
    chatlog_reader_thread = threading.Thread(target=startLoop)

    # webserver_thread.start()
    chatlog_reader_thread.start()
    socketio.run(app, local_ip, target_port)
    # webserver_thread.join()
    # chatlog_reader_thread.join()

    print("Exiting...")



