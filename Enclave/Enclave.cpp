#include "Enclave_t.h"
#include "sgx_trts.h"
#include <stdint.h>

static inline uint64_t get_cycles(void) {
    uint32_t cycles_high, cycles_low;
    __asm__ volatile (
        "lfence\n\t"
        "rdtsc\n\t"
        : "=a" (cycles_low), "=d" (cycles_high)
        : 
        : "memory"
    );
    return ((uint64_t)cycles_high << 32) | cycles_low;
}

static inline uint64_t get_cycles_end(void) {
    uint32_t cycles_high, cycles_low;
    __asm__ volatile (
        "rdtsc\n\t"
        "lfence\n\t"
        : "=a" (cycles_low), "=d" (cycles_high)
        : 
        : "memory"
    );
    return ((uint64_t)cycles_high << 32) | cycles_low;
}

// 1. Pipeline Test ECall
void ecall_run_pipeline(uint64_t *dependent_time, uint64_t *independent_time) {
    uint64_t start, end;

    // Dependent instruction chain
    start = get_cycles();
    __asm__ volatile (
        "mov $0, %%rax\n\t"
        ".rept 1000\n\t"
        "add $1, %%rax\n\t"
        ".endr\n\t"
        : : : "rax", "memory"
    );
    end = get_cycles_end();
    *dependent_time = end - start;

    // Independent instruction stream
    start = get_cycles();
    __asm__ volatile (
        "mov $0, %%r8\n\t"
        "mov $0, %%r9\n\t"
        "mov $0, %%r10\n\t"
        "mov $0, %%r11\n\t"
        ".rept 250\n\t"
        "add $1, %%r8\n\t"
        "add $1, %%r9\n\t"
        "add $1, %%r10\n\t"
        "add $1, %%r11\n\t"
        ".endr\n\t"
        : : : "r8", "r9", "r10", "r11", "memory"
    );
    end = get_cycles_end();
    *independent_time = end - start;
}

// 2. Branch Prediction ECall
void ecall_run_branch(uint64_t *random_cycles, uint64_t *sorted_cycles) {
    size_t n = 4096; // Enclave-friendly size
    int data[4096];
    int sorted_data[4096];

    for (size_t i = 0; i < n; i++) {
        int val = (i * 33) % 100;
        data[i] = val;
        sorted_data[i] = val;
    }

    // Simple bubble sort for sorted version inside enclave
    for (size_t i = 0; i < n - 1; i++) {
        for (size_t j = 0; j < n - i - 1; j++) {
            if (sorted_data[j] > sorted_data[j + 1]) {
                int temp = sorted_data[j];
                sorted_data[j] = sorted_data[j + 1];
                sorted_data[j + 1] = temp;
            }
        }
    }

    int threshold = 50;
    volatile unsigned long long sum = 0;
    int iterations = 100;

    // Unsorted branch test
    uint64_t start = get_cycles();
    for (int it = 0; it < iterations; it++) {
        for (size_t i = 0; i < n; i++) {
            if (data[i] > threshold) sum += data[i];
        }
    }
    uint64_t end = get_cycles_end();
    *random_cycles = end - start;

    // Sorted branch test
    start = get_cycles();
    for (int it = 0; it < iterations; it++) {
        for (size_t i = 0; i < n; i++) {
            if (sorted_data[i] > threshold) sum += sorted_data[i];
        }
    }
    end = get_cycles_end();
    *sorted_cycles = end - start;
}
