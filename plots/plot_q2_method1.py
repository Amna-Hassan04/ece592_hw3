#!/usr/init/env python3
import csv
import glob
import os
import matplotlib.pyplot as plt

# Find all *_q2.csv files
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
                row["rdtscp_cycles"] = float(row["rdtscp_cycles"])
                rows.append(row)
            except Exception:
                pass

hosts = sorted(list(set(r["host_short"] for r in rows)))
PLOT_DIR = "plots/q2"
os.makedirs(PLOT_DIR, exist_ok=True)

# Generate standalone wide figure for Method 1
fig, ax = plt.subplots(figsize=(10, 6))

x = list(range(len(hosts)))
width = 0.35

dep_vals, ind_vals = [], []
for h in hosts:
    dep = [r["rdtscp_cycles"] for r in rows if r["host_short"] == h and r.get("method") == "Method1_ALU" and r.get("variant") == "Dependent"]
    ind = [r["rdtscp_cycles"] for r in rows if r["host_short"] == h and r.get("method") == "Method1_ALU" and r.get("variant") == "Independent"]
    dep_vals.append(dep[0] if dep else 0.0)
    ind_vals.append(ind[0] if ind else 0.0)

rects1 = ax.bar([pos - width/2 for pos in x], dep_vals, width, label="1A: SQRTSD + 16 Dependent ADDs", color="#d95f02")
rects2 = ax.bar([pos + width/2 for pos in x], ind_vals, width, label="1B: SQRTSD + 16 Independent ADDs", color="#1b9e77")

ax.set_ylabel("Cycles per Iteration (RDTSCP)", fontsize=11, fontweight="bold")
ax.set_title("Method 1: Long-Latency ALU Latency Hiding Benchmark", fontsize=13, fontweight="bold", pad=15)
ax.set_xticks(x)
ax.set_xticklabels(hosts, fontsize=10, rotation=15, ha="right")
ax.legend(loc="upper left", fontsize=10)
ax.grid(axis="y", linestyle="--", alpha=0.6)

# Give extra headroom at the top so annotations don't cut off
max_val = max(dep_vals + ind_vals) if (dep_vals or ind_vals) else 60
ax.set_ylim(0, max_val * 1.15)

# Add clean numerical annotations on top of bars
for rect in list(rects1) + list(rects2):
    h = rect.get_height()
    if h > 0:
        ax.annotate(f"{h:.2f}",
                     xy=(rect.get_x() + rect.get_width() / 2, h),
                     xytext=(0, 4), textcoords="offset points",
                     ha="center", va="bottom", fontsize=9, fontweight="bold")

plt.tight_layout()
png_path = os.path.join(PLOT_DIR, "q2_method1_alu.png")
plt.savefig(png_path, dpi=300)
plt.close()
print(f"Saved standalone Method 1 plot to: {png_path}")