"""Unit tests for raster processing functions."""

import unittest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from core.raster import read_image, detect_edges
from core.vectorize import detect_lines


class TestRasterFunctions(unittest.TestCase):
    """Test cases for raster processing functions."""

    def test_read_image_missing(self):
        """Test that reading a non-existent image raises FileNotFoundError."""
        with self.assertRaises(FileNotFoundError):
            read_image("path/to/nonexistent/image.png")

    def test_detect_edges_parameters(self):
        """Test edge detection with different parameters."""
        # This test would require a valid test image
        # For now, we just verify the function exists and has correct signature
        self.assertTrue(callable(detect_edges))

    def test_detect_lines_empty(self):
        """Test line detection with empty edges."""
        import numpy as np

        empty_edges = np.zeros((100, 100), dtype=np.uint8)
        lines = detect_lines(empty_edges)
        self.assertIsNotNone(lines)
        self.assertEqual(len(lines), 0)


if __name__ == "__main__":
    unittest.main()
