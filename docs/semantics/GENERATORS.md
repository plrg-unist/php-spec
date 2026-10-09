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

Literal `send` and `throw` validate and capture their single argument before
initialization. Fresh calls first reach the initial yield, then deliver the
value or Throwable at that suspension. `send` supplies the result of a used
yield expression; `next` supplies null. Closed `send` returns null, while closed
`throw` rethrows the same object. If fresh initialization throws, `throw` keeps
its supplied exception as primary and links the initialization exception as its
previous exception. Ordinary catch/finally execution can yield again before the
pending exception resumes.

The saved API operation owns its argument through initialization and resumption.
Arrays keep copied-container behavior and shared embedded references; objects
retain identity. API trace rows retain the actual argument and live caller.
Admission separates pending argument evaluation from completed resume arity,
type and phase. A restored exception search precedes one closed, unsuccessful
resume marker; it cannot be duplicated or moved into a saved owner frame.

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

[Implicit ArrayAccess Get344](SOURCE-ARRAYACCESS.md) creates mixed/untyped Get
Generators, with both declaration reference flags. The real saved frame owns the
receiver and arguments; a nonowning source certificate authenticates Get after
its caller returns. Ordinary close preserves the actual destructor continuation
and pending exception through its finished marker.

Array, source Iterator and Generator graph delegation are covered by
[Module289](GENERATOR-DELEGATION.md), including shared progress, return transfer,
live callback references and natural owner cleanup. [Reference yields328](GENERATOR-REFERENCE-YIELDS.md)
add live cells, value-API snapshots, foreach/destructuring aliases and authentic
Notice/cleanup readback. IteratorAggregate, broader reference producers, dynamic/nullsafe
API calls, named/unpacked API arguments, scoped static and other implicit callback
creation, and creation through changed/imported caller scope remain required.
[Module303](GENERATOR-FORCE-CLOSE.md) adds ordinary last-owner forced close,
pending finally execution and ordered input/frame/cache release.
[Module310](GENERATOR-FIBER-CLOSE.md) extends ordinary paused-Generator release
to the active Fiber stack while preserving real parked caller owners. Wider
terminal cleanup, parked running Generators, switching finalizers, general user
destructors and cyclic collection remain required; their explicit Unsupported controls earn no
agreement. Natural return/throw/finally cleanup remains distinct from forced close.

Normal request cleanup340 uses real global/store owners and borrowed zero-owner
buckets. Module349 also closes fresh store frames without running their bodies,
preserves immediate CV-handler ordering, and releases a closed Generator's Closure before its
caches. Module355 retains a physical closed-Generator storage pin through those
releases, preserving weak liveness, readable RETURN and pending child exceptions.
[Storage-pin checks](../../coverage/semantics/generator-storage-pin-review.json)
remain separate from the [fresh cuts](../../coverage/semantics/generator-fresh-store-review.json).
Module 360 extends normal request close to delegated inputs, preserving input-before-finally
order, independent CV owners, shared store order and the physical CURRENT cache slot.
Nested normal handlers keep the genuine inner/outer close claims and cache owners;
queued source views remain distinct from actual handler contexts.
[Eight originals and 553 reached premises](../../coverage/semantics/generator-request-delegation-review.json)
retain separate cuts. Composition with 346 modules over `9cacdbf51` passes strict
compilation at `4d867f6b0`; earlier source/state cuts retain their inputs.
Module 363 handles uncaught request-finally exceptions and throwing registered
handlers. Normal custom rendering retains the Generator/cache and original handler
exception, including live Weak lookup and registry changes. Reporting freezes
before the reported exception's release; bailout then preserves the real abandoned
carriers and marks later destructors called. C-root traces retain internal frames.
[Seven exact fatal originals and 493 reached premises](../../coverage/semantics/generator-request-abrupt-review.json)
retain separate cuts; the original refusals remain zero agreement. Actual 351 over
`7c4a13bc1` passes strict compilation at `ba1c17c07`; current schema, storage and
collector/source guards remain intact, without renewing earlier source/state cuts.
Normal post-report stdClass and ordinary child storage add one exact fatal original
and 161 premises at its own cut, preserving real pins and full admission through
Weak lookup and the authenticated future continuation. Composition with 353 modules
over `a210cd253` passes strict compilation at `b7b693fa3`; prior cuts remain separate.
At request C root with no current exception handler, a throwing custom renderer
reports and releases its builtin inner Throwable before bailout abandons the
original report and Generator/cache owners. Three exact fatal originals and 527
reached premises retain separate cuts, including the real receiver decrement,
handler exception retention and reporting mutation after emission. Actual 356 over
`2b98ff468` passes strict compilation at `72d5f7353`, preserving current fields;
private source/state cuts retain their own inputs. A renderer-installed handler
that returns normally releases its inner exception before restoring the registry.
The invalid-return warning runs before fatal reporting reads the live original cache;
callbacks receive Unknown/line0 and can refresh it through `parent::__toString()`.
Three fatal originals and 611 reached premises validate the real handler/destructor
pins, transient Weak owners, warning delivery, cache mutation and replay at separate cuts.
Actual 358 over `b721887ce` passes strict compilation at `00536106a`; current
source/argument/storage fields remain intact and private 3/611 retain their inputs.
A throwing renderer-installed handler rethrows at its genuine C root and receives
its own fatal report. Authentic EHR, renderer-return and outer-report carriers keep
the original exception and Generator/cache alive; its custom renderer has three
real owners from CURRENT, STRINGIFY_RESULT and REPORT. The new exception releases
after frozen emission and before bailout, including a destructor that sets reporting
to zero. Two exact fatal originals and 163/180 strict premises retain separate cuts.
Final 358 over `ea04fbbe4` passes strict compilation at `ff3d3278b`, preserving the
named-SEND warning shapes. Earlier 2aa/646 and source/state cuts retain their inputs.
A throwing renderer warning callback passes its new exception to the restored
handler at the real C root. Handler release precedes raw warning-handler restoration;
the original empty cached fatal report then releases its receiver before bailout.
The handler carrier owns the warning object independently of the consumed inner
exception; original REPORT and real Generator/cache owners survive throughout.
Exact source1 and compiler358 retain `558e53a9c`; strict220 retains `80be20cde`, with
authentic continuations, malformed producer rejection and budget replay. Original
binding stops and the incorrect fixed-argument phase remain zero. Actual361 over
`59c163ef4` passes strict compilation at `7983c825f`, preserving current ARG/CALLS
fields; private source/state cuts retain their inputs. Absent or throwing
restored handlers, deeper custom rendering, abrupt child free_obj/destructor/weak-Generator
lifetimes, message warnings, parked or escaped storage and generic terminal cleanup
remain required.

[Arrow Generators311](ARROW-GENERATORS.md) validate the existing capture
and implicit-return routes. Eager parameters, sent results, delegation, scope and
original signatures retain separate source/state cuts. Value-warning cleanup
retains the same Throwable, cached key and closed Closure owner. A separate
frozen287 default/Fiber/eval composition passes one source and148 reached
premises. The actual292 property/collection parent separately passes the same
source and75 reached physical-HANDLE/Arrow-close premises. Final294 passes strict
compilation; earlier source/state cuts retain their own tested parents.

[YIELD key warnings321](YIELD-KEY-WARNINGS.md) cache the value before an ordinary
missing key-CV warning. Handler reference/array writes preserve the copied value;
the read freezes null without advancing the implicit index. Actual child resumer
markers distinguish delegated exception reinjection from direct API close.
Cached user-destructor release retains an authenticated operation/frame carrier
and replacement exception priority. Wider producers and lifetimes remain required.

Constructor-created global constant instances follow the existing noncache
policy for object defaults. Receives, yield caches and return values retain the
original instance identity; the completed source receipt adds no heap owner.
Ordinary deferred body NEW can run a registered autoload Closure. Generator
functions used as implicit autoload callbacks remain a required scope boundary.

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

Twenty-three new send/throw sources agree at `26328ca39` in separate five and
eighteen source cuts: `generator-effects-review-_839imxs` and
`generator-effects-review-zjs5gu53`. They cover fresh/paused/closed inputs,
argument errors before initialization, array/reference sharing, real API trace
arguments, catch/finally suspension and reentrant calls. The original
`generator-effects-review-xsm5m8_5` structuring failure earns no agreement;
an equivalent operand-binding rewrite passes production SL preparation.
Three new source-derived phases pass at fixture `887f51d29`, semantic `26328ca39`:
array146, finally124 and initialization101 (371 conditions). Full public and
heap admission check actual input/cache/return owners, pending-finally exception
identity and previous chaining. Heap-valid count/type/phase/method/line, wrapped or
stranded resume, and doubled/misplaced search mutations reject; zero-budget
resumption matches direct execution. Their raw record is
`generator-effects-protocol-szlr6xpv`.

One introduced source agrees on actual parent `c729a1f62`, semantic union
`ca7da215e` and fixture `63b45bb26`: default NEW autoload changes live precision
before eager argument/construction, while the body retains parser-folded text;
fresh `send` retains its distinct object input and the original default return.
Raw record `generator-effects-review-w21x2zng` keeps this cut separate.
The actual union also passes production SL structuring with the complete main
and a fresh adapter build (`generator-effects-actual-sl-n4ctdfq0`).

`python3 tests/semantics/generator_review.py --select first-current-rewind`
compares ordinary PHP source with the pinned native runtime.
`python3 tests/semantics/generator_review_protocol.py --select carrier`
checks source-reached frame movement, cached owners and malformed continuations.
`python3 tests/semantics/generator_effects_review.py --select send-fresh-target`
compares input delivery and exception injection with the pinned runtime.
`python3 tests/semantics/generator_effects_review_protocol.py --select array-input`
checks actual input owners and resume admission.
Raw commands, profiles and observations stay in ignored `.tools` directories.
This slice does not establish complete Generator or complete core semantics.
