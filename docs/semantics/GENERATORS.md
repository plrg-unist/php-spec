# Generators

Module280 creates Generator objects after ordinary argument, type and default
receives. The function body and Closure lexical loads remain deferred until
initialization. Named functions, ordinary Closures and ordinary object method
calls use the accepted call machinery; no unaccepted return implementation is
required.

The Generator owns its suspended function frame. Resuming moves that frame into
the machine and saves the actual resumer. Yielding moves it back into the object.
The frame, received arguments, receiver and Closure captures are outgoing heap
edges of the Generator, not permanent roots. Natural completion releases the
execution frame but retains the last yield cache, return value and Closure owner.

By-value yields retain raw keys, copied array containers and embedded reference
cells. Key expressions precede value expressions; a simple key CV is fetched
after value effects. Implicit integer keys wrap at the pinned signed64 boundary.
The old yield cache is released before fetching the next CV operands. Ordinary
eager destructors remain an explicit dependency boundary.

Literal `current`, `key`, `valid`, `rewind`, `next` and `getReturn` calls initialize
a fresh Generator as required. The first yield can be rewound; later advancement
forbids rewind. Fresh `next` initializes and advances, while empty initialization
preserves the first-yield flag. `getReturn` starts an uninitialized Generator,
then returns its by-value completion or throws without advancing a suspended
yield. Positional excess arguments run before the argument-count error and appear
in its trace.

Value `foreach` uses the native Generator iterator protocol without adding a
synthetic method trace row. Direct method resumption adds its actual method row.
Both retain the live resumer and eager receive arguments, including nested calls
to the same Generator function. Ordinary private-method creation keeps its
original source caller permission after that caller returns.

Generator declarations mirror Zend's one-level return-supertype scan. A pure
intersection containing `Iterator`, `Traversable` or `Generator` is accepted even
when the resulting Generator does not satisfy every intersection member. A DNF
intersection branch does not expose its inner names to that scan. Generator
completion does not perform ordinary declared-return coercion.

Admission authenticates source functions and yield unit/path pairs, suspended
frame scopes, Closure targets and one real saved resumer per running Generator.
Internal continuations cannot hide in source wrappers or branches. Public
admission and ownership checks use actual source-reached states.

Delegation, reference yields, arrow Generators, `send`/`throw`, dynamic/nullsafe
API calls, named/unpacked API arguments, scoped static and implicit callback
creation, and creation through changed/imported caller scope remain required.
Started force-close finalizers, eager destruction and cyclic collection also
remain required; their explicit Unsupported controls earn no agreement.
Natural return/throw/finally cleanup is distinct from forced close.

Constructor-created global constant instances follow the existing noncache
policy for object defaults. Receives, yield caches and return values retain the
original instance identity; the completed source receipt adds no heap owner.
Ordinary deferred body NEW can run a registered autoload Closure, while creation
inside an implicit autoload callback remains a required scope boundary.

Twenty-seven normal sources and three compiler rejections agree at `e235d8dd1`
in separate first5 and independent25 cuts. Four independent source-derived
phases pass: carrier144 and Closure154 at `2f21dec3e`, nested77 at `d7ca57f5c`
and abrupt44 at `6c221db16`. Their 419 premises check full public admission at
genuine stable states, moving frames, cached/reference owners, cursor uniqueness
and natural try/finally cleanup. Closure154 is the passing phase in the record
whose later nested check failed; original failures remain retained.

Three introduced parent sources agree at `9abff30b8`: global constant default
identity, deferred REAL Closure autoload and parse-folded versus live precision
after a container warning. A new 95-premise constant phase passes at the same
cut, checking full public/heap admission, unchanged nonowning receipts and the
2→3→3→1 receive/cache/return/constant owner flow. Their raw records are
`generator-independent-cigy7vgb` and `generator-review-protocol-1z9ssugw`; the
initial `generator-independent-gbe1sfu4` interpreter failure and native fixture
failures remain retained with zero credit.

Raw private records are `.tools/generator-independent-n_gi07p8` (first5),
`generator-independent-3xhzyjou` (remaining25 and six zero-credit controls),
`generator-review-protocol-j09b_g9p` (carrier), `generator-review-protocol-eos1w4wf`
(Closure), `generator-review-protocol-0zcv39l1` (nested) and
`generator-review-protocol-8m71dnav` (abrupt). These directories retain runtime,
profile, commands, exits, exact bytes and stable semantic inputs.

`python3 tests/semantics/generator_review.py --select first-current-rewind`
compares ordinary PHP source with the pinned native runtime.
`python3 tests/semantics/generator_review_protocol.py --select carrier`
checks source-reached frame movement, cached owners and malformed continuations.
Raw commands, profiles and observations stay in ignored `.tools` directories.
This slice does not establish complete Generator or complete core semantics.
