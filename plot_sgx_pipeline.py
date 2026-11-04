import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

csv_files = glob.glob("data/sgx_comparison/*_pipeline_comparison.csv")
all_dfs = [pd.read_csv(f) for f in csv_files if os.path.exists(f)]

if all_dfs:
    df = pd.concat(all_dfs, ignore_index=True)
    df.columns = df.columns.str.strip()
    
    plot_df = df.melt(
        id_vars=["Machine", "Execution_Mode"], 
        value_vars=["Dependent_Cycles", "Independent_Cycles"],
        var_name="Instruction Type", 
        value_name="Cycles"
    )

    plot_df["Instruction Type"] = plot_df["Instruction Type"].replace({
        "Dependent_Cycles": "Dependent Chain (1000 instrs)",
        "Independent_Cycles": "Independent Stream (250 instrs)"
    })

    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(9, 6))

    palette = {"Dependent Chain (1000 instrs)": "#d95f02", "Independent Stream (250 instrs)": "#1b9e77"}
    sns.barplot(data=plot_df, x="Execution_Mode", y="Cycles", hue="Instruction Type", palette=palette, ax=ax)

    for p in ax.patches:
        height = p.get_height()
        if height > 0:
            ax.annotate(f'{height:,.0f}', (p.get_x() + p.get_width() / 2., height),
                        ha='center', va='bottom', fontsize=10, color='black', xytext=(0, 3), textcoords='offset points')

    ax.set_title("Intel SGX Enclave Performance: Native vs. Enclave", fontsize=13, weight="bold")
    ax.set_ylabel("Execution Cycles (RDTSC)", fontsize=11)
    ax.set_xlabel("Execution Mode", fontsize=11)
    ax.legend(title="Workload Type", loc="upper left")

    plt.tight_layout()
    os.makedirs("plots/sgx_comparison", exist_ok=True)
    plt.savefig("plots/sgx_comparison/sgx_pipeline_comparison.png", dpi=300)
    plt.close()
    print("Saved plots/sgx_comparison/sgx_pipeline_comparison.png")
else:
    print("No SGX pipeline CSV files found.")
