#!/bin/bash
SRC_DIR="src/q3_rob"
DATA_DIR="data/q3_rob"
mkdir -p "$DATA_DIR"
CSV_FILE="$DATA_DIR/$(hostname -s)_hw_rob.csv"
echo "Machine,Window_Size,Cycles" > "$CSV_FILE"
gcc -O3 "$SRC_DIR/robsize_hw.c" -o "$SRC_DIR/robsize_hw"
"$SRC_DIR/robsize_hw" 4 | tail -n +2 | while IFS=',' read -r size cycles; do
    echo "$(hostname),$size,$cycles" >> "$CSV_FILE"
done
echo "ROB benchmark saved to $CSV_FILE"
