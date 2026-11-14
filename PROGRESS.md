# Core PHP semantics progress

This project targets PHP 8.5.10 CLI, NTS, 64-bit. Executable core semantics and
source-driven differential validation are active; complete PHP core, the later
Rocq interaction-tree model and BOLA/CRIS verification remain unfinished.
[PLAN](PLAN.md) records settled scope; the [feature inventory](coverage/semantics/features.json)
and current family documents identify implemented routes and remaining obligations.

## Current checkpoint

Quiet emitted BOOL/INT/FLOAT casts retain NORMAL/source/CODEfalse/read-eps/equal precision, recursively typed inputs, signed64 integer bounds and exact full-state cast_apply. FLOAT-to-INT separately proves empty notices even under suppressed reporting; fitting fractional casts truncate quietly and FLOAT BYTE stays eps. Native4 once/source4, authorSL944/129-derived and inclusive independentSL1792/977-derived with33 explicit derived controls retain separate cuts. Actual65bda8fcb and its sole canonical SL508 load15.738608s/source0 pass; wider producers/owners/lifetimes and all exact holds remain partial. [Runtime primitive-cast review](coverage/semantics/string-offset-request-base-runtime-scalar-cast-review.json).

Completed ordinary-CV producers also admit required canonical standalone false and true formals together. Each accepts only its exact Boolean tag under either caller mode. Ordinary BYREF formals impose no persistent alias constraint; existing return/frame/private-cell and owner bounds remain. Five native originals ran once: three fresh Notice agreements and two distinct weak integer RECEIVE-priority controls. Separate author444/peer296 fixture-SL507 cuts and the sole actual c3fc20b8 production-SL508 load (16.332990513183177 seconds, cap60, source0) retain their own identities. Wider nullable/union literal-Boolean forms and returns remain partial; all exact holds remain. [Literal-Boolean formal review](coverage/semantics/cv-literal-bool-formal-producer-reference-notice-review.json).

Selected mask8194 handlers also admit own raw canonical binary64 FLOAT returns through 16 lowercase hexadecimal digits, exact child/CODE/line and compiled-bit authority. Four finite/subnormal/+0/+INF originals preserve AH/AHH, real formal retirement and FINAL MOD-zero Error without default diagnostics. Malformed payloads refuse before decoding; local -0/NaN projections stay source0. Actual `a7826ca029`/508 loading passes separately (15.987692816s/cap60/source0); UnaryMinus, named/computed returns and wider handlers, operands, histories, lifetimes and OB31 remain partial. [FLOAT-return review](coverage/semantics/output-final-selected-float-return-modulo-error-review.json).

BooleanNot directly accepts certified nonzero signed64 integer trees, including ADD/SUBTRACT/MULTIPLY roots without an outer sign. The general certificate subsumes the old raw-Integer spelling with pointwise equivalent source/range/pool guards; nonzero/NOTfalse, parentEPS/fallback2 and ownership bounds remain. Native2 once/source2, genuine A92/B91 prelaw full155, separate author339/201 and peer484/321 fixtures, the specifically affected raw-Integer187/76 fixture/source0 and actual MAIN6e0fc4b397 joined SL508 loading pass. Constructed raw MIN controls earn no source credit; other operators, wider producers/lifetimes and held lanes remain partial. [Review](coverage/semantics/string-offset-boolean-not-integer-arithmetic-shorthand-base-initial-raw-leading-key-review.json).

Own public static USER method Get values on a child of a genuine empty global source parent now cross quiet CV ??, private ??= and literal/CV Empty, including authenticated Shared clones. Exact raw empty-parent/link and own child-scope authority retain existing cache and cleanup guards. Four native-once agreements and separate fixture-SL145/146/421/361 plus affected parentless292 pass; three fixture preparation failures and four prelaw Unsupported cuts retain0. Sole actual902d/SL508 canonical loading adds source0. Wider ancestry and exact holds remain. [Review](coverage/semantics/magic-property-methodclosure-static-empty-parent-quiet-get-review.json).

Shared-cache clones and finite clone chains of the fixed global own public static USER method capture now cross quiet CV ??, private ??= and literal/CV Empty. Descending raw ancestry and immutable owner/cache stamps authenticate retired sources; absent historical scope rows are expected. Original Shared birth and current source/live/consumer fences remain. Four new native-once source agreements and separate new/affected-old fixtures pass; earlier Unsupported and preparation failures retain zero credit. No policy or exact held-boundary changes. [Review](coverage/semantics/magic-property-methodclosure-static-clone-quiet-get-review.json).

Direct NName and NNameFullyQualified static-method capture labels now match their genuine global class names case-insensitively through quiet CV ??, private ??= and literal/CV Empty, including authenticated Shared clones. Raw own-method/source/CODE.NAMES/scope/cache/birth and existing cleanup fences stay exact. Four native-once source agreements and separate fixture-SL129/130/292/232 plus affected-old231 pass; four prelaw Unsupported cuts retain0. Sole joined726/SL508 loading adds source0. Wider forms and exact holds remain. [Review](coverage/semantics/magic-property-methodclosure-static-named-selector-quiet-get-review.json).

Original direct global public static USER method captures now cross quiet CV ??, private ??= and literal/CV Empty through exact own-method/source/scope/cache/birth authority. Shared method statics survive wrapper retirement. Four native-once source agreements and separate lifetime/source-counterfeit fixtures pass; wider METHOD producers, wrappers and lifetimes remain partial. No policy or exact held-boundary changes. [Review](coverage/semantics/magic-property-methodclosure-static-quiet-get-review.json).

Shared-cache clones of raw named USER FCC Get results now cross quiet CV ??,
private ??= and literal/CV Empty. A strictly descending same-origin raw ancestry
certificate extends the unchanged explicit original guard. Current cache fields
are checked separately after two executed private-cache counterfacts; all four
new source comparisons pass at the final guard using native originals once.
Separate new and affected-old fixtures retain zero source credit. Earlier source
positives, counterfact failures and Unsupported baselines keep their own cuts.
No cache/free/GC policy or exact held boundary changes.
[Review](coverage/semantics/magic-property-namedclosure-clone-quiet-get-review.json).

Original unscoped named user-function FCC Get results now cross quiet CV ??,
private ??= and literal/CV Empty. Exact source/callable/cache authority keeps
wrapped, bound and private-cache named results outside; the literal
Empty gate authenticates the actual result ID. Four changed-source agreements
reuse native originals once. Separate fixtures check result/receiver retirement,
shared function-static roots, receiver throw and budget rejoining; four prelaw
Unsupported baselines and the fixture binding failure retain zero credit.
No free/cache/GC policy or exact held boundary changes.
[Review](coverage/semantics/magic-property-namedclosure-quiet-get-review.json).

Four pinned float startup primitives now have exact integer/binary64 values.
Global/FQN/import reads, namespace shadow/fallback, boundary arithmetic and typed
defaults pass four original-source comparisons. Separate compiler and peer
model controls, fixture failures and the sole combined db42/e703 SL508 load are
recorded in the [review](coverage/semantics/startup-float-constants-review.json).
Other startup values and complete core remain unfinished.

Pinned release components PHP_MAJOR_VERSION, PHP_MINOR_VERSION, PHP_RELEASE_VERSION
and PHP_VERSION_ID also supply integers 8, 5, 10 and 80510 through ordinary
fold/import/fallback, typed defaults and runtime queries. Other startup values
remain partial.
[Version-constant review](coverage/semantics/startup-version-constants-review.json).

PHP_ZTS and PHP_DEBUG are Boolean false for the pinned nondebug NTS build.
Other build variants, startup values and complete core remain partial.
[Boolean startup review](coverage/semantics/startup-bool-constants-review.json).

Eight registered UPLOAD_ERR constants supply pinned integers 0, 1, 2, 3, 4, 6,
7 and 8 through existing constant consumers. These are fixed startup facts;
other startup values and complete core remain partial.
[Upload-error constant review](coverage/semantics/startup-upload-constants-review.json).

DEBUG_BACKTRACE_PROVIDE_OBJECT/IGNORE_ARGS supply integer flags 1/2;
ZEND_THREAD_SAFE/ZEND_DEBUG_BUILD are Boolean false for the pinned nondebug NTS
build. Trace/debug APIs, other startup values and complete core remain partial.
[Zend startup review](coverage/semantics/startup-zend-constants-review.json).

PHP_VERSION and PHP_EXTRA_VERSION supply the fixed strings "8.5.10" and "" through
existing fold/import/fallback, runtime queries and repeated defaults. Actual
source reads retain INTERNED identity and the existing compiler-pool trust boundary;
other startup values and complete core remain partial.
[Release-string review](coverage/semantics/startup-release-string-constants-review.json).

Recent integrated behavior includes the checked setter-header presence repair,
implicit untyped class/trait block and short setters, and public parentless
untyped backed GET/SET pairs with block or short bodies in either source order,
implicit or actual required untyped SET parameters, and initialized or omitted
defaults.
Untyped backed GET/SET pairs also import from one raw direct trait into a
parentless class or one with a genuine ordinary source parent whose complete
layout is plain and lacks the hook name. Repeated direct uses may resolve to
that same single fetched exporter, including lexical namespace aliases.
On this trait route, a short GET may omit backing access when its block SET
supplies the backing. Untyped direct trait pairs also admit automatic short-SET backing when neither
hook accesses the property directly. Block or short GET retain exact raw/imported
source, RHS/CODE/line and Param authority.
[Automatic short-SET trait review](coverage/semantics/deprecated-reference-object-untyped-automatic-short-set-trait-pair-review.json).
Exact raw/imported origins, no exporter uses or
adaptations, first matching NAME row and actual Param/body/source-parent
authority remain required; wider traits, nonpublic/modifier/virtual/byref pairs
and lifetimes remain partial.
[SET-backed trait-pair review](coverage/semantics/deprecated-reference-object-untyped-set-backed-trait-pair-review.json).
Own public parentless untyped class pairs also admit a short GET without
backing access when a genuine block SET supplies backing, with implicit or
required actual untyped parameters. Raw Hook/Param/source/CODE/line, physical
DIRECT storage and owner/cleanup bounds remain; wider class/trait/modifier/virtual/
byref forms stay partial.
[SET-backed class-pair review](coverage/semantics/deprecated-reference-object-untyped-set-backed-class-pair-review.json).
Own public parentless untyped pairs also admit automatic short-SET backing
with block or short GET even when neither hook uses the property directly.
Implicit and required actual untyped SET parameters keep their source/header/Param
authority. Existing DIRECT storage and cleanup remain. At that cut, parented own
classes, wider owners/modifiers/signatures, virtual/byref pairs and lifetimes
remained partial.
[Automatic short-SET class-pair review](coverage/semantics/deprecated-reference-object-untyped-automatic-short-set-class-pair-review.json).

Own public untyped backed GET/SET pairs also accept a genuine ordinary source
parent whose complete plain layout lacks the hook name. Canonical headers,
SOURCE_PARENT and raw Hook/Param/CODE/line authority retain own declaration
identity and existing physical storage and cleanup. Wider inheritance remains
partial.
[Parented own class-pair review](coverage/semantics/deprecated-reference-object-untyped-parented-class-pair-review.json).

Own public untyped backed pairs also override same-name ordinary public fields
on a genuine parentless source parent without traits. Canonical headers,
SOURCE_PARENT and raw own Hook/Param/body/CODE/line authority remain. Physical
storage keeps the already-backed child in declaration order and drops the old
parent live slot; metadata order stays unchanged. Wider and sole-virtual/typed/
byref allocation contexts remain partial.
[Same-name parent class-pair review](coverage/semantics/deprecated-reference-object-untyped-same-name-parent-class-pair-review.json).

Own public untyped sole BYVAL GET hooks over a same-name ordinary root parent retain distinct physical allocation: omitted-default getters without same-field THIS access receive backing after existing child slots; body-backed block/short getters retain their lexical child slot. Four saved-native agreements per slice and separate source-zero ownership/budget fixtures cover defaults, declaration identity and cleanup; wider ancestry/types/BYREF and lifetimes remain partial. [Appended-slot review](coverage/semantics/ordinary-parent-unbacked-get-child-slot-review.json), [existing-slot review](coverage/semantics/ordinary-parent-backed-get-child-slot-review.json).

Own public untyped backed block &get hooks also retain their lexical child slot over a same-name ordinary root parent. Actual returned references, unconstrained aliases and real ALIAS-cell edges survive to physical cleanup without reusing the old parent slot. [Block reference-Get slot review](coverage/semantics/ordinary-parent-backed-reference-get-child-slot-review.json). Typed, parented and wider short reference Get producers, ordinary This-reference-fetch consumers and wider lifetimes remain partial.

Parentless public untyped sole short `&get => $this->sameField` now uses genuine Hook/BODY and compiled expression/arrow lines. Alias/copy identity, physical child/cell retirement and exact zero/one-step return/fetch/cleanup resumptions pass; expression fetches stay distinct from implicit-null/Notice fallthrough. Four originals reuse native once, with author 189/189 and independent 305/305 fixture-SL cuts kept separate. The actual 14242d240 SL508 canonical load passes in 15.587678412906826s with source credit 0. Wider typed/parented/Trait/SET bodies, consumers and lifetimes remain partial. [Short-reference Get review](coverage/semantics/parentless-short-reference-get-hook-review.json).

Same-field short reference getters also accept literal-string field spellings, including an escaped-name witness. Four new originals reuse native once; author189/189 and independent340/340 fixture-SL cuts retain separate identities, malformed-name/body refusals and exact resumptions. Actual006fba302 and joined3196/SL508 canonical15.330673544202s add source0; wider parent/type/consumer/lifetime modes remain partial.

Own public untyped sole short reference Get hooks retain their lexical child slot over a same-name ordinary public untyped field on a genuine trait-free root source parent. Raw canonical extends/SOURCE_PARENT and actual Hook/BODY/CODE/line authority preserve child defaults and existing ownership/cleanup guards. Four source agreements use native originals once; author212/212 and peer387/373/373 per form retain separate fixture cuts, with original failures/timeouts/unrun cases at zero credit. Actual `97f6f17d6`/SL508 loading passes separately (16.088962591s/source0). Wider parents, types, consumers and lifetimes remain partial. [Parented short-reference Get review](coverage/semantics/ordinary-parent-short-reference-get-hook-review.json).

Existing DIRECT storage and cleanup remain. Live array/object Get results, selected
canonical-int, Boolean, FLOAT, string and NULL quiet Get returns, nullable scalar
and scalar-union quiet headers and supported unselected typed Get companions.
Canonical mixed joins the existing scalar, NULL, nullable scalar, scalar-union
and void/never quiet Get headers, retaining raw source proof, exact values and
receiver ownership. Literal-name Empty results preserve payload-before-receiver cleanup.
Selected quiet __get() calls accept canonical array and object return
headers, and authenticated CV-name empty() sites admit live arrays and
ordinary objects using the existing truth cache and cleanup phases. Saved
names, separate value and receiver owners, destructor replacement and
resumption remain intact. Authenticated CV-name binary ?? also transfers live
arrays and ordinary object getter results through receiver retirement without
changing their values. Saved names and separate result/receiver owners survive
rebinding, COW, exceptions and resumption.
Private CV-name ??= now accepts bounded live array/object Get results through exact source/target proof and the existing receiver/value handoff; missing-property ??= remains Unsupported. Other internal CV object kinds and wider producers or lifetimes remain partial.
[Owning coalesce-assignment Get review](coverage/semantics/magic-property-owning-quiet-coalesce-assignment-get-review.json).
Authenticated enum-case Get values now cross quiet CV coalesce and literal/CV Empty through the existing singleton-cache and separate receiver/value ownership rules.
[Enum quiet Get review](coverage/semantics/magic-property-enum-quiet-get-review.json).
Bounded raw empty/singleton WeakMap Get results cross quiet CV binary ??,
private ??= and Empty with separate map/value/receiver owners and existing key
notification.
[WeakMap quiet Get review](coverage/semantics/magic-property-weakmap-quiet-get-review.json).
[Owning quiet Get review](coverage/semantics/magic-property-owning-quiet-empty-get-review.json).
[Owning coalesce Get review](coverage/semantics/magic-property-owning-quiet-coalesce-get-review.json).
Normalized branches retain complete raw method/source authority and existing
strictness/owner guards.
NaN Empty retains its Isset guard through Warning, including
authenticated literal or string-CV same-name terminal Isset, preserving
different-name calls. Reference-send Notices admit quiet
`stdClass` REQUEST DIRECT fields with
authenticated non-NUL strings, bounded ordinary scalar ALIAS fields and live
finite object-free DIRECT/ALIAS array-field graphs, preserving real cells and edges,
COW, detach order and cleanup. Finite acyclic quiet `stdClass` object paths admit
DIRECT and ordinary ALIAS fields, retaining shared siblings, real cell edges and path-local cycle checks;
finite fields may alternate object and array paths with separate ancestor stacks
and ordinary nested cells. Typed property-sourced descendants within object paths
and wider source/backing/GC/lifetime contexts remain partial.
Completed producer calls without a return declaration also admit multiple literal
CV arguments with fixed required untyped formals.
Completed producers with multiple literal ordinary CV actuals and fixed
required untyped formals admit canonical array/int/float/bool/string return
declarations. Raw/normalized return proof and actual verification retain the
existing scalar, authenticated non-NUL INTERNED/REQUEST-string and finite
array/quiet stdClass payload bounds; frame retirement precedes private
Notice-cell creation, and the last compiled CV supplies its line.
Completed producers with multiple literal ordinary CV actuals and fixed
required untyped formals admit raw ?array with exact[array,null], ordered
array|null/null|array matched pointwise, and canonical
?int/?float/?bool/?string with exact[scalar,null]. Actual return verification
uses callee strictness and producer-frame retirement precedes private Notice
cells; existing snapshot/current-reference/COW and authenticated
payload/source/backing/history/GC bounds remain, while wider unions, typed
multi formals and broader contexts remain partial; Owned-NUL remains held.
[Multi-CV nullable review](coverage/semantics/multi-cv-nullable-array-return-producer-reference-notice-review.json),
[ordered-union review](coverage/semantics/multi-cv-union-array-return-producer-reference-notice-review.json),
[Nullable scalar review](coverage/semantics/multi-cv-nullable-scalar-return-producer-reference-notice-review.json).

Completed producers with multiple literal ordinary CV actuals and fixed
required untyped formals also admit explicit scalar|null and null|scalar, where
scalar is canonical int/float/bool/string and exactly two distinct raw members
match normalized types in source order. Existing callee-strict verification and
producer-frame retirement precede private Notice cells; snapshots/current prior
references/COW retain existing payload/source/backing/history/GC bounds, while
wider unions and other typed multi formals remain partial; Owned-NUL remains held.
[Scalar-union producer review](coverage/semantics/multi-cv-union-scalar-return-producer-reference-notice-review.json).
Completed producers with multiple literal ordinary CV actuals admit matching
fixed required untyped, array or canonical int/float/bool/string formals through
pointwise raw identifiers, normalized types and BYREF proof. Reception uses caller
strictness: BYVAL coercion preserves caller values, while ordinary BYREF coercion
changes the shared cell without a persistent parameter constraint. Existing return,
frame-retirement, last compiled-CV-line and payload/source/backing/ownership/GC
guards remain; wider union formals, defaults/variadics/attributes and wider
lifetimes remain partial; Owned-NUL remains held.
[ARRAY-formal review](coverage/semantics/multi-cv-array-formal-producer-reference-notice-review.json),
[scalar-formal review](coverage/semantics/multi-cv-scalar-formal-producer-reference-notice-review.json).

Completed multiple-CV producers also admit matching fixed required nullable array/int/float/bool/string formals, preserving pointwise raw/normalized/BYREF proof and caller-strict reception. Existing return/frame/ownership bounds remain. [Nullable-formal review](coverage/semantics/multi-cv-nullable-formal-producer-reference-notice-review.json).

Completed singleton producers with one literal ordinary CV also admit matching
fixed required canonical scalar or nullable array/scalar formals, preserving
raw/normalized/BYREF proof, caller-strict reception and existing return/frame/
ownership bounds.
[Singleton formal review](coverage/semantics/singleton-cv-typed-formal-producer-reference-notice-review.json).

Singleton producers also admit canonical nullable scalar and ordered scalar|null/
null|scalar return declarations. Callee-strict verification and producer-frame
retirement precede private Notice cells; existing formal/source/payload/ownership
bounds remain.
[Singleton nullable-return review](coverage/semantics/singleton-cv-nullable-scalar-return-producer-reference-notice-review.json).

Completed singleton and multi-CV producers also admit ordered array/int/float/bool/string with null formal unions, preserving pointwise raw/normalized/BYREF proof, caller-strict reception and existing return/frame/ownership bounds. [Union-null formal review](coverage/semantics/cv-union-null-formal-producer-reference-notice-review.json).

Completed singleton and multi-CV producers also admit ordered two-member formal unions of distinct array/int/float/bool/string/null kinds, preserving pointwise raw/normalized/BYREF proof, caller-strict reception and existing return/frame/ownership bounds. [Distinct builtin union-formal review](coverage/semantics/cv-distinct-builtin-union-formal-producer-reference-notice-review.json).

Completed singleton and multi-CV producers admit ordered distinct formal unions over array/int/float/bool/string/null. A finite raw/normalized member fold rejects duplicates and mismatches, preserving caller-strict reception and existing return/frame/ownership bounds. [Primitive union-formal review](coverage/semantics/cv-primitive-union-formal-producer-reference-notice-review.json).

Completed singleton and multi-CV producers admit distinct nonnull two-member array/int/float/bool/string return unions. Callee-strict return verification precedes frame retirement/private Notice cells, retaining ordinary alias/snapshot/COW ownership bounds. [Distinct nonnull return-union review](coverage/semantics/cv-distinct-builtin-union-return-producer-reference-notice-review.json).

Completed singleton and multi-CV producers admit three to six distinct ordered array/int/float/bool/string/null return members. Raw/normalized authentication preserves callee-strict verification before frame retirement and private Notice cells, with existing alias/snapshot/COW bounds. [Primitive return-union review](coverage/semantics/cv-primitive-union-return-producer-reference-notice-review.json).

Completed singleton and multi-CV producers admit canonical standalone null return declarations. Return checking accepts only NULL even in weak mode; producer retirement precedes the fresh untyped private Notice cell, retaining existing alias and cleanup bounds. [Null return review](coverage/semantics/cv-null-return-producer-reference-notice-review.json).

REF67 admits standalone raw mixed/normalized[mixed] returns through the existing completed ordinary-CV producer proof. Three new Notice source agreements and a separate prelaw strict RECEIVE-priority control use four native originals once; author390 and peer200 fixture-SL507 conditions keep separate source-zero cuts. The sole actual canonical load is recorded in the mixed-return review. The current old39 exact-mixed header expectation changes without renewing historical evidence; wider contexts and all held lanes remain partial.

REF68 extends the pointwise ordinary-CV argument proof to required canonical mixed formals with exact raw/normalized/reference-mode authority. Four new Notice source agreements use four native originals once; author427 and peer296 fixture-SL507 cuts stay separate from the sole actual canonical load. Two current matching formal-header expectations change without renewing historical evidence. Wider formals/contexts and all exact holds remain partial.

REF69 admits required canonical standalone null formals through the existing pointwise argument proof, with return/frame/payload/ownership rules unchanged. Four native originals ran once; three new Notice agreements and one separate fresh weak BYREF REQUEST RECEIVE-priority agreement pass. Author fixture-SL507416 (296 reached, 120 derived) and peer fixture-SL507217 (188 reached, 29 derived) retain separate source0 cuts, as do genuine prelaw188/140 and original Unsupported2. Actual MAIN 4c1cc93c has the sole 508-module SL load at 15.837800811976194 seconds, cap60, quiet/stable/reaped/source0; report main48-null-formal-producer-joined-508-v1 SHA5274b143dc9eb679accd1625f27f47452b374b826e8d2044ea610822052803b6. The combined controller is UNEXECUTED. All held lanes and complete-core partial status remain. [Null-formal review](coverage/semantics/cv-null-formal-producer-reference-notice-review.json).

Exact CONCAT certificates now cover signed64 integer bitwise operations,
modulo with a nonzero divisor, shifts with nonnegative counts, quiet
integer-result powers, equality/spaceship and all four logical short-circuit forms.
Logical XOR and those short-circuit certificates also admit quiet valid binary64
non-NaN FLOAT children through actual source/read/precision facts and existing
truth conversion; decisive branches leave the RHS unexecuted. Unary FLOAT NOT
remains unfolded.

Quiet runtime FLOAT NOT keys now authenticate actual nonconstant CODE/read-eps facts, genuine folded FLOAT values, quiet truth and real CONCAT bytes/carriers. Saved index, current owners, supplied Throwable and fixed-bounds cleanup retain existing laws; warningful NaN truth and wider producers/owners remain partial. Source4, author645 and inclusive peer1029 fixture-source-zero cuts remain separate. [Runtime FLOAT-NOT review](coverage/semantics/string-offset-request-base-float-boolnot-runtime-review.json). Quiet runtime double/triple NOT also retains genuine typed PFLOAT/PBOOL links through actual emitted source/CODE/read-eps, equal precision and full-state truth. [Nested FLOAT-NOT review](coverage/semantics/string-offset-request-base-nested-float-boolnot-runtime-review.json).

Quiet runtime unary +/- preserves fitting integer bytes from typed Boolean and integer results; existing NOT can consume the resulting integer. Exact emitted source, code and precision facts, quiet NINT conversion and full-state results retain the real REQUEST key and existing owners. Four source agreements reuse native originals once; authorSL731 and inclusive peerSL1231 remain separate from the sole fce0c4887 SL508 load (16.187261943006888s/source0). NaN warnings, wider producers/owners/lifetimes and complete core remain unfinished. [Runtime integer-sign review](coverage/semantics/string-offset-request-base-runtime-unary-integer-review.json).

Quiet emitted ADD/SUB/MUL and PINT-only BITNOT retain actual source/CODE/read-eps/equal precision, quiet fitting NINT inputs and exact whole-state PINT results/decimal bytes. Native4 once/source4, authorSL932/129derived and inclusive peerSL1660/857derived (=932+728, including42 checked-source compiler conditions) remain separate in string-offset-request-base-runtime-integer-operator-review.json. The v1 fixture expectation failure and unrun3 retain0; actual5889f080 has ONE canonical SL508 load16.2823896210175s/source0. Runtime FLOAT bytes, wider operators/producers/owners/lifetimes and complete core remain unfinished. [Runtime integer-operator review](coverage/semantics/string-offset-request-base-runtime-integer-operator-review.json).

Quiet emitted division retains exact integer bytes from genuinely typed Boolean/integer children, quiet fitting inputs, pure exact-integer division and unchanged full-state results. Source, code, read and captured precision facts preserve the existing Warning histories; zero divisors and floating results remain outside this runtime certificate. Native4 once/source4 retain their agreement identity; authorSL1124/129-derived and independent corrected fixtureSL1685/690-derived keep separate source-zero cuts; v1 notation failure/unrun3 retain0. Actual14002 has one combinedSL508 load15.739573478000239s/source0; wider producers/owners/lifetimes remain partial. [Runtime integer-division review](coverage/semantics/string-offset-request-base-runtime-integer-division-review.json).

Quiet emitted ===/!== retain exact typed Boolean/integer/float operands, pure strict results and unchanged full-state evaluation through actual source, code, reads and captured precision. Equal bytes or truth do not erase types; wider leaves, NaN truth and runtime FLOAT producers remain partial. Native4 once/source4 retain their agreement identity; authorSL1055/129-derived and independent fixtureSL1679/753-derived remain separate source-zero cuts. Actualf1c9 has one combinedSL508 load15.580887952819467s/source0; wider producers/owners/lifetimes remain partial. [Runtime identity review](coverage/semantics/string-offset-request-base-runtime-identity-review.json).

Quiet emitted ==/!= preserve PHP's Boolean truth and numeric comparison for recursively certified Boolean/integer/float operands. Exact source, code, read and precision facts plus pure comparison and full-state checks retain existing keys and Warning cleanup. Four saved native originals and four source agreements retain their evidence; author SL1091/129-derived and independent fixture SL1764/802-derived retain separate source-zero cuts. The combined SL508 load at e1245c8cc passed in 15.287736607016996s with source credit 0. Wider leaves, runtime FLOAT producers, ownership and lifetimes remain partial. [Runtime equality review](coverage/semantics/string-offset-request-base-runtime-equality-review.json).

Quiet emitted <, <=, >, >= and <=> preserve PHP truth/numeric order and greater-operand reversal through exact typed operands, source, code, reads, captured precision and full-state checks. Four saved native originals and four source agreements retain separate evidence; author fixture SL1089/129-derived and independent SL1897/937-derived (=1089+808 controls) carry source credit 0. The combined SL508 load at f8cd56221 passed in 15.990203514927998s with source credit 0. Wider leaves, runtime FLOAT producers, ownership and lifetimes remain partial. [Runtime order review](coverage/semantics/string-offset-request-base-runtime-order-review.json).

Quiet emitted XOR preserves recursive PFLOAT/PBOOL/PINT truth through actual NORMAL/source/CODE/read/precision facts, sequential full-state conversions and unchanged binary_apply. Genuine Boolean results retain existing keys and cleanup. Native4 once/source4, author fixture SL1074/129-derived and independent SL1932/987-derived remain separate from actual57633f6f7 SL508 load15.387549259932712s/source0. The first fixture failure/unrun3 retains0; wider producers, NaN truth, owners and lifetimes remain partial. [Runtime XOR review](coverage/semantics/string-offset-request-base-runtime-xor-review.json).

Quiet emitted &&/and/||/or retains actual NORMAL/source/CODE/read/precision and recursive typed truth. A decisive left skips RHS value/precision; selected right conversions retain exact full-state results. All four spellings preserve existing keys, Warning owners and cleanup; wider producers, NaN truth and lifetimes remain partial. Native4 once/source4, author fixture SL1040/129-derived and corrected independent SL2336/1425-derived retain distinct cuts from actualec251/c57d SL508 load16.183977286797017s/source0. The original peer fixture failure and unrun3 retain0. [Runtime AND/OR review](coverage/semantics/string-offset-request-base-runtime-short-review.json).

Quiet emitted FLOAT arithmetic supplies exact nonNaN VALUE through existing typed truth/identity/comparison consumers while BYTE remains eps. Native4 once/source4, authorSL1196/129-derived, inclusive independentSL2782/1715-derived and narrow affected-logicalSL34 retain separate identities. Whole8 source/test integration0024679cf and the sole composed7266312e1 SL508 load16.382309734s/source0 pass; earlier Unsupported4 remain0. Wider producers/owners/lifetimes and all exact holds remain partial. [Runtime FLOAT arithmetic review](coverage/semantics/string-offset-request-base-runtime-float-arithmetic-review.json).

Quiet emitted unary +/- supplies genuine nonNaN FLOAT VALUE, including nested signs, with BYTE eps. Four final source agreements retain2+1+1 pointwise cuts and six native originals once; both earlier adapter90 timeouts/recorder failures and missed final-assertion limits remain0. AuthorSL1143/129-derived and inclusive peerSL1950/936-derived, including24 controls and source-zero MIN overflow, remain separate. Actual79c161bda and its sole canonical SL508 load16.642128s/source0 pass. Wider producers/owners/lifetimes and all exact holds remain partial. [Runtime FLOAT unary review](coverage/semantics/string-offset-request-base-runtime-float-unary-review.json).

Quiet runtime modulo, bitwise AND/OR/XOR and shifts retain exact integer bytes from recursively certified PINT children. Matching emitted source, code, read and precision facts, IRESULT and full-state checks preserve the existing key and ownership rules; wider types, operators, producers and lifetimes remain partial. [Strict integer-binary review](coverage/semantics/string-offset-request-base-runtime-integer-binary-review.json).

Typed numeric comparisons include FLOAT operands and canonical
NaN ConstFetch values through actual child/source/read/precision facts. NaN enters VALUE without
minting a string-byte certificate; old non-NaN rules retain their own cuts.
Raw PSTRING byte NOT/AND/OR/XOR and seven raw-string comparison forms also retain
exact own/child byte, source, read and precision certificates. Comparisons reuse
existing numeric-versus-lexicographic string order and overflow provenance.
Ordered signed64/non-NaN binary64 numbers also compare with raw PSTRING children
in either orientation at captured compile precision, retaining actual source/read,
byte certificates and three matching precisions. Wider mixed forms remain partial.
Comparisons with at least one Boolean or NULL child also admit quiet ordered
numeric, exact raw-string or Boolean/NULL partners under the same actual
source/read/recursive-byte and precision facts.
NaN ConstFetch values also compare with raw PSTRING, Boolean or NULL partners in
either orientation, retaining actual source/read/partner-byte/precision facts
and both scalar-order directions. NaN itself has no string-byte certificate.
Runtime-carrier and owning mixed forms stay partial.
Strict NaN ===/!== CONCAT certificates retain genuine per-occurrence VALUE,
exact scalar types and actual source/read/precision facts. Even equal NaN bits
are nonidentical; no NaN BYTE certificate is minted. Wider producers,
carriers/owning values and lifetimes remain partial.
Quiet nonNaN FLOAT ConstFetch leaves retain actual source/read facts and exact
BYTE at captured precision. Existing INF values compose through unary,
arithmetic and comparison certificates; no startup values, raw PSTRING
provider or NaN BYTE certificate is added. Wider producers, ownership and
lifetimes remain partial.
Quiet ADD/SUBTRACT/MULTIPLY/DIVIDE results can supply genuine arithmetic NaN
VALUE through actual source/read/precision facts, ordered nonNaN numeric child
BYTE and exact quiet arithmetic.
Quiet unary `+`/`-` of genuine NaN children retains actual own/child source
and reads, matching capture precision and exact quiet result bits, without
NaN BYTE. Four immediate-sign originals agree with native observations reused
once; finite nested signs have compiler-fixture evidence only. NaN BYTE, FLOAT NOT and wider producers/ownership/lifetimes remain separate.
[Unary NaN review](coverage/semantics/string-offset-request-base-unary-nan-special-concat-leading-key-review.json).
Quiet ADD/SUBTRACT/MULTIPLY/DIVIDE with genuine NaN numeric children retains
actual own/child source/read facts, three matching capture precisions, quiet
coercions and exact result bits. Ordered child VALUE retains BYTE; NaN
children/results retain BYTE EPS. At that NaN-child cut, quiet BOOL/NULL/raw
numeric-string children, NaN BYTE, FLOAT NOT and wider producers/ownership/
lifetimes remained separate.
[NaN-child arithmetic review](coverage/semantics/string-offset-request-base-nan-child-arithmetic-special-concat-leading-key-review.json).

Quiet ADD/SUBTRACT/MULTIPLY/DIVIDE NaN VALUE also admits genuine BOOL/NULL/raw
numeric-string children through scalar identity VALUE, quiet coercions and exact
own/child source/read/precision facts. Four original agreements reuse native
observations once; author887/105-derived, independent fixture1275/493-derived,
corrected compiler1031/52, affected pool127/60 and compiler42/14/42 retain separate
source-zero cuts. The source startup failure, original compiler static failure
and false full-report aggregate remain explicit. MAIN `e32d48dbb` is integrated;
its composed `8892a1510` production-SL508 load passes in15.588865828s/source0.
NaN BYTE, FLOAT NOT, wider producers/owners/lifetimes and held lanes remain partial.
[Quiet coercive NaN review](coverage/semantics/string-offset-request-base-coercive-arithmetic-nan-special-concat-leading-key-review.json).
Evaluated operands retain actual source, read, type/range and
precision facts; decisive logical branches leave the RHS unexecuted. Callback
string reads distinguish a rebound plain key CV from the live payload of its
captured initial reference wrapper, including aliases created during callbacks,
under the closed 21-field provider frontier. Selected normal callback retargets
also admit quiet Boolean, NULL and fitting FLOAT values, choosing a distinct
ordinary current scalar cell or the live old-wrapper payload according to
captured KEYREF under that same frontier. Plain compiled key CVs also admit
supported same-slot text or an absent current name after the cast Warning. Missing
UNDEF converts silently to zero without creating storage, under captured KEYREFfalse
and the existing source/heap/owner proof. An initial reference key reads its live
wrapper independently of the current name or value, retaining full heap validity
and the existing old-cell source, owner and provider proofs.
Admitted late non-NUL INTERNED or authenticated REQUEST key text converts silently
after the CAST Warning, preserving raw storage and offset bounds. REQUEST uses
its exact selected header owned by the current ordinary unmarked compiled CV or
live initial reference wrapper, retaining the full heap, source, static-CV,
backing, liveness, closed21 and provider ownership proofs.
Closed normal selected-callback CAST reads also follow a captured plain CV’s
actual marked current cell for valid non-NUL INTERNED or authenticated REQUEST
text, including same-slot and retargeted wrappers. Text converts silently
after Warning. These marked-current reads retain source/static-CV, nonblocked
lookup, backing/released, full heap, closed21, callback/provider ownership and
offset-range proofs. REQUEST additionally authenticates its exact selected
header and real cell owner. Captured initial-reference reads keep their live
old-wrapper proof independently of the current name/value. Selected raw/NUL
payloads and wider histories remain partial.
Normal selected-callback CAST reads silently convert valid non-NUL raw
PSTRING bytes from the actual current ordinary or valid marked cell when
captured KEYREFfalse, or from the saved live marked KEYCELL when KEYREFtrue,
even after current-name replacement/removal. Existing
source/static-CV/full-heap/pruned-liveness/released/backing/constraint/exact-callback-owner/range/closed21
proofs remain. These marked-current and initial-reference routes retain the
existing callback owner; initial raw-key acquisition, selected NUL and wider
histories remain outside this admission.
[Ordinary raw review](coverage/semantics/string-offset-request-callback-ordinary-raw-key-review.json),
[marked raw review](coverage/semantics/string-offset-request-callback-raw-message-key-review.json),
[Initial-reference raw review](coverage/semantics/string-offset-request-callback-reference-raw-key-review.json).

Ordinary current raw Warning-message keys also complete CAST after selected
callback-owner loss when the unchanged provider authenticates the exact REQUEST
base in its original cell or an admitted real ENV retainer. Initial KEYREFfalse,
current ordinary-cell, source/full-heap/non-NUL/in-range and closed21 bounds remain.
At that ordinary-current cut, marked current keys and captured-reference keys
still required the callback owner. Two original agreements reuse native observations once; author
SL182 and peer SL212 remain separate source0 cuts, with four fixture failures0.
Initial raw, selected NUL, zero-owner raw release, abrupt and wider histories
remain partial.
[Live-cell owner review](coverage/semantics/string-offset-request-callback-raw-key-cell-owner-review.json).

Valid marked-current raw keys with captured KEYREFfalse now share the
provider-backed owner-loss route, retaining pruned-cell, released/backing,
source/full-heap and closed21 proofs.
[Marked live-cell review](coverage/semantics/string-offset-request-callback-marked-raw-key-cell-owner-review.json).
Captured initial-reference KEYREFtrue raw keys also complete normal CAST after
selected callback-owner loss when the unchanged provider authenticates the exact
REQUEST base in its original cell or a real ENV keeper. Selection stays at the
saved live marked KEYCELL despite current-name replacement or removal;
source/full-heap/pruned-cell/released/backing/non-NUL/in-range/closed21 proofs remain.
Two originals agree with native observations captured once; author188/99 and
independent245/133 fixture-SL cuts stay separate/source0. Initial raw acquisition,
zero-owner raw release, selected NUL, abrupt and wider histories remain partial.
[Initial-reference live-cell review](coverage/semantics/string-offset-request-callback-reference-raw-key-cell-owner-review.json).
Literal non-NUL INTERNED bases also admit valid late raw PSTRING keys after
a normal selected CAST callback. Captured KEYREFfalse follows the actual ordinary
or valid marked current key cell; KEYREFtrue follows the saved live marked KEYCELL
independently of current-name replacement or removal. Known literal-base/source/
provider, full heap, pruned-cell/released/backing/non-NUL/range and closed21 proofs
remain. Other initial raw acquisition, key NUL, INTERNED CV bases, zero-owner
REQUEST raw release, abrupt and wider histories remain partial.
[Literal-base raw-key review](coverage/semantics/string-offset-literal-callback-raw-key-review.json).
Initial valid non-NUL raw CV keys classified as leading integers also retain
their selected index through normal Warnings on authenticated literal INTERNED
bases. Ordinary and initial-reference histories preserve frozen bytes/index
through key rebinding or cell retirement; actual compiled base-source proof
excludes generic compiled-EPS producer authority. Two saved-native source
agreements and separate A168/78 and B174/74 fixture-SL/source0 cuts remain
distinct; runtime/REQUEST bases, NUL and wider contexts stay partial.
[Initial raw leading-key review](coverage/semantics/string-offset-initial-raw-leading-key-review.json).
Ordinary initialized INTERNED base CVs also preserve their selected non-NUL
header and initial raw leading-integer key index through normal Warning callbacks.
Base replacement and key-reference rebinding leave the selected byte unchanged;
later removal of either borrowed cell adds no owner. Two saved-native source
agreements and separate author162/59-derived and independent167/52-derived
fixture-SL/source0 cuts cover this bounded extension. Other base producers,
REQUEST/NUL, abrupt and wider histories remain partial.
[CV-base raw-leading review](coverage/semantics/string-offset-variable-base-initial-raw-leading-key-review.json).

Genuine initial-reference INTERNED base CVs now share that raw leading-key
acquisition. A returning Warning can mutate the shared base or rebind both
current names while the captured header/index still returns the original byte.
Two saved-native source agreements and separate author162/54-derived and
independent170/40-derived fixture-SL cuts retain their own identities; bounded
extraction checks only the promoted ordinary-source controls. Other base
producers, REQUEST/NUL, abrupt and wider histories remain partial.
[Reference-base raw-leading review](coverage/semantics/string-offset-reference-base-initial-raw-leading-key-review.json).

Quiet full ternaries with literal Boolean conditions and raw string arms now
preserve the selected non-NUL INTERNED base and initial raw leading-integer
offset through returning Warning handlers. Both arms and the condition retain
exact source/compiled proofs; plain and initial-reference key rebinding returns
the frozen byte. Two saved-native agreements and separate A205/104-derived and
B175/55-derived fixture-SL/source0 cuts remain distinct. Other producers,
REQUEST/NUL and abrupt/wider histories remain partial.
[Conditional-base raw-leading review](coverage/semantics/string-offset-conditional-base-initial-raw-leading-key-review.json).

Raw string-literal shorthand ternaries also preserve their truth-selected non-NUL
INTERNED base and initial raw leading-integer index through returning Warning
handlers. Exact condition/fallback source, compiled reads and string identities
distinguish a truthy condition from false "0" fallback. Wider producers,
REQUEST/NUL ingress, abrupt paths and lifetimes remain partial.
[Shorthand-base review](coverage/semantics/string-offset-shorthand-base-initial-raw-leading-key-review.json).

Quiet full ternaries with raw string conditions also retain their selected
non-NUL INTERNED header and frozen leading index through returning Warning
handlers, authenticating the condition and both literal arms. Source2 and
A162/B188 fixture-source-zero cuts remain separate; wider conditions/producers,
REQUEST/NUL ingress, abrupt paths and lifetimes remain partial.
[String-condition base review](coverage/semantics/string-offset-string-conditional-base-initial-raw-leading-key-review.json).

Literal string/null coalesce bases also retain the selected non-NUL INTERNED
header and frozen leading index through returning Warning handlers. Exact raw
source, child reads and string/null identities preserve nullness selection;
wider producers, REQUEST/NUL ingress, abrupt paths and lifetimes remain partial.
[Coalesce-base review](coverage/semantics/string-offset-coalesce-base-initial-raw-leading-key-review.json).

Literal integer full ternaries also retain the selected non-NUL INTERNED header and frozen leading index through returning Warning handlers, including initial-reference key rebinding. Exact condition and both arm pools authenticate selection; source2 and A161/B188 fixture-source-zero cuts remain separate. Wider producers, REQUEST/NUL ingress, abrupt paths and lifetimes remain partial. [Integer-condition review](coverage/semantics/string-offset-integer-conditional-base-initial-raw-leading-key-review.json).

Finite raw float full ternaries also retain the selected non-NUL INTERNED header and frozen leading index through returning Warning handlers. Exact raw condition bits, finite decode and both arm pools authenticate selection; source2 and A180/B201 fixture-source-zero cuts remain separate. Nonfinite/unary/computed conditions, REQUEST/NUL ingress, abrupt paths and lifetimes remain partial. [Float-condition review](coverage/semantics/string-offset-float-conditional-base-initial-raw-leading-key-review.json).

Literal NULL full ternaries retain the selected non-NUL INTERNED fallback header and initial raw leading-integer index through returning Warning handlers. Exact simple-name null/PNULL, both raw arm pools and parent-EPS source facts preserve the frozen byte through ordinary or initial-reference key rebinding. Saved-native source2, separate author174/70 and peer201/77 fixture-SL/source0, and canonical MAIN8c719050 SL508 loading retain distinct evidence; wider producers, selected NUL/REQUEST bases, abrupt paths and all existing holds remain partial. [NULL-condition review](coverage/semantics/string-offset-null-conditional-base-initial-raw-leading-key-review.json).

Literal NULL shorthand bases retain their non-NUL INTERNED fallback header and initial raw leading-integer index through returning Warning handlers, including ordinary key replacement and initial-reference rebinding. Exact simple-name null/PNULL, ABSENT true arm, raw fallback2/INTERNED identity and parent-EPS source facts remain required. Saved-native source2 and separate author169/65 and peer198/75 fixture-SL/source0 cuts pass; actual MAIN596521e has one canonical SL508 load16.191108686849475s/source0. Wider scalar conditions/producers, selected NUL/REQUEST bases, abrupt paths and existing holds remain partial. [NULL-shorthand review](coverage/semantics/string-offset-null-shorthand-base-initial-raw-leading-key-review.json).

Literal false shorthand bases retain their non-NUL INTERNED fallback header and initial raw leading-integer index through returning Warning handlers, including ordinary key replacement and initial-reference rebinding. Exact simple-name false/PBOOLfalse, ABSENT true arm, raw fallback2/INTERNED identity and parent-EPS source facts remain required. Saved-native source2 and separate author169/65 and peer201/78 fixture-SL/source0 cuts pass; actual MAINa9c32f0d has one canonical SL508 load15.73283217404969s/source0. Wider scalar conditions/producers, selected NUL/REQUEST bases, abrupt paths and existing holds remain partial. [FALSE-shorthand review](coverage/semantics/string-offset-false-shorthand-base-initial-raw-leading-key-review.json).

Literal integer-zero shorthand bases retain their non-NUL INTERNED fallback header and initial raw leading-integer index through returning Warning handlers, including ordinary key replacement and initial-reference rebinding. Exact raw INTEGER0/compiledPINT0, ABSENT true arm, raw fallback2/INTERNED identity and parent-EPS source facts remain required. Saved-native source2 and separate author168/65 and peer199/78 fixture-SL/source0 cuts pass; actual MAINe98f35c5 has one combined integer/binary SL508 load15.932173192035407s/source0. Wider conditions/producers, selected NUL/REQUEST bases, abrupt paths and existing holds remain partial. [Integer-zero shorthand review](coverage/semantics/string-offset-integer-zero-shorthand-base-initial-raw-leading-key-review.json).

Literal positive-zero float shorthand bases retain their non-NUL INTERNED fallback header and initial raw leading-integer index through returning Warning handlers, including ordinary key replacement and initial-reference rebinding. Exact raw FLOAT bits0/compiledPFLOAT0, ABSENT true arm, raw fallback2/INTERNED identity and parent-EPS source facts remain required. Saved-native source2 and separate author169/65 and peer215/93 fixture-SL/source0 cuts pass; actual MAIN14002d6ef has one combined SL508 load15.739573478000239s/source0. Negative/computed/nonfinite conditions, wider producers, selected NUL/REQUEST bases, abrupt paths and existing holds remain partial. [Positive-zero FLOAT shorthand review](coverage/semantics/string-offset-float-zero-shorthand-base-initial-raw-leading-key-review.json).

Actual unary-minus float-zero shorthand bases retain their non-NUL INTERNED fallback header and initial raw leading-integer index through returning Warning handlers, including ordinary key replacement and initial-reference rebinding. Exact UnaryMinus/raw-positive-zero leaf source, compiled unaryPFLOAT2^63/leafPFLOAT0, ABSENT true arm, raw fallback2/INTERNED identity and parent-EPS facts remain required. Saved-native source2 and separate author183/76 and peer239/114 fixture-SL/source0 cuts pass; actual MAIN1e86e3dc1 has one combined SL508 load16.03118209494278s/source0. Wider conditions/producers, direct raw negative-zero or nonfinite scalars, selected NUL/REQUEST bases, abrupt paths and existing holds remain partial. [Unary-minus FLOAT-zero shorthand review](coverage/semantics/string-offset-negative-zero-shorthand-base-initial-raw-leading-key-review.json).

Actual unary-plus float-zero shorthand bases retain their non-NUL INTERNED fallback header and initial raw leading-integer index through returning Warning handlers, including ordinary key replacement and initial-reference rebinding. Exact UnaryPlus/raw-positive-zero leaf source, compiled unaryPFLOAT0/leafPFLOAT0, ABSENT true arm, raw fallback2/INTERNED identity and parent-EPS facts remain required. Saved-native source2 and separate author183/76 and peer248/123 fixture-SL/source0 cuts pass; actual MAIN9d2af7d6e has one combined SL508 load16.392686638981104s/source0. Wider conditions/producers, direct raw negative-zero or nonfinite scalars, selected NUL/REQUEST bases, abrupt paths and existing holds remain partial. [Unary-plus FLOAT-zero shorthand review](coverage/semantics/string-offset-unary-plus-zero-shorthand-base-initial-raw-leading-key-review.json).

BooleanNot of simple-name literal true preserves the raw shorthand fallback's non-NUL INTERNED header and frozen leading offset through returning Warnings, including current-key replacement and initial-reference rebinding. Exact parent/condition/leaf source, false/true pools, fallback2 identity and parentEPS remain required. Saved-native source2, separate author184/76 and peer286/156 fixture-SL/source0 cuts, and actual MAIN3973 SL508 load16.283693879842758s/source0 pass. Wider operands, producers and lifetimes remain partial; existing holds stay unchanged. [BooleanNot true shorthand review](coverage/semantics/string-offset-boolean-not-true-shorthand-base-initial-raw-leading-key-review.json).

BooleanNot of raw nonzero signed64 integer literals preserves the non-NUL INTERNED shorthand fallback and frozen leading offset through returning Warnings, including key replacement and initial-reference rebinding. Exact parent/condition/leaf/fallback source, range/nonzero, ownfalse/leafPINTi pools and parentEPS remain required. Saved-native source2, separate author187/76 and peer345/214 fixture-SL/source0 cuts, and actual MAINb181 SL508 load16.090435076970607s/source0 pass. Raw MININT local-law fixtures earn0 source credit; unary-signed source syntax and wider operands/lifetimes remain partial, with all holds unchanged. [BooleanNot integer shorthand review](coverage/semantics/string-offset-boolean-not-integer-shorthand-base-initial-raw-leading-key-review.json).

BooleanNot of finite +/- chains over raw integer literals preserves the non-NUL INTERNED shorthand fallback and frozen leading offset through returning Warnings, including key replacement and initial-reference rebinding. Exact source/child occurrences, signed64 PINT at every node, quiet full-state signs, final nonzero/ownNOTfalse and parentEPS/fallback2 remain required. Saved-native source2, separate author272/144 and peer425/277 fixture-SL/source0 cuts, and actual MAINf2c joined SL508 load16.382158543914557s/source0 pass. Raw MININT local fixtures earn0 source credit; FLOAT overflow, wider operands/lifetimes and all holds remain unchanged. [BooleanNot integer-unary shorthand review](coverage/semantics/string-offset-boolean-not-integer-unary-shorthand-base-initial-raw-leading-key-review.json).

BooleanNot of quiet integer-result +/- chains rooted in raw numeric strings now preserves the non-NUL INTERNED shorthand fallback and frozen leading offset through returning Warnings, including ordinary key replacement and initial-reference rebinding. Actual child/source, raw PSTRING and INTERNED authority, exact quiet NINT input and PINT at every sign retain final nonzero/NOTfalse, parentEPS and fallback2 guards. Saved-native source2, separate author373/239 and peer335/199 fixture-SL/source0, affected INTEGER272/144 and actual MAIN726 joined SL508 loading pass. FLOAT classification/overflow, wider producers/lifetimes and all holds remain unchanged.

BooleanNot of finite integer-result +/- chains rooted in raw simple-name true preserves the non-NUL INTERNED shorthand fallback and frozen leading offset through returning Warnings, including ordinary key replacement and initial-reference rebinding. Exact ConstFetch and indexed NName, case folding, PBOOL true leaf pool, signed64 PINT signs and quiet full-state results retain the final nonzero value, false NOT pool, absent parent pool and fallback identity. Saved-native source2, separate author352/218 and peer383/242 fixture-SL/source0 cuts and actual MAINf755 joined SL508 loading pass. Other name/leaf forms, wider producers/lifetimes and all holds remain unchanged. [Literal-true unary-chain review](coverage/semantics/string-offset-boolean-not-true-unary-shorthand-base-initial-raw-leading-key-review.json).

BooleanNot of truthy raw string literals preserves the non-NUL INTERNED shorthand fallback and frozen leading offset through returning Warnings, including key replacement and initial-reference rebinding. Exact parent/condition/leaf/fallback source, decoded truth, ownfalse/leafPSTRING+INTERNED pools and parentEPS remain required. All decoded byte strings except empty and exactly ASCII zero qualify, including a pooled NUL condition without owned release. Saved-native source2, separate author225/112 and corrected peer339/204 fixture-SL/source0 cuts, and actual MAINc694 SL508 load15.990419904934242s/source0 pass. The first peer binding failure and unrun state retain0. Wider operands/lifetimes remain partial and all holds stay unchanged. [BooleanNot string shorthand review](coverage/semantics/string-offset-boolean-not-string-shorthand-base-initial-raw-leading-key-review.json).


Integer-default reception includes guarded integer casts and truth of computed FLOAT
trees, plus typed selected FLOAT leaves and explicit FLOAT casts inside numeric
trees. Certified byte-string, special Boolean/null and quiet Boolean-predicate
leaves retain actual declaration-ENV and stored-PINT guards on that cast route.
Typed NINT/NFLOAT comparisons preserve numeric tags for identity and reversed
operands for greater relations, retaining the same actual default/ENV/PINT and
ownership authority.
Ordinary named exact-int defaults under weak caller typing retain actual
source/declaration ENV and Shared-cache authority. Exact case-sensitive resolved
PHP_INT_MAX/MIN/SIZE and PHP_FLOAT_DIG supply deferred PINT values;
PHP_FLOAT_EPSILON/MAX/MIN retain their fixed finite PFLOAT bits. Imported aliases
and FQN references retain these typed values; arithmetic and casts follow the
existing rules. Quiet in-range Numeric NINT truth permits
zero/nonzero, CASTBOOL, NOT and lazy logical conditions through proper selected
descent. Selected Numeric NINT leaves also preserve their integer values through
full/shorthand ternary and null-left coalesce descent, including existing arithmetic
parents and later TypeErrors for nonfitting results.
Literal-Boolean full ternaries also admit compiler-pruned skipped names through
exact condition pools and a unique proper selected-child redirect; condition/selected
bindings and whole-tree source/ENV/no-DIM/cache authority remain.

Quiet computed Boolean conditions also authenticate those pruned full ternaries
through the existing pure condition rule and exact matching raw PBOOL pool;
recursive condition/selected bindings and unique proper-child redirects remain
required.
[Computed Boolean ternary default review](coverage/semantics/computed-boolean-ternary-default-reception-review.json).

Decisive OR/AND conditions also authenticate only their proper left child through
pure truth and matching own/left raw Boolean pools, preserving complete
source/no-DIM/ENV/Shared-cache authority and existing outer ternary redirects.
[Lazy Boolean condition default review](coverage/semantics/lazy-boolean-condition-default-reception-review.json).
[Platform-number default review](coverage/semantics/float-platform-default-reception-review.json).

Quiet Numeric-only signed64 integers retain identity through explicit int casts
and nonnull-left coalesce, including zero. Exact raw source/declaration ENV,
no-DIM/name bindings and Shared-cache/receive/owner guards remain; wider
producers, pruned syntax, private/Generator contexts and lifetimes remain partial.
[Numeric integer-cast default review](coverage/semantics/numeric-integer-cast-default-reception-review.json).

Resolved case-sensitive PHP_MAJOR_VERSION, PHP_MINOR_VERSION,
PHP_RELEASE_VERSION and PHP_VERSION_ID also supply deferred integers 8/5/10/80510
through existing arithmetic/casts/selection and named warning reentry. Exact
source/declaration ENV, no-DIM/name/cache/receive/owner guards remain; wider
producers, pruned syntax, entries and lifetimes stay partial.
[Version integer-default review](coverage/semantics/version-integer-default-reception-review.json).

Registered nondeprecated E_* constants also supply deferred integer defaults, including E_ALL=30719, through existing arithmetic/casts/selection and named warning reentry. Exact source/declaration ENV, no-DIM/name/Shared-cache/receive/owner guards remain; E_STRICT, wider producers, entries and lifetimes stay partial. [Diagnostic integer-default review](coverage/semantics/diagnostic-integer-default-reception-review.json).

Numeric-only signed64 AND/OR/XOR/NOT now compose deferred integer defaults, including cold/warm BYREF caches, named holes, warning reentry, MIN/MAX and nonnull zero. Exact source/ENV/no-DIM/cache and owner guards remain; coercion, effectful E_STRICT and wider operators/lifetimes stay partial. [Numeric bitwise default review](coverage/semantics/numeric-bitwise-default-reception-review.json).

Quiet Numeric-only signed64 modulo and shifts now compose deferred integer defaults, including wrapped/signed/count64 results, MIN%-1, nonnull zero, cold/warm BYREF caches and named warning reentry. Source/ENV/no-DIM/cache and owner guards remain; invalid divisor/count results, coercion, E_STRICT, wider powers and wider scope stay partial. [Review](coverage/semantics/numeric-integer-operator-default-reception-review.json).

Quiet Numeric-only signed64 integer-result powers now compose deferred defaults, including exact (-2)**63, MIN/MAX identity, exponent-zero, odd negative bases, nested powers and nonnull zero through cold/warm BYREF caches and named warning reentry. Source/ENV/no-DIM/cache and owner guards remain; float results and negative exponents extend below, while coercion, E_STRICT and wider scope stay partial. [Review](coverage/semantics/numeric-power-default-reception-review.json).

Quiet completed Numeric FLOAT powers now compose deferred defaults, retaining raw one and signed-zero cache bits before integer conversion and preserving NaN/nonfitting TypeErrors. Cold/warm BYREF defaults, named warning reentry and the saved-native overflow promotion keep source/ENV/no-DIM/cache/owner authority. Quiet GENERAL plans extend below; power diagnostics, implicit coercion and wider scope stay partial. [FLOAT-power review](coverage/semantics/numeric-float-power-default-reception-review.json).

Quiet Numeric FLOAT powers now complete pure GENERAL plans under unchanged source/ENV/no-DIM/cache/owner guards. Raw fractional caches precede their own precision callbacks, throw/retry and private integer reception. Three fresh source agreements plus three explicit Unsupported controls, two promoted saved originals, author fixtureSL184 and independent229 retain separate cuts/source0 for fixtures. Actual joined `14002d6ef` SL508 loading passes in15.739573478s/source0; held lanes and inventory remain unchanged. [GENERAL-power review](coverage/semantics/numeric-general-power-default-reception-review.json).

Quiet POWER-specific conversion now admits existing decoded FULLNUM strings and Boolean/null operands, retaining generic Numeric/Add/Mul identity and source/ENV/no-DIM/cache/owner guards. Three fresh source agreements plus three explicit Unsupported controls and two saved-original promotions stay separate; corrected authorSL109 and independent257 have source0, while the original pre-main fixture syntax failure retains0. Raw int/float caches precede private receives and own precision throw/retry. Actual `c8749a4fc` SL508 loading passes15.738766288s/source0; leading/nonnumeric effects, power diagnostics and wider scope remain partial. [Scalar-power review](coverage/semantics/numeric-coercive-power-default-reception-review.json).

Quiet scalar ADD/SUB/MUL/DIV defaults now share the unchanged operand projection with POWER, preserving raw int/float cache types before private reception and own precision callbacks. Three new source agreements plus three explicit Unsupported controls remain separate from accepted throw103, corrected BYREF cold132 and independent307 source0 cuts; the original cold132 and static generator failures retain0. Twenty affected old helper formulas execute only in fresh fixtures. Actual combined `3196dd2b7` SL508 loading passes15.330673544s/source0; conversion effects, DIVZERO and wider scope remain partial. [Scalar-arithmetic review](coverage/semantics/numeric-coercive-arithmetic-default-reception-review.json).

Genuine computed Boolean operands now enter existing arithmetic/POWER defaults through Boolean-shape, quiet-condition and NINT0/1 proofs, without generic Numeric widening. Three fresh source agreements plus three explicit Unsupported controls, author 233 and corrected peer 329 retain separate cuts/source0 for fixtures; the original peer elaboration failure stays at 0. BYREF raw float 2.5, own precision throw/retry, named reentry and real skipped E_STRICT retain source/ENV/no-DIM/cache/owner guards. Actual joined `f2c6bd851` SL508 loading passes in 16.382158544 s/source0; noisy truth, selected effects, raw selections and wider scope remain partial. [Boolean-operand review](coverage/semantics/computed-boolean-operand-default-reception-review.json).

Raw deferred FLOATs cache before local conversion. Own precision callbacks
borrow a private formal, resume the saved PINT on normal return and preserve
handler-throw cleanup/retry plus registry replacement/reentry. Overflow retains its raw PFLOAT tag through
ordinary parameter checking. Named holes, supplied bypass and no-DIM/NaN/owner
bounds remain. Other pruned syntax, unresolved names/namespaces and wider
producers/entries/lifetimes
remain partial; private/Generator contexts remain partial.
[Immutable integer default review](coverage/semantics/immutable-integer-default-reception-review.json),
[integer-truth default review](coverage/semantics/immutable-integer-truth-default-reception-review.json).
[Selected integer default review](coverage/semantics/selected-integer-default-reception-review.json).
[Folded Boolean ternary default review](coverage/semantics/folded-boolean-ternary-default-reception-review.json).
[Quiet fitting FLOAT review](coverage/semantics/quiet-fitting-float-default-reception-review.json),
[fractional default review](coverage/semantics/fractional-float-default-reception-review.json).
FINAL MOD handling
preserves the admitted CONST/CV diagnostic order and one-/two-cell retirement,
including both-noisy CV pairs and quiet-left CVs with noisy CONST or CV divisors.
FINAL also preserves a left precision-loss Deprecated notice or a range Warning
from a FLOAT before its quiet-zero MOD Error, retaining original CONST/private-CV
reads and real cell retirement. Canonical NaN left operands preserve ordered
Warning and Deprecated notices on the same quiet-zero path.
An unrelated eligible Deprecated handler also permits a sole leading-number MOD
Warning before the quiet-zero Error through FINAL. The handler stays uncalled;
canonical operand pointers, the exact converted RHS snapshot and null scratch
preserve original reads and real cell retirement. With an unrelated eligible
Warning handler, FINAL also preserves a sole precision-loss Deprecated notice
from an admitted string or FLOAT before that MOD Error. The handler stays uncalled;
canonical operands, null scratch and real zero-/two-cell retirement retain their
existing guards. With an eligible Warning or Deprecated handler, two quiet staged
MOD conversions also preserve the zero-divisor Error through FINAL. The handler
stays uncalled; original pointers, empty intrinsic notice vectors and genuine
zero-/one-/two-cell retirement remain required. An unrelated Deprecated handler
also leaves a sole FLOAT range Warning before the quiet-zero MOD Error through
FINAL, with exact conversion caches, source/pointers and real zero-/two-cell
retirement; the handler stays uncalled.
With a quiet left MOD operand, FINAL also preserves a sole intrinsic Warning
or Deprecated notice from the converted RHS before the zero-divisor Error. The
eligible opposite numeric handler remains uncalled. Fresh left conversion
reproduces its saved integer; the exact RHS singleton snapshot, canonical
pointers and null scratch remain required. Lifecycle checks cover actual
zero/one/two-cell retirement.
FINAL preserves one intrinsic Warning from each MOD operand under an unused
eligible Deprecated handler, or one Deprecated from each operand under an
unused eligible Warning handler, before the zero-divisor Error. Fresh left
conversion reproduces its saved integer; the exact current RHS singleton
snapshot, original CONST/private-CV source, canonical pointers and null
scratch remain required, and lifecycle witnesses include two same-CV notices
with one retired cell.
[Both-operand MOD review](coverage/semantics/output-final-default-unrelated-handler-both-modulo-conversion-error-review.json).
Four further CONST/CV originals complete two real calls to the selected named
Warning handler, one per MOD operand, before FINAL reports the zero Error. Its
two required untyped by-value formals and literal-echo/implicit-NULL body retire
four distinct formal cells while `AHH` stays buffered. Exact original source,
cache, pointer and native Error guards remain; wider handler/retarget/lifetime
forms and OB31 stay partial.
[Selected both-Warning review](coverage/semantics/output-final-selected-both-warning-modulo-error-review.json).

Selected LEFT precision Deprecated handlers also return NULL and retire their
two formal cells before the fresh quiet MOD-zero RHS and FINAL Error. Eight
originals agree with native observations run once; precode14, lifecycle12 and
independent12 fixtures retain separate source-zero cuts. Wider handlers, operands
and lifetimes remain partial.
[Selected left-Deprecated review](coverage/semantics/output-final-selected-left-deprecated-modulo-error-review.json).

Selected quiet PINT-left/RHS precision Deprecated or both same-kind precision
callbacks return NULL and retire two/four formal cells before FINAL MOD-zero
Error, preserving the actual store and buffered AH/AHH. Sixteen originals reuse
native observations once; precode17, lifecycle12 and peer16 remain separate
source-zero cuts, and the initial fixture failure remains zero credit. Mixed
notices/masks and wider handlers/operands/lifetimes and OB31 remain partial.
[Selected precision review](coverage/semantics/output-final-selected-precision-modulo-error-review.json).

Selected mask8194 handlers with a literal Echo followed by one own bare `return;` preserve FINAL MOD-zero Error through exact raw/emitted-line authority and two/four-cell retirement. Native4 once/source4 at `1008ec0ca` retain their agreement identity; prelaw19, lifecycle13 and independent24 fixture-SL conditions keep separate source-zero cuts. Baseline2 Unsupported and the other2 unrun retain0. The sole actual `be48fce13` SL508 load passes in15.689459902s/source0; arbitrary PNULL-producing bodies, wider forms and existing holds remain partial. [Bare-return review](coverage/semantics/output-final-selected-bare-return-modulo-error-review.json). Literal `return true;` also preserves that Error through its own raw TRUE child, emitted line, true flag and PBOOLtrue read, keeping its Boolean return distinct from resumed NULL scratch. Its four source agreements at `3b319c2cf`, prelaw19, lifecycle13 and independent24 fixture-SL cuts retain separate identities from the bare-return cuts. The corrected peer run passes; the original fixture syntax failure retains zero credit. The combined `e1245c8cc` SL508 load passes in 15.287736607s/source0. [TRUE-return review](coverage/semantics/output-final-selected-true-return-modulo-error-review.json). Own literal integer-zero Returns after the selected handler Echo also preserve FINAL MOD-zero Error. PINT0 is consumed under strict-FALSE handling and remains distinct from resumed NULL scratch. Native4 once/source4, prelaw19, lifecycle13 and peer24 retain separate cuts; the actual86fe SL508 load passes16.141093342s/source0. Wider forms and OB31 remain partial. [Integer-zero return review](coverage/semantics/output-final-selected-zero-return-modulo-error-review.json). Literal FALSE handler Returns preserve default Warning/Deprecated diagnostics before FINAL MOD-zero Error. Actual atomic fallback appends each diagnostic before restoring NULL scratch and the saved callback. Native4 once/source4, prelaw19, lifecycle13 and peer30 keep separate cuts. The actual883305 SL508 load passes15.880750462s/source0. Wider forms, stdout diagnostics and OB31 remain partial.

Selected mask8194 handlers also admit own raw nonzero signed64 integer-literal returns through exact child/CODE/line and compiled PINT authority. Four positive originals preserve AH/AHH, two/four real formal retirements and FINAL MOD-zero Error without default diagnostics; negative/MIN and overflow projections stay source0. Actual `40459b788e`/508 loading passes separately (16.331940516s/cap60/source0); UnaryMinus and wider return, handler, operand, history and lifetime forms and OB31 remain partial. [Integer-return review](coverage/semantics/output-final-selected-integer-return-modulo-error-review.json).

These are bounded extensions; the linked family reviews and inventory retain
wider producers, consumers, signatures, ownership and lifecycle obligations.

The setter repair preserves an explicit token-derived fact for a present hook
parameter list throughout checked conversion, printing and semantic header
validation. An omitted setter parameter list supplies implicit `$value`; explicit empty
`set()` remains distinct.
Its required classified syntax campaign (30,981 entries/profiles) and affected
grammar/scanner inventories passed at their recorded private cuts. The original
native Fatal/model NORMAL mismatch and all failed or Unsupported cuts retain
zero credit in the [repair review](coverage/semantics/property-hook-parameter-list-review.json).

Compiler class/constant lookups preserve complete typed tuple tails during
recursion. Focused fixture checks and independent typed-domain equivalence retain
first-match behavior and source-zero credit.
[Lookup review](coverage/semantics/compiler-lookup-tail-review.json) records the separate cuts. ENUM220 retains its separate current
precision/pending source cuts and earlier quiet cut; old timeouts remain zero credit.

The latest source cut `6e0fc4b39` passes its once-only 508-module production SL
load in 16.6919290041551 s under the unchanged 60-second cap, with `true` plus LF,
quiet stderr, stable HEAD and all 512 watched inputs, 511 ordered arguments and
fully reaped processes. It adds zero source credit. Raw report:
`../php-spec-evidence-archive/resumed-main-20261112/main49-direct-integer-arithmetic-shorthand-base-joined-508-v1/report.json`
(SHA-256 `1ffd26c740fe5bdb4849cb34bcad39a30654e4fc19823f7451d1f43bf7b7e844`).
Earlier joined loads and private source/native/state evidence keep their original
identities and credit. Metadata descendants do not renew execution credit.

The inventory remains 169 constructors and 306 runtime obligations, with zero
constructors and one obligation closed. Complete core remains unfinished.

Ordinary property-reference source removal now matches Zend's declaration
identity across distinct instances. First-match swap-last order is preserved
while surviving owner tags still identify their actual live slots. The existing
supported repeated-class counterexample now agrees with native PHP; 68 independent
state/protocol conditions (61 reached, 7 derived; 2 heap bindings) pass at their
recorded 501-module cut. The earlier normal-output mismatch retains zero credit.
The [source-order review](coverage/semantics/object-property-source-order-review.json)
binds these cuts separately from the joined `7e81d487b` 503-module production SL
load (14.979878857 s, zero source credit). That correction changes module229
alone and preserves generic ownership; the separate Notice extension follows.

Named and positional reference-send Notice arrays admit finite genuine rooted
instance-property sources on one quiet object-valued ALIAS leaf. Distinct owners
may share a declaration. A source owner may have finite plain public `stdClass`
slots, all active aliases to that same cell, with fresh `PROP_INITIAL` and actual
explicit-unset `PROP_UNSET` holes. Complete descriptor/physical-slot traversal
requires every active sibling's reciprocal source and preserves each CELL edge.
Owners retain the parentless, methodless, no-default/hook/setter bounds and must
survive logical pruning independently of their metadata.

Same-cell rebinding preserves native source order; failed binding preserves
membership. Gradual unset retains constraints until the final source detaches.
Shared COW retains the cell, while explicit CV/old-table removal permits singleton
DIRECT copying. A final transfer can constrain a new cell after the old sibling
sources detach. At that cut, active DIRECT/different-cell siblings, wider source
kinds, source-object retirement and held lanes remained partial; REF25 below
extends quiet DIRECT siblings. Quiet payload, ancestor
and cell/history bounds, generic ownership, GC and modules138/229 are unchanged.

Two new originals agree at their 505-module SL cuts, reusing two native originals
run once. AL172/136 execute 308 conditions, 240 unique: 172 source-reached and
68 derived, with 7 distinct heap bindings and a repeated 68-condition prefix.
The unchanged AL79 fence isolation and source Unsupported baseline retain zero
source credit. The [same-owner review](coverage/semantics/same-owner-property-alias-stdclass-reference-notice-review.json)
separates those cuts from its recorded joined 507-module load. The earlier
[finite instance-source review](coverage/semantics/multi-property-alias-stdclass-reference-notice-review.json)
retains its own 501/503-module source/state cuts, preserved failures and joined505.

REF18 composes finite instance/static property-source memberships for a quiet
ALIAS `stdClass` leaf. The ordered actual source list is nonempty and unique;
each member uses its unchanged proof against the complete state. Slot/class
identity, rooted owners, logical pruning, history and array-ancestor checks remain.
Explicit detach/transfer preserves constraints until the final source leaves.
Two originals agree at their separate author507/peer505 SL cuts, with native
observations reused once. PeerAL224 passes 178 reached and 46 derived conditions
across seven heap bindings at its 505-module cut. The prior Unsupported baseline,
AL72 fence isolation and first pre-main223 fixture failure retain zero credit.
The actual `5a263de68`/507 load passes in 15.471802748 s with zero source credit.
Implicit owner retirement, wider source/declaration forms and held lanes remain partial.
[Review](coverage/semantics/mixed-property-alias-stdclass-reference-notice-review.json).

REF19 admits multiple separate plain public static `stdClass` declarations in one
class for the same quiet ALIAS leaf. Each active same-cell row retains a reciprocal
source; fresh INITIAL holes remain allowed. Active DIRECT/different-cell/UNSET
rows and same-class mixed instance/static layouts remain partial. Two exact
originals retain separate author507/peer505 SL cuts with native
reuse. Author AL105, peer checkpoint54 and controls80 execute 239 conditions,
217 unique (159 reached, 58 derived; 22 repeated context), across seven heaps.
The failed peer112, Unsupported baseline and AL63 isolation retain zero credit.
Actual `e1025e63c`/508 loading is separate/source0; metadata renews no private cut.
[Review](coverage/semantics/same-class-static-alias-stdclass-reference-notice-review.json).

REF20 admits grouped plain public static `stdClass` source declarations through
the selected item's exact indexed origin and absent initializer. Existing complete
class descriptors, actual rows, reciprocal sources, quiet leaf, roots and history
retain their prior authority. Two exact originals reuse two native observations
once at separate author507/peer505 SL cuts. Peer AL152 executes 123 unique
conditions (64 reached, 59 derived; 29 repeated context) across two heaps.
Unsupported baseline, AL68 ingress and two pre-main fixture diagnostics remain0.
Actual `bc96df310`/508 loading passes in 15.411876949 s with zero source credit.
Same-class mixed instance/static layouts and wider active rows remain partial.
[Review](coverage/semantics/grouped-static-alias-stdclass-reference-notice-review.json).

REF21 composes genuine same-class instance/static plain `stdClass` sources against
unchanged actual state. Static heads validate real rows without an object slot or
edge; instance complements require the selected cell's exact declaration/key/class
OBJECT source and full live-owner/slot/pruning proof. Static INITIAL under an
OBJECT-only source adds no root. Two exact originals retain separate author507 and
peer505 SL cuts with two native originals reused once. Peer AL176 executes 145
unique conditions (69 reached, 76 derived; 31 repeated context) across three heaps.
Baseline Unsupported, AL71 fence and the first pre-load SL failure remain0.
Actual `f5312f510`/508 loading passes in 15.365779470 s/source0. At that cut, inactive
instance complements without their own selected source, static-only mixed
membership and both split-cell orientations stayed partial; REF22 below extends
the authentic hole case. Modules138/229 and generic ownership remain unchanged.
[Review](coverage/semantics/same-class-mixed-property-alias-stdclass-reference-notice-review.json).

REF22 admits genuine same-class instance INITIAL/UNSET complements through an
actual selected instance source and its complete owner/slot/pruning proof. Exact
class/member/DECL/key authority uses unchanged S; inactive holes add no CELL edge.
Two exact originals at separate author507/peer505 SL cuts reuse two native
observations once. Peer AL172 physical/139 unique comprises 73 reached,66 derived
and33 repeated context across four heap bindings. Baseline Unsupported and AL75
ingress remain0, with no new failure. Actual `0a607aaeb`/508 loading passes in
15.014739971 s/source0. Static-only mixed membership with an exact-class INSTANCE
arena record, both split-cell orientations and wider layouts remain partial;
modules138/229 and generic ownership stay unchanged.
[Review](coverage/semantics/same-class-mixed-hole-alias-stdclass-reference-notice-review.json).

REF23 admits unused plain singleton instance declarations when the complete stable
object arena has no INSTANCE record of that exact declaring-class origin. Past
and non-rooted records also block admission. Full class-member and raw index-zero
item authority remain; the route adds no physical owner, slot, source, edge or root.
This exact-origin condition is separate from ancestry and live-root checks. Two
originals reuse native observations once at separate author507/peer505 SL cuts.
Peer AL179 executes138 unique conditions:73 reached,65 derived and41 repeated
context across two heaps. Unsupported baseline, ingressAL75 and the canceled
117.976 s checkpoint retain0. Actual `35a324ba9`/508 loading passes in
15.893075395 s/source0. At that cut, grouped unused declarations, exact-class records,
split cells and wider layouts remained partial; modules138/229 and generic ownership
stay unchanged. [Review](coverage/semantics/static-only-mixed-alias-stdclass-reference-notice-review.json).

REF24 authenticates every raw grouped unused item against its exact indexed
occurrence and actual class-member descriptor, with guarded target indexing. The
unchanged whole stable-arena absence check includes past and non-rooted INSTANCE
records of the exact declaring origin; metadata adds no owner, slot, source or edge.
Two originals reuse native observations once at separate author507/peer505 SL cuts.
Peer AL178 executes129 unique conditions:84 reached,45 derived and49 repeated
context across two heaps. Baselines, ingress86 and two fixture diagnostics retain0.
Actual `e59706332`/508 loading passes in15.836923168 s/source0. Exact-class records,
split cells and wider layouts remain partial; modules138/229 and generic ownership
remain unchanged. [Review](coverage/semantics/grouped-unused-mixed-alias-stdclass-reference-notice-review.json).

REF25 admits quiet DIRECT `stdClass` instance siblings alongside same-cell ALIAS
slots and existing INITIAL/UNSET holes. The complete descriptor/physical-slot walk
preserves every real child edge, including duplicate object identities; reciprocal
selected sources and independent owner pruning remain required. Handler retarget,
failed binding and returned shared COW preserve the actual owners. Two originals
reuse native observations once at separate author507/peer505 SL cuts. Peer AL101
checkpoint plus AL108 controls execute 209 conditions, 149 unique: 101 reached and
48 derived, with 60 repeated context and three distinct heaps. Prepatch Unsupported
and AL60 ingress retain zero source credit. Actual `4f4ba2f6f`/508 loading passes
in 15.089919813 s/source0. Static DIRECT rows, different-cell aliases and wider
source-owner/lifetime forms remain partial; modules138/229 and generic ownership
are unchanged.
[Review](coverage/semantics/direct-sibling-property-alias-stdclass-reference-notice-review.json).

REF26 admits same-class quiet DIRECT instance complements through another genuine
selected OBJECT source and the complete actual owner, ordered-edge and pruning
proof. No source or owner is added for the complement. Two originals retain
author507/peer505 cuts with native reuse; peer286 conditions comprise211 unique
(144 reached,67 derived),75 repeated context across five distinct graphs/six
executions. Baseline, AL75 and the original failure retain0. Actual `cd502e13d`/508
loading passes in15.874029035 s/source0. Static DIRECT rows, different-cell aliases
and wider forms remain partial; modules138/229 and generic ownership are unchanged.
[Review](coverage/semantics/same-class-mixed-direct-alias-stdclass-reference-notice-review.json).

REF27 admits quiet DIRECT `stdClass` static siblings through genuine selected-source
and static-row authority, preserving every physical root without a metadata owner.
Two originals retain author507/peer505 SL cuts with native2 once. Separate AL127/111
at peer505 execute238 physical/177 unique conditions (127 reached,50 derived,
61 repeated context), with six distinct/seven executed heap bindings, source0.
Precode Unsupported/AL61 stay0; six old predicate-only positives are promoted
without replay. Actual `00cc247e2`/508 loading passes in14.798786004 s/source0.
Different-cell aliases and wider declarations/owners/lifetimes remain partial;
modules138/229 and exact holds are unchanged.
[Review](coverage/semantics/static-direct-sibling-alias-stdclass-reference-notice-review.json).

REF28 admits own public untyped nonfinal raw `NScalarInt` constants on global named
instance/static source classes. Exact class/group/item/initializer and folded
`PINT`/`PVSCALAR` authority add no owner. Two originals retain author507/peer505
SL cuts with native2 once. Separate AL174/225 at peer505 execute399 physical/294
unique conditions (174 reached,120 derived,105 repeated context), with five
distinct/six executed heap bindings, source0. An exact-byte bridge preserves
checkpoint174 after two derived-control fixes; historical wrapper inputs/revisions
remain distinct. Baselines/AL107 and original diagnostics/expectation correction
stay0. Actual `972cd9882`/508 loading passes in15.123888404 s/source0. Existing
constant-free scope, property/source/owner bounds, modules138/229 and holds remain;
unary-minus nodes, namespace-qualified companions and wider constants stay partial.
[Review](coverage/semantics/class-int-constant-alias-stdclass-reference-notice-review.json).

REF29 additionally admits one raw `NExprUnaryMinus(NScalarInt z)` with exact
parent/child occurrences, signed-long input/result and folded `PINT(0-z)` /
`PVSCALAR` authority. The literal and empty-constant arms and all property/source/
owner bounds remain. Two originals retain author507/peer505 SL cuts with native2
once. AL175+250 at peer505 execute425 physical/319 unique conditions:175 reached,
144 derived and106 repeated context across five distinct/six executed heaps,
source0. Equal revisions/source/input maps retain the checkpoint without replay;
baselines and ingress108 stay0, with no new failure. Actual576c composition and
c9c770e1a/508 loading pass separately in15.467628574 s/source0. Namespaced and wider
constants remain partial;138/229 and exact holds stay unchanged.
[Review](coverage/semantics/class-negative-int-constant-alias-stdclass-reference-notice-review.json).

REF30 also admits namespaced named source classes through a valid short raw name,
the actual source unit/path and canonical class context with its real file/positive
line and exact qualified descriptor name. Existing integer/minus pools, empty
constants and all property/source/root/lifetime bounds remain. Two qualified
originals retain separate author507/peer505 SL cuts with native2 once. Peer505
AL190+193 executes383 physical/262 unique conditions (190 reached,72 derived,
121 repeated context), five distinct/six executed heaps, source0. Original
unqualified sources, Unsupported baselines, ingress123 and failed candidates stay0.
The actual namespace composition and combined Get `58e20adf7`/508 load are separate;
the latter passes15.759459066 s/source0. Namespace producer fallback, wider constants
and owner/lifetime forms remain partial;138/229 and exact holds stay unchanged.
[Review](coverage/semantics/namespaced-class-int-constant-alias-stdclass-reference-notice-review.json).

REF31 admits fallback-present producer names through primary-only lookup, the
call's source unit and authentic early PPFUNCTION publication history. Current
lookup or the descriptor EARLY bit alone is insufficient. Existing no-argument/
untyped-CV, source, payload and ownership bounds remain. Two normal originals and
a late-install expected-Unsupported control retain separate author507/peer505
SL cuts with native3 once; the control has source0. Separate AL66/43/98 cuts
execute207 physical conditions (163 reached,44 derived), without a unique
aggregate. Baselines, the old e05 refusal, two diagnostics and the fixture parser
failure stay0. Actual98b own composition and the combined `47dc49ad9`/508 load
remain separate; the latter passes15.566676035 s/source0. Actual global fallback,
late/dynamic/different-unit primaries, wider signatures and lifetimes remain partial.
[Review](coverage/semantics/namespaced-primary-producer-reference-notice-review.json).

REF32 admits one required array BYVAL producer formal through exact raw/normalized
header authority, with no defaults, variadics, attributes or return declaration.
Existing zero-argument/untyped, target/publication and ownership rules remain.
Three normal originals comprise two Notice snapshots and one caught entry-TypeError
control, with native3 once at separate author507/peer505 SL cuts. Separate AL92/115
cuts execute207 physical conditions (156 reached,51 derived), without a unique
aggregate. Both Unsupported baselines stay0; the older normal type control retains
its own cut. Caller-CV replacement by int17 preserves the completed private array
snapshot. Actualeba own composition and combined `9302e90cb`/508 loading remain
separate; the latter passes15.115694686 s/source0. Array BYREF formals, typed returns,
wider headers and lifetimes remain partial.
[Review](coverage/semantics/array-producer-cv-reference-notice-review.json).

REF33 admits the same required array formal by reference when raw and normalized
BYREF flags agree. Entry reception adds no persistent constraint: a producer can
save its array, replace the shared caller cell with int17 and return the snapshot;
handler writes then affect that caller cell, separately from the private Notice
cell. Three normal source agreements retain author507/peer505 SL cuts and native3
once. Separate AL108/129 cuts execute237 physical conditions (180 reached,57
derived), without a unique aggregate. Both Unsupported baselines stay0; one old
REF32 pure-header query is promoted without renewing its historical AL115 cut.
Actual source/test composition `39c2183eb` and its joined508 load remain separate;
the latter passes15.432399042 s/source0. Typed producer returns, wider headers,
actual global fallback and broader payload/owner/lifetime forms remain partial.
[Review](coverage/semantics/array-byref-producer-cv-reference-notice-review.json).

Completed one-CV producers with required canonical `array` formals now authenticate
their raw `array` return against the normalized signature before Notice admission.
Ordinary return verification and frame retirement preserve the returned table,
while the fresh private argument cell can later hold an integer. Three new
originals agree with native observations run once. Author AL149 and peer
fixture-SL174 retain separate cuts; the unchanged AL174 timeout is inconclusive.
The [array-return review](coverage/semantics/array-return-producer-cv-reference-notice-review.json)
keeps actual composition/joined loading at zero source credit. Wider producer
headers and all standing holds remain partial.

Required untyped one-CV producers now admit canonical `array` returns from scalar
arguments. Three originals agree using three native executions once. Author
fixture-SL177 and peer fixture-SL192 execute 369 conditions: 318 reached and 51
derived, without a unique aggregate claim. The fresh return/header front101 and
affected header-only28 check remain separate/source0. The
[untyped array-return review](coverage/semantics/untyped-array-return-producer-cv-reference-notice-review.json)
preserves the first wrong-table fixture failure and Unsupported baselines at zero
credit. The actual joined 508-module SL load at `484d489ce` passes separately
(33.197897111 s, zero source credit). Nullable/other returns, wider
headers/lifetimes and standing holds remain partial.

Earlier [finite static-source](coverage/semantics/multi-static-alias-stdclass-reference-notice-review.json),
[single static-source](coverage/semantics/typed-static-alias-stdclass-reference-notice-review.json),
[typed instance-property](coverage/semantics/typed-alias-stdclass-reference-notice-review.json),
[untyped ALIAS-object](coverage/semantics/alias-object-leaf-reference-notice-review.json),
[DIRECT-object](coverage/semantics/direct-object-leaf-reference-notice-review.json)
and [root-object](coverage/semantics/stdclass-reference-notice-review.json)
source, COW, cancellation and WeakReference cuts retain their own identities.
Finite DIRECT/ALIAS array graphs retain singleton unwrapping, shared-cell payload
identity, nested COW and last-owner cleanup; their
[array-cell](coverage/semantics/alias-child-reference-notice-review.json),
[DIRECT-graph](coverage/semantics/direct-child-reference-notice-review.json),
[flat-array](coverage/semantics/array-reference-notice-review.json) and
[scalar-reference](coverage/semantics/alias-array-reference-notice-review.json)
ledgers remain unchanged. Object-leaf ancestry checks do not narrow older root
scalar/array routes.

I84–I91 cover selected typed magic, captured and raw method Generator
factories; Fiber SEND/THROW and reference caches; and array/string method
Closure binding and identity. Joined source and reached-state gates validate
these bounded routes. Original failures retain zero credit in the linked
ledgers. Wider signatures, callback/API entry, delegation and lifecycle
combinations remain partial. [Generators](docs/semantics/GENERATORS.md),
[Fibers](docs/semantics/FIBERS.md), [Closure calls](docs/semantics/CLOSURE-CALL.md);
reviews [I84](coverage/semantics/generator-magic-factory-review.json),
[I85](coverage/semantics/generator-direct-magic-review.json),
[I86](coverage/semantics/generator-captured-method-body-review.json),
[I87](coverage/semantics/generator-raw-method-factory-review.json),
[I88](coverage/semantics/generator-raw-method-cache-review.json),
[I89](coverage/semantics/generator-captured-method-throw-review.json),
[I90](coverage/semantics/generator-direct-magic-throw-review.json), and
[I91](coverage/semantics/generator-string-method-closure-review.json).

Published enum `cases()`/`from()`/`tryFrom()` support admitted direct,
captured and pipe calls through method strings and class/case arrays. Selection
and original bytes survive argument rebinding and named Stringable callbacks;
internal Closure captures add no owner of an input array or receiver. Callable
typed parameters and `Closure::fromCallable` share these generated targets.
The [enum/callable scope](docs/semantics/SOURCE-CLASSES.md) and
[feature inventory](coverage/semantics/features.json) retain the individual cuts.

Published enum `is_callable` queries cover generated, absent and syntax-only
methods, source-certified magic fallback and direct public case methods.
Malformed live arrays return false before syntax-only lookup. Admitted name
output accepts admitted literal/string-variable inputs and initialized scalar
CVs, preserving spelling and the captured reference cell. An input-SEND receipt
keeps a variable input fixed through later callbacks, output aliases and nested
queries; argument throws skip the query's assignments.
[Saved-input review](coverage/semantics/enum-is-callable-saved-input-review.json).
Named nonunpack output separates source SEND order from signature slots,
including early `callable_name` and omitted `syntax_only`. A nonowning acquisition
certificate preserves the sent cell through CV unset/rebinding. Real SENT/output
owners, genuine input history and clear/destructor/name commitment remain intact;
nested queries, argument/output throws and named errors keep their order. Separate
rebound-array source/value proofs, packs and wider output places remain partial.
[Named-output](coverage/semantics/enum-is-callable-named-output-review.json) and
[reference-history](coverage/semantics/enum-is-callable-named-output-reference-history-review.json)
reviews retain the two cuts.
`syntax_only` now receives weak scalars or enforces caller strictness before
query/output work. Weak null deprecation retains actual operands and the acquired
cell through handler reentry/throw; missing value keeps priority and name commit
waits for successful reception. Separate input/output and nonunpack bounds stay
explicit. Three source agreements, 454 independent checks and joined SL452 pass
at their recorded cuts. [Boolean reception](coverage/semantics/enum-is-callable-bool-reception-review.json).
Ordinary function-string queries now distinguish actual USER/builtin availability
from body support and known absence. Lookup follows flag reception; captured
bytes and the real output cell survive null-handler rebinding. A nonowning output
publication prefix freezes the result through destructor publication. Wider
domains remain partial. One source agreement, 313 independent checks and joined
SL453 pass at their recorded cuts. [Function strings](coverage/semantics/is-callable-function-string-review.json).
Quiet primitives and existing known Closure objects now share the query/output
path, preserving exact scalar/function names without invoking bodies. Actual
SENT retains Closure/receiver ownership across source removal and same-CV writes;
saved query-time precision preserves float names through output callbacks.
Three source agreements and 161 independent ownership/budget checks pass at their
recorded cuts; current joined SL454 passes. Producer and wider Closure/output
domains remain partial. [Review](coverage/semantics/is-callable-primitive-closure-review.json).
Existing ordinary USER instances and `stdClass` now classify without entering
`__invoke` or `__toString`. Published public method presence and proved table
absence stay separate from unresolved metadata; inherited names use the runtime
class. Real SENT and acquired-cell owners retain same-CV/removal history through
normal and throwing output effects. Two source agreements and 179 independent
ownership/budget checks pass at their recorded cuts. [Review](coverage/semantics/is-callable-instance-review.json).
Ordinary USER method strings and class/object arrays now share public concrete
method/known-absence queries without body entry. Structural syntax-only admission
stays separate from lookup; exact names and selected booleans survive member-cell
mutation, receiver retirement and normal/throwing cleanup using borrowed history
and the existing result carrier. Three source agreements and 227 independent
history/ownership/budget checks pass at recorded cuts. [Review](coverage/semantics/is-callable-user-method-review.json).
Qualified USER array queries now use staged effectful API resolution, retaining
the resolved boolean independently of the later name snapshot. Lookup-handler
throw still commits NAME and cancels result assignment; reception-handler throw
keeps the old NAME. Real SOURCE/cell/exception owners preserve reentry, direct
receiver drain and namespaced nested queries. Seven source agreements and 259
independent history/ownership/budget checks pass at recorded cuts. [Review](coverage/semantics/is-callable-api-resolution-review.json).
Untyped receiver references now keep qualified public method resolution tied to
the original live USER object while a warning changes the current member. A
completed receipt survives later holder removal/receiver retirement during output
cleanup. Receiver loss during the warning reaches explicit Unsupported through
coherent callback/exception transport; no historical lookup or new owner is granted.
One three-mode source agreement and 98 independent loss/ownership/budget checks
pass at recorded private 461-module cuts. [Review](coverage/semantics/is-callable-alias-api-review.json).
Raw keyword callable strings and bare-method arrays now resolve self/parent/static
from the actual ordinary USER caller frame. Lexical versus called class and real
This ownership preserve public availability; known invalid scope is false without
a lookup deprecation. Existing phase-aware receipts retain exact names and lookup-throw
commitment through reentry and output cleanup. Five source agreements and 166
independent owner/phase/budget checks pass at recorded private 456-module cuts.
[Review](coverage/semantics/is-callable-keyword-context-review.json).
Last-owner ordinary Closure name outputs now use the existing NULL-clear, ordered
capture/static/This drain and NAME/result continuation. The real captured OLD
identity remains valid after retirement without rechecking drained cells or
adding a root; fresh Closure queries still require liveness. Normal, rebind,
throw, retained/same-CV and shared-edge controls use existing producers/entries.
Opaque/internal graphs and unproved cycles stay explicit. Three source agreements
and 247 independent owner/history/budget checks pass at their private 457-module
cuts. [Review](coverage/semantics/is-callable-closure-output-review.json).
Ordinary USER/stdClass name outputs now admit live acyclic owning property graphs
with plain untyped slots, through unique and retained/same-CV recipients. Existing
post-destructor storage handles actual unset/replacement, dynamic-before-declared
order, resurrection and pending throw without frozen child lists or new owners.
Historical std identity remains borrowed after retirement; source/cell/NAME/BOOL
continuations stay unchanged. Four source agreements and 426 independent
owner/history/budget checks pass at recorded private 458-module cuts.
[Review](coverage/semantics/is-callable-property-output-review.json).
Ordinary array name outputs now record the actual pre-clear heap identity through
ordered child cleanup and saved-name commitment, including rebinding/throw,
retained copies and same-CV SENT. The legacy rebound witness stays distinct;
new array history adds no owner and never rereads retired buckets. Current graph,
producer/nonunpack and opaque/cycle bounds remain. Three source agreements and
95 independent history/budget checks pass at their recorded private 459-module
cuts. [Review](coverage/semantics/is-callable-array-output-review.json).

Retained childless ordinary output objects delay destruction until their last
owner leaves. Last-owner output clears to NULL before the destructor, then
commits the saved name before return, throw or root VM exit. Unset/rebinding,
resurrection and API trace snapshots retain real cells and owners. Root exit
drains locals before the C pin; nested queries preserve status and skip
interrupted result assignments.
[Retained](coverage/semantics/enum-is-callable-output-retained-review.json),
[unique](coverage/semantics/enum-is-callable-output-unique-review.json) and
[exit](coverage/semantics/enum-is-callable-output-exit-review.json) reviews.

Cleanup throws now cancel exit and commit the name before propagating.
Compiled CV order preserves shared-wrapper decrements and exception previous chains;
integer exit status survives catch and later string exit. Eight new/promoted
source agreements, one affected enum exit-status source, three explicit
controls, strict433 and 256+47 independent guards pass at their recorded cuts.
[Cleanup review](coverage/semantics/enum-is-callable-output-cleanup-review.json).
Nested cleanup exits now return through their own C pins and preserve the
original output receipt. The latest integer exit supplies status; string exit
preserves it. Ordinary Child throws cancel exit while the name still commits;
nested queries commit their separate names without assigning abandoned booleans.
Nine source agreements, three explicit Unsupported controls, strict433 and five
separate reached groups (90+62+35+43+78 checks) pass at recorded cuts.
[Reexit review](coverage/semantics/enum-is-callable-output-reexit-review.json).
Two-entry live enum callable arrays now carry a first-SEND receipt through
positional name output. Class strings preserve spelling, case receivers use the
canonical class, and the sent array survives source rebinding and same-cell
output. Old-output destruction can rebind or throw before the saved name commits.
Seven exact agreements, two explicit Unsupported controls, strict435 and four
separate reached groups (60+53+33+70 checks) pass at recorded cuts.
[Variable-array review](coverage/semantics/enum-is-callable-variable-array-review.json).
An aliased source/output cell can now rebound to a new two-entry direct-string
array after the first SEND. The old selected name overwrites that cell, while a
separate holder keeps the rebound array live; a pre-output throw leaves the
rebound array and result assignment target untouched. Four exact agreements, one explicit
Unsupported owning-object control, strict435 and five separate reached groups
(64+50+53+29+33 checks) pass at recorded cuts.
[Array-alias rebound review](coverage/semantics/enum-is-callable-array-alias-rebound-review.json).
An exact rebound array with one ordinary childless object follows two owner
paths: last-owner output clears the shared cell before destruction, while a
separate holder delays destruction until after the saved name commits. A
throwing child commits the name before exception transfer without assigning
the interrupted result target. Three exact agreements, one excluded-builtin
control, strict435 and three separate reached groups (53+60+87 checks) pass
at recorded cuts. [Owning-array review](coverage/semantics/enum-is-callable-array-alias-owning-review.json).
A rebound array may lose its shared-cell owner while a distinct variable still
owns its ordinary child object. The array's eager release completes before
that variable is cleared, so its destructor sees the committed name; clearing
the variable before output gives the existing null-before-destructor path.
Three exact agreements, strict435 and separate held75/released55 reached
checks pass at recorded cuts. [Retained-child review](coverage/semantics/enum-is-callable-array-alias-retained-child-review.json).
Live two-entry callable arrays now retain their real reference cells through
the first SEND. Invocation reads current receiver/method payloads and freezes
the selected name and boolean before output destruction; later reference
mutation, output aliases and throwing cleanup preserve that selection.
Borrowed snapshots add no owners. Shared and singleton COW keep their ordinary
array behavior. Seventeen originals agree; two explicit controls and four
separate reached groups pass at their recorded cuts.
[Reference-member review](coverage/semantics/enum-is-callable-reference-array-review.json).
Literal, assignment-result and value/reference-return arrays now share that
receipt and invocation snapshot. Actual SEND transfers retain the table without
an extra pin; argument throws release a last referenced child before catch and
skip output/result assignment. Nine originals agree; the
[temporary-array review](coverage/semantics/enum-is-callable-temporary-array-review.json)
records source-bound transfer/owner/resumption checks.
First-SEND capture now accepts initially invalid untyped members and defers
callable admission until invocation. Borrowed old object/array history survives
its actual retirement without adding owners or resolving class names. Current
type-invalid pairs return false/`Array`, including syntax-only queries; output
repair/throw preserves that selection, and argument cleanup runs after the
handler with the result still unassigned. Sixteen originals agree at recorded
cuts, with independent history178 and focused55/37 checks in the
[initial-member review](coverage/semantics/enum-is-callable-initial-members-review.json).
Wrong-length and missing-key arrays now receive false/`Array` through the same
receipt, using one structural check and their real SENT owner. Source repair,
same-cell output, retained holders and owning-entry cleanup preserve the saved
shape and assignment order. Typed payload references are ignored when only the
bad shape matters; typed valid pairs remain partial. The
[structural-array review](coverage/semantics/enum-is-callable-structural-array-review.json)
records the exact source and ownership cuts.
The selected `is_callable` signature now acquires a simple third-output CV by
reference at SEND3 independently of query admission. Missing CVs become null
without an undefined-variable read; real owners preserve retained old aliases,
callback-created outputs and dynamic saved targets. Earlier argument throws
skip acquisition. The [output-acquisition review](coverage/semantics/enum-is-callable-output-acquisition-review.json)
records its bounded source/state cuts.
Fixed namespace fallback now records the actual selected builtin before
arguments. Callback publication cannot replace its target/signature; root and
ordinary named-function cache owners reuse that choice on later invocations,
including after an argument throw. Fresh sites select the newly published local
function. The [fixed-fallback review](coverage/semantics/enum-is-callable-fixed-fallback-review.json)
records source/authority/timing checks; unproved cache
owners remain explicit Unsupported.
The first real-Closure cache slice now records literal births and clone policy
without adding owners. Authenticated unscoped root/named-function factories and
their normal clones share the template cache, including after original retirement.
Unknown first births remain unknown; live stamps must match the actual function
and scope. The [Closure cache review](coverage/semantics/enum-is-callable-closure-cache-review.json)
records the shared slice. Real bind copies and Generator `Closure::call` copies
now preserve known cache policy: shared same-scope copies share, while changed
scope and every private copy receive a fresh private key. Retired source stamps
add no owners. The [private-cache review](coverage/semantics/enum-is-callable-private-cache-review.json)
records the copy hooks. Ordinary user `Closure::call` now records a separate
nonowning temporary-function cache identity. Each scope-changing/private call
gets a fresh key; warmth inside that invocation survives throws and nested calls.
Ordinary function entry clears inherited keys and frame restoration retains the
caller key. The [invocation-cache review](coverage/semantics/enum-is-callable-ordinary-call-cache-review.json)
records the bounded source/context checks. Named/inherited method factories
now authenticate first literal cache births from the exact ordinary creator,
compiled lexical owner and actual post-created scope. An inherited Child receiver
keeps Base lexical cache policy; clone and same-Base bind/call share it, while
Child scope changes are fresh. Unknown first births still block later inference.
The [scoped-birth review](coverage/semantics/enum-is-callable-scoped-cache-review.json)
records the source/lifetime and unknown-first control cuts. Raw ordinary named
and inherited nongenerator methods now authenticate their shared function cache
from the exact descriptor, actual target/function and lexical owner. `is_callable` selection
stays before arguments and survives argument/output throws and receiver retirement;
a fresh method can choose the newly published local function. The
[method-cache review](coverage/semantics/enum-is-callable-method-cache-review.json)
records this slice. Runtime named-function and direct method FCC and plain-function
`Closure::fromCallable` now stamp actual INIT/lookup-proven shared cache policy.
Clones preserve that policy after original retirement; existing-Closure FCC/API
conversions retain the same object and add no birth. The
[shared-capture review](coverage/semantics/enum-is-callable-shared-capture-cache-review.json)
records ownership, aliases and the promoted runtime-method control. Method
`fromCallable` now distinguishes known cold/private births from initialized/shared
source caches. Own-method registration, before-argument INIT, runtime FCC and
authenticated raw CAPI entry supply nonowning facts; missing or uncertain views
stay unknown. Birth-relative history preserves old private captures and fresh
private clones after later source initialization and retirement. The
[method-API cache review](coverage/semantics/enum-is-callable-method-api-cache-review.json)
records the source/owner/budget cuts. Runtime array/string method captures and
clones now authenticate shared cache ownership from actual INIT, immutable raw
function identity and canonical scope. Saved selectors remain coherent after
selected-array/source/receiver retirement, and argument/output throws preserve
namespace fallback warmth. The
[runtime-capture review](coverage/semantics/enum-is-callable-runtime-capture-cache-review.json)
records this bounded slice. Known user fake `bind`/`bindTo` copies and bound clones
now retain actual source cache policy and completed scope. Shared same-scope
copies share; Private and dummy-scope copies receive fresh keys. Immutable source
history survives original source/receiver retirement without new owners, and
copied calls leave raw method initialization facts unchanged. The
[fake-bind cache review](coverage/semantics/enum-is-callable-fake-bind-cache-review.json)
records two exact source agreements and 123 reached conditions with strict446.
Known unbound nongenerator user-method `Closure::call` now authenticates fresh
Private invocation keys from immutable method/source and exact completed scope,
while Shared same-scope calls retain their cache. Source removal during arguments
keeps real API owners until cleanup; history adds no pins or raw initialization.
The [fake-call cache review](coverage/semantics/enum-is-callable-fake-call-cache-review.json)
records one exact source agreement and 77 reached conditions with strict446.
Bound nongenerator user-method temporary calls now follow immutable SOURCE after
ancestor capture/receiver retirement. Completed Base SCOPE, distinct from Child
CALLED, and actual call authority preserve Private freshness or Shared reuse with
exact Base replacements. The
[bound-call cache review](coverage/semantics/enum-is-callable-bound-method-call-cache-review.json)
records one public-method source agreement and 107 reached conditions with
strict446. Known early top-level named user functions bound to the dummy
`Closure` scope now retain their warmed Private source cache while every temporary
call on a plain real nongenerator user Closure receives a fresh key. Argument-time
source removal preserves actual API owners and separate captured-leaf cleanup;
pure history survives retirement without pins. The
[dummy-scope review](coverage/semantics/enum-is-callable-dummy-user-call-cache-review.json)
records one exact source agreement, 120 independent reached conditions and
strict446. Direct top-level `if`-body named functions now authenticate actual
callable publication, a root runtime-declaration receipt and completed main-unit
history before the same dummy-bound temporary calls. The
[conditional-source review](coverage/semantics/enum-is-callable-conditional-user-call-cache-review.json)
records one exact source agreement, 136 independent conditions and strict447.
A named function published by an ordinary early named factory now retains
cache authority after creator-frame retirement. The saved call/source selection
and earlier publication prefix authenticate its real declaration cause without
live-frame inference. The [factory-source review](coverage/semantics/enum-is-callable-factory-user-call-cache-review.json)
records one exact source agreement, 165 independent conditions and strict447.
Public static nongenerator user-method captures from named class constants now
record cold Private versus pre-birth initialized Shared policy at the real
constant-creation hook. Actual initializer/PREFIX/scope and object birth ordinal
preserve old Private births after later raw initialization; Shared history and
clone policy recognize the new producer without metadata roots or raw INIT.
The [constant-method cache review](coverage/semantics/enum-is-callable-constant-method-cache-review.json)
records one distinct source agreement, 140 independent conditions and strict448.
Root globals authenticate that policy from declaration/SITE/PREFIX receipts;
unscoped entered include/eval globals additionally require real source bindings.
Entered units require an available unscoped caller before their first recorded
entry and completed compilation within the birth PREFIX; eval additionally retains
the exact generated filename and excludes constant/default receive contexts.
Pending, nonentered and forged receipts add no authority. Real constant roots
remain separate from nonowning cache history. The
[root](coverage/semantics/enum-is-callable-global-constant-method-cache-review.json),
[include](coverage/semantics/enum-is-callable-included-constant-method-cache-review.json) and
[eval](coverage/semantics/enum-is-callable-eval-constant-method-cache-review.json)
reviews retain their separate original-source, entry/owner/budget and strict
cuts, with include recorder controls counted separately.
Class-scoped include/eval producers authenticate named public nongenerator
methods and their class publication before entry. An inherited
Producer scope stays distinct from Child CALLED and captured Host scope;
producer retirement adds no metadata pin. Completed class/method publication
establishes caller availability even during surrounding compilation, while
the target unit must finish compilation before its constant birth. Eval retains
exact generated filename and empty LOCATION/RECEIVES. The
[scoped-include](coverage/semantics/enum-is-callable-scoped-included-constant-method-cache-review.json) and
[scoped-eval](coverage/semantics/enum-is-callable-scoped-eval-constant-method-cache-review.json)
reviews retain their separate source, entry/history/retirement and strict cuts.
Public static producers now share that exact declaring-scope/publication proof
across both routes with no This or Producer allocation. One mixed source and
shared route-specific entry/history/root-budget evidence are retained in the
[static-producer review](coverage/semantics/enum-is-callable-static-producer-constant-method-cache-review.json).
Other constant/default captures, wider conditional/factory sources, unproved
transformed copies and Generator/Fiber query owners remain partial.
Cleanup exit with an ordinary Throwable already pending, switched Fiber
completion/force-close, other owning rebound arrays, late attached type sources,
wider variable arrays, typed/backed/debt valid-pair cells, unpacked output,
loading and wider enum
member/lifetime contexts remain partial.

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

I93 extends real Generator Closure::call copies to admitted reference
formals. Copy/static ownership precedes warning callbacks; fresh formal cells
wrap frozen values afterward. Used Generator results survive API cleanup, and
warning traces retain the real handler and call frames. Five private native/model
sources and six reached fronts pass at their recorded cuts; joined strict433,
three exact I93 sources, one affected I92 value SEND source, temporary return92
and independent parked-cache169 states pass at f34d1214a. Original failures
retain zero credit. Receive/callback/mapping errors and wider calls remain
partial. [I93 review](coverage/semantics/generator-call-reference-review.json).

I94–I98 cover fake user-method Generator Closure::call copies, finite bound
source histories and distinct dynamic/folded string policies. Fake copies keep
shared method statics and exact declaring-class receivers; normal/abrupt binding
warnings release actual API owners in native order. Existing reference-warning
cursors also survive Fiber suspension in handlers and owning retval destructors.
Each milestone retains its original native/source/reached cuts and failures.
Joined strict433, four source comparisons and 187 custom/192 reported ownership
checks pass at their recorded cuts; see the [joined review](coverage/semantics/generator-call-series-current-review.json). Wider
call/receiver/signature, mapping, no-Gen receive and abrupt warning contexts remain
partial. Reviews [I94](coverage/semantics/generator-fake-call-copy-review.json),
[I95](coverage/semantics/generator-fake-string-call-review.json),
[I96](coverage/semantics/generator-folded-string-call-review.json),
[I97](coverage/semantics/generator-call-warning-fiber-review.json) and
[I98](coverage/semantics/generator-call-warning-retval-review.json).

I99 handles PHP throws during copied reference warnings, including a Fiber throw
in an owning handler-return destructor. Only the hidden copy stays request-owned;
prepared prefix and API owners release before catch. Four native originals,
three CLI comparisons and two reached fronts (237 custom/247 reported checks)
pass; one front also matches repeated native output without extra CLI credit.
The affected 59/64 trace checks and joined strict433 pass at recorded cuts.
Receive/mapping and bailout paths remain partial.
[I99 review](coverage/semantics/generator-call-cancellation-review.json).

I100 extends hidden-copy cleanup to ordinary unknown/overwritten named arguments
and required named holes. Generated Error traces retain raw arguments until the
Error is released; prepared argv and original source owners still retire in order.
Three native/source originals, one affected successful call and strict433 pass.
Two joined reached fronts pass 243 custom/253 reported checks. Original baseline,
compile and fixture failures retain zero credit. Later receives, default throws
and bailout paths remain partial.
[I100 review](coverage/semantics/generator-call-mapping-review.json).

I101 replaces required-hole-specific retention with one authenticated restored
API cursor for admitted pre-Generator receive failures. Arity, type and default
throws preserve the copy while callee cells retire before API arguments/source.
Three native/source originals, strict433, new259 custom/269 reported checks and
the affected129/134 hole recipe pass. A matching adapter and joined default134/139
gate load current434, covering changed weak-free cleanup. Baseline and fixture
parser failures retain zero credit; wider producers, collection and bailout
contexts remain partial. [I101 review](coverage/semantics/generator-call-receive-review.json).

I102 admits exit during copied reference warnings and named default construction
before Generator creation. Handler restoration, failed-constructor suppression
and ordered prepared/API cleanup keep the hidden copy through shutdown. Two
native/CLI originals, strict434 and304 custom/314 reported reached checks pass.
The joined peer loads435 and covers shared destructor return and adapter changes.
Original semantic/fixture failures retain zero credit; wider cleanup, owning
retval, Fiber and bailout paths remain partial.
[I102 review](coverage/semantics/generator-call-exit-review.json).

I103 carries ordinary exit through an owning copied-warning retval destructor,
its Child and the real C cleanup before handler/API release. The hidden copy
survives through shutdown; fake and real originals agree at exit29/41. Strict435,
author151/156 and independent joined peer192/197 pass at their recorded cuts.
Earlier interpreter, compiler, descriptor, timeout and peer fixture
elaboration failures retain zero credit. At this cut, a cleanup throw replacing
the pending exit and wider bailout remained partial.
[I103 review](coverage/semantics/generator-call-cleanup-exit-review.json).

I104 validates the existing cleanup-throw path: a supplied plain Child exception
replaces the pending exit before Generator creation. Catch/finally run, cleanup
frees retval/Child and prepared owners, and a final string exit retains status41.
The pinned native and unchanged-model source agree; joined reached153/158 checks
cover the pending transfer, owner counts and shutdown. At that cut, aliased
throws, repeated cleanup exit and wider lifecycle remained open.
[I104 review](coverage/semantics/generator-call-cleanup-throw-review.json).

I105 carries a second exit through the owning warning retval's Child and
remaining fields before copied-call CLEAN and API release. A literal string
exit keeps status29; an independent integer exit changes41 to53. Native/source
pairs, strict435 and two reached fronts (349 custom/359 reported) pass at their
recorded cuts. The unchanged-model mismatch and first author fixture failure
retain zero credit; wider nested exit, pending-Throwable, Fiber and GC paths
remain partial. [I105 review](coverage/semantics/generator-call-repeated-exit-review.json).

I106 was automatically stopped for possible cybersecurity risk; private work remains preserved, with zero integration or validation credit.

I107 validates the existing normal return after an owning copied-warning
retval and its Child/After fields retire. The handler resumes the second fresh
reference; fake and captured real copies then create and use a Generator even
after the source CV clears. Two native/model source comparisons, fake full
reached116/121 and independent real joined handoff82/87 pass. The first
fixture error and timed-out full peer retain zero credit; wider Fiber, GC and
warning cleanup remain partial.
[I107 review](coverage/semantics/generator-call-cleanup-return-review.json).

I108 admits ARRAY-packed real and fake Generator `Closure::call` through the
existing collector. Retired source arrays leave nonowning authenticated history;
canonical RAW selects named entry and freezes values through reference warnings.
The saved value gets a fresh cell despite caller-alias replacement, and deferred
inner duplicate-name errors retain warning priority and raw API traces. Five
original source agreements and independent 84/89 ownership/reference-resumption
checks pass with the full 435-module SL manifest at their recorded cuts. Computed
method names, Traversable packs and wider lifecycles remain partial.
[I108 review](coverage/semantics/generator-call-array-pack-review.json).

I109 routes native Generator named/ARRAY-packed arguments through one shared
collector, then transfers its exact receiver/value roots into the ordinary
Generator argument cursor. Case-sensitive names, pack-local ordering and early
unknown/duplicate errors preserve initialization and trace priority. Array COW,
copied reference values and a sole receiver survive source-variable retirement.
Five unique source agreements (including the positional control), one explicit
Unsupported control with zero agreement, and the final 83/88 reached gate pass
at recorded cuts with the full 436-module SL manifest. Earlier runtime, diagnostic
and fixture failures retain zero credit. Dynamic selection, Traversable inputs,
specialized delegated histories and wider lifetimes remain partial.
[I109 review](coverage/semantics/generator-method-arguments-review.json).

I110 admits literal nullsafe native Generator API calls through the existing
receiver/argument protocol. NULL skips named-CV reception and spread producers;
nonnull calls preserve their selected receiver, copied values and method-result
handoff. Ignored owning zero-argument getter copies release before the receiver,
while used copies survive. Source checks distinguish cache-destructor weak
liveness, supplied cache-destructor throws and actual empty-pack normalization.
Seven unique originals agree, one
Unsupported assertion earns zero agreement, and the 83/88 ownership gate passes
with the full 436-module SL manifest. Earlier mismatches retain zero credit.
Native API callable creation, Traversable inputs, wider delegation and lifetimes
remain partial.
[I110 review](coverage/semantics/generator-nullsafe-method-review.json).

I111 freezes computed native Generator method selection before arguments in a
nonowning receipt. Receiver/name CV rebinding cannot change the target or named
parameter mapping; exact CONFIG-to-operation transfer preserves all owners.
NULL skips both producers; invalid method-name types avoid Stringable conversion
and unknown methods fail before arguments/initialization. The prior computed
named-send Unsupported original is promoted to normal. Shared binding/__invoke
site classification keeps its truth table with disjoint clauses. Three unique
originals agree; the 97/102 ownership/authority gate, including eight pure site
views, passes with the full 437-module SL manifest. Earlier runtime and fixture
failures retain zero credit. Wider callable, Traversable, delegation and lifecycle
combinations remain partial.
[I111 review](coverage/semantics/generator-computed-method-review.json).

I112 owns native Generator API first-class captures through the existing internal
Closure child edge. Literal/computed capture and `fromCallable` preserve a Gen
after its CV retires. Invocation roots the capture and borrows its receiver,
retaining the exact argument/Throwable roots through ordinary reception. Unused
owning returns clear before capture retirement; last-capture forced close runs
Generator finally after capture weak notification. Active call authority requires a real live marker;
saved source history remains nonowning. Its earlier binding and explicit
`__invoke` boundaries are promoted by I114 and I113; the call boundary is
promoted by I115. Six unique originals agree;
the 89/94 ownership/history gate passes with the private 438-module SL manifest.
Earlier compile/fixture failures retain zero credit; wider lifecycle combinations
remain partial.
[I112 review](coverage/semantics/generator-api-capture-review.json).

I113 gives captured native Generator API `__invoke` calls their real outer
signature, argv and capture owner. Pre-handler mapping errors keep no API frame;
inner count/type errors and body traces retain both Generator and Closure frames.
The inner return stays owned through outer argv cleanup. Unused results release
before capture retirement; used uncommitted results survive it when an argument
destructor throws. Five unique originals and one affected I111 computed-call
control agree exactly. The 98/103 bounded ownership/authority gate passes with
the private 440-module SL manifest.
Earlier compile, native-fixture and abrupt mismatches keep zero credit; no core
obligation closes. [I113 review](coverage/semantics/generator-explicit-invoke-review.json).

I114 retargets captured native Generator methods through existing binding-copy
storage. The original keeps its old Generator; each new copy owns only its
replacement, with historical SOURCE metadata preserving permission after the
original retires. Binding warning/type and supplied-throw cleanup reuse the
existing native machinery. Ignored instance `bindTo` copies release before the
original receiver through a dedicated owner continuation, including nullsafe
supplied-finally throws. Six unique originals agree; the sole 132/137 unused-copy
owner/resumption front passes with the private 441-module SL manifest. A generic
fresh/started request predicate
overlap has a separate truth-preserving guard already integrated. Its captured
call boundary is promoted by I115; no core obligation closes.
[I114 review](coverage/semantics/generator-api-binding-review.json).


I115 invokes captured native Generator APIs through `Closure::call` on the frozen
replacement receiver. The original capture and replacement argument retain their
actual owners; the temporary internal function adds no heap Closure or cache
owner. Raw outer argv and copied inner arguments preserve native mapping/trace
phases. The always-used inner return survives replacement/argv cleanup; source
demand controls its release before original capture or through supplied argv
throws. Compiled SEND locations also govern callback/default undefined-CV
warnings independently of API frame lines. Seven unique originals agree; the
sole 123/128 bounded owner/forward/budget front passes full 444 SL. It does not
drive terminal cleanup. Original failures retain zero credit;
Traversable and wider lifecycle combinations remain partial.
[I115 review](coverage/semantics/generator-api-call-review.json).


I116 receives one initialized user-Iterator CV pack at ordinary literal native
Generator APIs. Selected receiver and current snapshots survive callback CV and
property replacement; finite DATA retires before API reception. Mapping errors
precede body entry, and count errors retain native frames. Cancellation preserves
the selected owner even with scalar current/no copied slots. Lookup-only history
survives receiver retirement while active cursors require real membership.
Normal genuine direct SEND pins its receiver through argv cleanup and saves
returned values separately from the retained cache through reentry and
demand-sensitive supplied throws. Six unique originals agree across their recorded cuts; the sole 99/104
owner/budget front passes full 445 SL with raw-versus-public decrement staging.
Captured/temp/borrowed/loop/startpack/from/pending-advance protocols remain
separate. Original failures and the expensive diagnostic timeout retain zero
credit; wider Traversable/lifecycle scope remains partial.
[I116 review](coverage/semantics/generator-method-iterator-pack-review.json).

I117–I120 keep an ordinary named Generator's selected SEND receiver through
body-Throwable argv cleanup. By-reference bodies require their actual328 producer
and live cached HCELL; cell/cache owners stay separate from API argv, and the
storage pin keeps Gen weak-live during cache destruction. Ordinary and nonnull
nullsafe calls retain the frozen method/receiver through argument CV rebinding;
NULL skips both producers. Pending search/Previous chaining preserve original
traces and the unassigned result, with a nonowning nullsafe tail. Five unique
originals and four separate reached owner/cache/receipt/budget fronts pass full446
SL at their recorded cuts. Shared Throwable search rules are unchanged. Active
delegation, pending initialization, reference snapshots without a live cache cell
and wider API/lifecycle modes remain partial.
[Literal review](coverage/semantics/generator-send-body-throw-review.json),
[computed review](coverage/semantics/generator-computed-send-body-throw-review.json),
[nullsafe review](coverage/semantics/generator-nullsafe-send-body-throw-review.json),
[reference-cache review](coverage/semantics/generator-reference-send-body-throw-review.json).

I121 admits an owning VALUE snapshot after the genuine by-reference yield/Notice
path and proves its separate cache, reference and API-argument owners. The actual
handler API SEND/REF carriers now preserve Notice identity and borrowed scope
before invocation. The normal R source component retains its original cut through
that API-only repair; the corrected throwing C source has its own exact cut.
Independent R107/C117 fronts pass 224 reported conditions (214 custom) over446
runtime modules plus the fixture at SL447. The original false packet and failed
diagnostics retain zero credit; wider producers/lifecycle contexts remain partial.
[Snapshot review](coverage/semantics/generator-reference-snapshot-send-body-throw-review.json).

I122 extends direct post-init SEND body-throw cleanup to registered ordinary
public instance-method by-value Generators. The actual factory This retires
during Generator close with the native SEND trace before caller-only argv
destruction; lexical/called classes, receiver/cache/argv owners, supplied Previous
and untouched result remain distinct. An authenticated descriptor view preserves
the physical pending cleanup wrapper and all owners. Static/reference/magic
producers and wider lifecycle modes remain partial.
One frozen original agrees with PHP; the 274-condition NORMAL/closed frontier
and separate 50-condition factory-budget check pass at their recorded cuts over
448 runtime modules plus fixture449. Earlier failures retain zero credit.
The joined main SL449/inventory load also passes with COMP189, ENUM143 and
CLASS200; its shared record adds no source-agreement credit.
[Instance-method review](coverage/semantics/generator-instance-send-body-throw-review.json).

I123 admits ordinary public static by-value Generator methods through exact
descriptor/source static-flag equality in the same physical-method certificate.
An object-CV selector retires before initialization; the actual frame keeps its
distinct lexical/called classes without This or receiver owners. Pending frame,
cache and argv retain the existing direct SEND body-throw cleanup and budget law.
Reference/magic/captured/delegated producers, incoming throw, pending initialization
and held I106 remain separate.
One frozen original agrees with PHP; the actual static-frame/cleanup/budget
front passes 223 conditions across 449 runtime modules plus fixture450. Source
flags, absent receiver ownership and malformed-state refusals are independently
reviewed; the instance case retains its original evidence without replay.
[Static-method review](coverage/semantics/generator-static-send-body-throw-review.json).

I124 admits ordinary public instance/static reference-Generator SEND body throws
through source/signature BYREF agreement and their actual live ordinary Module 328
REFCELL, before storage consumption. CELL/cache/argv and instance This retain
separate owners; the static selector can retire before initialization. Existing
static/source authority remains exact. VALUE/Notice, typed/backed/borrowed cells,
capture/delegation, incoming throw, pending initialization, Closure::call and
held I106 remain separate.
Two frozen originals agree with PHP; paired instance/static fronts pass
393 custom/403 reported conditions across 449 runtime modules plus fixture450,
with actual CELL/cache/argv/This owners, source guards and budget continuation.
[Method-reference review](coverage/semantics/generator-method-reference-send-body-throw-review.json).

I125 connects borrowed Aggregate getIterator/return authority to post-init,
nondelegated literal Generator SEND and zero-argument APIs. An initialized
ordinary user Iterator supplies DATA; selected Gen and copied argv survive
source-CV rebinding, while INPUT/producer history adds no Aggregate owner.
DATA retires before reception, mapping errors precede the API, and count or
ordinary USER-call body TypeErrors keep their actual trace frames. One shared
return-admission hook defaults to true for old consumers and leaves effective
BYREF current explicit Unsupported before promotion on this route.
Generator-returning Aggregates, typed/borrowed current, incoming throw, pending
initialization, capture, delegation, Closure::call, held I106 and wider packs
remain separate.
Four frozen originals agree with PHP; the actual getter/return/copy/cleanup and
public-budget frontier passes 271 conditions across 449 runtime modules plus
fixture450. The constructed BYREF refusal has no native agreement credit.
All selections pass on their first attempt; existing cleanup law is reused.
[Aggregate reception review](coverage/semantics/generator-aggregate-arguments-review.json).

I126 connects existing direct named by-value Generator-CV traversal to literal
native Generator SEND and zero-argument reception, with distinct initialized
nondelegated source/selected Generators. The actual CONFIG marker supplies the
receiver root; borrowed source rewind/next keeps real DATA/cache ownership.
Quiet source retirement and retained owning caches keep their existing limits,
including the unchanged pending-destructor value guard.
Pending mapping cleanup transfers selected Gen/copied argv into CONFIG_INVOKE
before releasing DATA; ordinary throw cleanup then retires that real cursor.
Old INI/numeric owner checks and source/value/storage policy remain unchanged.
BYREF/typed/borrowed cells, temporary/Aggregate sources, incoming throw, pending
initialization, capture/delegation, Closure::call and I106 remain held.
Frozen native selections cover scalar normal, quiet retained cache/body TypeError,
mapping and count. Four maintained source agreements retain separate scalar and
affected/unrun cuts; the destructor-bearing payload refusal and failed selection
have zero credit. Separate scalar/quiet-cache/mapping fronts pass 430 conditions
(208/134/88) across 450 runtime modules plus fixture451 per case. Real borrowed
source, cache/argv roots, direct quiet transfers and public budgets are checked;
initial front/diagnostic fixture failures retain zero credit. The actual current
451-module joined load/inventory also pass without renewing source cuts.
[Generator-source review](coverage/semantics/generator-source-arguments-review.json).

I127 connects existing computed/nullsafe selected-method authority to admitted
single-CV Iterator, Aggregate-to-Iterator and initialized named by-value
Generator packs. Shared source/selection proof keeps method/receiver identity
fixed through callback rebinding while actual CONFIG roots own selected Gen
and argv; NULL skips method and pack reads. New paths stay post-init,
nondelegated/by-value and exclude captured/temporary selectors and held modes.
Callback reentry and wider destructor histories stay outside this join.
Producer/value/owner policies and old ordinary literal admission remain intact;
new direct Iterator current is by-value. Module 447 reuses existing argument domains
and 280/450 receipt minting/liveness. A defaulted 420 cancellation dispatch keeps
the actual native receiver/prefix in CONFIG_INVOKE while key/current/DATA retire,
including the equivalent admitted literal root shape; old INI/value policy stays.
Native nullsafe CONFIG descriptors advance tail validation to the outer callsite
while physical origins/tasks/owners remain unchanged. Six maintained source
contrasts agree at separate first-four and affected/unrun cuts. Independent
623 conditions pass as retained Iterator169 plus affected/unrun
Aggregate190/Generator160/mapping104 at separate cuts. Public descriptors,
physical selected/cursor/argv roots and 0/1 budgets pass. The actual current
453-module joined load/inventory also pass. Pre-semantic failures, the genuine
mapping cleanup-order mismatch, failed frontier selections and the bounded
descriptor diagnostic retain zero credit.
[Selected Traversable review](coverage/semantics/generator-computed-traversable-arguments-review.json).

I128 removes the artificial two-item prefix limit for the existing named
by-value Generator CV source at authenticated native Generator consumers.
The shared consumer policy leaves old INI bounds exact; item/source/value,
real DATA/receiver/copied-prefix owners and borrowed-resume laws remain intact.
One-CV syntax and held producer/value/lifecycle modes do not widen. Four frozen
native contrasts pass: scalar fourth-item count, source throw after owning
prefix3, fourth-key mapping failure and distinct owning prefix3/cache/trace
retirement. Four exact source comparisons and 363 independent conditions also
pass first attempt, covering actual third/fourth appends, INI controls,
borrowed/pending/count/cache roots and public 0/1 budgets. The actual current
453-module joined load/inventory also pass. Wider core remains partial.
[Finite-prefix review](coverage/semantics/generator-finite-prefix-arguments-review.json).

I129 composes ordinary positional arguments with one terminal simple-CV
Traversable at admitted native Generator consumers. Real argument-index and
ordinary-SENT replay preserve frozen earlier values through callbacks; terminal
DATA/finish/pending paths use their actual source position. Generator roots
count normalized earlier/new argv once and preserve old root order. INI,
prefix-free and producer/value/lifetime bounds remain intact; ARRAY prefixes,
multiple Traversables and held modes do not widen. Native4 plus one focused
scalar witness pass. The first owning-prefix/empty Iterator SEND source agrees
at its authentic cut; remaining Aggregate/Gen/count/scalar comparisons also pass.
Five source agreements retain first/remainder cuts without replay. Independent
566 owner/index/budget conditions pass as retained401 plus corrected/unrun165;
the raw-count fixture phase error and failed containing selection retain zero credit.
The actual current 454-module joined load/inventory also pass, without source/state replay.
[Positional-prefix review](coverage/semantics/generator-prefixed-traversable-arguments-review.json).

I130 joins Fiber transfer to the existing named by-value Generator-CV argument
source during authentic borrowed NEXT. One local saved-frame proof reuses
CONFIG/source authority and existing VM ownership/unique-resumer checks, without
new roots or PARKED mutation. DATA/selected/prior+copied argv roots stay distinct
from the source VALUE cache. Unfinished copied native calls now release argv
before receiver in actual pre-API throw context. Three native-first sources
agree at separate retained/corrected cuts; independent N169 plus focused T138
compose307 conditions without a full307 rerun. The original ordering mismatch,
superseded T prototypes and diagnostic timeouts retain zero credit. Current456
joined load/inventory pass with a scoped195/196/GC65 compatibility bridge.
Source/value/CV/last-DATA and held-mode bounds remain. Existing helper,
Fiber-Throwable and guarded-close paths have common-law review, without new
direct source credit. Early noncopied cursor retirement has its separate I131
scope below.
[Borrowed-source Fiber review](coverage/semantics/generator-borrowed-fiber-arguments-review.json).

I131 extends argv-before-receiver retirement to actual early CONFIG_SEND/PREP
at admitted native Generator ordinary-prefix/terminal-CV calls. Exact partial
source replay preserves frozen SENT without reading a future pack. A throwing
operational producer now retains its real cursor until Search transfers prior
argv then receiver into the existing eager queue. No DATA is acquired and no
source/value/root/schema or held mode changes. Two native-first originals and
two source comparisons agree: scalar pack TypeError precedes zero-arg API count;
a later no-arg argument throw skips an undefined local pack. Both preserve
original trace/Previous/sentinel and release prior argv before Gen finally.
Independent PREP97+SEND80=177 actual source/retention/owner/queue/budget checks
pass first attempt. Original pre-retention mismatch and diagnostics retain zero
credit. Actual current457 joined load/inventory pass without source/front replay.
Other task/array-ledger/producer/default policies stay unchanged.
[Early-cursor review](coverage/semantics/generator-early-cursor-cleanup-review.json).

I132 replaces the outside-callee-owner assumption during native Generator
Aggregate acquisition with proof of the actual PREP/CONFIG_AGGREGATE marker.
The borrowed Aggregate retains its real owner; ordinary Iterator return still
transfers RESULT into DATA once. Native cancellation transfers prior SENT before
receiver in both operational and ordinary contexts, through the existing real
Search queue. INI-only Generator returns and producer/value/frame policies stay
unchanged. Native3 and source3 pass first attempt: normal getter rebinding/return,
supplied getter exception in a named Fiber, and return-type failure outside one.
Independent N99/E81/T78=258 owner/promotion/cancellation/public-budget checks
pass. Existing pending-cleanup activation validates queued jobs after ordinary
entry; one fixture type-check stop retains zero credit. Actual current459 joined
interface load/inventory pass; no source/front replay.
[Aggregate acquisition review](coverage/semantics/generator-aggregate-acquisition-review.json).

I133 authenticates saved direct-Iterator cursor history while its callback runs
the already selected initialized Gen via `next`/`send`. One real resumer proof
and a finite ordinary named-helper fold authorize only the saved callback/cursor
phase view; runtime state, complete graph and global owner checks stay real.
Entry PAUSED/CLOSED and existing selection/source/value/held policies are exact.
Two source agreements pass at separate retained-N/corrected-E cuts; independent
N120/E121=241 ownership/phase/graph/budget checks pass. The elaboration stop and count-only observer
Unsupported retain zero credit. Actual current461 shared-interface load/inventory
pass without source/front or older replay.
[Iterator reentry review](coverage/semantics/generator-iterator-reentry-review.json).

I134 connects two actual running Generators during native argument collection:
borrowed source NEXT invokes selected next/send. A default-old423 operation-frame
scope and local447 dual-pair/source proof authorize only saved target phase
history; both physical IDs/roots and global pair checks remain real. Source
CV/cache/DATA, ordinary-prefix/value and final cleanup bounds are unchanged.
Native2/source2 and independent N135/E139=274 phase/pair/ownership/budget checks
pass first attempt. The current load of 461 modules and inventory pass at the
accepted main cut; private source/front cuts remain separate.
No I133 or older campaign is replayed; Fiber transfer rules and all holds remain.
[Source reentry review](coverage/semantics/generator-source-reentry-review.json).

I135 adds the remaining borrowed Aggregate-getter reentry endpoint: selected
next/send may run before normal Iterator DATA or getter failure. The existing
real singleton/frame proof and phase-only view are reused; the Aggregate's real
allocation/positive owner remains mandatory. Literal-prefix0 and computed/prefix
calls share this law. Native2/source2 and independent N138/E93=231
phase/ownership/return/budget checks pass first attempt. The current integration
uses a narrow absence/default bridge without a new load or semantic replay. No older replay, new root, source/value/INI-Gen
return or Fiber/held-mode expansion is introduced.
[Aggregate reentry review](coverage/semantics/generator-aggregate-reentry-review.json).

I136 adds source-authenticated public USER method helper links to the existing
singleton Fiber and Iterator/Aggregate/source-Generator reentry walks. Helpers
return by value; ordinary parameter/source/storage policies are unchanged.
Immutable simple-CV instance or receiver-free scoped-static callsites preserve
real method receiver roots across rebinding and VM movement. A real validation
cycle is cut by checking the cursor head before the body proof; necessary saved-ID
checks run before deeper helper proofs without changing accepted endpoints.
Two maintained native/model agreements compose authentic N909 and lean-Ef9 cuts.
One complete focused packet passes 161 conditions (parked VM 86, dual reentry 75)
at private462 plus fixture463. Accepted source cuts retain later return/catch and
retirement observations; repeated validators and later seeks are omitted.
Original timeouts, fixture stops and diagnostics retain zero credit, including
the earlier whole237 timeout. The named-function fallback and all source/value/
held domains remain. Other This/object-static/receiver-bearing scoped helper
sources gain no new proof here; no older campaign is replayed. One actual current
466-module shared-interface load passes at `7715a03b0` with inventory 169/306;
that load adds no source-agreement credit.
[Method-helper review](coverage/semantics/generator-method-helper-reentry-review.json).

I137 closes receiver-free object-form static USER helper links in the existing
Generator reentry and Fiber walks. One disjoint late447 classifier arm reuses
physical public/static/by-value-return method and immutable simple-CV source
proofs; no selector is reread or retained. Native2 distinguishes preargument
selector death, inherited lexical/called-class identity through normal parking,
and static helper links before/inside borrowed-source reentry with a Given throw.
Both exact source comparisons and the independent180 focused conditions pass
first attempt at private467 plus fixture468. Actual preclear selector1→parked/
dual0, cached classes, source/pairs/phase graph and public0/1 cuts are checked.
The three executable/test commits are accepted at `37e293f57` without another
load or semantic replay. All old helper guards, real roots, source/value and
parked-operation bounds remain.
[Object-static helper review](coverage/semantics/generator-object-static-helper-review.json).

I138 admits raw uncaptured static Closure helper contexts in the existing four
Generator reentry/Fiber walks. Matching TARGET/FUNCTION/INSTANCE and physical
empty, unbound template source preserve the real call-instance owner after CV
clearing. Both allocated static cells and latent function-static code are
excluded; all current/saved/source/tail/ID/transfer guards stay unchanged.
Native2/source2 and complete independent164 actual INSTANCE/parked-VM/dual-source/
budget conditions pass first attempt at private468 plus fixture469. The exact
executable/test packet is accepted at `5ecf29066` with a narrow actual-current
absence/default bridge. An already-READY shared469-module load passes at that
cut separately, with zero source credit and no standalone I138 replay. No capture/
binding/arrow/fake/Closure::call or other held mode is reopened.
[Raw Closure helper review](coverage/semantics/generator-raw-closure-helper-review.json).

I139 authenticates a parked Iterator cursor while an external ordinary resumer
runs its selected Generator, including reactivation from an admitted actor Fiber.
Snapshot/full-cursor authority supplies a descriptor phase view; old physical
entry, real VM roots, transfer and global-ID checks remain intact. Actual consumed
cursor and eager-operation continuations retain existing cancellation rules.
Source agreement composes unchanged N at `b34665291` with actor-Fiber E at
`dbf6f3cdc`; original main-hosted E Unsupported and two elaboration stops retain
zero credit. Retained N76 at `e92fedae7` plus affected E97 at `cb6037386` compose
173 conditions at private469 plus fixture470, with no full current rerun. A
one-premise saved-ID fallback guard removes a duplicate singleton derivation,
retaining every previously defined result. Earlier failed selections retain zero credit.
The exact packet is accepted at `79ce60a0e`; its actual shared472-module load
passes separately with zero source credit. Private469/fixture470 cuts stay exact.
[Parked-cursor review](coverage/semantics/generator-parked-cursor-reentry-review.json).



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

GC61 corrects generic TEMP receipt progress: a replacement consumes the old
receipt only when its new queue is exactly the old head's tail. Storage cleanup
can retain the next queued TEMP without advancing either single or ordered-list
receipt metadata. Actual pop, storage and decrement behavior use existing rules;
no source/array whitelist, schema, phase or collector policy changes.
Two supported originals and the motivating ATTR63 expression agree with native;
one 137-condition (132 authored) strict450 front passes. The original failure
and diagnostic/control preparations remain external with zero new credit.
[TEMP-consumption review](coverage/semantics/gc-temp-release-consumption-review.json).

GC68 separates positive unmatched native-RC units from physical heap ownership.
A normal root function-string query can replace the exact sent NAME cell's
eligible callback-written object with its saved string while retaining
one native count and scheduling no decrement. Weak-reference recovery, genuine
temporary release, GC trial protection/snapshots, pruning and store shutdown use
the effective count; actual retirement removes the units. Empty excess preserves
old behavior, and wider raw overwrites remain explicit. The retained original
matches native weak-live/collection-zero/shutdown order; the focused independent
front passes 208 reported / 203 authored conditions at its private 461-module cut.
The authentic current 462-module load passes separately.
[Native-count review](coverage/semantics/gc-native-rc-excess-review.json).
Finite public untyped DIRECT scalar/fieldless-Child slots now share this query
admission. The Parent's unit protects its actual descendant closure without
crediting Children or copying their repeated edges. Store callbacks follow
allocation order while the Parent and its fields remain live, separating this
case from standard last-owner slot cleanup. Generic count, release, GC and
shutdown rules are unchanged.
Two allocation-order originals and the focused 213-condition front (208 authored)
pass at exact private462 cuts; current acceptance uses a separate static bridge.
[Property-graph review](coverage/semantics/gc-native-rc-property-graph-review.json).
Reference-copy decisions now keep those native-retained Parent edges in their
pruned ownership views. A property reference and array entry remain two real
HCELL owners, so COW and unpack preserve the alias and writes reach both original
storage places. Only the two read-only prune images change; physical cell counts,
singleton/source-self rules, COW thresholds and all producers remain unchanged.
Two exact originals and the focused 154-condition front (149 authored) pass at
their recorded 463-module cuts; the original wrong normal result stays zero.
[Reference-copy review](coverage/semantics/gc-hidden-reference-copy-review.json).
Raw NAME commitment also admits flat mutable DIRECT arrays with an actual
distinct retained root CV, existing quiet scalars and fieldless Children. Losing
the sent-cell edge reduces physical owners from two to one while the native count
stays two through an old-header unit. Separation creates a new header
with zero excess and real copied Child edges; the hidden original survives visible
replacement/removal and collection. An exact source/image receipt keeps the
old-header `GC_TRY_DELREF` out of candidate visits while ordinary item decrements
remain intact. Old object/abrupt paths and physical owner graphs remain unchanged.
Two originals retain their private 463-module cuts through the reviewed observation
bridge; the final 322-condition front (317 authored) and actual joined SL465 load pass.
[Array-COW review](coverage/semantics/gc-array-native-cow-review.json).
The existing retained DIRECT-array domain also supports ordinary item-reference
acquisition. Native-count separation leaves the old DIRECT row/unit unchanged;
the new ALIAS owns a fresh CELL once, with a NULL acquisition result. The exact
ACQUIRE_ARRAY receipt reuses old-header TEMP consumption without a GC visit.
Ordinary REF_NAME binding, later writes and visible-array cleanup stay unchanged.
Two originals retain their genuine pre-edit/patched console cuts through the
observation bridge. The 306-condition front (301 authored) and actual joined
SL466 load pass at their separate recorded revisions.
[Item-reference review](coverage/semantics/gc-item-reference-cow-review.json).
Quiet scalar ALIAS leaves now share the retained-array raw-NAME fold. Genuine
untyped reference metadata excludes backing, coercion, literal-debt and released
history; CELL excess remains zero. Existing duplication unwraps physical
singleton cells and preserves shared aliases. A disjoint clone/write image
accounts for scalar STORE-through without replacing the shared entry binding;
old DIRECT and generic count/reference rules remain unchanged.
Two exact originals and 321 independent conditions (311 authored) pass at their
recorded private 466-module cuts. The shared fixture syntax stop retains zero;
its corrected affected facet passes without replaying the unchanged singleton.
The separate current combined SL467 load passes with zero source credit.
[Scalar-reference review](coverage/semantics/gc-scalar-alias-cow-review.json).
GC74 accounts for the existing-domain DIRECT target copied then overwritten
during retained-array COW. Exact source/clone/STORE images supply its transient
nonlast decrement to existing GC buffering; the old-header TEMP receipt,
physical ownership and ordinary same-table release rules remain unchanged.
The focused 230-condition front (225 authored) passes at private SL467. Two
originals retain console/status matches with zero complete-behavior credit:
the author comparison precedes the fix, and the peer retains a separate raw
borrowed-root header-buffer mismatch at that recorded cut.
The separate current combined SL468 load passes with zero source credit.
[Copied-target review](coverage/semantics/gc-copied-target-decrement-review.json).
Current array/reference coverage distinguishes borrowed lookup from real
reference/header loss. Source-authenticated ROOT/CV lookup suppresses only its
borrowed visit, while variable self-assignment, ELEMENT writes and genuine Child
VALUE decrements remain. An unused AssignRef's modeled result protector uses TEMP
at every admitted positive owner count: one edge is consumed, leaving at least
the real array and destination CV. Existing-CV rebinding to the same array CELL
keeps its genuine binding-time visit, separate from unused-result disposal;
real reference-CV removal retains ordinary VALUE checks. The
[borrowed-root](coverage/semantics/gc-borrowed-array-writeback-review.json) and
[unused-result](coverage/semantics/gc-unused-reference-result-review.json) reviews
retain historical labels; the
[owner-count review](coverage/semantics/gc-unused-reference-owner-count-review.json)
records the current law and two superseded count-only control updates.

Retained unit1 arrays support singleton/shared owning ALIA, real nonlast payload
loss and last-Child callbacks with actual saved-root authority. Copied DIRECT
siblings that hide a payload drop contribute one inferred decrement. Header-first
TEMP remains separate from real item VALUE; positive remaining header owners use
native progress and exact one-pop suffixes. COW deletion checks only its copied
selected item and derives ROOT independently of scratch CELL. Generic counts,
physical owners and task types stay unchanged. Scope and separate validation cuts
remain in the [owning-alias](coverage/semantics/gc-owning-alias-cow-review.json),
[header-owner](coverage/semantics/gc-shared-header-owner-review.json) and
[deletion](coverage/semantics/gc-array-unset-copy-review.json) reviews.

Ordinary zero-unit DIRECT and quiet-scalar ALIA arrays use that nonvisiting
header law only with a distinct surviving compiled-CV old view and explicit
source/data/history/HELD/GC bounds. Singleton wrappers unwrap in the new table;
shared/repeated CELLs preserve real entry multiplicity and scalar write-through.
A separate zero-only image and pre-domain guard reject owning-to-quiet receipt
escape. Later genuine last-view ARRAY/CELL cleanup retires storage and can invoke
Child D before shutdown. Quiet-ALIA item-reference acquisition now separates
fresh versus reused CELL images: singleton copying unwraps before one new CELL
is allocated, while shared copying reuses its marked CELL without STORE append
or REFCELLS change. Acquisition borrows CELL with NULL; later reference-CV
binding/removal keeps its existing result and VALUE laws. Owning ALIA acquisition,
zero-unit owning callbacks and held contexts retain their separate bounds.
See [DIRECT COW](coverage/semantics/gc-ordinary-direct-cow-review.json),
[quiet-ALIA writes](coverage/semantics/gc-ordinary-quiet-alias-review.json) and
[quiet acquisition](coverage/semantics/gc-ordinary-alias-reference-review.json).
Without objects, references or active destructor machinery, finite DIRECT scalar
array graphs use the quiet observer. Replacing an outer item checks its copied
selected table; a scalar write through two integer dimensions separates both
headers without visiting either. Repeated sharing keeps real child-edge multiplicity;
ordinary later deletion and last-view retirement retain their decrements. The
[root-copy](coverage/semantics/gc-quiet-scalar-array-dag-review.json) and
[nested-copy](coverage/semantics/gc-nested-scalar-array-cow-review.json) reviews
retain separate cuts. The latest nested cut has two first complete originals and
whole 221/211 checks at private 484; accepted 71f/485 uses a static composition note.
The preceding 257f/485 load has source credit zero and predates that fix. Earlier
source/state, partial/failure and load labels remain in their linked ledgers;
historical GC76 198/193 is not rerun or promoted.

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

GC27 admits finite direct capture graphs with at least two mutable array
occurrences under the same authenticated active Closure root. Distinct arrays
may share childless stdClass leaves; repeated array captures retain each owner
with at most one candidate slot per identity. Three originals agree exactly,
including a reordered three-array graph with an unrelated direct leaf and final weak death.
Three strict D-state groups pass 204+146+193 assertions, independent review
passes 73, and both affected GC26 groups pass 148. Nested, reference, proxy and finalizer graphs
remain partial; the hidden Closure capture table remains black under the real
caller root. [GC27 review](coverage/semantics/gc-multi-array-review.json).

GC28 admits finite nested DIRECT-array capture DAGs under the same real Closure
root. Unique traversal preserves repeated owner/trace edges; per-array self-reach
rejects forged DIRECT cycles, and the nested-edge guard is component-local.
Shared depth-three nesting, local parent/child COW and an independent self-copy
snapshot give three exact source pairs through final weak death. Strict reached fronts pass 246+191 assertions and the
changed GC27 group passes 207. Independent graph/self-copy fronts pass 63+85.
Reference, proxy, pooled and finalizer graphs remain partial.
[GC28 review](coverage/semantics/gc-nested-array-review.json).

GC29 admits mixed value/reference captures through ordinary untyped HCELLs.
Capture/local aliases own wrappers separately while each wrapper owns its payload
once; surviving reference decrements buffer only a collectable payload. Three
originals preserve shared/separate wrapper lifetime and request-string rebinding,
and one combined A95 original preserves old-cell 22/global 44 through Generator
retirement and actual GC. All four agree; strict reached fronts pass 177+197+154.
Independent mixed COW gives a fifth exact source and 214 further assertions.
Constrained/backed cells, ALIAS array entries
and arbitrary reference/Closure cycles remain partial.
[GC29 review](coverage/semantics/gc-reference-capture-review.json).

GC30 adds quiet inactive WeakReference unregister and standard notification in
terminal cleanup. The association view preserves owning edges while ordinary
field releases/C guards update the local heap; real handle order preserves fast
field shielding and inactive-destructor failure. Eight exact source/request
contexts include all three unchanged OB10 originals on their actual canonical
composition. Author206 and independent341 strict conditions pass. Map/custom
notification remained partial at that cut. [GC30 review](coverage/semantics/gc-inactive-weak-free-review.json).

GC31 adds inactive WeakMap free with all-key unregister before ordered value
release. Later value leases and shared ALIAS payload ownership survive correctly;
retired Maps no longer force unrelated key-field cleanup. Seven exact source/request
contexts cover empty/singleton/multi-entry Maps, AB/BA fatal order, fast/slow alias
cells and an independent all-unregister-before-value discriminator. Author292,
peer172 and affected GC30 HIGHER135 pass (599 total); two key-notification
Unsupported controls retain zero agreement at their original cuts. Key/incoming-Map
notification and active free pins remained partial at that cut. [GC31 review](coverage/semantics/gc-inactive-weakmap-free-review.json).

GC32 adds inactive standard-Key notification before fields. Per-Key registration
rank and surviving value-slot position preserve selective entry removal, duplicate
owners and later Map order; nested notifications retain pending entry/field owners.
Nine exact contexts (eight programs) include the two promoted GC31 originals,
fast/nonfast reference cells and an independent nonadjacent-duplicate discriminator.
Author359, independent208 and affected384 conditions pass (951 reported), with
strict434 at recorded cuts. Original Unsupported, binding/elaboration failures and
the wrong-W first draft retain zero credit. Internal/custom key hooks and active
free pins remained partial at that cut. [GC32 review](coverage/semantics/gc-key-notify-review.json).

GC33 composes inactive internal-Key hooks: WeakReference unregisters its referent
before incoming Map values; WeakMap unregisters outgoing keys and releases own
values before incoming notification. Shared values, self-keys and two incoming
Maps preserve separate owners and registration order. Nine exact positive
contexts/eight programs include nonfast table retirement; at that cut, three
ordinary unset controls stopped before generic retirement with zero agreement.
Author495, independent51 and affected320 conditions pass (866 reported), with
strict435 at recorded cuts. Original source/fixture failures remain zero credit.
Later producer policies, ordinary callback continuations, weak Closure keys and
active free pins remain partial. [GC33 review](coverage/semantics/gc-compound-key-review.json).

GC34 adds ordinary internal-Key callback continuations. Quiet registrations
activate cleanup; per-entry leases and parent/Key pins survive nested throws.
Wrapper unregister precedes incoming callbacks, while Map own values run first;
authenticated callbacks preserve or replace their weak observer. Fourteen exact
normal programs and 464 reported conditions (author233, independent86, affected145)
pass at recorded cuts. The three GC33 ordinary controls are promoted; earlier
mismatch/timeout/fixture stops retain zero credit. Wider producers, freeing-object
escape/mutation and active-pin collection remain partial.
[GC34 review](coverage/semantics/gc-ordinary-key-review.json).

GC36 admits one direct destructor-child property on an ordinary `stdClass`
WeakMap Key, attached before or after first insertion. The physical Key pin keeps
the field owner through Map value cleanup; wrapper registration order changes
Value callback visibility, and Key child release follows weak notification.
Six fresh normal source programs agree (author2, independent4), including a
throwing Value caught after Child cleanup. Author102 and independent70 reached
conditions plus an affected GC32 exact source and 71 reached conditions pass at
their recorded cuts. A two-field producer remains Unsupported with zero agreement;
the original baseline and fixture failures retain zero credit. Wider layouts,
multiple Maps, freeing-object mutation and active-pin collection remain partial.
[GC36 review](coverage/semantics/gc-standard-key-field-review.json).

GC37 admits a methodless user WeakMap Value with one public untyped declared
property owning a child before first insertion into an empty Map. The leaf
`stdClass` Key's retirement removes the Map edge, makes the Value observer's get
null, then releases its sole child through the ordinary storage pin.
Three new exact programs include a caught Child destructor throw; three affected
post-insertion/GC36 sources and 90 source-reached conditions (author46,
independent44) pass at recorded cuts. At the GC37 cut, occupied replacement was
Unsupported; that historical control retains zero agreement. Wider Value
layouts, extra child owners,
Map-first teardown and active-pin collection remain partial.
[GC37 review](coverage/semantics/gc-declared-value-child-review.json).

GC38 admits ordinary Map-first retirement of the GC37 one-declared-Child
Value while its leaf `stdClass` Key remains live. The Map unregisters its Key
and transfers its Value owner before the Value releases Child. During Child's
destructor, the Value observer's get is null while the Map observer's get is
still live under the Map storage pin. The new free arm requires no incoming
Map-key registrations; the existing leaf-Value free path remains available.
Three new exact sources (including caught Child throw), two affected exact
sources and 97 reached conditions (author57, independent40) pass at recorded
cuts. Retained Child owners and incoming Map-key registration stop explicitly
with zero agreement. Wider Value layouts and active-pin collection remain
partial; earlier fixture/source drafts retain zero credit.
[GC38 review](coverage/semantics/gc-map-first-value-child-review.json).

GC39 admits ordinary Map-first retirement of a one-declared-Child Value whose
Child has two physical owners: the Value property and one other strong owner.
The Map is the Value's sole owner and has no incoming Map-key registration.
In the tested outside-CV source, Map and Value weak gets become null after
teardown while Child stays live; unsetting that owner later runs its destructor.
The new arm leaves GC37 insertion, GC38 sole-owned Child cleanup and
replacement/foreach unchanged.
Two fresh exact sources (one caught Child throw), two affected exact sources,
and 96 reached conditions (author62, independent34) pass at recorded cuts. At
the GC39 cut, an owner-three Child was Unsupported with zero agreement. Wider
ownership graphs and active-pin collection remain partial; the baseline and
early fixture elaboration failures retain zero credit.
[GC39 review](coverage/semantics/gc-map-first-retained-child-review.json).

Safe scalars, finite methodless objects and finite direct-array graphs share
WeakMap payload validation across insertion,
ordinary leaf-Key append, occupied replacement, reads/explicit entry removal from
multiple-entry tables,
singleton/multiple-entry Map retirement and selective Key notification. Safe
null/bool/int/validated startup strings and binary64 floats add no heap edge.
Object payloads have
public untyped nonstatic/nonreadonly backed slots containing primitives,
fieldless destructor Children or one direct array of those leaves; matching
identities and keys fix declaration order. Ordered jobs preserve repeated Value
and Child edges, outside owners and later cleanup after a Child throw. Backed
storage clears without hook dispatch; used results, temporary producers and
clones retain their existing evaluation and owner transfers. Direct fetches
and used coalescing results add actual Value owners; terminal isset/empty borrow
storage. These many-table reads keep existing source/key authority, require a
nonfreeing input Key. Explicit offsetUnset now shares the same guard and
existing detach/release executor. Missing-Key bool/coalescing/Error behavior is unchanged.
Two new originals and one 73-condition spare-Key reached group pass at their
separate cuts; the native-checked variant adds no original agreement.
[Read review](coverage/semantics/gc-finite-value-reads-review.json).
The finite fallback now explicitly excludes the old storage selector, fixing
an overlapping-success regression on leaf-many access. A fresh comparison of
the exact legacy M141 separate-leaf original passes; its repair entry in that
review retains the separate tested cut and reports.

Explicit removal unlinks the entry before Child cleanup. A fetched Value owner
can delay all property cleanup; otherwise the removed Value job precedes the
consumed selected-Key job, keeping a returned Key live through callbacks even
after its outside CV was cleared. Supplied Child throws preserve later fields,
Throwable identity/creation trace and the skipped next-statement marker. Two
new originals and one 102-condition reached group pass at their recorded cuts;
the original overlap failure and old baseline keep zero credit.
[Explicit-removal review](coverage/semantics/gc-finite-value-unset-review.json).

Occupied singleton and multiple-entry writes publish the new slot before old
Value cleanup, preserving registration/order. A fetched old Value owner delays
its Children; immediate Child throws preserve supplied/fresh traces and skip
the outer result assignment after RHS rebinding. Same-identity replacement
records the native old-zval GC visit despite unchanged Value/Child owner counts.
The old writer domains remain disjoint and authoritative.
Three new originals agree exactly and one 71-condition source-reached group
passes. The supplemental native-only roots probe adds no source agreement;
the original baseline and initial independent timeout retain zero credit.
[Replacement review](coverage/semantics/gc-finite-value-replacement-review.json).

The shared payload policy permits scalar/object mixtures throughout those
consumers. Present-row predicates borrow the actual stored value: isset tests
NULL and empty tests truth, so false/zero differ from NULL. The initial GC49
object-only predicate and two state-fixture setup failures retain zero
credit. Mixed replacement, retained-owner, unset/append, Key notification and
Map retirement evidence are bound in the
[mixed-payload review](coverage/semantics/gc-mixed-scalar-finite-review.json).
Three new originals agree exactly and one 89-condition ownership/default group
passes at its recorded cut; constructed counterstates add no PHP agreement.

Validated float entries preserve negative zero, NaN and infinity through
ordinary storage/copies and cleanup. NaN empty warns before rereading the
selected row's numeric word, including a warning handler's same-row update and
reentry. The borrowed continuation preserves original operands and source/caller
authority, with no new Value or receiver owner; structural mutation/free is
fenced across old/new paths. Current float/long words use the pinned 64-bit
representation, while other post-warning tags stop explicitly. Property-float
validation delegates to the same bound without a duplicate success arm.
Two originals agree exactly and one 93-condition handler-write front passes;
[float-payload review](coverage/semantics/gc-float-payload-review.json) retains
the failed setup/dispatch cuts with zero credit.

Public typed float-property NaN warnings also retain their selected borrowed
receiver through authenticated API callback argument delivery. A handler can
write the captured slot and rebind the original CV; the result still reads that
slot. One unchanged original and one 82-condition cursor/ownership/resumption
front pass. The old interpreter failure keeps zero credit; WeakMap rules and
their evidence remain unchanged.
[Property cursor repair](coverage/semantics/gc-property-nan-cursor-review.json).

Root arrays form finite acyclic DIRECT graphs over the existing scalar/object
leaves. Branch-local ancestor paths reject cycles while admitting shared children;
property arrays keep their separate one-layer policy. Fetched arrays retain real
table owners across Key death, and COW creates separate physical edges. Ordered
retirement transfers each edge to a job without copying descendants. The earlier
[flat-array cut](coverage/semantics/gc-direct-array-payload-review.json) retains its
99-condition record; its constructed nested-root refusal is promoted and retired
from the current fixture without rerunning that campaign.
Two nested-array originals agree exactly and one 93-condition front passes:
outer retirement transfers two jobs for the same inner table, then an actual
inner owner2-to1 release leaves Value/Child edges unchanged. Cycle, ALIAS and
property-layer counterstates add no PHP agreement; the old baseline remains zero.
[Nested-array review](coverage/semantics/gc-nested-array-payload-review.json).

Ordinary leaf `stdClass` Keys can register across canonical Maps using the same
finite payload policy. A nonrecursive fold checks actual associated tables and
registration ranks; ordinary reads, occupied writes and explicit unset inherit
that validation. Selective Map retirement removes only its registrations and
Value/HARRAY owners. Key retirement transfers one slot at a time to ordered
release jobs under the exact retiring-Key pin. A later wrapper stays weak-live
through every preceding registration's cleanup; an already-delivered wrapper
stays weak-null through finite continuation. The other Keys and Maps remain
nonfreeing, with no active cursor or incoming Map-key association. Existing
leaf/reference, callback, singleton and cursor policies keep their prior domains.
Two originals agree exactly, and one front passes 144 conditions across real
pending/delivered-wrapper selections. The preserved early-wrapper source supplies
the second selection and adds no original differential credit.
[Shared-Key review](coverage/semantics/gc-shared-key-finite-review.json).

Direct by-value foreach now acquires finite scalar/object/nested DIRECT-array
payloads through one authenticated cursor and plain Map/Key/Value CVs. Pending
assignments copy Key and Value/HARRAY owners while the saved foreach continuation
owns Map; inner DAG edges stay unchanged. Map-CV unset, break and exhaustion
preserve fetched owners. Three originals agree exactly and the sole reached-state
front passes 131 conditions across 447 modules. Common storage cursor rejection,
by-reference iteration and factory/owned Iterator acquisition retain their earlier
domains. The occupied-current-row write exception below leaves other mutation,
retiring Keys, extra cursors and active lifecycle contexts Unsupported.
[Foreach review](coverage/semantics/gc-finite-byvalue-foreach-review.json).

An ordinary KEY_R read of the current multiple-entry row now copies its fetched
object/array owner during one authenticated direct by-value loop. Exact header
CVs, the current loop marker, body source and selection receipts preserve that
row. Its copied owner survives loop-Value/Map CV unset, break and later Key
cleanup without copying descendant edges. Two originals agree exactly and one
reached front passes 110 conditions (105 authored) across447 modules. Singleton
reads and common storage/quiet/reference/API/mutation/lifecycle fences keep their
earlier domains. [Current-read review](coverage/semantics/gc-foreach-current-read-review.json).

Occupied current-row replacement now uses that direct multiple-entry finite
cursor while the actual plain loop Value CV still owns the old payload. Original
Map/Key CVs, source and Key snapshot preserve selection and registration; existing
publication, copied-result and ordered release rules retain native timing. A
separate cursor operation proof covers only quiet old-value and later Map-pin
release, including the old payload's real nonlast GC visit. Two originals agree
exactly and the sole front passes 169 conditions (164 authored) across 448 modules.
Common storage, wider old callbacks, other mutations, Key retirement/freeing
and wider cursor/lifecycle forms retain their limits.
[Replacement review](coverage/semantics/gc-foreach-current-replacement-review.json).

Last-owner current-row replacement now authenticates a separate callback phase
after the loop Value CV is rebound to a nonowning scalar. Ordered old slots
select the real fieldless Child; its read through original Map/Key global cells
sees the published leaf. Normal return assigns the result, while a fresh Exception
preserves the outer target. A nonowning continuation claim retains old-row,
cursor and cell authority through Map-pin release without adding owners.
Root callers and ordinary leaf inputs are this cut; quiet GC58 remains separate,
and held GC35's freeing-Map write is unchanged. Wider mutation/callers, Key freeing,
by-reference/owned Iterator and active-GC/threshold cases remain partial.
Four exact originals and one 242-condition (237 authored) strict449 front pass;
failed fresh/descriptor/dispatch runs remain external with zero agreement.
[Last-owner review](coverage/semantics/gc-foreach-last-owner-read-review.json).

That same last-owner operation now accepts quiet NULL/boolean/integer/non-NaN
float and authenticated interned-string replacements. Incoming storage and KEY_R
results add no heap owner; present NULL assigns the outer result normally, while
a fresh Exception leaves its sentinel intact. The existing claim, source/cells,
cursor, old pin and Map-release phases are unchanged. Request/unknown string
identities, NaN and wider mutation/lifecycle forms remain outside this admission.
Seven exact originals and one 208-condition (203 authored) strict450 front pass;
the sole preimplementation baseline retains zero agreement.
[Quiet-scalar review](coverage/semantics/gc-foreach-quiet-scalar-review.json).

A separate current-row phase now admits a direct fieldless old Value's own
public destructor. Its actual last old-zval job selects the call; the old root
stays weakly live under call/result owners, with no storage pin during that
callback. Original Map/Key globals read the published leaf or quiet primitive.
Normal return assigns the outer result; a fresh Exception preserves its sentinel.
Only later cleanup creates the real standard-storage pin, then retires old and
releases the Map carrier through the existing nonowning claim.
Fresh unwind retains its genuine generic THROW_SEARCH inner operation; exact
phase and readonly future-prefix checks preserve its separate authority.
Root callers, the existing all-object construction domain and held Keys remain
bounded;
resurrection, callback writes, GC35 and active collection are unchanged.
Four originals and the maintained ownership front's normal/fresh facets pass
329 conditions (319 authored) at separate451 cuts; current joined453 also passes.
[Own-destructor review](coverage/semantics/gc-foreach-own-destructor-review.json).

Own-destructor Values now also admit finite public untyped declared scalar and
fieldless-Child slots. Source-bound construction/acquisition preserves the common
storage fences and ordinary leaf companion rows. The own callback sees old weak
live; actual standard teardown then makes it weak-null before declaration-ordered
Child release. Shared Child slots preserve physical multiplicity and invoke the
Child only at its real last release. Normal and fresh-own paths read the installed
replacement through the same original cells. Fresh Child calls remain attached to
the genuine generic inner operation, while the outer claim owns the pending
Exception. Exact saved-task certification restores borrowed registries with
identical heap; no pin/receipt/schema or executor change is needed. Four originals
and 506 independent conditions (496 authored) pass at their recorded453 cuts.
[Declared-own review](coverage/semantics/gc-own-declared-slots-review.json).

A fresh Child throw during fresh-own cleanup now transfers the protected old
Exception from the actual parent pending root into the new Exception's Previous
edge. The parent claim owns the new pending Exception; the genuine generic inner
operation keeps its source and zero roots. Later declared Children still run in
order and read the installed row before catch, with the outer result unassigned.
Separate source/slot/history and saved-prefix proofs cover this handoff without
changing the earlier read guards or held lifecycle domains. At that cut, a further
Child throw in that established Previous history stops explicitly before RESULT
consumption; its raw fence retains every pending and callback root. Two originals
and 375 independent conditions (365 authored) pass at their recorded454 cuts;
authentic joined455 also passes.
[Pending-handoff review](coverage/semantics/gc-child-pending-handoff-review.json).

Finite repeated fresh Child throws now preserve the original inner SOURCE while
extending the parent pending Exception's canonical Previous path. Every path
identity is fresh and decreases toward the original NULL Previous; the real
selected RESULT and Root slot history authorize each atomic transfer only while
every existing node and the new Throwable have one owner. Later normal Child
reads preserve the installed row and outer sentinel. Existing default pending
behavior, refusal outside the proved history and held domains remain unchanged.
Two exact originals and the focused 206-condition front (201 authored) pass at
their recorded455 cuts; authentic joined456 also passes.
[Finite-chain review](coverage/semantics/gc-finite-previous-handoff-review.json).

Retained plain DIRECT-array DAG incoming values now share the existing
current-row own/Child callback phases. Slot publication, KEY_R copy and explicit
callback-local release change only outer-array owners; shared subarrays and
ordinary leaf edges retain their physical multiplicity. The RHS remains held
and unimported, normal used assignment adds its outer result owner, and fresh
own throw preserves the sentinel before later Child reads. Dedicated finite
incoming validation leaves old payload/free policies and held domains unchanged.
Four originals and the focused 230-condition front (225 authored) pass at exact
private456 cuts; the review records current457 default-route compatibility.
[Retained-array review](coverage/semantics/gc-retained-array-callback-review.json).

Own-Value cleanup now separates declared array ownership from descendant Child
selection. Shared Root array slots first decrement without visiting elements;
last release retires the array ownership node and transfers ordered VALUE jobs.
The actual Root slot/NEXT, borrowed original row and remaining release suffix
authorize each last-owner Child read, preserving old weak-null and later direct
field order. Own normal/fresh paths keep the original claim/cells and deferred
outer result. Unproved Child throws stop before RESULT/root consumption.
Four originals and seven bounded facets pass 492 reported / 457 authored
conditions at their private 457-module cuts; full endings belong to the originals.
[Own-array review](coverage/semantics/gc-own-array-slots-review.json).

Property-array owners survive ordinary copies and COW. Removing the Value leaves
a fetched array owner intact; repeated array identities in declared slots defer
element cleanup until their last owner releases. Slots release in declaration
order; a final array release runs elements in table order, including cleanup
after a supplied Child throw between shared array slots.
Two originals agree exactly and one 91-condition front passes. The front checks
the actual slot-to-array job transfer and array owner2-to1 with Child edges
unchanged; later callback order comes from the original endings. The old
first-insertion baseline retains zero agreement.
[Property-array review](coverage/semantics/gc-property-array-payload-review.json).

Typed/alias/virtual/inherited/deeper, nested-array and recursive property layouts,
wider mutation/caller contexts,
freeing-Map dimension access and active-pin collection remain partial. Paused
work is untouched. The earlier [private-Key notification review](coverage/semantics/gc-finite-value-key-notice-review.json)
separates its source/owner/budget results from reconstructed helper inputs and
zero-credit baseline/structuring failures. Earlier cuts remain in the reviews for
[two entries](coverage/semantics/gc-two-entry-map-first-review.json),
[finite entries](coverage/semantics/gc-finite-map-first-review.json),
[declared slots](coverage/semantics/gc-finite-declared-properties-review.json),
[singleton/backed storage](coverage/semantics/gc-singleton-finite-values-review.json)
and [insertion/append](coverage/semantics/gc-finite-value-insertion-review.json).

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

Scalar Generator unpack reaches fixed untyped reference parameters in argument
positions 1 or 2 of direct named functions returning by value, within the first
two sends. By-value caches keep their Warning snapshot; ordinary reference
caches reread a nonowning source-cell designation after the handler. Alias writes
change delivery, while actual global-name rebinding preserves the old cell.
Distinct private cells retain earlier sends across the second Warning.
A96 extends delivery from the selected live reference cell through cache
replacement, changed keys/index, normal closure and a running Generator in a
suspended Fiber. The next iterator advance retains its ordinary phase behavior.
Closed Generators keep their cache until storage retirement; CELL adds no owner.
By-value delivery retains its existing restrictions. Ineligible reference
carriers and pending warning exceptions remain partial. Eight new and two legacy
source agreements, strict433 and source-derived ownership/continuation gates pass
at their recorded cuts; two Unsupported controls retain zero agreement credit.
Original fixture failures remain preserved separately.
[Snapshot review](coverage/semantics/generator-byref-sink-review.json),
[reference-cell review](coverage/semantics/generator-reference-sink-review.json),
[captured-cell review](coverage/semantics/generator-captured-cell-sink-review.json).

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

ATTR27 preserves pending C owners when an ignored body-value integer exit replaces
a saved main exit 263. Actual 9/515/519 remains separate from saved phase 263 and
CLI status. A genuine NORMAL/BUDGET canonical unwind and its current singleton
null-C Tick-source frame authenticate a status-only history view. Frame validation
retains that witness before ordinary caller-scope drop; readiness, actual status,
phase facts and148 delivery are unchanged. Five new originals and two affected26
controls agree; strict435 and five independent groups/775 conditions (765 genuine,
ten derived) pass. Original Unsupported and narrow owner-loss diagnostic keep0.
[Replacement review](coverage/semantics/callback-late-tick-body-reexit-review.json).
Earlier [body-value exit](coverage/semantics/callback-late-tick-body-exit-review.json)
retains its normal/stable-main integer/string and 739-condition cuts.
Earlier [handler-value throw](coverage/semantics/callback-late-tick-handler-throw-review.json)
retains its separate disabled-handler/old-Throwable cut.
Earlier [normal handler-value](coverage/semantics/callback-late-tick-handler-value-review.json),
[body-value bailout](coverage/semantics/callback-late-tick-body-throw-review.json),
[body-return](coverage/semantics/callback-late-tick-body-return-review.json),
[handler](coverage/semantics/callback-late-tick-handler-review.json),
[exit/throw](coverage/semantics/callback-late-tick-exit-throw-review.json),
[bailout](coverage/semantics/callback-late-tick-throw-review.json),
[stable-exit](coverage/semantics/callback-late-tick-exit-review.json),
[cache-shape](coverage/semantics/callback-late-tick-callables-review.json) and
[copied-value](coverage/semantics/callback-late-tick-values-review.json) evidence
keeps its original cuts. Unshared owning channels, uncovered selected completion
owners, wider handler/callable/previous-chain/frame contexts and reentry remain
partial.

Tick plans follow Zend compiler order across Switch conditions/bodies, Match
conditions/results, Yield key/value and YieldFrom operands. Compiled unselected
callables contribute lexical declarables. Constant/CV versus temporary cleanup,
assignment/discard lines and ordinary Generator suspension preserve canonical
statement markers and the shared request counter. Grouped Echo, unset, global
and static operations interleave canonical ticks with completed operations and
later item evaluation, preserving late targets, reads, initializers and compiler
lines/frequencies. Unset cleanup finishes before its Tick; abrupt callbacks leave
later owners intact. Cached static bindings still tick on later calls.
Foreach value/key targets compile before the body even for empty input. Shared
by-value list traversal visits RHS, keys and nested targets in compiler order.
Runtime target callbacks stay lazy per iteration, and later failure preserves
completed writes while skipping pending targets/body and releasing the iterator.
Plain global constant groups compile initializers in order and tick after all
bindings, preserving the final emitter line and installed values on callback abort.
Class-like plans consume completed early-binding facts to preserve or break prior
adjacency. Methods, ordinary block/expression-GET hooks, class-constant and plain
property initializers contribute lexical declarations even when uncalled. Constant groups
remain unticked; property-group Ticks preserve main adjacency, type/name lines
and callback abort before pending class activation. Short GET expressions retain
nested callable order and implicit return; callback removal of the global receiver
keeps it alive until unwind, with later fresh-object retry. Nested Closure scope
uses completed getter/property ownership. Escaped Trait-getter Closures match
shared physical code to actual consumer property/getter imports, retaining separate
lexical/called classes and receivers after getter frames retire.
Escaped block-SET Closures authenticate exact class/trait setter origins and
actual consumer imports while retaining captured values and receiver ownership
after hook return and removal of the original receiver variables
([review](coverage/semantics/tick-set-closure-review.json)).
Ordinary public typed class short SET hooks evaluate the real expression, write
backing storage and fall through as void while preserving the caller's input
result. Input errors skip the body; RHS throws skip the implicit assignment and
result type errors prevent its slot update. Retry and receiver cleanup retain
the existing owners
([review](coverage/semantics/short-set-expression-review.json)).
These short SET bodies also bind an actual typed, defaultless by-value Param,
preserving its name, contravariant signature and original string input separately
from integer storage. Body compilation precedes variance checks; the existing
receiver owners survive throw/retry and budget resumption
([review](coverage/semantics/short-set-explicit-review.json)).
Existing public typed class block GET and short SET hooks now share one authentic
backing descriptor and retain their distinct indexed functions/signatures. Crossed
own-backing access skips the other hook; assignment input, stored transformation
and getter result stay distinct through RHS throw, retry and receiver release.
Three originals agree and strict448 passes; 137 independent source/owner/budget checks
are in the [short-pair review](coverage/semantics/short-get-set-pair-review.json).
Initialized properties now also admit pure block GET plus an inherently backed
short SET through the actual source/property/initializer certificate. Neither body
needs syntactic backing use; persisted SET storage stays distinct from GET 700.
Four source agreements, strict448 and 148 independent source/slot/owner/budget checks
retain their recorded cuts in the [pure-pair review](coverage/semantics/pure-get-short-set-pair-review.json).
With no initializer, the same pair keeps genuine uninitialized backing until its
first successful write. GET 700 precedes that write; backing-read Error, parameter/implicit-write
TypeErrors, persistent 15/12 and first-write receiver abort/retry preserve storage.
Four originals, strict449 and 148 independent initial-slot/owner/budget checks retain
their cuts in the [uninitialized-pair review](coverage/semantics/uninitialized-pure-get-short-set-pair-review.json).
Trait, byref/attribute/default and wider headers stay partial.
Existing expression-bodied GET now pairs with short SET on the same initialized
or uninitialized property. Actual backing/source authority reuses implicit-return
compilation and runtime; getter throw/return TypeError preserves the caller target
and storage. One saved getter-context receiver owner survives global removal;
the result receipt adds none. Five originals, strict449 and 146 independent source/
return/owner/budget checks are in the [expression-pair review](coverage/semantics/expression-get-short-set-pair-review.json).
Short SET can also precede GET: actual source derives logical GET 1/SET 0 while
compilation visits physical 0 then 1, preserving checked SET body/builtin-variance error priority.
Existing descriptor, return, storage and Closure source-owner rules consume those
real roles, including source-covered absent initializers. Seven originals and
strict449 pass; main 148 and corrected Closure 37 checks retain separate cuts in the
[SET-first review](coverage/semantics/set-first-hook-pair-review.json).
Source-backed block SET now composes with admitted GET forms and actual physical
roles, including explicit typed/defaultless input and reversed statement pairs.
Actual SET syntax authenticates pure initialized GET backing; absent initialization,
original string input, transformed storage and checked compiler error order remain
distinct. Seven originals, strict449 and 156 independent statement/receiver/budget checks
are in the [block-SET pair review](coverage/semantics/block-set-hook-pair-review.json).
Backed GET syntax now establishes whole-property storage even when block SET has
no own-backing access/write. Actual pair/role/default authority preserves initialized
values or a real uninitialized slot through no-write success, throw and retry;
implicit parameter coercion stays distinct from the caller's original input result.
Five originals, strict449 and 147 independent source/slot/receipt-owner/budget checks are
in the [GET-backed no-write review](coverage/semantics/get-backed-no-write-set-review.json).
True virtual class GET/block-SET pairs now retain source roles and typed metadata
without any object slot. Existing GET forms and implicit/explicit typed SET preserve
input/return checks, no-write effects and receiver throw/retry. Explicit defaults
fail after physical hooks at the last hook's end line; earlier default-type and
checked body/builtin-variance errors keep their priority. Seven originals and
150 independent no-slot/source/receipt-owner/budget conditions use the current
450-module manifest in the [virtual-pair review](coverage/semantics/virtual-get-block-set-pair-review.json).
The original temporary-cast comparison cleanup failure stays unresolved/zero;
accepted empty-cast observations use a CV. Pair overrides, Trait and wider headers
remain separate.
Direct flat Trait GET/block-SET pairs also compose admitted backed bodies, actual
roles and typed/defaultless builtin parameters. Raw partners and source/type facts
authenticate both Consumer clones atomically; two Consumers retain separate slots
and lexical/called classes while sharing Trait code/magic. Original string input,
weak reception, no-write initialization state, callback throw/retry and imported
GET1 return/Closure source owners reuse existing execution rules. Six originals and
212 independent source/clone/slot/receipt-owner/budget conditions are in the
[Trait pair-family review](coverage/semantics/trait-backed-get-block-set-pair-review.json).
The initial source timeout and first peer fixture typing failure retain zero credit.
GET/block-SET and GET/short-SET pairs also export through acyclic unadapted Trait
wrappers and multiple Traits with disjoint properties. Each property's real immediate
exporter and installed path authenticate flattened raw hooks/Params; wrapper rows
remain noncallable. Unique callable selection is separate from admission of a
specific incoming edge, preserving diamond and first local-property conflict
priority. Virtual Consumer pairs keep both authentic hooks without a value slot,
while adjacent backed properties retain real storage. Original input, weak/union
reception, GET return typing, callback throw/retry and raw Trait versus Consumer
scope use existing execution. Imported virtual pairs stay outside the admitted
virtual override/inheritance paths. Short SET is inherently backed, even with
pure GET and no own-property syntax. Its real raw RHS evaluates before the implicit
write at the Consumer hook origin; input, stored transformation and GET700 remain
distinct through initialization, implicit-write TypeError, abort/retry and two
pending receiver owners. The [nested](coverage/semantics/nested-trait-backed-pairs-review.json),
[branching](coverage/semantics/branching-trait-exporters-review.json),
[virtual](coverage/semantics/virtual-trait-pairs-review.json) and
[short Trait reviews](coverage/semantics/trait-short-set-pairs-review.json) retain
separate source/path/clone/slot/receipt-owner/budget cuts and zero-credit failures.
Consumers may also extend ordinary source Parents with disjoint stored fields and
no declared or effective hooks. Pre-link import checks the actual installed
declared Parent; runtime hook authority requires the final SOURCE_PARENT link and
publication. Existing inherited layout, raw Trait/Consumer/descendant scope and
receiver owners remain distinct through
throw/retry. Trait conflict precedes a final-Parent linking error, while a raw body
error precedes main.
[Parented pair review](coverage/semantics/parented-trait-pairs-review.json).
Backed Trait pairs also preserve public reads with protected/private SET access.
Exact source flags authenticate setter visibility and private(set) implicit finality.
Consumer lexical permission stays distinct from Grand called-scope diagnostics;
RHS effects precede denial and allowed input then reaches reception. Initialized
and genuine uninitialized storage, original assignment input and writer/SET owners
survive the tested store/throw/retry paths. Virtual-asymmetric, arbitrary explicit
final and wider override forms remain excluded.
[Asymmetric pair review](coverage/semantics/asymmetric-trait-pairs-review.json).
Symmetric protected/private READ backed Trait pairs now authenticate canonical
keys through real raw Trait, wrapper and Consumer rows. Dispatch checks the actual
permitted descriptor, preserving private-first lookup and original caller access
while a plain helper runs. Short SET retains the source name before storage-key
resolution. Consumer readers, unrelated Consumers, Grand private fallback and
protected uninitialized storage keep their distinct outcomes; reader/getter owners
retain the receiver through throw and fresh retry.
[Nonpublic key review](coverage/semantics/nonpublic-trait-pair-keys-review.json).
Quiet and conditional planners now use that permitted descriptor and check their
result tails in the saved caller scope. Inaccessible `isset`/`empty` skips GET;
NULL and zero retain different `??=` paths. The real conditional write task
reacquires its receiver after the RHS and enters the existing SET call/result
rules, preserving original input, transformed storage and private denial after
rebinding. Getter and RHS aborts preserve the prior result and permit fresh retry.
[Quiet conditional review](coverage/semantics/nonpublic-quiet-trait-pairs-review.json).
Existing integer-RHS `+=` now invokes SET after GET/addition for symmetric
builtin-backed pairs. Permitted descriptor lookup and saved caller access retain
the selected receiver even if GET rebinds its CV. Real compound source and the
retained finish task authenticate the SET target; expression result and transformed
storage remain distinct. The outer operation pin survives the independent SET
receipt through normal return or unwind; GET-only storage/finish remains unchanged.
[Compound pair review](coverage/semantics/compound-get-set-pairs-review.json).
Direct named CV/This `unset` now recognizes nonpublic hooks through the resolved
canonical key. Visibility denial stays first; permitted caller and active own
GET/SET contexts still receive the hooked-property Error, with backing retained.
An unset-specific descriptor query keeps raw-name magic-property consumers and
ordinary storage rules unchanged; indirect hooked unset remains Unsupported.
[Canonical unset review](coverage/semantics/canonical-hook-unset-review.json).
Normal GET/SET on admitted backed pairs now accepts plain non-NUL string-CV
property names. The existing pending selector resolves a normal assignment name
after the RHS; the selected hook property stays fixed through later name changes.
Actual source/code/line and saved caller access authenticate the selected
Consumer descriptor independently of a helper's current name CV. Changed-name
GET abort, receiver cleanup and fresh retry retain ordinary ownership. Arbitrary
expressions and Stringable-name forms stay separate.
[String-CV name review](coverage/semantics/string-cv-hook-names-review.json).
Plain string-CV names also compose with existing quiet/coalesce-assignment and
symmetric builtin-backed integer-RHS compound consumers. Quiet task roles stay
distinct from normal GET. Conditional writes retain late receiver/name
reacquisition, including retirement of the original GET receiver before an RHS
abort. A retry can select SET again and preserve the original string input while
transforming storage;
zero skips the write. Compound dispatch instead uses the retained property's
source NAME through GET-time name changes, preserving its fixed target and
independent operation/SET holds. Existing literal, type and ownership laws remain.
[CV name consumer review](coverage/semantics/string-cv-hook-consumers-review.json).
Normal magic GET/private SET now authenticate plain string-CV names on direct CV
receivers. Entry checks the original emitted operand; selected NAME/DECL and
actual method arguments remain authoritative after handlers change the name CV.
A scalar-int/nonref completion gate preserves wider getter/coercion boundaries.
Existing getter receipt ownership, private setter body/signature/scope and
integer literal/direct-CV RHS delivery remain unchanged through throw and retry.
[Magic CV name review](coverage/semantics/string-cv-magic-properties-review.json).
Quiet magic CV-name consumers now reuse the selected NAME receipt for terminal
`isset`, `empty` and coalesce, including the `__isset` to GET handoff after name
mutation. New callback results stay boolean for `__isset` and scalar integer for
GET; false `__isset` supplies the existing no-GET null path. Conditional assignment
keeps its real VARIABLE selectors and reacquires receiver/name after the existing
no-argument integer RHS, preserving ordinary fallback versus actual SET dispatch,
throw and retry. Entry/source changes leave storage and receipt ownership intact.
[Quiet magic CV name review](coverage/semantics/string-cv-magic-quiet-review.json).
Private ordinary `__unset` now authenticates direct-CV/string-CV source and the
actual pending VARIABLE name through existing PPUNSET resolution. Initial name
equality is separate from entered receipt history, preserving selected NAME and
one receiver hold after handler mutation/removal. Void method/body/scope gates,
literal/public history, broad fallback, canonical hook exclusion and storage
rules stay unchanged.
[Magic unset CV name review](coverage/semantics/string-cv-magic-unset-review.json).
Public integer CV unset now distinguishes actual INITIAL/VALUE ordinary clearing
from PROP_UNSET magic dispatch using an authenticated source/name/PPUNSET/slot
certificate. Only that ordinary case partitions broad unknown-name pending;
callback entry requires UNSET, while entered public history survives repopulation.
Literal/private, void method/body, storage and one-receipt ownership laws remain
pointwise; bounded public CV recursion is described below.
[Public CV unset state review](coverage/semantics/public-cv-magic-unset-state-review.json).
Public integer CV unset now clears repopulated VALUE before consulting an active
same-object/name guard. PROP_UNSET with that guard uses the existing no-op without
another callback or receipt; the ordinary callback plan still excludes recursion.
Authentic CV/source/name/PPUNSET/public-int/no-hook/void/scope gates remain, with
existing context/receipt and local-CV ownership through helper throw and retry.
Reachable active VALUE and UNSET are witnessed; inactive INITIAL evidence stays
pointwise, without an active-INITIAL claim or storage/root/body change.
[Recursive CV unset review](coverage/semantics/public-cv-magic-unset-recursion-review.json).
Active private integer CV-name unset now authenticates actual PROPERTY_DENIED
and existing source/name/PPUNSET/capture/scope/no-hook/void gates before using the
ordinary visibility Error at the inner source line. The same-object/name guard
suppresses another callback; no public no-op, storage deletion or inner receipt
is introduced. Existing local-CV plus outer-receipt ownership survives Error
catch, helper throw and fresh retry; public/literal and normal callback paths stay
pointwise.
[Private recursive unset review](coverage/semantics/private-cv-magic-unset-recursion-review.json).
Terminal literal-name `unset` now admits genuinely absent properties on ordinary
instances, including anonymous ones, through a direct non-This CV receiver.
Optional descriptor identity separates immutable declaration absence from
fresh slot/cache capture; saved history and the one-receiver receipt survive callback changes. Actual void
frame-exit membership retains the recursive guard through compiled-local
destruction. Five source agreements, author AL99/110/158, peer AL82/32 and legacy
SL212/579/127/137/163/140 pass at their recorded 503-module cuts. Original budget,
cast-cache and legacy source-refusal fixture failures retain zero credit;
the [review](coverage/semantics/anonymous-missing-unset-review.json) records their corrections.
Indirect append now authenticates its actual main-scope CV/literal-property
assignment before calling an existing nonref getter on a private integer slot.
After return, the receiver hold transfers from guarded RESULT to guard-free BASE
through the indirect-modification Notice. Handler reentry sees IN_GET clear;
after the handler, scalar verification/copy precedes receiver release and the
ordinary append Error. Handler throw/destruction and retry preserve the outer
result. Existing tasks, source nodes, storage and root formulas are reused.
[Indirect magic getter review](coverage/semantics/indirect-magic-get-append-review.json).
Main-scope private integer magic `+=` now authenticates plain CV names after the
existing no-argument integer RHS, then retains the selected receiver/name through
GET and SET. Existing scalar-int/nonref getter, void setter, method/body and
range gates remain; computed result differs from transformed store. The operation
and current handler receipt retain independent receiver holds through abort and
retry, without a new source node, storage rule or root formula.
[Magic compound CV name review](coverage/semantics/string-cv-magic-addassign-review.json).
Main-scope private integer magic pre/post updates now authenticate actual OP/POST
and a plain CV name at UPDATE_PREP/PPRW selection. Retained GET/SET history keeps
that object/name through live-variable changes; immutable OLD/NEW distinguish the
prefix/postfix result from transformed storage. Existing scalar/range/method/body,
literal and independent operation/handler-hold laws remain.
[Magic update CV name review](coverage/semantics/string-cv-magic-incdec-review.json).
Terminal `isset` now admits the existing typed-bool method alongside a same-owner
admitted getter, authenticating both physical functions and canonical no-hook
private descriptor while dispatching only `__isset`. The literal terminal defer
and existing CV entry use the same bool/source/receipt law; old untyped/noGET and
empty paths remain pointwise, with no getter-result or body/type expansion.
[Terminal bool pair review](coverage/semantics/terminal-typed-isset-pair-review.json).
Sole short-SET Traits, same-name/hooked Parents, adaptation, nominal and wider
binding remain separate.
Conditional declarations activate before their header-line Tick, while top
declarations have no outer Tick.
Trait use and admitted alias/precedence metadata add no Tick or repeated method
compilation; callbacks retain physical source, alias trace name and receiver
through abort and retry.
Namespace markers use authenticated form/name/brace facts: semicolon headers
precede following work, braced markers follow it, and empty/EOF boundaries remain
in the flattened compiled stream. Header callback abort skips pending body activation.
Ordinary/group imports contribute one metadata Tick per statement at name/prefix
lines. Literal eval namespace/import events share the caller's request counter;
callback abort skips pending class activation and restores the eval continuation.
Global-file `__halt_compiler` adds no opcode but can emit a terminator-line Tick.
Its callback sees the existing halt offset and can abort while payload remains inert.
Ordinary function, method, Closure and arrow defaults contribute lexical declarables
left-to-right before body planning, with separate callee adjacency and the caller
plan preserved. Fresh received Closures retain declaring lexical/called scope,
while callbacks can read the actual receiver and abort before later body work.
Certified EnumCase markers run before the existing enum activation task, retaining
member order, prior-marker frequency, backed-value lines and abort/resume behavior.

Conditional and coalescing plans use published operands, redirects and retained
effects. Bodies erased during compilation and their static errors stay absent;
bodies skipped at runtime still compile. Retained effects run once and real conversions,
jumps and writes break adjacency. Quiet coalesce reads retain lazy RHS execution;
assignment target children compile once before RHS and memoized writable refetch.
Captured key consumers preserve string-carrier identities and classify their bytes
with the ordinary numeric-string rules. Registered-handler callable-key coalesce
writes and equal-byte runtime write/unset now consume their tasks and complete.
Exact source, strict and reached-state cuts remain in the
[Switch](coverage/semantics/tick-switch-review.json),
[Generator](coverage/semantics/tick-generator-review.json),
[Match](coverage/semantics/tick-match-review.json),
[conditional](coverage/semantics/tick-elision-review.json),
[coalesce](coverage/semantics/tick-coalesce-review.json),
[Echo](coverage/semantics/tick-echo-review.json),
[grouped emitters](coverage/semantics/tick-grouped-review.json),
[Foreach targets](coverage/semantics/tick-foreach-review.json),
[destructuring](coverage/semantics/tick-list-review.json),
[global constants](coverage/semantics/tick-constant-review.json),
[class-like declarations](coverage/semantics/tick-classlike-review.json),
[enum cases](coverage/semantics/tick-enum-case-review.json),
[member constants](coverage/semantics/tick-class-const-review.json),
[plain property defaults](coverage/semantics/tick-property-review.json),
[property hooks](coverage/semantics/tick-hook-review.json),
[plain trait use](coverage/semantics/tick-trait-use-review.json),
[trait adaptations](coverage/semantics/tick-trait-adaptation-review.json),
[namespace forms](coverage/semantics/tick-namespace-review.json),
[import emission](coverage/semantics/tick-import-review.json),
[halt emission](coverage/semantics/tick-halt-review.json),
[named defaults](coverage/semantics/tick-parameter-review.json),
[callable defaults](coverage/semantics/tick-callable-parameter-review.json),
[short getters](coverage/semantics/tick-short-get-review.json),
[Trait getter scopes](coverage/semantics/tick-trait-get-review.json) and
[carrier-key](coverage/semantics/tick-key-carrier-review.json) reviews.

Compiler-special builtin/fallback result fences, empty multiline control-body
lines and wider child/result/lifetime contexts remain partial. The earlier
registered-handler timeouts retain zero agreement credit; the carrier-key review
records their exact successful-conversion fixed point and the completed fix.

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
diagnostics retain their distinct formats. Three changed private and joined strict433 cuts,
native6+2+1, old2 and source/state cuts stay separate; the never-kind mismatch
and fixture elaboration failure retain zero credit. Wider magic, reference,
attribute, callable and lifecycle contexts remain partial.
[Stringable review](coverage/semantics/anonymous-stringable-review.json).

CLASS156 admits public zero-argument anonymous destructors through the ordinary
method compiler and lifecycle. Alias and temporary release, eval callbacks,
reverse global cleanup, escaped failed constructors and pending-exception
replacement have five exact source agreements. Two reached groups pass 240
conditions (228 reached, 12 derived across six controls); private and joined strict433 passes.
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

Effectful callable return checks now retain a fresh array temporary across
qualified public lookup, live member mutation and finally. Valid lookup carries
a handler exception through callee-CV cleanup; invalid lookup drops the temporary
before finally and creates a return TypeError, retaining any pending handler
exception as Previous. Exact union branches
bypass lookup. Four source agreements, private 463-module strict compilation and an independent
190-condition owner/budget packet pass. Accepted current464 source/interface
composition is recorded separately;
the scoped review keeps the unresolved pending/replacing-finally timeouts and
model-only refusal checks separate. [Callable returns](coverage/semantics/callable-return-review.json).

Plain compiled CV callable returns now distinguish protected compiler copies
from unique/shared local unref. Shared references separate only the local ENV
binding before even an exact union match; API lookup borrows its value without
adding a pin. Used RETURN moves and clears that slot, while ignored results keep
native compiled-variable cleanup order. Pending handler throws and invalid
TypeError/local catch-retry preserve the same value and real Exception carriers;
ignored protected temporaries drain after finally before locals. Plain-cell,
active-finalizer and existing callable/context bounds remain explicit. Four new
source agreements and 913 independent ownership/source/budget conditions pass at
the recorded private 465-module cut; the accepted current 467-module interface
load is recorded separately.
[CV return review](coverage/semantics/callable-return-cv-review.json).

Public ordinary instance and fixed literal class static method returns now share
callable verification through published method descriptors and separately
validated live target/scope/This context. Creator This and returned arrays keep
independent owners, including descriptor validation after creator retirement,
lexical method TypeError/Previous and used/ignored cleanup. Two new source
agreements and 548 independent conditions pass at the private 467-module cut;
no new task, root, entry or wider context is introduced.
[Method return review](coverage/semantics/callable-return-method-review.json).

Raw self/parent/static strings and bare keyword arrays now verify through the
actual API phase in the existing return context. Raw string bytes and
member-reference identity are preserved, without a captured This owner or
caller-scope recheck.
Keyword-class handler throws reject with TypeError/Previous; compound-member
throw resumption remains separate. Structural cleanup survives resumed leaf
mutation, with scoped NUL/compound refusals before lookup. Three new originals
agree; the affected 246-condition pending/union packet passes at private469.
Earlier failed aggregates and projections retain zero credit, and actual471's
joined interface load is separate.
[Keyword return review](coverage/semantics/callable-return-keyword-review.json).

Unprotected named USER by-reference CV returns now borrow their cells through
effectful callable verification without unref, detachment or payload restoration.
A live captured query can succeed while a handler replaces the cell or rebinds
its global name; RETURN still uses the captured cell's current contents. Used
results retain the real reference through pending cleanup, while ignored and
invalid calls preserve CV-slot retirement. TypeError retains a pending handler
Exception as Previous. Lost query graphs reach explicit refusal, without a pin
or historical lookup permission; the loss controls are model-only. Three new
originals agree; the affected 125-condition packet
passes at the private 471-module cut, with the failed 561-condition packet,
diagnostic cuts and the actual 473-module joined load
kept separate.
[Reference callable review](coverage/semantics/callable-reference-return-review.json).

Protected named USER reference returns now keep one real MAKE_REF temporary
through quiet finally and the actual second callable check, using the captured
cell after CV rebinding. Normal/pending ignored drain precedes locals; used
pending results and fresh TypeError/Previous retain separate cell/Exception
owners. First-pending callback suppression requires the proven canonical prefix
and quiet callback-free continuation; failing recheck remains Unsupported.
Two effectful source agreements and one retained pure control pass at their own
cuts; the affected 270-condition packet passes at the private 473-module cut. The original
pending mismatch, timeout, failed/interrupted packets and diagnostics stay zero.
Actual 481's joined load is separate.
[Protected reference review](coverage/semantics/callable-reference-protected-review.json).

Pure protected named-function CV returns now replace the duplicated recheck root
with a nonowning witness for a bounded single quiet finalizer and unchanged
TYPEVALUE conversion. Exact union acceptance is independent of callable shape.
The captured cell survives name rebinding with one real temporary; ignored
returns schedule one cell release before locals, preserving any surviving CV
owner. One new three-mode source agrees, and the first 178-condition packet
passes at the private 481-module cut. The separate current 483-module load
passes with zero source renewal. Earlier failures and finite projections remain
zero. Legacy computed, cursor, overriding and wider-finalizer paths stay open.
[Pure protected reference review](coverage/semantics/pure-protected-reference-review.json).

Exact-int protected reference returns now admit one quiet scalar-literal write
through the captured cell. Initial verification proves its earlier payload is
primitive. Existing integer conversion writes back through that same reference;
TypeError transfers the one temporary to a real release before local catch and
source-derived finally replay. Detached cells retire, while retained ENV owners
survive. One four-mode source and the first 224 conditions pass at the private
483-module cut; the separate current 484-module load adds zero source renewal.
Finite baseline/admission observations and the declaration-order failure remain
zero. Wider conversions, pending callbacks and legacy finalizer paths stay open.
[Scalar protected reference review](coverage/semantics/pure-protected-reference-scalar-review.json).

Protected plain-CV exact-int returns now carry one temporary through two quiet
nonreplacing finalizers. Source-derived inner/outer phases preserve one nonowning
witness and defer the repeated check until both bodies finish; the outer write
repairs the intermediate invalid value before that check. Final conversion/rejection uses the captured
cell after CV rebinding, including detached/ENV-held local catch and replay.
New multi-body entry requires empty output/tick callback state. One four-mode
source and the first 343 conditions pass at the private 484-module cut. The
separate current 487-module load adds zero source renewal. Finite root/projection
observations stay zero; wider finalizer/callback paths remain open.
[Two-finalizer reference review](coverage/semantics/pure-protected-reference-multi-review.json).

Protected plain-CV exact-int returns now follow a finite source-derived chain of
quiet nonreplacing finalizers, preserving the first inner owner and one temporary.
Each remaining owner/restore suffix authenticates progress; the repeated check
runs only when that suffix is exhausted. The three-body source agrees in four
modes at the private 487-module cut, including repair after two invalid writes
and detached/ENV-kept rejection with full replay. The reduced 271-condition
independent packet passes at that cut; the full 514-condition state timeout and
finite diagnostic remain zero. The separate actual 489-module load adds zero
source renewal. The original 360-second source timeout remains zero;
the separate retry passed in 358.147415 seconds under its declared 600-second
limit. Finite root observations add no agreement credit.
[Finite-chain reference review](coverage/semantics/pure-protected-reference-chain-review.json).

Protected plain-CV exact-int returns now stage a finite fractional-float
precision warning while one real MAKE_REF temporary owns the captured cell.
The saved integer survives handler writes; normal completion writes it back,
while handler throw creates TypeError/Previous without that writeback and
releases the temporary before local catch/finally replay. Genuine GLOBAL/ENV
aliases survive independently. Two selected sources and the reduced 185-condition
packet pass at the private 489-module cut. The failed 207-condition packet,
ignored-return projection and all preparation/finite observations remain zero.
Primitive-cell release is covered; no new owning-payload or user-destructor
behavior is claimed. The separate actual 492-module load adds zero source
renewal. [Lossy reference review](coverage/semantics/pure-protected-reference-lossy-review.json).

Unprotected named USER reference returns now stage finite-float precision
verification without an extra cell/value owner. The restored local ENV binding
authenticates the borrowed cell; normal saved-integer writeback precedes real
used-only wrapper creation. Ignored calls add none. Handler throw produces
TypeError/Previous over the original catch tail, keeping the current cell for
local catch without a temporary release or synthetic replay. Two source
agreements cover plain/aliased used/ignored and handler-throw observations; the
first 251 conditions pass at the private 492-module cut. Declaration-binding
failure and finite observations remain zero. The separate actual 494-module
load adds zero source renewal.
[Unprotected precision review](coverage/semantics/unprotected-reference-lossy-review.json).

Unprotected named weak-int by-value CV returns now stage finite-float precision
warnings after the actual local unref/separation. Nonreferences stay; unique
references lose their marker; shared references separate only the local ENV
binding. Scalar success keeps the local integer through cleanup. Handler
TypeError/Previous preserves the real catch tail and local value 1.5 while an old
shared GLOBAL holds 41, without a result-cell owner or temporary release/replay.
Two new originals and the first 304 checks pass at the private cut with 494
modules. Two fixture-only preparation failures and all finite/load observations
remain0. This establishes
primitive-cell lifetime, with no new user-destructor or owning-payload claim.
The [by-value precision review](coverage/semantics/by-value-lossy-return-review.json)
keeps the source, state and actual joined-load cuts separate.

Named weak-int by-value FLOAT-literal returns now stage the precision warning
on the actual CONST-to-TMP value. The zero-root continuation never reads or
writes a local/global cell or uses stale LOCATION. Normal saved1 enters ordinary
return/finally, while handler failure uses the saved FLOAT tag for TypeError,
links Previous and preserves the genuine finally/catch tail. An int|float
literal bypasses the warning. Two source originals and the first 205 checks pass
at the private cut with 494 modules; finite/native/strict observations remain0.
The [literal precision review](coverage/semantics/by-value-literal-lossy-return-review.json)
keeps the actual joined load separate. Protected CV QM_ASSIGN, generalized TMP,
active-finalizer and wider conversion/entry domains remain partial.

Named weak-int BYREF FLOAT-literal returns now stage precision verification
before ordinary finally and the later variable-reference Notice. The zero-root
resume requeues VALUE with savedINT, leaving all Notice/RV work to existing379.
Precision failure creates TypeError/Previous before any Notice; fresh Notice
failure keeps its original Exception. Used frames own one returned HCELL,
ignored frames none, and pending E moves once through FRAME.PENDING before
real local-destructor cleanup. Two originals and the first 191 checks pass at
the private cut with 495 modules; finite/native/strict/recovery preparations
remain0. The [reference literal review](coverage/semantics/reference-literal-lossy-return-review.json)
keeps those cuts separate from the actual joined load. Wider coercion/entry,
active-finalizer and protected-CV/general-expression paths remain required.

Supplied weak-int reception now stages finite-float precision warnings for one
required by-value formal on an ordinary named nongenerator call. The zero-root
continuation borrows the ENV-owned formal: saved1 reaches the body while the
caller GLOBAL remains41. Handler throw preserves the original Exception and
skips body/result assignment. Cross-unit eval controls distinguish caller from
callee strictness. The [reception review](coverage/semantics/supplied-integer-reception-review.json)
keeps three source agreements, their scope-guard bridge, the earlier 194-condition
state gate and final 33-condition singleton gate separate. Failed and diagnostic
cuts retain zero credit. Wider signatures, entries,
owning payloads and held contexts remain partial.

Ordinary terminal string `isset`/`empty` now preserves strict float conversion's
range Warning followed by precision Deprecated. Separate INF and finite-overflow
source agreements, author AL104 (43 derived controls) and independent AL60 retain
their recorded cuts; the initial fixture syntax failure stays zero credit.
The [strict-float review](coverage/semantics/string-offset-strict-float-review.json)
keeps the actual joined498 SL load separate. Shared numeric and quiet/R/W rules,
handler/lifetime fences and complete-family status remain unchanged.

Supplied weak-int BYREF reception now preserves one real shared caller/formal
cell through its precision callback. Saved-integer success overwrites the
handler's write before body entry; a handler throw leaves that write, preserves
the original Exception and skips body/result assignment. The continuation adds
no owner. Three source agreements and 133 independent conditions pass at their
private 498-module cuts, including caller strictness across eval units. The
[reference reception review](coverage/semantics/supplied-reference-integer-reception-review.json)
keeps those cuts, the initial binding failure and unchanged Unsupported controls
separate from actual joined loading. Wider signatures, entries, owning late
payloads and held contexts remain partial.

Ordinary nested string `unset` now resolves the live intermediate key before
its Error, suppressing leading-integer text warnings in the UNSET context.
Four source agreements preserve final-key assignment effects, skipped late CV
reads and the distinct first-key versus nested-string Errors. Separate author
AL72 (31 derived guards) and independent AL76 retain their private498 cuts;
the initial fixture syntax failure stays zero credit. The
[nested-unset review](coverage/semantics/string-offset-nested-unset-review.json)
keeps handler and NUL paths and wider key ownership/lifetimes partial; the actual
joined500 SL load has zero source credit.

Terminal string `unset` now dispatches authenticated non-NUL carriers after the
existing R-key read, without casting the key. A wrapper used only by the final
unset path keeps the shared ArrayAccess helper literal. One grouped source and
author AL93 (34 derived guards) plus independent AL53 retain private501 cuts;
preliminary broader dispatch/AL87/89 cuts keep zero final acceptance credit.
The [terminal review](coverage/semantics/string-offset-terminal-unset-review.json)
keeps owning/reference keys, NUL, handlers and wider lifetimes partial.

Finite required by-value int formal lists now keep supplied ordinary CV
snapshots through ordered precision callbacks. An indexed zero-root continuation
stores the selected saved integer, then advances the actual next receive or
body. Earlier completed reception precedes a later missing-argument error;
a handler throw keeps its original Exception and cancels the remaining schedule.
Three source agreements and 150 independent conditions pass at their private
500-module cuts. The [ordered reception review](coverage/semantics/supplied-positional-integer-reception-review.json)
keeps those cuts, unchanged Unsupported controls and finite preparation separate
from actual joined loading. Wider signatures, producers, entries and held
contexts remain partial.

Finite required BYREF int formal lists now read each selected cell at its actual
receive. A shared CV can warn once, while a handler may change a later input
before its conversion or an earlier verified input before body entry. An indexed
zero-root snapshot writes the saved integer through the real current formal;
handler throw preserves current writes and its original Exception. Three source
agreements and 157 independent conditions pass at their private 502-module cuts.
The [ordered reference review](coverage/semantics/supplied-positional-reference-integer-reception-review.json)
keeps source, state and initial failed/preparation cuts separate from actual
joined loading. Mixed modes, wider signatures/producers, owning late payloads
and held contexts remain partial.

Finite required int signatures with both value and reference formals now select
readiness from each immutable formal mode. Copied SEND values and live referents
retain their separate behavior through later handlers; reversing modes on the
same caller CV changes diagnostics and body values. Positional and all-named
ordinary CV prefixes retain the same six-field zero-root snapshot. Named SEND
order maps to fixed slots before formal receives: interior required holes fail
before precision callbacks, while a supplied prefix receives before a later
missing parameter. Original handler exceptions and current writes survive.
The [positional](coverage/semantics/supplied-mixed-integer-reception-review.json)
and [named](coverage/semantics/supplied-named-mixed-integer-reception-review.json)
reviews keep their private 505/506-module source and state cuts separate from
actual joined loading. The named cut has three source agreements and 264 executed
AL conditions, with repeated prefixes and derived controls recorded separately.
Failed fixtures, Unsupported baselines and finite preparation retain zero source
credit. Actual joined `a4bc1ddc9` with 507 modules passes production SL loading in
15.675159260 s with stable inputs, quiet stderr and zero source credit. Wider
signatures, producers, entries and held contexts remain partial.

ENUM181 extends mixed exact-int reception to a required prefix followed by a
nonempty tail of plain integer-literal defaults. Authenticated source/default
metadata reuses the existing snapshot, receive schedule and default binders for
ordinary positional or all-named CVs. Six production-SL comparisons pass at
`6012663b0`/508: five precision cases and one existing quiet-default control, with
native observations reused. AuthorAL118 and derived peerAL84 execute 202 physical
conditions across four fixtures (178 body, 24 setup); their cuts remain separate.
The original peer fixture timeout300 and prior Unsupported/preparation cuts keep
zero credit. Actual `b9c23c11e`/508 loads in 15.871470989 s with zero source credit.
Wider signatures, producers and lifetime contexts remain partial.
[Review](coverage/semantics/optional-integer-tail-reception-review.json).

ENUM182 removes the mixed-mode-only guard from that same optional exact-int
header proof. All-value and all-reference headers now share the existing source,
default, receive, task and owner rules with mixed headers. Six exact production-SL
originals pass at `200b2b8ec`/508, reusing six native originals once. Author AL126
and independent derived AL176 execute 302 physical conditions across six fixtures
(266 body, 36 setup), with no unique-count claim or state source credit. The
separate actual `3a421cff7`/508 load passes in 15.479143263 s with zero source credit.
Earlier ENUM181 cuts, Unsupported controls and failures retain their original identities;
wider signatures, producers and lifetimes remain partial.
[Review](coverage/semantics/homogeneous-optional-integer-reception-review.json).

ENUM183 adds homogeneous value-only and reference-only required exact-int
headers, including arity1, to the all-named ordinary CV path in module518. Only
mixedness and the redundant two-formal bound are removed; other source/shape,
strictness, readiness, task, owner and cleanup rules remain unchanged. Seven exact
originals at `1b899490f`/508 cover six precision cases and one quiet control with
fresh native reuse. Author AL166 and independent derived AL211 execute 377
physical conditions across eight fixtures (329 body, 48 setup), with no unique-
count claim; pre-receive90 remains separate/source0. Actual `f4eb179e4`/508 loading
passes in 15.435803216 s with zero source credit. Prior mixed and optional cuts
are unchanged and not replayed. Mixed sends and wider signatures, producers and
lifetimes remain partial.
[Review](coverage/semantics/homogeneous-named-required-integer-reception-review.json).

Ordered exact-int reception now admits an ordinary positional CV prefix followed
by a nonempty named CV tail under required-only or plain integer-literal optional/
all-optional headers, with arbitrary declared value/reference modes. A shared518
predicate and two518/519 substitutions preserve named validity before shape,
genuine holes/defaults, source order versus receive order, snapshots and cleanup.
Earlier all-optional source/state cuts stay separate. Seven mixed-send SL originals
(six precision and one quiet) atb383/private508 reuse fresh native observations once.
Author127 retains original35 plus corrected92; peer194 is independent. Their321
physical conditions (279 body,42 setup,7 fixtures) have source0 and no unique-count
claim; original constructor-list parser failures stay0. Actual `7fc065501`/508
loading passes in 15.578487689 s/source0. Wider defaults, signatures, producers and
lifetimes remain partial.
[All-optional review](coverage/semantics/all-optional-integer-reception-review.json),
[mixed CV-send review](coverage/semantics/mixed-cv-integer-reception-review.json).

ENUM186 admits plain integer defaults or finite unary `+`/`-` integer-literal
chains when existing pure `psnumber` yields PSINTEGER. Optional/all-optional
exact-int headers retain their existing positional/named/mixed ordinary CV shapes.
Exact full source expressions and parameter index/origin agree with PDSTORED
origin/kind and the compiled PINT; equal-value simplified ASTs are insufficient.
Receive/default-hole timing, copied values, live references, pending throws and
ordinary cleanup stay unchanged. Six exact private508 SL originals (five precision,
one quiet) reuse six natives once. Author150=original81+corrected69 and peer115
execute265 physical conditions:235 body,30 setup across five fixtures, source0
without a unique aggregate. Three failed67 fixtures and Unsupported remain0;
accepted81 and source/native cuts are not replayed. Actual `e6ae629b6`/508 loading
passes in 15.018899741 s/source0. Float/overflow/arithmetic/constant defaults and
wider signatures/producers/entries/lifetimes remain partial.
[Review](coverage/semantics/signed-integer-default-reception-review.json).

ENUM187 admits one root binary `+`/`-` default over two operands independently
classified PSINTEGER by the existing pure classifier, with a long-range result.
Exact full AST, parameter origin/index, stored descriptor and compiled PINT authority
remain conjunctive; old literal/unary defaults and receive/owner rules stay unchanged.
Three private508 SL originals (two precision, one quiet) reuse native originals
once. First-pass authorAL132 and peerAL130 execute262 physical conditions across
four fixtures:238 body and24 setup, all state-derived/source0 without a unique
aggregate. Pre-receive47 remains separate/source0; no new failures or old replay.
Actual `cd577eda4`/508 loading passes in15.482561237 s/source0. Nested arithmetic,
unary signs over arithmetic, overflow and wider defaults remain partial.
[Review](coverage/semantics/binary-integer-default-reception-review.json).

ENUM188 extends optional exact-int defaults to finite source-literal unary/binary
`+`/`-` trees. Every arithmetic child and intermediate must fit a target long; exact
AST/signature/index/origin/stored-PINT authority and old classifier fallback remain.
Three private508 SL originals reuse native originals once. First-pass authorAL104
and peerAL80 execute184 physical conditions across two fixtures:172 body and12
setup, all state-derived/source0 without a unique claim. Pre-receive34 remains
separate/source0. Two affected187 pure expectations become -6/-7 and are checked
by the new104 without renewing the old campaign. Derived out-of-range child
cancellation refusals carry source0 and make no engine-divergence claim. Actual
`227863411`/508 loading passes in15.548771071 s/source0. Other operators, float/
overflow, constant/object defaults and wider types/producers/lifetimes remain partial.
[Review](coverage/semantics/additive-integer-default-reception-review.json).

ENUM189 adds multiplication to finite source-literal integer-default trees.
Every arithmetic child and product must fit a target long; exact AST/signature/
index/origin/stored-PINT authority and old fallback remain unchanged. Three
private508 SL originals reuse native observations once. Corrected author AL103
and first-pass peer AL95 execute 198 physical conditions across two fixtures:
186 body and 12 setup, all source0 without a unique aggregate. Pre-receive38 and
the first pre-main author binding failure remain separate/source0; only that
fixture reruns. Actual `8730988b5`/508 loading passes in 16.058807609 s/source0.
Division remained partial at that cut; the extension below admits exact integer
division. Float/overflow, wider defaults and owning late payloads remain partial.
[Review](coverage/semantics/product-integer-default-reception-review.json).

ENUM190 admits exact division in those finite optional integer-default trees.
The divisor is nonzero and operands/quotient fit a target long; full AST/index/
origin, stored descriptor/PINT and supplied-versus-default authority remain
coupled. Reception and cleanup remain unchanged. Three private508 SL originals
reuse native observations once. Author108 and peer96 execute204 physical
conditions (192 body,12 setup), source0 with separate pre38 and no unique claim,
new failure or replay. Actual `492435ebd`/508 loading passes in15.922594844 s,
source0. Inexact division, wider operators/defaults/types/producers remain partial.
[Review](coverage/semantics/division-integer-default-reception-review.json).

ENUM191 adds seven closed-int modulo, shift and bitwise constructors to those
default trees through the existing pure kernels. Full AST/index/origin/stored-PINT
authority and all reception bodies remain; only valid left shifts wrap to a target
word. Three private508 SL originals reuse natives once. Separate author117 and
peer108 fixtures execute225 physical conditions (213 body,12 setup), source0 with
pre74 separate and no unique aggregate, new failure or replay. The current joined
load above is separate/source0. Power, float/overflow children and wider defaults,
types, signatures or owning producers remain partial.
[Review](coverage/semantics/integer-operator-default-reception-review.json).

ENUM192 admits finite integer-power defaults with long children, a nonnegative
exponent and a completed long result through the unchanged pure kernel. Full
AST/index/origin/stored-PINT and supplied-versus-default authority remain; an
unsupported child is refused even before exponent zero. Three private508 SL
originals reuse natives once. Separate author133 and peer95 execute228 physical
conditions (216 body,12 setup), source0 with pre67 separate and no unique claim,
new failure or replay. Actual `2d3fffd58`/508 loading passes in15.665881192 s/source0.
Float/overflow powers and wider defaults, types, producers and lifetimes remain partial.
[Review](coverage/semantics/power-integer-default-reception-review.json).

ENUM193 adds full/shorthand conditional and coalesce exact-int defaults using the
immutable actual declaration ENV. Bare resolved Boolean/null or admitted-long
conditions select long values; coalesce left is an admitted long or bare null.
All14 integer kernels retain their bounds while threading that ENV. Three normal
private508 originals use global names and reuse natives once; namespace/import/
scope checks are derived fixtures. Separate AL175/AL160 execute335 physical
conditions (323 body,12 setup), source0 with pre67 separate and no unique claim,
failure or replay. Actual `ccc4ed2f4`/508 loading passes in15.223471997 s/source0.
Wider values, operators, signatures and producers remain partial.
[Review](coverage/semantics/integer-selection-default-reception-review.json).

ENUM194 adds finite Boolean NOT, AND/OR and XOR conditions under the actual
declaration ENV. Decisive AND/OR skips its right truth projection; XOR needs both.
Selected defaults remain long-only with unchanged full source/default authority
and reception bodies. Three exact private508 SL originals reuse natives once.
Corrected author185 and first-pass peer138 execute323 physical conditions
(311 body,12 setup); pre68 is separate, all state/source0 without a unique claim.
The original author binding collision retains0 and only its fixture reran.
Actual `8fd314a07`/508 loading passes in15.792155415 s/source0; family `be54ee67f`
preserves its separate cuts. Wider conditions, defaults and lifetimes remain partial.
[Review](coverage/semantics/boolean-condition-default-reception-review.json).

ENUM195 adds eight comparison predicates over admitted longs as selection
conditions and normalized integer spaceship values. Both children retain their
actual ENV and long bounds; full source/default authority and reception bodies
remain unchanged. Three exact private508 production-SL originals reuse natives
once. Separate first-pass fixture-SL208/139 execute347 physical conditions
(335 body,12 setup); pre77 is separate, all state/source0 without AL or a unique
claim. The peer EOF-only cleanup changes no fixture; no failures or replay occur.
Actual `0aea1af1c`/508 loading passes in15.399514147 s/source0, separate from those
private cuts. Wider operands, selections, defaults and lifetimes remain partial.
[Review](coverage/semantics/comparison-integer-default-reception-review.json).

ENUM196 adds quiet integer casts of bounded long trees, resolved Boolean/null,
literal strings and compiler-eligible signed float-literal chains. Complete signs
precede float eligibility; string numeric prefixes/overflow retain saturation.
Full source/default authority and reception bodies remain unchanged. Three exact
private508 production-SL originals reuse natives once. Separate first-pass
fixture-SL131/142 execute273 physical conditions (261 body,12 setup), with pre77
separate and all state/source0 without AL or a unique claim. No failures or replay
occur. Actual `99485d599`/508 loading passes in16.086345817 s/source0, separate from
private cuts. Wider producers, selections, casts and lifetimes remain partial.
[Review](coverage/semantics/scalar-integer-cast-default-reception-review.json).

ENUM197 admits integer casts of Boolean-producing NOT, AND/OR, XOR and eight long
predicates in finite optional-default trees using the actual declaration ENV.
Ordinary integer/spaceship casts, full source/default authority and reception/owner
bodies remain unchanged. Three exact private508 production-SL originals reuse
natives once. Separate first-pass fixture-SL174/153 and pre77 retain their own cuts
and source0, without AL or unique-count credit; no failures or replay occur.
Actual `d92dd08ec`/508 loading passes in 15.629225030 s/source0, separate from private
cuts. General Boolean-valued selections and wider casts, producers, signatures and
lifetimes remain partial.
[Review](coverage/semantics/boolean-integer-cast-default-reception-review.json).

ENUM198 preserves selected primitive values below integer casts of full/shorthand
ternary and coalesce trees under the existing Boolean/null/long truth domain.
False, zero and empty strings retain a nonnull coalesce left value; only resolved
null selects the RHS. Original cast eligibility, full source/default authority and
reception/owner bodies remain. Three exact private508 production-SL originals reuse
natives once. Separate first-pass fixture-SL155/151 and pre77 retain distinct cuts
and source0, with old a=-7 positive; no AL/unique claim, failure or replay occurs.
Actual `c90b74ae3`/508 loading passes in 15.510795725 s/source0 at its own cut.
String/float truth conditions, selection beneath other operators, wider producers,
signatures and lifetimes remain partial.
[Review](coverage/semantics/selection-integer-cast-default-reception-review.json).

ENUM199 adds raw literal string and non-NaN signed float truth through five lines
in module519. Only an empty string or the single byte `0` is false; both float zero
signs are false and other non-NaN floats, including infinity, true. Existing cast
eligibility, compiler-root/source/default authority and reception/owners remain.
Three private508 production-SL originals match on their first semantic executions,
reusing natives once. The earlier catalogue recorder failure before selected-source
parsing/execution retains zero credit; a one-line catalogue correction preserves that cut.
Separate fixture-SL157/169 and pre77 retain distinct cuts/source0, without AL or
unique-count credit. Actual `9182b7aeb`/508 loading passes in 15.447642532 s/source0.
Explicit Boolean casts, general condition producers, operators and lifetimes remain
partial. [Review](coverage/semantics/scalar-truth-default-reception-review.json).

ENUM200 adds explicit Boolean casts over the existing bounded actual-ENV truth
projection, including nested casts and integer 0/1 conversion. Full source/default
and stored-PINT authority, operation-specific NaN/float eligibility and receive/owner
bodies remain unchanged. Three private508 production-SL originals match on their
first semantic executions, reusing native observations once. Separate first-pass
fixture-SL187/171 and pre91 retain distinct cuts/source0, without AL or unique-count
credit. The real unused float-NOT initializer stays deferred; tag/kind forgeries
without its compiled integer refuse. Actual `79b95118f`/508 loading passes in
15.494809378 s/source0. No failures or replay occur. General conditional and
Boolean-valued coalesce conditions, wider producers, signatures and lifetimes remain
partial. [Review](coverage/semantics/boolean-cast-default-reception-review.json).

ENUM201 adds full/shorthand ternary truth over the existing bounded actual-ENV
domain, evaluating the condition once and preserving original selected values for
later casts. Source/default and owner authority remain; Boolean-valued coalesce
conditions stay partial. Corrected private 508-module production-SL source-v2 matches one
existing quiet control and two new precision agreements, reusing natives once.
The original optional-Boolean dispatch failure and minimal diagnostics retain zero credit.
Separate first-pass fixture-SL183/184 execute 367 physical conditions (355 body,
12 setup), with pre91 separate at source credit 0 and no AL or unique-count claim.
Actual `3905effdf`/508 loading passes in 15.334248181 s at source credit 0. Wider producers,
signatures and lifetimes remain partial.
[Review](coverage/semantics/ternary-truth-default-reception-review.json).

ENUM202 shares an original selected AST and cached truth across ternary/coalesce
choices. Only resolved null selects the RHS; false-like nonnull leaves stay left.
Infinity retains quiet truth without integer eligibility, and selected string
`13tail` still casts to `13`. Source/default and owner guards stay unchanged.
Three first-pass private508 production-SL originals reuse natives once: one
existing quiet control and two new precision agreements. Separate fixture-SL212/238
execute450 physical conditions (438 body,12 setup), with pre91 separate/source0
and no AL or unique-count claim. Unused-helper cleanup preserves generated CASES
without rerun. Actual `b9a3ac1eb`/508 loading passes15.731924920s/source0.
[Review](coverage/semantics/coalesce-truth-default-reception-review.json).

ENUM203 adds explicit float-cast truth over that original-AST/cached-truth
certificate. Raw or selected strings use decimal-prefix conversion; numeric,
Boolean and null leaves preserve cached truth. Unknown/reached NaN refuses;
integer eligibility and full source/default/pool and reception owners remain.
Three first-pass private508 production-SL originals reuse native3 once: one
existing quiet control and two new precision agreements. Separate fixture-SL249/283
execute532 physical conditions (520 body,12 setup), with pre91 separate/source0
and no AL or unique-count claim. Unused peer construction cleanup preserves
identical CASES without rerun; no203 failure occurs. Actual `994493f99`/508 loading
passes16.131328344s/source0. CONCAT/general string or float producers, signatures
and lifetimes remain partial.
[Review](coverage/semantics/float-cast-truth-default-reception-review.json).

ENUM204 adds one decoded-byte projection for finite literal-string CONCAT truth
and explicit integer/float conversion. Empty values, byte order, NUL/non-ASCII
and selected original AST remain; source/default/pool/header and receive/owner
bodies stay literal. Assembled `0.0` is rawtrue, floatfalse and integer0.
Three first-pass private508 production-SL originals reuse native3 once: one
existing quiet control and two new precision agreements. Corrected author310
and first-pass peer314 fixture-SL conditions execute624 physical checks (612 body,
12 setup), with corrected pre91 separate/source0 and no AL or unique-count claim.
Original prefixture boundary-digit typo and author expected-MAX for infinite text
retain0; only affected fixtures repeat. Four old203 mixed string/int0 refusals are
checked freshly without old replay. Actual `484d489ce`/508 loading passes
33.197897111s/source0. Mixed/selected CONCAT operands, other string/float producers,
signatures and lifetimes remain partial.
[Review](coverage/semantics/concat-string-default-reception-review.json).

Current combined behavior is summarized below. Family docs and linked reviews
retain exact admission limits, original failures and tested cuts; this file does
not repeat historical receipt counts or renew their execution credit.

## Integrated behavior and entrypoints

| Family | Current behavior and scope |
| --- | --- |
| Source and compilation | Checked ASTs retain source occurrences, ordered declaration publication, lexical/called scope and emitted-task authority. Include/eval, anonymous classes, traits and linked headers use source-authenticated routes; remaining acquisition and linker contexts stay explicit. [Source context](docs/semantics/SOURCE-CONTEXT.md), [linking](docs/semantics/LINKING-HANDOFF.md), [classes](docs/semantics/SOURCE-CLASSES.md). |
| Values, operators and warning decisions | Arithmetic and conversions are pure executable SpecTec. Supported warning callbacks preserve saved operands, live delayed reads, source sites, handler changes and pending-Throwable order. Ordinary valid non-NUL interned and authenticated REQUEST string bases and keys use the existing byte rules for `??`, `isset` and `empty`. Concatenating two nonempty operands produces REQUEST identity with exact immutable STRINGDATA records. The [interned](coverage/semantics/string-offset-quiet-carriers-review.json) and [REQUEST](coverage/semantics/string-offset-request-carriers-review.json) reviews keep their source, AL/SL state and affected regression cuts separate. Actual combined 51a739458/496 loads successfully with zero source credit. Operators, casts, dimensions and undefined-variable routes remain partial across their producers. [Numerics](docs/semantics/NUMERICS.md), [dimensions](docs/semantics/DIMENSIONS.md), [comparisons](docs/semantics/COMPARISONS.md). |
| Arrays and references | Physical owner edges distinguish DIRECT copies from ALIAS cells, COW table copies, selected lvalues and shared descendants. Iterator spreads retain raw current references through key before copying the value; invalid-key cleanup retires current before DATA while protecting the partial builder. Ordinary initialized declared fields share the reviewed fold across legal return modes. Materialized/special/cyclic graphs and wider callback lifetimes retain their documented limits. [Array unpack](docs/semantics/ARRAY-UNPACK.md), [reference wrappers](docs/semantics/REFERENCE-WRAPPERS.md), [cleanup review](coverage/semantics/array-iterator-invalid-key-cleanup-review.json), [field review](coverage/semantics/array-iterator-byval-fields-review.json). |
| Comparisons | Reached physical slots, count/key/value order, live reference contents and COW snapshots decide comparisons. Visited captured-graph traversal has no fixed depth limit and reports an authentic active-left recursion Error; earlier identity/class/leaf decisions skip later unsupported payloads. Canonical root admission and acyclic Previous-path validation have no numeric context/length ceiling. Canonical same-kind roots of the admitted builtin kinds share the visited physical-slot fold after older admissions once both finite Previous paths authenticate, preserving cache/trace/previous/severity order and reached table effects. Invalid/cyclic/materialized/freeing Previous nodes, pending states and actually reached callback contexts retain family limits. Captured canonical builtin Throwables share this fold; every distinct equal-kind entry checks active-left recursion before slots, including Previous descent. Supported ordinary images of any visibility admit uncalled methods, locally authenticated interfaces including implicit Stringable, and finite source-parent paths validated by actual names, links and publication order. Seen origins reject parent cycles before layout expansion; builtin parents/hook/readonly and wider layout fences remain. Whole-path authentication stays eager. Empty inline same-class images return zero before the object recursion guard; actual empty caches retain table order, COW and ordinary owners. Empty foreach produces a real table, and empty cached clones share without a callback or start uncached with one. Private/protected fields retain mangled KEY/DECL authority through actual caches and final typed-alias source retirement. Declared INITIAL/UNSET holes retain inline position and physical cached INDIRECT count/key order. Deleted dynamic mirrors leave current live count/order intact; deleted-only clone histories preserve sharing and callback copy routes. [Dynamic-deletion review](coverage/semantics/throwable-trace-dynamic-unset-comparison-review.json). [Declared-hole review](coverage/semantics/throwable-trace-uninitialized-comparison-review.json). [Nonpublic-image review](coverage/semantics/throwable-trace-nonpublic-comparison-review.json). [Empty-image review](coverage/semantics/throwable-trace-empty-layout-comparison-review.json). [Current comparison contract](docs/semantics/COMPARISONS.md), [finite captured graphs](coverage/semantics/throwable-trace-unbounded-comparison-review.json), [finite Previous paths](coverage/semantics/throwable-previous-finite-comparison-review.json), [standalone traces](coverage/semantics/throwable-null-trace-comparison-review.json), [base fallback](coverage/semantics/throwable-base-null-comparison-review.json), [linked base](coverage/semantics/throwable-base-previous-comparison-review.json), [captured Throwables](coverage/semantics/throwable-captured-comparison-review.json), [ordinary methods](coverage/semantics/throwable-trace-methods-comparison-review.json), [local interfaces](coverage/semantics/throwable-trace-interfaces-comparison-review.json), [inherited images](coverage/semantics/throwable-trace-inheritance-comparison-review.json). |
| Calls and callable values | Ordinary, scoped, captured and magic-call routes retain the selected callee/receiver, lexical/called scope, argument origin, positional/named ordering and reference mode across later effects. Closure and pipe consumers preserve their real owners, send diagnostics and abrupt cleanup. Callable producers, signatures and reentry remain partial. Bounded NoDiscard declarations preserve pre-body warning and pending-owner behavior. [Attributes](docs/semantics/BUILTIN-ATTRIBUTES.md), [Calls](docs/semantics/SOURCE-CALLS.md), [Closure::call](docs/semantics/CLOSURE-CALL.md), [first-class callables](docs/semantics/SOURCE-FIRST-CLASS-CALLABLES.md). |
| Configuration and constants | Supported INI_SET/DEFINE/CONSTANT/DEFINED routes retain their selected callee, option/name and API timing. Iterator and named Generator inputs preserve real DATA/INPUT and Aggregate producer history, copied sends, named-key Error priority and pre-API cleanup. CONFIG typed-current reads reuse property-source validation; structural receipts remain valid after physical cache retirement. Iterator sends retain raw scalar snapshots or real finite ARRAY/ordinary-instance slot roots, then defer INI_SET binding/conversion until after DATA/INPUT cleanup. Strict callers reject copied Stringable INI_SET options before casting, including retained setters after source-variable rebinding. An exact converted `zend.assertions` option reaches array/object value TypeError before lookup or accepts copied nonnegative integers, null, Boolean false/true, valid warning-free nonnegative quantity strings and finite floats whose post-option precision produces a warning-free nonnegative quantity. A saved receipt certificate keeps entry precision through assertion state/restore; false and null retain present empty raw INI bytes while their parsed quantity is 0, and strings retain exact raw bytes. Other accepted values remain outside this receipt. COW, shared embedded aliases and API TraceArgs keep their ordinary owners. Generator/other consumers, effectful casts and wider lifetimes retain their documented limits. [Include/configuration](docs/semantics/INCLUDE-SOURCES.md), [constants](docs/semantics/SOURCE-USER-CONSTANTS.md). |
| Classes, properties and enums | Linked declarations preserve receiver identity, slot declaration, visibility, typed-reference sources, readonly/hook policy and diagnostic order. Supported magic getters and reference-get chains preserve alias/copy and rebind timing. Enum declarations lower to cached singleton cases with lazy backing checks, readonly slots, ordered interfaces and generated/user methods. Registered-loader first use for static calls and class-constant fetches preserves selected class/member order and source-authenticated resume; reached dynamic/named/folded/enum cases and forged-target rejection retain separate raw cuts under `.tools/enum-acquisition-review-state-*`. Captured enum `cases(...)` preserves its selected target and singleton cache after closure retirement. Captured scalar `from(...)`/`tryFrom(...)` preserve cold backing tables, ordinary/inherited constant aliases, caller strictness and cached case identity after closure retirement. Captured Stringable arguments preserve their real callback child and line, selected closure lifetime and temporary retirement before lookup. For published enums, class-string array callables select generated `cases()`/`from()`/`tryFrom()` before argument evaluation; a case-object receiver also invokes `from()`. Array Stringable conversion preserves the selected enum and temporary retirement. Computed, literal and folded class-method strings also fix generated targets before arguments, preserving full original bytes and real named Stringable children across rebinding and temporary retirement; packed Stringable origins remain Unsupported. First-class string and array captures use internal Closures held through argument clears and released after invocation. Source-certified direct or negated enum-case conditions in class constants retain selected case identity or scalar results, including a condition from another enum; wider object-valued conditional transfers, other callable routes, the default loader, case attributes, link/type contexts and object lifetimes remain partial. [Classes](docs/semantics/SOURCE-CLASSES.md), [properties](docs/semantics/SOURCE-PROPERTIES.md), [property references](docs/semantics/SOURCE-PROPERTY-REFERENCES.md), [enum evidence](docs/ARTIFACTS.md). |
| Generators and Fibers | Supported named/method/Closure producers retain actual resumer and callee owners, by-value or reference caches, supplied Throwables and catch/finally continuations across Fiber suspension. Receiver-free static and same-`$this` nonstatic Generator bodies called through finite scoped chains retain real scope after return; supported real Closure, captured/bound user-method, implicit invokable and admitted magic-handler factories also authenticate scoped method-created bodies when the original source scope differs. Direct Generator-bodied __invoke uses its runtime-selected method; admitted direct magic handlers retain their actual target/owner receipt through close and Fiber transfer. Delegation and SEND preserve their selected chains and copied/delivered owners. Wider producers, binding/delegation combinations and teardown remain partial. [Generators](docs/semantics/GENERATORS.md), [Fibers](docs/semantics/FIBERS.md), [delegation](docs/semantics/GENERATOR-DELEGATION.md), [reference yields](docs/semantics/GENERATOR-REFERENCE-YIELDS.md). |
| Lifetime, weak references and collection | Eager release tracks real ownership, pending results/Throwables, destructor frames and protected storage. WeakMap protocols preserve weak-Key visibility, ordinary Value owners, aliases, selective notification and conditional collection. Physical tracing handles admitted ordinary/materialized graphs; quiet same-Key entries and no-Map ordinary siblings use claimed first-visit counts. Canonical materialized destructor callbacks retain claimed count and nested-buffer authority across retrace, including ordinary caller locals and receivers. Source-authenticated temporary cleanup, borrowed result caches and unused WeakReference result transfer preserve potential-root order. Enum cases and original receiverless fake Closures skip GC candidate buffering while retaining their owners and graph edges; clone and bind copies remain collectable. WeakMap callbacks, skipped prior histories, residual and other active collector contexts remain open. Stable retired cell metadata owns nothing; pooled literal arrays remain rooted by compiled constants. [Eager cleanup](docs/semantics/SOURCE-EAGER-DESTRUCTORS.md), [reference returns](docs/semantics/SOURCE-REFERENCE-RETURNS.md), [weak references](docs/semantics/WEAK-REFERENCES.md), [cycle collection](docs/semantics/CYCLE-COLLECTION.md). |
| Diagnostics, output and environment | Supported handlers retain registration, callback and emitting-frame identity through warnings, throws and cleanup. Echo/print preserve left-to-right effects and flat-array diagnostics; bounded default output buffers retain native callback/output order. Request, clock, stream and startup profiles have explicit contracts rather than ambient host answers. Wider buffering/shutdown/tick behavior remains open. [Handlers](docs/semantics/SOURCE-ERROR-HANDLERS.md), [exception handlers](docs/semantics/SOURCE-EXCEPTION-HANDLERS.md), [output buffers](docs/semantics/OUTPUT-BUFFERS.md), [request inputs](docs/semantics/REQUEST-INPUTS.md). |

Copied positional Iterator `ini_get` now waits for a sole Stringable `precision`
option to retire before reading the live value; selected first-class getters
keep their original Closure through key-time rebinding. Held/named inputs stop
outside this receipt. [A107 review](coverage/semantics/config-iterator-get-stringable-review.json).

Copied positional Iterator `ini_restore` now waits for the same sole Stringable
`precision` option to retire before restoring startup precision. A selected
first-class restorer keeps its original Closure through key-time rebinding;
held/named options stop before the unvalidated restore.
[A108 review](coverage/semantics/config-iterator-restore-stringable-review.json).

A borrowed direct-CV `IteratorAggregate` may now return a fresh initialized
user Iterator for positional `ini_get` or `ini_restore` with the copied
Stringable `precision` option. The existing unary receipt runs after Iterator
and option cleanup; selected restore retains its original callee. Generator
returns remain SET-only. [A109 review](coverage/semantics/config-aggregate-unary-stringable-review.json).

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

OB08–09 use ordinary `ob_start` argument reception during normal post-output
executor queue release. Named/unpacked defaults, converted chunk/flag cases,
deprecations and type/count errors precede callback creation. NULL/default
callbacks then emit E_NOTICE and return false without pushing a buffer,
including in the authenticated destructor of a Notice handler's returned object.
Private and actual2257 composition strict433, author17 and independent4
source/request contexts and scoped reached checks pass at the recorded cuts.
OB10 adds pure callable creation after conversion, with no callback invocation
or buffer push. Its transient owner releases before the Notice, while ordinary
argument ownership preserves temporary invokable/array receivers, captured
Closure cells, bound method receivers and caught-throw cleanup. Selection survives
Notice-time reference mutation; earlier conversion-handler mutation affects lookup.
Consumed Closure metadata uses borrowed source certificates and owns nothing.
The VM argument's root decrement skips GC candidate buffering; array children
still use ordinary cleanup. The source and reached checks retain their separate
cuts in the [creation review](coverage/semantics/output-executor-creation-review.json).
OB11 freezes known invalid callback lookup after conversion, emits Warning then
the failed-start Notice, and keeps failure final even if the Warning callback
defines the missing function or repairs referenced selectors. Declaration-prefix
history and DIRECT snapshots are borrowed checking data. Retired Warning-handler
objects release before the current Notice handler runs. Warning-return destructor
throws preserve the pending operation and real builtin argument trace, retaining
the argument through catch and caller-local cleanup. Pending Notice selection
distinguishes eligible-handler skip from ordinary reporting/suppression.
[Failed-lookup review](coverage/semantics/output-executor-invalid-review.json).
OB12 shares one argument-discard certificate across admitted Warning and Notice
throws. A precreated Throwable exposes direct-cycle NOGC versus ordinary
array-child cleanup; a new Throwable retains the argument through its trace.
Consumed Closure checks borrow retired capture facts without adding owners.
Seven exact originals, 279 reported reached conditions and 90 affected Warning
conditions pass at the recorded private cuts.
[Notice-discard review](coverage/semantics/output-executor-notice-discard-review.json).
OB13 admits a live Throwable thrown by a selected Notice handler's returned-object
destructor before the saved cleanup resumes. The genuine `ob_start` trace keeps
its temporary callback through catch; precreated-Throwable controls separate
VM root NOGC from ordinary array-child cleanup. An `ob_end_clean` countercontrol
also exposes the shared output-intrinsic trace frame. Seven exact originals
agree, and three reached groups pass 165 reported conditions (author 54,
independent 76, off-kind 35). Private strict435 passes; earlier failed packets
retain zero credit. [Returned-Notice throw review](coverage/semantics/output-executor-notice-retval-throw-review.json).
OB14 admits the normal Warning handler's returned-object destructor to a nested
post-deactivation `ob_start`. Its saved Warning receipt and unreleased RESULT
cleanup authenticate the start while the handler is disabled. Three exact
originals agree with native PHP; the genuine reached state passes 42 reported
conditions, and private strict435 passes. The selected handler resumes for the
original failed-start Notice after nested default Notice reporting. Throwing
paths through this new Warning-retval bridge remain outside this milestone.
[Normal Warning retval review](coverage/semantics/output-executor-warning-retval-nested-review.json).
OB15 adds ordinary positive-chunk pre-entry reference-warning throws from echo,
print and inline output. Diagnostic cursors retain the exact running producer;
prepared scalar wrappers retire before undefined-result failure routes live bytes
through lower buffers. Reached lower user chunks skip entry while smaller chunks
retain their bytes. Warning output retains PRODUCED without deprecation, and
owned print operands retire before catch without assigning the print result.
Seven targeted originals and one promoted original agree. Cached parameter
metadata survives a warning retiring its borrowed method receiver; actual entry
after retirement stays explicitly Unsupported. Prepared-prefix and producer fronts pass 108
reported conditions at their separate cuts. Eleven independent originals and one
SL435 front with seven reached groups/475 conditions pass at the repaired cut.
[Independent review](coverage/semantics/output-vm-reference-warning-review.json)
retains the receiver-retirement finding and original failures; the
[author evidence](coverage/semantics/output-vm-reference-warning-author.json)
keeps its separate source and reached cuts.
Explicit lower-cascade/FINAL pre-entry warnings and wider diagnostic cleanup
remain partial.
OB16 preserves scalar output-handler returns through produced-output deprecation
throws in source VM output and all six direct buffer APIs. Normal headers and
result bytes commit before pending lower routing; FALSE and suppressing results
retain their distinct dispositions. Ignored diagnostic-return destructors retain
the disabled running layer, real VM source sites and authentic API trace frames.
Owned producer reentry, current precision and frozen getter copies stay ordered.
Sixteen authored originals, two repaired fresh-trace witnesses and three reached
fronts/160 conditions pass at their recorded cuts. Seven independent originals
and one SL436 front with two reached groups/110 conditions pass at the repaired
cut. [Independent review](coverage/semantics/output-deprecation-warning-review.json)
records the trace findings, real owners and exact evidence. FINAL/lower API
cascades and wider return/control dependencies remain partial.
OB17 retains actual returned reference cells through warnings and callee cleanup,
then converts their live scalar payload without changing aliases. Referenced
FALSE suppresses, referenced TRUE emits1, and unused print/for output still
requests the callback result. Defined Notice/cleanup throws keep the return;
normal FINAL uses the existing drain, while pending FINAL and nonscalar payloads
remain Unsupported. Eight exact independent originals and one SL438 front with
two groups/183 conditions pass. The real HCELL release authenticates its COMMIT
continuation even after cell retirement. [Independent review](coverage/semantics/output-reference-return-review.json)
records the return-demand regression, release guard and affected checks;
[author evidence](coverage/semantics/output-reference-return-author.json) retains its separate cuts.
OB18 adds Array return conversion through the real Warning and child release,
then commits `Array` while preserving pending replacements, traces, frozen getters
and late PRODUCED flags. Reference unwrap transfers the actual Array before
warning-time alias changes; a narrow GC handoff hook leaves the later retval
decrement ordinary. Twenty author originals and two reached groups/234 conditions
pass at recorded cuts. Four independent originals and one SL439 front with three
groups/162 conditions pass at the final cut. [Independent review](coverage/semantics/output-array-return-review.json)
records real transfer/retirement owners, forged-source fallback and affected scalar
marker authority. That cut leaves FINAL Array and object/resource conversion Unsupported.
[Author evidence](coverage/semantics/output-array-return-author.json) retains the
failed dispatch diagnosis, scoped GC reviews and affected renewals.
OB19 adds ordinary standard-object/Stringable output returns, retaining the
original retval, cast receiver and actual method result through their ordered
cleanup. Returned string cells are read late; defined return-by-reference Notice
throws keep their cell and pending Throwable through genuine frame or unstaged
owners. Pending exceptions skip the method body while preserving the native cast
guard decrement and destructor-visible GC candidate. Conversion Errors, fresh
method throws and destructor replacements preserve normal buffer processing,
frozen getter copies and API/VM traces. Eighteen exact normal originals, two
refusal controls and four reached groups/420 conditions pass at their recorded
cuts. Checks and remaining FINAL/internal/custom/resource boundaries are recorded in
[author evidence](coverage/semantics/output-object-return-author.json). Five independent
originals agree at their recorded cuts; three reached groups/219 conditions pass
at the final scope-repaired cut. [Independent review](coverage/semantics/output-object-return-review.json)
records real C-frame authority, late-cell traces and collector dispatch. The two Notice originals retain public60 timeout cuts
with zero source agreement; their completed ownership fronts are state evidence.
That source-performance limitation remains unfinished.
OB20 extends normal FINAL returns to Arrays and ordinary Stringable objects.
Warnings retain `Unknown:0`; known methods enter at a null callsite/internal line
while the registration remains documentary metadata. Actual retval/cast owners,
frozen converted bytes and the normal drain retain their order. Two exact normal
originals, one pending refusal and a reached Array group/95 conditions pass at
their recorded cuts. [Author evidence](coverage/semantics/output-final-conversion-author.json)
records authority and limits. One independent normal original and one SL446
group/69 conditions validate the actual null caller, two Object owners, internal
trace and forged/nested frame refusals through full drain.
[Independent review](coverage/semantics/output-final-conversion-review.json) records
the exact cuts and observer/fixture corrections. Pending
conversion exceptions, FINAL non-Stringable Errors and abandoned cast/fatal
owners remain explicit dependencies. OB19's public Notice performance limitation
is unchanged.
OB21 adds direct fatal reporting for a top FINAL non-Stringable return. Real
null-C entry reports `Unknown:0`/255 before retval destruction; a source-only
abandoned-C receipt retains the actual object/FCI owners through existing
deactivation and inactive executor cleanup. No Throwable, method or cast guard
is fabricated. Two exact originals and one reached user-T packet/14 assertion
groups pass at their recorded cuts. The [independent review](coverage/semantics/output-final-error-review.json)
clears public validity, strict receipt/class-history guards, budgets and full
deactivation. A readonly view removes only the current authenticated receipt
from class-history checking to break recursive validation. [Author evidence](coverage/semantics/output-final-error-author.json)
preserves the initial failure and timed-out fronts with zero credit. Lower cascades,
pending cast exceptions and the earlier Notice performance limitation remain open.
OB22 handles a sole direct literal-new Exception throw from a no-local FINAL
`__toString` body with no selected exception handler. The actual null-C handoff
retains the RV and cast guard as two owners before ordinary receiver cleanup,
then reuses real Throwable reporting/release and deactivation. One exact
retained-destructor witness and 14 reached assertion groups pass at their recorded
cuts. The [independent review](coverage/semantics/output-final-cast-throw-review.json)
clears real owner/GC transfer, Throwable retirement, public guards, budgets and
full fatal completion; [author evidence](coverage/semantics/output-final-cast-throw-author.json)
keeps earlier failures at zero.
OB23 extends the direct literal-new builtin `Exception` route to ordinary compiled
CVs and in-method catch/finally. Real null-C restoration precedes ordered local
destruction; an actual frame-exit barrier retains retval/cast owners even when
no jobs or user destructor exist. Borrowed birth metadata clears on catch or
staged/unstaged normal return. A structural saved-consumer check removes repeated
immutable declaration replay during pending unwind; full capture/public/report
authority remains. One exact original now agrees within its unchanged 90-second
cap. [Author evidence](coverage/semantics/output-final-cast-locals-author.json) and
[independent review](coverage/semantics/output-final-cast-locals-review.json) retain
the source, owner, native-header, budget and normal-return cuts. Selected handlers,
supplied identities, replacement chains, wider constructor/result owners, ticks
and lower FINAL cascades remain partial; prior performance/paused boundaries stand.
OB24 adds a local destructor's fresh literal-new `Exception` at its own genuine
null-C return. Its fatal abort retains the saved outer exception, remaining outer CVs,
two destructor C protections and the outer retval/cast pair, with NULL previous
and ordinary reported-Throwable release before deactivation. One exact original
and independent primary11/caught2/finally2 groups pass, including public validity
after real normal owner consumption. Source/runtime and the current 451-module
joined load are integrated. [Review](coverage/semantics/output-final-cast-nested-review.json),
[author evidence](coverage/semantics/output-final-cast-nested-author.json).
OB25 replaces literal-message/latest-object freshness in the structural native
paths with a genuine completed `CTOR_NEW` record. Actual selected receiver/result,
NEW site and normalized fields survive arguments; only the matching own-code throw
becomes pending. Catch/normal consumption and retired-report validation preserve
the existing owners. Two original string-CV/helper-allocation sources agree exactly
with PHP under the unchanged 90-second cap.
[Author evidence](coverage/semantics/output-ctor-birth-author.json) and
[review](coverage/semantics/output-ctor-birth-review.json) retain the affected cuts;
independent 28 provenance, 5 local-endpoint and 8 catch/finally groups pass.
The current 452-module joined load passes. Current constructor, rendering and
held-path bounds remain.
OB26 transports a completed fresh builtin `Exception` from a direct no-argument
nongenerator helper into the existing native output consumer. Its producer origin
and native call site remain separate; only the same pending identity at real VM
restoration advances to native report authority. Helper cleanup keeps its producer
FUNCTION and restored native CURRENT/callsite, with ordinary staged/unstaged release.
Both frozen originals agree exactly under90; the reached helper-restore front passes
8+8 groups. [Author evidence](coverage/semantics/output-helper-unwind-author.json) and
[review](coverage/semantics/output-helper-unwind-review.json) retain the affected cuts.
Independent 71 transport/report/issuer/clearing/empty/byref groups pass, including
the current-continuation owner guard at birth and its checked source bridge.
The current joined 454-module interface load passes.
Constructor-argument aborts, owning saved continuations and held domains stay outside
this cut.
OB27 folds the actual finite saved helper contour, retaining immutable leaf birth
and native-consumer facts plus a nonowning position cursor. Each same-pending real
VM restoration consumes one frame tail, including recursive activations with
identical contexts. Departing cleanup FUNCTION/caller/callsite remain distinct;
only contour exhaustion at the original null-C boundary grants native authority.
Intermediate catch/normal overrides clear the contour, with current-at-birth and
every saved-continuation owner bounds preserved.
[Author evidence](coverage/semantics/output-call-contour-author.json) and
[review](coverage/semantics/output-call-contour-review.json) record the affected cuts.
Two exact per-source comparisons finish in73.295/57.220 seconds under90, with
original mixed-batch and layered/control timeouts retained0. Independent31 actual
edge/owner/report/receipt/intermediate-clearing groups pass; complete old26 fixture
adaptation is declaration-only. The current455-module joined load passes.
OB28 carries a completed fresh by-value factory result through its actual
RETURN_UNWIND/result/compiled-CV cleanup handoff before the native caller throws
it. Producer NEW/RETURN and native call/THROW are authenticated separately;
restored CURRENT alone grants no authority. The nonowning three-phase fact uses
existing return/value owners and constructor hook, with no80/161/257 change.
Two exact frozen originals agree in46.463/66.174 seconds under90; the affected
staged/unstaged owner/phase front passes7+7. Independent45 provenance, return-slot,
report/retirement, override/catch, two-site identity and native-destructor checks pass.
The actual current457-module joined load and169/306 inventory pass at the recorded cut.
[Author evidence](coverage/semantics/output-factory-return-author.json) and
[review](coverage/semantics/output-factory-return-review.json) retain the exact cuts.
OB29 folds finite by-value factory-return contours with immutable leaf NEW/RETURN
and final native THROW facts. Selected intermediate RETURN(call) sites and each
actual same-object frame pop consume one cursor position, including identical
recursive contexts. Cleanup VALUE belongs to the actual departing function;
final capture requires an exhausted contour and no remaining contour VALUE owner.
Intermediate normal override clears partial RETURNED provenance before retirement.
Two exact originals agree in 50.700/59.611 seconds under 90; 55 affected assertions
and baseline 45 on the unchanged runtime remain separate. Independent 48 provenance,
report/retirement, cleanup/override, catch and native-destructor relay groups pass.
The actual 458-module joined load and 169/306 inventory pass at the recorded cut.
[Author evidence](coverage/semantics/output-factory-contour-author.json) and
[review](coverage/semantics/output-factory-contour-review.json) retain the exact cuts.

OB30 follows completed fresh factory results through real private compiled-CV
publication and a later matching variable throw. Nonowning cell associations
preserve siblings, selective rebinding/catch and the selected historical report
fact while existing CV/pending owners supply the transfer. The single-CV source
matches native in 64.972 seconds under 90; multiple-CV public comparisons still
time out and retain zero credit. The baseline passes 16 owner checks and the
affected front passes 7. Independent 49 protocol, refusal, selective clearing,
cleanup, native-consumer and retired-receipt groups pass. The measured early commit
rejection is filtered before full validation without removing admission authority.
The actual current462 joined load and 169/306 inventory pass at their recorded cut.
[Author evidence](coverage/semantics/output-factory-cv-author.json) and
[review](coverage/semantics/output-factory-cv-review.json) retain the separate
source/state/performance cuts.
OB31 stores fresh factory results in ordinary helper CVs before their actual
same-cell VARIABLE throw. Recipient frame position and cell distinguish recursive
and caller siblings; normal RETURN-to-WRITE and exceptional same-pending restoration
use separate cursors. Only real VM pops exhaust the latter at the original native
C0. The helper's CV releases before native reporting, retaining the departing
FUNCTION and real pending owner. 35 independent groups cover pivotal public validity, guard refusals,
reports/retired receipts, sibling/recursive isolation, clearing, cleanup and staged
local-native ownership; the failed local aggregate and its C0 observation stay zero.
Both public 90-second attempts time out with zero source agreement. No shared
validator or generic owner/return protocol changes; public source performance
remains unfinished. The actual 465-module joined load and 169/306 inventory pass;
complete old30 fixture adaptation is declaration-only.
[Author evidence](coverage/semantics/output-factory-helper-cv-author.json) and
[review](coverage/semantics/output-factory-helper-cv-review.json) retain the scoped cuts and failures.
Generated native `__toString` errors retain actual producer/source authority
through FINAL cleanup: scalar/private-CV return checks; quiet integer/string binary,
unary-string and bool/null bitwise-not TypeErrors; post-body missing-return TypeError; numeric
division and quiet modulo DivisionByZeroError,
negative integer shifts ArithmeticError, and pool-integer UnhandledMatchError in
authenticated scan/table modes. Own source/opcode/compiled line, exact request/materialized
identity and native/current/nonowning bounds remain mandatory. Four-field facts
add no owner; live admission rechecks normalized fields, while retired receipts
bind the original source and abandoned native row.

Native T2/Error1 persist through real CV retirement and empty-release/C0;
normal publication retains retvalT1. Catch and bare-finally consume in-body errors;
a finally return prevents the appended missing-return check. Empty method CVs
are admitted for these generated errors; the
structural constructor-birth gate and separate no-CV literal-throw route are
unchanged. No shared match/type/return/root/renderer protocol is broadened.

OB50 admits quiet exact PFLOAT modulo operands through the existing integer
conversion's empty diagnostic result. Original operands, own Mod/opcode/RHS line
and real ordered54/exact152 transition remain required. Three error originals
and a normal contrast agree in 71.903/70.855/68.572/42.761 seconds under90. Ten
affected groups include real empty-release/C0; four reached lossy-refusal groups
retain the precision diagnostic and Unsupported boundary. Ten independent
source-authority/catch/finally groups pass first applications at fixed494.
Baseline7 adds zero agreement. Exact source/runtime/test are accepted at
`34aaaab8dd`; its actual combined494 load passes in 26.583237268 seconds with
zero source credit. Private2fe/494 evidence remains at its original cut. Existing
bounds and OB31 performance remain unfinished.

OB51 shares the own-child name/compiled-line/private-cell read proof across the
existing binary, unary and BITNOT error captures. Validated string carriers join
plain scalar CV values. Original operands are retained; KNOWN branches and return
filters stay pointwise. Seven exact originals agree under90, including distinct
two-CV and literal/CV MUL order. Four real CV-retirement/C0 groups and fifteen independent
authority/driver/catch/finally groups pass; baseline26 and the reference Unsupported
control add zero agreement. Exact source/tests are accepted at `3312a9d34c`; its
actual joined496 load passes in 14.736813546 seconds with zero source credit.
Private495 cuts remain separate; fixture corrections and unused fronts add zero.

OB52 admits quiet private scalar-CV subjects to the existing scan/table match-error
path. Actual delayed reads and Module144/152 materialization preserve current subject
values; static own-child/CODE/CVS authority survives real CV and Error retirement
without rereading dead storage or adding owners. Seven original agreements and
one independent true/table agreement pass at their separate 496-module cuts. Eighteen
independent SL authority/clearing groups and two actual retired-receipt groups pass.
Reference and undefined source controls remain Unsupported with zero agreement.
Both AL300 timeouts retain zero credit and undetermined causes; caps are unchanged.
Source/tests through `1b813f560` are independently cleared for integration;
current joined MAIN evidence remains separate. [Author](coverage/semantics/output-final-cv-match-error-author.json)
and [review](coverage/semantics/output-final-cv-match-error-review.json).

OB53 admits existing quiet scalar coercions to DIV/MOD zero-error capture.
DIV uses `COERCED(_, false)`; MOD strings use the actual `STRINT(_, eps)` result,
preserving integer, quiet-float and saturating string-long distinctions. Both
original operands retain rootless and S-aware string identity checks before the
unchanged raw152/source/owner protocol. Three first source agreements and two
actual retired-receipt groups pass. Seven independent DIV and eight MOD groups
form a stable completed prefix; three corrected noisy groups pass separately. The aggregate stays failed; both
unexecuted noisy-fixture failures retain zero credit. Noisy production remains
Unsupported with exact deprecation-prefix output and zero agreement. Source/tests
through `ec598c530` retain their private 501-module cuts. Source/tests integrated
at `7e81d487b7`; its actual joined503 SL load passes in 14.979878857 seconds with
zero source credit. [Author](coverage/semantics/output-final-quiet-zero-coercion-author.json)
and [review](coverage/semantics/output-final-quiet-zero-coercion-review.json).

OB54 admits quiet scalar integer coercions to negative LEFT/RIGHT shift capture
through the existing modulo conversion law, retaining both original operands,
rootless/string identity guards and genuine ordered54/exact152 authority.
Three source agreements, four actual CV-retirement/C0/retired-receipt groups and
independent LEFT6/RIGHT6/noisy3 groups pass at separate private504 cuts. Noisy
and reference sources remain Unsupported with zero agreement; a derived two-noisy
fixture preserves left-then-right diagnostics. Source/tests through `cb6012223`
are independently cleared. [Author](coverage/semantics/output-final-quiet-shift-coercion-author.json)
and [review](coverage/semantics/output-final-quiet-shift-coercion-review.json).

OB55 admits quiet integer-coercible non-PINT left values to the MODULO/BADNUMBER
right-string TypeError capture. Original operands retain rootless and S-aware
string admission; Module54 left conversion and exact Module152 materialization preserve
the original type names. The old PINT/KNOWN-right arm remains pointwise. Two exact
production SL originals, eight actual CV-retirement/C0/retired-receipt groups and
independent 6/9/3 guard groups pass at private 505-module cuts. Five native originals
and five unchanged baselines are reused without replay or new baseline credit;
noisy/reference remain Unsupported with zero agreement. A fresh coherent
plain-string guard validates the sole old MOD
expectation promotion. Source/tests are integrated at `7cdfeb622`; its actual
joined 506-module SL load passes with zero source credit. Private source/state
cuts remain separate. No kernel, tag, root, task or lifetime
expansion is added; held bounds and OB31 performance remain unfinished.
[Author](coverage/semantics/output-final-quiet-modulo-type-coercion-author.json)
and [review](coverage/semantics/output-final-quiet-modulo-type-coercion-review.json).

OB56 shares the existing arithmetic scalar-number admission across ADD/SUB/MUL/DIV
TypeErrors with quiet non-PINT left values and a BADNUMBER right string. Both
original values retain rootless and S-aware string guards; real Module35/404/152
keeps RHS scratch, original type names and native multiplication slot order.
The old PINT and MOD55 branches remain pointwise. Four exact originals, eight
actual CV/C0/retired-receipt groups and 21 independent groups pass at their private
505-module cuts. Normal/noisy/reference baselines add zero new source credit;
fresh controls retain quiet success, leading-numeric Warning and reference refusal.
Three coherent fresh guards validate the old ADD/SUB/DIV expectation promotions
without replay. Source/tests are integrated at `e9f8c0ec0` and registered at
`c4af99fa0`; the actual `7251409ec` joined507 SL load passes in 15.220595181 seconds
with zero source credit. Private cuts stay separate; held bounds and OB31
performance remain unfinished.
[Author](coverage/semantics/output-final-quiet-arithmetic-type-coercion-author.json)
and [review](coverage/semantics/output-final-quiet-arithmetic-type-coercion-review.json).

OB57 preserves leading-number arithmetic Warning followed by TypeError through
admitted ordinary named returning handlers. Defined private nonreference scalar
CVs and non-NUL strings retain their original operand types, source and native
slot order; false handlers preserve the default Warning. Five error-source
agreements, author lifecycle8 and independent direct14 plus empty-cleanup2 groups
retain separate private505 cuts. The normal prepatch control renews no source
credit. Direct restoration uses no destructor-operational mode; only the unused,
uninstantiated class control exercises real empty CLEAN with no old-Value owner.
Original fixture failures remain0. Actual `e1025e63c`/508 loading passes in
15.708744843 s with zero source credit. That cut does not establish default/no-
eligible-handler capture; wider contexts, held bounds and OB31 remain unfinished.
[Author](coverage/semantics/output-final-arithmetic-warning-type-error-author.json)
and [review](coverage/semantics/output-final-arithmetic-warning-type-error-review.json).

OB58 adds the no-eligible-handler BINARY path for leading-number arithmetic
Warning then TypeError. Existing private reads and rootless/string guards retain
live operands; the default MUL path requires its real unswapped receipt. Actual
mask/display settings govern the Warning projection. Five exact SL agreements
(new ADD/MUL/DIV/normal plus the retained SUB original/native/path), author
lifecycle8 and independent11 groups retain separate private505 cuts. The peer
packet includes exactly two fresh conditions for the one affected old SUB guard,
without renewing the prior campaign. No failures or source/native retries arose.
Actual `286ef4a89`/508 loading passes in 15.588131937 s with zero source credit.
Wider contexts, held bounds and OB31 performance remain partial.
[Author](coverage/semantics/output-final-default-arithmetic-warning-type-error-author.json)
and [review](coverage/semantics/output-final-default-arithmetic-warning-type-error-review.json).

OB59 admits quiet nonnumeric left strings with quiet numeric right scalars for
FINAL ADD/SUB/MUL/DIV TypeErrors. Twenty-nine additive module456 lines retain
physical slots, original RHS scratch, rootless/S-aware identity, unchanged raw
events and exact152. Six source comparisons at `44a63ab24`/505 reuse six native
originals once; separate author8 and peer12 SL groups retain their own cuts.
Heterogeneous swapped MUL preserves native physical order. The prior56 normal
original is retained without replay or renewed credit. Unsupported baseline and
compile-only reviewer preparation failure remain0. Actual `37f36b283`/508 loading
passes in 15.520188379 s with zero source credit. Kernels, tasks, fields, roots,
reads, lifetime and held bounds remain unchanged; true-swapped leading RHS, wider contexts
and OB31 remain partial.
[Author](coverage/semantics/output-final-left-arithmetic-type-error-author.json)
and [review](coverage/semantics/output-final-left-arithmetic-type-error-review.json).

OB60 admits two valid nonnumeric strings to quiet FINAL ADD/SUB/MUL/DIV
TypeError capture, preserving original source reads, physical slots and RHS
scratch under the existing identity/native/current/owner proofs. Five exact
source comparisons reuse five native originals once; author4 and peer9 SL groups
retain separate private505 cuts. Equal string type names do not distinguish
message order; distinct X/Y state checks retain true-swap scratch, with OB59's
heterogeneous evidence remaining separate. Prior56 NORMAL is retained without
replay or renewed credit; baseline/preparation failures remain0. Actual
`70377d7c7`/508 loading passes in 14.958761738 s/source0. Kernels, tasks, fields,
roots, reads, lifetime and held bounds stay unchanged; true-swapped leading RHS, wider contexts
and OB31 remain partial.
[Author](coverage/semantics/output-final-both-string-arithmetic-type-error-author.json)
and [review](coverage/semantics/output-final-both-string-arithmetic-type-error-review.json).

FINAL string TypeErrors preserve actual physical MUL order. Unswapped
nonnumeric-left/leading-right remains quiet; true swap converts the leading RHS
first and warns before rejecting the left. The opposite true-swapped direction
now rejects the BAD original RHS first without converting the leading left,
producing a quiet TypeError. Disjoint404 dispatches use unchanged35 before
separate456 captures; original reads, physical slots, RHS scratch, exact error
materialization and owner laws remain authoritative. Earlier quiet/Warning cuts
stay separate. One new production-SL original reuses its fresh native observation
once at private505; fallback1, author4 and peer10 first-pass SL groups retain
source0 cuts. Baseline37.682s Unsupported with an incorrect Warning remains0.
Actual `749fa1776`/508 loading passes in 15.932522630 s/source0. Stdout profile
checks are raw/capture-only and add no later C0-rendering claim. Wider producers,
eligible handlers, rendering/lifetimes, held lanes and OB31 remain partial.
[Quiet review](coverage/semantics/output-final-leading-right-arithmetic-type-error-review.json),
[swapped-Warning review](coverage/semantics/output-final-swapped-arithmetic-warning-type-error-review.json),
[first-BAD author](coverage/semantics/output-final-swapped-left-arithmetic-type-error-author.json)
and [review](coverage/semantics/output-final-swapped-left-arithmetic-type-error-review.json).

OB64 preserves a default leading-number Warning before FINAL DivisionByZeroError
for an admitted defined private nonreference CV divided by its original compiled
CONST PINT0, with no eligible Warning handler. Existing source/value/CONST-rank
proofs retain raw35 Warning order, original0 scratch, exact152/live Error and
current/native/owner bounds; readers, kernels, tasks, roots and lifetime rules
remain unchanged. One private505 production-SL comparison reuses native01 once
and agrees on P/Warning then DivisionByZeroError255. Separate author4 and peer9
first-pass SL groups have source0; peer9 includes a genuine divisor1 source-state
refusal. Preeditraw1 and baseline31.935s Unsupported/P+Warning retain0. Mask0 and
display0 capture pass; buffered stdout Warning stays Unsupported without later
rendering credit. Actual `c0d891c7c`/508 loading passes in 15.345181812 s/source0.
Other zero coercions/slots, handlers, wider producers/ownership/rendering/lifetimes,
held lanes and OB31 remain partial.
[Author](coverage/semantics/output-final-default-division-warning-error-author.json)
and [review](coverage/semantics/output-final-default-division-warning-error-review.json).

OB65 adds only the original compiled NULL divisor to that default capture. Real
source/value and child1 CONST authority remain; an equal Error after substituting
NULL into an integer-zero source state still refuses. One private505 production-SL
original reuses native01 once. Author4 and independent peer9 first-pass SL groups
retain separate source0 cuts through an exact tested-blob bridge to418. Baseline
Unsupported and raw01 pre-evaluation binding failure remain0; corrected raw02
precode passes separately/source0. Actual `8466a7b90`/508 loading passes
in15.767998964 s/source0. Other zero forms/slots, handlers, owning/reference/place
operands, wider producers/rendering/lifetimes and OB31 remain partial.
[Author](coverage/semantics/output-final-default-null-division-warning-error-author.json)
and [review](coverage/semantics/output-final-default-null-division-warning-error-review.json).

OB66 extends the same original compiled quiet scalar-zero capture to false,
signed floating zeros and quiet numeric-zero strings. Existing source/CONST-slot,
original scratch, ordered Warning and exact live Error proofs remain required;
equal Error cannot substitute source/value or carrier identity. Five private505
production-SL originals reuse five native observations once. Separate author4 and
peer10 fixture groups retain source0, including genuine nonzero/noisy RHS refusals.
The original baseline-classifier failure and corrected unexecuted tails, Unsupported
baselines and precode5 retain0. Actual `8730988b5`/508 loading passes in
16.058807609 s/source0. Other slots, eligible handlers, owning/reference/place
operands, wider lifetimes and OB31 remain partial; kernels/readers/roots are unchanged.
[Author](coverage/semantics/output-final-default-scalar-zero-division-warning-error-author.json)
and [review](coverage/semantics/output-final-default-scalar-zero-division-warning-error-review.json).

OB67 admits its own initialized quiet RHS CV through the unchanged reader and
default leading-left Warning capture. Exact current name/line/carrier and one-owner
cells retain raw scratch, exact152 and three-cell retirement before C0. Two
private505 source originals reuse natives once; authorSL4 and peerSL8 retain
separate source0 cuts, with baseline2/precode2 also0. Actual `fe4ed4316`/508 loading
passes in14.987835177 s/source0. Reference/nonzero/noisy or wider operands, places,
handlers and lifetimes remain partial; OB31 is unfinished.
[Author](coverage/semantics/output-final-default-cv-zero-division-warning-error-author.json)
and [review](coverage/semantics/output-final-default-cv-zero-division-warning-error-review.json).

OB68 retains ordered right-only or both-operand numeric Warnings before the
actual division-zero Error for its own CONST/private-CV divisor. Original reads,
source/slot/scratch authority, private rootless operands and no eligible Warning
handler remain required. Four private505 source agreements reuse natives once;
author fixtureSL4, peer fixtureSL7 and the two affected noisy guard stages retain
separate source0 cuts without an aggregate. Baseline4/precode4 stay0; no new failure
or replay occurs. Actual `00cc247e2`/508 loading passes in14.798786004 s/source0.
Wider operands, handlers, places and lifetimes remain partial; OB31 is unfinished.
[Author](coverage/semantics/output-final-default-division-operand-warning-error-author.json)
and [review](coverage/semantics/output-final-default-division-operand-warning-error-review.json).

OB69 adds own original CONST-left rank1 to own RHS-CV rank8, preserving exact
compiled child0 value/carrier and the old CV8-left/right1|8 clauses. Three
private505 originals compare right-only/both Warnings1/1/2 before the actual
DivisionByZeroError, php_error255 at line8, with native3 once. Left-only is a
separate unchanged35/quiet-RHS pointwise composition with no extra source credit.
SL4/SL7 fixtures, baseline3/precode3 and the nonsemantic preparation assertion
retain separate source0 cuts. Actual `ccc4ed2f4`/508 loading passes in15.223471997 s/
source0. Wider pairings, owners, handlers, lifetimes and OB31 remain partial.
[Author](coverage/semantics/output-final-default-constant-left-division-warning-error-author.json)
and [review](coverage/semantics/output-final-default-constant-left-division-warning-error-review.json).

OB70 adds only Warning-producing original CONST1-by-CONST1 DIV capture when the
function/current CVS and ENV are empty. Original compiled values/carriers, source
children/ranks/lines and exact raw35/152/native-owner bounds remain mandatory;
the earlier CV clauses stay literal. Three private505 originals agree on P,
Warning counts 1/1/2 and DivisionByZeroError255 at line6, using three native originals once. Left-only
with a quiet zero RHS is separate unchanged-law composition/source0. Author SL5
reaches actual empty release/C0/retired receipt; independent SL4/4/1 retains exact
source/carrier/line refusals and the affected old69 live-unused-CV Warning refusal.
Baseline3/precode3 and preparation2 remain separate/source0. Actual `157dda256`/508
loading passes in 15.025217987 s/source0; all private cuts remain separate.
Wider pairings, owners, handlers, lifetimes and OB31 remain partial.
[Author](coverage/semantics/output-final-default-constant-pair-division-warning-error-author.json)
and [review](coverage/semantics/output-final-default-constant-pair-division-warning-error-review.json).

OB71 adds only sole-leading-number MOD capture for an original string CONST
modulo its original integer-zero CONST in an empty-CV method. Exact source,
carrier/rank and unchanged raw54 converted-zero scratch/152/native-owner laws
remain mandatory. Two private505 source comparisons reuse native originals
once; author SL5 and peer SL3/2/2/1 remain separate source0 cuts. Genuine
nonzero-RHS substitution, valid same-byte carrier, changed line, masked
precision-loss and allocated unused-CV controls refuse. The original raw01
notation/recorder failure remains0; corrected precode2 and baseline2 remain0.
Actual `0253e97fe`/508 loading passes in 14.958807680 s/source0. Other RHS
values/slots, handlers, producers, lifetimes and OB31 remain partial.
[Author](coverage/semantics/output-final-default-constant-modulo-warning-error-author.json)
and [review](coverage/semantics/output-final-default-constant-modulo-warning-error-review.json).

OB73 also admits an own initialized quiet-zero RHS CV8 with the original CONST1
left for that sole leading-number MOD Warning. Exact child/compiled-line/private-cell,
quiet-zero and valid-string guards remain. Two originals reuse native observations
once; author SL5 and peer SL3/2 retain separate private505 cuts, including actual
two-cell retirement before C0 and equal-Error source/read refusals. Actual
`e6ec8e73e`/508 loading passes in 15.800782290 s/source0. Wider left/slot producers,
handlers, rendering/lifetimes and OB31 remain partial.
[Author](coverage/semantics/output-final-default-cv-zero-modulo-warning-error-author.json)
and [review](coverage/semantics/output-final-default-cv-zero-modulo-warning-error-review.json).

OB74 adds only the own initialized leading-number left CV8 paired with its original
quiet-zero CONST1 RHS. Sole-LEAD, exact source/read/line and unchanged raw54/152
remain required; old CONST-left pairings stay pointwise. Two originals reuse
native observations once; author SL5 and peer SL2/1 retain separate private505
cuts. Actual two-cell retirement before C0, same-Error RHS refusal and the genuine
CV8/CV8 refusal are retained. Actual `4c7efbbab`/508 loading passes in
15.094850045 s/source0. At that cut, both-CV pairings, extra notices, handlers and wider
producers/lifetimes remain partial; OB31 performance is unfinished.
[Author](coverage/semantics/output-final-default-left-cv-modulo-warning-error-author.json)
and [review](coverage/semantics/output-final-default-left-cv-modulo-warning-error-review.json).

OB75 adds only the own CV8/CV8 pair through one rank-condition alternative;
all readers, source/line, sole-LEAD/quiet-zero, raw54/152 and ownership guards
remain literal. Two originals reuse new native observations once; author SL4,
fresh affected old74 SL1 and new peer SL3/2 retain separate private505 cuts.
The old integer-pair refusal keeps its original cut; only its exact affected
expectation is promoted before the first post-edit execution, without replaying
old RHS/native/source campaigns. Actual `9302e90cb`/508 composed loading passes
in 15.115694686 s/source0. Wider places, extra notices, handlers and lifetimes
remain partial; OB31 performance is unfinished.
[Author](coverage/semantics/output-final-default-cv-pair-modulo-warning-error-author.json)
and [review](coverage/semantics/output-final-default-cv-pair-modulo-warning-error-review.json).

OB76 retains Warning then precision-loss Deprecated before the MOD zero Error
for original fractional-prefix CONST pairs in empty-CV methods. Exact notices,
rank1x1, no eligible2/8192 handler and two visible events authenticate capture.
Two private505 originals reuse native2 once; author SL6, affected old71 SL2
and peer SL3/1 retain separate source0 cuts. Baseline2/raw57/57 remain0.
Actual `39c2183eb`/508 loading passes in15.432399042 s/source0. Other noisy
pairings, handlers and lifetimes remain partial; OB31 stays unfinished.
[Author](coverage/semantics/output-final-default-fractional-modulo-warning-error-author.json)
and [review](coverage/semantics/output-final-default-fractional-modulo-warning-error-review.json).

OB77 adds only the own quiet-zero RHS-CV8 beside a fractional CONST-left1,
preserving exact notices/source/line/private-cell/raw54/152 and no2/8192
handler/two-visible-event bounds. Old precision1x1-empty and all sole-LEAD
combinations remain pointwise. Two private505 originals reuse native2 once;
author SL4 and peer SL3/1 retain separate source0 cuts through actual one-cell
retirement/C0/receipt and read-line/reference-mark/left-CV scope controls.
Actual `f1b8fb03e`/508 loading passes in17.476803223 s/source0. At this cut,
precision left-CV/both-CV pairings, handlers and wider lifetimes remain partial;
OB31 is unfinished. [Author](coverage/semantics/output-final-default-fractional-cv-zero-modulo-warning-error-author.json)
and [review](coverage/semantics/output-final-default-fractional-cv-zero-modulo-warning-error-review.json).

OB78 adds an own fractional-prefix left CV with original quiet-zero CONST RHS.
Two exact private505 originals reuse natives once; author SL4, affected old77 SL1
and peer SL3/1 retain separate source0 cuts. Actual `e759cd453`/508 loading passes
in59.352827975 s/cap60/source0. [Review](coverage/semantics/output-final-default-fractional-left-cv-modulo-warning-error-review.json).
OB79 adds an own left/right CV pair with the same source/read/quiet-zero and
visible Warning/Deprecated bounds. Two private505 originals reuse natives once;
author SL4, fresh old78 SL1, old76 SL1 and peer SL3/1 retain separate source0 cuts.
Original positive timeout and incomplete affected attempt retain zero without
replay or a cause claim. Actual combined `994493f99`/508 loading passes
in16.131328344 s/cap60/source0. Masked diagnostics, eligible handlers, wider
operands/lifetimes and OB31 remain partial.
[Review](coverage/semantics/output-final-default-fractional-cv-pair-modulo-warning-error-review.json).

Match accepts a pool-backed PINT or an admitted private scalar CV subject, with
present, equal own/unit mode facts;
DIV admits quiet number coercions; MOD and negative shifts admit scalar integer
coercions with empty diagnostic results. Original numeric
branches remain pointwise. New strings must pass both rootless and S-aware
identity admission on the original operands.
The shared CV proof requires a quiet read of its own literal child and a defined,
private, nonreference, non-global/nonstatic/unbacked cell; return checks retain
their original scalar filter. Generated-error issuance stays in the
direct by-value native method; other owning/noisy operands or wider places, supplied identities/
COMP88, constructor abort/custom rendering and other held expansions remain outside
these additions. OB31 public performance remains unfinished as above.

| Generated-error coverage | Evidence |
| --- | --- |
| Scalar return checks | [Author](coverage/semantics/output-final-return-type-author.json), [review](coverage/semantics/output-final-return-type-review.json) |
| Empty-CV return checks | [Author](coverage/semantics/output-final-empty-return-author.json), [review](coverage/semantics/output-final-empty-return-review.json) |
| Weak rejection/coercion | [Author](coverage/semantics/output-final-weak-return-author.json), [review](coverage/semantics/output-final-weak-return-review.json) |
| Post-body missing return | [Author](coverage/semantics/output-final-missing-return-author.json), [review](coverage/semantics/output-final-missing-return-review.json) |
| Private scalar CV returns | [Author](coverage/semantics/output-final-cv-return-type-author.json), [review](coverage/semantics/output-final-cv-return-type-review.json) |
| Private scalar CV error operands | [Author](coverage/semantics/output-final-scalar-cv-error-author.json), [review](coverage/semantics/output-final-scalar-cv-error-review.json) |
| Private scalar CV match subjects | [Author](coverage/semantics/output-final-cv-match-error-author.json), [review](coverage/semantics/output-final-cv-match-error-review.json) |
| Quiet zero-error coercions | [Author](coverage/semantics/output-final-quiet-zero-coercion-author.json), [review](coverage/semantics/output-final-quiet-zero-coercion-review.json) |
| Quiet negative-shift coercions | [Author](coverage/semantics/output-final-quiet-shift-coercion-author.json), [review](coverage/semantics/output-final-quiet-shift-coercion-review.json) |
| Numeric division by zero | [Author](coverage/semantics/output-final-division-error-author.json), [review](coverage/semantics/output-final-division-error-review.json) |
| Integer modulo by zero | [Author](coverage/semantics/output-final-modulo-error-author.json), [review](coverage/semantics/output-final-modulo-error-review.json) |
| Quiet exact float modulo by zero | [Author](coverage/semantics/output-final-quiet-float-modulo-author.json), [review](coverage/semantics/output-final-quiet-float-modulo-review.json) |
| Negative integer left/right shifts | [Author](coverage/semantics/output-final-shift-error-author.json), [review](coverage/semantics/output-final-shift-error-review.json) |
| Pool-integer match scan/table | [Scan author](coverage/semantics/output-final-match-error-author.json), [review](coverage/semantics/output-final-match-error-review.json); [table author](coverage/semantics/output-final-match-table-author.json), [review](coverage/semantics/output-final-match-table-review.json) |
| Quiet integer/string arithmetic TypeError | [ADD author](coverage/semantics/output-final-arithmetic-type-error-author.json), [review](coverage/semantics/output-final-arithmetic-type-error-review.json); [SUB/MUL author](coverage/semantics/output-final-arithmetic-operator-author.json), [review](coverage/semantics/output-final-arithmetic-operator-review.json); [DIV author](coverage/semantics/output-final-divide-type-error-author.json), [review](coverage/semantics/output-final-divide-type-error-review.json); [MOD author](coverage/semantics/output-final-modulo-type-error-author.json), [review](coverage/semantics/output-final-modulo-type-error-review.json) |
| Quiet MODULO left coercion before TypeError | [Author](coverage/semantics/output-final-quiet-modulo-type-coercion-author.json), [review](coverage/semantics/output-final-quiet-modulo-type-coercion-review.json) |
| Quiet arithmetic left coercion before TypeError | [Author](coverage/semantics/output-final-quiet-arithmetic-type-coercion-author.json), [review](coverage/semantics/output-final-quiet-arithmetic-type-coercion-review.json) |
| Quiet shift/bitwise TypeError | [Author](coverage/semantics/output-final-integer-type-error-author.json), [review](coverage/semantics/output-final-integer-type-error-review.json) |
| Quiet POWER TypeError | [Author](coverage/semantics/output-final-power-type-error-author.json), [review](coverage/semantics/output-final-power-type-error-review.json) |
| Quiet unary PLUS/MINUS TypeError | [Author](coverage/semantics/output-final-unary-type-error-author.json), [review](coverage/semantics/output-final-unary-type-error-review.json) |
| Quiet bool/null BITNOT TypeError | [Author](coverage/semantics/output-final-bitnot-type-error-author.json), [review](coverage/semantics/output-final-bitnot-type-error-review.json) |

Unresolved/effectful creation, active handler-body reentry, other Warning/deprecation-handler returned-object
starts, other output Notice returned-object cases, allocation failure/memory limits
and wider executor completion remain partial.
[Explicit-null review](coverage/semantics/output-executor-explicit-null-review.json),
[general reception review](coverage/semantics/output-executor-reception-review.json).

CLASS156–163 are integrated at `0d756bb0e` after independent cumulative review and a joined 433-module SL gate. Their scoped evidence and remaining limits are in [SOURCE-CLASSES](docs/semantics/SOURCE-CLASSES.md) and the linked reviews.
CLASS164 is integrated at `4f3d1a90a`: four exact copied trait `parent` source originals and three reached state groups validate existing rules. [Review](coverage/semantics/trait-captured-parent-view-review.json).
CLASS165 is integrated at `fde2099b3`: four exact copied-alias trace originals and two reached groups pass; three tick-wrapper probes remain zero credit. [Review](coverage/semantics/trait-captured-alias-parent-trace-review.json).
CLASS166–168 establish deferred parented/parentless anonymous trait captures,
parent receive checks and one alias; their original cuts remain linked from
[SOURCE-CLASSES](docs/semantics/SOURCE-CLASSES.md).
CLASS169 shares ordinary finite trait plans across parentless, parented and
explicit-interface contexts. Qualified/visibility/final aliases, precedence,
multiple uses and distinct static cells preserve first-`new` publication and
copied FCC scope. Sixteen exact originals, 190 author and 135 independent reached
conditions, 229 affected conditions and private strict433 pass. The repaired
private-final warning retains class-site authority until `new` resumes before
allocation. Original Unsupported/interpreter and fixture failures retain zero
agreement credit. [Review](coverage/semantics/anonymous-trait-adaptations-review.json).
CLASS170 authenticates inferred Stringable interfaces before restoring the raw
anonymous header view. Direct imports and aliases preserve original name prefixes,
interface spelling and copied parameter scope; return/private/static conflicts
fail at the trait method before publication or allocation. Eight exact originals,
277 independent and 121 author reached conditions and strict433 pass. The ordinary
parentless `parent` receive view requires published interface targets and full
history; old empty-interface and snapshot paths stay unchanged. Original source
failures and three fixture corrections retain zero agreement credit.
Wider source and explicit/unpublished/collision scope histories, illegal-modifier
diagnostics and other member/lifetime contexts remain partial.
[Review](coverage/semantics/anonymous-trait-stringable-review.json).
CLASS171 shares composed trait views with closed successful include/eval units,
retaining source-entry bindings, request counters, publication and full replay.
Ordinary cached scopes validate before extra trait parameter views, breaking the
dynamic replay/cache cycle while retaining interface forgery refusals. Nine exact
originals, strict433, 82 author, 263 independent and 79 retained saved-view
conditions pass. Argument type and object trace displays use native C strings;
fresh eval classes preserve copied constants' selected callable targets. Original
display/timeout failures and the own-constant author control retain zero credit.
Wider source/member/scope histories remain partial.
[Review](coverage/semantics/dynamic-anonymous-traits-review.json).
CLASS172 admits nonempty own constant groups through the ordinary class compiler,
including multiple declarators, types, visibility and final checks. Own FCCs keep
separate source/function scopes across eval compilations; trait compatibility and
parent-final failures retain first-new ordering. Eleven exact originals,
strict433, 75 author and 192 independent reached conditions pass. Full stored
names remain authoritative; diagnostic operands use native C strings. The author
sort-prefix elaboration failure retains zero credit. Attributes and wider
member/type/initializer contexts remain partial.
[Review](coverage/semantics/anonymous-own-constants-review.json).

CLASS173–175 share ordinary anonymous property compilation, final/asymmetric
modifiers and parameter promotion with the existing named-class rules. Deferred
defaults finish before allocation; private keys, lexical setter permission,
reference constraints, eval/self identities and native compile/link ordering are
preserved. The pinned engine's final/private promotion acceptance remains distinct
from ordinary property declarations. Original failures and qualified standalone
warning evidence retain their actual cuts in the
[property](coverage/semantics/anonymous-properties-review.json),
[modifier](coverage/semantics/anonymous-property-modifiers-review.json) and
[promotion](coverage/semantics/anonymous-promotion-review.json) reviews.

CLASS176 admits readonly anonymous headers through those same member/runtime
rules. Physical class-token metadata and compiler counters authenticate names
and readonly bits; implicit fields, clone reinitialization, private keys and
recompiled self scopes retain source authority. Fifteen exact originals,
strict435, 144 metadata checks, 157 author and 220 independent reached conditions
pass at scoped cuts. The original dynamic-property display mismatch and author
metadata-sequence elaboration failure remain zero credit. Attributes/hooks
and wider contexts remain partial.
[Review](coverage/semantics/anonymous-readonly-review.json).

CLASS177 shares concrete named-method modifiers with anonymous methods and
constructors. Final flags/callable scopes, nonpublic access before arguments,
failed-construction destructor suppression and related bound-Closure lexical
access retain source authority. Static-constructor rejection follows parameter
and body compilation. Fourteen exact originals, strict435, one affected named
source, 139 author and 151 independent reached conditions pass at scoped cuts.
Two author front corrections retain their failed batches; completed components
keep explicit credit. Anonymous abstract diagnostics and wider method-body factory
contexts remain partial; the next review admits named source owners.
[Review](coverage/semantics/anonymous-method-modifiers-review.json).

CLASS178 admits anonymous factories in ordinary named-class methods with actual
owner/method/GOTOROOT, namespace/import and current/folded class-context authority.
Complete-unit images and child-before-deferred-owner counter order preserve
static/instance/default/byref/inherited/namespace/readonly behavior. Twelve exact
originals, final435 plus five member-fence checks, 155 author reached +31 pure
context queries and 212 independent conditions pass at scoped cuts. Initial
elaboration stops and failed whole state batches retain separate zero-credit
identities, with completed components qualified. At that cut, trait/anonymous
source owners, method-owned Closures, generators/byref returns/attributes and
wider contexts remain partial. [Review](coverage/semantics/anonymous-method-factories-review.json).

CLASS179 admits anonymous child factories in named `__construct` bodies with
authenticated owner and compiler context. Child-before-deferred-owner keys,
repeated construction, inherited access, promotion, failure cleanup and compile
diagnostic priority match PHP 8.5.10. Reached lazy final-link errors retain their
constructor trace through eager cleanup. At that cut, anonymous-owner methods
still required provisional key reservation before body compilation.
[Review](coverage/semantics/anonymous-constructor-factories-review.json).

CLASS180 reserves an anonymous owner's compiler-local descriptor before its
method bodies and replaces it in place after successful compilation. This
preserves source-order owner/child/grandchild keys, including reverse and
repeated calls, named factories with forward parents and anonymous constructors.
The ordinary runtime handles inherited scope, protected constructors, failed
owner cleanup and lazy links. Abrupt unit compilation drains child diagnostics
and skips only authenticated child checkpoints without installed images.
Twenty-two exact PHP 8.5.10 sources, 106 reached plus 20 pure conditions and
35 source-boundary checks cover this slice. At that cut, method-owned deferred
scopes, owner traits/constants/implicit Stringable siblings and dynamic units
remained partial. [Review](coverage/semantics/anonymous-owner-factories-review.json).

CLASS181 admits an ordinary public `__toString` sibling in an anonymous owner
whose other method or constructor creates anonymous children. The provisional
owner remains compiler-local with empty interfaces; existing in-place finish
derives implicit `Stringable` and clears early status. Before/after member
order, parented and nested owners, constructor children and compile-error
priority match PHP 8.5.10. Fifteen exact source rows plus a separately bounded
recursive source, 79 reached plus 17 source-derived conditions and 35 current
source-boundary checks cover this slice. The earlier full-batch recursive
timeout retains zero credit. Child factories inside `__toString`, private/static
magic variants, traits/constants, deferred scopes and dynamic units remain
partial. [Review](coverage/semantics/anonymous-owner-stringable-review.json).

CLASS182 admits anonymous factories through method-owned Closures and arrows,
including nested deferred bodies, with source-derived lexical names and actual
named/anonymous method-owner authority. Ordinary capture, retained receivers,
failed construction and class-link ordering use the existing runtime. Rejected
constructors suppress deferred child checkpoints. Closure `__METHOD__` now keeps
its complete generated name; ordinary methods and copied/fake Generator Closures
have separate affected controls. The [review](coverage/semantics/anonymous-method-closure-factories-review.json)
retains scoped source/state cuts, the initial name mismatches, fixture correction,
short-path guard failure and timeouts. Attributed/generator/by-reference-return
factories, anonymous owner explicit-interface headers/traits/constants and
dynamic units remained partial at that cut.

CLASS183 shares ordinary explicit-interface headers and trait/constant members
with unit0 anonymous factory owners. Provisional raw interfaces and the compiler
early marker preserve parent/first-interface prefixes and source-order child
keys; member completion stays in place. Constant callables, trait-inferred
Stringable and deferred scopes reuse the existing runtime. Selected original
programs and distinct source/runtime state groups cover composition, owner scope,
forgery refusal and compile/link order. The
[mixed-owner review](coverage/semantics/anonymous-owner-declarations-review.json)
records actual cuts and native-only preparation separately. Trait-owned source
factories, attributes and wider dynamic/member/lifetime contexts remained partial
at that cut.

CLASS184 admits unit0 trait-source method/constructor and Closure/arrow anonymous
factories through the real Trait body and PTTRAIT compiler context. Ordinary
copying preserves consumer lexical/called scope while repeated consumers and
aliases reuse compiled child identity. Abrupt compilation replays earlier
diagnostics and skips only source-owned uninstalled trait children. The
[review](coverage/semantics/trait-source-factories-review.json) separates source,
consumer/cleanup state and source-derived refusal evidence, retaining the
original missing-checkpoint Unsupported and fixture correction. Attributes,
generator/by-reference-return factories and wider dynamic/lifetime contexts
remained partial at that cut.

CLASS185 admits anonymous factories in ordinary nonmagic generator methods of
named/anonymous classes and unit0 traits, including admitted nongenerator nested
Closures/arrows and static anonymous methods. Source templates keep compiler key
order while actual saved frames restore method source, receiver and lexical/called
classes across yields and injected throws. Existing ownership handles completion
and escaped Closure lifetime. Shared Generator traces distinguish native API
resumptions from user/`foreach` callers, including lazy child-link errors before
arguments. The [review](coverage/semantics/generator-method-factories-review.json)
separates original source agreements, actual paused/resumed frame and retirement
checks, derived forged-frame refusals and retained explicit source boundaries.
Generator constructors, generator Closure/arrow bodies, attributes, by-reference
factories and wider dynamic/lifetime contexts remained partial at that cut.

CLASS186 admits unit0 method-owned generator Closure/arrow anonymous factories
through the existing source ancestry and lexical-name checks. Actual saved
Closures retain captures, receiver and lexical/called scope across deferred
initialization and resume; closed Generators keep those Closures after execution
frames retire. Static Closures keep source identity after creator retirement.
The [review](coverage/semantics/anonymous-generator-closure-factories-review.json)
separates selected originals, actual paused/resumed/closed ownership and budget
checks, derived refusals and native-only preparation. Generator constructors,
by-reference-return factories, attributes and wider binding/dynamic contexts
remained partial at that cut.

CLASS187 admits anonymous factories in ordinary nongenerator methods declared
with `&` across admitted named/anonymous/Trait owners. Direct compiler return mode
matches the parsed header; nested byvalue Closure ancestry restores that method
mode only in a source-authentication query. Existing returned cells and notice
handling preserve aliases, receiver/child retirement and used/unused temporary
return cancellation. The [review](coverage/semantics/anonymous-reference-method-factories-review.json)
separates source agreements, actual cell/budget checks and derived mode refusals.
Reference constructors/generators/Closure declarations, attributes and wider
binding/dynamic contexts remained partial at that cut.

CLASS188 admits unit0 method-owned nongenerator reference-return Closure/arrow
factories in named/anonymous/Trait owners. The deferred header authenticates its
own return mode independently of the checked parent method. Existing cells and
notice materialization preserve aliases and callback cleanup. Narrow shared
return-source checks authenticate the actual Arrow template/body line and exclude
Arrow expression returns from ordinary implicit-null fallthrough. The
[review](coverage/semantics/anonymous-reference-closure-factories-review.json)
separates exact originals, real cell/notice ownership and budget checks from
derived mode/refusal queries and preserved implementation failures. Reference
generators, reference/generator constructors, attributes and wider binding/dynamic
contexts remain partial.

CLASS189 admits anonymous factories in byvalue nongenerator `__invoke`, `__get`
and `__toString` bodies under existing method/deferred source ancestry. Getters
keep untyped required nonref/nonvariadic/default-free parameters and no declared
return type. Existing real consumers preserve receiver ownership after caller
variables clear. Authenticated named/Trait child checkpoints stay unpublished on
abrupt owner compilation, preserving child warnings before magic signature errors.
A bounded post-body compiler arm supplies the missing plain getter arity fatal.
The [review](coverage/semantics/anonymous-magic-factories-review.json) separates
original observations, source-derived mode bounds and real getter ownership/budget
checks. Reference/generator magic forms, wider getter headers, other magic bodies,
attributes and wider dynamic/binding contexts remain partial.

CLASS190 admits anonymous factories in byvalue nongenerator `__set`, `__isset`
and `__unset` methods using their existing plain-header and actual consumer
contracts. Parentless named/anonymous declaring owners and inherited receivers
keep their source scopes and saved-marker receiver roots. Setter inputs remain
integer CV/literal RHSs: the body receives the captured value while delivery reads
the original cell after receiver destruction. The
[review](coverage/semantics/anonymous-property-magic-factories-review.json)
separates original execution, actual NEW/delivery ownership and budget checks,
with retained Trait/mode/RHS boundaries. Other magic argument protocols, wider
signatures/receivers, attributes and generic dispatch remain partial.

CLASS191–201 admit anonymous factories in ordinary byvalue nongenerator `__call`
and `__callStatic` bodies under their existing plain headers and argument
consumers. Captured scalar/ordinary leaf-object sends stay fixed through later
CV/receiver mutation; real packed arrays and actual lexical/called scope preserve child/payload ownership
after return and receiver cleanup. The
[review](coverage/semantics/anonymous-magic-argument-factories-review.json)
separates exact admitted originals, one real frame/array ownership front and
retained producer/mode boundaries. Zero sends now use explicit empty capture and
the real name and immutable empty array parameters, with actual ownership and budget
checks in the [zero-send review](coverage/semantics/anonymous-zero-argument-magic-review.json).
The [object-CV review](coverage/semantics/anonymous-object-cv-magic-review.json)
promotes byte-exact original191 sources and tracks real captured-object owners;
instance sends retain positional, mixed or explicitly named first object CVs.
Named-only argument tables share the real retained buffer, which can remain the
last payload owner through return before receiver cleanup; the
[named-CV review](coverage/semantics/anonymous-named-object-cv-magic-review.json)
tracks this source/ownership slice. Old Unsupported cuts keep zero credit.
Initial reference-cell first CVs may now hold the same ordinary leaf objects.
BY VALUE SEND owns the copied object value before later alias writes; actual packed
tables and returned children retain OLD after the caller cell changes to NEW or
retires. The [reference-CV review](coverage/semantics/anonymous-refcell-magic-review.json)
records positional instance/static and independent named-Closure originals,
source authentication, real owners and budget/cleanup checks.
First flat-array CVs, including initial reference cells, retain integer/ordinary
leaf-object snapshots through generic COW and caller rebinding; the
[array-CV review](coverage/semantics/anonymous-array-cv-magic-review.json)
tracks source/index authentication and real table/payload owners. The
[reference-array review](coverage/semantics/anonymous-refarray-magic-review.json)
records the real CELL/table owners before and after SEND/COW, shared leaf identity,
real argument tables, returned children and alias/Closure cleanup.
First flat-array literals now use the same contextual collected-value bound, with real transient
array/payload/selected-receiver roots during later sends and returned-child
lifetime in the [literal review](coverage/semantics/anonymous-array-literal-magic-review.json).
A first source-certified nullary ordinary byvalue producer may return the same
flat array; the [producer review](coverage/semantics/anonymous-array-producer-magic-review.json)
retains its exact source and pending-owner cuts. Primitive COPY extends the first
CV/reference-CV and either-position ordinary nullary byvalue user producer to
NULL, bool, int, binary64 and authenticated string carriers, preserving exact
carrier identity and generic SEND ownership. Flat-array leaves keep their prior
integer/ordinary-leaf bound. Unknown byte-only strings remain Unsupported;
request-owned NUL stays held.
The [primitive review](coverage/semantics/anonymous-primitive-magic-review.json)
records 23 distinct source agreements and separate owner/budget packets of 105
and 107 conditions at their recorded cuts. Direct literal sends now authenticate
their exact quiet compiled value and interned string carrier, with raw-source
priority over existing COPY roles. Fixed NULL/bool, scalar and single-sign
numeric literals share the existing protocols; general constant fetches and
other folded expressions stay separate. Explicit unpack prefixes retain their earlier
policy. The [literal review](coverage/semantics/anonymous-literal-magic-review.json)
records five distinct source agreements, separate 112/124 owner/budget fronts,
and a separate 28-condition real-source unpack guard at their recorded cuts.
Indexed second CV sends now check the actual initialized ordinary cell after
earlier argument effects, then retain the copied primitive/leaf value through
handler writes and source-cell detachment. Missing/array/typed/backed reads stop
before warnings or coercions. The [later-CV review](coverage/semantics/anonymous-later-cv-magic-review.json)
records six distinct source agreements, separate 143/153 owner/budget fronts and
a 30-condition pre-warning source guard at their recorded cuts. Unpack prefixes
retain their earlier policy.
Fixed-name USER producers with exact required untyped by-value arguments now
share ordinary inner SEND/parameter/return ownership for quiet primitive/leaf
results. Source/target/formal certificates have priority over old value-only
admission. Nullary routes and contextual first-array returns stay unchanged;
438 preserves earlier unpack prefixes. The
[required-producer review](coverage/semantics/anonymous-user-argument-magic-review.json)
records five distinct source agreements, separate 140/188 owner/budget fronts
and a 27-condition unpack source guard at their recorded cuts.
Literal USER function-name strings now authenticate direct/FCC producers through
complete source, normalized CODENAME and actual INITs without a child READ.
Real arguments retain zero/required untyped by-value formals without a return
type and COPY0/1 bounds. Ordinary origin targets and receiver-free
NAMEDCLOSURE/INSTANCE preserve snapshots through caller and wrapper retirement.
Seven distinct normal source agreements and separate author SL103/112/28 and
independent SL112/115 conditions pass at private492 cuts. Two builtin Unsupported
controls and the original budget-observer, CLI-recorder and pre-main checker
failures retain zero credit; native/source replay is zero. The actual accepted
`8ea27308d`/493 load passes with source0, separately from those private cuts.
Builtin, wider modes and the old438 fence remain unchanged.
[Review](coverage/semantics/anonymous-function-string-callable-producer-magic-review.json).
Initialized plain/reference CV function names now select ordinary USER direct/FCC
producers for positional/named instance `__call` arguments before inner arguments. An absent-class function-origin receipt owns
no cell/string/receiver and survives callee retargeting/removal and producer,
wrapper and caller retirement. Exact CV emission, INITs, source and real arguments
retain existing quiet COPY0/1, signature, header and438 bounds. Six distinct
normal originals agree at private494 SL cuts, including runtime-built name
retirement. Author SL106/112/17, affected existing method-receipt SL47 and
independent SL145/151 all pass separately; two builtin Unsupported controls and
the old refusal baseline earn zero agreement. Wider/held modes remain partial;
no engine divergence or native/source replay is claimed. Current-main
composition is separate. [Review](coverage/semantics/anonymous-function-cv-callable-producer-magic-review.json).
Fixed named new expressions now admit source-certified effective plain public
constructors with zero/required untyped positional by-value parameters. Generic
constructor/result owners preserve the allocated ordinary leaf instance across
argument effects and ignored scalar returns. Collection binds its exact class;
the old empty no-constructor and unpack-prefix bounds stay unchanged. The
[constructor-producer review](coverage/semantics/anonymous-constructor-magic-review.json)
records five distinct source agreements, separate 160/201 owner/budget fronts and
a 30-condition zero-constructor unpack guard at their recorded cuts.
Keyword `new self/parent/static` arguments now select their allocation class
from the saved caller and real compiled site. Inherited constructors use that
allocated called class; existing This/result/SEND owners ignore constructor
returns and can preserve the ordinary leaf through caller retirement. Real-state
collection keeps the class bound. Wider headers, inner named/unpack and nonleaf
results remain partial; the [keyword-NEW review](coverage/semantics/anonymous-keyword-new-producer-magic-review.json)
retains separate source/state cuts and the original zero-credit timeout.
Fixed class/literal public static USER producers now share the quiet COPY
family with zero/required untyped positional by-value parameters. Actual inherited
scoped targets preserve declaring/called classes before arguments and add no
receiver root. Generic inner snapshots, fresh parameters and returned table/child
owners survive caller mutation and frame retirement. Constructor, nullary,
contextual-array and438 policies stay unchanged. The
[static-producer review](coverage/semantics/anonymous-static-producer-magic-review.json)
records five distinct source agreements, separate 134/204 owner/budget fronts and
a 29-condition real-source unpack guard at their recorded cuts; five intended
Unsupported controls retain zero agreement credit.
Direct literal static no-capture USER Closures now share quiet COPY through
zero/required untyped positional by-value arguments. Original child/template and
compiled INIT authority remain usable after the real target/INSTANCE owner and
parameter frame retire. Inner snapshots preserve old values through caller writes;
real outer tables and children retain the returned payload. Existing constructor,
nullary, contextual-array, header and438 bounds stay unchanged. The
[literal-Closure review](coverage/semantics/anonymous-literal-closure-magic-review.json)
records five distinct source agreements, separate 145/221 owner/budget fronts
and a 29-condition real-source unpack guard at their recorded cuts; six intended
Unsupported controls retain zero agreement credit.
Fresh fixed-name receivers support literal public ordinary method producers and
direct/FCC two-item callable arrays. Actual NEW source/CODE_NAME/class and
no/approved-constructor authority remain separate from call INITs: fixed NEW adds
no INIT, direct arrays use outer INIT and FCC arrays use outer/capture INITs.
Real arguments retain zero/required untyped positional by-value bounds. Original
physical source scope preserves private-first selection; private shadows are refused.
Generic copy positions0/1 remain exact. Direct nonstatic ARRAY_METHOD_TARGET owns
This; nonstatic ARRAYMETHODCLOSURE owns its receiver edge, frame INSTANCE owns
the wrapper and frame RECEIVER borrows This.
Static selection has no selector edge; request snapshots survive real argument
writes and caller/wrapper retirement. Real object RESULT transfers to bare SENT;
generic table/child laws keep separate evidence. The latest array cut has eight
source agreements and558 strict state conditions, with two private source refusals
retaining zero agreement credit. Existing quiet COPY/header/438 bounds remain;
wider array modes stay partial. The
[instance-producer review](coverage/semantics/anonymous-instance-producer-magic-review.json) and
[fixed-name callable-array review](coverage/semantics/anonymous-fresh-array-callable-producer-magic-review.json)
retain separate cuts and earlier zero-credit originals.
Fresh `new self/parent/static` method and invokable producers use saved caller
metadata and actual compiled NEW authority. Direct/FCC literal public methods
and callable arrays, plus normal fromCallable method arrays, retain original
private-first selection; private shadows remain refused. Direct, FCC and normal
fromCallable implicit invokers use allocated effective public nonstatic `__invoke`.
FCC real arguments stay separate from the placeholder. FCC arrays authenticate
actual outer/capture INITs and receiver NEW at its original three-FIELD0 path;
normal factories retain authored CODEEXPR/source line and outer INIT plus NEW.
Direct arrays authenticate outer INIT and the actual receiver/literal item paths.
Direct nonstatic targets own This. Array selection preserves the allocated called
class after temporary-header retirement. Nonstatic METHODCLOSURE,
ARRAYMETHODCLOSURE and FROMCALLABLECLOSURE wrappers own receiver edges; frame
INSTANCE owns the wrapper and borrows This. Static targets have no selector edge
and may release fresh selectors before real arguments. FCC array conversion
allocates after header retirement; normal-factory cleanup can park a wrapper
result in an eager-operation record before restoration. Object RESULT transfers
to bare SENT, while request snapshots survive selector/wrapper/caller retirement.
Constructor, formal, quiet COPY, header and unpack bounds remain exact; generic
table/child laws keep separate evidence. The FCC-array ledger records five source
agreements and504 strict state conditions; its private-shadow source refusal
retains zero agreement credit. Earlier normal-factory166 FALSE and corrected175
fixture cuts remain separate. Inner named/unpack
and wider modes remain required. Authentic cuts and zero-credit originals remain in the
[method](coverage/semantics/anonymous-keyword-new-method-producer-magic-review.json),
[method FCC](coverage/semantics/anonymous-keyword-new-firstclass-method-producer-magic-review.json),
[invoker](coverage/semantics/anonymous-keyword-new-invokable-producer-magic-review.json),
[invoker FCC](coverage/semantics/anonymous-keyword-new-firstclass-invokable-producer-magic-review.json),
[normal invoker factory](coverage/semantics/anonymous-keyword-new-invokable-from-callable-producer-magic-review.json),
[method-array factory](coverage/semantics/anonymous-keyword-new-array-from-callable-producer-magic-review.json),
[direct callable array](coverage/semantics/anonymous-keyword-new-array-callable-producer-magic-review.json) and
[FCC callable array](coverage/semantics/anonymous-keyword-new-array-firstclass-producer-magic-review.json)
ledgers; no family or full-core closure is claimed.

Initialized plain/reference CV receivers now support the same literal public
ordinary instance producers. Actual-time receiver/read and private-first selection
mint a nonowning source/class/method fact on the active outer descriptor; collection
uses that fact after CV rebinding/unsetting or receiver retirement. Future facts
and malformed pending carriers refuse without a default-route bypass. Generic
receiver/SEND/parameter/result/table owners stay unchanged; missing/constrained/
nonleaf cells stop before warning effects. The
[CV-instance review](coverage/semantics/anonymous-cv-instance-magic-review.json)
records six source agreements, separate 147/267 full owner/budget proofs and
24/43/26/45 missing/typed/future/repeated-source guards at their recorded453 cuts.
Seven intended source refusals and all preserved setup, admission and fixture
failures retain zero agreement; the typed-formal guard has an explicit root-context
bridge for completed positives. The actual joined 455-module interface load and
inventory169/306 pass at a2cc73a0c; no source/frontier replay. Broader receiver/call
modes remain partial.
Immediate fixed-source function/public-static USER first-class callables now
produce the existing quiet COPY values. Capture and invocation origins/INITs are
separate; placeholder conversion selects a real wrapper before outer sends.
Generic cleanup releases the wrapper call/INSTANCE owner after return; the tested
unaliased wrappers retire before table/child retention of the result. Collection
uses permanent function/class source.
Raw FCC priority and438 isolation keep old nullary/constructor/array/header bounds.
The [first-class producer review](coverage/semantics/anonymous-firstclass-producer-magic-review.json)
records five distinct first-pass source agreements, separate 194/267 full
owner/budget proofs and a 28-condition eligible-pack guard at recorded455 cuts.
Five intended Unsupported controls retain zero agreement. No209 failures,
corrections, timeouts or native repeats occurred; current456 composition is
independently reviewed without source/frontier replay.
Fresh fixed-name instance FCC producers now reuse the no-ctor/approved constructor
and public ordinary method source certificates. Actual capture and outer arity
remain separate. The wrapper owns its receiver edge; frame INSTANCE retains the
wrapper while `$this` borrows. Return-old releases that edge before the handler in
the tested unaliased case; return-this preserves the receiver in the real result.
The [instance-FCC review](coverage/semantics/anonymous-instance-firstclass-producer-magic-review.json)
records five first-pass original agreements and trimmed107/223 receiver frontiers.
The author compares a bounded retirement fence; the peer proves full split cleanup.
A25-condition eligible-pack guard and five intended Unsupported controls preserve
refusal boundaries with zero agreement. Generic CLASS209 call/table/child laws
are reused; all held/wider modes remain partial.
Literal instance FCC producers now accept initialized plain/reference CV receivers.
Actual capture and outer argument sites remain separate; the guarded read mints
an outer descriptor receipt before conversion. Collection uses it after source-CV
or wrapper/receiver retirement, with existing ownership and value bounds.
The [CV instance-FCC review](coverage/semantics/anonymous-cv-instance-firstclass-producer-magic-review.json)
records four first-pass original agreements, a100-condition return-old frontier,
a corrected168-condition returnThis proof and a25-condition eligible-pack guard.
The new read/cache/conversion budget is1+1+1=3; existing208/210 table/child/full-tail
laws are reused. Five intended Unsupported controls, the original peer cache-phase
fixture failure and its bounded diagnostic retain zero agreement.
Fresh fixed-name USER invokable producers now reuse approved NEW and public
`__invoke` source/formals. Effective runtime selection precedes arguments;
ordinary receiver call owners distinguish return-old release from return-this
result/table/child retention, with no Closure wrapper or CV history.
The [invokable producer review](coverage/semantics/anonymous-invokable-producer-magic-review.json)
records four first-pass original agreements,51/129 complementary owner frontiers,
a25-condition eligible-pack guard and23-condition anonymous-New raw-priority guard.
The one-word class-domain correction preserves the fixed-name source cuts;
five intended Unsupported controls have zero agreement. Generic tail laws are
reused without source/native replay; all wider/held modes remain partial.
Ordinary USER invokable CVs now guard the actual lookup before read/warning
and mint an effective-public-method receipt on the active descriptor. Receiver
call owners and source facts survive CV removal; even zero arguments cannot use
old integer/leaf fallback without a receipt. Stored Closure/string/array values
and wider modes remain held. The
[CV invokable review](coverage/semantics/anonymous-cv-invokable-producer-magic-review.json)
records four first-pass originals,63/128 complementary owner frontiers,39 genuine
zero-argument receipt checks and25 eligible-pack guards at private458 cuts.
Seven intended Unsupported controls retain zero agreement; no failed attempt or
source/native replay occurred. Generic tail laws remain reused.

Literal self/parent/static producers now derive requested and called classes from
the authenticated saved magic caller, then retain effective public static source
through frame retirement. Real-state collection preserves quiet values and mixed
CV receipts without a receiver owner or new history. The
[keyword static review](coverage/semantics/anonymous-keyword-static-producer-magic-review.json)
records four original agreements, complementary70/118 state frontiers and25
eligible-pack guards at private459 cuts. Five intended Unsupported controls,
the corrected source-admission attempt and all fixture failures/diagnoses keep
zero agreement. Only affected checks repeated; no native replay or broader gate.
Keyword-static first-class producers now authenticate separate capture and real
invocation origins/INITs while preserving forwarded called class. Generic wrapper
INSTANCE and parameter/result owners need no receiver edge or new source fact.
Four originals agree on their first model runs; complementary72/109 frontiers
and25 eligible-pack guards pass at private461 cuts. Three intended Unsupported
controls retain zero agreement, with no failure/correction/replay. Generic tail
laws remain reused. [Review](coverage/semantics/anonymous-keyword-static-firstclass-producer-magic-review.json).
This direct/FCC method and literal callable-array producers select public
ordinary instance/static methods from saved caller receiver, function and scopes.
Arrays authenticate actual This-fetch/literal paths and one direct or two FCC INITs;
only real invocation arguments determine formals. Original private-first lookup
stays exact. Nonstatic targets/wrappers add a receiver edge, while static selection
still leaves the independent caller This owner alive through arguments. Returned
This can survive caller retirement. Explicit unpack prefixes and wider modes
remain partial. The [method](coverage/semantics/anonymous-this-producer-magic-review.json)
and [callable-array](coverage/semantics/anonymous-this-array-callable-producer-magic-review.json)
reviews retain their distinct source/state cuts and zero-credit controls.
The callable-array cut has seven normal source agreements and 575 strict state
conditions at private cuts with 486 modules. Two private-source Unsupported controls, the real
unpack boundary and the original FCC checker failure retain zero agreement credit.
The latest preceding actual joined load `ea9ca05c2` with 488 modules passes with
zero source credit; it predates CLASS243 and does not renew the private evidence.
Fixed class-string/public-static direct and FCC callable arrays now reuse whole
compiled-pool authority and effective class-table selection. Real invocation
arguments and one direct/two FCC INITs remain distinct from capture placeholders;
static targets/wrappers add no receiver edge. Seven distinct first source
agreements pass at private488 cuts. Author SL113/130/25 and independent
SL112/62/39/128 checks preserve pool/returned-value ownership, caller retirement,
private refusals and the actual unpack boundary. The original parser, recorder
and helper failures plus the AL timeout retain zero credit. Actual joined
`f2f581dbb`/490 loads cleanly with zero source credit; it does not renew the
private cuts. Generic tails and the factored normal-factory proof are reused
without source/native replay. Wider modes remain partial.
[Review](coverage/semantics/anonymous-static-array-callable-producer-magic-review.json).
Literal USER `Class::method` direct/FCC producers now authenticate complete call
source, normalized CODENAME and actual INITs without requiring a child READ.
Effective public static selection and real arguments retain existing COPY0/1
bounds. STRING_METHOD_TARGET and the real STRINGMETHODCLOSURE preserve spelling,
scopes and returned leaves without a receiver edge. Seven distinct source
agreements and separate author SL102/120/25 and independent SL108/57/34/119
conditions pass on first execution at private490 cuts. Two private-source
Unsupported controls and actual unpack have zero agreement credit; no executed
failure, retry or native/source replay occurred. The direct-origin review fix
preceded modeled execution. Actual `9a5efad9f`/492 loads cleanly with source0,
separate from those cuts. Wider modes remain partial.
[Review](coverage/semantics/anonymous-static-string-callable-producer-magic-review.json).
Initialized plain/reference CV nonkeyword `Class::method` strings now select
ordinary public static USER producers for positional/named instance `__call`
arguments. Actual string selection saves requested class and method origin before
arguments, independently of caller-private lookup. Existing STRING wrappers,
INSTANCE and payload owners preserve scope and snapshots through CV overwrite/
unset and producer/wrapper/caller retirement; the receipt owns no nodes.
Five distinct normal originals agree at private495 SL cuts. New author
SL118/128/17, affected prior function-CV SL106 and peer SL139/152 pass separately;
two accessible-private Unsupported controls and the old refusal earn zero source
credit. No source/native replay, failure or timeout is claimed. Signature,
COPY0/1, header/438, wider access/callee/`__callStatic` and held bounds stay partial.
Current-main composition is separate.
[Review](coverage/semantics/anonymous-method-string-cv-callable-producer-magic-review.json).
Runtime two-item nonkeyword class-string method arrays in initialized plain/
reference CVs now supply ordinary public-static USER direct/FCC producers for
the same instance `__call` COPY0/1 boundary. Selection preserves requested versus
declaring class before argument effects without retaining the input array;
overwrite/unset, wrapper/caller retirement and the real result owners are checked.
Five current originals agree at private496 SL cuts; author SL125/134/17/38 and
peer SL164/171 conditions pass separately. Three source/fixture failures and the
interrupted packet retain zero credit; its completed direct observation is
supplemental only. No native replay or timeout occurred. Shared205 defaults,
private/unpack refusals and unchanged438 bounds are checked; wider forms remain
partial. Actual joined `36a093245`/498 loads cleanly (15.430357 s, source0);
the private496 source and state cuts retain their original identities.
[Review](coverage/semantics/anonymous-static-array-cv-callable-producer-magic-review.json).
Scoped self/parent/static instance producers now authenticate requested/effective
method selection against compatible saved callerThis, keeping declaring/called
classes separate. Four originals, separate 66/104 target/context fronts, a
25-check unpack guard and three refusal controls pass first execution at
private461 cuts. Existing static/This source and generic owner laws are reused;
actual462 composition follows empty-excess/default fallbacks. [Review](coverage/semantics/anonymous-keyword-instance-producer-magic-review.json).
Implicit This calls now select inherited public USER __invoke from saved caller
source and real INIT metadata, using ordinary receiver ownership without CV
receipts or Closure wrappers. Three originals, 71/94 focused target/context
fronts,25 pack guards and three refusal controls pass first execution at
private462 cuts;213/216 generic tails remain reused.
[Review](coverage/semantics/anonymous-this-invokable-producer-magic-review.json).
Fresh invokable-object FCC producers now authenticate both INITs, approved NEW
source and effective public __invoke against real outer arguments. Three
originals, separate67/corrected112 owner/escape fronts,25 pack guards and three
refusal controls pass at private462 cuts. Original114/diagnostic retain zero
credit;212/210 generic laws are reused, with actual463 default/absence review.
[Review](coverage/semantics/anonymous-invokable-firstclass-producer-magic-review.json).
Immediate CV invokable FCC producers now guard the actual conversion read and
preserve the selected outer-source receipt through receiver replacement or
removal. Three originals, separate68/112 ownership fronts,47 zero-receipt checks,
31 pre-warning guards,25 pack guards and six refusal controls pass first execution
at private463 cuts. Existing receipt and wrapper laws remain reused.
[Review](coverage/semantics/anonymous-cv-invokable-firstclass-producer-magic-review.json).
Implicit This invokable FCC producers now authenticate original capture and
real arguments from immutable saved caller context. Three originals, separate
67/104 caller/wrapper/escape fronts,25 pack guards and three refusal controls pass
first execution at private463 cuts. Existing receiver/result laws remain reused;
source certification survives the tested This retirement.
[Review](coverage/semantics/anonymous-this-invokable-firstclass-producer-magic-review.json).
Normal fromCallable producers now authenticate compiled fixed strings, factory
CODEEXPR and outer INIT against real invocation arguments. Three distinct source
agreements,65/corrected116 ownership fronts,25 pack guards and four refusal
controls pass at private464 cuts. The initial qualified-name omission and two
peer checker attempts retain zero credit; existing factory/wrapper laws are reused.
[Review](coverage/semantics/anonymous-from-callable-producer-magic-review.json).
Fresh invokable fromCallable producers now reuse original factory parts,
approved NEW and effective public invoke source against real arguments. Three
originals,71/106 argument-owner/wrapper/escape fronts,25 pack guards and three
refusal controls pass first execution at private466 cuts. Existing receiver,
INSTANCE and result laws are reused; fixed-string222 behavior stays pointwise.
[Review](coverage/semantics/anonymous-invokable-from-callable-producer-magic-review.json).
Fresh two-item method-array fromCallable producers authenticate actual item
origins, constructor class and private-first public target in the original
factory scope. Three originals,80/123 array-retirement/receiver-transfer fronts,25
pack guards and four refusal controls pass first execution at private466 cuts.
Existing wrapper/INSTANCE/result ownership is reused; fixed-string and direct
invoker factory behavior stays pointwise.
[Review](coverage/semantics/anonymous-array-from-callable-producer-magic-review.json).
Fixed class-string/static-method callback arrays use compiled parent-pool
authority and effective selection, including the lexical-private contrast. Three
source agreements,92/124 pool/SEND/wrapper fronts,25 pack guards and two refusal
controls pass at private466 cuts. The original runtime guard failure, checker-only
correction and bounded diagnostic retain zero credit; no native/state replay.
[Review](coverage/semantics/anonymous-static-array-from-callable-producer-magic-review.json).
This method-array fromCallable producers now use original CALLER authority and
actual This emission, keeping dynamic array/wrapper edges distinct from the
caller owner. Three source agreements,92/122 transfer/retirement fronts,25 pack
guards and two refusal controls pass first execution at private467 cuts; the
pack fixture correction preceded execution. Existing owners and438 stay fixed.
[Review](coverage/semantics/anonymous-this-array-from-callable-producer-magic-review.json).
Fresh-object method arrays now admit the unchanged plain-static source tail.
Two original agreements,80/121 selector-retirement/history fronts,25 pack guards
and one refusal control pass first execution at private468 cuts. The tested
unaliased selectors die before real argument reads; wrapper metadata adds no
receiver root. Constructor and generic owner rules stay unchanged.
[Review](coverage/semantics/anonymous-fresh-static-array-from-callable-producer-magic-review.json).



Static This-array factories now use an array-specific saved-caller/public-static
certificate. Real array release leaves the caller owner intact; receiver-free
wrapper INSTANCE, inherited scopes, saved arguments and source authority remain
valid through caller retirement. Two exact sources and separate109/125 owner/source/
budget checks pass at private469 cuts; initial setup/peer-fixture failures retain
zero credit. Direct/FCC This,234/438 and actual held bounds stay fixed. [Review](coverage/semantics/anonymous-this-static-array-from-callable-producer-magic-review.json).
Direct literal This-static producers now reuse the same public source proof.
Actual selected STATIC_METHOD_TARGET and its body have no receiver/INSTANCE
owner; the saved caller retains This through argument mutation and SEND until
retirement. Declaring, caller and called scopes stay distinct. Two exact sources
and separate80/85 owner/source/budget checks pass first attempt at private469;
FCC remains separate. [Review](coverage/semantics/anonymous-this-static-producer-magic-review.json).
Immediate This-static FCC producers now authenticate the placeholder capture
and real invocation through the same saved-caller public proof. Receiver-free
METHODCLOSURE/INSTANCE ownership stays separate from callerThis; wrapper and
caller retirement preserve snapshots and scope. Two exact sources and separate
96/111 convert/owner/budget checks pass first attempt at private469.
[Review](coverage/semantics/anonymous-this-static-firstclass-producer-magic-review.json).
Fresh fixed-name static direct/FCC producers now use the existing public-static
source check after unchanged constructor/private-first selection. Static targets
and wrappers retain no selector; actual owners determine retirement. Two exact
sources and separate75/109 selected/convert/owner/budget fronts pass first attempt
at private469, including selector-destructor changes before real arguments.
[Review](coverage/semantics/anonymous-fresh-static-producer-magic-review.json).
Public ordinary CV-object static direct/FCC producers now stamp the existing
SITE/CLASS/METHOD receipt from actual normalized selection. The142 hook preserves
the rewritten descriptor/cache state; old guards and ordinary identity defaults
stay exact. Static targets/wrappers add no selector owner, and real arguments can
replace/remove its CV without changing selected scope or snapshots.
Two exact sources and separate92/115 receipt/owner/budget fronts pass first
attempt at private469; missing receipts and malformed active carriers stay refused.
[Review](coverage/semantics/anonymous-cv-static-producer-magic-review.json).
Later array sends,
unpacking, nested arrays/reference entries, static named sends, Trait,
reference/generator, attributes and wider scope remain partial.

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

COMP165 admits the disabled-multibyte parser warning followed by a static
first-statement fatal for late or nested sole-string encoding declarations.
Five pinned-native source cases cover root, namespace and block fatals plus
included and eval first-declaration controls. Forty-four checked-AST premises
authenticate declaration and item paths, warning location, and malformed
occurrence refusal. Other declaration shapes and multibyte source conversion
remain partial. [Review](coverage/semantics/encoding-placement-review.json).

COMP166 admits arbitrary mixed/repeated encoding items with parser-literal values
and ordinary bodies in checked single-line declarations. Source token positions
order the complete recursive parser-warning prefix before compiler diagnostics;
literal concatenation passes the matching parser-form check. Ten original
sources agree, including strict/tick interactions and include/eval body returns.
Authored 256, independent dynamic 93 and affected legacy 179 strict-SL premises
pass, alongside six CLI guards and two explicit multiline Unsupported controls.
Actual cuts and preserved failures are in the
[review](coverage/semantics/encoding-list-review.json). COMP167/168 below extend its multiline and rejected-source boundaries;
multibyte conversion remains partial.

COMP167 retains checked declaration header-close line/token facts. Multiline
headers use their closing line for parser warnings while compiler diagnostics
keep the first item's line. Nested header reductions precede enclosing headers;
comment-only Nops retain their genuine empty token spans. Twenty-one new original
comparisons, independent compiler/state gates and affected regressions pass;
strict compilation covers 433 modules. Fresh classified syntax covers 30,980
profiles and independent metadata checks cover 17 profiles. Original failures
and exact cuts remain in the [review](coverage/semantics/encoding-header-review.json).
COMP168 below extends rejected dynamic sources; multibyte conversion remains partial.

COMP168 preserves encoding warnings from completed foreign header reductions
when eval/include parsing later fails, without compiling a partial AST. Literal
items warn in reduction order until the first nonliteral encoding item raises
CompileError. Rejected-source Throwable handles are installed before publishing
zero-budget continuations. Twenty-two exact sources plus one explicit lexical
refusal, 214 authored and 375 independent reached conditions pass; accepted
eval/file service controls also pass. Actual cuts, prior failures and the remaining
lexer/multibyte limits are in the [review](coverage/semantics/encoding-rejection-review.json).

COMP169 preserves completed headers before the first foreign lexer error by
validating its token boundary and parsing the preceding token prefix. Earlier
grammar errors still stop parsing; harmless control bytes inside strings/comments
do not truncate it. All 32 new eval/file originals agree, with 30 independent
boundary controls, 40 affected service checks, three selected legacy originals
and 220 reached conditions. Accepted syntax and authored P4 rules are unchanged;
unreported prefix differences and multibyte conversion remain partial.
COMP170 extends main-file failures below.
[Review](coverage/semantics/encoding-lexical-review.json).

COMP170 delivers completed-header warnings before rejected main-file parser
errors through existing checked file receipts. Warning 128, Parse 4 and Compile 64
report independently, including separate stdout newlines and exit 255 at zero
VM steps. The terminal result installs no program/history or Throwable and
explicitly refuses VM reentry. Thirty-seven exact profiles from 15 originals,
28 independent service controls, 240 terminal-state conditions and two accepted
include/eval controls pass; strict compilation covers 435 modules. The original
fixture's misplaced VM-history check remains a failed gate with zero credit.
Parser/schema contracts are unchanged; wider source profiles remain partial.
[Review](coverage/semantics/main-source-rejection-review.json).

COMP171 supplies rejected file/eval units with parser-mode lexical token tapes,
without calling the Zend grammar. Trivia and original positions survive; malformed
Unicode/heredoc segments stop later headers while retaining earlier interpolation
declarations. Accepted lexers, schema, adapter and authored P4 rules are unchanged.
Private native build, 53 independent scanner/service controls, 30 affected controls,
35 exact source cases, 200 reached conditions and four main-file regressions pass.
The initial null-scanner eval/file heredoc failures remain zero-credit packets.
Multibyte conversion and wider core remain partial.
[Review](coverage/semantics/rejected-scanner-tape-review.json).

COMP172 preserves completed encoding headers after nested namespace reductions
when a later parser error rejects the unit. Namespace nesting remains a compiler
check; genuine grammar errors and other parser validation still stop collection.
Sixteen eval/include and four rejected-main comparisons, 24 independent service
controls, 100 reached conditions with SL435 and two affected main regressions pass.
The original service fixture's extra namespace diagnostic remains zero credit;
accepted parsing and the receipt/runtime contracts are unchanged.
[Review](coverage/semantics/rejected-namespace-review.json).

COMP173 defers rejected-only class/interface/enum, static magic-method and try
validation to its native compiler phase, retaining later completed parser headers.
Readonly and duplicate-modifier parser stops remain active. Readonly body-prefix
differences were explicit refusals at that cut; COMP174 below extends them.
Thirty-eight dynamic and four rejected-main
comparisons, 49 service controls, 24 affected controls and 110 reached conditions
with SL435 pass at their recorded cuts. The original history fixture failure
remains zero credit; its correction requires exactly the rejection-exit record
and no partial declaration installation.
[Review](coverage/semantics/rejected-static-validation-review.json).

COMP174 validates rejected method-target modifiers at the foreign grammar's
actual function lookahead, before parameters/body. Earlier attribute headers
survive; forbidden readonly/asymmetric-set bodies supply none. Valid readonly
properties and ordinary method flags keep their headers. All 22 dynamic and four
main comparisons, 37 service controls, 108 reached conditions/SL435 and affected
49/24 controls pass at one cut. Constant-target prefix differences were explicit
refusals at that cut; COMP175 below extends them.
[Review](coverage/semantics/rejected-method-modifier-review.json).

COMP175 extends the checked foreign lookahead rule to constant modifiers before
initializers. Earlier attribute headers remain; forbidden static/abstract/readonly
and asymmetric-set initializers supply none. Visibility/final typed constants and
method/property contexts retain their behavior. All 22 dynamic and four main
comparisons, 42 service controls, 108 reached conditions/SL435 and 37 affected
controls pass at one cut. The mistaken native control missing `const` remains
separate; accepted parsing and native/schema/adapter/P4 contracts are unchanged.
[Review](coverage/semantics/rejected-constant-modifier-review.json).

COMP176 checks rejected trait-use alias modifiers at the named and unnamed
foreign reductions, retaining earlier encoding headers but cutting off later
ones for readonly and asymmetric-set flags. Six method-target flags still allow
later parsing; a missing semicolon stops in the foreign grammar with the same
empty later prefix. Native diagnostics retain their own message and alias-end
line. Thirty-eight dynamic and four main originals, 73 service controls, 108
reached conditions/SL435 and affected constant42/method37 controls pass at
their recorded cuts. The preliminary relative-path and multiline-line fixture
failures and an interrupted unwatchable-`cases.json` run have zero credit;
corrected authoritative campaigns hash their expectations. Accepted parser,
native helper, schema, adapter and P4 interfaces are unchanged. Broader
rejected-source prefixes remain partial.
[Review](coverage/semantics/rejected-trait-alias-modifier-review.json).

COMP177 defers rejected-only property-hook name, `get(...)` parameter-list and
empty-list checks until compilation, retaining completed encoding headers before
later parser failure. Property, promoted and ordinary parameter, and interface
contexts agree; parser-time invalid modifiers keep their earlier cutoff and can
preempt deferred checks. Thirty-six dynamic and four main originals, 62 service
controls, 110 reached conditions/SL435 and affected method37/constant42/trait
alias73 controls pass at their recorded cuts. Two multi-property grammar controls
are explicit Unsupported refusals with zero agreement, and the initial service
fixture failures have zero credit. Accepted parsing, native helper, schema,
adapter and P4 interfaces are unchanged; wider rejected-source prefixes remain
partial. [Review](coverage/semantics/rejected-property-hook-static-review.json).

COMP178 stops rejected comma-separated property declarations at their opening
hook brace, matching Zend's grammar before any hook body. Earlier attribute,
initializer and completed-hook headers survive; parameter and ordinary property
lists retain their behavior. Twelve dynamic and four main originals agree,
76 maintained service controls and 40 independent challenges pass at their
recorded cuts. The two COMP177 multi-property refusals are now supported.
Accepted parsing, native helper, schema, adapter and P4 rules are unchanged;
wider rejected-source prefixes remain partial.
[Review](coverage/semantics/rejected-multiproperty-hook-review.json).

COMP179 defers rejected-only attributed global constant-list validation to
compilation, preserving later headers across namespaces and initializer closures.
Later parser-time modifiers and nonliteral encoding declarations keep their
priority; class, single and unattributed constants retain their behavior.
Sixteen dynamic and four main originals agree; 25 service controls, 76 affected
hook controls and 32 independent challenges pass at their recorded cuts.
Accepted parsing, native helper, schema, adapter and P4 rules are unchanged;
wider compiler and attribute behavior remains partial.
[Review](coverage/semantics/rejected-constant-attribute-review.json).

COMP180 stops rejected abstract/final anonymous classes before constructor
arguments and bodies, preserving earlier attributes and encoding headers.
The actual NEW terminal's value and span distinguish named classes whose
preceding statement list begins with NEW; the empty-list sentinel is excluded.
Sixteen dynamic and four main originals agree; 27 service controls, 101 affected
controls and 52 independent challenges pass at their recorded cuts. The initial
direct-parser negative-index warnings remain preserved with zero gate credit.
Accepted parsing, native helper, schema, adapter and P4 rules are unchanged;
wider rejected-source/compiler behavior remains partial.
[Review](coverage/semantics/rejected-anonymous-class-modifier-review.json).

COMP181 admits parsed attributed global multi-constant declarations to authored
compilation. Ordered initializers, reached closure bodies, qualified class checks
and retained compiler lines precede the final attribute fatal; ignored attribute
arguments retain parser warnings. Eval/file compilation terminates before
catch/finally. Single attributed constants and wider attribute behavior remain
partial. Across preserved cuts and reviewed guard bridges,93 distinct original
source comparisons agree; one single-attribute control remains Unsupported.
Strict412 conditions/435 modules and the final pipe controls pass. The full
classified syntax/inventory gate passes30,981 profiles with zero unresolved
failures at its frozen syntax cut; the [review](coverage/semantics/attributed-constant-compile-review.json)
records the pointwise bridge to final semantic bytes.

COMP182 compiles quiet single attributed constants in initializer/name/metadata
order and activates them through their original declaration. Metadata arguments
stay deferred; structural argument errors retain their per-value order and builtin
target/repetition errors follow every group. Existing compiled-image authentication
and exact closure-template reuse preserve source/code authority and initializer
behavior. The former COMP181 quiet singleton refusal is promoted. Successful
Deprecated metadata remained Unsupported at the COMP182 cut;
wider attributes and full core remain partial. Thirty-seven new source agreements,
two explicit Deprecated refusals, six affected originals and132 strict conditions
across438 modules pass at the recorded cuts. Final pipe controls pass. The failed metadata-array pool case
is preserved; its source-domain fix admits no runtime metadata root.
[Review](coverage/semantics/single-attributed-constant-review.json).

COMP183 pairs literal/null Deprecated metadata with actual source and
`constant()` reads. Installed name/metadata, user versus startup severity,
captured query/prefix selection and recursive-handler protection preserve
warning order across rebinding, namespace shadows and direct handler throws.
Body/retval exits retain the disabled handler through local cleanup and protect
the constant while the saved callback releases; repeated destructor exit keeps
the latest status. At this cut, a fresh local-destructor throw cancelling exit
stayed named Unsupported for COMP184. `defined()` remains quiet. Nonowning primitive/interned
strings are paired; owning values, converted queries, trait collision folding
and wider metadata remain partial. The56-original family has49 exact agreements
and seven separate refusals across preserved disjoint cuts;341 strict conditions
across441 modules,132 affected conditions and six older originals pass. Final
pipe controls pass; parser inputs stay fixed.
[Review](coverage/semantics/deprecated-global-constant-review.json).

COMP184 cancels Deprecated handler exit when a local destructor throws a fresh
Exception, then restores the real saved catch/caller tail. The two existing
marker phases preserve pending exceptions/read/API owners through eager saved
callback release, retain native previous links on replacement and keep exit
status 3 after catch. The unchanged COMP183 refusal source is promoted; five
more originals cover source/API and cleared captured-call ownership. Six exact
source comparisons,550 reached conditions across444 modules and four ordinary
throw/exit controls pass. The requested joined SL444/inventory base load passes;
parser/task/state interfaces stay fixed, so the prior pipe/syntax cuts stand.
[Review](coverage/semantics/deprecated-handler-cancellation-review.json).

COMP185 pairs owning values from existing ordinary constant producers with
Deprecated reads. Direct opcodes retain the fetched value/class before warning;
stable-text APIs and genuine global constant AST initializers retain selection
until successful delivery. Original nonfoldable lookup/class certificates survive
handler-created namespace shadows. Live receipts own pre-warning copies while
borrowed parameter metadata stays empty. Genuine saved binders and readonly eval
control views preserve global-AST exit/cancellation frontiers, including parked
caller frames. Owned parameter, class and static-property defaults remain
Unsupported; function-local dynamic statics remain ordinary opcode reads.
Thirteen new/promoted source agreements, three separate default refusals,
345 owned-state and550 affected conditions across445 modules, plus four older
scalar/builtin throw/exit originals pass at frozen156cfe734. The joined SL445/
inventory base load passes; prior syntax/pipe and other source cuts remain historical.
[Review](coverage/semantics/deprecated-owned-constant-review.json).

COMP186 pairs owning Deprecated defaults with genuine unscoped named-function
receives. Captured prefix/class/read certificates and bounded direct DEFINE cuts
preserve namespace shadowing and reentry. A nested receive can fill the same cache;
the outer value replaces that slot only when cacheable. Cache publication and the
formal's ownership precede type verification, including failure. Fresh/released
exit markers preserve the real parameter binder and retire the receive at its
actual discard. Method/Closure and class/static-property owning defaults stay
explicitly Unsupported. Twelve new/promoted source agreements, two separate
receiver refusals and 449 reached conditions across 446 modules pass at 3b89b723b;
the promoted old default passes six affected conditions. An equivalent user-leaf
discriminator at ded9e52f4 restores the original E_STRICT/eval-cut check: all 76
conditions pass under the unchanged cap. Prior source, pipe and syntax cuts stay historical.
[Review](coverage/semantics/deprecated-parameter-default-review.json).

COMP187 receives owning Deprecated defaults through fixed-name instance/static
calls to ordinary named-class by-value nongenerator methods. Actual descriptors,
default/function identities, declaring/called scopes and saved publication/call
prefixes authenticate reception and handler reentry. Inherited methods share the
declaring cache; formal/cache ownership precedes type failure, and receiver roots
and real binders survive cancellation cleanup. Only user-Deprecated frontiers and
leaves enter this new route. Eleven originals agree exactly, four separate
Unsupported controls retain zero agreement, and 259 author plus220 independent
reached conditions pass across448 modules. Closure/trait/byref/variadic/Generator/
dynamic-call recipients and class/static-property defaults remain partial.
A focused current-manifest SL448 load also passes; source comparisons retain
their recorded cuts without replay.
[Review](coverage/semantics/deprecated-method-default-review.json).

COMP188 receives owning defaults in actual unscoped real Closure literals and
ordinary clones whose same-template history proves Shared/Unscoped. Source donor
checks guard omitted/named-hole cache hits and post-handler binds. Captured reads
and cleanup survive callback-created private siblings, while the real binder
refuses their cache transfer. Actual captures/formals preserve ownership and
type-failure/cancellation order. Twelve originals agree; seven explicit refusals
retain zero agreement. Private reached checks and the joined main SL449/inventory
load pass at their recorded cuts. Bound/scoped/private, unknown/temporary cache
families, arrows and wider defaults remain partial; prior source cuts stand.
[Review](coverage/semantics/deprecated-closure-default-review.json).

COMP189 receives owning defaults through receiver-free same-scope bind/bindTo
REAL Closure copies and ordinary bound clones. Actual binding/API/source proof
and the retired source's known Shared/Unscoped stamp preserve the existing full
family cache guard without retaining the source or its captures. Eight originals
agree, one private scope-roundtrip refusal retains zero agreement, and one actual
binder/cache/formal owner front passes75 strict449 conditions with zero/one-step
budget and resumed/direct equality. Reentry, TypeError and exit cancellation
retain ordinary ownership and cleanup. Empty lexical/called scopes are this
implementation cut; broader This/called-class modes, private/mixed/temporary
cache identities and wider default forms remain core work. The prior source cuts
stand without replay; only460's selected-binding predicate changes.
[Review](coverage/semantics/deprecated-bound-closure-default-review.json).

COMP190 separates receiver-free empty-scope REAL private caches by actual
Closure/default identity, alongside unchanged Shared entries. Scalar-before-donor
and named-invoke preparation use the same owner routing. Genuine receive births
capture nonowning cache owners; same-cache children can fill a pending slot while
other live/retired owners cannot. Fresh clones, COW, type ownership and cancellation
retain native behavior. Private empty-array availability lasts through captured
child callbacks until actual storage release, without pinning Closure/source
objects. Fourteen originals agree at preserved cuts;273 independent strict450
checks cover reentry/provenance, cache/formal roots, retired handles and quiet
drop. Shared/default/class-constant encodings and455 policy stay fixed. Wider
scope/This/temporary/unknown modes and default families remain core work.
[Review](coverage/semantics/deprecated-private-closure-default-review.json).

The combined main SL450 load passes for COMP190, OB23 and GC59; its [shared record](coverage/semantics/deprecated-private-closure-default-review.json) preserves the tested source cut and adds no source-agreement credit.

COMP191 adds ordinary nongenerator REAL `Closure::call` owning defaults through
actual Shared or invocation cache identity. Distinct calls stay separate even
with identical source/receiver/site; receive history cannot transfer a child's
cache across owners. Temporary values survive callee local callbacks, then an
exact nonowning cache-free job precedes API receiver/source cleanup. Same-scope
Shared reuse, TypeError, throw and cancellation preserve native behavior. Ten
originals agree at retained cuts; two fake-method cold/warm controls remain
explicit future refusals with zero agreement. Independent361 strict451 premises
cover the actual cache/formal budget front, local/free/context order and nested
owner isolation. Source-only donor guards also protect scalar cache hits.
Direct scoped, wider receiver/default and held Generator/captured-entry/pending
families remain core work. [Review](coverage/semantics/deprecated-closure-call-default-review.json). The current joined main SL451 load and inventory check pass; the review records their exact tested cut.

COMP192 adds direct class-scoped REAL Closure literals, binding copies and clones
with actual borrowed This and distinct lexical/called classes. Existing Shared
and private owner/birth laws retain clone freshness, named holes, cache reentry,
TypeError and throw behavior. Ordinary scoped-private destruction preserves rows
through capture/static callbacks, then frees them before bound This; pending
HANDLE history alone cannot revive the cache. Quiet and staged receiver-free
copies, including inherited CalledChild, use the same authentic records. Eleven
originals agree; one warmed fake-method refusal retains zero agreement. Separate
107/93/187 strict452 fronts prove roots, exact cache death and owner/scope cuts.
Generator-close release and other held entry families remain outside this law.
[Review](coverage/semantics/deprecated-scoped-closure-default-review.json).

COMP193 adds direct public ordinary instance/static method FCC and
`Closure::fromCallable` default recipients and their clones. Actual captured
descriptor/scope/receiver records select the callee; a nonowning ENTRY witness
preserves Shared history after source/receiver retirement. Genuine child entry
and exact cache-owner proof govern reentry. Fake method statics remain owned by
the original method; private cache-free precedes This-only child cleanup.
The warm scalar-before-owning-donor source is promoted from its complete192
native packet. Twelve owning-default originals and one scalar preservation
original agree; three held controls earn zero agreement. Separate123/114/155/90
strict453 fronts prove ownership, entry history and cache authority. Explicit
wrapper/pending owning invokes, nonpublic/Trait/Generator and held303 cleanup
remain outside this finite family.
[Review](coverage/semantics/deprecated-method-fcc-default-review.json). The current
joined main SL453 load and inventory pass at their recorded cut.

COMP194 receives owning Deprecated globals during ordinary named-class constant
lazy initialization. Actual declaration/binder and selected lookup facts retain
callback cleanup and namespace shadowing. Type validation precedes publication;
a genuine begin-history cut supports nested fills, and untyped replacement
preserves earlier compiler cache views. Historical facts/snapshots add no root;
old computed cache-only values were a future boundary at that cut. Static-property
and Trait initialization and established Generator/303 holds stay separate.
Twelve originals agree, one explicit availability refusal earns0, and355
independent strict454 conditions pass. Current joined454/inventory also passes
at the recorded source cut.
[Review](coverage/semantics/deprecated-class-constant-owned-review.json).

COMP195 replaces computed class-cache arrays through genuine staged old-value
release while one publication task protects the pending new value. Readonly
structural history reconstructs earlier foldable arrays only in a compiler view;
retired containers and opaque Closure leaves acquire no historical owner.
Five originals agree, including one authentic194 native promotion. Separate
106/114 strict455 fronts prove ownership, history, nested lazy initialization
and budget continuation. The throwing-old-child native times out after `H|F|D|`;
its model-only Unsupported control has zero agreement. Wider abrupt,
static-property/Trait and held Generator/303 paths remain separate.
[Review](coverage/semantics/computed-class-cache-replacement-review.json). Current
joined455/inventory also passes at the recorded cut.

COMP196 receives owning Deprecated globals in ordinary named-class deferred
static defaults through actual declaring cells and saved binders. Selected
lookup facts preserve arrays, objects and Closure aliases across shadows;
first-fill, handler cancellation and retired typed-reference constraints remain
intact. Normal old-slot cleanup keeps one pending value owner and commits after
old-item release. Eight originals agree, including one explicit exit; independent
82/63/135 strict456 fronts and current joined456/inventory pass. Busy same-slot,
old-release abrupt, Trait/Generator/303 and wider forms remain separate.
[Review](coverage/semantics/deprecated-static-property-default-review.json).

COMP197 receives owning globals through genuine instance-template binders before
object allocation. Selected lookup records preserve shadowing and exact values;
actual write/link cuts freeze inherited templates and reject stale receipts,
including later legacy overwrites and replayed events. Templates and each object
own their current values; historical records add no root after old computed
containers and Closures retire. Normal replacement protects one pending value
through old cleanup and a different class's initialization. Nine originals agree
(eight normal, one explicit exit); independent strict457 fronts pass 79/73/46/82.
Busy same-template, old-release abrupt, Trait/Generator/303 and existing holds
remain separate. [Review](coverage/semantics/deprecated-instance-property-default-review.json).
Actual current joined457/inventory pass at b6d797120; source/runtime/tests and material review are secured.

COMP198 receives omitted owning defaults through fixed-name public ordinary
constructors. Actual allocated This/scopes and caller CTOR_RESULT govern live
reception; Shared caches compose with explicit/inherited constructor calls and
existing promotion. Closed receipts survive receiver retirement without adding
roots. Actual Deprecated-handler and body exits mark failed construction before
owner release, preserving destructor suppression for escaped This and ordinary
explicit-call behavior. Eight originals agree (six normal, two explicit exits);
independent strict458 fronts pass 91/51/106 conditions, and current joined458
plus inventory pass at e4618952198. Dynamic/anonymous/keyword/default-NEW227,
nonpublic/Generator/wider signatures and held families remain separate.
[Review](coverage/semantics/deprecated-constructor-default-review.json).

COMP199 receives owning constructor defaults through initialized CV class strings.
Exact caller selection and a nonowning birth witness preserve pre-argument class
selection through rebinding, same-site nested calls and receiver retirement.
Different selected subclasses retain their own receipts while sharing inherited
constructor caches. Four originals agree (three normal, one explicit exit7);
independent strict459 fronts pass 70/73/53 conditions. Ordinary CV aliases keep
their existing by-value read behavior; wider selectors and held entries remain
separate. Actual joined459 and inventory pass at ba1bd7c5a9; source/tests and review are secured.
[Review](coverage/semantics/deprecated-class-string-constructor-default-review.json).

COMP200 receives owning constructor defaults through `self`/`parent`/`static`
inside ordinary named method factories. Genuine factory scope/call history stays
distinct from constructor scope and survives factory-receiver retirement without
adding roots. Selected parents require authenticated child cache entries. Four
originals agree (three normal, one exit7); independent strict460 fronts pass
63/63/52/23 conditions. Actual joined460/inventory pass at 8c4a3e17e; the child
omission diagnostic remains zero credit and no completed source/front was replayed.
Captured/service/Trait/Generator/wider and established held entries remain separate.
[Review](coverage/semantics/deprecated-keyword-constructor-default-review.json).

COMP201 receives owning defaults through public ordinary method calls whose
member name comes from an initialized CV string. Actual selected function/scopes
and captured publication history survive rebinding, case aliases and receiver
retirement without a new witness or root. Same-site different methods keep their
function/default caches separate. Four normal originals agree; independent
strict461 fronts pass 55/57/56 conditions, and actual joined461/inventory pass at
95668007e4. Literal/keyword static class Names and existing ordinary alias reads
retain their bounds; callback/nonpublic/magic/Generator/wider and held entries
remain separate. [Review](coverage/semantics/deprecated-cv-method-default-review.json).

COMP202 receives owning defaults in authentic public method shutdown callbacks.
Exact current entry/arguments and a nonowning selected-target witness preserve the
absent callee callsite and closed history after registry reset/receiver retirement.
Registry owners and borrowed This stay unchanged; ordinary implicit This is
included. Five normal originals agree; independent strict462 fronts pass 86/78/83.
Fixed registration/public/by-value/nongenerator and capture/producer/held bounds
remain explicit. Source/runtime/tests are accepted at fae753133a; actual joined462
and inventory pass. [Review](coverage/semantics/deprecated-shutdown-method-default-review.json).

COMP203 receives owning extra defaults in authentic public method error/exception
handlers after four diagnostic arguments or one Throwable. Exact entered-target
proofs and nonowning kind/producer history preserve Shared identity and actual
callback/formal/Throwable owners; borrowed This stays rootless. Four normal
originals agree, including one builtin default deprecation before repeated caught
TypeErrors. Strict463 fronts pass 86 exception/76 error-owner/90 rejection checks;
only the exception front renews budget continuation. Source/runtime/tests are
accepted at fa5139bf5c; actual joined463 and inventory pass. Broader producers and
held domains stay separate. [Review](coverage/semantics/deprecated-handler-method-default-review.json).

COMP204 receives owning extra defaults in authentic ordinary public autoload
methods. One class-name argument, selected callback and real lookup/explicit-call
contours preserve Shared function/default identity. The registry owns its receiver;
current This borrows it, so actual warning-time unregister can retire it before
binding/body. Captured selection/request history stays heap-free; retired receiver
consumers remain held. Four normal originals agree and strict464 fronts pass
76 shifted-cut/scope,96 retirement and86 rejection checks. Source/runtime/tests
are accepted at67b944566d; actual joined465 and inventory pass.
[Review](coverage/semantics/deprecated-autoload-method-default-review.json).

COMP205 receives owning extra defaults in genuine ordinary public tick method
callbacks after their registered arguments. Exact marker/selected-row proof and
nonowning history preserve Shared identity after unregister, with existing registry
and formal owners; active unregister retains the calling row. Four normal originals
agree, including registration-argument rebinding and repeated TypeErrors. Strict466
fronts pass 72 marker/history, 96 owners/continuation and 91 type/cache conditions.
The finite noarg Deprecated donor plan applies while ticks are inactive
(`FREQUENCY=0`); active attributed declarations keep their boundary.
Source/runtime/tests are accepted at 50f1ee75a; actual joined466 and inventory pass.
[Review](coverage/semantics/deprecated-tick-method-default-review.json).

COMP206 receives owning extra defaults in genuine named USER string error,
exception, shutdown, tick and autoload callbacks. Existing family contexts authenticate supplied
arity; their witnesses retain selected function/source/publication. Shared identity
and all argument/cache/Throwable roots stay unchanged. Source-only owning hit checks and
explicit named/method proof domains preserve cold/warm and direct-child authority.
Six normal originals agree, including one builtin Deprecated stderr case. Strict467
fronts pass 59 autoload, 58 child/reentry, 52 cold shutdown, 85 type and 89 exception
conditions; only the exception front renews continuation checks. Runtime/source/
tests are accepted at714d1bd8c; actual joined467 and inventory pass.
[Review](coverage/semantics/deprecated-named-callback-default-review.json).

COMP207 receives owning defaults in direct quiet-CV public method string/array
calls. Full selected-wrapper proof survives argument mutation; normal instance
and static source-object lifetimes stay intact. A nonowning raw-entry bit separates
closed raw/FCC history and rejects missing FCC child ENTRY without changing cache
identity. Five normal originals agree; strict468 fronts pass 63 instance, 52 distinct
functions, 47 raw/FCC, 93 inherited scopes and 87 static-retirement conditions. The
four initial sources retain their genuine-raw bridge; only the affected mixed
source repeated. Source/tests are accepted at e3d2c106c; actual joined468 and inventory pass.
[Review](coverage/semantics/deprecated-raw-callable-default-review.json).

COMP236 reuses the existing string-class kind stamp with quiet member CVs or
compiled members. Two source-selected contracts preserve old defaults while
checking immutable bytes or original VARIABLE identity; old class entry/mint,
triple/fallback/task/root and cleanup bodies remain literal.
Two originals and 281 first-attempt strict496 conditions pass (122 author,159 peer).
Actual class-before-member effects, false-override refusals, protected nested
stamp consumption, saved source changes and folded array COW are verified.
One old495 missing-kind/order/refusal front has43 conditions at zero acceptance
credit; no separate oldCLI run, correction or replay occurred.
The exact seven-commit source/runtime/test packet is accepted at `cb4897556`;
actual current496 passes (30.048519440 s, source0). Existing producer/API/held
bounds remain separate, with no new kind, field, value or owner.
[Class rvalues/quiet members](coverage/semantics/deprecated-rvalue-class-quiet-member-constant-review.json)
The preceding scoped/CV pool gate retains two originals/344 conditions at its own
cut in the [immutable-member review](coverage/semantics/deprecated-scoped-cv-pooled-member-constant-review.json).

COMP237 admits direct This class-constant reads in existing ordinary public method
bodies through the allocated current receiver's physical named class. Literal,
compiled, quiet-CV and runtime members preserve existing source/saved-head laws;
lexical Base does not replace actual Child. Current/saved frames retain the receiver
after handler global removal, and folded arrays keep ordinary COW. Two public
originals and 349 strict497 conditions pass at their frozen cuts; old496's 34 reached
notice-source refusal conditions retain zero agreement. Nonpublic composition is
structural through unchanged491. No new kind, task, field or owner is added. Actual joined498 passes at
`582faadf5` (15.990735010 s, source0); inventory statuses stay unchanged.
[Review](coverage/semantics/deprecated-this-class-constant-review.json).

COMP238 handles ordinary-object class rvalues with literal constant members through
a value-free normal cursor. Existing eager cleanup retires the temporary before
notice protection, preserving selected class without an object root. Same-constant
destructor reentry warns independently; a supplied destructor Exception instead
cancels acquisition and preserves the old target. Three public folded originals
and 318 strict497 conditions pass at their frozen cuts. Old496's 38 reached refusal
conditions and one corrected fixture failure retain zero credit. The
neutral cursor has no roots; a genuine later pending Throwable keeps its ordinary
owner. Wider members, object/producer/lifecycle and held domains remain separate.
Actual joined500 passes at `641680373` (15.790159808 s, source0); inventory statuses
stay unchanged. [Review](coverage/semantics/deprecated-object-rvalue-class-constant-review.json).

COMP239 preserves original ordinary-object class kind across runtime, quiet-CV and
compiled member evaluation using a separate value-free marker. Existing staging
retires the raw receiver before destructor-modified member reads; handler rebinding
then preserves the captured class/member. Three public folded originals and 310
strict497 conditions pass, including array COW and actual pending-Throwable discard
of the unentered member/pair/marker. Old496's 45 reached refusals and one pre-main
fixture-name failure retain zero credit. Old STRING and511 Identifier paths remain
disjoint and unchanged. Actual joined502 passes at `0915539956` (15.680219577 s,
source0); inventory statuses stay unchanged.
[Review](coverage/semantics/deprecated-object-class-computed-member-review.json).

COMP240 acquires class strings from original live returned references through
physical-cell and supported primitive payload checks. Existing literal dispatch
and STRING marker/member laws retain selection after local cell retirement or
global handler retarget/unset, with no new owner or cell pointer. Two public folded
originals and 293 strict497 conditions pass. Old496's 37 refusals/operand observation,
both pre-main fixture-name failures and one pre-execution joined-recorder failure
retain zero credit. Owning payloads, wider contexts and held lanes stay separate.
Actual joined504 passes at `4fc2f3928` (15.086509630 s, source0); inventory statuses
stay unchanged. [Review](coverage/semantics/deprecated-reference-class-string-review.json).


COMP241 acquires physically fieldless ordinary object classes from live returned
references. Existing rootless OBJECT tasks and generic retirement preserve local
D-before-member order, retained-global H-before-D, protected same-constant reads,
retargeted saved class/array COW and supplied-D-throw cancellation. Four public
folded originals and separate strict505 packets execute 256+461=717 conditions;
old50441 refusals and all four fixture failures retain zero credit. Actual joined506
passes at `5506b290f` (15.701051526 s, source0); inventory statuses stay unchanged.
[Review](coverage/semantics/deprecated-reference-object-class-review.json).

COMP242 adds a disjoint plain singleton declared DIRECT-child selector proof in517.
Actual inherited slots, source/effective hook refusals and canonical fieldless
children preserve receiver-D-before-child-P order, outside-child retention,
array COW and supplied-child-Exception cancellation. Three public folded originals
and separate strictSL505 fixtures execute 422+191=613 conditions; old50552 refusals
and two pre-main fixture failures retain zero credit. Actual joined507 passes at
`a4bc1ddc9` (15.675159260 s, source0); inventory statuses stay unchanged.
[Review](coverage/semantics/deprecated-reference-object-property-review.json).

COMP243 admits width>=2 plain declared public untyped DIRECT fields containing
null/bool/int or canonical physically fieldless ordinary children, including
repeated identities. The unchanged entry validates inherited physical slot order
and uniqueness; generic cleanup transfers each real edge and finishes later fields
before catching a supplied child Exception. Three source comparisons and separate
strict-SL281/203 fixtures pass at their private 507-module cuts; their 484 conditions
carry no unique-count claim. The old 76-condition late-Unsupported observation and
both failed timing/owner fixtures retain zero credit. The actual `56df02fe6`/507
load passes in 15.938919702 s with zero source credit. Wider graphs and held lanes
remain partial.
[Review](coverage/semantics/deprecated-reference-object-fields-review.json).

COMP244 extends plain DIRECT selector fields to finite nonflat acyclic graphs of
ordinary named instances with non-NUL class names, sibling sharing and outside owners. Pure traversal
rejects ancestor cycles; unchanged full entry retains physical layout authority.
Generic cleanup preserves every real field edge and supplied child Exception.
Two exact SL originals and separate strict-SL211/217 fixtures pass at private507;
prior Unsupported and already-normal throw control keep zero source credit.
The actual `3e242b84a`/508
load passes in 16.499710402 s with zero source credit.
[Review](coverage/semantics/deprecated-reference-object-graph-review.json).

COMP245 fills the physical-singleton plain DIRECT null/bool/int field case using
the existing graph policy. Inherited or own slot identity and ordinary receiver
cleanup remain intact; retained-cell retargeting keeps saved class/protected10
distinct from the later class value80. Two originals cover NULL/false/17/true,
with two native originals reused once. Separate strict-SL166/152 fixtures execute
318 conditions at private507 with no unique-count claim. Original Unsupported,
finite preparation, pre-main fixture and recorder failures retain zero source credit.
Actual `5f001a897`/508 loading passes in 15.678898274 s with zero source credit.
Wider payloads, cycles, property forms and held lanes remain partial.
[Review](coverage/semantics/deprecated-reference-object-scalar-review.json).

COMP246 admits plain DIRECT PFLOAT fields in the existing singleton, flat and
nested graph routes through three additive module517 clauses. Floats contribute
no heap edge; the existing whole-graph proof retains named/non-NUL class policy
and arm disjointness. Three exact SL originals at private507 reuse three native
originals once, covering 1.5 and nested NaN/shared-child retirement. Separate
strict-SL210/179 fixtures execute 389 conditions with no unique-count claim.
The original wrong-checkpoint179 failure and finite24 pending-VALUE diagnosis
retain zero credit; only the affected readiness fixture reran. Three obsolete
FLOAT refusal controls were retired without prior native/source replay. Actual
`286ef4a89`/508 loading passes in 15.588131937 s with zero source credit. Wider
strings/carriers, containers, aliases, property forms and held lanes remain partial.
[Review](coverage/semantics/deprecated-reference-object-float-review.json).

COMP247 admits authenticated non-NUL PSTRING_CARRIER values in those plain DIRECT
singleton, flat and nested selector fields through seven additive module517 lines.
Supplied-field authentication and the graph proof validate actual INTERNED or
request STRINGDATA identities; the structural singleton classifier adds no state
authority. String metadata adds no owner. Existing full-entry and cleanup proofs
preserve physical object edges and retirement. Three exact source comparisons at
private507 reuse three native originals once. Separate strict-SL275/221 fixtures
execute 496 conditions at their private507 cuts, with zero source credit and no
unique-count claim. Prior Unsupported3 and finite110/56 remain0. Actual
`d1d56fa46`/508 loading passes in 15.172327948 s with zero source credit. Byte-only
PSTRING/NUL, other types, alias/hook/setter/readonly fields and held/wider lanes stay partial.
[Review](coverage/semantics/deprecated-reference-object-string-review.json).

Canonical single string/float/int/bool TYPE fields require matching initialized
DIRECT authenticated non-NUL carriers/PFLOAT/PINT/PBOOL. Supplied type/payload
correlation remains separate from full-entry descriptor/slot/layout and cleanup
authority. Bool flat fields reuse the owner-aware whole named-graph wrapper;
old guards and the unconditional PBOOL whitelist stay literal. Three bool originals
reuse three native observations once at author508/peer507. Separate strict-SL
241/300 execute541 conditions/source0, including flat-policy refusals and real
shared-child retirement, without a unique-count claim. Earlier string/float/int
cuts remain separate. Precode Unsupported3 and finite51/59 retain0. Actual
`e6ae629b6`/508 loading passes in 15.018899741 s/source0. Standalone true/false,
wider types/property forms and held lanes remain partial.
[String review](coverage/semantics/deprecated-reference-object-typed-string-review.json),
[float review](coverage/semantics/deprecated-reference-object-typed-float-review.json),
[int review](coverage/semantics/deprecated-reference-object-typed-int-review.json),
[bool review](coverage/semantics/deprecated-reference-object-typed-bool-review.json).

Canonical single `false` TYPE fields admit matching initialized DIRECT PBOOL false
through the pure type guard and existing owner-aware whole-graph wrapper. PBOOL
true for that type stays refused; old bool paths remain literal. Three fresh
originals reuse native observations once at author508/peer507. Separate strict245/
305 execute550 conditions/source0 without a unique-count claim. Exactly four
obsolete251 false-pair refusals retire;237 retained premise strings stay literal.
Earlier cuts remain separate. Fresh Unsupported3 and finite51/59 retain0. Actual
`c0d891c7c`/508 loading passes in 15.345181812 s/source0. The separate true-type
extension follows; null types, wider forms and held lanes remain partial.
[Review](coverage/semantics/deprecated-reference-object-typed-false-review.json).

Canonical single `true` TYPE fields now admit initialized DIRECT PBOOL true through
the existing owner-aware whole-graph proof; PBOOL false for that type stays refused.
Three fresh originals reuse native observations once at author508/peer507. Separate
strict245/305 execute550 conditions/source0 without a unique-count claim. Only five
obsolete251 true-pair refusals retire;295 retained premise strings stay literal.
Earlier cuts remain separate; Unsupported3 and finite checkpoints retain0. Actual
`cd577eda4`/508 loading passes in15.482561237 s/source0. Standalone null, wider types,
byte-only/NUL strings and held lanes remain partial.
[Review](coverage/semantics/deprecated-reference-object-typed-true-review.json).

Canonical single `null` TYPE fields now admit initialized DIRECT PNULL through the
existing owner-aware whole-graph proof; default uninitialized slots remain distinct.
Only six module517 lines and new tests/registration change, with no legacy edits.
Three fresh originals reuse native observations once at author508/peer507. Separate
strict255/301 execute556 conditions/source0 without a unique-count claim. Fresh
Unsupported3 and finite55/58 retain0. Actual `6e6f0c182`/508 loading passes
in15.546954842 s/source0. Byte-only/NUL strings, wider types/property forms and held
lanes remain partial. The Generator-close private Closure cache / This release
contours under COMP192/193 remain held, separately from local selector exclusions;
callbacks and either family are not globally held.
[Review](coverage/semantics/deprecated-reference-object-typed-null-review.json).

COMP255 admits initialized DIRECT fields with exactly two singleton builtin
branches, `[T,null]` or `[null,T]`, for int/float/string/bool/false/true. NULL or
delegation to the unchanged exact-value guard must match the stored value; guarded
flat dispatch still proves the complete owner graph. Four fresh originals reuse
native observations once at author508/peer507 cuts. Separate strict author541 and
peer303 execute 844 conditions/source0 without a unique claim. Exactly 58 obsolete
nullable refusals retire across 14 protocols; every retained premise stays literal
and ordered, without historical replay. Unsupported4, finite precode inventories
and the peer pre-main notation failure retain0; only the affected peer fixture reruns.
Actual `16c6fd726`/508 loading passes in 16.037753027 s/source0. The primitive-union
extension below follows that cut. Uninitialized/alias fields, byte-only/NUL
strings and held lanes remain partial;
the narrow COMP192/193 Generator-close private Closure cache/This release holds stay.
[Review](coverage/semantics/deprecated-reference-object-nullable-primitive-review.json).

COMP256 admits initialized DIRECT fields under well-formed primitive unions of
at least two branches. The whole canonical type/whitelist/redundancy check
precedes unchanged exact-value branch selection and complete owner-graph proof.
Three normal source agreements retain author508/peer507 cuts with native
observations reused once. Separate strict516/319 execute835 conditions/source0
without a unique aggregate or new exception-source credit. Precode Unsupported3,
finite actual9/2-row checks and the original binder failure stay0; exactly two
obsolete nullable refusals retire while301 retained premises remain literal.
Actual `508c467b6`/508 loading passes in15.919208375 s/source0. Class/object/mixed
types, uninitialized/ALIAS fields and wider property forms remain partial;
the exact held contours stay held.
[Review](coverage/semantics/deprecated-reference-object-primitive-union-review.json).

COMP257 admits initialized DIRECT object fields under one resolved canonical
PTCLASS naming a loaded ordinary user class, with allocated exact/subclass INSTANCE
children. Complete owner-graph validation precedes singleton lookup; physical
edges, source/slot authority and cleanup remain. Three normal originals retain
author508/peer507 cuts with natives reused once. Separate strict329/321 execute650
conditions/source0 without a unique claim or child-throw source credit. The original
constructor-parenthesis elaboration failure stays0; only its affected fixture reruns.
Actual `53bc7c47a`/508 loading passes in15.848385727 s/source0. Unresolved/interface/
object/mixed/nullable/class-union and wider property forms remain partial; already
resolved self/parent spellings use this representation. Exact held contours remain.
[Review](coverage/semantics/deprecated-reference-object-typed-class-review.json).

COMP258 admits initialized DIRECT fields under canonical class/primitive unions
after complete shape/name/mask/class-duplicate validation, then unchanged
exact-value selection and the complete owner graph. Unused class alternatives
need not load; a selected object still requires a loaded ordinary class/subtype.
Three normal originals retain author2/508 and peer1/507 cuts with native3 once.
Separate strict630/374 execute1004 physical conditions/source0 without a unique or
child-throw source claim. Nine generic refusals retire while1476 retained premise
strings stay literal and ordered. Actual `1fcbad267`/508 loading passes in
15.526689657 s/source0. Wider property forms and exact held contours remain partial.
[Review](coverage/semantics/deprecated-reference-object-class-union-review.json).

COMP259 admits bounded initialized DIRECT fields under standalone object/mixed
or valid object-containing primitive unions. Complete mask/Boolean validation and
local carrier/object authentication precede exact tag matching and the unchanged
owner graph. Three normal originals retain author2/508 and peer1/507 cuts with
native3 once. Separate strict671/404 execute1075 physical conditions/source0
without a unique or child-throw source claim. Seventy old conditions retire
(69 generic refusals and one context binding);5115 retained strings stay literal
and ordered, without historical replay. Two before-launch preparations remain0;
no semantic attempt fails or retries. Actual composition `a10f49109` and combined
`972cd9882`/508 loading in15.123888404 s/source0 retain separate identities.
Nominal interface/intersection constraints, arrays, aliases and wider property/
lifetime forms remain partial; exact held contours remain.
[Review](coverage/semantics/deprecated-reference-object-object-mixed-review.json).

COMP260 admits ordinary resolved nominal interface/intersection/DNF constraints
with the prior seven primitive alternatives after full canonical shape/name/mask/
Boolean/subset checks. Selected targets must all be loaded ordinary class/interface
descriptors; primitive matches avoid nominal lookup. Source3 normal agreements
retain author2/508 and peer1/507 cuts with native3 once. Separate strict633/432
execute1065 physical conditions/source0 without a unique or child-throw source
claim. Five obsolete conditions retire;653 retained strings in two boundary lists
and one field list stay literal/ordered, without old replay. The initial draft
source failure and bounded diagnostic/preparation failures retain0; affected
source-v2 reuses saved natives. Actual `cf2fa7065` composition and `93807cdd6`/508
loading in15.739862419 s/source0 retain separate identities. Arrays, aliases,
readonly/hooks/setter variants and wider lifetimes remain partial; exact holds remain.
[Review](coverage/semantics/deprecated-reference-object-nominal-review.json).

COMP261 admits initialized public readonly typed DIRECT fields with canonical
protected(set) metadata, including inherited declarations and readonly-class
normalization from real constructors. Existing exact field types, source/class/
layout authority and physical owners remain. Source3 NORMAL agreements retain
native3 once at author2/508 and peer1/507 cuts; strict336/327 execute663 physical
conditions/source0 without a unique or child-throw source claim. The precode
signature-v1 elaboration diagnostic remains0; only its corrected finite inventory
reruns. All524 prior517 lines stay literal; no old condition retires or semantic
campaign replays. Actual `f4d1610d1` composition and the same508 loading in
15.366782398 s/source0 (report754cfb43) remain distinct from private cuts.
Protected/private get visibility, other setters, aliases, hooks and wider
lifetimes remain partial; exact held contours remain.
[Review](coverage/semantics/deprecated-reference-object-readonly-review.json).

COMP262 admits plain protected/private typed and untyped DIRECT fields with the
canonical default setter, retaining actual mangled KEY/DECL, inherited private
shadows and stored defaults. Local policy keeps type-only EPS separate from full
source/layout and owner-graph authority. Source3 NORMAL agreements use native3 once
at author2/508 and peer1/507 cuts; strict333/344 execute677 physical conditions/
source0 without a unique or child-throw claim. Exactly18 obsolete PRIVATE local
refusals retire across10 old field lists;2171 retained strings remain literal/
ordered without historical replay. The finite-v1 local-negative error and text
preparation retain0; only its corrected inventory reruns, with no changed source
or strict state retry. Actual `106a1c338` composition and combined `c90b74ae3`/508
loading in15.510795725 s/source0 (report2a22b631) retain separate identities.
Structural NUL keys add no Owned-NUL payload authority. Other setters, nonpublic
readonly, aliases, hooks and wider lifetimes remain partial; exact holds remain.
[Review](coverage/semantics/deprecated-reference-object-nonpublic-review.json).

COMP263 admits the remaining initialized typed DIRECT modifier forms: readonly with
no setter bits, public nonreadonly protected(set), and public/protected private(set)
with FINAL. Readonly defaults remain uninitialized; nonreadonly defaults gain no
restriction. Existing exact types, whole-owner graph and full source/layout checks
preserve equivalent-set/readonly-class normalization and physical cleanup. Three
NORMAL originals use native3 once at author2/508 and peer1/507; separate strict
354/352 execute706 physical conditions/source0 without a unique or child-throw
claim. Exactly20 obsolete generic projections retire while2219 retained strings
and specialized helper/source negatives remain literal/ordered. No COMP263 attempt
fails or retries; earlier Unsupported/inventory cuts retain0. Bilateral actual
`9182b7ae` composition and joined508 SL loading in15.447642532 s/source0
(reporta08e04d4) remain separate from private cuts. Hooks, aliases, containers and
wider lifetimes remain partial; exact held contours remain.
[Review](coverage/semantics/deprecated-reference-object-modifiers-review.json).

COMP264 admits initialized typed public DIRECT backed GET and block SET fields
through real source origins/bodies, separate from active hook context. Existing
exact types, full source/layout and whole owner graphs preserve physical release;
all615 prior517 lines remain literal with35 additions. Three NORMAL originals use
native3 once at separate author508/peer508 cuts. Strict389/252 execute641 physical
conditions/source0 without a unique or child-throw claim. Ten actual rows and six
hook ASTs retain GET/SET, default, virtuality and job distinctions. Shared Leaf
release and nested outside ownership preserve B10 and resumption without implicit
hook dispatch. Both initial finite-fixture failures retain0; only those queries
rerun, with no legacy edits or campaign replay. Bilateral actual `39c2183e`
composition and joined508 SL loading in15.432399042 s/source0 (report04b22ceb)
remain separate from private cuts. Untyped hooks, short SET implicit backing,
aliases and wider forms remain partial; exact held contours remain.
[Review](coverage/semantics/deprecated-reference-object-hooks-review.json).

COMP265 admits initialized typed public short SET DIRECT storage through actual
SET-origin, installed-function, source-expression and compiled-child receipts,
even without lexical own-property use. Existing exact types, graph paths and full
source/default/layout authority retain physical cleanup; all650 prior517 lines
remain literal with4 additions. Three first NORMAL originals use native3 once at
separate508 cuts. Strict367/292 execute659 physical conditions/source0 without a
unique or child-throw claim. Ten actual fields (3 short SET,2 GET,5 plain) retain
stored defaults, real jobs, false setter markers, shared/outside release, B10 and
resumption. One finite-fixture type failure retains0; only that query reruns,
without legacy edits or historical replay. Bilateral source composition0d3024
and tested ENUM202 joinb9a3/508 load15.731924920s/source0 (reportd6068694) remain
separate from private cuts. Untyped hooked fields, wider modifiers, aliases and
lifetime forms remain partial; exact held contours remain.
[Review](coverage/semantics/deprecated-reference-object-short-set-review.json).

COMP266 admits initialized public untyped DIRECT backed GET fields through real
source bodies, independently of active hook context. TYPEeps remains type-only;
complete graph and source/default/layout checks retain inherited/shared/outside
owners and physical cleanup. All654 prior517 lines stay literal with39 additions.
Three NORMAL originals reuse native3 once at separate author/peer508 cuts.
Strict410/317 execute727 physical conditions/source0 without a unique or
child-throw claim. Ten actual fields retain canonical TYPE/default/slot/job facts,
false GET markers, saved B10 and zero/one/full resumption. Baseline Unsupported3
and finite140/74 retain0; daemon-interrupted authorv1 has unknown exit/output and0
credit, while byte-identical affectedv2 passes under the unchanged240 cap.
Bilateral actual composition994493f99 and its six-group508 SL loading in
16.131328344s/source0 (report0fd70c23) remain separate from private cuts. Untyped
block/short SET, wider modifiers, aliases and lifetimes remain partial; exact
held contours remain.
[Review](coverage/semantics/deprecated-reference-object-untyped-hook-review.json).

Ordinary typed-name magic `__get` now admits canonical `int|string`/`string|int`
and singleton `true`/`false`/`null` returns within its existing source, value,
consumer and receiver bounds. Defining-context types and shared return verification
preserve exact strings, weak integer conversion and TypeErrors before caller
stores. Each group has two private507 source agreements with native once reused;
union SL93/32+82 and literal SL142+107 retain separate source0 cuts. Separate
joined508 checks establish loading, with no source/state renewal. Quiet Get,
BYREF/untyped-name, broader return/producer/ownership/lifetime forms remain partial.
[Int/string review](coverage/semantics/magic-property-int-string-return-get-review.json),
[literal review](coverage/semantics/magic-property-literal-return-get-review.json).

Ordinary typed-name `__get` also accepts primitive `T|null` and `null|T`
returns, authenticating both raw orders against the defining normalized type.
Two private507 originals agree with native once reused; SL135/93 and affected
125/19/86 keep separate source0 cuts. The preexecution19 fixture binding failure
is preserved; only19 was corrected and rerun, with125 unchanged. Actual484d
runtime/test/Make and reciprocal seams are reviewed; a separate joined508 load
passes in33.197897s with source0. Quiet Get, wider returns and value/producer/
consumer/root/lifetime bounds remain partial.
[Primitive-null union review](coverage/semantics/magic-property-nullable-union-return-get-review.json).

## Active work

Ordinary named functions returning by value support scalar goto through declare
bodies and empty zero-frequency Declare/Switch bodies. Checked opener/separator
lines preserve compiler adjacency; goto skips directives and prefixes while
reusing loop continuations. Nonowning CV operands read the current environment
after case effects; empty-case/default fallthrough and continue2 use the
existing Switch/loop kernel. Ordinary source/current/saved scalar boundaries and
no-tick identity defaults remain explicit. Direct global `func_num_args()` Switch
subjects also reuse the existing TMP/FREE proof under zero frequency; actual
argument count stays independent of default/formal slots, with runtime argument
views unchanged. [Argument-count review](coverage/semantics/plain-switch-argc-review.json).
Direct `@$cv` subjects use the forced-read TMP proof: snapshot0/NULL survives
case rebinding, with the existing read-before-mask-restore transport. The added
route requires no registered error-handler callback.
[Suppressed-CV review](coverage/semantics/plain-switch-silenced-cv-review.json).
Count-left logical operators also reuse the nonfolding TMP proof under the same
scalar/no-handler boundary, preserving lazy RHS writes and Boolean results;
the source/history guards retain exact root and child-line authority.
[Logical count review](coverage/semantics/plain-logical-argc-review.json).
Source-proved unbuffered USER RHS helpers retain their own current-frame count,
physical scalar locals and the restored caller's Boolean continuation.
[USER-RHS review](coverage/semantics/plain-logical-user-rhs-review.json).
Compact literal-integer exit RHS uses the same source boundary with cold heap,
output and shutdown state. A selected exit discards normal Boolean/assignment
work and unwinds real scalar frames; skipped exit returns normally. Source
evidence separates one normal outcome from one explicit exit13, and 193
focused conditions cover actual status/frame retirement and public resumption.
[Exit-RHS review](coverage/semantics/plain-logical-exit-rhs-review.json).
The distinct native, source, focused and acceptance/load cuts, including earlier
failures, are retained in these ledgers and the
[goto](coverage/semantics/plain-goto-declare-review.json),
[empty Declare](coverage/semantics/plain-empty-declare-review.json) and
[empty Switch](coverage/semantics/plain-empty-switch-review.json) reviews.
Wider payload/protected/callback/resumable contexts gain no route; I140/I106 remain
entirely unstarted.

Computed-property reads in main or a direct ordinary reader leave the CV
receiver unpinned through an exact quiet global-rebind helper. Actual request-cell
identity, relevant reference constraints and a distinct retained old-object CV
bound entry; saved history remains source/context-only. Initialized public
untyped DIRECT slots also support terminal single isset and quiet coalesce with
an integer-literal RHS. Exact consumer/source/line continuations preserve quiet
NULL presence and lazy fallback; existing selected-value copy, cell/owner laws
and pending-writer defaults remain intact. Terminal nullsafe reads check the
original CV before the name, then fetch the current CV without a second checkpoint.
If the helper leaves NULL, the normal fetch emits its Warning and returns NULL
under the same no-handler boundary. Terminal quiet nullsafe isset/fallbacks use
their real parent and independent access/consumer lines, retaining object targets.
Wider helpers, callers and consumers
remain partial. Source/state/load cuts and original failures stay separate in the
[timing](coverage/semantics/property-cv-dynamic-name-review.json),
[reader/global-cell](coverage/semantics/property-reader-global-name-review.json),
[terminal-isset](coverage/semantics/property-terminal-isset-name-review.json),
[coalesce](coverage/semantics/property-coalesce-name-review.json),
[nullsafe](coverage/semantics/property-nullsafe-name-review.json),
[late-NULL Warning](coverage/semantics/property-nullsafe-null-warning-review.json) and
[quiet-nullsafe](coverage/semantics/property-nullsafe-quiet-name-review.json) reviews.

ArrayAccess quiet consumers admit public untyped/mixed by-reference
`offsetExists`, demanding its result even when the outer expression is unused.
Scalar truth decides Get and releases the callback-result owner before that call.
Four exact source comparisons and 79 AL premises retain separate private cuts;
the original literal-string-key failure and 276-premise timeout remain zero
credit. Typed non-mixed returns and wider contexts remain
partial. [Review](coverage/semantics/arrayaccess-reference-exists-review.json).

Untyped/mixed reference Set/Unset callbacks ignore their return slot regardless
of outer assignment use. Existing shared cells and callback writes persist;
Set retains live RHS readback while direct method calls use ordinary return
demand. Three exact sources and separate 84/87-condition AL recipes pass at
their private cuts; the repeated prefix is not unique coverage. Non-mixed typed
returns and wider lifetimes remain partial.
[Review](coverage/semantics/arrayaccess-reference-discard-review.json).

Literal string dimension keys now authenticate their canonical interned carrier
against the actual key origin, raw compiled pool and existing literal producer.
All original input arms remain unchanged. Two exact sources and 73 AL conditions
pass at their private cuts; the preserved earlier failure receives agreement only
at this new cut. Wider source/producer/lifetime contexts remain partial.
[Review](coverage/semantics/arrayaccess-literal-key-review.json).

Compiled literal string bases now authenticate into the existing cast/bounds
Warning continuation. Two exact sources preserve accepting-handler dispatch,
live cast-key changes and fixed bounds results; 93 AL conditions check source and
identity refusals with unchanged roots/providers/locators. The two actual
producer-continuation refusals retain zero credit at that defined-key cut. Marked
keys and wider handler/owner histories remain partial.
[Review](coverage/semantics/string-literal-base-review.json).

Initially undefined ordinary key CVs on authenticated literal non-NUL INTERNED
bases now retain KEY_CV/name/frozen NULL through the first Warning. A mandatory
cast Warning follows even if the first handler defines an integer. Normal resume reads
the current unmarked, unconstrained null/bool/bounded integer/float CV, or silent NULL
while missing; later bounds completion keeps its fixed index/result. Two exact
SL originals at bfd/private508 and AL126 at13fd/private508 retain separate cuts.
The 28 derived conditions and 98 including acquisition/scaffolding carry no
unique-coverage claim; the Unsupported baseline remains0. Actual
`373824a8b`/508 loading passes in 15.845942714 s/source0. Generic capture, retention,
provider, locator, root and schema laws remain unchanged. REQUEST/other unsupported
strings, marked or constrained keys, other base producers, abrupt handlers and
wider lifetimes remain partial.
[Review](coverage/semantics/string-offset-undefined-cv-review.json).

The initially undefined CV receipt admits current valid non-NUL INTERNED and
REQUEST strings under the live unmarked/unconstrained ordinary-CV proof. Pure
string-to-integer conversion handles leading/nonnumeric text and saturation silently
after the mandatory cast Warning. REQUEST conversion requires the exact current
carrier and live selected cell; registry identity alone adds no owner. Two INTERNED
SL originals/AL97 retain their recorded private508 cuts. Two new REQUEST SL originals
at091/private508 reuse native observations once; separate AL109/34-derived and
independent AL80/34-derived cuts retain source0, without a unique aggregate. Baseline,
finite AL38 and compiler diagnostics remain0; old AL126/97 are not renewed. Actual
`7535a1811`/508 loading passes in 15.523780986 s/source0. Generic source/capture/phase/
provider/retainer/root laws remain unchanged. Other current value kinds, marked/
constrained keys, broader bases and abrupt/lifetime histories remain partial.
[INTERNED review](coverage/semantics/string-offset-current-string-cv-review.json),
[REQUEST review](coverage/semantics/string-offset-current-request-cv-review.json).

Initially undefined KEY_CV reads may select fresh live marked unconstrained
null/bool/int/fitting-float cells after mandatory CAST. Exact current-name binding
and explicit primitive/quiet guards retain separate String saved histories; absent
KEYCELL adds no root. Two private508 SL originals reuse natives once. Author AL112/
64-derived, peer AL108/56-derived and precode47 stay separate/source0; both original
compiler-only failures retain0. One checked PINT1 refusal is promoted without
renewing old AL126. Actual `e4835ad9d`/508 loading passes in15.118756066 s/source0.
Wider payloads, constraints and histories remain partial.
[Review](coverage/semantics/string-offset-current-marked-cv-review.json).

Fresh current marked cells also admit valid non-NUL INTERNED/authenticated REQUEST
string carriers after mandatory CAST. Current-name/liveness and exact selected
REQUEST identity remain required; registry bytes and absent KEYCELL add no owner.
Two private508 SL originals reuse native2 once. Separate authorAL116/71-derived,
peerAL133/81-derived and genuine precode52 keep source0 without an aggregate. The
original AL fixture-name collision stays0; only its same116/71 fixture retries
after a label-only fix. Seven old refusals gain checked positive replacements;
the formerly negative valid ARRAY controls gain positive replacements below,
without old protocol replay. The current joined load above is separate/source0.
Marked current raw/NUL or constrained strings, wider arrays and broader abrupt or
ownership/lifetime histories remain partial.
[Review](coverage/semantics/string-offset-current-marked-string-cv-review.json).

After Undefined and mandatory CAST, current marked unconstrained ARRAY CVs use
the selected physical/logical cell and table with the existing finite
DIRECT/ALIAS and quiet-child entry proofs. Conversion reads only outer
empty0/nonempty1 without a copy, COW or new owner. Two private508 SL originals
reuse native observations once. Author AL101 (51 derived), independent AL149
(79 derived) and the genuine precode68 graph retain separate source0 cuts,
without an aggregate. Fifteen old expectations across eleven fixtures gain
checked replacement classes without old-protocol replay. Family loading at
`972cd9882`/508 passes in 15.123888404 s/source0, separately from these private
cuts. Deeper/cyclic or object/constrained entries, constrained current cells,
broader bases and abrupt/lifetime histories remain partial. Initial ARRAY
offsets and generic capture/converter/API/source/provider/retainer/root laws
remain unchanged.
[Review](coverage/semantics/string-offset-current-marked-array-cv-review.json).


After the Undefined and mandatory CAST Warnings, current ordinary ARRAY keys
also convert by count with finite DIRECT scalar entries. The exact current
unmarked unconstrained CV/cell, physical allocation and logical table liveness
authenticate the selected table; no entry is read or coerced. Literal pool plus
CV sharing is harmless for immediate empty0/nonempty1 conversion. Initial ARRAY
keys keep their illegal-offset route. Two exact SL originals atf02/private508
reuse natives once. Author AL95/43-derived and peerAL85/35-derived remain separate
source0 cuts, without a unique aggregate. Snapshot19 plus14helper premises and
all baseline/fixture failures retain0. Actual `e6ae629b6`/508 loading passes in
15.018899741 s/source0. Mixed/nested/object entries, marked/constrained keys,
abrupt handlers, broader bases and wider histories remain partial; generic
source/capture/phase/provider/retainer/root laws stay unchanged.
[Review](coverage/semantics/string-offset-current-array-cv-review.json).

Nonempty current arrays also admit homogeneous ALIAS entries to initialized
unconstrained null/bool/signed-64-bit-int/binary64 reference cells. Existing current
CV/table authority and per-cell physical/logical liveness remain; repeated entries
retain real edges without a fixed owner count. Conversion uses only count, with
no payload conversion, COW or added ownership. Two exact production-SL originals
at6b73/private508 reuse natives once. AuthorAL106/49-derived and peerAL117/58-derived
retain separate source0 cuts, without a unique aggregate. Baseline/precode47 and
peer parser-only failure remain0; only the one-line fixture correction executes.
Actual `641d0cfb9`/508 loading passes in 15.936299678 s/source0, with both actual425
composition reviews CLEAR. Mixed DIRECT/ALIAS, string/nested/object/constrained
cells and wider histories remain partial; old DIRECT/API/converter, generic
capture/source/provider/retainer/root laws and held lanes remain unchanged.
[Review](coverage/semantics/string-offset-current-array-alias-cv-review.json).

Finite current ARRAY entries now mix the unchanged DIRECT scalar and primitive
ALIAS domains through one recursive traversal. Exact current CV/table and every
cell retain physical/logical authority; repeated aliases keep real edges while
conversion uses only count, without payload conversion, COW or new ownership.
Two private508 production-SL originals reuse native observations once. Separate
authorAL112/61 derived and peerAL124/64 derived retain source0 cuts without an
aggregate; precode48 and baseline Unsupported remain0. Only two historical derived
cv_key mixed refusals are promoted, with their exact replacements checked and no
old replay. Actual `58216a767`/508 loading passes in15.703481279 s/source0, with
both Dynamic and String425 composition reviews CLEAR. Wider ALIAS payloads,
nested/object DIRECT entries, marked/constrained keys and abrupt histories remain
partial; generic laws and initial ARRAY illegal-offset behavior stay unchanged.
[Review](coverage/semantics/string-offset-current-array-mixed-cv-review.json).

Current ARRAY entries also admit authenticated non-NUL INTERNED/REQUEST strings
in initialized marked unconstrained reference cells. Existing carrier validation,
physical/logical cell liveness and current CV/table authority remain required;
registry identity adds no owner. Conversion still uses only nonemptiness, without
payload conversion, COW or new ownership, and repeated aliases retain real edges.
Two private508 production-SL originals reuse native observations once. Separate
author AL90/41-derived and peer AL107/51-derived cuts retain source0, without a unique
aggregate. The actual REQUEST precode54, Unsupported baseline and peer pre-AL
binding-order failure retain0; only that fixture correction is retried. Four old
string refusals are promoted with replacement coverage and no historical replay.
Actual `4120052b7`/508 loading passes in 15.705737219 s/source0, with both Dynamic
and String425 composition reviews CLEAR. NUL/raw ALIAS string payloads, wider or
constrained referents, marked/constrained current keys and broader histories remain
partial; initial ARRAY offsets and generic capture/provider/retainer/root laws are
unchanged.
[Review](coverage/semantics/string-offset-current-array-string-alias-cv-review.json).

Current ARRAY conversion also admits one quiet level of DIRECT child arrays with
the existing DIRECT scalar entries. Each child is physically allocated and
logically live; pooled/shared children and repeated edges need no uniqueness,
mutation, COW or new owner. Only outer nonemptiness supplies the integer result.
Two private508 SL originals reuse native observations once. Separate author
AL91/38-derived and peer AL132/71-derived cuts retain source0; precode50 and
Unsupported baselines remain0, without historical promotion or replay. Deeper
children, object DIRECT entries, wider ARRAY-valued ALIAS cells and histories
remain partial. The current joined load above is separate/source0.
[Review](coverage/semantics/string-offset-current-array-child-cv-review.json).

Initialized marked unconstrained ALIAS cells also admit those quiet child arrays
through physical/logical HCELL authority and absent property/coercion/parameter
constraints. Repeated outer aliases own the cell; the cell owns its child once.
Only outer nonemptiness supplies the result, with no edge/owner/state changes.
Two private508 SL originals reuse native observations once. Author AL91/36-derived
and peer AL145/76-derived retain separate source0 cuts; precode61 and baseline
Unsupported remain0. Exactly two old derived refusals are replaced with checked
positive shapes, without renewing the old132 cut. Actual `508c467b6`/508 loading
passes in15.919208375 s/source0. Deeper/reference/object child entries, constraints
and wider current-key/base/abrupt/lifetime histories remain partial.
[Review](coverage/semantics/string-offset-current-array-alias-child-cv-review.json).

Initially undefined ordinary key CVs also retain a source-authenticated VARIABLE
base's valid non-NUL INTERNED header through returning Warning handlers. Two
local receipt/source arms preserve the frozen header and absent BASECELL/KEYCELL
when the current base is replaced, marked or removed; mandatory CAST and the
existing quiet current-key domain remain. Two exact private508 SL originals reuse
native observations once. Author AL154 (77 derived), peer AL153 (63 derived) and
precode50/full-state evidence retain separate source0 cuts without an aggregate.
One old structural receipt refusal is promoted with its wrong-source fence intact
and no old-protocol replay. Actual `c9c770e1a`/508 loading passes in15.467628574 s/
source0, separately from those private cuts. Wider bases, abrupt handlers and
lifetime histories remain partial; generic capture/provider/retainer/root laws
and String KEY_NULL histories stay unchanged.
[Review](coverage/semantics/string-offset-variable-base-cv-review.json).
Initially undefined VARIABLE non-NUL REQUEST bases also survive returning Warning
callbacks through a distinct ordinary unconstrained keeper of the exact saved
header. That current owner is required before CAST and after its callback;
BASECELL/KEYCELL stay absent even after the original cell physically retires.
Source authority survives owner loss, while genuine later BOUNDS stays fixed and
owner-free. Two exact private508 SL originals reuse native2 once. Separate author
AL126 (46 derived), peer AL184 (55 derived) and authentic precode67/full-state/heap
cuts retain source0 without an aggregate; Unsupported/preparation/fixture failures
remain0. Both pairs clear actual `47dc49ad9`/425 and Make while preserving later
String changes. Its 508-module load passes in15.566676035 s/source0, separately
from those private cuts and the current load above. Ownerless histories outside
the closed release contour below, changed masks and wider keepers/producers/
lifetimes remain partial; String KEY_NULL/API/root laws remain unchanged.
[Review](coverage/semantics/string-offset-request-base-cv-review.json).

First-Undefined supplied-Throwable callbacks also retain those REQUEST headers
through the same distinct ordinary keeper. Only two INTERNED-only discard fences
are removed; pending THROW_SEARCH, explicit KEY_CV receipt and keeper-gated source
plan remain. Two exact private508 SL originals reuse native2 once, preserving the
same Exception/destination99 while CAST alone or CAST plus old bounds8 precede
propagation. Separate author AL145 (62 derived), peer AL179 (58 derived) and
precode93/full-state/heap cuts retain source0 without an aggregate. One old normal
mask0/key4 identity expectation gains a fresh checked CAST/bounds4 replacement;
its old184 cut is not replayed or renewed. Both pairs clear actual `0e671433b`/425,
unchanged nested String33 and Make. Its 508-module load passes in14.983122608 s/
source0, separately from all private cuts and the current load above. Lost/marked
or wider keepers, other abrupt control and broader ownership/lifetime histories
remain partial; API/root laws, String KEY_NULL and held lanes remain unchanged.
[Review](coverage/semantics/string-offset-request-throw-review.json).

Initially undefined key CVs now return NULL when Undefined or CAST retires every
owner of the selected non-NUL REQUEST header, before the next conversion or bounds
Warning. A closed top-level contour checks all live cells/providers, a restored
INTERNED handler with mask0, scalar pools and non-owning source continuations;
missing ordinary keepers alone never prove release. Two exact private508 SL
originals at `fe6c0c4a8` reuse native2 once. Separate author AL130 (48 derived), peer
AL146 (46 derived) and authentic precode85/89 full-state/heap cuts retain source0
without an aggregate. The first author fixture notation failure stays0; its
correction changes no runtime/source evidence. Both pairs clear actual
`39c2183eb`/233/425 and current String/Get/foreign seams. Its 508-module load passes
in15.432399042 s/source0 separately from private cuts and the current load above.
Wider masks/providers, abrupt control and lifetime histories remain partial;
String KEY_NULL, supplied-throw discard, generic owner/root APIs and held lanes
stay unchanged.
[Review](coverage/semantics/string-offset-request-release-cv-review.json).

The same closed release also admits a still-registered valid non-NUL INTERNED
callback with mask2 and exactly one prior None/mask0 entry. Every other provider
guard remains. Two new private508 SL originals reuse native2 once. Separate
author AL141/56-derived, peer AL170/67-derived and precode83/89 full-state/heap
cuts retain source0 without an aggregate. Actual `8c3f0b691`/508 loading passes
in19.627555390 s/source0, separately from those cuts. Wider masks, stacks,
callbacks, providers, abrupt control and lifetimes remain partial; held lanes,
String KEY_NULL, supplied-throw discard and generic owner/root APIs stay unchanged.
[Review](coverage/semantics/string-offset-request-release-registered-cv-review.json).


Initially undefined ordinary key CVs on authenticated literal non-NUL INTERNED
bases now complete mandatory CAST and quiet current-key bounds diagnostics after
a supplied handler throw. The same Throwable and unchanged destination survive;
restored callback/mask state decides default reporting. Explicit KEY_CV receipt,
literal-owner and pending-THROW_SEARCH guards preserve String KEY_NULL histories.
Two normal private508 SL originals reuse native2 once. Separate author AL98 (41
derived), peer AL128 (63 derived) and precode51/full-state evidence retain source0
without an aggregate; a fresh genuine KEY_NULL fixture checks the receipt fence.
The original normal missing-diagnostic mismatches and preguard source cuts retain
zero additional credit. Actual `6063187d8`/508 loading passes in15.249904863 s/
source0, separately from the private cuts. VARIABLE/REQUEST bases and wider
abrupt/ownership histories remain partial; normal, API and root rules stay intact.
[Review](coverage/semantics/string-offset-undefined-throw-review.json).


Initially undefined key CVs on authenticated VARIABLE non-NUL INTERNED bases also
complete mandatory CAST and quiet current-key bounds diagnostics after a supplied
handler throw. The original base cell may physically retire; its source receipt
preserves the selected header without recapturing the current base. Two exact
private508 SL originals reuse native2 once. Author AL127 (52 derived), peer AL143
(40 derived) and authentic precode77/full-state evidence remain separate/source0,
without an aggregate; the original missing-diagnostic baseline retains0. Actual
`87842e7f5` preserves the later String changes; both pairs clear the shared425 and
Make composition. Its `eb1b36cf9`/508 load passes in14.865226590 s/source0, separately
from those private cuts and the current load above. REQUEST bases, other abrupt
control and wider ownership histories remain partial; generic API/root laws and
String KEY_NULL histories remain unchanged.
[Review](coverage/semantics/string-offset-variable-throw-review.json).

An outside ordinary CV now preserves the exact selected request-string carrier
when a cast Warning callback replaces the base CV and changes the live key.
Normal return reads the old bytes; a supplied exception keeps its identity and
the unchanged destination. Two originals agree at the private 504-module cut;
211 author and 144 independent AL conditions retain separate cuts, including 51
derived controls.
Baselines, failed runs and the registry-localization projection keep zero
source credit. Wider owner histories remain partial.
[Review](coverage/semantics/string-offset-retained-carrier-review.json).

Valid non-NUL interned strings are required for both the leading-text key and
base. The integer index is captured before the Warning. Handler return preserves that index through key deletion,
old-byte/bounds selection and supplied-Exception cleanup. Three exact source
comparisons pass at the private 506-module cut. Author287/30 derived and independent
202/15 derived AL conditions retain separate cuts, with no unique-count claim.
The actual `7ddc75785`/507-module SL load passes in 15.991617877 s with zero source
credit; it remains separate from these private checks and the current load above.
Baselines and the first AL parse failure retain zero credit. Wider key, base and
ownership contexts remain partial.
[Review](coverage/semantics/string-offset-leading-text-review.json).

Ordinary VARIABLE primitive reference keys retain the same selected live cell
through cast-Warning callbacks. Marked floats require a fitting quiet conversion;
base/provider/keeper/phase/root laws stay unchanged. Two exact INTERNED-base
originals agree at private507, reusing two native originals once. AuthorAL209
(30 derived) and independentAL181 (54 derived) retain separate executed cuts, with
no unique-count claim. The peer cut includes an entirely derived 45-condition
REQUEST entry/resume projection, with zero additional source credit. Actual
`cf42b2812`/508 loading remains a separate source0 check. Wider key/base/ownership
contexts remain partial.
[Review](coverage/semantics/string-offset-reference-key-review.json).

Against a valid non-NUL INTERNED base, leading-integer text keys admit marked
ordinary CVs containing valid non-NUL INTERNED strings and initially unmarked
ordinary CVs containing authenticated non-NUL REQUEST strings. The pre-Warning
index/message survives overwrite or key retirement without a key owner. Earlier
marked-INTERNED source/state cuts remain separate. Two REQUEST SL originals at006/
private508 reuse the normal native once and observe the supplied-throw native once.
Author AL226/43-derived and peer AL198/54-derived retain separate source0 cuts;
all67 affected old-front conditions are derived/source0. Acquisition42 and original
binder/fixture/recorder failures remain0, with no unique aggregate or old-tail replay.
Actual `8eb5783da`/508 loading passes in 15.363113732 s/source0. Both pairs accept the
literal shared425 composition: KEY_NULL/presentKEYCELL remains disjoint from
initially undefined KEY_CV/absentKEYCELL. The marked REQUEST increment below
extends initial acquisition; REQUEST leading bases, broader producers/ownership
and held lanes remain partial.
[Marked-INTERNED review](coverage/semantics/string-offset-reference-leading-key-review.json),
[ordinary-REQUEST review](coverage/semantics/string-offset-request-leading-key-review.json).

Initially marked ordinary reference keys also admit authenticated non-NUL REQUEST
leading-integer text against valid non-NUL INTERNED bases. Initial current-cell
acquisition and saved KEY_NULL/presentKEYCELL history remain distinct; the index
and message survive alias overwrite or key retirement without an extra owner.
Two SL originals at0137/private508 reuse native observations once. Separate author
AL243/52-derived and peer AL231/70-derived retain source0; all47 affected-front
conditions are derived/source0, without old-tail replay or a unique aggregate.
Baseline and acquisition34 stay0. Actual `64d425bab`/508 loading passes in
15.399402520 s/source0; shared425 composition is independently CLEAR. REQUEST
leading bases, constrained keys, NUL and wider histories remain partial.
[Review](coverage/semantics/string-offset-reference-request-leading-key-review.json).

A marked ordinary VARIABLE containing a valid non-NUL INTERNED base now captures
its immutable header before the cast Warning. Alias replacement preserves old
bytes while the current key supplies the later index; a supplied Exception keeps
identity, Previous and the unassigned destination. Two exact originals pass at
`18ef67e86`/508 with native reuse. Author AL210 (27 derived) and independent AL193
(62 derived) retain separate cuts; the latter includes all 54 entirely derived
affected entry checks with zero source credit. Actual `2289f000e`/508 loading
passes in 15.311957679 s with zero source credit. Generic keeper/key/phase/root
laws remain unchanged; the separate REQUEST-base extension follows.
[Review](coverage/semantics/string-offset-reference-base-review.json).

Authenticated non-NUL REQUEST bases in marked ordinary VARIABLEs now share one
current capture for readiness: exact selected-cell header identity or the existing
different live ordinary unmarked keeper. STRINGDATA supplies no owner. Two exact
originals pass at `d0d38baca`/508 with native reuse; author AL259 (66 derived) and
independent AL227 (96 derived) retain separate cuts. All 38 affected-entry checks
and three late-wrapper predicates are derived with zero source credit. Actual
`bec688099`/508 loading passes in 15.411343048 s with zero source credit. Generic
capture/keeper/key/phase/source/root/kernel laws remain unchanged. The separate same-cell alias extension
below preserves this cut; different marked keepers and wider ownership remain
partial.
[Review](coverage/semantics/string-offset-reference-request-base-review.json).

A distinct current ordinary alias can now retain the original BASECELL and exact
saved non-NUL REQUEST header after selected-name unset. Existing current lookup
and base capture prove the live owner without an extra marker or two-owner gate.
Two originals agree at c930/private508 with native reuse; author AL226/36 derived
and peer AL232/87 derived retain separate cuts, including57 affected derived
checks/source0 and no unique aggregate. Actual `257b351c7`/508 loading passes in
15.553720015 s/source0. Eleven compatible report filters pass66 author and66 peer
pure shape checks, with no backend replay. Different marked keeper cells, ownerless
release and wider ownership remain partial.
[Review](coverage/semantics/string-offset-reference-alias-keeper-review.json).

Ordinary unmarked VARIABLE base/key CVs now admit a non-NUL REQUEST base with an
INTERNED leading-integer key. Historical source/index receipts remain separate
from current provider readiness. Two source originals use a distinct ordinary
keeper; same-selected-cell alias reuse is an explicit derived control. Losing
the owner makes normal and supplied-throw LEADING completion Unsupported, while
authenticated BOUNDS completion stays fixed and owner-free. SL2 at2b30/private508
reuse native observations once. Author AL282/91 derived and peerAL238/73 derived
retain separate source0 cuts; affected68 are entirely derived, without a unique
aggregate. Baseline, acquisition44 and generation SyntaxError retain0. Actual
`cd577eda4`/508 loading passes in15.482561237 s/source0. Marked entries, REQUEST keys
on REQUEST bases remained partial at that cut; the matrix below extends those
combinations. Constraints, NUL and wider histories remain partial.
[Review](coverage/semantics/string-offset-request-leading-base-retainer-review.json).

The REQUEST leading-base receipt now admits ordinary or marked base/key CVs with
valid non-NUL INTERNED or REQUEST leading text, including a selected cell shared
by four names. Fixed index/message history survives writes and retired cells;
readiness still requires a current owner of the exact header. Normal and supplied-
throw lost-owner paths remain Unsupported. Four private508 SL originals reuse
native observations once; author AL339/37-derived, peer AL326/62-derived and the
entirely derived affected45 retain separate source0 cuts. The current joined
load above is separate/source0. Constraints, NUL, computed keys and wider owner
histories remain partial.
[Review](coverage/semantics/string-offset-request-leading-carrier-matrix-review.json).

Literal INTERNED leading keys now authenticate the actual string node and decoded
bytes on ordinary or marked REQUEST-base CVs, with present BASECELL and absent
KEYCELL. Current header ownership protects normal and supplied-throw completion;
genuine later bounds completion stays fixed after the final keeper retires. Three
private508 SL originals reuse natives once. AuthorAL305/44-derived and peerAL296/
87-derived retain separate source0 cuts without a unique aggregate; earlier ingress
and the narrowed pre-literal-node source cut retain their identities. The current
joined load above is separate/source0. Other computed/owning producers, constraints, NUL
and wider lifetimes remain partial.
[Review](coverage/semantics/string-offset-request-base-literal-leading-key-review.json).

String-only literal CONCAT trees now authenticate their exact decoded INTERNED
leading-key bytes on ordinary/marked REQUEST-base CVs, with present BASECELL and
absent KEYCELL. Fixed index/message and current-owner normal or supplied-throw
completion remain; genuine later bounds stay owner-free. Three private508 SL
originals reuse natives once. AuthorAL311/44-derived and peerAL350/118-derived retain
separate source0 cuts without an aggregate; precode175, baseline and the binder
diagnostic stay0. One old literal CONCAT refusal is promoted without replaying its
historical cut. Actual `00cc247e2`/508 loading passes in14.798786004 s/source0.
Other computed or owning keys, NUL, constraints and wider histories remain partial.
[Review](coverage/semantics/string-offset-request-base-concat-leading-key-review.json).

Integer/float leaves also enter literal-root CONCAT leading keys through exact
decoded bytes and actual compiled precision, retaining compile14 despite live17.
Four normal0 private508 originals reuse natives once, including genuine caught
supplied-throw and second-bounds callbacks. Separate pre144, AL423/57-derived and
AL422/112-derived retain source0 cuts without an aggregate. Two old numeric entry
refusals are promoted without historical350 replay. Actual `ccc4ed2f4`/508 loading
passes in15.223471997 s/source0 with separate String/Dynamic preservation reviews.
Other computed or owning keys, NUL, constraints and wider histories
remain partial.
[Review](coverage/semantics/string-offset-request-base-numeric-concat-leading-key-review.json).

Resolved bool/null CONCAT leaves now use their own compiler facts and each
CONCAT's raw pool bytes to retain INTERNED identity. The parser, owners and saved
continuations stay unchanged. Three normal0 private508 originals reuse natives
once, including caught supplied-throw and genuine later-bounds callbacks. Pre223,
author368/80-derived and peer383/128-derived plus44 compiler-only conditions retain
separate source0 cuts without an aggregate. A fixture-only elaboration failure
stays0; corrected affected/unrun checks pass. Actual `307bca8d1`/508 loading passes
in15.915859906 s/source0, separate from the current shared load above. Mixed
numeric-special trees, missing descendant facts and wider histories remain partial.
[Review](coverage/semantics/string-offset-request-base-special-concat-leading-key-review.json).

Integer literals also compose with resolved bool/null CONCAT leaves through the
existing pure decimal formatter, exact origins and per-CONCAT pools. Three normal0
private508 originals reuse native3 once. Pre217, authorAL380/80-derived and
peerAL404/132-derived plus fresh float8 retain separate source0 cuts without an
aggregate. Actual `1e75ceb9e`/508 loading passes in14.976729858s/source0
(`3025f0fc`), without renewing earlier source/state cuts or failures. Float-special,
unary/computed nodes, missing descendant facts and wider ownership remain partial.
[Review](coverage/semantics/string-offset-request-base-integer-special-concat-leading-key-review.json).

Quiet float literal leaves also retain compiled precision through resolved
bool/null CONCAT trees and exact per-CONCAT pools. Three normal0 private508
originals reuse native3 once, distinguishing compile14 from live17 for normal,
supplied-throw and genuine later bounds. Pre232, authorAL401/80-derived and
peerAL476/192-derived plus unary12 retain separate source0 cuts, with no aggregate
or replay. Actual `f4e88feaf`/508 loading passes in15.373098855s/source0
(`46aa4292`), separate from all private cuts. At that cut, float-valued ConstFetch,
unary/computed leaves, missing descendant facts and wider histories remained partial.
[Review](coverage/semantics/string-offset-request-base-float-special-concat-leading-key-review.json).

Immediate unary +/- of integer or quiet float literals now compose with resolved
bool/null CONCAT leaves through their own compiled result and precision. Four
normal0 private508 originals reuse native4 once, including negative selection,
caught supplied throw and genuine negative bounds at compile14/live17. Author
AL559/105-derived and peer AL701/292-derived plus17 fresh nested-unary compiler
conditions retain separate source0 cuts. Pre first84 and affected260, the original
fixture parse failure and prior integer/float cuts retain their identities without
replay or an aggregate. At that cut, nested unary, float ConstFetch, missing facts
and wider ownership remained partial.
[Review](coverage/semantics/string-offset-request-base-unary-numeric-special-concat-leading-key-review.json).

Finite nested numeric unary chains now require every actual child, own folded
result and matching compiled precision. Four normal0 private508 originals reuse
native4 once. Pre AL420, corrected author AL627/105-derived and peer
AL833/374-derived plus41 fresh numeric-string/binary compiler conditions retain
separate source0 cuts without an aggregate or replay. The original binding
failure retains zero credit and three unrun fixtures; only fixture order changed
before the corrected campaign. Numeric-string unary, binary-expression children,
float ConstFetch, missing facts and wider ownership remain partial.
[Review](coverage/semantics/string-offset-request-base-nested-unary-numeric-special-concat-leading-key-review.json).

Quiet fully numeric string-literal unary chains also compose with resolved
bool/null CONCAT leaves through actual decoded bytes, quiet coercion and each own
compiled result/precision. Four normal0 private508 originals reuse native4 once.
Pre432, author639/105-derived and peer909/438-derived retain separate source0 cuts.
The peer report aggregate remains false and both fixture failures retain zero;
only corrected compiler95 repeats at its separate cut. Actual `a2907470c`/508
loading (`9db1e93a`, 15.388192947 s, source0) is separate from the private cuts and
generic load above. Warningful or nonliteral strings, binary children, numeric
ConstFetch and wider histories remain partial.
[Review](coverage/semantics/string-offset-request-base-numeric-string-unary-special-concat-leading-key-review.json).

Quiet bare ADD/SUB/MUL/DIV children now compose with authenticated bool/null
CONCAT keys through actual child certificates, own compiler facts, both quiet
conversions and exact pure numeric results at compiled precision. Four normal0
private508 originals reuse native4 once. Pre v2 remains false: first98/97 pass,
third158 fails and fourth97 is unrun; only affected158 and formerly unrun97 pass
in v3. No passing450 aggregate is claimed, and all failures retain zero credit.
Author657/105-derived and peer862/367-derived plus100 compiler conditions retain
separate source0 cuts without replay. Actual `994493f99`/508 loading passes in
16.131328344 s/source0, separate from private cuts and the generic load above.
Unary-over-constant/arithmetic and wider histories remain separate at this cut.
[Review](coverage/semantics/string-offset-request-base-arithmetic-special-concat-leading-key-review.json).

Initially undefined REQUEST-base reads now release to NULL through finite prior
stacks of absent or valid non-NUL INTERNED callbacks at arbitrary integer masks.
The current callback remains valid non-NUL INTERNED; every other source, primitive
current-key, live-cell, pool, task, heap and 21-field provider gate stays closed.
Two exact SL originals retain `ede31907f`/508 and their native observations once;
author SL170/83-derived and peer SL193/90-derived retain `7cc7bec39` separately.
The actual `994493f99`/508 load passes in 16.131328344 s with zero source credit.
Preserved AL timeouts and the corrected NUL fixture compiler failure keep zero
credit. Wider providers/callbacks, abrupt histories and held lanes remain partial.
[Review](coverage/semantics/string-offset-request-release-prior-cv-review.json).

The same closed release now admits live HCELLs with authenticated non-NUL REQUEST
identities distinct from the selected header, including equal-byte bystanders.
Only the cell classifier gains that identity parameter; every other provider,
current-key, callback, pool and state-frontier guard remains literal. Source2 at
`7fd3bc65f`/508 reuses native2 once; author SL217/119-derived at `11c7f6a60` and
independent SL151/48-derived at `7fd3bc65f` retain separate source0 cuts. The first
source timeout stays zero; one affected retry and the other source's first attempt
pass at the original60/80 caps. Wider providers and held lanes remain partial.
[Review](coverage/semantics/string-offset-request-release-distinct-cv-review.json).

Public by-reference `offsetGet(): int` now enters the existing typed CV return
verifier. Two exact production-SL originals cover integer CV/reference returns,
weak numeric-string success and weak/strict TypeErrors. The returned alias has no
persistent return-type constraint. One source-reached AL fixture passes 89
conditions, including same-cell owners from one to two and source/frame/signature refusals;
the original explicit Unsupported retains zero credit. This earlier cut does not
establish other callback/type signatures.
[Review](coverage/semantics/arrayaccess-typed-reference-get-review.json).

Reference Get now admits canonical `int`/`float`/`bool`/`true`/`false`/`null`
return branches and their nullable/union forms through the existing verifier.
Strict integer-to-float promotion writes the actual CV before reference wrapping.
Four exact SL originals retain their first and corrected source cuts; the oversized
weak-source timeout keeps zero credit. The new promotion fixture passes 99 AL
conditions and the affected integer fixture passes 89. Shared checks repeat;
the older integer cut is not renewed.
That Get-only cut does not establish other callback/type signatures or wider
producer/lifetime histories.
[Review](coverage/semantics/arrayaccess-scalar-reference-get-review.json).

Canonical `int`/`float`/`bool`/`true`/`false`/`null` and recursive nullable/union
signatures now admit all four by-reference ArrayAccess callbacks in module319.
Verification and shared-CV writeback precede result wrapping or discard; Exists
tests the result, while Set/Unset discard it or raise the real TypeError. Float Set/Unset
tests use explicit `ReturnTypeWillChange` for tentative void prototypes; bool
Exists matches its prototype. Two exact SL originals at the private `34276fb7f`/498-module
cut and one new 87-condition AL fixture pass. Affected 89/99-condition Get fixtures
pass at this cut with repeated checks; earlier Get cuts remain separate. The two
Unsupported baselines keep zero credit. String/callable/class/container
signatures and wider producer/lifetime contexts remain partial.
[Review](coverage/semantics/arrayaccess-scalar-reference-callbacks-review.json).

Canonical single-void by-reference Set/Unset callbacks match their own prototypes
while retaining BYREF-void compiler deprecations. Bare/fallthrough NULL returns
emit Notice8 even with no result slot. Two production-SL originals at `17f6dad70`/498
match stdout/stderr exactly, including two compiler Deprecated and two runtime
Notice messages each, without suppression. AL73 at `17bae9813` authenticates the
actual method ENDLINE marker, false demand and no return wrapper/allocation/owner
change. The compiler-prefix-then-Unsupported baseline retains zero credit.
Actual `802410d21`/508 loading passes in 15.663896844 s with zero source credit;
private cuts remain separate and establish Set/Unset only. String/callable/class/
container and wider producer/lifetime contexts remain partial.
[Review](coverage/semantics/arrayaccess-void-reference-callbacks-review.json).

Canonical singleton `never` by-reference signatures now admit all four known
ArrayAccess callbacks against their own bool/mixed/void prototypes. Fallthrough
raises the existing method-ENDLINE TypeError before NULL Notice or return wrapping;
ordinary abrupt Error control stays unchanged. These legal BYREF declarations need
no attribute or deprecation suppression. Two exact production-SL originals at
private498, newAL65 and affected scalar-GetAL99 retain separate cuts with repeated
checks; the Unsupported baseline remains source0. Actual `e1025e63c`/508 loading
is separate/source0. Wider signatures, producers and lifetimes remain partial.
[Review](coverage/semantics/arrayaccess-never-reference-callbacks-review.json).

Canonical void signatures now admit Get/Exists as well as Set/Unset in module319.
Get/Exists retain tentative mixed/bool prototype-mismatch deprecations separately
from BYREF-void compiler deprecations. Bare/fallthrough NULL returns emit the
mandatory runtime Notice. The existing
return path materializes a fresh NULL reference even for a discarded outer read;
false Exists skips Get. Two exact SL originals at `931737274`/498 each match eight
diagnostics. New AL93 and affected AL73/99 at `546c70ccc` retain separate repeated
checks, including the exact inactive receiver root-buffer update. The failed
71-condition fixture, projection diagnostic and Unsupported baseline retain zero credit. Actual `b15f494fb`/508
loading passes in 16.007008785 s with zero source credit. Wider signatures,
producers and lifetimes remain partial.
[Review](coverage/semantics/arrayaccess-void-result-callbacks-review.json).

Strict canonical by-reference `offsetGet(): string` now has method-aware
admission. The existing verifier preserves an ordinary local interned non-NUL
string and returns the same CV cell by reference, without a persistent property-
type constraint. Strict integer/bool returns throw before callback-result owner
acquisition; a local alias may already mark the cell. Two exact originals at
`ef2d54b5d`/498 reuse native originals once. AL91 at `41c5da4c4`/498 checks actual
one-to-two ownership and unchanged value/storage, source/frame and admission
boundaries. The Unsupported baseline stays0. Actual `fbf190fc4`/508 loading
passes in 15.992135756 s with zero source credit. Weak/Stringable conversion,
nullable/union strings, other string callbacks and wider producer/provider/
lifetime histories remain partial.
[Review](coverage/semantics/arrayaccess-string-reference-get-review.json).

Terminal undeclared nonempty literal-property `isset` now admits the existing
same-owner untyped by-value Get alongside typed-bool Isset on an emitted external
CV. Only Isset executes; its Boolean, original name and receiver survive callback
writes or caller-CV removal. New module407 absence proofs preserve actual Isset/~Empty
and existing method, Some/noGet/PREP/result/root rules. Three distinct source
comparisons pass at separate private507 SL cuts. Author AL92/43 and peer AL84/25
retain separate source0 cuts, with no unique aggregate. Original failed82/25 and
one finite owner checkpoint28 stay0; only fixture stage and Empty-tail assertions
needed correction. Actual `c4b3d36dd`/508 loading passes in 15.541147190 s/source0;
the pre-run recorder path failure is separately0. Wider names, receivers,
signatures and lifetimes remain partial.
[Review](coverage/semantics/anonymous-missing-isset-pair-review.json).

Terminal missing Isset also accepts initialized nonempty plain non-NUL string-CV
names with the same-owner admitted Get or no Get. The existing selector capture
and saved frame/target/result equality retain the original name and receiver
through both CV rebindings; Get never runs. Three distinct SL originals reuse
native observations once at private507. Author AL88/88 and peer AL110 retain
separate source0 cuts with no unique aggregate; Unsupported baselines stay0.
Actual `73c1cec57`/508 loading passes in 15.697317981 s/source0. Empty names and wider
producers, signatures and lifetimes remain partial.
[Review](coverage/semantics/anonymous-missing-isset-cv-pair-review.json).

Terminal undeclared-property `empty` admits nonempty names from literals or
initialized plain non-NUL string CVs with the existing typed-bool Isset and
same-owner untyped by-value Get/noGet contracts. False skips Get; true uses its
result while retaining the original name and receiver through callback CV
rebindings. The CV-name route retains the known-integer Get result bound.
Without Get, either callback Boolean yields empty true. Actual consumer flags,
declared-property identity and one-receiver ownership remain unchanged. Four
literal-name originals retain their earlier source/state cuts. Three new CV-name
SL originals at private507 reuse native observations once; separate author AL87/99
and peer AL86 first-pass cuts retain source0 without a unique aggregate. Baseline
Unsupported stays0. Actual `05e6faeae`/508 combined loading passes in 15.602213624 s,
source0. Empty names and wider producers, signatures and lifetimes remain partial.
[Literal review](coverage/semantics/anonymous-missing-empty-review.json),
[CV-name review](coverage/semantics/anonymous-missing-empty-cv-pair-review.json).

Terminal binary `??` now admits a genuine undeclared nonempty literal property
on an external non-This CV. Existing typed-bool Isset and same-owner untyped
by-value Get preserve the selected name and receiver through callbacks. False
skips Get; zero suppresses the fallback, while NULL/noGet uses the unchanged
ordinary RHS continuation. IN_ISSET ends before Get; the existing RESULT owner
retires before fallback. The binary-parent fence leaves missing `??=` Unsupported.
Five distinct production-SL originals at private507, separate author AL71/94/94/86,
genuine `??=` refusal AL29 and peer AL93 pass. Affected declared-property strict-SL
215/146 retain their own cuts; the failed peer93 and finite checkpoint14 remain0.
Actual `f4f667702`/508 loading is separate/source0. Wider names, receivers, methods
and lifetimes remain partial.
[Review](coverage/semantics/anonymous-missing-coalesce-review.json).

Terminal binary `??` also accepts undeclared nonempty names from initialized
plain non-NUL string CVs on emitted external non-This receiver CVs. Existing
typed-bool Isset uses the admitted same-owner untyped by-value Get at the PINT
result bound, or noGet. Fresh absence and saved name/receiver history
survive both CV rebindings. False skips Get; zero skips fallback; noGet uses the
ordinary RHS. IN_ISSET clears before Get and the RESULT owner retires before
fallback. Three exact private507 SL originals reuse native observations once.
Separate author AL87/100, original `??=` refusal30 and peerAL93 retain source0,
without a unique aggregate. Failed86/99 and the peer recorder false0 remain; the
corrected peer source agreement uses original raw only. Actual `27ba0d582`/508
loading passes in 15.045074170 s/source0. Empty names, missing `??=`, wider
results/producers/receivers/signatures/lifetimes and held lanes remain partial.
[Review](coverage/semantics/anonymous-missing-coalesce-cv-pair-review.json).

Terminal missing Isset, Empty and binary `??` also admit empty initialized plain
string-CV names on the existing external non-This receiver. Five guard alternatives
preserve nonempty literal names, genuine absence, saved name/receiver history,
typed-bool Isset and PINT Get/noGet bounds. Missing `??=` stays Unsupported. Three
distinct private507 SL originals reuse native observations once. Fixture-SL49/93
and precodeSL34 retain separate source0 cuts; the notation diagnostic and AL300
timeout retain0, with no AL credit or unique aggregate. Actual `cd577eda4`/508
loading passes in15.482561237 s/source0. Wider names, receivers, signatures, Get
results and lifetimes remain partial.
[Review](coverage/semantics/anonymous-missing-empty-name-review.json).

Canonical string Get name reception on named parentless owners now composes
with admitted Isset/Empty, binary `??`, literal getter-only skip and existing
private `??=`. Existing
literal result domains, CV integer bounds, generic Get and missing-`??=` gates
remain. Four source agreements retain separate private507 cuts with native
observations reused once. Fixture SL69/101 and precode36 retain separate source0
cuts without AL or unique-count credit; the current joined load above is
separate/source0. Wider owners, signatures, results and lifetimes remain partial.
[Review](coverage/semantics/magic-property-typed-get-review.json).

Canonical required string Get-name headers without a declared return type also
compile on source-validated parentless anonymous owners with class-free bodies.
Factory helpers and generic Get/missing-`??=` gates remain unchanged. Two sources
retain separate private507 cuts with native reuse; fixture SL53/SL102 and precode
SL31 remain separate/source0 without AL or aggregate credit. Original precode and
notation failures retain0. Actual `172232d4d`/508 loading passes in14.952704033 s/
source0. Wider owners, headers, results and lifetimes remain partial.
[Review](coverage/semantics/anonymous-typed-get-member-review.json).

Named parentless Get now admits required nullable-string, well-formed
string-bearing-union and mixed name headers through raw AST normalization to the
real TYPE in defining ENV/class/member/file/parameter context. Two normal
private507 originals reuse natives once: numeric12 executes only union/mixed,
while the nullable original uses an empty name; nullable numeric12 is fixture
evidence. Separate SL98/SL135 and pre48 remain source0 without AL or an aggregate.
Two preframework launcher failures retain0. Actual `94509c433`/508 loading passes
in16.590478442 s/source0. Wider anonymous headers, generic Get/factories/results/
PREP/roots and missing-`??=` keep their bounds.
[Review](coverage/semantics/magic-property-string-compatible-get-review.json).

Parentless anonymous Get also accepts those required nullable-string,
well-formed string-bearing-union and mixed name headers with class-free
bodies. Raw module383 candidates retain normalized141/408 signature and
defining-context checks. Two exact originals reuse native observations once
at separate private507 cuts; author SL106, peer SL141 and provisional
precode87 remain separate with source0, without AL or aggregate credit.
Actual `ccc93ac38` static acceptance and the joined `972cd9882`/508
load (`2f738c90`, source0) remain separate. Generic380, factories, PREP,
roots, results and missing-`??=` retain their bounds; wider consumers and
lifetimes remain partial.
[Review](coverage/semantics/anonymous-string-compatible-get-review.json).

Ordinary missing reads now accept an own parentless by-value canonical-string
Get with no return declaration on an emitted external non-This CV. Existing
literal/plain string-CV names retain strict-identity-left or discarded source
and exact saved-tail checks; new results remain known integers. Typed entry
uses the authenticated implicit-call context and retains the existing RESULT
receiver hold. Two originals reuse native observations once at separate
private507 cuts; author SL76, peer SL111 and precode54/54 retain separate
source0 cuts without AL or aggregate credit. Failures remain preserved.
Actual `0aea1af1c`/508 and the `fa35de77` load (source0) remain separate.
Wider consumers, signatures, results, receivers and lifetimes stay partial.
[Review](coverage/semantics/magic-property-string-read-get-review.json).

Those canonical-string Get reads also admit direct singleton Echo through the raw
indexed property child and exact saved Echo origin/same-site AT/EMIT line. Header,
owner, missing-property, integer-result and receiver ownership bounds remain.
Two originals reuse native observations once at separate private507 source cuts;
author SL67, peer SL133 and precode SL49 retain separate source0 cuts without AL
or aggregate credit. Actual `43b7c5e35`/508 and its `1650c1a0` load
(15.246240716 s, source0) remain separate. Comma echo, wider consumers, signatures,
results, receivers and lifetimes remain partial.
[Review](coverage/semantics/magic-property-string-echo-get-review.json).

Those ordinary reads also accept required nullable-string, well-formed
string-bearing-union and mixed name headers through existing raw normalization
in the defining context. An explicit nonempty TYPE preserves genuine untyped Get
and its noninteger results; consumer, integer-result and receiver bounds remain.
Two new originals rotate headers across the three consumers at separate private507
production-SL cuts, reusing native observations once. Author SL107, peer SL142,
genuine-untyped SL40 and precode SL63/58 retain separate source0 cuts, without AL,
aggregate or cross-product credit. Actual `58e20adf7` and combined Get/REF30
508-module SL loading (`2e87618f`, 15.759459066 s, quiet/stable/reaped/source0)
remain separate. Wider consumers, results, receivers and lifetimes stay partial.
[Review](coverage/semantics/magic-property-compatible-read-get-review.json).

Those ordinary typed-name reads also admit known null, Boolean, finite binary64
and authenticated non-NUL INTERNED string results. Existing integer, genuine
untyped CV-name and declared-property branches remain unchanged; returned
primitives add no heap edges. Two production-SL507 originals reuse native
observations once. Separate author SL85, peer SL109, genuine-untyped refusal SL32
and precode SL46/47 retain their cuts/source0; two peer pre-main fixture failures
remain zero, without AL, aggregate or cross-product credit. Actual `47dc49ad9`
and one composed 508-module SL load (`b36e2a45`, 15.566676035 s, quiet/stable/reaped,
source0) stay separate. Return declarations, wider values, receivers and lifetimes
remain partial.
[Review](coverage/semantics/magic-property-primitive-read-get-review.json).

Those ordinary typed-name reads also admit canonical int/float/bool/string/mixed
return declarations through raw defining-context RETURNS and the existing
strictness verifier before Get RESULT. Tested weak literal conversions add no
source-store writes. Narrow bare-return diagnostics and anonymous Get error names
match native. Two normal production-SL507 originals reuse native observations
once. Diagnostic originals/control retain their separate observations; author
SL134/36 and peer SL103 are separate source0 cuts. Failures and corrections stay
explicit, without aggregate renewal. Actual `a2907470c`/508 and joined `9db1e93a` (15.388192947 s, quiet/stable/
reaped) remain separate with source0. Nullable/union/void/never returns and wider
values, producers, receivers and lifetimes stay partial.
[Review](coverage/semantics/magic-property-scalar-return-get-review.json).

Those reads also admit canonical ?int/?float/?bool/?string return syntax through
matching raw nullable nodes, normalized [T,null] and defining context. Equivalent
named T|null declaration types can be admitted, while raw union Get execution
stays Unsupported before the body. Two production-SL507 originals reuse native once.
Author SL125/19, peer SL86 and affected old scalar SL134 retain separate source0
cuts; the union refusal is not native agreement and historical SL134/36 stay
separate. New source/state checks pass first try. Actual `532c971b2`/508 and joined
`18abf3d4` (15.680194817 s, quiet/stable/reaped) remain separate with source0.
Raw unions, wider return forms, producers and lifetimes remain partial.
[Review](coverage/semantics/magic-property-nullable-return-get-review.json).

Quiet Empty/coalesce Get now admits canonical void/never declarations.
Bare/fallthrough void returns NULL; implicit never preserves the native method
kind, anonymous C-string name and method-end line. Explicit supplied throws and
exit(13) skip fallback and caller assignment while preserving receiver cleanup.
Six new source originals agree with native observations run once; fixture SL
84/78 and peer 105/105 retain separate source-zero cuts. The actual production
SL load of 508 modules at 9de26d0eb passes in 15.932177914 s under 60 seconds,
separately/source0. One old never helper-query case flips three negations
without renewing its 126-condition cut. Wider quiet headers, producers and
lifetimes remain partial; held boundaries stay unchanged.
[Quiet void/never Get review](coverage/semantics/magic-property-void-never-quiet-get-review.json).

Quiet completed POWER also supplies genuine NaN VALUE through actual own/child
source/read/precision facts, genuine scalar children, quiet coercions and exact
`POWERDONE`/full-state results. Four originals reuse native observations once;
pre659, author858/105-derived, independent2002/497-derived and affected14/14 keep
separate source-zero cuts. MAIN `1d179a605` and its `9bc7dcad3` SL508 load
(15.438906230964s/source0) remain separate. NonNaN power BYTE, GENERAL, Deprecated,
NaN BYTE, FLOAT NOT, wider producers/owners/lifetimes and held lanes stay partial.
[Completed-power NaN review](coverage/semantics/string-offset-request-base-power-nan-special-concat-leading-key-review.json).

Quiet completed POWER nonNaN FLOAT results also retain exact BYTE at captured
precision through actual own/child facts, scalar VALUE, quiet coercions and full
state/result checks. Four originals reuse native observations once. Pre-v2
remains false: first109/151/136 pass, fourth204 is corrected separately; no passing
600 aggregate is claimed. Author799/105-derived, independent1675/542-derived and
affected18/26 retain separate source-zero cuts. Actual `c68397001` has one combined
SL508 load passing15.982042335905135s/source0. GENERAL, Deprecated, NaN BYTE,
wider producers/owners/lifetimes and held lanes remain partial.
[Completed-power FLOAT review](coverage/semantics/string-offset-request-base-power-float-special-concat-leading-key-review.json).

Quiet completed scalar-coerced POWER also supplies exact PINT BYTE through
genuine children, equal captured precisions, quiet NINT coercions and unchanged
full-state results. Native4 once/source4 and separate pre458, author657/105-derived,
peer1570/557-derived and affected90/30 cuts pass. MAIN `7da259b5e` has one combined
SL508 load15.68941183295101s/source0; no historical campaign or aggregate is renewed.
[Review](coverage/semantics/string-offset-request-base-coercive-integer-power-special-concat-leading-key-review.json).

Current implementation/reviewer pairs work in private trees; their changes remain
unaccepted until integrated.

| Track | Current work and private trees |
| --- | --- |
| Classes | Live array/object Get results, canonical-int, Boolean, FLOAT, string and NULL quiet returns, nullable scalar and scalar-union quiet headers, canonical void/never and mixed quiet Get declarations and supported unselected typed companions are integrated. Complete raw method/source proof retains normalized headers, strictness and owner guards. String payloads retain byte/carrier authority and authenticated non-NUL REQUEST bounds. NaN Empty warning reentry admits authenticated literal/string-CV terminal Isset, including empty names. Literal-name Empty results preserve payload-before-receiver cleanup. Canonical array/object quiet Get headers and bounded live array/ordinary-object CV Empty results preserve saved names, raw source proof and separate value/receiver cleanup; binary CV-name coalesce also transfers live arrays and ordinary objects through receiver retirement with saved names and separate result/receiver owners. Private CV-name ??= now transfers admitted live array/object Get results through exact assignment-target and named integer RHS authority, preserving saved names, COW, self-results and receiver/payload exception replacement. Authenticated live enum-case singletons also cross quiet CV-name binary ??/private ??= and literal/CV Empty through separate cache/result/receiver ownership. Live raw empty/singleton WeakMap Get results also cross quiet CV binary ??, private ??= and Empty with separate map/value/receiver owners and existing key notification ([WeakMap review](coverage/semantics/magic-property-weakmap-quiet-get-review.json)). Initialized WeakReference Get wrappers also cross those quiet consumers with live or retired borrowed targets; Empty retires its wrapper result before receiver cleanup ([WeakReference review](coverage/semantics/magic-property-weakreference-quiet-get-review.json)). Authentic unscoped function-literal and Arrow Closure Get results cross quiet CV ??/private ??=/Empty with complete captures and authenticated original-or-clone shared cache history; raw same-origin ancestor stamps remain nonowning, Arrow templates retain actual BODY/marker/IMPLICIT-name proof, and Empty releases its result owner before its receiver ([literal Closure review](coverage/semantics/magic-property-realclosure-quiet-get-review.json), [Arrow review](coverage/semantics/magic-property-arrow-quiet-get-review.json), [clone review](coverage/semantics/magic-property-clone-quiet-get-review.json)). Unscoped USER named FCC results and their authenticated shared-cache clones also cross these quiet consumers through the explicit original guard or strictly descending raw same-origin cache ancestry and live-function authority; named wrapper retirement leaves function statics rooted independently, and literal Empty authenticates the actual result ID ([named FCC review](coverage/semantics/magic-property-namedclosure-quiet-get-review.json)). [Named FCC clone review](coverage/semantics/magic-property-namedclosure-clone-quiet-get-review.json). Missing-property ??=, other internal CV kinds, wider returns, Echo and lifetimes remain partial. |
| Compiler/hooks | Checked header presence, implicit class/trait block/short SET and public untyped backed GET/SET pairs across block/short bodies and initialized/omitted defaults are integrated. Untyped backed GET/SET pairs also import from one raw direct trait into a parentless class or one with a genuine ordinary source parent whose complete layout is plain and lacks the hook name. Repeated direct uses may resolve to that same single fetched exporter, including lexical namespace aliases. On this trait route, a short GET may omit backing access when its block SET supplies the backing. Untyped direct trait pairs also admit automatic short-SET backing when neither hook accesses the property directly. Block or short GET retain exact raw/imported source, RHS/CODE/line and Param authority. Exact raw/imported origins, no exporter uses or adaptations, first matching NAME row and actual Param/body/source-parent authority remain required; wider traits, nonpublic/modifier/virtual/byref pairs and lifetimes remain partial. Existing DIRECT storage and cleanup remain. Own public parentless untyped class pairs also admit a short GET without backing access when a genuine block SET supplies backing, with implicit or required actual untyped parameters. Raw Hook/Param/source/CODE/line, physical DIRECT storage and owner/cleanup bounds remain; wider class/trait/modifier/virtual/byref forms stay partial. Own public parentless untyped pairs also admit automatic short-SET backing with block or short GET even when neither hook uses the property directly. Implicit and required actual untyped SET parameters keep their source/header/Param authority. Own public untyped backed pairs also accept a genuine ordinary source parent whose complete plain layout lacks the hook name, retaining canonical headers/SOURCE_PARENT/raw Hook/Param/CODE/line and existing storage/cleanup ([parented-pair review](coverage/semantics/deprecated-reference-object-untyped-parented-class-pair-review.json)). Own backed pairs also override same-name ordinary public fields on a parentless plain source parent, retaining raw own authority and child declaration-order live storage ([same-name parent review](coverage/semantics/deprecated-reference-object-untyped-same-name-parent-class-pair-review.json)). Wider parents/owners/modifiers/signatures, virtual/byref pairs and lifetimes stay partial. |
| Enums/int defaults | Selected typed FLOAT/default-cast and numeric-comparison behavior retains stored-PINT, declaration-ENV and owner guards. Ordinary named exact-int defaults retain source/declaration ENV and Shared-cache authority. Resolved case-sensitive PHP_INT_MAX/MIN/SIZE and PHP_FLOAT_DIG supply deferred PINTs, while PHP_FLOAT_EPSILON/MAX/MIN supply fixed finite PFLOAT values; authenticated names retain their types, while arithmetic and casts follow existing rules. Quiet in-range NINT truth retains proper selected descent. Raw deferred FLOATs cache before private conversion; handler throws/reentry preserve cleanup and raw cache bits. Overflow retains its raw PFLOAT tag through ordinary parameter checking; only nonfitting results raise later TypeErrors. Selected Numeric NINT leaves also retain integer values through full/shorthand ternary, null-left coalesce and existing arithmetic parents. Literal-Boolean full ternaries also admit compiler-pruned skipped names through exact condition pools and a unique proper selected-child redirect, retaining condition/selected bindings and whole-tree source/ENV/no-DIM/cache authority. Quiet computed Boolean conditions also authenticate exact raw PBOOL pools with recursive condition/selected bindings and unique proper-child redirects. Decisive OR/AND conditions authenticate only the proper left child through pure truth and matching own/left raw Boolean pools, retaining source/no-DIM/ENV/cache and outer ternary authority. Quiet Numeric-only signed64 integers also retain identity through explicit int casts and nonnull-left coalesce, including zero ([numeric-cast review](coverage/semantics/numeric-integer-cast-default-reception-review.json)). Pinned release-component constants also supply deferred integers 8/5/10/80510 through the same guarded receipt ([version review](coverage/semantics/version-integer-default-reception-review.json)). Registered nondeprecated E_* values, including E_ALL=30719, supply guarded deferred defaults ([diagnostic review](coverage/semantics/diagnostic-integer-default-reception-review.json)); Numeric-only signed64 AND/OR/XOR/NOT compose through the same source/ENV/no-DIM/cache and owner guards ([bitwise review](coverage/semantics/numeric-bitwise-default-reception-review.json)). Other pruned syntax, unresolved names/namespaces, private/Generator and wider producers/entries/lifetimes remain partial. |
| References | REQUEST DIRECT fields, scalar ALIAS fields, finite object-free DIRECT/ALIAS array fields and finite acyclic quiet stdClass paths are integrated. Mixed object/array fields retain separate ancestor stacks, shared siblings, real edges and COW/cleanup. Completed producers with multiple literal ordinary CV actuals and fixed required untyped formals admit canonical array/int/float/bool/string return declarations. Raw/normalized return proof and actual verification retain the existing scalar, authenticated non-NUL INTERNED/REQUEST-string and finite array/quiet stdClass payload bounds; frame retirement precedes private Notice-cell creation, and the last compiled CV supplies its line. Raw ?array, ordered array\|null/null\|array and canonical ?int/?float/?bool/?string retain exact pointwise normalized types; callee-strict return verification and producer-frame retirement precede private Notice cells. Explicit scalar\|null/null\|scalar return unions retain exact ordered raw/normalized authority. Matching fixed required untyped, array or canonical int/float/bool/string formals retain pointwise raw/normalized type/BYREF authority and caller-strict reception; BYVAL coercion preserves caller values, while ordinary BYREF coercion changes the shared cell without a persistent parameter constraint. Matching fixed required nullable array/int/float/bool/string formals also retain pointwise raw/normalized/BYREF proof and caller-strict reception ([nullable-formal review](coverage/semantics/multi-cv-nullable-formal-producer-reference-notice-review.json)). Singleton CV producers also admit matching scalar/nullable formals and nullable scalar/ordered scalar-null returns ([formal review](coverage/semantics/singleton-cv-typed-formal-producer-reference-notice-review.json), [return review](coverage/semantics/singleton-cv-nullable-scalar-return-producer-reference-notice-review.json)). Existing return/frame-retirement and ownership bounds remain. Wider unions/formal types/defaults/variadics/attributes and actual/source/backing/GC/lifetime contexts remain partial; Owned-NUL remains held. Typed property-sourced descendants within object paths remain partial. |
| String offsets | Exact PINT bitwise/MOD/shift/power/equality, quiet logical forms, raw-string and mixed numeric/scalar comparisons, strict NaN identity, nonNaN FLOAT ConstFetch BYTE and genuine quiet arithmetic/unary NaN VALUE, including numeric NaN children in ADD/SUBTRACT/MULTIPLY/DIVIDE, are integrated. Actual source/read/byte/precision facts and skipped-RHS behavior remain. Quiet BOOL/NULL/raw numeric-string children now share exact scalar-identity and quiet-coercion proofs for these arithmetic NaN values. Quiet completed POWER also supplies genuine NaN VALUE through exact scalar-child, source/read/precision, quiet-coercion and full-state POWERDONE facts. Quiet completed nonNaN FLOAT POWER BYTE retains exact source/read/precision, scalar child identity, quiet full-state POWERDONE and pure formatting. Quiet completed scalar-coerced POWER also supplies exact PINT BYTE through genuine scalar children, equal captured precisions, quiet NINT coercions and unchanged full-state results. Quiet runtime FLOAT NOT keys retain actual nonconstant CODE/read-eps and quiet FLOAT truth proofs with real CONCAT carriers ([runtime review](coverage/semantics/string-offset-request-base-float-boolnot-runtime-review.json)). Quiet double/triple NOT retains typed PFLOAT/PBOOL links under emitted source/CODE/read-eps, equal precision and full-state truth ([nested review](coverage/semantics/string-offset-request-base-nested-float-boolnot-runtime-review.json)). GENERAL, Deprecated, NaN BYTE, warningful NaN truth and wider producers/ownership/lifetimes remain partial. |
| Callback ownership | Closed normal selected-callback reads retain captured KEYREF, exact callback ownership and the 21-field frontier. Plain CVs follow admitted quiet values or non-NUL INTERNED/REQUEST text in ordinary or later-marked current cells. Under captured KEYREFfalse, actual current ordinary or valid marked cells admit non-NUL raw PSTRING keys; captured KEYREFtrue follows the saved live marked KEYCELL despite current-name replacement or removal. Marked-current reads retain source/static-CV/nonblocked lookup, current live/pruned cell, full heap, backing/released, provider ownership and range proofs; REQUEST retains its exact selected header and owner. Initial references retain the live old-wrapper proof independently of current names/values. Ordinary current raw keys also complete after callback-owner loss when the unchanged provider authenticates the exact REQUEST base in its original cell or an admitted real ENV retainer. Valid marked-current raw keys with captured KEYREFfalse also share the provider-backed owner-loss route, retaining pruned-cell, released/backing, source/full-heap and closed21 proofs. Captured initial-reference KEYREFtrue raw keys also complete after callback-owner loss through that same exact REQUEST-base provider and saved live marked KEYCELL, independently of current-name replacement/removal. Literal non-NUL INTERNED bases also admit late raw PSTRING keys through authenticated known-source/provider and current-or-saved-cell proofs. Initial valid non-NUL raw CV leading-integer keys on authenticated literal INTERNED bases retain frozen bytes/index through normal Warning rebinding or cell retirement under actual compiled-base source proof ([leading-key review](coverage/semantics/string-offset-initial-raw-leading-key-review.json)). Ordinary initialized INTERNED base CVs also preserve captured header/index through normal Warning rebinding or borrowed-cell removal ([CV-base review](coverage/semantics/string-offset-variable-base-initial-raw-leading-key-review.json)). Genuine initial-reference INTERNED base CVs share that captured header/index path through normal Warnings ([reference-base review](coverage/semantics/string-offset-reference-base-initial-raw-leading-key-review.json)). Quiet full ternaries with literal Boolean conditions and raw string arms also retain the selected non-NUL INTERNED header/index through returning Warnings, authenticating both arms and the condition ([conditional-base review](coverage/semantics/string-offset-conditional-base-initial-raw-leading-key-review.json)). Raw string-literal shorthand and full ternaries also retain their selected INTERNED header/index through the same returning Warning route ([shorthand](coverage/semantics/string-offset-shorthand-base-initial-raw-leading-key-review.json), [string-condition](coverage/semantics/string-offset-string-conditional-base-initial-raw-leading-key-review.json)). Literal string/null coalesce bases also retain their nullness-selected header/index through that returning Warning route ([coalesce review](coverage/semantics/string-offset-coalesce-base-initial-raw-leading-key-review.json)). Literal integer full ternaries retain that truth-selected header/index through the same returning Warning route ([integer-condition review](coverage/semantics/string-offset-integer-conditional-base-initial-raw-leading-key-review.json)). Finite raw float conditions retain that header/index through exact raw bits and finite decode ([float-condition review](coverage/semantics/string-offset-float-conditional-base-initial-raw-leading-key-review.json)). Other initial raw acquisition, selected NUL, wider runtime/REQUEST bases, zero-owner REQUEST raw release, abrupt and wider histories remain partial. |
| ArrayAccess | Typed scalar/nullable/union callbacks and undefined-offset sequencing with current keys, quiet marked primitive/string cells and bounded DIRECT/ALIAS array children are published. Current marked arrays use that same finite entry domain; wider signatures, payloads and lifetimes remain partial. |
| Output | Ordered CONST/CV MOD conversions, precision/range/NaN notices, sole leading-number or FLOAT-range Warning under an unrelated Deprecated handler and sole precision Deprecated under an unrelated Warning handler are integrated through FINAL. Two quiet staged MOD conversions also preserve the zero-divisor Error with an eligible Warning or Deprecated handler left uncalled. Quiet-left RHS singleton and same-class both-operand Warning/Deprecated conversions cross FINAL while the opposite eligible handler stays uncalled. Exact caches, fresh saved-left and current RHS records, canonical pointers, intrinsic notice vectors and null scratch remain required; lifecycle checks cover real zero/one/two-cell retirement, including two same-CV notices with one retired cell; wider handler/operand/lifetime forms and OB31 stay partial. Selected named Warning handlers with two required untyped by-value formals and a literal echo/implicit NULL body also preserve the MOD zero Error through FINAL in four quiet-left/noisy-RHS and four noisy-left/quiet-RHS originals at separate cuts; exact source/cache/pointer and real cell-retirement guards remain required, while wider handler/retarget histories remain partial ([quiet-left review](coverage/semantics/output-final-selected-warning-modulo-error-review.json), [noisy-left review](coverage/semantics/output-final-selected-left-warning-modulo-error-review.json)). Four further CONST/CV originals complete two calls to that same handler, one per MOD operand, retiring four distinct formal cells with `AHH` buffered before the zero Error; the existing guards and wider limits remain ([both-Warning review](coverage/semantics/output-final-selected-both-warning-modulo-error-review.json)). Selected LEFT precision Deprecated handlers retire their two formal cells before fresh quiet MOD-zero RHS and FINAL Error ([left-Deprecated review](coverage/semantics/output-final-selected-left-deprecated-modulo-error-review.json)). Selected RHS/both precision Deprecated callbacks retire two/four formal cells before FINAL MOD-zero Error, retaining full storage and AH/AHH ([precision review](coverage/semantics/output-final-selected-precision-modulo-error-review.json)). |
| ATTR87 (held) | Stopped after repeated generic service flags; no restart or reroute. |
| GC87 (held) | Quiet unique-outer nested-write assessment stopped after recurrent generic service flags; source-only notes preserved, no runtime edits or active jobs. |

Keep V110, GC35, I106, COMP123 and the paused boundaries below held. Preserve
private drafts and external raw evidence; [ARTIFACTS](docs/ARTIFACTS.md) records
recovery locations.
I140 and GC84 remain unstarted pending exact user scope.

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
