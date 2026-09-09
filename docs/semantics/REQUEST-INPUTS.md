# Request inputs and native fixture transport

The request fixture provider is infrastructure, not PHP bootstrap semantics.
`be12200b` adds the provider; native/build evidence is `add0e4c1` and independent
transport checks are in [the review](../../coverage/semantics/request-provider-independent-review.json).
Request initialization, auto-global callbacks and their source admission remain
pending. Existing ordinary oracle invocations continue to use the sole pinned
`.tools/php/bin/php` without this provider.

A controlled fixture invocation loads `.tools/request-clock.so` through LD_PRELOAD
and inherits descriptor198 containing a regular binary input file at offset zero.
The provider receives external clock/environment facts, replaces its process's
ordered environment before PHP starts, closes descriptor198, and implements only
`gettimeofday`. It does not execute PHP, compile source, construct PHP globals,
calculate expression results or alter diagnostics. Monotonic clocks and process
timeouts remain real. The original script bytes, argv, cwd and file identities
are supplied through the normal CLI invocation.

The payload is little endian: eight magic bytes `PHPRQ001`, signed64 seconds,
unsigned32 microseconds, unsigned32 environment-entry count, then each entry as
unsigned32 byte length followed by bytes. Microseconds are0..999999. Entries must
contain `=` and no NUL; duplicate names, empty names/values and arbitrary other
bytes remain intact in their original order. Trailing/truncated data or missing
transport produces exit125 and a fixture diagnostic before any PHP execution;
this is a harness failure, never a PHP error or differential agreement.

Payload environment entries are the logical request input. Loader configuration
belongs to the transport invocation and is recorded separately. Thus a logical
LD_PRELOAD or PHP_SPEC_REQUEST_CLOCK entry is delivered to PHP as ordinary data,
including collisions and duplicates; it does not load a second library. No names
are excluded merely because an earlier prototype used them for transport. The
provider never inherits or archives the agent's environment as request data.

SpecTec must derive PHP bootstrap values from these inputs. In the pinned CLI,
`main/SAPI.c::sapi_get_request_time` computes seconds + microseconds/1000000.0;
`php_register_server_variables` produces REQUEST_TIME_FLOAT and the silently
converted integer REQUEST_TIME. Those conversions belong in pure `.watsup`.
`import_environment_variable` skips empty names and names containing space, dot
or `[`, converts numeric-string keys, and retains the last duplicate value. Raw
process entries and the resulting PHP arrays are distinct. CV allocation order,
undefined slots and lazy auto-global activation likewise remain semantic rules,
not values to obtain by dumping an oracle's initial globals.

The independent transport review covers exact integral/fractional/negative/large
clock inputs, arbitrary ordered environment bytes and collisions, descriptor
closure, monotonic progression, timeout controls, argv/path/global/environment
order, lazy SERVER behavior and diagnostics. Author evidence compares137 existing
non-clock sources against uninstrumented native execution. Neither campaign is
request-semantic coverage. Two incorrect reviewer expectations about environment
name normalization/preservation are retained before the source-backed correction.

`scripts/build-request-provider.sh` rebuilds from local C source with the documented
system compiler. Provider source, executable and harness hashes are evidence
inputs; changing or deleting the optional provider invalidates fingerprints.
Author and reviewer each performed a fresh copied-source build in a distinct
network namespace with `sudo -n unshare --net`, producing the identical binary.
The initial unprivileged namespace rejection is preserved separately. This is a
provider-only offline check; the mandatory final whole-project offline rebuild,
full syntax/source audit and core closure remain outstanding.

The broader request record is still being implemented. It must explicitly carry
configuration, argument/stdin bytes, source/cwd identities and finite service
facts alongside clock and ordered environment entries. Missing required facts
remain Unsupported until provided. Shared fixture inputs cannot be replaced by
hardcoded sample globals or native output-derived semantic defaults.

## Bootstrap originals

[Eight independent originals](../../coverage/semantics/request-bootstrap-independent-originals.json)
retain explicit native request inputs before runtime admission. They confirm that
`check_http_proxy` replaces imported HTTP_PROXY with the first matching native
environment entry, whereas ordinary duplicate keys keep the last value. Empty
first values and case-sensitive names remain distinct. Reserved SERVER entries
are overwritten without changing their existing insertion positions; later
script metadata keys append. CLI argc/argv remain present even with
`register_argc_argv=0`; omitting S from `variables_order` leaves SERVER empty while
global argc/argv remain. The JIT-disabled registration order is also retained.
These source-backed observations are requirements for bootstrap semantics, not
semantic agreements. The [binding](../../coverage/semantics/request-bootstrap-independent-binding.json)
retains the exact capture script and immutable original hash.
