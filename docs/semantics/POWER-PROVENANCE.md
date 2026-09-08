# Power's platform reference

PHP's floating `**` calls system `pow`; pinning PHP alone does not pin its last
bit. This study's oracle uses Ubuntu amd64 glibc **2.39-0ubuntu8.8**, the FMA/AVX2
variant, binary64 round-to-nearest ties-to-even. General power is still pending;
this import establishes its implementation source, not validated semantics.

[Machine provenance](../../dependencies/libm-provenance.json) records the exact
library hash, source archives, selected files and Debian patch audit. The
[official descriptor](https://archive.ubuntu.com/ubuntu/pool/main/g/glibc/glibc_2.39-0ubuntu8.8.dsc)
is retained locally. Archive hashes match its SHA256 entries; its OpenPGP
signature was not independently verified. None of the Debian patch diff targets
modifies the selected files. Their unchanged bytes and modes are covered by
`dependencies/files.jsonl` and `scripts/verify-inputs.py`.

`vendor/libm-pow-source` preserves full selected arithmetic/table files, wrapper,
dispatch/rounding evidence and upstream license texts. It is a source-evidence
closure, not a glibc build tree. No imported C code may supply semantic answers.
The future reference must implement its operations and tables in pure `.watsup`.
Derived translations must preserve the source's LGPL-2.1-or-later attribution.
The host libm remains an ordinary system prerequisite; a different library or
CPU-dispatched variant needs separate differential evidence and a distinct pin.

## Dispatch and rounding evidence

The pinned PHP ELF imports `pow@GLIBC_2.29`. That wrapper at ELF offset `0x3a630`
calls `__pow_finite@GLIBC_2.15`; its IFUNC resolver is at `0x2bfb0`. Runtime
`dlvsym` resolution, translated through `/proc/self/maps`, selects `0x7a1e0`.
The retained [disassembly](../../dependencies/libm-pow-disassembly.txt) proves
that branch and the actual arithmetic below. Stripped ELF labels naming a
neighboring exported symbol are not function identities.

`sysdeps/x86_64/fpu/multiarch/ifunc-fma4.h` selects FMA when FMA and AVX2 are
usable, then FMA4, otherwise SSE2. `e_pow-fma.c` includes the generic `e_pow.c`;
the multiarch Makefile supplies `-mfma -mavx2`. Compiler contraction fuses more
than the explicit `__builtin_fma` calls. A literal rounding after every C
operator is therefore incorrect. The source describes a worst-case error of
0.54 ULP: correctly rounded mathematical power is also an incorrect substitute.

The following operation graph records the selected binary's ordinary finite
path. `fma(a,b,c)` rounds the exact product-plus-addition once; every other
arithmetic operation rounds individually to binary64. Integer bit operations
retain the C unsigned wrapping and signed shifts documented in `e_pow.c`.
Coefficient names and table lookup/range definitions are exactly that file's.

```
r   = fma(z, invc, -1)
t1  = fma(kd, Ln2hi, logc)
t2  = t1 + r
lo1 = fma(kd, Ln2lo, logctail)
lo2 = (t1 - t2) + r
ar  = A[0] * r
ar2 = r * ar
ar3 = r * ar2
hi  = t2 + ar2
lo3 = fma(ar, r, -ar2)
lo4 = (t2 - hi) + ar2
p1  = fma(r, A[2], A[1])
p2  = fma(r, A[4], A[3])
p3  = fma(r, A[6], A[5])
p4  = fma(ar2, p3, p2)
p5  = fma(ar2, p4, p1)
lo  = fma(ar3, p5, ((lo1 + lo2) + lo3) + lo4)
log_hi   = hi + lo
log_tail = (hi - log_hi) + lo
ehi = exponent * log_hi
elo = fma(exponent, log_tail, fma(exponent, log_hi, -ehi))

kd0 = fma(ehi, InvLn2N, Shift)
ki  = bits(kd0)
kd  = kd0 - Shift
r   = fma(kd, NegLn2loN, fma(kd, NegLn2hiN, ehi)) + elo
r2  = r * r
r4  = r2 * r2
p1  = fma(r, C3, C2)
p2  = fma(r, C5, C4)
tmp = fma(r4, p2, fma(r2, p1, tail + r))
normal_result = fma(scale, tmp, scale)
```

`python3 tests/semantics/libm_data_evidence.py` independently checks all 657
generated constant/coefficient/table words against the pinned ELF bytes using
the retained data references and struct layout. The report is
`coverage/semantics/libm-data.json`; no arithmetic routine is executed.

These contractions correspond to `0x7a29a`–`0x7a34a` (log and product),
`0x7a364`–`0x7a3e5` (exp reduction/polynomial), and `0x7a3f7` (normal scale).
The overflow branch rounds `2^1009 * fma(scale,tmp,scale)` (`0x7a6f2`).
The underflow branch instead rounds `product=scale*tmp`, `y=scale+product`,
`lo=(scale-y)+product` separately (`0x7a586`, `0x7a58a`, `0x7a5c4`–`0x7a5cd`),
then follows the source's remaining correction/scaling operations. It must not
be fused. Tiny/huge, zero, infinity, NaN, negative-base and integer exponent
branches remain separate obligations, including PHP's integer fast path and
ordered diagnostics. Tests must include domain, overflow/subnormal, range/table
boundaries, NaN bits, and a broad deterministic differential campaign.
