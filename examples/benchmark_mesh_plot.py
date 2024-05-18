"""Plot data from mesh_generation_time.csv."""
import pandas as pd
import matplotlib.pyplot as plt


if __name__ == "__main__":
    df = pd.read_csv("mesh_generation_time.csv")
    plt.figure(figsize=(10, 6), dpi=100)
    plt.plot(df["num_elements"], df["time"])
    plt.ylabel("Time [s]")
    plt.xlabel("Number of mesh elements")
    plt.grid()
    plt.show()
    plt.close()
