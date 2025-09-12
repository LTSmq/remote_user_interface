# bridge_display.py
from tkinter import Canvas, Misc
from math import sqrt, sin, cos, floor, pi

from common import *

REFRESH_TIME = 0.01  # Seconds
BRIDGE_SPEED = 0.6


def move_toward(source: float, destination: float, delta: float) -> float:
    if abs(destination - source) <= delta:
        return destination
    return source + delta if destination > source else source - delta


def isometric_coordinate(x: float, y: float, z: float) -> tuple[float, float]:
    x_projection = sqrt(3.0) / 2.0
    y_projection = 0.5
    return (
        x_projection * (x - z),
        y + (y_projection * (x + z)),
    )


def get_box_vertices(p1: tuple[float, float, float], p2: tuple[float, float, float]):
    x1, y1, z1 = p1
    x2, y2, z2 = p2

    # Determine min and max for each coordinate axis
    xmin, xmax = sorted([x1, x2])
    ymin, ymax = sorted([y1, y2])
    zmin, zmax = sorted([z1, z2])

    corners_of_a_box = 8
    vertices = []
    for i in range(corners_of_a_box):
        x = xmin if i % 2 == 0 else xmax
        y = ymin if floor(i / 2.0) == 0 else ymax
        z = zmin if floor(i / 4.0) == 0 else zmax
        vertices.append((x, y, z))

    return vertices


def draw_box(on_canvas: Canvas, origin: tuple[float, float], size: tuple[float, float, float], angle_degrees: float = 30,
             **polygon_kwargs):
    leftward, upward, rightward = size
    radian_converter = pi / 180.0
    theta = angle_degrees * radian_converter

    leftward_vertical = leftward * sin(theta)
    leftward_horizontal = leftward * cos(theta)

    rightward_vertical = rightward * sin(theta)
    rightward_horizontal = rightward * cos(theta)

    # vertical direction correction
    rightward_vertical *= -1
    leftward_vertical *= -1
    upward *= -1

    origin_x, origin_y = origin

    faces = {
        "left": [
            (origin_x, origin_y),
            (origin_x, origin_y + upward),
            (origin_x + leftward_horizontal, origin_y + upward - leftward_vertical),
            (origin_x + leftward_horizontal, origin_y - leftward_vertical),
        ],

        "right": [
            (origin_x + leftward_horizontal, origin_y - leftward_vertical),
            (origin_x + leftward_horizontal, origin_y + upward - leftward_vertical),
            (origin_x + leftward_horizontal + rightward_horizontal, origin_y - leftward_vertical + rightward_vertical + upward),
            (origin_x + leftward_horizontal + rightward_horizontal, origin_y - leftward_vertical + rightward_vertical),
        ],

        "top": [
            (origin_x, origin_y + upward),
            (origin_x + rightward_horizontal, origin_y + upward + rightward_vertical),
            (origin_x + leftward_horizontal + rightward_horizontal, origin_y + upward - leftward_vertical + rightward_vertical),
            (origin_x + leftward_horizontal, origin_y + upward - leftward_vertical)
        ],
    }

    for coordinates in faces.values():
        on_canvas.create_polygon(coordinates, **polygon_kwargs)


def draw_bridge_2d(on_canvas: Canvas, at_position: float) -> None:
    scale = 0.9
    thickness = 10
    abutment_size = 0.7
    altitude_domain = 0.7

    width = 960 #on_canvas.winfo_width()
    height = 512 # on_canvas.winfo_height()

    for direction in [1, -1]:
        x = int(direction * scale * width * abutment_size / 2) + width / 2.0
        y1 = int((1.0 - scale) * height)
        y2 = int(scale * height)
        on_canvas.create_line(x, y1, x, y2, width=thickness, fill=theme["secondary_color"])

    y = height / 2.0
    y += (height * 0.5 * altitude_domain) * (1.0 - (2.0 * at_position))
    y = int(y)
    x1 = int((1.0 - scale) * width)
    x2 = int(scale * width)

    on_canvas.create_line(x1, y, x2, y, width=thickness, fill=theme["secondary_color"])


def draw_bridge_3d(on_canvas: Canvas, at_position: float):
    angle = 30
    theta = angle * pi / 180.0
    length = 300
    mast = 150
    length_vector = (length * cos(theta), length * sin(theta))
    origin = (175, 250)
    abutment_size = (50, 200, 50)
    second_origin = tuple([a + b for a, b in zip(origin, length_vector)])
    bridge_origin = (origin[0] + (sin(theta) * (abutment_size[0] + abutment_size[2])),(origin[1] - (sin(theta) * abutment_size[0]))  + (30 - (mast * at_position)))
    boxes = {
        "left_abutment": {
            "origin": origin,
            "size": abutment_size,
            "angle_degrees": angle,
        },
        "bridge": {
            "origin": bridge_origin,
            "size": (length, 30, 40),
            "angle_degrees": angle,
        },
        "right_abutment": {
            "origin": second_origin,
            "size": abutment_size,
            "angle_degrees": angle,
        },
    }
    for box in boxes.values():
        draw_box(on_canvas, **box, outline=theme["secondary_color"], fill=theme["primary_color"], width=3)

class BridgeDisplay(Canvas):
    def __init__(self, master: Misc, initial_position: float = 0.0,):
        super().__init__(master, bg=theme["primary_color"], selectforeground=theme["secondary_color"],
                         highlightcolor=theme["tertiary_color"], highlightbackground=theme["tertiary_color"])
        self.current_position = initial_position
        self.target_position = initial_position
        self._refresh()

    def set_position(self, to: float):
        to = max(0.0, min(1.0, to))
        self.delete("all")
        draw_bridge_3d(self, to)

    def _refresh(self):
        travel = BRIDGE_SPEED * REFRESH_TIME
        if self.current_position != self.target_position:
            self.current_position = move_toward(self.current_position, self.target_position, travel)
            self.set_position(self.current_position)

        self.after(int(REFRESH_TIME * 1000), self._refresh)
