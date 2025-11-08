"""DXF and GeoJSON export functionality."""

import ezdxf
import json


def export_to_dxf(lines, output_path):
    """
    Export lines to a DXF file.
    
    Args:
        lines: List of lines where each line is (x1, y1, x2, y2).
        output_path: Path to save the output DXF file.
    """
    doc = ezdxf.new()
    msp = doc.modelspace()
    
    for line in lines:
        if len(line) == 4:
            x1, y1, x2, y2 = line
            msp.add_line(start=(x1, y1), end=(x2, y2))
    
    doc.saveas(output_path)


def export_to_geojson(lines, output_path):
    """
    Export lines to a GeoJSON file.
    
    Args:
        lines: List of lines where each line is (x1, y1, x2, y2).
        output_path: Path to save the output GeoJSON file.
    """
    features = []
    
    for line in lines:
        if len(line) == 4:
            x1, y1, x2, y2 = line
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[x1, y1], [x2, y2]]
                },
                "properties": {}
            }
            features.append(feature)
    
    feature_collection = {
        "type": "FeatureCollection",
        "features": features
    }
    
    with open(output_path, 'w') as f:
        json.dump(feature_collection, f, indent=2)