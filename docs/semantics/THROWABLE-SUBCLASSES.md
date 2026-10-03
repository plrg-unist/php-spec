# Source subclasses of internal Throwables

This increment links source classes to `Exception`, `Error`, or
`ErrorException` through an authenticated internal-parent fact. Instances keep
their source `INSTANCE` identity and one ordered `OBJECTPROPS` row. The row
starts with seven inherited internal slots (eight for `ErrorException`), then
merges source declarations. Internal private `string`, `trace`, and `previous`
retain their original declaration IDs; a source private shadow adds its own
slot. Protected replacements occupy the inherited position.

`$throwable_object` means the finite built-in `THROWABLE` representation only.
It guards the built-in property denial, scalar/string conversion, foreach,
clone, callable, and comparison routes in 35, 69, 95, 136, 142, 150, 152,
and 154. Source subclasses continue through normal source object routes there.
A separate ancestry-checked Throwable membership predicate is available for
throw/catch, previous types, inherited getters/constructors, and trace
observers. Its recursion is bounded by the linked-class count. Allocation
materializes a live trace array before constructor sends, even when source
properties shadow internal ones. Source instances retain their normal
materialization and property rules. An inherited internal `__toString()` uses
the dynamic source class name; a source override follows normal method
dispatch. First-class inherited getter capture retains the source instance
and internal declaring owner in the existing getter closure; a source method
override remains on source dispatch. At uncaught termination, the override
runs as a rooted callback.
Its returned bytes stay in the completion, leaving the inherited private
`string` cache unchanged. If it throws, the new Throwable replaces the old
one and receives an internal `__toString()` trace frame.

The installed finite 189 increment also checks source `__wakeup` overrides.
Built-in parents require a public concrete method and accept a sole variadic
parameter. An omitted return emits their tentative-void deprecation at the
source method; a source ancestor supplies its own signature instead, including
through empty intermediate classes. Source parent methods are checked before
inherited built-ins, and `ErrorException::getSeverity` precedes its inherited
`__wakeup`. Activation and paused-link authentication share these predicates.
Publication190–196 preserves early-root declarations and their notices before
later compilation diagnostics, including roots captured from earlier source
units. [Publication review](../../coverage/semantics/compiler-publication-review.json)
records the replacement of the historical conservative guard and retained
native comparisons.
The [renewed review](../../coverage/semantics/interface-internal-renewed-review.json)
separates source agreements, reporting-mask controls and historical evidence.
Serialization lifecycle invocation and ReturnTypeWillChange attributes remain
required.

The project-local PHP 8.5.10 native probes under ignored
`.tools/throwable-subclass-probes` pin inherited/source cast order, final
getter owner diagnostics, protected override values, and terminal callback
output. Source differentials and paused protocols check those paths. Uncaught
rendering of a source subclass whose protected `message` holds a non-stringable
object and has no source `__toString()` override remains an explicit
unsupported boundary. PHP array callables remain on the generic unsupported
array-callable path, including inherited getters.
