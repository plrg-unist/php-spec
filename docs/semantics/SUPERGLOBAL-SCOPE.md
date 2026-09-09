# Compiled superglobal scope across function frames

The pinned compiler selects `ZEND_FETCH_GLOBAL` only when the variable name is
known during compilation and registered as an auto-global. A runtime-computed
name with identical bytes uses the active local table. `CODE.GLOBALS` records
that decision at the original source occurrence. Source constants and the
original variable node validate each marker; absent required markers, duplicate
markers and markers on an incompatible occurrence reject execution.

`82-superglobal-scope.watsup` applies that decision only around the final name
operation. Name expressions, dimension keys, right-hand sides and function calls
retain their active frame. Existing `BASE_GLOBAL` location protocols handle
superglobal dimensions, quiet reads, coalescing, updates and compound assignment.
An ordinary read captures the global value before a later call; a dimension
base remains delayed through key evaluation. Public request callbacks replace
the request table binding while preserving active locals and aliases to the old
cell.

The try-CV reference shortcut excludes auto-globals, matching
`zend_try_compile_cv`. Their reference fetch therefore occurs through ordinary
source acquisition. Function-local `global $_ENV` and a folded constant-name
variant bind the global name to itself. An activated dynamic `global $$name`
creates a local alias even when its runtime bytes are `_ENV`.

Direct `GLOBALS` snapshot lowering bypasses ordinary name-fetch registration.
The descriptor validator permits its established try-CV registration in global
statements and non-reference list right-hand sides, without requiring a marker
for snapshot occurrences. Computed constant `GLOBALS` remains subject to its
source compilation path.

Compiler CV visitation now receives its explicit occurrence path. This fixes
`$_GET[0] = $_GET`, whose optimized right-hand compilation formerly attached the
right-hand global marker to the left-hand key occurrence.

The [paired call review](../../coverage/semantics/calls-final-review.json) retains exact original PHP source and request facts, native
stdout/stderr/status, checked ASTs, full old machine states, immutable SpecTec
module snapshots, source comparisons, callback state assertions, descriptor
negatives and resumed heap/foreach ownership checks. This work does not close
pending reference parameters, named/unpacked arguments, defaults or types.
