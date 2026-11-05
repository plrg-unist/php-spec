# Core PHP semantics progress

This project targets PHP 8.5.10 CLI, NTS, 64-bit. Executable core semantics and
source-driven differential validation are active; complete PHP core, the later
Rocq interaction-tree model and BOLA/CRIS verification remain unfinished.
[PLAN](PLAN.md) records settled scope; the [feature inventory](coverage/semantics/features.json)
and current family documents identify implemented routes and remaining obligations.

## Current checkpoint

I87 authenticates direct raw array and string method Generator creation and
scoped factories from the immutable selected method. Archived receiver history
adds no owner; direct producer and Fiber entry require the real live receiver.
Six originals agree and seven reached fronts pass 561 custom/596 reported
checks at private cuts. Joined strict433, three exact sources and a strengthened
93-assertion closed-history state pass; e0e3ce7f composition is reviewed.
Wider binding, callback and lifecycle contexts remain partial.
[I87 review](coverage/semantics/generator-raw-method-factory-review.json).

I86 authenticates captured ordinary method Generator bodies during Fiber
transfer and reference-cache reads using the actual resumer, Closure and
selected method. After Closure storage retirement, the recorded selection
reconstructs a nonowning scope without a new owner. Four originals agree;
five reached fronts pass 501 custom/526 reported checks at their private cuts.
Joined strict433, two exact sources and 111 independent reached checks pass at
4462bc6d; the 779569a8 composition is reviewed. Original compiler,
refusal and storage failures retain zero credit. Wider bound/API and lifecycle
contexts remain partial.
[I86 review](coverage/semantics/generator-captured-method-body-review.json).

I85 admits direct Generator-bodied `__call` and `__callStatic` through the
existing typed source policy. Actual entered context retains the selected
target through close and Fiber transfer, while live bodies require their real
receiver. Five current originals agree; five reached fronts pass 444 custom/469
reported checks at their private cuts. Joined strict433, three exact sources
and 166 independent reached checks pass at bd274e79f; b1adc40c composition is
reviewed. The original compiler, COUNT, Fiber-consumer and
fixture-prefix failures retain zero credit. BYREF magic signatures and wider
source/API/lifecycle forms remain partial.
[I85 review](coverage/semantics/generator-direct-magic-review.json).

I84 carries admitted `__call`/`__callStatic` factory authority into scoped
method Generators after the maker or packed argument array retires. Five
originals agree; five reached fronts pass 442 custom/467 reported checks at
their recorded private cuts. Joined strict433 and the protected-close OB05
interaction source pass at 5e33a7f88. Both original fixture failures retain
zero credit. Direct magic
Generator bodies and wider ancestry/API/lifecycle contexts remain partial.
[I84 review](coverage/semantics/generator-magic-factory-review.json).

Published generated enum array captures now create internal Closures without
retaining the input array or receiver, preserving selection through COW and
callback rebinding. Four fresh originals agree and 123 state/guard conditions pass. Private
compilation covers 432 modules; actual-tail compilation covers 433. Runtime array retirement, warm case
receivers and cold class-name tables retain separate checks; literal inputs make
no deallocation claim. Other consumers, loading and backing contexts remain
partial.
[Array-capture review](coverage/semantics/enum-array-capture-review.json).

Published generated enum method strings now form first-class internal Closures.
Real call ownership retains the selected target through argument clearing and
Stringable callbacks, then releases the Closure after invocation. Four new
originals agree; 114 state/guard conditions, private431 and actual-tail joined432
pass. Array captures, other string consumers, loading and backing contexts remain
partial; enum collectability is separately owned by GC08.
[Capture review](coverage/semantics/enum-string-capture-review.json).

Published enum class-method strings now select generated `cases()`/`from()`/
`tryFrom()` before arguments, retaining full original bytes through rebinding and
real named Stringable callbacks. Temporary Stringable inputs retire before lookup;
packed source origins remain Unsupported. Six new originals agree exactly and
159 state/guard conditions pass; private and actual-tail joined strict431 pass.
The separately reviewed 301 receipt normalization repairs the preserved ordinary
136/137 identity observer. Wider callable consumers, backing dependencies and
the default loader remain partial.
[String-callable review](coverage/semantics/enum-string-callable-review.json).

Generated enum method strings pass through ordinary callable-typed parameters as
raw values, and `Closure::fromCallable` converts generated string/array targets.
The separate reviewed cuts are source5/state111 and source4/state138, each with
strict433 compilation; the joined current-tail cut has strict433 and three exact
originals at 2614477b2. Published generated methods now also run through pipe
strings and arrays. Four native-first originals agree, including strict typing,
cold table selection across Stringable rebinding, case-object arrays, arity and
temporary cleanup. Private strict433 and two source-reached strict SL groups
pass 68 guards at db3b26b16. Published enum method strings and class/case
arrays now answer direct, dynamic-name and pipe `is_callable` queries with
one or two arguments and no third output. Two native-first originals agree,
covering generated and absent methods, syntax-only checks, selected-name
rebinding and cold backing tables; 43 source-reached strict SL guards pass.
The third output, autoload and wider magic/user-method cases remain partial.
Malformed live callback arrays now return false for wrong length, keys,
receiver or method type before syntax-only lookup. The first published-enum
source and 23 reached guards still pass after the broader precheck. A new
seven-outcome original and 46 reached guards cover missing key 0, nonclass
receivers and valid reordered keys without cache or event changes.
For published pure enums without the requested method, `is_callable` now
checks source-certified `__callStatic` for class strings/name arrays and
`__call` for case arrays. One native-first original agrees on eight outcomes,
including opposite-handler false results and explicit user-method controls;
56 reached strict guards prove no magic body is entered by the query.
Live enum case arrays now also query direct public user instance and static
methods. One native-first original agrees on seven case/class/string controls;
49 source-reached strict guards tie the method descriptor to its enum source
member and show that the query enters neither user method body.
The third output now captures an initialized string-valued CV for a literal
generated enum method string and writes its canonical name before returning
the boolean.
One exact original, strict433 and 45 source-reached guards pass; array input,
old-object destructor and input/output aliasing remain explicit Unsupported.
Absent literal methods now also write the name on runtime false and syntax-only
true results. A second exact original and 42 reached guards pass.
Canonical class-name and live case-object literal arrays now write their
generated method names through the same direct string CV. Two exact outcomes
and 68 reached guards pass. Literal class-string arrays also preserve lowercase
and leading backslash receiver spelling, while case arrays use the canonical
enum name. Three exact outcomes and 64 reached guards pass; other array
sources remain partial. The same direct output path now accepts initialized
int, bool and null CV values, writing the name before returning the boolean.
Three exact outcomes and 79 reached guards pass; an old output object remains
explicit Unsupported because its destructor runs during replacement.
Literal enum method strings now also retain their raw class and method spelling
in the third output, including lowercase and a leading backslash. Three exact
outcomes and 88 reached guards pass.
A separate live variable can now supply the enum method string to a direct
three-argument `is_callable` call with literal `false`. Its saved and current
bytes agree, and a distinct initialized output CV receives the name before the
boolean. One exact original and 46 reached guards pass. A shared scalar
input/output reference cell also retains the saved name through its write;
one exact original and 43 reached guards pass. Argument-time target rebinding
remains explicit Unsupported.
[Reception](coverage/semantics/enum-string-admission-review.json),
[conversion](coverage/semantics/enum-from-callable-review.json),
[current-tail gate](coverage/semantics/enum-callable-current-tail-review.json),
[pipe review](coverage/semantics/enum-pipe-review.json),
[query review](coverage/semantics/enum-is-callable-review.json),
[shape review](coverage/semantics/enum-is-callable-shape-review.json),
[wide-shape review](coverage/semantics/enum-is-callable-wide-shape-review.json),
[magic review](coverage/semantics/enum-is-callable-magic-review.json),
[case-method review](coverage/semantics/enum-is-callable-case-method-review.json),
[output-CV review](coverage/semantics/enum-is-callable-output-review.json),
[false-output review](coverage/semantics/enum-is-callable-output-false-review.json),
[array-output review](coverage/semantics/enum-is-callable-output-array-review.json),
[spelling review](coverage/semantics/enum-is-callable-output-spelling-review.json),
[scalar-output review](coverage/semantics/enum-is-callable-output-scalar-review.json),
[string-spelling review](coverage/semantics/enum-is-callable-output-string-spelling-review.json),
[variable-output review](coverage/semantics/enum-is-callable-output-variable-review.json),
[alias-output review](coverage/semantics/enum-is-callable-output-alias-review.json).

I88 carries raw method Generator reference caches and warm/fresh THROW across
Fibers using the actual resumer/Gen/current proof. Fresh initialization now
retains Zend's extra pending exception reference until injection; calibrated
native controls distinguish pending input2 from warm input1 after CV unset.
Nonstatic object-array calls from fixed ordinary method sources preserve lexical private
selection over a public child override. Four native/model originals agree;
four reached fronts pass 439 custom/459 reported checks at distinct cuts.
Private433 keeps its original cut; later reached checks compile both corrections.
Original refusal and reached failures plus the native diagnostic keep zero extra
agreement credit. Eight legacy expectations are maintained without execution
renewal or historical rewrite. Joined strict433, three exact sources, two affected
old THROW states (143+105 checks) and an independent 153-check state pass at
1ecc939d; 5096cbb1 current composition is reviewed. Wider captured-Closure,
API/binding/delegation/collection/lifecycle combinations remain pending.
[I88 review](coverage/semantics/generator-raw-method-cache-review.json).

I89 carries authenticated nonstatic captured/bound method-Closure Generators
through warm by-value/reference THROW and fresh initialization across Fibers.
The actual resumer/Gen/current proof keeps Closure and This through CLOSED;
Gen drop releases Closure/receiver before the cache. Four native/model originals
agree at distinct cuts; five reached fronts pass 632 custom/657 reported checks.
Private433 keeps its initial cut; later source/front checks compile the ARRAY
nominal Closure identity and admitted bindTo dispatch corrections. Original
Unsupported, stdout mismatch and interpreter failure keep zero agreement credit.
Joined strict433, three exact sources, a fresh 117-check state and independent
closed-body 118-check state pass at c81b8c5e; 26cf6684 composition is reviewed.
Wider producer/API/binding/lifecycle combinations remain pending.
[I89 review](coverage/semantics/generator-captured-method-throw-review.json).

I90 carries direct typed BYVAL magic Generator warm/fresh THROW across Fibers
through a shared actual resumer/Gen/current and entered-handler receipt proof.
Native fresh abort releases payload before This, then throws the original API
Throwable with the supplied abort as Previous; the existing initialization rule
supplies that order unchanged. Four native/model originals agree at distinct
cuts; five reached fronts pass 623 custom/648 reported checks. Private433 keeps
its original cut and the unchanged Unsupported keeps zero agreement credit.
Joined strict433, three exact sources, fresh parked125, affected I85 SEND166
and independent closed102 checks pass at dfa4386d; d1f314c0 composition is
reviewed. Source/signature and wider producer/API/lifecycle limits remain partial.
[I90 review](coverage/semantics/generator-direct-magic-throw-review.json).

I91 restores nominal Closure identity for static user-method string captures and
routes admitted non-first-class bindTo calls through existing binding authority.
Source retargeting, called-scope reset, a retained Gen Closure and a retired
factory's nonowning history retain distinct controls. Three native/model
originals and five reached fronts 614 custom/639 reported pass at their recorded
cuts; private433 keeps its original cut. Both original failures remain zero credit.
Joined strict433, three exact sources and parked127 pass at ee4b3cdb; the
strengthened closed-cache126 state at 5610e476 checks GC09's receiverless
marker. The 4544a539 composition is reviewed. Wider callable/API/lifecycle
contexts remain partial.
[I91 review](coverage/semantics/generator-string-method-closure-review.json).

I92 gives real user Generator Closure::call entry its actual copied Closure and
new receiver, with separate API owners and ordered used/ignored-result cleanup.
The saved Gen keeps its copy through CLOSED without an API wrapper or later
API trace. Five native/model originals and private433 pass at recorded cuts;
six reached fronts pass 744 custom/774 reported checks at separate fixture cuts.
Original Unsupported and two fixture failures retain zero credit. Native-only
receive-error retention and reference formals remain partial. Joined strict433,
four exact sources, API-entry99, unused-result81 and independent closed143 checks
pass at a84bf6c0; 3486d56c composition is reviewed. Wider calls remain partial.
[I92 review](coverage/semantics/generator-call-copy-review.json).

I83 gives implicit invokable-object factories and direct Generator-bodied
`__invoke` calls one compiled-source/runtime-effective-method proof. Direct entry
requires the live receiver; a bounded lookup view authenticates retired factory
history without another owner. Finite forwarding and actual lexical/called
scope retain the ordinary receiver/cache/SEND owners. Five new originals agree
at their recorded cuts; five reached fronts pass 374 custom/399 reported checks,
including live-entry refusal, close/forwarding, parked BYREF input/cache owners
and budget continuation. Private strict432 retains its original cut; actual-tail
joined strict433 passes at the integration cut. The original SL-overlap and fixture-syntax failures
retain zero credit after narrow corrections. Wider implicit/callback/API,
delegation, collection and lifecycle combinations remain partial.
[I83 review](coverage/semantics/generator-invokable-factory-review.json).
[I82](coverage/semantics/generator-bound-factory-review.json),
[I81](coverage/semantics/generator-array-string-factory-review.json) and
[I80](coverage/semantics/generator-captured-factory-review.json) retain their
original scope and tested cuts.

GC06 carries an authenticated claimed count source through canonical materialized
ordinary destructor callbacks and PASS1, including retired original tables.
Ordered nested buffer removal preserves proxy-table count roles and free slots:
one first pass contributes 1 after debit 2, then retrace contributes 3.
Source-authenticated immediate `===`/`!==` temporary release and borrowed
matching `BASE` caches avoid false potential roots. Four native-first sources
agree at their recorded cuts; 11 reached SL groups pass 330 checks. Private
strict430 and actual-tail joined strict431 pass. WeakMap callbacks, skipped
prior histories, worker/residual/reentry paths, hooks, active contexts and wider
cache lifetimes remain partial.
[GC06 review](coverage/semantics/gc-materialized-claimed-callback-review.json).

GC07 carries canonical materialized destructor collection through ordinary
named-function and method callers. Current locals, saved caller locals and real
receivers keep their existing roots; GC sites must belong to the authenticated
caller body. Successful `WeakReference::create()` argument retirement and unused
local result-cache transfer preserve native potential-root order. Four new
native-first originals agree exactly, including resurrection count -1 followed
by later count 3. Nine reached SL groups pass 392 checks at their recorded
cuts. Private strict431 and compact AL/SL metadata controls pass; joined
actual-tail strict432 compilation passes at the integration cut. Fiber, worker,
residual, reentry, hooks and wider cache/table lifetimes remain partial.
[GC07 review](coverage/semantics/gc-caller-materialized-review.json).

GC08 skips potential-root buffering for enum cases, following Zend's
`GC_NOT_COLLECTABLE` flag. Cached cases retain their class-constant owner and
WeakReference identity; ordinary collectable objects still enter the physical
buffer in real order. One native-first source agrees exactly and a native status
witness plus two strict reached groups (47 checks) distinguish the buffer slots.
Joined actual-tail strict432 compilation passes; graph traversal and owner
counting are unchanged. Other builtin eligibility and wider collection contexts
remain partial.
[GC08 review](coverage/semantics/gc-enum-collectability-review.json).

GC09 records Zend's allocation-time `GC_NOT_COLLECTABLE` flag for receiverless
fake Closures created by the modeled named, intrinsic, method, constant,
fromCallable and Fiber capture routes. Clones and bind copies allocate without
that flag; bound fake and real Closures remain collectable. Two native status
batches distinguish these cases, three new sources agree exactly, and three
strict reached groups pass 153 checks. Actual-tail strict433 compilation passes;
GC graph traversal and owners are unchanged. Wider collection contexts remain
partial.
[GC09 review](coverage/semantics/gc-fake-closure-collectability-review.json).

GC10 admits direct calls through a plain childless real Closure as canonical
materialized collector callers. The active GC receipt binds the caller and its
real machine root; the Closure stays outside the white set while unrelated
Closures remain refused. One native-first original agrees exactly, a strict
pre-begin diagnostic passes 23 checks, and the affected reached group passes
87 checks. Private strict432 and actual-tail joined433 compilation pass.
Explicit `->__invoke`, pipe, captured and wider active collector contexts
remain partial.
[GC10 review](coverage/semantics/gc-closure-caller-review.json).

GC11 admits a normal literal, zero-argument `->__invoke()` call through a live
global variable holding a plain static real Closure without captures,
attributes, a by-reference return or a declared return type. Its wrapper owns
two current Closure roots and the global cell supplies a third owner; the existing
active caller and count rules still protect the held sibling. The native-first
original agrees exactly, a pre-edit reached diagnostic passes 24 checks, and
the private strict reached group passes 95 checks; the current-tail group passes
96 after the global receiver guard. The independent computed-receiver refusal
passes 18 strict checks; joined OB05 strict96 and the unchanged native/model
original also pass.
Calls with arguments, computed receivers,
attributes, return declarations, nullsafe selection and wider active contexts
remain partial.
[GC11 review](coverage/semantics/gc-closure-invoke-caller-review.json).

GC12 admits a complete childless by-value capture in a live direct real-Closure
collector caller. A scalar `use ($seed)` source agrees with PHP; a pre-edit
reached diagnostic passes 28 checks and the affected strict reached group
passes 95. The active caller, machine root and empty child set still guard the
ordinary count walk; object/reference captures and static cells remain outside
this cut. [GC12 review](coverage/semantics/gc-captured-caller-review.json).

GC13 admits one unbuffered, childless ordinary `stdClass` capture under an
authenticated live direct real-Closure collector caller. The captured object
stays outside the white set through the Closure's real root. One native-first
original agrees exactly, a pre-edit diagnostic passes 35 checks, and the
affected strict reached group passes 103. This cut left buffered leaves,
captured object graphs and reference/array captures fenced.
[GC13 review](coverage/semantics/gc-object-leaf-caller-review.json).

GC15 admits the same childless capture after a real post-`P|0` copy release
buffers it again. The live Closure keeps the token black; the second pass
removes its physical slot before the D/held count plan. A native status witness
shows roots 0→1 after that release. One new source agrees exactly; the new
strict reached group passes 103 checks and the affected GC13 group passes 101.
The old constructed buffered-token refusal is superseded; object graphs,
reference/array captures and wider collector contexts remain fenced.
[GC15 review](coverage/semantics/gc-rebuffered-leaf-caller-review.json).

GC16 admits one runtime-written, childless array capture in the active direct
real-Closure caller. The model binds the same nonimmutable array in the global
cell, Closure capture and entered local; both ordinary and physical GC tracing
find no child edge. A native status control observes roots 0→1 after an owning
copy release, and the original source agrees exactly. Pre-edit reached checks
pass 43; the affected strict group passes 106. At that cut, buffered active
array captures remained fenced; COW after capture, nonempty persistent
provenance and wider collector contexts are untested.
[GC16 review](coverage/semantics/gc-array-leaf-caller-review.json).

GC17 admits that same childless array after an owning copy release following
`P|0` buffers it for the D pass. The rooted capture keeps the real array black,
and its slot leaves the count plan before held/drop destruction. A native status
control observes roots 0→1; one source agrees exactly. Pre-edit reached checks
pass 45, the new strict group passes 106, and the affected GC16 group passes
104 after removing its superseded constructed buffered-array refusal. COW and
nonempty persistent provenance remain untested; graph/count/owners are unchanged.
[GC17 review](coverage/semantics/gc-rebuffered-array-caller-review.json).

GC18 admits one runtime-written array capture with exactly one direct childless
`stdClass` entry. The active direct Closure caller remains machine-rooted; the
array and leaf are unbuffered, with matching ordinary and physical GC edges.
One native-first source agrees exactly, a pre-edit reached group passes 54,
and the strict affected group passes 115. The final source read proves child
liveness only. At that cut, buffered array or leaf candidates and wider entry
shapes remained fenced; COW and nonempty persistent provenance were untested.
[GC18 review](coverage/semantics/gc-array-object-child-caller-review.json).

GC19 admits that same array after a post-`P|0` owning copy release buffers it
for the D pass. The globally held childless `stdClass` remains unbuffered, and
the live Closure keeps the array black. Native status observes roots 0→1; one
original agrees exactly. Pre-edit reached checks pass 57 and the strict D
group passes 118, including removal of the real array slot before held/drop
counting. Leaf candidates and wider entries remain fenced; COW and nonempty
persistent provenance are untested. Graph/count/owners are unchanged.
[GC19 review](coverage/semantics/gc-rebuffered-array-child-caller-review.json).

GC20 admits that childless `stdClass` when releasing one owning local copy
buffers it after the array. Native status observes roots 0→1→2; the exact
original agrees, and 122 strict reached assertions bind both ordered slots,
their removal from the D plan, and the rooted Closure/array/leaf owners.
Pre-edit model refusal remains zero credit. At that cut, wider entries,
backedges, COW and nonempty persistent provenance remained open.
[GC20 review](coverage/semantics/gc-buffered-array-child-leaf-caller-review.json).

GC21 admits two distinct childless `stdClass` entries at array keys 0 and 1
under the same direct Closure caller. The array and key-0 leaf are buffered;
key-1 stays outside the buffer. One pinned original agrees, and 136 strict
reached assertions check both slots, black removal, owners and a duplicate
child refusal at that cut, superseded by GC25. The pre-edit Unsupported
retains zero credit. At the GC21 cut, wider arrays, backedges and
post-capture COW remained open.
[GC21 review](coverage/semantics/gc-two-array-children-caller-review.json).

GC22 admits the same two-entry array after a third owning copy release
buffers the key-1 leaf. Pinned status sees roots 0→1→2→3; one original
agrees, and 139 strict reached assertions prove three ordered slots,
black D-plan removal and owners 2/3/2/2. A corrected fixture selects D
by collection nonce 2. Pre-edit refusal remains zero credit. At the GC22
cut, broader entries, backedges and post-capture COW remained open.
[GC22 review](coverage/semantics/gc-buffered-second-array-child-caller-review.json).

GC23 admits an ordered node-free scalar capture before one childless
runtime-written array capture in the same direct Closure. A pinned
Reflection control observes `seed,token` order; one original agrees and
110 strict reached assertions bind the capture layout, shared array owners
and source/caller bounds. Pre-edit Unsupported retains zero credit.
[GC23 review](coverage/semantics/gc-scalar-array-caller-review.json).

GC24 admits finite ordered node-free scalar captures around one mutable
one-level array in the same authenticated direct Closure. Its entries may
be direct scalars or childless stdClass leaves in physical order;
compiled-pool descendants and materialized property tables are fenced.
Reversed capture order, three mixed-key leaves and post-capture COW give
three exact source pairs. Strict reached checks pass 113+146 assertions,
and the corrected GC23 group passes 110. Its original duplicate-identity
refusal is superseded by GC25; shared separate captures, aliases, nested
arrays and user-destructor children remained refused at the GC24 cut; GC26
admits the bounded shared-capture case. Earlier Unsupported,
overlap and fixture failures retain
zero credit. [GC24 review](coverage/semantics/gc-finite-capture-review.json).

GC25 admits repeated direct edges to the same childless stdClass inside
that finite captured array. With global strong owners removed, two array
edges keep one leaf alive until Closure release; pinned status sees roots
0→1→2 and then 0. One full source agrees exactly. Strict reached checks
pass 127 new and affected GC21/22/24 groups 137+140+147, proving two
physical edges, one leaf buffer slot, owners 2/2, black D protection and
nested-array refusal. The source-only Unsupported and first fixture error
retain zero credit. [GC25 review](coverage/semantics/gc-duplicate-edge-review.json).

GC26 admits one finite captured array together with direct captures of
childless stdClass leaves already present in that array. Forward and reversed
capture orders match pinned PHP exactly, including weak liveness after the
call and death after Closure release. Two strict D-state groups pass 146
assertions each, proving separate Closure and array edges to the leaf, one
buffer slot, owners 2/2/3 and black protection. Pre-edit Unsupported and a
corrected P4 helper compile failure retain zero credit. Other captured
object layouts and nested or destructor-bearing graphs remain partial.
[GC26 review](coverage/semantics/gc-shared-capture-review.json).

The cumulative GC12–19 join passes seven exact original source pairs and seven
strict SL reached groups (742 assertions) at its frozen cut. One representative
GC12 source pair passes after the A80 and enum-pipe joins; A81's named Generator
factory path is disjoint. Separate native status controls and original failures
retain their own evidence. [Joined review](coverage/semantics/gc-caller-cumulative-review.json).

Immediate identity cleanup now validates a sole produced right object/array
temporary with a borrowed or scalar left operand in both AL and SL. Fourteen
focused conditions pass in each mode, including strict compilation of the actual
431-module tail; the affected cached-enum Stringable original matches PHP again.
Existing owners and collection policy are unchanged.
[Identity receipt review](coverage/semantics/identity-produced-right-review.json).

Earlier [I75](coverage/semantics/generator-keyword-creation-review.json),
[I76](coverage/semantics/generator-keyword-chain-review.json),
[I77](coverage/semantics/generator-keyword-receiver-review.json),
[I78](coverage/semantics/generator-closure-factory-review.json) and
[I79](coverage/semantics/generator-closure-method-review.json) reviews retain
their distinct scope, counts and raw failures.

CONFIG Iterator sends preserve scalar snapshots and finite CFG-admitted ARRAY or
ordinary non-Stringable INSTANCE arguments. Existing by-value Generator routes
also copy flat scalars before later resumes; INI_SET conversion, strict errors and
NULL handlers follow traversal and DATA/INPUT cleanup. COW protects array tables,
while embedded aliases, object identity and API TraceArgs retain ordinary owners.
Owning Iterator aborts release CURRENT, DATA/INPUT, then the copied prefix. Admitted
last-owner temporary Iterator INPUT finalizers keep live copied arguments protected.
Typed-source reads and existing producer/key/finite-graph policies stay intact;
named direct-CV Generator reference yields now copy scalars from authenticated
ordinary cells before later writes. One local scalar-cell route retires a CLOSED
Generator from sole DATA through the normal storage pin or quiet terminal cleanup.
Outside aliases can now retain an ordinary scalar cell after that Generator dies;
copied sends and retired source history survive later writes to the cell.
A direct temporary zero-argument BYREF Generator call keeps separate INPUT and DATA
owners; DATA drops first, then final INPUT/storage cleanup precedes API or catch.
A distinct BYVAL factory can return that BYREF Generator while publishing only a
weak observer; its source, owner transitions and weak death have private validation.
An outside-retained named BYVAL Generator now copies finite quiet owning ARRAY
or ordinary INSTANCE sends. The copied prefix survives cache replacement until
INI_SET TypeError trace reception, or retires before a terminal saved catch;
four new sources agree and 296 reached conditions pass at private cuts.
A named BYVAL factory temporary now copies a quiet owning first option and
finishes with an integer cached value; four sources and 372 reached conditions
pass at private cuts, including normal TypeError trace and terminal cleanup.
The joined strict433 and fresh normal source/state gate pass at `04d38dc55`,
which received independent review before guarded integration.
With a scalar first option, the same temporary source admits a finite quiet
owning final cache when its copied last argument protects the cache child.
Four more sources and 405 reached conditions pass at private cuts, including
real storage release and terminal saved-throw cleanup. Typed Generator cells,
effectful finalizers/casts and wider last-DATA reference graphs and lifecycles
remain partial.
The joined strict433 and fresh terminal-throw source/state gate pass at
`c7eb56942`; disjoint I84/ATTR07 changes were independently reviewed before
guarded integration.
Two quiet owning Generator sends now preserve distinct or repeated copied roots
through cleanup. Four frozen object sources, a separate array COW regression,
and 421 reached conditions pass; joined strict433 and terminal source/state
gates passed at `4c6d75817` and `6daa1de90`.
A retained named BYREF Generator now copies a finite quiet owning value from
an ordinary cell before later writes and a scalar send. Four originals and 406
reached conditions pass; joined strict433 and terminal source/state pass at
`186d8c368`.
A final owning BYREF cell value now copies after a scalar send and survives
later cell writes. Four originals and 408 reached conditions pass; joined
strict433 and terminal source/state pass at `86082901b`.
A retained BYREF Generator can keep that final ordinary owning cell through
closed storage while the copied send remains stable. Four originals and 448
reached conditions pass; joined strict433 and terminal source/state pass at
`c5086c205`.
Outside aliases can keep the ordinary owning cell after Generator retirement;
the copied final argument remains stable across later cell writes and COW.
Four originals, 527 reached conditions and an affected 266-condition control
pass; joined strict433 and fresh terminal source/state pass at `a00e229f9`.
A direct temporary BYREF Generator now copies an owning final value from its
ordinary local cell after a scalar send. Four sources and 472 reached conditions
pass; DATA then INPUT cleanup releases the temporary before API or catch.
Joined strict433 and fresh terminal source/state pass at `3699279a5`.
Outside aliases now keep that temporary Generator's ordinary final cell and its
current value after real storage release; copied arguments remain independent.
Four sources and 565 reached conditions pass; joined strict433 and fresh terminal
source/state pass at `9cde7e64d`.
A named BYVAL factory can return a distinct BYREF Generator with a final owning
ordinary cell. Four sources and 512 reached conditions pass; copied arguments
survive DATA/INPUT release and real Generator storage cleanup. Joined strict433
and fresh terminal source/state pass at `1a7c38d0b`.
The cumulative A88-A93 rule shares authenticated copied ITEM and live ordinary
cell sends across retained, direct temporary and BYVAL-factory BYREF Generators.
Six selected originals and four crossed/effectful sources agree exactly; strict433
and 827 reached conditions/11 raw steps pass. Stringable conversion and a
factory-retained Generator stop at exact send frontiers with zero credit.
[Bounded ownership review](coverage/semantics/config-generator-bounded-ownership-review.json).
[Owning arguments](coverage/semantics/config-iterator-argument-review.json),
[INPUT cleanup](coverage/semantics/config-iterator-input-finalizer-review.json),
[Generator scalars](coverage/semantics/config-generator-scalar-review.json),
[Generator reference scalars](coverage/semantics/config-generator-reference-scalar-review.json),
[Sole-DATA reference cleanup](coverage/semantics/config-generator-reference-sole-data-review.json),
[Surviving-alias cleanup](coverage/semantics/config-generator-reference-outside-alias-review.json),
[Temporary reference cleanup](coverage/semantics/config-generator-temporary-reference-review.json),
[Factory reference cleanup](coverage/semantics/config-generator-factory-reference-review.json),
[Owning Generator sends](coverage/semantics/config-generator-owning-value-review.json),
[Temporary owning sends](coverage/semantics/config-generator-owning-temporary-review.json),
[Owning final caches](coverage/semantics/config-generator-owning-cache-review.json),
[Two owning sends](coverage/semantics/config-generator-two-owning-review.json),
[Owning reference snapshots](coverage/semantics/config-generator-reference-owning-review.json),
[Final owning reference snapshots](coverage/semantics/config-generator-reference-owning-cache-review.json),
[Retained owning reference cells](coverage/semantics/config-generator-reference-owning-live-review.json),
[Outside owning-cell aliases](coverage/semantics/config-generator-reference-owning-alias-review.json),
[Temporary owning reference cells](coverage/semantics/config-generator-temporary-owning-reference-review.json),
[Temporary owning-cell aliases](coverage/semantics/config-generator-temporary-owning-alias-review.json),
[Factory owning reference cells](coverage/semantics/config-generator-factory-owning-reference-review.json),
[CONFIG contract](docs/semantics/INCLUDE-SOURCES.md).

ATTR01 adds builtin NoDiscard declarations with literal/NULL messages and
ordinary source-call warnings after sends/named defaults, before reception/body.
Selected references, real argument/receiver owners and caller-only traces survive
handlers and supplied throws; used results and callback APIs remain distinct.
Twenty-six originals agree, and four reached fronts pass 297 checks including 24
derived guards. Joined strict430 and the new FINAL callback control pass;
accepted private cuts are unchanged. Wider messages, targets, hooks and wrappers
remain partial.
[Attribute contract](docs/semantics/BUILTIN-ATTRIBUTES.md),
[review](coverage/semantics/builtin-nodiscard-review.json).

ATTR02 adds literal/NULL-message and since Deprecated declarations for named
functions and ordinary methods. Prepared VM calls warn after sends and named-hole
completion, before NoDiscard and reception, for used and discarded results.
Selected arguments, references and receivers survive handlers and abrupt cleanup.
Thirteen originals agree exactly (nine authored, four independent);
at the ATTR02 cut, two internal API cases were explicit Unsupported with zero
agreement credit.
Four reached fronts pass 314 conditions: 278 source-reached checks, 24 derived
guards and 12 raw API projections. Private and actual-tail joined strict430
pass; earlier failed fixtures retain zero credit. Wider messages, targets,
wrappers and other internal API consumers remain partial.
[Attribute contract](docs/semantics/BUILTIN-ATTRIBUTES.md),
[ATTR02 review](coverage/semantics/builtin-deprecated-review.json).

ATTR03 stages selected error-handler and `assert` callbacks at the internal API
phase: Deprecated precedes copies, by-reference warnings and reception. Error
handlers run with their registry disabled; `assert` warnings retain the active
handler, saved target and live failure policy. Captured Closure targets stay
borrowed until one call owner starts at entry. Ten new native-first originals
agree exactly, including one unmarked control; four reached fronts pass 179
conditions (172 reached, seven derived guards), and private and actual-tail
joined strict431 pass.
The maintained ATTR02 `assert` boundary is promoted without replay or new
agreement credit. Explicit captured-Closure `__invoke()` was still excluded
at that cut; wider API consumers remain partial. [ATTR03 review](coverage/semantics/builtin-deprecated-api-review.json).

ATTR04 extends that selected API cursor to exception handlers, including
unmarked callbacks. Deprecated precedes copies and by-reference warnings;
the moved registry owns the selected callback and the cursor holds the original
Throwable. Warning-handler replacement and nested exception reentry preserve
the original target; Closure call ownership begins at entry and can end before
readonly result validation. Nine new native-first originals agree, including
two terminal fatals. Four reached fronts pass 189 checks (184 reached, five
derived), and private and actual-tail joined strict431 pass. One measured old
API refusal remains zero credit. Effectful special callables remain partial.
[ATTR04 review](coverage/semantics/builtin-deprecated-exception-api-review.json).

ATTR05 stages explicit captured-Closure `__invoke()` wrapper (8192) then callee
(16384) warnings before inner copies, named holes and reception. Raw arguments and live
references survive both handlers; inner Closure ownership begins after fake
named preflight, while trace redaction keeps raw and coerced snapshots distinct.
Nine normal originals agree; a tenth native original was an explicit
unused-owning-result boundary with zero agreement credit at that cut. Six full reached
groups pass 337 checks (328 reached, nine derived), plus a separate bounded
53-check inner-throw diagnostic. Private and actual-tail joined strict432 pass
at separate cuts.
Wider special callables/messages remain partial.
[Wrapper review](coverage/semantics/builtin-deprecated-closure-invoke-review.json).

ATTR06 removes that owning-result fence: existing release jobs retire raw outer
arguments, then the unused by-value return, then the outer Closure receiver.
Each pending owner stays distinct through aliases; destructor callbacks use the
real caller and preserve supplied throws through remaining outer retirement.
Four originals agree: one former boundary uses retained native bytes, and three
new native-first controls cover used results, returned-argument aliases and a
throwing value destructor with caller traces. Three full reached groups pass
186 checks (no derived guards); private and actual-tail joined strict432 pass
at separate cuts. Wider callback, reference-return and reentry histories remain partial.
[Return review](coverage/semantics/builtin-deprecated-closure-return-review.json).

ATTR07 admits builtin literal/NULL NoDiscard and Deprecated on real Closure/arrow
expressions. Checked keyword receipts preserve multiline names/lines; shared and
snapshot captures survive handlers, warnings use selected/rebound scopes, and
Closure calls borrow their bound receiver. Nine eligible originals agree (six
normal, three static rejections); five reached groups pass 428 checks (422 reached,
six derived), focused syntax11 and private strict432 pass. One unsafe `assert`
reentrancy source has an unresolved native lifetime observation, preserved at zero
credit with exact expired-before-copy refusal; the safe control keeps an external
owner. General messages and wider consumers remain partial. The current-tail
join passed strict433 and three retained-native source comparisons at separate
cuts; later disjoint GC, enum, CONFIG and magic Generator changes have a reviewed
compatibility bridge. [Producer review](coverage/semantics/builtin-deprecated-closure-expression-review.json).

ATTR08 gives shutdown/tick FCC caches separate object and Closure owners,
including duplicate object IDs. Raw invokable and array-form tick identities
stay distinct; methods borrow This and inline unregister retires arguments,
cache.object, then cache.closure. Readonly selected metadata validates cleanup
after scope retirement. Quiet shutdown retention continues through FINAL.
Five normal originals agree; four reached groups pass 296 checks (292 reached,
four derived), private strict 432 passes, and one Closure-array control remains
an exact Unsupported boundary/zero credit at that cut; ATTR09 below extends its
tick consumer. The OB05 join passes strict433,
the retained captured-FINAL original, and two new exact raw-invokable originals.
Buffered post-output release reaches two equal FCC owners before retirement;
the affected bound-Closure executor case also passes. Other late-free and wider
callback/compiler forms remain partial. The current-parent bridge retains the accepted
strict and focused source/reached gates across disjoint enum pipe, Generator and
explicit-GC additions.
[Cache review](coverage/semantics/callback-fcc-cache-review.json).

ATTR09 stages cached tick `[Closure,"__invoke"]` calls: 8192 before outer copies,
reference warning 2 with a fresh private cell, then 16384 before inner reception.
The FCC owns the outer Closure; the user call adds one instance and borrows This.
Raw/received sensitive traces stay distinct, and unused results retire after raw
arguments while the cache remains live. Five normal originals agree (four new
native originals plus one retained-native former boundary); four reached groups
pass 302 checks (300 reached, two derived); private strict 432 and joined
strict 433 pass. A retained-native reference-warning/unregister source agrees
again on the corrected cache owners. The first normal deadline and two fixture
failures retain zero credit. Other API wrappers, late free and the older
source-wrapper inner-warning trace-head location remained partial at that cut.
[Tick wrapper review](coverage/semantics/callback-closure-invoke-review.json).

ATTR10 gives that source-wrapper inner warning's handler trace head the real
explicit `Closure->__invoke` call file/line, matching its existing wrapper frame.
One native-first original now agrees exactly; a reached warning state passes 24
assertions and full strict433 passes. The old model's two missing location
predicates remain a zero-credit counterexample. Wider wrapper/reentry and late
callback cleanup remain partial. [Trace-head review](coverage/semantics/builtin-deprecated-closure-trace-head-review.json).

ATTR11 retires a single raw invokable tick callback and one copied object
argument after output FINAL, with no assertion callback and normal completion.
The tick task owns the argument and both equal FCC object/closure slots while
the registry empties; it releases the argument first, then the two FCC slots,
before the existing shutdown-list queue. Two native-first originals agree
exactly, including a retained shutdown entry. Three reached states pass 88
assertions and show callback owners 2→1→0; private and joined strict433 pass.
The earlier Unsupported baseline, two compiler attempts, recorder failure and
exploratory output-buffer restart controls retain zero agreement credit. Wider
tick entries, assertion callback, abrupt reentry and late-free paths remain
partial. [Late tick review](coverage/semantics/callback-late-tick-final-review.json).

ATTR12 extends normal post-FINAL tick retirement to two raw invokable entries,
each with one copied object argument. The first task owns only its argument and
two FCC slots while the second stays rooted in the tick list; after the first
callback retires, the second follows in registration order. One native-first
source agrees exactly (`B;F;A1;C1;A2;C2;`). Four reached states pass 120
assertions, including both callbacks' 2→1→0 owner transitions; the ATTR11
singleton source and reached state still pass. Strict433 passes. The original
two-entry Unsupported baseline and an unanchored stage selector have zero
agreement credit. More than two entries, mixed callbacks, assertion callbacks
and abrupt reentry remain partial. [Tick-pair review](coverage/semantics/callback-late-tick-pair-review.json).

ATTR13 removes that length cap for a nonempty ordered tick list whose entries
have the same normal raw-invokable/one-object-argument shape. Its task still
transfers one head at a time and leaves the tail rooted. A three-entry
native-first source agrees exactly in registration order; six reached states
pass 143 selected checks across first, middle and last entries, including each
callback's 2→1→0 owners. One shared-callback alias source also agrees, and the
ATTR11/12 source regressions and private/joined strict433 pass. The prior
Unsupported baseline and three fixture elaboration failures retain zero
credit. Mixed callback shapes, assertion roots and abrupt reentry remain
partial. [Tick-list review](coverage/semantics/callback-late-tick-list-review.json).

ATTR14 admits any finite number of copied object arguments, including zero,
per raw invokable entry in that ordered post-FINAL list. Each copied argument
must differ from its callback object. Two native-first mixed-arity sources
agree exactly, including a shared callback across zero- and two-argument
entries; a repeated-argument control also agrees. Six source-reached states
pass 122 checks and show the shared callback's FCC owners 4→3→2→1→0, with both
arguments retiring before the callback. Private strict433 passes. The earlier
Unsupported baseline and a draft binding error retain zero credit. Scalar,
array/reference and callback-as-argument payloads, assertion roots and abrupt
reentry remain partial. [Tick-argument review](coverage/semantics/callback-late-tick-arguments-review.json).

The earlier GC05 cut admitted public destructors on quiet, canonical
materialized ordinary cycles when the legacy callback walk and claimed walk
agree on ordered visits and counted nodes in the actual collector plan. The
collector rechecks after callback
mutation and before fresh collection of already-called survivors, refusing an
order mismatch. Two native-first sources agree, including resurrection followed
by later count 3; four strict SL reached groups pass 151 checks. Private strict429
and actual-tail joined strict430 compilation pass; source and reached cuts retain
their original inputs. At that cut, count-ambiguous callbacks, WeakMap callbacks,
residual tags, workers, hooks, reentry and active contexts remained partial.
[GC05 review](coverage/semantics/gc-materialized-callback-review.json).

CLASS157 admits public zero-argument anonymous `__toString` through ordinary
implicit Stringable linking and conversion. Raw-header names/counters remain
stable through deferred publication; saved conversion owners release before
emission, destroying the receiver when no other owner remains. Nine originals agree (seven normal, two static rejections), and
285 conditions pass (278 reached, seven controls). Return, never-kind and compile
diagnostics retain their distinct formats. Three changed private strict433 cuts,
native6+2+1, old2 and source/state cuts stay separate; the never-kind mismatch
and fixture elaboration failure retain zero credit. Wider magic, reference,
attribute, callable and lifecycle contexts remain partial.
[Stringable review](coverage/semantics/anonymous-stringable-review.json).

CLASS156 admits public zero-argument anonymous destructors through the ordinary
method compiler and lifecycle. Alias and temporary release, eval callbacks,
reverse global cleanup, escaped failed constructors and pending-exception
replacement have five exact source agreements. Two reached groups pass 240
conditions (228 reached, 12 derived across six controls); private strict433 passes.
Native5/old2, source and state cuts stay distinct. Nonpublic/reference-return/
attributed destructors, other magic methods and wider lifecycle contexts remain
partial. [Destructor review](coverage/semantics/anonymous-destructors-review.json).

CLASS155 admits anonymous array argument unpack through the ordinary
source classifier, array prescan/COW and binder. Embedded aliases stay shared;
direct slots promote only in the live table. Direct elements of value inputs use
fresh cells when reference demand requires them; embedded aliases remain shared.
Expanded names preserve holes/default reception and error priority;
constructorless arrays use the existing dummy send frame. Seven originals agree,
and 242 conditions pass (235 reached, seven derived guards), with private strict432
and actual-tail joined strict433 at separate cuts.
The original native5/old2 and separate literal/no-ctor natives retain their cuts;
projection has no agreement credit.
Traversable constructors, promotion/nonpublic modes and other anonymous magic
methods remain required class work.
[Array-unpack review](coverage/semantics/anonymous-constructor-unpack-review.json).
The prior [variadic review](coverage/semantics/anonymous-constructor-variadic-review.json)
retains CLASS154 source6/state270, its excluded COUNT observer and failed fixture.
The prior [reference review](coverage/semantics/anonymous-constructor-reference-review.json)
retains CLASS153 source6/state217 and its own native, strict and fixture cuts.
The prior [finite-arity review](coverage/semantics/anonymous-constructor-arity-review.json)
retains CLASS152 source6/state212 and its argument-TypeError/missing-arity display distinctions.
The [rejected-source review](coverage/semantics/anonymous-rejected-sources-review.json)
retains CLASS151 source5/state261 and zero-cost parser-rejection history at its own cuts.

GC03's quiet WeakMap registration/proxy-count behavior and its separate tested
cuts remain in the [GC03 review](coverage/semantics/gc-registration-order-review.json).
Typed-current capture and scalar argument snapshots remain in the
[CONFIG contract](docs/semantics/INCLUDE-SOURCES.md).

Current combined behavior is summarized below. Family docs and linked reviews
retain exact admission limits, original failures and tested cuts; this file does
not repeat historical receipt counts or renew their execution credit.

## Integrated behavior and entrypoints

| Family | Current behavior and scope |
| --- | --- |
| Source and compilation | Checked ASTs retain source occurrences, ordered declaration publication, lexical/called scope and emitted-task authority. Include/eval, anonymous classes, traits and linked headers use source-authenticated routes; remaining acquisition and linker contexts stay explicit. [Source context](docs/semantics/SOURCE-CONTEXT.md), [linking](docs/semantics/LINKING-HANDOFF.md), [classes](docs/semantics/SOURCE-CLASSES.md). |
| Values, operators and warning decisions | Arithmetic and conversions are pure executable SpecTec. Supported warning callbacks preserve saved operands, live delayed reads, source sites, handler changes and pending-Throwable order. Operators, casts, dimensions and undefined-variable routes remain partial across their producers. [Numerics](docs/semantics/NUMERICS.md), [dimensions](docs/semantics/DIMENSIONS.md), [comparisons](docs/semantics/COMPARISONS.md). |
| Arrays and references | Physical owner edges distinguish DIRECT copies from ALIAS cells, COW table copies, selected lvalues and shared descendants. Iterator spreads retain raw current references through key before copying the value; invalid-key cleanup retires current before DATA while protecting the partial builder. Ordinary initialized declared fields share the reviewed fold across legal return modes. Materialized/special/cyclic graphs and wider callback lifetimes retain their documented limits. [Array unpack](docs/semantics/ARRAY-UNPACK.md), [reference wrappers](docs/semantics/REFERENCE-WRAPPERS.md), [cleanup review](coverage/semantics/array-iterator-invalid-key-cleanup-review.json), [field review](coverage/semantics/array-iterator-byval-fields-review.json). |
| Comparisons | Reached physical slots, count/key/value order, live reference contents and COW snapshots decide comparisons. Visited captured-graph traversal has no fixed depth limit and reports an authentic active-left recursion Error; earlier identity/class/leaf decisions skip later unsupported payloads. Canonical root admission and acyclic Previous-path validation have no numeric context/length ceiling. Canonical same-kind roots of the admitted builtin kinds share the visited physical-slot fold after older admissions once both finite Previous paths authenticate, preserving cache/trace/previous/severity order and reached table effects. Invalid/cyclic/materialized/freeing Previous nodes, pending states and actually reached callback contexts retain family limits. Captured canonical builtin Throwables share this fold; every distinct equal-kind entry checks active-left recursion before slots, including Previous descent. Supported ordinary images of any visibility admit uncalled methods, locally authenticated interfaces including implicit Stringable, and finite source-parent paths validated by actual names, links and publication order. Seen origins reject parent cycles before layout expansion; builtin parents/hook/readonly and wider layout fences remain. Whole-path authentication stays eager. Empty inline same-class images return zero before the object recursion guard; actual empty caches retain table order, COW and ordinary owners. Empty foreach produces a real table, and empty cached clones share without a callback or start uncached with one. Private/protected fields retain mangled KEY/DECL authority through actual caches and final typed-alias source retirement. Declared INITIAL/UNSET holes retain inline position and physical cached INDIRECT count/key order. Deleted dynamic mirrors leave current live count/order intact; deleted-only clone histories preserve sharing and callback copy routes. [Dynamic-deletion review](coverage/semantics/throwable-trace-dynamic-unset-comparison-review.json). [Declared-hole review](coverage/semantics/throwable-trace-uninitialized-comparison-review.json). [Nonpublic-image review](coverage/semantics/throwable-trace-nonpublic-comparison-review.json). [Empty-image review](coverage/semantics/throwable-trace-empty-layout-comparison-review.json). [Current comparison contract](docs/semantics/COMPARISONS.md), [finite captured graphs](coverage/semantics/throwable-trace-unbounded-comparison-review.json), [finite Previous paths](coverage/semantics/throwable-previous-finite-comparison-review.json), [standalone traces](coverage/semantics/throwable-null-trace-comparison-review.json), [base fallback](coverage/semantics/throwable-base-null-comparison-review.json), [linked base](coverage/semantics/throwable-base-previous-comparison-review.json), [captured Throwables](coverage/semantics/throwable-captured-comparison-review.json), [ordinary methods](coverage/semantics/throwable-trace-methods-comparison-review.json), [local interfaces](coverage/semantics/throwable-trace-interfaces-comparison-review.json), [inherited images](coverage/semantics/throwable-trace-inheritance-comparison-review.json). |
| Calls and callable values | Ordinary, scoped, captured and magic-call routes retain the selected callee/receiver, lexical/called scope, argument origin, positional/named ordering and reference mode across later effects. Closure and pipe consumers preserve their real owners, send diagnostics and abrupt cleanup. Callable producers, signatures and reentry remain partial. Bounded NoDiscard declarations preserve pre-body warning and pending-owner behavior. [Attributes](docs/semantics/BUILTIN-ATTRIBUTES.md), [Calls](docs/semantics/SOURCE-CALLS.md), [Closure::call](docs/semantics/CLOSURE-CALL.md), [first-class callables](docs/semantics/SOURCE-FIRST-CLASS-CALLABLES.md). |
| Configuration and constants | Supported INI_SET/DEFINE/CONSTANT/DEFINED routes retain their selected callee, option/name and API timing. Iterator and named Generator inputs preserve real DATA/INPUT and Aggregate producer history, copied sends, named-key Error priority and pre-API cleanup. CONFIG typed-current reads reuse property-source validation; structural receipts remain valid after physical cache retirement. Iterator sends retain raw scalar snapshots or real finite ARRAY/ordinary-instance slot roots, then defer INI_SET binding/conversion until after DATA/INPUT cleanup. COW, shared embedded aliases and API TraceArgs keep their ordinary owners. Generator/other consumers, effectful casts and wider lifetimes retain their documented limits. [Include/configuration](docs/semantics/INCLUDE-SOURCES.md), [constants](docs/semantics/SOURCE-USER-CONSTANTS.md). |
| Classes, properties and enums | Linked declarations preserve receiver identity, slot declaration, visibility, typed-reference sources, readonly/hook policy and diagnostic order. Supported magic getters and reference-get chains preserve alias/copy and rebind timing. Enum declarations lower to cached singleton cases with lazy backing checks, readonly slots, ordered interfaces and generated/user methods. Registered-loader first use for static calls and class-constant fetches preserves selected class/member order and source-authenticated resume; reached dynamic/named/folded/enum cases and forged-target rejection retain separate raw cuts under `.tools/enum-acquisition-review-state-*`. Captured enum `cases(...)` preserves its selected target and singleton cache after closure retirement. Captured scalar `from(...)`/`tryFrom(...)` preserve cold backing tables, ordinary/inherited constant aliases, caller strictness and cached case identity after closure retirement. Captured Stringable arguments preserve their real callback child and line, selected closure lifetime and temporary retirement before lookup. For published enums, class-string array callables select generated `cases()`/`from()`/`tryFrom()` before argument evaluation; a case-object receiver also invokes `from()`. Array Stringable conversion preserves the selected enum and temporary retirement. Computed, literal and folded class-method strings also fix generated targets before arguments, preserving full original bytes and real named Stringable children across rebinding and temporary retirement; packed Stringable origins remain Unsupported. First-class string and array captures use internal Closures held through argument clears and released after invocation. Source-certified direct or negated enum-case conditions in class constants retain selected case identity or scalar results, including a condition from another enum; wider object-valued conditional transfers, other callable routes, the default loader, case attributes, link/type contexts and object lifetimes remain partial. [Classes](docs/semantics/SOURCE-CLASSES.md), [properties](docs/semantics/SOURCE-PROPERTIES.md), [property references](docs/semantics/SOURCE-PROPERTY-REFERENCES.md), [enum evidence](docs/ARTIFACTS.md). |
| Generators and Fibers | Supported named/method/Closure producers retain actual resumer and callee owners, by-value or reference caches, supplied Throwables and catch/finally continuations across Fiber suspension. Receiver-free static and same-`$this` nonstatic Generator bodies called through finite scoped chains retain real scope after return; supported real Closure, captured/bound user-method, implicit invokable and admitted magic-handler factories also authenticate scoped method-created bodies when the original source scope differs. Direct Generator-bodied __invoke uses its runtime-selected method; admitted direct magic handlers retain their actual target/owner receipt through close and Fiber transfer. Delegation and SEND preserve their selected chains and copied/delivered owners. Wider producers, binding/delegation combinations and teardown remain partial. [Generators](docs/semantics/GENERATORS.md), [Fibers](docs/semantics/FIBERS.md), [delegation](docs/semantics/GENERATOR-DELEGATION.md), [reference yields](docs/semantics/GENERATOR-REFERENCE-YIELDS.md). |
| Lifetime, weak references and collection | Eager release tracks real ownership, pending results/Throwables, destructor frames and protected storage. WeakMap protocols preserve weak-Key visibility, ordinary Value owners, aliases, selective notification and conditional collection. Physical tracing handles admitted ordinary/materialized graphs; quiet same-Key entries and no-Map ordinary siblings use claimed first-visit counts. Canonical materialized destructor callbacks retain claimed count and nested-buffer authority across retrace, including ordinary caller locals and receivers. Source-authenticated temporary cleanup, borrowed result caches and unused WeakReference result transfer preserve potential-root order. Enum cases and original receiverless fake Closures skip GC candidate buffering while retaining their owners and graph edges; clone and bind copies remain collectable. WeakMap callbacks, skipped prior histories, residual and other active collector contexts remain open. Stable retired cell metadata owns nothing; pooled literal arrays remain rooted by compiled constants. [Eager cleanup](docs/semantics/SOURCE-EAGER-DESTRUCTORS.md), [reference returns](docs/semantics/SOURCE-REFERENCE-RETURNS.md), [weak references](docs/semantics/WEAK-REFERENCES.md), [cycle collection](docs/semantics/CYCLE-COLLECTION.md). |
| Diagnostics, output and environment | Supported handlers retain registration, callback and emitting-frame identity through warnings, throws and cleanup. Echo/print preserve left-to-right effects and flat-array diagnostics; bounded default output buffers retain native callback/output order. Request, clock, stream and startup profiles have explicit contracts rather than ambient host answers. Wider buffering/shutdown/tick behavior remains open. [Handlers](docs/semantics/SOURCE-ERROR-HANDLERS.md), [exception handlers](docs/semantics/SOURCE-EXCEPTION-HANDLERS.md), [output buffers](docs/semantics/OUTPUT-BUFFERS.md), [request inputs](docs/semantics/REQUEST-INPUTS.md). |

## Decisions that constrain further work

- Implement PHP behavior in authored semantics, including pure arithmetic; the
  pinned project-local PHP binary is the differential oracle, never a runtime
  fallback. Core intrinsics/internal protocols are included where the language
  needs them; ordinary external libraries and services are separate.
- Authenticate execution from actual source, selected declarations and genuine
  frames. Historical/nonowning receipts preserve provenance; they neither own a
  dead value nor establish a current live alias.
- Keep acquisition, key evaluation, send snapshots, API reception and cleanup
  distinct. Type-source metadata constrains writes without adding owner edges;
  reading an authenticated typed cell does not perform coercion.
- Preserve diagnostic priority, skipped later work, PHP Error/Throwable identity,
  pending completion and physical lifetime. Explicit Unsupported, failed
  derivations, runner failures and timeouts are different outcomes.
- A bounded passing family does not close its inventory obligation. Extend
  coherent producers/consumers and shared invariants without special-casing
  spelling or weakening refusal boundaries.

OB01 integrates normal EOF and integer/string EXIT draining for existing user
output handlers after real shutdown/global/store retirement. Nested lower writes,
weak diagnostics and callback-local destructors preserve saved completion and the
sole handler owner. Fifteen native-first normal originals agree, six reached
groups pass 238 assertions, private strict427 and joined actual-tail strict429
pass. Its original 90/40-second abnormal timeouts and then-unrun captured throw
retain their historical zero-credit status. OB02 now covers those sources at
new tested cuts. [OB01 review](coverage/semantics/output-request-end-review.json).

OB02 admits default fatal takeover from builtin FINAL throws with scalar messages
and NULL previous. Stored traces and cache mutation precede fatal reporting;
inactive buffers then release raw owners without lower writes. Four originals
match PHP and three reached groups pass 131 assertions. Actual-tail strict431
and both affected guard fronts (70+33) pass without native or differential source
reruns. Its original pending-Throwable decrement admission was nonfinal or
destructor-inactive; OB03 extends it below. Selected exception handlers, wider
rendering and reentrant/abrupt deactivation remain partial.
[OB02 review](coverage/semantics/output-final-throw-review.json).

OB03 releases the retained local FINAL Throwable after cache/reporting while
buffers remain active/running; child output stays buffered. A child destructor
throw preserves the first report, emits a fresh unchained fatal and retains the
existing abandoned C cleanup owners before raw-zoh deactivation. Four originals
agree exactly and four reached groups pass 169 checks. Private and actual-tail
joined strict431 and separate affected FINAL fronts 77+33 pass. The original sole Unsupported and later failed
attempts retain zero agreement credit. Wider selected-handler/rendering and
reentrant/abrupt raw-owner teardown remain partial.
[Pending-release review](coverage/semantics/output-pending-release-review.json).

OB04 selects existing exception handlers for FINAL throws through authenticated
API reception and ordinary ignored-return/original cleanup. Normal handling keeps
UNDEF failure forwarding and real lower callbacks; abrupt cleanup preserves only
actual C owners before fresh fatal/deactivation. Retained Closure fast-free effects
after executor inactivity preserve the pinned late diagnostic and CLI0. Eleven
originals agree and eight reached groups pass 465 checks. Private strict432 and
actual-tail joined strict433 pass.
The independent 303 checks include retired GC HANDLE authority; author 162 includes
first-duplicate allocator mode controls. Slow executor teardown was still open at
that cut; wider internal hooks/rendering and reentrant deactivation stay partial. Source/state cuts retain
their original identities; failed forecasts, fixtures and the repaired invariant
cut keep zero credit.
[Selected FINAL review](coverage/semantics/output-final-exception-handler-review.json).

OB05 adds allocator-selected executor table/storage effects after FINAL and active
retirement of late shutdown registrations. Ordered arguments, the independent FCC
receiver and Closure retain their real C counts through ordinary release and caught
destructor throws. Native symbol/function/class/handler order, shared inherited
method statics and standard-hook shields determine the first inactive callback.
Twelve source/request contexts agree exactly at their recorded cuts; nine reached
groups pass 573 checks (author 171, independent 402), with a separate affected OB04
allocator group passing 58. Private strict433 and current-master joined strict433
pass; one inherited-static original agrees again at the joined 95f5bebf7 cut.
Earlier owning module/autoload
cleanup, uncovered table owners, wider hooks/rendering and reentrant/abrupt cleanup
remain partial. Original failures retain zero credit; the retained slow native
control is promoted without native replay.
[Nonfast executor review](coverage/semantics/output-executor-nonfast-review.json).

OB06 models a no-argument buffer start attempted by a shutdown-argument
destructor after output deactivation. The Notice, false result and unchanged
buffer stack/sequence agree in six source/request contexts, including suppression,
selected handler and fallback paths, slow allocation and an early-shutdown
success control. Three argument/reentrant forms reach checked Unsupported; one
source-reached Notice state passes 30 checks with budget resume. Private and
joined strict433 pass; joined plain/slow and selected-handler sources plus the
three refusals pass on the parent with changed executor queue roots. A retained
handler-return object destructor has native fast/slow observations but fails
before its nested call at the OB06 cut and earns zero credit there.
[Post-deactivation review](coverage/semantics/output-executor-post-deactivate-review.json).

OB07 models the selected Notice handler's returned-object destructor during
normal post-deactivation queue release. Echo-only and nested no-argument
`ob_start()` destructors agree with pinned PHP in both allocator modes; the
nested call uses the built-in Notice while the selected handler is disabled,
returns false and leaves the buffer stack/sequence unchanged. One source-reached
state passes 40 conditions, and OB06's explicit-argument, callable and active
handler-body starts remain checked Unsupported. Private and joined strict433
pass; joined nested fast/slow sources and the three refusals pass with the
executor tick-owner branch present. The retained OB06 native original is now
promoted with exact model agreement.
[Returned-handler cleanup review](coverage/semantics/output-executor-retval-review.json).

OB08 admits one positional `ob_start(null)` after output deactivation during
normal executor queue release. The default handler creation fails before any
buffer push, emits E_NOTICE and returns false. Fast and slow allocator sources
and a selected-handler source agree exactly with pinned PHP. Two source-reached
checkpoints validate call/Notice authority, empty buffers and unchanged output
sequence; named-null, callable, invalid-integer and handler-body reentrant
forms remain checked Unsupported. The previous noarg Notice state still passes.
[Explicit-null executor review](coverage/semantics/output-executor-explicit-null-review.json).

CLASS156–163 are integrated at `0d756bb0e` after independent cumulative review and a joined 433-module SL gate. Their scoped evidence and remaining limits are in [SOURCE-CLASSES](docs/semantics/SOURCE-CLASSES.md) and the linked reviews.
CLASS164 is integrated at `4f3d1a90a`: four exact copied trait `parent` source originals and three reached state groups validate existing rules. [Review](coverage/semantics/trait-captured-parent-view-review.json).
CLASS165 is integrated at `fde2099b3`: four exact copied-alias trace originals and two reached groups pass; three tick-wrapper probes remain zero credit. [Review](coverage/semantics/trait-captured-alias-parent-trace-review.json).
CLASS166 is integrated at `0ed9ac41f`: one parented anonymous trait capture source and 48 reached conditions pass with private and joined strict433. [Review](coverage/semantics/anonymous-trait-capture-review.json).
CLASS167 admits bounded parentless anonymous trait capture at first `new`; two exact sources, 45+43 reached conditions, private and joined strict433, and a non-NUL trace control pass. Native-only name lookup changes from 0 to 1 across `new`. Interface combinations, multiple uses and adaptations remain excluded. [Review](coverage/semantics/anonymous-parentless-trait-capture-review.json).

COMP160–161 are integrated through `084768600`: declared INITIAL/UNSET cached
images and deleted dynamic histories retain comparison, cast and clone behavior.
Their exact source, reached-state and affected gates are in
[SOURCE-CLONE](docs/semantics/SOURCE-CLONE.md) and the linked reviews.

COMP162 copies ordinary mixed declared tables after dynamic reinsertion when
obsolete dead mirrors precede a later live row. Four exact source agreements,
39 reached conditions, two affected clone sources and joined strict433 pass.
Live/live duplicate names and nonordinary tables remain partial.
[Review](coverage/semantics/throwable-mixed-reinsert-clone-review.json).

COMP163 admits checked file-mode shebang `ENCODEDPROGRAM` tick plans for main and
included units. Seven exact native/model sources and 32 source-reached tick-plan
conditions pass at the committed cut, with joined strict433 on the composed
master. BOM files follow the existing `PROGRAM`/InlineHTML route; eval uses its
separate parser mode. Other preamble profiles and wider encodings remain partial.
[Review](coverage/semantics/source-preamble-tick-review.json).

COMP164 admits terminal HALT offsets in raw, BOM-free file shebang units. Six
exact native/model sources cover direct offsets, an included child, CV lookup
and filename-local registration; ten checked-AST premises cover source offsets
and nonraw/BOM refusal. Joined strict433 passes. Plain and BOM files retain
their `PROGRAM` behavior; other encoded HALT profiles remain partial.
[Review](coverage/semantics/halt-preamble-review.json).

## Active and unintegrated work

| Track | Owner-confirmed current work |
| --- | --- |
| V110 | Temporarily held/unintegrated after repeated generic cybersecurity-risk flag; CPU3 released, exact rejected action unknown. Accepted source3 retained. |
| COMP123 | Held unrun; no actor. |

The active table is an owner-confirmed handoff snapshot, not validation credit
for private changes. Integrated work is indexed by the current family docs,
[feature inventory](coverage/semantics/features.json) and linked reviews above;
[ARTIFACTS](docs/ARTIFACTS.md) locates original evidence and private cuts.

## Remaining core work

- Finish the partial inventory obligations across every source constructor and
  runtime dependency. Unsupported cases remain explicit; a passing bounded slice
  does not close its family.
- Extend warning/read/cast and argument consumers, callable/Closure forms,
  reference parameters/returns and constrained coercions without erasing delayed
  reads, diagnostic priority, saved targets or abrupt cleanup.
- Complete wider array/object/reference ownership, nested access and key forms,
  ArrayAccess/Iterator interactions, COW, released targets and callback lifetimes.
- Complete remaining class/static/trait/enum/attribute/hook/readonly contexts and
  wider magic/property/callable producers, including reentry and typed aliases.
  Beyond public destructors and Stringable, anonymous magic methods and wider forms
  remain substantive class work; Traversable constructor producers,
  promotion/nonpublic modes and wider factories also remain required.
- Complete wider Generator/Fiber suspension, delegation, destructor reentry,
  physical collection, weak-reference/WeakMap, output/shutdown/tick and other
  required lifecycle behavior.
- Extend remaining Traversable CONFIG producers, consumers and lifetimes beyond
  initialized user Iterators, fresh named Generators, their bounded Aggregate producers and the empty/singleton WeakMap slice.
- Extend dynamic compilation, startup/configuration profiles, environment and
  provider consumers within the agreed core/intrinsic boundary. Ordinary external
  libraries/services are separate; builtin presence alone supplies no semantics.
- Run final combined current-source validation and a fresh copied-path,
  network-isolated offline rebuild. Current local tool reuse is not that rebuild.

Interaction-tree semantics in Rocq and the selected BOLA/CRIS proofs follow
completed PHP core and renewed differential validation; they are not established
by these tests.

## Paused boundaries

Do not resume or broaden these lanes through neighboring work:

- OP12 increment/decrement dimension warnings.
- Source47 low-precision DEFINE-name NaN conversion.
- Owned-NUL source-release behavior.
- Undefined by-reference LIST key handling.
- COMP88 Stringable supplied-throw crash.

## Validation and evidence

Use the pinned project-local PHP oracle and matching profile. Preserve original
bytes/path/cwd, raw streams/status, semantic completion, tested revision,
compiler/runtime identity, commands and relevant environment. Ordinary, explicit
request and callable profiles retain separate contracts.

Independent review covers semantic correctness, counterexamples and test
reliability. Fix discrepancies narrowly; rerun affected checks only. Metadata
edits and pointwise disjoint composition do not renew accepted execution credit.
Interrupted, timed-out, Unsupported, malformed and budget-control outcomes remain
separate from native agreements. State fixtures complement source comparisons.

Large originals and raw failures stay outside Git; [ARTIFACTS](docs/ARTIFACTS.md)
provides recovery. Detailed prior checkpoints remain in their existing ledgers,
[MILESTONE-HISTORY](MILESTONE-HISTORY.md), and Git history through `25b63539e`.
The [post-arrow baseline](coverage/semantics/post-arrow-integration-review.json)
retains its historical profile/count identities, not current full-core coverage.
Keep this file focused on current behavior, remaining work and active boundaries;
replace superseded status prose instead of accumulating receipt history.
