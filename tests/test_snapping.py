"""Unit tests for snapping functions."""

import unittest
import sys
import os
import numpy as np

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.snapping import snap_to_grid, snap_to_angles, snap_lines


class TestSnapping(unittest.TestCase):
    """Test cases for line snapping functions."""

    def test_snap_to_grid(self):
        """Test grid snapping functionality."""
        lines = [[(1.1, 2.2), (3.5, 4.7)]]
        grid_size = 1.0
        result = snap_to_grid(lines, grid_size)
        self.assertEqual(len(result), 1)
        # Check that points are snapped to grid
        for line in result:
            for point in line:
                self.assertEqual(point[0] % grid_size, 0)
                self.assertEqual(point[1] % grid_size, 0)

    def test_snap_to_angles(self):
        """Test angle snapping functionality."""
        # Create a simple line
        lines = np.array([[[0, 0, 100, 100]]])
        snap_angle = 45
        result = snap_to_angles(lines, snap_angle)
        self.assertIsNotNone(result)
        self.assertTrue(len(result) > 0)

    def test_snap_to_grid_empty(self):
        """Test grid snapping with empty input."""
        lines = []
        grid_size = 1.0
        result = snap_to_grid(lines, grid_size)
        self.assertEqual(result, [])

    def test_snap_lines_integration(self):
        """Test combined snapping functionality."""
        lines = np.array([[[0, 0, 10, 10]]])
        result = snap_lines(lines, snap_angle=15)
        self.assertIsNotNone(result)
        self.assertTrue(len(result) > 0)


if __name__ == '__main__':
    unittest.main()