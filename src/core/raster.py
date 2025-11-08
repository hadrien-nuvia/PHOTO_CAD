"""Raster image processing module for orthophoto conversion."""

import cv2
import numpy as np


def read_image(image_path):
    """
    Read an image from the specified path.
    
    Args:
        image_path: Path to the input image file.
        
    Returns:
        Loaded image as numpy array.
        
    Raises:
        FileNotFoundError: If the image file doesn't exist.
    """
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Image not found at {image_path}")
    return image


def convert_to_grayscale(image):
    """
    Convert an image to grayscale.
    
    Args:
        image: Input image as numpy array.
        
    Returns:
        Grayscale image.
    """
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def detect_edges(image, low_threshold=50, high_threshold=150):
    """
    Detect edges in an image using Canny edge detection.
    
    Args:
        image: Input image (grayscale or color).
        low_threshold: Lower threshold for Canny edge detection.
        high_threshold: Upper threshold for Canny edge detection.
        
    Returns:
        Binary edge map.
    """
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image
    
    edges = cv2.Canny(gray, low_threshold, high_threshold, apertureSize=3)
    return edges