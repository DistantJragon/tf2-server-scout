import json
from enum import Enum
from typing import Any, TypeAlias

from server_types import Server

Filter: TypeAlias = dict[str, dict[str, Any]]


class FilterType(Enum):
    LIST = 1
    RANGE = 2


FILTER_TYPES: dict[str, FilterType] = {
    "server_id": FilterType.LIST,
    "region": FilterType.LIST,
    "cc": FilterType.LIST,
    "players": FilterType.RANGE,
    "max_players": FilterType.RANGE,
    "bots": FilterType.RANGE,
    "map": FilterType.LIST,
    "distance": FilterType.RANGE,
    "ping": FilterType.RANGE,
}

DEFAULT_FILTERS: Filter = {
    "server_id": {"list": [], "blacklist": True},
    "region": {"list": [], "blacklist": True},
    "cc": {"list": [], "blacklist": True},
    "players": {"min": None, "max": None},
    "max_players": {"min": None, "max": None},
    "bots": {"min": None, "max": None},
    "map": {"list": [], "blacklist": True},
    "distance": {"min": None, "max": None},
    "ping": {"min": None, "max": 150.0},
}


def write_filters(filters: Filter):
    try:
        with open("filters.json", "w") as f:
            json.dump(filters, f, indent=4)
    except Exception as e:
        print(f"Error writing filters file: {e}")


def read_filters() -> Filter:
    try:
        with open("filters.json", "r") as f:
            filters: Filter = json.load(f)
        return filters
    except FileNotFoundError:
        print("No filters file found, creating a new one.")
        write_filters(DEFAULT_FILTERS)
        return DEFAULT_FILTERS.copy()


def apply_filters(servers: list[Server], filters: Filter) -> list[Server]:
    filtered_servers: list[Server] = []
    for server in servers:
        failed = False
        for key, item in server.items():
            if item is None:
                continue
            if key not in filters:
                continue
            if FILTER_TYPES[key] == FilterType.LIST:
                in_list = item in filters[key]["list"]
                if in_list and filters[key]["blacklist"]:
                    failed = True
                    break
                if not in_list and not filters[key]["blacklist"]:
                    failed = True
                    break
            elif FILTER_TYPES[key] == FilterType.RANGE:
                if filters[key]["min"] is not None and item < filters[key]["min"]:
                    failed = True
                    break
                if filters[key]["max"] is not None and item > filters[key]["max"]:
                    failed = True
                    break
        if not failed:
            filtered_servers.append(server)

    return filtered_servers


def get_default_filters() -> Filter:
    return DEFAULT_FILTERS.copy()


def get_filter_types() -> dict[str, FilterType]:
    return FILTER_TYPES.copy()
