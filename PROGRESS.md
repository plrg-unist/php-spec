# Core PHP semantics progress

Target: PHP 8.5.10 CLI NTS 64-bit. [PLAN.md](PLAN.md) defines complete core;
[the inventory](coverage/semantics/features.json) tracks obligations. Selected
agreement does not establish complete semantics. Large evidence stays outside
Git; [ARTIFACTS.md](docs/ARTIFACTS.md) locates it.

## Current checkpoint

Private220 validates ordinary missing-CV reference sends and rejected ASSIGN
writes. Reference sends create genuine null cells without warnings, after named
slot selection. A rejected write retains the live typed value and replaces a
thrown handler error with a TypeError carrying its previous chain. The small
implementation is reviewed and elaborated; nine source comparisons and three
reached fixtures remain unrun. Five independent native characterizations pass
with zero model/state agreement credit. Existing213 observations stay separate.

Warning-read consumers213 retain original null for six casts, selected copies and
ordinary by-value sends across handler mutation. Selected callees and prior arrays
keep their real owners; named-slot errors precede warnings. Direct ASSIGN writes
null even after a handler throws, before the same exception continues. Its
original rejected constrained-write control is addressed by private220 above.
Mixed author21 normal tuples/control0 and
58/60/65/53=236, plus independent10/197, retain their actual revisions and original
failures. Fresh actual6395 composition at181f separately accepts source1/94 and
independent cached-callee source1/96, covering static-reference sends, the real
outer-array prepass redirect and cached target/handler retention. Source-equivalent
publication preserves subsequent reporting, parameter backing and named-class
changes. [Consumer ledger](coverage/semantics/warning-consumers-review.json).

Weak Stringable string parameters214/216 convert supplied fixed values in receive
order, preserving caller strictness and nominal/callable precedence. Free
by-reference parameters write through their captured formal cell; existing
property constraints reject before the callback. Same-site reentry and throws
retain authentic receive frames and release converter owners. When a callback
attaches property sources, parameter authority permits the resulting backing
string without relaxing later writes or binds. Legal source rebinding, exact
string receives and cell retirement preserve or remove that authority as needed;
throws mint none.
The [parameter ledger](coverage/semantics/weak-string-parameters-review.json)
separates the earlier 214 checks from source6/state299 and independent2 at
73d6 on accepted6395. The current reporting composition preserves those tested
routes and adds no execution credit.

Named constexpr `::class` preserves namespace/alias spelling without requiring
class lookup, declaring self/parent and source-spelled known parents. Deferred
Closure/eval contexts use their authenticated lexical scope; rebound defaults
avoid origin-only cache reuse. Seventeen constant-context and two ordinary-form
source comparisons plus 25/38 focused guards retain separate tested cutoffs.
The maintained catalogue contains 93 agreements; the callable helper retains its
earlier 159 + 44 predicates and adds these 63. [The constants ledger](coverage/semantics/class-constants-current-review.json)
preserves original failures and the refuted native concat prediction. Static
Closure/FCC identity, owner/called scope, clone cells and compile-entry caches
remain covered by their earlier checks. On actual reporting/214 composition, a
Stringable receive callback invokes the rebound B default before original A and
retains cached identity (`B:A:same`). Released216 backing authorization composes
without changing the named-class/default-cache paths. Wider callable initializer contexts,
builtin FCC targets, uncertified object transfers, unretained update selectors and
references into incomplete tables remain Unsupported. Modifier admission,
attributes and broader consumers stay open; the runtime is reused.

Nonstatic private/protected `__invoke` supports bare calls, callable admission,
object capture/clone and bare-object error handlers through the effective runtime
method table. Explicit method calls keep lexical visibility. Compilation checks
parameters/body before the static fatal or nonpublic warning; inheritance access
errors retain preceding warnings. The [publication ledger](coverage/semantics/invoke-publication-current-review.json)
separates the original source/compiler/runtime checks from the current strict USER
truth-warning interaction, failures and unchanged return-classification boundary.

Public method-array and class-method-string error handlers register raw values and
select afresh at dispatch. Entered targets retain genuine emitter scope, arguments
and owners through member mutation, nested replacement, throw and false fallback.
The [method-handler ledger](coverage/semantics/handler-callables-current-review.json)
keeps mixed author/independent checks, current CONFIG PIPE and original failures
at their actual revisions.

The installed families compose as follows; each ledger records its scope and limits.

| Family | Current behavior and evidence |
| --- | --- |
| Class constants183/184/212 | Lazy scalar/array and selected Closure/FCC caches preserve strict types, inheritance priority and compile-entry availability. Named constexpr `::class` and rebound lexical defaults preserve source spelling/scope. Catalogue of 93 and 159 + 44 + 63 callable/class-name guards retain separate cutoffs; broader consumers remain open. [Constants ledger](coverage/semantics/class-constants-current-review.json). |
| Warning-truth decisions209 | Branch/loop/short-circuit/NOT/ternary-condition choices consume the captured null even after handlers define the CV. Saved consumers and thrown-handler cleanup retain authenticated source/line. Later cast/copy/SEND checks are recorded separately below. [Truth ledger](coverage/semantics/warning-truth-review.json). |
| Warning-read consumers213 | Six casts, selected ternary/coalesce copies and ordinary by-value sends preserve captured null, aliases and selected targets through callbacks. Direct ASSIGN retains its null write through throw. Mixed21/control0+236 and independent10/197 remain separate from fresh static-reference/outer-array source1/94 and cached-callee source1/96 at181f. [Consumer ledger](coverage/semantics/warning-consumers-review.json). |
| Borrowed warning reads208 | Strict identity retains the old reference cell across callbacks without adding an owner; saved callers and throw cleanup preserve it. Defined ordinary `$GLOBALS[key]` uses the real table. Getter/setter and method-string interactions keep separate revisions. [Warning-read ledger](coverage/semantics/warning-reads-review.json). |
| Error handlers/reporting206/207/211 | Raw registrations and selected targets retain four arguments and genuine emitting frames through mutation, replacement, nested reentry, throw and false fallback. Reporting get/set/Restore separates full raw bytes, signed32 masks and modified-entry state across suppression and handler writes; twelve normal sources across two revisions and 74 conditions are accepted. Fifteen nondeprecated error constants resolve exactly. Broader handler forms, deprecated constants and lossy-conversion warning ingress remain open. [Reporting](coverage/semantics/reporting-ini-review.json), [method handlers](coverage/semantics/handler-callables-current-review.json), [earlier handlers](coverage/semantics/error-handlers-review.json). |
| Class-method strings210 and FCC119 | Full-byte lookup separates frame-based callable admission, computed static dispatch and fixed compatible-this selection. Captures/clone retain immutable source certificates and defaults/static cells. A named throwing handler preserves the selected static caller and arguments. [String ledger](coverage/semantics/class-method-strings-current-review.json). |
| Method arrays205 | Public source method arrays retain immutable selected receiver/owner/called-class certificates through dynamic calls and capture. Current two-slot INI checkpoint **f9f47f115/61370c98/1353** accepts source1/finite103; broader resolution remains open. [Array ledger](coverage/semantics/array-callables-current-review.json). |
| Include/configuration | Failed CHDIR warnings retain provider certificates and caller frames through handler CWD/raw writes, false fallback and throw. One current throwing source/136 conditions, earlier three sources and compiler25 checks keep separate revisions. Stringable CHDIR PIPE retains post-callback CWD/held operands; unary CONFIG PIPE preserves source strictness through borrowed warnings. [PIPE ledger](coverage/semantics/include-config-pipe-review.json). Raw getters, primitive/null Restore, weak-null handler continuations and two-slot INI ownership retain their separate checkpoints. [Readback](coverage/semantics/include-ini-readback-review.json), [INI](coverage/semantics/include-stringable-ini-option-review.json). |
| Stringable SET/Restore and paths | SET separates raw INI bytes from effective C-string paths. Weak Restore uses exact full-name lookup and preserves callback mutations on misses. Current ARG/Restore checks retain caller arguments and zero-argument callbacks. [Restore](coverage/semantics/include-stringable-restore-review.json), [prefix](coverage/semantics/include-ini-prefix-review.json), [SET](coverage/semantics/include-set-current-review.json). |
| Typed static properties197 | Weak simple Stringable assignment rechecks live aliases and retains paired callback owners. Current Restore/ARG/INI composition preserves full property bytes, caller arguments and normal/throw cleanup. [Property ledger](coverage/semantics/typed-static-string-assignment-review.json). |
| Weak string parameters214/216 | Supplied value/free-reference conversion preserves receive order, caller strictness, nominal/callable precedence and captured formal-cell ownership. Existing constraints reject before callbacks; newly attached sources permit only the parameter-authorized backing value. Later ordinary writes/binds enforce live types, and throw/retirement removes transient owners. Source6/state299 and independent2 keep their tested revision distinct from the earlier cached Closure/invocation checks. [Parameter ledger](coverage/semantics/weak-string-parameters-review.json). |
| Static setters200/201 | Backed final/asymmetric declarations normalize equivalent setters and preserve inheritance/error priority; direct and indirect consumers retain lexical access, live raw-slot checks and typed aliases. [Setter ledger](coverage/semantics/static-setter-access-review.json). |
| StaticCall reference acquisition141/142 | Getters with untyped return signatures retain scoped selection, typed and legal untyped static aliases and returned-cell cleanup. Typed REF flags preserve initialization/error priority even when discarded. Direct reference sends retain the real cell; ignored untyped getters leave raw values unchanged. Ownership/type-source and getter/borrowed-read checks keep their distinct revisions. [Reference ledger](coverage/semantics/static-method-reference-review.json). |
| Argument introspection198/199 | Ordinary current and saved frames retain genuine named/unpacked argument views through invocation and callbacks. [Argument ledger](coverage/semantics/argument-introspection-calls-current-review.json). |
| Object invocation and callable typing | Effective nonstatic `__invoke` lookup includes private/protected methods, retaining declaring owner, called class and receiver across argument effects and clone. Explicit access remains lexical. Callable-before-string parameters preserve dual-role objects; shared ordinary by-value return classification adds no fresh return agreement. [Publication](coverage/semantics/invoke-publication-current-review.json), [earlier invocation](coverage/semantics/source-invoke-current-review.json), [parameter reception](coverage/semantics/callable-string-current-review.json). |
| Selection and capture | Source method selection preserves owner/called class; capture/clone retains selected targets and scoped defaults/static cells without retaining retired origin-only creators. [Capture](coverage/semantics/method-capture-current-review.json), [default caches](coverage/semantics/closure-default-cache-review.json). |
| Compiler publication190–196 | Ordered class/function availability, early diagnostics and authenticated declaration history compose with calls and callbacks. Compile-stop freezes saved callers and retires active file replies; it does not perform ordinary unwind. [Publication ledger](coverage/semantics/compiler-publication-review.json). |

Executables and compiler inputs are reused; source-equivalent publication adds
no rebuild or fresh execution credit. Earlier selector, capture, invocation and
baseline milestones remain in [MILESTONE-HISTORY.md](MILESTONE-HISTORY.md) and the
linked ledgers. [Cleanup](coverage/semantics/error-origin-author.json) and
[migration](coverage/semantics/throwable-migration-review.json) retain deferred
failures and interrupted evidence.

## Remaining core work

- Calls: broader nonpublic/scope-dependent array and class/method-string resolution,
  magic/autoload/internal consumers, dynamic compile-warning handler delivery,
  transformed wrappers and broader CONFIG PIPE consumers. Only the selected captured-static
  array and string Closure PIPE routes are covered; defined ordinary `$GLOBALS[key]` is admitted; missing-global warnings and whole-table snapshots remain partial.
- Include/configuration: deprecated `E_STRICT` constant diagnostics and handled
  lossy reporting conversions, nondefault startup profiles, wider directives,
  other warning producers, OS services and lifecycle. The
  [include contract](docs/semantics/INCLUDE-SOURCES.md) separates these consumers.
- Values, references and coercion: variadic/default callback reception and broader weak
  parameter/property conversion, constrained-reference object conversion, wider nonstatic delayed receivers and
  broader reference-result consumers. Deferred property defaults and references into incomplete constant tables remain Unsupported.
  Deprecated constant producer ingress remains open. Generic156 return replay, temporary-return
  Notice timing and typed
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
  Broader constant consumers and compiler reporting interactions remain open.
  get_called_class() remains an unimplemented introspection body; static::class
  observations do not close it.

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
