from typing import Any

from filters import apply_pre_filters
from models import DisplayLine, Options, Server
from options import (
    compile_display_options,
    display_lines_to_string,
    get_default_options,
    read_options,
    write_options,
)
from server_main import (
    format_last_played,
    get_uncle,
    update_cache_uncle,
    update_last_played,
    update_servers_with_steam_info,
)
from server_print import justify_strings, pretty_print_server
from ui_main import auto_join, quick_print


def sub_filter_to_string(options: Options, field: str, add_field: bool = True) -> str:
    filter = options["filters"][field]
    field_str = f"{field} filter - " if add_field else ""
    if "values" in filter:
        exclude_str = "Exclude: " if filter["exclude"] else "Only include:"
        values_str = " ; ".join([str(x) for x in filter["values"]])
        return f"{field_str}{exclude_str} {values_str}"
    elif "min" in filter:
        min_str = "-∞" if filter["min"] is None else str(filter["min"])
        max_str = "∞" if filter["max"] is None else str(filter["max"])
        return f"{field_str}{min_str} to {max_str}"
    else:
        return "Invalid filter"


def sub_filter_menu(args: Any, options: Options, field: str):
    if field not in options["filters"]:
        print("Invalid field")
        return
    filter = options["filters"][field]
    user_back = False
    while not user_back:
        # Check if the filter is a list filter or a range filter
        if "values" in filter:
            print(sub_filter_to_string(options, field))
            print("  1. Add value")
            print("  2. Remove value by index")
            print("  3. Remove value by name")
            print("  4. Toggle exclude")
            print("  5. Clear values")
            choice = input("Enter choice (b for back): ")
            if choice.lower() == "b" or choice.lower() == "back":
                user_back = True
                return
            elif choice == "1":
                new_value = input("Enter value to add: ")
                if field == "server_id":
                    try:
                        new_value = int(new_value)
                        filter["values"].append(new_value)
                    except ValueError:
                        print("Invalid server id")
                else:
                    filter["values"].append(new_value)
            elif choice == "2":
                index = input("Enter index to remove: ")
                if (
                    index.isdigit()
                    and int(index) < len(filter["values"]) + 1
                    and int(index) >= 1
                ):
                    filter["values"].pop(int(index) - 1)
                else:
                    print("Invalid index")
            elif choice == "3":
                value = input("Enter value to remove: ")
                if field == "server_id":
                    try:
                        value = int(value)
                        filter["values"] = [
                            x for x in filter["values"] if x != value]
                    except ValueError:
                        print("Invalid server id")
                else:
                    filter["values"] = [
                        x for x in filter["values"] if x != value]
            elif choice == "4":
                filter["exclude"] = not filter["exclude"]
            elif choice == "5":
                filter["values"] = []
            else:
                print("Invalid choice")
        elif "min" in filter:
            print(sub_filter_to_string(options, field))
            print("  1. Set min")
            print("  2. Set max")
            print("  3. Clear filter")
            choice = input("Enter choice (b for back): ")
            if choice.lower() == "b" or choice.lower() == "back":
                user_back = True
                return
            elif choice == "1":
                new_min = input("Enter new min (or leave empty for -∞): ")
                if len(new_min) == 0:
                    filter["min"] = None
                try:
                    filter["min"] = int(new_min)
                except ValueError:
                    print("Invalid min")
            elif choice == "2":
                new_max = input("Enter new max (or leave empty for ∞): ")
                if len(new_max) == 0:
                    filter["max"] = None
                try:
                    filter["max"] = int(new_max)
                except ValueError:
                    print("Invalid max")
            elif choice == "3":
                filter["min"] = None
                filter["max"] = None
            else:
                print("Invalid choice")


def filter_menu(args: Any, options: Options):
    filters = options["filters"]
    filter_choices = [x for x in filters.keys()]
    filter_max_length = max([len(x) for x in filter_choices])
    user_back = False
    while not user_back:
        print("Filters:")
        for i, field in enumerate(filter_choices):
            print(
                f"  {justify_strings(filter_max_length + 6, left=f'{i + 1}. {field}:')}"
                + f"{sub_filter_to_string(options, field, add_field=False)}"
            )
        choice = input("Enter choice (b for back): ")
        if choice.lower() == "b" or choice.lower() == "back":
            user_back = True
            return
        elif (
            choice.isdigit()
            and int(choice) - 1 < len(filter_choices)
            and int(choice) > 0
        ):
            field = filter_choices[int(choice) - 1]
            sub_filter_menu(args, options, field)


def new_display_line(display_line: DisplayLine | None = None) -> DisplayLine:
    if display_line is None:
        new_line: DisplayLine = {
            "left": "",
            "middle": "",
            "right": "",
            "empty": " ",
        }
    else:
        new_line = display_line.copy()
    possible_fillables: list[str] = [x for x in Server.__annotations__.keys()]
    possible_fillables.append("index")
    possible_fillables.append("name_utrim")
    possible_fillables.append("cc_emoji")
    user_back = False
    while not user_back:
        print("Edit line:")
        print(f"  1. Left: {new_line['left']}")
        print(f"  2. Middle: {new_line['middle']}")
        print(f"  3. Right: {new_line['right']}")
        print(f'  4. Empty: "{new_line["empty"]}"')
        choice = input("Enter choice (b for back, f for fill options): ")
        if choice.lower() == "b" or choice.lower() == "back":
            user_back = True
            return new_line
        elif choice.lower() == "f":
            print("Fill options:")
            for field in possible_fillables:
                print(f"  {field}")
        elif choice == "1":
            new_line["left"] = input("Enter new left: ")
        elif choice == "2":
            new_line["middle"] = input("Enter new middle: ")
        elif choice == "3":
            new_line["right"] = input("Enter new right: ")
        elif choice == "4":
            user_empty = input("Enter new empty: ")
            if len(user_empty) != 1:
                print("Empty must be a single character")
                continue
            new_line["empty"] = user_empty
        else:
            print("Invalid choice")
    return new_line


def display_sub_menu(options: Options, field: str):
    if field != "grid_display" and field != "join_display":
        raise ValueError("Invalid field")
    user_back = False
    display_options = options["display"][field]
    while not user_back:
        display_options_lines = display_lines_to_string(display_options)
        display_options_lines_split = display_options_lines.splitlines()
        print(f"Display options for {field}:")
        print(display_options_lines)
        print("  1. Add line")
        print("  2. Edit line")
        print("  3. Remove line")
        choice = input("Enter choice (b for back): ")
        if choice.lower() == "b" or choice.lower() == "back":
            user_back = True
            return
        elif choice == "1":
            for i, line in enumerate(display_options_lines_split[:-1]):
                print(f"  {i}. " + line)
            print("     " + display_options_lines_split[-1])
            line_number = input(
                "Enter line number to add after (empty for end, b for back): "
            )
            if line_number.lower() == "b" or line_number.lower() == "back":
                continue
            elif len(line_number) == 0:
                display_options.append(new_display_line())
            elif (
                line_number.isdigit()
                and int(line_number) >= 0
                and int(line_number) <= len(display_options)
            ):
                display_options.insert(int(line_number), new_display_line())
            else:
                print("Invalid line number")
                continue
        elif choice == "2":
            print("     " + display_options_lines_split[0])
            for i, line in enumerate(display_options_lines_split[1:-1], start=1):
                print(f"  {i + 1}. " + line)
            print("     " + display_options_lines_split[-1])
            line_number = input("Enter line number to edit (b for back): ")
            if line_number.lower() == "b" or line_number.lower() == "back":
                continue
            elif (
                line_number.isdigit()
                and int(line_number) > 0
                and int(line_number) <= len(display_options)
            ):
                line_number = int(line_number) - 1
                display_options[line_number] = new_display_line(
                    display_options[line_number]
                )
            else:
                print("Invalid line number")
                continue
        elif choice == "3":
            print("     " + display_options_lines_split[0])
            for i, line in enumerate(display_options_lines_split[1:-1], start=1):
                print(f"  {i}. " + line)
            print("     " + display_options_lines_split[-1])
            line_number = input("Enter line number to remove (b for back): ")
            if line_number.lower() == "b" or line_number.lower() == "back":
                continue
            elif (
                line_number.isdigit()
                and int(line_number) > 0
                and int(line_number) <= len(display_options)
            ):
                _ = display_options.pop(int(line_number) - 1)
            else:
                print("Invalid line number")
                continue
        else:
            print("Invalid choice")
            continue


def display_menu(args: Any, options: Options):
    display_options = options["display"]
    user_back = False
    while not user_back:
        print("Display options:")
        print("  1. Grid display")
        print(display_lines_to_string(display_options["grid_display"]))
        print("  2. Join display")
        print(display_lines_to_string(display_options["join_display"]))
        choice = input("Enter choice (b for back): ")
        if choice.lower() == "b" or choice.lower() == "back":
            user_back = True
            compile_display_options(options)
            return
        if choice == "1":
            display_sub_menu(options, "grid_display")
        elif choice == "2":
            display_sub_menu(options, "join_display")
        else:
            print("Invalid choice")


def sort_menu(args: Any, options: Options):
    sort_choices = [x for x in options["display"].keys()]
    user_back = False
    while not user_back:
        print("Sort by:")
        for i, field in enumerate(sort_choices):
            print(f"  {i + 1}. {field}")
        reversed_str = "(reversed)" if options["server_sort"]["reverse"] else ""
        print(
            f"Current sort: {options['server_sort']['sort_by']} {reversed_str}")
        choice = input(
            "Enter choice (b for back, r to toggle reverse sorting): ")
        if choice.lower() == "b" or choice.lower() == "back":
            user_back = True
            return
        elif choice.lower() == "r":
            options["server_sort"]["reverse"] = not options["server_sort"]["reverse"]
        elif (
            choice.isdigit() and int(choice) - 1 < len(sort_choices) and int(choice) > 0
        ):
            options["server_sort"]["sort_by"] = sort_choices[int(choice) - 1]
        else:
            print("Invalid choice")


def edit_misc_menu(args: Any, options: Options):
    misc_options = options["misc"]
    misc_choices = [x for x in misc_options.keys()]
    user_back = False
    while not user_back:
        print("Misc options:")
        for i, field in enumerate(misc_choices):
            value_str: str = str(misc_options[field])
            if field == "forced_width":
                value_str += " characters (0 for auto)"
            if field == "refresh_interval":
                value_str += " seconds"
            print(f"  {i + 1}. {field}: {value_str}")
        choice = input("Enter choice (b for back): ")
        if choice.lower() == "b" or choice.lower() == "back":
            user_back = True
            return
        elif (
            choice.isdigit() and int(choice) - 1 < len(misc_choices) and int(choice) > 0
        ):
            field = misc_choices[int(choice) - 1]
            if isinstance(misc_options[field], bool):
                misc_options[field] = not misc_options[field]
            elif isinstance(misc_options[field], str):
                new_value = input(f"Enter new value for {field}: ")
                misc_options[field] = new_value
            else:
                new_value = input(f"Enter new value for {field}: ")
                try:
                    if "." in new_value:
                        misc_options[field] = float(new_value)
                    else:
                        misc_options[field] = int(new_value)
                except ValueError:
                    print("Invalid value")
        else:
            print("Invalid choice")


def edit_option_menu(args: Any, options: Options):
    user_back = False
    while not user_back:
        print("Edit options:")
        print("  1. Filters")
        print("  2. Sort")
        print("  3. Display")
        print("  4. Misc")
        print("  5. Reload options from file")
        print("  6. Save options to file")
        print("  7. Reset options to default")
        choice = input("Enter choice (b for back): ")
        if choice.lower() == "b" or choice.lower() == "back":
            user_back = True
            return
        elif choice == "1":
            filter_menu(args, options)
        elif choice == "2":
            sort_menu(args, options)
        elif choice == "3":
            display_menu(args, options)
        elif choice == "4":
            edit_misc_menu(args, options)
        elif choice == "5":
            pass
        elif choice == "6":
            pass
        elif choice == "7":
            pass
        else:
            print("Invalid choice")


def main_menu(args: Any, servers: list[Server], options: Options):
    user_exit = False
    last_server_joined: Server | None = None
    last_server_joined_played: float | None = None
    pre_filtered_servers = apply_pre_filters(servers, options["filters"])
    while not user_exit:
        print("Main menu:")
        print("  1. Auto join")
        print("  2. Quick print")
        print("  3. Edit options")
        print("  4. Undo Join (reset last played)")
        print("  5. Update using Steam info")
        print("  6. Update using Uncletopia API")
        choice = input("Enter choice (q to quit): ")
        if len(choice) == 0 or len(choice) > 1:
            print("Invalid choice")
            continue
        if choice == "1":
            # Auto join
            if (
                last_server_joined is not None
                and options["misc"]["update_last_played_on_join_new_server"]
            ):
                update_last_played(last_server_joined)
                print("Last played server: ")
                pretty_print_server(last_server_joined, options)
                print()
            last_server_joined = auto_join(args, pre_filtered_servers, options)
            if last_server_joined is not None and not args.disable_join:
                last_server_joined_played = last_server_joined["last_played"]
                update_last_played(last_server_joined)
        elif choice == "2":
            # Quick print
            quick_print(args, pre_filtered_servers, options)
        elif choice == "3":
            # Edit options
            edit_option_menu(args, options)
            pre_filtered_servers = apply_pre_filters(
                servers, options["filters"])
        elif choice == "4":
            # Undo join
            if last_server_joined is None:
                print("No server joined yet")
            elif last_server_joined_played is None:
                print("You have already undone the last join")
            else:
                last_server_joined["last_played"] = last_server_joined_played
                last_server_joined_played = None
                print(
                    f'The server that was "joined" has been reset to {format_last_played(last_server_joined)}'
                )
        elif choice == "5":
            # Update using Steam info
            update_servers_with_steam_info(
                pre_filtered_servers, options["misc"]["steam_username"]
            )
        elif choice == "6":
            # Update using Uncletopia API
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
        elif choice == "F":
            filter_menu(args, options)
            pre_filtered_servers = apply_pre_filters(
                servers, options["filters"])
        elif choice == "S":
            sort_menu(args, options)
        elif choice == "D":
            display_menu(args, options)
        elif choice.lower() == "q" or choice.lower() == "quit":
            user_exit = True
            break
        else:
            print("Invalid choice")
