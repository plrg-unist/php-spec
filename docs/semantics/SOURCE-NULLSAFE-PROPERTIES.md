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
A post-name NULL remains outside this bounded target policy, rather than becoming
a second short circuit. Other chain/quiet/temporary/This, Warning/handler and
property-storage domains keep their existing limits. The
[review](../../coverage/semantics/property-nullsafe-name-review.json) separates
the original model11/native22 mismatch, corrected source1 and first-pass141
precheck/owner/history/budget conditions from current composition evidence.
