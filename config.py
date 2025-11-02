"""
Configuration file
Contains all constants and default values used throughout the application
"""

from pathlib import Path


class UIConfig:
    """UI-related configuration constants"""

    # Window settings
    WINDOW_TITLE = "Pendant Droplet Analyzer"
    WINDOW_WIDTH = 900
    WINDOW_HEIGHT = 600
    WINDOW_GEOMETRY = f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"

    # Font settings
    FONT_FAMILY = "JetBrains Mono"
    FONT_SIZE_NORMAL = 14
    FONT_SIZE_TITLE = 14

    # Colors
    COLOR_BG_PRIMARY = '#1e1e2e'
    COLOR_BG_SECONDARY = '#181825'
    COLOR_BORDER = '#45475a'
    COLOR_TEXT_PRIMARY = '#cdd6f4'
    COLOR_TEXT_ACCENT = '#cba6f7'
    COLOR_STATUS_CONNECTED = '#63cf65'
    COLOR_STATUS_DISCONNECTED = '#e64c4c'

    # Layout settings
    PADDING_SMALL = 5
    PADDING_MEDIUM = 10
    PADDING_LARGE = 15

    # Header settings
    HEADER_TITLE = "[PENDANT DROPLET ANALYZER] CONTROLS"
    HEADER_BORDER_WIDTH = 2

    # Button settings
    BUTTON_WIDTH = 50
    BUTTON_HEIGHT = 30
    BUTTON_CORNER_RADIUS = 0
    START_BUTTON_HEIGHT = 35

    # Panel titles
    PANEL_TITLE_IMAGE = "IMAGE"
    PANEL_TITLE_PARAMETERS = "PARAMETERS"
    PANEL_TITLE_SERIAL = "SERIAL"
    PANEL_TITLE_OUTPUT = "OUTPUT"

    # Grid weights (for layout proportions)
    GRID_WEIGHT_IMAGE = 8
    GRID_WEIGHT_PARAMETERS = 7
    GRID_WEIGHT_SERIAL = 6


class ProcessingConfig:
    """Image processing configuration constants"""

    # Default crop parameters (for 1920x1080 video)
    DEFAULT_CROP = {
        'initial_x_crop': 445,
        'initial_y_crop': 88,
        'x_max': 1160,
        'y_max': 932
    }

    # Default Canny edge detection parameters
    DEFAULT_FILTER_SIZE = 3
    DEFAULT_CANNY_LOW = 25
    DEFAULT_CANNY_HIGH = 51
    DEFAULT_MIN_OBJECT_SIZE = 100
    DEFAULT_SIGMA = 3.0

    # Calibration frame parameters
    CALIBRATION_FILTER_SIZE = 15
    CALIBRATION_CANNY_LOW = 25
    CALIBRATION_CANNY_HIGH = 51
    CALIBRATION_MIN_OBJECT_SIZE = 100

    # Edge detection thresholds
    MIN_EDGE_POINTS = 5

    # Video processing
    DEFAULT_STARTING_FRAME = 5
    DEFAULT_ENDING_FRAME = 545
    CALIBRATION_FRAME_OFFSET = 1

    # Progress reporting
    PROGRESS_REPORT_INTERVAL = 50  # Report every N frames


class SliderConfig:
    """Configuration for UI parameter sliders"""

    # Crop parameter ranges (for 1920x1080 video)
    X_MIN = 0
    X_MAX = 1920
    X_STEPS = 1920

    Y_MIN = 0
    Y_MAX = 1080
    Y_STEPS = 1080

    # Filter size range
    FILTER_MIN = 1
    FILTER_MAX = 25
    FILTER_STEPS = 12

    # Canny threshold ranges
    CANNY_MIN = 0
    CANNY_MAX = 255
    CANNY_STEPS = 255

    # Min object size range
    MIN_OBJ_MIN = 0
    MIN_OBJ_MAX = 500
    MIN_OBJ_STEPS = 500

    # Sigma range
    SIGMA_MIN = 1.0
    SIGMA_MAX = 4.0
    SIGMA_STEPS = 100

    # Slider label width
    VALUE_LABEL_WIDTH = 50


class SerialConfig:
    """Serial communication configuration"""

    # Default device name
    DEFAULT_DEVICE_NAME = "Arduino UNO R3"

    # Available COM ports (Windows)
    DEFAULT_PORTS = ["COM1", "COM2", "COM3", "COM4", "COM5", "COM6"]
    DEFAULT_PORT = "COM1"

    # Available baud rates
    BAUD_RATES = ["9600", "19200", "38400", "57600", "115200"]
    DEFAULT_BAUD_RATE = "9600"

    # Serial communication settings
    TIMEOUT = 1  # seconds

    # Status messages
    STATUS_CONNECTED = "● Connected"
    STATUS_DISCONNECTED = "● Disconnected"

    # Output placeholder
    OUTPUT_PLACEHOLDER = "No output yet"


class PathConfig:
    """Path configuration for file operations"""

    # Base paths
    BASE_PATH = Path(__file__).parent
    ASSETS_PATH = BASE_PATH / "assets"
    OUTPUT_PATH = BASE_PATH / "output"
    TEST_DATA_PATH = BASE_PATH / "test_data"

    # Asset subdirectories
    FONTS_PATH = ASSETS_PATH / "fonts"
    IMAGES_PATH = ASSETS_PATH / "images"
    THEMES_PATH = ASSETS_PATH / "themes"

    # Specific asset files
    FONT_FILE = FONTS_PATH / "JetBrainsMono.ttf"
    THEME_FILE = THEMES_PATH / "terminal_dark.json"

    # Output subdirectories
    OUTPUT_EDGE_DATA = OUTPUT_PATH / "edge_data"
    OUTPUT_EDGE_PLOTS = OUTPUT_PATH / "edge_plots"
    OUTPUT_BINARY_EDGES = OUTPUT_PATH / "binary_edges"

    # Default video file
    DEFAULT_VIDEO_FILE = TEST_DATA_PATH / "test_video_2.mov"

    @classmethod
    def create_output_directories(cls):
        """Create all output directories if they don't exist"""
        cls.OUTPUT_EDGE_DATA.mkdir(parents=True, exist_ok=True)
        cls.OUTPUT_EDGE_PLOTS.mkdir(parents=True, exist_ok=True)
        cls.OUTPUT_BINARY_EDGES.mkdir(parents=True, exist_ok=True)


class PlotConfig:
    """Configuration for matplotlib plots"""

    # Figure settings
    FIGURE_WIDTH = 10
    FIGURE_HEIGHT = 8
    FIGURE_DPI = 300

    # Plot settings
    COLORMAP = 'gray'
    EDGE_POINT_COLOR = 'blue'
    EDGE_POINT_MARKER = '.'
    EDGE_POINT_SIZE = 2
    EDGE_POINT_ALPHA = 0.6

    # Plot labels
    PLOT_TITLE = "Edge Detection"


class PopupConfig:
    """Configuration for popup windows"""

    # Popup dimensions
    VIDEO_POPUP_WIDTH = 600
    VIDEO_POPUP_HEIGHT = 400

    VIEWDATA_POPUP_WIDTH = 800
    VIEWDATA_POPUP_HEIGHT = 600

    EXPORT_POPUP_WIDTH = 500
    EXPORT_POPUP_HEIGHT = 450

    SETTINGS_POPUP_WIDTH = 700
    SETTINGS_POPUP_HEIGHT = 500

    HELP_POPUP_WIDTH = 650
    HELP_POPUP_HEIGHT = 550

    # Export formats
    EXPORT_FORMATS = ["CSV", "Excel (XLSX)", "JSON", "NumPy (NPZ)"]
    DEFAULT_EXPORT_FORMAT = "CSV"

    # Settings categories (tabs)
    SETTINGS_TABS = ["Processing", "UI Settings", "File Paths"]

    # Help text content
    HELP_TEXT = """PENDANT DROPLET ANALYZER - HELP

OVERVIEW
This application performs automated edge detection and analysis of pendant droplets from video files.

WORKFLOW
1. Click 'Video' to load a video file
2. Adjust crop parameters to select the droplet region
3. Tune Canny edge detection parameters for optimal edge detection
4. Click 'Start Analysis' to process the video
5. View results in the Output panel
6. Export data using the 'Export' button

PARAMETERS

Crop Parameters:
- X Start/Y Start: Top-left corner of crop region
- X End/Y End: Bottom-right corner of crop region

Canny Parameters:
- Filter Size: Median filter kernel size (odd numbers, 1-25)
- Canny Low: Lower threshold for edge detection (0-255)
- Canny High: Upper threshold for edge detection (0-255)
- Min Object Size: Minimum size of detected objects in pixels
- Sigma: Gaussian blur sigma value (1.0-4.0)

SERIAL CONNECTION
Connect to Arduino or other serial devices for hardware integration:
- Select the correct COM port
- Set the appropriate baud rate
- Send commands via the command box

KEYBOARD SHORTCUTS
- Ctrl+O: Open video file
- Ctrl+E: Export data
- Ctrl+S: Open settings
- F1: Show help

TIPS
- Start with default parameters and adjust incrementally
- Use calibration frame to test parameter settings
- Export data regularly to avoid loss
- Check serial connection status before sending commands

Version: 1.0.0
"""


class AppConfig:
    """Main application configuration"""

    # Application metadata
    APP_NAME = "Pendant Droplet Analyzer"
    APP_VERSION = "1.0.0"

    # Debug settings
    DEBUG_MODE = False
    VERBOSE_LOGGING = False

    # Performance settings
    MAX_FRAME_BUFFER = 100  # Maximum frames to keep in memory


# Convenience function to get all config as dictionary
def get_all_configs():
    """Returns all configuration classes as a dictionary"""
    return {
        'ui': UIConfig,
        'processing': ProcessingConfig,
        'sliders': SliderConfig,
        'serial': SerialConfig,
        'paths': PathConfig,
        'plots': PlotConfig,
        'popups': PopupConfig,
        'app': AppConfig
    }


# Convenience function to get slider parameters
def get_slider_params():
    """Returns dictionary of slider parameters for UI creation"""
    return {
        'x_start': {
            'from_': SliderConfig.X_MIN,
            'to': SliderConfig.X_MAX,
            'number_of_steps': SliderConfig.X_STEPS,
            'default': ProcessingConfig.DEFAULT_CROP['initial_x_crop']
        },
        'y_start': {
            'from_': SliderConfig.Y_MIN,
            'to': SliderConfig.Y_MAX,
            'number_of_steps': SliderConfig.Y_STEPS,
            'default': ProcessingConfig.DEFAULT_CROP['initial_y_crop']
        },
        'x_end': {
            'from_': SliderConfig.X_MIN,
            'to': SliderConfig.X_MAX,
            'number_of_steps': SliderConfig.X_STEPS,
            'default': ProcessingConfig.DEFAULT_CROP['x_max']
        },
        'y_end': {
            'from_': SliderConfig.Y_MIN,
            'to': SliderConfig.Y_MAX,
            'number_of_steps': SliderConfig.Y_STEPS,
            'default': ProcessingConfig.DEFAULT_CROP['y_max']
        },
        'filter_size': {
            'from_': SliderConfig.FILTER_MIN,
            'to': SliderConfig.FILTER_MAX,
            'number_of_steps': SliderConfig.FILTER_STEPS,
            'default': ProcessingConfig.DEFAULT_FILTER_SIZE
        },
        'canny_low': {
            'from_': SliderConfig.CANNY_MIN,
            'to': SliderConfig.CANNY_MAX,
            'number_of_steps': SliderConfig.CANNY_STEPS,
            'default': ProcessingConfig.DEFAULT_CANNY_LOW
        },
        'canny_high': {
            'from_': SliderConfig.CANNY_MIN,
            'to': SliderConfig.CANNY_MAX,
            'number_of_steps': SliderConfig.CANNY_STEPS,
            'default': ProcessingConfig.DEFAULT_CANNY_HIGH
        },
        'min_object_size': {
            'from_': SliderConfig.MIN_OBJ_MIN,
            'to': SliderConfig.MIN_OBJ_MAX,
            'number_of_steps': SliderConfig.MIN_OBJ_STEPS,
            'default': ProcessingConfig.DEFAULT_MIN_OBJECT_SIZE
        },
        'sigma': {
            'from_': SliderConfig.SIGMA_MIN,
            'to': SliderConfig.SIGMA_MAX,
            'number_of_steps': SliderConfig.SIGMA_STEPS,
            'default': ProcessingConfig.DEFAULT_SIGMA
        }
    }
