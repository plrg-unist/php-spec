# Magic constants and source context

The [private1430 review](../../coverage/semantics/magic-context-independent-review.json)
approves nine top-level magic constructors for pairing with the request runtime.
It retains41 fresh native/lint/checked sources,55 metadata/CWD controls,61 current
adapter replays,24 descriptor cases,23 native dirname observations and the original
request path/magic failure. Canonical publication and declaration contexts remain
pending.

`__LINE__` uses its original AST leaf line. `__FILE__` uses the compiled source
identity, and `__DIR__` uses its POSIX dirname. When dirname is `.`, the request
supplies the working-directory fact explicitly; semantics performs no host lookup.
The optional `cwd` transport is canonical base64. Empty/NUL primitive paths reject,
and duplicate or malformed transport fields fail before semantic execution.

Compiled source identity remains separate from invocation spelling. SERVER path
fields and argv can retain a relative or symlink spelling while diagnostics and
file magic use the resolved source filename. The exact original combined source
now agrees with native PHP.

Namespace magic uses the active lexical namespace. Shared pure evaluation serves
both constant prepass and ordinary compilation, while their facts and effects
remain distinct. Computed magic variable names retain their ordinary no-CV
classification, including a computed name equal to `GLOBALS`.

Class, function, method, trait and property magic have empty top-level values.
Function/class/trait/closure bodies remain explicit execution boundaries. Future
frames and linking must install their proper declaration contexts before these
values can be used there; this review does not admit those bodies.
