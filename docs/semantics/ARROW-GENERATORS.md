# Arrow Generators

Module311 compiles by-value arrow Generator bodies through the existing arrow
capture and implicit-return machinery. Arguments, defaults and parameter type
checks finish before creating the Generator. Closure captures are snapshots at
arrow creation; their invocation locals load only when the Generator first
resumes. Parameters shadow captures, and reference parameters retain their real
cells.

The arrow expression remains an implicit return. A used `yield` receives the
sent value or null; arithmetic can consume it before completion. `yield from`
returns null for arrays and the delegated Generator's completion value for a
Generator child. The declared return type checks Generator admission using the
pinned one-level supertype scan; it does not coerce this completion payload.
The original signature stays on the published Closure template.

Lexical, called-class and receiver scope use the existing Closure and Generator
owners. Ordinary and static arrows keep their distinct `$this` behavior.
Delegated child release follows303 and310, including ordinary last-owner close
inside an active Fiber. Nested arrows and Closures classify their own yields;
they do not turn their enclosing arrow into a Generator.

The change removes the obsolete arrow body exclusion and adds a compiler helper;
runtime returns reuse accepted95/118/280. Reference yields remain required and
stop explicitly. A reference arrow containing `yield from` retains the native
compiler rejection. Its diagnostic uses the operand's Zend AST line, including
multiline operands. Wider Generator creation scopes, dynamic/nullsafe and named/
unpacked API forms, IteratorAggregate, parked running Generators, switching
finalizers, request/terminal cleanup, user destructors and GC remain required.
No paused or unaccepted generic return implementation is imported.

Pinned source authority is `Zend/zend_compile.c` (`zend_compile_func_decl_ex`,
`zend_mark_function_as_generator`, `zend_compile_return`,
`zend_compile_yield_from`) and `Zend/zend_ast.c::zend_ast_create_1` in the vendored
PHP8.5.10 source. `Zend/tests/arrow_functions/008.phpt` supplies a seed; maintained
core-only companions replace its `var_dump` observer with language operations
and add independent capture, scope, return and ownership witnesses.

Ordinary YIELD value-CV warnings freeze null before reading a delayed key.
Source/site/name/line and key shape authenticate the continuation. Handler throws
skip this Generator's own body catch/finally, retain the cached key and transfer
the same Throwable to its real resumer. The closed Generator owns its Closure
before frame retirement; this matches `zend_generator_get_gc` and avoids freeing
a last-owned Closure during the new throw shortcut. A pending exception in an
already-entered finally is discarded without adding a previous link. Forced close
is excluded from this warning ingress; a known-value key-CV warning remains
Unsupported.

Literal `$GLOBALS` keys require an array snapshot. The unchanged source uses
explicit primitive request facts through the existing native FD198 provider and
model `--request-context`, with matching file/argv/cwd, clock and EGPCS/JIT profile.
No PHP globals or evaluation answers are supplied. A source-reached role control
rejects a cached scalar while retaining source/code/templates/frames/request and
a valid heap. Writable ordinary superglobals retain their general value domain.

Private validation closes55 distinct maintained originals:44 normal agreements,
nine exact compiler rejections and two required Unsupported controls with zero
agreement. Ten genuine strict-SL programs/groups pass987 setup-inclusive premises
(530 authored,225 independent,203 warning and29 GLOBALS role), including public/
heap admission, malformed controls and exact zero-budget/direct-resumed completion.
The final277 compiler and three affected throw originals pass after the closed
Closure ownership repair. Earlier cuts retain their original identities; unchanged
branches receive no renewed credit. Original warning/signature/prerequisite,
fixture and lifetime failures remain zero-credit records in
[the ledger](../../coverage/semantics/arrow-generator-review.json).

Recovery root is `.tools/traversal-arrow-generators-sjuqxdki`, an exact child of
accepted310 publication23031d529e4c.../276 modules. Its ignored `.tools` records
retain source bytes, profiles, native exits, observations, checked AST fixtures,
evaluated premises and unchanged numeric caps. No311 canonical write has occurred;
accepted289/303/310 are separately integrated at main d56228a77/282.

The isolated current-parent composition is
`.tools/traversal-arrow-generators-current-286`, parent `68393cbbb` with286
modules plus the exact311 source and accepted fixtures. New normal source
`default-fiber-eval-entry-and-child-close` combines an eager NEW default, active
Fiber, captured temporary Stringable eval with a CV ECHO first opcode, and
last-owner delegated-child close. Its native/model tuple is
`A|D1|C|S|R|E4|5|L1|F|M9`. The frozen287 cut passes strict compilation and148
independent reached premises after a narrow84/281 repair: source publication is
checked on the live stack, while parked Fiber tasks retain their own eval-marker
guards. Controls reject live OWNER and parked direct/CHOOSE marker forgeries;
the frame-marker helper uses authentic saved leaf fields. The original invalid
eval response and two fixture syntax stops retain zero credit.

The actual `2a2e1af7c` property/collection parent plus311 passes strict compiler292,
the same source and75 independent cleanup premises. Its genuine retired source
object has one physical HANDLE obligation; removing the task/registry marker
keeps the heap valid but rejects that helper obligation. No occupied GC_RETIRED
slot or public rejection is claimed. Arrow Closure last ownership, new gc/clone
validation and actual close/budget resumption pass. The parked projection also
clears FILECONTEXTS under the existing empty-loader transfer domain; genuine
file-marker runtime evidence belongs to the calls pair. Frozen148 is not renewed.
The later ARG309 join at `93e721d06`/293 is independently reviewed as statically
compatible: shared factoring preserves its predicates and the new append arms
do not match this original. It earns no new execution credit. Ordered Git
integration remains required.

Maintained commands are:

```sh
python3 tests/semantics/arrow_generator_prepare.py --mode full
python3 tests/semantics/arrow_generator_review.py --mode full
python3 tests/semantics/arrow_generator_protocol.py --mode check --sl
python3 tests/semantics/arrow_generator_review_protocol.py --mode check --sl
python3 tests/semantics/arrow_generator_warning_review_protocol.py --mode check --sl
python3 tests/semantics/arrow_generator_globals_role_review_protocol.py --mode check --sl
python3 tests/semantics/arrow_generator_integration.py --mode full
python3 tests/semantics/arrow_generator_integration_protocol.py --mode check --sl
python3 tests/semantics/arrow_generator_cleanup_protocol.py --mode check --sl
```

This bounded slice does not establish complete Generator, arrow or core semantics.
