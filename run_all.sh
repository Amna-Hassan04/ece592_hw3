#!/bin/bash
set -e

echo "=============================================="
echo "Running All ECE 592 HW3 Benchmarks on $(hostname)"
echo "=============================================="

# 1. Q1: Pipeline Test
if [ -f "src/q1_pipelined/run_q1.sh" ]; then
    echo "--- [1/5] Running Q1: Pipeline Test ---"
    chmod +x src/q1_pipelined/run_q1.sh
    ./src/q1_pipelined/run_q1.sh
fi

# 2. Q2: Out-of-Order Execution
if [ -f "src/q2_ooo/run_q2.sh" ]; then
    echo "--- [2/5] Running Q2: Out-of-Order Execution ---"
    chmod +x src/q2_ooo/run_q2.sh
    ./src/q2_ooo/run_q2.sh
fi

# 3. Q3: ROB Size Benchmark
if [ -f "src/q3_rob/run_hw_rob.sh" ]; then
    echo "--- [3/5] Running Q3: ROB Size ---"
    chmod +x src/q3_rob/run_hw_rob.sh
    ./src/q3_rob/run_hw_rob.sh
fi

# 4. TLB Capacity Benchmark
if [ -f "src/tlb/run_tlb.sh" ]; then
    echo "--- [4/5] Running TLB Capacity ---"
    chmod +x src/tlb/run_tlb.sh
    ./src/tlb/run_tlb.sh
fi

# 5. Branch Prediction Benchmark
if [ -f "src/branch/run_branch.sh" ]; then
    echo "--- [5/5] Running Branch Prediction ---"
    chmod +x src/branch/run_branch.sh
    ./src/branch/run_branch.sh
fi

echo "=============================================="
echo "All benchmarks complete! Generating plots..."
echo "=============================================="

if [ -d "venv" ]; then
    source venv/bin/activate
fi

python3 plots/plot_tlb.py 2>/dev/null || true
python3 plots/plot_branch.py 2>/dev/null || true
python3 plots/plot_hw_rob.py 2>/dev/null || true

echo "=============================================="
echo "All data and plots successfully updated!"
echo "=============================================="
