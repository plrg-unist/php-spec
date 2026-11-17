# Direct reserved-keyword signs in CONCAT coalesce bases

Folded CONCAT trees admit direct unary plus/minus over plain reserved
`NExprConstFetch(NName)` true, false and null leaves. ASCII case folding remains
exact. True supplies integer 1 or -1; false/null supply integer 0 for either
sign. Four pure byte cases in module 425 preserve the existing STRING-only
classifier, coalesce-RHS exclusions and all ownership gates.

The existing root CODE/read, exact INTERNED header, precision and complete
Expr/Name SOURCE checks remain mandatory. Measured compiler state retains typed
integer/Boolean/null pools, identity reads and folded CODE for sign/ConstFetch nodes.
Name children have no read, CODE or pool; their precision uses fallback 14.
Intermediate CONCAT and raw tail STRING facts remain as compiled, without
adding a blanket demand on raw STRING child pools. No compiler API changes.

Two originals cover all six operator/tag combinations. The current-key source
uses `+false . ""`, yielding nonnull falsey STRING `0` and skipping the emitted
ternary RHS. The reference source contains the other five signs and produces
`1-1000bc`: saved index 6 reads `b` after the handler rebinds the current key
to 7, whose byte would be `c`. Saved value/reference authority survives the
returning Warning.

The pinned engine route is `zend_compile_unary_pm` and
`zend_try_ct_eval_unary_pm` in `vendor/php-src/Zend/zend_compile.c`: reserved
tags fold quietly through multiplication by signed 1. Existing
`compiled_special_concat_bytes` certifies their typed sign/ConstFetch facts;
the specification uses pure authored byte rules throughout.

Native two once, two original-source agreements reusing those observations,
author 307/217-derived and independent 721/621-derived retain separate first-pass
SL508 cuts. Source/A at e53 remain unchanged through the B-only final freeze b82.
The prelaw Unsupported outcomes and recorded preparation issues keep zero credit.
Actual and joined `04d52e8` pass the sole production-SL509 load in
16.742607196 seconds with zero source credit. Independent immutable tuple f03633bb
binds the complete nine-file composition and preserved foreign parents; author48
records that tuple without rereading or rerunning the saved load.

Exactly six maintained older pure helper expectations are promoted pointwise:
two PLUS author queries, two PLUS peer queries and two SIGNED peer queries.
Their archived campaigns retain their original identities. The new author
and independent fixtures exercise the affected byte laws.

See the [review record](../../coverage/semantics/string-offset-literal-unary-keyword-concat-runtime-scalar-coalesce-base-initial-raw-leading-key-review.json)
for frozen inputs and separate validation cuts. Nested signs, FLOAT/string
coercions, ordinary/FQN/relative names and wider producers/owners/lifetimes
remain partial. Exact holds, reserve93807cdd6/255, inventory169/306 and closed0+1
are unchanged. Prior finite PFLOAT acceptance at a547 stays withdrawn; foreign
corrected FLOAT acceptance remains separate.
