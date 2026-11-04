#!/bin/bash
set -e

echo "=== 1. Cleaning and Building SGX Enclave & App == "
make clean
make

echo "=== 2. Creating Data Directory ==="
mkdir -p data/sgx_comparison

echo "=== 3. Executing Enclave Benchmark Suite ==="
./app

echo "=== All experiments completed successfully! Results are in data/sgx_comparison/ ==="
