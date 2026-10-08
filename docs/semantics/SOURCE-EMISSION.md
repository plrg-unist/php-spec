# Dynamic-source first emitted work

For the selected nontrivial child programs, PHP 8.5.10 retires an owned include
operand after compilation but before the child's first instruction. A throwing
destructor reports that instruction's line even though the child body never runs.

Module 314 adds three nonconstant ECHO cases to 298's accepted constant/assignment
selection: an ordinary CV emits ECHO at line 5; a literal instance-property read
after an ordinary CV emits FETCH_OBJ_R at property-name line 6; a resolved named
nonbuiltin call receiver with no arguments or namespace fallback emits INIT at
line 5 before the property fetch. Authored CODEEXPR/CODENAME rows certify the
occurrences. The existing completed-image, source-entry suffix and exit checks
authenticate their use; AST start lines alone do not choose them.

The rules follow vendored `zend_compile_echo`, `zend_try_compile_cv`,
`zend_delayed_compile_prop` and `zend_compile_call`. Ordinary CV classification
excludes `this`, all auto-globals and `http_response_header`. Dynamic property
names, builtin/argument receivers and wider expressions retain the earlier
fallback and remain required first-emission work.

The [ledger](../../coverage/semantics/source-expression-emission-review.json)
records an independently accepted isolated 277-module cut: strict compilation,
three exact normal source agreements, 57 genuine entry/image/heap/public premises and 72
matching-compiler-image shape premises. The two original fixture-only stops
remain zero credit. Relocated tests prepare the same 57/72 with zero applications.

The isolated 277-module cut is reproduced using the ledger's
explicit `--semantic-root .tools/source-stringable-expression-emission-314`;
canonical module 314 is installed after Fiber308 on the 286-module parent. One
fresh nested-Generator property source and 70 genuine entry/retirement/public
premises pass there, including heap-identical receiver/image/owner/suffix
forgeries. The maintained generator case prepares70 with zero applications.
Earlier literal, retirement and Generator-composition cuts keep their original
identities. Broader emission, complete core and the final combined, fresh offline
rebuild remain required.

Module316 adds literal core auto-globals except `GLOBALS`: direct ECHO emits
FETCH_R at the variable line, and a literal property receiver emits that same
fetch before the property instruction. Both expression records retain their
real lines and the source-entry hook authenticates the complete image.
The [separate ledger](../../coverage/semantics/source-autoglobal-emission-review.json)
records isolated278 source2 with explicit request facts, independent79 genuine
MAIN entry/retirement/heap/image/resumption premises, computed-name11 and a new
maintained72 classification cut. The source cases use the reviewed FD198 request
provider; `scripts/build-request-provider.sh` prepares it. Relocation earns zero
renewed source credit. `GLOBALS`, `this`, `http_response_header`, computed names
and broader producers remain required. A fresh cc397-parent291 readonly-clone
source1 and independent64-premise cut pass separately. The owned include operand
comes from a genuine readonly clone callback; the original seed stays unchanged.
Its maintained relocation earns no refreshed execution credit. The actual293 join
retains returned-child ArrayAccess309 and collector301, passing strict compilation,
the same exact original and47 focused source-retirement/GC/public premises. A
heap-identical DISCARD-only NOGC receipt on genuine SOURCE_ENTER is rejected;
earlier suites keep their original inputs and execution credit.

Module320 adds literal `$GLOBALS` FETCH_GLOBALS selection before direct ECHO or a
literal property read. It authenticates the actual AST, certified variable line
and completed compiler image, without requiring an ordinary global scope marker.
Snapshot creation and later warning/coercion remain runtime work. The
[separate ledger](../../coverage/semantics/source-globals-emission-review.json)
records private294 strict compilation, four exact originals and independent67
premises. Parenthesized property FETCH6/property8 reaches first destruction with
no child snapshot; heap-identical line/scope-marker forgeries reject public entry.
Returning destructors preserve direct Array Warning5 and property-on-array
Warning6. Actual296 retains Arrow311/Fiber313 and passes strict compilation with
independently reviewed introduced compatibility; private source/state cuts keep
their inputs. Relocations earn no renewed credit; broader emissions remain required.

Module323 adds literal `$this` FETCH_THIS before direct ECHO or a literal property
read in separately compiled nested code. Selection authenticates the original AST,
certified receiver/variable line and complete image, independently of runtime
instance existence. The [ledger](../../coverage/semantics/source-this-emission-review.json)
retains private297 strict compilation, four exact originals,70 independent premises
and9 newly affected maintained checks. Genuine method/private scope permits the
later property read; absent-instance retirement precedes Error5. Parenthesized
FETCH6/property8 and same-heap line/scope counterexamples pass. The initial wrong
INSTANCE fixture false has zero accepted credit; previous72 is preparation-only.
Actual303 passes strict compilation while retaining property warnings318, current
default/source/DIR rules and ArrayAccess319. Their introduced paths are independently
reviewed as disjoint here. Private source/state cuts and relocations gain no renewed credit.

Module327 selects INIT for a computed variable name supplied by a resolved
no-argument named user call, before FETCH_R/ECHO or a literal property read.
Original AST, CODENAME without fallback, call/variable CODEEXPR lines and effects
certify selection; helper execution and the returned name remain runtime work.
Its [ledger](../../coverage/semantics/source-computed-emission-review.json) retains
private304 source3 and the corrected missing-name source1 as separate cuts,
plus188 independent premises. INIT6/FETCH6/property8 and later warning6 agree.
The new nonowning NAME_READ_RESULT captures ordinary name/site/line and resumes
with null after a handler defines the target; genuine handler identity and
heap-identical source/line forgeries are checked. Source-keyword293, this,
auto-global/global and no-handler paths retain their protocols. Six excluded
admission shapes, the original missing-name Unsupported and two fixture stops
remain distinct. Actual307 preserves the accepted collector/Generator/ArrayAccess
fields and passes strict compilation. Independent review finds their introduced
selectors disjoint from the name call and warning continuation. Earlier source/state
cuts and relocations gain no renewed execution credit.

Module330 adds the ordinary CV-computed name: the name CV emits no opcode,
so the outer variable FETCH inherits its child's compiler line. Reused314 CV
certification, original nested AST, outer/child CODEEXPR6 and literal property8
identify that occurrence; selection never reads the current name value.
The [ledger](../../coverage/semantics/source-cv-name-emission-review.json) retains
private308 source4 and174 genuine entry/warning/identity/control premises.
Returning retirement changes the live name before lookup; reused327 fixed-null
resume retains later handler name/target writes. The noarg-call control remains
327-positive and330-negative. Actual310 passes strict compilation; independently
reviewed Fiber/collector/constructor parent paths are disjoint here. Earlier cuts
and relocations gain no renewed credit. Module339 below adds undefined ordinary
name CVs;343 below adds ordinary Stringable CVs. Wider producers remain required.

Module333 adds a resolved named user call with one positional ordinary CV
argument as the computed name. INIT6 precedes argument lookup; DO_CALL retains6
while outer FETCH inherits argument7 before property10. Exact NArg/CV AST,
CODENAME, call/argument/outer CODEEXPR and effects certify selection without
reading the live argument. Ordinary by-value CV compilation emits no CODEARG.
The [ledger](../../coverage/semantics/source-call-argument-emission-review.json)
retains private311 source5 and275 independent entry, target-warning and
argument/fallback/admission premises. Existing213 argument and327 computed-name
continuations freeze null while retaining handler writes; the narrow runtime-line
helper preserves noarg/CV defaults. The original parser stop and wrong-CODEARG
trace remain separate with zero affected credit. Actual316 passes strict
compilation with reviewed trait/ArrayAccess/collector compatibility. Earlier
source/state cuts and relocations gain no renewed credit; wider argument forms
and providers remain required.

Module336 adds the corresponding single named ordinary CV argument. Its completed
compiler descriptors select INIT6 before lookup, then known fixed-name FETCH8
before property11; a deferred unknown `Sent` name uses binding/Error7 before the
missing CV can warn. No argument value is read during entry selection. Existing
213 NAMED_SEND and327 computed-name continuations retain handler writes while
resuming the interrupted read with null, including second-slot binding/default holes.
The [ledger](../../coverage/semantics/source-named-argument-emission-review.json)
retains six exact originals and325 independent premises at private317. The failed
fixture conflated deferred VARIABLE metadata8 with compiled binding7; its sole
expectation correction leaves the semantics unchanged and earns no original credit.
Actual320 preserves331/324/335 and passes strict compilation with reviewed disjoint
selectors. Earlier cuts and relocations gain no renewed credit; wider argument forms,
computed producers, first emissions and providers remain required.

Module339 adds the first warning when an ordinary CV supplying a computed name
is undefined. Vendored `zend_fetch_var_address_helper` ignores the return from
`ZVAL_UNDEFINED_OP1` and converts the actual CV pointer after the handler returns.
The source-authenticated, nonowning NAME_CV_READ_RESULT therefore rereads the
restored caller CV quietly before NAME_READ. Handler-created names and empty-name
targets are live; a second missing-target warning still uses327's fixed-null
result. The early327 missing-operand guard keeps the two producers disjoint.
The [ledger](../../coverage/semantics/source-missing-name-cv-review.json) retains
private321 strict compilation, seven exact originals and171 independent premises,
including local/global isolation, handler-false fallback, first-warning throw,
missing/unset cells and include retirement before FETCH6/property8. The original
fixture failures and diagnostic vectors earn zero affected credit. Actual324 over
`6b51f811c` passes strict compilation at `e3d6a7c85`; independent review finds the
introduced bound-Fiber, Generator, collector and array guards compatible without
renewing earlier cuts.343 and350 below add ordinary Stringable/array name CVs.
Wider names, emissions and providers remain required.

Module343 converts Stringable ordinary name CVs through a source-authenticated
implicit call. STRINGIFY_RESULT owns the cast receiver; the new result/ready
metadata does not. Captured returned bytes survive receiver destruction before
lookup of the live caller target. A returning target-warning handler still
resumes327's fixed null. When receiver retirement throws after a successful cast,
FETCH_R performs target lookup before propagating that exception: the default
missing-target warning remains observable, while an eligible registered handler
and its fallback are suppressed. The [ledger](../../coverage/semantics/source-stringable-name-review.json)
retains private325 strict compilation, eight exact originals and134 independent
premises for selected calls, source/frame integrity, alias-delayed destruction,
live targets and pending diagnostics. Fixture phase corrections retain all failed
cuts with zero affected credit. Actual329 passes strict compilation with reviewed
bound-Fiber/trait/collector compatibility, without renewing the private cuts.
350 below adds ordinary array-name warnings. Special targets (`this`/auto-globals)
and wider computed producers remain explicit dependencies.

Module350 stages the array-to-string warning for an ordinary name CV through the
existing error dispatcher. NAME_ARRAY_RESULT carries only its authenticated
source/name/line and owns no array: replacing the CV can retire its children inside
the handler. A normal return fixes the name to `Array`, including replacement with
a Stringable object, then reads the live target. Later missing-target warnings
retain327's fixed null. Vendored `__zval_get_string_func` returns NULL after a
throwing try conversion, so handler/child exceptions abort before FETCH;343's
successful-cast pending-exception path does not apply.
The [ledger](../../coverage/semantics/source-array-name-review.json) retains seven
exact originals and117 independent premises at private331, including local/fallback,
339-created arrays, borrowed child lifetime, source/frame forgeries and retirement
FETCH6. The original fixture elaboration stop has zero evaluation credit. Actual335
over `94e3593e6` passes strict compilation with reviewed current-H, Generator,
property, trait and Fiber compatibility. Relocation and earlier cuts gain no renewed
credit; wider name producers, special forms and emissions remain required.

Module353 selects an ordinary CV-base dimension read with an ordinary CV or plain
int/string literal key, directly under ECHO or before a literal property. Vendored
`zend_delayed_compile_dim` emits FETCH_DIM_R at the key compiler line; the original
AST, exact operand descriptors and completed image authenticate selection without
reading the base/key. Owned include/eval operands retire before that lookup, even
when the live base would be ArrayAccess or retirement throws.
The affected nested property writer follows `zend_delayed_compile_prop`'s writable
DIM mode: direct CV/fixed-global array roots with quiet int/string keys selecting
existing DIRECT object entries separate through ordinary location acquisition.
This can leave the interrupted key-warning read with only its protected old table,
so it returns null; an extra ordinary owner keeps that table readable. A subsequent
literal property-on-null warning carries a nonowning source/name/line certificate
and resumes with fixed null after handler writes. The [ledger](../../coverage/semantics/source-dimension-emission-review.json)
retains seven exact sources and245 independent premises across private336 cuts.
The COW disagreement, missing-producer stop and fixture failures/vector retain
zero affected credit. Actual340 over `ea7cf0a34` passes strict compilation with
reviewed ARG/GEN/Fiber/current-allocation-edge compatibility, without renewing
earlier cuts. Other receiver
modes, missing/alias entries, readonly chains, strings, ArrayAccess and wider
property diagnostics remain on their earlier paths and require further coverage.

Module357 selects the first INIT of a resolved named noarg nonbuiltin key call
without namespace fallback in an ordinary CV-base DIM, under ECHO or before a
literal property. The exact call/outer compiler lines, CODENAME and completed
source image authenticate the key-call origin rather than the later DIM/property.
Owned include/eval operands retire before the key call. Existing DIM_PATH keeps
the CV base borrowed: the callback can define an absent base or replace it and
retire its old child before lookup, while the returned key remains fixed. The
existing missing-key warning resume likewise retains null after handler writes.
The [ledger](../../coverage/semantics/source-call-key-emission-review.json) records
six exact originals and128 independent premises at private341. Actual343 over
`36ccc4520` passes strict compilation with reviewed Generator storage compatibility;
relocation and the earlier cuts gain no renewed credit. Dynamic/builtin/argument/
fallback calls, wider bases/consumers/emissions and providers remain required.

Module361 selects first INIT for a direct ECHO of a named noarg nonbuiltin call
without namespace fallback. Its exact AST/CODENAME/call line and completed image
remain valid when operand retirement installs the function. Declaration history
authenticates that implicit public destructor through the completed parent/child
images, literal first top-level ECHO and fixed noarg named new operand, without a
former-object root. Its local classifier uses the already authenticated images;
the projected history prefix is not recompiled. Returned Stringable TMPVARs and reference wrappers retain their ECHO owner beside the cast pin.
Successful bytes are emitted before freeing that temporary; a reference can
change its referent during the cast, allowing the old receiver to retire first.
If that retirement throws after a successful cast, a pending carrier owns the
reference and Throwable until bytes are emitted, then performs ordinary cleanup
and exception search. Consumed certificates do not reread retired owners.
Borrowed CVs keep their existing release path. The [ledger](../../coverage/semantics/source-direct-call-emission-review.json)
retains ten exact originals and247 independent premises at separate private344
cuts; actual349 over published CALLS362 passes strict compilation without renewing
those cuts. Original early-free/admission failures and the corrected pre-call owner
fixture retain zero affected credit. Dynamic/builtin/wider argument/fallback calls, wider temporary and
borrowed pending-output producers, wider implicit-destructor declaration causes,
and final combined offline validation remain required.

SOURCE365 extends361's ECHO-call certificate to one ordinary positional CV
argument. Exact AST/CODENAME without fallback and separate INIT5/SEND8 descriptors
select first work without reading argument storage. The same hook extends the
literal first-top-level ECHO history classifier under195's preauthenticated images
and admits returned TMPVAR/REFERENCE owners after the argument changes. ECHO's
post-SEND line8 is shared by scheduling, cast authentication and operation-aware
destructor selection/validation. Public pending/active casts authenticate that
separate ECHO line; ordinary call/SEND and property lines keep their defaults.
Returning argument warnings retain fixed null; function/retirement/handler throws
keep their earlier priority. The [ledger](../../coverage/semantics/source-echo-cv-call-review.json)
retains nine exact originals and236 independent premises across private349 cuts.
The original lost-bytes
and line/admission mismatches keep zero affected credit. Actual351 over `760771d9d`
passes strict compilation with reviewed current-parent compatibility. Wider named/unpacked/multiple/effectful
arguments, dynamic/fallback/builtin callees and wider ECHO/source producers remain
required.

The same361 certificate now admits one named ordinary CV argument under direct
ECHO. Its completed CV descriptor certifies SEND/ECHO8 for a known second slot
and7 for a deferred name; CV metadata remains8. INIT5 still selects operand
retirement before binding and demand. No live argument/callee lookup occurs in
that selection or in the existing returned TMPVAR/REFERENCE owner certificates.
Default holes and returning warning handlers preserve fixed null; unknown names
and earlier exceptions retain their priority. Seven exact originals pass at
private351, with204 independent premises. Actual354 over `1c4c8f283` passes
strict compilation with reviewed current-parent compatibility.
The [ledger](../../coverage/semantics/source-echo-named-cv-call-review.json)
retains the original baseline mismatch separately. Wider argument/callee/output
producers and final combined offline validation remain required.
