# Engine discrepancies

This ledger separates intentional departures from observed engine irregularities
that the specification must reproduce. Only explicitly chosen departures belong
in the intentional-divergence inventory.

## Namespace-relative `static` declaration types

PHP 8.5.10 accepts the syntax `namespace\static`. In a named class without a
parent, compiling it as a return type segfaults. With a parent, it becomes the
parent type: a method may return a parent instance that a bare `static` return
type rejects. Both the frontend and native parser accept the retained sources.

The specification interprets this spelling as late-static `static`, preserving
ordinary position and class-scope restrictions. This avoids both a memory fault
and accidental parent substitution. It agrees with the engine's recognition of
the spelling as `ZEND_FETCH_CLASS_STATIC`, its handling in `new`, and the existing
relative `self`/`parent` pseudo-types. This is an intentional interpretation, not
an assertion that the pinned engine implements it.

At source pin `34308a6666b2d489c509541ea9befea9e2b42348`,
`Zend/zend_compile.c::zend_compile_single_typename` assumes every non-default
class-fetch kind is `SELF` or `PARENT`; relative `STATIC` reaches the parent branch.
Its null parent pointer causes the crash. The separate bare-type path correctly
handles `IS_STATIC`.

[Retained observations](../../coverage/semantics/engine-defects.json) include
source bytes, binary/source fingerprints, parser acceptance and exact process
outcomes. Regenerate with `python3 tests/semantics/engine_defects.py`. A reproduced
crash is recorded as `engine-crash`, never as PHP failure or conformance success.
The static helper's chosen-behavior checks are reported separately from engine
comparisons; source activation remains subject to its own integration gate.

## Static-return variance: follow the pinned behavior

The pinned `Zend/zend_inheritance.c::zend_type_permits_self`, called by
`zend_perform_covariant_type_check`, treats a top-level named member matching the
child class as sufficient for a `static` return type. It does not require every
intersection member and does not inspect an intersection nested inside DNF.

The retained `variance-static-*` oracle targets establish that a child `static`
return is accepted against parent `I&J` when its class implements either I or J,
and rejected when neither matches. An accepted implementation can actually return
a value that is not J. Parent `(I&J)|null` rejects `static` even when the child
implements both interfaces. `variance-self-intersection` confirms that an ordinary
`self` return rejects the missing member in the same setting.

These are candidate engine inconsistencies, not a selected divergence. Future
variance rules must reproduce the pinned predicate instead of replacing it with
logical set inclusion. [Oracle evidence](../../coverage/semantics/conformance-oracle.json)
retains exact sources, diagnostics, process outcomes and source hashes; the
[catalog](../../tests/semantics/conformance/cases.json) names each witness. No
source-class coverage is established by these probes. Covariance helper
`8a6c5708` now reproduces the pinned predicate under supplied visible class graphs;
its checked return-type/oracle comparisons are recorded separately in
[variance evidence](../../coverage/semantics/variance.json).

## Reference-assignment result: resolved specification defect

With `$a=1`, `($x=&$a)+($a=2)` originally produced spec 3 versus PHP 4.
`ZEND_ASSIGN_REF` returns an owning reference wrapper; its consumer reads the
cell's current value. Commit `751fbcff` models that captured cell explicitly,
including survival when both variable names are rebound. Ordinary assignment
still consumes its value. The independent witness now passes in the mandatory
388-case source gate, alongside 25 negative checks.

[Raw history and resolution](../../coverage/semantics/reference-result-disagreement.json)
retain the original process observations and the accepted correction fingerprint.
This was a specification defect, with no intentional departure selected.

## CV classification and reference initialization: resolved specification defects

`${$x}=&$x; echo ${""}===null;` emits an undefined `$x` warning in PHP,
but the previous machine initialized the direct source variable before reading
the delayed target name and omitted that warning. The multiline witness locates
the warning on the target-name expression line. A dynamic source fetch has a
different acquisition point; array-literal reference acquisition also remains
before delayed key conversion.

`${1.5}=1; echo ${1.5}+(${1.5}=2);` gives PHP 4 versus spec 3 because
literal float variable names are compiled variables at the pin. An overflowing
positive float literal has the same behavior; unary-negative and boolean
expressions are controls and must retain ordinary captured reads.

[Raw nine-case evidence](../../coverage/semantics/reference-timing-disagreement.json)
retains five disagreements and four controls, exact source bytes and both process
observations. These were newly uncovered outside the previous 421-case selection,
not excluded comparisons. Commit `eea66b2d` corrects both defects; all nine witnesses now pass in the
mandatory 439-case source gate, alongside 25 negative checks. Historical
observations remain unchanged in the raw record; its resolution binds the
accepted source IDs and fingerprint. No intentional divergence is selected.

## Constant-import seen-symbol casing: observed pin behavior

After `namespace Ns; const X=1;`, `use const Other\Y as X;` is accepted.
Changing the namespace spelling to `ns` rejects the import as already in use.
Putting the import before the declaration rejects the declaration with either
namespace spelling. `zend_compile_use` lowercases the namespace prefix of its
seen-symbol key, while `zend_compile_const_decl` registers the original spelling.

The three `constant-import-*` [oracle targets](../../tests/semantics/conformance/cases.json)
retain this case/order distinction. It must follow the pin during compiler-context
integration; no intentional divergence or source-semantic coverage is claimed.

## Compiler-context import lines: resolved specification defect

Multiline imports use the pinned compiler AST's name anchor rather than the
PHP-Parser statement start. `use` followed by a newline and `A,A;` emits both
no-effect warnings and its duplicate-alias fatal on line 2; the draft helper
reported line 1. Function/constant imports and group-use prefixes reproduce
the same distinction. An independently checked namespace/group witness reports
the fatal on line 4 in PHP and line 3 in the helper.

[Five raw disagreements](../../coverage/semantics/compiler-context-line-disagreement.json)
retain original source bytes, parsed nodes, exact oracle streams/status and the
helper's diagnostic events under its recorded implementation fingerprint.
Commit `891c2c95` uses the first imported name, group prefix or named namespace
location; 211 mandatory prefix comparisons and 64 independent alternates passed.
Commit `9658958c` subsequently transports checked anonymous namespace brace
locations, with 233 source-prefix comparisons and four encoding profiles. Missing
multiline or invalid locations remain explicit Unsupported boundaries. No
intentional divergence or source runtime activation is claimed.


## Numeric-string boundary suffixes: resolved specification defect

At the pinned `_is_numeric_string_ex`, the nineteen-significant-digit bound check
uses `strcmp`, including any non-NUL suffix. Negative minimum text followed by
whitespace is therefore floating-point; a NUL terminator preserves its integer
classification. An incomplete exponent with a sign advances the comparison
pointer: `9223372036854775808e+` becomes the minimum integer, and
`-9223372036854775809e+` becomes the maximum integer after signed conversion.
Larger prefixes can still compare above the shifted bound and remain floating.

The previous shared numeric classifier omitted these distinctions. This was found
in independent string-offset testing: the minimum text plus `tail` throws a
TypeError in PHP, while the helper wrongly warns about an integer offset.
[Raw arithmetic evidence](../../coverage/semantics/numeric-boundary-disagreement.json)
retains 104 original-source observations, including 28 disagreements and their
controls, exact bytes/outcomes and implementation fingerprints. Seven independent
source fixtures retain the principal discriminators. Correction `9fc9628f` follows
the pin and keeps explicit float casts separate from the numeric classifier. All
104 observations now agree; the independent 514-source gate and expanded numeric
helper campaigns pass. No intentional divergence or family closure is selected.


## Constant replacement lines: resolved compiler-helper defect

The ordered compiler draft locates a folded expression using its original AST
line. Zend's `zend_eval_const_expr` instead creates its replacement ZVAL with
`zend_ast_create_zval`, whose line is the current compiler invocation line.
For a dynamic array beginning with a variable on line 3 and a folded string DIM
on line 4, the native outer array-to-string warning is on line 3; the draft
expression descriptor records line 4.

[Ten independent observations](../../coverage/semantics/constant-rewrite-line-disagreement.json)
retain exact original sources, checked ASTs, helper fixtures, raw oracle/helper
streams, statuses and fingerprints. Six disagreements cover DIM, constant names,
arithmetic and unary rewrites; four controls cover whole arrays, original scalar
literals, nonfolding arithmetic and assignment barriers. Original scalar literals
retain their original line, so assigning one surrounding line to every fact is
incorrect. The ordered compiler and runtime fact consumer are not yet activated;
commit `72d3a65d` fixes the defect by retaining effective lines in each fact and
using them during ordinary compilation. All ten original probes now agree; the
report preserves the six old failures beside the accepted resolution. Cached
revisits preserve the first replacement line. Runtime fact consumption remains
pending; no intentional divergence is claimed.


## Heredoc and nowdoc scalar lines: resolved specification defect

For a dynamic array ending with a heredoc or nowdoc opened on line 4, the
pinned runtime emits its array-to-string warning on line 5. The current source
machine and ordered compiler helper both originally used line 4. Quoted multiline strings
correctly retain line 4. This is an admitted source behavior defect, distinct
from the corrected constant-replacement provenance above.

[Twelve independent original-source observations](../../coverage/semantics/heredoc-line-disagreement.json)
retain ten failures covering heredoc, nowdoc, empty bodies, indentation, CRLF
and binary prefixes, plus two quoted controls. Exact original bytes, checked
ASTs, native/runtime/helper commands, streams, statuses and fingerprints are
preserved unchanged. Correction `4297dadf` follows the scanner increment after
the opener; empty bodies follow the same line. All twelve original probes now
agree. The independent 526-source gate plus 25 negatives passed; `0270197e`
retains the twelve regular regressions and byte-preserving filename transport.
Missing or invalid ambiguous metadata rejects explicitly. The subsequent source compiler/pool bridge preserves these corrected lines;
no intentional divergence is selected.


## Qualified constant import prefixes: resolved source resolution

The first compiler/runtime bridge draft admitted `use Vendor\Package as A;
echo A\Missing;` while retaining the original constant name for runtime lookup.
PHP reports undefined `Vendor\Package\Missing`; the draft reports `A\Missing`.
The shared lexical resolver supplied the right name; the source consumer was
missing from that draft.

[Seven retained observations](../../coverage/semantics/qualified-constant-alias-disagreement.json)
include four admitted disagreements: an exact alias, ASCII case-folded alias,
preceding output and a partial array. Unmatched-prefix and unqualified names are
matching controls; fully qualified names remain an explicit Unsupported boundary.
Original source bytes, checked ASTs and exact native/runtime process observations
are preserved. The precise temporary guard `ff941f17` now returns Unsupported for the four
matching-prefix sources, suppressing execution, while both controls still agree.
The report retains these boundary observations separately from the original
failures. The guard alone established no source conformance. Source consumer `d5d28dc6`,
following byte-backend prerequisite `e2e31084`, now resolves all four original
failures. All seven original sources match native bytes and process status,
including preceding output before the missing-name error. The report preserves
original failures, temporary guard results and final resolution separately.
The independent 621-source +24-negative gate and namespace/helper campaigns
passed; no intentional divergence is selected.

## Bare break ending lines: resolved token context

The admitted out-of-loop `break` compiler rule uses the keyword start line.
PHP creates its AST node at the statement ending line, so `break` followed by
a newline and semicolon reports that later line. [Eight exact original-source
observations](../../coverage/semantics/break-line-disagreement.json) retain six
admitted mismatches (newlines, comments, CRLF, preceding output and a block) and
two controls. Both implementations suppress prior runtime output; the fatal
line differs. A narrow ending-line correction and permanent source regressions
are required before accepting the next source checkpoint. Numeric/expressive
break depths and valid loop targets remain a separate pending control milestone.

The first ending-line correction resolves those six cases but regresses closing
tags: `break ?>` followed by a newline has checked `endLine=2`, while PHP reports
line1. Six further observations (two admitted candidate regressions and four
controls) are preserved in the same report. A closing tag can consume a newline
without advancing the compiler line used for this statement. Ordinary AST end
line alone is insufficient; the checked terminator/compiler line must be retained.
The token-derived `statementTerminatorLine` correction `64e320b0` now resolves
all fourteen observations. Source checkpoint `8f1b47a2` passed 664 exact cases
+23 negatives, and the report retains the two original failure stages unchanged
beside their final resolution. Twenty transport profiles/200 checks, eight
additional original sources and five metadata controls passed, including encoded
sources and in-range edited line consumption. This establishes no valid-loop or
explicit-depth semantics; no intentional divergence is selected.

## Destructuring provenance: pending frontend preservation

Before source destructuring admission, [28 retained originals](../../coverage/semantics/destructuring-metadata-disagreement.json)
expose three transport losses. Recursive array-to-list conversion discards a
nested item's unpack flag, and converts `array()` to the same list kind as `[]`,
erasing distinct compiler errors. Leading omitted entries also lose their comma
line: two original sources have identical checked ASTs, including all positions,
but PHP reports lines 1 and 2. Preserve token-derived list creation context.

Independent frontend/checked-adapter and native-lint repeats reproduce all 28
streams and statuses. These observations establish the preservation prerequisite;
destructuring execution remains pending. Original records remain unchanged, and
no intentional divergence is selected.

Nested unpack preservation is now repaired by `d4706937`, forwarding the existing
item flag during recursive conversion. [Independent review](../../coverage/semantics/destructuring-unpack-review.json)
adds ten profiles/80 checks to 16 author profiles/96 checks; bounded syntax,
inventory and exact distribution patch reconstruction pass. Original syntax kind,
comma context and later compiler/runtime admission remain pending.

Original array syntax is now preserved by `09f33419`: converted lists retain
`destructuringArrayKind`, and printing restores long `array(...)` forms including
omitted slots. [Style review](../../coverage/semantics/destructuring-array-kind-review.json)
passes 35 author profiles/437 checks and 12 independent profiles/88 checks,
including original/printed native diagnostic families and edited-kind consumption.
First-hole token context is now preserved by `87341500`; the
[review](../../coverage/semantics/destructuring-first-hole-review.json) repeats 12
original line witnesses and adds 20 independent source/encoding profiles. Compiler
consumption remains pending. A separate [genuine-list phase witness](../../coverage/semantics/destructuring-list-hole-phase-disagreement.json)
records `list(array(,$x))=$a`: the frontend rejects empty array entries early,
while the pinned compiler rejects the long-array assignment target. `5c756e5e` repairs frontend acceptance and skipped-branch execution; reached
destructuring checks remain pending. No divergence is selected.

## Reference-wrapped false dimension fetch: resolved source mismatch

[Seven original FETCH/final-write observations](../../coverage/semantics/false-reference-fetch-review.json)
and [four nested-UNSET observations](../../coverage/semantics/false-reference-unset-review.json)
retain five prior mismatches and six controls. Reference wrappers survive singleton
unset, and generic dimension fetch through wrapped false skips the deprecation.
Final ASSIGN_DIM and UNSET_DIM still warn. Owner count alone could not recover
that distinction.

`3585707a` records wrapper identity independently of owners and roots. The
[review](../../coverage/semantics/reference-wrapper-review.json) confirms all eleven
unchanged originals now agree within 1,163 exact sources, with 79 independent
source comparisons and separate COW, lifetime and resumption checks. No intentional
divergence is selected; source collection and later mutation operators remain pending.


## Smart string comparison overflow: resolved draft defect

The [unchanged four original observations](../../coverage/semantics/comparison-overflow-draft-disagreement.json)
retain two draft disagreements and two controls. Twenty significant integer-prefix
digits can set overflow before an exponent rescales the float into range. Preserving
that scanner history repairs smart string comparison in `0e065cc6`; all four now
agree through original-source execution. [Independent comparison review](../../coverage/semantics/comparison-review.json)
records source and helper boundaries separately. No intentional divergence is selected.

## Expanded array-omission phase gaps: independently confirmed, repair pending

[Retained originals](../../coverage/semantics/frontend-phase-originals-review.json)
add 16 genuine-list and six ordinary-array omission sources, including native-valid
skipped branches currently rejected by the frontend. All 22 original captures are independently repeated. Genuine-list conversion
`5c756e5e` now preserves nested array targets until compiler visitation. Its
[review](../../coverage/semantics/list-target-review.json) validates 20 skipped
source cases and explicitly retains 14 reached originals as Unsupported. Ordinary
Array_ omission representation remains open; this is not full destructuring admission.

## Dynamic callable invocation lines: repaired transport prerequisite

[Eight original captures](../../coverage/semantics/incdec-call-line-original-review.json)
include two identical complete checked ASTs whose pinned write-context errors use
lines 3 and 2. Dynamic calls take their compiler creation line from the opening
argument token, which ordinary node positions cannot recover. `c6a7d67d` preserves
that integer context. [Independent review](../../coverage/semantics/callable-line-review.json)
validates checked transport and 24 additional native error lines; compiler consumption and update source admission now pass `7d5718fb` and its
[independent source review](../../coverage/semantics/incdec-review.json).

## Update array prepass: retained draft boundary

[Three exact original observations](../../coverage/semantics/incdec-prepass-originals.json)
retain two Unsupported draft results for updates in array values/keys and one
matching skipped-branch control. Constant-expression traversal must stop at all
four update forms without visiting their children. The corrected private draft
adds those explicit barriers; `7d5718fb` now admits all three unchanged originals
within the independently audited 1,484-source campaign. Unsupported was
not conformance success, and no intentional divergence is selected.

## Ordinary computed-name writes: admitted wrapper regression

The wrapper-identity correction accidentally reused reference acquisition for an
ordinary computed-name write: `$n="a";$$n=false;` marked `$a` as a reference.
Later nested dimension mutation then omitted a required false-to-array deprecation.
[Four author originals](../../coverage/semantics/wrapper-dynamic-write-originals.json)
and [28 independent observations](../../coverage/semantics/wrapper-dynamic-write-original-review.json)
retain three original mismatches, nine additional mismatches and sixteen controls.
Existing references, singleton history and copied assignment results distinguish
ordinary writable fetch from actual reference acquisition. Correction `84d70299` separates initialized writable fetch from actual reference
acquisition. [Independent resolution](../../coverage/semantics/wrapper-dynamic-write-review.json)
confirms all 28 originals and 12 additional source controls, 49 marker/state checks
and the prior wrapper/ownership gates. Full source refresh shares the following
update campaign; previous wrapper validation remains historical.
No intentional divergence is selected.

## Computed-name update access lines: retained draft defect

[Seven exact original observations](../../coverage/semantics/incdec-computed-line-originals.json)
retain four draft line mismatches and three controls. An ordinary computed-name
RW fetch diagnoses an absent variable at its own line; the following missing array
key uses the dimension line. Computed `$this` similarly raises its rebinding error
at the root fetch line, after any forced key expression has run. Direct compiled
variables use the dimension opcode's line instead. Both lines already exist in
checked access descriptors; runtime correction `7d5718fb` now preserves both. All seven originals pass in the
[independently audited source gate](../../coverage/semantics/incdec-review.json),
with 71 additional context replays. No intentional divergence is selected.

## Compound draft corrections: follow the pin

Independent review found an incorrect early `$this` rejection in the unpublished
compound compiler draft. Unlike assignment and reference rebinding, compound
updates compile `$this` normally; a global direct fetch then raises the missing
object-context error. An invalid RHS can fail during compilation first.
[72 originals](../../coverage/semantics/compound-this-originals.json) preserve
both native phases and the rejected draft's exact completion trace. The correction
uses `zend_compile_compound_assign` and `zend_compile_simple_var`; no engine
divergence is intended. Code `63028b5a` removes the incorrect static guard;
[independent resolution](../../coverage/semantics/compound-review.json) passes all
original bytes in the 2,639-source campaign.

A second draft error used the final compiler line for a delayed dimension opcode.
[Three runtime originals](../../coverage/semantics/compound-line-runtime-originals.json)
retain a native arithmetic warning on line 3 versus the draft's line 5;
[72 compiler controls](../../coverage/semantics/compound-line-originals.json)
separate final compiler context from the earlier target opcode's line. The parent
expression descriptor correctly retains final compiler context. Final DIM compound
conversion and delayed RHS reads must use the captured target opcode line, while
forced RHS expressions retain their own diagnostics. Code `63028b5a` preserves
that split; the current source/raw audit resolves all original failures unchanged.
`zend_delayed_compile_end` explains the distinction.

The first broad compound run stopped because a logical source ID containing `/=`
was used as a filesystem path. The [original traceback](../../coverage/semantics/compound-path-original.json)
is retained as an infrastructure failure. Unique ordinal paths now materialize
every selected source before execution; [independent checks](../../coverage/semantics/compound-path-review.json)
cover all catalog IDs and ten hostile IDs. The corrected full campaign passes; no
interrupted run was counted as semantic agreement.
