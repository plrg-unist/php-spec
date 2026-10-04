# Source trait composition

Module 228 compiles and links method-only source traits under pinned PHP 8.5.10.
A using class overrides trait methods; trait methods override inherited methods.
Nested uses, duplicate imports, `insteadof`, aliases, visibility changes and final
adaptations preserve Zend's method selection and diagnostics. Abstract trait
requirements are checked against the selected implementation after parent
inheritance and before interface contracts.

Imports retain two identities. The declaring owner and lexical `self` scope are
the using class; the body, filename, line and `__TRAIT__`, `__METHOD__` and
`__FUNCTION__` remain those of the original trait method. Aliases have their own
class/name identity and declared spelling in traces. `__CLASS__` and contextual
class-name defaults use the selected import or authenticated rebound Closure
scope. Constructor-free `new self` and `new parent` in trait method parameter
defaults use the selected method's lexical scope. An inherited method keeps its
original import identity. Goto and include/eval entry retain the physical checked body
while authenticating the selected importing scope.

Method static cells are separate for every using class and alias. Inherited
methods and their captured/clone callables share the selected import's cells;
explicitly reusing the trait in a child creates new cells. Real Closures keep
per-instance storage and their creating import's lexical/called class after
other classes import the same body. Retired private method captures retain a
source-compatible maker and caller-scope certificate without acquiring a new
receiver owner. These are structural wellformedness checks, not a reconstruction
of arbitrary retired execution history.

Classes and composed traits containing a real trait use always defer early
publication. Linking resolves parent names, trait names and interface names in
that order, then validates adaptations and binds concrete methods before parent
inheritance. Abstract requirements follow parent checks. This preserves prior
output, missing-name priority, final/abstract conflicts and failed declaration
rollback. Successful declaration history is replayed from raw source images;
imported descriptors and alias identities must equal that replay's result.

Private-final alias warnings use `E_COMPILE_WARNING` and do not enter ordinary
error handlers. Abstract alias warnings occur after parent linking. Direct
static access to an accessible concrete trait method emits the native deprecation
before arguments or first-class capture. A throwing handler aborts the pending
call; capture emits the warning once and subsequent invocation uses the selected
callable.

Logical method entry and finalizer continuations retain the complete selected
class/alias identity. Protected regions use the physical source method only
after authenticating CURRENT; saved frames restore their own scope and locals.

The source truth is `Zend/zend_compile.c::zend_compile_class_decl`,
`Zend/zend_inheritance.c::zend_do_link_class` and its trait binding helpers,
`Zend/zend_object_handlers.c::zend_std_get_static_method`, and the trait branch
of `Zend/zend_ast.c::zend_ast_evaluate_ex`.

Run author source controls with
`python3 tests/semantics/method_runtime.py --catalogue tests/semantics/trait_method_cases.json`.
Independent source catalogues cover composition, warning masks, abstract priority,
retired caller scopes and finalizers; `trait_method_review_protocol.py` checks selected
import identity, defaults, static keys, closures, source scope and rollback.
The [review ledger](../../coverage/semantics/trait-methods-review.json) records
actual cutoffs, commands, original failures and finite limits.

Trait properties and constants are explicitly Unsupported at this method
checkpoint. Their composition, static property sharing, readonly constraints and
constant compatibility are the next required phase. A parentless trait `parent`
parameter remains a valid declaration; receiving that unresolved dependent type
retains the existing Unsupported boundary. Constructor defaults, Closure keyword
NEW defaults and body keyword NEW retain their existing boundaries. Broader
attributes, autoload, hooks, lifecycle services and paused return work remain
separate obligations.
