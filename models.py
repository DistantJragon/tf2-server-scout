from typing import TypedDict

from user_template import TemplateFunction


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
    # Fields not given by the Uncletopia API
    ping: float
    slots: int
    ip_port: str
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


class DisplayLine(TypedDict):
    left: str
    middle: str
    right: str
    empty: str


class DisplayLineCompiled(TypedDict):
    left: TemplateFunction
    middle: TemplateFunction
    right: TemplateFunction
    empty: str


class DisplayOptions(TypedDict):
    grid_display: list[DisplayLine]
    grid_display_compiled: list[DisplayLineCompiled] | None
    join_display: list[DisplayLine]
    join_display_compiled: list[DisplayLineCompiled] | None


class MiscOptions(TypedDict):
    always_ping: bool
    auto_distance_calculation: bool
    cache_uncletopia_state: bool
    disable_colors: bool
    compact_output: bool
    fast_grid_calculation: bool
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
