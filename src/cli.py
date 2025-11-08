"""Command-line interface for orthophoto to DXF conversion."""

import argparse

# Support both relative imports (when used as module) and absolute imports (when run directly)
try:
    from .convert_orthophoto_to_dxf_snapping import convert_orthophoto_to_dxf
except ImportError:
    from convert_orthophoto_to_dxf_snapping import convert_orthophoto_to_dxf


def create_cli_parser():
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Convert orthophotos to DXF format with line snapping."
    )
    parser.add_argument(
        "input", 
        type=str, 
        help="Path to the input orthophoto image."
    )
    parser.add_argument(
        "output", 
        type=str, 
        help="Path to the output DXF file."
    )
    parser.add_argument(
        "--geojson",
        type=str,
        default=None,
        help="Optional path to output GeoJSON file."
    )
    parser.add_argument(
        "--snap-angle",
        type=int,
        default=15,
        help="Angle increment in degrees for snapping (default: 15)."
    )
    parser.add_argument(
        "--low-threshold",
        type=int,
        default=50,
        help="Lower threshold for Canny edge detection (default: 50)."
    )
    parser.add_argument(
        "--high-threshold",
        type=int,
        default=150,
        help="Upper threshold for Canny edge detection (default: 150)."
    )
    parser.add_argument(
        "--line-threshold",
        type=int,
        default=100,
        help="Accumulator threshold for Hough line detection (default: 100)."
    )
    parser.add_argument(
        "--min-line-length",
        type=int,
        default=100,
        help="Minimum line length to detect (default: 100)."
    )
    parser.add_argument(
        "--max-line-gap",
        type=int,
        default=10,
        help="Maximum gap between line segments (default: 10)."
    )
    parser.add_argument(
        "--verbose", 
        action="store_true", 
        help="Enable verbose output."
    )
    return parser


def main():
    """Main entry point for the CLI."""
    parser = create_cli_parser()
    args = parser.parse_args()
    
    if args.verbose:
        print(f"Input file: {args.input}")
        print(f"Output DXF file: {args.output}")
        if args.geojson:
            print(f"Output GeoJSON file: {args.geojson}")
        print(f"Snap angle: {args.snap_angle}°")
        print(f"Edge detection thresholds: {args.low_threshold}-{args.high_threshold}")
        print(f"Line detection threshold: {args.line_threshold}")
        print(f"Min line length: {args.min_line_length}")
        print(f"Max line gap: {args.max_line_gap}")
    
    try:
        result = convert_orthophoto_to_dxf(
            args.input,
            args.output,
            args.geojson,
            args.snap_angle,
            args.low_threshold,
            args.high_threshold,
            args.line_threshold,
            args.min_line_length,
            args.max_line_gap
        )
        
        print(f"\n✓ Conversion complete!")
        print(f"  Detected {result['lines_detected']} lines")
        print(f"  Snapped to {result['lines_snapped']} lines")
        print(f"  DXF saved to: {result['dxf_path']}")
        if result['geojson_path']:
            print(f"  GeoJSON saved to: {result['geojson_path']}")
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())