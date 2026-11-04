#include <stdio.h>
#include <stdint.h>
#include <unistd.h>
#include "Enclave_u.h"
#include "sgx_urts.h"

void ocall_print(const char *str) {
    printf("%s", str);
}

int main() {
    char hostname[256];
    gethostname(hostname, sizeof(hostname));

    sgx_enclave_id_t eid = 0;
    sgx_status_t ret = SGX_SUCCESS;
    sgx_launch_token_t token = {0};
    int updated = 0;

    // Initialize Enclave
    ret = sgx_create_enclave("enclave.signed.so", SGX_DEBUG_FLAG, &token, &updated, &eid, NULL);
    if (ret != SGX_SUCCESS) {
        fprintf(stderr, "App: error 0x%x, failed to create enclave.\n", ret);
        return -1;
    }

    // --- 1. PIPELINE BENCHMARK (Outside vs Inside) ---
    {
        char csv_path[512];
        snprintf(csv_path, sizeof(csv_path), "data/sgx_comparison/%s_pipeline_comparison.csv", hostname);
        FILE *f = fopen(csv_path, "w");
        fprintf(f, "Machine,Execution_Mode,Dependent_Cycles,Independent_Cycles\n");

        // Outside Enclave (Native)
        uint64_t dep_out, ind_out;
        uint64_t s, e;
        
        // Measure outside
        __asm__ volatile ("lfence\n\t" "rdtsc\n\t" : "=a" (s));
        __asm__ volatile ("mov $0, %%rax\n\t" ".rept 1000\n\t" "add $1, %%rax\n\t" ".endr\n\t" : : : "rax");
        __asm__ volatile ("rdtsc\n\t" "lfence\n\t" : "=a" (e));
        dep_out = e - s;

        __asm__ volatile ("lfence\n\t" "rdtsc\n\t" : "=a" (s));
        __asm__ volatile ("mov $0, %%r8\n\t" "mov $0, %%r9\n\t" ".rept 250\n\t" "add $1, %%r8\n\t" "add $1, %%r9\n\t" ".endr\n\t" : : : "r8", "r9");
        __asm__ volatile ("rdtsc\n\t" "lfence\n\t" : "=a" (e));
        ind_out = e - s;

        fprintf(f, "%s,Outside_Enclave,%lu,%lu\n", hostname, dep_out, ind_out);

        // Inside Enclave (ECall)
        uint64_t dep_in = 0, ind_in = 0;
        ecall_run_pipeline(eid, &dep_in, &ind_in);
        fprintf(f, "%s,Inside_Enclave,%lu,%lu\n", hostname, dep_in, ind_in);

        fclose(f);
        printf("Pipeline benchmark saved to %s\n", csv_path);
    }

    // --- 2. BRANCH PREDICTION BENCHMARK (Outside vs Inside) ---
    {
        char csv_path[512];
        snprintf(csv_path, sizeof(csv_path), "data/sgx_comparison/%s_branch_comparison.csv", hostname);
        FILE *f = fopen(csv_path, "w");
        fprintf(f, "Machine,Execution_Mode,Random_Cycles,Sorted_Cycles\n");

        // Run inside enclave branch test
        uint64_t rand_in = 0, sort_in = 0;
        ecall_run_branch(eid, &rand_in, &sort_in);

        fprintf(f, "%s,Inside_Enclave,%lu,%lu\n", hostname, rand_in, sort_in);
        fclose(f);
        printf("Branch prediction benchmark saved to %s\n", csv_path);
    }

    sgx_destroy_enclave(eid);
    return 0;
}
