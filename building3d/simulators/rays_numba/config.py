# All paths relative to the project output directory
ENERGY_FILE = "energy_<step>.npy"
POSITION_FILE = "position_<step>.npy"
VELOCITY_FILE = "velocity_<step>.npy"
HITS_FILE = "hits_<step>.npy"
STATE_DIR = "state"

BUFF_SIZE = 3000

MAIN_LOG_FILE = "main.log"
MOVIE_FILE = "simulation.mp4"
B3D_FILE = "building.b3d"

# Movie settings
# ==============
RAY_LINE_LEN = 500
RAY_OPACITY = 0.5
RAY_TRAIL_OPACITY = 0.3
RAY_POINT_SIZE = 3  # default 3, looks good if many rays
BUILDING_OPACITY = 0.1
BUILDING_COLOR = [0.8, 0.8, 0.8]  # gray
FPS = 30
CMAP = "RdPu"  # energy color scale
