# Executable semantics design

The checked syntax adapter now offers `execute`: it constructs and checks the
actual `program` value before passing it and the actual source filename to
`$php_run`. The specification decodes checked base64 filename transport into the
machine's per-unit `FILES` context without host character conversion. Authored
modules are listed once, in dependency order, in `spec/semantics/modules.json`. The direct
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
Checked source units and structural occurrence paths now travel with task scopes;
[Source origins](SOURCE-ORIGINS.md) describes retention, validation and budget
restoration. The internal [compiled pool installer](COMPILED-POOLS.md) retains
permanent per-unit roots and remaps array IDs above existing backing storage.
Source execution does not yet install pools or consume compiler facts.

An operand is a captured value, a delayed compiled-variable read, or an owning
reference-result cell. `ZEND_ASSIGN_REF` copies the reference wrapper into its
expression result. Consumers dereference that fixed cell at consumption time;
later writes change its value, while rebinding a variable name does not retarget
the result. Its `HCELL` root keeps the cell and contained array alive after the
last environment binding is removed. Ordinary assignment and array insertion
consume its value without creating an embedded alias. The retained
`reference-assignment-result` regression distinguishes PHP's result `4` from the
previous erroneous captured-value result `3`; it was absent from the earlier
371-case selection and is now a mandatory source comparison.

Dynamic
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
simple/nested assignment, append and unset separate only shared containers,
preserving other value copies and variable-cell aliases. A sole container owner
reuses the array. Shallow copies unwrap a singleton reference except when that
reference points back to the source array; other wrappers remain shared. Union
duplicates its left entries with this rule, while the right merge unwraps every
singleton wrapper without a source-self exception (`zval_add_ref`). Conflicting
right keys skip the copy constructor. The merge advances its target graph per
insertion, with both borrowed operand arrays retained until completion. These
wrapper rules now also have source evidence through variable-source reference
literals. Writable element sources acquire references after path separation;
element targets replace the final entry's alias binding. Unpacking remains pending.

The allocation helper separates allocated cells/containers from historical backing
vectors. Incoming ownership counts include repeated root/entry edges, but expand
each allocated node once. Releasing nodes with zero incoming owners cascades;
unreachable cycles and their outgoing reference owners survive until collection.
This distinction is observable in singleton-reference array copying before versus
after `gc_collect_cycles`. The pure graph collection operation has no PHP trigger,
return-count, destructor or automatic-GC claim. The source driver now prunes
after each completed task transition. Location separation also prunes after
discarding its borrowed lookup result; source GC remains pending.

Captured task operands, array builders and explicit `HELD` values contribute roots;
delayed variable descriptors borrow their cells. Task transitions move captured
values and discard consumed results instead of retaining obsolete roots. The root
projection applies at audited task boundaries. Array write/unset and binary helper entry
consumes the current task and moves its captured path, RHS and scratch inputs
into `HELD` before reusing `RESULT` for borrowed lookups. Helper return restores
the previous `HELD`, including on abrupt outcomes. Location separation discards
borrowed `RESULT` before pruning and counting owners, with live inputs already
held. Entry duplication computes singleton counts from a pruned graph projection
that roots its borrowed source table. It does not prune caller allocations:
isolated constant classification has local builder IDs outside machine task roots.
Scalar/read helpers otherwise have no internal pruning or
callback/suspension boundary. Adding callbacks requires explicit resumable roots.

`CELL` and `LOCATION` remain borrowed after variable/element acquisition.
`zend_compile_assign_ref` emits `ZEND_MAKE_REF` for a nonliteral target and
non-CV source; `REF_CAPTURE`/`REF_ARRAY_CAPTURE` move that cell into owning
`REF_DYNAMIC`/`REF_ARRAY` tasks across target designation. Literal string, integer and float variable targets
are direct too; they retain the borrowed source protocol. Element acquisition
uses the existing held path designation and COW helpers, then promotes its final
direct/uninitialized slot into a cell or borrows its existing alias cell.
For assignment to a dynamic variable name, a CV source is initialized only after
the delayed target name is consumed. Element reference targets designate their
slot before initializing the CV source; non-CV sources are owned across target
COW and acquisition. Binding replaces the entry's alias, preserving the old cell
for other owners, and returns an owning reference operand. This differs from
literal reference entries, which acquire their source
before consuming the delayed key. CV names include literal string, integer and
floating-point names (`zend_try_compile_cv`); unary and named-constant expressions
remain dynamic even when their values can be folded.

Terminal throw/error/Unsupported outcomes release pending tasks, scratch values
and `HELD`, even when the last task already emptied `TODO`; environment roots and
uncollected cycles survive. This is temporary cleanup in the current machine
without catch/finally or call frames, not effectful PHP request shutdown or future
exception unwinding. Budget exhaustion preserves the interrupted state and roots.
Source-unit/compiled-occurrence identities now travel with runtime tasks.
Source activation of the permanent pool installer and fact consumption are still
required before repeated literal execution in loops/calls.
`tests/semantics/ownership.py` checks graph invariants separately from source claims.
Source anchors are `i_zval_ptr_dtor`, `zend_array_dup_value`, and `zend_gc_collect_cycles`.

Array literals admit references to direct/dynamic variables and writable array
elements. Their constant-evaluation prepass visits every value then key before
checking by-reference flags. Append reads there cause a compiler error with the
ambient array line; its recursion stops at assignments and variable names.
Consequently `$x=&$a[]` is valid while `[&$a[]]` is rejected. Key expressions
are evaluated first; variable acquisition initializes an absent source to null
before the delayed key is read. Thus `[$x=>&$x]` has a null-key deprecation without
an undefined-variable warning. `ZEND_ADD_ARRAY_ELEMENT` creates an owning wrapper
temporary before key conversion; `HELD` retains that cell and captured key/builder
inputs until insertion transfers the reference to an `ALIAS` entry. Duplicate keys
replace the old entry and release its owner at the task boundary. Earlier `HELD`
is restored on normal/error/Unsupported paths. The handler-specific extra copy
around null-key diagnostics remains part of future callback semantics. Source
anchors are `zend_compile_array` and `ZEND_ADD_ARRAY_ELEMENT`. Element target
rebinding has separate rules; by-reference argument/return and foreach remain pending.

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

Public `$php_run` binds actual filename bytes before invoking the ordered compiler.
`33-runtime-compiler.watsup` completes compilation before starting any `PPCWORK`
statement, preserving original checked source units and occurrence paths. Compile
errors suppress all recorded work. Ordered lexical warnings survive a subsequent
ordinary static error or Unsupported completion. Byte-valued lexical fatal messages
use `STATICBYTES`; ordinary static errors retain `STATICERROR`. The renderer projects
both as compile errors with exact byte messages, source lines and status255.

Successful compilation merges partial constant facts and ordinary constant operands,
rejects compiler variable storage, and installs a permanent pool into disjoint runtime
array storage. Compact `CODEEXPR` descriptors retain each expression's ending line
and whether ordinary compilation produced a constant read operand. A partial fact
below a wholly folded parent does not authorize execution. Scoped `AT EVAL` and
`AT DIM_PREP` consume pooled values only for that read permission; write, reference
and unset acquisition retain their designation tasks. Pool values are reused after
temporary cleanup and budget resumption, without allocating another literal.

Runtime consumers obtain compiler lines by the current unit/path and explicit child
path. Missing descriptors in a compiled unit produce missing context, not an AST
line substitute. Internal bare-state fixtures may still use the legacy AST line
helper and `$run_source` trace wrapper; neither is the public source entry point.
The old whole-source availability traversal remains only for that internal test
path. Ordinary compilation still shares its direct-CV predicate, which invokes
the old constant classifier on literal name forms; retiring that narrow dependency
and the legacy trace traversal is pending. Namespace/import work currently
executes only expressions admitted by the ordered compiler; unresolved namespace
constant lookup remains Unsupported. Ordinary string/scalar reads use the reviewed dimension helper through delayed
base resolution. The compiler uses a separate constant-read leaf, preserving
prepass suppression of warnings inside array literals. String writes/reference
errors remain a separate activation gate.

The compiler rejects unfinished syntax before source execution. This is a visible
implementation boundary, not a claim that every unsupported expression would run.
`tests/semantics/runtime_compiler.py` checks compiled execution, pool ownership,
per-occurrence identity and constructed interruption/re-entry states; it does not
claim loop or function execution. Existing original-source comparisons separately
validate the admitted behavior against the pinned engine.

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
