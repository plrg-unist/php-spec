# Positional reference parameter compilation

The paired source-call runtime consumes this compiler contract for untyped,
fixed-position reference parameters and value returns. Defaults, parameter/return
types, variadics, named/unpacked arguments and reference returns retain their
separate activation boundaries. All seven existing pending signature controls
remain pending; there was no reference-parameter control to retire.

An earlier finalized user declaration supplies each parameter's BYREF flag.
An actual variable argument for a known reference parameter compiles in PPW;
known value parameters and surplus positions compile in PPR. Forward, recursive,
conditional and namespace-fallback calls retain the existing PPF/try-CV decision.
The runtime-selected parameter determines acquisition without retroactively
changing the compiler's static checks or source-backed CODEARG occurrences.

Calls used as writable DIM bases compile their call expression as a read while
retaining the enclosing write context. This applies consistently to reference
arguments, ordinary DIM assignments, reference assignments and reference-list
sources. Direct call expressions are not themselves ordinary writable targets.
The [builtin compiler contract](BUILTIN-CALL-COMPILER.md) records special lowering
that can reject an optimized builtin DIM base before runtime.

Nonvariable arguments follow their compiled result kind. The source-derived
`$ppsend_var` predicate identifies direct value calls, reference assignments,
reference destructuring and recursively a value-destructuring RHS of that kind.
Ordinary assignment, pre/post increment, conditional and coalesce results remain
values even when an internal runtime operand carries a reference cell. A direct
call result may cause a Notice and a fresh temporary reference; an actual
reference result preserves its cell. A literal or temporary-value result instead
causes the reference-send Error. Variable acquisition is a separate path.

Reference destructuring accepts a direct call RHS through the ordinary call
compiler. Runtime retains the distinction between an actual source reference and
a by-value call result: MAKE_REF does not turn the latter into an actual source
reference. The reference-element Notice and subsequent argument-send Notice have
their measured order. Argument diagnostics use their argument expression line;
ordinary call traces retain the outer call site.

The implementation reuses the existing signature normalizer, source occurrence
paths, lexical resolver, list-reference scan and compiled operand records.
Primary sources are the pinned `Zend/zend_compile.c` argument, assignment, list
and DIM compilers and `Zend/zend_vm_def.h` send/MAKE_REF handlers. These compiler
facts specify no builtin runtime bodies or complete callable family.

Historical preparation evidence is deliberately separate: the first 48 native
phases/16 descriptors, the 12 send-kind phases/36 path-kind checks, and the later
91 builtin compiler phases each retain their original source/tool bindings and
pre-repair full states. The compiler pairing manifest identifies the exact final
modules. Actual source execution, resumable-state integrity, alias/COW behavior
and ownership belong to the separately reviewed runtime evidence.
