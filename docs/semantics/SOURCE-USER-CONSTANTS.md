# Ordinary source user constants

Ordinary `const` declarations and reads use the checked source compiler and runtime for the pinned PHP 8.5.10 CLI profile. Scalar/array and certified Closure/FCC values are supported; the constant family and full core remain partial.

## Declaration and lookup

The compiler handles each actual `NConst` initializer before validating its declaration name. Shared constant-expression preparation preserves selected/skipped branches, compile diagnostics, and deferred expressions. `CODENAME` and `CODEEXPR` at the declaration origin retain the resolved name and emitted opcode line; initializer paths remain the original source paths. The compiler contract describes the admitted constant-expression boundary.

Runtime `CONSTANT_INIT` evaluates one initializer through the ordinary expression machine, then `CONSTANT_BIND` activates its value before the next declaration starts. A missing name or other initializer error leaves earlier constants active. A duplicate name evaluates its initializer first, emits the native duplicate warning, releases its temporary value ownership, and preserves the earlier binding. Constant-AST diagnostics use the recorded declaration opcode line, including multiline initializers.

The request-local table normalizes namespace prefixes to lowercase and preserves terminal-name case. Reads use the compiler-resolved primary and namespace-fallback names in order. Constants become visible when their declaration executes; source declaration presence does not preactivate the value. Existing constant-name compilation handles imports and namespace contexts.

## Values and allocation classes

`USERCONSTANTS` entries own their ordinary runtime values. Constant reads, array copies, nested value calls, reference sends, and temporary foreach references use the existing heap and copy-on-write machinery. The table's roots are included across active and saved frames and abrupt cleanup. A failing initializer clears pending initializer work and scratch facts while retaining existing table and request roots.

Allocation provenance is a separate non-owning tree: `PVSCALAR`, `PVSTRING bool`, `PVCLOSURE` with its exact object identity, or `PVARRAY bool` with ordered keyed child classes. The flag records the source-backed non-refcounted case needed by subsequent default-receive semantics. It is not inferred from final bytes or length. Both string flags can accompany empty bytes; an allocated array can be empty. The shared empty-array class requires empty topology.

Shared compiler facts export `PCCLASS` beside existing `PCONSTANT` values. The compiler records classes while folding actual child facts. Runtime `CONSTANT_OBSERVE` records the result of actual evaluation and propagates classes through the same selected children and operations. A fully stored initializer applies direct-root string interning at declaration installation; strings inside its arrays retain their own classes. Deferred initializers preserve operation and imported-value provenance. The allocation-class contract records the pinned scanner, literal-installation, cast, concatenation, bitwise, and array distinctions.

## Resumption invariants

Static/no-use REAL Closure and named/static-method FCC initializers retain an
exact full `NConst` receipt, callable source path and publication prefix. REAL
Closures use the source unit's immutable entry class for both lexical and called
scope, with no receiver; an inherited include/eval therefore uses its declaring
method scope rather than its forwarded called class. Named functions remain
unscoped. Wrapped objects and genuine plain clones retain exact receipt authority.
Registration checks the actual value against its allocation class and certified
source transfer; array aliases retain existing object identity.

Duplicate registration suspends through the genuine warning dispatcher. Its
continuation owns the actual discarded candidate and captures the preceding
constant-table prefix, so callback namespace shadows cannot change that alias
lookup. Return or throw preserves the installed binding and releases the
candidate. Raw-trait method capture similarly suspends before allocation; its
saved source/target/publication facts authenticate resumption. Receipt metadata
adds no roots, and successful constants remain owners after local variables die.

Public source-state checks bind table names and declaration tasks to actual `NConst` origins and compiler descriptors. They check unique names, valid task indexes, initializer/bind/observer ordering, declaration context, exact source-derived pooled class facts, and value/class tag and ordered array topology. Metadata adds no heap owners.

Initializer scratch facts retain a scalar operand or an array's non-owning class tree. Their origins must belong to the active initializer. Pooled origins agree with the fixed pool class. Conditional and coalesce facts must agree with the already recorded condition truth or left nullness, so an unexecuted opposite arm cannot determine the selected class. These checks inspect current values and continuation relationships; they do not replay expressions or reconstruct arbitrary runtime values from source. Positive tests change condition values and selected string bytes while preserving the source-consistent branch.

The quiet-coalesce path captures the already computed left result before temporary-base disposal, only while an initializer context is active. It does not perform another read, evaluate a key twice, or add events. A missing string offset contributes null to this observation. Outside a constant initializer the added helper is the identity; independent ordinary quiet-source and resumption checks cover that shared boundary.

## Validation and remaining work

The maintained author catalogue compares 75 exact native stdout/stderr/exit profiles and checks 46 class/scratch assertions. Public protocols cover 14 table/class controls, 14 context/task controls, and six branch variants with 126 assertions. Three author state programs pass 821 assertions over adjacent steps and selected full resumes. Independent source, constant-owner, quiet-path, historical call-state, and compiler gates are recorded separately in the acceptance evidence.

The initial final reports used 899 inputs at `e7d552ec`; the final state report uses 899 at `ca3c06e5`. The explicit bridge changes only the state-test expectation from an empty allocation set to the initial request allocation set. Runtime/compiler bytes and modes are identical. The failed fixture outcome remains retained.

Nine new global callable originals pass at separate414/5d0/92ff source cuts; seven
source-derived AL programs/341 premises pass at21b5. The
[default ledger](../../coverage/semantics/deferred-static-defaults-review.json)
retains exact profiles, failures and fixture recovery. Matching8.5.10 sources are
`zend_compile_const_decl`, `ZEND_DECLARE_CONST`, `zend_ast_evaluate_ex` and
`zend_register_constant`: evaluate in the executing op-array scope, then register,
and destroy a duplicate candidate only after its warning finishes.

An alias evaluated before an initializer callback publishes a namespace shadow
still needs its own immutable transfer continuation; this is immediate required
work. Global NEW, wider object-producing initializers, remaining builtin constant
values and `define`/`defined` remain open. Class/default and callable consumer
families retain their separate inventory and evidence; no complete-core claim.
