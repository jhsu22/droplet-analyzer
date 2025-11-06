"""
UI Builder
Contains all UI building logic and widgets
"""

import sys
from io import StringIO
import customtkinter as ctk
from config import UIConfig, SliderConfig, SerialConfig, get_slider_params, processing_config
from popup_windows import VideoPopup, ViewDataPopup, ExportPopup, SettingsPopup, HelpPopup, CropPopup


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

        # Start/Stop button
        self.start_analysis_button = ctk.CTkButton(
            button_frame,
            text="Start Analysis",
            font=self.master.custom_font_bold,
            width=UIConfig.BUTTON_WIDTH,
            height=UIConfig.START_BUTTON_HEIGHT,
            command=self.master.start_analysis,
            state="disabled"
        )
        self.start_analysis_button.current_state = "on"
        self.start_analysis_button.pack(side="right", padx=UIConfig.PADDING_SMALL, pady=UIConfig.PADDING_SMALL)

        # Calibrate button
        self.calibrate_button = ctk.CTkButton(
            button_frame,
            text="Calibrate",
            font=self.master.custom_font_bold,
            height=UIConfig.START_BUTTON_HEIGHT,
            width=UIConfig.BUTTON_WIDTH,
            command=self.master.start_calibration,
            state="disabled"
        )
        self.calibrate_button.pack(side="right", padx=UIConfig.PADDING_SMALL, pady=UIConfig.PADDING_SMALL)

        # Video crop button
        self.crop_button = ctk.CTkButton(
            button_frame,
            text="Crop",
            font=self.master.custom_font_bold,
            width=UIConfig.BUTTON_WIDTH,
            height=UIConfig.START_BUTTON_HEIGHT,
            command=self.open_crop_popup
        )
        self.crop_button.pack(side="right", padx=UIConfig.PADDING_SMALL, pady=UIConfig.PADDING_SMALL)

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

        video_control_frame = ctk.CTkFrame(
            image_container,
            fg_color="transparent",
        )
        video_control_frame.pack(side="bottom", fill="x", pady=(UIConfig.PADDING_SMALL, 0))

        video_control_frame.grid_columnconfigure(0, weight=1) # Slider column
        video_control_frame.grid_columnconfigure(1, weight=0) # Label column

        self.video_slider = ctk.CTkSlider(
            video_control_frame,
            from_=0,
            to=1,                                   # Placeholder
            number_of_steps=1,                      # Placeholder
            command=self.master.seek_video_frame,
            state="disabled"
        )
        self.video_slider.grid(row=0, column=0, sticky="ew", padx=(UIConfig.PADDING_SMALL, UIConfig.PADDING_SMALL), pady=UIConfig.PADDING_SMALL)

        self.frame_number_label = ctk.CTkLabel(
            video_control_frame,
            text="Frame 0/0",                           # Placeholder
            text_color=UIConfig.COLOR_TEXT_PRIMARY,
            font=self.master.custom_font
        )
        self.frame_number_label.grid(row=0, column=1, sticky="e", padx=(0, UIConfig.PADDING_SMALL))

        self.image_panel = ctk.CTkFrame(
            image_container,
            border_width=UIConfig.HEADER_BORDER_WIDTH,
            border_color=UIConfig.COLOR_BORDER,
            fg_color=UIConfig.COLOR_BG_PRIMARY
        )
        self.image_panel.pack(fill="both", expand=True, pady=(8, 0))

        image_title = ctk.CTkLabel(
            image_container,
            text=f" {UIConfig.PANEL_TITLE_IMAGE} ",
            text_color=UIConfig.COLOR_TEXT_PRIMARY,
            font=self.master.custom_font,
            fg_color=UIConfig.COLOR_BG_PRIMARY
        )
        image_title.place(x=UIConfig.PADDING_MEDIUM, y=0)

        self.image_label = ctk.CTkLabel(
            self.image_panel,
            text="(Droplet Preview)",
            text_color=UIConfig.COLOR_TEXT_PRIMARY,
        )
        self.image_label.pack(fill="both", expand=True, padx=UIConfig.PADDING_SMALL, pady=UIConfig.PADDING_SMALL)

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
        self.slider_params = get_slider_params()
        self.sliders = {}
        self.slider_labels = {}

        # === FILTERING & SMOOTHING PARAMETERS ===
        canny_title = ctk.CTkLabel(
            param_inner,
            text="Filtering & Smoothing",
            text_color=UIConfig.COLOR_TEXT_ACCENT,
            font=self.master.custom_font_bold
        )
        canny_title.grid(row=5, column=0, columnspan=3, sticky="w", padx=UIConfig.PADDING_SMALL, pady=(UIConfig.PADDING_LARGE, UIConfig.PADDING_MEDIUM))

        self.create_slider(param_inner, "filter_size", "Median Filter Size:", 6)
        self.create_slider(param_inner, "sigma", "Gaussian Blur Sigma:", 7, is_float=True)

        # === CANNY DETECTION PARAMETERS ===
        canny_title = ctk.CTkLabel(
            param_inner,
            text="Canny Edge Detection",
            text_color=UIConfig.COLOR_TEXT_ACCENT,
            font=self.master.custom_font_bold
        )
        canny_title.grid(row=8, column=0, columnspan=3, sticky="w", padx=UIConfig.PADDING_SMALL,
                         pady=(UIConfig.PADDING_LARGE, UIConfig.PADDING_MEDIUM))

        self.create_slider(param_inner, "canny_low", "Canny Low Threshold:", 9)
        self.create_slider(param_inner, "canny_high", "Canny High Threshold:", 10)

        canny_note = ctk.CTkLabel(
            param_inner,
            text="Note: low threshold must be <= high threshold",
            text_color=UIConfig.COLOR_TEXT_ACCENT,
            font=(self.master.custom_font),
        )
        canny_note.grid(row=11, column=0, columnspan=3, sticky="w", padx=UIConfig.PADDING_MEDIUM,
                         pady=(0, UIConfig.PADDING_SMALL))

        # === EDGE CLEANING PARAMETERS ===
        canny_title = ctk.CTkLabel(
            param_inner,
            text="Edge Cleaning",
            text_color=UIConfig.COLOR_TEXT_ACCENT,
            font=self.master.custom_font_bold
        )
        canny_title.grid(row=12, column=0, columnspan=3, sticky="w", padx=UIConfig.PADDING_SMALL,
                         pady=(UIConfig.PADDING_LARGE, UIConfig.PADDING_MEDIUM))

        self.create_slider(param_inner, "min_object_size", "1st Pass Min Object Size:", 13)
        self.create_slider(param_inner, "min_size_mult", "Adaptive Size Multiplier:", 14, is_float=True)


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

        self.output_text = ctk.CTkTextbox(
            output_panel,
            fg_color=UIConfig.COLOR_BG_SECONDARY
        )
        self.output_text.pack(fill="both", expand=True, padx=UIConfig.PADDING_MEDIUM, pady=UIConfig.PADDING_MEDIUM)
        self.output_text.configure(state="disabled")

    def create_slider(self, parent, name, text, row, is_float=False):
        """Helper function to create a slider and its label."""
        ctk.CTkLabel(parent, text=text, font=self.master.custom_font).grid(
            row=row, column=0, sticky="w", padx=(UIConfig.PADDING_MEDIUM, UIConfig.PADDING_MEDIUM), pady=UIConfig.PADDING_SMALL
        )

        params = self.slider_params[name]
        slider = ctk.CTkSlider(
            parent,
            from_=params['from_'],
            to=params['to'],
            number_of_steps=params['number_of_steps']
        )
        slider.set(params['default'])
        slider.grid(row=row, column=1, sticky="ew", pady=UIConfig.PADDING_SMALL)

        value_label = ctk.CTkLabel(
            parent,
            width=SliderConfig.VALUE_LABEL_WIDTH,
            font=self.master.custom_font
        )
        value_label.grid(row=row, column=2, sticky="e", padx=(UIConfig.PADDING_MEDIUM, 0), pady=UIConfig.PADDING_SMALL)

        if is_float:
            slider.configure(command=lambda v, n=name: self.update_parameter(n, v, is_float=True))
            value_label.configure(text=f"{params['default']:.2f}")
        else:
            slider.configure(command=lambda v, n=name: self.update_parameter(n, v))
            value_label.configure(text=str(int(params['default'])))

        self.sliders[name] = slider
        self.slider_labels[name] = value_label

    def update_parameter(self, name, value, is_float=False):
        """Update the label for a slider and the corresponding config value."""
        if is_float:
            self.slider_labels[name].configure(text=f"{float(value):.2f}")
            setattr(processing_config, name, float(value))
        else:
            self.slider_labels[name].configure(text=f"{int(value)}")
            setattr(processing_config, name, int(value))

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

    def open_crop_popup(self):
        """Open crop popup window"""
        CropPopup(self.master)