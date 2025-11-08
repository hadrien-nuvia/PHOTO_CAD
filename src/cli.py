"""Command-line interface for orthophoto to DXF conversion."""

import argparse

# Support both relative imports (when used as module) and absolute imports (when run directly)
try:
    from .convert_orthophoto_to_dxf_snapping import convert_orthophoto_to_dxf
    from .learning import LearningSystem
except ImportError:
    try:
        from convert_orthophoto_to_dxf_snapping import convert_orthophoto_to_dxf
        from learning import LearningSystem
    except ImportError:
        from src.convert_orthophoto_to_dxf_snapping import convert_orthophoto_to_dxf
        from src.learning import LearningSystem


def create_cli_parser():
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Convert orthophotos to DXF format with line snapping."
    )
    
    # Subcommands for different modes
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Convert command (main functionality)
    convert_parser = subparsers.add_parser('convert', help='Convert orthophoto to DXF')
    convert_parser.add_argument("input", type=str, help="Path to the input orthophoto image.")
    convert_parser.add_argument("output", type=str, help="Path to the output DXF file.")
    convert_parser.add_argument(
        "--geojson", type=str, default=None, help="Optional path to output GeoJSON file."
    )
    convert_parser.add_argument(
        "--snap-angle",
        type=int,
        default=None,
        help="Angle increment in degrees for snapping (default: learned or 15).",
    )
    convert_parser.add_argument(
        "--low-threshold",
        type=int,
        default=None,
        help="Lower threshold for Canny edge detection (default: learned or 50).",
    )
    convert_parser.add_argument(
        "--high-threshold",
        type=int,
        default=None,
        help="Upper threshold for Canny edge detection (default: learned or 150).",
    )
    convert_parser.add_argument(
        "--line-threshold",
        type=int,
        default=None,
        help="Accumulator threshold for Hough line detection (default: learned or 100).",
    )
    convert_parser.add_argument(
        "--min-line-length",
        type=int,
        default=None,
        help="Minimum line length to detect (default: learned or 100).",
    )
    convert_parser.add_argument(
        "--max-line-gap",
        type=int,
        default=None,
        help="Maximum gap between line segments (default: learned or 10).",
    )
    convert_parser.add_argument(
        "--use-learned",
        action="store_true",
        help="Use learned parameters from previous feedback.",
    )
    convert_parser.add_argument(
        "--feedback-file",
        type=str,
        default="feedback_history.json",
        help="Path to feedback history file (default: feedback_history.json).",
    )
    convert_parser.add_argument("--verbose", action="store_true", help="Enable verbose output.")
    
    # Feedback command
    feedback_parser = subparsers.add_parser('feedback', help='Provide feedback on a conversion result')
    feedback_parser.add_argument("image", type=str, help="Path to the image that was processed.")
    feedback_parser.add_argument(
        "--rating",
        type=int,
        required=True,
        choices=[1, 2, 3, 4, 5],
        help="Rating for the result (1-5 stars).",
    )
    feedback_parser.add_argument(
        "--notes",
        type=str,
        default=None,
        help="Optional notes about the result.",
    )
    feedback_parser.add_argument(
        "--snap-angle", type=int, default=15, help="Snap angle used."
    )
    feedback_parser.add_argument(
        "--low-threshold", type=int, default=50, help="Low threshold used."
    )
    feedback_parser.add_argument(
        "--high-threshold", type=int, default=150, help="High threshold used."
    )
    feedback_parser.add_argument(
        "--line-threshold", type=int, default=100, help="Line threshold used."
    )
    feedback_parser.add_argument(
        "--min-line-length", type=int, default=100, help="Min line length used."
    )
    feedback_parser.add_argument(
        "--max-line-gap", type=int, default=10, help="Max line gap used."
    )
    feedback_parser.add_argument(
        "--feedback-file",
        type=str,
        default="feedback_history.json",
        help="Path to feedback history file.",
    )
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show feedback statistics')
    stats_parser.add_argument(
        "--feedback-file",
        type=str,
        default="feedback_history.json",
        help="Path to feedback history file.",
    )
    
    # For backward compatibility, allow direct arguments (old style)
    parser.add_argument("input", type=str, nargs='?', help="Path to the input orthophoto image.")
    parser.add_argument("output", type=str, nargs='?', help="Path to the output DXF file.")
    parser.add_argument(
        "--geojson", type=str, default=None, help="Optional path to output GeoJSON file."
    )
    parser.add_argument(
        "--snap-angle",
        type=int,
        default=15,
        help="Angle increment in degrees for snapping (default: 15).",
    )
    parser.add_argument(
        "--low-threshold",
        type=int,
        default=50,
        help="Lower threshold for Canny edge detection (default: 50).",
    )
    parser.add_argument(
        "--high-threshold",
        type=int,
        default=150,
        help="Upper threshold for Canny edge detection (default: 150).",
    )
    parser.add_argument(
        "--line-threshold",
        type=int,
        default=100,
        help="Accumulator threshold for Hough line detection (default: 100).",
    )
    parser.add_argument(
        "--min-line-length",
        type=int,
        default=100,
        help="Minimum line length to detect (default: 100).",
    )
    parser.add_argument(
        "--max-line-gap",
        type=int,
        default=10,
        help="Maximum gap between line segments (default: 10).",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output.")
    
    return parser


def handle_convert(args):
    """Handle the convert command."""
    learning_system = LearningSystem(feedback_file=getattr(args, 'feedback_file', 'feedback_history.json'))
    
    # Get learned parameters if requested or if not explicitly set
    if getattr(args, 'use_learned', False) or args.snap_angle is None:
        learned_params = learning_system.get_suggested_parameters(image_path=args.input)
        
        # Use learned parameters for any that weren't explicitly set
        snap_angle = args.snap_angle if args.snap_angle is not None else learned_params.get('snap_angle', 15)
        low_threshold = args.low_threshold if args.low_threshold is not None else learned_params.get('low_threshold', 50)
        high_threshold = args.high_threshold if args.high_threshold is not None else learned_params.get('high_threshold', 150)
        line_threshold = args.line_threshold if args.line_threshold is not None else learned_params.get('line_threshold', 100)
        min_line_length = args.min_line_length if args.min_line_length is not None else learned_params.get('min_line_length', 100)
        max_line_gap = args.max_line_gap if args.max_line_gap is not None else learned_params.get('max_line_gap', 10)
        
        if getattr(args, 'use_learned', False) and args.verbose:
            print("Using learned parameters from feedback history:")
            stats = learning_system.get_statistics()
            print(f"  Based on {stats['total_feedback']} previous conversions")
            print(f"  Average rating: {stats['average_rating']:.1f}/5.0")
    else:
        snap_angle = args.snap_angle
        low_threshold = args.low_threshold
        high_threshold = args.high_threshold
        line_threshold = args.line_threshold
        min_line_length = args.min_line_length
        max_line_gap = args.max_line_gap

    if args.verbose:
        print(f"Input file: {args.input}")
        print(f"Output DXF file: {args.output}")
        if args.geojson:
            print(f"Output GeoJSON file: {args.geojson}")
        print(f"Snap angle: {snap_angle}°")
        print(f"Edge detection thresholds: {low_threshold}-{high_threshold}")
        print(f"Line detection threshold: {line_threshold}")
        print(f"Min line length: {min_line_length}")
        print(f"Max line gap: {max_line_gap}")

    try:
        result = convert_orthophoto_to_dxf(
            args.input,
            args.output,
            args.geojson,
            snap_angle,
            low_threshold,
            high_threshold,
            line_threshold,
            min_line_length,
            max_line_gap,
        )

        print("\n✓ Conversion complete!")
        print(f"  Detected {result['lines_detected']} lines")
        print(f"  Snapped to {result['lines_snapped']} lines")
        print(f"  DXF saved to: {result['dxf_path']}")
        if result["geojson_path"]:
            print(f"  GeoJSON saved to: {result['geojson_path']}")
        
        print("\nTo provide feedback on this conversion, run:")
        print(f"  python -m src.cli feedback {args.input} --rating [1-5]")

        return 0

    except Exception as e:
        print(f"✗ Error: {e}")
        return 1


def handle_feedback(args):
    """Handle the feedback command."""
    learning_system = LearningSystem(feedback_file=args.feedback_file)
    
    parameters = {
        "snap_angle": args.snap_angle,
        "low_threshold": args.low_threshold,
        "high_threshold": args.high_threshold,
        "line_threshold": args.line_threshold,
        "min_line_length": args.min_line_length,
        "max_line_gap": args.max_line_gap
    }
    
    try:
        learning_system.add_feedback(
            image_path=args.image,
            parameters=parameters,
            rating=args.rating,
            user_notes=args.notes
        )
        
        print(f"✓ Feedback recorded!")
        print(f"  Rating: {args.rating}/5")
        if args.notes:
            print(f"  Notes: {args.notes}")
        
        stats = learning_system.get_statistics()
        print(f"\nTotal feedback entries: {stats['total_feedback']}")
        print(f"Average rating: {stats['average_rating']:.1f}/5.0")
        
        return 0
    
    except Exception as e:
        print(f"✗ Error recording feedback: {e}")
        return 1


def handle_stats(args):
    """Handle the stats command."""
    learning_system = LearningSystem(feedback_file=args.feedback_file)
    stats = learning_system.get_statistics()
    
    if stats['total_feedback'] == 0:
        print("No feedback recorded yet.")
        return 0
    
    print("Feedback Statistics:")
    print(f"  Total entries: {stats['total_feedback']}")
    print(f"  Average rating: {stats['average_rating']:.2f}/5.0")
    print(f"\nRating distribution:")
    for rating in range(5, 0, -1):
        count = stats['rating_distribution'].get(rating, 0)
        bar = '★' * count
        print(f"  {rating} stars: {bar} ({count})")
    
    print(f"\nMost recent feedback: {stats['most_recent']}")
    
    # Show suggested parameters
    suggested = learning_system.get_suggested_parameters()
    print("\nSuggested parameters based on good results:")
    for key, value in suggested.items():
        print(f"  {key}: {value}")
    
    return 0


def main():
    """Main entry point for the CLI."""
    parser = create_cli_parser()
    args = parser.parse_args()

    # Handle subcommands
    if args.command == 'convert':
        return handle_convert(args)
    elif args.command == 'feedback':
        return handle_feedback(args)
    elif args.command == 'stats':
        return handle_stats(args)
    elif args.input and args.output:
        # Backward compatibility: direct arguments without subcommand
        return handle_convert(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    exit(main())
