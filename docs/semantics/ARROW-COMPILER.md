# Arrow compiler and expression-return metadata

Compiler117 adds arrow expressions to the existing real closure template pipeline.
Creation records an unregistered template and its source-derived implicit capture
list; invocation uses the existing signature, argument and return contracts.
Named functions and explicit closure templates keep their own source scopes.
The paired runtime118 owns implicit undefined values, object lifetime, receive
bindings and invocation. Compiler admission alone is not runtime agreement.

Discovery follows the pinned Zend AST traversal. Direct literal variable names
include parser folding; computed names contribute their name expression. Direct
`$this` and autoglobals are excluded. Nested explicit closures contribute their
use list, while nested arrows contribute their expression without removing the
nested arrow's parameters. Only the current arrow's parameters are removed after
ordered deduplication. Zend array elements visit value before key, even though
PHP-Parser lists the key field first. Named function and class scopes are excluded.

`CODEIMPLICIT` binds an ordered capture name to the actual FIELD5 expression root
and the signature cursor used by invocation's implicit binding. It does not invent
a checked explicit-use node or an undefined-read warning at creation.
`CODEARROW` marks every arrow template, including zero-capture and `never`, at that
same body root and stores the emitted return line after body compilation. The
checked signature supplies reference/return type facts. Named functions also use
FIELD5, so that path alone cannot identify an arrow. Both markers are filtered by
existing own-scope code projection and authenticated by runtime source validation.

Ordinary arrows compile the actual expression through the shared return demand
and static checks. Their existing child `CODEEXPR`, constant flag and access mode
remain intact; no checked `NStmtReturn` is fabricated. `never` arrows compile a
discarded expression followed by typed fallthrough, without an implicit return
continuation. The separate marker still identifies the template. The retained
multiline array witness returns a type error on line6, distinct from arrowstart3
and arraystart5. Void-return and invalid-default priority have separate retained
native compilation outcomes. Magic names retain enclosing named/closure context.

Private compiler evidence currently binds18 exact baseline1017 ordinary native,
lint, native-parser, frontend and model contexts, all Unsupported before admission,
plus11 separately instrumented preoptimizer profiles. No ordinary native context
was repeated. The expanded pure gate passes18 phases/202 projections on1018/d96a.
The maintained gate passes18 phases/186 context assertions on1020/6984; its fresh
lint profiles are separate from the ordinary runtime originals. Five shared gates
pass on that same compiler snapshot: closure26, typed59 plus5 explicit pending,
reference-return58, dynamic42 plus2 explicit pending, and call-reference29.
Two already retained runtime originals then add39 pure projections for arrow
BYREF signatures, variable PPW versus value/call PPR demand, and preserved body
constant flags. The final test-only1020/286b gate passes20 phases/223 assertions.
Its40 parse/check responses and20 fresh lint profiles are separately recorded;
the earlier six gates retain their6984 identity. No ordinary native call repeats.

The first compiler AL otherwise-clause failure and later test producer ID/DSL
failures remain original evidence. The final runtime pair1026/365a contains the exact compiler, schema and two
maintained-test files verified against1020/286b. Runtime source/protocol results
and canonical installation remain separately recorded in the pairing report. No current broad integration or complete callable/core claim follows from
these focused gates. Class-bound scope, ordinary-object services and remaining
callable forms are required later work; broad integration follows arrow acceptance.

A later test-only runtime successor1026/0ec5 changes only arrows_state.py; all
compiler and semantic bytes/modes are unchanged. The original365a COW state
fixture reached900 seconds without a verdict, and its second numeric fixture
was not run. The reviewed successor partitions the same493 unique assertions
and36 zero/one/full-resume cuts into9 groups, repeating common premises for960
executed checks. Each retains900 seconds and reuses the original source/native/
request setup. All nine numeric groups completed and the independent archived-byte/raw/
partition audit passed. Canonical code commit `1d438e8a34f0deac425b3a1e0bd250f72c86a89c` matches all1026 bytes/modes of0ec5. The immutable compiler archive and earlier gate identities remain
unchanged; the pairing report binds this outer test-only bridge.
