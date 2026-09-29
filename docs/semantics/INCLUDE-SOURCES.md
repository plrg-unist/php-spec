# Include/require source boundary

The pinned PHP 8.5.10 CLI profile uses `include_path=.:`. The finite file
snapshot is explicit input to a semantic run. It contains the canonical main
script path, a fixed CWD and
unique `(caller filename, requested operand bytes)` entries. Each entry is
either `missing` with a stream-error fact, `open_failure` with a successfully
resolved path and stream-error fact, or `opened`
with successfully resolved path, opened canonical path, and original file bytes.
Unknown keys are `Unsupported`; they are not modeled as missing PHP files.
Distinct entries naming one opened path must have identical bytes. The opened
path is a trusted, authenticated snapshot fact, separate from the display
filename and the parser's temporary file.
The stream-error bytes are explicit finite OS/stream-open facts supplied by
the snapshot; the parser and model do not derive them from Zend execution.

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
script is already included. The current execution rules cover successful file
returns and fallthrough, nested includes, once skips, and finite open failures.
Parser rejection and accepted-source compiler diagnostics remain separate
transitions to complete before this route is installed as include support.

Resolver-null but openable paths are a required followup: they have no resolved
identity for the pre-open once check. The first finite-provider implementation
marks those keys `Unsupported`, while keeping resolution and opening distinct
so that fallback case can be added without changing once semantics.
