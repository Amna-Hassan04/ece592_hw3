#!/usr/bin/env python3
import csv
import glob
import os
import matplotlib.pyplot as plt

# Recursively find all *_q2.csv files anywhere in the repository structure
csv_files = glob.glob("**/*_q2.csv", recursive=True) + glob.glob("data/**/*q2*.csv")
csv_files = sorted(list(set(csv_files)))

print(f"Found Q2 CSV files: {csv_files}")

if not csv_files:
    print("Error: No Q2 CSV files found! Check your working directory.")
    exit(1)

# Read all rows using Python's standard csv module
rows = []
for fpath in csv_files:
    print(f"Reading file: {fpath}")
    with open(fpath, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # Handle possible hostname column variations or fallbacks
                hostname = row.get("hostname", row.get("Machine", os.path.basename(fpath)))
                row["host_short"] = str(hostname).split(".")[0].lower()
                
                row["num_independent_insts"] = int(row["num_independent_insts"])
                row["rdtscp_cycles"] = float(row["rdtscp_cycles"])
                rows.append(row)
            except Exception as e:
                print(f"Skipping malformed row in {fpath}: {e} -> {row}")

print(f"Total parsed rows: {len(rows)}")
if not rows:
    print("Error: Parsed 0 valid rows from the CSV files. Check CSV columns!")
    exit(1)

# Get unique sorted hostnames
hosts = sorted(list(set(r["host_short"] for r in rows)))
print(f"Detected hosts: {hosts}")

# Setup target plot directory: plots/q2/
PLOT_DIR = "plots/q2"
os.makedirs(PLOT_DIR, exist_ok=True)

# Create a 1x2 figure: Left = Method 1 (ALU Bar Chart), Right = Method 2 (DRAM Sweep Line Plot)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# ----------------------------------------------------------------------------
# Subplot 1: Method 1 (SQRTSD + 16 Dependent vs. 16 Independent ADDs)
# ----------------------------------------------------------------------------
x = list(range(len(hosts)))
width = 0.35

dep_vals = []
ind_vals = []
for h in hosts:
    dep = [r["rdtscp_cycles"] for r in rows if r["host_short"] == h and r.get("method") == "Method1_ALU" and r.get("variant") == "Dependent"]
    ind = [r["rdtscp_cycles"] for r in rows if r["host_short"] == h and r.get("method") == "Method1_ALU" and r.get("variant") == "Independent"]
    dep_vals.append(dep[0] if dep else 0.0)
    ind_vals.append(ind[0] if ind else 0.0)

rects1 = ax1.bar([pos - width/2 for pos in x], dep_vals, width, label="1A: SQRTSD + 16 Dependent ADDs", color="#d95f02")
rects2 = ax1.bar([pos + width/2 for pos in x], ind_vals, width, label="1B: SQRTSD + 16 Independent ADDs", color="#1b9e77")

ax1.set_ylabel("Cycles per Iteration (RDTSCP)")
ax1.set_title("Method 1: Long-Latency ALU Latency Hiding")
ax1.set_xticks(x)
ax1.set_xticklabels(hosts)
ax1.legend()
ax1.grid(axis="y", linestyle="--", alpha=0.6)

for rect in list(rects1) + list(rects2):
    h = rect.get_height()
    if h > 0:
        ax1.annotate(f"{h:.2f}",
                     xy=(rect.get_x() + rect.get_width() / 2, h),
                     xytext=(0, 3), textcoords="offset points",
                     ha="center", va="bottom", fontsize=9)

# ----------------------------------------------------------------------------
# Subplot 2: Method 2 (DRAM Cache Miss + N Independent ADDs Sweep)
# ----------------------------------------------------------------------------
markers = ["o", "s", "^", "D"]

for idx, h in enumerate(hosts):
    sub = [r for r in rows if r["host_short"] == h and r.get("method") == "Method2_DRAM"]
    sub.sort(key=lambda r: r["num_independent_insts"])

    if not sub:
        continue

    n_vals = [r["num_independent_insts"] for r in sub]
    c_vals = [r["rdtscp_cycles"] for r in sub]

    ax2.plot(n_vals, c_vals, marker=markers[idx % len(markers)], linewidth=2,
             label=f"{h} (Measured OoO)")

    if c_vals:
        base_dram = c_vals[0]
        expected_inorder = [base_dram + n for n in n_vals]
        ax2.plot(n_vals, expected_inorder, linestyle="--", alpha=0.6,
                 label=f"{h} (Expected In-Order)")

ax2.set_xlabel("Number of Chained Independent ADDs (N)")
ax2.set_ylabel("Total Elapsed Cycles (RDTSCP)")
ax2.set_title("Method 2: DRAM Cache Miss Latency Hiding")
ax2.legend()
ax2.grid(True, linestyle="--", alpha=0.6)

plt.tight_layout()
png_path = os.path.join(PLOT_DIR, "q2_ooo_comparison.png")
pdf_path = os.path.join(PLOT_DIR, "q2_ooo_comparison.pdf")
plt.savefig(png_path, dpi=300)
plt.savefig(pdf_path)
print(f"Successfully saved Q2 plots to:\n  {png_path}\n  {pdf_path}")