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

Module378 adds real `IteratorAggregate` acquisition to foreach. Implicit getter
receivers remain borrowed; each returned Aggregate occurrence owns its raw
retval, and layers retire inside-out before terminal Iterator/Generator startup.
The original iterable stays alive through first rewind/valid or Generator yield.
Raw valid retval cleanup precedes original input retirement, then the existing
cursor runs current/key/body without repeating initial valid. Acquisition or layer
retirement errors prevent startup. Retval cleanup throws release data before
input; an input destructor throw prevents current/body while data remains protected.

Persistent iterable CVs remain borrowed without reference conversion. A
reference-valued original call is dereferenced for acquisition while its raw HCELL
survives until operand retirement. Raw reference getter returns are rejected
without dereferencing. Reference foreach accepts actual reference-yielding
Generators; terminal Iterator results raise Error and nonreference Generator
results raise Exception. Changed original CV/reference operands and wider
reference-location modes remain explicit Unsupported boundaries.

A Generator getter's stored foreach receipt owns its receiver once and binds the
actual source statement and iterable line. MAIN break uses the compiled foreach
boundary for user close execution. A genuine active close frame may move with a
Fiber VM during finally suspension; saved close IDs participate in unique
Generator operation ownership across object, caller and closer VMs. Other
Generator transfer contexts retain their previous boundaries. The
[foreach ledger](../../coverage/semantics/foreach-aggregate-review.json) records
the earlier twenty selected original agreements, historical NaN control and
focused reached checks at their original cuts.

Initial Aggregate and later ordinary Iterator valid NaN results now dispatch the
ordinary Warning before choosing the next foreach action. The raw retval stays
owned through handler invocation, return cleanup and Fiber suspension. A live
numeric reference is reread after the handler writes; a copied NaN remains true.
The raw owner clears before current/body or initial input retirement. A throwing
handler releases raw retval, then Iterator data, then any initial input, while
preserving the original Throwable. Default no-handler warnings keep the real
iterable line and source filename. [NaN evidence](../../coverage/semantics/foreach-valid-nan-review.json)
records eight exact agreements and eighteen genuine-source groups/495 physical
premises at separate retained cuts.
Foreign raw reference payload tags remain a named Unsupported boundary.

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
publication and nested hard eval/include compilation failures preserve the original fatal
and genuine user trace. The compact compiler plan is checked against the accepted
source image; pause/resume chronology proves the actual publication prefix.
Compiler continuations have one real task owner and cannot hide in source wrappers
or branches. Concrete Traversable-only classes still await the native core-fatal
location (`Unknown`, line0).
Module275 preserves that recorded primary when a deferred runtime class link
fails inside the formatter. It retains the genuine inner eval/include trace row,
replays the recorded notice prefix and retires only discarded source owners.
Chronological replay rederives the failed source binding and rollback; the actual
report requires its failure record and genuine caller cause.

Aggregate yield-from has its separate [acquisition route](GENERATOR-DELEGATION.md).
Ordinary-call unpack and
wider original/reference operand modes remain required. ArrayAccess, wider
ordinary object/reference traversal and complete lifecycle remain unfinished.
This milestone does not establish complete traversal or complete PHP core semantics.

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
Actual23c composition source2 at5cf39c0dd covers dollar-curly compiler callbacks
changing live reporting and pending compiler exit before request destruction.
One actual261 source at0ef99 confirms NaN-to-object warning suppression and the
retained scalar during a source fatal formatter.
Seven new sources at4293f196 confirm deferred runtime eval/constant/include
failures and give the four remaining258 eval originals their first agreements.
Independent strict-SL eval81/constant83/include84 pass at the same semantic cut;
their raw record is `.tools/traversal-review-14/eval-protocol-independent-rb9xcsp6/report.json`.
`python3 tests/semantics/runtime_formatter_protocol.py` checks genuine runtime
links, reported primary/history authority and saved-owner retirement in strict SL.
Raw native/model commands, outputs, revisions and runtime profiles stay in ignored
`.tools` directories; the harness records each selected run separately.
