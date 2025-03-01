from typing import Any, Literal, TypedDict

ServerFieldLiteral = Literal[
    "server_id",
    "host",
    "port",
    "ip",
    "name",
    "name_short",
    "region",
    "cc",
    "players",
    "max_players",
    "bots",
    "map",
    "game_types",
    "latitude",
    "longitude",
    "distance",
    "humans",
    "ping",
    "slots",
    "ip_port",
    "join_url",
]


class Server(TypedDict):
    server_id: int
    host: str
    port: int
    ip: str
    name: str
    name_short: str
    region: str
    cc: str
    players: int
    max_players: int
    bots: int
    map: str
    game_types: list[str]
    latitude: float
    longitude: float
    distance: float
    humans: int
    ping: float
    slots: int
    ip_port: str
    join_url: str


class SortServerOptions(TypedDict):
    sort_by: ServerFieldLiteral
    reverse: bool


class ListFilter(TypedDict):
    values: list[str | int]
    exclude: bool


class RangeFilter(TypedDict):
    min: int | float | None
    max: int | float | None


class ServerFilter(TypedDict):
    server_id: ListFilter
    region: ListFilter
    cc: ListFilter
    players: RangeFilter
    max_players: RangeFilter
    bots: RangeFilter
    map: ListFilter
    distance: RangeFilter
    ping: RangeFilter
    slots: RangeFilter
    ip_port: ListFilter


class DisplayOptions(TypedDict):
    server_id: bool
    host: bool
    port: bool
    ip: bool
    name: bool
    name_short: bool
    region: bool
    cc: bool
    players: bool
    max_players: bool
    bots: bool
    map: bool
    game_types: bool
    latitude: bool
    longitude: bool
    distance: bool
    humans: bool
    ping: bool
    slots: bool
    ip_port: bool
    join_url: bool


class Options(TypedDict):
    filters: ServerFilter
    server_sort: SortServerOptions
    display: DisplayOptions
    misc: dict[str, Any]
