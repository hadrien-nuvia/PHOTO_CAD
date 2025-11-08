from typing import List, Tuple, Dict, Any

# Define a type for coordinates
Coordinate = Tuple[float, float]

# Define a type for a line represented by two coordinates
Line = Tuple[Coordinate, Coordinate]

# Define a type for a collection of lines
Lines = List[Line]

# Define a type for configuration settings
Config = Dict[str, Any]

# Define a type for the result of the conversion process
ConversionResult = Dict[str, Any]