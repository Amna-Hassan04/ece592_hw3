import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os

csv_files = glob.glob("data/q3_rob/*_hw_rob.csv")
print(f"Found Henry Wong ROB CSV files: {csv_files}")

dfs = [pd.read_csv(f) for f in csv_files]

if dfs:
    df = pd.concat(dfs, ignore_index=True)
    df.columns = df.columns.str.strip()
    df["Machine_Clean"] = df["Machine"].str.split(".").str[0]

    os.makedirs("plots", exist_ok=True)

    # 1. Generate individual plots for each machine so they don't overwrite
    for machine in df["Machine_Clean"].unique():
        machine_df = df[df["Machine_Clean"] == machine].sort_values("Window_Size")
        
        sns.set_theme(style="whitegrid")
        fig, ax = plt.subplots(figsize=(9, 6))

        sns.lineplot(
            data=machine_df, 
            x="Window_Size", 
            y="Cycles", 
            marker="o", 
            color="teal",
            linewidth=2.5, 
            markersize=6, 
            ax=ax
        )

        ax.set_title(f"ROB Capacity Benchmark ({machine})", fontsize=13, weight="bold")
        ax.set_ylabel("Normalized Execution Cycles", fontsize=11)
        ax.set_xlabel("Instruction Window Size (N)", fontsize=11)

        plt.tight_layout()
        out_path = f"plots/{machine}_hw_rob.png"
        plt.savefig(out_path, dpi=300)
        plt.close()
        print(f"Saved machine-specific plot: {out_path}")

    # 2. Generate combined multi-machine comparison plot
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(9, 6))

    sns.lineplot(
        data=df, 
        x="Window_Size", 
        y="Cycles", 
        hue="Machine_Clean",
        marker="o", 
        linewidth=2.5, 
        markersize=6, 
        ax=ax
    )

    ax.set_title(" ROB Capacity Benchmark Comparison", fontsize=13, weight="bold")
    ax.set_ylabel("Normalized Execution Cycles", fontsize=11)
    ax.set_xlabel("Instruction Window Size (N)", fontsize=11)
    ax.legend(title="Course Machine", loc="upper left")

    plt.tight_layout()
    comparison_path = "plots/hw_rob_comparison.png"
    plt.savefig(comparison_path, dpi=300)
    plt.close()
    print(f"Saved comparison plot: {comparison_path}")

else:
    print("Error: No Henry Wong ROB CSV data found.")
