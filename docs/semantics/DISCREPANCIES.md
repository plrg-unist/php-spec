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
while the pinned compiler rejects the long-array assignment target. Repair its
phase before source destructuring admission; no divergence is selected.

## Reference-wrapped false dimension fetch: open source mismatch

[Seven independently repeated originals and controls](../../coverage/semantics/false-reference-fetch-review.json)
show three admitted mismatches. After `$r=&$a` wraps false `$a`, nested dimension
fetch and `$x=&$a[0]` omit the pinned false-to-array deprecation, but the model
emits it. The difference survives `unset($r)`, so live owner count cannot replace
reference-wrapper history. Final dimension assignment still warns in both
implementations. Preserve that operation distinction when repairing state.

[Four nested-UNSET originals](../../coverage/semantics/false-reference-unset-review.json)
independently confirm two more mismatches and two controls: intermediate UNSET
fetch suppresses the warning through a wrapper, while final UNSET_DIM still warns.

This existing source discrepancy is the immediate corrective prerequisite after
the bounded comparison checkpoint; comparison results do not establish a
globally clean runtime. Original observations remain unchanged. No intentional
divergence is selected.


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
skipped branches currently rejected by the frontend. All 22 captures are independently repeated with exact native lint and frontend
outcomes. Genuine-list conversion and ordinary Array_ omission representation
remain separate open repairs; first-hole metadata is reviewed independently.
No phase repair or runtime admission is claimed.
