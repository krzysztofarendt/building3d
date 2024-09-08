from os.path import join

# Parallel simulation settings
# ============================
# All paths relative to the project output directory
ENERGY_FILE = "energy_<step>.npy"
POSITION_FILE = "position_<step>.npy"
STATE_DIR = "state"

MAIN_LOG_FILE = "main.log"
MOVIE_FILE = "simulation.mp4"
B3D_FILE = "building.b3d"

MERGE_DIR = "all"
MERGE_HIT_CSV = join(MERGE_DIR, "hits.csv")
MERGE_STATE_DIR = join(MERGE_DIR, STATE_DIR)
MERGE_ENR_STATE_FILE = join(MERGE_STATE_DIR, ENERGY_FILE)
MERGE_POS_STATE_FILE = join(MERGE_STATE_DIR, POSITION_FILE)

JOB_DIR = "job_<job>"
JOB_LOG_FILE = "job_<job>.log"
JOB_HIT_CSV = join(JOB_DIR, "hits_<job>.csv")
JOB_STATE_DIR = join(JOB_DIR, STATE_DIR)
JOB_ENR_STATE_FILE = join(JOB_STATE_DIR, ENERGY_FILE)
JOB_POS_STATE_FILE = join(JOB_STATE_DIR, POSITION_FILE)

# Movie settings
# ==============
RAY_LINE_LEN = 50
RAY_OPACITY = 0.03
RAY_TRAIL_OPACITY = 0.03
RAY_POINT_SIZE = 3  # default 3, looks good if many rays
BUILDING_OPACITY = 0.1
BUILDING_COLOR = [0.8, 0.8, 0.8]  # gray
FPS = 30
CMAP = "RdPu"  # energy color scale
