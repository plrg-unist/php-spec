# Initial builtin positional argument modes

This prerequisite specifies compilation metadata for the pinned PHP 8.5.10 CLI,
NTS, 64-bit configuration with `-n`, empty `disable_functions`, and the configured
initial module registry. It implements no builtin bodies and activates no calls.

Builtin occupancy alone cannot choose argument access. For example, `sort($a[])`
compiles because the first parameter expects a reference; `strlen($a[])` is a
compile error because the first parameter takes a value. The new pure helper
`$pfunction_builtin_ref(name, position)` provides the compiler's positional
`ARG_SHOULD_BE_SENT_BY_REF` predicate, including preferred references and variadic
tails. Positions are one-based. Unknown names and positions without a reference
parameter return false; function existence remains the separate occupancy helper.

The source generator reuses the configured registration/preprocessor inventory
from `generate-builtin-functions.py`. It follows each of the 780 registered
entries to its exact expanded arginfo array across 13 C tables. Every parameter
must match the pinned `_ZEND_ARG_INFO_FLAGS` expansion; unknown layouts fail
instead of becoming assumed value parameters. The source report retains names,
parameter send flags, variadic flags, original arginfo identities and hashes,
all 238 configured input hashes, producer root and raw preprocessing outputs.
Aliases consume the arginfo attached to their actual registration entries.

The source authority is the pinned `vendor/php-src/Zend/zend_compile.h`
(`zend_check_arg_send_type`, `ARG_SHOULD_BE_SENT_BY_REF`), `zend_API.h`
(`_ZEND_ARG_INFO_FLAGS`) and the generated arginfo/function-entry tables under
that same dependency. Required-reference and prefer-reference both select
writable compilation for variable arguments. Extra arguments use the variadic
parameter flag when present; otherwise they use value compilation.

The generator never executes PHP. The separate test enumerates native Reflection
metadata as a differential oracle, checks the exact runtime identity and all
780 signatures, and executes 7,508 pure SpecTec flag assertions including case
folding and extra positions. This check does not delegate program evaluation.
The test loads only the syntax/byte/type prerequisites and the generated table.

Regenerate using `python3 scripts/generate-builtin-argument-modes.py`; use
`--check` for read-only comparison with the configured source. Run
`python3 tests/semantics/builtin_argument_modes.py` for the focused metadata and
pure-specification gate. Disabling or dynamically registering functions belongs
to later explicit configuration transitions; this table does not claim them.
