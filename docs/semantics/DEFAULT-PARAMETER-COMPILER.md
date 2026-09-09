# Untyped positional default compilation

Compiler90 uses the existing signature17 suspension and constant45 folder.
It compiles each original parameter default in the declaration's namespace,
imports and function magic context before compiling the body. Source defaults
are admitted only with the paired runtime91 receive/cache implementation and
its checked ownership/source guards. Types, reference returns, variadics,
named/unpacked arguments and additional callable forms remain later core work.

`$psstep_start` stops after parameter guards and before default/type/optional
normalization. Compiler90 resolves that request through45 and the accepted88
constant-expression validator/emitter, then resumes17 with the actual folded
value's materialization kind or `deferred`. The legacy `$pscompile` wrapper
continues resolving requests through its existing literal helper. No duplicate
signature normalization or constant evaluator is introduced.

The explicit `pfstate.DEFAULT` policy inhibits ordinary and persistent constant
substitution in both45 and46, while retaining language true/false/null. Folding
precedes validation of the remaining expression; a skipped invalid branch can
therefore disappear. Unsupported object/class/closure/callable constant forms
remain explicit. The policy is cleared before body compilation.

Each `pfunction.DEFAULTS` entry records a zero-based `INDEX`, original `ORIGIN`
and `PDSTORED` or `PDDEFERRED`. Stored values borrow the existing unit pool.
For declaration path D, parameter i's default path is
`D ++ [PCFIELD 3, PCINDEX i, PCFIELD 6]`. Normalized required parameters have no
receive descriptor, but their original defaults still compile, diagnose and
retain pool/class/code facts. Each parameter also emits a `CODEEXPR` at its
actual parameter root, carrying the emitted receive line for runtime errors.

Function CODE includes its original parameter roots and body. Nested function
parameter roots are excluded from the enclosing function's CODE by the existing
ownership projection. Per-unit CODE retains its existing flattened form.
Pool/class guards must accept only actual checked parameter field6 descendants;
receive/cache guards additionally require the surviving matching descriptor.
These are runtime91 obligations, not a relaxation to arbitrary source paths.

Authority is PHP8.5.10 source34308a6666b2d489c509541ea9befea9e2b42348:
`zend_compile_params` (parameter/default ordering, substitution flags and receive
emission), `zend_const_expr_to_zval`, `zend_eval_const_expr` and
`zend_compile_const_expr`. The exact pinned source files accompany the evidence.

The frozen compiler candidate has902 inputs (standard fingerprint9b36dbb4).
Its57 source cases contain54 exact phase comparisons,3 explicit later-core
boundaries and51 descriptor/context assertions. Focused regressions cover41
named-function comparisons plus5 remaining signature boundaries,42 shared
constant observations plus5 probes,45 user-constant phases plus10 boundaries,
and48 magic-constant sources with their existing metadata/context controls.
The two former named-function default boundaries have retained899 originals.
No broad compiler, full callable, full syntax or offline campaign is claimed.

The first wrapper manifest used a JSON-map digest9d7b3919; the retained
fingerprint-label-correction records its alignment to the standard902/9b36dbb4
fingerprint with all file hashes/modes unchanged. Raw gate identities are not
rewritten. Retained setup failures include declaration-order errors and an
optional-pattern ambiguity fixed before the passing gates. An attempted direct
constant-context helper run failed before testing because the private root has
no Opam switch; the focused wrapper instead verifies the copied runner hash and
explicitly records that no rebuild occurred.

The initial39 baseline capture reused a historical compiler filename while its
fresh native lint used the copied filename. Those runs remain a nonpaired setup
attempt, with the immutable initial8276 archive retained. The corrected39 use
one identical source file for native and compiler requests on unchanged899.
`original-profile-correction.json` records both identities; the passing57-case
gate always used matching filenames and was unaffected.

The paired implementation is committed as `1fce6586`, with909 inputs and
standard fingerprint e25eb2b9. The companion
[compiler pairing report](../../coverage/semantics/default-parameter-compiler-pairing.json)
records the exact eight copied compiler/test paths, merged schema token equality
and ordered registry bridge. The archive retains its historical
compiler-only scope; runtime acceptance and protocol evidence are separate.
