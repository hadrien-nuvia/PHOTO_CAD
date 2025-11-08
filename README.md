# Convert Orthophoto to DXF

A Python tool for converting orthophoto images to DXF (Drawing Exchange Format) files using image processing and vectorization techniques. This tool detects lines in orthophotos, applies angle snapping for cleaner CAD drawings, and exports the results to DXF and optionally GeoJSON formats.

## Features

- **Image Processing**: Reads and processes orthophoto images
- **Edge Detection**: Uses Canny edge detection to identify features
- **Line Detection**: Employs Hough Line Transform for line extraction
- **Angle Snapping**: Snaps detected lines to dominant angles for cleaner CAD drawings
- **Multiple Output Formats**: Exports to both DXF and GeoJSON formats
- **Configurable Parameters**: Customizable detection and snapping parameters
- **GUI Application**: User-friendly graphical interface for easy conversions
- **Standalone Executable**: Pre-built executables available for Windows, Linux, and macOS

## Installation

### Using Pre-built Executables (Recommended)

Download the latest standalone executable for your platform from the [Releases](https://github.com/hadrien-nuvia/PHOTO_CAD/releases) page:
- **Windows**: `OrthophotoToDXF.exe`
- **Linux**: `OrthophotoToDXF`
- **macOS**: `OrthophotoToDXF`

No Python installation required! Just download and run the executable.

### From Source

#### Prerequisites

- Python 3.8 or higher
- pip package manager

#### Install Dependencies

```bash
pip install -r requirements.txt
```

Or install the package in development mode:

```bash
pip install -e .
```

## Project Structure

```
convert-orthophoto-to-dxf/
├── src/
│   ├── __init__.py                                # Package initialization
│   ├── convert_orthophoto_to_dxf_snapping.py     # Main conversion module
│   ├── cli.py                                     # Command-line interface
│   ├── gui.py                                     # Graphical user interface
│   ├── config.py                                  # Configuration management
│   ├── types.py                                   # Type definitions
│   └── core/
│       ├── __init__.py                            # Core module exports
│       ├── raster.py                              # Image reading and edge detection
│       ├── vectorize.py                           # Line detection and vectorization
│       ├── snapping.py                            # Line snapping utilities
│       └── dxf_export.py                          # DXF and GeoJSON export
├── tests/
│   ├── __init__.py
│   ├── test_raster.py                             # Tests for raster processing
│   ├── test_snapping.py                           # Tests for snapping functions
│   └── test_dxf_export.py                         # Tests for export functions
├── examples/
│   └── sample_config.yaml                         # Example configuration file
├── .github/
│   └── workflows/
│       └── build-exe.yml                          # GitHub Actions workflow for building executables
├── .gitignore                                     # Git ignore rules
├── LICENSE                                        # MIT License
├── README.md                                      # This file
├── pyproject.toml                                 # Project metadata and configuration
└── requirements.txt                               # Python dependencies
```

## Usage

### Graphical User Interface (GUI)

The easiest way to use the tool is through the GUI application:

#### Using Standalone Executable
Simply double-click the downloaded executable (`OrthophotoToDXF.exe` on Windows, or `OrthophotoToDXF` on Linux/macOS).

#### From Source
```bash
python -m src.gui
```

The GUI provides:
- File browser for selecting input images and output locations
- Adjustable parameters with helpful tooltips
- Real-time progress indication
- Status messages showing conversion progress
- Support for optional GeoJSON export

### Command Line Interface

Basic usage:

```bash
python -m src.cli input_image.jpg output.dxf
```

With GeoJSON output:

```bash
python -m src.cli input_image.jpg output.dxf --geojson output.geojson
```

With custom parameters:

```bash
python -m src.cli input_image.jpg output.dxf \
  --snap-angle 15 \
  --low-threshold 50 \
  --high-threshold 150 \
  --line-threshold 100 \
  --min-line-length 50 \
  --max-line-gap 10 \
  --verbose
```

### Command Line Arguments

- `input`: Path to the input orthophoto image (required)
- `output`: Path to the output DXF file (required)
- `--geojson`: Optional path to output GeoJSON file
- `--snap-angle`: Angle increment in degrees for snapping (default: 15)
- `--low-threshold`: Lower threshold for Canny edge detection (default: 50)
- `--high-threshold`: Upper threshold for Canny edge detection (default: 150)
- `--line-threshold`: Accumulator threshold for line detection (default: 100)
- `--min-line-length`: Minimum line length to detect (default: 100)
- `--max-line-gap`: Maximum gap between line segments (default: 10)
- `--verbose`: Enable verbose output

### Python API

```python
from src.convert_orthophoto_to_dxf_snapping import convert_orthophoto_to_dxf

result = convert_orthophoto_to_dxf(
    image_path='input.jpg',
    dxf_output_path='output.dxf',
    geojson_output_path='output.geojson',  # Optional
    snap_angle=15,
    low_threshold=50,
    high_threshold=150,
    line_threshold=100,
    min_line_length=100,
    max_line_gap=10
)

print(f"Detected {result['lines_detected']} lines")
print(f"Snapped to {result['lines_snapped']} lines")
```

## Configuration

An example configuration file is provided in `examples/sample_config.yaml`. You can customize various processing parameters including:

- Raster processing settings (grayscale conversion, thresholds)
- Vectorization parameters (edge detection, line smoothing)
- Snapping options (grid size, angle snapping)
- DXF export settings (layer name, colors, line weights)

## Testing

Run the test suite:

```bash
pytest tests/
```

Run tests with verbose output:

```bash
pytest -v tests/
```

Run a specific test file:

```bash
pytest tests/test_dxf_export.py
```

## Building Standalone Executables

### Automatic Build via GitHub Actions

Executables are automatically built for Windows, Linux, and macOS when you:
1. Push to the `main` branch
2. Create a pull request
3. Create a tag starting with `v` (e.g., `v1.0.0`)
4. Manually trigger the workflow

The built executables are available as artifacts in the GitHub Actions run, and are automatically attached to releases when you create a version tag.

### Manual Build with PyInstaller

To build an executable locally:

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Build the executable:

**Windows:**
```bash
pyinstaller --name="OrthophotoToDXF" ^
  --onefile ^
  --windowed ^
  --add-data "src;src" ^
  --hidden-import="cv2" ^
  --hidden-import="numpy" ^
  --hidden-import="ezdxf" ^
  --hidden-import="yaml" ^
  --hidden-import="queue" ^
  --hidden-import="threading" ^
  --hidden-import="traceback" ^
  --hidden-import="atexit" ^
  --hidden-import="tkinter" ^
  --collect-all cv2 ^
  --collect-all numpy ^
  --collect-all ezdxf ^
  --noupx ^
  --clean ^
  src/gui.py
```

**Linux/macOS:**
```bash
pyinstaller --name="OrthophotoToDXF" \
  --onefile \
  --windowed \
  --add-data "src:src" \
  --hidden-import="cv2" \
  --hidden-import="numpy" \
  --hidden-import="ezdxf" \
  --hidden-import="yaml" \
  --hidden-import="queue" \
  --hidden-import="threading" \
  --hidden-import="traceback" \
  --hidden-import="atexit" \
  --hidden-import="tkinter" \
  --collect-all cv2 \
  --collect-all numpy \
  --collect-all ezdxf \
  --noupx \
  --clean \
  src/gui.py
```

3. Find the executable in the `dist/` directory.

## Development

### Code Style

This project uses Black for code formatting and Flake8 for linting:

```bash
# Format code
black src/ tests/

# Check code style
flake8 src/ tests/
```

### Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add or update tests as needed
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

This tool uses the following open-source libraries:

- [OpenCV](https://opencv.org/) for image processing
- [ezdxf](https://ezdxf.mozman.at/) for DXF file generation
- [NumPy](https://numpy.org/) for numerical operations