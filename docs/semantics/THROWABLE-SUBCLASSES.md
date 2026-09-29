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
observers; those call routes still need their dedicated bridges. Its recursion
is bounded by the linked-class count. Allocation materializes a live trace
array before constructor sends, even when source properties shadow internal
ones. Source instances retain their normal materialization and property rules.

The project-local PHP 8.5.10 native probes under ignored
`.tools/throwable-subclass-probes` pin inherited/source cast order, final
getter owner diagnostics, and protected override values. Those observations
are native contracts until the corresponding model paths are implemented and
differentially checked.
