# Runtime continuation

Read PLAN, PROGRESS, AGENTS and the php/php-spec/p4-spectec skills first. Root
orchestrates; compiler owns static/frontend work and reviewer owns independent
evidence/PROGRESS. Never push. The sole oracle remains local PHP 8.5.10 CLI NTS,
64-bit; semantic answers after checked syntax are pure executable `.watsup`.
Complete core remains unfinished. Read [runtime interfaces](RUNTIME-BRIDGE-HANDOFF.md)
and [compiler continuation](COMPILER-HANDOFF.md) before rediscovering old work.

## Comparison checkpoint

Source compilation and execution now connect `==`, `!=`, `<`, `<=`, `>`, `>=`
and `<=>` for the six current values. [COMPARISONS](COMPARISONS.md) explains the
contract. Author gates pass 1,142 exact source observations plus 25 negatives,
232 comparison source/state cases with 3,388 assertions, 48 original comparison
compiler cases, 1,184 broad lint cases and 15 emission-line observations. Independent
review and the separately open fetch discrepancy are recorded by the reviewer.
No semantic family is complete. The four raw overflow draft records remain
byte-identical; all four exact originals now pass through the public source path.

`tests/semantics/comparison.py` and `comparison_compiler.py` consume the retained
comparison phase archive. Their direct fingerprints and the shared source closure
also bind archive bytes. Never overwrite the original disagreement archive or
rewrite fingerprints to make evidence appear current.

## Accepted reference wrapper correction

Code `3585707a`, reports `eebf79e9` and independent
[review](../../coverage/semantics/reference-wrapper-review.json) pass 1,163 exact
sources plus 25 negatives on `1f71f10d`. All eleven original FETCH/final-write/UNSET
sources remain unchanged and integrated; five prior differences now agree.
Independent gates add 79 public sources, 72 replay programs/1,288 assertions and
45 constructed transition checks. Canonical wrapper tests have 21 sources/396
assertions; compiler, origins, bridge and ownership pass the same closure.

[REFERENCE-WRAPPERS](REFERENCE-WRAPPERS.md) defines explicit REFCELLS history.
Acquisition/binding marks stable backing cells; singleton unset and writes retain
history. Fresh bindings are unmarked. Copies may unwrap singleton ALIAS entries
without erasing the original wrapper. Markers add no roots; compiler isolation
rejects them in permanent pools. Generic FETCH/intermediate UNSET and final
ASSIGN_DIM/UNSET_DIM preserve distinct false conversion warnings. Collection
checks remain graph-helper evidence, not source GC admission.

## Following update operators and arrays

The private source candidate uses `.tools/{20-update-compiler,30-incdec,
46-incdec-compiler,53-incdec-source}.watsup` with existing pure05 string helpers.
`python3 .tools/probe-incdec-source.py` passes 77 original programs/1,148 assertions
in `.tools/incdec-source.json`; independent review/publication remains pending. Compiler drafts `46-incdec-compiler.watsup` and
`46-update-compiler.watsup` add PPRW target access and preserve key reads, append
legality and compiler order. Their 48 original static controls live in
`.tools/update-compiler-originals.json`. Four incdec forms precede twelve compound
forms paired with remaining numeric/string dispatch. `??=` needs its own quiet
read and memoized write path. Source context, missing-target warnings, nested
FETCH versus final INCDEC string errors, copied pre/post results, and captured
locations require explicit tests. Call/property target line projections matter
even when the target is statically rejected. Coordinate 20/30/45/46 ownership.

Compiler's unpack/destructure and first-hole metadata drafts remain separate.
Foreach subsequently needs stable cursor/bucket identity and mutation ownership.
Declarations, frames/calls, linking, objects, dynamic sources, callbacks, collection
and resumable lifetime remain pending. Keep the separately documented relative
`static` intentional divergence unchanged; its source activation is still pending.
