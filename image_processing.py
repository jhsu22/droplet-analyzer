"""
Image Analysis Script

Takes a video file and performs canny edge detection on every frame to get the edge of the droplet
"""

import numpy as np
import cv2
import matplotlib.pyplot as plt
import skimage as ski
import os

from config import ProcessingConfig, PathConfig, PlotConfig
from popup_windows import VideoPopup

def bwareaopen(binary_image, min_size):
    """
    Remove small objects from a binary image
    (equivalent of MATLAB bwareopen using skimage.morphology)

    :param binary_image: ndarray of binary image
    :param min_size: minimum size of object to keep (int)
    :return: ndarray of binary image with small objects removed
    """

    binary_bool = binary_image.astype(bool)
    cleaned = ski.morphology.remove_small_objects(binary_bool, min_size=min_size)
    return cleaned.astype(np.uint8) * 255

def extract_edge_points(binary_image):
    """
    Extract edge points from a binary image

    :param binary_image: Binary image with edges marked as white pixels (ndarray)

    :return: edge_points (ndarray) of (x, y) coordinates of edges
    """

    row, col = np.nonzero(binary_image)
    edge_points = np.column_stack((col, row))

    return edge_points

def crop_image(frame, crop_params):
    """
    Crop the image to the specified parameters (define in ui)

    :param frame: Input frame (ndarray)
    :param crop_params: Dictionary with crop parameters

    :return: Cropped image (ndarray)
    """

    # Convert to grayscale
    video_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Crop image
    initial_x_crop = crop_params['initial_x_crop']
    initial_y_crop = crop_params['initial_y_crop']
    x_max = crop_params['x_max']
    y_max = crop_params['y_max']

    imgcrop = video_gray[initial_y_crop:y_max, initial_x_crop:x_max]

    return imgcrop

def process_frame_edge(frame, crop_params,
                       filter_size=ProcessingConfig.DEFAULT_FILTER_SIZE,
                       canny_low=ProcessingConfig.DEFAULT_CANNY_LOW,
                       canny_high=ProcessingConfig.DEFAULT_CANNY_HIGH,
                       min_object_size=ProcessingConfig.DEFAULT_MIN_OBJECT_SIZE,
                       adaptive_threshold=True):
    """
    Performs edge detection for a single frame

    :param frame: Input frame (ndarray)
    :param crop_params: Dictionary with crop parameters
    :param filter_size: Median filter size (int, odd)
    :param canny_low: Lower canny threshold (0-255)
    :param canny_high: Upper canny threshold (0-255)
    :param min_object_size: Minimum size of objects to keep (pixels)
    :param adaptive_threshold: Whether to use adaptive thresholding

    :return: Dictionary containing:
             cropped image, filtered image, binary edge image, edge coordinates, and number of edge points
    """

    imgcrop = crop_image(frame, crop_params)

    # Apply a median filter to the image to smooth noise
    im_med = cv2.medianBlur(imgcrop, filter_size)

    # Find edges using canny
    edges = cv2.Canny(im_med, canny_low, canny_high, apertureSize=3)

    # Clean noise using bweareaopen (scikit-image morphology)
    clean_edges = bwareaopen(edges, min_object_size)

    # Extract edge point coordinates
    edge_points = extract_edge_points(clean_edges)

    results = {
        'cropped_image': imgcrop,
        'filtered_image': im_med,
        'binary_edge_image': clean_edges,
        'edge_points': edge_points,
        'num_edge_points': len(edge_points)
    }

    return results

def plot_edge_points(cropped_image, edge_points):
    """
    Plots detected edge points on top of original image

    :param cropped_image: Grayscale cropped image (ndarray)
    :param edge_points: Edge points (ndarray)

    :return: matplotlib figure
    """

    fig, ax = plt.subplots(figsize=(PlotConfig.FIGURE_WIDTH, PlotConfig.FIGURE_HEIGHT))
    ax.imshow(cropped_image, cmap=PlotConfig.COLORMAP)

    if len(edge_points) > 0:
        ax.plot(edge_points[:, 0], edge_points[:, 1],
                color=PlotConfig.EDGE_POINT_COLOR,
                marker=PlotConfig.EDGE_POINT_MARKER,
                linestyle='none',
                markersize=PlotConfig.EDGE_POINT_SIZE,
                alpha=PlotConfig.EDGE_POINT_ALPHA)

    ax.set_title(PlotConfig.PLOT_TITLE)
    ax.axis('off')

    return fig

def main():

    # Set base paths
    VIDEO_PATH = PathConfig.DEFAULT_VIDEO_FILE
    OUTPUT_DATA_PATH = PathConfig.OUTPUT_EDGE_DATA
    OUTPUT_IMG_PATH = PathConfig.OUTPUT_EDGE_PLOTS
    OUTPUT_BINARY_PATH = PathConfig.OUTPUT_BINARY_EDGES

    # Create output directories if they don't exist
    PathConfig.create_output_directories()

    # Image crop parameters
    crop_params = ProcessingConfig.DEFAULT_CROP

    # Edge detection parameters
    canny_params = {
        'filter_size': ProcessingConfig.DEFAULT_FILTER_SIZE,
        'canny_low': ProcessingConfig.DEFAULT_CANNY_LOW,
        'canny_high': ProcessingConfig.DEFAULT_CANNY_HIGH,
        'min_object_size': ProcessingConfig.DEFAULT_MIN_OBJECT_SIZE,
        'adaptive_threshold': True
    }

    # Calibration frame parameters
    calibration_params = {
        'filter_size': ProcessingConfig.CALIBRATION_FILTER_SIZE,
        'canny_low': ProcessingConfig.CALIBRATION_CANNY_LOW,
        'canny_high': ProcessingConfig.CALIBRATION_CANNY_HIGH,
        'min_object_size': ProcessingConfig.CALIBRATION_MIN_OBJECT_SIZE,
        'adaptive_threshold': False
    }

    # Check if video path exists
    if not os.path.exists(VIDEO_PATH):
        print(f"{VIDEO_PATH} does not exist.")
        print("Place video path in 'test_data' as 'test_video.mov'")
        return

    # Open video
    video = cv2.VideoCapture(str(VIDEO_PATH))

    # Get video properties
    video_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    video_fps = video.get(cv2.CAP_PROP_FPS)
    num_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

    # Set frame range to process
    starting_frame = ProcessingConfig.DEFAULT_STARTING_FRAME
    ending_frame = ProcessingConfig.DEFAULT_ENDING_FRAME
    frame_range = ending_frame - starting_frame

    # Calibration frame
    # Read calibration frame
    calib_frame_num = starting_frame + ProcessingConfig.CALIBRATION_FRAME_OFFSET
    video.set(cv2.CAP_PROP_POS_FRAMES, calib_frame_num)
    ret, frame = video.read()

    if not ret:
        print("Error reading calibration frame.")

    # Process calibration frame
    calibration_results = process_frame_edge(frame, crop_params, **calibration_params)

    print(f"  Frame {calib_frame_num}: {calibration_results['num_edge_points']} edge points detected")

    # Save calibration edge data
    np.savez(OUTPUT_DATA_PATH / f"calibration_frame_{calib_frame_num}.npz",
             edge_points=calibration_results['edge_points'],
             frame_number=calib_frame_num)

    # Plot calibration frame
    fig = plot_edge_points(calibration_results['cropped_image'], calibration_results['edge_points'])
    fig.savefig(OUTPUT_IMG_PATH / f"calibration_frame_{calib_frame_num}.png", dpi=PlotConfig.FIGURE_DPI)
    plt.close(fig)

    # Process all the frames

    frame_data = []
    processed_count = 0
    skipped_count = 0

    # Discard bad frames in the beginning
    for i in range(ProcessingConfig.DEFAULT_STARTING_FRAME, frame_range):
        frame_num = starting_frame + i

        if frame_num >= num_frames:
            break

        # Read frame
        video.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = video.read()

        if not ret:
            print(f"Error reading frame {frame_num}. Skipping.")
            skipped_count += 1
            continue

        # Process frame
        results = process_frame_edge(frame, crop_params, **canny_params)

        # Check edge point count
        if results['num_edge_points'] < ProcessingConfig.MIN_EDGE_POINTS:
            print(f"Insufficient edge points detected for frame {frame_num}. Skipping.")
            skipped_count += 1
            continue

        # Save edge data
        np.savez(OUTPUT_DATA_PATH / f"frame_{frame_num}.npz",
                 edge_points=results['edge_points'],
                 frame_number=frame_num,
                 frame_index=i)

        # Plot frame
        fig = plot_edge_points(results['cropped_image'], results['edge_points'])
        fig.savefig(OUTPUT_IMG_PATH / f"frame_{frame_num}.png", dpi=PlotConfig.FIGURE_DPI)
        plt.close(fig)

        # Save binary edge image
        cv2.imwrite(str(OUTPUT_BINARY_PATH / f"frame_{frame_num}.png"), results['binary_edge_image'])

        # Store summary data
        frame_data.append({
            'frame_number': frame_num,
            'num_edge_points': results['num_edge_points']
        })

        processed_count += 1

        if processed_count % ProcessingConfig.PROGRESS_REPORT_INTERVAL == 0:
            print(f"Processed {processed_count} frames...")

    video.release()

    print(f"\nProcessing complete!")
    print(f"Total frames processed: {processed_count}")
    print(f"Frames skipped: {skipped_count}")


if __name__ == "__main__":
    main()