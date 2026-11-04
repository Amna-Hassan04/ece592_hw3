import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

os.makedirs("plots/enclave comparison", exist_ok=True)

files = {
    "Native": "data/tlb/artemisia_tlb.csv",
    "Enclave": "data/tlb/artemisia_tlb_enclave.csv"
}

for mode, path in files.items():
    if os.path.exists(path):
        df = pd.read_csv(path)
        df.columns = df.columns.str.strip()
        
        sns.set_theme(style="whitegrid")
        fig, ax = plt.subplots(figsize=(9, 6))

        sns.lineplot(
            data=df, 
            x="Pages", 
            y="Avg_Cycles_Per_Access", 
            marker="o", 
            color="m" if mode == "Native" else "b",
            linewidth=2.5, 
            markersize=6, 
            errorbar=None,
            ax=ax
        )

        ax.set_title(f"Artemisia TLB Capacity & Hierarchy ({mode})", fontsize=13, weight="bold")
        ax.set_ylabel("Average Latency per Access (Cycles)", fontsize=11)
        ax.set_xlabel("Working Set Size (Number of 4KB Pages)", fontsize=11)

        plt.tight_layout()
        out_path = f"plots/enclave comparison/artemisia_{mode.lower()}_tlb_capacity.png"
        plt.savefig(out_path, dpi=300)
        plt.close()
        print(f"Saved {mode} TLB plot: {out_path}")
    else:
        print(f"File not found: {path}")