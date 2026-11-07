# Source class constants

The 183/184 increment extends the existing user-constant compiler and
expression machine for PHP8.5.10 CLI. Scalar/array constants and selected static
Closure/fixed first-class callable initializers execute; the family remains partial.

Class descriptors retain each constant's declaring owner, visibility, type,
initializer origin and folding status; folded values remain in initializer unit pools. Earlier available scalar constants can fold;
forward/deferred expressions remain lazy. Typed constants use strict acceptance,
including integer-to-float promotion. Existing `::class` strings retain their
separate lexical/called-class behavior.

Runtime fetch checks visibility before initialization, evaluates deferred values
in the declaring owner's scope, and publishes a cache value only after successful
evaluation and type checking. Failed initialization can be retried. Arrays remain
owned cache roots and ordinary reads use copy-on-write. Parent private constants
are excluded from inherited lookup. AST constant expressions and ordinary VM
fetch preserve their different class/member evaluation and diagnostic priorities.

A single resolved noarg `#[Deprecated]` is admitted on constants of a physical
named class, and public constants of a named interface. Fixed-name, literal-member fetches emit E_USER_DEPRECATED
(16384) with the declaring class and the fetch file/line, after access checks and
before value acquisition. Warm reads still warn. Protection follows the selected
declaration across inherited aliases; a recursive read may initialize its value
without a second notice. The outer continuation then reads the current slot.
A handler throw discards that continuation and protection, preserving an unfinished
assignment and allowing the next fetch to warn again. Table updates keep their
separate initialization path without a fetch notice.

The same noarg attribute may cover several public constants in one named class
or interface group. Attribute preprocessing happens once, then the ordinary
compiler processes the original ordered list. Each member retains its own source
index, initializer, declaring guard and pool/cache identity. Guarding one sibling
does not guard another. Existing type/link checks and compiler substitution vetoes
remain in place; no descriptor or notice task changes.
[Grouped constants](../../coverage/semantics/deprecated-multi-constant-group-review.json).

Literal `self`, `parent` and `static` reads in ordinary public named-class method
bodies use their actual current normal target, function and lexical/called scopes.
The fetch must lie inside the compiled method body, excluding default/attribute/
initializer sites. Existing selection chooses the requested class and canonical
declaration; the same value-free notice task restores that method context.
Static calls distinguish Base lexical scope from Child called scope and overrides.
A constructed receiver may have initialized the inherited cache already; a warm
parent read still warns and keeps its normal This owner through callback alias
removal, then permits receiver cleanup before the caller continues. Cache history
adds no receiver root or access to retired This. Contextual `constant()` queries
and wider call targets retain their separate bounds.
[Keyword notices](../../coverage/semantics/deprecated-keyword-class-constant-review.json).

Protected/private named-class constants use their actual source visibility.
Outside and unauthorized inherited reads raise Error before a notice or value,
even when the slot is cached or the same declaration is already notice-protected.
Normal and keyword pending-notice validation rechecks the restored caller's
access; metadata recognition remains independent of that access for existing
owning-source, update and history consumers. Source-flag mismatches reject both
public/nonpublic forgeries without narrowing source-wide compiler/query vetoes.
Public API selection and interface visibility retain their prior bounds.
[Nonpublic notices](../../coverage/semantics/deprecated-nonpublic-class-constant-review.json).

Quiet literal string/null `message` and `since` arguments reuse the existing
positional/named parser, including reordered named fields. Recognition reads the
declaring namespace, imports, class/member and source line rather than the reader
or handler. Nonempty `since` precedes a nonempty message; null/empty fields add no
suffix. Literal and public API notices use the same stateful text hook, while
existing source visibility and access checks remain in force. The compiler marks
these exact attribute argument locations as deferred metadata: their pool classes
validate without ordinary operand emission or initializer authority. No descriptor,
notice task, value owner or constructor-object protocol is added. Two scalar
originals and 240 strict481 conditions validate this slice; existing initializer
and consumer bounds remain separate from that evidence.
[Message metadata](../../coverage/semantics/deprecated-class-constant-message-review.json).

An initialized static-name, non-This/non-autoglobal CV may select the class of a
literal public constant. Existing normalization accepts a string or live ordinary
USER object and captures the published named class/interface before notice.
Entry authenticates that normalized RESULT. Once a notice occupies the current
task head, its exact declaration/requested-class/member/line tuple takes priority
over RESULT. Restored frames validate their own task head; an outer saved notice
does not block a fresh nested selection. Validation never rereads the CV or object.
The task adds no owner of an input object: the observed last-alias clear destroys
it before the folded constant result is acquired. Two originals and 208 strict482
conditions cover rebinding, real retirement, tuple priority and folded-array COW.
These fronts do not claim a deferred binder/cache fill or whole-state equivalence;
existing initializer and consumer bounds remain unchanged.
[CV selectors](../../coverage/semantics/deprecated-cv-class-constant-review.json).

With a literal nonkeyword class/interface name, a quiet initialized non-This/
non-autoglobal CV may supply the public constant member. Existing literal-class
selection stays source-authenticated; resolved member string bytes authenticate
the current fetch. The unchanged current-head decoder then requires the exact
saved tuple, with priority over a different RESULT. A fresh local member read at
a different handler line remains valid while an outer same-declaration notice is
protected; no repeated notice occurs. Handler rebinding/unset cannot redirect the
outer member, while a later evaluation sees the new value. Two originals and 225
strict483 conditions also check request-string metadata and folded-array COW.
Native observations establish captured bytes and values, not carrier pointer
identity. No task/root/history or initializer rule changes; class-CV+member-CV,
keyword/API/effectful members and owning-NUL modes retain their separate bounds.
[CV members](../../coverage/semantics/deprecated-cv-member-constant-review.json).

When both operands are quiet initialized CVs, the real adjacent member/capture
pair retains the normalized class while RESULT retains the resolved member.
The new forwarding arm validates that pair, source, line and exact tail before
consuming it; its default preserves the old path. Common notice dispatch keeps the original protected and
unprotected branches; only real dispatch creates a saved notice, so the first
warning is not suppressed by synthetic protection. Resumed validation requires
the exact saved tuple and has no RESULT fallback or mutable input read. Two
originals and 224 strict484 conditions cover both string-CV rebindings and actual
object retirement/member unset before the folded result. Class cache remains
empty/history unchanged in these fronts; existing initializer bounds are not
renewed. No task/root/history field is added.
[Dual CV snapshots](../../coverage/semantics/deprecated-dual-cv-constant-review.json).

Ordinary public named method bodies also admit quiet CV members with `self`,
`parent` and `static`. The existing method/body proof authenticates lexical,
parent and called-class selection; current member bytes then exact saved-tuple
priority preserve the selected member. No forwarding or shared transport changes.
Two originals and 288 strict485 conditions distinguish Base/Child overrides,
actual member rebinding/null and normal This ownership through notice to return.
Both fronts remain folded, with empty class cache and unchanged history.
[Keyword CV members](../../coverage/semantics/deprecated-keyword-cv-member-constant-review.json).

For fixed nonkeyword named requests, a nonvariable member expression may instead
carry immutable compiler authority: its exact FIELD1 child has true code and a
non-NUL PSTRING pool value while the whole Deprecated fetch has false code.
Source/DECL/access proof determines the member independently of RESULT; no new
snapshot is needed. Two originals and 234 strict486 conditions cover braced strings,
concat, genuine protected reentry, repeated notices and array result/COW. The
values remain folded/cache-empty; general runtime expressions remain separate.
[Pooled members](../../coverage/semantics/deprecated-pooled-member-constant-review.json).

An immutable compiled class expression uses exact FIELD0 true-code/string
identity and the existing literal-selection proof. Requested bytes retain raw
case after existing one-leading-slash removal; canonical class NAME is not a
substitute. Identifier members keep their literal proof, while non-CV expression
members need their exact FIELD1 string. Two originals and 246 strict487 conditions
cover class/member concat, protected reentry, normalization and interface result/COW.
Both fronts remain folded/cache-empty/history-unchanged, with no new snapshot.
[Compiled classes](../../coverage/semantics/deprecated-compiled-class-constant-review.json).

The value-free pending task retains only declaration, requested class, member and
line; it adds no root or initializer context. Same-unit folding, folded-pool imports
and warm-cache imports refuse substitution for these declarations. The first
ordinary formal-default evaluation fetches and warns; its later parameter-cache hit
does not fetch again. `defined()` keeps its existing separate path. Other attribute
argument forms, declaration kinds and wider dynamic/keyword contexts remain
separate. [Notice review](../../coverage/semantics/deprecated-class-constant-fetch-review.json).

Interface source groups use their physical field3 path. Inherited interface and
implementer fetches share the declaring interface's attribute, notice guard and
value slot; only interface requests need the additional source-validity arm.
Implementing-class requests retain the existing class proof. Deferred scalar
reentry, warm throw, diagnostics and checked eval/formal-default compilation are
validated separately from the original class slice. Owning-global recipient source
authority has its own gate; the attr-free source arms remain unchanged.
[Interface notices](../../coverage/semantics/deprecated-interface-constant-fetch-review.json).

`constant()` receives attributed public scalar constants through a literal or
initialized plain-CV string query. The pending task retains the captured config
and selected declaration. Its notice phase protects that declaration across API
and literal reads; its acquisition phase is unprotected and never stores a
selected value. Successful handler return then uses a folded scalar, current
cache or the existing lazy `CLASS_CONST_CALL` binder. The actual adjacent API
acquisition continuation authenticates that binder; an autoload resume alone
does not grant permission. Handler throw cancels acquisition and leaves an
unfinished assignment unchanged.

The task delegates existing config roots and nonce. Request-string carriers are
immutable metadata with zero heap nodes. The checks establish captured-query
stability across CV rebinding. Existing class/interface lookup,
source facts, cache history and trace rules stay in place. Wider owning results,
keyword/autoload/conversion contexts and wider query expressions remain separate.
A held keyword query now honors the same value fence. `defined()` and ordinary
unattributed query routes retain their prior behavior.
[API review](../../coverage/semantics/deprecated-class-constant-api-review.json).

The same API phases now admit folded literal-array initializers using the existing
array-tree validator. Eligibility reads pool class metadata; acquisition reads the
actual tree after the notice. The notice task adds no array owner. Handler-local
COW copies can retire before the outer API returns the original pool value and
adds one result edge. Later result mutations preserve the permanent pool tree.
Empty and nested literals, named-class/interface aliases and warm notice throws
retain these distinctions. No nonfolded owning initializer, image, task or root
law is added. [Array API review](../../coverage/semantics/deprecated-class-constant-array-api-review.json).

Authenticated nonfolded declarations with this exact attribute also receive
existing owning globals. Their declaration and initializer-child origins reuse
the ordinary binder and source facts. The class notice finishes and its protection
clears before the initializer emits a global notice. Normal outer replacement
releases a computed child value before publishing its own value; a global-notice
throw leaves assignment/cache uncommitted and allows retry. Global Closure aliases
retain identity and scope, and typed outer failure preserves a child cache fill.
The source gate also serves existing authenticated update consumers without a new
construction protocol. Wider owning API initializers and abrupt old-value release
remain separate. [Owning source review](../../coverage/semantics/deprecated-owned-class-constant-notice-review.json).

The API also acquires existing owning values from an untyped, fully resolved
direct global-name initializer. At acquisition it authenticates the actual USER
donor's value/class. Cold reads retain the real CLASS_CONST_CALL and API task;
warm reads require exact donor/cache identity and the existing publication/type/
history proof. No value is copied into the notice continuation. A nested literal
read during the global warning can fill the same slot; the API's visited state
and the declaration notice guard keep their existing separate roles. Result/cache
owners, caller array COW and global Closure identity/scope are preserved without
a new task or root rule. Computed initializers and wider query forms remain separate.
[Owning API review](../../coverage/semantics/deprecated-owned-class-constant-api-review.json).

Initializer continuations preserve nested global/default contexts, selected class
and member operands, source origins and recursion protection. Simple unresolved
names report the fetch file/line; compound evaluation uses its expression location
and an extra constant-expression frame only when the executor location differs.
Post-evaluation type errors restore the fetch context. Finite controls reject
swapped, duplicated or skipped update tasks and coherently forged selected slots.

[Diagnostic ingress217](../../coverage/semantics/reporting-diagnostics-review.json)
saves and restores initializer facts through error-handler and nested ordinary
calls. The active lexical evaluator is separate from the global busy stack;
callbacks retain recursion protection without inheriting initializer scope.
Selected deprecated-constant values survive callback declarations, and failed
initializations can retry. Compound diagnostics and thrown constructors keep
expression/fetch locations and synthetic constant-expression traces distinct.
Compound callback/eval filename creation remains open.

Inheritance checks preserve finality, different-owner ambiguity, visibility and
type covariance in that order. Same-owner interface diamonds remain unambiguous;
private parent constants do not constrain a child's replacement. Real linking
checks constants before methods, while the early availability probe keeps its
separate method/property/constant order and defers only unresolved types.

Append-only link, cache-fill and table-completion origins preserve temporal AST
status. Individual fetches never mark a class fully updated. NEW enters the
parent-first updater only when the requested class still needs it; successful
earlier fills survive a later failure, and retry retains the unfinished work.
Source-derived inverse controls reject incorrect task order, missing completion
markers, unrelated update sites and a class used before its publication.

The earlier bounded evidence comprises25 original source/native comparisons
across successive revisions and finite16+13. The later linking slice accepts
twelve further tuples (6 normal,5 static rejections,1 PHP error) and five finite
programs with27+13+19+18+16 overlapping predicates. These are distinct cutoffs,
not a single-revision37 rerun or whole-family acceptance.
The [ledger](../../coverage/semantics/class-constants-current-review.json) retains
original failures, including the refuted native update hypothesis. Maintained
source and finite commands are in `Makefile`; raw files stay outside Git.

Included/evaluated units import only earlier published scalar/constant-array
values that were folded or successfully cached before that unit entered. Uncached
initializers stay lazy even when their referenced global is now defined. Imported
arrays are copied into the new pool, and later fills cannot retroactively change
a compiled image. Five further native comparisons (3 normal/2 static) and one
finite fixture/31 predicates validate this boundary. The original negative
transport expectation is retained as a fixture failure.

Current-runtime checks add six native agreements for static access priority,
runtime array FCC owner/called-class scope, handler fetch, completed reference
aliasing and static unset. Their two source cutoffs remain separate. A later
borrowed strict-identity callback fills a deferred array cache and reads it after
handler retirement (`7ne7`). On the current StaticCall-reference composition,
NewC completes its table before a getter exports the property cell; alias mutation
changes the property while the cached constant stays unchanged (`32`). The
earlier catalogue contains 50 agreements across these preserved revisions.

Static anonymous Closure initializers require no explicit use-list and create
with the declaring owner as both lexical and called scope, without a receiver.
Fixed function callables preserve the first successful namespace/fallback target
even when a later initializer error discards the object. Static-method callables
retain the method owner and selected called class separately, including private
access from the initializer owner. Literal string class selectors use global
spelling, while named selectors keep their namespace/scope rules. Invalid
nonstatic/use/dynamic forms and literal nonstring names retain PHP compile errors.

Object caches retain genuine constructor identity and recursive array/alias
certificates; objects never become cross-unit folded pool values. Nonowning
creation records preserve retired selection history. The cache owns the object
and its scope and static cells. Clones copy the current body/scope/static state
without acquiring the original constructor marker. Four finite fixtures reject
coherent scalar erasure, wrong array sites, substituted clones with invented
records, invalid selection prefixes/scopes and missing roots (159 predicates).
A later literal-class fixture adds 44 predicates. Twenty-two new full native
comparisons bring the maintained catalogue to 72 (32 normal, 22 PHP errors, 18 static
rejections). Source and finite cutoffs remain separate; promotion adds no rerun.
A later current-source comparison registers a cached constant Closure as a handler.
Its GLOBALS write leaves the folded false-left expression's original null intact,
and repeated identity/direct invocation retains the static counter (`1null:same:2`).
This brings the maintained catalogue to 73; the earlier 72 sources stay unchanged.

Named constexpr `::class` folds namespace/import spelling without class lookup.
Known self uses the declaring owner; known parent retains its source spelling.
Closure and eval contexts resolve deferred self/parent from authenticated lexical
scope, including rebound defaults. Contextual defaults bypass origin-only caches;
ordinary defaults retain their existing cache ownership. Literal class strings
and parser-folded literal concatenation follow Zend's separate class-name route.
Live static/computed forms and nonstring literals retain their PHP errors, while
folded dead branches disappear before admission.

Seventeen constant-context and two ordinary keyword-form comparisons add nineteen
agreements (11 normal, one PHP error, seven static rejections), bringing the
catalogue to 92. Two focused fixtures add 25/38 predicates for coherent folded
spelling substitution and a forged contextual default cache/rebound scope.
Original Unsupported and elaboration failures stay preserved; the earlier
binding-premise draft remains unrun.
The original concat rejection hypothesis remains refuted by normal `GhostName`.
These source and finite cutoffs are separate. One later current reporting/214
comparison invokes a rebound B default before original A inside a Stringable
receive callback, retaining cached identity (`B:A:same`), bringing the catalogue
to 93. Maintenance adds no execution credit.

Accessible references into an incomplete class table are explicitly Unsupported;
the separate rejected control is not a native agreement. Unretained
computed/scoped table-update selectors remain
Unsupported. Constructor contexts outside class constants, builtin FCC targets
and object transfers without an authenticated source/cache relation also remain
Unsupported. Constant modifier
admission, wider attributes, traits/enums/internal constants and broader default/property
consumers stay open. These checks reused the recorded runtime; they add no fresh
copied rebuild, reporting-mask, paused return or full-core closure.
