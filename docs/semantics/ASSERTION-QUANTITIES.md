# Assertion INI quantity warnings

The bounded PHP 8.5.10 rules preserve the parsed numeric quantity separately
from current raw INI bytes. Parsing warnings run the real error handler before
the update completes. The quantity and old return value stay frozen while
handler writes, restore or an original thrown Throwable survive. A later
negative-mode refusal reads the live mode and returns false without installing
the rejected raw value. The [review ledger](../../coverage/semantics/assertion-quantity-review.json)
keeps the exact source and reached-state cuts.

Runtime strings carry immutable bytes and either an interned identity or an
authenticated request identity. Literal execution, scalar conversion, bounded
concat/interpolation and bitwise producers retain their matching Zend identities;
CV, reference and string-to-string copies preserve them. Equality, truth, type,
keys, names, output and trace rendering observe bytes. Only the INI raw-install
comparison observes identity. These tokens add no heap owner or destructor;
legacy producers with unknown identity remain explicit Unsupported when an INI
update needs that identity.

`ini_get` canonicalizes empty and one-byte strings and shares longer request
strings. Startup assertion strings are interned at this target. A
malformed outer update can therefore install its raw input after a same-pointer
nested write, while an interned-old nested replacement can leave different raw
bytes and numeric mode. The decoder authenticates `MODE.INPUT` and its numeric
value; it does not require raw quantity = live mode or modified=false = original
raw. Active update records bind the exact option, input, parsed value, warning,
old raw/return, frozen original, entry modified bit, caller and resume phase.

The startup `INIT` stays immutable. A fresh `ini_set` captures current raw as the
per-round `ORIGINAL` before updating, even when reentrant restore left modified
false with malformed raw. `ini_restore` parses the frozen saved input and runs its
warning handler. Successful completion installs the live saved original and
clears modified, including when the original shared Throwable is pending. If a
nested restore already cleared that live original, outer completion installs raw
NULL with modified=false while preserving the frozen parsed mode. The cached
`ORIGINAL` remains the last authenticated string; it is not a live saved pointer
when modified=false. The existing directive getter returns canonical empty bytes,
distinct from a missing directive's false result. Later no-op restore leaves NULL
and the real `MODE.INPUT` unchanged.

Retained-entry Stringable SET converts the option once, replaces actual argument0
and then snapshots the old return. Frozen records authenticate the converted call
and borrowed original conversion; only the converted call owns and supplies trace
arguments. Warning/refusal handlers may retire the Option without delaying its
destructor or invalidating source evidence. Pending shared Throwable identity and
normal false refusal both survive completion. Stringable RESTORE uses a separate
unary converted call with frozen `INPUT=ORIGINAL` and null return. Parsing warnings
receive the converted option in traces; successful restore commits the live saved
original despite handler raw writes, Option retirement or the shared Throwable.

NaN SET snapshots its old return before formatting the scalar value. The formatted
`NAN` input stays frozen through its conversion warning; raw pointer/original
capture occurs afterward, using the live handler-modified state. A pending shared
Throwable survives the subsequent parsing warning and update. An eligible handler
is skipped for that second warning; default reporting remains active when ineligible.
Byte authentication does not repeat conversion or callback dispatch.

Retained-owner Stringable descriptions convert once before truth in enabled weak
assertions. Successful conversion replaces only argument1 and resumes the entered
test even if the callback disabled later assertions. During the cast, implicit
trace frames retain the original description object; assertion failure afterward
stores the converted string and message. A cast throw propagates the original
Throwable without assigning the outer return. Disabled direct/dynamic calls retain
their existing argument-evaluation distinction. Unpacked descriptions and last-owner
entry/handoff cleanup remain explicit Unsupported, not completed core behavior.

The engine releases a frozen modified `prev_value` after a successful warning
callback, even when a nested update already replaced and released that request
raw retain. Four retained originals expose the resulting lifetime defect; a
post-outer probe reads `pin:4` after a later float-string allocation. The model
stops successful completion with `reentrant assertion INI retired request-string
owner` when modified request OLDRAW has been replaced and the live saved original
does not retain it. It preserves same-allocation getter and interned-old paths. It does
not simulate allocator reuse or freed string contents. These controls have zero
native agreement; see [the discrepancy](DISCREPANCIES.md).

Seventeen safe quantity/carrier/export originals pass across preserved cuts.
Six genuine phase groups pass 234 premises: 208 well-defined checks and 26
reached boundary checks. Three affected Throwable sources and one retained
Generator renderer pass separately, with genuine trace47 and report52 checks.
The 46 typed projections are diagnostic only. The maintained catalogue includes
the safe originals and keeps four lifetime controls separate from the excluded
Count observer. Its two path-bearing outputs normalize only the recorded main
source filename, preserving literal `given.php`.
Two fresh safe recapture/restore originals pass at57ee, with182 checks at real
source frontiers plus one pure NULL trace companion. These are separate cuts;
the earlier originals, lifetime controls and failures retain their identities.
Three fresh Stringable SET originals pass at7eaee with236 checks at real frontiers,
including a projected converted-call ownership query. These checks cover genuine
handoff/commit, refusal/shared throw, converted trace arguments and Option owners0
after handler retirement; they are not236 distinct states. Two further safe
Stringable RESTORE originals pass at05db with211 frontier checks, including one
owner projection. The shared Throwable is observed while its handler frame is
active and after actual restore completion, before catch; the retired Option
has no allocation or owner at either frontier. Earlier cuts remain separate.
Two safe NaN originals pass atc2b195 with247 checks at actual entry, conversion,
parsing and shared-throw frontiers, plus eight explicitly projected trace-clear
companions. The original unsupported baseline and failed entry certificate stay
zero credit; the corrected pure byte proof is checked at the real call entry.
Two safe cleared-original restore originals pass at242576 with323 checks at actual
outer completion, handler/caller throw, getter and no-op frontiers, plus12 pure
helper exclusions. The normal path checks three genuine PhpSteps; the pending
path checks two after observing the same Throwable before catch. The prior
cleared-original Unsupported baseline remains zero credit.
Three fresh retained-owner description originals pass atb4ea with265 checks at real
entry, return, published throw and cast/caller trace frontiers plus4 pure ownership
exclusions. The fixture preserves raw throwing PhpStep facts and checks admission
after the actual driver publishes THROW_SEARCH. The original premature-descriptor
failure remains zero credit; these are checks, not269 distinct states.

```sh
python3 tests/semantics/method_runtime.py --catalogue tests/semantics/assertion_cases.json --match assertion-quantity
python3 tests/semantics/method_runtime.py --catalogue tests/semantics/assertion_cases.json --match assertion-carrier
```

Required follow-ons remain explicit: new SET and already-active SET/NaN
continuations encountering NULL raw stop before further conversion, pointer comparison or
original capture. Zend quantity parsing dereferences a NULL string; no source
probes SET-fromNULL or NULL parsing. This supported getter/no-op domain is separate
from the intentional lifetime divergence above. Last-owner Stringable SET/RESTORE
entry cleanup remains required. Description last-owner entry/handoff, unpack and
weak scalar trace-argument replacement, wider string identity producers, exporter
forms and callback paths remain core work. This is bounded assertion/INI coverage.
