import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

os.makedirs("plots/enclave comparison", exist_ok=True)

files = {
    "Native": "data/q3_rob/artemisia_hw_rob.csv",
    "Enclave": "data/q3_rob/artemisia_hw_rob_enclave.csv"
}

for mode, path in files.items():
    if os.path.exists(path):
        df = pd.read_csv(path)
        df.columns = df.columns.str.strip()
        
        sns.set_theme(style="whitegrid")
        fig, ax = plt.subplots(figsize=(9, 6))

        sns.lineplot(
            data=df, 
            x="Window_Size", 
            y="Cycles", 
            marker="o", 
            color="teal" if mode == "Native" else "darkorange",
            linewidth=2.5, 
            markersize=6, 
            ax=ax
        )

        ax.set_title(f"Artemisia ROB Capacity Benchmark ({mode})", fontsize=13, weight="bold")
        ax.set_ylabel("Normalized Execution Cycles", fontsize=11)
        ax.set_xlabel("Instruction Window Size (N)", fontsize=11)

        plt.tight_layout()
        out_path = f"plots/enclave comparison/artemisia_{mode.lower()}_hw_rob.png"
        plt.savefig(out_path, dpi=300)
        plt.close()
        print(f"Saved {mode} ROB plot: {out_path}")
    else:
        print(f"File not found: {path}")