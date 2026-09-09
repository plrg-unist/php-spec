# First source calls: independent review continuation

Read AGENTS.md, PLAN.md, PROGRESS.md, CORE.md and the php/php-spec/p4-spectec
skills before work. Root orchestrates; compiler/runtime/review work is delegated.
Never push. Preserve exact failures before repair, keep Unsupported/timeouts/
harness failures separate from agreement, and use small coordinated Git commits.
Only pinned PHP8.5.10 CLI NTS64 is the oracle; execution remains pure SpecTec.

## Current accepted boundary

Code **a8fdac1e**, runtime author **d907c5db**, compiler author **04ac151f** and
independent acceptance **f3149e32** bind this checkpoint.
Production869/c946394c pairs actual plain named declarations/calls, recursion,
value parameters/returns, frames, global/superglobal routing and fatal cleanup.
Read SOURCE-CALLS.md and `coverage/semantics/calls-final-review.json` first.
Reference parameters/returns, defaults/types/strictness, named/unpacked/variadic
arguments, closures/arrows/statics/dynamic callables remain incomplete. Inventory
169 constructors/306 obligations stays partial; only oracle identity closes.

Evidence identities must remain distinct:

- Historical846/14d17662: full5706 ordinary +263 explicit-request observations;
  5969 case/profile rows,5926 source bytes,21 separate controls,4997 old sources
  unchanged. Accepted df1ddd18; do not rerun its completed raw audit.
- Frozen866/02f6029f:139 source cases; broad compiler5751 lints/5783 assertions,
  5778 subprocess records and11561 decoded Worker responses. Broad archive
  1dac5ba5 has70239 paths; Worker stderr was inherited and wire reserialized.
- Final870/f3605a94: only84 semantic delta from866 is source-derived ARGC/EXTRA
  counts and remaining-argument/index/held-count checks. Independent139 source
  replay retains278 exact Worker responses identical to866 complete states.
- Production869/c946394c: all870 loaded modules/five tools exact. Preserve canonical
  standalone builtin_argument_modes.py; omit unused78-call-frames-first.watsup.txt.
  Canonical CLI keeps historical100755 even though private copy lost its bit.
  Nine current state programs/2079 assertions,40 protocol fixtures,20 no-call
  full-response bridge and8 canonical CLI cases bind this publication.

Author base history fbad3452 has19445 paths/4447 payloads. Supplement0d20ce69
has6155 paths with1210 new payloads; it references the exact base payloads and
includes historical868 state9. Final publication archive separately retains
current869 state9 and canonical smoke/preflight. Do not relabel historical runs.
Compiler archive audits: scope32d68612 (3664 paths), compiler3c4db19a (7783),
argument52d02a43 (5375), line9faa9fe6 (682), focused a8a6bae5 (5434), broad1dac5ba5.
Reviewer preparation/final archives retain independent replays and all setup
corrections; author transport/fixture limits are explicit in their reports.

## Review invariants and next work

CURRENT/saved NAME/FUNCTION/PARAMS/CVS/CALLSITE/LINE derive from checked source
projections. ARGC equals source argument count; EXTRA length is signature surplus.
CALL_ARGS/SEND retain selected ORIGIN, source suffix/index and held operand count;
selected primary/fallback must remain stable across argument effects. The native
GN witness activates namespaced f during an argument after global f was selected.
Do not re-resolve that choice at resume. Runtime values, mutations/unsets/reference
rebinding and heap history are not reconstructed from source. Check finite
metadata relationships without attempting arbitrary unreachable-state proofs.

Heap ownership includes current and saved locals, pending operands, surplus args,
HELD results and caller iterators. Error unwinding retains only iterator IDs still
represented in saved continuations. Public drive checks source-derived descriptors;
recursive drive_steps preserves transition budgets. Recorded workers retain exact
binary request/response chunks, stderr and closure, reject trailing/stdout/stderr
and malformed/partial/error replies, and close both workers in nested finally.

The old `copy-unwind-nested-return` source is exactly `calls0-top-return-alias`,
SHA c3e18caf: output13, return7, cleared iterator/task roots and surviving
v→a[0]=1/w→b[0]=3 aliases. Four old property/nullsafe controls and two eval callback
witnesses remain pending. Global `namespace\static` signature rejection matches
native; only the intentional class-scope relative-static divergence remains pending.

Next private reference preparation: `.tools/compiler5-reference-parameters`,
48 phases/16 descriptors, five-path delta and869 frozen preparation inputs.
Archive3cc3c691 (2521 paths) and independent
`.tools/review8-reference-preparation-audit.json` are checked; no independent
execution replay/runtime-reference agreement claimed. Preserve the48 originals,
earlier114 argument protocol originals52d02a43 and later forward arrayliteral-DIM
control (lint0/runtime temporary-write Error, unlike known-target static error).
Read compiler successor handoff for exact next-stage path; pair runtime before
publishing source admission. SEND_VAL_EX non-lvalue fatal and SEND_VAR_NO_REF
value-result Notice have distinct timing; do not reuse ordinary writable-target
rejection for every actual argument. Defaults/types/variadics stay subsequent.

Complete all remaining core work: switch/match/labels/goto, call protocols,
objects/properties/class linking, exceptions/handlers/finally, dynamic sources,
generators/fibers, observable lifetime/weak references/GC, required intrinsics and
source encoding/preamble/halt handling. A later full current-source checkpoint,
full syntax audit and fresh network-isolated offline rebuild remain mandatory.

A future equivalent state-harness optimization may bind direct states once for
B union (B+1) before adjacent-step comparisons. Current B=0–32,64,128. Sharing
38 direct states replaces70 prefix evaluations while preserving all cuts,
invariants and seven selected full resumes. It was deliberately not applied to
the accepted campaign; any later change needs its own evidence bridge.

## Next concrete reviewer task

After skill/context recovery, coordinate with the fresh runtime and compiler5.
Review the paired positional-reference candidate against preserved native sources:
known/forward/self/fallback modes, non-lvalue fatal versus call-result Notice,
forward temporary-array-dimension error, alias/rebinding/COW and argument-effect
order. Preserve new failures before fixes, then check actual source outcomes,
reference-cell ownership at cuts and public continuation metadata. Reuse completed
firstcalls/source139/broad5751 audits with explicit byte bridges; refresh broader
runtime gates when shared changes justify it. Do not replay completed historical
archives merely because an agent rotated. No review8-owned processes survive.
