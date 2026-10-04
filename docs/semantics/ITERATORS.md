# Iterator foreach

Module224 adds source `Iterator` objects to ordinary by-value `foreach`. The
callback order is `rewind`, `valid`, `current`, optional `key`, body, then `next`
and `valid`. Keys retain their returned PHP values. Direct by-reference traversal
throws before calling any Iterator method.

Implicit calls select the effective public method, retain its declaring and called
class, and pass zero arguments. Saved foreach continuations authenticate the
selected receiver, source statement, callback stage and diagnostic line. Cursor
continuations require one matching metadata entry below `NEXTITER`; their IDs
must differ across the current task list and saved callers, including same-site
recursive traversal.
The iterator and its actual current result remain owned during `key()` and the body;
a reference result is read after `key()` and its original cell survives rebinding.
Break, return, goto and abrupt frame teardown release the cursor and its owners.

Module230 admits omitted or incompatible tentative returns as deprecations.
Checks follow the actual parent and ordered interface prototypes: source methods
can replace tentative obligations, direct Iterator bindings restore them, and
repeated bindings preserve duplicate notices. The no-argument built-in
`#[ReturnTypeWillChange]` suppressor uses ordinary namespace/import resolution.
Hard signature or constant failures default-report their warning prefix.

Runtime notices run after complete class publication. Early `compile_file`
notices wait for all unit publications and retain their order among existing
compiler warnings. Handler arguments identify the physical method declaration;
callback scope and trace retain the real class opcode or include ingress.
Early include trace arguments come from preceding real trace rows; a direct
notice callback exposes no include argument, while ordinary body traces retain
the opened filename.
Throwing handlers leave published classes available; remaining diagnostics use
the live handler mask and reporting settings. Nested includes own separate
queues. Source/compiler chronology authenticates batches, and one continuation
owns each runtime publication or file unit across current tasks and saved frames.

Module236 suspends genuine early `eval` compilation for each class's notices;
generic compiler warnings run at their actual point before publication. The
handler can traverse classes already published, with the real eval caller scope,
line and trace. A handler's exception or exit remains owned while later classes
publish, then prevents the unit's statements from running. A user fatal stops
compilation and retires the compiler owner before request shutdown.

Later hard declaration failures retain their diagnostic prefix and primary fatal
while a pending exception's source formatter runs. Recorded nonfatal diagnostics
stay suppressed during formatting. Formatter throws, exit, conditional class
publication and nested hard eval/include failures preserve the original fatal
and genuine user trace. The compact compiler plan is checked against the accepted
source image; pause/resume chronology proves the actual publication prefix.
Compiler continuations have one real task owner and cannot hide in source wrappers
or branches. Concrete Traversable-only classes still await the native core-fatal
location (`Unknown`, line0).

`IteratorAggregate`, `ArrayAccess`, Traversable argument/array unpacking and wider
ordinary object/reference traversal remain required. Broader object destruction
and cyclic garbage collection remain unfinished. This milestone does not establish
complete traversal or complete PHP core semantics.

`python3 tests/semantics/user_iterator.py --mode native` checks the authored native
expectations. `python3 tests/semantics/user_iterator_protocol.py --select cursor-claims,cursor-alias`
reaches real callback/body states and rejects duplicate or aliased cursor claims.
`python3 tests/semantics/iterator_declaration_notices.py` checks notice order,
prototype replacement, suppressors, file/eval publication and fatal-prefix behavior.
`python3 tests/semantics/eval_declaration_notices_protocol.py --select pending`
reaches a real early-eval pause and checks source-plan, prefix and owner authority.
Its other phases cover callback/traversal frames, nested compilers, retained
exceptions and fatal formatter/file retirement. The `file-public` and
`file-history-retirement` phases use the maintained runner's `--sl` option with
the same strict checks, disabled cache and300-second cap; other phases retain
AL mode. Their43/49 predicates pass at semantic c9e6 (private43b), after the original
AL attempts timed out without a verdict. The ordinary independent phases retain
their separate65/36/28/42/30/45 cut at ea077, nested-fatal57 at3bd and the coherent
function-descriptor forgery24 at c9e6. Authored USERfatal48 and21 distinct source
agreements keep their original cuts; affected nested/file source2 passes at3bd.
Raw native/model commands, outputs, revisions and runtime profiles stay in ignored
`.tools` directories; the harness records each selected run separately.
