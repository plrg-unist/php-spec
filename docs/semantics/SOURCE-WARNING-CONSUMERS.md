# Missing-CV casts, copies and argument sends

Module213 privately extends source-certified warning continuations to the six
ordinary casts, selected ternary/coalesce value copies, and ordinary by-value
positional/named sends. Explicit by-value arguments following an unpack use the
same selected-slot checks; unpack expansion itself remains outside this slice.
Each consumer retains the original null after a handler defines the variable.
Selected callees and already sent arrays retain their actual owners across
callback mutation. Named-slot errors precede the missing-CV warning.

Cast and copy results use temporaries before a later destination assignment;
a thrown callback suppresses that assignment or the selected callee body.
Direct variable assignment differs: its captured null is written to the real
destination even after the handler throws, before the same pending exception
continues. This includes unconstrained and null-admitting typed aliases. A typed
destination rejecting null remains explicit `Unsupported` until replacement
TypeError/previous-exception priority is implemented.

Folded selected-arm copies preserve the actual redirect, expression origin and
copy boundary. A forged alternative variable arm cannot authenticate against a
fixed redirect. Callback-created destination aliases are used by the later write;
the warning continuation never rereads the newly defined source CV.

Primary contracts are `CAST`, `QM_ASSIGN`, `SEND_VAR`, `SEND_VAR_EX` and `ASSIGN`
in `vendor/php-src/Zend/zend_vm_def.h`, the undefined-CV and typed-reference write
helpers in `Zend/zend_execute.c`, and assignment/ternary lowering in
`Zend/zend_compile.c`. Direct ASSIGN uses the left-variable diagnostic line.
These are the pinned PHP8.5.10 ordinary CLI profile, without OPcache/JIT claims.
Discarded `(void)$cv` has no corresponding read and is not admitted by this rule.

Preparation is compiler-only: four reached fixtures58/60/65/53=236 are typed,
with alias, folded-arm, selected Closure/prior-array owner and pending-throw
controls. Independent fixtures60/77/60=197 are separately typed. Independent
native4 originals characterize cast/copy/SEND mutation and direct ASSIGN throw
ordering; they are not model agreement. Author17 sources (16 ordinary plus one
Unsupported control), all state checks, and independent native-reused model4
remain pending. The original combined six-cast source passed natively but timed
out in the model at CLI60, earning no agreement. Six independent one-cast
witnesses retain the same limits; only their array58 fixture is re-prepared,
with the other178 retained. Fixture DSL failures retain their original reports and receive
zero semantic credit. The [ledger](../../coverage/semantics/warning-consumers-review.json)
locates preparation and native originals.

With built local tools, prepare and run the actual generated report:

```sh
python3 -B tests/semantics/warning_consumer_prepare.py
python3 -B tests/semantics/warning_consumer_run.py .tools/warning-consumers/PREPARED/report.json
```

The complete fixed selection is authenticated before affected-case filters.
Ordinary13 uses serial native45s/model90s/finite300s limits and2325s/1230s phase
limits. Original packets, streams, exits and cleanup records stay outside Git.
The [truth family](SOURCE-WARNING-TRUTH.md) retains its earlier cast Unsupported
control at its actual revision; only that affected cast source is selected here
as newly admitted behavior. Wider producers, constrained rejection, broader byref/reference-result
consumers and paused return validation remain separate obligations.
Canonical integration, combined validation and a fresh offline rebuild remain open.
