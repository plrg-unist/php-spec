# Destructuring and retained expression effects

The checked compiler and pure SpecTec runtime execute keyed, unkeyed, nested and
reference destructuring for the currently admitted scalar/array operands and
targets. They evaluate the RHS once, fetch each selected element before preparing
its target, and return the original RHS result. Nested patterns finish in source
order. Ordinary CV RHS reads snapshot before targets can overwrite their source;
the compiler supplies their special list context and diagnostic lines.

Null list reads are silent. Other scalar reads warn rather than using string-offset
semantics. Key expressions still resolve in order. Array reads copy values;
reference targets acquire the actual array-element wrappers. The source operand
has one active owner through traversal, and fetched values move into target tasks.
Target evaluation, alias rebinding, array copies and abrupt completion preserve
that ownership. Object/ArrayAccess operands and property/frame-dependent targets
remain pending.

`zend_propagate_list_refs`, `zend_compile_assign` and `zend_compile_list_assign`
in the pinned `zend_compile.c` determine referenceability checks, RHS compilation,
key/style/empty-pattern checks and fetch/store contexts. The runtime follows the
`ZEND_FETCH_LIST_R`/`ZEND_FETCH_LIST_W` paths and existing location operations.
Ordinary CV names include parser-designated literal concat names; equal computed
names do not automatically receive that designation. The per-scope
`http_response_header` compiler diagnostic remains an explicit unfinished case.

A compiler-known result may still emit stores: `(list($a)=[1])==[1]` yields a known
boolean and assigns `$a`. `PPCEFFECT`/`CODEEFFECT` retain original source occurrences
separately from operand results and constant-prepass facts. Before returning a
pooled result, execution runs the ordered topmost effect roots. Duplicate markers
are removed; a selected ancestor covers its descendants. `EVAL_EFFECT` bypasses
only its own root's pooled shortcut, retaining its children's descriptors.
Dynamic redirects run preceding effects outside the selected subtree first.
No replacement AST or original-source execution bypass supplies these effects.

Nonvariable-left coalescing compiles both sides through its ordinary compiler path,
evaluates the left once, copies a nonnull selected result or evaluates the right
when null. Existing constant-prepass selection remains separate. Variable,
dimension, property, nullsafe and static-property quiet access is explicitly
Unsupported until its full access protocol is implemented; `??=` is also pending.
The newly reached runtime array-key path raises TypeError, preserving the separate
static constant-array key error and its phase.

Accepted code `77f8d3c0`, compiler evidence `c2893aea` and runtime evidence
`54bda2fa` share closure `f1699a75`: 283 selected sources (263 additions and 20
retained cases), 24 outcome negatives, seven state programs/3,633 assertions,
23 mechanism assertions, 328 retained cross-family sources and 18 context checks.
All five compiler gates pass, including 4,867 source lints, 108 focused list lints,
32 list metadata controls and the four effect-marker consumers.
[Independent acceptance](../../coverage/semantics/destructuring-review.json)
binds exact source/archive membership, the frozen semantic inputs, 44 earlier
controls, 16 additional cross-family sources and 12 dense programs/6,192 assertions.
The original helper failure, four earlier compiler-result failures and a reused
private-source-path incident remain preserved with distinct classifications.

No constructor family closes here. The one header case, five quiet-access cases,
seven earlier request-environment cases and later object/call contexts remain
required work. Full current source validation follows the foreach integration
checkpoint; final full syntax and fresh offline validation are still pending.
