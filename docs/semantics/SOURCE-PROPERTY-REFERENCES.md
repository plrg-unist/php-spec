# Property references

Public/protected/private property slots may point to shared reference cells. A cell carries an
ordered list of typed-property sources, identified by the owning object and
declaring property. Binding checks the prospective value before replacing the
old slot source; a failed bind leaves both bindings intact. Unconstrained incoming
cells may coerce, while already constrained cells retain their type. A self-rebind
removes and re-adds its type source, preserving native source ordering. `unset` detaches a
slot source, and object collection detaches sources in slot order. Source
metadata does not own the object. Live cells and their values remain owned by
the ordinary heap graph.

Writes through variables, array elements, property aliases, compound updates,
unpack destinations and by-reference object traversal check every source before
changing the cell. Any scalar conversions must agree on one resulting value;
conflicting conversions and rejected types leave the old value in place.
Simple assignment through typed property syntax first converts against the selected
declaration, then checks that result against the live cell sources. Variable,
untyped property and dynamic property aliases and aliased compound updates keep
the original-value checks.
By-reference parameter and return type checks do not coerce a cell held by a
typed property, although ordinary variable references may be coerced. Typed
reference increment/decrement at integer bounds uses PHP's special overflow
error and preserves the old integer. Null or false array auto-initialization
checks property constraints before allocating an array. String-offset writes
retain the assigned character as the expression result.

Nonobject property writes use the pinned PHP modify or assign error and keep
the operation's evaluation order; null and false do not create an object. The
compiler and runtime changes are in modules 137 and 138, with central writer
and cursor changes in earlier modules. Nullsafe property reference sends and public method dispatch are implemented in
their respective modules. [Property visibility](SOURCE-PROPERTY-VISIBILITY.md)
uses physical slot keys for constraints and raw names for diagnostics, including
independent same-name private slots. [Class static sources](SOURCE-CLASS-STATICS.md)
share the constraint writer through distinct declaration IDs. Resumable string
conversion, readonly, hooked and magic property access remain dependencies.
