import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Recursively find all Q1 CSV files across any folder structure inside data/
csv_files = glob.glob("data/**/*q1*.csv", recursive=True) + glob.glob("data/*q1*.csv")
# Deduplicate file list
csv_files = sorted(list(set(csv_files)))

print(f"Found Q1 CSV files: {csv_files}")

all_dfs = []
for file in csv_files:
    try:
        df = pd.read_csv(file)
        df.columns = df.columns.str.strip()
        
        # Extract clean machine name from filename (e.g., "data/q1_pipelined/sunbird_q1.csv" -> "sunbird")
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
    df = pd.concat(all_dfs, ignore_index=True)

    avg_df = df.groupby("Machine_Clean")[["Dependent_Cycles", "Independent_Cycles"]].mean().reset_index()

    plot_df = avg_df.melt(id_vars="Machine_Clean", value_vars=["Dependent_Cycles", "Independent_Cycles"],
                          var_name="Instruction Type", value_name="Average Cycles")

    plot_df["Instruction Type"] = plot_df["Instruction Type"].replace({
        "Dependent_Cycles": "Dependent Chain (Stalled)",
        "Independent_Cycles": "Independent Stream (Overlapped)"
    })

    # Set up figure styling
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(9, 6))

    palette = {"Dependent Chain (Stalled)": "#d95f02", "Independent Stream (Overlapped)": "#1b9e77"}
    bars = sns.barplot(x="Machine_Clean", y="Average Cycles", hue="Instruction Type", data=plot_df, palette=palette, ax=ax)

    # Add exact numerical labels on top of the bars
    for p in ax.patches:
        height = p.get_height()
        if height > 0:
            ax.annotate(f'{height:.2f}',
                        (p.get_x() + p.get_width() / 2., height),
                        ha='center', va='bottom',
                        fontsize=10, color='black',
                        xytext=(0, 3),
                        textcoords='offset points')

    ax.set_title("Pipeline Efficiency: Dependent vs. Independent Instructions", fontsize=13, weight="bold")
    ax.set_ylabel("Cycles per 1000 Instructions (RDTSC)", fontsize=11)
    ax.set_xlabel("Course Machine", fontsize=11)
    ax.legend(title="Execution Mode", loc="upper right")

    plt.tight_layout()
    
    # Create target directory: plots/q1/
    output_dir = "plots/q1"
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, "q1_pipeline_comparison.png")
    plt.savefig(output_path, dpi=300)
    plt.close()
    
    print(f"Graph successfully generated and saved to {output_path}!")
else:
    print("Error: No Q1 CSV data files found.")