#!/bin/bash

SRC_DIR="src/q3_rob"
DATA_DIR="data/q3_rob"

mkdir -p "$DATA_DIR"

CSV_FILE="$DATA_DIR/$(hostname -s)_rob_fine.csv"
echo "Machine,Window_Size,Cycles" > "$CSV_FILE"

echo "Compiling fine-grained ROB test..."
gcc -O0 "$SRC_DIR/rob_fine_test.c" -o "$SRC_DIR/rob_fine_test"

echo "Running fine-grained ROB benchmark on $(hostname)..."
"$SRC_DIR/rob_fine_test" | tail -n +2 | while IFS=',' read -r size cycles; do
    echo "$(hostname),$size,$cycles" >> "$CSV_FILE"
done

echo "Fine-grained ROB benchmark complete! Data saved to $CSV_FILE"
