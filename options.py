import json
from copy import deepcopy

from filters import get_default_filters
from models import DisplayLine, Options
from object_grid.grid_layout import GridLayout
from server_sort import get_default_sort
from user_template import compile_template

DEFAULT_OPTIONS: Options = {
    "filters": get_default_filters(),
    "server_sort": get_default_sort(),
    "display": {
        "grid_display": [
            {"left": "{index}.", "middle": "{name_utrim}", "right": "", "empty": " "},
            {"left": "", "middle": "{name_short}",
                "right": "{ping}ms", "empty": " "},
            {
                "left": "{region} ({cc})",
                "middle": " ",
                "right": "{players}/{max_players} players",
                "empty": " ",
            },
            {
                "left": "{map}",
                "middle": " ",
                "right": "{bots} bots",
                "empty": " ",
            },
            {
                "left": "{last_played}",
                "middle": " ",
                "right": "{since_played} ago",
                "empty": " ",
            },
        ],
        "grid_display_compiled": None,
        "join_display": [
            {"left": "", "middle": "", "right": "", "empty": "-"},
            {"left": "|", "middle": "{name_utrim}", "right": "|", "empty": " "},
            {"left": "", "middle": "{name_short}",
                "right": "{ping}ms", "empty": "-"},
            {
                "left": "{region} ({cc})",
                "middle": " ",
                "right": "{players}/{max_players} players",
                "empty": " ",
            },
            {
                "left": "{map}",
                "middle": " ",
                "right": "{bots} bots",
                "empty": " ",
            },
            {
                "left": "{last_played}",
                "middle": " ",
                "right": "{since_played} ago",
                "empty": " ",
            },
        ],
        "join_display_compiled": None,
    },
    "misc": {
        "always_ping": False,
        "auto_distance_calculation": True,
        "cache_uncletopia_state": True,
        "disable_colors": False,
        "compact_output": False,
        "fast_grid_calculation": False,
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
    options_copy = deepcopy(options)
    options_copy["display"]["grid_display_compiled"] = None
    options_copy["display"]["join_display_compiled"] = None
    try:
        with open("options.json", "w") as f:
            json.dump(options_copy, f, indent=4)
    except Exception as e:
        print(f"Error writing options file: {e}")


def compile_display_options(options: Options):
    options["display"]["grid_display_compiled"] = [
        {
            "left": compile_template(line["left"]),
            "middle": compile_template(line["middle"]),
            "right": compile_template(line["right"]),
            "empty": line["empty"],
        }
        for line in options["display"]["grid_display"]
    ]
    options["display"]["join_display_compiled"] = [
        {
            "left": compile_template(line["left"]),
            "middle": compile_template(line["middle"]),
            "right": compile_template(line["right"]),
            "empty": line["empty"],
        }
        for line in options["display"]["join_display"]
    ]


def read_options() -> Options:
    try:
        with open("options.json", "r") as f:
            options: Options = json.load(f)
        compile_display_options(options)
        return options
    except FileNotFoundError:
        print("No options file found, creating a new one.")
        write_options(DEFAULT_OPTIONS)
        options = get_default_options()
        compile_display_options(options)
        return options


def display_lines_to_string(options: list[DisplayLine]):
    """
    Print the display options.
    """
    grid = GridLayout()
    grid_element = grid.new_element()
    for line in options:
        grid_element.add_line(
            line["left"], line["middle"], line["right"], line["empty"]
        )
    return grid.compile_grid()
