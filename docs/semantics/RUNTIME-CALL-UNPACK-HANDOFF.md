# Historical preparation: array call unpack

Implemented107/108 is now accepted on981/3f3; see the [runtime contract](SOURCE-CALL-UNPACK.md)
and [current integration handoff](RUNTIME-CALLABLE-INTEGRATION-HANDOFF.md). The preparation
below retains its original baseline and pending-at-the-time obligations.

Start from accepted972/e1bf: code84fc35f5, compiler467e8788 and independentbb38d1d7.
Read current PROGRESS and the [compiler106 contract](BUILTIN-NAMED-COMPILER.md).
All972 watched bytes/modes and generated report7e9200 are bound by the
[review](../../coverage/semantics/builtin-named-review.json). Module25 positional
modes and87's exclusion of named/unpacked special calls remain unchanged.
Builtin lookup is compiler metadata; builtin bodies/defaults/callbacks remain due.

Root coordinates compiler7/runtime7/review10. Proposed next pair107/108 requires
root's accepted-checkpoint read before activation. Preparation is
`.tools/runtime7-unpack-preparation/PLAN.md` and `INTERFACE108.md`, archive dcd5c6c2.
It retains exact968 baseline,22 author plus6 independent ordinary native/current
Unsupported sources,8 separate opcode profiles and6 independent parser/lint
observations. Reuse these sources/requests on accepted972 without duplicate native
execution. Opcode instrumentation is separate evidence, never runtime agreement.

Compiler107 must preserve original NArg indices and emitted operand lines while
compiling unpack children in PPR. Named operands after unpack use deferred modes.
Retain static priority before forbidden later operands. Confirm actual operand
class from pinned lowering: literal/folded CV, computed/DIM TMP and call VAR are
observed; assignment/reference/conditional expressions need any missing concrete
contrasts before a general classifier. Source VALUE designation alone is
insufficient to decide whether unpack may wrap entries in its source table.

Runtime108 can reuse NAMED_HOLE/SENT slots (SENT owns its operand; HOLE owns none)
and ordered extra keys, with a
separate owned unpack container, insertion cursor and per-container named flag.
Source send count, expanded positional extent, fixed destinations and extra names
remain distinct. Integer key values do not choose destinations. A string then
integer key errors within one container; the named flag resets for each unpack.
Complete operand evaluation precedes sending; a send error prevents later source
arguments from running. Traversable needs its separate object/iterator protocol.

Eligible shared CV/VAR arrays undergo reference-destination prescan and separation
before entry iteration, including its name errors. Per-entry promotion follows
successful destination selection. Existing references remain shared; TMP/CONST
uses fresh callee cells without wrapping source entries. Preserve source-slot
versus temporary-container ownership and COW, then release only the container
owner after its final entry. Sent operands must survive subsequent argument effects.
Do not introduce a persistent location class without an actual continuation need.

Reuse105 hole preflight/cache/receive semantics after dynamic binding. Independent
six controls pin named-hole C+1 warning before TypeError versus positional type
failure before trailing default,0 positional arguments with named trace keys,
mixed-tail TypeError#3, fresh omitted references with uncoerced string cache, and
saved caller suppression. Their ordinary native outcomes do not establish model
state until the future paired replay. Later aliases may change earlier types.

Guard actual source/callee/class/line, finite cursor/container/key/mode/owner shape
and local continuation relationships. Explicit-NArg prefix reconstruction from105
cannot describe expanded calls. Use current effective ARGC for integer destinations
and current lookup for names; no saved initial extent solely to reconstruct history.
Prescan may keep its local argument-number accumulator. Preserve arbitrary
consistent runtime values/cells and do not inspect unrelated RESULT in saved tasks.
Freeze an early runnable pair before retaining malformed-stage counterexamples.

Freeze maintained source/compiler/protocol and disjoint author/reviewer dense
producers before final gates. Use meaningful preparation/send/cache/cleanup cuts,
full suffixes and complete prior no-unpack state bridges. The existing900s allowance
is evidence-based; retain timeouts/setup failures and exact identity bridges.
Review, install, verify all bytes/modes, then publish small sequential code/evidence/
docs commits; never push. Full callable integration, all required core intrinsics,
objects/exceptions/dynamic callables, lifetime and final current source/full syntax/
fresh network-isolated offline gates remain mandatory. No family closes here.
