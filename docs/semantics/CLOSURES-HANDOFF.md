# Explicit closure foundation

Compiler115/runtime116 are independently accepted on1017/9325, code875c7867.
The [review](../../coverage/semantics/closures-review.json) binds exact source,
compiler, protocol, ownership, compatibility, archive and canonical CLI evidence.
The [contract](SOURCE-CLOSURES.md) records the bounded source behavior and remaining
services. Full PHP core remains the objective in [PLAN](../../PLAN.md).

Real closure objects own ordered captures and per-instance static slots through
the shared heap. Value captures supply fresh invocation-local cells; reference
captures share actual wrappers. Pending targets and active/saved contexts own the
selected instance across argument effects and cleanup. Source-authenticated guards
permit arbitrary consistent current values and never reconstruct execution history.
Unreachable cycles survive reference-count pruning; no cycle collector is claimed.

Next is the [arrow-function slice](ARROWS-HANDOFF.md), with fresh review of implicit
capture discovery, completed undefined values and expression-return metadata.
Ordinary objects, required Closure/class/method services, fake first-class callable
lifetime, exceptions and dynamic sources remain open. Historical broad integration
is not current validation; full syntax and fresh offline checks remain required.
