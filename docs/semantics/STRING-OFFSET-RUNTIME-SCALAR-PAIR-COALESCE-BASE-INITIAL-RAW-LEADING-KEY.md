# Certified emitted coalesce RHS headers

Two emitted ordinary coalesce operands now retain their certified selected
INTERNED string header before an initial raw leading-integer CV offset. A NULL
left value selects an emitted full-ternary RHS; a nonnull STRING, including empty
and "0", retains its own header. Returning Warning handlers preserve the captured
header and integer offset for ordinary and initially referenced keys.

The emitted-RHS arm requires both child/read-eps proofs and excludes raw STRING
or pure literal-CONCAT syntax through the existing literal-byte classifier.
Their dedicated mandatory-header route remains intact. The whole typed NORMAL
runtime certificate authenticates immediate operands and demands only the chosen
value, CODE and precision. Quiet-location exclusions, source identity, full-state
quietness, carriers, ownership, key-cell and continuation guards are unchanged.
The pinned compiler's `zend_compile_coalesce` and VM `ZEND_COALESCE`/`ZEND_QM_ASSIGN`
retain nullness selection and the selected value header regardless of RHS AST kind.

Native2 ran once. Final source2 reused the exact saved originals, profile, argv
and observations. Author326/193-derived and independent439/339-derived first-pass
SL508 fixtures retain separate cuts. Baseline Unsupported2 has zero agreement.
The prelaw duplicate-module compiler rejection has semantic execution UNRUN and
zero credit; corrected72 compiled facts and the earlier plain source-v1 retain
their original identities and are not relabelled as final execution.

Source5f1d08e53 maps to actual/SAMEa55b110d4. The sole production-SL509 load passed
in 16.84144012304023 seconds at cap60, with source credit zero. The
[review record](../../coverage/semantics/string-offset-runtime-scalar-pair-coalesce-base-initial-raw-leading-key-review.json)
links the immutable tuple and external recovery records.

Wider producers, carriers, contexts, lifetimes and complete core remain partial.
Every exact hold, reserve93807cdd6/255 and inventory169/306/closed0+1 remains
unchanged; older accepted DYN evidence is not renewed.
