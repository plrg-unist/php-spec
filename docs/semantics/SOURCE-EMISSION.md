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
name CVs; conversion callbacks and wider producers remain required.

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
renewing earlier cuts. User Stringable
and warning-producing name conversions keep their existing Unsupported boundaries;
wider names, emissions and providers remain required.
