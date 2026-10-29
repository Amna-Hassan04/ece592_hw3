#define _GNU_SOURCE             // Enable GNU extensions for CPU core pinning (sched_setaffinity)
#include <stdio.h>              // Standard I/O for printf, fopen, fprintf, fclose
#include <stdint.h>             // Fixed-width integers (uint64_t)
#include <stdlib.h>             // Memory allocation (aligned_alloc, free)
#include <string.h>             // Memory functions (memset)
#include <unistd.h>             // POSIX syscalls (read, close, gethostname)
#include <sys/syscall.h>        // Syscall numbers (__NR_perf_event_open)
#include <sys/ioctl.h>          // Counter control (ioctl)
#include <linux/perf_event.h>   // Hardware performance counter structs and constants
#include <sched.h>              // CPU affinity macros (CPU_ZERO, CPU_SET)
#include <x86intrin.h>          // x86 intrinsics (__rdtscp, _mm_lfence, _mm_mfence, _mm_clflush)

// Number of iterations for the ALU dependency test
#define ALU_ITERS 100000
// Number of iterations for the DRAM cache-miss test
#define MEM_ITERS 10000

// Helper wrapper around the Linux perf_event_open system call
static long perf_event_open(struct perf_event_attr *hw_event, pid_t pid,
                            int cpu, int group_fd, unsigned long flags) {
    return syscall(__NR_perf_event_open, hw_event, pid, cpu, group_fd, flags);
}

// Configure and open a hardware performance counter (PMU)
int open_pmu_counter(uint64_t config_event) {
    struct perf_event_attr pe;
    memset(&pe, 0, sizeof(struct perf_event_attr));
    pe.type = PERF_TYPE_HARDWARE;
    pe.size = sizeof(struct perf_event_attr);
    pe.config = config_event;
    pe.disabled = 1;
    pe.exclude_kernel = 1;
    pe.exclude_hv = 1;
    return perf_event_open(&pe, 0, -1, -1, 0);
}

// Pin current process to Core 0
void pin_to_core(int core_id) {
    cpu_set_t mask;
    CPU_ZERO(&mask);
    CPU_SET(core_id, &mask);
    if (sched_setaffinity(0, sizeof(mask), &mask) < 0) {
        perror("Warning: sched_setaffinity failed");
    }
}

// Preprocessor macros to repeat assembly instructions cleanly for our sweep
#define ADD_IND_1  "add $1, %%rbx\n\t"
#define ADD_IND_4  ADD_IND_1 ADD_IND_1 ADD_IND_1 ADD_IND_1
#define ADD_IND_8  ADD_IND_4 ADD_IND_4
#define ADD_IND_16 ADD_IND_8 ADD_IND_8
#define ADD_IND_32 ADD_IND_16 ADD_IND_16
#define ADD_IND_64 ADD_IND_32 ADD_IND_32

int main(int argc, char *argv[]) {
    pin_to_core(0);

    char hostname[128];
    gethostname(hostname, sizeof(hostname));

    FILE *csv = NULL;
    if (argc > 1) {
        csv = fopen(argv[1], "w");
        if (csv) {
            fprintf(csv, "hostname,method,variant,num_independent_insts,rdtscp_cycles,pmu_cycles,ipc\n");
        }
    }

    int fd_cycles = open_pmu_counter(PERF_COUNT_HW_CPU_CYCLES);
    int fd_insts  = open_pmu_counter(PERF_COUNT_HW_INSTRUCTIONS);

    unsigned int aux;
    uint64_t t0, t1, pmu_cyc = 0, pmu_ins = 0;

    printf("============================================================\n");
    printf("Host: %s | Question 2: Out-of-Order Execution Detection\n", hostname);
    printf("============================================================\n");

    // METHOD 1A: Long-Latency ALU (SQRTSD) + 16 DEPENDENT ADDs
    if (fd_cycles != -1 && fd_insts != -1) {
        ioctl(fd_cycles, PERF_EVENT_IOC_RESET, 0);
        ioctl(fd_insts,  PERF_EVENT_IOC_RESET, 0);
        ioctl(fd_cycles, PERF_EVENT_IOC_ENABLE, 0);
        ioctl(fd_insts,  PERF_EVENT_IOC_ENABLE, 0);
    }

    _mm_lfence();
    t0 = __rdtscp(&aux);
    _mm_lfence();

    for (int i = 0; i < ALU_ITERS; i++) {
        __asm__ volatile (
            "cvtsi2sd %%rcx, %%xmm0\n\t"
            "sqrtsd %%xmm0, %%xmm0\n\t"
            "cvtsd2si %%xmm0, %%rax\n\t"
            "add $1, %%rax\n\t" "add $1, %%rax\n\t" "add $1, %%rax\n\t" "add $1, %%rax\n\t"
            "add $1, %%rax\n\t" "add $1, %%rax\n\t" "add $1, %%rax\n\t" "add $1, %%rax\n\t"
            "add $1, %%rax\n\t" "add $1, %%rax\n\t" "add $1, %%rax\n\t" "add $1, %%rax\n\t"
            "add $1, %%rax\n\t" "add $1, %%rax\n\t" "add $1, %%rax\n\t" "add $1, %%rax\n\t"
            "mov %%rax, %%rcx\n\t"
            : : : "rax", "rcx", "xmm0", "cc"
        );
    }

    _mm_lfence();
    t1 = __rdtscp(&aux);
    _mm_lfence();

    if (fd_cycles != -1 && fd_insts != -1) {
        ioctl(fd_cycles, PERF_EVENT_IOC_DISABLE, 0);
        ioctl(fd_insts,  PERF_EVENT_IOC_DISABLE, 0);
        read(fd_cycles, &pmu_cyc, sizeof(uint64_t));
        read(fd_insts,  &pmu_ins, sizeof(uint64_t));
    }

    double m1_dep_tsc = (double)(t1 - t0) / ALU_ITERS;
    double m1_dep_pmu = (fd_cycles != -1) ? (double)pmu_cyc / ALU_ITERS : 0.0;
    double m1_dep_ipc = (fd_cycles != -1 && pmu_cyc > 0) ? (double)pmu_ins / pmu_cyc : 0.0;

    printf("[Method 1A] SQRTSD + 16 Dependent ADDs   : %6.2f cycles (RDTSCP) | %6.2f cycles (PMU) | IPC: %.2f\n",
           m1_dep_tsc, m1_dep_pmu, m1_dep_ipc);
    if (csv) fprintf(csv, "%s,Method1_ALU,Dependent,16,%.2f,%.2f,%.2f\n",
                     hostname, m1_dep_tsc, m1_dep_pmu, m1_dep_ipc);

    // METHOD 1B: Long-Latency ALU (SQRTSD) + 16 INDEPENDENT ADDs
    if (fd_cycles != -1 && fd_insts != -1) {
        ioctl(fd_cycles, PERF_EVENT_IOC_RESET, 0);
        ioctl(fd_insts,  PERF_EVENT_IOC_RESET, 0);
        ioctl(fd_cycles, PERF_EVENT_IOC_ENABLE, 0);
        ioctl(fd_insts,  PERF_EVENT_IOC_ENABLE, 0);
    }

    _mm_lfence();
    t0 = __rdtscp(&aux);
    _mm_lfence();

    for (int i = 0; i < ALU_ITERS; i++) {
        __asm__ volatile (
            "cvtsi2sd %%rcx, %%xmm0\n\t"
            "sqrtsd %%xmm0, %%xmm0\n\t"
            "cvtsd2si %%xmm0, %%rcx\n\t"
            "add $1, %%rbx\n\t" "add $1, %%rdx\n\t" "add $1, %%rbx\n\t" "add $1, %%rdx\n\t"
            "add $1, %%rbx\n\t" "add $1, %%rdx\n\t" "add $1, %%rbx\n\t" "add $1, %%rdx\n\t"
            "add $1, %%rbx\n\t" "add $1, %%rdx\n\t" "add $1, %%rbx\n\t" "add $1, %%rdx\n\t"
            "add $1, %%rbx\n\t" "add $1, %%rdx\n\t" "add $1, %%rbx\n\t" "add $1, %%rdx\n\t"
            : : : "rbx", "rcx", "rdx", "xmm0", "cc"
        );
    }

    _mm_lfence();
    t1 = __rdtscp(&aux);
    _mm_lfence();

    if (fd_cycles != -1 && fd_insts != -1) {
        ioctl(fd_cycles, PERF_EVENT_IOC_DISABLE, 0);
        ioctl(fd_insts,  PERF_EVENT_IOC_DISABLE, 0);
        read(fd_cycles, &pmu_cyc, sizeof(uint64_t));
        read(fd_insts,  &pmu_ins, sizeof(uint64_t));
    }

    double m1_ind_tsc = (double)(t1 - t0) / ALU_ITERS;
    double m1_ind_pmu = (fd_cycles != -1) ? (double)pmu_cyc / ALU_ITERS : 0.0;
    double m1_ind_ipc = (fd_cycles != -1 && pmu_cyc > 0) ? (double)pmu_ins / pmu_cyc : 0.0;

    printf("[Method 1B] SQRTSD + 16 Independent ADDs : %6.2f cycles (RDTSCP) | %6.2f cycles (PMU) | IPC: %.2f\n\n",
           m1_ind_tsc, m1_ind_pmu, m1_ind_ipc);
    if (csv) fprintf(csv, "%s,Method1_ALU,Independent,16,%.2f,%.2f,%.2f\n",
                     hostname, m1_ind_tsc, m1_ind_pmu, m1_ind_ipc);

    // METHOD 2: DRAM Cache Miss (CLFLUSH) + Sweep of N = 0, 8, 16, 32, 64 ADDs
    uint64_t *target = (uint64_t *)aligned_alloc(4096, 4096);
    target[0] = 42;

    #define RUN_MEM_SWEEP(N_VAL, ASM_BLOCK) do { \
        uint64_t sum_tsc = 0; \
        for (int i = 0; i < MEM_ITERS; i++) { \
            _mm_clflush(&target[0]); \
            _mm_mfence(); \
            _mm_lfence(); \
            uint64_t s = __rdtscp(&aux); \
            _mm_lfence(); \
            __asm__ volatile ( \
                "mov (%0), %%rax\n\t" \
                ASM_BLOCK \
                : : "r"(target) : "rax", "rbx", "cc", "memory" \
            ); \
            _mm_lfence(); \
            uint64_t e = __rdtscp(&aux); \
            _mm_lfence(); \
            sum_tsc += (e - s); \
        } \
        double avg_tsc = (double)sum_tsc / MEM_ITERS; \
        printf("[Method 2] DRAM Load + %2d Indep ADDs     : %6.2f cycles (RDTSCP)\n", N_VAL, avg_tsc); \
        if (csv) fprintf(csv, "%s,Method2_DRAM,Independent,%d,%.2f,0.0,0.0\n", hostname, N_VAL, avg_tsc); \
    } while(0)

    RUN_MEM_SWEEP(0,  "");
    RUN_MEM_SWEEP(8,  ADD_IND_8);
    RUN_MEM_SWEEP(16, ADD_IND_16);
    RUN_MEM_SWEEP(32, ADD_IND_32);
    RUN_MEM_SWEEP(64, ADD_IND_64);

    free(target);
    if (csv) fclose(csv);
    if (fd_cycles != -1) close(fd_cycles);
    if (fd_insts != -1)  close(fd_insts);

    return 0;
}
