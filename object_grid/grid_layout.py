import math
import shutil

from object_grid.grid_element import GridElement


class GridLayout:
    def __init__(self):
        self.elements: list[GridElement] = []
        self.grid_matrix: list[list[GridElement]] = []
        self.column_widths: list[int] = []
        self.grid_width: int = -1
        self.grid_height: int = -1
        self.grid_width_characters: int = -1
        self.forced_character_limit: int = -1
        self.forced_grid_width_limit: int = -1
        self.fast_mode: bool = False

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
        # Calculate the grid width
        if self.forced_grid_width_limit > 0:
            self.grid_width = min(
                self.forced_grid_width_limit, math.floor(
                    line_width / max_width)
            )
        else:
            self.grid_width = math.floor(line_width / max_width)
        self.grid_height = math.ceil(len(self.elements) / self.grid_width)
        self.grid_width_characters = 1 + self.grid_width * (max_width + 1)
        self.column_widths = [max_width] * self.grid_width
        self.grid_matrix = [[] for _ in range(self.grid_height)]
        for i in range(len(self.elements)):
            element = self.elements[i]
            self.grid_matrix[i // self.grid_width].append(element)

    def calculate_dimensions(self):
        if len(self.elements) == 0:
            return
        # Calculate the maximum grid width
        line_width: int = self.forced_character_limit
        if line_width < 0:
            line_width = shutil.get_terminal_size(fallback=(-1, -1)).columns
        # Sort by min_width ascending
        elements_sorted = sorted(
            self.elements, key=lambda element: element.min_width)
        # Check if any element is too wide (add 2 for padding)
        if elements_sorted[-1].min_width + 2 > line_width:
            raise ValueError("Some elements are too wide")
        maximum_grid_width = 0
        character_count = 1
        for element in elements_sorted:
            if character_count + element.min_width + 1 > line_width:
                break
            character_count += element.min_width + 1
            maximum_grid_width += 1
            if maximum_grid_width == self.forced_grid_width_limit:
                break
        if maximum_grid_width == 0:
            raise ValueError("No elements fit in the grid")
        # Calculate the grid width (and save column widths)
        elements_fit = False
        current_grid_width = maximum_grid_width
        current_grid_height = math.ceil(
            len(self.elements) / current_grid_width)
        while not elements_fit:
            # Assume elements can fit in the grid of maximum width
            # If not, try to fit them in the grid of maximum width - 1
            elements_fit = True
            self.column_widths = [0] * current_grid_width
            self.grid_matrix = [[] for _ in range(current_grid_height)]
            row_character_count = 0
            current_row = -1
            for i in range(len(self.elements)):
                column = i % current_grid_width
                if column == 0:
                    row_character_count = 0
                    current_row += 1
                element = self.elements[i]
                row_character_count += element.min_width
                if row_character_count > line_width:
                    elements_fit = False
                    current_grid_width -= 1
                    current_grid_height = math.ceil(
                        len(self.elements) / current_grid_width
                    )
                    break
                self.column_widths[column] = max(
                    self.column_widths[column], element.min_width
                )
                self.grid_matrix[current_row].append(element)
        if elements_fit:
            self.grid_width = current_grid_width
            self.grid_height = current_grid_height
            self.grid_width_characters = 1
            for width in self.column_widths:
                self.grid_width_characters += width + 1

    def compile_grid(self) -> str:
        if self.fast_mode:
            self.calculate_dimensions_fast()
        else:
            self.calculate_dimensions()
        if self.grid_width == -1:
            raise ValueError("Grid dimensions not calculated correctly")
        row_line_height = len(self.elements[0].lines)
        row_separator = "-" * self.grid_width_characters
        result = row_separator + "\n"
        for i in range(self.grid_height):
            row = self.grid_matrix[i]
            for j in range(row_line_height):
                result += "|"
                for k in range(len(row)):
                    element = row[k]
                    line = element.lines[j]
                    result += line.compile_line(self.column_widths[k])
                    result += "|"
                result += "\n"
            result += row_separator + "\n"
        return result
