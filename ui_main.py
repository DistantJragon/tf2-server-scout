import time
from typing import Any

from filters import apply_filters
from models import Options, Server
from server_main import (get_uncle, join_server, refresh_since_played_all,
                         update_servers_with_steam_info)
from server_print import pretty_print_server, print_server_grid
from server_sort import sort_servers


def play_sound():
    import platform

    if platform.system() == "Windows":
        import winsound

        winsound.Beep(440, 500)
        winsound.MessageBeep(winsound.MB_ICONHAND)


def auto_join(args: Any, servers: list[Server], options: Options) -> Server | None:
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
    refresh_interval: float = misc["refresh_interval"]
    if args.refresh_interval is not None:
        refresh_interval = float(args.refresh_interval)
    try:
        while not found_server:
            if misc["query_steam"]:
                update_servers_with_steam_info(servers, misc["steam_username"])
            else:
                servers, new_max_distance = get_uncle(
                    ping_servers, calculate_max_distance
                )

                if new_max_distance is not None:
                    filters["distance"]["max"] = new_max_distance

            refresh_since_played_all(servers)
            filtered_servers = apply_filters(servers, filters)
            if not filtered_servers:
                print("No servers found, waiting for refresh")
                time.sleep(refresh_interval)
                continue
            sort_servers(filtered_servers, server_sort)
            found_server = True
            server_to_join: Server = filtered_servers[0]
            if not args.disable_join:
                join_server(server_to_join)
            pretty_print_server(server_to_join, options)
            if args.disable_join or misc["auto_join_command"]:
                print(
                    f"Join command:\nconnect {server_to_join['ip']}:{server_to_join['port']}")
            if misc["play_sound_on_join"]:
                play_sound()
            return server_to_join
    except KeyboardInterrupt:
        print("User interrupted search")
        return None
    return None


def quick_print(
    args: Any,
    servers: list[Server],
    options: Options,
):
    """
    Print all servers that fit the filters and exit.
    """
    filters = options["filters"]
    server_sort = options["server_sort"]
    misc = options["misc"]
    if misc["query_steam"]:
        update_servers_with_steam_info(servers)
    else:
        ping_servers: bool = args.ping_servers or options["misc"]["always_ping"]
        calculate_max_distance = (
            options["misc"]["auto_distance_calculation"]
            and filters["distance"]["max"] is None
        )
        servers, new_max_distance = get_uncle(
            ping_servers, calculate_max_distance)
        if new_max_distance is not None:
            filters["distance"]["max"] = new_max_distance
    server_list = apply_filters(servers, filters)
    if server_list:
        sort_servers(server_list, server_sort)
        print_server_grid(server_list, options)
    else:
        print("No servers found")
