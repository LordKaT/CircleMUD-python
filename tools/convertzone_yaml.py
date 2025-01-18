import json
import pyjson5
import sys
import yaml

from pprint import pprint
from lib.zone import load_zones, ZoneData

def remove_none_values(d):
    if not isinstance(d, dict):
        return d

    cleaned_dict = {}
    for key, value in d.items():
        if value is None:
            continue
        elif isinstance(value, dict):
            cleaned_value = remove_none_values(value)
            cleaned_dict[key] = cleaned_value
        elif isinstance(value, list):
            cleaned_list = [remove_none_values(item) if isinstance(item, dict) else item for item in value]
            cleaned_dict[key] = cleaned_list
        else:
            cleaned_dict[key] = value

    return cleaned_dict

def main():
    try:
        print("CircleMUD Zone to JSON Converter")
        if (len(sys.argv) != 2):
            print("Useage: python convertzone.py <zonefile>")
            sys.exit()
        zonefile = sys.argv[1]
        zonejson = sys.argv[1] + ".yaml"
        zone_info = None
        with open(zonefile, 'r') as f:
            zone_info = load_zones(f, zonefile)
        if zone_info is None:
            raise Exception("Bad zone data")

        with open(zonejson, 'w') as f:
            new_zone = {
                "number": zone_info.number,
                "name": zone_info.name,
                "bot": zone_info.bot,
                "top": zone_info.top,
                "lifespan": zone_info.lifespan,
                "reset_mode": zone_info.reset_mode,
                "script": None,
                "cmd": []
            }
            for cmd in zone_info.cmd:
                command = {
                    "command": cmd.command,
                    "if_flag": cmd.if_flag,
                    "max_existing": cmd.arg2,
                    "mob": None,
                    "obj": None,
                    "room": None,
                    "eq_pos": None,
                    "container": None,
                    "exit": None,
                    "state": None,
                }
                match cmd.command:
                    case "M": # Mob
                        command["command"] = "spawn_mob"
                        command["mob"] = cmd.arg1
                        command["room"] = cmd.arg3
                    case "O": #Object
                        command["command"] = "spawn_object"
                        command["obj"] = cmd.arg1
                        command["room"] = cmd.arg3
                    case "G": # Give Obj to last loaded Mob
                        command["command"] = "give_object"
                        command["obj"] = cmd.arg1
                    case "E": # Equip Mob
                        command["command"] = "equip_mob"
                        command["obj"] = cmd.arg1
                        command["eq_pos"] = cmd.arg3
                    case "P": # Put Obj in Container
                        command["command"] = "put_object"
                        command["obj"] = cmd.arg1
                        command["container"] = cmd.arg3
                    case "D": # Door state
                        command.pop("max_existing")
                        command["command"] = "door_state"
                        command["room"] = cmd.arg1
                        command["exit"] = cmd.arg2
                        command["state"] = cmd.arg3
                    case "R": # Remove Object from Room
                        command.pop("max_existing")
                        command["command"] = "remove_object"
                        command["room"] = cmd.arg1
                        command["obj"] = cmd.arg2
                    case "S": # Stop parsing
                        break
                    case _:
                        print(f"Unknown command: {cmd.command}")
                command = remove_none_values(command)
                new_zone["cmd"].append(command)
            yaml.dump(new_zone, f, sort_keys=False)
            print("YAML Dumped")
        with open(zonejson, 'r') as f:
            yaml.safe_load(f)
            print("YAML Validated")

    except KeyboardInterrupt:
        print("\r\nShutting down.")
        sys.exit()
    #except pyjson5.Json5EncoderException as e:
    #    print(f"\r\nJsson5 Exception: {e}")
    #    sys.exit()
    except yaml.YAMLError as e:
        print(f"\r\nYAML Exception: {e}")
        sys.exit()
    except TypeError as e:
        print(f"\r\nType error: {e}")
        sys.exit()
    except Exception as e:
        print(f"\r\nException: {e}")
        sys.exit()

if __name__ == "__main__":
    main()
