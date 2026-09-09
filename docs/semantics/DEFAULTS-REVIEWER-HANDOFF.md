# Reviewer continuation after positional defaults

Review9 recommends rotation to review10; root assigns the successor. Runtime6 and
compiler6 retain continuity. Read workspace AGENTS.md, PLAN.md, PROGRESS.md and
php/php-spec/p4-spectec skills, then this handoff and the
[core checklist](CORE-CONTINUATION-CHECKLIST.md). Complete core remains the goal.

## Accepted inputs and evidence

Canonical **909/e25eb2b920c4e2d2a5468fb4ccdf0c95e2a1671a68c3b2d397067d1e474201bb**
is exact in bytes and modes: code **1fce6586**, compiler evidence **2b247d81**,
runtime evidence **8151b96d**, independent acceptance **c7cb1b44**. No publication
closure correction or post-freeze mutation occurred. Frozen copies are
`.tools/runtime6-parameter-defaults/final-inputs.json` and
`.tools/review9-defaults-final/inputs.json`; baseline899/ca3c06e5 remains in
`.tools/review9-defaults-current-baseline/inputs.json`.

The [review](../../coverage/semantics/default-parameter-review.json) is the main
acceptance index. Independent gates:130 retained source profiles,57 exact author
contexts,4 states/1,091 assertions, readiness6,12 source projections/95 assertions,
and2 historical no-default full-state bridges. Author:57 sources,33 protocol,
4 states/1,082 assertions; PHP_VERSION boundary separate. Canonical CLI8 passes.
Compiler902 retains54 phase comparisons+3 pending/51 descriptors and focused gates.
Do not add overlapping source sets. Every dense state checks35 cuts, adjacent
public resumes and7 full resumes. Independent raw audit452 responses/14 clean
closures and author140/8 retain full packets, process outputs and source profiles.

Archives under `coverage/semantics/` (full hashes in companion JSON):

- `default-parameter-review-originals`:6136fca4,4,660 paths; publication22301708.
- `default-parameter-runtime-originals`:6ed7684f,5,628 paths; publication2fd4f65c.
- `default-parameter-compiler-originals`:bdc64012,7,294 paths, including immutable
  initial8276 filename-mismatched capture. Corrected39 current899 originals and
  eight additional profiles are paired; original mismatched39 are setup evidence.
  Compiler focused wrappers retain decoded responses, not exact wire/stderr.
- Earlier current899 baseline9f4c14ae and exploratory903 diagnosis3effccdc retain
  the119 default/cache observations and original source/guard failures.

Review producers/audits are `.tools/review9-default-*.py` and
`.tools/review9-audit-default-*.py`; exact files are in the review archives.
Maintained `tests/semantics/default_readiness_protocol.py` is SHA030c4c7d.
No semantic gate remains running or pending for defaults.

## Semantics to preserve

Read [compiler90](DEFAULT-PARAMETER-COMPILER.md), [runtime91](SOURCE-POSITIONAL-DEFAULTS.md)
and [allocation classes](CONSTANT-VALUE-CLASSES.md). Actual NParam/default CODE roots
extend the prior NConst guard. Dropped defaults still compile, but only surviving
deferred descriptors permit cache entries. Supplied operands skip receives; omitted
reference defaults start in fresh ordinary cells. Cached values own roots, classes
do not. Successful caches survive later failures and precede future type checking.
NEW-only AST side effects are currently excluded and must be integrated when admitted.

Shared fixes retain counterexamples: parameter receive-opcode lines repair three
old899 arity line mismatches; disjoint89 readiness premises repair actual ternary/
coalesce pre-observer nondeterminism; finite receive/bind queue guards reject trailing
DISCARD. Arbitrary consistent runtime/cache values remain valid. Historical no-default
bridges remove only empty DEFAULTCACHE/DEFAULTS and exact source-derived NParam
CODEEXPR additions; existing state/descriptors compare completely.

## Next: strictness and types

Private `.tools/compiler6-strict-paired/HANDOFF.md` binds minimal
**910/e7227852**, five changes against909:92+registry, pcode.STRICT, unit/function
projection. ENDLINE and return roots are excluded. Main archive `originals.tar.xz`
is **8e7f6e1eae512cdef67566c1ef4ff038ef3883f54359597fb3392ad1c156026e**,
4,549 paths.37 exact phases+2 other-directive boundaries and10 source projections
pass as compiler preparation.39 exact current909 Unsupported compiler originals
retain matching native/source contexts. Runtime/source/protocol acceptance is pending.

Separate `builtin-originals.{json,tar.xz}` and `builtin-archive.json` under that root
bind **2e9c9d11**,262 paths:7 native/current909 profiles (5 strict,2 weak) with exact
wire and request contexts. Implementers report80 rejects registered builtin bodies;
87 supplies compiler write facts only. Independently confirm this boundary and
strict metadata consumers before admission; no implemented weak builtin receiver
was found. Future strict strlen/in_array execution still needs correct coercion.

Typed preparation `.tools/compiler6-types-preparation/{PLAN.md,gap-originals.json,
archive.json,originals.tar.xz}` retains12 new type/cache originals (16458087) plus
114 historical indexes. `.tools/compiler6-type-descriptors`902/605b70b2 is synthetic
STRICT/ENDLINE/return-root preparation; `.tools/compiler6-strict-compiler`903/b5f306c7
is an older source prototype. Neither is accepted runtime. Agree caller/callee
strictness, typed receive/return, cache/type failure order and ownership before pairing.

Use only PHP8.5.10 `vendor/php-src` commit34308a6666b2d489c509541ea9befea9e2b42348,
never sibling development source. Preserve new concrete originals before repairs,
full process/packet evidence and exact watched identities. Audit finite source/task
relationships without general runtime-history reconstruction. Avoid unchanged broad
campaigns absent shared risk. Only oracle closes169 constructors/306 obligations;
PHP_VERSION/other builtin values, define/defined, object constants, remaining calls,
control, objects, exceptions, dynamic sources, generators/fibers, GC and core
intrinsics remain required. Final source/syntax/fresh offline campaigns and the full
design report wait for complete core. No push; coordinate index and shared builds.
