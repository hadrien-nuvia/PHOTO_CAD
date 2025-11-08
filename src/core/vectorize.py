"""Vectorization module for line detection and processing."""

import cv2
import numpy as np


def detect_lines(edges, threshold=100, min_line_length=100, max_line_gap=10):
    """
    Detect lines in an edge-detected image using Hough Line Transform.

    Args:
        edges: Binary edge map from edge detection.
        threshold: Accumulator threshold parameter for line detection.
        min_line_length: Minimum line length. Line segments shorter than this are rejected.
        max_line_gap: Maximum allowed gap between points on the same line to link them.

    Returns:
        Array of detected lines, each line defined by [x1, y1, x2, y2].
    """
    lines = cv2.HoughLinesP(
        edges,
        1,
        np.pi / 180,
        threshold=threshold,
        minLineLength=min_line_length,
        maxLineGap=max_line_gap,
    )
    return lines if lines is not None else []


def simplify_lines(lines, epsilon=1.0):
    """
    Simplify line segments by removing redundant points.

    Args:
        lines: Array of line segments.
        epsilon: Approximation accuracy parameter.

    Returns:
        Simplified lines.
    """
    # For now, return lines as-is; can be extended with Douglas-Peucker algorithm
    return lines
