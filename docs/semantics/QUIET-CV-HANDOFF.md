# Quiet access and CV context worklist

This is assigned core work after the container milestones and before broader call
integration. No entry below is a permanent exclusion or a completed family. Only
pinned PHP8.5.10 CLI NTS64 and vendor/php-src establish the target. Unsupported
observations remain failures/pending boundaries, never source passes.

## Existing request-environment boundaries

The seven exact originals and their old candidate outcomes are retained in
`coverage/semantics/ordinary-request-environment-boundaries.json`. The original
680-source campaign has673 agreements and seven pending cases; do not relabel its
aggregate as a pass. Repair these together with the shared name-access protocol:

- Computed ternary names equal to `this` in plain write and unset.
- Parser-folded literal-concat names equal to `GLOBALS` in read, void, string
  cast, plain write and unset.

Keep parser ZVAL designation separate from arbitrary constant facts and ordinary
computed names. Writable fetch, real reference acquisition, plain assignment,
compound RW, unset, quiet lookup and source-name rebinding are different protocols.
Existing inc/dec and compound this/global behavior must remain unchanged.

## Compiler header state

`$http_response_header` is a predefined-name compiler rule, even when ordinary
HTTP/library behavior is outside the current source implementation. The exact
multiline list witness is `cv-deprecated` in
`coverage/semantics/list-rhs-line-originals.json`. The private252-source list gate
retains251 agreements plus this existing Unsupported boundary; its aggregate is
not a pass. Current `$ppcvcheck` rejects header reads because the source compiler
lacks `CG(context).has_assigned_to_http_response_header` state.

Implement the state at the correct compilation-unit/frame scope. Pinned
zend_compile.c2874ff distinguishes literal CV selection from computed FETCH:
BP_VAR_R can emit deprecation, BP_VAR_W marks assignment, and other access modes
must not be collapsed into either. Recheck the exact dynamic-name branch at2915ff,
parser-folded names, repeated reads, writes before/after reads, nested control flow,
references and defaults/frame boundaries before designing a field. Nonreference
list RHS direct CV bypasses ordinary expression-line setup, including this and
header; its descriptor inherits the list AST line. Foreach direct CV value targets
use BP_VAR_R in the compiler despite being runtime assignments. These source paths
must consume the same state protocol, not local warning exceptions.

## Quiet coalesce access

The private nonvariable-lhs coalesce increment uses ordinary reads only where
zend_compile_var_inner falls through to expression compilation. Ordinary coalesce
always compiles both operands and emits a temporary; prepass folding is separate.
Its five retained quiet-location boundaries are in `.tools/coalesce-source-originals.json`:
variable, dimension, property, nullsafe property and static property. The scalar,
array and list result source cases do not establish these location paths.

Introduce faithful IS-mode compilation/runtime lookup for quiet locations. Preserve
undefined versus null, invalid key diagnostics, delayed key/name evaluation,
nullsafe short-circuiting, string offsets, existing references and absence without
creation. Add source/native and dense ownership/resumption controls before adding
`??=`: zend_compile_assign_coalesce memoizes expressions during quiet lookup and
reuses them during the later write, so an ordinary read followed by repeated target
acquisition is wrong. Its direct this/global and nullsafe checks have their own
phase/order. Unknown class/property/call protocols remain explicitly assigned until
the relevant linking/object/frame APIs exist; do not return null for missing models.

Before closure, rerun every retained original under the repaired source path,
remove only the corresponding active exemptions/boundaries, retain the old raw
failures, and obtain independent review. The final complete syntax and fresh offline
build audits remain required for the overall core objective.
