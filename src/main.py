"""
Pendant Droplet Analyzer - Main Application
"""

import copy
import os
import sys
import threading

import customtkinter as ctk
from serial import Serial

if sys.platform == "win32":
    from tkextrafont import Font

import cv2
from PIL import Image

from config import (
    PathConfig,
    PopupConfig,
    SerialConfig,
    UIConfig,
    processing_config,
    serial_config,
)
from image_processing import calibrate, crop_image, process_frame_edge
from popup_windows import CalibrationPopup
from serial_manager import SerialManager, list_ports
from ui_builder import UIFrame
from young_laplace import YoungLaplaceFitter


def resource_path(relative_path):
    # Get absolute path to resource, works for dev and for PyInstaller
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = PathConfig.BASE_PATH

    return base_path / relative_path


class TextboxRedirector:
    """Redirects stdout to a CTkTextbox widget"""

    def __init__(self, textbox_widget):
        self.textbox = textbox_widget

    def write(self, text):
        self.textbox.after(0, self.insert_text, text)

    def insert_text(self, text):
        self.textbox.configure(state="normal")
        self.textbox.insert("end", text)
        self.textbox.see("end")
        self.textbox.configure(state="disabled")

    def flush(self):
        pass


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.serial_manager = None

        self.is_drawing_frame = False

        # State variables
        self.video_capture = None
        self.is_playing = False
        self.is_calibrated = False
        self.is_live = False
        self.num_frames = 0

        self.debug_popup = None

        self._setup_paths()
        self._set_output_paths()
        self._load_theme()
        self._load_fonts()
        self._load_ports()
        self._configure_window()
        self._create_ui()

        # Threading variables
        self.current_frame = None  # Latest frame from camera
        self.analysis_results = None  # Latest analysis results
        self.analysis_thread = None  # Thread object for analysis
        self.lock = threading.Lock()

        # Create textbox widget
        output_textbox = self.frame.output_text
        redirector = TextboxRedirector(output_textbox)

        sys.stdout = redirector
        sys.stderr = redirector

        print("---Application Started ---")

    # === Initialization === #
    def _set_output_paths(self):
        # Set base paths
        self.VIDEO_PATH = PathConfig.DEFAULT_VIDEO_FILE
        self.OUTPUT_DATA_PATH = PathConfig.OUTPUT_EDGE_DATA
        self.OUTPUT_IMG_PATH = PathConfig.OUTPUT_EDGE_PLOTS
        self.OUTPUT_BINARY_PATH = PathConfig.OUTPUT_BINARY_EDGES

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
            if sys.platform == "win32":
                Font(file=self.FONT_PATH, family=UIConfig.FONT_FAMILY)

            self.custom_font = ctk.CTkFont(
                family=UIConfig.FONT_FAMILY, size=UIConfig.FONT_SIZE_NORMAL
            )
            self.custom_font_bold = ctk.CTkFont(
                family=UIConfig.FONT_FAMILY,
                size=UIConfig.FONT_SIZE_NORMAL,
                weight="bold",
            )
        except Exception as e:
            print(f"Warning: Could not load custom font: {e}")
            # Fallback to system font
            self.custom_font = ctk.CTkFont(size=UIConfig.FONT_SIZE_NORMAL)
            self.custom_font_bold = ctk.CTkFont(
                size=UIConfig.FONT_SIZE_NORMAL, weight="bold"
            )

    def _load_ports(self):
        # Load available serial ports
        ports, descriptions = list_ports()

        serial_config.ports = ports
        serial_config.descriptions = descriptions

    # === UI Logic === #
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

        self.frame.image_panel.bind(
            "<Configure>", lambda e: self.frame.image_label.configure
        )

    def _create_ctk_image(self, np_array, panel_width, panel_height):
        # Convert a np array to a CTkImage and fit it to a panel

        if np_array is None or panel_width < 1 or panel_height < 1:
            return None

        image = Image.fromarray(np_array)
        image_aspect = image.width / image.height
        panel_aspect = panel_width / panel_height

        if image_aspect > panel_aspect:
            new_width = panel_width
            new_height = int(new_width / image_aspect)
        else:
            new_height = panel_height
            new_width = int(new_height * image_aspect)

        image_resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

        return ctk.CTkImage(
            light_image=image_resized,
            dark_image=image_resized,
            size=(new_width, new_height),
        )

    def update_fit_results(self, results):
        # Updates the results panel with calculated data
        if not results:
            return

        # Format the output string with aligned columns
        text = (
            f"\n"
            f"{'Bond Number':<16} : {results['bond_number']:>8.4f}\n"
            f"{'Surface Tension':<16} : {results['surface_tension'] * 1000:>8.4f} mN/m\n"
            f"{'Volume':<16} : {results['volume']:>8.4f} mL\n"
            f"{'Apex Radius':<16} : {results['apex_radius_physical']:>8.4f} mm\n"
        )

        # Update the UI element
        try:
            self.frame.fit_text.configure(state="normal")
            self.frame.fit_text.delete("0.0", "end")
            self.frame.fit_text.insert("0.0", text)
            self.frame.fit_text.configure(state="disabled")

        except Exception as e:
            print(f"Error updating UI: {e}")

    # === Analysis Logic === #
    def start_calibration(self):
        current_frame = int(self.frame.video_slider.get())
        print(f"Starting calibration on frame {current_frame}")

        calibration_results = calibrate(
            starting_frame=current_frame,
            crop_params=processing_config,
            video=self.video_capture,
            OUTPUT_DATA_PATH=self.OUTPUT_DATA_PATH,
            OUTPUT_IMG_PATH=self.OUTPUT_IMG_PATH,
        )

        final_image_np = calibration_results.get("cropped_image_color")

        if final_image_np is not None:
            final_image_rgb = cv2.cvtColor(final_image_np, cv2.COLOR_BGR2RGB)

            panel_width = self.frame.image_panel.winfo_width()
            panel_height = self.frame.image_panel.winfo_height()

            ctk_image = self._create_ctk_image(
                final_image_rgb, panel_width, panel_height
            )

            if ctk_image:
                self.frame.image_label.configure(image=ctk_image, text="")
                self.frame.image_label.image = ctk_image

        panel_width = PopupConfig.DEBUG_POPUP_WIDTH // 3
        panel_height = PopupConfig.DEBUG_POPUP_HEIGHT - 150

        images_for_popup = {
            "median": self._create_ctk_image(
                calibration_results.get("filtered_image"), panel_width, panel_height
            ),
            "gaussian": self._create_ctk_image(
                calibration_results.get("gaussian_image"), panel_width, panel_height
            ),
            "final": self._create_ctk_image(
                calibration_results.get("binary_edge_image"), panel_width, panel_height
            ),
        }

        CalibrationPopup(self, images=images_for_popup)

        calibration_radius = calibration_results.get("calibration_radius", 0)

        self.is_calibrated = True
        self.frame.start_analysis_button.configure(state="normal")
        print("Calibration complete. Ready to start analysis.")

    def start_analysis(self):
        if self.is_playing:
            self.is_playing = False
            self.frame.start_analysis_button.configure(text="Start Analysis")
            self.processing_complete = True
            print("Analysis stopped.")
            return

        if not self.is_calibrated:
            print("Run calibration before analysis.")
            return

        self.frame.start_analysis_button.configure(text="Stop Analysis")
        self.processing_complete = False

        print("Starting analysis.")
        # Create list to store results
        self.analysis_results = []
        self.is_playing = True
        self.yl_fitted_points = None

        # Start processing loop for image analysis
        if self.is_live:
            self.analysis_thread = threading.Thread(
                target=self.analysis_worker, daemon=True
            )
            self.analysis_thread.start()
            print("Live analysis started in background thread.")
            return

        # Start processing loop for video analysis
        self.frame.video_slider.set(0)
        self.update_video()

    def analysis_worker(self):
        # Background thread that processes the latest available frame
        while self.is_playing and self.is_live:
            # Take latest frame
            frame_to_process = None

            with self.lock:
                if self.current_frame is not None:
                    frame_to_process = self.current_frame.copy()

                if frame_to_process is None:
                    self.after(10)
                    continue

            # Run analysis code
            try:
                frame_results = process_frame_edge(
                    frame_to_process,
                    crop_params=processing_config,
                    filter_size=processing_config.filter_size,
                    canny_low=processing_config.canny_low,
                    canny_high=processing_config.canny_high,
                    min_object_size=processing_config.min_object_size,
                    sigma=processing_config.sigma,
                    adaptive_threshold=True,
                    yl_fitted_points=self.yl_fitted_points,  # Use fitted points from previous frame
                )

                radius = frame_results.get("apex_radius")
                edge_points = frame_results.get("edge_points")
                apex_point = frame_results.get("apex_point")

                if (
                    edge_points is not None
                    and radius is not None
                    and apex_point is not None
                ):
                    initial_params = {
                        "apex_radius": radius,
                        "apex_x": apex_point[0],
                        "apex_y": apex_point[1],
                        "rotation": 0,
                        "bond_number": processing_config.bond_number,
                        "delta_rho": processing_config.delta_rho,
                        "calibration_factor": processing_config.calibration_factor,
                    }

                    # Get Young-Laplace fit profile
                    fitter = YoungLaplaceFitter(edge_points, initial_params)
                    fitter.fit_profile()

                    # Get fit points
                    self.yl_fitted_points = fitter.get_fitted_profile()

                    younglaplace_results = fitter.get_results()

                    self.after(0, self.update_fit_results, younglaplace_results)

            except Exception as e:
                print(f"Analysis error: {e}")

    # === Video File Logic === #
    def load_video(self, video_path):
        # Load video, update UI controls, and show first frame
        if self.video_capture:
            self.video_capture.release()

        self.video_capture = cv2.VideoCapture(video_path)
        if not self.video_capture.isOpened():
            print("Error: Could not open video file")
            self.video_capture = None
            return

        # Get video properties
        self.num_frames = self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT)

        # Configure slider
        self.frame.video_slider.configure(
            to=self.num_frames - 1, number_of_steps=self.num_frames - 1
        )
        self.frame.video_slider.configure(state="normal")

        # Update button states
        self.frame.calibrate_button.configure(state="normal")
        self.frame.start_analysis_button.configure(state="disabled")
        self.is_calibrated = False

        self.show_frame(0)

    def seek_video_frame(self, value):
        # Called when video slider is moved
        frame_num = int(value)
        self.show_frame(frame_num)

    def show_frame(self, frame_num):
        # Seeks to specific frame and displays it
        if self.is_drawing_frame:
            return

        try:
            # Update drawing frame flag
            self.is_drawing_frame = True

            if not self.video_capture:
                return

            # Get frame and read it
            self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = self.video_capture.read()

            if ret:
                # Convert and crop image
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                cropped_frame = crop_image(
                    frame=rgb_frame, crop_params=processing_config
                )

                image = Image.fromarray(cropped_frame)

                # Get panel dimensions
                panel_width = self.frame.image_panel.winfo_width()
                panel_height = self.frame.image_panel.winfo_height()

                # Resize image based on limiting dimension
                if panel_width > 1 and panel_height > 1:
                    image_aspect = image.width / image.height
                    panel_aspect = panel_width / panel_height

                    if image_aspect > panel_aspect:
                        new_width = panel_width
                        new_height = int(new_width / image_aspect)
                    else:
                        new_height = panel_height
                        new_width = int(new_height * image_aspect)

                # Resize the image
                image_resized = image.resize(
                    (new_width, new_height), Image.Resampling.LANCZOS
                )

                # Create CTkImage
                ctk_image = ctk.CTkImage(
                    light_image=image_resized,
                    dark_image=image_resized,
                    size=(new_width, new_height),
                )

                # Update the label
                self.frame.image_label.configure(image=ctk_image, text="")
                self.frame.image_label.image = ctk_image

                # Update slider and its label
                self.frame.video_slider.set(frame_num)
                self.frame.frame_number_label.configure(
                    text=f"Frame {frame_num}/{int(self.num_frames - 1)}"
                )

            else:  # Video ended
                self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset

        finally:
            self.is_drawing_frame = False

    def get_current_frame(self):
        # Gets current frame as a cv2 frame
        if not self.video_capture:
            return None

        # Frame number from slider
        frame_num = int(self.frame.video_slider.get())

        # Get frame
        self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_num)

        ret, frame = self.video_capture.read()

        if ret:
            return frame
        else:
            return None

    def _on_image_panel_configure(self, event):
        current_frame = int(self.frame.video_slider.get())

        self.show_frame(current_frame)

    def update_video(self):
        if not self.is_playing:
            return

        current_frame = int(self.frame.video_slider.get())

        if current_frame < self.num_frames - 1:
            self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
            ret, frame = self.video_capture.read()

            if ret:
                frame_results = process_frame_edge(
                    frame,
                    crop_params=processing_config,
                    filter_size=processing_config.filter_size,
                    canny_low=processing_config.canny_low,
                    canny_high=processing_config.canny_high,
                    min_object_size=processing_config.min_object_size,
                    sigma=processing_config.sigma,
                    adaptive_threshold=True,
                    yl_fitted_points=self.yl_fitted_points,
                )

                radius = frame_results.get("apex_radius")

                edge_points = frame_results.get("edge_points")
                apex_point = frame_results.get("apex_point")

                if (
                    edge_points is not None
                    and radius is not None
                    and apex_point is not None
                ):
                    initial_params = {
                        "apex_radius": radius,
                        "apex_x": apex_point[0],
                        "apex_y": apex_point[1],
                        "rotation": 0,
                        "bond_number": processing_config.bond_number,
                        "delta_rho": processing_config.delta_rho,
                        "calibration_factor": processing_config.calibration_factor,
                    }

                    fitter = YoungLaplaceFitter(edge_points, initial_params)
                    fitter.fit_profile()
                    younglaplace_results = fitter.get_results()

                    self.yl_fitted_points = fitter.get_fitted_profile()

                    if younglaplace_results["is_converged"]:
                        self.update_fit_results(younglaplace_results)

                self.analysis_results.append(
                    {
                        "frame_number": current_frame,
                        "apex_radius": radius,
                        "num_edge_points": frame_results.get("num_edge_points"),
                    }
                )
                if current_frame % 50 == 0:
                    if radius is not None:
                        print(f"Frame {current_frame}: Apex Radius = {radius:.2f}")
                        print(
                            f"Frame {current_frame}: Young-Laplace fit converged after {younglaplace_results['iterations']} iterations"
                        )
                    else:
                        print(f"Frame {current_frame}: Apex fit failed.")

                final_image_np = frame_results.get("cropped_image_color")

                frame_data = {
                    "frame_number": current_frame,
                    "num_edge_points": frame_results.get("num_edge_points"),
                }

                if younglaplace_results and younglaplace_results["is_converged"]:
                    frame_data.update(
                        {
                            "bond_number": younglaplace_results["bond_number"],
                            "surface_tension": younglaplace_results["surface_tension"],
                            "volume": younglaplace_results["volume"],
                            "apex_radius": younglaplace_results["apex_radius_physical"],
                        }
                    )
                else:
                    frame_data.update(
                        {
                            "bond_number": None,
                            "surface_tension": None,
                            "volume": None,
                            "apex_radius": None,
                        }
                    )

                self.analysis_results.append(frame_data)

                if final_image_np is not None:
                    final_image_rgb = cv2.cvtColor(final_image_np, cv2.COLOR_BGR2RGB)

                    panel_width = self.frame.image_panel.winfo_width()
                    panel_height = self.frame.image_panel.winfo_height()

                    ctk_image = self._create_ctk_image(
                        final_image_rgb, panel_width, panel_height
                    )

                    if ctk_image:
                        self.frame.image_label.configure(image=ctk_image, text="")
                        self.frame.image_label.image = ctk_image

                next_frame = current_frame + 1
                self.frame.video_slider.set(next_frame)
                self.frame.frame_number_label.configure(
                    text=f"Frame {next_frame}/{int(self.num_frames - 1)}"
                )

                self.after(15, self.update_video)
        else:
            print("Analysis complete.")
            print(f"Processsed {len(self.analysis_results)} frames.")
            self.is_playing = False
            self.processing_complete = True

            self.frame.start_analysis_button.configure(text="Start Analysis")

    # === Live Video Logic === #
    def load_camera(self, index):
        # Initialize live camera and start feed
        if self.video_capture:
            self.video_capture.release()

        # Initialize camera
        if sys.platform == "win32":
            self.video_capture = cv2.VideoCapture(
                index, cv2.CAP_DSHOW
            )  # Use DirectShow on windows for better performance
        else:
            self.video_capture = cv2.VideoCapture(index)

        if not self.video_capture.isOpened():
            print("Error: Could not open camera")
            self.video_capture = None
            return

        # Set state flags
        self.is_live = True  # Live camera flag
        self.is_playing = False  # Analysis flag
        self.is_calibrated = False  # Calibration flag

        self.frame.video_slider.configure(state="disabled")
        self.frame.frame_number_label.configure(text="LIVE FEED")
        self.frame.calibrate_button.configure(state="normal")
        self.frame.start_analysis_button.configure(state="disabled")

        self.update_camera_feed()

    def update_camera_feed(self):
        # Continuous loop for live camera feed
        if not self.is_live or not self.video_capture:
            return

        ret, frame = self.video_capture.read()

        if ret:
            with self.lock:
                self.current_frame = frame

                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                display_rgb = crop_image(
                    frame_rgb,
                    crop_params=processing_config,
                )

                # If we have points from the background thread, draw them
                if self.is_playing and self.yl_fitted_points is not None:
                    cv2.polylines(
                        display_rgb,
                        [self.yl_fitted_points],
                        isClosed=False,
                        color=(0, 255, 0),
                        thickness=5,
                    )

                # Get panel dimensions
                panel_width = self.frame.image_panel.winfo_width()
                panel_height = self.frame.image_panel.winfo_height()

                # Create and set the image
                ctk_image = self._create_ctk_image(
                    display_rgb, panel_width, panel_height
                )

                if ctk_image:
                    self.frame.image_label.configure(image=ctk_image, text="")
                    self.frame.image_label.image = ctk_image

        # Schedule the next update (approx 30 FPS -> 33ms)
        self.after(30, self.update_camera_feed)

    # === Serial Logic === #
    def connect_serial(self):
        # Get port and baud rate from UI widgets
        port = self.frame.port_entry.get()
        baud = int(self.frame.baud_combo.get())

        # Create a SerialManager instance
        self.serial_manager = SerialManager(port, baud)

        self.serial_manager.connect()

        if self.serial_manager.is_running:
            self.frame.connection_status.configure(text=SerialConfig.STATUS_CONNECTED)
            self.frame.connection_status.configure(
                text_color=UIConfig.COLOR_STATUS_CONNECTED
            )

            self.check_serial_queue()

        else:
            self.frame.connection_status.configure(text="Connection Failed")
            self.frame.connection_status.configure(
                text_color=UIConfig.COLOR_STATUS_DISCONNECTED
            )

    def send_serial_command(self):
        # Get command from UI widget
        command = self.frame.command_box.get()

        if self.serial_manager and command:
            # Send command to serial port
            self.serial_manager.send_command(command)

            # Clear entry box
            self.frame.command_box.delete(0, "end")

    def check_serial_queue(self):
        try:
            if (
                self.serial_manager and self.serial_manager.is_running
            ):  # Check if connected
                message = self.serial_manager.read_line(timeout=0.1)

                if message:
                    # Add the message to the output box
                    self.frame.output_box.configure(state="normal")
                    self.frame.output_box.insert("end", message + "\n")
                    self.frame.output_box.configure(state="disabled")

        except Exception as e:
            # If serial fails, print once and stop checking
            print(f"Serial read error (stopping queue): {e}")
            return  # Stop the recursive loop

        # Loop every 100ms
        self.after(100, self.check_serial_queue)


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    main()
