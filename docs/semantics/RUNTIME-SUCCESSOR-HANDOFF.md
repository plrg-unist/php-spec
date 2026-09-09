# Runtime continuation

Read AGENTS, PLAN, PROGRESS and the php/php-spec/p4-spectec skills first. Root
orchestrates, compiler4 preserves frontend/compiler continuity, and an independent
reviewer owns evidence/PROGRESS. Never push. Semantic execution is pure SpecTec;
the sole oracle is local PHP 8.5.10 CLI NTS64. Complete core remains unfinished.
Read [bridge invariants](RUNTIME-BRIDGE-HANDOFF.md), [compiler continuation](COMPILER-HANDOFF.md),
[reviewer continuation](REVIEWER-HANDOFF.md), [updates](UPDATES.md),
[reference wrappers](REFERENCE-WRAPPERS.md) and [ordinary operators](ORDINARY-OPERATORS.md).
All `.tools/` paths below are relative to the repository and survive this rotation.

## Accepted ordinary checkpoint

Nullable/context prerequisite code `9b82507a`, reports `22b36687`, review
`91f035e0`, status `b5c6698b` precede ordinary code **`dba21cee`**, compiler reports
**`a3290ae3`**, and source/state/contract **`e397b137`**. PROGRESS records the final
independent review **`2ab579eb`**, private-list review **`d0c65f91`** and status
**`5a2ef96f`**. Accepted closure is
`a8f6aa0cac996578befe8fa49621af2fdc214a44e4d9612a4cb8ce5dcee05691` (799 inputs).
The full **4,407 exact sources +25 outcome negatives pass**. Raw
`coverage/results-semantic-source.jsonl` has SHA256
`a1df0fdfcf893b067b4a581ad7a2c9e8c82a1014cfb542732b5f13cd2693695a`.
Canonical ordinary.py adds 1,506 source literals and 25 state programs/2,875
assertions, including five loops at every budget 0–100. All eleven compiler gates
pass: 4,449 source lints; omissions 262/2,135 resumptions; constant42, truth79,
comparison48, incdec108, compound289, control46, runtime15/148, context233,
occurrences169/1,084/1,495. Independent 62 sources and the complete ordered raw
audit pass; the audit binds 16 archive groups and 13 current reports.

Archive commit `ef9ed822` preserves exact 805 initial, 28 concat and 680 expansion
originals. Precisely 673 expansion cases are admitted; seven request-environment
Unsupported cases remain: computed-ternary `this` write/unset and literal-concat
`GLOBALS` read/void/string-cast/write/unset. They are not passing source cases.
All four earlier concat-CV originals are admitted. No semantic family closes.
The accepted 13-path delta is preserved in `.tools/ordinary-production-delta.json`;
`.tools/runtime-ordinary-final` is its immutable candidate. Older ordinary draft
generators predate nullable remapping and compound/power helpers: never replay them
over accepted code. Concat constant conversions, delayed CV capture, parser name
provenance and five casts/bitnot/void are now production behavior, not pending drafts.

## First next task: immutable validation outputs

Make a separate small harness commit before new source admission. validate.py
around line756 still hardcodes broad/selected raw output paths. Use exclusive
NamedTemporaryFile creation in coverage with existing
`results-semantic-source[-selected]-` prefixes; report consumers already follow
`raw_results.path`, and `.gitignore` covers these files. No new CLI/schema needed.
Run the same selected prefix twice and prove distinct paths and preservation of
the first raw bytes/hash plus historical selected/broad evidence. Also replace
the stale report scope with “authored source fixtures for currently admitted core
semantics”. Perform evidence/inventory/source-path preflight before costly runs.

The negative preflight accidentally overwrote the previous four-case selected raw;
the reviewer recovered its **exact** original SHA256
`841d9a646dcaf859348d0c6214025ebfefdb51d53b7a2cee2bbd5653867d8ef3`.
The committed ordinary-selected-raw-recovery.json proves recovery, not relabeling.
`.tools/ordinary-negative-preflight/previous-*` preserves that selected evidence;
the same directory keeps the new 1+25 preflight separately. Previous full 2,639
source report/raw/inputs are in `.tools/ordinary-previous-source/`.

Then publish coherent unpack/list/foreach increments with targeted exact source,
compiler, state, ownership, dense-resumption and independent gates. Root requests
one full current source campaign at the combined unpack+destructuring+foreach
checkpoint, or earlier if a real unresolved shared regression risk demands it.
After inputs change, older full reports remain explicitly historical. Final full
syntax, fresh offline build and complete core validation are still required.

## Immutable next candidate: private, not admitted

Use **`.tools/runtime-list-candidate/`**, not its mutable predecessors.
`candidate-inputs.json` binds 55 modules, 66 local inputs, five canonical tools
and eight report/fixture hashes. It contains accepted ordinary plus real unpack,
destructuring, effectful known results and nonvariable-left coalesce. Preserve it;
work in a distinct copy and deliberately rebase later compiler changes.

* source-originals.json/source-replay.json: **251 exact agreements of252**, with
  one retained `$http_response_header` Unsupported (`list-rhs-line-cv-deprecated`,
  `compile-time http_response_header context`). Aggregate fail is intentional and
  honest; exclude that boundary from any source admission count.
* store-line-source-originals.json/store-line-source-replay.json: 12 exact extra
  multiline target-fetch/store controls pass.
* state-replay.json: seven checked source programs, 3,633 assertions, budgets0–100.
  Resume only BUDGET states; resetting THROWN to NORMAL was a retained fixture defect.
* mechanism.watsup/mechanism-result.json: 23 occurrence/effect/pool assertions.
  quiet-boundaries.json records five explicit Unsupported cases, not agreements.
* Independent frozen replay: 44 exact sources pass; see
  coverage/semantics/list-source-review.json and reviewer handoff. Snapshot inputs,
  tools and report hashes stayed unchanged.

Earlier `.tools/runtime-unpack-joint` passed154 sources (112 runtime+42 compiler)
and31 state cases/2,454 assertions. `.tools/runtime-unpack-final` rebases that work
onto final ordinary; the immutable list candidate includes it. The earlier
`.tools/runtime-list-next` 123 native-derived task fixtures/1,353 assertions,
12 dense fixtures/6,192 assertions and value-helper68 assertions are **unchecked
fixtures**, not source passes. `.tools/runtime-list-effects/paired` preserves
first actual source failures and repair scripts, but its prepare.py predates later
fixes. Do not regenerate or overwrite the immutable candidate with old scripts.

## Paired APIs and semantic constraints

60-array-unpack defines `array_unpack(state,target,value,line)` and shared
`unpack_error_bytes(value)`: borrow source/target roots, append integer keys,
replace string keys, apply merge_item singleton-reference unwrapping, stop on
overflow. 61 schedules ARRAY_UNPACK at the original item FIELD1, then ARRAY_NEXT;
preserve nullable item indices. Compiler45 PFSPREAD/PFSTATICBYTES shares the scalar
error, checks holes first, and defers overflow through pfinserted. Load60 before45.
Traversable objects remain future object-protocol work.

62-list-values (before45/46) defines list_pattern, recursive list_references,
list_read and list_acquire. Nested array/list operands under spread propagate
references before spread rejection; nonnested spread contributes false. Array
list reads copy values; null is silent; other scalars warn “Cannot use TYPE as
array” without string-offset access or key coercion. Resolve undefined keys first.
Reference acquisition uses dimension_location/element_reference and actual wrappers.

63-list-control adds LIST_CAPTURE/PATTERN/NEXT/FETCH/STORE/STORE_NAME/STORE_DIM;
30/31/39 carry tasks, origins and owners. Evaluate RHS once, retain one active
source owner, evaluate key, fetch/copy/acquire element, then prepare target.
Nested traversal finishes left-to-right; return original RHS. Ordinary CV RHS,
including parser literal-concat names and `$this`, uses special list_value_cv;
missing `$this` warns as a CV instead of generic FETCH_THIS Error. Initial nonref
CV fetch line inherits pattern context exported by compiler64. Next unkeyed fetch
carries original target source_line only for ordinary VAR; reference/DIM preserve
prior fetch line. Computed name acquisition still has its own warning line; do
not substitute variable_line(target) or generic ending context. Nested patterns
carry actual final context. Compiler validates referenceability before RHS;
style/empty/keyed-hole checks follow RHS, with key compilation before target/style.

List assignment can return a compiler-known RHS while still emitting stores.
Compiler46/64 adds PPCEFFECT(path), mapped by33 to CODEEFFECT(path). Runtime30/31/33
select ordered topmost effect roots, deduplicate markers and run each under AT as
nullary EVAL_EFFECT followed by DISCARD, then COMPILED_RESULT(bool) reads the pool.
EVAL_EFFECT bypasses only its own root shortcut; children retain descriptors.
COMPILED_RESULT false/true distinguishes ordinary/DIM-base reads without an extra
held pooled owner. Missing/nonexpression origins and missing pools reject.
Dynamic redirects also run effects **outside the redirected subtree** first;
the target executes its own effects. Constant-only prefixes erase required stores.
Path prefix uses guarded slices; an earlier repeated-pattern form crashed SpecTec
anti-unification and is retained in first-source-* reports. No new pstate fields.
Before admission compiler4 must update PPCEFFECT consumers in source_compiler.py
(expression_paths and pprecord), incdec_compiler.py and compound_compiler.py.

36 key_value(PARRAY) now delegates dimension_key_value's TypeError in the candidate;
compiler45 still emits its distinct static Illegal offset error. This closes two
old runtime Unsupported failures while preserving prepass timing.
65/66 implement only **nonvariable-left coalesce**: compile both sides, keep result
TMP, resolve left once; nonnull copies/clears BASE, null evaluates right+VALUE_COPY.
Existing PFCOALESCE prepass remains separate. Variable/DIM/property/nullsafe/static
property left operands explicitly stop at coalesce quiet-access compilation.
Seven environment cases, header context and full quiet access/IS/??/??= follow
containers before broader calls; coordinate runtime/compiler ownership with root.

## Foreach work still to implement

`.tools/container-next/{RUNTIME-PLAN.md,native-originals.json}` retains60 initial
list/foreach controls; `.tools/runtime-foreach-next/history-originals.json` retains
30 COW/cursor witnesses; `.tools/foreach-prerequisite-originals.json` adds33 compiler
controls. No foreach runtime implementation is admitted. Compiler4 owns its next
private frontend/compiler work and has the exact captured multiline protocol.
Its isolated `.tools/foreach-frontend-next` appends keyByRef at FIELD5, preserving
FIELD0–4 and all70 domains; 33 parser, 29 checked-print and seven typed controls
pass. Its67 compiler currently implements only key-reference/list-key prechecks;
pair later against the unchanged runtime-list-candidate, preserving both originals.

Current visible ITEMS order cannot represent cursor history. Track insertion
occurrences and each iterator's separate saved positions in COW descendants;
progress in the original must not advance saved copies. Choosing a descendant
discards other copies; empty-array duplication does not copy iterators. By-value
iteration holds HARRAY, by-reference holds the actual HCELL (temporary iterables
may create owned wrappers). Cursor metadata adds no owners. Replacing an array
switches traversal; rebinding/unsetting its source name retains the old wrapper.
Preserve alias tails and cleanup on break/return/error; nested loops and budget
pauses keep independent positions. Do not approximate bucket behavior by keys.

Compiler rejects key-reference/list-key before iterable, propagates nested value
references, uses PPW only for writable byref iterable, otherwise PPR. RESET/FETCH
use iterable ending context; direct CV value target binds without advancing CG
line, other targets/list and key use synthetic assignment. FOREACH original Zend
line is iterable original AST line, not parser statement start; prechecks/final
restore use that line. Pinned routes: zend_compile.c list3515/foreach6079,
zend_vm_def.h FETCH_LIST2431/2443 and FE_RESET/FETCH6882–7256,
zend_hash.c iterator-copy597/dup2444.

## Preservation and process state

Only actual reference acquisition marks REFCELLS; ordinary initialized writable
fetch stays unmarked (84d70299 correction). Preserve singleton history, COW/union
unwrapping, uncollected cycles, captured locations, delayed CV versus copied
expression results, ternary copies versus raw redirects, permanent pools and
exact origins. Numeric00–09 are pure and reviewed. Namespace-relative static
resolution remains the sole intentional divergence, source activation pending.
Frames/calls, classes/objects/protocols, dynamic sources, generators/Fibers,
callbacks and lifecycle/source GC remain required; no family closure is claimed.

Private helper campaigns must invoke the canonical numeric runner directly.
Private Dune builds through shared _build previously changed it; restored hash is
0787d1435876ac0522de9f30f3ae3605858d0c79337b5f2885e48abdb882d1f7.
Candidate manifest and .tools/omission-restored-tools.json bind tools. No runtime
campaign or owned process remains running at handoff. No owned uncommitted code
remains; reviewer/compiler files are independently owned. Stage explicit paths.
