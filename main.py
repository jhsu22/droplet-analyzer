"""
Pendant Droplet Analyzer - Main Application
"""

import sys
import os
import customtkinter as ctk

if sys.platform != "darwin":
    from tkextrafont import Font

from ui_builder import UIFrame
from config import UIConfig, PathConfig

import cv2
from PIL import Image


def resource_path(relative_path):
    # Get absolute path to resource, works for dev and for PyInstaller
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = PathConfig.BASE_PATH

    return base_path / relative_path


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self._setup_paths()
        self._load_theme()
        self._load_fonts()
        self._configure_window()
        self._create_ui()

    def _setup_paths(self):
        # Initialize asset paths
        self.BASE_PATH = PathConfig.BASE_PATH
        self.FONT_PATH = PathConfig.FONT_FILE
        self.IMAGE_PATH = PathConfig.IMAGES_PATH
        self.THEME_PATH = PathConfig.THEMES_PATH

    def _load_theme(self):
        # Load application theme
        try:
            ctk.set_default_color_theme(str(PathConfig.THEME_FILE))
        except Exception as e:
            print(f"Warning: Could not load theme: {e}")
            # Continue with default theme

    def _load_fonts(self):
        # Load custom fonts
        try:
            if sys.platform != "darwin":
                Font(file=self.FONT_PATH, family=UIConfig.FONT_FAMILY)

            self.custom_font = ctk.CTkFont(
                family=UIConfig.FONT_FAMILY,
                size=UIConfig.FONT_SIZE_NORMAL
            )
            self.custom_font_bold = ctk.CTkFont(
                family=UIConfig.FONT_FAMILY,
                size=UIConfig.FONT_SIZE_NORMAL,
                weight="bold"
            )
        except Exception as e:
            print(f"Warning: Could not load custom font: {e}")
            # Fallback to system font
            self.custom_font = ctk.CTkFont(size=UIConfig.FONT_SIZE_NORMAL)
            self.custom_font_bold = ctk.CTkFont(size=UIConfig.FONT_SIZE_NORMAL, weight="bold")

    def _configure_window(self):
        # Configure main window properties
        self.title(UIConfig.WINDOW_TITLE)
        self.geometry(UIConfig.WINDOW_GEOMETRY)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def _create_ui(self):
        # Create and display main UI
        self.frame = UIFrame(master=self)
        self.frame.grid(row=0, column=0, sticky="nsew")


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    main()