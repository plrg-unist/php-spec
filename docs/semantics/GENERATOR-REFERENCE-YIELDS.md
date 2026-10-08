# Generator reference yields

Module328 preserves the producer's original `BYREF` signature and treats its
body returns as Generator completion payloads. It uses accepted call, Closure,
Arrow and return machinery; paused generic-return work is not imported.

The yield cache owns a reference cell independently of its original variable
name. Literal APIs return values, including copied array containers, while
reference foreach binds the cached cell. References inside a destructuring
pattern enable the same reference iteration even when the outer AST flag is
false. Element aliases survive loop break, producer rebinding and Generator
release; earlier API array copies retain their separate values.

Simple CV write acquisition follows old-cache retirement. Writable dimension
and property operands acquire their cell earlier, preserving readonly fetch
errors and destructor order. Reference-returning calls preserve their cell;
nonreferenceable operands raise the native Notice and keep the captured value
through callbacks. Bare yields, temporary values, `$this` and `$GLOBALS` retain
their distinct wrapping/snapshot behavior. Foreach creates a cache-only reference
when the producer has cached a value rather than a cell.

Key effects precede value effects, while simple key-CV reads remain delayed.
Callbacks can observe the previous value/key until each cache slot is replaced.
`BORROWED` records those retired bits without adding heap roots or release jobs;
readback requires the corresponding storage to remain live. Genuine Notice and
error-handler cleanup continuations authenticate their source, payload, line and
single Generator owner. Handler throws preserve the cached result and use the
actual child resumer for delegated exception reinjection.

A genuine direct-global request release can retire a paused, nondelegating frame
with no active finally. Its cache cell remains owned until ordered object release.
Request-end active finally still stops at the existing authentic Unsupported
boundary: native `C|7|F` versus modeled partial `C|7|`, with zero agreement.
Reference producers containing `yield from` retain the native compiler rejection.
Wider producer/call forms, suspension during handlers, parked running Generators,
other request/terminal paths and complete destruction/collection remain required.

Authority is the vendored PHP8.5.10 `Zend/zend_vm_def.h::ZEND_YIELD`,
`zend_compile.c::zend_compile_yield`, `zend_compile_yield_from`,
`zend_compile_foreach`/`zend_propagate_list_refs`, and Generator iterator,
resume, storage destruction and GC paths in `zend_generators.c`.

The [ledger](../../coverage/semantics/generator-reference-yields-review.json)
retains distinct source/state cuts and original zero-credit failures. The earlier
35 normal originals, promoted Arrow original and four new destructuring originals
keep their own inputs. Eight cache/alias/warning groups pass690 physical premises;
delegated warning/close adds163, nonfinalizing request release adds215, the required
terminal refusal adds40 and effective destructuring adds177. These counts include
repeated setup and do not renew the accepted321 campaigns.

Maintained focused commands, run from the project root:

```sh
python3 tests/semantics/reference_yield_prepare.py --mode full --select destructuring-inner-reference-mutates-producer-array
python3 tests/semantics/reference_yield_review.py --mode full --select source-reference-rebind-does-not-retarget-cache-alias
python3 tests/semantics/reference_yield_protocol.py --mode check --sl --select destructuring-live-reference,destructuring-cache-wrapper
python3 tests/semantics/reference_yield_delegation_protocol.py --mode check --sl
python3 tests/semantics/reference_yield_terminal_protocol.py --mode check --sl --select terminal-active-finally-refused
```

The sole oracle is `.tools/php/bin/php`, with `tests/semantics/profile.json`,
`LC_ALL=C` and `TZ=UTC`. Raw commands, source bytes, runtime identities,
fingerprints and process output remain in ignored private `.tools` directories.
No full-Generator or complete-core claim is made.
