import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os

# Find CSV files across repository paths
search_paths = [
    "data/q1_pipelined/*_q1.csv",
    "../data/q1_pipelined/*_q1.csv"
]

csv_files = []
for pattern in search_paths:
    files = glob.glob(pattern)
    if files:
        csv_files.extend(files)

csv_files = list(set(csv_files))
print(f"Found CSV files: {csv_files}")

dfs = [pd.read_csv(f) for f in csv_files]

if dfs:
    df = pd.concat(dfs, ignore_index=True)
    df.columns = df.columns.str.strip()
    
    # Clean up machine names (e.g., skylark.ece.ncsu.edu -> skylark)
    df["Machine"] = df["Machine"].str.split(".").str[0]

    avg_df = df.groupby("Machine")[["Dependent_Cycles", "Independent_Cycles"]].mean().reset_index()

    plot_df = avg_df.melt(id_vars="Machine", value_vars=["Dependent_Cycles", "Independent_Cycles"],
                          var_name="Instruction Type", value_name="Average Cycles")

    plot_df["Instruction Type"] = plot_df["Instruction Type"].replace({
        "Dependent_Cycles": "Dependent Chain (Stalled)",
        "Independent_Cycles": "Independent Stream (Overlapped)"
    })

    # Set up a 1-row, 2-column figure layout (or single clean panel styled like your reference)
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(8, 6))

    palette = {"Dependent Chain (Stalled)": "#d95f02", "Independent Stream (Overlapped)": "#1b9e77"}
    bars = sns.barplot(x="Machine", y="Average Cycles", hue="Instruction Type", data=plot_df, palette=palette, ax=ax)

    # Add exact numerical labels on top of the bars (similar to your reference image)
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
    
    # Save to plots directory
    plt.savefig("q1_pipeline_comparison.png", dpi=300)
    if os.path.exists("../plots"):
        plt.savefig("../plots/q1_pipeline_comparison.png", dpi=300)
        
    print("Graph successfully generated with data labels and reference styling!")
else:
    print("Error: No CSV data files found.")
