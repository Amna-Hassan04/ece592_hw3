#include <stdio.h>
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

int main() {
    uint64_t start_cycles, end_cycles;

    // --- TEST 1: DEPENDENT INSTRUCTION CHAIN ---
    start_cycles = get_cycles();
    __asm__ volatile (
        "mov $0, %%rax\n\t"
        ".rept 1000\n\t"
        "add $1, %%rax\n\t"
        ".endr\n\t"
        : 
        : 
        : "rax", "memory"
    );
    end_cycles = get_cycles_end();
    uint64_t dependent_time = end_cycles - start_cycles;

    // --- TEST 2: INDEPENDENT INSTRUCTION STREAM ---
    start_cycles = get_cycles();
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
        : 
        : 
        : "r8", "r9", "r10", "r11", "memory"
    );
    end_cycles = get_cycles_end();
    uint64_t independent_time = end_cycles - start_cycles;

    printf("--- Pipeline Verification Test ---\n");
    printf("Dependent Chain Cycles for 1000 instructions: %lu cycles\n", dependent_time);
    printf("Independent Stream Cycles for 1000 instructions: %lu cycles\n", independent_time);
    printf("Ratio (Dependent / Independent): %.2f\n", (double)dependent_time / independent_time);

    return 0;
}
