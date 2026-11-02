#!/bin/bash

SRC_DIR="src/tlb"
DATA_DIR="data/tlb"
mkdir -p "$DATA_DIR"

CSV_FILE="$DATA_DIR/$(hostname -s)_tlb.csv"

echo "Compiling TLB benchmark..."
gcc -O3 "$SRC_DIR/tlb_size.c" -o "$SRC_DIR/tlb_size"

echo "Running TLB benchmark on $(hostname)..."
"$SRC_DIR/tlb_size" > "$CSV_FILE"

echo "TLB benchmark complete! Saved to $CSV_FILE"
