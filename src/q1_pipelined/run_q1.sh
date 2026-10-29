#!/bin/bash

SRC_DIR="src/q1_pipelined"
DATA_DIR="data/q1_pipelined"

mkdir -p "$DATA_DIR"

CSV_FILE="$DATA_DIR/$(hostname -s)_q1.csv"
echo "Machine,Iteration,Dependent_Cycles,Independent_Cycles,Ratio" > "$CSV_FILE"

echo "Compiling pipeline test..."
gcc -O0 "$SRC_DIR/pipeline_test.c" -o "$SRC_DIR/pipeline_test"

echo "Running pipeline benchmark on $(hostname)..."
for i in {1..10}
do
    OUTPUT=$("$SRC_DIR/pipeline_test")
    # Column 7 contains the cycle count value
    DEP_CYCLES=$(echo "$OUTPUT" | grep "Dependent Chain" | awk '{print $7}')
    IND_CYCLES=$(echo "$OUTPUT" | grep "Independent Stream" | awk '{print $7}')
    RATIO=$(echo "$OUTPUT" | grep "Ratio" | awk '{print $3}')
    
    echo "$(hostname),$i,$DEP_CYCLES,$IND_CYCLES,$RATIO" >> "$CSV_FILE"
done

echo "Benchmark complete! Data saved to $CSV_FILE"
