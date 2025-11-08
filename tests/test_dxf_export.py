"""Unit tests for DXF export functionality."""

import unittest
import sys
import os
import tempfile

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.dxf_export import export_to_dxf, export_to_geojson


class TestDxfExport(unittest.TestCase):
    """Test cases for DXF and GeoJSON export functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_lines = [
            (0, 0, 10, 10),
            (10, 10, 20, 20),
            (20, 20, 30, 30)
        ]
        # Use temporary directory for output files
        self.temp_dir = tempfile.mkdtemp()
        self.dxf_output = os.path.join(self.temp_dir, 'test_output.dxf')
        self.geojson_output = os.path.join(self.temp_dir, 'test_output.geojson')

    def test_export_to_dxf(self):
        """Test DXF export functionality."""
        export_to_dxf(self.test_lines, self.dxf_output)
        self.assertTrue(os.path.exists(self.dxf_output))
        # Check file is not empty
        self.assertGreater(os.path.getsize(self.dxf_output), 0)

    def test_export_to_geojson(self):
        """Test GeoJSON export functionality."""
        export_to_geojson(self.test_lines, self.geojson_output)
        self.assertTrue(os.path.exists(self.geojson_output))
        # Check file is not empty
        self.assertGreater(os.path.getsize(self.geojson_output), 0)
        
        # Verify JSON structure
        import json
        with open(self.geojson_output, 'r') as f:
            data = json.load(f)
            self.assertEqual(data['type'], 'FeatureCollection')
            self.assertEqual(len(data['features']), len(self.test_lines))

    def test_export_empty_lines(self):
        """Test exporting with empty line list."""
        empty_lines = []
        export_to_dxf(empty_lines, self.dxf_output)
        self.assertTrue(os.path.exists(self.dxf_output))

    def tearDown(self):
        """Clean up test files."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)


if __name__ == '__main__':
    unittest.main()