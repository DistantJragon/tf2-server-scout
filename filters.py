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
    "since_played": {"min": None, "max": None},
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
        return get_default_filters()


def apply_filters(
    servers: list[Server], server_filter: ServerFilter, print_stats: bool = False
) -> list[Server]:
    filtered_servers: list[Server] = []
    for server in servers:
        failed = False
        reason = None
        for key, item in server.items():
            reason = key
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
                if key == "since_played" and item == -1:
                    # Sever has never been played, skip this filter
                    continue
                if range_filter["min"] is not None and item < range_filter["min"]:
                    failed = True
                    break
                if range_filter["max"] is not None and item > range_filter["max"]:
                    failed = True
                    break
            else:
                raise ValueError(f"Invalid filter key: {key}")

        if not failed:
            filtered_servers.append(server)
        elif print_stats and reason is not None:
            print(f"{server['name']} failed on {reason} filter")

    return filtered_servers


def apply_pre_filters(
    servers: list[Server], server_filter: ServerFilter, print_stats: bool = False
) -> list[Server]:
    """
    Make new filters such that the filter criteria is only ones that don't vary often
    (e.g cc, region, map, ip_port)
    """
    pre_filters = deepcopy(server_filter)
    pre_filters["players"] = {"min": None, "max": None}
    pre_filters["map"] = {"values": [], "exclude": True}
    pre_filters["slots"] = {"min": None, "max": None}
    pre_filters["since_played"] = {"min": None, "max": None}
    return apply_filters(servers, pre_filters, print_stats)
