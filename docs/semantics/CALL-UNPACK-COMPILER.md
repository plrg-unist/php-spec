# Array call-unpack compilation

Compiler107 compiles unpack operands in read mode and preserves source argument
indices while runtime108 expands their arrays. Named arguments after the first
unpack use deferred fetch modes. Positional arguments after unpack, and unpack
after a named argument, fail before compiling the forbidden operand. Errors
inside an earlier operand retain their priority. Existing106 builtin name lookup
and87's named/unpack shortcut exclusions remain unchanged.

Unpack reference eligibility follows emitted operand class. The query reads the
checked source unit and its constant, redirect and resolved-name descriptors.
Ordinary CV, eligible VAR and value operands remain distinct. Assignment produces
a value; reference assignment produces VAR. Reference destructuring produces VAR,
and value destructuring forwards its RHS class except that CV is fetched to a
value. Suppression fetches CV to a value while preserving a VAR child. Ordinary
conditional and coalesce expressions materialize values, including literal-true
ternaries; source return designation does not determine these classes.

Contextual false redirects and truth redirects retain their existing compiler
meaning. Ordinary call operands stop the contextual prepass, so the tested
ordinary conditional/coalesce roots have no false redirect. A false contextual
root redirect is not claimed as an admitted source witness. Whole GLOBALS and
auto-globals are excluded from ordinary CV classification. Known builtin result
lowering remains an explicit dependency; direct and aliased array_reverse and
strlen operands compile in read mode without claiming builtin execution.

Each successful unpack NArg receives a false CODEEXPR at the final compiler
LOCATION, recording the emitted SEND_UNPACK line. Its child retains its own
operand or call line. This separates a nested call on line4, SEND_UNPACK on line5,
and callee type diagnostics using the original call line. Abrupt compilation
adds no NArg marker. The source-derived runtime projection must bind the marker,
child class descriptors and consumed redirects to the checked call.

The compiler archive retains29 original source/native/parser/lint/request
contexts and20 separate preoptimizer profiles. The first DSL formulation failure,
VAR passthrough projection failure, first paired reference and line disagreements,
and stale named compiler expectation remain distinct evidence. Explicit class
guards repair the VAR passthrough; the NArg marker repairs the unpack line without
changing suppression runtime101 or child call descriptors.

On compiler975/ca709,29 compiler phases and56 projections pass. Focused shared
gates pass60 named phases plus1 catch boundary/129 projections,58 reference-return
phases,57 typed phases plus7 boundaries,91 builtin-write phases and46 function
phases. These compiler gates do not establish runtime expansion or ownership;
the paired runtime source/state gates and installed981/3f3ca6b6 codeadb21f56
are linked separately in the [pairing record](../../coverage/semantics/call-unpack-compiler-pairing.json)
and [runtime contract](SOURCE-CALL-UNPACK.md). Fresh runtime55-source,34-protocol/824 and2-state/435 checks bind981/ec4cf850;
a reviewed unused-helper removal bridges that snapshot to installed981/3f3.
Earlier981/862dc gate identities remain separately retained. Builtin bodies, Traversable, remaining callable protocols
and complete core validation remain required.
