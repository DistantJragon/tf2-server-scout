import json
from copy import deepcopy

from models import Server, SortServerOptions

DEFAULT_SORT: SortServerOptions = {"sort_by": "players", "reverse": True}


def get_default_sort() -> SortServerOptions:
    return deepcopy(DEFAULT_SORT)


def write_sort(sort_object: SortServerOptions):
    try:
        with open("sort.json", "w") as f:
            json.dump(sort_object, f, indent=4)
    except Exception as e:
        print(f"Error writing sort file: {e}")


def read_sort() -> SortServerOptions:
    try:
        with open("sort.json", "r") as f:
            sort_object: SortServerOptions = json.load(f)
        return sort_object
    except FileNotFoundError:
        print("No sort file found, creating a new one.")
        write_sort(DEFAULT_SORT)
        return get_default_sort()


def sort_servers(servers: list[Server], sort_object: SortServerOptions):
    """
    Sort the servers list passed in based on the sort object.
    Modifies the list in place.
    """
    if not servers:
        return
    if sort_object["sort_by"] not in servers[0]:
        raise ValueError("Invalid sort key")
    if sort_object["sort_by"] == "game_types":
        raise ValueError("Cannot sort by game types")
    servers.sort(
        key=lambda x: x[sort_object["sort_by"]], reverse=sort_object["reverse"]
    )
