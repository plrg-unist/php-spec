# Allocation classes for constant values

Equal PHP values can have different observable omitted-default caching behavior.
The class model records that provenance without retaining additional PHP values,
heap identities, or owners. It is a prerequisite interface; defaults90/91 remain
unimplemented at this checkpoint.

`PVSCALAR` describes null, Boolean, integer and float values. `PVSTRING bool`
records whether the string is interned/non-refcounted. `PVARRAY bool entries`
records the engine's non-refcounted empty-array class and each actual key's child
class. A true array flag requires no entries; false also permits empty arrays.
The class entries preserve key order and overwrite behavior. They own nothing.

Existing45 produces `CLASSFACTS : (pcpath,pvalueclass)*` alongside its successful
folds only in constant-declaration mode. `$pfclass_at` looks up an original path.
Array construction threads classes through the same insertions and evaluated
keys used for values. Transfers consume existing scalar operands, actual keys,
and child classes. They do not independently evaluate the expression or replay
its effects. An unavailable class for an otherwise successful constant fold is
explicit Unsupported. Ordinary constant-context consumers keep their old policy.

33 exports `PCCLASS path class` alongside the matching `PCONSTANT path value`.
All folded children remain exported. The direct stored declaration root is
interned by its consumer; child pool entries inside a deferred expression keep
their raw classes. Interning does not recurse into array elements. Runtime89
validates exact source-derived class entries and keeps them out of pool owner
traversals. Observer array operands use `eps`; scalar operands can use
`pvalue?`. No discarded intermediate array value is retained by metadata.

The shared transfer rules follow the pinned constructors:

- Concatenation checks an empty left operand first, preserving the converted
  right operand's class, then checks the right operand. Two nonempty strings
  allocate. Empty-result bytes alone do not determine the class.
- String bitwise binary operations use an interned character only when both
  operand lengths are one. Unary bitwise-not uses that path for one-byte input.
  Other lengths allocate, including empty and some one-byte results.
- String conversion of integers0..9 uses character strings; floats allocate.
  Array/null/Boolean conversions follow their actual constructor branches.
- Array union duplicates its left container and preserves left-key precedence.
  A syntactically empty array is non-refcounted; an array containing an empty
  unpack still allocates. Insertion and unpack use existing NEXT history,
  including negative keys and numeric-key renumbering.
- `PVFOLD` and `PVEXEC` distinguish null-to-array conversion: folding allocates
  an empty array, while constant-AST execution uses the engine empty array.

Literal classes use checked source metadata, not decoded byte length. Quoted
strings test raw content length before escape conversion. Heredoc uses its
stripped pre-escape content. Nowdoc with a content token allocates, even if that
content becomes empty; the grammar's no-content production uses an empty string.
Existing token start/end positions distinguish these nowdoc cases. Namespace
and ordinary function-name magics preserve one-character scanner identifiers;
qualified/long names allocate. File copies and directory construction remain
refcounted. Empty missing magic contexts use the engine empty string.

Source-backed descriptor assertions are not native allocation observations.
The independent retained default-cache sources supply the observable native
basis; default receive integration must still establish effect order, cache behavior,
ownership and public-resume integrity against those originals.

Pinned source anchors: `zend_language_scanner.l` escape/single-quote/heredoc/
nowdoc constructors; `zend_language_parser.y` empty doc-string production;
`zend_compile.c` literal insertion, folding and magic constants;
`zend_operators.c` conversions, concatenation, bitwise operations and union;
`zend_ast.c` constant-AST casts; `zend_execute.h` array cast helper;
`zend_string.h`, `zend_types.h` and `zend_hash.h` allocation constructors.
The private archive binds the exact files and actual tools.
