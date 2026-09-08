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

`18-class-headers.watsup` adds `$pchcompile(statement, active-class, context)`
for named class, interface and trait headers. `PCHOK` contains kind, fully
qualified declaration name, abstract/final/readonly flags, optional parent,
ordered interface names, the unchanged checked body and ordered diagnostics.
`PCHERROR` retains earlier deprecations and the first fatal header diagnostic;
`PCHUNSUPPORTED` identifies a pending phase or invalid edited input. An interface
has its abstract flag set. The descriptor does not register a name, compile its
body or establish inheritance validity. The caller must compile that retained
body and perform the required linking before treating a declaration as usable.

The active-class input means another class declaration is currently compiling;
it is separate from the type helper's inherited runtime class scope. The caller
also supplies the exact class-keyword compiler line. Modifiers and attributes
can start on earlier lines than that keyword, while a name may start later;
the helper never substitutes the PHP-Parser node's startLine. Missing file/line
and edited invalid names/modifiers/references produce explicit Unsupported.

Header checks preserve nesting, reserved declaration name, underscore deprecation,
local-import conflict, parent-reference, attribute and interface-reference order.
The underscore declaration deprecation also applies inside a namespace. Parent
and interface references use `$pchref`, the separate constant class-reference
rule derived from `zend_resolve_const_class_name_reference`. In these positions,
`int` is an unresolved class name, and no type-normalization warning or primitive
substitution applies. Bare and namespace-relative self/parent/static are rejected
as reserved references; fully qualified forms receive the invalid-class-name
error. This rule is distinct from the intentional namespace-relative static type
interpretation described above. Namespace/class-import prefix replacement remains
case insensitive, with original resolved byte spellings retained.

Class attributes, anonymous identity generation and enum header compilation are
pending. Body compilation, trait-use/adaptation rules, duplicate declarations,
class-table lookup, autoload, inheritance/variance and activation are separate
unfinished milestones. A retained `BODY` is an obligation to compile, not a claim
that its members are valid. `PCHOK` deliberately allows unresolved parent and
interface references, just as lint can succeed without those classes existing.

Run `python3 tests/semantics/class_headers.py`. Empty declaration fixtures compare
ordered exact lint diagnostics; descriptor cases check resolved names, flags,
interface order and retained body syntax. Exact PHP-Parser early special-name
rejections are reported separately with pinned lint evidence. Equivalent edited
checked headers exercise those reference errors without claiming frontend
agreement. Reports retain per-case source/AST hashes and IDs, source contexts,
local runtime identity, budgets and dependency fingerprints. Evidence comes from
`zend_compile_class_decl`, `zend_assert_valid_class_name`,
`zend_resolve_const_class_name_reference`, `zend_resolve_class_name` and
`zend_compile_implements` in the pinned `Zend/zend_compile.c`, and declaration
keyword-line capture in `Zend/zend_language_parser.y`. These are header helper
checks; they do not establish source declaration execution or complete class
semantics.

Oracle-only trait phase witnesses constrain the later binding work. At this pin,
`trait T { function f(): self|C {} } class C { use T; }` declares successfully,
while writing that method directly in `C` gives the duplicate-C type compile
error. `trait T { function f(): parent {} } class C { use T; }` also declares
successfully with no parent. Trait binding must therefore retain the accepted
union structure and contextual markers rather than rerunning local redundancy
or no-parent checks. These witnesses are not implemented trait semantics or
runtime return-type validation. `zend_do_link_class` also loads parent, traits
and interfaces before trait-member binding, parent inheritance and interface
checks; eventual requests and resumptions must preserve that ordering.

`19-variance.watsup` adds `$pvcovariant(child-type, child-scope,
prototype-type, prototype-scope, visible-classes)`. It returns `PVCOMPATIBLE`,
`PVINCOMPATIBLE`, or `PVNEEDS` with missing class names. Absent types or unnamed
scope inputs return explicit Unsupported. Other inputs must be valid normalized
branch descriptors. Each class descriptor supplies its canonical identity,
parent name, complete transitive class/interface ancestor names and final flag;
registry keys may be aliases for that same identity. These are authoritative
inputs from a future independent linker, not facts inferred from all declarations
in the AST. Both scope identities are explicitly known. Registry visibility must
match the particular compilation or linking phase.

The rules compare primitive masks, class ancestry, unions and intersections,
including iterable's array/Traversable components, Closure/callable, final-self
replacement of static, mixed and never. Equal class names compare case
insensitively without requiring a registry entry. Definite failure dominates an
unresolved conjunction; definite success dominates an unresolved disjunction.
Contextual self/parent markers are resolved for comparison without rerunning the
local type compiler or changing the retained declaration type structure.

The pinned engine's static-permits-self predicate is deliberately separate from
general subtype checking. A child static return can replace a pure `I&J` return
when its class implements either member, but cannot replace `(I&J)|null` merely
because its class implements both. `zend_type_permits_self` scans the top-level
named entries and skips nested DNF intersections. The specification follows this
observed predicate; it does not substitute mathematical set subtyping.

`PVNEEDS` collects every missing class name from the child type followed by the
prototype type, preserving branch/member order and deduplicating exact byte
strings. This reflects `register_unresolved_classes` for an unresolved comparison
under the supplied visibility environment. It is not a callback/autoload schedule
or a complete delayed-obligation machine. Actual lookup visibility, existing
pending requests, inactive-engine errors, autoload timing, resume checks and
class activation remain unfinished. The helper emits no declaration diagnostics.

Run `python3 tests/semantics/variance.py`. Checked source return ASTs are locally
normalized and compared under manually specified class graphs corresponding to
executed declaration-only oracle fixtures. The harness compares covariance
status and test-rendered fatal text, file and line for isolated return-only
methods; this does not implement production method diagnostic rendering or
source declaration activation. Separate symbolic descriptors exercise aliases,
contextual markers and missing-name order. Reports retain stable source/type-AST
hashes and case IDs, explicit registry/context inputs, raw oracle channels,
runtime identity, budgets and implementation fingerprints. Evidence is
`zend_perform_covariant_type_check`, its class/intersection helpers,
`zend_type_permits_self`, `resolve_class_name`, `lookup_class_ex`,
`register_unresolved_classes` and `emit_incompatible_method_error` in the pinned
`Zend/zend_inheritance.c`. Method arity/by-reference/contravariant parameter
checks, tentative internal returns, member legality and trait binding remain
separate pending steps.
