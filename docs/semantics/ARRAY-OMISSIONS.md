# Ordinary array omissions and compiler context

Ordinary Array.items now has nullable slots, sharing the existing List.items field
domain. A hole keeps its original index; it is not a new expression constructor.
The checked schema still has169 constructors, with70 deduplicated field domains.
The printer preserves omitted trailing slots in short and long array syntax.

Zend rejects a visited ordinary hole during the array constant prepass, before
runtime and before pass-two key insertion or scalar unpack rejection. It visits
all values then keys, even after discovering a dynamic item. A later hole uses
the preceding original value/unpack operand line. An initial hole uses the active
compiler context; arrayFirstHoleLine retains its source context for ordinary entry.
A skipped array can therefore be legal, for example false && [,$x]. Runtime
ARRAY_NEXT rejects a raw ABSENT slot explicitly; admitted source holes never reach it.

The prepass has explicit, source-backed barriers and child traversals. Calls,
assignments, print/exit/throw/yield and other enumerated Zend defaults stop without
walking children; properties and NEW visit their specified children. Argument
unpack is a barrier distinct from array unpack. Coalesce retains selected-child
redirects. Cast folding consumes the shared pure cast API under Zend's narrower
constant eligibility rules; ordinary cast execution is a separate milestone.
No unknown expression is silently classified as nonconstant. Known classconstant
lookup, named ::class, magicconstant context and remaining operator folds remain
explicit prerequisites where their value is required; full prepass coverage is
not claimed. In particular Attribute::TARGET_CLASS cannot be discarded as an
unknown value, because its branch selection can change which static error wins.

concatExprLine records the parser's concat reduction lookahead, while pure
parser_literal recognizes only the scalar ZVAL forms actually folded by Zend's
parser. Compiler facts cannot substitute for that parser provenance. nullaryExprLine
records the otherwise lost reduction line only for bare yield and exit/die.
Retained sources prove identical complete checked ASTs can have different native
hole lines without this field. Existing checked token spans distinguish bare exit
from exit(); a wider valid span uses its existing endLine. Missing/nonpositive
required lines and missing/invalid spans stay Unsupported, while edited positive
context is consumed as supplied. Typed checking validates representation, not a
claim that edited metadata came from the original source.

PHP8.5 also lowers clone and exit/die keyword forms into synthetic calls.
Legacy ExprClone consumes cloneExprLine; full checked-AST equality witnesses
prove the lookahead cannot be recovered from its child or endLine. Named/unpack/
multiargument unqualified keyword calls use their existing endLine. Qualified
and namespace-relative calls preserve ordinary name-line behavior, including
uppercase keyword controls. Empty shell expressions use their existing endLine.
The existing pure ASCII name-folding functions are shared from10-bytes.

The prerequisite has bounded source, compiler, metadata, ownership/resumption and
independent review gates. Their reports do not establish complete core semantics
or refresh the full source closure; that campaign follows combined ordinary source
activation. Raw disagreements and retired syntax-phase exemptions remain immutable
history. Full syntax validation and a fresh offline build remain required final gates.
