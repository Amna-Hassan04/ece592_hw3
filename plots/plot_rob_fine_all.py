import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os

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
dfs = [pd.read_csv(f) for f in csv_files]

if dfs:
    df = pd.concat(dfs, ignore_index=True)
    df.columns = df.columns.str.strip()
    df["Machine_Clean"] = df["Machine"].str.split(".").str[0]

    os.makedirs("plots", exist_ok=True)

    for machine in df["Machine_Clean"].unique():
        machine_df = df[df["Machine_Clean"] == machine].sort_values("Window_Size")
        
        # --- 1. RAW PLOT (Preserving hardware jitter/sawtooth) ---
        sns.set_theme(style="whitegrid")
        fig, ax = plt.subplots(figsize=(9, 6))
        sns.lineplot(
            data=machine_df, x="Window_Size", y="Cycles", 
            marker="o", color="teal", linewidth=2.0, markersize=7, ax=ax
        )
        ax.set_title(f"Fine-Grained ROB Inflection Zone - Raw ({machine})", fontsize=13, weight="bold")
        ax.set_ylabel("Total Execution Cycles", fontsize=11)
        ax.set_xlabel("Instruction Window Size (N)", fontsize=11)
        plt.tight_layout()
        raw_path = f"plots/{machine}_rob_fine_raw.png"
        plt.savefig(raw_path, dpi=300)
        plt.close()

        # --- 2. SMOOTHED PLOT (Highlighting structural knees) ---
        machine_df["Smoothed_Cycles"] = machine_df["Cycles"].rolling(window=3, center=True, min_periods=1).mean()
        fig, ax = plt.subplots(figsize=(9, 6))
        sns.lineplot(
            data=machine_df, x="Window_Size", y="Smoothed_Cycles", 
            marker="o", color="darkcyan", linewidth=2.5, markersize=7, ax=ax
        )
        ax.set_title(f"Fine-Grained ROB Inflection Zone - Smoothed ({machine})", fontsize=13, weight="bold")
        ax.set_ylabel("Total Execution Cycles", fontsize=11)
        ax.set_xlabel("Instruction Window Size (N)", fontsize=11)
        plt.tight_layout()
        smooth_path = f"plots/{machine}_rob_fine_smoothed.png"
        plt.savefig(smooth_path, dpi=300)
        plt.close()
        print(f"Generated preserved plots for {machine}: {raw_path} & {smooth_path}")

    # --- 3. COMBINED COMPARISON PLOT (Smoothed) ---
    fig, ax = plt.subplots(figsize=(9, 6))
    for machine in df["Machine_Clean"].unique():
        m_df = df[df["Machine_Clean"] == machine].sort_values("Window_Size")
        m_df["Smoothed_Cycles"] = m_df["Cycles"].rolling(window=3, center=True, min_periods=1).mean()
        sns.lineplot(
            data=m_df, x="Window_Size", y="Smoothed_Cycles", hue="Machine_Clean",
            marker="o", linewidth=2.5, markersize=6, ax=ax
        )
    ax.set_title("Fine-Grained ROB Inflection Zone Comparison (Smoothed)", fontsize=13, weight="bold")
    ax.set_ylabel("Total Execution Cycles", fontsize=11)
    ax.set_xlabel("Instruction Window Size (N)", fontsize=11)
    ax.legend(title="Course Machine", loc="upper left")
    plt.tight_layout()
    plt.savefig("plots/rob_fine_comparison_smoothed.png", dpi=300)
    plt.close()
    print("Generated combined comparison plot: plots/rob_fine_comparison_smoothed.png")

else:
    print("Error: No fine-grained ROB CSV data found.")
