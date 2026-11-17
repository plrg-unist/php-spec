# Reserved keyword CONCAT coalesce bases

Folded CONCAT trees admit plain `NExprConstFetch(NName)` leaves spelling
`true`, `false` or `null`, with ASCII case folding. The pure byte certificate
maps true to `1` and false/null to empty bytes. The STRING-only classifier and
coalesce-RHS exclusions remain unchanged; ordinary constants, fully qualified
and relative names, FLOAT leaves and wider expression forms remain partial.

The existing root CODE/read, exact INTERNED header, precision and complete
Expr/Name SOURCE checks still authenticate the base. The actual compiler
retains typed BOOL/NULL pools and CODE for ConstFetch expressions, while Name
children have no compiled read, CODE or pool. Their precision uses the existing
fallback 14. No compiler API or ownership gate changes.

The false/null witness yields nonnull falsey STRING `0` and skips the emitted
ternary RHS. The true-prefix reference witness yields `1bc`: saved index 1
reads `b` after the Warning handler rebinds the current key to 2, whose byte
would be `c`. The saved key and reference identity remain authoritative.

The pinned engine route is `zend_try_ct_eval_const` in
`vendor/php-src/Zend/zend_compile.c`, which substitutes reserved true/false/null
before ordinary constant lookup; existing `compiled_special_concat_bytes`
provides the retained typed pools and header. New semantic behavior is confined
to two pure byte cases in module 425.

Native two once, two original-source agreements reusing those saved native
observations, author 323/233-derived and independent 505/405-derived retain
separate first-pass SL508 cuts. Compiler/runtime caps stay 120/180 seconds.
The prelaw two Unsupported outcomes and the observation-only fact probe retain
zero source credit. Four affected older integer helper queries are promoted
without renewing their accepted campaigns.

Actual and joined `894482bce` pass the sole production-SL509 load in
16.438920544 seconds with zero source credit. The independent actual/SAME
tuple binds the unique module-425 and Makefile additions while preserving
complete foreign parents and four later Makefile recipes. Author48 records
that immutable tuple without rereading or rerunning the saved load.

See the [review record](../../coverage/semantics/string-offset-literal-keyword-concat-runtime-scalar-coalesce-base-initial-raw-leading-key-review.json)
for exact frozen revisions, hashes and external raw evidence. Full core and
the string-offset family remain partial. Exact holds, reserve93807cdd6/255,
inventory169/306 and closed0+1 are unchanged; finite PFLOAT acceptance at a547
remains withdrawn with zero credit.
