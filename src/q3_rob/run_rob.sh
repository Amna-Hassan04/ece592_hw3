#!/bin/bash

SRC_DIR="src/q3_rob"
DATA_DIR="data/q3_rob"

mkdir -p "$DATA_DIR"

CSV_FILE="$DATA_DIR/$(hostname -s)_rob_alu.csv"
echo "Machine,Window_Size,Cycles" > "$CSV_FILE"

echo "Compiling ROB ALU test..."
gcc -O0 "$SRC_DIR/rob_alu_test.c" -o "$SRC_DIR/rob_alu_test"

echo "Running ROB ALU benchmark on $(hostname)..."
# Read the compiled binary output line by line, setting comma as IFS delimiter
"$SRC_DIR/rob_alu_test" | tail -n +2 | while IFS=',' read -r size cycles; do
    echo "$(hostname),$size,$cycles" >> "$CSV_FILE"
done

echo "ROB benchmark complete! Data saved to $CSV_FILE"
