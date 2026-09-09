# Positional reference parameters

This increment extends source named calls with untyped positional reference
parameters and value returns. It remains part of the complete-core plan.
Defaults, parameter/return types, reference returns, variadics, named/unpacked
arguments, closures and other callable protocols remain separate work.

## Send and bind

The selected function origin remains fixed before argument effects. Each send
consults its normalized `psparam.BYREF`; surplus arguments remain by value.
Writable variable arguments prepare their original name/dimension expression,
acquire its location, initialize missing slots to null, and promote the final
cell. The resulting `REFERENCE` operand owns that cell immediately. Subsequent
argument effects may unset or rebind the original variable without changing the
sent cell. Frame entry binds the parameter name to the cell, while by-value
parameters and surplus arguments retain copied values.

Source expression result kind is separate from runtime reference identity.
`$ppsend_var` models the relevant compiled result distinction: calls and reference
assignments produce VAR operands; destructuring preserves its RHS result and
reference patterns request MAKE_REF. Ordinary assignments, updates, conditionals
and coalescing produce TMP operands. TMP sends to required-reference parameters
throw the exact argument error. A VAR holding an actual reference passes that
reference; a VAR holding a value emits `Only variables should be passed by
reference`, allocates a temporary reference and enters the body. Diagnostic lines
come from the original argument occurrence, separately from the outer call line.

## Shared dimensions and destructuring

The compiler's call-result dimension admission also reaches ordinary writes,
reference acquisition, destructuring and foreach targets. Writable temporary
containers use unnamed slots; acquisition transfers the held value owner to the
slot before array-copy ownership checks. A captured reference outlives its
otherwise dead temporary container. Literal-array dimensions remain statically
invalid for known writable fetches; deferred reference fetches fail at runtime
after the measured key effects. Deferred VAR expression bases can remain usable.

A reference-binding target in a temporary dimension raises the pinned engine's
`Cannot assign by reference to an array dimension of an object` error, despite
its wording also applying to returned arrays. A reference-list RHS preserves
actual references, but a value-returning call or extracted temporary value stays
a value. Each reference fetch from that value emits `Attempting to set reference
to non referenceable value`. Nested list values remain values; final reference
leaves receive detached cells. Passing the resulting value to a reference
parameter emits the separate send notice. Ordinary list results preserve actual
VAR references rather than unconditionally dereferencing the RHS.

## Ownership and public resumption

Existing operand-root traversal owns pending references in CALL_ARGS/CALL_SEND,
current/saved locals, held temporaries, and saved continuations. Return/error
unwinding uses the established frame and iterator cleanup. Temporary reference
acquisition retains a result owner until the next consumer moves it; array
literal insertion avoids counting that same owner twice.

Public entry validates source-derived reference-task origin/index/target and
pending operand modes. A sent reference must designate an allocated, marked,
defined cell. By-value sends and surplus values have KNOWN operands. These are
finite representation checks: arbitrary legitimate values, aliases, mutations,
unsets and rebindings are not reconstructed from source history.

## Engine provenance and validation boundary

The sole oracle remains vendored PHP8.5.10 CLI NTS64. Relevant authored symbols:
`zend_compile_args`, `zend_compile_list_assign`, `zend_compile_assign`,
`zend_delayed_compile_dim`, `zend_separate_if_call_and_write`,
SEND_VAL_EX/SEND_VAR_NO_REF(_EX)/SEND_REF, FETCH_DIM_W/FETCH_LIST_W, MAKE_REF,
ASSIGN_REF, and `zend_fetch_dimension_address_read` in the pinned Zend compiler,
VM definitions and executor. Ordinary-library execution is not delegated to PHP;
compiler builtin result-kind facts do not implement library bodies.

Author and independent reports bind the exact source bytes, native/provider
profiles, stdout/stderr/status, actual tools and loaded modules. Original
Unsupported states, temporary-dimension mismatches, fixture syntax/elaboration
errors, the list-target rule overlap and the interrupted exploratory state run
remain distinct from final agreement. No full-callable or full-core closure is
claimed by this increment.

Current [independent acceptance](../../coverage/semantics/reference-parameter-review.json)
binds tested882 to canonical884 through the explicit unchanged two-file bridge.
[Author history](../../coverage/semantics/reference-runtime-originals.json) and
[publication/CLI evidence](../../coverage/semantics/reference-runtime-publication-originals.json)
retain their separate scopes and original failures.
