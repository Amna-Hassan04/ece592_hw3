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
    int pbuf = 0;
    ADD_WORD(0x9066);
    return pbuf;
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
