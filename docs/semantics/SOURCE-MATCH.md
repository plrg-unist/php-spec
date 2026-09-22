# Match expressions

Modules 143/144 execute `match` using the checked AST and pure SpecTec rules.
The target is PHP 8.5.10 CLI NTS 64-bit with the ordinary semantics profile.
No schema, frontend, adapter or native evaluator changes are required.

The compiler follows `zend_compile_match` and `can_match_use_jumptable` in
`vendor/php-src/Zend/zend_compile.c`: compile the subject, fold leading eligible
integer/string conditions, reject a second default, compile all conditions,
then compile all bodies. The folding prepass stops at the first ineligible
condition. Its warnings can precede a duplicate-default error. Compiled line
markers retain condition, body and unhandled-error positions; an authenticated
flag records table eligibility because it changes undefined-variable warnings.

Runtime conditions use strict identity in source order, stop at the first hit,
and evaluate only the selected body. Multiple conditions share one body; a
default is selected only after all conditions fail, regardless of its position.
Direct CV subjects remain delayed reads and can observe condition mutations.
Temporary subjects retain their value/reference owners through result
materialization. Eligible constant tables read an undefined CV once; sequential
comparisons can warn more than once. A default-only match does not read a direct
CV. Bodies materialize values, including array copies with shared embedded
references and object identities, and cannot supply a writable temporary.

Unhandled matches use the existing `THROWN "UnhandledMatchError"` completion,
with ordinary trace capture and cleanup. `ZEND_MATCH_ERROR` reads its raw operand:
an undefined CV adds no warning, and a reference wrapper gives a type message
instead of the contained scalar text. Formatting follows
`zend_match_unhandled_error`, `smart_str_append_scalar` and the pinned exception
string limit, reusing the existing trace scalar formatter. General Throwable
objects, catch/finally, handlers and destructor unwinding remain explicit later
integration obligations; this increment does not claim those protocols.

Source-derived descriptors and queued-task guards authenticate source occurrences,
indices, lines and source-determined CV/scalar subjects. Captured dynamic values
are validated as live operands, without attempting to reconstruct prior mutable
state. Pauses inside condition/body calls preserve saved subject owners and resume
to the uninterrupted result. Both the production SL path and helper AL path are
validated; these are distinct checks, not a global determinism proof.

Maintained checks are `match_expressions.py`, `match_compiler.py` and
`match_protocol.py` under `tests/semantics/`. The small source catalogs retain
original bytes, source hashes and native expectations. Raw source/oracle/runner
records stay under ignored `.tools/`; the review ledger binds exact manifests,
selections, excluded dependencies and recovery paths.
