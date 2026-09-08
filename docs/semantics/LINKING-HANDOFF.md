# Static linking continuation

This is the interface handoff for the next declaration/linking milestone. Read
`STATIC.md`, `PROGRESS.md`, `PLAN.md`, `DESIGN.md` and `VALIDATION.md` first. The
static helpers are executable specification modules and dedicated local oracle
campaigns; they are not in the source machine's declaration dispatch. Coordinate
any shared runner/module-list/frontend integration with the runtime owner. Keep
namespace/import context, compiler diagnostics and class-table visibility
explicit. Do not infer a table of usable classes from every declaration in an AST.

## Available interfaces

- `16-static-types.watsup`: `$ptype_normalize(type, ptcontext)` returns ordered
  diagnostics and normalized union/intersection branches. Context includes
  namespace/class imports, class scope, declaration position, owner/member,
  source file and compiler line. Preserve the adjudicated namespace-relative
  static type distinction in `DISCREPANCIES.md`.
- `17-signatures.watsup`: `$pscompile(parameters, return-type, byref, context)`
  returns ordered compiled parameter/return descriptors and diagnostics. Defaults
  retain checked syntax and a materialization kind; a full constant-expression
  compiler/environment is still missing. Constant-import aliases, attributes,
  promotion and hooks are explicit pending boundaries.
- `18-class-headers.watsup`: `$pchcompile(statement, active-class, context)`
  returns named class/interface/trait header descriptors. Parent/interface names
  are resolved using header class-reference rules; the checked `BODY` is retained
  unchanged. The caller still must compile members and link the declaration.
- `19-variance.watsup`: `$pvcovariant(child-type, child-scope, prototype-type,
  prototype-scope, visible-classes)` returns a status or missing-name collection.
  Class descriptors supply canonical identity, parent, complete transitive
  class/interface ancestry and final flag. Alias keys denote those identities;
  scope descriptors are explicitly known. The registry must contain applicable
  visible builtins under global keys, including Traversable and Closure.
- `19-method-signatures.watsup`: `$pmcompare` accepts selected user-method
  descriptors, separate comparison scopes and the same visible registry.
  `pmmethod.OWNER` is the original display owner, distinct from contextual type
  scope. `PMCHECK` retains earlier missing-name collections even if a later
  argument/reference/return comparison fails. `PMINTERNAL` remains pending until
  a pinned signature/tentative-return catalog exists. `$pmmismatch` renders a
  definite mismatch; `$pmunavailable` may be called only after the caller exhausts
  loading attempts for its supplied pending collection. Source dispatch does
  neither automatically.

The signature and method contexts require exact compiler lines, not a parser
node's first modifier/attribute line. A future frontend/compiler context pass
must account for namespace/import processing, per-function assigned-name flags
(such as `http_response_header`) and declaration phase ordering. Runtime calls
must consume the compiled descriptors without redoing local normalization.

## Next bounded stages

1. Compile class bodies into ordered member tables: methods, properties,
   constants, trait uses/adaptations and attributes. Keep original declaration
   owner/source context separate from the class in which a member is compared or
   used. Complete missing local method/body legality, magic-method, property-hook
   and modifier checks before claiming a usable member table.
2. Represent class dependencies and resumption explicitly. Pinned
   `zend_do_link_class` loads the parent, traits, then all interfaces before
   member binding. Trait binding, parent inheritance, the abstract-trait pass,
   interface checks and delayed variance resolution have distinct later stages.
   A bulk table precheck must not reorder diagnostics or loading requests.
3. Select method prototypes and establish applicability before `$pmcompare`:
   private concrete-method exemptions, constructors' abstract/interface
   prototypes, final/static/abstract checks and visibility constraints. Derive
   internal/tentative signatures from pinned builtin metadata, not caller flags.
4. Implement trait member selection/adaptation and collisions, then inheritance
   of constants/properties/hooks and remaining class/interface obligations.
   Preserve declaration order and phase-specific error provenance.
5. Integrate declaration activation with the source machine: namespace/import
   state, compile effects, early/conditional declarations, duplicate definitions,
   dependency loading, resumptions and publication of usable descriptors. This
   requires runtime-owner agreement on states and transitions; no blanket
   hoisting or autoload implementation is supplied by the pure helpers.

Trait phase witnesses already in `STATIC.md` constrain stage 4. A trait's
`self|C` can remain accepted when used in C although the same direct declaration
is a duplicate-type error; trait `parent` can survive binding into a class without
a parent. Do not rerun the local type compiler on binding. Also retain the pinned
`zend_type_permits_self` shortcut: static versus a pure intersection differs from
static versus a DNF intersection, as documented and tested by the variance helper.

`PVNEEDS` and `PMCHECK` collections preserve missing-name insertion order under a
supplied visibility environment. They are not complete delayed-autoload queues or
callback schedules. Existing pending requests, inactive-engine errors, lookup
visibility and loading/resumption timing remain integration obligations.

## Evidence and ownership

Dedicated commands are `python3 tests/semantics/{static_types,signatures,
class_headers,variance,method_signatures}.py` (run each script separately).
Reports are in `coverage/semantics/`. Stable IDs and source/AST hashes describe
helper evidence, not source-machine coverage. The implementation fingerprint is
broad: coordinate spec/test edits across owners before final campaigns. Do not
start multiple Dune builds simultaneously; once built, independent oracle/helper
campaigns can share a quiet window.

Source anchors for the next stages are `zend_compile_class_decl`,
`zend_compile_func_decl`, `zend_compile_params`, trait-use compilation in
`Zend/zend_compile.c`, and `zend_do_link_class`, `do_inheritance_check_on_method`,
`do_inherit_method`, trait binding, delayed obligations and
`emit_incompatible_method_error` in pinned `Zend/zend_inheritance.c`. Use the
project-local PHP 8.5.10 binary only as an oracle, never as a semantic operation.

## Compiler context pass before further activation

The first [checked source-occurrence gate](SOURCE-CONTEXT.md) provides generated
typed child access, retained source units and stable unit-local structural paths.
It does not yet supply lexical environments or a PHP compilation schedule.

A useful next milestone is an ordered traversal producing explicit compiler
contexts and pending descriptor work from checked ASTs. Carry all three import
kinds (class/function/constant), namespace, original declaration identity,
known/anonymous/deferred class context, exact class/function compiler lines and
per-function assigned-name flags. Existing helpers accept only the documented
class-import subset; constant-import aliases require real environment support.
Track constant-expression compile effects, including changes to the compiler
line when retaining a deferred constant, instead of reconstructing context from
runtime lookup or the parser's first token alone.

Keep compiler diagnostic locations separate from active execution locations.
A computed NaN default can issue a string-coercion warning while formatting a
mismatch at the class activation line, followed by a fatal at the method line.
`method_signatures.py` retains a line-3/line-4 oracle witness: source default
compilation remains pending, and an edited NaN literal explicitly requests the
missing activation warning context. A later rendering/event interface must retain
that warning and its actual context. Do not silently discard numeric formatting
flags. This context traversal should precede claims that declaration helpers are
integrated into source execution; it must not replace unresolved names with an
AST-wide class table or perform blanket value/declaration activation.
