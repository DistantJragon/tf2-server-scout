from typing import TypedDict


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
    last_played: float
    since_played: float


class SortServerOptions(TypedDict):
    sort_by: str
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
    since_played: RangeFilter


class DisplayOptions(TypedDict):
    server_id: str
    host: str
    port: str
    ip: str
    name: str
    name_short: str
    region: str
    cc: str
    players: str
    max_players: str
    bots: str
    map: str
    game_types: str
    latitude: str
    longitude: str
    distance: str
    humans: str
    ping: str
    slots: str
    ip_port: str
    join_url: str
    last_played: str
    since_played: str


class MiscOptions(TypedDict):
    always_ping: bool
    auto_distance_calculation: bool
    border_server_name: bool
    cache_uncletopia_state: bool
    disable_colors: bool
    compact_output: bool
    fast_grid_calculation: bool
    forced_width: int
    play_sound_on_join: bool
    query_steam: bool
    refresh_interval: float
    steam_username: str
    update_last_played_on_join_new_server: bool
    use_emojis: bool
    use_icons: bool


class Options(TypedDict):
    filters: ServerFilter
    server_sort: SortServerOptions
    display: DisplayOptions
    misc: MiscOptions
