#!/bin/bash
SRC_DIR="src/branch"
DATA_DIR="data/branch"
mkdir -p "$DATA_DIR"
CSV_FILE="$DATA_DIR/$(hostname -s)_branch.csv"
gcc -O3 "$SRC_DIR/branch_pred.c" -o "$SRC_DIR/branch_pred"
"$SRC_DIR/branch_pred" > "$CSV_FILE"
echo "Branch benchmark saved to $CSV_FILE"
