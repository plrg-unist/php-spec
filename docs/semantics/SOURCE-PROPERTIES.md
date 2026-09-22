# Public object properties

Class descriptors record ordered public instance declarations, types and
source-backed defaults. Each allocation creates owned slots: a typed property
without a default starts uninitialized, while an untyped one starts as null.
An overriding public declaration must preserve the inherited type and then
reuses its slot; early and deferred links enforce the same condition. Reads, writes,
`unset`, `isset`, `empty` and computed names use the same slots; writes apply
the declared type and report the declaring class. Dynamic properties use the
same storage, with the pinned deprecation on ordinary source classes and no
deprecation on `stdClass`. A leading-NUL computed name raises the engine error
for read, write and unset, while quiet tests remain silent.

Object `foreach` by value uses a live slot cursor, so later writes can affect
later iterations. Dynamic deletion leaves a cursor tombstone; reinsertion
appends a new slot. Array casts expose initialized properties. Loose comparison
uses declared offsets until a property table materializes, then compares live
table entries, including uninitialized declared slots. The object heap owns
property values and their nested arrays or objects across copies, calls and
abrupt cleanup. Paused tasks authenticate the property source occurrence and
line without reconstructing captured receiver values.

The compiler and runtime rules are in `135-property-compiler.watsup` and
`136-property-runtime.watsup`. [The review](../../coverage/semantics/properties-review.json)
binds source, compiler and paused-state checks. Public property references
and by-reference object traversal are documented separately in
[SOURCE-PROPERTY-REFERENCES.md](SOURCE-PROPERTY-REFERENCES.md). Private/protected
and static members, hooks, magic methods, constructors and scalar-to-object
property population remain open obligations.
