# Paths
# =============================================================================
# All paths relative to the project output directory
ENERGY_FILE = "energy_<step>.npy"
POSITION_FILE = "position_<step>.npy"
VELOCITY_FILE = "velocity_<step>.npy"
HITS_FILE = "hits_<step>.npy"
STATE_DIR = "state"

MAIN_LOG_FILE = "main.log"
MOVIE_FILE = "simulation.mp4"
B3D_FILE = "building.b3d"

# Surface properties
# =============================================================================
ABSORB = 0.2

# Sink properties
# =============================================================================
SINK_RADIUS = 0.1

# Speed and time step
# =============================================================================
SPEED = 343.0
T_STEP = 1e-4  # Teapot: 1e-4, Sphere: 5e-5

# Grid
# =============================================================================
GRID_STEP = 0.5

# Movie settings
# =============================================================================
BUFF_SIZE = 1000  # Number of last steps to show in a movie
RAY_LINE_LEN = 16
RAY_OPACITY = 0.2
RAY_TRAIL_OPACITY = 0.1
RAY_POINT_SIZE = 3  # default 3, looks good if many rays
BUILDING_OPACITY = 0.1
BUILDING_COLOR = [0.8, 0.8, 0.8]  # gray
FPS = 30
CMAP = "RdPu"  # energy color scale
