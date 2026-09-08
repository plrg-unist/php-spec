# Independent declaration types

Target: the local PHP 8.5.10 CLI NTS signed64 build and pinned sources in
[dependencies](../../dependencies/README.md). `16-static-types.watsup` is authored
executable semantics, loaded after `spec/php.watsup` and `10-bytes.watsup`.
It is a helper milestone. The source machine does not yet compile or activate
function/class declarations through these rules.

`$ptype_normalize(phpType18, ptcontext)` consumes the actual checked syntax type
used by parameters, returns, properties and class constants. Its results are:

- `PTOK ptbranch* ptdiagnostic*`: ordered union alternatives, each a conjunction
  (`PTBRANCH ptatom*`), with ordered nonfatal compile diagnostics. An absent
  type has no branches. Nullable syntax adds a null branch; `iterable` remains
  an explicit alias atom with array/Traversable meaning. Primitive names are
  canonical; resolved class names preserve their byte spelling. Type lists
  retain declaration order, independently of diagnostic display order.
- `PTERROR ptdiagnostic*`: previously emitted warnings/deprecations followed by
  the first fatal compile diagnostic. A diagnostic stores severity, symbolic
  code, typed message arguments and the complete immutable source context.
  `$ptmessage` computes the exact message bytes independently, including Zend's
  class-first/primitive-order type display and nullable display conventions.
- `PTUNSUPPORTED text`: an edited invalid name/type shape, missing source
  identity/compiler line. It is neither acceptance nor a PHP diagnostic.

The context contains byte namespace and class-import alias/target pairs, scope,
position, diagnostic owner/member names, original file identity and the compiler's
current line. Imports must already be a legal class-import map; this helper does
not validate use declarations or resolve function/constant imports. No class
lookup, autoload, inheritance check, declaration activation, default evaluation,
parameter binding or runtime value type check occurs here. Ordinary class names
remain unresolved class descriptors, even when no such class has been declared.

Scope is explicit because absence of a current class does not determine it:

| Scope | Meaning |
| --- | --- |
| `PTGLOBAL` | A free function whose absence of class scope is known. |
| `PTKNOWN class parent?` | Named class scope; self/parent are substituted before duplicate/intersection checks. |
| `PTANONYMOUS has-parent` | Anonymous class scope; self/parent remain contextual markers. |
| `PTDEFERRED` | Trait, rebindable closure, or inherited file/eval scope; contextual markers remain unresolved. |

`static` remains a late-static atom. An unresolved self/parent cannot enter an
intersection, while a self/parent already substituted in a known named class
can. Namespace-relative self/parent also use contextual fetch in this pin;
fully qualified self/parent are invalid class names. Class aliases replace the
first qualified component case-insensitively. Duplicate class identity is
case-insensitive, but diagnostics retain the triggering spelling/resolved alias.
The union fold preserves primitive-overlap, true/false, class/DNF redundancy,
object/class, and void/never diagnostic precedence. Warnings for exact lowercase
confusable names and the global `_` deprecation precede later errors.

The caller chooses compilation timing and source lines. Exact pinned witnesses
show that a multiline parameter uses its parameter/type start line; a multiline
return type uses its function declaration line; a property uses its type line.
The helper propagates this explicit context, not type-node startLine metadata.
`OWNER` and `MEMBER` provide display names for property/constant diagnostics.
The runner must render CLI prefixes, file/line suffixes and compile-fatal stack
traces separately. Supplying these helpers with lint results would invalidate
the independence boundary: lint is used only by the tests.

Evidence routes in `vendor/php-src/Zend/zend_compile.c` are
`zend_compile_single_typename`, `zend_compile_typename_ex`,
`zend_is_type_list_redundant_by_single_type`,
`zend_are_intersection_types_redundant`, `zend_is_scope_known`,
`zend_get_class_fetch_type_ast`, `zend_resolve_class_name`,
`zend_type_to_string_resolved`, `zend_compile_params`,
`zend_compile_prop_decl`, and `zend_compile_class_const_decl`.
Matching PHPTs live in `Zend/tests/type_declarations/` (especially `iterable/`,
`relative_types/`, and union/intersection/DNF cases). The independent reviewer's
`tests/semantics/conformance/type-*.php` witnesses retain additional exact
source diagnostics; they remain oracle-only until source integration.

Run `python3 tests/semantics/static_types.py`. The test independently parses
source, checks real SpecTec values, and compiles helper fixtures through the
algorithmic and structured executable stages with encountered-path determinism
checking. It compares pinned lint acceptance and every ordered diagnostic's
severity, code, exact message bytes, original file and explicit compiler line.
Separate exact descriptors check aliases, qualified suffixes, known/deferred
scope, nullable and intersection structure. Edited shapes/missing context are
explicit Unsupported tests. The report records actual PHP version/SAPI/width/ZTS,
INI/env settings, finite process budgets, dependency fingerprints and original
sources. Unsupported cases, parser rejections, oracle crashes and compiler-stage
frontend restrictions do not count as source execution agreement.

PHP-Parser `ParserAbstract::checkParam` rejects direct `void $x` before Zend's
parser does. The harness pins that one exact source and frontend diagnostic,
confirms its corresponding pinned compile error, and obtains its type from a
separately checked return-type syntax fixture. The report labels this separately;
it is not parser agreement or a repaired frontend.

An independently reproduced engine inconsistency is retained in the
[discrepancy ledger](DISCREPANCIES.md), with
[raw oracle evidence](../../coverage/semantics/engine-defects.json): `function f():
namespace\static {}` enters the self/parent-only branch of
`zend_compile_single_typename`. In a class with no parent, the pinned non-debug
binary terminates with SIGSEGV during `-l`; with a parent it accepts. The source
asserts that this fetch is self or parent, then otherwise assumes parent_name.
The project deliberately interprets namespace-relative static as the same
late-static type as bare static: known absent class scope produces the usual
no-class compile error; named/anonymous/deferred scope preserves `PTSTATIC`.
Every non-return position produces the synthesized compile diagnostic
`static can only be used as a return type`, including deferred trait/closure
scope where binding is not yet known. This diagnostic and the correction of
parent substitution/crashing are intentional departures from this engine pin.
The dedicated 24 context/position witnesses are reported separately as intended
semantics, never included in the engine-agreement count. Oracle crashes are
retained by the independent reviewer, never counted as validation passes.

`17-signatures.watsup` adds `$pscompile(parameters, return-type, by-reference,
context)`, loaded after the type helper. Its `PSOK` result contains ordered
parameter descriptors, the return type and return-reference bit, together with
ordered compile diagnostics. `PSERROR` retains earlier nonfatal diagnostics and
the first fatal; `PSUNSUPPORTED` identifies an unfinished compilation step and
makes no claim about a completed diagnostic trace. The caller provides the
function/method display name and original declaration line in the context;
parameter lines come from each checked parameter node. A retained unresolved
constant default updates that line to its constant-fetch line, as the constant
compiler does; already-folded null/true/false literals retain the parameter line.
Namespace/import/class
context is passed unchanged to the type helper. No function is registered or
invoked, and no class is loaded by these rules.

Compilation normalizes the return type before walking parameters. The parameter
walk checks startup-profile auto-globals, duplicates, `$this`, variadic ordering
and variadic defaults before default/type validation. The target build has no
session extension: `_SESSION` is therefore an ordinary parameter name. Null
literal defaults can make a type implicitly nullable; the deprecation precedes
parameter-position errors. Optional parameters preceding the last required
parameter become required and lose their defaults, including implicitly nullable
parameters for which that particular optional-before-required notice is suppressed.
A terminal variadic parameter is optional and retains its reference bit. An absent
`__toString` return type receives the implicit string descriptor; magic-method
arity, body legality and other class obligations remain separate checks.

Each retained default stores the original checked expression and its materialized
kind, including the int-to-float conversion required by a float-only declaration.
Plain unresolved constants retain their syntax and the `deferred` kind; consumers
must resolve them in the eventual declaration environment. This does not accept
or evaluate their runtime values. Literal scalars, empty arrays, literal
true/false/null, and nested signs over numeric literals are classified here.
A namespace-relative special constant is resolved against the explicit namespace:
`namespace\null` is the null literal in global scope, and a deferred constant
in a named namespace. Case variants follow the same rule. This local interface
assumes no constant-import aliases; class imports remain the type helper
context. Constant-import processing is an explicit prerequisite of the later
complete default compiler.
Pure mathematical integer tracking checks signed64 negation overflow; float
operands remain floats under either sign. Thus the source decimal literal
`9223372036854775808`, including nested negative signs, remains a float. No host
PHP arithmetic, Zend compiler result, or binary64 calculation is used to classify
these signatures. Default materialization itself is still pending.

General constant expressions, nonempty arrays, dynamic new/closures/callables,
parameter attributes, promotion and hooks currently produce Unsupported. These
are unfinished core work, not excluded language features. The next default
milestone must compile constant expressions using the pure numeric rules and an
explicit declaration/constant environment, preserving deferred expressions and
compile effects before supplying the same signature descriptor. Full declaration
activation, namespace/constant-import processing, class linking/variance and
calls remain later integration steps. A caller must also account for parameter
`http_response_header` setting the function compiler's assigned-name flag before
body compilation (`zend_compile_params`); this helper does not compile bodies.

Run `python3 tests/semantics/signatures.py` for pinned lint comparisons of exact
ordered severity/message/file/line events, descriptor fields, retained default
ASTs and explicit pending/edited cases. PHP-Parser's early direct-void and
variadic-default rejections are retained separately with exact frontend and lint
evidence; equivalent edited checked parameter ASTs exercise the compiler rules
without claiming source-parser agreement. The report records the local oracle's
loaded extensions, profile, budgets, source/binary fingerprints and raw lint
channels. These are local helper checks, never source execution coverage.
Source evidence is `zend_compile_params`, `zend_is_valid_default_value`,
`zend_try_ct_eval_unary_pm`, `zend_compile_const_expr_const`,
`zend_resolve_const_name`, `zend_try_ct_eval_const`, `zend_const_expr_to_zval` and
`zend_compile_func_decl` in the pinned `Zend/zend_compile.c`, together with
`php_startup_auto_globals` in `main/php_variables.c`.
