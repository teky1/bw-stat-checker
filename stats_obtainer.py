import requests
import time

cached_players = {}

def get_player_stats(player, api_key):


    if player in cached_players:
        return cached_players[player]

    data = requests.get(f"https://api.hypixel.net/player?key={api_key}&name={player}").json()

    if data["success"] is False or data["player"] is None:
        return {"success": False, "ign": player}

    try:
        bw_data = data["player"]["stats"]["Bedwars"]
    except KeyError:
        bw_data = {}

    try:
        final_kills = bw_data["final_kills_bedwars"]
    except KeyError:
        final_kills = 0

    try:
        final_deaths = bw_data["final_deaths_bedwars"]
    except KeyError:
        final_deaths = 1

    try:
        wins = bw_data["wins_bedwars"]
    except KeyError:
        wins = 0

    try:
        losses = bw_data["losses_bedwars"]
    except KeyError:
        losses = 1

    try:
        beds_broken = bw_data["beds_broken_bedwars"]
    except KeyError:
        beds_broken = 0

    try:
        beds_lost = bw_data["beds_lost_bedwars"]
    except KeyError:
        beds_lost = 1

    try:
        bw_star = data["player"]["achievements"]["bedwars_level"]
    except KeyError:
        bw_star = 0

    try:
        streak = bw_data["winstreak"]
    except KeyError:
        streak = 0

    player_data = {
        "success": True,
        "ign": player,
        "level": bw_star,
        "FKDR": round(final_kills/final_deaths, 2),
        "WLR": round(wins/losses, 2),
        "WS": streak,
        "BBLR": round(beds_broken/beds_lost, 2),
        "finals": final_kills,
        "wins": wins,
        "losses": losses,
        "score": round(bw_star*((final_kills/final_deaths)**2)),
    }
    cached_players[player] = player_data
    return player_data

