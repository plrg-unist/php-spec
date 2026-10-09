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
clears modified, including when the original shared Throwable is pending.

Retained-entry Stringable SET converts the option once, replaces actual argument0
and then snapshots the old return. Frozen records authenticate the converted call
and borrowed original conversion; only the converted call owns and supplies trace
arguments. Warning/refusal handlers may retire the Option without delaying its
destructor or invalidating source evidence. Pending shared Throwable identity and
normal false refusal both survive completion. Stringable RESTORE uses a separate
unary converted call with frozen `INPUT=ORIGINAL` and null return. Parsing warnings
receive the converted option in traces; successful restore commits the live saved
original despite handler raw writes, Option retirement or the shared Throwable.

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

```sh
python3 tests/semantics/method_runtime.py --catalogue tests/semantics/assertion_cases.json --match assertion-quantity
python3 tests/semantics/method_runtime.py --catalogue tests/semantics/assertion_cases.json --match assertion-carrier
```

Required follow-ons remain explicit: a restore callback can clear the live saved
original, leaving a nullable raw value that this string-only state does not yet
represent. That path is Unsupported, distinct from the intentional lifetime
divergence above. Zend quantity parsing dereferences a NULL string; later set/restore
from that state is not probed. Last-owner Stringable SET/RESTORE entry cleanup
remains required; NaN conversion warnings need the pre-conversion old return
snapshot. Wider string identity producers, descriptions, exporter forms and callback
paths remain core work. This is a bounded milestone, not complete assertion/INI coverage.
