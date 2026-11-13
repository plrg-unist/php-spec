# Scalar and string dimensions

`44-dimension-read.watsup` supplies pure runtime R-fetch helpers. Delayed source dimension reads now delegate to it after resolving their base.
The ordered compiler separately uses its string constant-read leaf.
Array containers delegate to the existing array-read rules. Reference assignment and
acquisition cover writable array elements. String writes update their captured
locations; string-offset reference and nested fetches produce their PHP errors.

`$dimension_read(state, container_value, key_operand, line)` returns state with
`RESULT`, ordered `EVENTS` and `COMPLETION`. It delegates arrays to `$array_read`.
Scalar containers resolve the key to preserve undefined-variable diagnostics,
without applying array-key conversion, then warn and return null. Boolean names
in that warning are `true` or `false`. String containers return one byte, including
negative indexing from the end. Out-of-range offsets warn and return an empty
string. Integer numeric text is accepted; trailing text warns, with C-string
truncation at NUL. Numeric text classified as floating-point is a TypeError.
Float/null/bool keys issue the string-offset cast warning; float conversion then
uses the silent integer operation, without a second precision/NAN/INF diagnostic.

The source anchors are pinned `Zend/zend_execute.c`:
`zend_fetch_dimension_address_read`, `zend_illegal_string_offset`, and
`Zend/zend_API.c::zend_zval_value_name`. The helper consumes already captured
container values and resolves delayed/reference key operands. It does not prune
inside helpers or invoke callbacks. Source callbacks use the separate continuation
below; object dimensions, isset/empty, list and write contexts retain their own rules.

Module425 stages ordinary string R-offset cast, leading integer text and bounds
Warnings. A cast callback can change the live primitive offset while the selected
old carrier survives; float conversion stays silent. Interned carriers and
authenticated owning temporaries survive independently. A borrowed REQUEST carrier survives when its
exact identity remains in the same selected live ordinary CV cell, marked or
unmarked. If that selection changes, a different current name may keep the
original cell, or a different ordinary unmarked CV may retain the exact
authenticated non-NUL header. Current name lookup and live-cell capture establish
these owners; shadowed rows, equal bytes with another identity and immutable
STRINGDATA alone do not qualify. The [retained-carrier review](../../coverage/semantics/string-offset-retained-carrier-review.json)
records ordinary return and supplied-exception discard, with unchanged destination
on throw. A dropped borrowed carrier outside the closed `KEY_CV` release contour
below retains Unsupported.
Neither the base-cell nor key-cell locator becomes a heap root.

A dedicated base capture admits an ordinary marked CV holding valid non-NUL
interned bytes, with the same liveness and constraint fences. It saves the
dereferenced immutable header before the Warning: writing `XYZ` through a base
alias leaves the selected `abc` available, while the live key can become `2` and
select `c`. A supplied exception preserves its identity and the destination `99`.
The [reference-base review](../../coverage/semantics/string-offset-reference-base-review.json)
keeps two original source agreements, separate author/peer state checks and three
derived affected-entry projections distinct. Generic capture, keeper, key and
root rules stay unchanged.

Authenticated non-NUL REQUEST bases use that bounded reference capture. Their
current-cell provider proof and the existing ordinary-keeper alternative use
the same current capture to partition readiness. A handler can keep the exact
header in the selected marked cell; replacing that referent can instead use a
different live ordinary unmarked CV retaining the saved identity. The
[referenced REQUEST review](../../coverage/semantics/string-offset-reference-request-base-review.json)
separates two same-header source agreements from derived keeper-composition and
wrapper-timing checks. Removing the selected name can now use a current alias of
the original cell, authenticated by the same base capture. Plain `$GLOBALS`
unset leaves that marked cell and exact REQUEST header live through one surviving
alias. The [same-cell alias review](../../coverage/semantics/string-offset-reference-alias-keeper-review.json)
separates two new source agreements, author/peer AL cuts and two affected helper
projections. STRINGDATA alone supplies no owner. Different marked keeper cells,
dead aliases and wider ownership histories remain partial; roots stay unchanged.

An ordinary marked primitive reference key can use null, bool, bounded int or a fitting
float. Its key-only capture checks the current binding, same live cell and prior
constraint fences; the generic base and keeper captures stay unchanged. After a
cast Warning, conversion reads the live referent while the key still selects
that cell. The [reference-key review](../../coverage/semantics/string-offset-reference-key-review.json)
separates two new interned-base source agreements from the affected REQUEST-base
entry/resume fixture. Existing REQUEST provider proofs compose without gaining
base or lifetime authority.

Marked floats with range diagnostics remain partial: references created during
the handler can use a warning-capable converter, while an initially unwrapped
DOUBLE uses the silent path. The descriptor does not preserve that distinction.
Key rebinding/removal, constrained cells and NUL combinations retain their fences.

For valid non-NUL interned base and key strings, leading integer text such as
`"1x"` keeps the integer computed before its `Illegal string offset` Warning.
Completion reads the old bytes even if the handler replaces the base and unsets
the key. A subsequent bounds Warning uses that same integer and old string length;
the saved text authenticates the exact index. The [leading-text review](../../coverage/semantics/string-offset-leading-text-review.json)
records the first Warning, ensuing bounds callback and supplied-exception cleanup.
Initially marked ordinary reference keys now enter this same fixed-index branch
when both base and leading-text key are valid non-NUL interned strings. A handler
writing `2` through the key alias still reads `b` from saved index `1`; removing
both key names before a supplied throw leaves the original exception and
destination intact. The borrowed key cell can retire after capture. The
[referenced leading-key review](../../coverage/semantics/string-offset-reference-leading-key-review.json)
keeps two source agreements, separate author/peer AL cuts and the derived old CAST
guard distinct. Current text remains refused on the live primitive CAST path.

An initially unmarked ordinary CV can also supply authenticated non-NUL REQUEST
leading text against a valid non-NUL interned base. Acquisition checks its current live cell;
the saved receipt then authenticates immutable bytes and the fixed integer after
the handler overwrites or unsets that key. Neither the formatted Warning message
nor the saved integer needs a surviving key owner. Source and phase checks retain
the same integer for a later bounds Warning. The
[REQUEST leading-key review](../../coverage/semantics/string-offset-request-leading-key-review.json)
separates two source agreements, author/peer state cuts and derived affected-source
checks.

Initially marked ordinary reference keys also acquire valid non-NUL REQUEST
leading text against a valid non-NUL interned base. Key capture keeps its current
binding, liveness and constraint checks; the existing saved receipt then survives
alias writes and removal of both key names without adding an owner. The
[referenced REQUEST leading-key review](../../coverage/semantics/string-offset-reference-request-leading-key-review.json)
records two new source agreements and separate state and derived entry checks.
Live REQUEST text remains refused on the ordinary CAST path. REQUEST leading
bases use the bounded owner proof below; constrained cells and wider producers
retain their boundaries.

An ordinary base CV holding a valid non-NUL REQUEST string and an ordinary key
CV holding valid non-NUL INTERNED leading text use a separate acquisition and
saved-index receipt. Current provider and retainer
proofs keep the selected header available when a handler replaces the base CV.
Two source comparisons retain it through a different ordinary keeper; a derived
composition also checks the existing same-selected-cell alias proof. Source
validity records the saved meaning, while readiness requires a current owner.
Losing that owner produces explicit Unsupported on normal return or pending
Throwable discard. Once bounds have been selected, completion remains fixed
and owner-free. The [REQUEST leading-base review](../../coverage/semantics/string-offset-request-leading-base-retainer-review.json)
keeps source, state and derived affected-front cuts distinct.

The same receipt now admits ordinary or marked CVs for both the REQUEST base
and its valid non-NUL INTERNED or REQUEST leading-text key. Acquisition uses the
existing base/key captures and preserves actual cell and header identity,
including a single selected cell shared by four names. The index and message remain fixed
before the callback; both selected cells may retire before a supplied throw.
A distinct ordinary keeper can retain the old base after all aliases change.
Normal and Throwable lost-owner paths still return Unsupported. The
[carrier-matrix review](../../coverage/semantics/string-offset-request-leading-carrier-matrix-review.json)
keeps four source agreements, author/peer state cuts and the finite affected
ingress check separate. Constrained/direct-reference operands, NUL combinations,
computed/owning key producers and wider owner histories remain partial.

Literal leading-text keys also admit ordinary or marked REQUEST-base CVs without
a key cell. The new receipt requires the actual string-literal node and its exact
decoded bytes.
The existing current owner proof preserves old bytes through base replacement or
retirement. A genuine out-of-range literal also preserves the fixed empty result
when its later bounds callback removes the final keeper.
The [literal-key review](../../coverage/semantics/string-offset-request-base-literal-leading-key-review.json)
keeps its three source agreements, author/peer AL cuts and historical folded-source
refusal separate.

A disjoint receipt now admits actual CONCAT keys whose finite tree contains only
string-literal leaves and CONCAT nodes. Their recursively decoded bytes must equal
the compiled INTERNED key exactly; no key cell or owner is added. The same current
header owner protects normal and supplied-throw completion, while a genuine later
bounds callback may remove the final keeper before the fixed empty result.
The [CONCAT-key review](../../coverage/semantics/string-offset-request-base-concat-leading-key-review.json)
keeps three new source comparisons and separate author/peer AL cuts distinct.
The old folded control is promoted using fresh CONCAT coverage; its original
integer/float refusals retain their historical cuts.

Numeric-leaf CONCAT keys now authenticate the actual child's compiled precision
through the existing pure literal converter. The disjoint receipt requires the
old string-only byte helper to refuse, then matches the converted bytes exactly
to the saved INTERNED key. Rounded float leaves retain compiled precision 14 even
after source code sets live precision 17 before the offset read. The same owner,
exception and fixed later-bounds laws apply.
The [numeric-CONCAT review](../../coverage/semantics/string-offset-request-base-numeric-concat-leading-key-review.json)
keeps four original source comparisons, two new initial checkpoints and separate
author/peer AL cuts distinct. Earlier integer/float controls are promoted using
fresh coverage. Other computed or owning keys, constraints, NUL and wider owner
histories remain partial.

Bool/null CONCAT keys now restore their compiled INTERNED identity from exact
source and pool facts. Each ConstFetch uses its own resolved compiler value;
each CONCAT must match its own raw pool bytes. Parser-literal rules stay narrow.
The same saved-index, current-owner, supplied-throw and fixed later-bounds laws
apply. The [special-CONCAT review](../../coverage/semantics/string-offset-request-base-special-concat-leading-key-review.json)
keeps three source agreements, initial ENV/pool checkpoints and separate author,
peer and compiler-only cuts distinct, including the preserved fixture failure.
Other computed leaves and missing descendant CONCAT facts remain partial.

Integer literals now use the existing pure decimal formatter in those same
pool-authenticated CONCAT trees. Resolved bool/null facts, per-CONCAT pool bytes
and all saved-history/owner rules remain unchanged. The
[integer-CONCAT review](../../coverage/semantics/string-offset-request-base-integer-special-concat-leading-key-review.json)
keeps three source agreements, fresh initial checkpoints and author/peer cuts
separate; only the affected fresh float refusal replaces the old integer control.
Other computed leaves and missing descendant facts remain partial.

Quiet float literal leaves also use their own compiled precision and the existing
pure formatter in those pool-authenticated trees. A runtime precision change
does not rewrite the saved key. The [float-CONCAT review](../../coverage/semantics/string-offset-request-base-float-special-concat-leading-key-review.json)
keeps three rounded compile14/live17 source comparisons, initial checkpoints and
author/peer state cuts separate. Float-valued ConstFetch, other computed leaves,
missing descendant facts and wider ownership remain partial; owner and phase
laws are unchanged.

Unary `+` and `-` immediately around integer or float literals also require their
own compiled fact to match the existing pure unary operation. Quiet formatting
uses that node's compiled precision, while each CONCAT retains its exact pool
check. The [unary-CONCAT review](../../coverage/semantics/string-offset-request-base-unary-numeric-special-concat-leading-key-review.json)
keeps four compile14/live17 originals and separate initial/author/peer state cuts.
Negative indices retain the original character or fixed later bounds.

Finite nested numeric unary chains additionally authenticate each actual child,
its own numeric compiler result and matching compiled precision. Every step uses
the existing pure unary operation and quiet formatter; CONCAT pool checks and
borrowed ownership are unchanged. The [nested-unary review](../../coverage/semantics/string-offset-request-base-nested-unary-numeric-special-concat-leading-key-review.json)
keeps four fresh originals, initial420, corrected author627/105-derived and peer
833/374-derived plus41 compiler-only checks separate. The original fixture binding
failure and three unrun fixtures retain zero credit. Warningful string unary,
binary-expression children, float-valued ConstFetch, missing descendant facts and
wider ownership histories remain partial.

Unary chains also admit actual fully numeric string-literal leaves. Decoded bytes
must coerce without a Warning, and the own compiled result must match the existing
pure unary operation before quiet formatting at compiled precision. The explicit
quiet-coercion guard also rejects warningful text in an already abrupt state.
The [numeric-string unary review](../../coverage/semantics/string-offset-request-base-numeric-string-unary-special-concat-leading-key-review.json)
keeps four fresh compile14/live17 originals, pre432, author639/105-derived, peer
909/438-derived and affected compiler95 at their separate cuts. Two peer fixture
failures retain zero credit; only the affected compiler checks are repeated after
the second correction. Warningful strings, nonliteral string children, binary
children, float or unary ConstFetch and wider ownership remain partial.

Direct integer ConstFetch leaves now use their own compiler-proved PINT and the
existing decimal formatter in those CONCAT trees. Source names retain compiler
resolution; no runtime name lookup or spelling table is added. Four global,
imported and fully qualified originals cover both ordinary selections, supplied
throw and genuine positive later bounds. The [integer-constant review](../../coverage/semantics/string-offset-request-base-integer-const-special-concat-leading-key-review.json)
keeps source4, pre304, author511/105-derived and peer631/264-derived plus41 compiler
checks separate. Compiled pools retain their internal proof boundary; these checks
do not validate arbitrary forged pools. Float/unary ConstFetch, binary children
and wider ownership remain partial.

Quiet bare ADD/SUB/MUL/DIV children now compose with those authenticated CONCAT
trees. Each actual arithmetic node and child needs its own compiled fact; child
certificates, both quiet numeric conversions, a successful pure numeric result
and the exact existing operation must agree before formatting at compiled
precision. A parser-literal numeric CONCAT operand authenticates its literal
bytes without requiring omitted descendant facts. The
[arithmetic review](../../coverage/semantics/string-offset-request-base-arithmetic-special-concat-leading-key-review.json)
keeps four originals, corrected initial proofs, author657/105-derived and
peer862/367-derived plus100 compiler checks separate. Saved indices, real current
owners, supplied throw and fixed later bounds retain their existing laws.
Unary-over-constant/arithmetic and wider producers were outside this cut.

Once an out-of-range offset is selected, completion returns the fixed empty
string even if the bounds callback unsets both operands. A cast-handler throw
still converts the live key; a leading-text handler throw uses the saved integer.
Both check old bounds: an eligible registered handler suppresses the remaining
Warning, while an absent handler permits its default
display before the original Throwable unwinds. Source validity survives callback
writes and retired cells, separately from cast readiness. Other REQUEST text histories,
other text-entry Warnings, undefined or other marked text keys, constrained locators and wider
string-owner histories remain partial. The [string-read review](../../coverage/semantics/string-offset-read-warning-review.json)
retains source and independent reached-state evidence, including the zero-credit
borrowed-carrier release control.

Compiled literal bases now satisfy that existing R-read source certificate through
an origin-aware `233` arm: the captured interned value, actual base child, raw
pool bytes and existing literal producer must agree. Raw, CV, reference and
computed-base arms stay unchanged; no carrier rewriting, locator, provider, root
or release rule changes. Two exact sources cover accepting cast/bounds handlers
and live cast-key versus fixed bounds behavior. The separate 93-condition AL
recipe checks the actual resume, source/identity refusals and unchanged ownership.
The [literal-base review](../../coverage/semantics/string-literal-base-review.json)
keeps the two original Unsupported baselines at zero credit and retains that
defined-key cut. Other handler effects and wider owner histories remain partial.

An initially undefined ordinary key CV on a literal non-NUL interned base now
keeps its authenticated `KEY_CV` receipt after the Undefined Warning. That receipt
forces the cast Warning even if the first handler defines an integer key. Resume
then reads the current null, bool, int or float CV, or silently uses NULL if it is
still missing.
An out-of-range index is fixed before its bounds callback. Two exact SL originals
cover key `1` to `5` to `0` with a fixed empty result, and an untouched CV returning
`a` with only the Undefined and Cast messages. A source-reached AL recipe checks
126 conditions, including 28 derived controls, through the three genuine
continuations. The [undefined-CV ledger](../../coverage/semantics/string-offset-undefined-cv-review.json)
retains the original producer-continuation refusal at zero credit. Generic
retention and root rules stay in use; REQUEST/marked keys, other base producers,
abrupt-handler and wider lifetime histories remain partial.

That initially undefined CV continuation also admits a current marked,
unconstrained null, Boolean, signed-64-bit integer or fitting binary64 float.
The existing key capture checks the fresh current name and physical/logical cell,
release state and three constraint exclusions. Explicit primitive and quiet-float
guards keep wider String captures separate. No saved KEYCELL is acquired or rooted.
Two exact private508 SL originals at `86ac2e2c2` reuse native observations once:
a handler-created integer selects `c`, while a real global reference replacement
selects `d` from its current float rather than the retired integer cell.
Author AL112 (64 derived) and independent AL108 (56 derived) retain separate source0
cuts, without a unique aggregate. The [marked-current-CV review](../../coverage/semantics/string-offset-current-marked-cv-review.json)
preserves the genuine 47-condition pre-code checkpoint, Unsupported baselines and two
compiler-only failures at zero credit. Only one old marked-PINT1 refusal is
promoted and checked in the new fixtures; the old AL126 cut is not replayed.
Actual `e4835ad9d`/508 joined loading passes in 15.118756066 s with zero source
credit; it does not renew the private source/state cuts.
Wider marked arrays, constrained cells and broader base/abrupt/lifetime contexts
remain partial. Generic capture, conversion, source, provider, retainer and root
rules, and String `KEY_NULL` capture/history remain unchanged.

Current marked strings also admit valid non-NUL INTERNED and authenticated
REQUEST carriers. The unchanged base-capture helper checks the fresh current
name, marked cell, physical/logical liveness, release state and constraint exclusions.
An explicit carrier/non-NUL guard keeps this admission bounded. Conversion is
silent after the mandatory CAST Warning; it does not reenter initial string-key
validation. REQUEST conversion requires the exact current carrier, and registry
bytes alone add no owner. Two exact SL originals at `6f84f771a`/private508 reuse
native observations once: INTERNED `2tail` selects `c`, while true global reference
replacement with runtime REQUEST `noise` selects `a` instead of the old integer.
Author AL116 (71 derived) and independent AL133 (81 derived) retain separate
source0 cuts. The [marked-string review](../../coverage/semantics/string-offset-current-marked-string-cv-review.json)
keeps the genuine 52-condition pre-code checkpoint and original Unsupported baselines separate.
A fixture-name collision reached AL and failed; its label-only correction retries
only that fixture. Seven prior admission/conversion refusals are promoted and
their exact replacements checked in the new fixtures. The formerly negative ARRAY
controls join the marked-array promotion checks below, without old-protocol replay
or a unique aggregate. Actual `f800f4302`/508
joined loading passes in 15.710914590 s/source0 without renewing private cuts.
Marked current raw/NUL strings, wider arrays, constraints and broader base/abrupt/lifetime
contexts remain partial.
Generic capture, converter/API/callers, source/provider/retainer/root/schema laws
and String `KEY_NULL` saved histories stay unchanged.

After the initially undefined CV path, current marked ARRAY keys use the existing
finite entry domain: DIRECT scalars,
primitive or authenticated non-NUL string ALIAS cells, and one quiet level of DIRECT
or ALIAS child arrays, including mixtures. Fresh VARIABLE lookup authenticates the
initialized marked cell, physical/logical cell and table, release exclusions and
three absent constraints. Conversion reads only outer empty0/nonempty1 and acquires
no owner, copy or COW. Two exact SL originals at `1ddec481d`/private508 reuse native
observations once: the empty array selects `a`; a four-entry mixture selects `b`,
not raw-count `e`, old-integer `d` or child/payload `a`.
Author AL101 (51 derived) and independent AL149 (79 derived) retain separate source0
cuts. The [marked-array review](../../coverage/semantics/string-offset-current-marked-array-cv-review.json)
records the authentic 68-condition graph checkpoint: one current wrapper owns the
outer table once, the repeated leaf has two owners, and the shared child table has
three owners from its pool root, cell and DIRECT edge. Fifteen old expectations
across eleven fixtures are promoted and their replacement classes checked in the
new fixtures, without old-protocol replay or a unique aggregate. Actual
`972cd9882`/508 joined loading passes in 15.123888404 s/source0, separately from
the private source/state cuts. Deeper/cyclic,
object or constrained payloads, constrained current cells and broader base/abrupt/
lifetime contexts remain partial. Initial ARRAY offsets and generic capture,
converter/API/callers, source/provider/retainer/root/schema laws remain unchanged.

After that initially undefined CV path, a current ordinary unmarked non-NUL
interned string now uses the silent string-to-integer cast, including leading
text, nonnumeric zero and numeric-text saturation. It does not reenter the
initial string-key validator or emit an `Illegal string offset` Warning.
Two exact SL originals cover first-handler `"1"` followed by cast-handler
`"2tail"` selecting `c`, and no first write followed by `"noise"` selecting `a`.
The new source-reached AL recipe passes 97 conditions, including 23 derived
controls for conversion and source/carrier refusals. The
[current-string-CV review](../../coverage/semantics/string-offset-current-string-cv-review.json)
keeps these cuts and earlier failures separate; the old AL126 cut is not renewed.
Generic offset, capture, phase, provider, retainer and root rules stay unchanged.
Marked current keys, NUL, abrupt handlers and wider base/lifetime
contexts remain partial.

Authenticated non-NUL REQUEST strings in that current ordinary CV now share the
silent conversion. The state-aware helper requires the exact carrier from the
live selected unmarked cell; registry bytes alone add no owner. Two exact sources
use two nonempty CVs for runtime concatenation: `"2tail"` selects `c`, while
`"noise"` selects `a`. Author AL109 and independent AL80 retain separate cuts,
each with 34 derived controls, including stale identities, dead or shadowed cells
and source refusals. The [current-REQUEST-CV review](../../coverage/semantics/string-offset-current-request-cv-review.json)
keeps source comparisons, state checks and joined loading distinct. Generic
offset/capture/source/phase/provider/retainer/root rules stay unchanged. Marked,
constrained, NUL and other current value kinds, broader bases and abrupt/lifetime
histories remain partial.

That initially undefined CV receipt also admits current ordinary arrays with
finite DIRECT scalar entries. Empty arrays silently convert to index 0 and
nonempty arrays to index 1 after the mandatory cast Warning. The exact current
CV must capture an ordinary live cell and select an in-range, physically
allocated, logically live HARRAY. Retained array metadata or a different live
table cannot authorize conversion. Scalar payloads are classified by kind and
never read or coerced. Existing pool/CV sharing needs no copy, callback or new
owner for this immediate count read.
Two exact originals agree at `f02e8d7a6`/private508, reusing each native once.
Author AL95/43-derived and independent AL85/35-derived retain separate source0
cuts. The [current-array review](../../coverage/semantics/string-offset-current-array-cv-review.json)
keeps the finite checkpoint, corrected helper count and original failures
separate, without a unique aggregate. Initial ARRAY offsets retain their illegal
offset path. Marked/constrained current keys, wider entries, broader
bases and abrupt/lifetime histories remain partial.

A separate nonempty ALIAS-only route admits initialized null, Boolean, signed
64-bit integer and binary64 reference payloads. Each actual marked reference cell
must satisfy the existing plain-cell validator and remain logically live; typed,
coercion and parameter-backing constraints stay excluded. The converter uses the
array's nonempty count, while admission only validates the referent domain.
Repeated references preserve their separate HARRAY-to-HCELL edges, and conversion
adds no owner or payload conversion. The earlier DIRECT predicate and converter
API remain unchanged.
Two exact originals agree at `6b73bf7cb`/private508 with native-once reuse: a
zero-valued referent and two entries sharing false both select index 1, not the
referent truth or raw element count. Author AL106/49-derived and independent
AL117/58-derived retain separate source0 cuts. The
[alias-entry review](../../coverage/semantics/string-offset-current-array-alias-cv-review.json)
keeps the genuine pre-code checkpoint and parser-only peer fixture failure
separate. NUL/raw string or wider reference payloads, constrained
cells, initial ARRAY offsets and broader lifetime contexts gain no route.

Finite DIRECT/ALIAS mixtures now compose those existing per-entry guards in
order. The exact current CV/table authority and count-only conversion remain;
neither payloads nor reference edges are copied, converted or released. The old
homogeneous predicates and converter API remain literal. Two exact originals at
`12eeccb6f`/private508 reuse native observations once: `[0, &$false]` and three
entries `[&$false, false, &$false]` both select index 1. The latter distinguishes
nonempty conversion from false payloads and the raw entry count.
Author AL112/61-derived and independent AL124/64-derived retain separate source0
cuts. The [mixed-entry review](../../coverage/semantics/string-offset-current-array-mixed-cv-review.json)
keeps the pre-code 48-condition actual checkpoint and Unsupported baselines at
zero credit. Only two earlier derived mixed refusals are promoted, with both
replacement shapes checked; no historical campaign is replayed or renewed.
Initial ARRAY offsets, wider ALIAS payloads or constraints, object DIRECT entries,
marked current keys and broader base/abrupt/lifetime contexts remain partial.

Current arrays also admit non-NUL INTERNED and authenticated REQUEST strings in
initialized marked unconstrained reference cells. Admission requires the existing
carrier check and physical/logical cell liveness; registry identity alone adds no
owner. The primitive ALIAS helper stays literal. Conversion still uses only array
nonemptiness and preserves the cells, carriers and repeated edges.
Two exact originals at `5e8067ef3`/private508 reuse two native observations once:
an INTERNED zero string and a repeated REQUEST `2tail` string both select index 1,
which differs from payload conversion and the latter's three-entry count.
Author AL90/41-derived and independent AL107/51-derived retain separate source0
cuts. The [string-payload review](../../coverage/semantics/string-offset-current-array-string-alias-cv-review.json)
keeps the genuine 54-condition pre-code REQUEST checkpoint, Unsupported baseline
and peer pre-AL binding-order failure at zero credit. Only the affected peer fixture
is retried; four old string-payload refusals are superseded without old-suite replay.
NUL/raw ALIAS string payloads, wider owning or constrained referents and broader
current-CV/base/abrupt/lifetime histories remain partial; initial ARRAY offsets
stay illegal.

DIRECT child arrays now admit one quiet level of existing DIRECT scalar entries.
Each child must be an in-range, physically allocated, logically live HARRAY;
empty, pooled and shared children need no uniqueness or mutability condition.
The exact current CV still selects the outer table. Conversion reads its
nonempty count and preserves every real child edge without COW or new owners.
Two exact originals at `3cb7c72f4`/private508 reuse two native observations once:
`[[]]` and `[0, $empty, $empty]` both select index 1, differing from an empty
child's conversion and the latter's raw three-entry count. Author AL91/38-derived
and independent AL132/71-derived retain separate source0 cuts, with full state/
heap preservation and budget checks. The
[child-array review](../../coverage/semantics/string-offset-current-array-child-cv-review.json)
keeps the genuine 50-condition pre-code repeated-edge checkpoint and Unsupported
baselines at zero credit. No old assertion is promoted or campaign replayed.
Actual `dc82089bb`/508 joined loading passes in 15.554452909 s with zero source
credit; it does not renew the private source/state cuts.
Deeper/recursive child arrays or object DIRECT entries, wider ARRAY-valued ALIAS
cells, constrained current keys and wider base/abrupt/lifetime contexts remain
partial; initial ARRAY offsets and String `KEY_NULL` history keep their existing
paths.

Initialized marked unconstrained ALIAS cells can now hold the same quiet child
arrays. The existing reference validator and logical HCELL proof authenticate
the actual cell; property-source, coercion and parameter-backing metadata remain
excluded. A cell owns its child once regardless of the number of outer ALIAS
entries. The outer table alone supplies the converted count; no value, edge or
owner changes. Two exact originals at `02c195e73`/private508 reuse two native
observations once: `[&$empty]` and `[0, &$empty, &$empty]` both select index 1.
Author AL91/36-derived and independent AL145/76-derived retain separate source0
cuts. The [reference-child review](../../coverage/semantics/string-offset-current-array-alias-child-cv-review.json)
keeps the genuine 61-condition pre-code checkpoint and Unsupported baselines at
zero credit. Its actual repeated cell has two outer owners but one child edge;
singleton/triple wrappers and distinct-cell controls preserve that distinction.
Only two prior singleton-layout refusals are promoted, with their replacement
checked in the new fixture; the old 132-condition cut is not replayed or renewed.
Actual `508c467b6`/508 joined loading passes in 15.919208375 s with zero source
credit; it does not renew these private cuts.
Deeper/reference/object child entries, constrained cells or current key CVs and
wider base/abrupt/lifetime contexts remain partial. Initial ARRAY offsets and
String `KEY_NULL` capture/history keep their existing paths.

Initially undefined `KEY_CV` reads also admit a source-authenticated VARIABLE
base with a selected valid non-NUL INTERNED header. The header precedes Undefined
and survives base-name replacement or removal, even after the original cell
retires. Two caller-local receipt/source arms preserve that header without
inventing a saved BASECELL; KEYCELL also stays absent. Mandatory CAST then uses
the unchanged quiet current-key domain: primitives, authenticated non-NUL strings
and finite arrays, including marked cells. Old source/receipt arms, generic
`key_read_valid`, current-kind, capture, provider, retainer and root bodies remain
literal, as do String `KEY_NULL` saved histories.
Two exact originals at `da91ad611`/private508 reuse native observations once:
`abc` survives replacement by `XYZ` and selects `c`; `abcde` survives a true
reference replacement by integer99 and selects `b` from the current array.
Author AL154/77-derived, independent AL153/63-derived and the genuine precode50
full-state/heap checkpoint retain separate source0 cuts. One old structural
receipt refusal gains a positive replacement while wrong-source authority stays
false, without replaying the old126 cut. The
[variable-base review](../../coverage/semantics/string-offset-variable-base-cv-review.json)
keeps those cuts separate. Actual `c9c770e1a`/508 joined loading passes in
15.467628574 s/source0 without renewing them. Wider REQUEST bases, other abrupt
handlers, constraints and wider producers/lifetimes remain partial.

Initially undefined `KEY_CV` reads also admit a non-NUL REQUEST base retained by
a distinct ordinary unconstrained CV. The exact current keeper is required before
mandatory CAST and again after its callback; immutable registry bytes add no owner.
Source authority survives keeper removal; loss outside the closed release contour
below reports Unsupported, while later bounds completion stays fixed and owner-free.
BASECELL and KEYCELL stay absent, even when the original base cell physically retires.
Two exact originals at `b6930367d`/private508 reuse native observations once:
saved `abcde` survives replacement by integer99 and selects `e` from current key4;
saved `abc` uses old bounds8 despite a current longer string. Author AL126/46-derived,
peer AL184/55-derived and authentic precode67/full-state/heap remain separate
source0 cuts. The [REQUEST-base review](../../coverage/semantics/string-offset-request-base-cv-review.json)
preserves the original Unsupported baseline and fixture failures. Actual
`47dc49ad9`/508 joined loading passes in 15.566676035 s/source0 without renewing
those private cuts. Early lost-owner
and changed-handler histories remain partial; only the eligible-handler derived
fallback is checked. The supplied-Throwable extension below also requires the
same keeper; old String `KEY_NULL` histories remain unchanged.

An initially undefined key on an authenticated literal INTERNED base also
completes mandatory CAST and old-header bounds diagnostics before a supplied
handler Throwable propagates. At `7e4fafc1d`, two local discard arms require `THROW_SEARCH`,
literal ownership, an explicit `KEY_CV` receipt and the authenticated source plan.
The receipt matters because the generic plan can also accept `KEY_NULL` history.
An ineligible handler permits default warnings; an eligible callback is not
reentered with the pending Throwable. Raw callable restoration preserves the live
mask, so `restore_error_handler()` can leave a restored callable with mask0.
Existing conversion/bounds, normal continuations and handler/root APIs stay literal.
Two exact originals at `7e4fafc1d`/private508 reuse native observations once:
current1 gives CAST alone; current8 gives CAST then bounds8. Both preserve the
supplied exception and destination99. Author AL98/41-derived, independent
AL128/63-derived and the genuine precode51/full-state checkpoint retain separate
source0 cuts. A fresh parsed `"abc"[true]` control has a valid generic plan but no
CV receipt, preserving its existing String discard without extra diagnostics.
The [supplied-throw review](../../coverage/semantics/string-offset-undefined-throw-review.json)
preserves the original missing-diagnostic mismatches and pre-guard cut separately.
Actual `6063187d8`/508 loading passes in 15.249904863 s/source0. REQUEST
bases on this abrupt path, other abrupt control and wider conversions/lifetimes
remain partial; held lanes and String `KEY_NULL` histories stay unchanged.

The supplied-Throwable discard also accepts authenticated non-NUL VARIABLE INTERNED
bases. Removing only the two literal-owner guards preserves `THROW_SEARCH`,
the explicit `KEY_CV` receipt and source plan. The selected header survives real
base-cell retirement; current base bindings never replace it. Two exact originals
at `ad9958213`/private508 reuse native observations once: saved `abcde` with current
integer99/key4 emits CAST alone; saved `abc` with current longer string/key8 emits
CAST then bounds8. Both retain the same exception and destination99. Author
AL127/52-derived, peer AL143/40-derived and the genuine precode77/full-state/heap
checkpoint remain separate source0 cuts. The
[VARIABLE throw review](../../coverage/semantics/string-offset-variable-throw-review.json)
preserves the original missing-diagnostic mismatches. Actual `eb1b36cf9`/508 joined
loading passes in 14.865226590 s/source0. No old predicates or execution cuts are
renewed; all other runtime bodies and held lanes stay unchanged.

That first-Undefined supplied-Throwable path also admits REQUEST headers retained
by the same distinct ordinary keeper. Removing only the two INTERNED-only discard
fences preserves `THROW_SEARCH`, the explicit `KEY_CV` receipt and source/keeper
plan. Default CAST and old-header bounds finish before the original exception
propagates, without another handler entry. Two exact originals at
`a6a03df93`/private508 reuse native observations once: saved `abcde` with current
integer99/key4 emits CAST alone; saved `abc` with a current longer string/key8
emits CAST then bounds8. Both retain the same exception, destination99 and keeper.
Author AL145/62-derived, peer AL179/58-derived and authentic precode93/full-state/
heap remain separate source0 cuts. One old normal-peer mask0/key4 identity
expectation now reports CAST/bounds4; its replacement class is checked in the new
peer fixture without replaying the old184 cut. The
[REQUEST throw review](../../coverage/semantics/string-offset-request-throw-review.json)
preserves the original missing-diagnostic mismatches. Actual `0e671433b`/508 joined
loading passes in 14.983122608 s/source0 without renewing the private cuts.
Lost/marked keepers, wider
handler and lifetime histories remain partial; held lanes and String `KEY_NULL`
history stay unchanged.

Initially undefined `KEY_CV` reads now return NULL when the Undefined or CAST
callback retires every owner of the selected non-NUL REQUEST header. The first
top-level release contour requires a restored INTERNED handler with mask0, a quiet
current primitive key, only quiet primitive/INTERNED live cells and scalar constant pools,
and non-owning source continuations. Every other machine provider retains its
initial value. Thus an absent ordinary keeper alone never proves release: a marked
cell, container, cache, frame or owning operand still prevents this admission.
Retired STORE rows, STRINGDATA and scratch locators add no owner. The first boundary
returns NULL before CAST; the second returns NULL before key conversion or bounds.
Only the read continuation and result change; the full heap and event trace survive.
Two exact private508 SL originals at `fe6c0c4a8` reuse native2 once. Author
AL130/48-derived, independent AL146/46-derived and precode85/89 full-state/heap
frontiers retain separate source0 cuts without an aggregate. The first author
fixture notation failure stays0; its two-line correction changes no runtime or
source evidence. The [release review](../../coverage/semantics/string-offset-request-release-cv-review.json)
preserves these cuts and the original mismatch/Unsupported baseline. Actual
`39c2183eb`/508 joined loading passes in 15.432399042 s/source0, separately from
all private cuts without renewing them. Wider masks,
providers, abrupt control and lifetime histories remain partial; String `KEY_NULL`,
generic owner/root APIs, supplied-throw discard and held lanes stay unchanged.

The same release also admits a still-registered INTERNED callback with mask2 and
exactly one prior empty-handler/mask0 entry. That entry supplies no owner; the
current callback's INTERNED bytes are immutable and immortal. That earlier cut added
only ERRORHANDLERS to the state frontier, with exclusive mask0/empty-stack or
mask2/one-empty-entry profiles. Every other cell, pool, continuation and provider
guard stays unchanged.
In particular, a prior REQUEST callback or ARRAY payload does not prove release
when the ordinary keeper disappears. Two new private508 SL originals at
`3efc7ec76` reuse their native2 once. Separate author AL141/56-derived, independent
AL170/67-derived and authentic precode83/89 full-state/heap frontiers retain
source0 without an aggregate. Old fixtures stayed literal at that cut; a
fresh-derived mask0/empty-stack positive preserves that earlier profile without renewing its
execution. The [registered-handler review](../../coverage/semantics/string-offset-request-release-registered-cv-review.json)
retains the original Unsupported baseline and each cut. Actual `8c3f0b691`/508
loading passes in 19.627555390 s/source0, separately from private cuts. Wider
handler stacks/masks, callbacks, providers and lifetimes remained partial at that
cut; held lanes and String `KEY_NULL`, supplied-throw discard and generic owner/root
APIs stay unchanged.

Finite prior-handler stacks now admit absent or valid non-NUL INTERNED callbacks
independently of integer masks. The current callback stays INTERNED; every other
closed source, current-key, cell, pool, task, heap and state-frontier guard remains.
Two fresh default-mask30719 originals with a quiet prior literal handler agree at
private508, reusing native2 once. The
[prior-stack review](../../coverage/semantics/string-offset-request-release-prior-cv-review.json)
keeps source/state cuts, fresh replacements for obsolete refusals and zero-credit
failures separate. The actual `994493f99`/508 joined load passes in 16.131328344 s
with zero source credit; private source/state cuts retain their original identities.
A REQUEST callback after an accepted stack prefix still yields
Unsupported despite false ordinary-provider readiness. Raw/REQUEST/ARRAY/object
callbacks, broader providers, abrupt control, NUL and wider lifetime histories
remain partial; held lanes, String `KEY_NULL`, supplied-throw discard and generic
owner/root APIs stay unchanged.

Ordinary valid non-NUL `INTERNED_STRING` and authenticated `REQUEST_STRING`
carriers delegate to the existing byte rules for `??`, `isset`, and `empty`, as
both containers and string keys. A REQUEST forward validates the registry index,
exact immutable STRINGDATA bytes and byte range, then checks the absence of NUL.
Runtime concatenation with two nonempty operands creates this identity without
a request provider. Registry identity remains metadata with no heap owners.

The [interned review](../../coverage/semantics/string-offset-quiet-carriers-review.json)
retains its original SL cuts. The
[REQUEST review](../../coverage/semantics/string-offset-request-carriers-review.json)
separates two ordinary SL agreements, 133 author AL conditions including 24
derived guard conditions, 95 independent AL conditions, and 222 affected interned
AL conditions. Raw query steps preserve storage and STRINGDATA, including the
false byte `"0"` selected by a concatenated `"-1"` key. Malformed and NUL carriers
retain their prior boundaries; existing lifetime and handler fences remain.

Terminal string `isset`/`empty` uses strict `zval_get_long_ex`, separately from
quiet and ordinary R/W offset conversion. Infinity and finite out-of-range floats
emit a range Warning then precision Deprecated before testing the converted
index. NaN retains its existing pair, fitting fractional floats retain only the
precision Deprecated, and fitting integral floats stay silent. The
[strict-float review](../../coverage/semantics/string-offset-strict-float-review.json)
accepts ordinary no-handler execution: two separate source agreements, author
AL104 (43 derived controls) and independent AL60 retain their actual cuts.
The shared numeric kernel, quiet/R/W rules and wider handler boundaries stay unchanged.

Module38 separately handles intermediate string `unset` without an error handler.
After final-key expression effects, it reads the live inner key. Integer and
leading-integer text keys give `Cannot use string offset as an array` without
checking bounds; UNSET suppresses the usual trailing-text Warning. Invalid
admitted keys instead give `Cannot unset string offsets`, cancelling the second
Error. Null/bool/float keys retain one cast Warning before the nested Error;
the converted index is unused. A final delayed CV is never read after failure.

This admission requires valid non-NUL raw or authenticated carrier bytes.
Object and nonempty-array keys, malformed inputs, NUL and handler paths retain
their fences.
The [nested-unset review](../../coverage/semantics/string-offset-nested-unset-review.json)
separates four original-source agreements, author AL72 (31 derived controls),
independent AL76 and the preserved fixture failure.

Terminal string unset has a separate dispatch after its R-key read: valid
non-NUL interned and authenticated REQUEST bases produce `Cannot unset string
offsets` without converting the key. The new carrier arm requires a known
bounded primitive or valid non-NUL string key and no registered error handler.
A missing key CV still gives its ordinary Warning before the Error.

`$unset_terminal_nonarray` is called only by `$unset_final` after that read.
The shared `$unset_nonarray` remains literal for ArrayAccess callers whose
current RESULT can differ from the captured offset. No owning-key or wider
callback/lifetime admission is added. The
[terminal-unset review](../../coverage/semantics/string-offset-terminal-unset-review.json)
retains one original, author AL93 (34 derived controls) and independent AL53;
preliminary source/AL87/89 cuts stay separate from final acceptance.

`$string_constant_read(bytes, key_value)` is a distinct compiler leaf returning
an optional value. It implements only `zend_eval_const_expr`'s string DIM fold:
nonnegative, in-range integer offsets and integer numeric text, including trailing
text, fold silently. Negative offsets, floating keys and other cases do not fold.
It neither traverses arbitrary expressions nor allocates a source occurrence.
The compiler-context worker owns that traversal and attaches facts to checked
source-unit/occurrence identities.

This distinction is observable: `echo "abc"["1x"]` warns, while the same expression
inside either a constant or dynamic array literal is folded without that warning.
Assignments stop the prepass traversal, and negative `"-1x"` remains a warning at
runtime. The independent conformance fixtures retain these cases. Runtime helpers
must not be substituted for compiler folding merely because their values agree.

Run `python3 tests/semantics/dimension_read.py`. It compares 583 container/key
pairs against the pinned PHP runtime, with exact result types, values, ordered
messages, severity, lines and exception observations. Ten compiler-leaf assertions
and five missing-line/borrowed-key boundaries are reported separately. The report
retains original oracle source, input bytes, stdout, stderr, status and stable
implementation/binary fingerprints. This matrix is helper evidence. Source activation additionally retains all 16
read/prepass conformance fixtures and 15 original compiler emission-line cases
in `validate.py`; it does not establish complete dimension or callback behavior.

Module413 stages finite fitting lossy-float CV keys in ordinary array literals.
`ADD_ARRAY_ELEMENT` converts the key before its deprecation callback; its converted
integer survives later key writes or rebinding. An initially unwrapped
null/bool/int/float element CV supplies its live value if it remains unwrapped
and within those types after the callback. A captured nonconstant array temporary
instead retains its table and embedded
reference cells independently of live names. The continuation owns the builder
and captured temporary once, then transfers the temporary into the inserted entry.
Duplicate replacement preserves insertion position, and following items read
their keys and values afresh. Source, compiler ending lines, runtime/pool
distinctions, roots, raw steps and resumption are checked in the
[array-literal ledger](../../coverage/semantics/array-literal-float-key-warning-review.json).

This slice excludes objects reachable from the builder or captured array, both
before dispatch and on completion. Zend inserts even with a pending exception;
without objects, abandoning both graphs has the same observable cleanup. A
callback introducing objects enters explicit Unsupported on return or throw.
String CV elements and wider owning values remain outside this producer. Wrapped
CVs use only the separate bounded-array admission below.

The separate reference-element continuation acquires a direct CV's wrapper before
conversion. If the callback leaves or rebinds that CV to the same cell, insertion
transfers the acquired owner to an alias. If it rebinds the CV to an unwrapped
null/bool/int/float, insertion uses that live scalar directly and preserves the
acquired count: an existing debt cancels first, otherwise the old wrapper gains a
request owner. Supplied throws preserve that count while discarding the builder.
The acquired value may be primitive or an admitted untyped flat array; the
builder must remain object-free. Retargeting between different admitted reference
cells also records the omitted new-cell owner. This debt survives deletion of the originating entry and
abrupt builder cleanup. Copies at effective count1 unwrap the stored value; copies at
larger counts retain the alias. Same-cell insertion preserves an existing debt;
scalar and inverse-reference retargets cancel count biases per cell, including
repeated debts and residual positive owners. Logical edges are never removed to
represent the missing count. The [deficit ledger](../../coverage/semantics/array-literal-float-ref-deficit-review.json)
records fresh balanced source/state evidence; historical reference probes retain
zero credit in the [positive-owner ledger](../../coverage/semantics/array-literal-float-ref-key-warning-review.json).
Both acquired and new cells may also carry validated ordinary instance-property
type sources while their values remain null/bool/int/float. For debt-bearing
cells, every source object must survive logical pruning with its actual property
alias; type metadata adds no owner. A physical singleton copy unwraps without
carrying the constraint, while the original alias and shared copies still use
existing typed writes.
Fresh int-property witnesses check rejection, numeric-string coercion, multiple
type sources, supplied throws and inverse cleanup in the
[typed-source ledger](../../coverage/semantics/array-literal-float-ref-types-review.json).
Untyped reference cells may instead hold mutable nonpool flat arrays. Entries are
either DIRECT values (null/bool/int/float or validated byte strings) or bounded
ALIAS references described below. The debt remains on
the CELL, which owns one child table independently of its wrapper count. Singleton reference entries unwrap to DIRECT
array values; later child writes use ordinary COW. A still-indebted wrapper can
switch child tables while a direct CV retains its previous table. Stable same-cell
array insertion transfers the acquired owner without adding a request root.
Old array payloads also admit ordinary-scalar DIRECT completion: unmatched
acquired counts retain the wrapper and its child table, while existing wrapper
debt cancels first. Neither old nor current payload may be the active builder.
The [array-to-scalar ledger](../../coverage/semantics/array-literal-float-ref-array-scalar-review.json)
checks normal/throw transfer, debt cancellation and repeated owners.
The [flat-array ledger](../../coverage/semantics/array-literal-float-ref-arrays-review.json)
records fresh singleton/shared, deletion, supplied-throw and inverse-cleanup cases.
Array-valued type sources, pooled/immutable arrays, nesting and reference entries
outside the bounds below, other owning payloads, effective-zero, static/hooked/queued or retired
sources, coercion/backing records, active collection and outstanding request-end
debt remain explicit Unsupported before pruning. Ordinary by-value owning-CV
insertion remains partial.

A separate continuation stages ordinary unwrapped array-CV values. Array values
must be mutable nonpool flat arrays with the same bounded entries;
the builder stays object-free and distinct from their tables. The captured
old table gets one owner before conversion. An unwrapped completion uses the live
CV's table without its own ADDREF. `LITERALARRAYRETAINED` and `LITERALARRAYDEBTS` track
these HARRAY count biases separately from wrapper CELL biases. A same-table
retarget transfers its owner even if the original CV cell was retired. A different
retarget can make ordinary CV and literal values share writes at physical count1.
Deletion and supplied-throw cleanup preserve this table deficit; inverse retargets
cancel it before ordinary COW and teardown. The combined lifetime guard checks
positive flat tables after logical pruning and refuses effective-zero, active
collection or outstanding request-end debt before owner transitions.
The [ordinary array-CV review](../../coverage/semantics/array-literal-float-array-cv-review.json)
records these safe balanced cases. Mixed ordinary scalar/array retargets use the
same table counts: scalar-to-array completion owes one table owner or cancels a
retained occurrence, while array-to-scalar completion preserves the acquired count
or cancels debt. Initial scalar and array plans remain disjoint; captured runtime
array temporaries remain owned and frozen. The
[mixed-CV review](../../coverage/semantics/array-literal-float-mixed-cv-review.json)
checks both inverse cycles, entry deletion and supplied-throw cleanup with positive
physical counts. Wrapped scalar/string CVs, pooled/immutable tables, nesting and
reference leaves outside these bounds and other owning CV values remain Unsupported.
A callback may turn an initially ordinary array CV into an untyped reference
holding null/bool/int/float or a bounded array. Its by-value item then becomes an
ALIAS: the old HARRAY count is retained and the new CELL owes an owner. The
reciprocal reference-element callback may unset/recreate its CV as an ordinary
array, inserting DIRECT PARRAY and cancelling both count families. Physical
singleton copies unwrap; balanced shared copies preserve aliases, while child
snapshots and ordinary old-table writes keep their COW behavior. The
[CV/reference cycle review](../../coverage/semantics/array-literal-float-cv-ref-cycle-review.json)
checks normal, deletion and supplied-throw paths. These completion arms exclude
outer property/coercion/backing records and string CELL values; initial plans,
global gates and lifetime limits stay unchanged.
An initially wrapped array CV captures its dereferenced CELL payload
slot before conversion. The existing ARRAY marker owns only builder and old table;
its REFERENCE locator adds no CELL owner. Completion reads that captured slot,
ignoring current CV rebinding, and inserts DIRECT PARRAY. The allocated marked
CELL has no coercion/backing records or CELL debt, and both CELL and bounded
payload must survive logical pruning even before any debt exists. Source
metadata remains valid when a locator retires; readiness then refuses explicitly.
An outside alias keeps the borrowed slot alive, while deletion/throw requires
another ordinary table owner to keep a new HARRAY deficit positive. Reciprocal
slot retargeting cancels old/new table biases before ordinary COW and teardown.
The [wrapped array-CV review](../../coverage/semantics/array-literal-float-wrapped-array-cv-review.json)
checks rebinding-only, payload cycles, deletion and supplied throw.
The [wrapped mixed-CV review](../../coverage/semantics/array-literal-float-wrapped-mixed-cv-review.json)
adds initial wrapped null/bool/int/float values and primitive completion. The
existing scalar marker uses BORROWED ROOT for the captured slot and owns only the
builder; ARRAY capture still owns its old table. Both read the captured live slot
rather than the rebound name. Scalar-to-array completion owes one table owner;
array-to-scalar completion retains the acquired table count. Reciprocal changes
cancel these biases, including after entry deletion or supplied throw. A separate
ordinary table owner keeps entry-independent debt positive. The
[typed captured-CV review](../../coverage/semantics/array-literal-float-typed-wrapped-mixed-cv-review.json)
adds existing ordinary validated property sources accepting the captured primitive
or bounded array. Every source object must survive the same logical pruning as
the CELL and payload, even before debt. Fresh public int|array slots preserve
weak integer coercion and invalid-string rejection; removing the final property
source leaves an outside alias usable without its constraint. Direct strings,
wider source kinds and unsafe lifetimes remain Unsupported; global ordinary/A19
classifiers, task ownership and count/prune algorithms stay exact.
Ordinary no-argument named functions may supply an owning ARRAY return temporary.
The checked value occurrence must resolve without fallback to an active by-value
function. Its KNOWN table stays frozen while the handler mutates or removes
producer globals, even when a global originally named a reference. Existing
mutable/nonpool and object-free readiness bounds remain; no table or CELL count
bias is introduced. Entry deletion and supplied throw release the owning table
normally. The [return-value review](../../coverage/semantics/array-literal-float-return-array-value-review.json)
keeps these sources separate from borrowed CV slots; by-reference returns,
arguments and wider call producers remain Unsupported on this warning path.
NULL literal-key conversion separately backs up an ordinary unmarked value CV
before dispatch. It restores that same live slot before inserting its frozen
value under the empty-string key, or before propagating a supplied throw. A
shared NULL key/value CV therefore loses the handler's key write too; a distinct
key keeps its write. Scalar or mutable nonpool edge-free/debt-free DIRECT-leaf
array payloads use the existing validators. ARRAY capture keeps both acquisition
and backup owners; the overwritten callback table retires normally. The
[NULL-key review](../../coverage/semantics/array-literal-null-key-warning-review.json)
checks restoration, independent snapshots, COW, deletion and throw. Rebound or unset ordinary slots, typed slots, direct string/object values and
wider graphs remain Unsupported on this continuation; float-key rules stay
unchanged.
An initially untyped reference-wrapped value CV captures the old dereferenced
CELL payload. A surviving alias keeps that marked slot live, and NULL conversion
restores its snapshot even when the original name now refers to another CELL.
The latter binding stays intact. The existing two ARRAY snapshot owners and
DIRECT insertion/throw reset remain unchanged. The
[wrapped NULL-key review](../../coverage/semantics/array-literal-null-key-wrapped-cv-review.json)
checks primitive and array reset, independent snapshots/COW, deletion and throw.
Property/coercion/backing records, CELL debt and wider payloads remain excluded;
source metadata can remain valid after a locator retires while readiness refuses.
Captured typed slots use existing ordinary property-source validation in the
same logical live set as their current payload. Before reset, every current
constraint must also accept the saved snapshot. This check uses allocated
snapshot owners across popped-marker throw cleanup, after current source-object
liveness is established. Fresh public `int|array` slots cover scalar-to-array
reset, weak numeric-string-to-int writes, rejection, final-source detach and
restoration before catch. A transient public `int` source accepts current44 but
makes readiness refuse the old ARRAY; detach restores readiness before the
native callback returns. This is an explicit Unsupported boundary of this
continuation. No generic typed-write or owner
rule changes; see the
[typed NULL-key review](../../coverage/semantics/array-literal-null-key-typed-wrapped-cv-review.json).
Ordinary named calls with no arguments and a by-value function target can also
supply an owning ARRAY value at a NULL key. The active compiled name has no
fallback; mutable nonpool edge-free/debt-free returned tables use the existing
payload bound, with no object reachable from the value or builder. The VAR
acquisition plus NULL backup gives two pending table owners. Normal completion
keeps producer writes and inserts a frozen DIRECT value under `""`; throw removes
both owners without inserting, retiring an otherwise unowned returned table
and builder before catch.
This path has no captured CV to reset and introduces no literal bias. See the
[NULL return-value review](../../coverage/semantics/array-literal-null-key-return-array-value-review.json).
By-reference returns, array-constructor TMPs, calls with arguments and other
call producers remain outside this continuation.
Runtime `NExprArray` values have a separate one-owner NULL-key continuation.
The checked occurrence must be nonconstant and its table mutable and nonpool;
the existing edge-free/debt-free payload and object-free reach bounds apply.
There is no VAR backup or CV writeback: handler seed writes and rebinding persist,
while the constructor's DIRECT child remains frozen under the empty-string key.
Normal insertion transfers the owning edge; supplied throw inserts nothing and
retires an otherwise unowned child table and builder before catch. Fresh integer
leaves cover evaluation once, marked scalar reads by value, COW and last-entry
deletion. Existing primitive/validated-byte leaf checks compose unchanged; pooled
constants, embedded owning leaves and wider producers remain outside this path.
See the [NULL array-TMP review](../../coverage/semantics/array-literal-null-key-array-tmp-review.json).
The [string-leaf review](../../coverage/semantics/array-literal-float-string-leaf-review.json)
adds ordinary tables and untyped wrapper payloads containing canonical-byte or
validated-carrier string leaves. String snapshots remain independent across
shared table writes and restored ALIAS copies. Singleton reference entries
unwrap before child/string COW.
Existing byte/carrier validation and string-offset COW rules remain in use;
direct string CV/cell payloads and array/object-valued leaves outside the bounds below stay Unsupported.
Embedded ALIAS entries may name live untyped cells holding null/bool/int/float
or canonical-byte/validated-carrier strings, without property/coercion/backing
receipts or CELL debt. Every leaf must survive logical
pruning: positive tables keep their leaf edges, including the bounded child-table
edges described below. Child-table COW preserves shared leaf references and unwraps singleton
leaves independently of outer table/wrapper counts. The
[alias-leaf review](../../coverage/semantics/array-literal-float-alias-leaf-review.json)
checks both counts, sibling-slot separation, deletion, supplied throw and inverse cleanup.
The [string-alias review](../../coverage/semantics/array-literal-float-string-alias-leaf-review.json)
extends only embedded leaf admission: shared string references propagate byte
writes, singleton copies detach, and earlier string snapshots stay unchanged.
Global primitive-cell and direct string CV/cell bounds stay exact.
Embedded null/bool/int/float or validated byte-string ALIAS leaves may also
carry validated ordinary instance-property type sources. Each source object
and actual property alias must remain live; for debt-bearing payloads they must
survive logical pruning alongside the leaf. Type metadata adds no owner. Shared copies retain typed
rejection/coercion. Explicit property unset removes that source, permitting
singleton unwrapping when only its table entry remains, even while the object stays
rooted. Int-property witnesses, multiple sources and supplied throws are in the
[typed-leaf review](../../coverage/semantics/array-literal-float-typed-alias-leaf-review.json).
Object-valued leaves, static/hooked/queued or retired sources and
coercion/backing records remain outside this extension.
The [typed string-leaf review](../../coverage/semantics/array-literal-float-typed-string-alias-leaf-review.json)
checks shared byte writes and weak integer-to-string coercion, rejected array
writes, fixed snapshots and singleton byte COW after explicit property unset.
Global direct string CV/CELL retarget bounds remain unchanged.
Array-valued ALIAS leaves may hold one mutable nonpool child table of
DIRECT null/bool/int/float or validated byte strings. Child eligibility first
rejects all outgoing owner edges, before checking its DIRECT values; this excludes
recursive eligibility and cycles. The leaf has no CELL debt or coercion/backing
records, and its child has no HARRAY debt. Ordinary instance-property type sources
use the validation above. For debt-bearing payloads, the child and every source
object must survive the same logical prune. Positive outer tables keep leaf edges;
debt-free leaves keep their child-table edges. Shared leaf copies preserve ALIAS writes;
singleton leaves unwrap to DIRECT array values before independent child COW.
Snapshots and sibling writes separate these effects from outer table/wrapper
biases through deletion, supplied throw and inverse cleanup.
The [array-alias-leaf review](../../coverage/semantics/array-literal-float-array-alias-leaf-review.json)
records untyped cases; the
[typed array-leaf review](../../coverage/semantics/array-literal-float-typed-array-alias-leaf-review.json)
adds public array-property witnesses with scalar rejection, shared nested writes
and singleton copying after explicit property unset. Deeper owning children and
indebted descendants remain Unsupported.
DIRECT child-array entries use the same mutable nonpool, debt-free, edge-free
child bound. Their actual HARRAY nodes must survive logical pruning; repeated
entries contribute separate owner edges. A child write can therefore separate
one occurrence while another keeps its prior value, without an embedded leaf
CELL. Snapshot, repeated-child, deletion and supplied-throw witnesses in the
[direct child-leaf review](../../coverage/semantics/array-literal-float-direct-array-leaf-review.json)
separate child COW from outer HARRAY/CELL biases and inverse balancing. Child
eligibility still rejects outgoing owner edges before examining DIRECT values,
so no recursive eligibility or deeper graph is admitted.
Outer array-valued reference cells also admit validated ordinary property type
sources accepting the bounded payload. For debt-bearing cells, the payload and
every source object must survive the same logical prune. A physically singleton
reference entry unwraps during copying even while its property source stays
live: the copied array value permits scalar replacement and independent child
COW, while the original remains constrained. After inverse balancing, shared
copies retain the typed ALIAS. Explicit property unset detaches its constraint;
an extra alias keeps the count positive until balancing. The
[typed outer-array reference review](../../coverage/semantics/array-literal-float-typed-array-ref-review.json)
checks these paths, initial typed-old capture, deletion and supplied throw.
The source basis is pinned `Zend/zend_vm_def.h::ZEND_ADD_ARRAY_ELEMENT`,
`Zend/zend_hash.c::zend_array_dup_value`, and
`Zend/zend_operators.h::zend_dval_to_lval_safe`, with string writes from
`Zend/zend_execute.c::zend_assign_to_string_offset`.


`45-dimension-write.watsup` supplies separate callback-free write and reference
fetch helpers registered in the source module catalog. `$string_dimension_write`
returns a state and updated container bytes. It resolves/converts the key first;
an index below the negative bound warns and returns null before fetching a
delayed RHS. Otherwise it stringifies the RHS, rejects empty strings, warns for
multiple bytes, writes the first byte, and returns that byte as the assignment
value. Positive offsets beyond the current length extend with spaces. The pure
byte operation assumes allocation succeeds, like the current array model;
allocation failure and environment memory limits remain separate pending effects.

`$string_dimension_fetch` handles reference and nested-array W-fetch errors.
These contexts check key conversion first, then reject the operation without
checking byte bounds. An invalid key's TypeError therefore takes precedence over
the reference/nested-array Error. Append syntax has its own Error. Scalar write
promotion/errors remain in the existing array-location helpers.

The pinned source anchors are `zend_assign_to_string_offset`,
`zend_check_string_offset`, `zend_fetch_dimension_address`, and
`zend_wrong_string_offset_error` in `Zend/zend_execute.c`. These helpers restore
no temporary roots because they acquire none and never prune internally; callers
must preserve the input operands while consuming them. Handler suspension and
string replacement during warnings need an explicit resumable ownership protocol
before callbacks are admitted. Source integration resolves the writable prefix
once, then commits returned string bytes to that captured root or element location.
An intermediate string dimension uses the nested fetch error; the final reference
dimension uses the reference error. Existing array paths retain COW and delayed
key/RHS timing, including RHS-before-overflow ordering for array append.

Run `python3 tests/semantics/dimension_write.py`. The canonical matrix compares
2,220 writes/reference/nested fetches with the pinned oracle, checking updated
container bytes, assignment results, ordered diagnostic bytes/levels/lines and
exact exceptions. Twelve additional boundaries check missing source positions,
request-environment rejection, borrowed reference operands and preservation of
prior held roots. Source validation additionally includes all eight retained
write/error-order conformance fixtures and 20 original-source ownership, capture
and multiline regressions. Wider nested string unset keys/owners and callback
behavior remain pending.

The reviewed source write activation passed the 664-case source campaign plus
23 outcome negatives and 103 independent additional write sources. One temporary
literal lvalue remains explicitly unsupported by the compiler; it is not counted
as a modeled PHP error. The helper matrix and ownership/origin campaigns were
repeated against the same implementation closure.
