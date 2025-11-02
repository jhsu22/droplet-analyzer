"""
UI Builder
Contains all UI building logic and widgets
"""

import customtkinter as ctk
from config import UIConfig, SliderConfig, SerialConfig, get_slider_params
from popup_windows import VideoPopup, ViewDataPopup, ExportPopup, SettingsPopup, HelpPopup


class UIFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        kwargs.setdefault('fg_color', UIConfig.COLOR_BG_PRIMARY)
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
            text_color=UIConfig.COLOR_TEXT_PRIMARY,
            font=self.master.custom_font,
            fg_color=UIConfig.COLOR_BG_PRIMARY
        )
        title_label.place(x=UIConfig.PADDING_MEDIUM, y=0, anchor="nw")

        panel = ctk.CTkFrame(container, **frame_kwargs)
        panel.place(x=0, y=UIConfig.PADDING_MEDIUM, relwidth=1, relheight=1, height=-UIConfig.PADDING_MEDIUM)

        return container, panel

    def setup_ui(self):

        # Configure the frame to expand
        self.grid_rowconfigure(0, weight=0)     # New header (fixed height)
        self.grid_rowconfigure(1, weight=1)     # Content area
        self.grid_columnconfigure(0, weight=1)

        # === HEADER ===
        header_container = ctk.CTkFrame(self, fg_color="transparent")
        header_container.grid(row=0, column=0, sticky="ew", padx=UIConfig.PADDING_LARGE, pady=(UIConfig.PADDING_LARGE, UIConfig.PADDING_MEDIUM))

        header = ctk.CTkFrame(
            header_container,
            border_width=UIConfig.HEADER_BORDER_WIDTH,
            border_color=UIConfig.COLOR_BORDER,
            fg_color=UIConfig.COLOR_BG_PRIMARY
        )
        header.pack(fill="both", expand=True, pady=(8, 0))

        header_title = ctk.CTkLabel(
            header_container,
            text=f" {UIConfig.HEADER_TITLE} ",
            text_color=UIConfig.COLOR_TEXT_PRIMARY,
            font=self.master.custom_font,
            fg_color=UIConfig.COLOR_BG_PRIMARY
        )
        header_title.place(x=UIConfig.PADDING_MEDIUM, y=0)

        # Action buttons container
        button_frame = ctk.CTkFrame(
            header,
            fg_color=UIConfig.COLOR_BG_PRIMARY
        )
        button_frame.pack(fill="x", padx=UIConfig.PADDING_MEDIUM, pady=(UIConfig.PADDING_LARGE, UIConfig.PADDING_MEDIUM))

        # Action buttons with popup callbacks
        self.video_button = ctk.CTkButton(
            button_frame,
            text="Video",
            font=self.master.custom_font,
            width=UIConfig.BUTTON_WIDTH,
            height=UIConfig.BUTTON_HEIGHT,
            corner_radius=UIConfig.BUTTON_CORNER_RADIUS,
            command=self.open_video_popup
        )
        self.video_button.pack(side="left", padx=UIConfig.PADDING_SMALL, pady=UIConfig.PADDING_MEDIUM)

        self.viewdata_button = ctk.CTkButton(
            button_frame,
            text="View Data",
            font=self.master.custom_font,
            width=UIConfig.BUTTON_WIDTH,
            height=UIConfig.BUTTON_HEIGHT,
            corner_radius=UIConfig.BUTTON_CORNER_RADIUS,
            command=self.open_viewdata_popup
        )
        self.viewdata_button.pack(side="left", padx=UIConfig.PADDING_SMALL, pady=UIConfig.PADDING_MEDIUM)

        self.export_button = ctk.CTkButton(
            button_frame,
            text="Export",
            font=self.master.custom_font,
            width=UIConfig.BUTTON_WIDTH,
            height=UIConfig.BUTTON_HEIGHT,
            corner_radius=UIConfig.BUTTON_CORNER_RADIUS,
            command=self.open_export_popup
        )
        self.export_button.pack(side="left", padx=UIConfig.PADDING_SMALL, pady=UIConfig.PADDING_MEDIUM)

        self.settings_button = ctk.CTkButton(
            button_frame,
            text="Settings",
            font=self.master.custom_font,
            width=UIConfig.BUTTON_WIDTH,
            height=UIConfig.BUTTON_HEIGHT,
            corner_radius=UIConfig.BUTTON_CORNER_RADIUS,
            command=self.open_settings_popup
        )
        self.settings_button.pack(side="left", padx=UIConfig.PADDING_SMALL, pady=UIConfig.PADDING_MEDIUM)

        self.help_button = ctk.CTkButton(
            button_frame,
            text="Help",
            font=self.master.custom_font,
            width=UIConfig.BUTTON_WIDTH,
            height=UIConfig.BUTTON_HEIGHT,
            corner_radius=UIConfig.BUTTON_CORNER_RADIUS,
            command=self.open_help_popup
        )
        self.help_button.pack(side="left", padx=UIConfig.PADDING_SMALL, pady=UIConfig.PADDING_MEDIUM)

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
            height=UIConfig.START_BUTTON_HEIGHT
        )
        start_stop_button.current_state = "on"
        start_stop_button.configure(command=lambda: start_stop_text(start_stop_button))
        start_stop_button.pack(side="right", padx=UIConfig.PADDING_SMALL, pady=UIConfig.PADDING_SMALL)

        # === CONTENT AREA ===
        content_frame = ctk.CTkFrame(
            self,
            fg_color=UIConfig.COLOR_BG_PRIMARY
        )
        content_frame.grid(row=1, column=0, sticky="nsew", padx=UIConfig.PADDING_SMALL, pady=0)
        content_frame.grid_rowconfigure(0, weight=1)            # Top row (image, parameters, serial)
        content_frame.grid_rowconfigure(1, weight=1)            # Bottom row (output)
        content_frame.grid_columnconfigure(0, weight=1)

        # === TOP ROW ===
        top_row = ctk.CTkFrame(
            content_frame,
            fg_color=UIConfig.COLOR_BG_PRIMARY
        )
        top_row.grid(row=0, column=0, sticky="nsew", padx=UIConfig.PADDING_MEDIUM, pady=0)
        top_row.grid_rowconfigure(0, weight=1)
        top_row.grid_columnconfigure(0, weight=UIConfig.GRID_WEIGHT_IMAGE)           # Image area
        top_row.grid_columnconfigure(1, weight=UIConfig.GRID_WEIGHT_PARAMETERS)      # Parameter edit area
        top_row.grid_columnconfigure(2, weight=UIConfig.GRID_WEIGHT_SERIAL)          # Serial connection

        # Image output panel with container
        image_container = ctk.CTkFrame(top_row, fg_color="transparent")
        image_container.grid(row=0, column=0, sticky="nsew", padx=(0, UIConfig.PADDING_MEDIUM), pady=(UIConfig.PADDING_SMALL, UIConfig.PADDING_SMALL))

        image_panel = ctk.CTkFrame(
            image_container,
            border_width=UIConfig.HEADER_BORDER_WIDTH,
            border_color=UIConfig.COLOR_BORDER,
            fg_color=UIConfig.COLOR_BG_PRIMARY
        )
        image_panel.pack(fill="both", expand=True, pady=(8, 0))

        image_title = ctk.CTkLabel(
            image_container,
            text=f" {UIConfig.PANEL_TITLE_IMAGE} ",
            text_color=UIConfig.COLOR_TEXT_PRIMARY,
            font=self.master.custom_font,
            fg_color=UIConfig.COLOR_BG_PRIMARY
        )
        image_title.place(x=UIConfig.PADDING_MEDIUM, y=0)

        image_label = ctk.CTkLabel(
            image_panel,
            text="(Droplet Preview)",
            text_color=UIConfig.COLOR_TEXT_PRIMARY,
        )
        image_label.place(relx=0.5, rely=0.5, anchor="center")

        # Parameters panel with container
        parameters_container = ctk.CTkFrame(top_row, fg_color="transparent")
        parameters_container.grid(row=0, column=1, sticky="nsew", padx=(UIConfig.PADDING_MEDIUM, UIConfig.PADDING_MEDIUM), pady=(UIConfig.PADDING_SMALL, UIConfig.PADDING_SMALL))

        parameters_panel = ctk.CTkFrame(
            parameters_container,
            border_width=UIConfig.HEADER_BORDER_WIDTH,
            border_color=UIConfig.COLOR_BORDER,
            fg_color=UIConfig.COLOR_BG_PRIMARY
        )
        parameters_panel.pack(fill="both", expand=True, pady=(8, 0))

        parameters_title = ctk.CTkLabel(
            parameters_container,
            text=f" {UIConfig.PANEL_TITLE_PARAMETERS} ",
            text_color=UIConfig.COLOR_TEXT_PRIMARY,
            font=self.master.custom_font,
            fg_color=UIConfig.COLOR_BG_PRIMARY
        )
        parameters_title.place(x=UIConfig.PADDING_MEDIUM, y=0)

        # Configure grid for parameters panel
        parameters_panel.grid_columnconfigure(0, weight=1)  # Label column
        parameters_panel.grid_columnconfigure(1, weight=3)  # Slider column
        parameters_panel.grid_columnconfigure(2, weight=0)  # Value column

        # Add padding frame
        param_inner = ctk.CTkFrame(parameters_panel, fg_color="transparent")
        param_inner.pack(fill="both", expand=True, padx=UIConfig.PADDING_MEDIUM, pady=UIConfig.PADDING_MEDIUM)
        param_inner.grid_columnconfigure(0, weight=1)
        param_inner.grid_columnconfigure(1, weight=3)
        param_inner.grid_columnconfigure(2, weight=0)

        # Get slider parameters
        slider_params = get_slider_params()

        # === CROP PARAMETERS ===
        crop_title = ctk.CTkLabel(
            param_inner,
            text="Crop Parameters",
            text_color=UIConfig.COLOR_TEXT_ACCENT,
            font=self.master.custom_font_bold
        )
        crop_title.grid(row=0, column=0, columnspan=3, sticky="w", padx=UIConfig.PADDING_SMALL, pady=(UIConfig.PADDING_LARGE, UIConfig.PADDING_MEDIUM))

        # X Start slider
        ctk.CTkLabel(param_inner, text="X Start:", font=self.master.custom_font).grid(
            row=1, column=0, sticky="w", padx=(UIConfig.PADDING_MEDIUM, UIConfig.PADDING_MEDIUM), pady=UIConfig.PADDING_SMALL
        )
        self.x_start_slider = ctk.CTkSlider(
            param_inner,
            from_=slider_params['x_start']['from_'],
            to=slider_params['x_start']['to'],
            number_of_steps=slider_params['x_start']['number_of_steps']
        )
        self.x_start_slider.set(slider_params['x_start']['default'])
        self.x_start_slider.grid(row=1, column=1, sticky="ew", pady=UIConfig.PADDING_SMALL)
        self.x_start_value = ctk.CTkLabel(
            param_inner,
            text=str(slider_params['x_start']['default']),
            width=SliderConfig.VALUE_LABEL_WIDTH,
            font=self.master.custom_font
        )
        self.x_start_value.grid(row=1, column=2, sticky="e", padx=(UIConfig.PADDING_MEDIUM, 0), pady=UIConfig.PADDING_SMALL)
        self.x_start_slider.configure(command=lambda v: self.x_start_value.configure(text=f"{int(v)}"))

        # Y Start slider
        ctk.CTkLabel(param_inner, text="Y Start:", font=self.master.custom_font).grid(
            row=2, column=0, sticky="w", padx=(UIConfig.PADDING_MEDIUM, UIConfig.PADDING_MEDIUM), pady=UIConfig.PADDING_SMALL
        )
        self.y_start_slider = ctk.CTkSlider(
            param_inner,
            from_=slider_params['y_start']['from_'],
            to=slider_params['y_start']['to'],
            number_of_steps=slider_params['y_start']['number_of_steps']
        )
        self.y_start_slider.set(slider_params['y_start']['default'])
        self.y_start_slider.grid(row=2, column=1, sticky="ew", pady=UIConfig.PADDING_SMALL)
        self.y_start_value = ctk.CTkLabel(
            param_inner,
            text=str(slider_params['y_start']['default']),
            width=SliderConfig.VALUE_LABEL_WIDTH,
            font=self.master.custom_font
        )
        self.y_start_value.grid(row=2, column=2, sticky="e", padx=(UIConfig.PADDING_MEDIUM, 0), pady=UIConfig.PADDING_SMALL)
        self.y_start_slider.configure(command=lambda v: self.y_start_value.configure(text=f"{int(v)}"))

        # X End slider
        ctk.CTkLabel(param_inner, text="X End:", font=self.master.custom_font).grid(
            row=3, column=0, sticky="w", padx=(UIConfig.PADDING_MEDIUM, UIConfig.PADDING_MEDIUM), pady=UIConfig.PADDING_SMALL
        )
        self.x_end_slider = ctk.CTkSlider(
            param_inner,
            from_=slider_params['x_end']['from_'],
            to=slider_params['x_end']['to'],
            number_of_steps=slider_params['x_end']['number_of_steps']
        )
        self.x_end_slider.set(slider_params['x_end']['default'])
        self.x_end_slider.grid(row=3, column=1, sticky="ew", pady=UIConfig.PADDING_SMALL)
        self.x_end_value = ctk.CTkLabel(
            param_inner,
            text=str(slider_params['x_end']['default']),
            width=SliderConfig.VALUE_LABEL_WIDTH,
            font=self.master.custom_font
        )
        self.x_end_value.grid(row=3, column=2, sticky="e", padx=(UIConfig.PADDING_MEDIUM, 0), pady=UIConfig.PADDING_SMALL)
        self.x_end_slider.configure(command=lambda v: self.x_end_value.configure(text=f"{int(v)}"))

        # Y End slider
        ctk.CTkLabel(param_inner, text="Y End:", font=self.master.custom_font).grid(
            row=4, column=0, sticky="w", padx=(UIConfig.PADDING_MEDIUM, UIConfig.PADDING_MEDIUM), pady=UIConfig.PADDING_SMALL
        )
        self.y_end_slider = ctk.CTkSlider(
            param_inner,
            from_=slider_params['y_end']['from_'],
            to=slider_params['y_end']['to'],
            number_of_steps=slider_params['y_end']['number_of_steps']
        )
        self.y_end_slider.set(slider_params['y_end']['default'])
        self.y_end_slider.grid(row=4, column=1, sticky="ew", pady=UIConfig.PADDING_SMALL)
        self.y_end_value = ctk.CTkLabel(
            param_inner,
            text=str(slider_params['y_end']['default']),
            width=SliderConfig.VALUE_LABEL_WIDTH,
            font=self.master.custom_font
        )
        self.y_end_value.grid(row=4, column=2, sticky="e", padx=(UIConfig.PADDING_MEDIUM, 0), pady=UIConfig.PADDING_SMALL)
        self.y_end_slider.configure(command=lambda v: self.y_end_value.configure(text=f"{int(v)}"))

        # === CANNY PARAMETERS ===
        canny_title = ctk.CTkLabel(
            param_inner,
            text="Canny Parameters",
            text_color=UIConfig.COLOR_TEXT_ACCENT,
            font=self.master.custom_font_bold
        )
        canny_title.grid(row=5, column=0, columnspan=3, sticky="w", padx=UIConfig.PADDING_SMALL, pady=(UIConfig.PADDING_LARGE, UIConfig.PADDING_MEDIUM))

        # Filter Size slider
        ctk.CTkLabel(param_inner, text="Filter Size:", font=self.master.custom_font).grid(
            row=6, column=0, sticky="w", padx=(UIConfig.PADDING_MEDIUM, UIConfig.PADDING_MEDIUM), pady=UIConfig.PADDING_SMALL
        )
        self.filter_slider = ctk.CTkSlider(
            param_inner,
            from_=slider_params['filter_size']['from_'],
            to=slider_params['filter_size']['to'],
            number_of_steps=slider_params['filter_size']['number_of_steps']
        )
        self.filter_slider.set(slider_params['filter_size']['default'])
        self.filter_slider.grid(row=6, column=1, sticky="ew", pady=UIConfig.PADDING_SMALL)
        self.filter_value = ctk.CTkLabel(
            param_inner,
            text=str(slider_params['filter_size']['default']),
            width=SliderConfig.VALUE_LABEL_WIDTH,
            font=self.master.custom_font
        )
        self.filter_value.grid(row=6, column=2, sticky="e", padx=(UIConfig.PADDING_MEDIUM, 0), pady=UIConfig.PADDING_SMALL)
        self.filter_slider.configure(command=lambda v: self.filter_value.configure(text=f"{int(v)}"))

        # Canny Low slider
        ctk.CTkLabel(param_inner, text="Canny Low:", font=self.master.custom_font).grid(
            row=7, column=0, sticky="w", padx=(UIConfig.PADDING_MEDIUM, UIConfig.PADDING_MEDIUM), pady=UIConfig.PADDING_SMALL
        )
        self.canny_low_slider = ctk.CTkSlider(
            param_inner,
            from_=slider_params['canny_low']['from_'],
            to=slider_params['canny_low']['to'],
            number_of_steps=slider_params['canny_low']['number_of_steps']
        )
        self.canny_low_slider.set(slider_params['canny_low']['default'])
        self.canny_low_slider.grid(row=7, column=1, sticky="ew", pady=UIConfig.PADDING_SMALL)
        self.canny_low_value = ctk.CTkLabel(
            param_inner,
            text=str(slider_params['canny_low']['default']),
            width=SliderConfig.VALUE_LABEL_WIDTH,
            font=self.master.custom_font
        )
        self.canny_low_value.grid(row=7, column=2, sticky="e", padx=(UIConfig.PADDING_MEDIUM, 0), pady=UIConfig.PADDING_SMALL)
        self.canny_low_slider.configure(command=lambda v: self.canny_low_value.configure(text=f"{int(v)}"))

        # Canny High slider
        ctk.CTkLabel(param_inner, text="Canny High:", font=self.master.custom_font).grid(
            row=8, column=0, sticky="w", padx=(UIConfig.PADDING_MEDIUM, UIConfig.PADDING_MEDIUM), pady=UIConfig.PADDING_SMALL
        )
        self.canny_high_slider = ctk.CTkSlider(
            param_inner,
            from_=slider_params['canny_high']['from_'],
            to=slider_params['canny_high']['to'],
            number_of_steps=slider_params['canny_high']['number_of_steps']
        )
        self.canny_high_slider.set(slider_params['canny_high']['default'])
        self.canny_high_slider.grid(row=8, column=1, sticky="ew", pady=UIConfig.PADDING_SMALL)
        self.canny_high_value = ctk.CTkLabel(
            param_inner,
            text=str(slider_params['canny_high']['default']),
            width=SliderConfig.VALUE_LABEL_WIDTH,
            font=self.master.custom_font
        )
        self.canny_high_value.grid(row=8, column=2, sticky="e", padx=(UIConfig.PADDING_MEDIUM, 0), pady=UIConfig.PADDING_SMALL)
        self.canny_high_slider.configure(command=lambda v: self.canny_high_value.configure(text=f"{int(v)}"))

        # Min Object Size slider
        ctk.CTkLabel(param_inner, text="Min Object Size:", font=self.master.custom_font).grid(
            row=9, column=0, sticky="w", padx=(UIConfig.PADDING_MEDIUM, UIConfig.PADDING_MEDIUM), pady=UIConfig.PADDING_SMALL
        )
        self.min_obj_slider = ctk.CTkSlider(
            param_inner,
            from_=slider_params['min_object_size']['from_'],
            to=slider_params['min_object_size']['to'],
            number_of_steps=slider_params['min_object_size']['number_of_steps']
        )
        self.min_obj_slider.set(slider_params['min_object_size']['default'])
        self.min_obj_slider.grid(row=9, column=1, sticky="ew", pady=UIConfig.PADDING_SMALL)
        self.min_obj_value = ctk.CTkLabel(
            param_inner,
            text=str(slider_params['min_object_size']['default']),
            width=SliderConfig.VALUE_LABEL_WIDTH,
            font=self.master.custom_font
        )
        self.min_obj_value.grid(row=9, column=2, sticky="e", padx=(UIConfig.PADDING_MEDIUM, 0), pady=UIConfig.PADDING_SMALL)
        self.min_obj_slider.configure(command=lambda v: self.min_obj_value.configure(text=f"{int(v)}"))

        # Sigma slider
        ctk.CTkLabel(param_inner, text="Sigma:", font=self.master.custom_font).grid(
            row=10, column=0, sticky="w", padx=(UIConfig.PADDING_MEDIUM, UIConfig.PADDING_MEDIUM), pady=UIConfig.PADDING_SMALL
        )
        self.sigma_slider = ctk.CTkSlider(
            param_inner,
            from_=slider_params['sigma']['from_'],
            to=slider_params['sigma']['to'],
            number_of_steps=slider_params['sigma']['number_of_steps']
        )
        self.sigma_slider.set(slider_params['sigma']['default'])
        self.sigma_slider.grid(row=10, column=1, sticky="ew", pady=UIConfig.PADDING_SMALL)
        self.sigma_value = ctk.CTkLabel(
            param_inner,
            text=f"{slider_params['sigma']['default']:.2f}",
            width=SliderConfig.VALUE_LABEL_WIDTH,
            font=self.master.custom_font
        )
        self.sigma_value.grid(row=10, column=2, sticky="e", padx=(UIConfig.PADDING_MEDIUM, 0), pady=UIConfig.PADDING_SMALL)
        self.sigma_slider.configure(command=lambda v: self.sigma_value.configure(text=f"{v:.2f}"))

        # Serial connection panel with container
        serial_container = ctk.CTkFrame(top_row, fg_color="transparent")
        serial_container.grid(row=0, column=2, sticky="nsew", padx=(UIConfig.PADDING_MEDIUM, 0), pady=(UIConfig.PADDING_SMALL, UIConfig.PADDING_SMALL))

        serial_panel = ctk.CTkFrame(
            serial_container,
            border_width=UIConfig.HEADER_BORDER_WIDTH,
            border_color=UIConfig.COLOR_BORDER,
            fg_color=UIConfig.COLOR_BG_PRIMARY
        )
        serial_panel.pack(fill="both", expand=True, pady=(8, 0))

        serial_title = ctk.CTkLabel(
            serial_container,
            text=f" {UIConfig.PANEL_TITLE_SERIAL} ",
            text_color=UIConfig.COLOR_TEXT_PRIMARY,
            font=self.master.custom_font,
            fg_color=UIConfig.COLOR_BG_PRIMARY
        )
        serial_title.place(x=UIConfig.PADDING_MEDIUM, y=0)

        # Configure grid for serial panel
        serial_panel.grid_columnconfigure(0, weight=1)
        serial_panel.grid_columnconfigure(1, weight=1)

        # Add padding frame
        serial_inner = ctk.CTkFrame(serial_panel, fg_color="transparent")
        serial_inner.pack(fill="both", expand=True, padx=UIConfig.PADDING_MEDIUM, pady=UIConfig.PADDING_MEDIUM)
        serial_inner.grid_columnconfigure(0, weight=0)
        serial_inner.grid_columnconfigure(1, weight=1)

        # === SERIAL CONNECTION ===

        # Connected device
        self.connected_label = ctk.CTkLabel(
            serial_inner,
            text=f"Connected Device: {SerialConfig.DEFAULT_DEVICE_NAME}",
            font=self.master.custom_font_bold,
            text_color=UIConfig.COLOR_TEXT_ACCENT,
        )
        self.connected_label.grid(row=0, column=0, pady=(20, UIConfig.PADDING_MEDIUM), padx=UIConfig.PADDING_MEDIUM, sticky="w")

        # Connection status (add python arduino integration)
        self.connection_status = ctk.CTkLabel(
            serial_inner,
            text=SerialConfig.STATUS_DISCONNECTED,
            text_color=UIConfig.COLOR_STATUS_DISCONNECTED,
            font=self.master.custom_font
        )
        self.connection_status.grid(row=0, column=1, pady=(20, UIConfig.PADDING_MEDIUM), padx=UIConfig.PADDING_LARGE, sticky="w")

        status = "disconnected"

        if status == "connected":
            self.connection_status.configure(
                text=SerialConfig.STATUS_CONNECTED,
                text_color=UIConfig.COLOR_STATUS_CONNECTED
            )
        elif status == "disconnected":
            self.connection_status.configure(
                text=SerialConfig.STATUS_DISCONNECTED,
                text_color=UIConfig.COLOR_STATUS_DISCONNECTED
            )

        # Port selection
        ctk.CTkLabel(serial_inner, text="Port:", font=self.master.custom_font).grid(
            row=1, column=0, sticky="w", pady=(UIConfig.PADDING_SMALL, UIConfig.PADDING_MEDIUM), padx=UIConfig.PADDING_MEDIUM
        )
        self.port_entry = ctk.CTkComboBox(
            serial_inner,
            values=SerialConfig.DEFAULT_PORTS,
            font=self.master.custom_font
        )
        self.port_entry.set(SerialConfig.DEFAULT_PORT)
        self.port_entry.grid(row=1, column=1, sticky="ew", padx=(UIConfig.PADDING_MEDIUM, 0), pady=(UIConfig.PADDING_SMALL, UIConfig.PADDING_MEDIUM))

        # Baud rate selection
        ctk.CTkLabel(serial_inner, text="Baud Rate:", font=self.master.custom_font).grid(
            row=2, column=0, sticky="w", pady=UIConfig.PADDING_MEDIUM, padx=UIConfig.PADDING_MEDIUM
        )
        self.baud_combo = ctk.CTkComboBox(
            serial_inner,
            values=SerialConfig.BAUD_RATES,
            font=self.master.custom_font
        )
        self.baud_combo.set(SerialConfig.DEFAULT_BAUD_RATE)
        self.baud_combo.grid(row=2, column=1, sticky="ew", padx=(UIConfig.PADDING_MEDIUM, 0), pady=UIConfig.PADDING_MEDIUM)

        # Command send
        self.send_command = ctk.CTkLabel(
            serial_inner,
            text="Send Command",
            font=self.master.custom_font_bold,
            text_color=UIConfig.COLOR_TEXT_ACCENT
        )
        self.send_command.grid(row=3, column=0, pady=(20, UIConfig.PADDING_MEDIUM), padx=UIConfig.PADDING_MEDIUM, sticky="w")

        self.command_box = ctk.CTkEntry(
            serial_inner,
            placeholder_text="Enter command here",
            font=self.master.custom_font
        )
        self.command_box.grid(row=4, column=0, columnspan=2, pady=(UIConfig.PADDING_MEDIUM, UIConfig.PADDING_MEDIUM), padx=UIConfig.PADDING_MEDIUM, sticky="ew")

        self.send_button = ctk.CTkButton(
            serial_inner,
            text="Send",
            font=self.master.custom_font
        )
        self.send_button.grid(row=5, column=0, pady=(UIConfig.PADDING_SMALL, UIConfig.PADDING_MEDIUM), padx=UIConfig.PADDING_MEDIUM, sticky="ew")

        # Serial output
        self.output_label = ctk.CTkLabel(
            serial_inner,
            text="Serial Output",
            font=self.master.custom_font_bold,
            text_color=UIConfig.COLOR_TEXT_ACCENT
        )
        self.output_label.grid(row=6, column=0, pady=(20, UIConfig.PADDING_MEDIUM), padx=UIConfig.PADDING_MEDIUM, sticky="w")

        self.output_box = ctk.CTkTextbox(
            serial_inner,
            fg_color=UIConfig.COLOR_BG_SECONDARY,
        )
        self.output_box.insert("0.0", SerialConfig.OUTPUT_PLACEHOLDER)
        self.output_box.configure(state="disabled")
        self.output_box.grid(row=7, column=0, columnspan=2, pady=(UIConfig.PADDING_MEDIUM, UIConfig.PADDING_MEDIUM), padx=UIConfig.PADDING_MEDIUM, sticky="ew")

        # === BOTTOM ROW ===
        bottom_row = ctk.CTkFrame(
            content_frame,
            fg_color=UIConfig.COLOR_BG_PRIMARY
        )
        bottom_row.grid(row=1, column=0, sticky="nsew", padx=UIConfig.PADDING_MEDIUM, pady=0)
        bottom_row.grid_rowconfigure(0, weight=1)
        bottom_row.grid_columnconfigure(0, weight=1)

        # Output panel with container
        output_container = ctk.CTkFrame(bottom_row, fg_color="transparent")
        output_container.grid(row=0, column=0, sticky="nsew", pady=UIConfig.PADDING_SMALL)

        output_panel = ctk.CTkFrame(
            output_container,
            border_width=UIConfig.HEADER_BORDER_WIDTH,
            border_color=UIConfig.COLOR_BORDER,
            fg_color=UIConfig.COLOR_BG_PRIMARY
        )
        output_panel.pack(fill="both", expand=True, pady=(8, 0))

        output_title = ctk.CTkLabel(
            output_container,
            text=f" {UIConfig.PANEL_TITLE_OUTPUT} ",
            text_color=UIConfig.COLOR_TEXT_PRIMARY,
            font=self.master.custom_font
            )
        output_title.place(x=UIConfig.PADDING_MEDIUM, y=0)

    # === POPUP CALLBACK METHODS ===

    def open_video_popup(self):
        """Open Video popup window"""
        VideoPopup(self.master)

    def open_viewdata_popup(self):
        """Open View Data popup window"""
        ViewDataPopup(self.master)

    def open_export_popup(self):
        """Open Export popup window"""
        ExportPopup(self.master)

    def open_settings_popup(self):
        """Open Settings popup window"""
        SettingsPopup(self.master)

    def open_help_popup(self):
        """Open Help popup window"""
        HelpPopup(self.master)
