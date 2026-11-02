#include <stdio.h>
#include <stdint.h>

static inline uint64_t get_cycles(void) {
    uint32_t cycles_high, cycles_low;
    __asm__ volatile ("lfence\n\t" "rdtsc\n\t" : "=a" (cycles_low), "=d" (cycles_high) :: "memory");
    return ((uint64_t)cycles_high << 32) | cycles_low;
}

static inline uint64_t get_cycles_end(void) {
    uint32_t cycles_high, cycles_low;
    __asm__ volatile ("rdtsc\n\t" "lfence\n\t" : "=a" (cycles_low), "=d" (cycles_high) :: "memory");
    return ((uint64_t)cycles_high << 32) | cycles_low;
}

int main() {
    printf("ROB ALU Window Size,Total Cycles\n");
    int window_sizes[] = {128, 136, 144, 152, 160, 168, 176, 184, 192, 200, 208, 216, 224, 232, 240, 248, 256, 264, 272, 280, 288};
    int num_tests = sizeof(window_sizes) / sizeof(window_sizes[0]);

    for (int t = 0; t < num_tests; t++) {
        int n = window_sizes[t];
        uint64_t start, end;
        unsigned long long total_cycles = 0;
        int iterations = 1000;

        for (int iter = 0; iter < iterations; iter++) {
            start = get_cycles();
            __asm__ volatile ("sqrtsd %%xmm0, %%xmm1\n\t" ::: "xmm1", "memory");
            for (int i = 0; i < n; i++) {
                __asm__ volatile ("add $1, %%rax\n\t" ::: "rax", "memory");
            }
            end = get_cycles_end();
            total_cycles += (end - start);
        }
        printf("%d,%llu\n", n, total_cycles / iterations);
    }
    return 0;
}
