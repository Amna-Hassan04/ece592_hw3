#include <stdio.h>
#include <stdint.h>
#include <x86intrin.h>
#include <unistd.h>
#include "sgx_urts.h"
#include "Enclave_u.h"

#define ENCLAVE_FILENAME "enclave.signed.so"

static inline uint64_t get_cycles_app(void) {
    unsigned int aux;
    return __rdtscp(&aux);
}

void run_normal_pipeline(uint64_t *dep_cycles, uint64_t *ind_cycles) {
    uint64_t start, end;

    start = get_cycles_app();
    __asm__ volatile (
        "mov $0, %%rax\n\t"
        ".rept 1000\n\t"
        "add $1, %%rax\n\t"
        ".endr\n\t"
        : : : "rax", "memory"
    );
    end = get_cycles_app();
    *dep_cycles = end - start;

    start = get_cycles_app();
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
    end = get_cycles_app();
    *ind_cycles = end - start;
}

int main() {
    sgx_enclave_id_t global_eid = 0;
    sgx_status_t ret = SGX_ERROR_UNEXPECTED;
    sgx_launch_token_t token = {0};
    int updated = 0;

    ret = sgx_create_enclave(ENCLAVE_FILENAME, SGX_DEBUG_FLAG, &token, &updated, &global_eid, NULL);
    if (ret != SGX_SUCCESS) {
        fprintf(stderr, "App: error %#x, failed to create enclave.\n", ret);
        return -1;
    }

    uint64_t norm_dep = 0, norm_ind = 0;
    run_normal_pipeline(&norm_dep, &norm_ind);

    uint64_t enc_dep = 0, enc_ind = 0;
    int retval = 0;
    ret = enclave_pipeline_test(global_eid, &retval, 1000, &enc_dep, &enc_ind);
    if (ret != SGX_SUCCESS || retval != 0) {
        fprintf(stderr, "ECALL failed: error %#x (retval=%d)\n", ret, retval);
        sgx_destroy_enclave(global_eid);
        return -1;
    }

    char hostname[256];
    gethostname(hostname, sizeof(hostname));

    printf("Machine,Execution_Mode,Dependent_Cycles,Independent_Cycles\n");
    printf("%s,Outside_Enclave,%lu,%lu\n", hostname, norm_dep, norm_ind);
    printf("%s,Inside_Enclave,%lu,%lu\n", hostname, enc_dep, enc_ind);

    sgx_destroy_enclave(global_eid);
    return 0;
}
