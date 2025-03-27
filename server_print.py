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
    use_emojis: bool = misc["use_emojis"]
    fast_mode: bool = misc["fast_grid_calculation"]
    for server in servers:
        grid_element = grid.new_element()
        middle = ""
        right = ""
        # Server Name / Name Short / Ping
        if display["name_short"] != "0" and display["name"] == "0":
            middle = server["name_short"]
        else:
            if display["name"] == "c":
                to_strip = "Uncletopia | "
                if server["name"].startswith(to_strip):
                    name_stripped = server["name"][len(to_strip):]
                else:
                    name_stripped = server["name"]
                grid_element.add_line(middle=name_stripped)
        if display["ping"] != "0" and server["ping"] >= 0:
            if display["ping"] == "f":
                right = f"{int(server['ping'])}ms"
            else:
                right = str(int(server["ping"]))
        if middle or right:
            grid_element.add_line(left=middle, right=right, empty=" ")
        # Structured Server Information
        # Region / CC and Players / Max Players
        left = ""
        right = ""
        if display["region"] != "0" or display["cc"] != "0":
            if display["region"] == "f" and display["cc"] == "f":
                left += "Region: "
            if display["region"] != "0":
                left += f"{server['region']}"
            if display["cc"] != "0":
                left += f" ({server['cc']})"
            if use_emojis:
                left += " " + get_country_emoji(server["cc"])
        if display["players"] != "0" or display["max_players"] != "0":
            if display["players"] != "0":
                right += str(server["players"])
            if display["max_players"] != "0":
                right += f"/{server['max_players']}"
            if display["players"] == "f" and display["max_players"] == "f":
                right += " players"
        if left or right:
            grid_element.add_line(left=left, middle=" ",
                                  right=right, empty=" ")
        # Map / Bots
        left = ""
        right = ""
        if display["map"] == "f":
            left += f"Playing on {server['map']}"
        elif display["map"] == "c":
            left += server["map"]
        if display["bots"] == "f":
            right += f"{server['bots']} bots"
        elif display["bots"] == "c":
            right += str(server["bots"])
        if left or right:
            grid_element.add_line(left=left, middle=" ",
                                  right=right, empty=" ")
        # Last / Since Played
        left = ""
        right = ""
        if display["last_played"] != "0":
            if server["last_played"] == -1:
                left += "Never played"
            else:
                if display["last_played"] == "f":
                    left += f"Played: {format_last_played(server)}"
                else:
                    left += format_last_played(server)
        if display["since_played"] == "f":
            refresh_since_played(server)
            right += f"{format_since_played(server)} ago"
        elif display["since_played"] == "c":
            refresh_since_played(server)
            right += format_since_played(server)
        if left or right:
            grid_element.add_line(left=left, middle=" ",
                                  right=right, empty=" ")
        # Unstructured Server Information
        for key, item in display.items():
            if item == "0":
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
                if display[key] == "f":
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
    if print_width < 0:
        print_width = misc["forced_width"]
        if print_width == 0:
            terminal_width = shutil.get_terminal_size(
                fallback=(-1, -1)).columns
            print_width = int(terminal_width * 0.4)
    server_str = ""
    # Server Name / Name Short / Ping
    middle = ""
    right = ""
    if misc["border_server_name"]:
        server_str += "-" * print_width + "\n"
        if display["name_short"] != "0" and display["name"] == "0":
            middle = server["name_short"]
        elif display["name"] == "c":
            strip = "Uncletopia | "
            if server["name"].startswith(strip):
                server_str += (
                    justify_strings(
                        print_width, "| ", server["name"][len(strip):], " |"
                    )
                    + "\n"
                )
            else:
                server_str += (
                    justify_strings(print_width, "| ",
                                    server["name"], " |") + "\n"
                )
        else:
            server_str += (
                justify_strings(print_width, "| ", server["name"], " |") + "\n"
            )
        if display["ping"] != "0" and server["ping"] >= 0:
            right = f"{int(server['ping'])}ms"
        server_str += (
            justify_strings(
                print_width, md=server["name_short"], rt=right, em="-")
            + "\n"
        )
    else:
        if display["name"]:
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
    # Region / CC and Players / Max Players
    left = ""
    right = ""
    if display["region"] != "0" or display["cc"] != "0":
        if display["region"] == "f" and display["cc"] == "f":
            left += "Region: "
        if display["region"] != "0":
            left += f"{server['region']} "
        if display["cc"] != "0":
            left += f" ({server['cc']})"
        if misc["use_emojis"]:
            left += " " + get_country_emoji(server["cc"])
    if display["players"] != "0":
        right += f"{server['players']}"
    if display["max_players"] != "0":
        right += f"/{server['max_players']}"
    if display["players"] == "f" and display["max_players"] == "f":
        right += " players"
    if left or right:
        server_str += justify_strings(print_width, lf=left, rt=right) + "\n"
    # Map / Bots
    left = ""
    right = ""
    if display["map"] != "0":
        if display["map"] == "f":
            left += "Playing on "
        left += server["map"]
    if display["bots"] != "0":
        right += f"{server['bots']} bots"
    if left or right:
        server_str += justify_strings(print_width, lf=left, rt=right) + "\n"
    # Last / Since Played
    left = ""
    right = ""
    if display["last_played"] != "0":
        if server["last_played"] == -1:
            left += "Never played"
        else:
            if display["last_played"] == "f":
                left += "Played: "
            left += format_last_played(server)
    if display["since_played"] != "0":
        refresh_since_played(server)
        right += format_since_played(server)
        if display["since_played"] == "f":
            right += " ago"
    if left or right:
        server_str += justify_strings(print_width, lf=left, rt=right) + "\n"
    # Unstructured Server Information
    for key, item in display.items():
        if item == "0":
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
            if item == "f":
                server_str += f"{key}: "
            server_str += f"{server[key]}\n"

    print(server_str)
