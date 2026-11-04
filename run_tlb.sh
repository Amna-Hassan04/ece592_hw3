#!/bin/bash
SRC_DIR="src/tlb"
DATA_DIR="data/tlb"
mkdir -p "$DATA_DIR"
CSV_FILE="$DATA_DIR/$(hostname -s)_tlb.csv"
gcc -O3 "$SRC_DIR/tlb_size.c" -o "$SRC_DIR/tlb_size"
"$SRC_DIR/tlb_size" > "$CSV_FILE"
echo "TLB benchmark saved to $CSV_FILE"
