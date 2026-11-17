# Literal STRING coalesce bases with emitted RHS

A literal nonnull STRING left operand now retains its exact INTERNED header when
coalescing with an emitted full-ternary RHS before an initial raw leading CV
string offset. The native "0" and ordinary "abc" sources preserve their headers
and captured integer offsets through returning Warning handlers; empty-string
nullness is covered separately by derived fixture checks.

A dedicated arm authenticates the raw left bytes, compiled read and INTERNED
header, both child origins/read kinds, and the whole typed NORMAL runtime value.
The existing literal-byte classifier excludes raw STRING and pure literal-CONCAT
RHS syntax from this emitted route, preserving mandatory raw-literal RHS proofs.
Immediate operand source identities remain required while deeper skipped RHS
CODE, values and precision remain undemanded. Quiet-location exclusions, carrier,
ownership, key-cell and continuation bounds stay unchanged. Pinned
`zend_compile_coalesce` and VM `ZEND_COALESCE`/`ZEND_QM_ASSIGN` select nonnull values
by type, so falsey "0" retains its original value rather than selecting the RHS.

Native2 ran once; source2 at07b7ed350 reused the exact saved originals, argv,
profile and observations. Prelaw80, author224/134-derived and independent324/224-
derived first-pass SL508 fixtures retain separate cuts; baseline Unsupported2
keeps zero agreement. A cold fixture substitution was narrowed before its first
compiler/runtime to preserve the independent negative-key probe. The exact
one-file/source-input bridge binds final8728302a3 without repeating source checks.
No execution failure occurred.

Final source8728302a3 maps to actuale1bf337223f and join76ceffde6. Its sole saved
production-SL509 load passed in16.039205512963235 seconds at cap60, source credit0.
The [review record](../../coverage/semantics/string-offset-literal-string-runtime-scalar-coalesce-base-initial-raw-leading-key-review.json)
links the independent immutable tuple and external recovery records.

Wider producers, carriers, contexts, lifetimes and full core remain partial.
Every exact hold, reserve93807cdd6/255 and inventory169/306/closed0+1 remains
unchanged; older accepted evidence is not renewed.
