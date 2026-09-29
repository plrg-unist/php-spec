# Ordinary `Closure::call`

The bounded `182` increment admits literal `$closure->call(newThis, ...args)`
for ordinary real closures. A user-class object supplies the temporary `$this`,
visibility scope, and called class for this invocation. The original closure,
including a closure made by `bindTo`, keeps its saved binding and shares its
static-local cells with the call. `call` does not allocate a bound copy.

The selected closure remains rooted while `newThis` and forwarded argument
expressions run. The task also roots the evaluated receiver and sent values.
Simple-variable closure and `newThis` selectors are checked at their immediate
selection boundary; later argument effects may rebind those variables without
changing the selected objects. Forwarded positional and named arguments use the
closure's parameter list after omitting `newThis`. An invalid named argument is
reported after its expression runs and before the closure body starts. A thrown
body frame records the temporary receiver and an internal `Closure->call` wrapper;
a pre-entry argument error records the wrapper with the evaluated arguments.

Calling a static closure with an object emits the native warning after argument
evaluation and returns `null`. A nonstatic closure called with `stdClass` also
emits the native internal-scope warning after arguments and returns `null`.
Calling without `newThis` raises the native `ArgumentCountError`. These paths
and the user-class cases have exact PHP 8.5.10 CLI source controls; paused
checks cover selected-object roots, immediate selector authenticity, the
`stdClass` pending task, and global call/closure/heap invariants.

This increment leaves named `newThis`, reference and unpacked arguments,
non-`stdClass` internal or Throwable receiver representations, computed `call`
method names, and `call` on captured method/getter/invoke wrappers for follow-up.
Those forms are not counted as native agreement here. Generic array callables,
source `__invoke`, and captured callable rebinding also remain required core
work. The [review ledger](../../coverage/semantics/closure-call-review.json)
separates the frozen source gate from later current-base and installed checks.
