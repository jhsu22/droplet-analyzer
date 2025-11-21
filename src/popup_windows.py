"""
Popup Windows for Pendant Droplet Analyzer
Contains all popup dialog classes with consistent styling
"""

import csv
import os
from datetime import datetime
from tkinter import filedialog
from typing import Text

import customtkinter as ctk
import cv2
import matplotlib.figure as fig
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from PIL import Image, ImageTk

from config import PathConfig, PopupConfig, ProcessingConfig, UIConfig


def enumerate_cameras(max_tested=10):
    """
    Enumerate available cameras on the system

    :param max_tested: Maximum number of camera indices to test
    :return: List of available camera indices
    """
    available_cameras = []

    for i in range(max_tested):
        if cv2.VideoCapture(i).isOpened():
            cap = cv2.VideoCapture(i)

            camera_name = cap.getBackendName()
            available_cameras.append({"index": i, "name": camera_name})
            cap.release()

        else:
            pass

        if not available_cameras:
            print("No cameras found.")

    return available_cameras


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
        self.after(10, self.grab_set)

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
        self.container.pack(
            fill="both",
            expand=True,
            padx=UIConfig.PADDING_LARGE,
            pady=UIConfig.PADDING_LARGE,
        )

        # Create bordered panel
        self.panel = ctk.CTkFrame(
            self.container,
            border_width=UIConfig.HEADER_BORDER_WIDTH,
            border_color=UIConfig.COLOR_BORDER,
            fg_color=UIConfig.COLOR_BG_PRIMARY,
        )
        self.panel.pack(fill="both", expand=True, pady=(8, 0))

        # Create title label
        self.title_label = ctk.CTkLabel(
            self.container,
            text=f" {title} ",
            text_color=UIConfig.COLOR_TEXT_PRIMARY,
            font=parent.custom_font,
            fg_color=UIConfig.COLOR_BG_PRIMARY,
        )
        self.title_label.place(x=UIConfig.PADDING_MEDIUM, y=0)

        # Content frame inside panel (extra top padding to avoid label overlap)
        self.content_frame = ctk.CTkFrame(self.panel, fg_color="transparent")
        self.content_frame.pack(
            fill="both",
            expand=True,
            padx=UIConfig.PADDING_MEDIUM,
            pady=(UIConfig.PADDING_LARGE + 5, UIConfig.PADDING_MEDIUM),
        )


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
        self.preview_update_id = None  # Track the after callback ID

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
            command=self._on_mode_switch,
        )
        self.live_switch.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(UIConfig.PADDING_MEDIUM, UIConfig.PADDING_LARGE),
            padx=UIConfig.PADDING_SMALL,
        )

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
            placeholder_text="No video selected",
        )

        # Browse button
        self.browse_button = ctk.CTkButton(
            self.content_frame,
            text="Browse...",
            font=self.parent.custom_font,
            command=self.browse_video,
            width=100,
        )

        # Video info section label
        self.file_info_label = ctk.CTkLabel(
            self.content_frame,
            text="Video Information:",
            font=self.parent.custom_font_bold,
            text_color=UIConfig.COLOR_TEXT_ACCENT,
        )

        # Info display frame
        self.file_info_frame = ctk.CTkFrame(
            self.content_frame, fg_color=UIConfig.COLOR_BG_SECONDARY
        )

        self.file_info_text = ctk.CTkTextbox(
            self.file_info_frame,
            font=self.parent.custom_font,
            fg_color=UIConfig.COLOR_BG_SECONDARY,
            wrap="word",
        )
        self.file_info_text.pack(
            fill="both",
            expand=True,
            padx=UIConfig.PADDING_SMALL,
            pady=UIConfig.PADDING_SMALL,
        )
        self.file_info_text.insert("0.0", "No video loaded")
        self.file_info_text.configure(state="disabled")

        # Button frame
        self.file_button_frame = ctk.CTkFrame(
            self.content_frame, fg_color="transparent"
        )

        # Load Video button
        self.load_button = ctk.CTkButton(
            self.file_button_frame,
            text="Load Video",
            font=self.parent.custom_font_bold,
            command=self.load_video,
            state="disabled",
        )
        self.load_button.pack(side="right", padx=UIConfig.PADDING_SMALL)

        self.file_cancel_button = ctk.CTkButton(
            self.file_button_frame,
            text="Cancel",
            font=self.parent.custom_font,
            command=self.destroy,
        )
        self.file_cancel_button.pack(side="right", padx=UIConfig.PADDING_SMALL)

    def _create_live_mode_widgets(self):
        """Create widgets for live camera mode"""
        # Enumerate available cameras
        self.available_cameras = enumerate_cameras()
        camera_options = [
            f"Camera {cam['index']}: {cam['name']}" for cam in self.available_cameras
        ]

        if not camera_options:
            camera_options = ["No cameras available"]

        # Camera selection
        self.camera_label = ctk.CTkLabel(
            self.content_frame,
            text="Camera:",
            font=self.parent.custom_font,
            text_color=UIConfig.COLOR_TEXT_PRIMARY,
        )

        self.camera_combo = ctk.CTkComboBox(
            self.content_frame,
            values=camera_options,
            font=self.parent.custom_font,
            state="readonly" if self.available_cameras else "disabled",
            command=self._on_camera_select,
        )
        if self.available_cameras:
            self.camera_combo.set(camera_options[0])

        # Resolution Display
        self.resolution_label = ctk.CTkLabel(
            self.content_frame,
            text="Resolution:",
            font=self.parent.custom_font,
            text_color=UIConfig.COLOR_TEXT_PRIMARY,
        )

        self.resolution_value_label = ctk.CTkLabel(
            self.content_frame,
            text="-",
            font=self.parent.custom_font,
            text_color=UIConfig.COLOR_TEXT_ACCENT,
        )

        # FPS Display
        self.fps_label = ctk.CTkLabel(
            self.content_frame,
            text="Frame Rate:",
            font=self.parent.custom_font,
            text_color=UIConfig.COLOR_TEXT_PRIMARY,
        )

        self.fps_value_label = ctk.CTkLabel(
            self.content_frame,
            text="-",
            font=self.parent.custom_font,
            text_color=UIConfig.COLOR_TEXT_ACCENT,
        )

        # Test camera button and status frame
        self.test_frame = ctk.CTkFrame(
            self.content_frame, fg_color=UIConfig.COLOR_BG_SECONDARY
        )

        test_button_container = ctk.CTkFrame(self.test_frame, fg_color="transparent")
        test_button_container.pack(
            fill="x", padx=UIConfig.PADDING_SMALL, pady=UIConfig.PADDING_SMALL
        )

        self.test_button = ctk.CTkButton(
            test_button_container,
            text="Test Camera",
            font=self.parent.custom_font,
            command=self.test_camera,
            width=120,
        )
        self.test_button.pack(side="left", padx=UIConfig.PADDING_SMALL)

        # Camera preview
        self.preview_label = ctk.CTkLabel(
            self.test_frame,
            text="Camera Preview",
            font=self.parent.custom_font,
            text_color=UIConfig.COLOR_TEXT_PRIMARY,
        )
        self.preview_label.pack(
            fill="both",
            expand=True,
            padx=UIConfig.PADDING_SMALL,
            pady=UIConfig.PADDING_SMALL,
        )

        # Button frame
        self.live_button_frame = ctk.CTkFrame(
            self.content_frame, fg_color="transparent"
        )

        # Start Live Feed button
        self.start_live_button = ctk.CTkButton(
            self.live_button_frame,
            text="Start Live Feed",
            font=self.parent.custom_font_bold,
            command=self.start_live_feed,
        )
        self.start_live_button.pack(side="right", padx=UIConfig.PADDING_SMALL)

        self.live_cancel_button = ctk.CTkButton(
            self.live_button_frame,
            text="Cancel",
            font=self.parent.custom_font,
            command=self.destroy,
        )
        self.live_cancel_button.pack(side="right", padx=UIConfig.PADDING_SMALL)

        # Trigger initial camera info update after all widgets are created
        if self.available_cameras:
            self._on_camera_select(camera_options[0])

    def _on_mode_switch(self):
        """Handle toggle between file and live mode"""
        if self.live_switch.get():
            self._show_live_mode()
        else:
            self._show_file_mode()

    def _on_camera_select(self, choice):
        """Updates resolution and FPS labels based on selected camera"""
        try:
            # Extract index from string "Camera N: Name"
            index = int(choice.split(":")[0].replace("Camera ", ""))

            # Probe the camera (use default backend for cross-platform compatibility)
            temp_cap = cv2.VideoCapture(index)
            if temp_cap.isOpened():
                width = int(temp_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(temp_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = temp_cap.get(cv2.CAP_PROP_FPS)

                self.resolution_value_label.configure(text=f"{width}x{height}")
                self.fps_value_label.configure(text=f"{fps:.2f}")

                temp_cap.release()
            else:
                self.resolution_value_label.configure(text="Error")
                self.fps_value_label.configure(text="Error")

        except Exception as e:
            print(f"Error probing camera: {e}")
            self.resolution_value_label.configure(text="-")
            self.fps_value_label.configure(text="-")

    def _show_file_mode(self):
        """Show file loading widgets, hide live camera widgets"""
        # Hide live mode widgets
        self.camera_label.grid_remove()
        self.camera_combo.grid_remove()
        self.resolution_label.grid_remove()
        self.resolution_value_label.grid_remove()
        self.fps_label.grid_remove()
        self.fps_value_label.grid_remove()
        self.test_frame.grid_remove()
        self.live_button_frame.grid_remove()

        # Show file mode widgets
        self.file_path_entry.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=UIConfig.PADDING_SMALL,
            pady=UIConfig.PADDING_SMALL,
        )
        self.browse_button.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="w",
            padx=UIConfig.PADDING_SMALL,
            pady=UIConfig.PADDING_SMALL,
        )
        self.file_info_label.grid(
            row=3,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(UIConfig.PADDING_LARGE, UIConfig.PADDING_SMALL),
            padx=UIConfig.PADDING_SMALL,
        )
        self.file_info_frame.grid(
            row=4,
            column=0,
            columnspan=2,
            sticky="nsew",
            padx=UIConfig.PADDING_SMALL,
            pady=UIConfig.PADDING_SMALL,
        )
        self.file_button_frame.grid(
            row=5,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(UIConfig.PADDING_MEDIUM, 0),
        )

    def _show_live_mode(self):
        """Show live camera widgets, hide file loading widgets"""
        # Hide file mode widgets
        self.file_path_entry.grid_remove()
        self.browse_button.grid_remove()
        self.file_info_label.grid_remove()
        self.file_info_frame.grid_remove()
        self.file_button_frame.grid_remove()

        # Show live mode widgets
        self.camera_label.grid(
            row=1,
            column=0,
            sticky="w",
            padx=UIConfig.PADDING_SMALL,
            pady=UIConfig.PADDING_SMALL,
        )
        self.camera_combo.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=UIConfig.PADDING_SMALL,
            pady=UIConfig.PADDING_SMALL,
        )

        self.resolution_label.grid(
            row=2,
            column=0,
            sticky="w",
            padx=UIConfig.PADDING_SMALL,
            pady=UIConfig.PADDING_SMALL,
        )
        self.resolution_value_label.grid(  # Changed
            row=2,
            column=1,
            sticky="w",
            padx=UIConfig.PADDING_SMALL,
            pady=UIConfig.PADDING_SMALL,
        )

        self.fps_label.grid(
            row=3,
            column=0,
            sticky="w",
            padx=UIConfig.PADDING_SMALL,
            pady=UIConfig.PADDING_SMALL,
        )
        self.fps_value_label.grid(  # Changed
            row=3,
            column=1,
            sticky="w",
            padx=UIConfig.PADDING_SMALL,
            pady=UIConfig.PADDING_SMALL,
        )

        self.test_frame.grid(
            row=4,
            column=0,
            columnspan=2,
            sticky="nsew",
            padx=UIConfig.PADDING_SMALL,
            pady=(UIConfig.PADDING_LARGE, UIConfig.PADDING_SMALL),
        )
        self.live_button_frame.grid(
            row=5,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(UIConfig.PADDING_MEDIUM, 0),
        )

    def browse_video(self):
        """Open file dialog to select video file"""
        filetypes = (("Video files", "*.mp4 *.avi *.mov *.mkv"), ("All files", "*.*"))

        filename = filedialog.askopenfilename(
            title="Select Video File",
            initialdir=PathConfig.TEST_DATA_PATH,
            filetypes=filetypes,
        )

        filename_truncated = os.path.basename(filename)

        if filename:
            self.selected_video_path = filename
            self.file_path_entry.delete(0, "end")
            self.file_path_entry.insert(0, filename)
            self.load_button.configure(state="normal")

            cap = cv2.VideoCapture(filename)

            if cap.isOpened():
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                duration = frame_count / fps

            # Update info display
            self.file_info_text.configure(state="normal")
            self.file_info_text.delete("0.0", "end")
            self.file_info_text.insert(
                "0.0",
                f"File:     {filename_truncated}\n"
                f"Frames:   {frame_count}\n"
                f"Duration: {duration:.2f} seconds\n"
                f"FPS:      {fps:.2f}",
                "end",
            )
            self.file_info_text.configure(state="disabled")

    def test_camera(self):
        """Test the selected camera and display information"""
        if hasattr(self, "is_testing") and self.is_testing:
            self.stop_camera_test()
            return

        selected_camera = self.camera_combo.get()

        chosen_camera = None
        for cam in self.available_cameras:
            if selected_camera == f"Camera {cam['index']}: {cam['name']}":
                chosen_camera = cam
                break

        if chosen_camera:
            self.test_cap = cv2.VideoCapture(chosen_camera["index"])
            if self.test_cap.isOpened():
                self.is_testing = True
                self.test_button.configure(
                    text="Stop Test", fg_color=UIConfig.COLOR_STATUS_DISCONNECTED
                )
                self.update_camera_preview()
            else:
                print(f"Failed to open camera {chosen_camera['index']}")

        else:
            print("No camera selected")

    def stop_camera_test(self):
        """Stop the camera test"""
        # First, stop the testing flag to prevent new callbacks
        self.is_testing = False

        # Cancel any scheduled preview updates
        if self.preview_update_id is not None:
            self.after_cancel(self.preview_update_id)
            self.preview_update_id = None

        # Release the camera
        if hasattr(self, "test_cap") and self.test_cap:
            self.test_cap.release()
            self.test_cap = None

        # Reset the button
        self.test_button.configure(
            text="Test Camera", fg_color=UIConfig.COLOR_BG_PRIMARY
        )

        # Clear the image reference and reset the label
        if hasattr(self.preview_label, "_current_image"):
            self.preview_label._current_image = None
        self.preview_label.configure(image="", text="Camera Preview")

    def update_camera_preview(self):
        """Update the camera preview"""
        # Check if we should still be updating
        if not hasattr(self, "is_testing") or not self.is_testing:
            return

        try:
            # Check if the widget still exists
            if not self.winfo_exists():
                self.is_testing = False
                return

            ret, frame = self.test_cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(frame_rgb)
                ctk_image = ctk.CTkImage(
                    light_image=image, dark_image=image, size=(320, 240)
                )
                # Store reference to prevent garbage collection
                self.preview_label._current_image = ctk_image
                self.preview_label.configure(image=ctk_image, text="")

            # Schedule the next update only if still testing
            if self.is_testing:
                self.preview_update_id = self.after(15, self.update_camera_preview)
        except Exception as e:
            # Window might be closing, stop the preview
            print(f"Preview update error: {e}")
            self.is_testing = False
            self.preview_update_id = None

    def destroy(self):
        self.stop_camera_test()
        super().destroy()

    def load_video(self):
        """Load the selected video file"""
        print(f"Loaded video file.")
        if self.selected_video_path:
            self.parent.load_video(self.selected_video_path)
        self.destroy()

    def start_live_feed(self):
        """Start live camera feed"""

        selected_camera = self.camera_combo.get()

        chosen_camera = None
        for cam in self.available_cameras:
            if selected_camera == f"Camera {cam['index']}: {cam['name']}":
                chosen_camera = cam
                break

        if chosen_camera:
            self.parent.load_camera(chosen_camera["index"])
            print(f"Starting live feed for camera {self.selected_camera_index}")
        else:
            print("No valid camera selected,")

        self.destroy()


class ViewDataPopup(BasePopup):
    """Popup for viewing processed data"""

    def __init__(self, parent):
        super().__init__(
            parent,
            "VIEW DATA",
            PopupConfig.VIEWDATA_POPUP_WIDTH,
            PopupConfig.VIEWDATA_POPUP_HEIGHT,
        )

        # Configure grid weights to allow plot to expand
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        self.plot_data()

    def plot_data(self):
        # Get the data from the main application
        data = self.parent.analysis_results

        if not data:
            print("No data to plot. Run analysis first.")
            self.destroy()
            return

        # 1. Load Data
        df = pd.DataFrame(data)

        required_cols = ["frame_number", "surface_tension", "bond_number"]
        if not all(col in df.columns for col in required_cols):
            ctk.CTkLabel(
                self.content_frame,
                text="No data available.\nPlease run analysis first.",
            ).pack(pady=20)
            return

        # 2. Filter Data
        # Ensure that it is working with numeric types
        df["surface_tension"] = pd.to_numeric(df["surface_tension"], errors="coerce")
        df["bond_number"] = pd.to_numeric(df["bond_number"], errors="coerce")

        # Remove rows where the fit obviously failed
        df = df.dropna(subset=["surface_tension", "bond_number"])
        df = df[(df["surface_tension"] > 0) & (df["surface_tension"] < 0.2)]

        if df.empty:
            ctk.CTkLabel(
                self.content_frame, text="No valid data points found after filtering."
            ).pack(pady=20)
            return

        # 3. Calculate Moving Median
        df["tension_smooth"] = (
            df["surface_tension"].rolling(window=50, center=True).median()
        )
        df["bond_smooth"] = df["bond_number"].rolling(window=50, center=True).median()

        # 4. Create the Plot with Twin Axes
        fig = plt.Figure(figsize=(10, 6), dpi=100)
        ax1 = fig.add_subplot(111)

        # --- Plot Surface Tension (Left Axis) ---
        color = "tab:blue"
        ax1.set_xlabel("Frame Number")
        ax1.set_ylabel("Surface Tension (N/m)", color=color, fontsize=12)
        ax1.plot(
            df["frame_number"],
            df["surface_tension"],
            ".",
            color=color,
            alpha=0.3,
            label="Raw Data",
        )
        ax1.plot(
            df["frame_number"],
            df["tension_smooth"],
            "-",
            color=color,
            linewidth=2,
            label="Moving Median",
        )
        ax1.tick_params(axis="y", labelcolor=color)

        ax1.axhline(
            y=0.072,
            color="red",
            linestyle=":",
            alpha=0.5,
            label="Water Reference (0.072)",
        )

        ax1.legend(loc="upper left")

        # --- Plot Bond Number (Right Axis) ---
        ax2 = ax1.twinx()
        color = "tab:green"
        ax2.set_ylabel("Bond Number", color=color, fontsize=12)
        ax2.plot(
            df["frame_number"],
            df["bond_smooth"],
            "-",
            color=color,
            linewidth=2,
            linestyle="dashed",
            label="Bond Number",
        )
        ax2.tick_params(axis="y", labelcolor=color)

        ax2.legend(loc="upper right")

        # --- Annotations ---
        ax1.set_title("Surface Tension vs. Bond Number", fontsize=14)
        ax1.grid(True, alpha=0.3)
        fig.tight_layout()

        # 5. Embed the Plot in the CustomTkinter Window
        canvas = FigureCanvasTkAgg(fig, master=self.content_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        # Optional: Add Matplotlib Toolbar
        toolbar = NavigationToolbar2Tk(canvas, self.content_frame)
        toolbar.update()
        canvas.get_tk_widget().pack(fill="both", expand=True)


class ExportPopup(BasePopup):
    """Popup for exporting data"""

    def __init__(self, parent):
        super().__init__(
            parent,
            "EXPORT",
            PopupConfig.EXPORT_POPUP_WIDTH,
            PopupConfig.EXPORT_POPUP_HEIGHT,
        )

        # Configure grid
        self.content_frame.grid_columnconfigure(1, weight=1)

        row = 0

        # Export format selection
        ctk.CTkLabel(
            self.content_frame,
            text="Export Format:",
            font=self.parent.custom_font,
            text_color=UIConfig.COLOR_TEXT_PRIMARY,
        ).grid(
            row=row,
            column=0,
            sticky="w",
            pady=UIConfig.PADDING_SMALL,
            padx=UIConfig.PADDING_SMALL,
        )

        self.format_combo = ctk.CTkComboBox(
            self.content_frame,
            values=PopupConfig.EXPORT_FORMATS,
            font=self.parent.custom_font,
        )
        self.format_combo.set(PopupConfig.DEFAULT_EXPORT_FORMAT)
        self.format_combo.grid(
            row=row,
            column=1,
            sticky="ew",
            pady=UIConfig.PADDING_SMALL,
            padx=UIConfig.PADDING_SMALL,
        )

        row += 1

        # Output directory
        ctk.CTkLabel(
            self.content_frame,
            text="Output Directory:",
            font=self.parent.custom_font,
            text_color=UIConfig.COLOR_TEXT_PRIMARY,
        ).grid(
            row=row,
            column=0,
            sticky="w",
            pady=UIConfig.PADDING_SMALL,
            padx=UIConfig.PADDING_SMALL,
        )

        dir_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        dir_frame.grid(
            row=row,
            column=1,
            sticky="ew",
            pady=UIConfig.PADDING_SMALL,
            padx=UIConfig.PADDING_SMALL,
        )
        dir_frame.grid_columnconfigure(0, weight=1)

        self.dir_entry = ctk.CTkEntry(
            dir_frame,
            font=self.parent.custom_font,
            placeholder_text=str(PathConfig.OUTPUT_PATH),
        )
        self.dir_entry.grid(
            row=0, column=0, sticky="ew", padx=(0, UIConfig.PADDING_SMALL)
        )

        ctk.CTkButton(
            dir_frame,
            text="Browse...",
            font=self.parent.custom_font,
            command=self.browse_directory,
            width=80,
        ).grid(row=0, column=1)

        row += 1

        # Frame range section
        ctk.CTkLabel(
            self.content_frame,
            text="Frame Range:",
            font=self.parent.custom_font_bold,
            text_color=UIConfig.COLOR_TEXT_ACCENT,
        ).grid(
            row=row,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(UIConfig.PADDING_LARGE, UIConfig.PADDING_SMALL),
            padx=UIConfig.PADDING_SMALL,
        )

        row += 1

        # Start frame
        ctk.CTkLabel(
            self.content_frame,
            text="Start Frame:",
            font=self.parent.custom_font,
            text_color=UIConfig.COLOR_TEXT_PRIMARY,
        ).grid(
            row=row,
            column=0,
            sticky="w",
            pady=UIConfig.PADDING_SMALL,
            padx=UIConfig.PADDING_SMALL,
        )

        self.start_frame_slider = ctk.CTkSlider(
            self.content_frame, from_=0, to=1000, number_of_steps=1000
        )
        self.start_frame_slider.set(ProcessingConfig.DEFAULT_STARTING_FRAME)
        self.start_frame_slider.grid(
            row=row,
            column=1,
            sticky="ew",
            pady=UIConfig.PADDING_SMALL,
            padx=UIConfig.PADDING_SMALL,
        )

        row += 1

        # End frame
        ctk.CTkLabel(
            self.content_frame,
            text="End Frame:",
            font=self.parent.custom_font,
            text_color=UIConfig.COLOR_TEXT_PRIMARY,
        ).grid(
            row=row,
            column=0,
            sticky="w",
            pady=UIConfig.PADDING_SMALL,
            padx=UIConfig.PADDING_SMALL,
        )

        self.end_frame_slider = ctk.CTkSlider(
            self.content_frame, from_=0, to=1000, number_of_steps=1000
        )
        self.end_frame_slider.set(ProcessingConfig.DEFAULT_ENDING_FRAME)
        self.end_frame_slider.grid(
            row=row,
            column=1,
            sticky="ew",
            pady=UIConfig.PADDING_SMALL,
            padx=UIConfig.PADDING_SMALL,
        )

        row += 1

        # Options
        ctk.CTkLabel(
            self.content_frame,
            text="Options:",
            font=self.parent.custom_font_bold,
            text_color=UIConfig.COLOR_TEXT_ACCENT,
        ).grid(
            row=row,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(UIConfig.PADDING_LARGE, UIConfig.PADDING_SMALL),
            padx=UIConfig.PADDING_SMALL,
        )

        row += 1

        self.include_plots_var = ctk.BooleanVar(value=True)
        self.include_plots_check = ctk.CTkCheckBox(
            self.content_frame,
            text="Include plot images",
            font=self.parent.custom_font,
            variable=self.include_plots_var,
        )
        self.include_plots_check.grid(
            row=row,
            column=0,
            columnspan=2,
            sticky="w",
            pady=UIConfig.PADDING_SMALL,
            padx=UIConfig.PADDING_SMALL,
        )

        row += 1

        self.include_binary_var = ctk.BooleanVar(value=False)
        self.include_binary_check = ctk.CTkCheckBox(
            self.content_frame,
            text="Include binary edge images",
            font=self.parent.custom_font,
            variable=self.include_binary_var,
        )
        self.include_binary_check.grid(
            row=row,
            column=0,
            columnspan=2,
            sticky="w",
            pady=UIConfig.PADDING_SMALL,
            padx=UIConfig.PADDING_SMALL,
        )

        # Spacer
        self.content_frame.grid_rowconfigure(row + 1, weight=1)

        # Button frame
        button_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        button_frame.grid(
            row=row + 2,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(UIConfig.PADDING_MEDIUM, 0),
        )

        ctk.CTkButton(
            button_frame,
            text="Export",
            font=self.parent.custom_font_bold,
            command=self.export_data,
        ).pack(side="right", padx=UIConfig.PADDING_SMALL)

        ctk.CTkButton(
            button_frame,
            text="Cancel",
            font=self.parent.custom_font,
            command=self.destroy,
        ).pack(side="right", padx=UIConfig.PADDING_SMALL)

    def browse_directory(self):
        """Open directory selection dialog"""
        directory = filedialog.askdirectory(
            title="Select Output Directory", initialdir=PathConfig.OUTPUT_PATH
        )

        if directory:
            self.dir_entry.delete(0, "end")
            self.dir_entry.insert(0, directory)

    def export_data(self):
        """Export data to the selected format"""
        format_type = self.format_combo.get()

        # Get directory from entry or use default
        output_dir = self.dir_entry.get() or str(PathConfig.OUTPUT_PATH)

        # Create a filename with the current timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"droplet_analysis_{timestamp}"

        # Get the data from the main application
        data = self.parent.analysis_results

        if not data:
            print("No data to export. Run analysis first.")
            self.destroy()
            return

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        full_path = os.path.join(output_dir, filename)

        if format_type == "CSV":
            full_path += ".csv"
            try:
                headers = [
                    "frame_number",
                    "num_edge_points",
                    "bond_number",
                    "surface_tension",
                    "volume",
                    "apex_radius_physical",
                    "fit_iterations",
                ]

                with open(full_path, "w", newline="") as csvfile:
                    writer = csv.DictWriter(
                        csvfile, fieldnames=headers, extrasaction="ignore", restval=""
                    )
                    writer.writeheader()
                    writer.writerows(data)

                print(f"Successfully exported data to: {full_path}")

            except Exception as e:
                print(f"Error exporting CSV: {e}")

        elif format_type == "JSON":
            import json

            full_path += ".json"
            try:
                with open(full_path, "w") as jsonfile:
                    json.dump(data, jsonfile, indent=4)
                print(f"Successfully exported data to: {full_path}")
            except Exception as e:
                print(f"Error exporting JSON: {e}")

        # Close the popup
        self.destroy()


class SettingsPopup(BasePopup):
    """Popup for application settings"""

    def __init__(self, parent):
        super().__init__(
            parent,
            "SETTINGS",
            PopupConfig.SETTINGS_POPUP_WIDTH,
            PopupConfig.SETTINGS_POPUP_HEIGHT,
        )


class HelpPopup(BasePopup):
    """Popup for help documentation"""

    def __init__(self, parent):
        super().__init__(
            parent, "HELP", PopupConfig.HELP_POPUP_WIDTH, PopupConfig.HELP_POPUP_HEIGHT
        )

        # Help text display
        self.help_textbox = ctk.CTkTextbox(
            self.content_frame,
            font=self.parent.custom_font,
            fg_color=UIConfig.COLOR_BG_SECONDARY,
            wrap="word",
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
            command=self.destroy,
        ).pack(side="right", pady=(UIConfig.PADDING_MEDIUM, 0))


class CropPopup(BasePopup):
    """Popup for cropping documentation"""

    def __init__(self, parent):
        super().__init__(
            parent, "CROP", PopupConfig.CROP_POPUP_WIDTH, PopupConfig.CROP_POPUP_HEIGHT
        )

        # Save and exit button
        ctk.CTkButton(
            self.content_frame,
            text="Save & Close",
            font=self.parent.custom_font,
            command=self.save_and_close,
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
            self.display_image.thumbnail(
                (max_width, max_height), Image.Resampling.LANCZOS
            )

            self.photo_image = ImageTk.PhotoImage(self.display_image)

            canvas_width, canvas_height = self.display_image.size

            self.canvas = ctk.CTkCanvas(
                self.content_frame, width=canvas_width, height=canvas_height
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
        self.rect = self.canvas.create_rectangle(
            self.x_start, self.y_start, event.x, event.y, outline="red"
        )

    def on_mouse_drag(self, event):
        # Update rectangle position
        self.x_current = event.x
        self.y_current = event.y

        self.canvas.coords(
            self.rect, self.x_start, self.y_start, self.x_current, self.y_current
        )

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
            PopupConfig.DEBUG_POPUP_HEIGHT,
        )

        # Configure content frame to hold images
        self.grid_columnconfigure([0, 1, 2], weight=1, uniform="group")
        self.grid_rowconfigure(0, weight=1)

        # Create frames for each image
        median_frame = self.create_image_box(self.content_frame, "MEDIAN FILTER", 0)
        median_image_label = ctk.CTkLabel(median_frame, text="")
        median_image_label.pack(
            fill="both",
            expand=True,
            padx=UIConfig.PADDING_SMALL,
            pady=UIConfig.PADDING_SMALL,
        )

        gaussian_frame = self.create_image_box(self.content_frame, "GAUSSIAN BLUR", 1)
        gaussian_image_label = ctk.CTkLabel(gaussian_frame, text="")
        gaussian_image_label.pack(
            fill="both",
            expand=True,
            padx=UIConfig.PADDING_SMALL,
            pady=UIConfig.PADDING_SMALL,
        )

        final_frame = self.create_image_box(self.content_frame, "FINAL EDGE", 2)
        final_image_label = ctk.CTkLabel(final_frame, text="")
        final_image_label.pack(
            fill="both",
            expand=True,
            padx=UIConfig.PADDING_SMALL,
            pady=UIConfig.PADDING_SMALL,
        )

        # Display the images
        median_image_label.configure(image=images.get("median"))
        median_image_label.image = images.get("median")

        gaussian_image_label.configure(image=images.get("gaussian"))
        gaussian_image_label.image = images.get("gaussian")

        final_image_label.configure(image=images.get("final"))
        final_image_label.image = images.get("final")

        # Close button
        ctk.CTkButton(
            self.content_frame,
            text="Close",
            font=self.parent.custom_font,
            command=self.destroy,
        ).grid(row=1, column=2, pady=UIConfig.PADDING_SMALL, sticky="se")

    def create_image_box(self, parent, title, column):
        # Function to create a frame for an image
        frame = ctk.CTkFrame(
            parent,
            border_width=UIConfig.HEADER_BORDER_WIDTH,
            border_color=UIConfig.COLOR_BORDER,
            fg_color=UIConfig.COLOR_BG_SECONDARY,
        )
        frame.grid(
            row=0,
            column=column,
            sticky="nsew",
            padx=(0, UIConfig.PADDING_SMALL) if column < 2 else 0,
        )

        title_label = ctk.CTkLabel(
            frame,
            text=title,
            font=self.parent.custom_font,
        )
        title_label.pack(pady=(5, 0))

        return frame
