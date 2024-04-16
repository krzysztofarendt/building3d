import logging

# Log file
LOG_FILE: str = "building3d.log"
LOG_LEVEL = logging.DEBUG

# Geometry epsilon used for comparison operations
GEOM_EPSILON: float = 1e-5

# General epsilon - used to avoid zero division etc.
# Should be as small as possible
EPSILON: float = 1e-9

# Mesh joggle - max distance to move vertices around
MESH_JOGGLE: float = 0.1  # Relative to delta
MESH_DELTA: float = 1.0

# Number of decimal digits for point coordinates used in hash
POINT_NUM_DEC: int = 6
