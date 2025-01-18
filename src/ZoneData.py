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
