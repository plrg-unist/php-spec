# Source interfaces

Modules 177–180 admit source `interface` declarations, ordered multiple
`extends` lists, class `implements` lists, public abstract method prototypes,
and finite `Stringable`/`Throwable` links. The target is the pinned PHP 8.5.10
CLI. A declaration without interface dependencies may be published early;
`extends`, `implements`, and compiler-added `Stringable` dependencies defer
publication. The compiler rejects illegal interface method modifiers, bodies,
and ordinary properties at the source line. Hooked interface properties remain
outside this increment.

An unresolved source parent fails first. Otherwise the linker fetches every
direct interface before checking parent compatibility, then scans direct
references for kind and duplicate errors. It applies
method, variance, and builtin obligations in direct-list order. Each linked
interface is a tagged source origin or pinned internal name; successful
publication records those links with the class name. Paused-state checks reject
stale, duplicate, wrong-kind, unpublished, out-of-order and unsatisfied links.
Method prototypes retain their declaring owner, and concrete classes aggregate
unimplemented methods from their own declaration, class parent and direct
interfaces. `__toString` adds a `Stringable` link even when no explicit return
type was written; the method compiler supplies its effective `string` return.
The nominal relation feeds `instanceof` and object type checks. Incompatibility
diagnostics use the selected method's source file and line, including methods
declared by an ancestor or in an eval unit.

The finite builtin model admits `Stringable` and the nominal `Throwable` root
rule. A source class may implement `Throwable` only under an authenticated
`Exception` or `Error` parent chain. Module 189 compares the seven `Throwable`
getters and inherited `__toString`, then selects concrete
`Exception`/`Error` constructors and `__wakeup`, plus
`ErrorException::getSeverity`, for rooted classes. These prototypes retain
builtin owners, optional defaults, method order and line-zero diagnostics;
`__wakeup` declaration errors remain compile-time. Other internal interface
method tables and hooks (`Traversable`, `Iterator`,
`IteratorAggregate`, `ArrayAccess`), interface constants, PHP 8.5 hooked
interface properties, traits and first-class interface method selectors remain
explicit obligations. Unsupported paths are tracked separately from PHP
agreement. The source [runtime](../../tests/semantics/interface_runtime_cases.json),
[compiler](../../tests/semantics/interface_compiler_cases.json), and
[internal-method](../../tests/semantics/interface_internal_cases.json) catalogues,
with the [source-interface ledger](../../coverage/semantics/interface-author.json)
and [internal-method ledger](../../coverage/semantics/interface-internal-review.json), record
exact original-source comparisons separately from these controls and
paused-state negatives. The checked frontend retains readonly method syntax
for the authored no-trace compile fatal; the pinned parser-phase discrepancy is
listed by source hash in `tests/phase-discrepancies.json`.
