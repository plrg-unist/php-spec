# Compiler continuation after user constants

The constants prerequisite is independently accepted: code5151608e,
compiler evidence41b2c1a2, runtime evidence06b64f88;
[review3341519d](../../coverage/semantics/user-constant-review.json) binds current899/ca3c06e5
and original899/e7d552ec through one test-only correction. Runtime6 and review9
retain continuity; root coordinates the complete-core goal. Archived drafts retain
their historical wording.
Read current PROGRESS first, then PLAN, DEFAULTS-ACTIVATION-PLAN and the
[runtime default handoff](RUNTIME-DEFAULTS-HANDOFF.md). Never push. Keep native8.5.10, checked source paths,
pure SpecTec semantics, independent review and small paired commits.

## Current immutable compiler input

`.tools/compiler5-constant-classes/final-inputs.json` identifies889/cb31d858.
`class-compiler-delta.json` gives ten paths relative to initial compiler887.
30 requires only the new syntax merged into runtime-owned declarations;32 was
borrowed from runtime6 and must not overwrite newer runtime code. Shared33 only
adds the class export to the existing pool installation.45 and88 own folding,
source facts and declaration compilation. Runtime6's later paired manifest and
canonical bridge, followed by reviewer acceptance, govern final production.

The compiler source gates are45 exact phases+10 explicit pending+29 declaration
assertions, and40 class source phases+120 descriptor assertions. Focused existing
constant-context42+5, source-context233 prefixes and additional controls, and
magic48/context gates pass on889. The archive/report pair under private
coverage/semantics/user-constant-compiler-originals retains original37+line6,
initial887, source-bound class tests, failures, tools and source anchors. The
reviewer owns independent allocation observations and legal-boundary originals.
Historical firstcall866 broad5751 remains historical; no broad rerun was claimed.

`pfstate.CLASSFACTS` contains non-owning original-path classes only in CONSTANT
mode. `$pfclass_at` and `$export_classes` expose them. Pool `PCCLASS` is distinct
from owning PCONSTANT. All successfully folded children retain both records.
Stored declaration roots intern direct strings; deferred child pool values keep
raw classes. Runtime89 observes classes through the existing evaluator, stores
user-constant VALUE+CLASS, and validates source descriptors plus value/class tags and topology. Runtime
values are not reconstructed from source.

`PVSCALAR`, `PVSTRING bool`, `PVARRAY bool keyedclasses` are not value evaluators.
Array true implies empty, while false may also be empty. Helpers take actual
scalar operands or eps for arrays. `$pvclass_insert`/`$pvclass_spread` thread
existing NEXT history; they reside in45 because next_history is declared36.
`PVFOLD` versus `PVEXEC` preserves null-to-array allocation differences. Quoted
strings use raw preescape length. Heredoc uses stripped preescape content.
Empty nowdoc needs its checked token span: no content token versus an empty
content token produces different classes. No new frontend field was needed.

## Next bounded milestone: untyped positional defaults

Use compiler90/runtime91 after accepted constants. Keep types, variadics, named
and unpacked arguments, reference returns and other callable forms separate.
Do not duplicate existing17 parameter/default/type normalization or45 folding.
The existing literal signature consumers remain supported by their wrappers.

The historical prototype `.tools/compiler5-default-parameters` changes only17:
`psstep_start` returns PSSDONE or PSSDEFAULTREQUEST; `psstep_resume` receives the
shared compiler's psdefault result. The request occurs after parameter guards
but before default/type/optional normalization. Continuation holds context,
raw parameter, remaining parameters, signature and diagnostics. The retained
signature-step-inputs.json binds the precise17 delta. Its helper gates are357
native signatures,28 descriptors,174 return-reference flags and eight suspension
probes; these are not default-source admission. A first module declaration-order
setup failure is retained separately.

`.tools/compiler5-default-compiler` is an abandoned prototype setup, not working
semantics. PAUSED.json and .tools/default-first-load preserve its exact first
syntax failure and modified modules. Do not copy its old88 file into production;
88 now belongs to user constants. The current design is in
`.tools/compiler5-default-stage-design/DESIGN.md` and the prototype's
DEFAULT-MILESTONE.md. Original selected/skipped12 are at
`.tools/compiler5-default-stage-design/.tools/default-originals-_su6nvmv`; further compiler39 originals are at
`.tools/compiler5-default-originals/.tools/send-kind-originals-hvami040`.

Current32/89 PCCLASS origin validation admits only descendants of actual
NConst initializers. Compiler90/runtime91 must atomically add parameter-default
roots, descriptors and checked source/integrity projections with receive
admission. No receive-cache code exists yet.

Proposed DEFAULTS entries are ordered parameter index, actual source origin,
and STORED or DEFERRED. Defaults use field6 of the actual parameter at function
field3. Extend existing function/unit code projection with these roots; no
second code-owner stack is needed. A default before a later required parameter
is compiled/diagnosed but receives no omitted-argument descriptor. Establish
callee declaration magic/namespace/import context. Parameter-default policy
must disable ordinary/persistent constant substitution while retaining language
true/false/null; this is distinct from declaration constant folding.

Runtime6's agreed sequence enters the real callee, binds supplied operands,
then receives omitted defaults in parameter order before the body. Supplied
operands skip evaluation. Reference parameters with omitted defaults receive
fresh cells; arrays/COW and retained aliases need repeated calls and recursion.
Deferred cacheability uses actual provenance, not bytes or result length.
Failures must not install a successful cache entry or execute the body.

The independent106-source preparation and56-source diagnosis are durably linked
from current DEFAULTS-ACTIVATION-PLAN. Separate [literal11](../../coverage/semantics/literal-class-review-preparation.json)
and the [final constant review](../../coverage/semantics/user-constant-review.json)
retain operation/stage and source-projection controls.119 independent
default/cache observations remain ready for receive/caching replay.
Key observations: scalar/interned/non-refcounted values can warn once across
omissions, while refcounted values can warn repeatedly. Root user strings and
equal literal array children differ; identity/empty concat can preserve a class,
while allocating concat permits later namespace-fallback changes to be observed.
All these observations require actual default receive pairing before admission.

## Remaining full core

Keep169 constructors and306 obligations from the inventory; only the oracle
ledger is closed. Follow CORE-CONTINUATION-CHECKLIST, preserving calls/types/
variadics/closures, objects/properties, exceptions, dynamic sources, resumable
execution, lifetime, core intrinsics, switch/match/labels/goto and source gaps.
Final all-source, full-syntax and fresh network-isolated offline gates remain.
The sole intentional relative-static divergence is the pending class-scope
branch; ordinary named function namespace\\static already agrees with native.

The current literal class rules target the accepted `-n` executable profile,
without a scanner output filter. `zend_language_scanner.l` also has an
output-filter reallocation after escape conversion. A future executable encoding
profile must carry that constructor fact consistently; syntax encoding support
alone does not establish allocation-class agreement for that profile. The
current semantics CLI has no encoding-profile option. Do not infer closure of
that source-input obligation from the default-profile literal tests.
