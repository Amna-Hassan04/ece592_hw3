import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Recursively find all TLB CSV files across any folder structure inside data/
csv_files = glob.glob("data/**/*tlb*.csv", recursive=True) + glob.glob("data/*tlb*.csv")
# Deduplicate file list
csv_files = sorted(list(set(csv_files)))

print(f"Found TLB CSV files: {csv_files}")

all_dfs = []
for file in csv_files:
    try:
        df = pd.read_csv(file)
        df.columns = df.columns.str.strip()
        
        # Extract clean machine name from filename (e.g., "data/tlb/sunbird_tlb.csv" -> "sunbird")
        basename = os.path.basename(file)
        inferred_machine = basename.split('_')[0].lower()
        
        # Assign or standardize machine column
        if "Machine" in df.columns:
            df["Machine_Clean"] = df["Machine"].astype(str).str.split(".").str[0].str.lower()
            df["Machine_Clean"] = df["Machine_Clean"].mask(df["Machine_Clean"] == "", inferred_machine)
        else:
            df["Machine_Clean"] = inferred_machine
            
        all_dfs.append(df)
        print(f"Successfully loaded {file} for machine: {inferred_machine}")
    except Exception as e:
        print(f"Error reading {file}: {e}")

if all_dfs:
    combined_df = pd.concat(all_dfs, ignore_index=True)
    
    # Create target directory: plots/tlb/
    output_dir = "plots/tlb"
    os.makedirs(output_dir, exist_ok=True)

    # 1. Generate individual machine-specific plots
    for machine in combined_df["Machine_Clean"].unique():
        machine_df = combined_df[combined_df["Machine_Clean"] == machine].sort_values("Pages")
        
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
            errorbar=None,
            ax=ax
        )

        ax.set_title(f"TLB Capacity & Hierarchy Benchmark ({machine.upper()})", fontsize=13, weight="bold")
        ax.set_ylabel("Average Latency per Access (Cycles)", fontsize=11)
        ax.set_xlabel("Working Set Size (Number of 4KB Pages)", fontsize=11)

        plt.tight_layout()
        out_path = os.path.join(output_dir, f"{machine}_tlb_capacity.png")
        plt.savefig(out_path, dpi=300)
        plt.close()
        print(f"Saved clean machine-specific TLB plot: {out_path}")

    # 2. Generate multi-machine comparison plot
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(10, 6))

    sns.lineplot(
        data=combined_df, 
        x="Pages", 
        y="Avg_Cycles_Per_Access", 
        hue="Machine_Clean",
        marker="o", 
        linewidth=2.5, 
        markersize=6, 
        errorbar=None,
        ax=ax
    )

    ax.set_title("TLB Capacity & Hierarchy Comparison", fontsize=13, weight="bold")
    ax.set_ylabel("Average Latency per Access (Cycles)", fontsize=11)
    ax.set_xlabel("Working Set Size (Number of 4KB Pages)", fontsize=11)
    ax.legend(title="Course Machine", loc="upper left")

    plt.tight_layout()
    comparison_path = os.path.join(output_dir, "tlb_capacity_comparison.png")
    plt.savefig(comparison_path, dpi=300)
    plt.close()
    print(f"Saved clean TLB comparison plot: {comparison_path}")

else:
    print("Error: No TLB CSV data found across search paths.")