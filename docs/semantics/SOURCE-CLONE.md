# Object and closure cloning

Modules 149/150 execute unary `clone` and the PHP 8.5 language intrinsic
`clone(object, withProperties = [])`. Literal, computed, first-class and pipe
calls share the finite intrinsic identity introduced by exit/die. The compiler
preserves the temporary result of unary clone and the ordinary call result of
named/two-argument forms, including their different reference-demand errors.

Cloning allocates a fresh identity with the original class. Public declared and
dynamic slots retain their order and initialized/uninitialized/unset state.
Values use ordinary shallow copying: nested objects remain shared, arrays use
existing copy-on-write rules, singleton reference wrappers are unwrapped, and
live aliases remain shared. Retained typed-property aliases acquire another
type source, which ordinary owner release detaches.

The earlier [declared-only cached clones](../../coverage/semantics/cached-property-clone-review.json)
cut rebuilds a fresh table for ordinary public declared-only storage after genuine
object foreach materialization. Each
nonowning INDIRECT locator targets the copy; existing slot-copy and type-source
rules unwrap singleton references and retain held aliases. Later foreach observes
independent writes/unset, escaped aliases retain only the clone constraint after
source unset, and a shallow Payload survives source retirement until the copy
releases it. Five source agreements and 378 focused premises have separate cuts.
This unary-clone evidence excludes dynamic buckets, clone callbacks, readonly,
active collection and wider cached/type/lifetime histories.

[Cached callbacks](../../coverage/semantics/cached-clone-callback-review.json)
now consume that declared-public cache path through existing public zero-argument
`__clone():void` methods. Actual callback foreach reads retargeted copy locators;
singleton and held int aliases retain their distinct copy/type-source behavior.
The unary CV operand preserves source identity without owning it, so source
retirement during the callback leaves the copy/Payload live. Supplied throw
releases the failed copy and last Payload before the same catch, without committing
the assignment. Four exact originals and 659 focused premises have separate cuts.
That declared-only cut added no iteration, reference-constraint or callback-cleanup
rule; mixed dynamic callbacks, readonly, intrinsic/update and wider callback/GC
histories were excluded.

[Mixed cached cloning](../../coverage/semantics/mixed-cached-clone-review.json)
adds ordinary public nonempty declared layouts with live dynamic buckets and no
`__clone`. Declared slots copy first; a fresh table retargets their locators and
copies source-consistent dynamic items. Matching lookup mirrors reuse the copied
items without another owner or reference-copy operation. Actual foreach checks
independent writes, bucket membership and order; singleton versus held dynamic
wrappers and shared Payload retirement retain their distinct lifetimes. Four
originals and 477 focused premises include a derived late-UNSET/compaction check.
Zero-declared sharing, copied-declared DIRECT images, undefined dynamic buckets,
readonly, mixed callbacks and active collection were outside that no-callback cut.

[Mixed cached callbacks](../../coverage/semantics/mixed-cached-clone-callback-review.json)
now consume this ordinary public nonempty declared/dynamic path through existing
public zero-argument `__clone():void`. Actual callback foreach reads copied locators
and mutates independent bucket membership; singleton and held untyped dynamic
aliases keep distinct copy behavior. A borrowed source can retire with its table
while the copy remains live. Deleting the copy's sole Payload bucket runs its
destructor inside the live callback window; a supplied callback throw instead
clears that window before failed-copy and Payload cleanup, preserving the same
catch and outer destination `42`. Four originals and 756 focused checks have
separate cuts. Only the mixed callback exclusion in module 150 changes; modules
300/261/138, access, ownership and generic cleanup stay exact. Wider layouts,
readonly, zero-declared sharing, copied-declared DIRECT images and GC remain partial.

Module300 executes genuine `__clone` callbacks with the selected method's
declaring scope and the copy's called class. Access is checked before allocation;
intrinsic access errors retain the authentic `clone()` trace frame. Fixed formal
arguments and static methods are rejected in compiler order; variadic-only
methods receive an empty array. Declared returns must be void-compatible.

The callback opens one allowance per physical readonly slot. A successful write
consumes it; failed type conversion preserves it. Unsetting a genuinely
uninitialized slot clears its allowance, while initialized or previously unset
slots retain it. Indirect/reference restrictions still apply. These permissions
belong to the actual copied object and remain shared across parked Fiber stacks:
an external write can consume an allowance. Normal return, throw and exit relock
unused slots. Manually calling `__clone` opens no window.

Real closures copy capture/static storage using the live owner graph. Singleton
cells become independent; active or escaped references remain shared. Shared
static cells require the same declaration origin. Named-function closures retain
shared named-function statics, and intrinsic closures retain their builtin
identity. Class-bound closures also copy lexical/called scope and their receiver
edge; dropping the original closure cannot release the receiver of its clone.

The callable binder preserves source order for positional, named and array
unpacked arguments. It receives exact object/array types before allocation.
Property updates then run in insertion order, with integer keys converted to
names. A surviving reference update value is an error; a singleton wrapper is
read by value. Writes are weak even for strict callers, and shared property
aliases can update the original object. Closure property updates retain ordinary
invalid-name/forbidden-property error priority. Intrinsic receive/update failures
include the internal clone frame and, when applicable, the `Closure->__invoke`
wrapper frame. A missing required named object is rejected by the wrapper before
the clone body and carries only that wrapper frame.

Paused tasks authenticate source, compiled line/category, argument prefix,
selected intrinsic owner and update progress. Intrinsic argument buffers retain
their actual sent owners; unary clone retains a genuine temporary input but
adds no owner for a borrowed CV. The cached original identity may therefore
retire during the callback. The copy remains owned by its real continuation.
Exact operation/target markers authenticate each implicit callback and window
through local, saved and parked stacks. Mutable input history remains bounded.
Ordinary last-owner Fiber close retains a live callback window in its existing
saved caller VM; the permission record contributes no heap owner. The separately
tested current290 composition restores the first window before the independent
clone-with update window and rejects heap-identical forged source lines.
The exit binder positively admits only EXIT/DIE identities after the enum grows.
Protected/private properties reuse the lexical resolver and mangled slot keys described
in [SOURCE-PROPERTY-VISIBILITY.md](SOURCE-PROPERTY-VISIBILITY.md).

Initialized `SensitiveParameterValue` wrappers also use a
[bounded shallow clone](../../coverage/semantics/sensitive-value-review.json).
A fresh wrapper retains the same owning private value snapshot: Map identities
remain shared, arrays retain COW and embedded reference cells stay shared. The
original can retire while its clone keeps the value alive; readonly constructor
re-entry still fails. Three originals and 413 Boolean premises cover three clones
and eight payload/aggregate comparisons. Uninitialized wrappers, hidden export,
payload comparison effects and nonempty clone-with-properties updates remain open.

These ordinary-object, Closure and initialized-wrapper rules remain bounded.
For ordinary objects, nonempty readonly `clone(..., withProperties)` updates use
a separate second window with [captured conversions and write revisions](READONLY-CLONE-UPDATES.md);
an empty update array uses only the callback window. Generator `__clone`
creation/discard, property hooks, lazy objects,
wider callback/destructor interactions, uncloneable internal objects, Traversable
argument unpacking and broader lifecycle integration remain required. The two
retired callback/readonly negative rows keep their historical results; hook and
wider callback/destructor controls remain.

[Callback sources](../../tests/semantics/readonly_clone_sources.py) retain 20
normal originals, five declaration errors and one explicit-exit shutdown case.
[Reached controls](../../tests/semantics/readonly_clone_protocol.py) check 264
conditions across windows, three input-owner shapes and a parked Fiber.
[The callback ledger](../../coverage/semantics/readonly-clone-review.json)
keeps these cuts separate from ordinary294 and records SL276/application0.
Later cached-producer controls in the
[update ledger](../../coverage/semantics/readonly-clone-updates-review.json)
cover parked writes and maker retirement without renewing that callback cut.
The maintained `closer-window` group in
[selection controls](../../tests/semantics/readonly_clone_selection_protocol.py)
adds79 actual-parent premises; [its ledger](../../coverage/semantics/readonly-clone-selection-review.json)
keeps these separate from the earlier source and state cuts.

Matching engine sources: `zend_compile_func_clone` and `zend_compile_clone` in
`vendor/php-src/Zend/zend_compile.c`; `ZEND_CLONE` in `Zend/zend_vm_def.h`;
`ZEND_FUNCTION(clone)` in `Zend/zend_builtin_functions.c`;
`zend_objects_clone_members`/`zend_objects_clone_obj_with` in `Zend/zend_objects.c`;
`zend_closure_clone`/`zend_create_closure_ex` in `Zend/zend_closures.c`.
The maintained source, compiler, protocol and Unsupported suites are
`tests/semantics/clone_*.py`; independent acceptance is recorded separately.
