import shutil
import time
from typing import Any

from filters import Filter, apply_filters
from options import Options
from server_sort import SortServer, sort_servers
from server_types import Server
from server_uncle import (
    compile_join_url,
    get_country_emoji,
    get_uncle,
    join_server,
    read_servers_from_file,
    update_servers_with_steam_info,
    write_servers_to_file,
)


def play_sound():
    import platform

    if platform.system() == "Windows":
        import winsound

        winsound.Beep(440, 500)
        winsound.MessageBeep(winsound.MB_ICONHAND)


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
        if print_width < terminal_width:
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
    server_str += justify_strings(print_width, lf=left, rt=right) + "\n"
    left = ""
    right = ""
    if display["map"]:
        if not compact_output:
            left += "Playing on "
        left += server["map"]
    if display["bots"]:
        right += f"{server['bots']} bots"
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
        ]:
            continue
        if key == "ip_port":
            server_str += f"{server['ip']}:{server['port']}\n"
        elif key == "join_url":
            server_str += f"{compile_join_url(server)}\n"
        elif key not in Server.__annotations__:
            raise ValueError(f"Invalid display key: {key}")
        else:
            if not compact_output:
                server_str += f"{key}: "
            server_str += f"{server[key]}\n"

    print(server_str)


def auto_join(args: Any, servers: list[Server], options: Options):
    """
    Continuously search for a server based on saved filters and join it when found.
    """
    filters = options["filters"]
    server_sort = options["server_sort"]
    found_server = False
    ping_servers: bool = args.ping_servers or options["misc"]["always_ping"]
    calculate_max_distance: bool = (
        options["misc"]["auto_distance_calculation"]
        and filters["distance"]["max"] is None
    )
    misc = options["misc"]
    try:
        while not found_server:
            if misc["query_steam"]:
                update_servers_with_steam_info(servers)
            else:
                servers, new_max_distance = get_uncle(
                    ping_servers, calculate_max_distance
                )

                if new_max_distance is not None:
                    filters["distance"]["max"] = new_max_distance

            filtered_servers = apply_filters(servers, filters)
            if not filtered_servers:
                print("No servers found, waiting for refresh")
                time.sleep(args.refresh_interval)
                continue
            sort_servers(filtered_servers, server_sort)
            found_server = True
            server_to_join = filtered_servers[0]
            join_server(server_to_join)
            pretty_print_server(server_to_join, options)
            if misc["play_sound_on_join"]:
                play_sound()
    except KeyboardInterrupt:
        print("User interrupted search")


def quick_print(args: Any, servers: list[Server], options: Options, ):
    """
    Print all servers that fit the filters and exit.
    """
    filters = options["filters"]
    server_sort = options["server_sort"]
    misc = options["misc"]
    ping_servers: bool = args.ping_servers or options["misc"]["always_ping"]
    calculate_max_distance = (
        options["misc"]["auto_distance_calculation"]
        and filters["distance"]["max"] is None
    )
    if misc["query_steam"]:
        if servers is None:
            servers = read_servers_from_file()
        update_servers_with_steam_info(servers)
    else:
        servers, new_max_distance = get_uncle(
            ping_servers, calculate_max_distance)
        if new_max_distance is not None:
            filters["distance"]["max"] = new_max_distance
    server_list = apply_filters(servers, filters)
    sort_servers(server_list, server_sort)
    if server_list:
        for server in server_list:
            pretty_print_server(server, options)

    else:
        print("No servers found")
