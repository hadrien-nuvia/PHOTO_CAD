# convert_orthophoto_to_dxf_snapping.py

import cv2
import numpy as np
import ezdxf
import geojson
import os

def read_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Image not found at {image_path}")
    return image

def detect_lines(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=10)
    return lines

def snap_lines(lines, snap_angle=15):
    snapped_lines = []
    for line in lines:
        for x1, y1, x2, y2 in line:
            angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
            snapped_angle = round(angle / snap_angle) * snap_angle
            length = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            x2 = x1 + length * np.cos(np.radians(snapped_angle))
            y2 = y1 + length * np.sin(np.radians(snapped_angle))
            snapped_lines.append((x1, y1, int(x2), int(y2)))
    return snapped_lines

def export_to_dxf(snapped_lines, output_path):
    doc = ezdxf.new()
    msp = doc.modelspace()
    for x1, y1, x2, y2 in snapped_lines:
        msp.add_line(start=(x1, y1), end=(x2, y2))
    doc.saveas(output_path)

def export_to_geojson(snapped_lines, output_path):
    features = []
    for x1, y1, x2, y2 in snapped_lines:
        line = geojson.LineString([(x1, y1), (x2, y2)])
        features.append(geojson.Feature(geometry=line))
    feature_collection = geojson.FeatureCollection(features)
    with open(output_path, 'w') as f:
        geojson.dump(feature_collection, f)

def main(image_path, dxf_output_path, geojson_output_path, snap_angle=15):
    image = read_image(image_path)
    lines = detect_lines(image)
    snapped_lines = snap_lines(lines, snap_angle)
    export_to_dxf(snapped_lines, dxf_output_path)
    export_to_geojson(snapped_lines, geojson_output_path)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert orthophotos to DXF with snapping.")
    parser.add_argument("image_path", help="Path to the input orthophoto image.")
    parser.add_argument("dxf_output_path", help="Path to save the output DXF file.")
    parser.add_argument("geojson_output_path", help="Path to save the output GeoJSON file.")
    parser.add_argument("--snap_angle", type=int, default=15, help="Angle to snap lines to (default: 15 degrees).")

    args = parser.parse_args()
    main(args.image_path, args.dxf_output_path, args.geojson_output_path, args.snap_angle)