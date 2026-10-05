# Global W/RW warning continuations

Module269 extends242's direct `$GLOBALS[key]` reference fetches to W/RW name
selection and missing-entry continuations for updates, compound assignment and
nested ordinary-array ingress. Global names use string conversion, separately
from ordinary array-key conversion: a missing key CV warns then rereads the
actual caller CV; an array key warns then retains the captured name `Array`.
Null and float global names do not use ordinary array-key deprecations.

A returning missing-global warning initializes a fresh null binding before the
consumer. Callback-created reference aliases, including constrained static cells
and cells captured by reentry, are detached rather than overwritten through their
constraints. The interrupted increment/compound operation then uses the new
binding. A throwing handler skips this initialization and the later RHS demand,
preserving callback writes, real aliases and the original previous chain.
Ordinary execution needs no explicit request facts for this binding operation.

Direct and nested GLOBALS compound walks follow any eager RHS computation.
Computed names are retained while CV names remain live. A simple RHS CV is
demanded after successful RW acquisition, so a missing-global handler can define
it first; a throwing handler leaves it unread. Nested ordinary-array conversion
retains242's separation/protection and acquisition rules. A moved keeper can keep
the selected table and embedded typed cells live; replacing that table can abort
the acquisition without writing into the new table.

Source/consumer, mode, compiled constant name, operand forms and opcode lines are
checked. Multiline direct compound operations distinguish the enclosing operation
line from the global-name fetch line. Consistent dynamic names, selected values
and borrowed places remain runtime facts, without invented callback history or
extra pointer owners. Pinned contracts are `zend_fetch_var_address_helper` and
`zend_compile_compound_assign` in `vendor/php-src/Zend`.

Author9 source agreements include four independent originals. Independent12
retains those four and adds eight fresh agreements:17 distinct private programs.
Author65/86/73=224 and independent69/64/67/73=273 reached assertions pass at their
recorded cuts. One actualc906 source at604958 retains parent-private FCC/Child
called-class selection, fresh-global detachment and live typed caller/static
introspection. The [ledger](../../coverage/semantics/globals-write-review.json)
keeps original native predictions, the multiline Unsupported and its focused line
correction separate from accepted runs.

The catalogue is `tests/semantics/globals_write_cases.py`.
`python3 -B tests/semantics/globals_write_prepare.py [fixture-id ...]` compiles
selected reached fixtures; exact source and AL_mode runner commands remain in the
raw records. Production source execution uses SL_mode and existing local tools;
there is no fresh build or portability claim.

[Container276](SOURCE-CONTAINER-WRITES.md) adds initial undefined/null/false
CV-rooted W/RW storage and final array-reference writes. Wider container/string/
object producers and GLOBALS quiet/memoized/unset consumers remain required core
work. Full-table snapshots without request facts and paused return verification
retain their separate boundaries; selected agreement does not establish complete
core semantics.
