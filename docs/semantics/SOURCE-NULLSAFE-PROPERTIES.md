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
saved tasks retain live receiver owners through nested name calls. Paused
source and phase guards reject forged syntax, names, lines, quiet mode, or a
short-circuit marker without a chain continuation. This cluster covers public
property/dimension chains. Nullsafe method calls, static property evaluation,
visibility and magic property hooks remain separate dependencies.
