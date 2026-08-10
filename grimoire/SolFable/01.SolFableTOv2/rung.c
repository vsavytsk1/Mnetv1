/* THE TOWER'S ORACLE, in the language Walsh wrote his in.
   Which rung of the golden Goldberg ladder is this shell?
   T_n ~ (2/5) phi^(2n+2) so log2(T_n) is linear in n, so n is linear in
   the raw bits. No log. No table. No FPU. */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <time.h>

#define MAGIC  0x3FF100E2F21F7C00LL
#define STRIDE 0x0016373AD151CA69LL

static inline int rung_bits(double T){
    int64_t i; memcpy(&i,&T,8);                 /* std::bit_cast, not the UB cast */
    return (int)((i - MAGIC + STRIDE/2) / STRIDE);
}
static inline double shell_bits(int n){
    int64_t i = MAGIC + STRIDE*(int64_t)n; double d; memcpy(&d,&i,8); return d;
}
static const double L2PHI = 0.6942419136306174;
static inline int rung_log(double T){
    return (int)floor((log2(T) - log2(0.4))/(2.0*L2PHI) - 1.0 + 0.5);
}

int main(void){
    /* correctness first: exact ladder in int64 as far as it goes */
    long long k=1,l=0; int n, ok_bits=0, ok_log=0, N=0;
    for(n=0;n<87;n++){
        long long T=k*k+k*l+l*l;
        if(T<0) break;
        if(rung_bits((double)T)==n) ok_bits++;
        if(rung_log ((double)T)==n) ok_log++;
        N++;
        long long t=k+l; l=k; k=t;
    }
    printf("  correctness over %d rungs:  bit-oracle %d/%d   log2-route %d/%d\n",
           N, ok_bits,N, ok_log,N);

    /* now the clock */
    const long REPS=200000000L; volatile long sink=0; struct timespec a,b; long r;
    clock_gettime(CLOCK_MONOTONIC,&a);
    for(r=0;r<REPS;r++) sink += rung_bits((double)(r%1000)+1.0);
    clock_gettime(CLOCK_MONOTONIC,&b);
    double t_bits=((b.tv_sec-a.tv_sec)*1e9+(b.tv_nsec-a.tv_nsec))/REPS;

    clock_gettime(CLOCK_MONOTONIC,&a);
    for(r=0;r<REPS;r++) sink += rung_log((double)(r%1000)+1.0);
    clock_gettime(CLOCK_MONOTONIC,&b);
    double t_log=((b.tv_sec-a.tv_sec)*1e9+(b.tv_nsec-a.tv_nsec))/REPS;

    printf("  rung_bits : %6.3f ns/call\n", t_bits);
    printf("  rung_log  : %6.3f ns/call   -> bits are %.2fx %s\n",
           t_log, t_log>t_bits ? t_log/t_bits : t_bits/t_log,
           t_log>t_bits ? "FASTER" : "SLOWER");
    printf("  (sink %ld)\n", (long)sink);
    return 0;
}
