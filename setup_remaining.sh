#!/bin/bash
set -e

# Create directories
mkdir -p src/branch src/q3_rob src/tlb data/branch data/q3_rob data/tlb

# 1. Branch Prediction Benchmark
cat << 'INNER_EOF' > src/branch/branch_pred.c
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
INNER_EOF

cat << 'INNER_EOF' > run_branch.sh
#!/bin/bash
SRC_DIR="src/branch"
DATA_DIR="data/branch"
mkdir -p "$DATA_DIR"
CSV_FILE="$DATA_DIR/$(hostname -s)_branch.csv"
gcc -O3 "$SRC_DIR/branch_pred.c" -o "$SRC_DIR/branch_pred"
"$SRC_DIR/branch_pred" > "$CSV_FILE"
echo "Branch benchmark saved to $CSV_FILE"
INNER_EOF
chmod +x run_branch.sh

# 2. ROB Capacity Benchmark
cat << 'INNER_EOF' > src/q3_rob/robsize_hw.c
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <malloc.h>
#include <sys/mman.h>
#include <unistd.h>
#include <stdint.h>
#include <stdbool.h>

#define ADD_BYTE(val) do{ibuf[pbuf] = (val); pbuf++;} while(0)
#define ADD_WORD(val) do{*(unsigned short*)(&ibuf[pbuf]) = (val); pbuf+=2;} while(0)
#define ADD_DWORD(val) do{*(unsigned int*)(&ibuf[pbuf]) = (val); pbuf+=4;} while(0)

bool is_xmm[128] = {0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0};

int add_filler(unsigned char* ibuf, int instr, int i2) {
    ADD_WORD(0x9066);
    return 2;
}

static int its = 8192;
static const int unroll = 17;
void make_routine(unsigned char* ibuf, void *p1, void *p2, int icount, int instr) {
    if (icount < 3) return;
    int pbuf = 0;
    for (int i=0; i<8; i++) ADD_WORD(0x9066);        
    ADD_BYTE(0x53); ADD_BYTE(0x55); ADD_BYTE(0x56); ADD_BYTE(0x57);        
    ADD_WORD(0xb948);        
    ADD_DWORD((unsigned long long)p1);
    ADD_DWORD((unsigned long long)p1>>32LL);        
    ADD_WORD(0xba48);        
    ADD_DWORD((unsigned long long)p2);
    ADD_DWORD((unsigned long long)p2>>32LL);        
    ADD_WORD(0xb848);        
    ADD_DWORD(its);
    ADD_DWORD(0);
    
    ADD_DWORD(0x00e88348 | (3<<16)); 
    ADD_DWORD(0x00e88348 | (5<<16)); 
    ADD_DWORD(0x00e88348 | (6<<16)); 
    ADD_DWORD(0x00e88348 | (7<<16)); 
    ADD_DWORD(0x00e88349 | (0<<16)); 
    ADD_DWORD(0x00e88349 | (1<<16)); 
    ADD_DWORD(0x00e88349 | (2<<16)); 
    ADD_DWORD(0x00e88349 | (3<<16)); 
    ADD_DWORD(0x00e88349 | (4<<16)); 
    ADD_DWORD(0x00e88349 | (5<<16)); 
    ADD_DWORD(0x00e88349 | (6<<16)); 
    ADD_DWORD(0x00e88349 | (7<<16));    
    
    while (((unsigned long long)ibuf+pbuf) & 0xf) ADD_BYTE(0x90);
    int loop_start = pbuf;        

    for (int u=unroll-1; u>=0; u--) {
        for (int j=0; j<16; j++) pbuf += add_filler(ibuf+pbuf, instr, 0);
        ADD_WORD(0x8b48); ADD_BYTE(0x09);        
        for (int j=0; j<icount-1; j++) pbuf += add_filler(ibuf+pbuf, instr, 0);
        ADD_WORD(0x8b48); ADD_BYTE(0x12);    
        for (int j=0; j<icount-1-16; j++) pbuf += add_filler(ibuf+pbuf, instr, 0);
    }
    
    ADD_WORD(0xe883); ADD_BYTE(0x1);        
    ADD_WORD(0x850f); ADD_DWORD(loop_start - pbuf - 4);
    
    ADD_BYTE(0x5f); ADD_BYTE(0x5e); ADD_BYTE(0x5d); ADD_BYTE(0x5b);        
    ADD_WORD(0x770f); ADD_BYTE(0xc3);    
    mprotect(ibuf, pbuf, PROT_READ|PROT_WRITE|PROT_EXEC);
}

inline unsigned long long int rdtsc() {
    unsigned int lo, hi;
    __asm__ volatile (".byte 0x0f, 0x31" : "=a" (lo), "=d" (hi));
    return (long long)(((unsigned long long)hi)<<32LL) | (unsigned long long) lo;
}

const int memsize = 268435456;
static int outer_its = 64;

int main() {
    int instr_type = 4;
    unsigned char *ibuf = (unsigned char*)valloc(1048576);
    void ** dbuf = (void**)valloc(memsize);
    for (int i=0; i<memsize/sizeof(void*); i++) dbuf[i] = &dbuf[i];
    void(*routine)() = (void(*)())ibuf;    

    printf("Machine,Window_Size,Cycles\n");
    for (int icount = 32; icount <= 384; icount += 4) {    
        make_routine(ibuf, dbuf, dbuf+((8388608+4096)/sizeof(void*)), icount, instr_type);
        routine();
        long long sum_diff = 0;
        for (int i=0; i<outer_its; i++) {
            void(*routine_skip)() = routine + (i%13);
            long long start = rdtsc();
            routine_skip();
            long long stop = rdtsc();
            sum_diff += (stop - start);
        }
        double avg_cycles = 0.5 * sum_diff / its / outer_its;
        printf("%d,%.2f\n", icount, avg_cycles);
    }
    free(dbuf); free(ibuf);
    return 0;
}
INNER_EOF

cat << 'INNER_EOF' > run_hw_rob.sh
#!/bin/bash
SRC_DIR="src/q3_rob"
DATA_DIR="data/q3_rob"
mkdir -p "$DATA_DIR"
CSV_FILE="$DATA_DIR/$(hostname -s)_hw_rob.csv"
echo "Machine,Window_Size,Cycles" > "$CSV_FILE"
gcc -O3 "$SRC_DIR/robsize_hw.c" -o "$SRC_DIR/robsize_hw"
"$SRC_DIR/robsize_hw" 4 | tail -n +2 | while IFS=',' read -r size cycles; do
    echo "$(hostname),$size,$cycles" >> "$CSV_FILE"
done
echo "ROB benchmark saved to $CSV_FILE"
INNER_EOF
chmod +x run_hw_rob.sh

# 3. TLB Capacity Benchmark
cat << 'INNER_EOF' > src/tlb/tlb_size.c
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
INNER_EOF

cat << 'INNER_EOF' > run_tlb.sh
#!/bin/bash
SRC_DIR="src/tlb"
DATA_DIR="data/tlb"
mkdir -p "$DATA_DIR"
CSV_FILE="$DATA_DIR/$(hostname -s)_tlb.csv"
gcc -O3 "$SRC_DIR/tlb_size.c" -o "$SRC_DIR/tlb_size"
"$SRC_DIR/tlb_size" > "$CSV_FILE"
echo "TLB benchmark saved to $CSV_FILE"
INNER_EOF
chmod +x run_tlb.sh

echo "=== Executing All Benchmarks ==="
./run_branch.sh
./run_hw_rob.sh
./run_tlb.sh
echo "All benchmarks completed and saved to data/!"
