# Backtick command construction and finite shell services

The target is PHP 8.5.10 CLI NTS 64-bit. Module389 implements backticks through
the existing interpolation rules, then validates the converted command and pauses
for explicit process facts. SpecTec and its CLI never launch the command.
Ordinary process-library calls remain outside this milestone.

`Zend/zend_compile.c::zend_compile_shell_exec` emits `E_DEPRECATED` during
compilation, including dead branches and uncalled functions, then constructs a
call to the root `shell_exec` function. Namespace functions do not replace it.
The supported profile retains the native builtin; `disable_functions` and
replacement user functions remain unsupported configuration dependencies.

`ext/standard/exec.c::PHP_FUNCTION(shell_exec)` validates a NUL-free path string
and rejects an empty command before opening a pipe. The rules preserve the real
builtin frame and converted argument in ValueError traces. Interpolation uses
the ordinary CAST/FAST_CONCAT/ROPE behavior, including Stringable callbacks,
array warnings and undefined-CV rereads. An interpolation throw prevents both
builtin validation and any service request.

## Request and response

A nonempty command requires an explicit request's ordered raw environment and a
finite current CWD. Missing facts yield `Unsupported`. CWD is sampled after
interpolation callbacks. A pending `SHELL_AWAIT` holds the original source site,
effective line, converted command, CWD, raw environment, caller depth, exact task
tail and monotonically allocated nonce. It carries the remaining execution
budget. Pure rules validate those facts before accepting a response.

The existing version-2 `--file-snapshot` may carry optional `shell_entries`.
Each entry has its sequence index as canonical decimal `id`, base64 `cwd` and
`command`, ordered base64 name/value pairs in `env`, and boolean `opened`.
An opened pipe also carries base64 `stdout` and `stderr`; a failed open carries
neither. Entries are consumed in nonce order, so repeated commands can have
different responses. The adapter checks the exact active site and matches the
entry to the frozen request and supplied snapshot. There is no native evaluation
fallback. Missing/mismatched entries keep the emitted prefix and compiler
diagnostics while returning `Unsupported`.

For an opened pipe, empty captured stdout returns PHP null and nonempty stdout
creates a fresh request string, including embedded NUL bytes. Shell exit status
does not distinguish those cases. Service stderr becomes a raw `STDERR` event,
independent of PHP warning suppression. A failed open emits the native
`shell_exec(): Unable to execute '...'` warning and returns false. A registered
error handler runs once; a normal return retains false, while an abrupt callback
keeps its completion. Nested shell operations use the same ordinary handler and
request protocols. Successful responses consume the pending context once;
forged or replayed responses are explicit `Unsupported` controls.

## Validation

`tests/semantics/shell_sources.py` compares original bytes against the pinned
oracle with the existing clock/environment fixture transport. Commands use only
fixed `printf`, `:` and `exit` shell builtins. Child-only `RLIMIT_NOFILE=4` produces
real pipe-open failures without starting a shell. The model receives independently
specified finite facts. Raw stdout, stderr and exit status remain strict.

`tests/semantics/shell_state.py` starts from checked original programs and checks
genuine pending requests, fresh string identities, corruption/replay negatives,
handler traces and budget resumption through the SL runner. The author ledger
keeps the 18 initial source agreements and the two corrected warning-handler
agreements at their distinct cuts; the original failure receives zero credit.
The 11 focused state groups pass 823 premises. See
[the author evidence](../../coverage/semantics/shell-dispatch-author.json) and
[the independent review](../../coverage/semantics/shell-dispatch-review.json).

This is finite-service execution evidence, not full PHP core closure. Wider
startup/service providers, disabled-builtin dispatch, filesystem or persistent
process effects, asynchronous effects and ordinary process-library behavior
remain outside the admitted boundary.
