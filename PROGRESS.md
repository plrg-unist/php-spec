# Core PHP semantics progress

Target: PHP 8.5.10 CLI NTS 64-bit. [PLAN.md](PLAN.md) defines complete core;
[the inventory](coverage/semantics/features.json) tracks obligations. Selected
agreement does not establish complete semantics. Large evidence stays outside
Git; [ARTIFACTS.md](docs/ARTIFACTS.md) locates it.

## Current checkpoint

Ordinary named keyword NEW267 now resolves self/parent/static in the actual
caller before class work and arguments. Inherited constructor entry uses its
immediate owning caller; service-unit main code follows persistent scope entry
bindings. Known function scope errors compile; main, eval, trait and Closure
errors remain deferred. Source18 normal/4 compiler and reached cold57/recursive44
plus corrected eval53 pass at91dc. Actual23c/264/257 composition at9b8 passes
private self/static and current identity after null-binding resets called scope.
Original preparation/eval-fixture failures remain in the [ledger](coverage/semantics/named-keyword-new-review.json).
Autoload and complete core remain open; returns stay paused.

Non-object casts261 now populate stdClass scalars/arrays, share all-string tables
through genuine COW and fast clone, and preserve numeric round trips, alias type
owners and active foreach cursor history. NaN warnings retain the allocated object
and original operand location; NUL-key notices retain a nonowning TABLE/SERIAL
marker through callbacks and delayed reference promotion. Raw undefined buckets
keep distinct read/isset/copy/comparison behavior. Twelve full source comparisons
retain 3a/82c/b0 cuts; one actual 8ada/a4fc composition gives the first agreement for
the former251 native-only multiline cast holder. Four source-derived groups pass
208 premises at b0, with original fixture stops preserved. The
[cast ledger](coverage/semantics/object-casts-review.json) separates these cuts,
two retired-pointer originals and a longer companion timeout (zero agreement).
Actual257 destruction/frame/pruning hooks are preserved separately. Wider
raw-undefined consumers, lifecycle/GC and callback contexts remain required.

Request-stage destructors257 now repeat reverse direct globals and then scan
reusable live store handles. Once marks, bailout/failed-constructor suppression,
private visibility, nested USER calls and ordered outgoing slots retain exact
owners. Caller restoration precedes compiled CV cleanup; extras precede receiver
release. Pending throws replace and chain through remaining slots. Ignored
by-value ordinary and automatic-constructor returns release in the live callee before
locals; C destructor helper returns remain retained. Eval/include continuations
keep source history. Explicit request facts preserve startup argc order; absent
facts keep the original environment Unsupported, and dead CVs remain admissible.
Author78 source agreements and seven/303 reached assertions retain distinct
cuts; independent64 agreements, two Unsupported controls and12/548 assertions
retain theirs. Actual253/259/260 routes and final SL/AL253 pass on the preserved
a4fc parent;264/262/266 preservation is source-reviewed without old-cut renewal.
[Contract](docs/semantics/SOURCE-DESTRUCTORS.md),
[author record](coverage/semantics/destructors-review.json),
[independent ledger](coverage/semantics/destructor-review.json).
Ordinary eager destruction and original Throwable release before stage1 are
explicit Unsupported dependencies for the next phase. GC, output buffering,
queue freeing and final cleanup remain required; complete core stays open.

REAL binding264 now resolves scope before ordered static, `$this`-unbind and
internal-scope warnings. Genuine handler continuations retain selected reasons
through callback mutation and throws. The function's own compiled entries supply
`USES_THIS`, including dead eager literal-name uses and excluding nested bodies
and runtime-name folding. Valid null bindings copy REAL statics, retain reference
captures and reset called scope; explicit null scope removes class permission.
Twenty normal source agreements retain separate2312606/ed1d5 cuts. Five genuine
owner/frame cases pass289 conditions (author113, independent176).
Actual601312 composition at2cb72 passes AL251 and one cached trait-property
METHOD child source: null bind/clone retains private default permission and exact
current identity after makers retire, with called scope reset to lexical Owner.
Original classifier nondeterminism, the combined45-second timeout and fixture
elaboration stop remain separate in the
[binding ledger](coverage/semantics/real-closure-binding-review.json).
Temporary-current and internal API consumers remain required; returns stay paused.

Ordinary dynamic NEW260 evaluates string/object selectors once and captures the
class before arguments, class-table updates and constructor dispatch. Parser
literals, later compiled keywords and runtime names keep distinct scope/error
behavior; fetch/access lines stay separate from constructor call lines. Immediate
caller records authenticate recursive constructors; completed cold-table history
retains nonowning scope after a rebound Closure retires. Source26/compile3 and
retired83/recursive46 pass at0091; affected source3 at a65 and new2 plus
contexts51/rebound45 at3f817 retain separate cuts. Actual6af8/252/263 composition
at26fba passes cached trait METHOD/clone source1 and34 scope premises with lexical
HostA and unrelated called HostB. The [ledger](coverage/semantics/dynamic-new-review.json)
preserves original failures and preparation-only checks. Ordinary named keywords are covered by267; autoload and complete core stay open.

Cached property method callables (module263) now create source Closure children
with authentic lexical scope and a separate, potentially unrelated called class.
Copied full method/receipt authority survives wrapped or plain-clone maker
retirement without owning those makers. Static and receiver-free nonstatic
children, child clones and private `new self` defaults preserve these scopes.
Two normal source agreements pass at aa899; static105 premises pass at9ae61 and
default65 atb8d10. Original fixture parse/elaboration stops remain zero-credit in
the [default ledger](coverage/semantics/deferred-static-defaults-review.json).
Wider transformed callable creation contexts remain required; complete core and
paused return verification remain open.

Current Closure/binding253 returns the exact immediate ordinary Closure and
preserves existing-object `__invoke` capture identity. Transformed fake bindings
keep frozen permission and source statics while owning only their new receiver;
internal REAL copies and returned children retain genuine scope after makers
retire. Static API receivers add no argument-evaluation owner. Selected warnings
preserve scope/error order and unwind callback writes. Source24 normal at distinct
cuts, nine owner/frame fixtures444 conditions (author214/independent230), affected
older identity3/37 and private AL237 pass. Actualc139 preserves246 modules and
passes AL247 plus one inherited property-default source: REAL current/`__invoke`
identity and private fake binding/clone permission, called scope and shared statics.
Original compiler, source and fixture failures,
the global-constant Unsupported control and native-only controls remain separate
in the [ledger](coverage/semantics/closure-current-binding-review.json).
The [contract](docs/semantics/CLOSURE-CURRENT-BINDING.md) keeps temporary-current
escape and further API/keyword consumers required. REAL warning/unbinding is
covered separately by264 above. Return verification stays paused and complete
core remains open.

Object defaults (module252) now create static/no-use source Closures and
function/method callables in genuine declaring scope. Requested-class templates
share their object values with instances and preserve exact successful bindings
across late inheritance, retry and reentry; arrays copy containers and share
embedded objects. Nonowning receipts/copy certificates reject foreign transfers
and survive source retirement, including plain clones. Nine normal source
agreements retain 0d0d (first2)/0e472 (other7); six programs/335 premises retain
0e472/72d5.
One actual238 trait-import source and98 premises pass at a502: cached private
method/function targets keep their first authentic lookup, while each property
uses its own publication prefix and fresh called class. All original compiler,
permission and fixture-seek failures remain separate in the
[default ledger](coverage/semantics/deferred-static-defaults-review.json).
Other object/default producers and consumers remain required; complete core and
paused return verification remain open.

Nested coalesce-assignment262 now owns quiet row values on defined CV-rooted
array chains while the memoized write walks current storage. Computed keys run
once; variable keys stay live. Prefix copy-abort creates a genuine temporary,
while final-key abort skips a delayed RHS CV. Late keyed RHS warnings follow
entry acquisition, write captured null through handler throw and recheck a live
typed cell at the restored emitter. Author9/233 and independent11/277 share two
originals, giving18 unique private programs/510 assertions atf9/2b65/cf7. The
independent tail check found and verified the late-dispatch double-pop fix; only
five affected sources and84/76/76 states were renewed. One actual6013 source
at9ac retains private Owner/Child selection, quiet row17 versus new parent13 and
live caller/static17. Original fixture/loader failures and native prediction
corrections remain in the
[nested coalesce ledger](coverage/semantics/nested-coalesce-review.json).
Wider memoized containers, GLOBALS RW and earlier container/string/object
producers remain required; complete core and paused returns remain open.

Nested unset and append255 now suspend defined CV-rooted array walks after key
and computed RHS evaluation. Intermediate unset separates before conversion,
latches missing keys as null and skips the next deprecation if the table dies;
ordered float notices share one protection. Final unset keeps its distinct rules.
Append copy-abort retains a genuine null temporary and the computed RHS. A late
missing RHS captures null, checks the old table's liveness, and can insert into a
rebound real child even before propagating its handler's exception. Key-handler
throws still stop the append and preserve typed destinations. Author6/247 and
independent18/356 share the retained expiry original, giving23 unique private
agreements at7ee/d281/643/75c8. One actual0b private-FCC/called-class source passes
at223 with abort/TEMP and live typed caller/RHS cells. Original overlap and
corrected native/source predictions remain in the
[tail ledger](coverage/semantics/dimension-tail-review.json).
Wider memoized containers, GLOBALS RW and earlier container/string/object
producers remain required; complete core remains open.

Legacy dollar-curly compiler notices258 retain the direct/computed grammar flag
through checked fresh printing and emit before child compilation with its real
path and the preceding compiler line. Main/include delivery reuses230 whole-unit
publication, genuine private emitter scope, live mask/display fallback and throw
cleanup. Five exact source/profile comparisons, SL242, 24 syntax/encoding profiles
with320 checks and37 compiler/certificate premises pass atfa084. Actual256 parent
preservation keeps243 modules without renewing those cuts. Original compiler and
fixture parse stops stay zero-credit in the
[ledger](coverage/semantics/dollar-curly-review.json). Five early-eval native pins
remain required for the genuine partial-compilation continuation after236; wider
interpolation and original non-object-cast/file-observer gaps remain open.

Dynamic object `::class`256 evaluates one child and returns its real class name
without a string cast. Eager parser concat keeps literal/keyword behavior; later
compiled constant operands reject. Embedded undefined-CV callbacks keep captured
null, including a throwing handler retained as the new TypeError previous chain;
dimension throws keep ordinary abort behavior. Source20 and seven full compiler
rejections pass at026ba, with165 reached premises in43+70+52 groups covering actual
lines, task/source admission, temporary retirement and read/exception ownership.
Unused preparation has zero execution. Original native prediction failures and
historical245 Unsupported stay preserved in the
[class-name ledger](coverage/semantics/object-class-name-review.json). One actual251
interpolation source atf626 on4208 retains callback receivers through global-slot
replacement and sees the later mutated operand. Actual247/251 routes are preserved;
complete core remains open.

Ordinary string interpolation251 now follows effective CAST/FAST_CONCAT/ROPE
order. Two-part fetched temporaries survive left callbacks; later variable
conversion reads live borrowed slots. Undefined direct CVs keep singleton null
but reread modes2+ without a second notice; callback-created arrays retain no
invented owner. Real Stringable/array callbacks, throwing cleanup and compiled
multiline lines preserve exact source/consumer/finish markers. Nine exact source
agreements and SL237 pass at88f; affected AFTER guards and111 distinct premises
pass ata7 in six unchanged groups with25 repeated setup premises. Original
fixture stops, full/fast timeouts and native-only non-object-cast line probe keep
zero credit. Actualcde/247 preservation retains240 parent modules plus251 without
renewing those gates. [Contract](docs/semantics/SOURCE-INTERPOLATION.md) and
[ledger](coverage/semantics/interpolation-review.json) retain these cuts. Wider
interpolation producers/source contexts, early eval compiler notices and affected
original dynamic-file observers remain required; complete core and paused return
verification remain open.

Ordinary Throwable reception250 now suspends weak-null/lossy warnings and
Stringable parsing for NEW and explicit inherited/scoped constructor calls.
Ordinary named-send priority stays intact; strict null/objects reject without
conversion. Successful string casts rewrite sent slots and retire old temporary
objects; integer trace arguments stay raw and fields commit only after all
formals pass. Private handlers, method retirement and recursive same-site calls
retain their own owners and traces. Source17 passes as2 at5e828 plus14+1 atb6cac;
141 ownership premises pass in71+70 partitions, and recursive29 passes at e6f71.
Thirteen repeated dependency bindings add no behaviors. Original overlap,
consumer-forgery and fixture failures plus the whole141 timeout stay preserved in
the [reception ledger](coverage/semantics/ordinary-throwable-reception-review.json).
Actual246 template/generic-EMIT composition1 at98c passes on ab5d; latest238/249
are preserved on e2e6 separately without renewing private gates. Complete core
remains open.

Callable default/variadic reception248 now suspends keyword/compound lookup in
actual receiving frames. Deferred class-constant defaults, named-hole preparation
and supplied/variadic operands keep their distinct order and ownership. Referenced
methods/current operands remain live, including borrowed retired arrays. Failed
lookup checks constrained sources before slow scalar fallback; lossy warnings
freeze their result and dual-role objects still invoke Stringable. Source23 normal
and one literal compiler rejection retain758/018/060 cuts; two affected221 sources
stay separate. Author116, independent180 and affected old hole35 conditions pass
on018. Actual99a composition keeps created-child default scope after a foreign
capture retires and passes AL236. Original compiler/fixture failures stay preserved;
RuntimeException Unsupported controls have zero agreement. The
[contract](docs/semantics/CALLABLE-RECEIVES.md) and
[ledger](coverage/semantics/callable-receives-review.json) retain these cutoffs.
Other internal and user-return consumers remain required; return verification
stays paused and complete core remains open.

Stringable include/require operands now convert before resolution and once
checks, retaining the receiver through rebinding and nested eval. Callback writes
determine subsequent CWD/path lookup; throw completes without file facts or a
provider nonce. Failed-open handlers resume ordered warning phases, sampling the
second message after callback1 and preserving saved owners and zero-argument
file traces. Exit, fatal and compiler-stop drops retire only their actual warning
owner; frozen output precedes shutdown callbacks. Fifteen exact source agreements
retain dcb/49/b371/dc9/4639 cuts; 81 conversion, 148 grouped warning and 45 shutdown
premises pass at their recorded revisions. SL229/231/233 stages/init also pass.
Actual f410/245 preservation retains 234 modules without renewing those gates.
[The file operand ledger](coverage/semantics/file-operand-review.json) keeps
original observer, fixture, model and timeout failures. Wider interpolation,
providers/source contexts and request lifecycle remain required.

Anonymous Closure/arrow default NEW245 resolves self/parent using the genuine
receiving lexical scope, independently of called class and receiver. Rebinding,
temporary Closure::call, imported trait makers and missing-scope errors preserve
argument order and private constructor access. Source11 passes as3+6+2 at89fe;
owner172/recursive97 pass at2d7fd, including callback retirement, same-template
saved scopes and public task/source rejection. The original object `::class`
observer remains Unsupported with zero agreement; reduced instanceof observers
retain the default behavior. Original descriptor and fixture failures stay in
the [scope ledger](coverage/semantics/anonymous-default-new-review.json).
Actual239 child composition1 at1b593 passes after temporary maker/receiver
variables retire; the child retains its receiver. Latest231/234/230/242 routes
are preserved without renewed private gates. Ordinary Throwable effects are
covered by250 above; object `::class` is covered by256 at its separate cutoff.

Writable dimension keys242 stage defined mutable CV-array W/RW fetches through
undefined/null/float/NaN callbacks, nested acquisition, updates and direct
assignment/compound consumers. Separation precedes conversion; callback-created
copies abort acquisition while real cell aliases and moved sole keepers preserve
it. Borrowed inner rows retire with their parent; aborted intermediate fetches
retain one genuine unnamed null cell. Delayed RHS CV demand follows successful
conversion. Direct GLOBALS W and named reference sends preserve selected names,
fetch/mapping priority and callable/earlier-argument owners. Throws retain the
old typed destination and previous chain. Author11 source agreements/340 reached
assertions include two independent originals; independent15 fresh agreements/266
assertions retain those two separately, giving26 unique private agreements. One
actual3b622 composition source at6ae passes private-handler/called-class and typed
caller alias/introspection behavior. Accepted231/234 routes are preserved. The
[contract](docs/semantics/SOURCE-DIMENSION-WRITES.md) and
[ledger](coverage/semantics/dimension-write-continuations-review.json) retain
original failures, revisions and the current adapter reuse. Broader GLOBALS RW
and earlier container/string/object producers remain required.

Coalesce-assignment and final unset keys249 now stage defined direct CV-array
consumers. Quiet reads retain captured values and genuine memo operands; live CV
and computed keys keep distinct later demand. Actual read/write lines, copy-induced
write abort, delayed RHS suppression and retired-storage reinitialization are
preserved. Unset keeps ordered float protection and deletes callback-shared tables
by liveness while real cells survive. Author6/255 and independent10/216 share one
multiline original, giving15 unique private agreements at cfb/ab7. Two reduced
actualab5 trait-handler sources pass at f5/ea: private selection, Child called
class, read11/write8, copied-table abort/deletion and shared typed caller cells.
Combined and first reduced coalesce CLI60 timeouts retain zero agreement. The
[contract](docs/semantics/SOURCE-DIMENSION-EDITS.md) and
[ledger](coverage/semantics/dimension-edit-review.json) keep original cuts and
native prediction corrections. Nested unset and append are covered by255 above;
wider memoized containers and other producers remain required.

Iterator declaration notices230 follow actual source/internal prototype order,
including source erasure, direct restoration, duplicate notices and the built-in
ReturnTypeWillChange suppressor. Runtime classes publish before callbacks;
early file units publish completely before ordered method/compiler warning
delivery. Real caller scope/trace stays distinct from physical diagnostic origin.
Live reporting, throwing-handler tails and method/constant fatal prefixes have
19 authored agreements; independent source11 and affected trace3 pass at their
separate cutoffs. Independent pending53/handler35/Iterator25/restored23 state
checks pass at19dae, including source-ledger authority and actual owners. Four
early-eval controls assert temporary Unsupported only; per-class eval callbacks
and publication after handler throws are the immediate required follow-on.
Actual3b622 composition source3 passes at e1a654: imported physical method
diagnostics, live argument/display state and effectful internal default traces.
The original recorder/transport failures and protocol timeouts remain preserved
without agreement credit. [Contract and tests](docs/semantics/ITERATORS.md).

Shutdown registration231 caches callable selection, private/rebound permission
and copied arguments after all argument effects. Ordered callbacks run after
normal, exit and fatal/uncaught paths, including serviced compiler failures.
Append, handled throw, exit override, weak/default/variadic reception and internal
send-warning continuations preserve selected targets and native owners. Frozen
fatal diagnostics precede the queue; effectful default message warnings finish
the builtin cache before pending exception dispatch. Exact registered and
converted argument views remain separate. Existing176 user formatters retain their
C return-warning continuation after handled throws; actual237 freezes the live
display destination after formatting. Imported trait makers preserve using scope
and physical provenance after retirement. Fatal snapshots retain runtime/compile
severity before callback mask writes; actual240 default reception retains its
warning and Stringable owners. Author checks cover 29 source tuples and 149 state
assertions; independent checks cover 77 tuples and 559 assertions. Each keeps its
recorded revision, and production stages pass on the accepted fe51 parent.
[Contract](docs/semantics/SOURCE-SHUTDOWN.md),
[author/composition record](coverage/semantics/shutdown-functions-review.json),
[independent ledger](coverage/semantics/shutdown-function-review.json).
Keyword/compound ingress now uses the staged247 consumers below. Request-stage
destructors are covered separately above; eager destruction, GC, output buffers
and queue release remain required.

Internal default reception240 now suspends weak-null and lossy integer warnings
through real error dispatch and invokes genuine Stringable callbacks in formal
order. Raw integer slots and rewritten string slots preserve internal constructor
traces, with the nearest saved owner through reentrant handlers. Exact source14
atd9 and builtin/fallback2 at7c pass; all185 reached premises at7c pass in unchanged
133+24+28 source groups under120-second caps. The original full185 timeout and
first-source interpreter overlap remain preserved. One composition source at
e7ec retains imported trait Stringable ownership and handler-mutated display
fallback after the filename global retires.
[The reception ledger](coverage/semantics/internal-default-reception-review.json)
records these cuts.
Ordinary constructor effects are covered by250; anonymous keyword defaults
are covered by245 above.

Trait method composition228 supports source use, nesting, precedence, aliases,
visibility/final and abstract requirements in Zend's publication order. Imported
class/alias identities retain physical body provenance, using/called scope,
defaults, static cells, captures, Closures, goto/eval and finalizer ownership.
Failed declarations restore unpublished tables; compile warnings and direct
trait-call deprecations retain their phases and callback ownership. The
[trait ledger](coverage/semantics/trait-methods-review.json) keeps the63 source
union, separate controls and252 conditions at their actual revisions, including
original failures. Actual227/232/239 composition adds nine source comparisons and
127 state premises at separate cutoffs: saved default constructors, cold selected
references, physical interface diagnostic files and imported-maker Closure scope.
Accepted233/237 routes remain preserved; the method checkpoint remains partial.

Trait data238 composes constants and properties before parent inheritance, with
scoped invariant types, evaluated pure compatibility, source keyword diagnostics
and full using-class member identities. Inherited statics share cells; explicit
child reuse resets the original default. Owning instance templates246 preserve
importing scope independently of the live caller and retain array copy-on-write.
The [data ledger](coverage/semantics/trait-data-review.json) records72 source tuples
and265 genuine state assertions at preserved cuts; four historical dependency
controls retain92 assertions and zero old-cut agreement. Runtime link fatals keep
native severity, reporting masks and declaration phase. Further effectful collision
evaluation, readonly storage and enums remain
required; this checkpoint does not close the trait family.

Raw trait static-property warnings254 follow lookup, access, table fill and typed
read priority. Retained source/root/member/mode resumes the live cell through
handler rebinding. Computed RHS values keep one store owner; compiled literals
also retain their pool owner. Late CV values remain delayed. Handler throws still finish
the actual write/update/reference opcode, while fetch-only reference promotion
aborts later assignment or call. Typed/Stringable conversion preserves pending
exceptions. Independent source33 (author6 subset) and six reached state groups286
pass at unchanged15155; preparation and incorrect owner assertions are retained
without extra credit in the [access ledger](coverage/semantics/trait-property-access-review.json).
Actual accepted core routes, including258, are preserved in244 modules without
renewing those cuts. Wider effectful collisions, readonly storage and enum
semantics remain required; the trait family stays open.

Trait collision recording259 compares deferred operands before typed table
conversion and records direct `E_STRICT` diagnostics during the source-owned
linking fold. Constants demand incoming then existing values; properties reverse
that order. Successful publication precedes live handler delivery; a handler throw
keeps the composed class. Later link fatals flush recorded diagnostics without
calling user handlers. The [collision ledger](coverage/semantics/trait-collisions-review.json)
retains14 source tuples (11 normal/3 PHP errors) and97 reached queue/callback
guards at their original cuts. Generic arithmetic/key recording now isolates
scratch handler/display settings and follows runtime key→value→insertion order
with checked AST lines. Five affected source comparisons (four new plus one
existing array neighbor),47 additional queue/array-owner guards and bounded
AL/structure checks pass. Private-final compile warnings now join the recorded
batch at concrete/abstract binding phases and remain handler-ineligible128. Four
affected source comparisons (two new and two128 mask neighbors) and43 genuine
alias/queue guards pass at their separate cuts. Real dependent-constant binding,
caching and endogenous expression errors remain required; traits stay partial.

Dynamic read-key continuations233 preserve selected bases/keys through missing-CV,
null/float and global-array-name callbacks. GLOBALS rereads undefined keys in the
caller environment; ordinary arrays retain their fixed converted key. Real
temporary owners and conversion protection distinguish COW, live references and
sole-table retirement; NaN keeps protection across both ordered notices. Quiet
isset/coalesce and nested temporaries keep their distinct demand/ownership paths.
Author9/246 includes the two independent NaN originals; independent14/235 passes
at its separate cut. One
actual71da constructor in a parameter default passes with private captured
handler selection, called class and authentic key line/name through root mutation.
[Contract](docs/semantics/SOURCE-DIMENSION-KEYS.md),
[ledger](coverage/semantics/dimension-key-review.json). Writable242 covers the
bounded CV-array consumers above;249 adds direct coalesce-assignment/final unset.
Nested unset, wider memoized containers, append and wider object/key/container
producers remain core work.

Prepared internal Throwable default constructors235 map completed227 values
before names, arity and sequential reception. Default declaration strictness,
finite holes and nested previous owners retain exact trace argc and ErrorException
fields. Earlier8+7/reached67 at9fa and string-slot trace2 at7fb keep their own cuts
in the [scalar ledger](coverage/semantics/internal-default-constructors-review.json);
the original count observer remains Unsupported with zero agreement.

Live `display_errors`237 retains nullable original/live INI entries and raw
get/set/Restore. Ordinary text diagnostics capture stdout/stderr/off after handler
effects, keeping their position among source output across later writes and
include retirement. Current terminal errors preserve status255 when display is
off. Ten author and one independent exact comparisons, 76 source-derived state
premises and 17 entry/transport controls pass at b8e8, alongside223-module SL
stages/init and the changed adapter build. Actualddb6/233 preservation retains
225 modules with the reviewed display and dimension-warning routes, without renewed execution.
The [display ledger](coverage/semantics/display-errors-review.json) separates
source-defined nullable controls from native profiles. The held shutdown/fatal
source matches its independent original at actual231/237 cutccd900: rendering
selects the fatal destination before queue OFF/Restore writes. This composition
has its own record; wider display, parser/profiles and request phases remain open.

Registered startup inputs225 provide original `error_reporting` and
`include_path` bytes before compilation, independently of file/CWD facts.
Getters and Restore preserve null/empty reporting, signed32 masks and raw bytes
through setters, `@` and callbacks. Restore of an unmodified reporting entry
remains a no-op even when silence leaves its live mask different from startup.
Author7 and independent2 exact profile comparisons, 99 source-derived state
premises and 15 transport controls pass at36810; that cut also passes216-module
SL stages/init and the changed adapter build. The source-equivalent actual0592
composition retains all220 parent modules plus225, with no renewed execution
credit. [Startup ledger](coverage/semantics/startup-ini-review.json).
Wider directives, startup parsing/profiles and lifecycle remain required.

Source-owned parameter default constructors227 complete lazy class tables before
allocation and evaluate every AST argument before constructor access/name mapping.
Direct/inherited dispatch preserves declaring permission, called class, default
declaration strictness and the compiled receive line. Required-reference API
warnings precede temporary wrapping; completed values and nested Stringable
receives retain genuine object/cell/frame owners. Source2/independent16 at a223,
affected cold5 at954 and reached183/affected fact2 atd441 retain separate cuts.
Actual219/222/229 composition2 at2b153 passes normal and terminal-handler paths.
Actual221 callable source1/owner39 at2a380 authenticates the suspended constructor
through deprecation callbacks and rejects a removed retained owner.
The [constructor ledger](coverage/semantics/default-constructors-review.json)
keeps original failures, the fixture line correction and fresh uncached NEW facts
precise. Anonymous keyword defaults are covered by245 and ordinary internal
constructor effects by250; complete core remains open.

Deprecated callable keyword/compound admission221 now stages supplied fixed
parameters, error registration and delayed dispatch. Warnings hold class choice
and string boundaries while rereading referenced methods; whole byref formal
replacement preserves its live value. Genuine receiving/emitting frames and a
narrow API carrier admit compound foreign-`$this` selection and declared receiver
fallback without relaxing ordinary scoped eligibility. Supplied guards exclude
authentic named default holes. Exact union branches bypass warnings; direct/FCC
raw keyword/compound calls preserve ordinary PHP lookup errors. The
[221 ledger](coverage/semantics/keyword-compound-callables-current-review.json)
records independent pins, affected checks and preserved failures. Actual include,
cold-static and GLOBALS interactions preserve real USER permission, constrained
references and captured null; initializer locations retain their declaration owner.
Default/variadic reception is covered by248 above; other internal and user-return
warning consumers remain required. Unstaged special conversion stays Unsupported.

`Closure::fromCallable`234 selects and creates durable captures over existing core
callable forms. Existing Closure inputs preserve identity; method captures freeze
live method bytes and selecting permission before raw values/makers retire.
USER admission and internal Closure getter scope remain distinct, including
foreign receiver/called-class cases. Invocation/clone retain real defaults,
source method statics and receiver ownership. Created source Closures retain
authenticated method/import scope after the parent capture retires; static
children add no receiver owner, while nonstatic children retain their bound
receiver. Imported private cold references and per-host source statics are covered.
Factory lookup-warning throws wrap only after handler/finally unwinding; argument-read throws before entry remain
unwrapped. [Contract](docs/semantics/FROM-CALLABLE.md),
[review ledger](coverage/semantics/from-callable-review.json).

Iterator224 adds compatible explicit declarations and inherited internal
obligations for source by-value foreach; callbacks use
effective runtime methods and retain the iterator/current result through key and
body. Independent source26 confirms callback order, reference results, ownership,
lexical/called scope, inherited signatures and source-interface priority at its
two recorded cutoffs. Author source5 and owner125 retain their original results.
Cursor checks enforce unique live continuation and metadata IDs below `NEXTITER`;
cursor49 and claim85 pass separately. Independent source1/reference63 and affected
fatal teardown38 pass with unchanged87d semantics; the latter corrects only a
fixture line binding. On accepted2e8, source12 passes control cleanup, arbitrary
keys, assignment priority, covariance and the remaining throwing callback stages
at284803284. Independent source1/protocol16 at the same cutoff confirms zero-argument
Stringable default reception. Earlier results and original failures remain preserved.
IteratorAggregate, ArrayAccess and remaining reference/ordinary object traversal
follow the required early-eval diagnostic work. [Scope and boundaries](docs/semantics/ITERATORS.md).

Direct missing `$GLOBALS[key]` R-fetches226 dispatch before their consumers and
retain the original null through key/global mutation. Handler throws skip later
ASSIGN/SEND, preserving typed destinations and the original exception chain.
Quiet/reference acquisitions keep their existing real cells. Genuine76 whole-table
snapshots under explicit request facts preserve numeric keys, singleton unwrap,
shared reference owners and COW after global retirement. Author8/207 and
independent8/221 pass at distinct private cutoffs. Two current derived sources
on accepted ed6 pass at bb90, retaining private first-class handlers, called class,
eager identity reads and a cold typed static alias. The combined observer retains
its inconclusive CLI60 timeout. [Contract](docs/semantics/SOURCE-GLOBAL-WARNINGS.md),
[ledger](coverage/semantics/global-warning-reads-review.json).

Exception handlers222 retain nullable raw stacks and dispatch an uncaught
Throwable after `finally` through the ordinary weak call receiver. Genuine null
caller and saved-frame certificates preserve one argument, selected targets and
owners through restoration, replacement, nested warning handling, throws and exit.
Author29/216 and independent33/331 retain their distinct source cutoffs; two
explicit Unsupported controls add no agreement at their original cut. Actual219
composition preserves
cross-file diagnostic origins during static defaults, and production algorithm
and structure checks pass. [Contract](docs/semantics/SOURCE-EXCEPTION-HANDLERS.md),
[author/composition record](coverage/semantics/exception-handlers-review.json),
[independent review](coverage/semantics/exception-handler-review.json).
Module247 supplies the effectful keyword/compound registration and terminal
selector through shared221 stages. Exception stacks retain raw values; shutdown
entries freeze the selected target after referenced-method warning effects.
Borrowed producer target/callsite/scope certificates preserve genuine ordinary,
C-handler, Stringable and Closure maker permissions after retirement.
[Author/composition checks](coverage/semantics/callback-api-consumers-review.json)
cover40 source tuples and140 reached assertions; the
[independent review](coverage/semantics/callback-api-consumer-review.json)
covers34 tuples and474 assertions at its own cut. Actual-parent getter Error,
trait/default and retired capture interactions pass; production algorithm and
structure checks retain the237-module cut. Accepted238/249/250 source preservation
adds no execution credit. Destructor/GC/output/free request phases stay open.

Called-class introspection223 implements `get_called_class()` using the active
authenticated called class. Plain functions and global Closures stop lookup;
captured/rebound source Closures retain their own class, while explicit builtin
Closure wrappers return `Closure`. Argument/count priority, optimized/generic
trace paths and real handler/emitter restoration are checked separately in the
[called-class ledger](coverage/semantics/called-class-review.json).

Deferred scalar/array static defaults219 retain the declaring scope, strict
property types, parent/constants/default order and first successful fills across
later failure/retry. Existing static rows own live values, arrays and typed aliases;
history stores no duplicate value. Eleven native/model agreements (seven normal,
four PHP errors) retain their original source cutoff. Five source-derived programs
accept 149 logical guards expressed as 152 sequential premises after narrow fixture
binding repairs. The [deferred-default ledger](coverage/semantics/deferred-static-defaults-review.json)
keeps original failures and unrun broader work visible. Two actual213/215
interactions at 8da51d193 retain inherited defaults through captured/private raw
handlers, captured-null cast/throwing assignment and a 214/216 Stringable receive.
Actual217 composition adds four normal agreements at 5c0887541, including saved
initializer contexts and compound callback traces, plus one cross-file fast-path
diagnostic agreement at 663811e8c. The unchanged owner41 guard passes. Module229
now supports same-default callback reentry: successful outer binding replaces
the live row, while escaped typed aliases retain ordered nonowning constraints.
Throw/type failure preserves the reentrant row; first-fill and table completion
remain once-only. Thirteen exact normal native/model comparisons and an inherited
67-premise ownership/history fixture pass at bf0954840. The earlier Unsupported
controls and declaration-order failure remain historical evidence; prior18/149
checks were not renewed. Cold static-reference continuations232 now keep the
captured RHS cell rooted through class-table initialization and reselect the live
target afterward. Immutable dynamic/ordinary method self/parent/static snapshots
survive callbacks and selected first-fill/retirement/table history. Seven exact
normal source agreements pass at69cc4546c;84 ownership/history premises pass at
0288de513 after narrow fixture syntax and selected work-block validator repairs.
Original failures remain separate; prior31/149/67 checks were not renewed.
Captured/rebound Closure keyword references239 now retain authentic nonowning
scope/binding evidence after pruning. Nested creation copies its immediate
creator's body, scope, receiver and nullable callsite, including error and
terminal callbacks; ordinary method ancestry stays exact. Nine new source
agreements and bound69 premises pass atd6bc09789; handler58/terminal35 pass at
860a8a19a after one fixture ordinal-binding repair. Temporary Closure::call child
creation now retains authentic source/receiver scope after maker collection;
nonstatic children keep the receiver and static children keep only nonowning
evidence. Five source agreements/global77 pass at e32dcc64a, affected callback81
at49d0b9579 after making ordinary/copied scope rules disjoint, and a fresh
same-class source/35 atadbfde09e: six sources/193 premises total. The original
validator failure is retained. Module246 now owns deferred scalar/array instance
templates by requested class and declaration, copies actual parent state at link
time, and fills constants, private-shadow instance layouts and statics before
allocation. Strict failure/retry and reentry retain once-only fill history;
objects copy template values and arrays remain owned after object collection.
Eight exact source agreements pass at80900fa4b; three programs/172 phase, copy
and ownership premises pass at449b45763 after a fixture source-origin binding
repair. Original compilation failures remain separate. Module252 extends these
templates to certified Closure/FCC values; other object/default producers and
wider consumers remain required.


Private and protected method arrays and class-method strings support callable
admission, selection, capture/clone and delayed error-handler dispatch. Object
selectors can redirect to the selecting parent's private method; concrete class
selectors use the requested class table. Protected access follows the root
prototype. Captures retain genuine selecting permission after makers retire,
while direct calls and API callbacks authenticate the real saved caller/emitter.
The current missing-CV assignment writes captured null through the referenced
caller argument after its private handler throws. Source1/94 stays separate from
the original author19/261 and independent16/345 checks.
The [scoped-callable ledger](coverage/semantics/scoped-callables-current-review.json)
keeps original failures and the three ordinary named-receive exclusions distinct.

Missing-CV reference sends retain the existing86/105 behavior: genuine null
cells, no warning and named-slot priority. Module220 rejects captured-null
ASSIGN through live typed aliases, retaining their value and replacing a handler
throw with a caller TypeError whose previous chain owns the original error.
At484d, author9/211 and independent5/249 pass; the latter corrects two fixture
phase assumptions without replaying passing models. The actual3919 composition
accepts one reduced scoped-handler source at5bce: TypeError context, typed caller
alias and the handler chain survive private selection and retired global owners.
The original observer-heavy source retains its inconclusive CLI60 timeout. The
[consumer ledger](coverage/semantics/warning-consumers-review.json) preserves
original failures and distinct revisions.

Warning-read consumers213 retain original null for six casts, selected copies and
ordinary by-value sends across handler mutation. Selected callees and prior arrays
keep their real owners; named-slot errors precede warnings. Direct ASSIGN writes
null even after a handler throws, before the same exception continues. Its
original rejected constrained-write control is addressed by private220 above.
Mixed author21 normal tuples/control0 and
58/60/65/53=236, plus independent10/197, retain their actual revisions and original
failures. Fresh actual6395 composition at181f separately accepts source1/94 and
independent cached-callee source1/96, covering static-reference sends, the real
outer-array prepass redirect and cached target/handler retention. Source-equivalent
publication preserves subsequent reporting, parameter backing and named-class
changes. [Consumer ledger](coverage/semantics/warning-consumers-review.json).

Fixed and variadic Stringable receives preserve receive order, captured cells,
caller strictness and backing authority; constructor-free defaults retain declaring
scope and fresh objects. Named constexpr `::class` retains source spelling and
authentic deferred/rebound lexical scope. Counts and original failures remain in
[parameter](coverage/semantics/weak-string-parameters-review.json),
[variadic/default](coverage/semantics/variadic-default-string-review.json) and
[constant](coverage/semantics/class-constants-current-review.json) ledgers and the
family table below. Internal and anonymous keyword constructor defaults retain
their235/240/245 cuts; broader attribute/modifier and callable initializer consumers
remain required.

Nonstatic private/protected `__invoke` supports bare calls, callable admission,
object capture/clone and bare-object error handlers through the effective runtime
method table. Explicit method calls keep lexical visibility. Compilation checks
parameters/body before the static fatal or nonpublic warning; inheritance access
errors retain preceding warnings. The [publication ledger](coverage/semantics/invoke-publication-current-review.json)
separates the original source/compiler/runtime checks from the current strict USER
truth-warning interaction, failures and unchanged return-classification boundary.

Method-array and class-method-string error handlers register raw values and
select afresh at dispatch. Entered targets retain genuine emitter scope, arguments
and owners through member mutation, nested replacement, throw and false fallback.
The [method-handler ledger](coverage/semantics/handler-callables-current-review.json)
keeps mixed author/independent checks, current CONFIG PIPE and original failures
at their actual revisions.

Diagnostic ingress217 dispatches runtime `E_STRICT` and lossy reporting
conversions through authentic handler continuations. Selected values survive
callback declarations; integer conversion precedes dispatch and the setter reads
the old mask afterward. Saved initializer facts and busy class scopes retain
normal/throw cleanup and expression/fetch exception locations. Fourteen author
and four independent sources plus 211 conditions keep their actual revisions.
Current 210 compilation and one scoped private-handler/Stringable-backing/lexical
class-name source comparison establish added composition separately. The
[diagnostic ledger](coverage/semantics/reporting-diagnostics-review.json) retains
original failures and cutoffs. The separate
[eval-location increment](coverage/semantics/compound-eval-location-review.json)
retains genuine filename owner/root/child through compound class, method/Closure
and static-property callbacks, with real eval call sites and lexical scopes.
Compiler exceptions use their failed unit; ordinary runtime exceptions keep the
execution override. Five original agreements/81 controls retain their distinct
cuts. One current inherited static-default/private-handler source plus214 compiler
stages at2c0c validate that composition and the static-fill compiler-prefix bridge.

The installed families compose as follows; each ledger records its scope and limits.

| Family | Current behavior and evidence |
| --- | --- |
| Class constants183/184/212 | Lazy scalar/array and selected Closure/FCC caches preserve strict types, inheritance priority and compile-entry availability. Named constexpr `::class` and rebound lexical defaults preserve source spelling/scope. Catalogue of 93 and 159 + 44 + 63 callable/class-name guards retain separate cutoffs; broader consumers remain open. [Constants ledger](coverage/semantics/class-constants-current-review.json). |
| Warning-truth decisions209 | Branch/loop/short-circuit/NOT/ternary-condition choices consume the captured null even after handlers define the CV. Saved consumers and thrown-handler cleanup retain authenticated source/line. Later cast/copy/SEND checks are recorded separately below. [Truth ledger](coverage/semantics/warning-truth-review.json). |
| Warning-read consumers213 | Six casts, selected ternary/coalesce copies and ordinary by-value sends preserve captured null, aliases and selected targets through callbacks. Direct ASSIGN retains its null write through throw. Mixed21/control0+236 and independent10/197 remain separate from fresh static-reference/outer-array source1/94 and cached-callee source1/96 at181f. [Consumer ledger](coverage/semantics/warning-consumers-review.json). |
| Borrowed warning reads208 | Strict identity retains the old reference cell across callbacks without adding an owner; saved callers and throw cleanup preserve it. Defined ordinary `$GLOBALS[key]` uses the real table. Getter/setter and method-string interactions keep separate revisions. [Warning-read ledger](coverage/semantics/warning-reads-review.json). |
| Error handlers/reporting206/207/211 | Raw registrations and selected targets retain four arguments and genuine emitting frames through mutation, replacement, nested reentry, throw and false fallback. Reporting get/set/Restore separates full raw bytes, signed32 masks and modified-entry state across suppression and handler writes; twelve normal sources across two revisions and 74 conditions are accepted. Fifteen nondeprecated error constants resolve exactly. Diagnostic ingress217 adds runtime `E_STRICT` and handled lossy reporting conversions with distinct 14+4/211 evidence and current source1. Broader handler forms and producer coverage remain open. [Diagnostics](coverage/semantics/reporting-diagnostics-review.json). [Reporting](coverage/semantics/reporting-ini-review.json), [method handlers](coverage/semantics/handler-callables-current-review.json), [earlier handlers](coverage/semantics/error-handlers-review.json). |
| Exception handlers222 | Raw nullable set/get/restore stacks and null-caller uncaught dispatch reuse ordinary calls with one authentic Throwable. Selected snapshots survive registry removal; weak receive, by-reference warning resume, nested restoration/replacement, throws, exit and fatal masks preserve ownership and termination. Author29/216 and independent33/331 pass at recorded cutoffs; actual219 source1 and production algorithm/structure gates pass. [Exception contract](docs/semantics/SOURCE-EXCEPTION-HANDLERS.md). |
| Class-method strings210 and FCC119 | Full-byte lookup separates frame-based callable admission, computed static dispatch and fixed compatible-this selection. Captures/clone retain immutable source certificates and defaults/static cells. A named throwing handler preserves the selected static caller and arguments. [String ledger](coverage/semantics/class-method-strings-current-review.json). |
| Method arrays205 | Public source method arrays retain immutable selected receiver/owner/called-class certificates through dynamic calls and capture. Current two-slot INI checkpoint **f9f47f115/61370c98/1353** accepts source1/finite103; broader resolution remains open. [Array ledger](coverage/semantics/array-callables-current-review.json). |
| Include/configuration | Failed CHDIR warnings retain provider certificates and caller frames through handler CWD/raw writes, false fallback and throw. One current throwing source/136 conditions, earlier three sources and compiler25 checks keep separate revisions. Stringable CHDIR PIPE retains post-callback CWD/held operands; unary CONFIG PIPE preserves source strictness through borrowed warnings. [PIPE ledger](coverage/semantics/include-config-pipe-review.json). Raw getters, primitive/null Restore, weak-null handler continuations and two-slot INI ownership retain their separate checkpoints. [Readback](coverage/semantics/include-ini-readback-review.json), [INI](coverage/semantics/include-stringable-ini-option-review.json). |
| Stringable SET/Restore and paths | SET separates raw INI bytes from effective C-string paths. Weak Restore uses exact full-name lookup and preserves callback mutations on misses. Current ARG/Restore checks retain caller arguments and zero-argument callbacks. [Restore](coverage/semantics/include-stringable-restore-review.json), [prefix](coverage/semantics/include-ini-prefix-review.json), [SET](coverage/semantics/include-set-current-review.json). |
| Typed static properties197 | Weak simple Stringable assignment rechecks live aliases and retains paired callback owners. Current Restore/ARG/INI composition preserves full property bytes, caller arguments and normal/throw cleanup. [Property ledger](coverage/semantics/typed-static-string-assignment-review.json). |
| Weak string parameters214/216/218 | Fixed and positional/named variadic receives preserve caller strictness, nominal/callable precedence and captured cells; existing constraints reject before callbacks. Newly attached sources permit only the parameter-authorized backing value. Constructor-free defaults use genuine scratch cells, declaring method scope and fresh objects. Source6/state299/independent2 and variadic/default6+6/focused4/independent3/state336 retain separate cutoffs. [Parameter ledger](coverage/semantics/weak-string-parameters-review.json), [variadic/default ledger](coverage/semantics/variadic-default-string-review.json). |
| Static setters200/201 | Backed final/asymmetric declarations normalize equivalent setters and preserve inheritance/error priority; direct and indirect consumers retain lexical access, live raw-slot checks and typed aliases. [Setter ledger](coverage/semantics/static-setter-access-review.json). |
| StaticCall reference acquisition141/142 | Getters with untyped return signatures retain scoped selection, typed and legal untyped static aliases and returned-cell cleanup. Typed REF flags preserve initialization/error priority even when discarded. Direct reference sends retain the real cell; ignored untyped getters leave raw values unchanged. Ownership/type-source and getter/borrowed-read checks keep their distinct revisions. [Reference ledger](coverage/semantics/static-method-reference-review.json). |
| Argument introspection198/199 | Ordinary current and saved frames retain genuine named/unpacked argument views through invocation and callbacks. [Argument ledger](coverage/semantics/argument-introspection-calls-current-review.json). |
| Object invocation and callable typing | Effective nonstatic `__invoke` lookup includes private/protected methods, retaining declaring owner, called class and receiver across argument effects and clone. Explicit access remains lexical. Callable-before-string parameters preserve dual-role objects; shared ordinary by-value return classification adds no fresh return agreement. [Publication](coverage/semantics/invoke-publication-current-review.json), [earlier invocation](coverage/semantics/source-invoke-current-review.json), [parameter reception](coverage/semantics/callable-string-current-review.json). |
| Selection and capture | Source method selection preserves owner/called class; capture/clone retains selected targets and scoped defaults/static cells without retaining retired origin-only creators. [Capture](coverage/semantics/method-capture-current-review.json), [default caches](coverage/semantics/closure-default-cache-review.json). |
| Compiler publication190–196 | Ordered class/function availability, early diagnostics and authenticated declaration history compose with calls and callbacks. Compile-stop freezes saved callers and retires active file replies; it does not perform ordinary unwind. [Publication ledger](coverage/semantics/compiler-publication-review.json). |

Executables and compiler inputs are reused; source-equivalent publication adds
no rebuild or fresh execution credit. Earlier selector, capture, invocation and
baseline milestones remain in [MILESTONE-HISTORY.md](MILESTONE-HISTORY.md) and the
linked ledgers. [Cleanup](coverage/semantics/error-origin-author.json) and
[migration](coverage/semantics/throwable-migration-review.json) retain deferred
failures and interrupted evidence.

## Remaining core work

- Calls: other internal and user-return
  keyword/compound warning consumers,
  magic/autoload/internal consumers, dynamic compile-warning handler delivery,
  transformed wrappers and broader CONFIG PIPE consumers. Only the selected captured-static
  array and string Closure PIPE routes are covered. Direct defined/missing
  `$GLOBALS[key]` reads and explicit-request full-table snapshots are admitted;
  233 additionally stages earlier missing key-CV and null/float/global-array-name
  conversions through nested/quiet reads. Writable242 adds bounded CV-array W/RW
  and direct GLOBALS reference fetches;249 adds direct CV-array coalesce-assignment
  and final unset;255 adds nested unset and append, and262 adds nested coalesce
  assignment on defined CV-rooted arrays.
  Wider memoized containers, broader GLOBALS RW, wider key/object/container
  producers and ordinary snapshots without request facts remain open.
- Include/configuration: wider initializer/callback/compile-warning consumers,
  wider startup directives/parsing/profiles,
  other warning producers, OS services and lifecycle. The
  [include contract](docs/semantics/INCLUDE-SOURCES.md) separates these consumers.
- Values, references and coercion: dynamic object `::class`, dynamic hole provenance and broader weak
  parameter/property conversion, constrained-reference object conversion, wider nonstatic delayed receivers and
  broader reference-result consumers. Other object-bearing default producers and
  wider Closure creation contexts remain Unsupported.
  Uncertified object transfers, unretained update selectors, builtin FCC targets and
  wider callable initializers remain Unsupported; modifiers/attributes stay open.
  Wider deprecated constant consumers remain open. Generic156 return replay, temporary-return
  Notice timing and typed
  by-reference string conversion186 remain open; accepted ordinary by-value
  classification does not close them. [String contract](docs/semantics/USER-STRING.md),
  [finally contract](docs/semantics/SOURCE-FINALLY.md).
- Objects and lifetime: remaining static members, effectful trait data composition,
  enums, hooks, readonly/instance asymmetric
  access, traversal, output handlers and lifecycle callbacks. Static cells remain
  partial across wider producers, bind/clone, include/eval reactivation
  and GC. [Method](docs/semantics/SOURCE-METHODS.md),
  [static-property](docs/semantics/SOURCE-CLASS-STATICS.md) contracts.
- Control and diagnostics: Generator/Fiber, remaining warning/read producers,
  broader API/callable argument consumers and remaining request phases.
  Broader constant consumers and compiler reporting interactions remain open.
  Called-class introspection223 leaves builtin Closure rebinding, builtin API
  callback targets, suspension and wider reference-result consumers open.

`returns_verify` is temporarily paused by the user. Preserve its branches and
evidence; do not retry the blocked engine experiment, substitute a reviewer,
merge changes awaiting its validation, or begin work depending on those
unaccepted changes. Independent work proceeds from the accepted baseline.

Rocq interaction-tree semantics and BOLA proofs follow completed PHP core.

## Validated baseline

The post-arrow checkpoint is **1026/0ec57507**, with arrow capture and returns
117/118 at **87cdc532f**. Its [review](coverage/semantics/post-arrow-integration-review.json)
binds these distinct profiles and independent audits:

| Gate | Accepted observations |
| --- | --- |
| Compiler | 5,751 source lints, 8 access sources, 15 line observations; existing binary reused |
| Explicit request | 263 source profiles, 526 responses with exact request/environment facts |
| Callable | 946 maintained rows in 18 suites plus one regression; 1,894 responses |
| Ordinary | 5,706 source comparisons (4,060 normal, 1,006 PHP errors, 640 static rejections), 21 separate controls; 11,435 process records |

These are observations, not unique PHP programs or current full-core coverage.
Ordinary, request and callable profiles have different environment contracts;
their counts are not interchangeable.

## Validation and integration limits

Configuration permits eight pairs/16 agents; the numerical/model concurrency
cap remains five until explicit resource coordination, with coordinated slot
handoffs. Record the tested revision, compiler/runtime identity, relevant inputs,
environment, exact commands/exits and raw originals. Independent review focuses
on semantic counterexamples and reliable completion; investigate failures
narrowly and repeat only affected checks. Metadata adds no execution credit.

Interrupted runs, timeouts, Unsupported and budget controls are never native
agreements. Paused-state fixtures complement original-source comparisons; passing
subsets do not establish equivalence or full core. Final combined current-source
gates and a fresh copied-path, network-isolated offline rebuild remain required.
