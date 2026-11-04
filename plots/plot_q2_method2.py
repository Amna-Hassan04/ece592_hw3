#!/usr/bin/env python3
import csv
import glob
import os
import matplotlib.pyplot as plt

csv_files = glob.glob("**/*_q2.csv", recursive=True) + glob.glob("data/**/*q2*.csv")
csv_files = sorted(list(set(csv_files)))

rows = []
for fpath in csv_files:
    with open(fpath, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                hostname = row.get("hostname", row.get("Machine", os.path.basename(fpath)))
                row["host_short"] = str(hostname).split(".")[0].lower()
                row["num_independent_insts"] = int(row["num_independent_insts"])
                row["rdtscp_cycles"] = float(row["rdtscp_cycles"])
                rows.append(row)
            except Exception:
                pass

hosts = sorted(list(set(r["host_short"] for r in rows)))
PLOT_DIR = "plots/q2"
os.makedirs(PLOT_DIR, exist_ok=True)

# Generate standalone wide figure for Method 2 with extra right margin for the legend
fig, ax = plt.subplots(figsize=(11, 6))

markers = ["o", "s", "^", "D", "v", "p", "*", "X"]

for idx, h in enumerate(hosts):
    sub = [r for r in rows if r["host_short"] == h and r.get("method") == "Method2_DRAM"]
    sub.sort(key=lambda r: r["num_independent_insts"])

    if not sub:
        continue

    n_vals = [r["num_independent_insts"] for r in sub]
    c_vals = [r["rdtscp_cycles"] for r in sub]

    marker_style = markers[idx % len(markers)]
    
    # Plot measured OoO line
    ax.plot(n_vals, c_vals, marker=marker_style, linewidth=2,
             label=f"{h} (Measured)")

    # Plot theoretical In-Order baseline
    if c_vals:
        base_dram = c_vals[0]
        expected_inorder = [base_dram + n for n in n_vals]
        ax.plot(n_vals, expected_inorder, linestyle="--", alpha=0.5,
                 label=f"{h} (Expected In-Order)")

ax.set_xlabel("Number of Chained Independent ADDs (N)", fontsize=11, fontweight="bold")
ax.set_ylabel("Total Elapsed Cycles (RDTSCP)", fontsize=11, fontweight="bold")
ax.set_title("Method 2: DRAM Cache Miss Latency Hiding Benchmark", fontsize=13, fontweight="bold", pad=15)

# Place legend outside the plot area on the right so it never overlaps graph lines
ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=9, frameon=True)
ax.grid(True, linestyle="--", alpha=0.6)

# Adjust layout to accommodate external legend
plt.tight_layout()
png_path = os.path.join(PLOT_DIR, "q2_method2_dram.png")
plt.savefig(png_path, dpi=300, bbox_inches="tight")
plt.close()
print(f"Saved standalone Method 2 plot to: {png_path}")