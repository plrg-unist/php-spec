# Fully qualified reserved tags in CONCAT coalesce bases

Folded CONCAT trees admit exact `NExprConstFetch(NNameFullyQualified)`
true/false/null leaves and direct unary plus/minus over them, with ASCII case
folding. Three pure byte projections reuse the corresponding plain-name rules.
Unsigned true contributes `1`; unsigned false/null contribute empty bytes.
Signed true contributes `1` or `-1`; signed false/null contribute `0`.

Original SOURCE remains fully qualified, with complete metadata and exact decoded
name bytes. The actual Name payload has no leading slash. Existing root CODE/read,
demanded typed compiler facts, precision, INTERNED header and full Expr/Name SOURCE checks
remain mandatory. Name children lack read/CODE/pool and use precision fallback14.
The STRING-only classifier, coalesce RHS and ownership bounds are unchanged.

The pinned engine route is `zend_compile_const`/`zend_try_ct_eval_const` and
`zend_compile_unary_pm`/`zend_try_ct_eval_unary_pm` in
`vendor/php-src/Zend/zend_compile.c`. Existing `compiled_special_concat_bytes`
authenticates retained typed values without a compiler API change.

Two originals cover all nine unsigned/sign/tag branches. The current-key case
uses `+\false . ""`, preserving nonnull falsey STRING `0`. The reference case
yields `11-1000bc`: saved offset7 reads `b` after the handler rebinds the current
key to8, whose byte is `c`. Returning Warning callbacks retain the saved key and
reference identity.

Native two execute once. Two production-source comparisons reuse those exact
observations; author332/242-derived and independent962/862-derived SL508
conditions pass at separate frozen cuts.
Prelaw Unsupported2 and the observation-only probe retain zero source credit.
Five maintained old pure helper expectations and one coherent FQName SOURCE
control are promoted without renewing their archived campaigns.

Actual and joined `ffe1c89ce` pass the sole production-SL509 load in
16.782138576963916 seconds with zero source credit. The independent immutable
actual/SAME tuple binds all ten source posts and preserves complete foreign
parents through the Makefile and module425 insertions. Author49 records that
tuple without reading or rerunning the saved canonical report.

The [review record](../../coverage/semantics/string-offset-literal-fqn-keyword-concat-runtime-scalar-coalesce-base-initial-raw-leading-key-review.json)
binds frozen inputs, separate validation cuts and external raw evidence. Wider
names, nested signs, coercive leaves, producers/owners/lifetimes and full core
remain partial. Exact holds, reserve93807cdd6/255, inventory169/306 and closed0+1
are unchanged; prior finite PFLOAT acceptance at a547 remains withdrawn.
