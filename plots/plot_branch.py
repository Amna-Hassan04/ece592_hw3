import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os

csv_files = glob.glob("data/branch/*_branch.csv")
print(f"Found Branch CSV files: {csv_files}")

dfs = [pd.read_csv(f) for f in csv_files]

if dfs:
    df = pd.concat(dfs, ignore_index=True)
    df.columns = df.columns.str.strip()
    df["Machine_Clean"] = df["Machine"].str.split(".").str[0]

    os.makedirs("plots", exist_ok=True)

    # 1. Generate individual machine-specific plots
    for machine in df["Machine_Clean"].unique():
        machine_df = df[df["Machine_Clean"] == machine]
        
        sns.set_theme(style="whitegrid")
        fig, ax = plt.subplots(figsize=(8, 6))

        sns.barplot(
            data=machine_df, 
            x="Branch_Type", 
            y="Cycles", 
            palette=["#e74c3c", "#2ecc71"],
            ax=ax
        )

        ax.set_title(f"Branch Prediction Impact ({machine})", fontsize=13, weight="bold")
        ax.set_ylabel("Execution Cycles (Lower is Better)", fontsize=11)
        ax.set_xlabel("Branch Behavior Type", fontsize=11)

        plt.tight_layout()
        out_path = f"plots/{machine}_branch_prediction.png"
        plt.savefig(out_path, dpi=300)
        plt.close()
        print(f"Saved machine-specific branch plot: {out_path}")

    # 2. Generate multi-machine comparison plot
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(9, 6))

    sns.barplot(
        data=df, 
        x="Branch_Type", 
        y="Cycles", 
        hue="Machine_Clean",
        palette="muted",
        ax=ax
    )

    ax.set_title("Branch Prediction Performance Comparison", fontsize=13, weight="bold")
    ax.set_ylabel("Execution Cycles (Lower is Better)", fontsize=11)
    ax.set_xlabel("Branch Behavior Type", fontsize=11)
    ax.legend(title="Course Machine", loc="upper left")

    plt.tight_layout()
    comparison_path = "plots/branch_prediction_comparison.png"
    plt.savefig(comparison_path, dpi=300)
    plt.close()
    print(f"Saved branch comparison plot: {comparison_path}")

else:
    print("Error: No Branch CSV data found.")
