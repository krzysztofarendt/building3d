from os.path import join

# Parallel simulation settings
# ============================
# All paths relative to the project output directory
MERGED_DIR = "all"
MAIN_LOG_FILE = "main.log"

JOB_DIR = "job_<jobnum>"
JOB_LOG_FILE = "job_<jobnum>.log"
JOB_HIT_CSV = join(JOB_DIR, "hits_<jobnum>.csv")
JOB_STATE_DIR = join(JOB_DIR, "state")
JOB_ENR_STATE_FILE = join(JOB_STATE_DIR, "energy_<stepnum>.npy")
JOB_POS_STATE_FILE = join(JOB_STATE_DIR, "position_<stepnum>.npy")

# Dump settings
ENERGY_FILE = "energy_*.npy"
POSITION_FILE = "position_*.npy"
DUMP_EXT = ".npy"

MERGED_JOBS_DIR = "all"
STATE_DIR = "state"
B3D_FILE = "building.b3d"

# Movie settings
RAY_LINE_LEN = 10
