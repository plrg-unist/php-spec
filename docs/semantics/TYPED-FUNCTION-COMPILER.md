# Typed positional function compilation

Compiler 94 admits normalized builtin scalar/container types and legal unions for
positional parameters and returns. Supported atoms are null, true, false, bool,
int, float, string, array and mixed, plus void/never return types. It reuses module 16's
type normalization and module 17's complete signature/default suspension pipeline through
90 and the shared constant folder. No second type or default evaluator is added.
Runtime 95 must pair actual receive/return verification with source and ownership
guards before typed source execution is admitted.

Class, intersection/DNF, object, callable, iterable and class-relative protocols
remain explicit dependent core work. Reference returns, variadics, named/unpacked
calls, closures and additional callable forms remain separate required increments.
Existing declaration diagnostics run before an unsupported normalized signature is
rejected. Unsupported outcomes never count as semantic agreement.

`ppstate.RETURNS` carries the normalized type of the body currently compiling. It
starts empty, is set after header completion and is restored when a nested function
finishes. `pfunction.ENDLINE` comes from checked declaration metadata. Every
original return statement emits a CODEEXPR with its emitted line, after compiling
its expression. These roots remain subject to existing function ownership projection.
No runtime return value or caller-strictness field is introduced by module 94.

Return static checks follow pinned PHP 8.5.10 `zend_emit_return_type_check`: void
allows bare return only, with a distinct suggestion for a compiled constant null;
never forbids every explicit return; other declared types forbid bare return,
using the null suggestion for nullable/mixed types. Expression compilation errors
retain priority. Implicit fallthrough remains a runtime check using ENDLINE: void
allows it, never fails distinctly, every other declared type reports none returned.

Existing module 90 parameter roots preserve receive lines and actual default origins.
Module 17 may normalize a stored integer default to kind float while the source pool
still contains the integer; runtime materialization must follow the normalized
kind. Deferred default caching remains before later type verification/coercion.
Five new native controls establish that a provided typed argument can fail before
a later required argument is missing, and reference coercion warnings can precede
that arity error. All supplied argument expressions execute before receive checks.
Runtime 95 owns this schedule and verification before return-frame cleanup.

Compiler 920/495fd39b has nine changed inputs over accepted strict 917/309b046c.
All initial 918/1406d4b9 code bytes are unchanged; final differences are two new
test files and three named-function controls moved from pending to comparisons.
The portable 64-case gate checks 56 exact native compilation phases, eight explicit
boundaries and 38 source/type/line projections. Focused regressions pass 44 named
comparisons plus two pending, 54 default phases plus three pending, and 37 strict
phases plus two pending. No broad helper or full callable campaign is claimed.

The evidence retains 35 selected historical/current 917 compiler and runtime
classifications, 29 new native phase/current 917 compiler originals and five new
native/full-request runtime/current 917 compiler receive-order originals. Native
compilation phases and execution outcomes are kept separate. Historical requests
without explicit primitive payload are not promoted to new full-request runtime
agreements. The portable typed gate and new originals retain recorded worker
packets, stderr and closure. Legacy focused wrappers retain decoded worker records
and closure plus raw subprocess streams; their narrower transport scope is explicit.
The initial module 94 constructor parse failure and its exact source are preserved.

The paired 926/baa85f57 freeze preserves all seven copied compiler/test files
byte-for-byte with their modes. Its storage declaration preserves the exact
source-owned ENDLINE field; its ordered module registry adds the two runtime 95
modules. The separate pairing report records those checks. Runtime acceptance
and the maintained paired compiler gate are reported independently.

Paired code commit `0ed17419` installs final 926/599f3963. The only change
from the earlier 926/baa85f57 freeze adds a missing helper to the maintained
protocol test: all other 925 files and every file mode are unchanged. The pairing
report embeds that bridge. Earlier compiler, source and state results retain their
original fingerprints; the corrected protocol gate ran afresh on 926/599f3963.
