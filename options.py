import json
from typing import Any, TypedDict

from filters import Filter, get_default_filters
from server_sort import (
    SortServer,
    SortServerWritable,
    convert_sort_object,
    convert_sort_object_writeable,
    get_default_sort,
)


class DisplayOptions(TypedDict):
    server_id: bool
    host: bool
    port: bool
    ip: bool
    name: bool
    name_short: bool
    region: bool
    cc: bool
    players: bool
    max_players: bool
    bots: bool
    map: bool
    game_types: bool
    latitude: bool
    longitude: bool
    distance: bool
    ping: bool
    ip_port: bool
    join_url: bool


class Options(TypedDict):
    filters: Filter
    server_sort: SortServer
    display: DisplayOptions
    misc: dict[str, Any]


class OptionsWritable(TypedDict):
    filters: Filter
    server_sort: SortServerWritable
    display: DisplayOptions
    misc: dict[str, Any]


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
        "ping": True,
        "ip_port": False,
        "join_url": False,
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
        "use_emojis": False,
        "use_icons": False,
    },
}


def convert_options_object(options: Options) -> OptionsWritable:
    return OptionsWritable(
        filters=options["filters"],
        server_sort=convert_sort_object(options["server_sort"]),
        display=options["display"],
        misc=options["misc"],
    )


def convert_options_object_writeable(options_writable: OptionsWritable) -> Options:
    return Options(
        filters=options_writable["filters"],
        server_sort=convert_sort_object_writeable(
            options_writable["server_sort"]),
        display=options_writable["display"],
        misc=options_writable["misc"],
    )


def write_options(options: Options):
    try:
        with open("options.json", "w") as f:
            json.dump(convert_options_object(options), f, indent=4)
    except Exception as e:
        print(f"Error writing options file: {e}")


def read_options() -> Options:
    try:
        with open("options.json", "r") as f:
            options: OptionsWritable = json.load(f)
        return convert_options_object_writeable(options)
    except FileNotFoundError:
        print("No options file found, creating a new one.")
        write_options(DEFAULT_OPTIONS)
        return DEFAULT_OPTIONS.copy()


def get_default_options() -> Options:
    return DEFAULT_OPTIONS.copy()
