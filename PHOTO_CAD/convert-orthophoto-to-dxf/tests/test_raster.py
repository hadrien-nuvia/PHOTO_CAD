import unittest
from src.core.raster import read_image, convert_to_grayscale
from src.core.vectorize import detect_edges, vectorize_lines

class TestRasterFunctions(unittest.TestCase):

    def test_read_image(self):
        image = read_image('path/to/test/image.png')
        self.assertIsNotNone(image)
        self.assertEqual(image.shape[2], 3)  # Assuming the image has 3 channels (RGB)

    def test_convert_to_grayscale(self):
        image = read_image('path/to/test/image.png')
        gray_image = convert_to_grayscale(image)
        self.assertEqual(gray_image.shape[2], 1)  # Grayscale image should have 1 channel

    def test_detect_edges(self):
        image = read_image('path/to/test/image.png')
        edges = detect_edges(image)
        self.assertIsNotNone(edges)

    def test_vectorize_lines(self):
        image = read_image('path/to/test/image.png')
        edges = detect_edges(image)
        lines = vectorize_lines(edges)
        self.assertIsInstance(lines, list)  # Assuming the output is a list of lines

if __name__ == '__main__':
    unittest.main()