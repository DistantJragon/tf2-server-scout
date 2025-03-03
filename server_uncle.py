import concurrent.futures
import json
import os
import re
import subprocess
import webbrowser
from copy import deepcopy
from platform import system

import a2s
import requests

from models import Server

COUNTRY_EMOJIS: dict[str, str] = {
    "ca": "🇨🇦",
    "gb": "🇬🇧",
    "au": "🇦🇺",
    "br": "🇧🇷",
    "de": "🇩🇪",
    "us": "🇺🇸",
    "hk": "🇭🇰",
    "pl": "🇵🇱",
}


def write_servers_to_file(servers: list[Server], dirty: bool = True):
    """
    Caches the servers to ./cache/servers.json
    Create cache directory if it doesn't exist.
    """

    if not os.path.exists("cache"):
        os.makedirs("cache")
    with open("cache/servers.json", "w") as file:
        json.dump(servers, file, indent=4)
    if dirty:
        with open("cache/dirty.info", "w") as file:
            _ = file.write("")


def check_cache_dirty() -> bool:
    """
    Check if the cache is dirty.
    """
    return os.path.exists("cache/dirty.info")


def clean_write_servers_to_file(servers: list[Server]):
    """
    Caches the servers to ./cache/servers.json
    Create cache directory if it doesn't exist.
    Fills values that change with each request with unusual values so that the user can see that the data is old.
    Will be slower, use other function if user may be trying use the program quickly.
    """
    servers_copy = deepcopy(servers)
    for server in servers_copy:
        server["players"] = -1
        server["max_players"] = -1
        server["bots"] = -1
        server["ping"] = -1.0
        server["slots"] = -1
        server["map"] = "[Outdated]"

    write_servers_to_file(servers_copy, False)
    if os.path.exists("cache/dirty.info"):
        os.remove("cache/dirty.info")


def read_servers_from_file() -> list[Server]:
    """
    Reads the servers from ./cache/servers.json
    If the file doesn't exist, return an empty list.
    """
    try:
        with open("cache/servers.json", "r") as file:
            servers: list[Server] = json.load(file)
            return servers
    except FileNotFoundError:
        return []


def get_country_emoji(cc: str) -> str:
    return COUNTRY_EMOJIS.get(cc, "")


def test_ping_uncle(server: Server | str) -> float:
    """
    Test the ping of a server using the ping command.
    Platform specific commands are used to ping the server.
    """
    ip = ""
    if isinstance(server, str):
        ip = server
    else:
        ip = server["ip"]
    if system() == "Windows":
        command = f"ping -n 1 -w 1000 {ip}"
    else:
        command = f"ping -c 1 -W 1 {ip}"
    try:
        output = subprocess.check_output(command, shell=True)
        # Look for the time= part of the output (e.g. time=10ms or time=10.0 ms)
        time = re.search(r"time=(\d+\.\d+|\d+)", output.decode())
        if time is None:
            return -1
        return float(time.group(1))
    except Exception as e:
        print(f"Error pinging server {ip} in test_ping_uncle: {e}")
        return -1


def ping_multiple_servers_uncle(servers: list[Server]) -> dict[str, float]:
    """
    Pings multiple servers concurrently and returns their latency in a dictionary.
    """
    results: dict[str, float] = {}
    unique_ips = {server["ip"] for server in servers}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(test_ping_uncle, ip)
                                   : ip for ip in unique_ips}
        for future in concurrent.futures.as_completed(futures):
            ip = futures[future]
            try:
                results[ip] = future.result()
            except Exception as e:
                print(
                    f"Error pinging server {ip} in ping_multiple_servers_uncle: {e}")
                results[ip] = -1
    return results


def compile_join_url(server: Server) -> str:
    return f"steam://connect/{server['ip']}:{server['port']}"


def get_uncle(
    ping: bool, calculate_max_distance: bool
) -> tuple[list[Server], float | None]:
    """
    Get the server list from the UncleTopia API
    https://uncletopia.com/api/servers/state
    The state API returns a JSON object with the following format:
    { "servers": [Server], lat_long: { "latitude": float, "longitude": float } }
    """
    response = requests.get("https://uncletopia.com/api/servers/state")
    servers: list[Server] = response.json()["servers"]
    max_distance_filter = None
    if ping or calculate_max_distance:
        ping_results = ping_multiple_servers_uncle(servers)
        for server in servers:
            server["ping"] = ping_results.get(server["ip"], -1)
    else:
        for server in servers:
            server["ping"] = -1
    if calculate_max_distance:
        from estimate_max_distance import estimate_max_distance

        max_distance_filter = estimate_max_distance(servers)

    for server in servers:
        server["slots"] = server["max_players"] - server["players"]
        server["ip_port"] = f"{server['ip']}:{server['port']}"
        server["join_url"] = compile_join_url(server)

    return servers, max_distance_filter


def update_cache_uncle(
    calculate_max_distance: bool,
) -> tuple[list[Server], float | None]:
    """
    Update the cache of servers from the UncleTopia API.
    """
    servers, new_max_distance = get_uncle(False, calculate_max_distance)
    write_servers_to_file(servers)
    return servers, new_max_distance


def update_server_with_steam_info(server: Server):
    """
    Update the server information with the steam information.
    Updates player count, map, and ping.
    """
    try:
        info = a2s.info((server["ip"], server["port"]))
        server["players"] = info.player_count
        server["max_players"] = info.max_players
        server["slots"] = info.max_players - info.player_count
        server["bots"] = info.bot_count
        server["map"] = info.map_name
        server["ping"] = info.ping * 1000
    except Exception as e:
        print(
            f"Error updating server {server['ip']} with steam info in update_server_with_steam_info: {e}"
        )


def update_servers_with_steam_info(servers: list[Server]):
    """
    Update the server information with the steam information.
    Updates player count, map, and ping.
    """

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(update_server_with_steam_info, server): server
            for server in servers
        }
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                server_ip = futures[future]["ip"]
                print(
                    f"Error updating server {server_ip} with steam info in update_servers_with_steam_info: {e}"
                )


def join_server(server: Server | str):
    if isinstance(server, str):
        _ = webbrowser.open(server)
    else:
        _ = webbrowser.open(compile_join_url(server))


def print_server_for_user(server: Server):
    """
    Pretty print the server information for the user.
    Should look nice and organized while being compact, informative and easy to read.
    (Primitive)
    """
    separator_len = len(server["name"]) + 4
    separator_single = "-"
    print(f"{separator_single * separator_len}")
    print(f"| {server['name']} |")
    print(f"{separator_single * separator_len}")

    print(f"Region: {server['region']}", end=" | ")
    print(
        f"{server['players']}/{server['max_players']} players, {server['bots']} bots")
    # Map
    print(f"Playing on {server['map']}")
    print(f"Join: {compile_join_url(server)}")
