import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os
import numpy as np

# Find all fine-grained ROB CSV data files
search_paths = [
    "data/q3_rob/*_rob_fine.csv",
    "../data/q3_rob/*_rob_fine.csv"
]

csv_files = []
for pattern in search_paths:
    files = glob.glob(pattern)
    if files:
        csv_files.extend(files)

csv_files = list(set(csv_files))
print(f"Found fine-grained ROB CSV files: {csv_files}")

dfs = [pd.read_csv(f) for f in csv_files]

if dfs:
    df = pd.concat(dfs, ignore_index=True)
    df.columns = df.columns.str.strip()
    df["Machine_Clean"] = df["Machine"].str.split(".").str[0]

    os.makedirs("plots", exist_ok=True)

    # 1. Generate individual plots with both raw points and a smooth trend line
    for machine in df["Machine_Clean"].unique():
        machine_df = df[df["Machine_Clean"] == machine].sort_values("Window_Size")
        
        sns.set_theme(style="whitegrid")
        fig, ax = plt.subplots(figsize=(9, 6))

        # Plot raw measured points as scatter/markers
        sns.scatterplot(
            data=machine_df, 
            x="Window_Size", 
            y="Cycles", 
            color="teal",
            s=70,
            zorder=3,
            ax=ax,
            label="Measured Data"
        )

        # Compute a smoothed rolling average or polynomial fit for the trend line
        # Using a rolling mean to smooth out alignment jitter while preserving the curve shape
        machine_df["Smoothed_Cycles"] = machine_df["Cycles"].rolling(window=3, center=True, min_periods=1).mean()

        sns.lineplot(
            data=machine_df,
            x="Window_Size",
            y="Smoothed_Cycles",
            color="darkcyan",
            linewidth=2.5,
            linestyle="--",
            ax=ax,
            label="Smoothed Trend"
        )

        ax.set_title(f"Fine-Grained ROB Inflection Zone with Trend ({machine})", fontsize=13, weight="bold")
        ax.set_ylabel("Total Execution Cycles", fontsize=11)
        ax.set_xlabel("Instruction Window Size (N)", fontsize=11)
        ax.legend(loc="upper left")

        plt.tight_layout()
        out_path = f"plots/{machine}_rob_fine_zoom.png"
        plt.savefig(out_path, dpi=300)
        plt.close()
        print(f"Saved smoothed individual plot: {out_path}")

    # 2. Generate a combined comparison plot with smooth trends
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(9, 6))

    for machine in df["Machine_Clean"].unique():
        m_df = df[df["Machine_Clean"] == machine].sort_values("Window_Size")
        m_df["Smoothed_Cycles"] = m_df["Cycles"].rolling(window=3, center=True, min_periods=1).mean()
        
        sns.lineplot(
            data=m_df, 
            x="Window_Size", 
            y="Smoothed_Cycles", 
            hue="Machine_Clean",
            marker="o", 
            linewidth=2.5, 
            markersize=6, 
            ax=ax
        )

    ax.set_title("Fine-Grained ROB Inflection Zone Comparison (Smoothed)", fontsize=13, weight="bold")
    ax.set_ylabel("Total Execution Cycles", fontsize=11)
    ax.set_xlabel("Instruction Window Size (N)", fontsize=11)
    ax.legend(title="Course Machine", loc="upper left")

    plt.tight_layout()
    combined_path = "plots/rob_fine_comparison_zoom.png"
    plt.savefig(combined_path, dpi=300)
    plt.close()
    print(f"Saved combined smoothed comparison plot: {combined_path}")

else:
    print("Error: No fine-grained ROB CSV data files found.")
