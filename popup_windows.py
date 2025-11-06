"""
Popup Windows for Pendant Droplet Analyzer
Contains all popup dialog classes with consistent styling
"""

import customtkinter as ctk
from tkinter import filedialog
import cv2
from PIL import Image, ImageTk
from config import UIConfig, PopupConfig, PathConfig, ProcessingConfig


def enumerate_cameras(max_tested=10):
    """
    Enumerate available cameras on the system

    :param max_tested: Maximum number of camera indices to test
    :return: List of available camera indices
    """
    # TODO: Implement camera enumeration
    available = []
    return available


class BasePopup(ctk.CTkToplevel):
    """Base class for all popup windows with consistent styling"""

    def __init__(self, parent, title, width, height):
        super().__init__(parent)

        self.parent = parent

        # Window configuration
        self.title(title)
        self.geometry(f"{width}x{height}")

        # Make modal
        self.transient(parent)
        self.grab_set()

        # Center on parent window
        self.update_idletasks()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        x = parent_x + (parent_width // 2) - (width // 2)
        y = parent_y + (parent_height // 2) - (height // 2)

        self.geometry(f"{width}x{height}+{x}+{y}")

        # Configure window background
        self.configure(fg_color=UIConfig.COLOR_BG_PRIMARY)

        # Create main container
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True, padx=UIConfig.PADDING_LARGE, pady=UIConfig.PADDING_LARGE)

        # Create bordered panel
        self.panel = ctk.CTkFrame(
            self.container,
            border_width=UIConfig.HEADER_BORDER_WIDTH,
            border_color=UIConfig.COLOR_BORDER,
            fg_color=UIConfig.COLOR_BG_PRIMARY
        )
        self.panel.pack(fill="both", expand=True, pady=(8, 0))

        # Create title label
        self.title_label = ctk.CTkLabel(
            self.container,
            text=f" {title} ",
            text_color=UIConfig.COLOR_TEXT_PRIMARY,
            font=parent.custom_font,
            fg_color=UIConfig.COLOR_BG_PRIMARY
        )
        self.title_label.place(x=UIConfig.PADDING_MEDIUM, y=0)

        # Content frame inside panel (extra top padding to avoid label overlap)
        self.content_frame = ctk.CTkFrame(self.panel, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=UIConfig.PADDING_MEDIUM, pady=(UIConfig.PADDING_LARGE + 5, UIConfig.PADDING_MEDIUM))


class VideoPopup(BasePopup):
    """Popup for loading and configuring video files or live camera feed"""

    def __init__(self, parent):
        super().__init__(
            parent,
            "VIDEO",
            PopupConfig.VIDEO_POPUP_WIDTH,
            PopupConfig.VIDEO_POPUP_HEIGHT,
        )

        self.selected_video_path = None
        self.selected_camera_index = None

        # Configure grid
        self.content_frame.grid_columnconfigure(1, weight=1)
        self.content_frame.grid_rowconfigure(4, weight=1)

        # Live vs loaded video switch (always visible at top row)
        self.live_switch = ctk.CTkSwitch(
            self.content_frame,
            text="Live Video Feed",
            font=self.parent.custom_font,
            corner_radius=1,
            button_length=10,
            command=self._on_mode_switch
        )
        self.live_switch.grid(row=0, column=0, columnspan=2, sticky="w", pady=(UIConfig.PADDING_MEDIUM, UIConfig.PADDING_LARGE), padx=UIConfig.PADDING_SMALL)

        # Create all widgets for both modes
        self._create_file_mode_widgets()
        self._create_live_mode_widgets()

        # Show file mode by default
        self._show_file_mode()

    def _create_file_mode_widgets(self):
        """Create widgets for file loading mode"""
        # File path display
        self.file_path_entry = ctk.CTkEntry(
            self.content_frame,
            font=self.parent.custom_font,
            placeholder_text="No video selected"
        )

        # Browse button
        self.browse_button = ctk.CTkButton(
            self.content_frame,
            text="Browse...",
            font=self.parent.custom_font,
            command=self.browse_video,
            width=100
        )

        # Video info section label
        self.file_info_label = ctk.CTkLabel(
            self.content_frame,
            text="Video Information:",
            font=self.parent.custom_font_bold,
            text_color=UIConfig.COLOR_TEXT_ACCENT
        )

        # Info display frame
        self.file_info_frame = ctk.CTkFrame(self.content_frame, fg_color=UIConfig.COLOR_BG_SECONDARY)

        self.file_info_text = ctk.CTkTextbox(
            self.file_info_frame,
            font=self.parent.custom_font,
            fg_color=UIConfig.COLOR_BG_SECONDARY,
            wrap="word"
        )
        self.file_info_text.pack(fill="both", expand=True, padx=UIConfig.PADDING_SMALL, pady=UIConfig.PADDING_SMALL)
        self.file_info_text.insert("0.0", "No video loaded")
        self.file_info_text.configure(state="disabled")

        # Button frame
        self.file_button_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")

        # Load Video button
        self.load_button = ctk.CTkButton(
            self.file_button_frame,
            text="Load Video",
            font=self.parent.custom_font_bold,
            command=self.load_video,
            state="disabled"
        )
        self.load_button.pack(side="right", padx=UIConfig.PADDING_SMALL)

        self.file_cancel_button = ctk.CTkButton(
            self.file_button_frame,
            text="Cancel",
            font=self.parent.custom_font,
            command=self.destroy
        )
        self.file_cancel_button.pack(side="right", padx=UIConfig.PADDING_SMALL)

    def _create_live_mode_widgets(self):
        """Create widgets for live camera mode"""
        # Enumerate available cameras
        self.available_cameras = enumerate_cameras()
        camera_options = [f"Camera {i}" for i in self.available_cameras] if self.available_cameras else ["No cameras found"]

        # Camera selection
        self.camera_label = ctk.CTkLabel(
            self.content_frame,
            text="Camera:",
            font=self.parent.custom_font,
            text_color=UIConfig.COLOR_TEXT_PRIMARY
        )

        self.camera_combo = ctk.CTkComboBox(
            self.content_frame,
            values=camera_options,
            font=self.parent.custom_font,
            state="readonly" if self.available_cameras else "disabled"
        )
        if self.available_cameras:
            self.camera_combo.set(camera_options[0])

        # Resolution selection
        self.resolution_label = ctk.CTkLabel(
            self.content_frame,
            text="Resolution:",
            font=self.parent.custom_font,
            text_color=UIConfig.COLOR_TEXT_PRIMARY
        )

        self.resolution_combo = ctk.CTkComboBox(
            self.content_frame,
            values=["Auto (Default)", "640x480 (VGA)", "1280x720 (HD)", "1920x1080 (Full HD)"],
            font=self.parent.custom_font,
            state="readonly"
        )
        self.resolution_combo.set("Auto (Default)")

        # FPS selection
        self.fps_label = ctk.CTkLabel(
            self.content_frame,
            text="Frame Rate:",
            font=self.parent.custom_font,
            text_color=UIConfig.COLOR_TEXT_PRIMARY
        )

        self.fps_combo = ctk.CTkComboBox(
            self.content_frame,
            values=["Auto (Default)", "15 FPS", "30 FPS", "60 FPS"],
            font=self.parent.custom_font,
            state="readonly"
        )
        self.fps_combo.set("Auto (Default)")

        # Test camera button and status frame
        self.test_frame = ctk.CTkFrame(self.content_frame, fg_color=UIConfig.COLOR_BG_SECONDARY)

        test_button_container = ctk.CTkFrame(self.test_frame, fg_color="transparent")
        test_button_container.pack(fill="x", padx=UIConfig.PADDING_SMALL, pady=UIConfig.PADDING_SMALL)

        self.test_button = ctk.CTkButton(
            test_button_container,
            text="Test Camera",
            font=self.parent.custom_font,
            command=self.test_camera,
            width=120
        )
        self.test_button.pack(side="left", padx=UIConfig.PADDING_SMALL)

        self.test_status_label = ctk.CTkLabel(
            test_button_container,
            text="Not tested",
            font=self.parent.custom_font,
            text_color=UIConfig.COLOR_TEXT_PRIMARY
        )
        self.test_status_label.pack(side="left", padx=UIConfig.PADDING_MEDIUM)

        # Test results display
        self.live_info_text = ctk.CTkTextbox(
            self.test_frame,
            font=self.parent.custom_font,
            fg_color=UIConfig.COLOR_BG_SECONDARY,
            wrap="word",
            height=100
        )
        self.live_info_text.pack(fill="both", expand=True, padx=UIConfig.PADDING_SMALL, pady=UIConfig.PADDING_SMALL)
        self.live_info_text.insert("0.0", "Click 'Test Camera' to verify camera connection")
        self.live_info_text.configure(state="disabled")

        # Button frame
        self.live_button_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")

        # Start Live Feed button
        self.start_live_button = ctk.CTkButton(
            self.live_button_frame,
            text="Start Live Feed",
            font=self.parent.custom_font_bold,
            command=self.start_live_feed
        )
        self.start_live_button.pack(side="right", padx=UIConfig.PADDING_SMALL)

        self.live_cancel_button = ctk.CTkButton(
            self.live_button_frame,
            text="Cancel",
            font=self.parent.custom_font,
            command=self.destroy
        )
        self.live_cancel_button.pack(side="right", padx=UIConfig.PADDING_SMALL)

    def _on_mode_switch(self):
        """Handle toggle between file and live mode"""
        if self.live_switch.get():
            self._show_live_mode()
        else:
            self._show_file_mode()

    def _show_file_mode(self):
        """Show file loading widgets, hide live camera widgets"""
        # Hide live mode widgets
        self.camera_label.grid_remove()
        self.camera_combo.grid_remove()
        self.resolution_label.grid_remove()
        self.resolution_combo.grid_remove()
        self.fps_label.grid_remove()
        self.fps_combo.grid_remove()
        self.test_frame.grid_remove()
        self.live_button_frame.grid_remove()

        # Show file mode widgets
        self.file_path_entry.grid(row=1, column=0, columnspan=2, sticky="ew", padx=UIConfig.PADDING_SMALL, pady=UIConfig.PADDING_SMALL)
        self.browse_button.grid(row=2, column=0, columnspan=2, sticky="w", padx=UIConfig.PADDING_SMALL, pady=UIConfig.PADDING_SMALL)
        self.file_info_label.grid(row=3, column=0, columnspan=2, sticky="w", pady=(UIConfig.PADDING_LARGE, UIConfig.PADDING_SMALL), padx=UIConfig.PADDING_SMALL)
        self.file_info_frame.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=UIConfig.PADDING_SMALL, pady=UIConfig.PADDING_SMALL)
        self.file_button_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(UIConfig.PADDING_MEDIUM, 0))

    def _show_live_mode(self):
        """Show live camera widgets, hide file loading widgets"""
        # Hide file mode widgets
        self.file_path_entry.grid_remove()
        self.browse_button.grid_remove()
        self.file_info_label.grid_remove()
        self.file_info_frame.grid_remove()
        self.file_button_frame.grid_remove()

        # Show live mode widgets
        self.camera_label.grid(row=1, column=0, sticky="w", padx=UIConfig.PADDING_SMALL, pady=UIConfig.PADDING_SMALL)
        self.camera_combo.grid(row=1, column=1, sticky="ew", padx=UIConfig.PADDING_SMALL, pady=UIConfig.PADDING_SMALL)
        self.resolution_label.grid(row=2, column=0, sticky="w", padx=UIConfig.PADDING_SMALL, pady=UIConfig.PADDING_SMALL)
        self.resolution_combo.grid(row=2, column=1, sticky="ew", padx=UIConfig.PADDING_SMALL, pady=UIConfig.PADDING_SMALL)
        self.fps_label.grid(row=3, column=0, sticky="w", padx=UIConfig.PADDING_SMALL, pady=UIConfig.PADDING_SMALL)
        self.fps_combo.grid(row=3, column=1, sticky="ew", padx=UIConfig.PADDING_SMALL, pady=UIConfig.PADDING_SMALL)
        self.test_frame.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=UIConfig.PADDING_SMALL, pady=(UIConfig.PADDING_LARGE, UIConfig.PADDING_SMALL))
        self.live_button_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(UIConfig.PADDING_MEDIUM, 0))

    def browse_video(self):
        """Open file dialog to select video file"""
        filetypes = (
            ("Video files", "*.mp4 *.avi *.mov *.mkv"),
            ("All files", "*.*")
        )

        filename = filedialog.askopenfilename(
            title="Select Video File",
            initialdir=PathConfig.TEST_DATA_PATH,
            filetypes=filetypes
        )

        if filename:
            self.selected_video_path = filename
            self.file_path_entry.delete(0, "end")
            self.file_path_entry.insert(0, filename)
            self.load_button.configure(state="normal")

            # Update info display
            self.file_info_text.configure(state="normal")
            self.file_info_text.delete("0.0", "end")
            self.file_info_text.insert("0.0", f"File: {filename}\n\n")
            self.file_info_text.insert("end", "TODO: Display video information")
            self.file_info_text.configure(state="disabled")

    def test_camera(self):
        """Test the selected camera and display information"""
        # TODO: Implement camera testing logic
        pass

    def load_video(self):
        """Load the selected video file"""
        print(f"Loaded video file.")
        if self.selected_video_path:
            self.parent.load_video(self.selected_video_path)
        self.destroy()

    def start_live_feed(self):
        """Start live camera feed"""
        # TODO: Implement live feed logic
        print(f"Starting live feed")
        print(f"Resolution: {self.resolution_combo.get()}")
        print(f"FPS: {self.fps_combo.get()}")
        self.destroy()


class ViewDataPopup(BasePopup):
    """Popup for viewing processed data"""

    def __init__(self, parent):
        super().__init__(
            parent,
            "VIEW DATA",
            PopupConfig.VIEWDATA_POPUP_WIDTH,
            PopupConfig.VIEWDATA_POPUP_HEIGHT
        )

        # Search/filter section
        search_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, UIConfig.PADDING_MEDIUM))

        ctk.CTkLabel(
            search_frame,
            text="Search:",
            font=self.parent.custom_font,
            text_color=UIConfig.COLOR_TEXT_PRIMARY
        ).pack(side="left", padx=(0, UIConfig.PADDING_SMALL))

        self.search_entry = ctk.CTkEntry(
            search_frame,
            font=self.parent.custom_font,
            placeholder_text="Filter by frame number..."
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=UIConfig.PADDING_SMALL)

        # Data display (scrollable)
        self.data_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color=UIConfig.COLOR_BG_SECONDARY
        )
        self.data_frame.pack(fill="both", expand=True, pady=UIConfig.PADDING_SMALL)

        # Header row
        header_frame = ctk.CTkFrame(self.data_frame, fg_color=UIConfig.COLOR_BORDER)
        header_frame.pack(fill="x", pady=(0, UIConfig.PADDING_SMALL))

        headers = ["Frame #", "Edge Points", "Status", "Timestamp"]
        for header in headers:
            ctk.CTkLabel(
                header_frame,
                text=header,
                font=self.parent.custom_font_bold,
                text_color=UIConfig.COLOR_TEXT_ACCENT,
                width=150
            ).pack(side="left", padx=UIConfig.PADDING_SMALL, pady=UIConfig.PADDING_SMALL)

        # Placeholder data
        ctk.CTkLabel(
            self.data_frame,
            text="No data available. Run analysis first.",
            font=self.parent.custom_font,
            text_color=UIConfig.COLOR_TEXT_PRIMARY
        ).pack(pady=UIConfig.PADDING_LARGE)

        # Button frame
        button_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(UIConfig.PADDING_MEDIUM, 0))

        ctk.CTkButton(
            button_frame,
            text="Refresh",
            font=self.parent.custom_font,
            command=self.refresh_data
        ).pack(side="left", padx=UIConfig.PADDING_SMALL)

        ctk.CTkButton(
            button_frame,
            text="Close",
            font=self.parent.custom_font,
            command=self.destroy
        ).pack(side="right", padx=UIConfig.PADDING_SMALL)

    def refresh_data(self):
        """Refresh data display (to be implemented)"""
        print("Refreshing data...")
        # TODO: Implement data loading and display


class ExportPopup(BasePopup):
    """Popup for exporting data"""

    def __init__(self, parent):
        super().__init__(
            parent,
            "EXPORT",
            PopupConfig.EXPORT_POPUP_WIDTH,
            PopupConfig.EXPORT_POPUP_HEIGHT
        )

        # Configure grid
        self.content_frame.grid_columnconfigure(1, weight=1)

        row = 0

        # Export format selection
        ctk.CTkLabel(
            self.content_frame,
            text="Export Format:",
            font=self.parent.custom_font,
            text_color=UIConfig.COLOR_TEXT_PRIMARY
        ).grid(row=row, column=0, sticky="w", pady=UIConfig.PADDING_SMALL, padx=UIConfig.PADDING_SMALL)

        self.format_combo = ctk.CTkComboBox(
            self.content_frame,
            values=PopupConfig.EXPORT_FORMATS,
            font=self.parent.custom_font
        )
        self.format_combo.set(PopupConfig.DEFAULT_EXPORT_FORMAT)
        self.format_combo.grid(row=row, column=1, sticky="ew", pady=UIConfig.PADDING_SMALL, padx=UIConfig.PADDING_SMALL)

        row += 1

        # Output directory
        ctk.CTkLabel(
            self.content_frame,
            text="Output Directory:",
            font=self.parent.custom_font,
            text_color=UIConfig.COLOR_TEXT_PRIMARY
        ).grid(row=row, column=0, sticky="w", pady=UIConfig.PADDING_SMALL, padx=UIConfig.PADDING_SMALL)

        dir_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        dir_frame.grid(row=row, column=1, sticky="ew", pady=UIConfig.PADDING_SMALL, padx=UIConfig.PADDING_SMALL)
        dir_frame.grid_columnconfigure(0, weight=1)

        self.dir_entry = ctk.CTkEntry(
            dir_frame,
            font=self.parent.custom_font,
            placeholder_text=str(PathConfig.OUTPUT_PATH)
        )
        self.dir_entry.grid(row=0, column=0, sticky="ew", padx=(0, UIConfig.PADDING_SMALL))

        ctk.CTkButton(
            dir_frame,
            text="Browse...",
            font=self.parent.custom_font,
            command=self.browse_directory,
            width=80
        ).grid(row=0, column=1)

        row += 1

        # Frame range section
        ctk.CTkLabel(
            self.content_frame,
            text="Frame Range:",
            font=self.parent.custom_font_bold,
            text_color=UIConfig.COLOR_TEXT_ACCENT
        ).grid(row=row, column=0, columnspan=2, sticky="w", pady=(UIConfig.PADDING_LARGE, UIConfig.PADDING_SMALL), padx=UIConfig.PADDING_SMALL)

        row += 1

        # Start frame
        ctk.CTkLabel(
            self.content_frame,
            text="Start Frame:",
            font=self.parent.custom_font,
            text_color=UIConfig.COLOR_TEXT_PRIMARY
        ).grid(row=row, column=0, sticky="w", pady=UIConfig.PADDING_SMALL, padx=UIConfig.PADDING_SMALL)

        self.start_frame_slider = ctk.CTkSlider(
            self.content_frame,
            from_=0,
            to=1000,
            number_of_steps=1000
        )
        self.start_frame_slider.set(ProcessingConfig.DEFAULT_STARTING_FRAME)
        self.start_frame_slider.grid(row=row, column=1, sticky="ew", pady=UIConfig.PADDING_SMALL, padx=UIConfig.PADDING_SMALL)

        row += 1

        # End frame
        ctk.CTkLabel(
            self.content_frame,
            text="End Frame:",
            font=self.parent.custom_font,
            text_color=UIConfig.COLOR_TEXT_PRIMARY
        ).grid(row=row, column=0, sticky="w", pady=UIConfig.PADDING_SMALL, padx=UIConfig.PADDING_SMALL)

        self.end_frame_slider = ctk.CTkSlider(
            self.content_frame,
            from_=0,
            to=1000,
            number_of_steps=1000
        )
        self.end_frame_slider.set(ProcessingConfig.DEFAULT_ENDING_FRAME)
        self.end_frame_slider.grid(row=row, column=1, sticky="ew", pady=UIConfig.PADDING_SMALL, padx=UIConfig.PADDING_SMALL)

        row += 1

        # Options
        ctk.CTkLabel(
            self.content_frame,
            text="Options:",
            font=self.parent.custom_font_bold,
            text_color=UIConfig.COLOR_TEXT_ACCENT
        ).grid(row=row, column=0, columnspan=2, sticky="w", pady=(UIConfig.PADDING_LARGE, UIConfig.PADDING_SMALL), padx=UIConfig.PADDING_SMALL)

        row += 1

        self.include_plots_var = ctk.BooleanVar(value=True)
        self.include_plots_check = ctk.CTkCheckBox(
            self.content_frame,
            text="Include plot images",
            font=self.parent.custom_font,
            variable=self.include_plots_var
        )
        self.include_plots_check.grid(row=row, column=0, columnspan=2, sticky="w", pady=UIConfig.PADDING_SMALL, padx=UIConfig.PADDING_SMALL)

        row += 1

        self.include_binary_var = ctk.BooleanVar(value=False)
        self.include_binary_check = ctk.CTkCheckBox(
            self.content_frame,
            text="Include binary edge images",
            font=self.parent.custom_font,
            variable=self.include_binary_var
        )
        self.include_binary_check.grid(row=row, column=0, columnspan=2, sticky="w", pady=UIConfig.PADDING_SMALL, padx=UIConfig.PADDING_SMALL)

        # Spacer
        self.content_frame.grid_rowconfigure(row + 1, weight=1)

        # Button frame
        button_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        button_frame.grid(row=row + 2, column=0, columnspan=2, sticky="ew", pady=(UIConfig.PADDING_MEDIUM, 0))

        ctk.CTkButton(
            button_frame,
            text="Export",
            font=self.parent.custom_font_bold,
            command=self.export_data
        ).pack(side="right", padx=UIConfig.PADDING_SMALL)

        ctk.CTkButton(
            button_frame,
            text="Cancel",
            font=self.parent.custom_font,
            command=self.destroy
        ).pack(side="right", padx=UIConfig.PADDING_SMALL)

    def browse_directory(self):
        """Open directory selection dialog"""
        directory = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=PathConfig.OUTPUT_PATH
        )

        if directory:
            self.dir_entry.delete(0, "end")
            self.dir_entry.insert(0, directory)

    def export_data(self):
        """Export data (to be implemented)"""
        format_type = self.format_combo.get()
        output_dir = self.dir_entry.get() or str(PathConfig.OUTPUT_PATH)
        start_frame = int(self.start_frame_slider.get())
        end_frame = int(self.end_frame_slider.get())
        include_plots = self.include_plots_var.get()
        include_binary = self.include_binary_var.get()

        print(f"Exporting {format_type} to {output_dir}")
        print(f"Frame range: {start_frame}-{end_frame}")
        print(f"Include plots: {include_plots}, Include binary: {include_binary}")

        # TODO: Implement export logic
        self.destroy()


class SettingsPopup(BasePopup):
    """Popup for application settings"""

    def __init__(self, parent):
        super().__init__(
            parent,
            "SETTINGS",
            PopupConfig.SETTINGS_POPUP_WIDTH,
            PopupConfig.SETTINGS_POPUP_HEIGHT
        )


class HelpPopup(BasePopup):
    """Popup for help documentation"""

    def __init__(self, parent):
        super().__init__(
            parent,
            "HELP",
            PopupConfig.HELP_POPUP_WIDTH,
            PopupConfig.HELP_POPUP_HEIGHT
        )

        # Help text display
        self.help_textbox = ctk.CTkTextbox(
            self.content_frame,
            font=self.parent.custom_font,
            fg_color=UIConfig.COLOR_BG_SECONDARY,
            wrap="word"
        )
        self.help_textbox.pack(fill="both", expand=True, pady=UIConfig.PADDING_SMALL)

        # Insert help text
        self.help_textbox.insert("0.0", PopupConfig.HELP_TEXT)
        self.help_textbox.configure(state="disabled")

        # Close button
        ctk.CTkButton(
            self.content_frame,
            text="Close",
            font=self.parent.custom_font,
            command=self.destroy
        ).pack(side="right", pady=(UIConfig.PADDING_MEDIUM, 0))

class CropPopup(BasePopup):
    """Popup for cropping documentation"""
    def __init__(self, parent):
        super().__init__(
            parent,
            "CROP",
            PopupConfig.CROP_POPUP_WIDTH,
            PopupConfig.CROP_POPUP_HEIGHT
        )

        # Save and exit button
        ctk.CTkButton(
            self.content_frame,
            text="Save & Close",
            font = self.parent.custom_font,
            command=self.save_and_close
        ).pack(side="bottom", anchor="se", pady=(UIConfig.PADDING_MEDIUM, 0), padx=10)

        # Blank variables for crop dragging
        self.x_start = None
        self.y_start = None
        self.x_final = None
        self.y_final = None
        self.rect = None

        # Get current video frame
        cv2_frame = self.parent.get_current_frame()

        if cv2_frame is not None:

            self.pil_image = Image.fromarray(cv2.cvtColor(cv2_frame, cv2.COLOR_BGR2RGB))

            max_width = PopupConfig.CROP_POPUP_WIDTH
            max_height = PopupConfig.CROP_POPUP_HEIGHT - 50

            self.display_image = self.pil_image.copy()
            self.display_image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

            self.photo_image = ImageTk.PhotoImage(self.display_image)

            canvas_width, canvas_height = self.display_image.size

            self.canvas = ctk.CTkCanvas(
                self.content_frame,
                width=canvas_width,
                height=canvas_height
            )
            self.canvas.create_image(0, 0, anchor="nw", image=self.photo_image)
            self.canvas.pack()

            # Bind mouse actions to methods
            self.canvas.bind("<ButtonPress-1>", self.on_button_press)
            self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
            self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        else:
            ctk.CTkLabel(self.content_frame, text="No video loaded.").pack()

    def on_button_press(self, event):
        # Record starting position
        self.x_start = event.x
        self.y_start = event.y

        # Delete any existing rectangles
        if self.rect:
            self.canvas.delete(self.rect)

        # Create new rectangle at starting position
        self.rect = self.canvas.create_rectangle(self.x_start, self.y_start, event.x, event.y, outline="red")

    def on_mouse_drag(self, event):
        # Update rectangle position
        self.x_current = event.x
        self.y_current = event.y

        self.canvas.coords(self.rect, self.x_start, self.y_start, self.x_current, self.y_current)

    def on_button_release(self, event):
        # Finalize crop
        self.x_final = event.x
        self.y_final = event.y

    def save_and_close(self):
        from config import processing_config

        # Get final rectangle coordinates
        x0 = min(self.x_start, self.x_final)
        y0 = min(self.y_start, self.y_final)
        x1 = max(self.x_start, self.x_final)
        y1 = max(self.y_start, self.y_final)

        # Calculate scale factor of thumbnail to original image
        scale_x = self.pil_image.width / self.display_image.width
        scale_y = self.pil_image.height / self.display_image.height

        # Scale rectangle coordinates
        scaled_x0 = x0 * scale_x
        scaled_y0 = y0 * scale_y
        scaled_x1 = x1 * scale_x
        scaled_y1 = y1 * scale_y

        # Apply crop
        processing_config.x_start = scaled_x0
        processing_config.y_start = scaled_y0
        processing_config.x_end = scaled_x1
        processing_config.y_end = scaled_y1

        # Update UI
        self.parent.show_frame(int(self.parent.frame.video_slider.get()))

        # Exit window
        self.destroy()

class CalibrationPopup(BasePopup):
    """Popup for viewing intermediate image processing steps"""
    def __init__(self, parent, images):
        super().__init__(
            parent,
            "CALIBRATION RESULTS",
            PopupConfig.DEBUG_POPUP_WIDTH,
            PopupConfig.DEBUG_POPUP_HEIGHT
        )

        # Configure content frame to hold images
        self.grid_columnconfigure([0, 1, 2], weight=1, uniform="group")
        self.grid_rowconfigure(0, weight=1)

        # Create frames for each image
        median_frame = self.create_image_box(self.content_frame, "MEDIAN FILTER", 0)
        median_image_label = ctk.CTkLabel(median_frame, text="")
        median_image_label.pack(fill="both", expand=True, padx=UIConfig.PADDING_SMALL, pady=UIConfig.PADDING_SMALL)

        gaussian_frame = self.create_image_box(self.content_frame, "GAUSSIAN FILTER", 1)
        gaussian_image_label = ctk.CTkLabel(gaussian_frame, text="")
        gaussian_image_label.pack(fill="both", expand=True, padx=UIConfig.PADDING_SMALL, pady=UIConfig.PADDING_SMALL)

        canny_frame = self.create_image_box(self.content_frame, "CANNY FILTER", 2)
        canny_image_label = ctk.CTkLabel(canny_frame, text="")
        canny_image_label.pack(fill="both", expand=True, padx=UIConfig.PADDING_SMALL, pady=UIConfig.PADDING_SMALL)

        # Display the images
        median_image_label.configure(image=images.get("median"))
        median_image_label.image = images.get("median")

        gaussian_image_label.configure(image=images.get("gaussian"))
        gaussian_image_label.image = images.get("gaussian")

        canny_image_label.configure(image=images.get("canny"))
        canny_image_label.image = images.get("canny")

        # Close button
        ctk.CTkButton(
            self.content_frame,
            text="Close",
            font = self.parent.custom_font,
            command=self.destroy
        ).grid(row=1, column=2, pady=UIConfig.PADDING_SMALL, sticky="se")

    def create_image_box(self, parent, title, column):
        # Function to create a frame for an image
        frame = ctk.CTkFrame(
            parent,
            border_width=UIConfig.HEADER_BORDER_WIDTH,
            border_color=UIConfig.COLOR_BORDER,
            fg_color=UIConfig.COLOR_BG_SECONDARY
        )
        frame.grid(row=0, column=column, sticky="nsew", padx=(0, UIConfig.PADDING_SMALL) if column < 2 else 0)

        title_label = ctk.CTkLabel(
            frame,
            text=title,
            font=self.parent.custom_font,
        )
        title_label.pack(pady=(5, 0))

        return frame