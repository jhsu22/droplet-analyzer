"""
Image Analysis Script

Takes a video file and performs canny edge detection on every frame to get the edge of the droplet
"""

import numpy as np
import cv2
import matplotlib.pyplot as plt
import skimage as ski
import os

from config import ProcessingConfig, PathConfig, PlotConfig, processing_config
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

    # Crop image
    initial_x_crop = int(crop_params.x_start)
    initial_y_crop = int(crop_params.y_start)
    x_max = int(crop_params.x_end)
    y_max = int(crop_params.y_end)

    imgcrop = frame[initial_y_crop:y_max, initial_x_crop:x_max]

    return imgcrop

def process_frame_edge(frame, crop_params,
                       filter_size=processing_config.filter_size,
                       canny_low=processing_config.canny_low,
                       canny_high=processing_config.canny_high,
                       min_object_size=processing_config.min_object_size,
                       min_size_mult=processing_config.min_size_mult,
                       sigma=processing_config.sigma,
                       adaptive_threshold=True,
                       calibration_radius=None):
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

    imgcrop_color = crop_image(frame, crop_params)

    imgcrop = cv2.cvtColor(imgcrop_color, cv2.COLOR_BGR2GRAY)

    # Apply a median filter to the image to smooth noise
    im_med = cv2.medianBlur(imgcrop, filter_size)

    # Apply a gaussian blur to smooth edges
    im_gaussian = cv2.GaussianBlur(im_med, (5, 5), sigma)

    # Find edges using canny
    edges = cv2.Canny(im_gaussian, canny_low, canny_high, apertureSize=3)

    # First pass of cleaning noise using bweareaopen
    clean_pass1 = bwareaopen(edges, min_object_size)

    # Extract edge point coordinates from first pass
    pass1_points = extract_edge_points(clean_pass1)

    # Dynamically calculated min object size for pass 2
    min_size_adapted = np.floor(len(pass1_points) * min_size_mult)

    # Second pass of cleaning noise using bweareaopen
    clean_edges = bwareaopen(clean_pass1, min_size_adapted)

    # Extract edge point coordinates from second
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

def calibrate(starting_frame, crop_params, video, OUTPUT_DATA_PATH, OUTPUT_IMG_PATH):

    # Calibration frame parameters
    calibration_params = {
        'filter_size': ProcessingConfig.CALIBRATION_FILTER_SIZE,
        'canny_low': ProcessingConfig.CALIBRATION_CANNY_LOW,
        'canny_high': ProcessingConfig.CALIBRATION_CANNY_HIGH,
        'min_object_size': ProcessingConfig.CALIBRATION_MIN_OBJECT_SIZE,
        'adaptive_threshold': False
    }

    # Read calibration frame
    calib_frame_num = starting_frame + ProcessingConfig.CALIBRATION_FRAME_OFFSET
    video.set(cv2.CAP_PROP_POS_FRAMES, calib_frame_num)
    ret, frame = video.read()

    if not ret:
        print("Error reading calibration frame.")

    # Process calibration frame
    calibration_results = process_frame_edge(frame, crop_params, sigma=5, **calibration_params)

    # Calculate centroid and average radius from edge points
    calibration_edge_points = calibration_results['edge_points']
    if len(calibration_edge_points) > 0:
        calibration_center_x = np.mean(calibration_edge_points[:, 0])
        calibration_center_y = np.mean(calibration_edge_points[:, 1])
        distances_from_center = np.sqrt((calibration_edge_points[:, 0] - calibration_center_x) ** 2,
                                        (calibration_edge_points[:, 1] - calibration_center_y) ** 2)
        calibration_radius = np.mean(distances_from_center)
        print(f"  Calibration frame average radius: {calibration_radius:.2f} pixels")
    else:
        calibration_center_x = 0
        calibration_center_y = 0
        calibration_radius = 0
        print(f"  No edge points detected in calibration frame. Average radius set to 0.")

    print(f"  Frame {calib_frame_num}: {calibration_results['num_edge_points']} edge points detected")

    # Save calibration edge data
    np.savez(OUTPUT_DATA_PATH / f"calibration_frame_{calib_frame_num}.npz",
             edge_points=calibration_results['edge_points'],
             frame_number=calib_frame_num)

    # Plot calibration frame
    fig = plot_edge_points(calibration_results['cropped_image'], calibration_results['edge_points'])
    fig.savefig(OUTPUT_IMG_PATH / f"calibration_frame_{calib_frame_num}.png", dpi=PlotConfig.FIGURE_DPI)
    plt.close(fig)

    return calibration_radius

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
    calibration_radius = calibrate(starting_frame, crop_params, video, OUTPUT_DATA_PATH, OUTPUT_IMG_PATH)

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
        results = process_frame_edge(frame, crop_params, **canny_params, calibration_radius=calibration_radius)

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