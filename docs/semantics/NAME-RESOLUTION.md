# Checked non-class lexical names

`22-name-resolution.watsup` resolves constant and function names in an explicit
`plenv` produced by the ordered namespace/import traversal. It retains the exact
checked name, including qualification and metadata, in `ORIGINAL`; it returns
resolved byte names, the compiler's `FULL` flag and an optional global fallback
name. It performs no symbol lookup, autoload, invocation or declaration publication.

`$pnresolve(environment, kind, name)` accepts `PLCONSTANT` or `PLFUNCTION` and
returns `PNRESOLVED reference`. Class resolution and edited invalid names return
`PNUNSUPPORTED`; class type resolution still belongs to its existing scope-aware
helpers. The lexical environment is an internal compiler context whose import
tables have already been validated and keyed by `21-source-context.watsup`.

Fully qualified names retain their bytes and set `FULL`. Namespace-relative names
are prefixed by the current namespace and also set `FULL`. Plain constant aliases
use exact-case keys, while function aliases use ASCII lowercase keys. An alias
from the relevant table sets `FULL` even if its target has no namespace separator.
For a compound name, only the class/namespace import table can replace its first
segment. Function and constant aliases do not replace compound-name prefixes.
Qualified names always set `FULL`, with or without an imported prefix.

An ordinary unqualified name in a namespace retains a namespace-prefixed resolved
name, `FULL false`, and its original unqualified bytes as `FALLBACK`. A global
unqualified name also has `FULL false`, but needs no redundant fallback. Import
reset across namespace blocks follows the existing lexical traversal. These are
compiler lookup instructions, not claims that either candidate exists.

The source is pinned PHP 8.5.10 `Zend/zend_compile.c:1073`
(`zend_resolve_non_class_name`). The later `zend_try_ct_eval_const` at line1671
uses `FULL` to recognize unqualified namespace `true`, `false` and `null` before
ordinary lookup. A namespaced unqualified `NAN` can instead require runtime global
fallback. The resolver does not fold either case or infer success merely because
`FALLBACK` is present. Integration into constant evaluation and ordinary compilation
must preserve this distinction. Original names remain available for diagnostics
and source-specific exceptions such as `__COMPILER_HALT_OFFSET__`.

Run `python3 tests/semantics/name_resolution.py`. Original source programs use
namespace/import prefixes followed by a constant or function name. The helper
obtains the exact environment from the first ordinary-work barrier and resolves
the checked name from that statement. Native undefined-name diagnostics establish
the resolved byte names; successful builtin and special-constant controls observe
fallback and qualification behavior. `FULL` and fallback fields are also checked
against the pinned source algorithm; an undefined-name observation alone cannot
prove which lookup attempts occurred. Reports retain original source bytes,
checked AST hashes, exact commands, profile, status and both raw output channels.

The ordered compiler and constant-expression prepass now consume these descriptors.
`23-named-constants.watsup` keeps compile-time substitution separate from runtime
fallback. The byte-keyed backend in `20-machine.watsup` contains one set of modeled
startup values; its wire-text wrapper decodes into that same lookup. The generated
`15-constant-names.watsup` remains a names-only startup table and distinguishes
existing unmodeled constants from missing names. Existing unmodeled constants
produce Unsupported, while genuinely absent names can try the explicit fallback.
Runtime lookup uses resolved bytes for an eventual undefined-constant message.
The anchors are `zend_compile_const` at11014 and `_zend_quick_get_constant` in
`Zend/zend_execute.c` at5411, including its separation from special-constant
substitution.

Run `python3 tests/semantics/namespace_constants.py` for original-source native/runtime
comparisons and compiler descriptor assertions: imported names, class prefixes,
case distinctions, namespace resets, raw bytes, exact diagnostic lines, partial
array folds and lexical cache reuse. These checks include namespaced `NAN` remaining
a nonconstant fetch while a `use const NAN` alias folds. `FULL` is not a promise
that a symbol exists. Function invocation, user constant declarations, autoload,
class constant access and magic source constants remain separate pending work.
