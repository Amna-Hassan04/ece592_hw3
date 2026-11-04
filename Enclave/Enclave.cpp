#include "Enclave_t.h"
#include <stdint.h>
#include <immintrin.h>

static inline uint64_t get_cycles_enclave(void) {
    unsigned int aux;
    return __rdtscp(&aux);
}

int enclave_pipeline_test(uint64_t iterations, uint64_t *dep_cycles, uint64_t *ind_cycles) {
    uint64_t start, end;
    (void)iterations;

    // --- 1. DEPENDENT INSTRUCTION CHAIN (Inside Enclave) ---
    start = get_cycles_enclave();
    __asm__ volatile (
        "mov $0, %%rax\n\t"
        ".rept 1000\n\t"
        "add $1, %%rax\n\t"
        ".endr\n\t"
        : : : "rax", "memory"
    );
    end = get_cycles_enclave();
    *dep_cycles = end - start;

    // --- 2. INDEPENDENT INSTRUCTION STREAM (Inside Enclave) ---
    start = get_cycles_enclave();
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
    end = get_cycles_enclave();
    *ind_cycles = end - start;

    return 0;
}
