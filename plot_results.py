import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('data/sgx_comparison/artemisia_sgx_comparison.csv')

fig, ax = plt.subplots(figsize=(8, 5))
width = 0.35
x = range(len(df))

bars1 = ax.bar([i - width/2 for i in x], df['Dependent_Cycles'], width, label='Dependent Cycles', color='#1f77b4', edgecolor='black', linewidth=0.6)
bars2 = ax.bar([i + width/2 for i in x], df['Independent_Cycles'], width, label='Independent Cycles', color='#ff7f0e', edgecolor='black', linewidth=0.6)

ax.set_xlabel('Execution Mode', fontweight='bold', fontsize=12)
ax.set_ylabel('Cycle Count', fontweight='bold', fontsize=12)
ax.set_title('Intel SGX Enclave vs. Outside Enclave Performance', fontsize=14, fontweight='bold', pad=15)
ax.set_xticks(list(x))
ax.set_xticklabels(df['Execution_Mode'], fontsize=11)
ax.legend(frameon=True, fontsize=11, loc='upper left')

ax.set_axisbelow(True)
ax.yaxis.grid(True, linestyle='--', alpha=0.7)

for bar in bars1:
    height = bar.get_height()
    ax.annotate(f'{height}', xy=(bar.get_x() + bar.get_width() / 2, height), xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight='semibold')

for bar in bars2:
    height = bar.get_height()
    ax.annotate(f'{height}', xy=(bar.get_x() + bar.get_width() / 2, height), xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight='semibold')

plt.tight_layout()
plt.savefig('data/sgx_comparison/sgx_comparison_plot.png', dpi=300)
plt.savefig('data/sgx_comparison/sgx_comparison_plot.pdf')
print("Plot successfully generated and saved to data/sgx_comparison/sgx_comparison_plot.png (.pdf)")
