import numpy as np
from numpy.typing import NDArray


FLOAT = np.float32
INT = np.uint32

PointType = NDArray[FLOAT]      # Shape (num_points, 3) or (3, )
VectorType = NDArray[FLOAT]    # Shape (num_vectors, 3), or (3, )
IndexType = NDArray[INT]       # Same shape as referenced array
