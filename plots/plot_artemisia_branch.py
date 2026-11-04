import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

os.makedirs("plots/enclave comparison", exist_ok=True)

files = {
    "Native": "data/branch/artemisia_branch.csv",
    "Enclave": "data/branch/artemisia_branch_enclave.csv"
}

for mode, path in files.items():
    if os.path.exists(path):
        df = pd.read_csv(path)
        df.columns = df.columns.str.strip()
        
        sns.set_theme(style="whitegrid")
        fig, ax = plt.subplots(figsize=(8, 6))

        sns.barplot(
            data=df, 
            x="Branch_Type", 
            y="Cycles", 
            palette=["#e74c3c", "#2ecc71"],
            ax=ax
        )

        ax.set_title(f"Artemisia Branch Prediction ({mode})", fontsize=13, weight="bold")
        ax.set_ylabel("Execution Cycles (Lower is Better)", fontsize=11)
        ax.set_xlabel("Branch Behavior Type", fontsize=11)

        plt.tight_layout()
        out_path = f"plots/enclave comparison/artemisia_{mode.lower()}_branch_prediction.png"
        plt.savefig(out_path, dpi=300)
        plt.close()
        print(f"Saved {mode} branch plot: {out_path}")
    else:
        print(f"File not found: {path}")