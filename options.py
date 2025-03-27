import json
from copy import deepcopy

from filters import get_default_filters
from models import Options
from server_sort import get_default_sort

DEFAULT_OPTIONS: Options = {
    "filters": get_default_filters(),
    "server_sort": get_default_sort(),
    "display": {
        "server_id": "0",
        "host": "0",
        "port": "0",
        "ip": "0",
        "name": "c",
        "name_short": "0",
        "region": "f",
        "cc": "0",
        "players": "f",
        "max_players": "f",
        "bots": "f",
        "map": "c",
        "game_types": "0",
        "latitude": "0",
        "longitude": "0",
        "distance": "0",
        "humans": "0",
        "ping": "f",
        "slots": "0",
        "ip_port": "0",
        "join_url": "0",
        "last_played": "f",
        "since_played": "f",
    },
    "misc": {
        "always_ping": False,
        "auto_distance_calculation": True,
        "border_server_name": True,
        "cache_uncletopia_state": True,
        "disable_colors": False,
        "compact_output": False,
        "fast_grid_calculation": False,
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
