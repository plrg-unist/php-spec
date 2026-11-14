# Raw string CONCAT trees in quiet static method captures

At PHP 8.5.10 CLI/NTS/64-bit, the bounded own/inherited public static USER
method captures accept recursively nested literal-string CONCAT selectors for
both class and method names. They compose with quiet CV `??`, private `??=`
and literal/CV Empty, including the existing authenticated Shared clone and
retired-source contours. This remains a partial callable/quiet-Get slice.

`$property_magic_cv_raw_string_tree` in module407 authenticates the exact root,
every internal CONCAT and every scalar leaf, including metadata, through actual
child origins. Its optional result distinguishes a successful empty byte string
from failure. The caller requires an identical compiled root PSTRING; child
constant pools are unnecessary. Class normalization removes one optional leading
backslash after the complete join and then folds case; method names only fold
case. The nested-only guards keep the existing flat two-string arms literal and
disjoint. All member, owner, lexical/called scope, cache, history, consumer and
cleanup guards remain required. Numeric, CV and other computed leaves refuse.

The matching engine routes are `zend_compile_binary_op` and
`zend_try_ct_eval_binary_op` for folding, then `zend_compile_class_ref` and
`zend_compile_static_call` for selector compilation and method-name handling in
the vendored `Zend/zend_compile.c`. PHP execution remains authored SpecTec;
native PHP is only the pinned differential oracle.

Four original programs ran natively once before the edit; all four prelaw
outcomes were Unsupported. Saved native observations were reused for the two
author and two independent production-SL507 source agreements. Separate SL507
fixture selections are author248/330, affected-old381/466 and peer798/846; all
are source0. One author syntax-escape preparation failure and the peer's first
malformed-PSTRING elaboration failure remain preserved with zero credit. The
peer correction changed only its test's payload parentheses; runtime and source
comparison inputs stayed frozen.

Actual source `eefc1e5b7cd9753a7f8b9ed26a913468473f8751` has the independent
composition/SAME clearance for exactly seven paths, 478 insertions and one
deletion. Its sole canonical production-SL508 load passed in
15.787233690032735 seconds under a 60-second cap, quiet, stable and reaped,
with source0. This is separate from the private SL507 observations.

The [review record](../../coverage/semantics/magic-property-methodclosure-static-raw-string-concat-tree-quiet-get-review.json)
binds the supplied actual tuple and exact private cuts. Original streams,
commands, identities and preserved failures are outside Git under the recorded
evidence root. Wider selector producers and lifetimes, the exact held lanes and
complete PHP core remain unfinished; this increment changes no held boundary.
