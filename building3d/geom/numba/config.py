import numpy as np
from numpy.typing import NDArray


PointType = NDArray[np.float32]     # Shape (num_points, 3) or (3, )
VectorType = NDArray[np.float32]    # Shape (num_vectors, 3), or (3, )
IndexType = NDArray[np.int32]       # Same shape as referenced array
