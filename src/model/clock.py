class Clock:
    __slots__ = "now"

    now: int

    def __init__(self) -> None:
        self.now = 0

    def tick(self) -> None:
        self.now += 1


clock = Clock()
