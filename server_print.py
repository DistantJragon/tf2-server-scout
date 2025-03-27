import shutil

from models import Options, Server
from object_grid.grid_layout import GridLayout
from server_main import (
    format_last_played,
    format_since_played,
    get_country_emoji,
    refresh_since_played,
)


def justify_strings(wd: int, lf: str = "", md: str = "", rt: str = "", em: str = " "):
    """
    Print a string justified to the left, middle, and right.
    """
    spaces = wd - len(lf) - len(md) - len(rt)
    if spaces < 0:
        raise ValueError("Width is too small")
    if len(em) != 1:
        raise ValueError("Empty string must be of length 1")
    if spaces % 2 == 0:
        lf += em * (spaces // 2)
        rt = em * (spaces // 2) + rt
    else:
        lf += em * (spaces // 2)
        rt = em * (spaces // 2 + 1) + rt
    return lf + md + rt


def print_server_grid(servers: list[Server], options: Options):
    """
    Print the servers in a grid layout.
    """
    grid = GridLayout()
    display = options["display"]
    misc = options["misc"]
    compact_output: bool = misc["compact_output"]
    use_emojis: bool = misc["use_emojis"]
    fast_mode: bool = misc["fast_grid_calculation"]
    for server in servers:
        grid_element = grid.new_element()
        middle = ""
        right = ""
        # Server Name / Name Short / Ping
        if display["name_short"] and not display["name"]:
            grid_element.add_line(middle=server["name_short"])
        else:
            grid_element.add_line(middle=server["name"])
            if display["name_short"]:
                middle = server["name_short"]
        if display["ping"] and server["ping"] >= 0:
            right = f"{int(server['ping'])}ms"
        if middle or right:
            grid_element.add_line(left=middle, right=right, empty=" ")
        # Structured Server Information
        # Region / CC and Players / Max Players
        left = ""
        right = ""
        if not compact_output and (display["region"] or display["cc"]):
            left += "Region: "
        if display["region"]:
            left += server["region"] + " "
        if display["cc"]:
            left += f"({server['cc']}) "
        if use_emojis and (display["region"] or display["cc"]):
            left += get_country_emoji(server["cc"])
        if display["players"]:
            right += str(server["players"])
        if display["max_players"]:
            right += f"/{server['max_players']}"
        if not compact_output and (display["players"] or display["max_players"]):
            right += " players"
        if left or right:
            grid_element.add_line(left=left, middle=" ",
                                  right=right, empty=" ")
        # Map / Bots
        left = ""
        right = ""
        if display["map"]:
            if not compact_output:
                left += "Playing on "
            left += server["map"]
        if display["bots"]:
            right += f"{server['bots']} bots"
        if left or right:
            grid_element.add_line(left=left, middle=" ",
                                  right=right, empty=" ")
        # Last / Since Played
        left = ""
        right = ""
        if display["last_played"]:
            if not compact_output:
                left += "Last played: "
            left += format_last_played(server)
        if display["since_played"]:
            refresh_since_played(server)
            right += format_since_played(server)
            if not compact_output:
                right += " ago"
        if left or right:
            grid_element.add_line(left=left, middle=" ",
                                  right=right, empty=" ")
        # Unstructured Server Information
        for key, item in display.items():
            if not item:
                continue
            if key in [
                "name",
                "name_short",
                "region",
                "cc",
                "players",
                "max_players",
                "bots",
                "map",
                "ping",
                "last_played",
                "since_played",
            ]:
                continue
            if key not in server:
                raise ValueError(f"Invalid display key: {key}")
            else:
                if not compact_output:
                    grid_element.add_line(left=f"{key}: {server[key]}")
                else:
                    grid_element.add_line(left=str(server[key]))

    print(grid.compile_grid(fast_mode))


def pretty_print_server(server: Server, options: Options, print_width: int = -1):
    """
    Pretty print a server for the user.
    Printing depends on the terminal width.
    """
    display = options["display"]
    misc = options["misc"]
    compact_output: bool = misc["compact_output"]
    MIN_WIDTH = 60
    if print_width < 0:
        print_width = misc["forced_width"]
        terminal_width = shutil.get_terminal_size(fallback=(-1, -1)).columns
        if print_width > terminal_width:
            print_width = int(terminal_width * 0.4)
        if print_width < MIN_WIDTH and not compact_output:
            print_width = MIN_WIDTH
    server_str = ""
    # Server Name / Name Short / Ping
    if misc["border_server_name"]:
        server_str += "-" * print_width + "\n"
        if display["name_short"] and not display["name"]:
            server_str += (
                justify_strings(print_width, "| ",
                                server["name_short"], " |") + "\n"
            )
        else:
            server_str += (
                justify_strings(print_width, "| ", server["name"], " |") + "\n"
            )
        right = ""
        if display["ping"] and server["ping"] >= 0:
            right = f"{int(server['ping'])}ms"
        server_str += (
            justify_strings(
                print_width, md=server["name_short"], rt=right, em="-")
            + "\n"
        )
    else:
        if not display["name"]:
            server_str += justify_strings(print_width,
                                          md=server["name_short"]) + "\n"
        else:
            server_str += justify_strings(print_width,
                                          md=server["name"]) + "\n"
            if display["name_short"]:
                server_str += (
                    justify_strings(
                        print_width, md=server["name_short"]) + "\n"
                )
    # Structured Server Information
    left = ""
    right = ""
    if not compact_output and (display["region"] or display["cc"]):
        left += "Region: "
    if display["region"]:
        left += server["region"] + " "
    if display["cc"]:
        left += f"({server['cc']}) "
    if misc["use_emojis"] and (display["region"] or display["cc"]):
        left += get_country_emoji(server["cc"])
    if display["players"]:
        right += str(server["players"])
    if display["max_players"]:
        right += f"/{server['max_players']}"
    if not compact_output and (display["players"] or display["max_players"]):
        right += " players"
    if left or right:
        server_str += justify_strings(print_width, lf=left, rt=right) + "\n"
    left = ""
    right = ""
    if display["map"]:
        if not compact_output:
            left += "Playing on "
        left += server["map"]
    if display["bots"]:
        right += f"{server['bots']} bots"
    if left or right:
        server_str += justify_strings(print_width, lf=left, rt=right) + "\n"
    # Last / Since Played
    left = ""
    right = ""
    if display["last_played"]:
        if not compact_output:
            left += "Last played: "
        left += format_last_played(server)
    if display["since_played"]:
        refresh_since_played(server)
        right += format_since_played(server)
        if not compact_output:
            right += " ago"
    if left or right:
        server_str += justify_strings(print_width, lf=left, rt=right) + "\n"
    # Unstructured Server Information
    for key, item in display.items():
        if not item:
            continue
        if key in [
            "name",
            "name_short",
            "region",
            "cc",
            "players",
            "max_players",
            "bots",
            "map",
            "ping",
            "last_played",
            "since_played",
        ]:
            continue
        if key not in server:
            raise ValueError(f"Invalid display key: {key}")
        else:
            if not compact_output:
                server_str += f"{key}: "
            server_str += f"{server[key]}\n"

    print(server_str)
