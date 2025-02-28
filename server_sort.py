import json
from typing import TypedDict

from server_types import Server, ServerField


class SortServer(TypedDict):
    sort_method: ServerField
    reverse: bool


class SortServerWritable(TypedDict):
    sort_method: str
    reverse: bool


DEFAULT_SORT = SortServer(sort_method=ServerField.PLAYERS, reverse=True)


def convert_sort_object(sort_object: SortServer) -> SortServerWritable:
    return SortServerWritable(
        sort_method=sort_object["sort_method"].value,
        reverse=sort_object["reverse"],
    )


def convert_sort_object_writeable(sort_object: SortServerWritable) -> SortServer:
    return SortServer(
        sort_method=ServerField(sort_object["sort_method"]),
        reverse=sort_object["reverse"],
    )


def write_sort(sort_object: SortServer):
    try:
        with open("sort.json", "w") as f:
            json.dump(convert_sort_object(sort_object), f, indent=4)
    except Exception as e:
        print(f"Error writing sort file: {e}")


def read_sort() -> SortServer:
    try:
        with open("sort.json", "r") as f:
            sort_object: SortServerWritable = json.load(f)
        return convert_sort_object_writeable(sort_object)
    except FileNotFoundError:
        print("No sort file found, creating a new one.")
        write_sort(DEFAULT_SORT)
        return DEFAULT_SORT.copy()


def sort_servers(servers: list[Server], sort_object: SortServer):
    """
    Sort the servers list passed in based on the sort object.
    Modifies the list in place.
    """
    if sort_object["sort_method"] == ServerField.GAME_TYPES:
        raise ValueError("Cannot sort by game types")
    servers.sort(
        key=lambda x: x[sort_object["sort_method"].value], reverse=sort_object["reverse"]
    )


def get_default_sort() -> SortServer:
    return DEFAULT_SORT.copy()
