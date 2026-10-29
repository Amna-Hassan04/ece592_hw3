#!/bin/bash
HOST=$(hostname -s)
OUT_DIR=~/ece592_hw3/data/q2_ooo
mkdir -p "$OUT_DIR"

echo "=== Collecting System & Enclave Info for $HOST ==="
{
    echo "Hostname: $(hostname)"
    echo "Date: $(date)"
    echo "--- CPU Info ---"
    lscpu | grep -E "Model name|Architecture|Socket|Core\(s\) per socket|Thread\(s\) per core|CPU family|Model:|Stepping"
    echo "--- Enclave / SGX / SEV Hardware Support ---"
    grep -E "sgx|sev" /proc/cpuinfo | head -n 2 || echo "No SGX/SEV flags in /proc/cpuinfo"
    ls -l /dev/sgx* /dev/isgx 2>/dev/null || echo "No /dev/sgx* device nodes present"
    echo "--- Perf Paranoia Level ---"
    cat /proc/sys/kernel/perf_event_paranoid
} | tee "$OUT_DIR/${HOST}_sysinfo.txt"

echo ""
echo "=== Compiling and Running Question 2 Experiment ==="
gcc -O2 q2_ooo.c -o q2_ooo
./q2_ooo "$OUT_DIR/${HOST}_q2.csv" | tee "$OUT_DIR/${HOST}_q2_output.txt"
