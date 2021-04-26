import csv
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def plot_accuracy(input_path, output_path):
    df = pd.read_csv(input_path, skiprows=[0])
    print(df)
    df.plot.line(x="round", y="accuracy", ylim=(0,1))
    plt.show()

def plot_regret(input_path, output_path):
    df = pd.read_csv(input_path, skiprows=[0])
    df["cumsum"] = df["regret"].cumsum()
    d = np.polyfit(df["k"]+df["round"]*df["k"].max(),df["cumsum"],1)
    f = np.poly1d(d)
    df.insert(4,"trend",f(df["k"]+df["round"]*df["k"].max()))
    ax = df.plot.line(y="cumsum")
    df.plot(y="trend", color="Red", ax=ax)
    plt.show()