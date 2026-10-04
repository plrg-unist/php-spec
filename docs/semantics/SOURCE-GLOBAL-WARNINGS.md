# Missing global fetches and full-table snapshots

Module226 dispatches warnings for direct `$GLOBALS[key]` R-fetches through the
actual global table. The name is evaluated before dispatch and the interrupted
fetch still produces null when a handler defines or rebinds that entry. Handler
locals do not become global entries. Literal/compiled names and source/key lines
are authenticated; dynamic name bytes are captured runtime facts, not values
reconstructed from the mutated key expression.

Zend completes this FETCH_R before its consumer. A throwing handler therefore
skips the later assignment or send and preserves the original exception and
previous chain. This differs from the missing-CV ASSIGN continuation213/220,
which writes null and can replace the handler exception at a rejecting typed
alias. Unknown or duplicate named slots follow the eager global fetch; ordinary
missing-CV sends retain their existing opposite warning priority. Quiet accesses
and reference acquisition of selected names keep the existing real-cell paths.
Earlier key evaluation can still warn; [module233](SOURCE-DIMENSION-KEYS.md) stages
undefined key CVs and global-array-name conversion before this lookup. GLOBALS
rereads a missing key in the caller environment after that earlier warning.

Whole `$GLOBALS` values use the existing76 genuine table snapshot under explicit
request facts. The snapshot omits undefined entries and callback locals, converts
numeric string keys, unwraps singleton references and preserves shared cells.
Array COW separates ordinary values while embedded references keep their real
owners after global bindings retire. Permanent compiled pools remain owners of
folded array literals. The request provider supplies only environment, argv,
configuration and clock inputs; it does not supply PHP global values.

Author eight source comparisons and 68/65/74=207 state checks pass with unchanged
production across fixture corrections. Independent eight sources and 66/72/83=221
checks pass at f947. Two derived sources on accepted ed6 preserve the private
handler, Child called class, eager identity read, typed alias and original previous
chain. The original combined observer retains an inconclusive CLI60 timeout.
Distinct cutoffs and raw tuples are in the [ledger](../../coverage/semantics/global-warning-reads-review.json).
The original unsupported count observer, request-notation failures and pool-owner
premise failure remain preserved. Only affected/unrun checks were executed.

In a built project root, reproduce the maintained cases with:

```sh
python3 -B tests/semantics/globals_warning_prepare.py
python3 -B tests/semantics/globals_warning_run.py .tools/globals-warning/PREPARED/report.json
```

Use the preparation path printed by the first command. Records retain original
native/model tuples, request facts, limits and revision. Existing tools are reused;
this establishes no fresh offline rebuild or full-family closure. Whole-table
snapshots without explicit request facts remain Unsupported. Module233 separately
accepts missing key-CV, array-name and ordinary null/float conversion callbacks,
including nested/quiet reads. Read-write continuations, wider object/key/container
producers and broader reference-result consumers remain required; paused returns
are separate.
