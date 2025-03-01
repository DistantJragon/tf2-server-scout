import json
from copy import deepcopy

from models import ListFilter, RangeFilter, Server, ServerFilter

DEFAULT_FILTERS: ServerFilter = {
    "server_id": {"values": [], "exclude": True},
    "region": {"values": [], "exclude": True},
    "cc": {"values": [], "exclude": True},
    "players": {"min": None, "max": None},
    "max_players": {"min": None, "max": None},
    "bots": {"min": None, "max": None},
    "map": {"values": [], "exclude": True},
    "distance": {"min": None, "max": None},
    "ping": {"min": None, "max": 150.0},
    "slots": {"min": None, "max": None},
    "ip_port": {"values": [], "exclude": True},
}


def get_default_filters() -> ServerFilter:
    return deepcopy(DEFAULT_FILTERS)


def write_filters(filters: ServerFilter):
    try:
        with open("filters.json", "w") as f:
            json.dump(filters, f, indent=4)
    except Exception as e:
        print(f"Error writing filters file: {e}")


def read_filters() -> ServerFilter:
    try:
        with open("filters.json", "r") as f:
            filters: ServerFilter = json.load(f)
        return filters
    except FileNotFoundError:
        print("No filters file found, creating a new one.")
        write_filters(DEFAULT_FILTERS)
        return DEFAULT_FILTERS.copy()


def apply_filters(servers: list[Server], server_filter: ServerFilter) -> list[Server]:
    filtered_servers: list[Server] = []
    for server in servers:
        failed = False
        for key, item in server.items():
            if item is None:
                continue
            if key not in server_filter:
                continue
            if "values" in server_filter[key]:
                list_filter: ListFilter = server_filter[key]
                in_list = item in list_filter["values"]
                if in_list and list_filter["exclude"]:
                    failed = True
                    break
                if not in_list and not list_filter["exclude"]:
                    failed = True
                    break
            elif "min" in server_filter[key]:
                range_filter: RangeFilter = server_filter[key]
                if range_filter["min"] is not None and item < range_filter["min"]:
                    failed = True
                    break
                if range_filter["max"] is not None and item > range_filter["max"]:
                    failed = True
                    break

        if not failed:
            filtered_servers.append(server)

    return filtered_servers
