# Typed static string assignment

Module197 consumes weak object-to-string conversion during simple assignment
through a typed static declaration in an ordinary source class. It uses module168's
effective public `__toString`, including inherited methods. Strict typing rejects
before conversion; exact class or `Stringable` admission keeps the object.
Source class/name selection precedes the callback.

After conversion, the consumer rereads `CLASSSTATICS` and checks the string
against the live alias's ordered type sources. A callback can replace that row,
add a source or mutate another row. Rejection preserves those effects and the
current value. Success returns the converted string. Callback exceptions keep
their original diagnostic and compiled property-target line.

Adjacent `STATIC_STRING_RESULT`/`STATIC_STRING_CAPTURE` tasks bind source,
declaration, class, name, receiver and line. CAPTURE owns the original RHS:
a temporary owns its value, a CV borrows its holder, and an admitted returned
reference owns its cell/current payload. The shared receiver and scratch result
have separate roots. Current and saved queues check the pair and caller scope;
discard removes the pair atomically. These guards validate present state and
transitions, rather than reconstructing history from arbitrary injected states.

The [ledger](../../coverage/semantics/typed-static-string-assignment-review.json)
keeps the tested compositions distinct. Earlier b566 CALLS/SET gates pass
public `(new I)(new Q)` between the property callback and named SET, with normal
and throwing frame/ownership fixtures. `I::__invoke` is the context name;
`__invoke` remains the method descriptor name. Exception traces retain Q through
two argument edges in five frames after consumer roots are released; the invoker
and outer receiver retire.

The focused INI union a092 passes two original tuples and755 assertions:
normal266, throw256, inherited/captured file165 and ordinary static68. INI keeps
raw `seed\0old`/`inner\0tail`, rejects leading-NUL updates without mutation,
and SET returns the effective live-old prefix. The property's `s\0typed` result
and output retain all bytes. Throwing preserves the inner raw INI side effect,
old property and original trace. The original normal329 timeout has no state
credit; fixture/preflight failures and the earlier wrong105 file scope remain
recoverable. Source2 and successful522 were carried without replay before the
exact captured165/static68 controls completed. Unused bodies prove elaboration
only.

On current ARG198/199 plus callable-first95, the fresh source f19 returns
`BS|ok`: a callable/Stringable object reaches `store(callable|string)` unchanged,
`func_get_arg(0)` reads its live formal, and the typed property then invokes
`__toString`. Both original processes agree on the full normal tuple, with
native30/model90/application60 limits and empty stderr. Source-equivalent
publication and reused executables add no new gate or offline rebuild credit.

The current Restore union7c5 retains that source identity and adds one fresh
normal tuple `BPR0.:1|s\0typed`. A property callback invokes Stringable Restore;
the option callback observes zero arguments and mutates the raw path. Restore
then resets the initial path, observed through scalar SET, while the saved
`store` caller retains one argument. The property keeps every returned byte.
No getter or broader Restore behavior is claimed by this source.

Instance, compound/coalescing, internal Throwable override, delayed receiver
and broader RHS/reference consumers remain open. CV constrained-reference
conversion has separate mutable-source and holder timing. The default-false186
API is unchanged: ordinary sources cannot mint its witness. Exceptional singleton
clone provenance, readonly/asymmetric access and full core remain separate.

Pinned engine routes are `ZEND_ASSIGN_STATIC_PROP` in `zend_vm_def.h`,
`zend_assign_to_typed_prop` in `zend_execute.c`, and
`zend_std_cast_object_tostring` in `zend_object_handlers.c`.
