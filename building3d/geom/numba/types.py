import numpy as np
from numpy.typing import NDArray


# Using float64 by default, because it works out-of-the-box
# float32 was often making problems due to implicit casting to float64 in some operations
# numba does not like to make operations on mixed types, so a lot of manual casting
# to float32 everywhere where possible was needed
FLOAT = np.float64
INT = np.uint32

PointType = NDArray[FLOAT]     # Shape (num_points, 3) or (3, )
VectorType = NDArray[FLOAT]    # Shape (num_vectors, 3), or (3, )
IndexType = NDArray[INT]       # Same shape as referenced array

# Constants
INVALID_PT = np.full(3, np.nan, dtype=FLOAT)
