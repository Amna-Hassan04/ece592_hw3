SGX_SDK ?= /opt/intel/sgxsdk
SGX_MODE ?= HW
SGX_ARCH ?= x64

CC = gcc
CXX = g++

SGX_COMMON_CFLAGS := -m64 -O2 -Wall -Wextra
SGX_LIBRARY_PATH := $(SGX_SDK)/lib64
SGX_INCLUDE_PATH := $(SGX_SDK)/include

.PHONY: all clean

all: app enclave.signed.so

# --- Enclave Objects ---
Enclave/Enclave_t.h Enclave/Enclave_t.c: $(SGX_SDK)/bin/x64/sgx_edger8r Enclave/Enclave.edl
	cd Enclave && $(SGX_SDK)/bin/x64/sgx_edger8r --trusted Enclave.edl --search-path $(SGX_INCLUDE_PATH)

Enclave/Enclave_t.o: Enclave/Enclave_t.h Enclave/Enclave_t.c
	$(CC) $(SGX_COMMON_CFLAGS) -nostdinc -fvisibility=hidden -fpie -fstack-protector \
	-I$(SGX_INCLUDE_PATH) -I$(SGX_SDK)/include/tlibc -I$(SGX_SDK)/include/libcxx \
	-I$(shell gcc -print-file-name=include) \
	-c Enclave/Enclave_t.c -o Enclave/Enclave_t.o

Enclave/Enclave.o: Enclave/Enclave_t.h Enclave/Enclave.cpp
	$(CXX) $(SGX_COMMON_CFLAGS) -nostdinc -fvisibility=hidden -fpie -fstack-protector \
	-I$(SGX_INCLUDE_PATH) -I$(SGX_SDK)/include/tlibc -I$(SGX_SDK)/include/libcxx \
	-I$(shell gcc -print-file-name=include) \
	-c Enclave/Enclave.cpp -o Enclave/Enclave.o

enclave.unsigned.so: Enclave/Enclave_t.o Enclave/Enclave.o Enclave/Enclave.lds
	$(CXX) Enclave/Enclave_t.o Enclave/Enclave.o -o $@ -shared -nostdlib -nodefaultlibs -nostartfiles \
	-L$(SGX_LIBRARY_PATH) \
	-Wl,--whole-archive -lsgx_trts -Wl,--no-whole-archive \
	-Wl,--start-group -lsgx_tstdc -lsgx_tcrypto -lsgx_tservice -lsgx_trts -Wl,--end-group \
	-Wl,-Bstatic -Wl,-Bsymbolic -Wl,--no-undefined \
	-Wl,--defsym,__ImageBase=0 \
	-Wl,-pie,-eenclave_entry -Wl,--export-dynamic \
	-Wl,--version-script=Enclave/Enclave.lds

enclave.signed.so: enclave.unsigned.so Enclave/Enclave.config.xml
	$(SGX_SDK)/bin/x64/sgx_sign sign -enclave enclave.unsigned.so -key Enclave/Enclave_private.pem -out $@ -config Enclave/Enclave.config.xml -ignore-rel-error

# --- App Objects ---
App/Enclave_u.h App/Enclave_u.c: $(SGX_SDK)/bin/x64/sgx_edger8r Enclave/Enclave.edl
	cd App && $(SGX_SDK)/bin/x64/sgx_edger8r --untrusted ../Enclave/Enclave.edl --search-path $(SGX_INCLUDE_PATH)

App/Enclave_u.o: App/Enclave_u.h App/Enclave_u.c
	$(CC) $(SGX_COMMON_CFLAGS) -fPIC -I$(SGX_INCLUDE_PATH) -c App/Enclave_u.c -o App/Enclave_u.o

App/App.o: App/Enclave_u.h App/App.cpp
	$(CXX) $(SGX_COMMON_CFLAGS) -fPIC -I$(SGX_INCLUDE_PATH) -c App/App.cpp -o App/App.o

app: App/Enclave_u.o App/App.o
	$(CXX) App/Enclave_u.o App/App.o -o $@ -L$(SGX_LIBRARY_PATH) -lsgx_urts -lpthread

clean:
	rm -f app enclave.signed.so enclave.unsigned.so Enclave/Enclave_t.* Enclave/*.o App/Enclave_u.* App/*.o
