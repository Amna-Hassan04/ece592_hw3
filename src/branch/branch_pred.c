#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>

static inline unsigned long long rdtsc() {
    unsigned int lo, hi;
    __asm__ volatile ("lfence\n\t" ".byte 0x0f, 0x31" : "=a" (lo), "=d" (hi));
    return ((unsigned long long)hi << 32) | lo;
}

int compare_ints(const void *a, const void *b) {
    int arg1 = *(const int *)a;
    int arg2 = *(const int *)b;
    if (arg1 < arg2) return -1;
    if (arg1 > arg2) return 1;
    return 0;
}

int main() {
    size_t n = 32768;
    int *data = (int *)malloc(n * sizeof(int));
    int *sorted_data = (int *)malloc(n * sizeof(int));

    srand(42);
    for (size_t i = 0; i < n; i++) {
        int val = rand() % 100;
        data[i] = val;
        sorted_data[i] = val;
    }
    qsort(sorted_data, n, sizeof(int), compare_ints);

    int threshold = 50;
    volatile unsigned long long sum = 0;
    int iterations = 1000;

    unsigned long long start_random = rdtsc();
    for (int it = 0; it < iterations; it++) {
        for (size_t i = 0; i < n; i++) {
            if (data[i] > threshold) sum += data[i];
        }
    }
    unsigned long long random_cycles = rdtsc() - start_random;

    unsigned long long start_sorted = rdtsc();
    for (int it = 0; it < iterations; it++) {
        for (size_t i = 0; i < n; i++) {
            if (sorted_data[i] > threshold) sum += sorted_data[i];
        }
    }
    unsigned long long sorted_cycles = rdtsc() - start_sorted;

    char hostname[256];
    gethostname(hostname, sizeof(hostname));

    printf("Machine,Branch_Type,Cycles\n");
    printf("%s,Unsorted_Random,%llu\n", hostname, random_cycles);
    printf("%s,Sorted,%llu\n", hostname, sorted_cycles);

    free(data); free(sorted_data);
    return 0;
}
