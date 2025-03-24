from object_grid.grid_line import GridLine


class GridElement:
    def __init__(self):
        self.lines: list[GridLine] = []
        self.min_width: int = 0

    def add_line(
        self, left: str = "", middle: str = "", right: str = "", empty: str = " "
    ):
        line = GridLine(left, middle, right, empty)
        self.lines.append(line)
        self.min_width = max(self.min_width, line.min_width)
