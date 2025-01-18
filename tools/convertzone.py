import json
import pyjson5
import sys

from pprint import pprint
from lib.zone import load_zones, ZoneData

def custom_dump_default(obj):
    if not isinstance(obj, ZoneData):
        raise TypeError(f"Not ZoneData")
    
    return {
        "bot": obj.bot,
        "cmd": obj.cmd,
        "lifespan": obj.lifespan,
        "name": obj.name,
        "number": obj.number,
        "reset_mode": obj.reset_mode,
        "top": obj.top
    }

def main():
    try:
        print("CircleMUD Zone to JSON Converter")
        if (len(sys.argv) != 2):
            print("Useage: python convertzone.py <zonefile>")
            sys.exit()
        zonefile = sys.argv[1]
        zonejson = sys.argv[1] + ".json5"
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
                "cmd": []
            }
            for cmd in zone_info.cmd:
                command = {}
                command["command"] = cmd.command
                command["if_flag"] = cmd.if_flag
                command["max_existing"] = cmd.arg2
                match cmd.command:
                    case "M": # Mob
                        command["mob"] = cmd.arg1
                        command["room"] = cmd.arg3
                    case "O": #Object
                        command["obj"] = cmd.arg1
                        command["room"] = cmd.arg3
                    case "G": # Give Obj to last loaded Mob
                        command["obj"] = cmd.arg1
                    case "E": # Equip Mob
                        command["obj"] = cmd.arg1
                        command["eq_pos"] = cmd.arg3
                    case "P": # Put Obj in Container
                        command["obj"] = cmd.arg1
                        command["container"] = cmd.arg3
                    case "D": # Door state
                        command.pop("max_existing")
                        command["room"] = cmd.arg1
                        command["exit"] = cmd.arg2
                        command["state"] = cmd.arg3
                    case "R": # Remove Object from Room
                        command.pop("max_existing")
                        command["room"] = cmd.arg1
                        command["obj"] = cmd.arg2
                    case _:
                        print(f"Unknown command: {cmd.command}")
                new_zone["cmd"].append(command)
            print(f"Data serializable: {pyjson5.encode_noop(new_zone)}")
            f.write(json.dumps(new_zone, indent=4))
            print("JSON Written")

        with open(zonejson, 'r') as f:
            json.load(f)
            print(*"JSON Validated")

    except KeyboardInterrupt:
        print("\r\nShutting down.")
        sys.exit()
    except pyjson5.Json5EncoderException as e:
        print(f"\r\nJsson5 Exception: {e}")
        sys.exit()
    except TypeError as e:
        print(f"\r\nType error: {e}")
        sys.exit()
    except Exception as e:
        print(f"\r\nException: {e}")
        sys.exit()

if __name__ == "__main__":
    main()
