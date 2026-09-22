# Empty-class inheritance

The source compiler records each resolved parent name in the class descriptor.
It binds an eligible top-level child early only when its parent is already
known; forward and conditional parents link when execution reaches the child.
The checked `classKeywordLine` fact supplies the line for link diagnostics,
including declarations whose modifier and name are on different lines.

An active class has a separate parent link to an active source class or the
pinned internal `stdClass`. Publication adds the name and link together after
parent lookup and final/readonly checks. A failed link leaves earlier bindings
intact. The link list is topologically ordered by parent dependency; paused
states verify source origins, active names, compatibility and that order.
Instances retain their allocated class identity while `instanceof` and class
parameter/return checks traverse the active parent chain, including admitted
class intersections and unions. An abstract empty parent can have a concrete
empty child; abstract class allocation remains an error.

The rules are in `133-inheritance-compiler.watsup` and
`134-inheritance-runtime.watsup`. [The review](../../coverage/semantics/inheritance-review.json)
binds source, compiler, syntax and paused-state checks. Valid internal parents
other than `stdClass`, interfaces, members, constructors, dynamic parent names
and late-bound `self`/`parent`/`static` remain separate obligations.
