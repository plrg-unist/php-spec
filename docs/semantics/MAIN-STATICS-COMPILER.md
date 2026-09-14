# Initial-main-script static declarations

Compiler113 admits static declarations in the initial script by reusing111's
ordered static-variable compiler. The named-function rule remains separate;
only the previous main Unsupported rule is replaced. No code or state schema
is added. Runtime114 authenticates MAIN ownership and preserves global binding.

The same pinned `zend_compile_static_var` operation applies to the active main
op_array. `$this` rejection precedes duplicate checking and initializer folding.
Names declared inside nested functions do not collide with main names, including
when the function declaration precedes the main static. Stored/null and ordinary
evaluated initializer modes, CV registration and distinct begin/bind lines use
the existing111 rules. The multiline bare-CV witness begins at line4 and reads
the missing variable at bind line5; its initialized null is reused afterward.

A unit's `CODE.EXPRESSIONS` is an aggregate containing nested named-function
markers. It is not a MAIN-only list. The compiler gate checks that aggregate,
the own-main projection through `ppownexpr`, and the separate function code.
Runtime MAIN eligibility must exclude function-owned declarations using checked
source ancestry. A source-compiler fixture may compile an arbitrary unit ID;
that helper fact does not admit include/eval or repeated op_array lifetimes.

Static declarations record CVs even for names whose ordinary reads are special.
Main `$_GET` reads, variable variables and the global table see the new binding;
a variable named `GLOBALS` remains distinct from direct `$GLOBALS` snapshots.
The runtime reuses its binding operation because the active MAIN environment is
the global table, and call restoration reestablishes it before a static bind.
Named-function hidden CVs retain their prior behavior.

The compiler retains six original990 contexts and six new999 contexts, including
full ordinary requests, native streams, parser and lint observations. The new
controls cover `$this`, multiline deferred reads, folded side effects, prior
nested declarations, bare-null caching and namespace constant lookup. Twelve
phase outcomes and59 source projections pass. Focused shared gates pass the
existing named-static29 phases plus one catch dependency and function46 cases.
No stale main-static pending expectation required retirement.

First fixture syntax/declaration-order errors, the accidentally reused begin
line in a generated expected bind descriptor, and an attempted overwrite of an
identical read-only private adapter copy remain failed setup evidence. Corrected
fixtures reuse retained native contexts. No runtime or compiler semantic defect
was found in these source replays; runtime protocol evidence is separate.

[Originals](../../coverage/semantics/main-static-compiler-originals.json) and
[exact pairing](../../coverage/semantics/main-static-compiler-pairing.json) retain
all executed identities. The fresh maintained compiler report belongs to the
[runtime publication](../../coverage/semantics/main-statics-runtime.json).
Closure/arrow/method identity, exceptions, dynamic sources and full-core closure
remain required; prior broad integration is historical.
