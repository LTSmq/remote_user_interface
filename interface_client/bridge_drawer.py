from tkinter import *

primary_color = "white"
secondary_color = "black"


def draw_bridge(on_canvas: Canvas, at_position: float) -> None:
    on_canvas.delete("all")

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
