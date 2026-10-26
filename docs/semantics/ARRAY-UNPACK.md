# Array unpacking

The checked source compiler and runtime implement array-valued spread operands
at PHP 8.5.10 CLI NTS64. Integer keys append in traversal order, preserving the
builder's next-index history; string keys replace an existing entry in place.
Nested array values retain copy-on-write behavior. Explicit embedded references
remain shared when they have multiple owners; singleton wrappers are unwrapped
for the copied entry. The source container's own wrapper history survives.

`60-array-unpack.watsup` supplies the pure transfer and shared scalar diagnostic.
`61-array-unpack-control.watsup` evaluates each spread operand once at its checked
item/value occurrence, resolves the operand at its compiler ending line, and
continues with the next original item index. The continuation owns the fresh
builder throughout operand evaluation. Transfer borrows both containers, then
restores the caller's temporary roots. It never imports a native execution result.

The constant prepass first visits every array item, retaining the existing hole
and child-error order. It then constructs a fully known array, including spread
operands. A fully known scalar spread produces a compiler fatal diagnostic;
scalar spread in a dynamic array raises a runtime Error when reached. Integer
append overflow defers constant construction to execution, preserving prior
output. The ordinary compiler treats spread operands as reads. Pooled constant
results keep their permanent occurrence owners.

Initialized user Iterators in ordinary CV spread operands now use genuine method
frames in `426-array-iterator-unpack.watsup`. The order is rewind, valid, current,
key, DIRECT insertion, cache release, then next. A raw current reference survives
key callbacks before its live payload is copied; the reference wrapper itself is
not inserted. Keys must be int|string; an invalid key raises Error before copying
the current payload. Canonical numeric-string keys append, while noncanonical strings
such as `"08"` retain their string identity. Existing string keys overwrite in place.

The continuation owns the partial builder, Iterator DATA and raw current/key
caches. Its immutable source receipt survives source-CV unset or rebinding.
Normal completion releases the cache before next and DATA at finish. Invalid-key
and current/key/next failures discard pending caches, DATA and the partial builder
within the quiet domain. This ordinary path requires an Iterator with no owning
heap children or destructor (primitive fields are allowed) and exact ordinary
public method signatures. Cache values are quiet primitives, validated strings
or finite acyclic DIRECT object-free array graphs. Current may return an ordinary
unconstrained reference cell; key remains by value. Shared child tables contribute
one edge per physical entry, independent of their parent's owner count. Path-local
validation permits shared descendants but rejects cycles, objects, debt and any
path back to the receiving builder. The no-destructor, by-value current-array
lane admits ordinary scalar reference cells as described below. Fresh
integer-graph witnesses distinguish key-time live-reference writes from later
selective COW. Other Iterator operand modes, wider reference descendants and
callback lifetimes remain partial. Unsupported Traversables
refuse explicitly rather than receiving a non-Traversable TypeError.

The bounded ordinary-CV Iterator scope now also admits a real public
`__destruct` with no owning instance children. Normal finish releases the last
DATA owner while the builder remains protected, so the destructor can mutate
globals or throw before the next literal item. A key callback's supplied
exception likewise retains the builder through DATA destruction; a destructor
exception replaces it with the original as `previous`. For an invalid bool key,
the insert step instead produces a raw Error. Same-frame throwable continuation
removes that producer, and generic eager cleanup releases the partial builder
before DATA and the cached current array. The cached array remains owned during
the destructor; there is no intervening `THROW_SEARCH`/Iterator task cut on that
route. The [DATA destructor review](../../coverage/semantics/array-iterator-data-destructor-review.json)
records the distinct source and reached-state checks. Owning instance children,
other operand modes and broader destructor reentry remain partial.

For a by-value `current()` result from an ordinary user Iterator without a
destructor, the cache also admits finite DIRECT ARRAY descendants with ordinary
scalar reference cells. The validator follows each path to reject cycles, debt,
pool-owned reference tables and builder backedges; shared sibling edges are
allowed. The raw cache and copied rows keep physical cell ownership. With an
external alias, a later COW write still reaches the shared cell. After that
alias is unset, a sole reference can be unwrapped during COW and the detached
row can change independently. The same Iterator mechanism applies to an
Iterator returned by an Aggregate getter. Three exact source agreements and
273 reached conditions (three raw steps) cover these cases in the
[reference-cache review](../../coverage/semantics/array-traversable-reference-cache-review.json).
The by-reference current route below has its own bounded admission; object,
typed, proxy, cyclic and debt-bearing descendants remain partial.

For an ordinary no-destructor Iterator whose `current()` returns a genuine
reference to an array, the raw outer cell survives `key()` and is dereferenced
when the spread entry is inserted. A key callback may rebind that cell to a
new finite row with ordinary scalar reference leaves. The spread entry copies
the new row as `DIRECT`; an independently saved old row remains unchanged.
Keeping the new row's external scalar alias shares later writes across COW;
removing it lets a sole inner reference unwrap in the detached copy. An
Aggregate getter returning the same Iterator follows this route. If `key()`
instead throws a supplied Exception after removing external names, it inserts
no entry. Quiet methodless cleanup discards the raw current, DATA and partial
builder together, then prunes their unowned nodes before catch. Four original
sources and 528 reached premises (four raw steps) are recorded in the
[by-reference Iterator cache review](../../coverage/semantics/array-iterator-byref-reference-cache-review.json).
The destructor-bearing by-reference route below has its own bounded admission;
owning Iterator fields, special cells and wider graphs remain outside both.

An ordinary Iterator with `&current()` and a real `__destruct` can return the
same outer array cell. After `key()` rebinds that cell, the spread entry takes
the new row with its scalar alias. When DATA is the last Iterator owner, the
partial builder and alias remain protected through the destructor. Its alias
and tail writes precede assignment and the next literal item. A retained
external Iterator delays the destructor until explicit `unset` after assignment;
the shared alias then updates the assigned row. A supplied key exception with
an earlier ALIAS entry keeps that partial builder until the raw current cell
and DATA retire, runs the destructor, and cancels the builder before catch.
The release continuation checks class and method history plus the builder graph
after the cached current has been cleared. A separately tested Aggregate getter
can promote the same Iterator. Four exact original source agreements include
that Aggregate promotion; strict424 and 670 reached premises (664 Boolean and
six raw steps) cover the three direct Iterator sources in the
[by-reference destructor review](../../coverage/semantics/array-iterator-byref-destructor-review.json).
Owning instance fields and special, typed, proxy, object, cyclic or debt-bearing
descendants remain partial.

`427-array-generator-unpack.watsup` adds ordinary named Generator bodies with
received parameters and reference yields, using real borrowed native resumes.
It admits ordinary unmarked CVs and owning direct named-call operands. The
iterator owns DATA; an owning call operand keeps its separate opcode owner through
traversal. No public cursor, PHP Generator-method frame or copied current-cache
owner is invented. The Generator's VALUE/REFCELL/KEY edges persist during resumed
code and after CLOSED, until actual storage destruction.

Fresh and cached-first-yield inputs rewind normally. A past-first input acquires
DATA before its rewind Exception; CLOSED acquisition throws before DATA exists.
Valid int|string keys reuse the existing append/string replacement rules, then
the live yielded value is dereferenced and copied into a DIRECT entry. Finite
DIRECT object-free array graphs retain COW; ordinary unconstrained current-reference cells
keep one physical payload edge regardless of wrapper multiplicity. Wider payloads
remain partial.

Completion releases DATA, then an owning opcode INPUT, before advancing the
literal. Failure retains the partial builder through those same releases and
real Generator finally/cache destruction, then cancels the builder. Immutable
item/function history authenticates terminal continuations after Generator
retirement without reading stale cached pointers as live owners. Explicit
payload/builder refusals retain their owners and stop. Delegation, direct
Closure/method/factory-call operands, reference-CV acquisition and wider lifetimes remain
partial. [Generator spread review](../../coverage/semantics/array-generator-unpack-review.json)
retains the separate source/state cuts and the retired A52 refusal control.

For a named by-value Generator, a yielded finite DIRECT array may also contain
ordinary defined scalar reference cells. The old value validator and the new
array branch are disjoint, and saved producer metadata excludes by-reference
Generator functions even when one yield is by value. A held outside alias stays
shared through COW; removing it permits a sole reference to unwrap in the
detached copy. The Generator retains its yielded VALUE through CLOSED. Normal
DATA release removes the final Generator owner after the body has unset its
source CV; a WeakReference observes that retirement. On a supplied body throw,
finally runs with the Generator live, then cleanup retires DATA and the partial
builder and its scalar cell. An Aggregate getter returning a named Generator
follows the same bounded route. Manual Generator methods, owning cached objects,
cyclic/debt graphs and wider producer forms remain partial.
Four original sources and 367 focused premises (four raw steps) are recorded in
the [Generator reference-cache review](../../coverage/semantics/array-generator-reference-cache-review.json).

For a named Generator function declared by reference, a real global-bound
outer reference cell may yield a finite array with ordinary scalar reference
leaves. Spread dereferences that outer cell and inserts a `DIRECT` copy of the
then-current row. Rebinding the outer cell later changes its row without
retargeting the spread entry; its inner scalar aliases can still share writes.
When an external leaf alias is removed, a separately retained old row makes a
later COW copy unwrap the sole inner reference. The same route accepts an
Aggregate getter returning the named Generator. With external outer-cell
owners removed, a supplied body throw runs `finally`; last-DATA release then
retires the outer cell before discarding the builder-held old row and inner
cell. Terminal builder checks use saved producer
history without dereferencing the retired outer cell. Four exact originals and
588 reached premises (six raw steps) cover this bounded mechanism in the
[by-reference Generator cache review](../../coverage/semantics/array-generator-byref-reference-cache-review.json).
Temporary by-value yields, owning or special reference cells, cycles and wider
producers retain their earlier boundary.

The shared cache validator also admits nested graphs returned through the existing
Aggregate promotions below. Runtime descendants cascade when their last physical
edge retires; folded siblings retain their permanent pool owners. The
[nested-cache review](../../coverage/semantics/array-traversable-nested-cache-review.json)
adds two normal COW/DAG originals and two supplied-throw originals. Iterator quiet
discard removes its pending roots together; Generator retirement preserves the
builder through real finally and VALUE/storage release before cancellation.

`430-array-aggregate-unpack.watsup` adds ordinary CVs of named IteratorAggregate
classes with a public non-generator `getIterator(): Traversable`. Genuine source owners
keep the receiver alive through the borrowed callback. The Aggregate has no
owning heap children or destructor; the pending task owns only the builder.
The owned return temporary transfers into the existing user Iterator or named
Generator DATA owner. Source-CV unset is permitted while another genuine owner
keeps the getter live, and the Aggregate may retire before the child body runs.

Returning the same Aggregate raises the native Exception only if the original
CV still contains that same ordinary object. Changed carriers at that rejection
point and recursive other-Aggregate returns explicitly refuse. A returned CLOSED
Generator acquires no DATA: its owning return temporary retires under the pending Exception while
the builder survives, including real cache destruction. Getter throws likewise
preserve callback writes and the original Throwable before builder cancellation.
Generator-method producers, owning Aggregate operands and wider receiver/payload
lifetimes remain partial. The [Aggregate spread review](../../coverage/semantics/array-aggregate-unpack-review.json)
retains the separate native/source/state evidence and counterexamples.

The pinned engine routes are `zend_try_ct_eval_array` and `zend_compile_array`
in `vendor/php-src/Zend/zend_compile.c`, `ZEND_ADD_ARRAY_UNPACK` in
`Zend/zend_vm_def.h`, and the existing reference-copy paths in `Zend/zend_hash.c`.
`Zend/zend_generators.c` supplies Generator acquisition, resume, force-close and
cache storage destruction.
The user Iterator cache and callback routes are in `Zend/zend_interfaces.c`.
Its `zend_user_it_get_new_iterator` calls the getter, acquires the returned
object's iterator, then destroys that return temporary before the first rewind.
The high-level rule models their observable ordering and ownership without
requiring the engine's packed-table representation.

`tests/semantics/array_unpack.py` retains 154 exact authored source inputs,
including the 112 runtime originals and 42 compiler originals. Its 31 checked
source state controls cover alias transfer, nested values, cycles, literal reuse,
root cleanup and dense loop resumption; only budget-exhausted states are resumed.
These checks do not close the array or spread families. The bounded Iterator
protocol adds four exact source agreements, with
[independent reached-state review](../../coverage/semantics/array-iterator-unpack-review.json).
Its earlier Generator refusal retains historical zero credit; the changed control
now exercises the Generator protocol above.
Argument unpacking is a separate call-semantics obligation. Reports at the later
combined container checkpoint establish the then-current broad source closure.

Accepted code `4ca826d2` and author evidence `7ac2519f` pass 155 exact source
comparisons and 24 outcome negatives, 31 state programs/2,454 assertions, and
42 native compiler lints plus 10 descriptor controls. The extra source is the
retired Unsupported control `<?php $a=[...[]];`; it is now an ordinary source pass.
[Independent review](../../coverage/semantics/array-unpack-review.json) audits every
ordered source row and retains eight additional native/state programs with
1,368 assertions. The earlier full ordinary campaign remains historical.
