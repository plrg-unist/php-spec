# Ordinary string interpolation

The partial executable rule covers parsed ordinary double-quoted strings and
heredocs, with literal bytes, scalar conversion and real Stringable callbacks.
[The ledger](../../coverage/semantics/interpolation-review.json) retains nine exact
source agreements at `88f457d1c` and 111 distinct state premises at `a7c117b6`.
Full interpolation and complete core semantics remain open.

Zend groups adjacent nonempty literal parts and drops empty literals before
choosing its conversion strategy. The authored planner follows that effective
cardinality for ordinary parsed parts:

| Effective parts | Zend operation | Observable order |
| --- | --- | --- |
| One | CAST | Evaluate and convert the part |
| Two | FAST_CONCAT | Evaluate both producers, then convert left and right |
| Three or more | ROPE | Evaluate and convert each part before the next producer |

Two-part interpolation retains a fetched property object even if the left
callback replaces the property. Rope interpolation fetches that replacement
after the callback. Direct variables remain borrowed: their later conversion
reads the live slot. The independent sources also rebind the converting object's
only global owner and reenter interpolation; the actual callback receiver stays
live until its consumer retires.

Undefined direct variables have a further distinction. A singleton CAST uses
the original null result after its warning. FAST_CONCAT and ROPE quietly reread
the actual variable after the handler: a defined variable keeps its borrowed
operand, while a still-absent variable yields null without a second warning.
Computed names, dimensions and properties retain their producer results.
An array warning resumes the real handler but freezes the resulting `Array`
bytes. Clearing a borrowed array during that handler can release its sole typed
property owner; no temporary array root is invented. Throwing conversion emits
no partial interpolation string and skips subsequent conversions.

Source identities authenticate each part, effective mode, line, retained operands
and finish marker. Pending, entered and restored Stringable continuations use
the same owning callback mechanism as other string consumers. Plain AFTER tasks
require their first matching descriptor to have the exact adjacent FINISH.
Singleton/rope traces use the part's compiled line; two-part callbacks share the
compiled final-producer line. Multiline originals constrain both choices.

The source routes are `zend_compile_encaps_list`/`zend_compile_rope_finalize` in
`vendor/php-src/Zend/zend_compile.c` and CAST/FAST_CONCAT/ROPE handlers in
`Zend/zend_vm_def.h`. The maintained sources and control groups are:

```sh
python3 tests/semantics/interpolation_sources.py
python3 tests/semantics/interpolation_protocol.py
```

The six control groups keep the original 111 premises and repeat only 25 setup
or binding premises. Each passes within the unchanged 90-second cap. The full
and first fast-group timeouts remain failures. A native multiline probe using
unsupported non-object cast-to-object has zero model credit; its declared-holder
companion is a separate agreement. Wider source contexts, producers and legacy
interpolation compiler deprecations remain required, as do the original dynamic
file warning cases whose interpolation observers were previously Unsupported.
