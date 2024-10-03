import logging

# Log file
LOG_FILE: str = "b3d.log"  # None to print to screen
LOG_LEVEL = logging.INFO

# GEOMETRY ====================================================================
# General epsilon - used to avoid zero division etc.
# Should be as small as possible
EPSILON: float = 1e-10

# Geometry absolute tolerance used for comparison operations
GEOM_ATOL: float = 1e-10  # At least 1e-10 needed for teapot :)

# Geometry relative tolerance (0.1%)
GEOM_RTOL: float = 1e-4

# Number of decimal digits for point coordinates used in hash
POINT_NUM_DEC: int = 8

# MESH ========================================================================
# Mesh joggle - max distance to move vertices around
MESH_JOGGLE: float = 0.1  # Relative to delta

# Default element size
MESH_DELTA: float = 1.0

# Min. distance of mesh points to fixed points (used in PolyMesh)
MESH_REL_DIST_TO_POINTS: float = 0.5  # Relative to delta

# Max. number of tries to re-mesh a solid
SOLID_MESH_MAX_TRIES = 10

# Max. number of tries for tetrahedralization quality improvement
TETRA_MAX_TRIES = 500
