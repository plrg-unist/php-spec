# Positional variadic compiler102

The [guarded pairing](../../coverage/semantics/variadic-compiler-pairing.json)
binds compiler955/60fb to installation959/4854:952 shared paths are unchanged;
runtime103, Makefile and the older function-compiler test differ, and four runtime
tests are added. All shared modes match; the four original compiler
implementation/test paths are byte-identical. Guarded source/protocol results
retain959/cee5;959/4d69 changes only that older test, then959/4854 changes
only the dense-state test timeout allowance from300 to900 seconds. Assertions and
implementation remain unchanged across that final timeout-only step.

Compiler102 admits a final variadic parameter with a supported type and compiles
known reference-tail arguments using the final descriptor at every later argument
index. Existing17/90 signature/default checks still precede admission. The fixed
parameter branch remains in78; its premise and the variadic branch are disjoint.
The variadic branch explicitly requires an empty remaining parameter list.

Known dimension tail sends compile in PPW; deferred dimension sends use PPF.
Direct variables, calls and suppression retain the existing source-result rules.
A suppressed reference-returning call remains a VAR send result, and reference
returns from variadic array elements retain98's source designation. Source
parameter, call and later operand lines stay distinct: the new multiline native
TypeErrors use declaration3/call6 and declaration9/call3, each for argument3 and
without the variadic parameter's name.

The [compiler archive](../../coverage/semantics/variadic-compiler-originals.json)
binds full accepted951/440f, failed first953/7791 and compiler955/60fb maps,
including exact bytes and modes. Seven new full-request native originals and
separate preoptimizer profiles cover multiline typing, known/deferred dimension
references, suppression, reference returns and an empty tail after an optional
fixed prefix. Runtime replay and the final guarded pairing are recorded separately.

The maintained compiler gate passes23 exact native lint/static phases and194
source projections, with two catch sidecars explicitly Unsupported. Focused
shared checks pass58 reference-return phases/49 projections,17 suppression
phases/131 projections,359 signature comparisons/28 descriptor checks/174
reference-return checks, and12 send-kind phases/36 projections. Worker streams,
closures, native/runner output and executable hash/mode bindings are retained.
The unchanged numeric runner is reused; semantic modules are supplied dynamically.

The [final compiler supplement](../../coverage/semantics/variadic-compiler-final-originals.json)
retains the stale function-compiler expectation failing on959/cee5 and the
corrected46-phase gate passing on959/4d69. The unchanged variadic source moves
from PENDING to ordinary CASES;958 other inputs and all modes remain equal.

The initial singleton-versus-recursive parameter patterns triggered the pinned
SpecTec SL casify assertion although a trivial AL fixture passed. A minimal
accepted-baseline reproducer isolates that formulation; identical head/tail
patterns with opposite VARIADIC premises repair it without framework changes.
Both failed compiler test fixtures are retained: one used the wrong NParam field
domain; the other incorrectly treated pending catch sources as admitted compiler
cases. Neither fixture repair changed semantic code or removed original sources.

The nested56f preparation retains earlier positional/native controls and explicit
named/unpack dependencies. Named binding, unpacking, exception execution and the
remaining callable/core obligations are required subsequent work; this slice
closes no callable family.
