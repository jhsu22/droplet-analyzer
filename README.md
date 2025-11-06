# Pendant Droplet Tensiometry Analyzer

A graphical user interface (GUI) application for analyzing pendant droplets from video files to determine surface tension and other properties.

![Application Screenshot](placeholder.png)

## About The Project

This application provides a user-friendly interface to perform automated edge detection and analysis of pendant droplets from video files. It is designed for researchers and students in surface science and materials science who need to analyze droplet shapes.

The core of the application is built on Python, using OpenCV for image processing and CustomTkinter for the graphical user interface.

### Features

*   **Video Analysis:** Process video files frame by frame to analyze droplet behavior over time.
*   **Interactive GUI:** Easily adjust parameters and see the results in real-time.
*   **Advanced Edge Detection:** Utilizes Canny edge detection with tunable parameters for optimal results.
*   **Image Preprocessing:** Includes cropping, median filtering, and Gaussian blurring to improve detection accuracy.
*   **Serial Communication:** Integrated panel for connecting to and controlling hardware like syringe pumps via serial/USB.
*   **Data Export:** Export analysis results to various formats including CSV, Excel, JSON, and NPZ.

## Built With

*   [Python](https://www.python.org/)
*   [OpenCV](https://opencv.org/)
*   [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
*   [NumPy](https://numpy.org/)
*   [SciPy](https://scipy.org/)
*   [scikit-image](https://scikit-image.org/)
*   [Matplotlib](https://matplotlib.org/)
*   [Pillow](https://python-pillow.org/)

## Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

This project uses Python and `pip` for dependency management. Ensure you have Python 3.8 or newer installed.

### Installation

1.  Clone the repo
    ```sh
    git clone https://github.com/your_username/droplet-analyzer.git
    ```
2.  Navigate to the project directory
    ```sh
    cd droplet-analyzer
    ```
3.  Install Python packages
    ```sh
    pip install -r requirements.txt
    ```

## Usage

To run the application, execute the `main.py` script from the root directory of the project:

```sh
python main.py
```

### Basic Workflow

1.  **Load Video:** Click the "Video" button to load a video file containing a pendant droplet.
2.  **Adjust Parameters:**
    *   Use the "Crop Parameters" sliders to isolate the droplet in the preview window.
    *   Tune the "Filtering & Smoothing" and "Canny Edge Detection" parameters for optimal edge detection.
3.  **Start Analysis:** Click the "Start Analysis" button to begin processing the video.
4.  **View Output:** The "Output" panel will display the progress and results of the analysis.
5.  **Export Data:** Use the "Export" button to save the collected data.

## Configuration

The application's default settings are stored in `config.py`. This file contains configurations for the UI, image processing parameters, file paths, and more. While many parameters can be adjusted live through the GUI, you can modify this file to change default behaviors.

## Project Structure

*   `main.py`: The main entry point for the application.
*   `ui_builder.py`: Contains all the logic for building the CustomTkinter user interface.
*   `image_processing.py`: Handles all the image analysis tasks, including edge detection, filtering, and data extraction.
*   `config.py`: A centralized file for all application constants and default settings.
*   `popup_windows.py`: Defines the various popup windows used in the application (e.g., for settings, help, and data export).
*   `requirements.txt`: Lists all the Python dependencies for the project.

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Contact

Your Name - your_email@example.com

Project Link: [https://github.com/your_username/droplet-analyzer](https://github.com/your_username/droplet-analyzer)