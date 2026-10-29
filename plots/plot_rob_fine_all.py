import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os

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

    os.makedirs("plots", abs=True) if not os.path.exists("plots") else None

    # 1. Generate an individual plot for each machine separately
    for machine in df["Machine_Clean"].unique():
        machine_df = df[df["Machine_Clean"] == machine]
        
        sns.set_theme(style="whitegrid")
        fig, ax = plt.subplots(figsize=(9, 6))

        sns.lineplot(
            data=machine_df, 
            x="Window_Size", 
            y="Cycles", 
            marker="o", 
            color="teal",
            linewidth=2.5, 
            markersize=8, 
            ax=ax
        )

        ax.set_title(f"Fine-Grained ROB Inflection Zone ({machine})", fontsize=13, weight="bold")
        ax.set_ylabel("Total Execution Cycles", fontsize=11)
        ax.set_xlabel("Instruction Window Size (N)", fontsize=11)

        plt.tight_layout()
        out_path = f"plots/{machine}_rob_fine_zoom.png"
        plt.savefig(out_path, dpi=300)
        plt.close()
        print(f"Saved individual plot: {out_path}")

    # 2. Generate a combined comparison plot for all machines together
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(9, 6))

    sns.lineplot(
        data=df, 
        x="Window_Size", 
        y="Cycles", 
        hue="Machine_Clean", 
        marker="o", 
        linewidth=2.5, 
        markersize=8, 
        ax=ax
    )

    ax.set_title("Fine-Grained ROB Inflection Zone Comparison", fontsize=13, weight="bold")
    ax.set_ylabel("Total Execution Cycles", fontsize=11)
    ax.set_xlabel("Instruction Window Size (N)", fontsize=11)
    ax.legend(title="Course Machine", loc="upper left")

    plt.tight_layout()
    combined_path = "plots/rob_fine_comparison_zoom.png"
    plt.savefig(combined_path, dpi=300)
    plt.close()
    print(f"Saved combined comparison plot: {combined_path}")

else:
    print("Error: No fine-grained ROB CSV data files found.")
