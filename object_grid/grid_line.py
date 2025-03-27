class GridLine:
    def __init__(
        self, left: str = "", middle: str = "", right: str = "", empty: str = " "
    ):
        if len(empty) != 1:
            raise ValueError("Empty string must be of length 1")
        self.left: str = left
        self.middle: str = middle
        self.right: str = right
        self.empty: str = empty
        self.min_width: int = len(left) + len(middle) + len(right) - 1
        if left:
            self.min_width += 1
        if middle:
            self.min_width += 1
        if right:
            self.min_width += 1

    def compile_line(self, width: int) -> str:
        if width < self.min_width:
            raise ValueError("Width is too small")
        if width == self.min_width:
            line = self.left
            if self.middle:
                if line:
                    line += self.empty
                line += self.middle
            if self.right:
                if line:
                    line += self.empty
                line += self.right
            return line
        spaces = width - len(self.middle)
        left_spaces = spaces // 2
        if spaces % 2 == 0:
            right_spaces = left_spaces - len(self.right)
        else:
            right_spaces = left_spaces + 1 - len(self.right)
        left_spaces -= len(self.left)
        if left_spaces < 1:
            right_spaces += left_spaces - 1
            left_spaces = 1
        elif right_spaces < 1:
            left_spaces += right_spaces - 1
            right_spaces = 1
        return (
            self.left
            + self.empty * left_spaces
            + self.middle
            + self.empty * right_spaces
            + self.right
        )
