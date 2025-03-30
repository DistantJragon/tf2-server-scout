from models import DisplayLineCompiled, Options, Server
from object_grid.grid_layout import GridLayout
from object_grid.grid_line import GridLine
from server_main import (
    format_last_played,
    format_since_played,
    get_country_emoji,
    refresh_since_played,
)


def justify_strings(
    width: int, left: str = "", middle: str = "", right: str = "", empty: str = " "
):
    """
    Print a string justified to the left, middle, and right.
    """
    line = GridLine(left=left, middle=middle, right=right, empty=empty)
    return line.compile_line(width)


def create_element_by_server(
    server: Server,
    grid: GridLayout,
    displayLines: list[DisplayLineCompiled],
    index: int = -1,
):
    grid_element = grid.new_element()
    refresh_since_played(server)
    server_dict: dict[str, str] = {
        key: str(server[key]) for key in server.keys()}
    server_dict["last_played"] = format_last_played(server)
    server_dict["since_played"] = format_since_played(server)
    server_dict["cc_emoji"] = get_country_emoji(server["cc"])
    server_dict["ping"] = f"{server['ping']:.0f}"
    utrim = "Uncletopia | "
    server_dict["name_utrim"] = server["name"]
    if server["name"].startswith(utrim):
        server_dict["name_utrim"] = server_dict["name_utrim"][len(utrim):]
    if index > 0:
        server_dict["index"] = str(index)
    for line in displayLines:
        grid_element.add_line(
            line["left"](server_dict),
            line["middle"](server_dict),
            line["right"](server_dict),
            line["empty"],
        )


def print_server_grid(servers: list[Server], options: Options):
    """
    Print the servers in a grid layout.
    """
    grid = GridLayout()
    grid_display = options["display"]["grid_display_compiled"]
    if grid_display is None:
        raise ValueError("Grid display is not compiled")
    misc = options["misc"]
    fast_mode: bool = misc["fast_grid_calculation"]
    for i, server in enumerate(servers, start=1):
        create_element_by_server(server, grid, grid_display, i)

    print(grid.compile_grid(fast_mode))


def pretty_print_server(server: Server, options: Options):
    """
    Pretty print a server for the user.
    Printing depends on the terminal width.
    """
    join_display = options["display"]["join_display_compiled"]
    if join_display is None:
        raise ValueError("Grid display is not compiled")
    grid = GridLayout()
    create_element_by_server(server, grid, join_display)

    print(grid.compile_grid())
