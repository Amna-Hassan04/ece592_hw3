#!/bin/bash

SRC_DIR="src/q3_rob"
DATA_DIR="data/q3_rob"
mkdir -p "$DATA_DIR"

CSV_FILE="$DATA_DIR/$(hostname -s)_hw_rob.csv"
echo "Machine,Window_Size,Cycles" > "$CSV_FILE"

echo "Compiling Henry Wong's ROB benchmark..."
gcc -O3 "$SRC_DIR/robsize_hw.c" -o "$SRC_DIR/robsize_hw"

echo "Running benchmark on $(hostname)..."
# Test type 4 is two-byte nop (standard for ROB size measurement)
"$SRC_DIR/robsize_hw" 4 | tail -n +2 | while IFS=',' read -r size cycles; do
    echo "$(hostname),$size,$cycles" >> "$CSV_FILE"
done

echo "Benchmark complete! Saved to $CSV_FILE"
