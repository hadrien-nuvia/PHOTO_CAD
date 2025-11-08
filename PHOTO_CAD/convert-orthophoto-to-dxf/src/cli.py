import argparse
from convert_orthophoto_to_dxf_snapping import main

def create_cli_parser():
    parser = argparse.ArgumentParser(description="Convert orthophotos to DXF format.")
    parser.add_argument("input", type=str, help="Path to the input orthophoto image.")
    parser.add_argument("output", type=str, help="Path to the output DXF file.")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to the configuration file.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output.")
    return parser

def main_cli():
    parser = create_cli_parser()
    args = parser.parse_args()
    
    if args.verbose:
        print(f"Input file: {args.input}")
        print(f"Output file: {args.output}")
        print(f"Configuration file: {args.config}")
    
    main(args.input, args.output, args.config)

if __name__ == "__main__":
    main_cli()