from tkinter import Canvas
from common import *

primary_color = "white"
secondary_color = "black"


def draw_bridge_2d(on_canvas: Canvas, at_position: float) -> None:
    scale = 0.9
    thickness = 5
    abutment_size = 0.7
    altitude_domain = 0.7

    width = on_canvas.winfo_width()
    height = on_canvas.winfo_height()

    for direction in [1, -1]:
        x = int(direction * scale * width * abutment_size / 2) + width / 2.0
        y1 = int((1.0 - scale) * height)
        y2 = int(scale * height)
        on_canvas.create_line(x, y1, x, y2, width=thickness, fill=secondary_color)

    y = height / 2.0
    y += (height * 0.5 * altitude_domain) * (1.0 - (2.0 * at_position))
    y = int(y)
    x1 = int((1.0 - scale) * width)
    x2 = int(scale * width)

    on_canvas.create_line(x1, y, x2, y, width=thickness, fill=secondary_color)


class BridgeDisplay(Canvas):
    def __init__(self, initial_position: float = 0.0,):
        super().__init__(bg=theme["primary_color"], selectforeground=theme["secondary_color"],
                         highlightcolor=theme["tertiary_color"])
        self.set_position(initial_position)

    def set_position(self, to: float):
        to = min(0.0, max(1.0, to))
        self.delete("all")

        draw_bridge_2d(self, to)
