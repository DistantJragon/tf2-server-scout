from typing import Any

from models import Options, Server
from server_uncle import get_uncle, update_cache_uncle, update_servers_with_steam_info
from ui_uncle import auto_join, quick_print


def main_menu(args: Any, servers: list[Server], options: Options):
    user_exit = False
    while not user_exit:
        print("1. Auto join")
        print("2. Quick print")
        print("3. Edit options")
        print("4. Update using Steam info")
        print("5. Update using Uncletopia API")
        choice = input("Enter choice (q to quit): ")
        if choice == "1":
            auto_join(args, servers, options)
        elif choice == "2":
            quick_print(args, servers, options)
        elif choice == "3":
            pass
        elif choice == "4":
            update_servers_with_steam_info(servers)
        elif choice == "5":
            new_max_distance = None
            if options["misc"]["cache_uncletopia_state"]:
                servers, new_max_distance = update_cache_uncle(
                    options["misc"]["auto_distance_calculation"]
                )
            else:
                servers, new_max_distance = get_uncle(
                    False, options["misc"]["auto_distance_calculation"]
                )
            if new_max_distance is not None:
                options["filters"]["distance"]["max"] = new_max_distance
        elif choice == "q":
            user_exit = True
        else:
            print("Invalid choice")
