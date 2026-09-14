# Named user-function argument compilation

Compiler 104 preserves each original NArg name and expression occurrence path.
Source argument order remains separate from the destination parameter index.
A case-sensitive fixed-name lookup excludes the variadic descriptor, including
its own declared name. Compile-known fixed destinations reuse existing module 78 fetch
mode selection; unknown names, extra keys and deferred callees retain the existing
CV/dimension distinction. Nonvariable and call-result arguments remain PPR with
existing source result classification. No AST/schema/metadata extension is used.

The compiler enters a separate argument recursion at the first named argument.
It compiles subsequent named operands in source order and checks illegal later
positional/unpack syntax before compiling the offending child. Earlier abrupt
compiler results remain earlier. Diagnostic location is the compiler location
after the preceding operand; multiline originals include a nested call argument
whose line differs from the outer call. Runtime 105 owns destination slots, source
send indexing, hole defaults, received aliases and trace formatting.

Literal CV reads/acquisition can remain delayed until named SEND checks the
destination. Computed variable FETCH_R/FETCH_W and dimension fetch effects occur
earlier. Native catch projection `01` distinguishes a literal CV that was not created
on a duplicate-name error from a computed reference variable whose writable fetch
already created it. FETCH_W acquisition and SEND_REF promotion remain distinct.
The catch projection is native evidence and an explicit unsupported statement
boundary. It is not an admitted caught-exception execution.

The immutable compiler archive 049c retains 24 exact source/request/native/parser/
lint originals on 959/4854, 18 separate preoptimizer profiles, full source maps and
tool modes. It includes the historical 88d5 and 8e43 preparations and their exact
parameter-phase 0f6 dependency. Instrumented streams do not replace ordinary native
observations. Compiler-only 960/5ce1 passes actual adapter structural execution;
962/ccca adds maintained compiler tests. The maintained gate passes 41 native
compiler phases (35 normal and 6 static), six explicit pending controls and 68
source projections. These counts are compiler-phase evidence, not runtime totals.

Focused regression evidence retains reference-return 58/49, variadic 23/194,
suppression 17/131 and send 12/36. Two stale named-argument Unsupported expectations
are preserved as actual failures on 962/ccca, then retired in 962/735f with all 960
other watched files and all 962 modes unchanged. Corrected call-reference 28 and
typed-function 57 compiler phases pass. Original producer failures also remain:
one omitted the test-only pptrace definition; one reused a metadata binder for two
different NArgs. Their repaired producers pass without compiler semantic edits.

Named builtin compilation is an explicit required next prerequisite. The existing
configured 780-function arginfo inventory contains fixed names and reference modes,
but generated compiler lookup currently covers positional modes only. Root's
bounded successor plan adds fixed-name lookup before array call unpacking. Pinned
zend_compile.c:5065 disables special/frameless lowering for named/unpacked calls,
so module 87's positional-only shortcut behavior remains correct. In particular,
strlen(string:"a")[0]=1 is native lint-normal and fails at runtime as a scalar
array write. Builtin named→positional/unpack controls remain explicitly pending
under the present guard; no generic builtin static-priority closure is claimed.
Builtin runtime bodies/default filling, array call unpacking, caught exceptions,
objects and the rest of the core checklist remain required work.

A later line audit found ten real disagreements in the first runtime pair. Deferred
literal CV sends use the first argument's native AST line; known fixed and computed
operands use their own emitted lines. Fourteen retained sources cover those
contrasts, successful reads, header deprecation, later static errors, parenthesized
first arguments, positional prefixes and an enclosing typed return. The pure
positional source already ran on accepted 959 with the wrong warning line; it is
recorded as a defect in that baseline, not as Unsupported.

The correction adds a narrow module 78 argument hook and module 104 compilation helper. It writes
the emitted CODEEXPR line and compiler location while preserving original SOURCE
metadata. The first named identifier supplies a named argument-list line; an
initial positional expression supplies its native expression line. Runtime 86
resolves value sends at the emitted line. The typed-return control now matches
PHP's RETURN line 5. The separate line archive retains the original failures,
first draft declaration-order error, repaired 962/ec54 compiler and final 962/578
compiler-test snapshot. Its 55 native phases, six pending controls and 129 source
projections pass, along with the scoped shared regressions listed above rerun on
the repaired compiler. These shared gates retain seven typed-function pending
controls (the caught cache/type-failure projection and six dependent type cases),
one dynamic-call reference boundary and two caught variadic-alias projections.
All 58 reference-return compiler cases are admitted. Twelve separate opcode
profiles retain instruction evidence.

Paired runtime 968/55cd matches the six compiler/test paths exactly. Installation
candidate 968/ab389 changes only the runtime regression catalogue producer,
with 967 other files and all modes unchanged. Existing source/compiler/protocol
gates retain their 55cd identity; the corrected runtime regression is recorded
separately. The
[pairing manifest](../../coverage/semantics/named-compiler-pairing.json) records full
snapshots, transitions and canonical installation. Compiler-only gate results keep
their original identities; current runtime source/protocol evidence is separately
bound. The [original manifest](../../coverage/semantics/named-compiler-originals.json)
and [line correction manifest](../../coverage/semantics/named-compiler-line-originals.json)
retain distinct immutable archives.
