#!/bin/bash

SRC_DIR="src/branch"
DATA_DIR="data/branch"
mkdir -p "$DATA_DIR"

CSV_FILE="$DATA_DIR/$(hostname -s)_branch.csv"

echo "Compiling branch prediction benchmark..."
gcc -O3 "$SRC_DIR/branch_pred.c" -o "$SRC_DIR/branch_pred"

echo "Running branch prediction benchmark on $(hostname)..."
"$SRC_DIR/branch_pred" > "$CSV_FILE"

echo "Branch benchmark complete! Saved to $CSV_FILE"
