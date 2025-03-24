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
        self.min_width: int = len(left) + len(middle) + len(right)

    def compile_line(self, width: int) -> str:
        if width < self.min_width:
            raise ValueError("Width is too small")
        spaces = width - self.min_width
        if spaces % 2 == 0:
            left_spaces = spaces // 2
            right_spaces = left_spaces
        else:
            left_spaces = spaces // 2
            right_spaces = left_spaces + 1
        return (
            self.left
            + self.empty * left_spaces
            + self.middle
            + self.empty * right_spaces
            + self.right
        )
