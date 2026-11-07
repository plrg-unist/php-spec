# Nullsafe property chains

The compiler admits nullsafe property reads and quiet `isset`, `empty`, and
coalesce operands. It checks the receiver before a computed property name.
Write, unset, and by-reference return contexts reject nullsafe chains at
compile time. A nullsafe argument to a by-reference function is evaluated as
a value, then raises PHP's could-not-pass-by-reference Error at send time.

Runtime chain preparation carries `BASE_SHORT` only after a nullsafe checkpoint
sees null. Property names and array keys in the remaining property/dimension
suffix are skipped. A successful property fetch whose value is null remains an
ordinary value, so its suffix still executes and reports ordinary warnings.
The marker becomes null at the expression boundary, false for `isset`, and
true for `empty`; quiet preparation suppresses undefined receiver warnings
without suppressing reached name/key expression effects. Function calls and
other independent expressions consume the marker before their caller resumes.

Each pending chain property base retains its checked name and access line;
the original captured-value routes retain live receiver owners through nested
name calls. Paused
source and phase guards reject forged syntax, names, lines, quiet mode, or a
short-circuit marker without a chain continuation. This cluster covers public
property/dimension chains. Nullsafe method calls, static property evaluation,
visibility and magic property hooks remain separate dependencies.

A terminal `$base?->{name()}` value read now also supports the source-proved quiet
global-rebind helper under the existing [plain-property bounds](SOURCE-PROPERTIES.md).
The initial and replacement objects are distinct, preallocated, parentless and
methodless, with initialized public untyped DIRECT scalar slots; a distinct CV
retains the old object. Main/direct-reader context, actual request-cell identity
and relevant cell constraints qualify entry.

The actual receiver read performs the original NULL checkpoint once before name
evaluation. After a nonNULL result, the CV source travels through the existing
nonowning operand carrier. Saved-task authority uses genuine nullsafe source/access lines, the
unique carrier and terminal fetch; it never rereads an old payload or alias.
Completion fetches the current CV into the ordinary property base without another
NULL check. Initial NULL stays on the old `BASE_SHORT` path and skips the helper.
A post-name NULL does not become a second short circuit. The fixed-NULL normal
fetch below extends its earlier target boundary; other chain/quiet/temporary/This,
handler and property-storage domains keep their existing limits. The
[review](../../coverage/semantics/property-nullsafe-name-review.json) separates
the original model11/native22 mismatch, corrected source1 and first-pass141
precheck/owner/history/budget conditions from current composition evidence.

The same exact helper can now copy a defined NULL replacement into the checked
CV. Entry still requires a plain initial object and a distinct retained alias,
with the existing cold context and cell constraints. Only the terminal normal
nullsafe route gains this alternative; ordinary property and quiet consumers
retain their prior object-target admission.

Completion authenticates the source/key/access line and actual terminal fetch,
requires no registered error handler or buffered/blocked output, and creates the
existing `BASE_PROPERTY PNULL`. It emits nothing yet. The normal fetch then uses
the old diagnostic kernel to report `Attempt to read property "slot" on null`
and return NULL. Existing reporting-mask behavior remains intact; no handler,
suppression API or new diagnostic continuation is introduced. The
[Warning review](../../coverage/semantics/property-nullsafe-null-warning-review.json)
keeps native/model diagnostic-channel/file/line agreement, 121 new reached-state
conditions and the one affected earlier fixture (144 conditions) separate from
the historical 491-module/141-condition cut. Only that earlier post-name NULL
expectation changes from target Unsupported to a normal base before the Warning.

Terminal single `isset($base?->{name()})` and `($base?->{name()} ?? 7)` now use
the same nonowning transport after the true quiet checkpoint. These routes keep
the old distinct/plain object targets: the replacement's initialized NULL slot
produces false presence or schedules the literal fallback. They do not admit a
NULL replacement receiver or the normal-read Warning alternative.

Source authority requires the actual nullsafe occurrence, true quiet origin and
only one of those two compiled parents. The access line remains separate from
the isset probe or coalesce left/right lines. Both real origin returns and the
terminal single-isset marker, or the actual coalesce parent/RHS, authenticate the
consumer. Saved history requires its unique carrier and a dedicated quiet pair;
an otherwise valid generic `DIM_FETCH` pair cannot stand in for that consumer.
Initial NULL still skips the name through the old marker path. Empty/truth,
wider chains, handlers, other helpers/callers and RHS producers gain no route.
The [review](../../coverage/semantics/property-nullsafe-quiet-name-review.json)
retains the original isset mismatch, separate coalesce native-only observation,
source2, corrected 269 state conditions and the original fixture-binding zero
as distinct cuts.
