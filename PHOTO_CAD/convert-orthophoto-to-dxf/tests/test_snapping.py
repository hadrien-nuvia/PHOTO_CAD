import unittest
from src.core.snapping import snap_lines

class TestSnapping(unittest.TestCase):

    def test_snap_to_grid(self):
        lines = [(1.1, 2.2), (3.5, 4.7)]
        grid_size = 1.0
        expected = [(1.0, 2.0), (4.0, 5.0)]
        result = snap_lines(lines, grid_size)
        self.assertEqual(result, expected)

    def test_snap_to_angle(self):
        lines = [(1.0, 1.0), (2.0, 2.0)]
        angle = 45
        expected = [(1.0, 1.0), (2.0, 2.0)]  # Assuming no change for this example
        result = snap_lines(lines, angle=angle)
        self.assertEqual(result, expected)

    def test_empty_lines(self):
        lines = []
        grid_size = 1.0
        expected = []
        result = snap_lines(lines, grid_size)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()