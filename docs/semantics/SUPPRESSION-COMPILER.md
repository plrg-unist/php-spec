# Suppression compiler100

Paired code14003331 installs these compiler bytes with runtime101 at
951/c6501bd8. The
[exact pairing](../../coverage/semantics/suppression-compiler-pairing.json) retains
942 unchanged shared files, four runtime/test/build changes and five added tests
from compiler946, with all shared modes equal. Independent runtime acceptance
and canonical publication remain separately recorded.

Compiler100 admits ordinary error-suppression expressions through the checked
source compiler. It compiles the child in PPR, retains the resulting operand kind
and enclosing source line, and leaves runtime101 to enter/restore the reporting
context and fetch a deferred direct variable before restoration. Pinned
`zend_compile_silence` forces that variable read inside BEGIN/END_SILENCE.

A known result remains visible to enclosing constant compilation: `@false &&
($GLOBALS=1)` skips the forbidden right operand. A PPCEFFECT marks each known
suppression result so the existing33 effect selection and EVAL_EFFECT path still
execute its region when the enclosing result is folded. Ancestor selection
prevents duplicate replay of nested/list effects. Non-idempotent append originals
verify that one list assignment adds only one array entry.

Suppression transparently preserves `$ppsend_var`: `f(@$a)` supplies a temporary
value while `f(@g())` can preserve an actual call reference. Source reference-return
designation98 and shared call/enclosing-line policy78 are unchanged. Both
`return @$a` and `return @g()` remain VALUE-designated; the runtime return Notice
is outside the restored region. Multiline typed-return evidence retains call4,
parent5 and return5. Static child diagnostics occur before suppression executes;
constant-default suppression remains rejected.

The [frozen compiler archive](../../coverage/semantics/suppression-compiler-originals.json)
2cb921c7788ab453380f79aeb2259977efec3532d45f89edaa3091d7769ccae7
binds3515 paths with exact bytes/modes, full942 and946 input maps, seven new native
originals on942,17 same-source lint phases/179 assertions on first944/e02f, and
maintained17 phases/131 source projections on compiler946/2e82245f. Updated
reference-return compilation passes58 phases/49 projections, retiring exactly
the two prior suppression boundaries. Historical12 send-kind/36 and111
destructuring/32 fixtures replay under946. These overlapping gates are distinct
from ordinary runtime agreement and the guarded-candidate pairing. The fresh17/131 author compiler gate on951/ff8d
bridges to final951/c650 through exactly one demand-test print correction; the
other950 files and all modes remain identical.

The archive retains frozenf38/e39/source-send originals and two failed phase
fixtures with exact original producer hashes. Initial setup failures before any
native execution have descriptions only; no nonexistent raw stderr is claimed.
[Runtime guards, reporting masks and ownership](SOURCE-ERROR-SUPPRESSION.md),
with independent acceptance, are separate. Named/unpacked/variadic sends, object protocols, handlers,
exceptions/finally and other full-core obligations remain required.
