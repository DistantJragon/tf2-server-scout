from enum import Enum
from typing import TypedDict


class ServerField(Enum):
    SERVER_ID = "server_id"
    HOST = "host"
    PORT = "port"
    IP = "ip"
    NAME = "name"
    NAME_SHORT = "name_short"
    REGION = "region"
    CC = "cc"
    PLAYERS = "players"
    MAX_PLAYERS = "max_players"
    BOTS = "bots"
    MAP = "map"
    GAME_TYPES = "game_types"
    LATITUDE = "latitude"
    LONGITUDE = "longitude"
    DISTANCE = "distance"
    PING = "ping"


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
    ping: float
