import json
from copy import deepcopy

from filters import get_default_filters
from models import Options
from server_sort import get_default_sort

DEFAULT_OPTIONS: Options = {
    "filters": get_default_filters(),
    "server_sort": get_default_sort(),
    "display": {
        "server_id": False,
        "host": False,
        "port": False,
        "ip": False,
        "name": True,
        "name_short": False,
        "region": True,
        "cc": False,
        "players": True,
        "max_players": True,
        "bots": True,
        "map": True,
        "game_types": False,
        "latitude": False,
        "longitude": False,
        "distance": False,
        "humans": False,
        "ping": True,
        "slots": False,
        "ip_port": False,
        "join_url": False,
        "last_played": True,
        "since_played": True,
    },
    "misc": {
        "always_ping": False,
        "auto_distance_calculation": True,
        "border_server_name": True,
        "cache_uncletopia_state": True,
        "disable_colors": False,
        "compact_output": False,
        "forced_width": 0,
        "play_sound_on_join": True,
        "query_steam": True,
        "refresh_interval": 5,
        "steam_username": "",
        "update_last_played_on_join_new_server": False,
        "use_emojis": False,
        "use_icons": False,
    },
}


def get_default_options() -> Options:
    return deepcopy(DEFAULT_OPTIONS)


def write_options(options: Options):
    try:
        with open("options.json", "w") as f:
            json.dump(options, f, indent=4)
    except Exception as e:
        print(f"Error writing options file: {e}")


def read_options() -> Options:
    try:
        with open("options.json", "r") as f:
            options: Options = json.load(f)
        return options
    except FileNotFoundError:
        print("No options file found, creating a new one.")
        write_options(DEFAULT_OPTIONS)
        return get_default_options()
