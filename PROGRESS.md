# Core PHP semantics progress

Target: PHP 8.5.10 CLI NTS 64-bit. [PLAN.md](PLAN.md) defines complete core;
[the inventory](coverage/semantics/features.json) tracks obligations. Selected
agreement does not establish complete semantics. Large evidence stays outside
Git; [ARTIFACTS.md](docs/ARTIFACTS.md) locates it.

## Current checkpoint

Unary Stringable CONFIG PIPE authenticates the held left child and compiled
send/call lines; ordinary RHS factories supply their returned callable. Ordinary
Closure PIPE follows caller strictness and retains the object after its source
cell is overwritten. The [PIPE ledger](coverage/semantics/include-config-pipe-review.json)
separates twelve earlier normal sources/165 state assertions from two fresh
borrowed-warning composition sources at **10c320623**. Normal handler return and
throw preserve callback/caller frames, raw INI mutation and CONFIG cleanup.

Borrowed strict-identity reads208 retain the old reference cell across warning
callbacks without adding an owner; nested saved callers and throw cleanup are
checked. Defined ordinary `$GLOBALS[key]` uses the real global table. Private
**f15d1f056** passes six normal tuples plus a zero-agreement control and author3/162;
independent three model comparisons reuse native originals and two/130 pass.
Fresh getter/setter **f9592b6ca** accepts author source1/74 and independent source1/111;
current method-string **c67e3511f** accepts source1/77. Their [ledger](coverage/semantics/warning-reads-review.json)
keeps profiles/revisions separate; publication adds no execution or rebuild credit.

Public concrete class-method strings distinguish callable reception from fixed
and computed dispatch/capture. Selected methods retain owner/called class and
receiver ownership through mutation, clone and retirement. Compiler119 clears
the callee result fold so literal-array captures produce Closure objects.
The [string ledger](coverage/semantics/class-method-strings-current-review.json)
keeps the private gates, preserved compiler failure/affected repair, and current
throwing-handler source/state observations at their separate tested revisions.

The installed families compose as follows; each linked ledger states its limits
and distinguishes historical evidence from current interaction checks.

| Family | Current behavior and evidence |
| --- | --- |
| Error handlers/reporting206/207 | Ordinary named, closure and public source-object callbacks retain four arguments and genuine saved frames; masks, replacements, restoration, throw and fatal fallback compose with current properties/calls. Broader producers/API/callable forms and reporting readback remain open. [Handler ledger](coverage/semantics/error-handlers-review.json). |
| Class-method strings210 and FCC119 | Full-byte lookup separates frame-based callable admission, computed static dispatch and fixed compatible-this selection. Captures/clone retain immutable source certificates and defaults/static cells. A named throwing handler preserves the selected static caller and arguments. [String ledger](coverage/semantics/class-method-strings-current-review.json). |
| Method arrays205 | Public source method arrays retain immutable selected receiver/owner/called-class certificates through dynamic calls and capture. Current two-slot INI checkpoint **f9f47f115/61370c98/1353** accepts source1/finite103; broader resolution remains open. [Array ledger](coverage/semantics/array-callables-current-review.json). |
| Include/configuration | Unary CONFIG PIPE preserves held operands, source strictness and callback guards through normal/throwing borrowed warnings. [PIPE ledger](coverage/semantics/include-config-pipe-review.json). Raw getters, primitive/null Restore, weak-null handler continuations and two-slot INI ownership retain their separate checkpoints. [Readback](coverage/semantics/include-ini-readback-review.json), [INI](coverage/semantics/include-stringable-ini-option-review.json). |
| Stringable SET/Restore and paths | SET separates raw INI bytes from effective C-string paths. Weak Restore uses exact full-name lookup and preserves callback mutations on misses. Current ARG/Restore checks retain caller arguments and zero-argument callbacks. [Restore](coverage/semantics/include-stringable-restore-review.json), [prefix](coverage/semantics/include-ini-prefix-review.json), [SET](coverage/semantics/include-set-current-review.json). |
| Typed static properties197 | Weak simple Stringable assignment rechecks live aliases and retains paired callback owners. Current Restore/ARG/INI composition preserves full property bytes, caller arguments and normal/throw cleanup. [Property ledger](coverage/semantics/typed-static-string-assignment-review.json). |
| Static setters200/201 | Backed final/asymmetric declarations normalize equivalent setters and preserve inheritance/error priority; direct and indirect consumers retain lexical access, live raw-slot checks and typed aliases. [Setter ledger](coverage/semantics/static-setter-access-review.json). |
| Argument introspection198/199 | Ordinary current and saved frames retain genuine named/unpacked argument views through invocation and callbacks. [Argument ledger](coverage/semantics/argument-introspection-calls-current-review.json). |
| Public invocation and callable typing | Public source `__invoke` is installed at **18a1383d7**; callable-before-string parameter admission at **b8a6f43f8** preserves dual-role objects across weak/strict, union order, inheritance and ownership. [Invocation](coverage/semantics/source-invoke-current-review.json), [parameter reception](coverage/semantics/callable-string-current-review.json). |
| Selection and capture | Source method selection preserves owner/called class; capture/clone retains selected targets and scoped defaults/static cells without retaining retired origin-only creators. [Capture](coverage/semantics/method-capture-current-review.json), [default caches](coverage/semantics/closure-default-cache-review.json). |
| Compiler publication190–196 | Ordered class/function availability, early diagnostics and authenticated declaration history compose with calls and callbacks. Compile-stop freezes saved callers and retires active file replies; it does not perform ordinary unwind. [Publication ledger](coverage/semantics/compiler-publication-review.json). |

Executables and compiler inputs are reused; source-equivalent publication adds
no rebuild or fresh execution credit. Earlier selector, capture, invocation and
baseline milestones remain in [MILESTONE-HISTORY.md](MILESTONE-HISTORY.md) and the
linked ledgers. [Cleanup](coverage/semantics/error-origin-author.json) and
[migration](coverage/semantics/throwable-migration-review.json) retain deferred
failures and interrupted evidence.

## Remaining core work

- Calls: broader class/method-string consumers, nonpublic/static `__invoke` publication,
  compound/scope-dependent array resolution, magic/autoload/internal consumers,
  transformed wrappers and broader CONFIG PIPE consumers. Only the selected captured-static
  array and string Closure PIPE routes are covered; defined ordinary `$GLOBALS[key]` is admitted; missing-global warnings and whole-table snapshots remain partial.
- Include/configuration: CHDIR provider PIPE, broader warning producers, wider directives
  and reporting readback, OS services and lifecycle. The
  [include contract](docs/semantics/INCLUDE-SOURCES.md) separates these consumers.
- Values, references and coercion: broader weak parameter/property conversion,
  constrained-reference object conversion, wider nonstatic delayed receivers and
  static-method reference acquisition. Named error constants such as E_USER_NOTICE
  remain unsupported by initial lookup; the handled-notice check uses literal1024. Generic156 return replay, temporary-return Notice timing and typed
  by-reference string conversion186 remain open; accepted ordinary by-value
  classification does not close them. [String contract](docs/semantics/USER-STRING.md),
  [finally contract](docs/semantics/SOURCE-FINALLY.md).
- Objects and lifetime: remaining static members, traits, hooks, readonly/instance asymmetric
  access, traversal, output handlers and lifecycle callbacks. Static cells remain
  partial across trait/inheritance sharing, bind/clone, include/eval reactivation
  and GC. [Method](docs/semantics/SOURCE-METHODS.md),
  [static-property](docs/semantics/SOURCE-CLASS-STATICS.md) contracts.
- Control and diagnostics: Generator/Fiber, remaining warning/read producers,
  exception/lifecycle handlers and broader API/callable argument consumers.
  Constants183/184 and compiler reporting/handler interactions remain open.

`returns_verify` is temporarily paused by the user. Preserve its branches and
evidence; do not retry the blocked engine experiment, substitute a reviewer,
merge changes awaiting its validation, or begin work depending on those
unaccepted changes. Independent work proceeds from the accepted baseline.

Rocq interaction-tree semantics and BOLA proofs follow completed PHP core.

## Validated baseline

The post-arrow checkpoint is **1026/0ec57507**, with arrow capture and returns
117/118 at **87cdc532f**. Its [review](coverage/semantics/post-arrow-integration-review.json)
binds these distinct profiles and independent audits:

| Gate | Accepted observations |
| --- | --- |
| Compiler | 5,751 source lints, 8 access sources, 15 line observations; existing binary reused |
| Explicit request | 263 source profiles, 526 responses with exact request/environment facts |
| Callable | 946 maintained rows in 18 suites plus one regression; 1,894 responses |
| Ordinary | 5,706 source comparisons (4,060 normal, 1,006 PHP errors, 640 static rejections), 21 separate controls; 11,435 process records |

These are observations, not unique PHP programs or current full-core coverage.
Ordinary, request and callable profiles have different environment contracts;
their counts are not interchangeable.

## Validation and integration limits

The authorized cap is five numerical/model campaigns with coordinated slot
handoffs. Record the tested revision, compiler/runtime identity, relevant inputs,
environment, exact commands/exits and raw originals. Independent review focuses
on semantic counterexamples and reliable completion; investigate failures
narrowly and repeat only affected checks. Metadata adds no execution credit.

Interrupted runs, timeouts, Unsupported and budget controls are never native
agreements. Paused-state fixtures complement original-source comparisons; passing
subsets do not establish equivalence or full core. Final combined current-source
gates and a fresh copied-path, network-isolated offline rebuild remain required.
