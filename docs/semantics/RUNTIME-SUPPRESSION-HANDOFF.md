# Source suppression after reference returns

Historical preparation for accepted951; use [the current variadic handoff](RUNTIME-VARIADIC-HANDOFF.md).

Start from accepted **942/3c331e74**, code563fee7a, compiler46c7d848,
author1c96b30b and [independent review9959e771](../../coverage/semantics/reference-return-review.json).
The complete input/hash/mode manifest is retained in the publication evidence
and `.tools/runtime7-return-candidate/final-inputs.json`. Compiler7/runtime7/review10
continue with proposed compiler100/runtime101. No suppression source admission
is accepted yet.

Preserve reference-return semantic gates942/7951 and regression942/dd8; only the
author state-test generator changed to final3c, with941 other files and all modes
identical. Source12, protocol26/378, independent4 states/1282, author2 states/777,
source31, compiler56+2/49, demand19/38, typed38/acquisition17 and CLI8 pass within
their recorded scopes. The two suppression cases are source projections and
Unsupported boundaries, not runtime agreements.

## Retained source evidence

Read `.tools/compiler6-suppression/STARTUP.md` and `PLAN.md`. Frozen preparation
archive f38c33f7e0d38ff904106bb4bc09f624f25d9a9b12e35ff97fb483312e3ae961
contains1257 paths on immutable933:10 new native/full-request originals (9
Unsupported,1 existing constant-default static agreement),10 same-source lint
observations and7 separately profiled opcode observations. Reuse e39c's two
suppression demand contexts. Replay old requests on accepted942 before admission;
never relabel their933 identities or treat instrumentation as ordinary execution.

Pinned PHP8.5.10 CLI NTS64 remains `vendor/php-src` commit
34308a6666b2d489c509541ea9befea9e2b42348. Inspect `zend_compile_silence`,
BEGIN/END_SILENCE, `cleanup_live_vars`/ZEND_LIVE_SILENCE and `zend_errors.h`.
A direct suppressed CV must be fetched before END; ordinary lazy CV resolution
after END is wrong. Preserve owning KNOWN/REFERENCE results. Suppressed call VAR
and suppressed CV temporary differ for reference sends; use existing ppsend_var
classification, without changing98 return designation or78 emission-line policy.
`return @$x` and `return @g()` finish silence before their VALUE-designated return
Notice; outer `@f()` instead covers the callee. Static errors remain compile-time.

## Runtime proposal to review before implementation

Current pstate has no reporting mask. A saved mask only in TODO is insufficient:
existing abrupt paths can clear TODO before cleanup. The proposed representation
uses global REPORTING plus an active SILENCES stack of source origins/saved masks;
frames save/restore their own SILENCES while REPORTING persists across calls.
BEGIN enters before the child fetch, END resolves only deferred VARIABLE inside
the scope, preserves owning results and performs Zend's conditional restoration.
Abrupt cleanup restores the active scope independently of TODO before dropping
its frame; caller scopes survive normal callee return and unwind on propagation.
This schema and its emission/cleanup boundary still require independent review.

The ordinary native profile uses30719; BEGIN preserves fatal bits. END/live-range
cleanup restores a saved nonfatal mask only while the current mask remains
fatal-only. Do not substitute unconditional restoration. Audit both shared
helpers and direct warning/diagnostic producers, including deferred default
verification. Filtering accumulated events at END or only in the observer is
insufficient. Keep fatal completion/display and diagnostic emission distinctions
explicit. error_reporting(), custom handlers and dynamic registration still lack
runtime bodies; native controls depending on them remain dependencies.

Bind saved scopes and restore tasks to actual suppression source origins and the
owning active/saved context. Keep mask values distinct from source metadata;
avoid reconstructing arbitrary execution history. Test normal and abrupt restore,
nested calls/scopes, output and side effects, owning reference results, one-step
cuts at entry/exit/unwind, and old states with only validated new-field projection.
Runtime owns nested calls, numeric/deprecation emission and reference COW controls;
reviewer owns deferred-default warning/cache and typed-failure restoration controls.

Remaining named/unpacked/variadic calls, closures/dynamic callables, objects,
exceptions/finally, dynamic sources, generators/Fibers, lifecycle and intrinsics
stay required. Full callable integration and final current-source/full-syntax/
fresh network-isolated offline checks remain mandatory. No family/core closure
or new intentional engine departure is authorized by this preparation.
