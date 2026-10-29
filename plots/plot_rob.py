import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os

# Search patterns to locate ROB CSV data files from root or plots directory
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
print(f"Found ROB CSV files: {csv_files}")

# Read and combine discovered dataframes
dfs = [pd.read_csv(f) for f in csv_files]

if dfs:
    df = pd.concat(dfs, ignore_index=True)
    df.columns = df.columns.str.strip()
    
    # Clean up machine domain names to concise labels (e.g., upgrade or skylark)
    df["Machine"] = df["Machine"].str.split(".").str[0]

    # Configure plotting style and dimensions
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(9, 6))

    # Plot line graph with markers for each machine
    sns.lineplot(
        data=df, 
        x="Window_Size", 
        y="Cycles", 
        hue="Machine", 
        marker="o", 
        linewidth=2.5, 
        markersize=8, 
        ax=ax
    )

    # Set chart labels, title, and legend
    ax.set_title("Reorder Buffer (ROB) ALU Window Size vs. Total Cycles", fontsize=13, weight="bold")
    ax.set_ylabel("Total Execution Cycles", fontsize=11)
    ax.set_xlabel("Instruction Window Size (N)", fontsize=11)
    ax.legend(title="Course Machine", loc="upper left")

    plt.tight_layout()
    
    # Save output plot to target directories
    plt.savefig("rob_alu_comparison.png", dpi=300)
    if os.path.exists("../plots"):
        plt.savefig("../plots/rob_alu_comparison.png", dpi=300)
        
    print("ROB comparison graph successfully generated!")
else:
    print("Error: No ROB CSV data files found.")
