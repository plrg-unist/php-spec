# Default output buffers

Module391 implements PHP 8.5.10 CLI default output handlers. `ob_start()` and
an explicit NULL callback create a request-global stack;
[Module395](OUTPUT-HANDLERS.md) stages chunk0 user callbacks on explicit
operations. Invalid/effectful callback creation remains a dependency.
The APIs share checked source-call argument capture, named/unpacked defaults,
strict/weak scalar conversion and real builtin error traces.

Echo, print, inline HTML, string exit and direct-call Stringable emission feed
one byte writer. Nested buffers capture exact bytes, including NUL. At a chunk
threshold the whole accumulated buffer enters the next lower layer. Explicit
flush temporarily removes the top layer and restores it empty; clean discards
its bytes. End operations check REMOVABLE independently of CLEANABLE/FLUSHABLE.
FLAGS first narrow to signed C int32, then preserve unknown ability bits through
`& ~0xf00f`. Processing adds STARTED/PROCESSED. Status and handler lists retain
bottom-up order, exact native key order and observable allocation sizes: initial
4096 alignment or default16384, with native growth at the `<=` free-space boundary.
`ob_implicit_flush` keeps its live request flag; it does not bypass active buffers.

Content getters copy an active buffer into a fresh string. A failed nonremovable
`ob_get_clean`/`ob_get_flush` retains that snapshot through two Notices and any
handler writes. The second Notice samples the live active layer after the first
callback. A throwing handler preserves its Throwable and prevents the wrapper
notice. The no-active get-clean case returns false quietly. The native unsafe
wrapper frontier with no live handler remains explicitly Unsupported.

Request completion forces top-to-bottom default-handler flush after shutdown
callbacks and request destructors, ignoring removal capabilities. Remaining user
handler drains are explicit dependencies. BUDGET, service pauses and
Unsupported retain the stack. Output buffers are global across calls and Fiber
VM switches; stored bytes add no object/reference roots.

Ordinary stderr diagnostics bypass buffering. A selected stdout diagnostic or
visible deferred stdout fatal while a buffer is active is Unsupported until
runtime diagnostic rendering is specified. Selection still observes the original
reporting mask, silence, handler result and pending-exception rules. A sticky
OUTPUTBLOCKED marker survives compiler/resume/lifecycle completion resets; no
unbuffered diagnostic event or forced buffer output escapes this boundary.
Masked diagnostics and a handler returning true under stdout mode remain supported.

The authority is `main/output.c` (handler append/op, stack pop, status and the
`ob_*` bodies), `main/php_output.h` (flags/allocation) and matching builtin stubs.
The source runner compares original bytes and exact stdout/stderr/exit against
the sole pinned oracle. Source-reached SL checks cover copies, lower-layer writes,
notice reentry, shutdown and malformed state; synthetic completion probes are
helper controls, separate from reached service pauses. Wider callback dispatch,
startup buffering/handler profiles, stdout diagnostic rendering and non-CLI SAPI
output effects remain required. Full core stays partial.

Accepted private evidence retains26 author originals at identical1+25 cuts,
6 independent originals, and separate4+2 Unsupported controls with zero native
agreement credit. Five source-reached SL groups pass177 premises. Original
compiler/PRINT and fixture failures retain zero failed-campaign credit;
[author evidence](../../coverage/semantics/output-buffer-author.json) and
[independent review](../../coverage/semantics/output-buffer-review.json) keep
the exact inputs and external recovery paths.
