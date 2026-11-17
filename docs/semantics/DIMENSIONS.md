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

Unary chains additionally accept quiet numeric PSTRING results of certified
mixed-CONCAT trees. Each actual child, own compiler value and matched precision
must agree; explicit quiet coercion precedes the existing pure unary equations.
Leading-number warnings remain refused even in an already abrupt state. The
[numeric-CONCAT unary review](../../coverage/semantics/string-offset-request-base-numeric-string-concat-unary-special-concat-leading-key-review.json)
keeps four unique source agreements across their original cuts, pre453 and
peer892/307-derived separate. The two source timeouts, incomplete prerequisite
composition and diagnostic-only third fixture retain zero credit. Current owners,
supplied throw and fixed negative bounds use the existing laws.

Boolean-not children now use their own PBOOL and actual scalar truth in those
CONCAT certificates. Literal int/string children use the embedded source value;
nonliteral children keep their own source, read, recursive certificate and matched
precision. Every float child remains refused, matching the compiler's guard.
The [Boolean-not review](../../coverage/semantics/string-offset-request-base-boolnot-special-concat-leading-key-review.json)
keeps four fresh source agreements, pre471 and peer898/273-derived separate.
Zero-string truth, truthy text, omitted literal child facts, a plausible
finite-float result, current owners, supplied throw and fixed bounds are checked.

Strict IDENTICAL/NOTIDENTICAL children additionally require both actual scalar
sources, recursive certificates, child reads and matching compiled precision.
Their own Boolean must agree with existing strict identity or its exact negation;
types and float values govern the result, preserving signed-zero equality without
weak or formatted-text comparison. The [strict-identity review](../../coverage/semantics/string-offset-request-base-identity-special-concat-leading-key-review.json)
keeps source4, pre461 and peer1037/321-derived at separate cuts. Both child-source
and all precision directions, malformed owning pools, equal formatted floats and
loose/array/NaN refusals are checked. Current owners, supplied throw, fixed bounds
and budget laws remain unchanged; wider child and comparison cases remain work.

Quiet non-float XOR children use both actual scalar truths and their own Boolean
through the same source/read/certificate/precision boundary. Truthy leading-number
text needs no numeric conversion; a zero-string CONCAT and strict-identity child
retain their original meanings. The [XOR review](../../coverage/semantics/string-offset-request-base-xor-special-concat-leading-key-review.json)
keeps source4, pre472 and peer1069/338-derived at separate cuts. Both child/source
and precision directions, same-result loose opcode and unchanged-truth malformed
float/array pools distinguish the gates. Owners, supplied throw and fixed bounds
retain existing laws; float and wider XOR children remain follow-up core work.

Exact signed64 integer `<`, `<=`, `>` and `>=` children retain both genuine
sources, recursive certificates, own PINT reads/ranges and matching precision.
Their own Boolean agrees with the direct integer relation. The
[integer relational review](../../coverage/semantics/string-offset-request-base-integer-relational-special-concat-leading-key-review.json)
keeps corrected source4, pre490 and peer1338/366-derived at separate cuts. MIN/MAX,
equal operands, greater-direction helper reversal, same-result type/range and
loose-opcode controls distinguish the gates. The load-order failure and preparatory
fixture diagnostic retain zero credit. Owners, supplied throw and fixed bounds
retain existing laws; mixed and wider comparison children remain follow-up work.

Exact signed64 integer bitwise-NOT children use their own and actual child's
PINT reads/ranges, recursive certificate and matching compiled precision. Early
pure `long_not` supplies the exact complement and existing decimal bytes. The
[integer bitwise-NOT review](../../coverage/semantics/string-offset-request-base-integer-bitnot-special-concat-leading-key-review.json)
keeps source4, pre423 and peer1013/288-derived separate. MIN/MAX and nested
complement, same-result float, string-byte distinction and combined range-fence
controls preserve current owners, supplied throw and fixed bounds. Noninteger
bitwise operations and wider children remain follow-up core work.

Exact signed64 integer `&`, `|` and `^` children retain both genuine sources,
recursive certificates, own/child PINT reads/ranges and three matching precisions.
Early pure integer helpers supply the exact result and decimal bytes. The
[integer bitwise review](../../coverage/semantics/string-offset-request-base-integer-bitwise-special-concat-leading-key-review.json)
keeps source4, pre504 and peer1315/309-derived separate. Signed endpoint sources
and overlapping-mask compiler controls have distinct roles; same-result float
and per-input AND0 range controls preserve current owners, supplied throw and
fixed bounds. Noninteger/string-byte operations remain follow-up core work.

Exact signed64 integer `%` children additionally require a nonzero divisor,
both genuine sources, recursive certificates, own/child PINT reads/ranges and
three matching precisions. Early pure `long_mod` must return the own `IRESULT`.
The [integer modulo review](../../coverage/semantics/string-offset-request-base-integer-modulo-special-concat-leading-key-review.json)
keeps source4, pre484 and peer1274/309-derived separate. Signed remainders,
MIN%minus-one, same-result float, per-input ranges and cached-zero refusal preserve
current owners, supplied throw and fixed bounds. Runtime zero/error and conversion
routes remain separate core work; no new stateful helper or ownership law is added.

Exact signed64 integer `<<` and `>>` children require nonnegative PINT counts,
both actual sources/certificates, own/child PINT reads/ranges and three matching
precisions. Early shift helpers must return the own `IRESULT`. The
[integer shift review](../../coverage/semantics/string-offset-request-base-integer-shift-special-concat-leading-key-review.json)
keeps source4, pre503 and peer1486/309-derived separate. Wrap, signed extension,
word-width boundaries and invalid inputs preserve current owners, supplied throw
and fixed bounds. Two old shift refusals are promoted with isolated17+17 checks;
other assertions and historical receipts remain. Error/coercion routes stay separate.

Exact signed64 integer `==`, `!=` and `<=>` children authenticate both source
occurrences, PINT reads/ranges, recursive certificates and three matching precisions.
Direct integer predicates or early `compare_int` must match the typed own result;
Boolean false keeps empty bytes and spaceship zero keeps decimal zero. The
[integer equality review](../../coverage/semantics/string-offset-request-base-integer-equality-special-concat-leading-key-review.json)
keeps source4, corrected pre458 and peer1496/309-derived separate. Two fixture-load
failures retain zero credit and three unrun cases each. Five affected compiler
selectors62 and one derived mutation124 pass separately; other assertions and
historical cuts remain. Mixed comparison and wider ownership remain core work.

Boolean/Logical AND/OR children distinguish decisive and live right operands.
Both child sources remain authentic; decisive admission uses only own/left facts,
while a live right operand needs its own read, certificate, nonfloat scalar type
and matching precision. Own Boolean results retain exact echo bytes. The
[logical branch review](../../coverage/semantics/string-offset-request-base-short-circuit-special-concat-leading-key-review.json)
keeps source4, pre450 and peer1654/297-derived separate. Skipped calls have no
executable read; their precision is declaration fallback. Unused pool/precision
mutations preserve admission, while evaluated type/source/precision failures refuse.
Float diagnostics, dynamic evaluated values and wider ownership remain core work.

Integer powers with nonnegative PINT exponents require exact own/child sources,
PINT reads/ranges, recursive certificates and three matching precisions. Early
`power_prepare` must yield the quiet integer result; no general floating power
plan is admitted. The [integer power review](../../coverage/semantics/string-offset-request-base-integer-power-special-concat-leading-key-review.json)
keeps source4, pre477 and peer1395/309-derived separate. Zero exponent, signed
endpoints, parity and invalid inputs retain existing owners, throw and fixed bounds.
One prior compiler branch passes17 isolated checks; other assertions/cuts remain.
Negative exponents, float results, conversion and wider ownership remain core work.

String byte `~`, `&`, `|` and `^` children authenticate exact raw-PSTRING own/child
facts, actual source occurrences, recursive certificates and matching precisions.
Early byte helpers preserve OR tails, AND/XOR shorter lengths and NOT complements.
The [string byte review](../../coverage/semantics/string-offset-request-base-string-bitwise-special-concat-leading-key-review.json)
keeps source4, pre368 and peer1321/292-derived separate. NUL/control/high operand
bytes retain non-NUL final source keys; compiler NUL results keep source0. Same-byte
runtime carriers are refused as compiler facts. Two old branches pass11+10 isolated
checks; historical cuts and downstream ownership/base/key guards remain.

Non-NaN numeric comparison children authenticate typed signed64 PINT or valid
binary64 PFLOAT operands, including mixed pairs with at least one float. Actual
source/read facts, quiet child-byte certificates and three matching precisions
bind the exact Boolean or spaceship integer result. The [numeric comparison
review](../../coverage/semantics/string-offset-request-base-numeric-comparison-special-concat-leading-key-review.json)
keeps source4, author714, independent2072 and affected controls at separate cuts.
At that cut, NaN still needed a numeric value certificate; nonnumeric coercions
and wider owners and lifetimes remain partial.

NaN ConstFetch operands now authenticate numeric values without operand byte
certificates. All seven comparisons retain actual source/read and precision facts;
greater reverses numeric order. The [NaN comparison review](../../coverage/semantics/string-offset-request-base-nan-comparison-special-concat-leading-key-review.json)
keeps source4, author747, independent1792 and isolated9 separate from the two
joined source-zero loads. Arithmetic NaN, coercive/owning comparisons and wider
lifetimes remain partial; Source47 DEFINE-name NaN stays held.

Quiet FLOAT operands also enter XOR and Boolean/Logical AND/OR through five
evaluated type guards requiring valid64bit non-NaN values. Source/read/byte and
precision facts remain. A RHS skipped by a decisive left retains source
authentication without a value proof. The [FLOAT logical review](../../coverage/semantics/string-offset-request-base-float-logical-special-concat-leading-key-review.json)
keeps source4, pre669, author868, independent2042 and affected controls separate
from joined loads. Every `!FLOAT` stays unfolded; an existing NOT can instead
receive a Boolean result. Wider coercions, owners and lifetimes remain partial.

Two raw compiler PSTRING operands also admit all seven weak comparisons through
actual source/read facts, identical recursive BYTE payloads and three matching
precisions. The existing pure string order preserves numeric overflow provenance,
same-sign infinity fallback and normalized lexical spaceship results; its body
stays unchanged. The [raw-string comparison review](../../coverage/semantics/string-offset-request-base-string-comparison-special-concat-leading-key-review.json)
keeps source4, pre502, author701 and independent1977/377-derived separate from
the joined source-zero load. Runtime carriers do not serve as raw compiler
PSTRING facts. Mixed-type and owning comparisons and wider lifetimes remain partial.

Ordered signed64 or non-NaN binary64 numbers also compare with exact raw PSTRING
children in either orientation through the existing pure number/string order.
Full numeric strings use numeric conversion; other strings compare against number
text at captured compile precision. Actual sources/reads, quiet recursive BYTE,
exact string payloads and three precisions bind the own Boolean or spaceship INT.
The [number/string review](../../coverage/semantics/string-offset-request-base-number-string-comparison-special-concat-leading-key-review.json)
keeps source4, pre503, author702, independent2193/419-derived and affected controls
separate from the joined source-zero load. Numeric reads need not equal literal
byte text. Other scalar/owning domains and wider lifetimes remain partial.

Quiet comparisons with at least one BOOL/NULL operand retain actual sources,
reads, recursive BYTE and three matching precisions. Partners are BOOL/NULL,
ordered valid numeric values or exact raw PSTRING payloads. Existing scalar order
preserves Boolean priority and the NULL/nonempty-string exception; the domain
cannot reach live numeric/string formatting. The [BOOL/NULL comparison review](../../coverage/semantics/string-offset-request-base-bool-null-comparison-special-concat-leading-key-review.json)
keeps source4, pre501, author700, independent2043/313-derived and affected controls
separate from the joined source-zero load. Certified Boolean results of NaN
comparisons differ from direct NaN operands. Wider producers, owners and lifetimes
remain partial.

Genuine NaN ConstFetch VALUE also compares with BOOL/NULL or exact raw PSTRING
partners in either orientation without minting NaN BYTE. Existing scalar order
keeps quiet Boolean/null compatibility and unordered string/NaN +1 in both
directions; greater therefore computes the real reverse. Actual sources, reads,
partner BYTE and three precisions bind the own Boolean or spaceship INT. The
[NaN/scalar review](../../coverage/semantics/string-offset-request-base-nan-scalar-comparison-special-concat-leading-key-review.json)
keeps source4, corrected pre538, failed pre115, author737, independent2298/363-derived
and affected89 separate from the joined source-zero load. NOT sees BOOL only;
arithmetic NaN and wider ownership/lifetimes remain partial.

Strict IDENTICAL/NOTIDENTICAL also admits genuine NaN ConstFetch VALUE through
per-occurrence scalar projections, preserving numeric tags and exact raw PSTRING
payloads. Both actual child sources/reads and three matching compile precisions
bind the own Boolean. Even equal NaN bits are nonidentical; NOTIDENTICAL negates
that result without converting either operand. NaN still has no BYTE certificate.
The [NaN identity review](../../coverage/semantics/string-offset-request-base-nan-identity-special-concat-leading-key-review.json)
keeps source4, pre530, author729, independent2350/437-derived and affected36
separate from the joined source-zero load. Coherent finite-source NaN reads fail
the new projection; the unchanged older BYTE identity arm retains its own bounds.
Arithmetic NaN, wider producers, carriers/owning values and lifetimes stay partial.

Direct integer ConstFetch leaves now use their own compiler-proved PINT and the
existing decimal formatter in those CONCAT trees. Source names retain compiler
resolution; no runtime name lookup or spelling table is added. Four global,
imported and fully qualified originals cover both ordinary selections, supplied
throw and genuine positive later bounds. The [integer-constant review](../../coverage/semantics/string-offset-request-base-integer-const-special-concat-leading-key-review.json)
keeps source4, pre304, author511/105-derived and peer631/264-derived plus41 compiler
checks separate. Compiled pools retain their internal proof boundary; these checks
do not validate arbitrary forged pools. At that cut, Float/unary ConstFetch,
binary children and wider ownership remained partial.

Quiet FLOAT ConstFetch leaves also retain their own actual read and captured
precision, valid64 non-NaN value and exact quiet formatter. Existing unary,
arithmetic and comparison certificates then compose through those leaf facts.
The current builtin source is INF; this does not add startup constant values or
raw PSTRING providers. NaN still has no BYTE certificate. The [FLOAT constant
review](../../coverage/semantics/string-offset-request-base-float-const-special-concat-leading-key-review.json)
keeps source4, pre588, author787, independent1412/488-derived and affected88
separate from joined loading. Finite pool variants distinguish captured14/17
formatting from live precision; the internal compiler-proof boundary is unchanged.
Arithmetic NaN VALUE was separate at that leaf cut.

Quiet ADD/SUBTRACT/MULTIPLY/DIVIDE results also supply genuine NaN VALUE through
actual source/read facts, three matching capture precisions, ordered nonNaN
numeric child BYTE and exact quiet arithmetic. Result bits are bound without a
canonical-payload assumption; comparisons consume VALUE while NaN BYTE remains
absent. The [arithmetic NaN review](../../coverage/semantics/string-offset-request-base-arithmetic-nan-special-concat-leading-key-review.json)
keeps source4/native-once, pre696, author895, independent2350/488-derived and
affected55 separate from the accepted MAIN920e49b09 joined source-zero load.
Binary arithmetic with NaN children, unary NaN and wider producers/ownership/
lifetimes were separate at that arithmetic cut; held Source47 stays unchanged.

Quiet unary `+`/`-` of genuine NaN children now supplies VALUE through actual
own/child source and reads, two matching capture precisions and the exact quiet
unary result bits. NaN BYTE remains absent. Four production-SL originals cover
immediate signs; finite nested signs have compiler-fixture/source-zero coverage.
The [unary NaN review](../../coverage/semantics/string-offset-request-base-unary-nan-special-concat-leading-key-review.json)
keeps source4/native-once, pre695, author894, independent fixture1236/447-derived,
compact compiler930/54 and affected28 separate from the actual MAINc10 joined
source-zero load. The original1706-condition compiler timeout stays zero-credit
in its failed full report.
Binary NaN-child arithmetic, FLOAT NOT, wider producers/owners/lifetimes and
held Source47 remain separate from that unary cut.

Quiet ADD/SUBTRACT/MULTIPLY/DIVIDE also supplies genuine NaN VALUE when an actual
numeric child is NaN. Both child VALUE proofs, own/child sources and reads, three
matching capture precisions and the exact quiet arithmetic result remain required.
Ordered partners retain BYTE; NaN children and results retain BYTE EPS. The
[NaN-child arithmetic review](../../coverage/semantics/string-offset-request-base-nan-child-arithmetic-special-concat-leading-key-review.json)
keeps source4/native-once, pre692, author891, independent2286/554-derived and two
affected42-condition selections separate from the actual MAINded joined
source-zero load. Old arithmetic/unary fixture recipes remain literal: stale
result bits still refuse and coherent child/result bits admit.
At that NaN-child cut, quiet scalar-coercive children, NaN BYTE, FLOAT NOT,
wider producers/owners/lifetimes and held Source47 remain separate.

Quiet ADD/SUBTRACT/MULTIPLY/DIVIDE NaN VALUE also admits genuine BOOL/NULL/raw
numeric-string children through scalar identity VALUE, quiet coercions and exact
own/child source/read/precision facts. Four original agreements reuse native
observations once; author887/105-derived, independent fixture1275/493-derived,
corrected compiler1031/52, affected pool127/60 and compiler42/14/42 retain separate
source-zero cuts. The source startup failure, original compiler static failure
and false full-report aggregate remain explicit. MAIN `e32d48dbb` is integrated;
its composed `8892a1510` production-SL508 load passes in15.588865828s/source0.
NaN BYTE, FLOAT NOT, wider producers/owners/lifetimes and held lanes remain partial.
[Quiet coercive NaN review](../../coverage/semantics/string-offset-request-base-coercive-arithmetic-nan-special-concat-leading-key-review.json).

Quiet completed POWER also supplies genuine NaN VALUE through actual own/child
source/read/precision facts, genuine scalar children, quiet coercions and exact
`POWERDONE`/full-state results. Four originals reuse native observations once;
pre659, author858/105-derived, independent2002/497-derived and affected14/14 keep
separate source-zero cuts. MAIN `1d179a605` and its `9bc7dcad3` SL508 load
(15.438906230964s/source0) remain separate. NonNaN power BYTE, GENERAL, Deprecated,
NaN BYTE, FLOAT NOT, wider producers/owners/lifetimes and held lanes stay partial.
[Completed-power NaN review](../../coverage/semantics/string-offset-request-base-power-nan-special-concat-leading-key-review.json).

Quiet completed POWER nonNaN FLOAT results also retain exact BYTE at captured
precision through actual own/child facts, scalar VALUE, quiet coercions and full
state/result checks. Four originals reuse native observations once. Pre-v2
remains false: first109/151/136 pass, fourth204 is corrected separately; no passing
600 aggregate is claimed. Author799/105-derived, independent1675/542-derived and
affected18/26 retain separate source-zero cuts. Actual `c68397001` has one combined
SL508 load passing15.982042335905135s/source0. GENERAL, Deprecated, NaN BYTE,
wider producers/owners/lifetimes and held lanes remain partial.
[Completed-power FLOAT review](../../coverage/semantics/string-offset-request-base-power-float-special-concat-leading-key-review.json).

Quiet completed scalar-coerced POWER supplies exact PINT BYTE through actual
own/child source/read facts, genuine scalar identity, equal captured precisions,
quiet NINT coercions, POWERDONE and the unchanged full-state result. Native4
once/source4 and separate pre458/author657/peer1570/affected90/30 cuts are retained
in the [review](../../coverage/semantics/string-offset-request-base-coercive-integer-power-special-concat-leading-key-review.json).
MAIN `7da259b5e` has one combined SL508 load15.68941183295101s/source0.
GENERAL, Deprecated, NaN BYTE, unary FLOAT NOT and wider lifetimes remain partial.

Ordinary nonnull NaN-left coalesce also supplies an exact named `instanceof`
operand through both actual source children, root/left compiler precision and
the unchanged full `coalesce_result` state. The skipped RHS needs no value or
compiler certificate. Four originals reuse native observations once; author
SL1236/129-derived and independent SL1758/651-derived retain separate cuts in
the [review](../../coverage/semantics/string-offset-request-base-runtime-nonnull-nan-coalesce-instanceof-review.json).
The missing fourth peer process remains incomplete0; only that fixture was
recovered. Actual `8a008c964` and the sole joined `266b8eab90` SL508 load
(16.444075383 s/source0) are independently clear. General NaN VALUE/BYTE/truth,
null-left selection and wider lifetimes retain their existing bounds.

Full ternaries also preserve an exact selected NaN operand for named `instanceof`
under an existing quiet condition. Both source arms remain authenticated; only
the selected arm supplies code, precision and value. Whole-state truth, copy and
module51 selected tasks retain the existing owners and completion histories.
Four originals reuse natives once through explicit retained-three/affected-fourth
cuts; author SL1466/129-derived and independent SL1786/449-derived are separate
in the [review](../../coverage/semantics/string-offset-request-base-runtime-full-ternary-nan-instanceof-review.json).
The two earlier CLI deadlines remain0. General runtime NaN VALUE/BYTE/truth,
quiet false shorthand selection and wider lifetimes retain their existing bounds.

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

Unary `+`/`-` now also accepts a recursively certified nonliteral numeric child,
including an integer ConstFetch or quiet arithmetic tree. The exact child origin,
own numeric facts and matching compiled precision must agree with the existing
pure unary result and quiet formatter. The
[composition review](../../coverage/semantics/string-offset-request-base-unary-const-arithmetic-special-concat-leading-key-review.json)
keeps four source agreements, pre-AL evidence, explicit fixture-SL checks and the
preserved AL timeout separate. Boolean/null unary children, nonliteral numeric
strings, float ConstFetch and wider ownership remain partial at this cut.

Boolean/null children now also enter that same unary arm through their own
resolved compiler facts. Existing quiet numeric conversion gives true one and
false/null zero; exact unary results and compiled precision still authenticate
every step. The [Boolean/null review](../../coverage/semantics/string-offset-request-base-bool-null-unary-special-concat-leading-key-review.json)
keeps four source agreements, pre436, author670 and peer886 plus63 compiler
conditions separate. Equal bytes in a different REQUEST header do not retain the
borrowed base; numeric PSTRING CONCAT children remain refused at this cut.

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

Live HCELLs may now hold other authenticated non-NUL REQUEST identities without
blocking this selected-header release. Two independent nonempty CV concatenations
produce equal `abc` bytes in different headers; the surviving bystander owns only
its own header. Only the cell classifier receives the selected identity. Pools,
callbacks, tasks and the 21-field provider closure keep their prior guards.
The [distinct-header review](../../coverage/semantics/string-offset-request-release-distinct-cv-review.json)
separates two new source agreements, author SL217/119-derived and independent
SL151/48-derived fixtures. The first source timeout retains zero credit; one
affected retry and the other source's first comparison pass at the original caps,
reusing native2 once. Exact selected owners, including marked cells with false
ordinary-provider readiness, remain refused. Wider providers, callbacks, NUL,
abrupt histories and held lanes remain partial.

After that closed frontier establishes selected-header death, NULL completion
does not demand a primitive current key. Handler-created nonnumeric text and
unrelated REQUEST key values need no conversion; the unchanged cell proof still
rejects any key cell owning the selected header. Live-header conversion stays
unchanged. The [early-return review](../../coverage/semantics/string-offset-request-release-key-cv-review.json)
separates two new source agreements from composed author SL244/146-derived and
independent SL181/78-derived fixtures. Both sources use their native observations
once at the original caps; no failures or older fixture renewals arose.
Raw/NUL/ARRAY keys, other providers and held lanes retain their prior boundaries.

The closed release also accepts valid non-NUL REQUEST callbacks whose header
identity differs from the selected base, in either the current handler or a
finite prior stack. Equal `abc` bytes do not imply shared ownership. An exact
selected-header callback still prevents release; the full provider frontier and
early NULL-before-key-conversion rule remain required. Two private508 originals
agree at `1556e7ca7` at the original60/80 model caps, reusing native2 once. Separate
author SL287/189-derived and independent SL217/114-derived fixtures retain their
own cuts; pre-admission117/110, both old timeouts and the recorder failure receive
no source credit. The [callback-header review](../../coverage/semantics/string-offset-request-release-callback-cv-review.json)
records those identities and the separate actual `ab60fab36`/508 joined load
(17.792991204 s/source0). Positive selected-header callback retention, wider
providers, abrupt histories and held lanes remained partial at that cut.

A normal `KEY_CV` read now also keeps its selected REQUEST header when that exact
value is registered as the current or a prior error callback. After the handler
rebinds the base to `99` and defines key `0`, the retained header survives Undefined
and CAST and supplies `a`. The positive provider proof requires the genuine
normal resume head, source/phase receipt, valid non-NUL carrier, retained callable
and exact registry identity. It supplies no pending-Throwable discard authority.
The [callback-owner review](../../coverage/semantics/string-offset-request-callback-owner-cv-review.json)
keeps the two source agreements at their separate cuts, with native2 reused once,
and separate author SL141/31-derived and independent SL165/51-derived checks.
A static bridge to the accepted MAIN snapshot preserves the first source/state
cuts; only the initially timed-out second source was retried at its original caps.
That timeout and the corrected peer fixture syntax failure retain zero credit.
Actual `e82acf6d6`/508 joined loading passes in 17.900858450 s with zero source
credit and preserves those private cuts.
Wider provider histories, abrupt callback remainders and held lanes remain partial.

A normal initialized-key CAST read also retains a selected REQUEST header held
by its exact current or prior error callback. The separate provider proof requires
the genuine `KEY_NULL`/`STRING_CAST` receipt, captured VARIABLE base/key locators,
source authentication and a valid retained callable registration. Retiring the
old base cell does not invalidate its saved source locator. The current key must
still select its original live cell: header ownership grants no key conversion
authority. Two exact originals read old `a` after the callback rebinds the base
to `99` and changes that key from false to `0`, reusing native2 once. Separate
author SL150/43-derived and independent SL134/48-derived checks retain their own
cuts in the [CAST callback-owner review](../../coverage/semantics/string-offset-request-callback-cast-owner-review.json).
The corrected pre-frontier binding failure keeps zero credit. Broader ownership
histories and abrupt callback remainders remain partial.
Actual `2d75552ae`/508 joined loading passes in 15.180301956 s with zero source
credit, separately from those private cuts.

The same CAST provider also accepts source-authenticated immutable primitive keys
with an absent key locator. Callback writes cannot change that saved KNOWN input;
the captured base locator remains source history after its cell retires. An exact
current callback preserves `a` for false and a prior callback preserves `b` for
true after rebinding the base to `99`. Two original-source agreements reuse native2
once, while author SL160/57-derived and independent SL150/66-derived checks retain
separate cuts. The [known-key review](../../coverage/semantics/string-offset-request-callback-known-key-review.json)
keeps pre-admission frontiers and the original Unsupported/timeout and recorder
setup failure at zero credit. Wider ownership histories and abrupt callback
remainders remain partial.

Normal CAST also returns `NULL` when the closed provider frontier proves that the
selected non-NUL REQUEST header has lost its last owner. The separate proof keeps
`KEY_NULL`/`STRING_CAST`, the captured VARIABLE base locator and immutable
KNOWN/absent-key-locator pairing. Existing handler, declaration, pool, task and
cell guards plus the complete initial-state projection exclude hidden owners;
retired rows and scratch locators add none. No current-key capture or conversion
runs. Two strict-NULL original-source agreements reuse fresh native2 once;
author SL184/73-derived and independent SL197/105-derived checks retain separate
source-zero cuts. The [release review](../../coverage/semantics/string-offset-request-known-key-release-review.json)
keeps both old Unsupported outcomes and full155-field frontiers at zero credit.
A source-valid NUL control refuses, preserving that paused boundary. Wider
histories and abrupt callback remainders remain partial.

That closed normal CAST release also accepts initialized VARIABLE keys with
captured key-cell history. Original base/key cells may both retire while their
names point to a shared or two distinct ordinary references. Source/locator
pairing, the non-NUL base, every provider guard and the complete initial-state
projection remain required. NULL precedes current-key capture even when the
current target differs from the saved locator. Two exact originals distinguish
shared alias updates from independent key updates and emit no bounds Warning.
They reuse fresh native2 once; author SL201/82-derived and independent
SL224/123-derived checks retain separate source-zero cuts. The [variable-key
release review](../../coverage/semantics/string-offset-request-variable-key-release-review.json)
keeps Unsupported2 and both full155-field frontiers at zero credit. Wider retained-header
reads, histories, abrupt remainders and held lanes stay partial.

A plain compiled global key CV may move to a distinct ordinary cell or reference
holding a quiet primitive or valid non-NUL INTERNED text whose selected offset
is in range while the current or prior callback still owns the selected
non-NUL REQUEST header. The normal closed state
and original source receipt remain required. Capture records whether the key
already was a reference, distinguishing its old wrapper from the current CV slot.
Two exact c/a originals reuse native2 once; author SL200/41-derived and independent
SL196/54-derived checks keep separate source-zero cuts in the [plain-key review](../../coverage/semantics/string-offset-request-callback-rebound-key-review.json).

That plain-CV path also admits an alias created by the handler before rebinding.
The old cell may remain live and marked with a different value; the reference
kind captured before the Warning still selects the current slot. The
[late-alias review](../../coverage/semantics/string-offset-request-callback-late-reference-review.json) records two exact c/a originals and separate new/affected SL
and joined cuts, preserving source, provider, type/range, closure, throw and held
boundaries.

An initially referenced key may instead use its live old wrapper after its name
is rebound, removed or still names that old cell. A surviving alias, an
ordinary marked/pruned old cell holding a quiet primitive or valid non-NUL
INTERNED text with an in-range selected offset, the
same closed normal state and exact callback owner remain required. The read selects
the live old payload independently of the captured Boolean and current name/value. Original b/c agreements
reuse each native capture once. Separate author SL222/54-derived, independent
SL148/49-derived and affected peer SL196/54-derived checks retain source-zero
cuts; the [initial-reference review](../../coverage/semantics/string-offset-request-callback-referenced-key-review.json) preserves failures and the distinct joined load.
Wider reference, provider, coercion, throw and held histories remain partial.

PINT, Boolean, NULL and finite int64-fitting FLOAT values enter either path
through the existing quiet conversion. Only the selected offset must be in range;
2.75 truncates to2, while an unused current integer99 can remain valid under
initial-reference history. Stored values remain unchanged. The [quiet-scalar
review](../../coverage/semantics/string-offset-request-callback-scalar-key-review.json) links six exact b/a/c originals across the two histories to separate
new/affected SL and joined cuts. Nonfinite/range or broader conversion, provider,
owner, throw and held contexts remain partial.

The current CV may also be unset and replaced by an ordinary unmarked quiet
primitive cell. The plain-key arm checks its selected current supported value
and FLOAT quietness; initial-reference history retains its selected old wrapper's
marked, live and backing guards. Two exact c/c originals retain distinct current
key and old-alias observations. The [ordinary-current review](../../coverage/semantics/string-offset-request-callback-ordinary-key-review.json)
keeps native reuse, source2, canonical and affected SL, and joined loading as
separate cuts. Wider source/provider/owner and lifetime contexts remain partial.

After the initial cast Warning, late valid non-NUL INTERNED text uses the
existing silent string-to-integer conversion: "2x" selects offset 2 and "word" selects offset 0,
without restarting initial string-key validation. Captured KEYREF still chooses
the current slot or live old wrapper. Consumed plain-key marked text retains the existing
LEADNUM capture restriction. The [late-text review](../../coverage/semantics/string-offset-request-callback-text-key-review.json)
separates two exact c/a originals and once-native reuse from new/affected SL,
the preserved fixture syntax failure and joined loading. Selected raw/NUL
payloads and wider histories remain partial.

Initial-reference reads also admit an absent current name or the same old cell.
The new arm checks complete heap validity and the existing old-cell source,
backing, liveness, selected-value, range and callback-owner proofs. It never
consumes the unused current value. Same-cell primitives retain their unchanged
stable rule through a disjoint partition. The [old-wrapper review](../../coverage/semantics/string-offset-request-callback-old-key-review.json)
separates two exact b/c originals, once-native reuse, new/affected SL, a preserved
rule-overlap failure and corrected production cut, and joined loading. Wider
source/provider/owner, selected raw/NUL, throw and held contexts remain partial.

A captured plain compiled key CV also admits supported same-slot text and an
absent current name after the cast Warning. Same-slot text uses silent conversion;
missing current UNDEF converts to zero without another diagnostic or any ENV/STORE
creation. Historical KEYREFfalse and the static nonblocked CV/source/normal
callback/closed21 proof remain required; the absent-name case also requires
complete heap validity. Two a/c originals reuse native2 once; author SL114/39 plus
affected106/33 and peer SL154/50 plus affected156/52 keep separate source0 cuts in
the [plain compiled-CV review](../../coverage/semantics/string-offset-request-callback-plain-key-review.json).
Selected raw/NUL and wider histories remain partial.

Selected late non-NUL REQUEST key text also uses that silent conversion when an
ordinary unmarked current compiled CV or the live marked initial wrapper owns the
exact authenticated carrier. Full heap validity, source/static-CV, backing/liveness
and closed21/range checks remain required. Callback provider readiness now yields
to an existing exact current or outside cell owner, preserving the admitted provider
set while keeping proofs disjoint. The [REQUEST-key review](../../coverage/semantics/string-offset-request-callback-request-key-review.json)
separates two a/c original comparisons reusing native2 once, current source and SL
cuts, preserved failures and joined loading. Later-marked current REQUEST keys,
raw/NUL payloads and wider contexts remain partial.

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

Quiet runtime unary +/- preserves fitting integer bytes from typed Boolean and integer results; existing NOT can consume the resulting integer. Exact emitted source, code and precision facts, quiet NINT conversion and full-state results retain the real REQUEST key and existing owners. Four source agreements reuse native originals once; authorSL731 and inclusive peerSL1231 remain separate from the sole fce0c4887 SL508 load (16.187261943006888s/source0). NaN warnings, wider producers/owners/lifetimes and complete core remain unfinished. [Runtime integer-sign review](../../coverage/semantics/string-offset-request-base-runtime-unary-integer-review.json).

Quiet emitted ADD/SUB/MUL and PINT-only BITNOT retain actual source/CODE/read-eps/equal precision, quiet fitting NINT inputs and exact whole-state PINT results/decimal bytes. Native4 once/source4, authorSL932/129derived and inclusive peerSL1660/857derived (=932+728, including42 checked-source compiler conditions) remain separate in string-offset-request-base-runtime-integer-operator-review.json. The v1 fixture expectation failure and unrun3 retain0; actual5889f080 has ONE canonical SL508 load16.2823896210175s/source0. Runtime FLOAT bytes, wider operators/producers/owners/lifetimes and complete core remain unfinished. [Runtime integer-operator review](../../coverage/semantics/string-offset-request-base-runtime-integer-operator-review.json).

Quiet runtime modulo, bitwise AND/OR/XOR and shifts retain exact integer bytes from recursively certified PINT children. Matching emitted source, code, read and precision facts, IRESULT and full-state checks preserve the existing key and ownership rules; wider types, operators, producers and lifetimes remain partial. [Strict integer-binary review](../../coverage/semantics/string-offset-request-base-runtime-integer-binary-review.json).

Quiet emitted modulo, bitwise AND/OR/XOR and shifts also accept certified BOOL/NULL values through ordered quiet full-state integer coercions and original typed operands. New BOOL/NULL operands require NORMAL; prior PINT completion behavior is preserved. Four source agreements and separate author1529/129-derived and independent2649/1249-derived fixture cuts pass. Wider types and owners remain partial; formatting and exact holds are unchanged. [Primitive integer-binary review](../../coverage/semantics/string-offset-request-base-runtime-primitive-integer-binary-review.json).

Quiet emitted modulo, bitwise AND/OR/XOR and shifts also admit fitting integral FLOAT values through exact bits, empty intrinsic conversion notices and ordered full-state integer coercions. New FLOAT operands require NORMAL; original typed results and prior PINT completion behavior remain. Four saved-native source agreements and separate author1532/129-derived and independent2538/1135-derived fixture cuts pass. Emitted FLOAT BYTE, formatting and every exact hold remain unchanged. [Integral-FLOAT review](../../coverage/semantics/string-offset-request-base-runtime-float-integer-binary-review.json).

Fitting integral FLOAT values now cross direct emitted bitwise NOT with their original typed operand, intrinsic empty conversion notices and exact full-state integer coercion/result checks. New FLOAT operands require NORMAL; prior PINT completion behavior and emitted FLOAT BYTE remain. Four saved-native source agreements and separate author944/129-derived and independent1647/832-derived fixture cuts pass. Wider operands and owners remain partial; formatting and every exact hold are unchanged. [FLOAT bitwise-NOT review](../../coverage/semantics/string-offset-request-base-runtime-float-bitnot-review.json).

Quiet completed integer-result powers now compose through emitted string-offset key parents. Exact original typed operands, quiet signed64 numeric coercions and POWERDONE(NINTi)false preserve the result under NORMAL. Four source agreements reuse native originals once; separate author1271/129-derived and independent1993/851-derived fixture cuts pass. FLOAT results, GENERAL and Deprecated stay outside this certificate; formatting, owners and every exact hold are unchanged. [Integer POWER review](../../coverage/semantics/string-offset-request-base-runtime-integer-power-review.json).

Quiet completed nonNaN FLOAT-result powers now compose through emitted string-offset key parents. Exact original typed operands, quiet numeric coercions, POWERDONE(NFLOATbits)false and whole-state results preserve exact bits under NORMAL. Four source agreements reuse native originals once; separate author1264/129-derived and independent1993/858-derived fixture cuts pass. GENERAL, Deprecated, NaN and emitted FLOAT BYTE remain outside this certificate; formatting, owners and every exact hold are unchanged. [FLOAT POWER review](../../coverage/semantics/string-offset-request-base-runtime-float-power-review.json).

Certified nonNUL literal strings retain their actual INTERNED header through emitted typed string-offset key parents. Exact decoded source bytes, raw PSTRING reads/identity and captured precision bind that carrier; leading-data arithmetic warnings remain refused. Four source agreements reuse native originals once; corrected author909/129-derived and independent1430/650-derived fixture cuts remain separate, with failures preserved. Emitted FLOAT BYTE, STRING bitwise operations and wider producers, consumers and owners remain partial. [Literal STRING review](../../coverage/semantics/string-offset-request-base-runtime-literal-string-review.json).

Quiet emitted BOOL/INT/FLOAT casts now consume certified nonNUL literal-INTERNED STRING values through exact source, captured precision and whole-state cast authority. Explicit numeric prefixes and nonnumeric integer casts stay quiet; FLOAT BYTE remains eps. Native4 once/source4, author938/129-derived and independent1479/670-derived fixture cuts pass separately, with no new campaign failures. Other casts, STRING bitwise operations and wider producers, consumers and owners remain partial; numeric, formatter, compiler, owner bodies and exact holds stay unchanged. [Literal STRING cast review](../../coverage/semantics/string-offset-request-base-runtime-literal-string-cast-review.json).

Quiet emitted CASTSTRING consumes exact NULL/Boolean/digit-PINT0..9 or nonNUL INTERNED STRING VALUE under actual source/CODEfalse/read-eps/positive-line/equal captured precision, NORMAL and exact whole-state cast_apply guards. False and selected NULL retain distinct typed inputs before STRINGempty→INT0; computed3 and nested STRING identity preserve the bounds key. Existing Warning/Throwable, ownership, cleanup and budget rules remain. [Review](../../coverage/semantics/string-offset-request-base-runtime-interned-string-cast-review.json).

The separate STRING branches require recursively certified one-byte nonNUL INTERNED operands, actual source/CODEfalse/read-eps/positive-line/equal captured precision, NORMAL and exact whole-state binary_apply/bitnot_value. Zend's one-character fast paths preserve the result header; empty/multibyte inputs, NUL results and raw/REQUEST inputs gain no authority. Numeric and mixed dispatch remain unchanged. [Review](../../coverage/semantics/string-offset-request-base-runtime-one-byte-string-bitwise-review.json).

Quiet emitted STRING CONCAT reuses canonical non-NUL INTERNED headers when runtime emptiness preserves an original header. Exact source/CODE/read/line/precision, actual const flags, empty CONSTCONTEXT and full-state string_concat proof preserve typed parents; allocating results and wider forms remain partial. Native4 once/source4, author1147/129-derived and independent1975/957-derived fixture cuts stay separate. Prelaw Unsupported4, original fixture failure plus 3 unrun and corrected integration-placement error retain0. Corrected8843/focused717+26 and sole acbb SL508 load16.282133s/source0 are independently clear. [Review](../../coverage/semantics/string-offset-request-base-runtime-empty-string-concat-review.json).

Quiet emitted empty CONCAT now admits certified NULL/BOOL/digit-PINT0..9 alongside non-NUL INTERNED STRING operands through actual const facts and ordered quiet whole-state preparation/stringification. Existing source/CODE/read/line/precision, empty CONSTCONTEXT and final canonical-header proofs remain. Current3+1 source4, author1133/129-derived and independent1783/779-derived fixture cuts stay separate; original timeout, wrapper/preparation failures and four UNRUN fixtures retain0. Actual690713/SL508 load15.840064s/source0 is independently clear. Allocating results, wider conversions and the known const-empty slowpath gap remain partial. [Review](../../coverage/semantics/string-offset-request-base-runtime-primitive-empty-string-concat-review.json).

Certified compiled signed64 PINT operands outside0..9 now retain their original type and actual const authority through quiet empty CONCAT, including folded10, negative1/4 and rawMAX. Ordered compiler preparation and full-state conversion preserve canonical INTERNED results; emitted wider integers and shared CASTSTRINGquiet remain unchanged. Native4 once/source4, author949/129-derived and independent1656/836-derived fixtures retain separate cuts; the preparation failure keeps0. Actual50136/SL508 load15.838813s/source0 is independently clear. FLOAT/raw/REQUEST, allocating results, the known const-empty gap and held lifetimes remain partial. [Review](../../coverage/semantics/string-offset-request-base-runtime-compiled-integer-empty-string-concat-review.json).

Quiet emitted MODULO, shifts and mixed AND/OR/XOR now consume certified nonNUL literal-INTERNED STRING values through intrinsic STRINT i eps and ordered whole-state integer conversion. Integral strings, signed zero and quiet boundary saturation retain original operands and exact PINT results; nonempty intrinsic notice vectors refuse even under suppressed reporting. Native4 once/source4, author1489/129-derived and independent2215/855-derived fixture cuts pass separately. FLOAT BYTE, STRING bitwise results and wider producers/owners remain partial; numeric, compiler, formatter, owner bodies and exact holds stay unchanged. [Literal STRING integer review](../../coverage/semantics/string-offset-request-base-runtime-literal-string-integer-binary-review.json).

Certified nonNUL INTERNED STRING values now supply exact bytes through emitted full/shorthand ternaries and ordinary coalesce. Read-eps and existing typed source, captured precision and quiet selector authority retain normal completion and the actual carrier; compiled-leaf BYTE remains disjoint. Native4 once/source4, author935/129-derived and independent1555/749-derived fixture cuts pass separately, including empty/nonnumeric bytes, skipped-arm authority and distinct raw-NUL versus selected-NUL behavior. FLOAT BYTE, explicit string casts and wider STRING producers/owners remain partial; no allocation, formatter, compiler, owner or exact held-boundary changes. [Selected STRING bytes review](../../coverage/semantics/string-offset-request-base-runtime-literal-string-bytes-review.json).

Quiet emitted XOR requires an actual NORMAL state, exact own and child source/code/read/precision facts and sequential full-state truth conversions over certified Boolean/integer/float values. Its Boolean result retains existing keys, owners and Warning cleanup. Raw BUDGET states refuse certification; only fixture discovery probes a guarded NORMAL view. Wider producers, NaN truth and lifetimes remain partial. [Runtime XOR review](../../coverage/semantics/string-offset-request-base-runtime-xor-review.json).

Quiet emitted &&/and/||/or retains actual NORMAL/source/CODE/read/precision and recursive typed truth. A decisive left skips RHS value/precision; selected right conversions retain exact full-state results. All four spellings preserve existing keys, Warning owners and cleanup; wider producers, NaN truth and lifetimes remain partial. [Runtime AND/OR review](../../coverage/semantics/string-offset-request-base-runtime-short-review.json).

The exact raw signed64 integer-tree truth certificate also composes through MODULO, shifts, bitwise AND/OR/XOR and integer-result POWER. Each own and child source/pool, recursive integer proof and quiet full-state result remains required. Native2 once/source2 and separate author272/169-derived, peer567/395-derived fixture cuts retain their own identities. [Review](../../coverage/semantics/string-offset-integer-binary-truth-base-initial-raw-leading-key-review.json).

BitwiseNot of certified signed64 integer trees retains the selected literal INTERNED header and frozen initial raw offset through returning Warnings. Exact own/child source, PINT/range/recursive-child proofs and the full-state lower bitnot_value result avoid completion-gated cached-result vacuity. Native2 once/source2 and separate author270/167-derived, independent332/196-derived fixtures retain their own cuts. [Review](../../coverage/semantics/string-offset-integer-bitnot-truth-base-initial-raw-leading-key-review.json).

Finite FLOAT ADD/SUB/MUL/DIV truth also admits exact original PINT/PFLOAT children. Source and typed pools stay authenticated; both recursive child proofs and the full operator state use the same NORMAL probe, rejecting cached-result zero-DIV forgeries under BUDGET. Native2 once/source2 and separate author264/159-derived, peer554/396-derived fixtures retain their own cuts. [Review](../../coverage/semantics/string-offset-numeric-arithmetic-truth-base-initial-raw-leading-key-review.json).

Quiet original BOOL/NULL/raw numeric STRING partners now supply finite FLOAT ADD/SUB/MUL/DIV truth through exact source and typed children, intrinsically quiet numeric conversions and the same NORMAL recursive/full-state proof. Finite quotients from strings converting to infinity are admitted; original nonfinite PFLOAT children remain excluded. Wider producers and full core remain partial. [Review](../../coverage/semantics/string-offset-coercive-arithmetic-truth-base-initial-raw-leading-key-review.json).

Shared scalar truth admits quiet signed64 integer-result ADD/SUBTRACT/MULTIPLY/DIVIDE trees with Boolean/null/raw numeric-string children. Exact source and typed pools, quiet NINT coercions and a shared NORMAL recursive/full-result probe preserve the selected INTERNED base and frozen raw key through returning Warnings. Existing integer-helper/broader-op and FLOAT rules remain unchanged; decimal FLOAT classification, nonquiet conversions, wider unary trees and held lifetimes remain partial. [Review](../../coverage/semantics/string-offset-coercive-integer-arithmetic-truth-base-initial-raw-leading-key-review.json).

Quiet signed64 POSITIVE/NEGATIVE over certified PINT arithmetic children selects literal INTERNED bases before returning initial raw-key Warnings. Exact own/child PINT source, typed pools and signed64 ranges, an original-state disjoint legacy guard and a shared NORMAL child/full-unary proof remain required. Wider producers and held lifetimes remain partial. [Review](../../coverage/semantics/string-offset-coercive-integer-unary-truth-base-initial-raw-leading-key-review.json).

Shared scalar truth admits quiet PINT unary signs over certified original Boolean/null children. Exact source, typed pools, quiet NINT coercion and the shared NORMAL recursive/full typed unary result preserve selected literal INTERNED bases and frozen raw offsets through returning Warnings. Existing integer premises remain equivalent; wider producers and lifetimes remain partial. [Review](../../coverage/semantics/string-offset-boolean-null-unary-truth-base-initial-raw-leading-key-review.json).

Shared scalar truth admits quiet signed64 integer-result MODULO, shifts, bitwise AND/OR/XOR and POWER with original INT/BOOL/NULL/raw STRING children. Exact source and typed pools, quiet NINT coercions and SAME NORMAL recursive/full typed results retain the selected INTERNED base and frozen raw key through returning Warnings. Legacy integer-helper and FLOAT rules remain; wider producers and lifetimes stay partial. [Review](../../coverage/semantics/string-offset-coercive-integer-binary-truth-base-initial-raw-leading-key-review.json).

Shared scalar truth admits folded scalar XOR and finite FLOAT children through the existing eight comparisons. Exact original types/source/pools and SAME NORMAL recursive/full typed results preserve selected literal INTERNED bases and frozen raw keys through returning Warnings. Signed zero, subnormals and quiet computed finite values retain their bits; NaN/infinities and wider producers/lifetimes remain partial at this cut. [Review](../../coverage/semantics/string-offset-folded-scalar-boolean-truth-base-initial-raw-leading-key-review.json).

Shared scalar truth certifies folded OR/AND with exact own PBOOL and both child source identities. Decisive left truth skips right value/pool demands; nondecisive evaluation preserves ordered quiet truth under one NORMAL probe. Demanded original scalar/finite FLOAT certificates preserve literal INTERNED bases and frozen raw keys through returning Warnings; wider producers and lifetimes remain partial. [Review](../../coverage/semantics/string-offset-folded-short-circuit-truth-base-initial-raw-leading-key-review.json).

Shared scalar truth certifies completed finite FLOAT powers with exact own and child source/typed-pool authority, quiet number coercions, POWERDONE and one NORMAL recursive/full-result probe. Selected literal INTERNED bases and frozen raw keys survive returning Warnings; GENERAL plans and wider producers/lifetimes remain partial. [Review](../../coverage/semantics/string-offset-completed-float-power-truth-base-initial-raw-leading-key-review.json).

Quiet scalar named instanceof authenticates namespace/import/relative targets through canonical whole-source lexical context and exact emitted CODE target; literal-name compiler-output authority and existing scalar/full-state/owner bounds remain. Self/parent/static, dynamic targets, wider NaN producers and owners/lifetimes remain partial. [Review](../../coverage/semantics/string-offset-request-base-runtime-scalar-resolved-instanceof-review.json).

Shared scalar truth now admits BitwiseNot over certified signed64 PINT children, preserving the selected literal INTERNED base and frozen raw CV offset through returning Warnings. Exact own/child source, typed pools/ranges and one NORMAL recursive/full bitnot_value probe retain quiet result authority. Wider children and lifetimes remain partial. [Review](../../coverage/semantics/string-offset-coercive-integer-bitnot-truth-base-initial-raw-leading-key-review.json).

Emitted CASTSTRING coalesce bases preserve their exact nonnull INTERNED header, including falsey strings, and frozen initial raw CV keys through returning Warnings. Exact root/read-eps and SAME NORMAL runtime VALUE proofs retain the cast carrier; the skipped literal fallback still needs exact source and pool authority. Native2 once/source2, author179/77-derived and independent402/302-derived retain separate accepted cuts. Actual9d8d8bd896 and the sole combined0d0f5d75b SL508 load16.642528873s/source0 are independently clear; wider producers and lifetimes remain partial, with all holds unchanged. [Review](../../coverage/semantics/string-offset-runtime-string-cast-coalesce-base-initial-raw-leading-key-review.json).

Direct emitted CONCAT bases preserve an exact INTERNED header through the existing quiet VALUE proof when an empty operand is nonconstant. Raw CONST-empty beside emitted nonempty remains a REQUEST allocation and is refused in both orientations. Native2 once/source2, reached prelaw26, author234/144-derived and independent363/263-derived retain separate cuts; actual6bd25d811b and its sole SL508 load16.440858809s/source0 are independently clear. Frozen raw keys, Warning cleanup and held boundaries remain unchanged; wider producers and lifetimes remain partial. [Review](../../coverage/semantics/string-offset-runtime-empty-concat-base-initial-raw-leading-key-review.json).

Literal NULL coalesce selects the emitted CASTSTRING fallback's exact INTERNED carrier through the existing SAME NORMAL VALUE proof, preserving root read-eps, compiled-left PNULL and frozen initial raw CV keys through returning Warnings. Native2 once/source2, genuine prelaw34, author239/149-derived and independent362/262-derived retain separate cuts. Actuala71c5b7ea and the sole combinedcf2631241 SL508 load16.481702748s/source0 are independently clear. Wider producers, owners and lifetimes remain partial; every exact hold remains unchanged. [Review](../../coverage/semantics/string-offset-null-runtime-string-cast-coalesce-base-initial-raw-leading-key-review.json).

Direct emitted one-byte STRING AND/OR/XOR bases preserve exact INTERNED carriers and frozen initial raw CV keys through returning Warnings. Root read-eps and the existing SAME NORMAL VALUE proof retain source/CODE/precision, one-byte children and quiet full-state operator authority. Native2 once/source2, reached prelaw38, author236/146-derived and independent360/260-derived keep separate cuts; an already-started extra peer model cut reuses those same two originals with native0. Actual5aebf1d410 and its sole SL508 load17.345459139s/source0 are independently clear. Wider producers, unary admission and lifetimes remain partial at this cut; every exact hold remains unchanged. [Review](../../coverage/semantics/string-offset-runtime-string-bitwise-base-initial-raw-leading-key-review.json).

Finite FLOAT unary signs also admit certified integer children, including minimum-integer negation overflow, with exact source and quiet typed-result checks. Recursive children and the full unary result use the same NORMAL probe. Wider producers and full core remain partial. [Review](../../coverage/semantics/string-offset-numeric-unary-truth-base-initial-raw-leading-key-review.json).

Finite FLOAT unary truth also admits certified raw numeric STRING children through exact literal/INTERNED source, intrinsically quiet numeric coercion and the same NORMAL child/full unary result proof. Wider producers and full core remain partial. [Review](../../coverage/semantics/string-offset-numeric-string-unary-truth-base-initial-raw-leading-key-review.json).

Quiet folded Spaceship certifies original scalar/finite FLOAT children, exact SOURCE/typed pools and signed64 PINT order under SAME NORMAL recursive/full comparison, preserving literal INTERNED bases and frozen raw CV offsets through returning Warnings; wider forms and held boundaries remain partial. [Review](../../coverage/semantics/string-offset-folded-spaceship-truth-base-initial-raw-leading-key-review.json).

Folded one-byte STRING complements authenticate exact own/child source and raw PSTRING pools, complemented byte and SAME NORMAL recursive/full INTERNED results, preserving literal full-ternary bases and frozen raw CV offsets through returning Warnings; computed STRING shorthand, wider forms and held boundaries remain partial. [Review](../../coverage/semantics/string-offset-string-bitnot-truth-base-initial-raw-leading-key-review.json).

Exact own/left/right SOURCE and original one-byte raw PSTRING pools; byte_binary; SAME NORMAL recursive child and full binary_apply result with the exact INTERNED byte. NUL is pooled nonowning data. Runtime/compiler/numeric and ownership rules are unchanged. Both truthy pooled NUL and falsey ASCII zero are distinguished from integer zero; initial-reference capture survives current-name rebinding. Empty/multibyte or mixed string-bitwise operands, truthy computed-string shorthand headers, wider producers/owners/lifetimes and complete core remain partial. Computed-string shorthand remains refused at this historical cut; subsequent scope is separate. [Review](../../coverage/semantics/string-offset-string-bitwise-truth-base-initial-raw-leading-key-review.json).

Actual shorthand/condition/fallback SOURCE, absent true arm and no compiled parent read, certified raw_truth, exact full-state false truth and fallback raw pool/INTERNED identity. Generic STRING reception excludes literal_bytes expressions, preserving the old literal JMP_SET rule disjointly. Runtime/compiler/numeric and owner rules are unchanged. The falsey computed condition contributes no surviving header; only its literal fallback survives. Initial-reference capture remains independent of current-name rebinding. Truthy computed STRING shorthand headers, computed empty/multibyte results, raw concatenation truth, wider producers/owners/lifetimes and complete core remain partial. Existing literal STRING shorthand behavior is retained. [Review](../../coverage/semantics/string-offset-falsey-string-shorthand-base-initial-raw-leading-key-review.json).

Quiet emitted CASTSTRING full-ternary conditions share the existing BOOL/INT/FLOAT clause through exact typed cast and full-state truth authority. Both literal arm sources, selected INTERNED identity and frozen raw CV key remain authenticated. Native2/source2 and the separate213/90,314/192 and367/245 fixture cuts are retained; wider producers/lifetimes and held boundaries remain partial. [Review](../../coverage/semantics/string-offset-runtime-string-cast-truth-base-initial-raw-leading-key-review.json).

Quiet falsey emitted BOOL/INT/FLOAT/STRING casts authenticate the exact literal INTERNED shorthand fallback through source/read-eps, SAME NORMAL typed VALUE and whole-state false truth. The frozen initial raw CV key survives returning Warning rebinding, including initial references. Native2/source2 and separate224/96 and corrected324/203 fixtures retain their cuts; wider producers/lifetimes and held boundaries remain partial. [Review](../../coverage/semantics/string-offset-runtime-cast-falsey-shorthand-base-initial-raw-leading-key-review.json).

Truthy emitted CASTSTRING shorthand conditions preserve their exact INTERNED base and frozen initial raw CV key through returning Warnings. Own/child source and read-eps, recursive VALUE and SAME NORMAL full-state truth proofs retain the cast carrier and exact literal fallback authority. The accepted execution cuts remain separate; actual13a71fbbf and its sole canonical5270949c SL508 load16.131720712s/source0 are independently closed. Wider producers and lifetimes remain partial; every exact hold remains unchanged. [Review](../../coverage/semantics/string-offset-runtime-string-cast-truthy-shorthand-base-initial-raw-leading-key-review.json).

Direct emitted CASTSTRING bases preserve their exact INTERNED header and frozen initial raw CV key through returning Warnings, including nested identity casts. Exact source/read-eps and SAME NORMAL runtime VALUE retain the carrier and existing owner/cleanup bounds. Native2 once/source2, author215/114-derived and independent347/247-derived stay separate. Actualb7107439 and sole canonical09c4c74e SL508 load16.681909007s/source0 are independently closed. Wider producers/lifetimes and every exact hold remain partial. [Review](../../coverage/semantics/string-offset-runtime-string-cast-base-initial-raw-leading-key-review.json).

Completed POWER NaNs also cross named instanceof through exact NORMAL/source/CODE/read/precision, proper recursive child certificates, quiet original coercions and unchanged POWERDONE/full-state results. General VALUE/BYTE and warningful truth stay unchanged. GENERAL/Deprecated plans and wider producers/lifetimes remain partial; exact holds stay held. [Review](../../coverage/semantics/string-offset-request-base-runtime-power-nan-instanceof-review.json).

Canonical emitted FLOAT casts of certified NaNs cross named instanceof through exact kind2/NORMAL/source/CODE/read/precision, proper recursive child certificates, unchanged bits and quiet whole-state cast_apply. General VALUE/BYTE and warningful truth retain their bounds; wider/noncanonical casts, producers, owners/lifetimes and every exact hold remain partial. [Review](../../coverage/semantics/string-offset-request-base-runtime-float-cast-nan-instanceof-review.json).

Named instanceof consumes authenticated compiled NaN operands through its own read/identity/precision certificate and returns false without truth conversion; general runtime VALUE/BYTE and warningful truth remain bounded. [Review](../../coverage/semantics/string-offset-request-base-runtime-compiled-nan-instanceof-review.json).

Emitted arithmetic NaNs also cross named instanceof through recursive source/CODE/precision authority and quiet whole-state ADD/SUBTRACT/MULTIPLY/DIVIDE under NORMAL. Four saved-native source agreements and separate author/peer fixtures pass; general VALUE/BYTE, warningful truth, wider owners/lifetimes and exact holds remain bounded. [Review](../../coverage/semantics/string-offset-request-base-runtime-arithmetic-nan-instanceof-review.json).

Emitted unary POSITIVE/NEGATIVE NaNs cross named instanceof through exact root/child source/CODE/precision, recursive NaN authority and quiet whole-state unary_apply under NORMAL. Four saved-native source agreements and separate author/peer fixtures pass; general VALUE/BYTE, warningful truth, wider owners/lifetimes and exact holds remain bounded. [Review](../../coverage/semantics/string-offset-request-base-runtime-unary-nan-instanceof-review.json).
