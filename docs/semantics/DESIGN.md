# Executable semantics design

The checked syntax adapter now offers `execute`: it constructs and checks the
actual `program` value before passing that value to `$php_run`. Authored modules
are listed once, in dependency order, in `spec/semantics/modules.json`. The direct
SL runner elaborates, checks executable bindings, and structures those modules
through Result-returning library APIs. It disables caches and checks encountered
alternative successes. No PHP evaluator computes semantic results.

The current bootstrap machine carries pending statement/echo tasks, output events,
and a distinct completion tag. Its recursive driver spends one explicit budget
unit per transition. This establishes the execution boundary; storage, calls,
objects and resumable control remain pending, as recorded in the feature inventory.
PHP values already distinguish null, booleans, signed integers, float bits and
byte sequences. Base64 decoding and integer decimal output are pure `.watsup`.

The initial slice handles empty statements, blocks, inline bytes, literal output
and discarded scalar expressions. Its independent static pass rejects a bare
`break` outside loop/switch before output. Unknown constants produce an Error;
known but unimplemented startup constants produce Unsupported. The startup names
catalog records the pinned CLI environment (including excluded library names),
not computed semantic values. `scripts/semantic-constant-names.py` regenerates the
pure lookup. Source evidence is `zend_compile_break_continue`, `zend_compile_echo`,
`ZEND_ECHO`, `ZEND_FETCH_CONSTANT`, and `zend_get_constant_ex` at the dependency pin.

The static pass currently rejects unsupported syntax before execution. This is a
visible bootstrap limitation, not a claim that unsupported code always executes.
Source-dependent errors require an actual positive source line; edited values
without one return Unsupported. The public source command supplies original file
identity for diagnostic rendering, with no pretty-print round trip.

`bin/php-semantics FILE` emits a JSON observation: status, base64 stdout/stderr,
exit status, diagnostics, events, and unsupported reason. Modeled PHP failure is
separate from malformed input, frontend failure, interpreter failure, process
failure, wall timeout and transition-budget exhaustion. Diagnostic rendering is
an observation projection; semantic rules produce structured completion/events.
The baseline profile is `tests/semantics/profile.json`, described in CORE.md.

`python3 tests/semantics/validate.py` executes authored original-byte fixtures in
fresh semantic/oracle processes under the same file identity, directory, profile
and locale, compares exact output channels and status, and retains raw classified
negative outcomes. It reuses the syntax harness dependency-closure fingerprint
before and after each campaign. These few bootstrap cases establish runner
integration only; they do not establish complete PHP semantics or BOLA freedom.
