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

This is an unregistered lexical helper. Its consumers in constant evaluation,
ordinary compilation and source runtime lookup remain pending. It does not remove
those consumers' current explicit namespace/import boundaries.
