# Allocated string temporaries through leading-key Warnings

An emitted coalesce-left `(string)` cast of a raw `NScalarInt` child outside
0..9 retains its actual non-NUL REQUEST identity. The integer must fit signed64.
One literal STRING suffix may follow through CONCAT; its actual constant flag
also distinguishes an empty literal from an emitted empty operand. Ordinary
negative literal syntax has a UnaryMinus child and remains outside this route.

A separate allocation certificate checks original source occurrences, emitted
CODE with positive lines, absent compiled reads, demanded typed child facts and
equal precision. It replays the quiet producer against its contiguous registry
prefix and requires exact full-state equality with its allocated result. The
pure runtime-value/cast certificate remains unchanged. CONCAT retains the cast
header and final header as distinct identities.

At entry, the actual KNOWN result must be the newest request allocation. The
saved continuation owns that exact temporary with no BASECELL or manufactured
CV/ADDREF. Later callback registry rows remain intact. STRINGDATA authenticates
identity and bytes without supplying an owner; the existing KNOWN provider
rule preserves the temporary until the read or abrupt cleanup finishes.

Pinned Zend FETCH_DIM_R frees TMP operands after the string read/callback.
`zend_fetch_dimension_address_read` caches the string and leading integer
before Warning user code; `zend_long_to_str` allocates nondigit integers.
`ZEND_CAST` and source-aware `ZEND_CONCAT` supply the corresponding producers.

Two originals distinguish direct STRING `10` from CONCAT `10bc`. The reference
case fixes offset2 before the callback rebinds the current key to3: the result
is `b`, while the current key would select `c`. Saved-native source2 and author
207/93-derived plus219/93-derived SL508 conditions pass at separate cuts.
The original fixture binding/upcast failures remain zero; no native replay was
needed. Independent443/343-derived SL508 passes after four expected-option
fixture corrections; its original typing failure also remains zero. WHOLE review
and integration are recorded in the
[review record](../../coverage/semantics/string-offset-runtime-allocated-string-base-initial-raw-leading-key-review.json).

WHOLE11 and actual=joined `fc62f52f` are independently clear. The sole
production-SL509 integration load passes in16.782057845965028 seconds with
zero source credit. One physical saved-report read checked all509 module
hashes/order and complete foreign425/Make preservation. Author50 records only
the immutable actual/SAME tuple; no canonical replay or campaign renewal occurs.

[Direct noncoalesce bases](STRING-OFFSET-RUNTIME-DIRECT-ALLOCATED-STRING-BASE-INITIAL-RAW-LEADING-KEY.md)
now reuse this allocation certificate. Wider producers, casts, contexts, owners
and lifetimes remain partial. Owned-NUL
release and all exact holds, reserve93807cdd6/255, inventory169/306 and closed0+1
remain unchanged; complete core is unfinished.
