# Parameter source phase prerequisite

PHP-Parser now transports variadic parameters with defaults and `void` parameters
through the checked syntax pipeline. The existing source compiler rejects these
declarations in native parameter order. Previously, PHP-Parser's eager
`checkParam` restrictions returned a frontend failure before source compilation
could select the correct diagnostic.

The patch removes only those two checks, preserving the method and its callers.
Existing compiler17/16/90 handles defaults, final variadic position, repeated
names and type diagnostics. No semantic module, source metadata, schema or
runtime implementation changes. The two corresponding entries in
`tests/phase-discrepancies.json` are retired; maintained signature tests now
exercise their source forms as well as the retained edited-AST controls.

Fourteen retained originals cover literal/constant defaults, multiline
declarations, body errors, same/later-slot `void`, nonfinal variadics, repeated
names and earlier invalid defaults. Thirteen agree with pinned native execution
(twelve static rejections and one normal fixed-parameter call); a syntactically
valid variadic declaration remains explicitly Unsupported at this prerequisite.
All fourteen pass checked elaborated reconstruction, printing and parser
roundtrip, with the same public CLI outcomes. The maintained signature gate
passes 359 comparisons, 28 descriptor checks and 174 reference-return checks.

The [originals manifest](../../coverage/semantics/parameter-phase-originals.json)
binds complete accepted951/c650 and candidate951/440f input maps, source
requests, native/parser/lint output, worker packets and closures, public CLI
streams and the maintained signature gate's subprocesses. Exactly three watched
paths change and all modes remain equal. The signature harness explicitly
reuses the unchanged accepted numeric runner; its build command was not rerun.
Executable tools are bound by hash and mode. Patch and provenance files are also
retained although outside the watched semantic input map.

Applying the complete handwritten patch with zero fuzz to the unchanged pinned
upstream distribution reproduces all five patched files. The pinned local
grammar generator reproduces the checked-in PHP8 parser exactly. Upstream
source, archive pins and unrelated parser restrictions remain unchanged.

Syntax transport applies globally; the source-static agreement here concerns
the admitted named-function compilation pipeline. Class and closure compilation,
positional variadic execution, named arguments and unpacking remain required
subsequent work. This prerequisite does not activate those consumers.
