#define _POSIX_C_SOURCE 200809L

/* Golden-ladder binary64 oracle, audited revision.

   Exact ladder:
       T_n = F_{n+1}^2 + F_{n+1}F_n + F_n^2.

   Positive normal IEEE-754 binary64 encodings are a piecewise-linear proxy for
   log2(x). The canonical asymptotic stride and intercept are

       D = round(2^53 log2(phi))
         = 0x0016373AD151CA68,

       C_asym = round(2^52(1023 + log2(2/5) + 2log2(phi)))
              = 0x3FF1109CBE5E8386.

   For every exact T_n representable as finite binary64 (n=0,...,737), all C in

       [0x3FE6AD27C6055065, 0x3FFAAD27C6055064]

   classify correctly with nearest-integer rounding. ORACLE_C is the exact
   midpoint of that interval. The older 0x3FF100E2F21F7C00 also lies inside it.

   This file assumes IEC 60559 / IEEE-754 binary64. It uses memcpy bit casts,
   never strict-aliasing violations. The benchmark is host- and compiler-specific.
*/

#include <float.h>
#include <inttypes.h>
#include <limits.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

_Static_assert(CHAR_BIT == 8, "8-bit bytes required");
_Static_assert(sizeof(double) == sizeof(uint64_t), "64-bit double required");
_Static_assert(FLT_RADIX == 2, "binary floating point required");
_Static_assert(DBL_MANT_DIG == 53, "IEEE-754 binary64 significand required");
_Static_assert(DBL_MAX_EXP == 1024, "IEEE-754 binary64 exponent required");

#define ORACLE_C UINT64_C(0x3FF0AD27C6055064)
#define ORACLE_D UINT64_C(0x0016373AD151CA68)
#define ASYM_C   UINT64_C(0x3FF1109CBE5E8386)
#define LEGACY_C UINT64_C(0x3FF100E2F21F7C00)
#define LEGACY_D UINT64_C(0x0016373AD151CA69)
#define MAX_RUNG 737

#ifndef ORACLE_BENCH_REPS
#define ORACLE_BENCH_REPS UINT64_C(100000000)
#endif
#ifndef ORACLE_BENCH_ROUNDS
#define ORACLE_BENCH_ROUNDS 7
#endif

static inline uint64_t bits_of(double x) {
    uint64_t bits;
    memcpy(&bits, &x, sizeof bits);
    return bits;
}

static inline double float_of_bits(uint64_t bits) {
    double x;
    memcpy(&x, &bits, sizeof x);
    return x;
}

/* Fast path: caller guarantees finite T >= 1 and certified range. */
static inline int rung_bits_unchecked(double T) {
    const int64_t delta =
        (int64_t)bits_of(T) - (int64_t)ORACLE_C + (int64_t)(ORACLE_D / 2u);
    return (int)(delta / (int64_t)ORACLE_D);
}

/* Checked public path. -1 denotes outside the certified domain. */
static inline int rung_bits(double T) {
    if (!isfinite(T) || T < 1.0) {
        return -1;
    }
    const int n = rung_bits_unchecked(T);
    return (0 <= n && n <= MAX_RUNG) ? n : -1;
}

static inline double shell_guess(int n) {
    if (n < 0 || n > MAX_RUNG) {
        return NAN;
    }
    const uint64_t pattern = ORACLE_C + ORACLE_D * (uint64_t)n;
    const double x = float_of_bits(pattern);
    return (isfinite(x) && x > 0.0) ? x : NAN;
}

static const double LOG2_PHI = 0.6942419136306174;

static inline int rung_log(double T) {
    if (!isfinite(T) || T < 1.0) {
        return -1;
    }
    const double index =
        (log2(T) - log2(0.4)) / (2.0 * LOG2_PHI) - 1.0;
    const long rounded = lround(index);
    return (0 <= rounded && rounded <= MAX_RUNG) ? (int)rounded : -1;
}

#if defined(__GNUC__) || defined(__clang__)
__attribute__((noinline))
#endif
int rung_bits_audit(double T) {
    return rung_bits_unchecked(T);
}

static uint64_t elapsed_ns(struct timespec start, struct timespec stop) {
    const int64_t seconds = (int64_t)(stop.tv_sec - start.tv_sec);
    const int64_t nanoseconds = (int64_t)(stop.tv_nsec - start.tv_nsec);
    const int64_t total = seconds * INT64_C(1000000000) + nanoseconds;
    return total >= 0 ? (uint64_t)total : UINT64_C(0);
}

static void sort_double(double *values, size_t count) {
    for (size_t i = 1; i < count; ++i) {
        const double key = values[i];
        size_t j = i;
        while (j > 0 && values[j - 1] > key) {
            values[j] = values[j - 1];
            --j;
        }
        values[j] = key;
    }
}

int main(void) {
    if (bits_of(1.0) != UINT64_C(0x3FF0000000000000)) {
        fputs("unsupported floating-point encoding\n", stderr);
        return 3;
    }

    printf("golden binary64 oracle v2.1\n");
    printf("compiler             : %s\n", __VERSION__);
    printf("ORACLE_C             : 0x%016" PRIX64 "\n", ORACLE_C);
    printf("ORACLE_D             : 0x%016" PRIX64 "\n", ORACLE_D);
    printf("ASYM_C               : 0x%016" PRIX64 "\n", ASYM_C);
    printf("LEGACY_C / D         : 0x%016" PRIX64 " / 0x%016" PRIX64 "\n",
           LEGACY_C, LEGACY_D);

    /* Exact signed-int64 ground truth through n=45. __uint128_t prevents UB. */
    uint64_t k = 1u;
    uint64_t ell = 0u;
    int exact_count = 0;
    int bits_hits = 0;
    int log_hits = 0;
    for (int n = 0; n < 100; ++n) {
        const __uint128_t wide_T =
            (__uint128_t)k * k + (__uint128_t)k * ell + (__uint128_t)ell * ell;
        if (wide_T > (__uint128_t)INT64_MAX) {
            break;
        }
        const uint64_t T = (uint64_t)wide_T;
        bits_hits += rung_bits((double)T) == n;
        log_hits += rung_log((double)T) == n;
        ++exact_count;
        const __uint128_t next = (__uint128_t)k + ell;
        if (next > UINT64_MAX) {
            break;
        }
        ell = k;
        k = (uint64_t)next;
    }
    printf("exact int64 rungs    : %d\n", exact_count);
    printf("bit-oracle hits      : %d/%d\n", bits_hits, exact_count);
    printf("log2-route hits      : %d/%d\n", log_hits, exact_count);

    const double inverse_samples[] = {
        shell_guess(0), shell_guess(1), shell_guess(2), shell_guess(737)
    };
    printf("shell guesses        : %.17g %.17g %.17g %.17g\n",
           inverse_samples[0], inverse_samples[1],
           inverse_samples[2], inverse_samples[3]);

    enum { SAMPLE_COUNT = 1024, ROUNDS = ORACLE_BENCH_ROUNDS };
    static double samples[SAMPLE_COUNT];
    for (int i = 0; i < SAMPLE_COUNT; ++i) {
        samples[i] = (double)(i + 1);
    }

    const uint64_t repetitions = ORACLE_BENCH_REPS;
    double bits_ns[ROUNDS];
    double log_ns[ROUNDS];
    volatile int64_t sink = 0;

    for (int round = 0; round < ROUNDS; ++round) {
        struct timespec a, b;
        if (clock_gettime(CLOCK_MONOTONIC, &a) != 0) {
            return 2;
        }
        for (uint64_t r = 0; r < repetitions; ++r) {
            sink += rung_bits_unchecked(samples[r & (SAMPLE_COUNT - 1u)]);
        }
        if (clock_gettime(CLOCK_MONOTONIC, &b) != 0) {
            return 2;
        }
        bits_ns[round] = (double)elapsed_ns(a, b) / (double)repetitions;

        if (clock_gettime(CLOCK_MONOTONIC, &a) != 0) {
            return 2;
        }
        for (uint64_t r = 0; r < repetitions; ++r) {
            sink += rung_log(samples[r & (SAMPLE_COUNT - 1u)]);
        }
        if (clock_gettime(CLOCK_MONOTONIC, &b) != 0) {
            return 2;
        }
        log_ns[round] = (double)elapsed_ns(a, b) / (double)repetitions;
    }

    sort_double(bits_ns, ROUNDS);
    sort_double(log_ns, ROUNDS);
    const double median_bits = bits_ns[ROUNDS / 2];
    const double median_log = log_ns[ROUNDS / 2];
    printf("median rung_bits     : %.3f ns/call\n", median_bits);
    printf("median rung_log2     : %.3f ns/call\n", median_log);
    printf("host speed ratio     : %.3fx (%s)\n",
           median_log > median_bits ? median_log / median_bits : median_bits / median_log,
           median_log > median_bits ? "bits faster" : "log2 faster");
    printf("sink                 : %" PRId64 "\n", sink);

    return (exact_count == 46 && bits_hits == 46 && log_hits == 46) ? 0 : 1;
}
