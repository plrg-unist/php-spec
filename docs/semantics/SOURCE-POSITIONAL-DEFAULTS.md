# Positional untyped defaults

The original compiler90/runtime91 increment admits untyped positional default parameters, including omitted by-reference parameters. Typed, variadic, named/unpacked and constructor reception have separate increment contracts; wider defaults and reference returns remain required. The missing PHP_VERSION builtin constant value stays an explicit source boundary; PHP_INT_SIZE is covered by the independent default catalogue.

Compiler17 normalizes signatures through its suspension interface and compiler90 uses the existing45 constant-expression pipeline in the declaration's namespace, imports and magic context. Every source default is compiled, including defaults removed by required-after-optional normalization. Function CODE owns actual parameter subtrees as well as the body. A surviving DEFAULTS entry records its zero-based index, original Param field6 origin and STORED or DEFERRED kind. Stored values borrow the existing unit pool. Parameter CODEEXPR entries retain emitted receive lines, including required parameters and discarded defaults.

Class-constant references remain deferred under Zend's parameter-default
substitution flags, including known own, foreign and imported constants.
[Callable reception248](CALLABLE-RECEIVES.md) checks their completed values in
the receiving frame without using the constant declaration as callable permission.

After supplied operands bind and the callee activates, DEFAULT_RECEIVE fills omitted slots in order. Supplied operands skip default evaluation. Fully supplied calls keep their existing task schedule. Missing required parameters report the first missing parameter's opcode line and the normalized required count. A deferred receive evaluates through the existing expression machine under the actual parameter context, then DEFAULT_BIND writes the result. The context reuses the constant observer's source paths and recorded branch results; it never evaluates an expression again to infer allocation provenance.

An omitted by-reference parameter starts in a fresh ordinary cell. Body alias acquisition promotes that cell. Each invocation owns its parameter values independently, so escaped aliases and array COW preserve repeated-call and recursive freshness. No reference wrapper is introduced solely from the signature flag.

DEFAULTCACHE is an owning state table keyed by a surviving deferred default origin. Pinned RECV_INIT caches a successfully evaluated non-refcounted result when AST evaluation recorded no side effects. The existing value-class tree distinguishes scalar, interned/static string, shared empty array and allocated string/array results, including equal bytes with different allocation histories. The admitted initializer language excludes NEW, the pinned AST evaluator's side-effect marker; later constructor admission must extend this condition atomically. Evaluation failures create no entry. Successful entries survive subsequent default or body failures; the pinned engine installs an evaluated cache before later type verification.

Cache values contribute heap roots. Class metadata contributes none. Abrupt unwinding clears the temporary parameter context and ordinary frame cleanup releases local owners; existing cache and pool owners survive. Public resumption checks cache origin, active declaration, uniqueness, cacheable class/value topology and allocated roots. Arbitrary consistent cache values remain valid. Pool/code guards also accept compiled default roots whose receive descriptors were normalized away, while receive/cache guards require surviving descriptors.

A separate generic91 repair authenticates deferred ordinary Closure and arrow
default caches through the surviving `CLOSURETEMPLATES` entry, without requiring
a live closure object or call context. It checks the exact source node, surviving
default index/expression and absent compiled pool; stored literal defaults cannot
be relabeled as deferred caches. Existing uniqueness, value-class and heap checks
remain in force. Seven source comparisons and five paused stages (107 assertions)
passed privately, including authentic caches after object retirement and forged
descriptor rejection. A current typed-static bridge passes one source and three
paused stages (69 assertions). Installed checks pass one source and the selected
stage after object retirement (27 assertions) at the actual runtime.
[The review](../../coverage/semantics/closure-default-cache-review.json)
preserves all three snapshots. Scoped class defaults remain open.
Prior class-constant and `self::class` probes stopped at explicit Unsupported
before establishing cache reuse behavior.

Receive tasks require the actual current callee, omitted index, previously initialized parameter slots and the exact source-derived queue shape. Bind tasks require their parameter context and final queue position. Observer readiness clauses are disjoint between stages requiring the current result and stages relying only on recorded facts. Retained actual-source counterexamples cover trailing tasks and ternary/coalesce readiness before their finite repairs.

The maintained source catalogue, cache/task protocol, readiness protocol and suspended-state driver complement independent original-context cache, alias, line and no-default compatibility replays. Final evidence identities and acceptance are recorded separately; this document does not claim completion of all call or constant families.

Parameter callable defaults286 extend surviving deferred `NParam` initializers
with static/no-use REAL Closures and fixed named-function/static-method FCCs.
At the286 cut, direct-array and compiled-redirect flow branches were implemented
without discriminating source/state witnesses. Omitted receives allocate fresh
Closure objects; callable values never enter `DEFAULTCACHE`. REAL lexical and
called scope both use the receiving function's current lexical scope, including
rebound makers. Physical FCC ASTs retain their first successful target through
later failure or trait import; each receive selects its fresh called class.

Source/default/index/publication receipts authenticate transfer to the receiving
slot. A raw-trait warning saves the actual target before allocation and resumes
through the genuine receive frame. Unscoped Closure makers mint an immutable
nonowning source marker; erasing it cannot turn a retired bound maker into an
unscoped one. Static writes preserve this marker, while clones copy the plain
body and rely on earlier receipt authority. Receipts own neither maker nor receiver.

The pinned routes are `ZEND_RECV_INIT`, `zend_compile_const_expr_closure` and
`zend_ast_evaluate_ex`'s CALL/STATIC_CALL/OP_ARRAY cases. Ordinary code in the
created Closure body uses ordinary NEW ordering: after autoload, a private
constructor rejects before nested argument effects. Parameter AST NEW retains
its separate initializer ordering. Eleven normal originals and two compiler
rejections, mixed 342 earlier plus 162 affected/new state premises, and one
separate body-autoload interaction retain their distinct revisions in the
[deferred-default ledger](../../coverage/semantics/deferred-static-defaults-review.json).
Builtin FCC targets and broader producers remain required. This increment is
private; it does not close defaults, Closures or PHP core.

Parameter aliases295 preserve the actual borrowed global or cached class-constant
Closure identity, shared statics and donor lexical/called permission. Receiving
scope grants no new body permission, and alias proofs add no owners. Direct mixed
arrays distinguish borrowed leaves from fresh direct Closures and preserve nested
COW; genuine compiled ternaries authenticate the selected arm and reject pruned
or transplanted facts. Eight exact normal sources and640 reached checks over14
originals pass at a separate dirty d39d cut (367 AL,273 strict SL).

At the295 cut, global aliases required a callback-free initializer, quiet value
classes and facts, and each read prefix equal to the current constant table.
Literal bool keys and null values were admitted; effectful null keys remained
unsupported. Six warning/retry/object/trailing-Closure/shadow controls rejected
explicitly and earned zero native agreement. The306 increment below adds bounded
single-emitter reads and registrations through callbacks, retries and nested
reentry. Suspended Fibers, wider transformed and object-bearing producers remain
required. The ledger preserves every failed
fixture, native null-key notice and original AL120s private-method timeout; the
unchanged private42 passes strict SL under the same cap. Canonical integration is pending.

Parameter alias causality306 records actual deferred receive births without adding
heap owners. The current/saved receive, exact source call chain and callback
frontier authenticate nested parents. Checked eval requests capture the prefix
and registration cut before provider work; completed declarations retain that
same birth and ingress. Captured LOOKUP/FACTS distinguish reads before and after
a callback and preserve the old deprecated2048 value after a user17 shadow.
The first causal branch admits regular fixed-key arrays in named functions with
one source-derived potential emitter. Ten exact normal originals pass across
v9/v10. All15 genuine state groups/1170 premises pass across v10 prefix134,
v11 five555 and v13 nine481; the existing37 reporting checks pass separately.
At the306 cut five controls rejected unsupported routes and earned zero native
agreement. The312 increment below adds bounded multiple emitters; parked Fibers,
object/null-key/outside-eval and wider producers remain required. The ledger
keeps these cuts distinct from accepted295/286.
Current295 main selects eight quiet originals and two object boundaries;306
replaces four superseded causal Unsupported tails. Historical sources and checks
remain unchanged, including full fourteen-fixture preparation.

Multiple-frontier defaults312 derive each borrowed read's prefix from preceding
source effects and genuine eval/registration cuts. Several declarations in one
callback share a frontier; warm or pre-shadowed potential emitters add no fabricated
cuts. Earlier failed-birth publications form the next retry's initial prefix.
A second-site throw preserves the first FCC's physical cache while leaving the
second cold, and every successful evaluation still creates fresh Closures.
Nested entry can warm both sites before the outer continuation. A pre-shadowed
E_STRICT reads user17 without a notice; shadowing during its notice preserves
the already selected2048. The rules add no heap owners or duplicate history logs.
The contract assumes real suspended-frame/eval histories; counterexamples keep
those histories fixed while changing read prefixes, payloads or publication copies.

Eight current normal originals and eight source-reached state groups/761 premises
pass, including unchanged-value stale/future prefixes and existing-birth owner
transplants. Seven native originals retain the preliminary cut; the minimized
warm source renews its exact native/model tuple. The original full warm source's
two host55 timeouts and valid bind diagnostic earn zero agreement credit.
Compiler277 passes separately. Current306 main delegates only its historical
two-frontier control to312, retaining all fifteen archival preparations and data.
Parked Fiber, object, null-key, outside-eval and broader producer obligations stay
open; this is a private bounded increment.

Accepted on exact909/e25eb2b9: code1fce6586, compiler2b247d81, runtime8151b96d and
[independent reviewc7cb1b44](../../coverage/semantics/default-parameter-review.json).
The [compiler contract](DEFAULT-PARAMETER-COMPILER.md) specifies source projection;
the [successor handoff](DEFAULTS-REVIEWER-HANDOFF.md) retains remaining obligations.

The actual-parent300 join preserves current property, clone, ArrayAccess,
collector and source hooks, appending only accepted286/295/306/312. Strict
initialization and one fresh two-frontier GLOBALS snapshot/storage original pass
on `279839ac4`: exact `ArrayArrayg:g:l2:A:B`, normal completion, exit0 and empty
stderr. Explicit CLI request facts correct only the original omitted-request
Unsupported; that failure keeps zero agreement. This source does not exercise
temporary Stringable first-emission cleanup.
Current107 reached predicates additionally preserve exact prefixes1/2/3, reject
generic-valid future/stale reads before binding and finish the original with
closed receives and empty default cache. Their initial parse/elaboration stops
keep zero runtime credit; only the corrected fixture passes.
The final301 join over canonical `ff1b7a888` retains property warning318 and
passes strict initialization on `3b6a92f2f`; its disjoint field/task updates add
no refreshed execution credit to the accepted source/107 cuts.

The scoped parked-VM source checks authenticate live eval/class/directory state,
clear loader contexts only in the validation view and exclude saved markers.
The genuine Stringable/Fiber chdir source and73 owner/log/marker controls retain
their296 cut; SOURCEPENDING is empty on that lane. The original72 elaboration
stop stays zero. The old v5 cut passes120 live and107 retry predicates. Current
eval31/saved42 and a separate persistent public response gate pass on their296
cut; new231 default controls remain UNRUN and their91 candidate is excluded from
this join. The full retry source still exceeds host55. Its bounded trace passes
throw/catch/new receive/bind before timing out in GC and earns zero agreement.
The separate pruning factor computes the same pure live-node list once before
the unchanged Generator/Fiber guards. Strict301 initialization and123 affected
collector/Generator/Fiber predicates pass on `1060496af1`; the unchanged full
retry still times out at host55. This establishes no speedup or whole-source agreement.
The later305 join preserves collector317 and Generator321 and passes strict
initialization on `ad5acdc4d`; the earlier lifecycle cut is not renewed.
Whole retry composition and wider producers remain open.
