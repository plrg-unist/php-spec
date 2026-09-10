# Source error suppression

Compiler100/runtime101 execute `@` on pinned PHP 8.5.10 CLI NTS64. The paired
input is 951/c6501bd8; the [independent report](../../coverage/semantics/error-suppression-review.json)
records acceptance and the exact evidence. Reporting configuration APIs, custom
handlers and the remaining PHP core are still required work.

`REPORTING` is global across calls; each frame owns its `SILENCES` stack of
source origins and saved masks. Entry saves the current mask and preserves only
fatal bits (4437). END and abrupt cleanup restore a saved nonfatal mask only while
the current mask remains fatal-only. Callee normal return preserves caller
silence; propagated errors restore each discarded frame's own scopes. Cleanup
uses the saved stack independently of TODO, which earlier abrupt rules may clear.
Budget suspension preserves the mask, saved scopes, owners and continuation.

An ordinary deferred variable is read before END restores reporting. Owning
values and returned references retain their identity. Thus `f(@$a)` and
`f(@g())` have their original temporary/VAR reference-send distinctions.
`return @$a` and `return @g()` remain VALUE-designated reference returns: their
Notice occurs after END, unless an enclosing caller silence covers it.

Known results remain available to enclosing compiler folding and branch pruning.
The existing retained-effect mechanism executes suppression even when its value
is folded. Nested append controls verify that effects execute once. Static child
diagnostics and compile-time parent warnings still occur before runtime silence.
Runtime Warning, Notice and Deprecated emission respects the mask without
removing earlier events; output and the fixed-profile fatal completions remain.

The engine field is a C int (`zend_globals.h:184`); BEGIN widens that value into
a zend_long saved slot. Current and saved masks therefore fit signed32 on this
build. Guards bind saved scopes and END tasks to actual suppression occurrences,
the owning current/saved function, nesting and pending close order. Suppression
and direct-child expression metadata and retained effects match the checked
compiler projection. Consistent arbitrary masks and owning values remain valid;
these paused-state controls do not establish source support for configuration.

The ordinary native profile fixes `error_reporting=30719`, used by initial state;
primitive request fields remain unchanged. `error_reporting()`, INI mutation,
custom handlers and configurable fatal display are pending. The observer's fatal
display currently covers this profile and `@`'s fatal mask; PHP's general display
filter in `main/main.c:1409` remains a later configuration integration obligation.
The duplicate-constant reporter is tested as a primitive because dynamic
include/define activation under `@` is not yet executable.

Author validation covers 26 fresh source profiles, 37 primitive reporter checks,
23 protocol controls/489 assertions, 17 compiler phases/131 projections,
19 demand projections/38 assertions, 31 reference-return sources, and two dense
states/779 assertions. Independent tests add four deferred-default/cache/error
profiles, four dense states/1312 assertions, and two complete 942 state comparisons
at seven cuts, projecting only new default reporting/empty silence fields.
These sets overlap. The compiler's 58 reference-return phases/49 projections and
focused send/destructuring checks have an exact compiler-input bridge.

Semantic gates used 951/ff8d; only a final demand-report print key changed for
c6501bd8, leaving 950 files and all modes unchanged. Failed fixture preparations,
the earlier private signed64 guard and source/task counterexamples remain retained.
No intentional engine departure is introduced. The next bounded work and all
remaining obligations are tracked in the core checklist and continuation handoff.
