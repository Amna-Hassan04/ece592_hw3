import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os

csv_files = glob.glob("data/tlb/*_tlb.csv")
print(f"Found TLB CSV files: {csv_files}")

dfs = [pd.read_csv(f) for f in csv_files]

if dfs:
    df = pd.concat(dfs, ignore_index=True)
    df.columns = df.columns.str.strip()
    
    # Clean machine name
    if "Machine" in df.columns:
        df["Machine_Clean"] = df["Machine"].str.split(".").str[0]
    else:
        df["Machine_Clean"] = "skylark"

    os.makedirs("plots", exist_ok=True)

    # 1. Generate individual machine-specific plots (clean lines, no confidence bands)
    for machine in df["Machine_Clean"].unique():
        machine_df = df[df["Machine_Clean"] == machine].sort_values("Pages")
        
        sns.set_theme(style="whitegrid")
        fig, ax = plt.subplots(figsize=(9, 6))

        sns.lineplot(
            data=machine_df, 
            x="Pages", 
            y="Avg_Cycles_Per_Access", 
            marker="o", 
            color="m",
            linewidth=2.5, 
            markersize=6, 
            errorbar=None,  # Removes the shaded confidence interval band
            ax=ax
        )

        ax.set_title(f"TLB Capacity & Hierarchy Benchmark ({machine})", fontsize=13, weight="bold")
        ax.set_ylabel("Average Latency per Access (Cycles)", fontsize=11)
        ax.set_xlabel("Working Set Size (Number of 4KB Pages)", fontsize=11)

        plt.tight_layout()
        out_path = f"plots/{machine}_tlb_capacity.png"
        plt.savefig(out_path, dpi=300)
        plt.close()
        print(f"Saved clean machine-specific TLB plot: {out_path}")

    # 2. Generate combined multi-machine comparison plot (clean lines, no shaded bands)
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(9, 6))

    sns.lineplot(
        data=df, 
        x="Pages", 
        y="Avg_Cycles_Per_Access", 
        hue="Machine_Clean",
        marker="o", 
        linewidth=2.5, 
        markersize=6, 
        errorbar=None,  # Removes the shaded confidence interval band
        ax=ax
    )

    ax.set_title("TLB Capacity & Hierarchy Comparison", fontsize=13, weight="bold")
    ax.set_ylabel("Average Latency per Access (Cycles)", fontsize=11)
    ax.set_xlabel("Working Set Size (Number of 4KB Pages)", fontsize=11)
    ax.legend(title="Course Machine", loc="upper left")

    plt.tight_layout()
    comparison_path = "plots/tlb_capacity_comparison.png"
    plt.savefig(comparison_path, dpi=300)
    plt.close()
    print(f"Saved clean TLB comparison plot: {comparison_path}")

else:
    print("Error: No TLB CSV data found.")
