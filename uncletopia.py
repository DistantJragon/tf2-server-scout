import argparse

from options import read_options, write_options
from server_uncle import read_servers_from_file, update_cache_uncle
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
if __name__ == "__main__":
    args = parser.parse_args()
    options = read_options()
    if args.refresh_interval is None:
        args.refresh_interval = options["misc"]["refresh_interval"]
    server_list = []
    if options["misc"]["cache_uncletopia_state"]:
        server_list = read_servers_from_file()
        if not server_list:
            server_list = update_cache_uncle()
        if not server_list:
            print("Could not get server list from cache or API")
            exit(1)

    if args.auto_join:
        auto_join(args, server_list, options)

    elif args.quick_print:
        quick_print(args, server_list, options)

    # user_choice = None
    # user_quit = False
    # while not user_quit:
    #
    # max_distance = filters["distance"]["max"]
    # server_list, new_max_distance = get_uncle(
    #     args.ping_servers, max_distance is None)
    # filters["distance"]["max"] = new_max_distance
    #
    # Pretty print the response
    # if server_list is not None:
    #     for server in server_list:
    #         print(server)
    #         print()

    write_options(options)
