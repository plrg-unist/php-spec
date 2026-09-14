# Successor: builtin named compilation and call unpacking

Start from accepted968/ab389: codecb1febe7, compiler5a19646a,
author2a0e0774 and independent1a562e8f. The
[named contract](SOURCE-NAMED-ARGUMENTS.md) and
[review](../../coverage/semantics/named-review.json) bind exact source/tools/modes.
Source/compiler/protocol and independent dense gates retain968/55cd; ab389 changes
only the regression selection test. Its original unsupported catch case remains
retained. All968 modes and967 other files are equal. Read current PROGRESS first.

The next bounded prerequisite is builtin fixed-name/reference-mode compilation
(proposed module106; verify registry before reserving it). Reuse the configured
780-function arginfo inventory and existing positional mode generator. Derive
case-sensitive name lookup and variadic-name handling from the pinned compiler
and generated signatures. Remove the named-builtin compiler boundary only when
known/unknown names, reference modes, aliases and native static-priority controls
have exact source evidence. Existing named→positional/unpack builtin boundaries
are retained in compiler049c/5ae and the named compiler catalogue. Named/unpacked
calls disable Zend's special/frameless lowering; preserve module87's positional
shortcut partition. Compiler admission does not implement builtin bodies, default
filling, callbacks or runtime unknown-name errors. Those dependencies remain
explicit; core intrinsics cannot be discarded merely because they are builtins.
Compiler preparation is `.tools/compiler7-builtin-named-next/PLAN.md`;
it remains preparation, and its original baseline must not be relabeled968.

Then prepare a coherent array argument-unpack slice before activating it.
Source argument count, expanded positional extent, fixed destinations and extra
named keys are distinct. The current104/105 source-prefix guards assume explicit
NArgs; do not reuse that assumption for dynamic expansion. Ground the next
continuation in actual container/key iteration and owning operands, without
reconstructing prior array values. Retain numeric/string-key order, positional
after named errors, duplicate names, variadic keys, reference cells, temporary/CV
array ownership and effects before failures. Traversable needs its object/iterator
protocol and remains separately required.

Reuse79/80/83/84/86/91/95/101/103/105 call, type, cache, suppression and owner
interfaces. Pending SENT slots and context NAMED entries own operands; HOLE has none.
ARGC is the effective positional extent, including positional tail values; extra
named keys do not extend it. Extra named SEND reference errors use fixed_count+1;
fixed named destinations use their mapped index+1;
named-tail TypeErrors use max(fixed_count, ARGC)+1 for every named entry. Later
coercion may change earlier shared aliases, so past types/values are not guards.

Interior missing defaults run in a callee frame before ordinary typed receives.
Successful hole caches retain uncoerced values; omitted reference parameters get
independent cells. Trailing defaults retain ordinary receive ordering. Native
traces render absent holes as NULL without filling machine storage. Object/NEW
side effects must preserve the pinned distinction between hole-preflight caching
and ordinary RECV_INIT caching. Source9369/default-cache and current named state
witnesses provide disjoint ordering, ownership and saved suppression controls.

Literal CV SEND reads/acquisition follow destination validation; computed FETCH
precedes it, and writable acquisition is distinct from reference promotion.
Deferred literal CV emission lines come from the argument-list AST, while known
fixed/computed operands keep their emitted lines. Module78/104 and86 repair actual
named and previously admitted positional line defects. The narrow84/105 unit
projection binds actual call argument roots; original SOURCE lines are unchanged.
Legacy positional tasks are invalid on named calls. Preserve arbitrary consistent
runtime values when extending these finite source/stage relations.

Root coordinates compiler7/runtime7 and independent review10, private immutable
candidates, original failures and sequential index ownership. Freeze meaningful
source/protocol/ownership/resume gates before publication; commit small reviewed
increments and never push. Full callable integration remains due. Final current
source, full syntax and fresh network-isolated offline rebuild are mandatory for
complete core. Objects, exceptions, dynamic callables/sources, reporting APIs,
generators/Fibers, lifetime and required intrinsics remain in scope; no family
closes at this checkpoint.
