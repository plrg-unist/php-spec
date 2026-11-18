# Direct raw FLOAT cast RHSs in allocated CONCAT bases

The allocated CONCAT VALUE certificate admits a direct STRING cast of a raw
`NScalarFloat` RHS. Its proper left BASE occupies result ID minus two; the RHS
cast appends one REQUEST row at result ID minus one. Both actual CONCAT constant
flags remain false. The existing FLOAT certificate retains compiled FLOAT bits, complete RHS
SOURCE, emitted CODE/read/line and captured/live precision under the established
[compiler-output trust boundary](COMPILED-POOLS.md). A full
CAST-to-CONCAT replay from the producer registry prefix preserves every other
state field. Later registry suffix rows remain valid producer history; initial
raw capture separately requires the fresh result row. A coherently rewritten
SOURCE tree with a stale compiler pool is outside that input contract; arbitrary
source-to-pool consistency is not rechecked by this certificate.

The direct original forms `420` from `(string)42 . (string)0.0`, then preserves
saved raw offset `2x` through the returning Warning (REQUEST3/four rows). The
reference original combines its certified NN/shorthand left `-10.5bcde` with
`(string)12.5`: saved11 reads `.` while rebound current12 would read `5`
(REQUEST5/six rows). The unchanged KNOWN temporary owner and saved-key wrapper
proofs carry the selected result across callback rebinding and budget resumption.

The pinned source route is `zend_compile_cast`, `ZEND_CAST`,
`__zval_get_string_func`, `zend_double_to_str` and `ZEND_CONCAT`. Zend may extend a
unique left temporary in place; the specification retains logical REQUEST rows
under the existing ownership bounds rather than claiming physical allocation.

Native2 were observed once at bb9e68708; sourceUnsupported2 retains zero credit.
Corrected prelaw74/85 at cd7d2cc95 proves the exact reached left/right allocation
facts while the old provider refuses. Source2 at a7853a479 reuses those exact
native bytes/profile; author199/70-derived and216/70-derived pass separate
first attempts with all508 modules in production SL. One original prelaw
compiler premise-order failure remains preserved with runtime UNRUN and zero
credit; the correction reorders fixture premises and reruns only that check.
Corrected independent252 checks pass in a separate production-SL508 cut,
including a checked unary-plus FLOAT RHS with a valid right VALUE/row/replay but
refused outer direct-raw gate. Two earlier peer fixture failures retain zero
credit: an optional-value upcast and an overclaimed stale-pool rejection. The
accepted stale-pool synthetic records the compiler trust boundary with source0.
WHOLE14 and current MAIN source5/Make1 composition are CLEAR. Fixed
actual0e4f72e7/tree7e691e19 passes the sole production-SL509 load in16.640102423s
at cap60/source0 through immutablefd08e229 and parsed cache341ac1a5. Original
canonical report/map reads are one each; author raw report/map/cache reads and
all semantic renewals remain zero. The peer-only protocol control is inactive
for both accepted author A paths. Full provenance and the separate cuts are in
the [review](../../coverage/semantics/string-offset-runtime-allocated-raw-float-rhs-concat-base-initial-raw-leading-key-review.json).

General VALUE RHSs, identity STRING casts, multirow RHSs, unary FLOAT RHSs, selected NUL, broader cleanup/release, precision histories and lifetimes
remain partial. Exact holds, reserve93807cdd6/255 and inventory169/306 with
closed0constructors+1runtime remain unchanged.
