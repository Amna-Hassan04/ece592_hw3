#include <stdio.h>    // Include standard input-output library for printf functions
#include <stdint.h>   // Include standard integer types for 64-bit cycle counters (uint64_t)

// Inline function to read starting timestamp counter with serialization fences
static inline uint64_t get_cycles(void) {
    uint32_t cycles_high, cycles_low; // Declare variables to hold high and low 32-bit timestamp halves
    __asm__ volatile (
        "lfence\n\t"        // Serialize the instruction stream to prevent prior out-of-order execution leakage
        "rdtsc\n\t"         // Read the Time-Stamp Counter into EDX (high) and EAX (low)
        : "=a" (cycles_low), "=d" (cycles_high) // Output low 32 bits to cycles_low, high to cycles_high
        :                   // No input operands needed for rdtsc
        : "memory"          // Clobber directive telling compiler memory and registers state changed
    );
    return ((uint64_t)cycles_high << 32) | cycles_low; // Combine high and low 32-bit values into a single 64-bit integer
}

// Inline function to read ending timestamp counter with serialization fences
static inline uint64_t get_cycles_end(void) {
    uint32_t cycles_high, cycles_low; // Declare variables to hold high and low 32-bit timestamp halves
    __asm__ volatile (
        "rdtsc\n\t"         // Read the Time-Stamp Counter immediately after instruction execution finishes
        "lfence\n\t"        // Serialize instruction stream after reading to lock execution window boundaries
        : "=a" (cycles_low), "=d" (cycles_high) // Output low to cycles_low, high to cycles_high
        :                   // No input operands
        : "memory"          // Clobber directive for memory and register state safety
    );
    return ((uint64_t)cycles_high << 32) | cycles_low; // Combine high and low halves into a 64-bit return value
}

// Main execution entry point for the ROB ALU window size sweep benchmark
int main() {
    printf("ROB ALU Window Size,Total Cycles\n"); // Print CSV header for output logging

    // Define array of instruction window sizes (N) spanning well below and above typical hardware ROB limits
    int window_sizes[] = {32, 64, 96, 128, 160, 192, 224, 256, 320, 384, 512, 768, 1024};
    
    // Calculate the total number of test points in our window size array
    int num_tests = sizeof(window_sizes) / sizeof(window_sizes[0]);

    // Outer loop to iterate through each distinct window size N
    for (int t = 0; t < num_tests; t++) {
        int n = window_sizes[t];         // Assign current window size N from array
        uint64_t start, end;             // Declare start and end cycle counter variables
        unsigned long long total_cycles = 0; // Initialize accumulator for average calculation across runs
        int iterations = 1000;           // Set number of inner iterations to average out OS jitter

        // Inner loop running multiple iterations for statistical stability
        for (int iter = 0; iter < iterations; iter++) {
            start = get_cycles();        // Capture the start timestamp right before the instruction window

            // Inline assembly block containing a long-latency anchor instruction (sqrtsd)
            __asm__ volatile (
                "sqrtsd %%xmm0, %%xmm1\n\t"  // Execute floating-point square root as long-latency execution bottleneck
                :                          // No output operands
                :                          // No input operands
                : "xmm1", "memory"         // Clobber list informing compiler xmm1 and memory are modified
            );

            // Loop to inject N independent instructions dynamically to fill out-of-order window
            for (int i = 0; i < n; i++) {
                __asm__ volatile (
                    "add $1, %%rax\n\t"    // Execute independent integer addition instruction
                    :                      // No output operands
                    :                      // No input operands
                    : "rax", "memory"      // Clobber list specifying rax register is modified per iteration
                );
            }

            end = get_cycles_end();        // Capture end timestamp immediately after instruction window completes
            total_cycles += (end - start); // Accumulate elapsed cycle count for this iteration
        }

        // Print the averaged cycle results for the current window size N in CSV format
        printf("%d,%llu\n", n, total_cycles / iterations);
    }

    return 0; // Return success status code to the operating system
}
