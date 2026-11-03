#!/bin/bash
set -e

echo "=============================================="
echo "Running All ECE 592 HW3 Benchmarks on $(hostname)"
echo "=============================================="

if [ -f "src/q1_pipelined/run_q1.sh" ]; then
chmod +x src/q1_pipelined/run_q1.sh
./src/q1_pipelined/run_q1.sh
fi

if [ -f "src/q2_ooo/run_q2.sh" ]; then
chmod +x src/q2_ooo/run_q2.sh
./src/q2_ooo/run_q2.sh
fi

if [ -f "src/q3_rob/run_hw_rob.sh" ]; then
chmod +x src/q3_rob/run_hw_rob.sh
./src/q3_rob/run_hw_rob.sh
fi

if [ -f "src/tlb/run_tlb.sh" ]; then
chmod +x src/tlb/run_tlb.sh
./src/tlb/run_tlb.sh
fi

if [ -f "src/branch/run_branch.sh" ]; then
chmod +x src/branch/run_branch.sh
./src/branch/run_branch.sh
fi

if [ -d "venv" ]; then
source venv/bin/activate
fi

python3 plots/plot_tlb.py 2>/dev/null || true
python3 plots/plot_branch.py 2>/dev/null || true
python3 plots/plot_hw_rob.py 2>/dev/null || true

echo "All benchmarks complete and plots updated!"
