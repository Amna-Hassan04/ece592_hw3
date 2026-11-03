#!/bin/bash
set -e

echo "=============================================="
echo "Running Data Collection Benchmarks on $(hostname)"
echo "=============================================="

if [ -f "src/q1_pipelined/run_q1.sh" ]; then
echo "--- Running Q1: Pipeline Test ---"
chmod +x src/q1_pipelined/run_q1.sh
./src/q1_pipelined/run_q1.sh
fi

if [ -f "src/q2_ooo/run_q2.sh" ]; then
echo "--- Running Q2: Out-of-Order Execution ---"
chmod +x src/q2_ooo/run_q2.sh
./src/q2_ooo/run_q2.sh
fi

if [ -f "src/q3_rob/run_hw_rob.sh" ]; then
echo "--- Running Q3: ROB Size ---"
chmod +x src/q3_rob/run_hw_rob.sh
./src/q3_rob/run_hw_rob.sh
fi

if [ -f "src/tlb/run_tlb.sh" ]; then
echo "--- Running TLB Capacity ---"
chmod +x src/tlb/run_tlb.sh
./src/tlb/run_tlb.sh
fi

if [ -f "src/branch/run_branch.sh" ]; then
echo "--- Running Branch Prediction ---"
chmod +x src/branch/run_branch.sh
./src/branch/run_branch.sh
fi

echo "=============================================="
echo "All benchmarks completed! CSV data successfully saved."
echo "=============================================="
