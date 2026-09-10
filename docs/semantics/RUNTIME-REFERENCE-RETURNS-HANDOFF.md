# Runtime successor after typed value returns

This handoff starts after the typed checkpoint is independently accepted. The
next bounded increment is reference returns and the necessary call-reference
acquisition consumer. It does not close calls or PHP core. Compiler6 and review10
retain continuity; a fresh runtime implementer should use their source evidence.
No next compiler/runtime source admission is present yet.

## Exact starting point

Paired code `0ed17419`, compiler evidence `2ea12015`, author `dabc28d9` and
[independent review e097f95e](../../coverage/semantics/typed-function-review.json)
bind canonical **926 inputs**, SHA256
`599f3963f5e347c41ba7dd0c632a407f73f7f9157ca8e64c6191ba6d32cc3de7`.
The full path/hash/mode manifest is retained in the author publication archive and
`.tools/runtime6-typed-calls/final-inputs.json`. Start a new private root from all
926 canonical files, including pre-existing helpers, binaries and comparison
archives; do not copy a historical compiler root wholesale.

The author source/compiler/state gates and independent semantic gates tested
926/`baa85f57`; only the maintained protocol output helper changed afterward.
`gate-input-bridge.json` proves 925 unchanged files, equal path sets/modes, and
exactly one test-file change to final926/`599f3963`. The corrected fresh protocol
and canonical CLI8 tested final599. Preserve these identities rather than
relabeling the earlier gates.

Pinned PHP8.5.10: `vendor/php-src` commit
`34308a6666b2d489c509541ea9befea9e2b42348`; `.tools/php/bin/php` is the comparison
oracle, never a semantic evaluator. The typed evidence binds 17 pinned source
inputs, including `Zend/zend_exceptions.c` for uncaught display formatting.

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

Accepted typed evidence: author38 native source profiles plus3 uncoerced-cache
projections/12 assertions; compiler56 native phases+8 explicit boundaries/38
projections; author4 dense states/1096 assertions; corrected protocol19/218;
independent15 native profiles+3 ticks-dependent controls,5 dense/1357, retained
protocol19/217, and2 exact no-type917 state bridges at seven cuts. Author raw
234 responses/8 worker closures and23 standalone runner closures were audited;
canonical CLI8 agrees exactly. Reuse these gates selectively according to actual
shared changes; do not repeat unchanged broad campaigns just for counts.

## Next source preparation and concrete work

Read `.tools/compiler6-reference-returns/PLAN.md`, `originals.json`,
`valuecall-original.json`, and `historical-index.json`. Frozen preparation archive
`originals.tar.xz` SHA256
`13b3c242a1c54247df27e966bd784293447d985877e41148948ace2eeb534aca`
contains 1397 paths: nine new reference-return sources, one value-call reference
assignment source, and seven selected historical114 identities. Their recorded
current-runtime baseline is917, with Unsupported results. Replay the exact
retained native/source/request contexts on accepted926 before new admission;
keep the old917/full primitive and separate lint/compiler evidence unchanged.

Agree compiler/runtime classification first. Pinned `zend_compile_return`
compiles variable reference returns in write mode, call returns as expressions
with RETURNS_FUNCTION, and other expressions as values. Native notices remain
observable even when a literal or forwarded value-call result is unused; unused
local-variable returns do not notice. Bare and implicit reference returns also
need the retained native notice behavior.

`$x =& g()` for a value-returning call is a necessary source/compiler ACQUIRE
prerequisite: native emits `Only variables should be assigned by reference` and
performs an ordinary target write, preserving existing target aliases. Accepted926
originals confirm this for literal, computed-variable and dimension targets.
`ZEND_MAKE_REF` leaves an ordinary call value unwrapped: its VAR branch wraps only
an indirect location. This differs from parameter-send and return-reference notices.
Admit only actual reference-source contexts; do not make arbitrary calls writable.
Preserve current call-DIM base lowering and temporary-array/reference-argument
behavior. Actual reference-return results retain their cell through ACQUIRE;
ordinary value consumers resolve them. Typed reference-return coercion must write
the shared source alias (retained native `1133`), whereas current typed value
returns preserve the external source strings (`211`).

Keep new source-derived task/result classifications finite, paired with source
admission and meaningful ownership tests. Module numbers/schema for this next
increment are not yet agreed. Reference constraints from typed properties,
finally rechecks, generators, objects/methods, multi-unit execution, named/unpacked
and variadic calls remain required later core work, not implemented by this
checkpoint. No push; publish reviewed paired code, evidence and concise docs in
separate small commits after exact canonical input equality and CLI validation.
