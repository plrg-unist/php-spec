# Source reference returns after call-result acquisition

Compiler6/runtime7/review10 continue with compiler98/runtime99. The next bounded
increment connects source reference returns and caller result demand. Calls and
PHP core remain incomplete.

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

Typed-property reference constraints, finally rechecks, objects/methods, dynamic
sources and dynamic callables, named/unpacked/variadic calls, generators/Fibers and lifecycle remain
required later core work. Publish reviewed paired code, evidence and concise docs
in small commits after exact canonical equality and CLI validation. Never push.
