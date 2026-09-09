# Untyped defaults checkpoint and continuation

Strict92/runtime93 subsequently passed independent review on917/309b046c; see the
[current contract](SOURCE-STRICT-DECLARATIONS.md) and
[review](../../coverage/semantics/strict-declaration-review.json). This document's
909/910 preparation identities remain historical. Typed parameter/return integration
is next; no typed execution or full callable closure is claimed.

Compiler90/runtime91 are independently accepted at c7cb1b44 on exact909/e25eb2b9:
code1fce6586, compiler2b247d81 and runtime8151b96d. The
[review](../../coverage/semantics/default-parameter-review.json) binds native
originals, complete states, source projections, raw protocols and production CLI.
This is a bounded stage of complete core; callable and constant families stay partial.

## Accepted units

1. Ordinary user constants through compiler88/runtime89 supply ordered activation,
   namespace/import/fallback lookup, value ownership and nonowning allocation
   provenance. Their [899 review](../../coverage/semantics/user-constant-review.json)
   and test-only correction bridge retain their historical identity.
2. Untyped positional defaults through compiler90/runtime91 supply omitted receives
   after provided binding and callee activation. Supplied arguments skip evaluation.
   Declaration contexts, cache provenance, fresh reference cells, array COW and
   abrupt cleanup are accepted in the [runtime contract](SOURCE-POSITIONAL-DEFAULTS.md).
3. Lexical strictness, parameter/return types and reference returns follow. Named,
   unpacked and variadic arguments, other callables, object defaults and the
   remaining [core checklist](CORE-CONTINUATION-CHECKLIST.md) are required later work.

## Interface and retained constraints

The [compiler contract](DEFAULT-PARAMETER-COMPILER.md) connects the byte-exact
historical signature17 suspension to shared constant compiler45. Actual default
origins are `declaration ++ [PCFIELD 3, PCINDEX i, PCFIELD 6]`. Default policy
prevents ordinary/persistent constant substitution while preserving true/false/null
and original declaration context. Every parameter emits its receive opcode line.

`pfunction.DEFAULTS` contains ordered zero-based source indexes, original origins
and `PDSTORED | PDDEFERRED`. Compiled pool/code roots include defaults dropped by
required-after-optional normalization; receive/cache roots require surviving
descriptors. Stored defaults borrow the existing pool. Deferred receives reuse
actual expression evaluation and the constant observer. Public guards project
source descriptors and validate runtime shape/ownership without reconstructing
arbitrary legitimate values or their execution history.

The owning DEFAULTCACHE table retains values plus nonowning classes. Cacheability
comes from actual [allocation operations](CONSTANT-VALUE-CLASSES.md), never final
string length. Successful non-refcounted, side-effect-free results can be cached;
failed evaluation adds no entry, while previous successful entries survive later
errors. Pinned RECV_INIT installs an evaluated cache before subsequent type checks.
NEW is the only pinned AST side-effect setter and remains unadmitted: object
activation must extend the cache condition atomically. Fresh omitted by-reference
parameters begin as ordinary cells and are promoted only by actual alias acquisition.

## Evidence and next review

The retained119 default/cache profiles were replayed on accepted899 before repairs;
116 were Unsupported and three already agreed. Their
[baseline archive](../../coverage/semantics/default-review-current-baseline.json)
and [diagnosis](../../coverage/semantics/default-review-diagnosis.json) preserve
original contexts, source bytes and failures. Final acceptance adds focused arity,
cache-failure and coalesce controls, source/owner/resume gates and two complete
historical no-default state bridges. Original compiler filename mismatch, fixture
failures and interpreter nondeterminism remain classified separately from agreement.

The [reviewer handoff](DEFAULTS-REVIEWER-HANDOFF.md) binds private strict92/type
preparation and the next audit. Preserve new concrete native/current909 failures
before repair; derive finite descriptor/task invariants from actual source. Broaden
regressions for changed shared paths or unresolved risk, not unchanged counts.
Full current-source/full-syntax/fresh offline and complete-core validation remain
mandatory. Authority is pinned `vendor/php-src` commit
34308a6666b2d489c509541ea9befea9e2b42348, PHP8.5.10 CLI NTS64.
