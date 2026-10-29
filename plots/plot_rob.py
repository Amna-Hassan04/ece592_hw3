import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os

search_paths = [
    "data/q3_rob/*_rob_alu.csv",
    "../data/q3_rob/*_rob_alu.csv"
]

csv_files = []
for pattern in search_paths:
    files = glob.glob(pattern)
    if files:
        csv_files.extend(files)

csv_files = list(set(csv_files))
print(f"Found broad ROB CSV files: {csv_files}")

dfs = [pd.read_csv(f) for f in csv_files]

if dfs:
    df = pd.concat(dfs, ignore_index=True)
    df.columns = df.columns.str.strip()
    df["Machine_Clean"] = df["Machine"].str.split(".").str[0]

    os.makedirs("plots", exist_ok=True)

    # 1. Generate individual broad plots per machine
    for machine in df["Machine_Clean"].unique():
        machine_df = df[df["Machine_Clean"] == machine].sort_values("Window_Size")
        
        sns.set_theme(style="whitegrid")
        fig, ax = plt.subplots(figsize=(9, 6))
        sns.lineplot(
            data=machine_df, x="Window_Size", y="Cycles", 
            marker="o", color="b", linewidth=2.5, markersize=8, ax=ax
        )
        ax.set_title(f"Reorder Buffer (ROB) ALU Window Size vs. Total Cycles ({machine})", fontsize=13, weight="bold")
        ax.set_ylabel("Total Execution Cycles", fontsize=11)
        ax.set_xlabel("Instruction Window Size (N)", fontsize=11)
        plt.tight_layout()
        out_path = f"plots/{machine}_rob_alu_broad.png"
        plt.savefig(out_path, dpi=300)
        plt.close()
        print(f"Saved broad plot for {machine}: {out_path}")

    # 2. Generate combined broad comparison plot (The crucial multi-machine graph)
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
    ax.set_title("Reorder Buffer (ROB) ALU Window Size vs. Total Cycles", fontsize=13, weight="bold")
    ax.set_ylabel("Total Execution Cycles", fontsize=11)
    ax.set_xlabel("Instruction Window Size (N)", fontsize=11)
    ax.legend(title="Course Machine", loc="upper left")
    plt.tight_layout()
    
    combined_path = "plots/rob_alu_comparison.png"
    plt.savefig(combined_path, dpi=300)
    plt.close()
    print(f"Saved combined broad comparison plot: {combined_path}")

else:
    print("Error: No broad ROB CSV data found.")
