# Source reference returns after call-result acquisition

This preparation handoff is superseded by [accepted reference returns](SOURCE-REFERENCE-RETURNS.md)
at9959e771, final942/3c331e74. Its933 baseline and original evidence below retain
their historical identities. Continue with the [suppression handoff](RUNTIME-SUPPRESSION-HANDOFF.md).

## Exact starting point

Canonical **933/7391ccdfe25882e01f21d1fe338763d6530cc55865cdf493f6c337677db8d910**
binds codeaf228143, compiler evidenceca6b7044, author971c9550 and
[independent acceptance36224bc3](../../coverage/semantics/call-reference-review.json).
Start from all933 files and modes in the retained publication manifest or
`.tools/runtime7-acquire-candidate/final-inputs.json`; do not copy an old compiler
root wholesale. All acquisition final gates use933. Typed semantic gates retain
926/baa85f57 and their one-test bridge to926/599f3963.

Pinned PHP8.5.10 CLI NTS64: `vendor/php-src` commit
`34308a6666b2d489c509541ea9befea9e2b42348`. The native binary is only the
comparison oracle. Use the retained full primitive requests, raw packets and
process closures; tool failure and Unsupported are never agreement.

## Current runtime interfaces

* `30-storage.watsup`: `pfunction.SIGNATURE` is normalized by existing16/17;
  `DEFAULTS` has retained parameter indexes/origins/stored-or-deferred kind;
  `ENDLINE` is the source end line. `CODE.STRICT` is source-derived lexical state.
  `TYPE_RECEIVE porigin nat` and `TYPE_FALLTHROUGH porigin` are explicit tasks.
* `79-call-frames.watsup`: active tables move into `GLOBALTABLE` or saved frames.
  A frame owns its locals, queued operands, HELD roots and CONTEXT.EXTRA. RESULT
  must already own a returned operand before `$restore_frame` drops callee roots.
  `86-reference-arguments.watsup` preserves actual reference send identity and
  owns temporary call-result dimension slots; reuse this established machinery.
* `80-call-control.watsup`: all argument expressions/sends/binding precede the
  receive loop. Typed parameters receive sequentially, so an earlier type error
  or precision warning occurs before a later missing-argument error. Untyped
  schedules remain unchanged. Calls to registered builtin bodies are still
  explicitly Unsupported; compiler builtin lowering facts do not execute them.
* `91-default-parameters.watsup`: omitted parameters get fresh ordinary cells,
  including by-reference parameters. Stored defaults use normalized float kind
  when an original integer pool value must materialize as float. Deferred
  successful evaluation caches the **uncoerced** value before type verification;
  evaluation failure never caches, but type failure retains an earlier cache.
  DEFAULTCACHE owns values. Value-class trees/scratch are non-owning and follow
  actual constant evaluation, never a second expression evaluator.
* `95-type-values.watsup`: `$typed_conversion` selects exact/mixed matches,
  strict int-to-float, or supported weak scalar conversions; `$typed_apply`
  reuses existing numeric/string helpers. Numeric-string int/float union choice
  uses FULLNUM kind and integer fit. Keep null/true/false diagnostic distinctions.
* `95-typed-calls.watsup`: `$typed_caller_strict` reads immediate saved caller
  function CODE or callsite unit CODE; return checks use callee CODE. Supplied
  by-reference coercions write the shared parameter cell. Current value-return
  verification resolves/detaches before coercion and **must not** alter external
  aliases: retained native examples print `211`. Typed reference returns will
  need their distinct shared-cell path, not a change to this value-return rule.

## Source guards and ownership regression obligations

`84-call-integrity.watsup` checks saved tasks in their saved CONTEXT, not the
active callee context. Receive tasks require the current owning function, a
bounded index, prior defined slots, no constant context, and the actual sole-task
queue. They do not recheck the historical types of earlier aliased parameters.
Typed RETURN_VALUE line/origin/unit must match an actual return root in the owning
function CODE. Unit return-root CODEEXPR projection is also exact, including a
source with no function declarations. Arbitrary consistent runtime values remain
valid: maintained protocol returns supplied PINT99 and verifies output `9911`.

Reuse machine heap/owner guards across active/saved/held frames, surplus values,
constant table/cache roots and cleanup. Return references must survive frame
release through an explicit owning operand, with alias identity intact. Test
adjacent public resumes and selected full suffixes, including abrupt conversion
errors. Do not infer compiler operand/reference designation from current heap
ownership or reconstruct arbitrary runtime history to validate metadata.

## Accepted acquisition interfaces

`96-call-reference-compiler.watsup` admits only direct named positional calls on
reference-assignment RHS; generic writable calls and reference array call items
remain rejected. Existing87 optimized builtin write checks still apply.
`97-call-reference-acquisition.watsup` preserves KNOWN values through ACQUIRE_CALL.
Assignment consumers emit their Notice and perform ordinary writes preserving
existing CV/computed/DIM aliases; actual REFERENCE results use the binding path.
Target fetch errors precede Notice and callee errors prevent it. Native MAKE_REF
leaves ordinary call VAR values unwrapped. Do not replace this with fresh cells.

The call instruction line differs from its enclosing post-argument emission line.
Shared46/78 preserve both, including nested calls and typed returns;88 constant
location restoration remains unchanged. Narrow source projection binds assignment
root lines. The active acquisition guard follows leading AT/ORIGIN_RETURN only,
accepts arbitrary valid KNOWN/REFERENCE results and rejects VARIABLE before step;
saved tasks validate metadata without using unrelated active results.

Final independent acquisition evidence is7 native+4 pending profiles,13/227
protocol,3 dense/819 and2 exact complete926 state bridges at seven cuts. Author17
source,2 dense/553, compiler26+3/29, typed38/adjacent13 and CLI8 pass. Linked review
retains all failures, raw closure audits and historical identities. Repeat only
focused gates justified by new shared changes; full callable integration and final
current-source/full-syntax/fresh offline checks remain mandatory.

## Next source preparation

Read `.tools/compiler6-reference-returns/PLAN.md` and its13b3c242 archive
(1397 paths:9 new sources,1 value-call assignment,7 historical114 contexts).
The exact10 requests now have accepted926 replays in
`.tools/compiler6-reference-returns/current926-originals/report.json`; old917
identities remain historical. Source reference-return declarations are still
Unsupported on933.

The separate7 current933 originals are at
`.tools/review10-reference-final/.tools/review10-return-demand-originals-dori_xf6/report.json`.
Unused untyped/mixed undefined CV returns are quiet; int CV return emits an
undefined-variable Warning before TypeError. Undefined GLOBALS DIM write fetch
creates null quietly, then int verification errors. Unused typed reference returns
still coerce the shared cell; value-return detachment must remain unchanged.
Explicit mixed returns omit VERIFY, even if an unreachable implicit verifier
occurs elsewhere in the body. Preserve position-aware evidence.

Compiler demand observations are in `.tools/compiler6-reference-demand/`:
`opcode-originals/report.json` retains19 caller contexts; `return-positions.json`
reuses those7 reviewer sources. Direct statements, @ and discarded for clauses
have unused slots; void casts, ternary/coalesce, final for conditions and actual
consumers retain used slots. Diagnostic opcode profiles are separate from ordinary
native observations. Derive demand from original source ancestry at CALLSITE,
not arbitrary continuation/result history; stop at a real consumer.

The proposed source classification is in
`.tools/compiler6-reference-demand/INTERFACE-98.md`. New933 class controls retain
whole `$GLOBALS` as a copied value without Notice, despite VARIABLE designation;
`return ($x =& $y)` remains VALUE-designated and notices even with a REFERENCE
operand. Neither should be mistaken for a lazy literal-CV alias path.

Agree finite stages and source guards before admission. Literal CV verification
must read before quiet write fetch when emitted; computed/DIM returns retain
write-fetch timing. Successful reference conversion writes the shared location;
only a demanded variable result is promoted to an owning reference. Preserve
return/source classification independently of runtime operand shape: literals
and forwarded value calls retain return Notices even when unused. Bare/implicit
returns need their own source/ENDLINE behavior. Keep return/send/assignment
Notices distinct, preserve cell owners through unwind, and test byvalue consumers,
external aliases, held arrays, conversion failure and adjacent/full resumption.

The bounded lifecycle29 chain keeps globally live string CV histories and a sole
checked echo-only destructor. Validate the entire saved destructor result/release/
operation-exit prefix before projecting to idle f scope; deleting the operation
exit must reject publicly. Capture preserves the selected object until ordinary
I2 disposal and retains the original Y TypeError. Use exact reached frontiers:
eager retirement schedules real work even while other CV aliases survive. Source2,
state3/306 and independent saved82/1 pass; active direct consumed validation and
other destructor bodies/lifecycle layouts remain OPEN.

The lifecycle30 body extension admits checked literal echo then literal-message
TypeError throw under the same certificate. Bind the fresh callback error with
empty Previous separately from its late Y-finally/caller Previous link; do not
infer object identity from `R:destructor` alone. Source2, state3/335 and independent
post-D91/1 pass. The full registered prefix admits publicly and deleting its
operation exit refuses; no active branch or error-chaining rule was added.
Broader destructor effects and lifecycle layouts remain OPEN.

The lifecycle31 extension links one checked global string write to W's return
beneath the last outer X. Preserve that source/cell relation as W retires: actual
WX and X public states retain the changed value. Source2/state3/355 and independent
post-write saved-frame110/1 pass; executed destructor ENV/global cell equality and
the full registered prefix are authenticated, with wrong-cell public refusal.
Fresh/late error identity, bypass alias/no object birth and late budget equality
remain distinct. This is a local source certificate after W retirement, with all
old idle/Notice/class/string/prefix guards; other mutation/lifecycle stays OPEN.

The lifecycle32 route admits an in-range integer literal only for source-linked W.
Use mutation_source_cursor or mutation_write_cursor at reached WX/X; the old
string mutation_cursor must remain absent when W=PINT17. Source2/state2/266 and
independent saved109/1 pass, with exact PINT17 alias/store, full prefix, wrong-W18
and non-W-X17 public refusals, late caller/error/budget and bypass checks.
Preserve original parse failure71e18 zero state credit. No coercion, active branch
or new Previous rule; post-W reconstruction stays local and broader returns OPEN.

The lifecycle33 route admits checked direct GLOBALS W→X reference rebinding before
echo/TypeError throw. Bind distinct ordinary f-local W/X strings, X's unchanged
global/local identity and global W equal original W or exactly X; reconstruct W
even at reduced [X]. Source2/state2/293 and independent public136/1 pass. Actual
callback current8/saved21 queues include the extra reference-rebinding release/
operation exit; global W=X and saved f-local W stays distinct. Wrong global W→Z
and non-W global X targets refuse publicly. Caller alias/probe/error/budget and
bypass pass. Preserve caller-table failure73a37924 zero state credit and retained
bypass compilation. No new roots, rebinding/eager/Previous rules or native Previous
observer; the certificate is local and wider rebinding/returns remain OPEN.

The lifecycle34 route admits checked singleton GLOBALS-W unset before echo/throw.
Keep global table presence, original live local W and all non-W global/string
guards; only W may be absent globally, including after its marker retires.
Source2/state2/326 and independent public134/1 pass. Actual callback current7/
saved21 and registered1/2/2 preserve W while global W is absent; forged global W
and non-W X targets refuse publicly. At main, GLOBALTABLE is absent and active
ENV has no W. Count WARNING events: zero through retirement/caller entry, then
two source-qualified WARNING(w,6) reads. Bypass is quiet; late error/budget checks
remain separate from the older native Previous observer. Reconstruction remains
local, with no unset/eager/active/Notice rule change; wider returns stay OPEN.

M42 adds validation only at `b55942bc`/385: pre-unset x and the saved owning return
carrier stay identical despite absent/present local bindings (public107/2), then
the carrier reaches main r/a and write-through with caller-cut budget equality
(reached2/176). The selected cell remains owned; physical collection and wider
released borrowed-cell conversion stay open. Recover with
`tests/semantics/reference_released_cv_state.py` and the local-CV lifetime ledger.

M43's untyped cancellation/control source2 and late2/230 stay at `43df347e`.
The real active cleanup exposed missing registered-operation EXIT integrity.
Require exact EXIT presence in scoped current/saved TODO via84/270; never add this
reverse check to generic operations_valid, whose fatal histories replace TODO.
The patched `b6805e2` passes strict/source2 and active68 + genuine parked23/two
EXIT-only refusals. Recover old late fixtures with reference_finally_cancelled_state.py.
reference_registered_exit_recovery.py is evidence recovery: copy it to preserved
private43 verifier make_parked_exit.py before running; it needs archived0bf9 and
emits exact50e1 at that original path. The ledger records paths/hashes. Abstract
HCELL retirement does not establish Zend physical collection; broad returns OPEN.

M44 changes no runtime: source2, early parked58/two controls and late2/230 pass at
`cb498f92`/385. The Fiber object retains the selected HCELL through its saved VM;
late checks resume the same in-fixture carrier into the anonymous worker's r/a,
write and completion/main E. Budget begins at that worker alias state. Early
pre-unset history and late delivery are separate executions. Recover with
reference_suspended_cv_state.py and suspended_carrier_validation in the local-CV
ledger; retain elaboration059ac0, syntax-only6c05app0 and unrun6909field0. Broader
suspension/borrowed conversion/physical collection and returns remain OPEN.

M45 is validation only at `cbc57fdb`/386: suspended untyped finally override/control
source2, early92/two phase/EXIT refusals and separate late214 pass. Early source
history owns the original x/O→parked carrier→resumed active destruction; late
fixtures start their own actual y/unwind carrier and follow worker delivery,
r/a mutation, main E and worker alias-state budget. Recover with
reference_suspended_cancel_state.py and suspended_cancellation_validation in the
local-CV ledger. Keep abstract old-cell retirement distinct from physical Zend
collection; wider cancellation/suspension/typed lifetimes and returns stay OPEN.

Typed-property reference constraints, finally rechecks, objects/methods, dynamic
sources and dynamic callables, named/unpacked/variadic calls, generators/Fibers and lifecycle remain
required later core work. Publish reviewed paired code, evidence and concise docs
in small commits after exact canonical equality and CLI validation. Never push.

M46 is validation only at `27a92e4b`/386: early/delayed external Fiber drop
source2, early98/two phase/close-VM EXIT refusals and separate late270 pass.
Late executions authenticate their own pre-drop carrier (delayed control retains
it through the first GC), active D, graceful non-returning Fiber retirement,
restored main L/G/E and caller-cut budget; worker R is canceled. Recover with
reference_orphaned_cv_state.py and orphaned_carrier_validation in the local-CV
ledger. Preserve parse d5310, syntax-only0db9app0 and unrun c677 marker correction0.
Physical collection, wider abrupt close and broad returns verification remain OPEN.

M47 is validation only at `0df6172`/387: throwing old-O orphan close source2,
early102/one saved-f operation EXIT refusal and separate late260 pass. Late fixtures
start at their own post-D source New/ordinary Exception, preserving the same
error/line2/pure trace and null Previous at main catch/caller; no delivered r/a.
Fiber FAILED=true/GRACEFUL=false differs from M46, and final error retirement
follows the live-caller identity checks. Budget starts at that restored caller.
Recover reference_orphaned_throw_state.py via orphaned_throw_validation in the
local-CV ledger; preserve both unrun source-wrapper/origin packets0. No native
trace/identity, cross-fixture identity, physical collection or returns closure.
