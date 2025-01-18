class ZoneData:
    def __init__(self, number: int = 0, name: str = "", bottom: int = 0,
                 top: int = 0, lifespan: int = 0, reset_mode: int = 0,
                 commands: list = []) -> None:
        self.number = number
        self.name = name
        self.bottom = bottom
        self.top = top
        self.lifespan = lifespan
        self.reset_mode = reset_mode
        self.commands = commands
    

def load(zone_data: ZoneData = ZoneData()) -> ZoneData:
    # spawn_mob("Puff", 1)
    return zone_data

def zone_event(zone_data:  ZoneData = ZoneData(), event: str = "") -> ZoneData:
    match event:
        case "load":
            zone_data = load(zone_data)
        case "reload":
            zone_data = load(zone_data)
        case _:
            pass
    return zone_data
