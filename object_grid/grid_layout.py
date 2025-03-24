import shutil

from object_grid.grid_element import GridElement
from object_grid.grid_line import GridLine


class GridLayout:
    def __init__(self):
        self.elements: list[GridElement] = []
        self.column_widths: list[int] = []
        self.preserve_order: bool = True
        self.forced_character_limit: int = -1
        self.forced_element_limit: int = -1
        self.force_element_height: bool = False

    def new_element(self) -> GridElement:
        element = GridElement()
        self.elements.append(element)
        return element

    def check_heights(self) -> bool:
        if len(self.elements) == 0:
            return True
        line_count = len(self.elements[0].lines)
        for element in self.elements:
            if len(element.lines) != line_count:
                return False
        return True

    def max_height(self) -> int:
        max_height = 0
        for element in self.elements:
            max_height = max(max_height, len(element.lines))
        return max_height

    def fix_heights(self):
        max_height = self.max_height()
        for element in self.elements:
            for _ in range(max_height - len(element.lines)):
                element.add_line()

    def compile_grid(self) -> str:
        if not self.check_heights() and self.force_element_height:
            raise ValueError("Element heights do not match")
        line_width: int = self.forced_character_limit
        if line_width < 0:
            line_width = shutil.get_terminal_size(fallback=(-1, -1)).columns
        result = ""
        for element in self.elements:
            for line in element.lines:
                result += line.compile_line(width) + "\n"
        return result
