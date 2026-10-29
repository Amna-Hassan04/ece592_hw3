#!/usr/bin/env python3
import csv                          # Built-in Python CSV reader (no pandas required!)
import glob                         # Finds all *_q2.csv files in our data directory
import os                           # Handles file paths
import matplotlib.pyplot as plt     # Generates publication-quality plots

# Paths where run_q2.sh saves CSV files and where plots will be saved
DATA_DIR = os.path.expanduser("~/ece592_hw3/data/q2_ooo")
PLOT_DIR = os.path.expanduser("~/ece592_hw3/plots")
os.makedirs(PLOT_DIR, exist_ok=True)

# Find all CSV files matching *_q2.csv in the data folder
csv_files = sorted(glob.glob(os.path.join(DATA_DIR, "*_q2.csv")))
if not csv_files:
    print(f"No CSV files found in {DATA_DIR}!")
    exit(1)

# Read all rows using Python's standard csv module
rows = []
for fpath in csv_files:
    with open(fpath, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["host_short"] = row["hostname"].split(".")[0]
            row["num_independent_insts"] = int(row["num_independent_insts"])
            row["rdtscp_cycles"] = float(row["rdtscp_cycles"])
            rows.append(row)

# Get unique sorted hostnames
hosts = sorted(list(set(r["host_short"] for r in rows)))

# Create a 1x2 figure: Left = Method 1 (ALU Bar Chart), Right = Method 2 (DRAM Sweep Line Plot)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# ----------------------------------------------------------------------------
# Subplot 1: Method 1 (SQRTSD + 16 Dependent vs. 16 Independent ADDs)
# ----------------------------------------------------------------------------
x = list(range(len(hosts)))
width = 0.35

dep_vals = []
ind_vals = []
for h in hosts:
    dep = [r["rdtscp_cycles"] for r in rows if r["host_short"] == h and r["method"] == "Method1_ALU" and r["variant"] == "Dependent"]
    ind = [r["rdtscp_cycles"] for r in rows if r["host_short"] == h and r["method"] == "Method1_ALU" and r["variant"] == "Independent"]
    dep_vals.append(dep[0] if dep else 0.0)
    ind_vals.append(ind[0] if ind else 0.0)

rects1 = ax1.bar([pos - width/2 for pos in x], dep_vals, width, label="1A: SQRTSD + 16 Dependent ADDs", color="#d95f02")
rects2 = ax1.bar([pos + width/2 for pos in x], ind_vals, width, label="1B: SQRTSD + 16 Independent ADDs", color="#1b9e77")

ax1.set_ylabel("Cycles per Iteration (RDTSCP)")
ax1.set_title("Method 1: Long-Latency ALU (SQRTSD) Latency Hiding")
ax1.set_xticks(x)
ax1.set_xticklabels(hosts)
ax1.legend()
ax1.grid(axis="y", linestyle="--", alpha=0.6)

# Add exact cycle numbers on top of each bar
for rect in list(rects1) + list(rects2):
    h = rect.get_height()
    ax1.annotate(f"{h:.2f}",
                 xy=(rect.get_x() + rect.get_width() / 2, h),
                 xytext=(0, 3), textcoords="offset points",
                 ha="center", va="bottom", fontsize=9)

# ----------------------------------------------------------------------------
# Subplot 2: Method 2 (DRAM Cache Miss + N Independent ADDs Sweep)
# ----------------------------------------------------------------------------
markers = ["o", "s", "^", "D"]

for idx, h in enumerate(hosts):
    sub = [r for r in rows if r["host_short"] == h and r["method"] == "Method2_DRAM"]
    sub.sort(key=lambda r: r["num_independent_insts"])

    n_vals = [r["num_independent_insts"] for r in sub]
    c_vals = [r["rdtscp_cycles"] for r in sub]

    ax2.plot(n_vals, c_vals, marker=markers[idx % len(markers)], linewidth=2,
             label=f"{h} (Measured OoO)")

    # Plot theoretical In-Order baseline (+1 cycle per sequential ADD instruction)
    if c_vals:
        base_dram = c_vals[0]
        expected_inorder = [base_dram + n for n in n_vals]
        ax2.plot(n_vals, expected_inorder, linestyle="--", alpha=0.6,
                 label=f"{h} (Expected if In-Order)")

ax2.set_xlabel("Number of Chained Independent ADDs (N) After DRAM Load")
ax2.set_ylabel("Total Elapsed Cycles (RDTSCP)")
ax2.set_title("Method 2: DRAM Cache Miss Latency Hiding")
ax2.set_xticks([0, 8, 16, 32, 64])
ax2.legend()
ax2.grid(True, linestyle="--", alpha=0.6)

plt.tight_layout()
png_path = os.path.join(PLOT_DIR, "q2_ooo_comparison.png")
pdf_path = os.path.join(PLOT_DIR, "q2_ooo_comparison.pdf")
plt.savefig(png_path, dpi=300)
plt.savefig(pdf_path)
print(f"Saved plots to:\n  {png_path}\n  {pdf_path}")
