# Executable semantics design

The checked syntax adapter now offers `execute`: it constructs and checks the
actual `program` value before passing that value to `$php_run`. Authored modules
are listed once, in dependency order, in `spec/semantics/modules.json`. The direct
SL runner elaborates, checks executable bindings, and structures those modules
through Result-returning library APIs. It disables caches and checks encountered
alternative successes. No PHP evaluator computes semantic results.

The machine carries explicit pending tasks, output/diagnostic events, a completion,
and a variable environment mapping byte names to cell identities. Cells contain
`UNDEFINED` or a PHP value; missing names, undefined slots and null remain distinct.
Ordinary assignment copies a value into the designated cell. Reference rebinding
changes one name's cell identity, leaving other aliases attached to their original
cell. Unset removes the binding. Writable paths designate either a variable cell
or an element in an internal array container. Property type sources remain pending.

An operand is either a captured value or a delayed compiled-variable read. Dynamic
name expressions can therefore retain a delayed read across RHS effects. A dynamic
write fetch initializes an absent cell to null before consuming its RHS operand;
a direct variable assignment reads its RHS first. Discarded direct variable reads
are eliminated by the pinned compiler, whereas dynamic fetches remain observable.
Diagnostic consumers also retain the compiler line after child compilation;
ordinary assignment explicitly resets that line to its left variable. AST start
lines alone are insufficient for multiline arithmetic. These distinctions follow
`zend_try_compile_cv`, `zend_compile_assign`,
`zend_compile_assign_ref`, the `ZEND_FETCH_*`/`ZEND_ASSIGN*` handlers, and
`zend_assign_to_variable_ex`; minimized source cases retain their diagnostic order.

The driver spends one budget unit per task transition, including expression
continuations. PHP values distinguish null, booleans, signed integers, float bits
byte sequences and internal array-container IDs. Base64 decoding and integer
decimal output are pure `.watsup`. Calls, objects, handlers and resumable control
remain pending in the feature
inventory. Access to an unimplemented request-owned variable is Unsupported,
including reference acquisition and unset; it cannot fabricate an ordinary local.
The guard follows this pinned startup profile; `_SESSION` is ordinary because the
session extension is absent. `http_response_header` is locally scoped: computed
names, direct writes/references and unset work normally, while literal reads remain
Unsupported until the compiler tracks its per-scope assignment/deprecation state
(`zend_try_compile_cv`). No extension behavior is inferred from name spelling.

The implemented source paths handle empty statements, blocks, inline bytes, scalar
output, assignments, reference rebinding, dynamic names, unset and the numeric bridge below. Its independent static pass rejects a bare
`break` outside loop/switch before output. Unknown constants produce an Error. Selected integer limits and INF/NAN have pure
initial values; other known but unimplemented startup constants produce Unsupported. The startup names
catalog records the pinned CLI environment (including excluded library names),
not computed semantic values. `scripts/semantic-constant-names.py` regenerates the
pure lookup. Source evidence is `zend_compile_break_continue`, `zend_compile_echo`,
`ZEND_ECHO`, `ZEND_FETCH_CONSTANT`, and `zend_get_constant_ex` at the dependency pin.

The numeric bridge decodes literal binary64 hex payloads in the specification,
then dispatches scalar unary signs and addition/subtraction/multiplication/division
to the pure numeric modules. Numeric-string conversion retains warning order and
separate TypeError/DivisionByZeroError completions. Echo uses precision 14 and emits
NaN conversion warnings. Strict scalar identity gives source tests a type observer,
including exact versus nonexact division, int/float distinction, signed zero and
NaN. See NUMERICS.md for helper evidence and still-pending numeric operations.

Dynamic names use the same explicit scalar string conversion and warnings. A pure
folding classifier detects NaN and array names whose warning belongs to compilation; those
cases are currently Unsupported until the compile phase accumulates diagnostics.
Emitting that warning at runtime would change its order. This pending case and
missing source context remain distinct from modeled PHP failures. Object/operator
protocol dispatch and callbacks are later obligations, not native fallbacks.

Ordinary arrays use ordered key/value entries and signed next-index history.
Literal construction evaluates key expressions before values, but consumes delayed
variable values before delayed keys. Dimension bases have separate descriptors:
dynamic names and nested dimension fetches remain delayed through key-expression
effects, while a computed name value is captured. This differs from a dynamic
variable used as an arithmetic value. Null and float key conversions retain their
ordered diagnostics; undefined variable keys suppress the null deprecation only
in literal construction. Missing string-key diagnostics truncate at NUL, matching
Zend's `%s` rendering. Reads, nested strict identity and left-biased union are
implemented. Strict identity first checks shared container identity, observable
for arrays containing NaN. Containers are shared by value assignment. Ordinary
simple/nested assignment and append copy each selected container shallowly before
mutation, preserving other value copies and variable-cell aliases. This is an
abstraction for the current absence of embedded reference entries; it must become
conditional separation with reachable edge/temporary accounting before embedded
references are admitted. Embedded references and unpacking remain pending.

Write preparation retains delayed name/key operands through RHS evaluation.
Dimension assignment acquires a keyed slot before reading a delayed RHS, whereas
terminal append reads its RHS before the overflow check. Missing/undefined/null
containers become arrays; false conversion emits its deprecation after creation.
New element slots retain an explicit uninitialized state. Zend specially captures
a syntactically matching root-variable RHS (`$a[0]=$a`) before location acquisition.
Dynamic roots and variable aliases can instead create cycles even without embedded
reference entries. Strict comparison protects active left-container IDs and returns
a PHP Error for recursive dependency; same-container identity still succeeds.
These rules follow `zend_compile_expr_with_potential_assign_to_self`,
`ZEND_ASSIGN_DIM`, `zend_fetch_dimension_address` and `zend_hash_compare`.

Dimension unset preserves append history and separates shared paths even when the
key is absent. It never creates an absent slot. A missing direct-variable base
warns, while a missing dynamic-name base is quiet. Terminal unset suppresses the
null-key deprecation; intermediate dimension access retains it. False/scalar
containers also differ in when they consume a missing key. These distinctions
follow `ZEND_UNSET_DIM` and `ZEND_FETCH_DIM_UNSET`, with independent byte/line/order
fixtures. Empty `[]` reads and unsets are rejected statically before output;
intermediate string offsets remain pending with the string access protocol.

A pure constant classifier reuses the array/numeric rules on isolated state and
accepts only normal results without diagnostics. This determines compiler source
lines: a folded array retains its first element's effective line, an empty array
uses its closing line, and a runtime array ends on its last compiled value.
Source evidence is `zend_try_ct_eval_array`, `zend_compile_array`,
`zend_delayed_compile_dim`, `zend_ast_create_list_1`, `ZEND_ADD_ARRAY_ELEMENT`,
`zend_fetch_dimension_address_inner` and `zend_hash_compare_impl`. Compile-time
array-key errors remain explicit Unsupported until their static phase is modeled.

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
before and after each campaign. The authored and seeded cases establish the current
scalar, variable-storage and ordinary-array literal/read/write/unset slice;
they do not establish complete PHP semantics or BOLA freedom. Compact current
evidence is `coverage/semantics/source.json`; exact raw observations are regenerated
in the ignored `coverage/results-semantic-source.jsonl`. `--prefix ID` runs a
focused source subset plus all outcome negatives and writes separate `source-selected`
reports, preserving the last full campaign. The earlier phase0 report
is historical evidence for its recorded fingerprint.
