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
    df["Machine_Clean"] = df["Machine"].str.split(".").str[0] if "Machine" in df.columns else "upgrade"

    os.makedirs("plots", exist_ok=True)

    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(9, 6))

    sns.lineplot(
        data=df, 
        x="Pages", 
        y="Avg_Cycles_Per_Access", 
        marker="o", 
        color="m",
        linewidth=2.5, 
        markersize=6, 
        ax=ax
    )

    ax.set_title("TLB Capacity & Hierarchy Benchmark", fontsize=13, weight="bold")
    ax.set_ylabel("Average Latency per Access (Cycles)", fontsize=11)
    ax.set_xlabel("Working Set Size (Number of 4KB Pages)", fontsize=11)

    plt.tight_layout()
    out_path = "plots/tlb_capacity_upgrade.png"
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Saved TLB plot: {out_path}")
else:
    print("Error: No TLB CSV data found.")
