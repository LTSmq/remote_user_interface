# common.py
from datetime import datetime
from tkinter import Misc
from tkinter.ttk import *

WINDOW_SIZE = 1280, 960
THEME_NAME = "hacker"


themes = {
    "hacker": {
        "primary_color": "black",
        "secondary_color": "lime",
        "tertiary_color": "lime",

        "standard_typeface": "Courier New",
        "standard_font_size": 12,
        "title_font_size": 16,

        "standard_margin": 10,
    },
    "powershell": {
        "primary_color": "#012345",
        "secondary_color": "white",
        "tertiary_color": "yellow",

        "standard_typeface": "Consolas",
        "standard_font_size": 11,
        "title_font_size": 14,

        "standard_margin": 5,
    },
    "nihon": {
        "primary_color": "white",
        "secondary_color": "black",
        "tertiary_color": "red",

        "standard_typeface": "MS Gothic",
        "standard_font_size": 12,
        "title_font_size": 16,

        "standard_margin": 8,
    },
    "barbie": {
        "primary_color": "pink",
        "secondary_color": "magenta",
        "tertiary_color": "cyan",

        "standard_typeface": "Ravie",
        "standard_font_size": 16,
        "title_font_size": 20,

        "standard_margin": 4,
    },
    "vampire": {
        "primary_color": "#220022",
        "secondary_color": "red",
        "tertiary_color": "white",

        "standard_typeface": "Old English Text Mt",
        "standard_font_size": 24,
        "title_font_size": 28,

        "standard_margin": 8,
    },
}

theme = themes.get(THEME_NAME, themes["hacker"])

widget_styles = {
    "TFrame": {
        "background": theme["primary_color"],
        "foreground": theme["secondary_color"],
    },
    "TLabel": {
        "font": (theme["standard_typeface"], theme["standard_font_size"]),
        "background": theme["primary_color"],
        "foreground": theme["secondary_color"],
    },
    "title.TLabel" : {
        "font": (theme["standard_typeface"], theme["title_font_size"]),
        "background": theme["secondary_color"],
        "foreground": theme["primary_color"],
    },
    "TCheckbutton": {
        "background": theme["primary_color"],
        "foreground": theme["secondary_color"],
        "activeforeground": theme["tertiary_color"],
        "activebackground": theme["tertiary_color"],
        "selectcolor": theme["tertiary_color"],
        "disabledforeground": theme["tertiary_color"],
        "highlightcolor": theme["tertiary_color"],
        "highlightbackground": theme["tertiary_color"],
        "font": (theme["standard_typeface"],theme["standard_font_size"]),
    },
    "TButton": {
        "background": theme["secondary_color"],
        "foreground": theme["primary_color"],
        "focuscolor": theme["tertiary_color"],
        "highlightcolor": theme["primary_color"],
        "bordercolor": theme["primary_color"],
        "font": (theme["standard_typeface"], theme["standard_font_size"]),
    },
    "TScale": {
        "troughcolor": theme["primary_color"],
        "background": theme["secondary_color"],
        "bordercolor": theme["tertiary_color"],
    },
}


def now() -> str:
    return datetime.now().strftime("%H:%M:%S.%f")


def to_readable(snake_case_string: str) -> str:
    return snake_case_string.replace("_", " ").title()


def to_snake_case(readable_string: str) -> str:
    return readable_string.replace(" ", "_").lower()


class InfoPair(Frame):
    def __init__(self, master: Misc, key, value):
        super().__init__(master)
        self.label_key = Label(self, text=str(key), justify="left")
        self.label_value = Label(self, text=str(value), justify="right", width=10)
        self.label_key.pack(side="left", anchor="nw")
        self.label_value.pack(side="right", anchor="ne")


title_packing = {
    "anchor": "n",
    "expand": False,
    "padx": theme["standard_margin"],
    "pady": theme["standard_margin"],
    "fill": "x",
}


class Title(Label):
    def __init__(self, master: Misc, text: str, **kwargs):
        super().__init__(master, **kwargs)
        self.label = Label(self, text=text, style="title.TLabel", justify="center")
        self.label.pack(expand=True, fill="both", anchor="center")
