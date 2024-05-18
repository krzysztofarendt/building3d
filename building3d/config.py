import logging

# Log file
LOG_FILE: str = "building3d.log"
LOG_LEVEL = logging.DEBUG

# GEOMETRY ====================================================================
# General epsilon - used to avoid zero division etc.
# Should be as small as possible
EPSILON: float = 1e-9

# Geometry epsilon used for comparison operations
GEOM_EPSILON: float = 1e-10

# Geometry relative tolerance (0.25%)
GEOM_RTOL: float = 0.0025

# Number of decimal digits for point coordinates used in hash
POINT_NUM_DEC: int = 10

# MESH ========================================================================
# Mesh joggle - max distance to move vertices around
MESH_JOGGLE: float = 0.1  # Relative to delta

# Default element size
MESH_DELTA: float = 1.0

# Min. distance of mesh points to fixed points (used in PolyMesh)
MESH_REL_DIST_TO_POINTS: float = 0.5  # Relative to delta

# Max. number of tries to re-mesh a solid
SOLID_MESH_MAX_TRIES = 10
