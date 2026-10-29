import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

upgrade_path = os.path.join("..", "data", "q1_pipelined", "upgrade_q1.csv")
skylark_path = os.path.join("..", "data", "q1_pipelined", "skylark_q1.csv")

dfs = []
if os.path.exists(upgrade_path):
    dfs.append(pd.read_csv(upgrade_path))
if os.path.exists(skylark_path):
    dfs.append(pd.read_csv(skylark_path))

if not dfs:
    if os.path.exists("upgrade_q1.csv"): dfs.append(pd.read_csv("upgrade_q1.csv"))
    if os.path.exists("skylark_q1.csv"): dfs.append(pd.read_csv("skylark_q1.csv"))

if dfs:
    df = pd.concat(dfs)
    df.columns = df.columns.str.strip()
    
    avg_df = df.groupby("Machine")[["Dependent_Cycles", "Independent_Cycles"]].mean().reset_index()

    plot_df = avg_df.melt(id_vars="Machine", value_vars=["Dependent_Cycles", "Independent_Cycles"],
                          var_name="Instruction Type", value_name="Average Cycles")

    plot_df["Instruction Type"] = plot_df["Instruction Type"].replace({
        "Dependent_Cycles": "Dependent Chain (Stalled)",
        "Independent_Cycles": "Independent Stream (Overlapped)"
    })

    plt.figure(figsize=(8, 6))
    sns.set_theme(style="whitegrid")
    sns.barplot(x="Machine", y="Average Cycles", hue="Instruction Type", data=plot_df, palette="muted")

    plt.title("Pipeline Efficiency: Dependent vs. Independent Instructions", fontsize=14, weight="bold")
    plt.ylabel("Average Cycles (1000 Instructions)", fontsize=12)
    plt.xlabel("Course Machine", fontsize=12)
    plt.legend(title="Execution Mode")

    plt.tight_layout()
    plt.savefig("q1_pipeline_comparison.png", dpi=300)
    print("Graph successfully generated and saved as plots/q1_pipeline_comparison.png")
else:
    print("Error: No CSV data files found under data/q1_pipelined/. Please run the benchmark script first.")
