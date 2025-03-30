import math
import shutil

from object_grid.grid_element import GridElement


class GridLayout:
    def __init__(self):
        self.elements: list[GridElement] = []
        self.column_widths: list[int] = []
        self.grid_width: int = -1
        self.grid_width_characters: int = -1
        self.forced_character_limit: int = -1
        self.forced_grid_width_limit: int = -1

    def new_element(self) -> GridElement:
        element = GridElement()
        self.elements.append(element)
        return element

    def calculate_dimensions_fast(self):
        if len(self.elements) == 0:
            return
        # Calculate the maximum grid width
        line_width: int = self.forced_character_limit
        if line_width < 0:
            line_width = shutil.get_terminal_size(fallback=(-1, -1)).columns
        # Find the largest element
        max_width = 0
        for element in self.elements:
            max_width = max(max_width, element.min_width)
        # Add one to the max width to account for the padding
        max_width_plus_separator = max_width + 1
        # Calculate the grid width
        min_grid_width = math.floor(
            (line_width - 1) / max_width_plus_separator)
        if self.forced_grid_width_limit > 0:
            self.grid_width = min(
                self.forced_grid_width_limit, min_grid_width, len(
                    self.elements)
            )
        else:
            self.grid_width = min(min_grid_width, len(self.elements))
        self.grid_width_characters = 1 + self.grid_width * max_width_plus_separator
        self.column_widths = [max_width] * self.grid_width

    def calculate_dimensions(self):
        if len(self.elements) == 0:
            return
        # Calculate the maximum grid width
        line_width: int = self.forced_character_limit
        if line_width < 0:
            line_width = shutil.get_terminal_size(fallback=(-1, -1)).columns
        # Find the smallest element
        min_width = self.elements[0].min_width
        for element in self.elements:
            min_width = min(min_width, element.min_width)
        # Add one to the min width to account for the padding
        min_width += 1
        maximum_grid_width = math.floor((line_width - 1) / min_width)
        if maximum_grid_width == 0:
            raise ValueError("No elements fit in the grid")
        # Calculate the grid width (and save column widths)
        elements_fit = False
        if self.forced_grid_width_limit > 0:
            current_grid_width = min(
                maximum_grid_width, len(
                    self.elements), self.forced_grid_width_limit
            )
        else:
            current_grid_width = min(maximum_grid_width, len(self.elements))
        current_grid_width_characters = 1
        while not elements_fit and current_grid_width > 0:
            # Assume elements can fit in the grid of maximum width
            # If not, try to fit them in the grid of maximum width - 1
            elements_fit = True
            current_grid_width_characters = 1 + current_grid_width
            column = 0
            self.column_widths = [0] * current_grid_width
            for element in self.elements:
                current_grid_width_characters -= self.column_widths[column]
                self.column_widths[column] = max(
                    self.column_widths[column], element.min_width
                )
                current_grid_width_characters += self.column_widths[column]
                if current_grid_width_characters > line_width:
                    elements_fit = False
                    current_grid_width -= 1
                    break
                column += 1
                if column == current_grid_width:
                    column = 0
        if elements_fit and current_grid_width > 0:
            self.grid_width = current_grid_width
            self.grid_width_characters = current_grid_width_characters
            # if self.grid_width_characters > line_width:
            #     raise ValueError("Grid width is too large")
        else:
            raise ValueError("No width fits all the elements")

    def compile_grid(self, fast_mode: bool = False) -> str:
        if fast_mode:
            self.calculate_dimensions_fast()
        else:
            self.calculate_dimensions()
        if self.grid_width == -1:
            raise ValueError("Grid dimensions not calculated correctly")
        row_line_height = len(self.elements[0].lines)
        row_separator: str = "-" * self.grid_width_characters
        result: str = row_separator + "\n"
        grid_height = math.ceil(len(self.elements) / self.grid_width)
        for row in range(grid_height):
            line_length = 0
            for lineIndex in range(row_line_height):
                result += "|"
                line_length = 1
                for rowIndex in range(self.grid_width):
                    elementIndex = row * self.grid_width + rowIndex
                    if elementIndex >= len(self.elements):
                        break
                    element = self.elements[row * self.grid_width + rowIndex]
                    line = element.lines[lineIndex]
                    column_width = self.column_widths[rowIndex]
                    result += line.compile_line(column_width)
                    result += "|"
                    line_length += column_width + 1
                result += "\n"
            result += row_separator[:line_length] + "\n"
        return result
