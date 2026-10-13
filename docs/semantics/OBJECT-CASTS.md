# Object casts and cached property tables

`(object)` preserves existing object identity and allocates a fresh `stdClass`
for scalar and array operands. Null creates no property; other ordinary scalars
populate `scalar`. Array keys become property names, including numeric and
leading-NUL bytes that ordinary property access cannot create.

An all-string array cast can share its table with the object. `OBJECTTABLES`
records that ownership: the object owns the table, while its projected slots add
no duplicate reference owners. Property writes, reference acquisition and unset
separate shared tables; a sole reference wrapper unwraps only on a genuine copy.
Fast stdClass clones share the table. Array round trips convert canonical numeric
names back to integer keys and preserve append history. Materialization and copies
retain live object-foreach cursor positions across unset tombstones.

[Ordinary mixed tables](../../coverage/semantics/mixed-property-stringable-comparison-review.json)
now cache nonowning INDIRECT locators for public declared slots alongside owning
dynamic buckets. The instance owns inline declared values and its current table;
dynamic mirrors add no duplicate owners. COW dereferences locators, drops underlying
UNDEF and applies normal reference-copy rules. The pinned old table still follows
live slots, while copied declared buckets keep their values. Property reads can
therefore differ from foreach and copied array views of the new table. Physical
old-table bucket count includes an INDIRECT whose slot becomes unset.

Source construction keeps these locators internal; ordinary array casts export
copied values. Copied declared-bucket reference iteration, cached ordinary cloning
and collector visitation remain explicit Unsupported boundaries. Six exact sources
and 743 reached premises/37 raw steps cover table generations, slot/cell ownership,
UNDEF and throw cleanup.

[Direct comparison materialization](../../coverage/semantics/direct-table-comparison-review.json)
now permits genuine foreach and dynamic-property table creation while the original
object-protected inline-slot comparison is active. Its captured cursor ignores new
dynamic membership; a nested cached comparison independently owns and protects the
actual tables, including implicit materialization of the other object. Three exact
sources and 383 reached premises/26 raw steps pass.

[Fast declared-property projections](../../coverage/semantics/direct-projection-comparison-review.json)
now run during the same object-protected walk without creating a cached table.
Their fresh arrays copy direct values and singleton references; shared references
remain live. Actual cast states verify copied entries, cell/object owners and
unchanged object maps/flags. Independent projected-array comparison and throwing
cleanup pass three exact sources and 503 reached premises/35 raw steps. Existing
GC, cached-clone, reference-iteration and broader lifetime limits remain open.

A NaN cast allocates the object before delivering its warning through the real
error handler. Its continuation retains the original operand category and zval
location. A borrowed CV can change during the callback; an already referenced CV
keeps the selected inner slot, while a newly introduced reference wrapper can
become the scalar property's alias. Captured values remain captured. Throw and
other abrupt retirement release the temporary object at its actual owner scope.

An unset plain CV can expose an undefined bucket. Storage uses `UNINITIALIZED`,
ordinary reads use internal `PUNDEFINED`, and quiet reads keep their existing
fallback. Object `isset` sees this bucket; array `isset` rejects it. Foreach skips
it, genuine table copies drop it, and comparisons retain the engine's raw count
and directional undefined-bucket rules. No public type name or general numeric
null approximation is assigned to this internal value.

Object foreach separates its table at reset. A requested key can then deliver a
real Illegal/Corrupt member-name notice before the selected value is copied or
promoted to a reference. The warning-only iterator marker authenticates the
selected table and bucket serial without owning either. Resumption reads that
original bucket; delayed reference promotion updates every object sharing it.
Saved handlers retain the marker until its emitter restores or discards it.
Value-only iteration does not request key diagnostics. Valid mangled names expose
their unmangled iteration key while raw storage and property-access rules stay
distinct.

[The ledger](../../coverage/semantics/object-casts-review.json) separates thirteen
full source comparisons, 208 source-derived ownership/authentication premises,
compiler cutoffs and publication. It includes the first model agreement for the
earlier multiline interpolation source with a nonempty cast holder. Original
expired-reference/expired-bucket sources and a longer companion timeout retain
zero agreement; live-owner companions are separate sources. See
[the discrepancy record](DISCREPANCIES.md) for those borrowed-pointer boundaries.
Other raw-undefined consumers, lifecycle/GC and wider callback contexts remain
required; this is partial core coverage.
