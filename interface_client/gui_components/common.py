from datetime import datetime
from tkinter import Misc
from tkinter.ttk import *

THEME_NAME = "hacker"

themes = {
    "hacker": {
        "primary_color": "black",
        "secondary_color": "lime",
        "tertiary_color": "lime",
        "standard_typeface": "Courier New",
        "standard_font_size": 12,
        "title_font_size": 16,
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
    "TCheckbutton": {
        "background": theme["primary_color"],
        "foreground": theme["secondary_color"],
        "focuscolor": theme["secondary_color"],
    },
    "TButton": {
        "background": theme["secondary_color"],
        "foreground": theme["primary_color"],
        "focuscolor": theme["tertiary_color"],
        "highlightcolor": theme["primary_color"],
        "bordercolor": theme["primary_color"],
        "font": (theme["standard_typeface"], 12),
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
        self.label_key = Label(text=str(key))
        self.label_value = Label(text=str(value))

        for label, side in zip([self.label_key, self.label_value], ["left", "right"]):
            label.pack(side=side, justify=side, expand=True, fill="both")
