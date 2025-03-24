import argparse

from options import read_options, write_options
from server_uncle import (
    check_cache_dirty,
    clean_write_servers_to_file,
    read_servers_from_file,
    update_cache_uncle,
)
from ui_menus import main_menu
from ui_uncle import auto_join, quick_print

# Parse arguments
parser = argparse.ArgumentParser(
    prog="uncletopia",
    description="Get server info and connection options from Uncletopia API\n"
    + "Usage: uncletopia.py [-aqP] [-R REFRESH_INTERVAL]",
)

_ = parser.add_argument(
    "-a",
    "--auto-join",
    help="Automatically search for and join a server based on saved filters",
    action="store_true",
)

_ = parser.add_argument(
    "-q",
    "--quick-print",
    help="Print all servers that fit the filters and exit",
    action="store_true",
)

_ = parser.add_argument(
    "-P",
    "--ping-servers",
    help="Ping servers to get latency",
    action="store_true",
)
_ = parser.add_argument(
    "-R",
    "--refresh-interval",
    help="Refresh interval for the server list",
    type=int,
)

_ = parser.add_argument(
    "-J",
    "--disable-join",
    help="Prevents the program from joining servers",
    action="store_true",
)

if __name__ == "__main__":
    args = parser.parse_args()
    options = read_options()
    server_list = []
    if options["misc"]["cache_uncletopia_state"]:
        server_list = read_servers_from_file()
        if not server_list:
            print("No servers found in cache, updating cache")
            server_list, new_max_distance = update_cache_uncle(
                options["misc"]["auto_distance_calculation"]
            )
            if new_max_distance is not None:
                options["filters"]["distance"]["max"] = new_max_distance
        if not server_list:
            print("Could not get server list from cache or API")
            exit(1)

    if args.auto_join:
        auto_join(args, server_list, options)

    elif args.quick_print:
        quick_print(args, server_list, options)

    else:
        main_menu(args, server_list, options)

    write_options(options)
    # Used to only write to file if the cache was dirty
    # Now, always write to file to keep each server's last_played time up to date
    if options["misc"]["cache_uncletopia_state"]:
        clean_write_servers_to_file(server_list)
