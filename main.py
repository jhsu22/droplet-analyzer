"""
Pendant Droplet Analyzer - Main Application
"""

import sys
import os
import customtkinter as ctk

if sys.platform != "darwin":
    from tkextrafont import Font

from ui_builder import UIFrame
from config import UIConfig, PathConfig, processing_config
from image_processing import crop_image, calibrate

import cv2
from PIL import Image

def set_paths(self):
    # Set base paths
    self.VIDEO_PATH = PathConfig.DEFAULT_VIDEO_FILE
    self.OUTPUT_DATA_PATH = PathConfig.OUTPUT_EDGE_DATA
    self.OUTPUT_IMG_PATH = PathConfig.OUTPUT_EDGE_PLOTS
    self.OUTPUT_BINARY_PATH = PathConfig.OUTPUT_BINARY_EDGES

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

        self.is_drawing_frame = False

        # State variables
        self.video_capture = None
        self.is_playing = False
        self.is_calibrated = False
        self.num_frames = 0

        self._setup_paths()
        self._load_theme()
        self._load_fonts()
        self._configure_window()
        self._create_ui()

        # Create textbox widget
        output_textbox = self.frame.output_text
        redirector = TextboxRedirector(output_textbox)

        sys.stdout = redirector
        sys.stderr = redirector

        print("---Application Started ---")

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

        self.frame.image_panel.bind("<Configure>", lambda e: self.frame.image_label.configure)

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
        self.frame.video_slider.configure(to=self.num_frames - 1, number_of_steps=self.num_frames - 1)
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

                cropped_frame = crop_image(frame=rgb_frame, crop_params=processing_config)

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
                image_resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

                # Create CTkImage
                ctk_image = ctk.CTkImage(light_image=image_resized, dark_image=image_resized, size=(new_width, new_height))

                # Update the label
                self.frame.image_label.configure(image=ctk_image, text="")
                self.frame.image_label.image = ctk_image

                # Update slider and its label
                self.frame.video_slider.set(frame_num)
                self.frame.frame_number_label.configure(text=f"Frame {frame_num}/{int(self.num_frames - 1)}")

            else: # Video ended
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

    def start_calibration(self):
        current_frame = int(self.frame.video_slider.get())
        print(f"Starting calibration onf frame {current_frame}")

        calibration_radius = calibrate(starting_frame=current_frame, crop_params=processing_config, video=self.video_capture,
                                       OUTPUT_DATA_PATH=self.OUTPUT_DATA_PATH, OUTPUT_IMG_PATH=self.OUTPUT_IMG_PATH)

        self.is_calibrated = True
        self.frame.start_analysis_button.configure(state="normal")
        print("Calibration complete. Ready to start analysis.")

    def start_analysis(self):
        if not self.is_calibrated:
            print("Run calibration before analysis.")
            return

        print("Starting analysis.")
        self.is_playing = True
        self.update_video()

    def update_video(self):
        if not self.is_playing:
            return

        current_frame = int(self.frame.video_slider.get())
        if current_frame < self.num_frames - 1:
            next_frame = current_frame + 1
            self.show_frame(next_frame)

            self.after(15, self.update_video)
        else:
            print("Analysis complete.")
            self.is_playing = False

def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    main()