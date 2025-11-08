"""Main conversion module for orthophoto to DXF."""

# Support both relative imports (when used as module) and absolute imports (when run directly)
try:
    from .core.raster import read_image, detect_edges
    from .core.vectorize import detect_lines
    from .core.snapping import snap_lines
    from .core.dxf_export import export_to_dxf, export_to_geojson
except ImportError:
    try:
        from core.raster import read_image, detect_edges
        from core.vectorize import detect_lines
        from core.snapping import snap_lines
        from core.dxf_export import export_to_dxf, export_to_geojson
    except ImportError:
        from src.core.raster import read_image, detect_edges
        from src.core.vectorize import detect_lines
        from src.core.snapping import snap_lines
        from src.core.dxf_export import export_to_dxf, export_to_geojson


def convert_orthophoto_to_dxf(
    image_path,
    dxf_output_path,
    geojson_output_path=None,
    snap_angle=15,
    low_threshold=50,
    high_threshold=150,
    line_threshold=100,
    min_line_length=100,
    max_line_gap=10,
):
    """
    Convert an orthophoto image to DXF format with optional snapping.

    Args:
        image_path: Path to input orthophoto image.
        dxf_output_path: Path to save output DXF file.
        geojson_output_path: Optional path to save GeoJSON file.
        snap_angle: Angle increment in degrees for snapping (default: 15).
        low_threshold: Lower threshold for Canny edge detection (default: 50).
        high_threshold: Upper threshold for Canny edge detection (default: 150).
        line_threshold: Accumulator threshold for Hough line detection (default: 100).
        min_line_length: Minimum line length to detect (default: 100).
        max_line_gap: Maximum gap between line segments (default: 10).
    """
    # Read and process the image
    image = read_image(image_path)

    # Detect edges
    edges = detect_edges(image, low_threshold, high_threshold)

    # Detect lines
    lines = detect_lines(edges, line_threshold, min_line_length, max_line_gap)

    # Snap lines to angles
    snapped_lines = snap_lines(lines, snap_angle)

    # Export to DXF
    export_to_dxf(snapped_lines, dxf_output_path)

    # Export to GeoJSON if requested
    if geojson_output_path:
        export_to_geojson(snapped_lines, geojson_output_path)

    return {
        "lines_detected": len(lines),
        "lines_snapped": len(snapped_lines),
        "dxf_path": dxf_output_path,
        "geojson_path": geojson_output_path,
    }


def main(image_path, dxf_output_path, geojson_output_path=None, snap_angle=15):
    """
    Main entry point for command-line usage.

    Args:
        image_path: Path to input image.
        dxf_output_path: Path to output DXF file.
        geojson_output_path: Optional path to output GeoJSON file.
        snap_angle: Angle for snapping (default: 15 degrees).
    """
    result = convert_orthophoto_to_dxf(image_path, dxf_output_path, geojson_output_path, snap_angle)

    print("Conversion complete!")
    print(f"Detected {result['lines_detected']} lines")
    print(f"Snapped to {result['lines_snapped']} lines")
    print(f"DXF saved to: {result['dxf_path']}")
    if result["geojson_path"]:
        print(f"GeoJSON saved to: {result['geojson_path']}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert orthophotos to DXF with snapping.")
    parser.add_argument("image_path", help="Path to the input orthophoto image.")
    parser.add_argument("dxf_output_path", help="Path to save the output DXF file.")
    parser.add_argument("--geojson", help="Path to save the output GeoJSON file.")
    parser.add_argument(
        "--snap_angle", type=int, default=15, help="Angle to snap lines to (default: 15 degrees)."
    )

    args = parser.parse_args()
    main(args.image_path, args.dxf_output_path, args.geojson, args.snap_angle)
