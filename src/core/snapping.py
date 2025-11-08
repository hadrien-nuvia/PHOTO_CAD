"""Snapping utilities for aligning lines to grids and angles."""

import numpy as np


def snap_to_grid(lines, grid_size):
    """
    Snap line endpoints to a grid.

    Args:
        lines: List of lines, where each line is a list of points [(x, y), ...].
        grid_size: Size of the grid cell.

    Returns:
        Lines with endpoints snapped to the grid.
    """
    snapped_lines = []
    for line in lines:
        snapped_line = []
        for point in line:
            snapped_point = (
                round(point[0] / grid_size) * grid_size,
                round(point[1] / grid_size) * grid_size,
            )
            snapped_line.append(snapped_point)
        snapped_lines.append(snapped_line)
    return snapped_lines


def snap_to_angles(lines, snap_angle=15):
    """
    Snap lines to dominant angles.

    Args:
        lines: Array of lines in format [[x1, y1, x2, y2], ...].
        snap_angle: Angle increment in degrees to snap to.

    Returns:
        Lines with angles snapped to multiples of snap_angle.
    """
    snapped_lines = []
    for line in lines:
        for x1, y1, x2, y2 in line:
            # Calculate current angle
            angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
            # Snap to nearest angle
            snapped_angle = round(angle / snap_angle) * snap_angle
            # Calculate new endpoint
            length = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            x2_new = x1 + length * np.cos(np.radians(snapped_angle))
            y2_new = y1 + length * np.sin(np.radians(snapped_angle))
            snapped_lines.append((x1, y1, int(x2_new), int(y2_new)))
    return snapped_lines


def snap_lines(lines, snap_angle=15, grid_size=None):
    """
    Snap lines to angles and optionally to a grid.

    Args:
        lines: Array of lines in format [[x1, y1, x2, y2], ...].
        snap_angle: Angle increment in degrees to snap to.
        grid_size: Optional grid size for grid snapping.

    Returns:
        Snapped lines.
    """
    # First snap to angles
    snapped = snap_to_angles(lines, snap_angle)

    # Optionally snap to grid
    if grid_size is not None:
        # Convert to point format for grid snapping
        lines_as_points = [[(x1, y1), (x2, y2)] for x1, y1, x2, y2 in snapped]
        snapped_grid = snap_to_grid(lines_as_points, grid_size)
        # Convert back to line format
        snapped = [(p1[0], p1[1], p2[0], p2[1]) for p1, p2 in snapped_grid]

    return snapped
