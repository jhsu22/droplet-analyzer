"""
Pendant Droplet UI
"""

import sys
import os
if sys.platform != "darwin":
    from tkextrafont import Font

from pathlib import Path
import customtkinter as ctk
from PIL import Image

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = Path(__file__).parent

    return base_path / relative_path

class UIFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        kwargs.setdefault('fg_color', '#1e1e2e')
        super().__init__(master, **kwargs)

        # Build UI
        self.setup_ui()

    def create_panel(self, parent, title, **frame_kwargs):

        # Container for title and panel
        container = ctk.CTkFrame(parent, fg_color="transparent")

        # Title label
        title_label = ctk.CTkLabel(
            container,
            text=f" {title} ",
            text_color="#cdd6f4",
            font=self.master.custom_font,
            fg_color="#1e1e2e"
        )
        title_label.place(x=10, y=0, anchor="nw")

        panel = ctk.CTkFrame(container, **frame_kwargs)
        panel.place(x=0, y=10, relwidth=1, relheight=1, height=-10)

        return container, panel

    def setup_ui(self):

        # Configure the frame to expand
        self.grid_rowconfigure(0, weight=0)     # New header (fixed height)
        self.grid_rowconfigure(1, weight=1)     # Content area
        self.grid_columnconfigure(0, weight=1)

        # === HEADER ===
        header_container = ctk.CTkFrame(self, fg_color="transparent")
        header_container.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 10))

        header = ctk.CTkFrame(
            header_container,
            border_width=2,
            border_color="#45475a",
            fg_color="#1e1e2e"
        )
        header.pack(fill="both", expand=True, pady=(8, 0))

        header_title = ctk.CTkLabel(
            header_container,
            text=" [PENDANT DROPLET ANALYZER] CONTROLS ",
            text_color="#cdd6f4",
            font=self.master.custom_font,
            fg_color="#1e1e2e"
        )
        header_title.place(x=10, y=0)

        # Action buttons container
        button_frame = ctk.CTkFrame(
            header,
            fg_color="#1e1e2e"
        )
        button_frame.pack(fill="x", padx=10, pady=(15, 10))

        # Action buttons
        action_buttons = ["Video", "View Data", "Export", "Settings", "Help"]
        for i in enumerate(action_buttons):
            button = ctk.CTkButton(
                button_frame,
                text=i[1],
                font=self.master.custom_font,
                width=50,
                height=30,
                corner_radius=0
            )
            button.pack(side="left", padx=5, pady=10)

        # Start/Stop button next to settings
        def start_stop_text(startstop):
            if startstop.current_state == "off":
                startstop.configure(text="Start Analysis")
                startstop.current_state = "on"
            else:
                startstop.configure(text="Stop Analysis")
                startstop.current_state = "off"

        start_stop_button = ctk.CTkButton(
            button_frame,
            text="Start Analysis",
            font=self.master.custom_font_bold,
            height=35
        )
        start_stop_button.current_state = "on"
        start_stop_button.configure(command=lambda: start_stop_text(start_stop_button))
        start_stop_button.pack(side="right", padx=5, pady=5)

        # === CONTENT AREA ===
        content_frame = ctk.CTkFrame(
            self,
            fg_color="#1e1e2e"
        )
        content_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=0)
        content_frame.grid_rowconfigure(0, weight=1)            # Top row (image, parameters, serial)
        content_frame.grid_rowconfigure(1, weight=1)            # Bottom row (output)
        content_frame.grid_columnconfigure(0, weight=1)

        # === TOP ROW ===
        top_row = ctk.CTkFrame(
            content_frame,
            fg_color="#1e1e2e"
        )
        top_row.grid(row=0, column=0, sticky="nsew", padx=10, pady=0)
        top_row.grid_rowconfigure(0, weight=1)
        top_row.grid_columnconfigure(0, weight=7)           # Image area
        top_row.grid_columnconfigure(1, weight=8)           # Parameter edit area
        top_row.grid_columnconfigure(2, weight=7)           # Serial connection

        # Image output panel with container
        image_container = ctk.CTkFrame(top_row, fg_color="transparent")
        image_container.grid(row=0, column=0, sticky="nsew", padx=(0,10), pady=(5, 5))

        image_panel = ctk.CTkFrame(
            image_container,
            border_width=2,
            border_color="#45475a",
            fg_color="#1e1e2e"
        )
        image_panel.pack(fill="both", expand=True, pady=(8, 0))

        image_title = ctk.CTkLabel(
            image_container,
            text=" IMAGE ",
            text_color="#cdd6f4",
            font=self.master.custom_font,
            fg_color="#1e1e2e"
        )
        image_title.place(x=10, y=0)

        image_label = ctk.CTkLabel(
            image_panel,
            text="(Droplet Preview)",
            text_color="#cdd6f4",
        )
        image_label.place(relx=0.5, rely=0.5, anchor="center")

        # Parameters panel with container
        parameters_container = ctk.CTkFrame(top_row, fg_color="transparent")
        parameters_container.grid(row=0, column=1, sticky="nsew", padx=(10,10), pady=(5, 5))

        parameters_panel = ctk.CTkFrame(
            parameters_container,
            border_width=2,
            border_color="#45475a",
            fg_color="#1e1e2e"
        )
        parameters_panel.pack(fill="both", expand=True, pady=(8, 0))

        parameters_title = ctk.CTkLabel(
            parameters_container,
            text=" PARAMETERS ",
            text_color="#cdd6f4",
            font=self.master.custom_font,
            fg_color="#1e1e2e"
        )
        parameters_title.place(x=10, y=0)

        # Configure grid for parameters panel
        parameters_panel.grid_columnconfigure(0, weight=1)  # Label column
        parameters_panel.grid_columnconfigure(1, weight=3)  # Slider column
        parameters_panel.grid_columnconfigure(2, weight=0)  # Value column

        # Add padding frame
        param_inner = ctk.CTkFrame(parameters_panel, fg_color="transparent")
        param_inner.pack(fill="both", expand=True, padx=10, pady=10)
        param_inner.grid_columnconfigure(0, weight=1)
        param_inner.grid_columnconfigure(1, weight=3)
        param_inner.grid_columnconfigure(2, weight=0)

        # === CROP PARAMETERS ===
        crop_title = ctk.CTkLabel(
            param_inner,
            text="Crop Parameters",
            text_color="#cba6f7",
            font=self.master.custom_font_bold
        )
        crop_title.grid(row=0, column=0, columnspan=3, sticky="w", padx=5, pady=(15, 10))

        # X Start slider
        ctk.CTkLabel(param_inner, text="X Start:", font=self.master.custom_font).grid(
            row=1, column=0, sticky="w", padx=(10, 10), pady=5
        )
        self.x_start_slider = ctk.CTkSlider(param_inner, from_=0, to=1920, number_of_steps=1920)
        self.x_start_slider.set(0)
        self.x_start_slider.grid(row=1, column=1, sticky="ew", pady=5)
        self.x_start_value = ctk.CTkLabel(param_inner, text="0", width=50, font=self.master.custom_font)
        self.x_start_value.grid(row=1, column=2, sticky="e", padx=(10, 0), pady=5)
        self.x_start_slider.configure(command=lambda v: self.x_start_value.configure(text=f"{int(v)}"))

        # Y Start slider
        ctk.CTkLabel(param_inner, text="Y Start:", font=self.master.custom_font).grid(
            row=2, column=0, sticky="w", padx=(10, 10), pady=5
        )
        self.y_start_slider = ctk.CTkSlider(param_inner, from_=0, to=1080, number_of_steps=1080)
        self.y_start_slider.set(0)
        self.y_start_slider.grid(row=2, column=1, sticky="ew", pady=5)
        self.y_start_value = ctk.CTkLabel(param_inner, text="0", width=50, font=self.master.custom_font)
        self.y_start_value.grid(row=2, column=2, sticky="e", padx=(10, 0), pady=5)
        self.y_start_slider.configure(command=lambda v: self.y_start_value.configure(text=f"{int(v)}"))

        # X End slider
        ctk.CTkLabel(param_inner, text="X End:", font=self.master.custom_font).grid(
            row=3, column=0, sticky="w", padx=(10, 10), pady=5
        )
        self.x_end_slider = ctk.CTkSlider(param_inner, from_=0, to=1920, number_of_steps=1920)
        self.x_end_slider.set(1920)
        self.x_end_slider.grid(row=3, column=1, sticky="ew", pady=5)
        self.x_end_value = ctk.CTkLabel(param_inner, text="1920", width=50, font=self.master.custom_font)
        self.x_end_value.grid(row=3, column=2, sticky="e", padx=(10, 0), pady=5)
        self.x_end_slider.configure(command=lambda v: self.x_end_value.configure(text=f"{int(v)}"))

        # Y End slider
        ctk.CTkLabel(param_inner, text="Y End:", font=self.master.custom_font).grid(
            row=4, column=0, sticky="w", padx=(10, 10), pady=5
        )
        self.y_end_slider = ctk.CTkSlider(param_inner, from_=0, to=1080, number_of_steps=1080)
        self.y_end_slider.set(1080)
        self.y_end_slider.grid(row=4, column=1, sticky="ew", pady=5)
        self.y_end_value = ctk.CTkLabel(param_inner, text="1080", width=50, font=self.master.custom_font)
        self.y_end_value.grid(row=4, column=2, sticky="e", padx=(10, 0), pady=5)
        self.y_end_slider.configure(command=lambda v: self.y_end_value.configure(text=f"{int(v)}"))

        # === CANNY PARAMETERS ===
        canny_title = ctk.CTkLabel(
            param_inner,
            text="Canny Parameters",
            text_color="#cba6f7",
            font=self.master.custom_font_bold
        )
        canny_title.grid(row=5, column=0, columnspan=3, sticky="w", padx=5, pady=(15, 10))

        # Filter Size slider
        ctk.CTkLabel(param_inner, text="Filter Size:", font=self.master.custom_font).grid(
            row=6, column=0, sticky="w", padx=(10, 10), pady=5
        )
        self.filter_slider = ctk.CTkSlider(param_inner, from_=1, to=25, number_of_steps=12)
        self.filter_slider.set(3)
        self.filter_slider.grid(row=6, column=1, sticky="ew", pady=5)
        self.filter_value = ctk.CTkLabel(param_inner, text="3", width=50, font=self.master.custom_font)
        self.filter_value.grid(row=6, column=2, sticky="e", padx=(10, 0), pady=5)
        self.filter_slider.configure(command=lambda v: self.filter_value.configure(text=f"{int(v)}"))

        # Canny Low slider
        ctk.CTkLabel(param_inner, text="Canny Low:", font=self.master.custom_font).grid(
            row=7, column=0, sticky="w", padx=(10, 10), pady=5
        )
        self.canny_low_slider = ctk.CTkSlider(param_inner, from_=0, to=255, number_of_steps=255)
        self.canny_low_slider.set(25)
        self.canny_low_slider.grid(row=7, column=1, sticky="ew", pady=5)
        self.canny_low_value = ctk.CTkLabel(param_inner, text="25", width=50, font=self.master.custom_font)
        self.canny_low_value.grid(row=7, column=2, sticky="e", padx=(10, 0), pady=5)
        self.canny_low_slider.configure(command=lambda v: self.canny_low_value.configure(text=f"{int(v)}"))

        # Canny High slider
        ctk.CTkLabel(param_inner, text="Canny High:", font=self.master.custom_font).grid(
            row=8, column=0, sticky="w", padx=(10, 10), pady=5
        )
        self.canny_high_slider = ctk.CTkSlider(param_inner, from_=0, to=255, number_of_steps=255)
        self.canny_high_slider.set(51)
        self.canny_high_slider.grid(row=8, column=1, sticky="ew", pady=5)
        self.canny_high_value = ctk.CTkLabel(param_inner, text="51", width=50, font=self.master.custom_font)
        self.canny_high_value.grid(row=8, column=2, sticky="e", padx=(10, 0), pady=5)
        self.canny_high_slider.configure(command=lambda v: self.canny_high_value.configure(text=f"{int(v)}"))

        # Min Object Size slider
        ctk.CTkLabel(param_inner, text="Min Object Size:", font=self.master.custom_font).grid(
            row=9, column=0, sticky="w", padx=(10, 10), pady=5
        )
        self.min_obj_slider = ctk.CTkSlider(param_inner, from_=0, to=500, number_of_steps=500)
        self.min_obj_slider.set(100)
        self.min_obj_slider.grid(row=9, column=1, sticky="ew", pady=5)
        self.min_obj_value = ctk.CTkLabel(param_inner, text="100", width=50, font=self.master.custom_font)
        self.min_obj_value.grid(row=9, column=2, sticky="e", padx=(10, 0), pady=5)
        self.min_obj_slider.configure(command=lambda v: self.min_obj_value.configure(text=f"{int(v)}"))

        # Serial connection panel with container
        serial_container = ctk.CTkFrame(top_row, fg_color="transparent")
        serial_container.grid(row=0, column=2, sticky="nsew", padx=(10,0), pady=(5, 5))

        serial_panel = ctk.CTkFrame(
            serial_container,
            border_width=2,
            border_color="#45475a",
            fg_color="#1e1e2e"
        )
        serial_panel.pack(fill="both", expand=True, pady=(8, 0))

        serial_title = ctk.CTkLabel(
            serial_container,
            text=" SERIAL ",
            text_color="#cdd6f4",
            font=self.master.custom_font,
            fg_color="#1e1e2e"
        )
        serial_title.place(x=10, y=0)

        # Configure grid for serial panel
        serial_panel.grid_columnconfigure(0, weight=1)
        serial_panel.grid_columnconfigure(1, weight=1)

        # Add padding frame
        serial_inner = ctk.CTkFrame(serial_panel, fg_color="transparent")
        serial_inner.pack(fill="both", expand=True, padx=10, pady=10)
        serial_inner.grid_columnconfigure(0, weight=0)
        serial_inner.grid_columnconfigure(1, weight=1)

        # === SERIAL CONNECTION ===

        # Connected device
        device_name = "Arduino UNO R3"

        self.connected_label = ctk.CTkLabel(
            serial_inner,
            text=f"Connected Device: {device_name}",
            font=self.master.custom_font_bold,
            text_color="#cba6f7",
        )
        self.connected_label.grid(row=0, column=0, pady=(20, 10), padx=10, sticky="w")

        # Connection status (add python arduino integration)
        self.connection_status = ctk.CTkLabel(
            serial_inner,
            text="● Disconnected",
            text_color="#e64c4c",
            font=self.master.custom_font
        )
        self.connection_status.grid(row=0, column=1, pady=(20, 10), padx=15, sticky="w")

        status = "disconnected"

        if status == "connected":
            self.connection_status.configure(text="● Connected", text_color="#63cf65")
        elif status == "disconnected":
            self.connection_status.configure(text="● Disconnected", text_color="#e64c4c")

        # Port selection
        ctk.CTkLabel(serial_inner, text="Port:", font=self.master.custom_font).grid(
            row=1, column=0, sticky="w", pady=(5, 10), padx=10
        )
        self.port_entry = ctk.CTkComboBox(
            serial_inner,
            values=["COM1", "COM2", "COM3", "COM4", "COM5", "COM6"],
            font=self.master.custom_font
        )
        self.port_entry.set("COM1")
        self.port_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=(5, 10))

        # Baud rate selection
        ctk.CTkLabel(serial_inner, text="Baud Rate:", font=self.master.custom_font).grid(
            row=2, column=0, sticky="w", pady=10, padx=10
        )
        self.baud_combo = ctk.CTkComboBox(
            serial_inner,
            values=["9600", "19200", "38400", "57600", "115200"],
            font=self.master.custom_font
        )
        self.baud_combo.set("9600")
        self.baud_combo.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=10)

        # Command send
        self.send_command = ctk.CTkLabel(
            serial_inner,
            text="Send Command",
            font=self.master.custom_font_bold,
            text_color="#cba6f7"
        )
        self.send_command.grid(row=3, column=0, pady=(20, 10), padx=10, sticky="w")

        self.command_box = ctk.CTkEntry(
            serial_inner,
            placeholder_text="Enter command here",
            font=self.master.custom_font
        )
        self.command_box.grid(row=4, column=0, columnspan=2, pady=(10, 10), padx=10, sticky="ew")

        self.send_button = ctk.CTkButton(
            serial_inner,
            text="Send",
            font=self.master.custom_font
        )
        self.send_button.grid(row=5, column=0, pady=(5, 10), padx=10, sticky="ew")

        # Serial output
        self.output_label = ctk.CTkLabel(
            serial_inner,
            text="Serial Output",
            font=self.master.custom_font_bold,
            text_color="#cba6f7"
        )
        self.output_label.grid(row=6, column=0, pady=(20, 10), padx=10, sticky="w")

        self.output_box = ctk.CTkTextbox(
            serial_inner,
            fg_color="#181825",
        )
        self.output_box.insert("0.0", "No output yet")
        self.output_box.configure(state="disabled")
        self.output_box.grid(row=7, column=0, columnspan=2, pady=(10, 10), padx=10, sticky="ew")

        # === BOTTOM ROW ===
        bottom_row = ctk.CTkFrame(
            content_frame,
            fg_color="#1e1e2e"
        )
        bottom_row.grid(row=1, column=0, sticky="nsew", padx=10, pady=0)
        bottom_row.grid_rowconfigure(0, weight=1)
        bottom_row.grid_columnconfigure(0, weight=1)

        # Output panel with container
        output_container = ctk.CTkFrame(bottom_row, fg_color="transparent")
        output_container.grid(row=0, column=0, sticky="nsew", pady=5)

        output_panel = ctk.CTkFrame(
            output_container,
            border_width=2,
            border_color="#45475a",
            fg_color="#1e1e2e"
        )
        output_panel.pack(fill="both", expand=True, pady=(8, 0))

        output_title = ctk.CTkLabel(
            output_container,
            text=" OUTPUT ",
            text_color="#cdd6f4",
            font=self.master.custom_font
            )
        output_title.place(x=10, y=0)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Asset management
        self.BASE_PATH = Path(__file__).parent
        self.FONT_PATH = self.BASE_PATH / "assets" / "fonts" / "JetBrainsMono.ttf"
        self.IMAGE_PATH = self.BASE_PATH / "assets" / "images"
        self.THEME_PATH = self.BASE_PATH / "assets" / "themes"

        # Set theme
        ctk.set_default_color_theme(str(self.THEME_PATH / "terminal_dark.json"))

        # Load custom font
        if sys.platform != "darwin":
            Font(file=self.FONT_PATH, family="JetBrains Mono")

        # Create font objects for use in widgets
        self.custom_font = ctk.CTkFont(family="JetBrains Mono", size=14)
        self.custom_font_bold = ctk.CTkFont(family="JetBrains Mono", size=14, weight="bold")

        # Window configuration
        self.title("Pendant Droplet Analyzer")
        self.geometry("900x600")

        # Make the window expandable (row and column 0 expand)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create and display the UI frame
        self.frame = UIFrame(master=self)
        self.frame.grid(row=0, column=0, sticky="nsew")

app = App()
app.mainloop()
