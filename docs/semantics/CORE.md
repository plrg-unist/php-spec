# Executable core contract

The target is **PHP 8.5.10 CLI, NTS, signed 64-bit integers**, with the exact
local dependency pins in [provenance](../../dependencies/README.md).
[PLAN.md](../../PLAN.md) defines the complete-core objective;
[PROGRESS.md](../../PROGRESS.md) records current implementation limits.
The [inventory](../../coverage/semantics/features.json) tracks every syntax
constructor and separate runtime obligations. A catalog entry is a requirement,
not a claim that its implementation exists. Entries remain partial until their
full implementation and evidence obligations close.

## Execution and observations

Execution consumes checked SpecTec AST values and explicit original source
context. Semantic answers, including arithmetic, come from authored `.watsup`.
Zend lexing and the checked frontend remain the syntax boundary; Zend compilation
or execution cannot implement static checks, dynamic rules or numeric helpers.
The sole differential oracle is `.tools/php/bin/php` from the local release.

The baseline oracle profile is `-n`, `opcache.enable_cli=0`, `opcache.jit=disable`,
`precision=14`, `serialize_precision=-1`, `display_errors=stderr`,
`display_startup_errors=1`, `html_errors=0`, `log_errors=0`,
`error_reporting=30719`, `date.timezone=UTC`, `output_buffering=0`,
`implicit_flush=1`, and `zend.assertions=1`. Use locale `C`, timezone `UTC`,
a fresh process, and an explicit environment/working directory for each test.
Record loaded extensions: availability in the oracle does not admit their APIs.
Reviewed profile changes must be supplied consistently to both executions.

Compare exact stdout and stderr bytes and process status. Also retain semantic
events (output bytes, diagnostic severity/message/location, external requests and
responses), final completion kind and structured throwable/fatal information.
These outcomes stay separate: normal, explicit exit, throw, runtime fatal, static
rejection, suspension, Unsupported, frontend rejection, malformed input,
interpreter failure/stuck state, process crash, timeout and step-budget exhaustion.
A bounded timeout does not establish PHP nontermination. Unsupported and tool
failures never count as semantic passes. PHP exceptions are not runner failures.

Run records retain original source/fixture hashes and identities, arguments,
stdin, configuration, seed, budgets, frontend/static/dynamic/oracle outcomes,
raw bytes, comparison result and implementation/oracle fingerprints before and
after execution. Mutation invalidates authoritative evidence. PHPT expectation
matching is separate from raw spec/oracle agreement. No blanket whitespace,
warning, path or type normalization is allowed. An explicit fixture-root mapping
may preserve source identity relationships. The runner's transport spelling is
an interface detail; it must preserve these distinctions.

## Required intrinsic and internal-class catalog

The following is a closed initial catalog, subject to additions supported by
language necessity and explicit review. Each row names its inventory obligations;
rules, source-level tests and review are recorded there.
`python3 scripts/check-semantic-inventory.py --complete` requires every entry to
be closed; numeric/byte/coercion entries additionally require helper evidence. Source paths below are
relative to `vendor/php-src`. All implementation/test statuses are **pending**.
Methods and inherited constraints are those of the matching stub/implementation,
including argument binding, visibility, callbacks and abrupt completion.

| Names/protocols | Why included; dependency and source route | Inventory |
| --- | --- | --- |
| `stdClass` | `(object)` and ordinary object creation; `Zend/zend_builtin_functions.stub.php` | `protocols.stdClass` |
| `Closure`, invocation, `bind`, `bindTo`, `call`, `fromCallable`, `getCurrent` | Closure creation, capture, calling and scope rebinding; `Zend/zend_closures.{c,stub.php}` | `calls.closures`, `calls.closure-binding`, `protocols.Closure` |
| `Throwable`, `Exception`, `Error`, `ErrorException`, `CompileError`, `ParseError`, `TypeError`, `ArgumentCountError`, `ValueError`, `ArithmeticError`, `DivisionByZeroError`, `UnhandledMatchError` | Language throws/catches, constructors, properties, accessors and trace rendering; `Zend/zend_exceptions.{c,stub.php}` | `protocols.Throwable`, `protocols.Exception`, `protocols.Error`, `protocols.error-subclasses`, `diagnostics.*` |
| `Traversable`, `Iterator`, `IteratorAggregate` and their methods | `foreach`/unpack protocol dispatch; `Zend/zend_interfaces.{c,stub.php}` | `protocols.Traversable`, `protocols.Iterator`, `protocols.IteratorAggregate` |
| `ArrayAccess`, `Stringable` and their methods | Dimension access and string coercion invoke user code; same source | `protocols.ArrayAccess`, `protocols.Stringable` |
| `UnitEnum::cases`, `BackedEnum::from`, `tryFrom` | Enum-generated values/methods and rejection constraints; `Zend/zend_enum.{c,stub.php}` | `declarations.enums`, `declarations.generated-enum-methods` |
| `Generator`: `rewind`, `valid`, `current`, `key`, `next`, `send`, `throw`, `getReturn`; `ClosedGeneratorException` | Creation, iteration, delegation and resumable execution; `Zend/zend_generators.{c,stub.php}` | `resumable.generator-*`, `resumable.yield*`, `resumable.send`, `resumable.throw`, `resumable.get-return` |
| `Fiber`: constructor, `start`, `resume`, `throw`, `isStarted`, `isSuspended`, `isRunning`, `isTerminated`, `getReturn`, `getCurrent`, `suspend`; `FiberError` | Core suspension and stack switching; `Zend/zend_fibers.{c,stub.php}` | `resumable.Fiber-*`, `resumable.suspension-cleanup` |
| `exit`, `die`, `clone` | Callable forms are builtin declarations at this pin; clone includes its property-update argument; `Zend/zend_builtin_functions.{c,stub.php}` | `control.exit`, `classes.clone`, `classes.clone-with-properties` |
| `func_num_args`, `func_get_arg`, `func_get_args` | Observe call-frame argument state, including variadics/references; same source | `calls.argument-introspection` |
| `error_reporting`, `set_error_handler`, `restore_error_handler`, `get_error_handler`, `set_exception_handler`, `restore_exception_handler`, `get_exception_handler`, `trigger_error`, `user_error` | Minimal diagnostic control and callback reentry; same source | `diagnostics.*` |
| `assert`, `assert_options`, `AssertionError`, `ASSERT_*` | Compiler-special assertion checks, generated descriptions, failure/callback policy and its deprecated controls; `Zend/zend_compile.c::zend_compile_assert`, `Zend/zend_vm_def.h::ZEND_ASSERT_CHECK`, `ext/standard/assert.c` | `static.assertion-elision`, `source.assertion-description`, `protocols.assert`, `protocols.assert_options`, `diagnostics.assertion-failure` |
| `define`, `defined` | Dynamic declaration and lookup needed alongside constant syntax; same source | `declarations.constants` |
| `spl_autoload_register`, `spl_autoload_unregister`, `spl_autoload_functions`, `spl_autoload_call` | Class lookup reenters ordinary PHP; `ext/spl/php_spl.{c,stub.php}` | `dynamic.autoload-registration`, `dynamic.autoload-dispatch` |
| `register_shutdown_function` | Request-end callback execution; `ext/standard/basic_functions.{c,stub.php}` | `lifecycle.shutdown-registration`, `lifecycle.shutdown-order` |
| `register_tick_function`, `unregister_tick_function` | `declare(ticks=...)` callbacks; same source | `lifecycle.ticks` |
| `gc_collect_cycles`, `gc_enabled`, `gc_enable`, `gc_disable` | Observable collection and destructor timing; `Zend/zend_builtin_functions.c`, `Zend/zend_gc.c` | `lifecycle.collection-control`, `lifecycle.cycles` |
| `WeakReference::create`, `get`; `WeakMap` and dimension/iterator methods | Reachability observations and language-triggered collection effects; `Zend/zend_weakrefs.{c,stub.php}` | `lifecycle.weak-reference`, `lifecycle.weak-map` |
| `ob_start`, `ob_flush`, `ob_clean`, `ob_end_flush`, `ob_end_clean`, `ob_get_flush`, `ob_get_clean`, `ob_get_contents`, `ob_get_level`, `ob_get_length`, `ob_list_handlers`, `ob_get_status`, `ob_implicit_flush` | Explicit output buffering and callback/cleanup interactions; `main/output.c`, `ext/standard/basic_functions.stub.php` | `lifecycle.output-buffer-callbacks`, `environment.output-destination` |
| `Attribute`, `ReturnTypeWillChange`, `AllowDynamicProperties`, `SensitiveParameter`, `SensitiveParameterValue`, `Override`, `Deprecated`, `NoDiscard`, `DelayedTargetValidation` | Builtin declaration checks, deprecations, discarded results and trace redaction; constructors/properties/constants follow `Zend/zend_attributes.{c,stub.php}` | `declarations` obligations with the same names |
| Core constants | Literal `true`/`false`/`null`, integer/float limits, PHP version/platform, `E_*`, and constants of admitted classes/APIs; explicit target/configuration values from `Zend/zend_constants.c` and the stubs | `declarations.constants`, `environment.config` |

Assertions require explicit compile/runtime configuration. A known direct `assert`
call omits argument evaluation when `zend.assertions` is zero or negative; a
dynamic call still evaluates arguments before the intrinsic returns early. The
compiler supplies an exported expression description for a one-argument direct
call. Preserve this distinction, `AssertionError`/supplied throwable behavior,
callback effects, and the deprecated `assert_options` controls. Source-backed
assertion obligations remain pending; treating the API as an ordinary excluded
library would hide these language effects.

Each intrinsic follows the target's argument/type checks and exception propagation,
including source-backed early-return cases such as disabled assertions.
Unavailable ordinary-library calls produce explicit Unsupported when reached;
unknown user names instead follow PHP's undefined-function/name semantics.
Compile-time contextual checks still examine unexecuted code as required by PHP.

## Environment and ordinary-library boundary

The pinned build registers `GLOBALS` plus `_GET`, `_POST`, `_COOKIE`, `_SERVER`,
`_ENV`, `_REQUEST` and `_FILES` as auto-globals. It has no session extension:
`_SESSION` and `http_response_header` are ordinary variable names under this
profile. Initial values and registered auto-global names are separate facts.

The environment supplies request configuration, argument/stdin bytes and explicitly
admitted initial values; deterministic source units have original bytes, canonical
identity and lookup/failure responses. Includes share the proper scope and once
state. Eval uses checked parsing in eval mode, then independent static/dynamic
semantics. Neither source service compiles/evaluates PHP through Zend.

Backticks remain core syntax. Their command construction/dispatch is specified;
a finite shell service supplies explicit response bytes/failure/effects. Missing
service yields Unsupported. Implementing the process library is outside this
boundary. Includes similarly need a source provider, not every filesystem stream.
Fixture inputs/services must be reviewed, finite and shared by both executions.

| Borderline family | Decision and reason |
| --- | --- |
| Ordinary scalar/container helpers, `var_dump`, `print_r`, serialization, regular expressions, date/math/string libraries, sessions, databases, network/process APIs | Excluded ordinary libraries. Use core expressions/output to observe tests; no hidden helper initializes semantic state. |
| Reflection and reflection-created lazy objects | Reflection is excluded. The environment admits no lazy objects, so lazy-object property callbacks are outside this stated environment, not validated ordinary-object behavior. Reflection APIs cannot be used as test setup. The matching `ext/reflection/php_reflection.c` methods `newLazyGhost`, `newLazyProxy`, `resetAsLazyGhost`, and `resetAsLazyProxy` call `zend_object_make_lazy`; ordinary class construction does not create this state. |
| Weak references/maps, explicit GC, closure binding, argument introspection, output buffers and ticks | Included above because they expose or control core alias/call/lifecycle/output behavior; unfinished rules cannot be reclassified as libraries to close coverage. |
| `Serializable`, `Countable`, `InternalIterator` | Declaration identities/signature obligations must be retained when admitted core types depend on them (notably WeakMap). Serialization/count library execution and foreign internal iterators are excluded; user-defined protocol methods remain ordinary methods. |
| Stream wrappers and `spl_autoload` default filesystem search | Excluded ordinary-library registration/search. Include and autoload services expose explicit source lookup; missing required service is Unsupported, not fabricated success. |
| Resources and arbitrary extension objects | No resource-producing APIs or foreign object handlers are admitted initially. Initial-state validation rejects them explicitly; resource/extension-specific effects are outside this environment. |
| Memory/GC statistics, generic reflection/introspection APIs | Excluded implementation/library observers except the explicitly cataloged call/exception/handler observers. This does not excuse destructor, identity, alias or ordering differences visible through core execution. |

Boundary decisions constrain the eventual claim, not the implementation schedule.
All supported environment cases of each core construct require rules, independent
review and source evidence. Any intentional departure must retain its exact
mismatch and reviewed rationale.

Intentional departures from engine defects are recorded separately in
[DISCREPANCIES](DISCREPANCIES.md); they never count as differential agreement.
