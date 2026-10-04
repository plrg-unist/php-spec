# Missing-CV casts, copies and argument sends

Module213 extends source-certified warning continuations to the six
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

Ordinary ternary copies authenticate a fixed compiled condition without rereading
its live variable. Prepass copies retain the actual redirect, expression origin and
copy boundary. A forged alternative arm cannot match either fixed selection. Callback-created destination aliases are used by the later write;
the warning continuation never rereads the newly defined source CV.

Primary contracts are `CAST`, `QM_ASSIGN`, `SEND_VAR`, `SEND_VAR_EX` and `ASSIGN`
in `vendor/php-src/Zend/zend_vm_def.h`, the undefined-CV and typed-reference write
helpers in `Zend/zend_execute.c`, and assignment/ternary lowering in
`Zend/zend_compile.c`. Direct ASSIGN uses the left-variable diagnostic line.
These are the pinned PHP8.5.10 ordinary CLI profile, without OPcache/JIT claims.
Discarded `(void)$cv` has no corresponding read and is not admitted by this rule.

The private author observations retain six one-cast tuples at241dd0 and fifteen
further normal tuples plus one exact Unsupported control at5728. The four
58/60/65/53 checks close at their actual revisions, with only the corrected
copy60 and previously unrun65/53 executed at215229. Independent source10 and
60/77/60 checks pass there; seven split casts have fresh native tuples and the
other three retain their original native observations. Grouped CLI60 timeouts,
the incorrect copy premise and compiler-only fixture errors stay preserved.

The fresh actual6395 composition checks the real outer-array prepass redirect,
static-reference prior argument and cached handler in source1/check94. It
preserves the installed parameter, CHDIR and constant-cache endpoints. The
complementary cached-callee source1/check96 also passes at181f: the cached handler
rebinds the live callee, while the saved call still receives7/null at the original
selected cached target.
These observations have separate revisions and profiles in the
[ledger](../../coverage/semantics/warning-consumers-review.json); they are not a
single full-family campaign or a rebuild claim.

With built local tools, prepare and run the actual generated report:

```sh
python3 -B tests/semantics/warning_consumer_prepare.py
python3 -B tests/semantics/warning_consumer_run.py .tools/warning-consumers/PREPARED/report.json
```

The complete fixed selection is authenticated before affected-case filters.
Ordinary13 uses serial native45s/model90s/finite300s limits and3000s/1230s phase
limits. Original packets, streams, exits and cleanup records stay outside Git.
The [truth family](SOURCE-WARNING-TRUTH.md) retains its earlier cast Unsupported
control at its actual revision; only that affected cast source is selected here
as newly admitted behavior. Wider producers, constrained rejection, broader byref/reference-result
consumers and paused return validation remain separate obligations.
Source-equivalent publication preserves released reporting430249, parameter
backing216 and named-class6771 paths without renewing the accepted observations.
Combined validation and a fresh offline rebuild remain open.
