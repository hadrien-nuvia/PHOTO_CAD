import unittest
from src.core.dxf_export import export_to_dxf

class TestDxfExport(unittest.TestCase):

    def setUp(self):
        self.test_lines = [
            [(0, 0), (1, 1)],
            [(1, 1), (2, 2)],
            [(2, 2), (3, 3)]
        ]
        self.output_file = 'test_output.dxf'

    def test_export_to_dxf(self):
        result = export_to_dxf(self.test_lines, self.output_file)
        self.assertTrue(result)
        # Additional checks can be added here to verify the contents of the DXF file

    def tearDown(self):
        import os
        if os.path.exists(self.output_file):
            os.remove(self.output_file)

if __name__ == '__main__':
    unittest.main()