# Foreach compiler contract

The checked `Stmt_Foreach` contract appends semantic boolean `keyByRef` at field
5, preserving iterable 0, key 1, value-by-reference 2, value 3 and body 4. There
are still 169 constructors and 70 generated field domains. The parser preserves
reference keys and short/genuine list keys; these are valid parser inputs whose
compiler rejection must remain observable. Fresh printing preserves the flag and
rejects an edited reference flag without a key target.

`67-foreach-compiler.watsup` checks reference keys before list keys and before
compiling the iterable. The diagnostic line comes from the original iterable
expression, as in pinned `zend_compile_foreach` in `vendor/php-src/Zend/zend_compile.c`.
Missing required source metadata remains explicit Unsupported. Other foreach
compilation and execution remain pending at this prerequisite checkpoint.

The three exact retired PHPT exceptions are `errmsg_042.phpt`,
`foreachLoop.006.phpt` and `foreach_list_003.phpt`; their original records remain
in [retained evidence](../../coverage/semantics/foreach-prerequisite-originals.json).
The phase ledger now rejects a recurrence of their former frontend rejection.

[Author validation](../../coverage/semantics/foreach-prerequisite-validation.json)
binds the exact private-to-production input identity, 4,884 compiler lints,
694 static comparisons and the 169-constructor occurrence audit. Canonical checks
also pass 17 exact source errors plus 24 outcome negatives, 17 focused lints,
26 metadata controls, 66 plain/UTF-16 parser profiles and 18 typed/printer
boundaries. [Independent review](../../coverage/semantics/foreach-publication-review.json)
replays the original syntax, printing, malformed payloads, compiler fixtures and
exact phase retirement. These are bounded prerequisite results; the full current
source campaign, syntax corpus audit and fresh offline rebuild remain pending.

The next paired compiler must propagate nested list references before iterable
compilation, distinguish direct CV targets from synthetic stores, compile value
before key, and preserve separate iterable ending, fetch, body and cleanup lines.
The runtime must retain per-iterator positions across array copies and exact
reference ownership; [reviewed design](FOREACH-REVIEW.md) records those constraints.
Header compiler state and nullsafe iterable access remain assigned core work,
not successful foreach observations.
