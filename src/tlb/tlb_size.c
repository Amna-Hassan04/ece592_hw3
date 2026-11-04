#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <sys/mman.h>
#include <unistd.h>

static inline unsigned long long rdtsc() {
    unsigned int lo, hi;
    __asm__ volatile ("lfence\n\t" ".byte 0x0f, 0x31" : "=a" (lo), "=d" (hi));
    return ((unsigned long long)hi << 32) | lo;
}

static inline void my_rand_shuffle(size_t *arr, size_t n) {
    for (size_t i = n - 1; i > 0; i--) {
        size_t j = rand() % (i + 1);
        size_t temp = arr[i];
        arr[i] = arr[j];
        arr[j] = temp;
    }
}

int main() {
    size_t page_size = 4096;
    size_t max_pages = 2048;
    size_t total_bytes = max_pages * page_size;

    char *buffer = (char *)mmap(NULL, total_bytes, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    size_t *indices = (size_t *)malloc(max_pages * sizeof(size_t));
    for (size_t i = 0; i < max_pages; i++) indices[i] = i;

    srand(42);
    printf("Pages,Avg_Cycles_Per_Access\n");

    int iterations = 1000;
    int outer_its = 20;

    for (size_t num_pages = 4; num_pages <= max_pages; num_pages += (num_pages < 128 ? 4 : (num_pages < 512 ? 16 : 64))) {
        my_rand_shuffle(indices, num_pages);

        for (size_t i = 0; i < num_pages; i++) {
            size_t next_i = (i + 1) % num_pages;
            char **current_ptr = (char **)(buffer + indices[i] * page_size);
            *current_ptr = buffer + indices[next_i] * page_size;
        }

        char **current = (char **)buffer;
        for (int k = 0; k < 200; k++) current = (char **)*current;

        unsigned long long min_total_cycles = -1;
        for (int o = 0; o < outer_its; o++) {
            unsigned long long start = rdtsc();
            for (int i = 0; i < iterations; i++) {
                current = (char **)*current;
                current = (char **)*current;
                current = (char **)*current;
                current = (char **)*current;
            }
            unsigned long long end = rdtsc();
            unsigned long long diff = end - start;
            if (diff < min_total_cycles) min_total_cycles = diff;
        }

        double cycles_per_access = (double)min_total_cycles / (iterations * 4);
        printf("%zu,%.4f\n", num_pages, cycles_per_access);
    }
    free(indices); munmap(buffer, total_bytes);
    return 0;
}
