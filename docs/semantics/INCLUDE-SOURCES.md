# Include/require source boundary

The pinned PHP 8.5.10 CLI profile uses `include_path=.:`. The finite file
snapshot is explicit input to a semantic run. It contains the canonical main
script path, a fixed CWD and
unique `(caller filename, requested operand bytes)` entries. Each entry is
either `missing` with a stream-error fact, `open_failure` with a successfully
resolved path, first-warning display path and stream-error fact, or `opened`
with a successfully resolved path or a null resolver result, opened canonical
path, and original file bytes.
Unknown keys are `Unsupported`; they are not modeled as missing PHP files.
Distinct entries naming one opened path must have identical bytes. The opened
path is a trusted, authenticated snapshot fact, separate from the display
filename and the parser's temporary file.
The warning display path and stream-error bytes are explicit finite
OS/stream-open facts supplied by the snapshot; the parser and model do not
derive them from Zend execution. An already included resolved path skips before
those failure facts produce a warning.

`parse-file` has a separate checked request from `parse-eval`: request nonce,
file mode and raw CLI profile, requested/resolved/opened identities, and bytes.
The local native extension parses file syntax only. The worker then imports a
PHP-Parser AST; it supplies neither execution results nor filesystem answers.
Native `ParseError` and exact base `CompileError` retain kind, message and line.
The adapter checks resolution against the immutable snapshot before resuming
the machine. A second parse pause only occurs after a newly opened file is
selected. A skipped `*_once` call consumes its request nonce without creating a
new source unit.

Zend's `zend_include_or_eval` checks a successfully resolved path against
`EG(included_files)` before opening it, then checks the opened path and records
that identity before compiling a new `*_once` file. Ordinary include/require
record the opened path after successful compilation. The initial executed
script is already included. The bounded execution rules cover successful file
returns and fallthrough, nested includes, once skips, and finite open failures.
File parser rejection retains a failed source unit and raises a catchable
`ParseError` or base `CompileError`; a static compiler fatal in an accepted file
stops compilation globally. The [source and paused-state ledger](../../coverage/semantics/include-source-author.json)
records the current finite-provider gates and their exact scope.

While a compiled file runs, its authenticated file context contributes an
`include`, `include_once`, `require` or `require_once` Throwable trace frame at
the caller site. The frame's argument is the opened canonical path when an
inner frame precedes it; Zend omits the argument when that file frame leads
the trace. Active file and eval units interleave by fresh source ID within a
call frame, while saved call frames retain their stack order. The
[trace ledger](../../coverage/semantics/include-trace-review.json) records
the direct, nested, caught and prefixed-error checks.

An authenticated null resolver result has no identity for the pre-open once
check. The machine opens the file, then checks its canonical opened path for a
once skip. The bounded source witness uses the identity-transform
`php://filter/read=/resource=...` wrapper: its resolver result is null, while
the opened path, `__FILE__`, and include trace refer to the underlying file.
The [resolver-null ledger](../../coverage/semantics/include-resolver-null-review.json)
records the source, pause and adapter comparisons. Other wrappers and stream
transformations need their own facts and source comparisons.
The [directory failure ledger](../../coverage/semantics/include-open-failure-review.json)
records exact relative and absolute directory observations, including their
different stream-error bytes. This bounded extension is installed.
Runs that mutate CWD or `include_path` need a new authenticated resolution
context. Other permission and path errors need source comparisons.
