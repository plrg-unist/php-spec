# Dynamic source foundation

Target: pinned PHP 8.5.10 CLI NTS64. The checked foreign parser service
accepts raw eval bytes and returns a versioned AST or a separate parser
rejection. Its stateless adapter check establishes shape and request identity;
the runtime must still issue and consume a trusted request from a paused state.

`$compile_source_append` registers a fresh nonzero unit and requires one
matching `SOURCEFILE`, including agreement with the compiler's unit and file
fields. It uses the existing ordered compiler and constant-pool installation
without replacing earlier units, pools or code. It restores the caller's task
continuation and leaves its live variable table, request and owned state in
place. The caller of this helper must later install the new unit's work inside
an eval continuation; the helper alone does not execute it.

Compiler warnings in new units and runtime warnings under a new source origin
carry the unit ID to the observer. Direct static failures and early-declaration
fatals retain that source identity as their terminal origin. Unit 0 keeps its
existing event and terminal representation. The focused registry fixture uses
checked file-mode ASTs for successful and direct-static units. Its namespace
branch composes two separately checked AST nodes only to exercise an internal
compiler failure path; the parser rejects those combined original bytes.
The [foundation ledger](../../coverage/semantics/dynamic-source-foundation.json)
binds the checked-unit fixture, unchanged main-source traces and pinned native
duplicate-declaration probes.

The separate [reached eval increment](DYNAMIC-EVAL.md) builds on this
compiler/registry foundation. Include/require and once identity still require
separate source-provider increments; this foundation alone does not execute a
dynamic source.

Selected nonowning positional `defined`/`constant` queries for the exact
`__COMPILER_HALT_OFFSET__` name use the API call site's compiled filename.
The first completed root-terminal HALT unit with no compilation reentry supplies
its offset; later units with that filename cannot replace it. Direct constant
reads still fold the current AST's offset, so repeated eval can return different
runtime and direct values. A fixed builtin `defined` with one raw string literal
and no namespace fallback follows Zend's ordinary-table quick check and returns
false, even in a HALT file.
A fixed compiled-global `defined($name)` with one ordinary CV argument carrying
the exact HALT name instead calls the builtin lookup. Its captured string may be
plain or an authenticated carrier; the result is true for a completed HALT in
the call site's filename and false when that filename has no registration.
The [CV-defined ledger](../../coverage/semantics/halt-defined-cv-review.json)
records the literal/CV contrast, child and eval isolation, and reached call
fronts.

The existing authenticated declaration journal supplies chronology. Accepted
HALT occurrences outside the canonical root shape, or earlier incomplete/failed
or reentrant HALT compilations, yield `Unsupported`; completion is sufficient
evidence here, not a claim that registration always waits for compilation to end.
Genuine parser rejection contributes no registration. Captured query strings and
selected-call receipts retain the existing structural variable-input policy.
An authenticated absent registration for the call site's filename raises the
ordinary `Error` for a nonowning positional call through a selected `constant`
callable with `'__COMPILER_HALT_OFFSET__'` as its argument. The Error has its
`constant` frame and original argument. An included
file's registration does not supply the caller's lookup; a main-file
registration does not supply an eval unit's lookup. The
[absent-lookup ledger](../../coverage/semantics/halt-absent-review.json) records
four native/model source agreements and three reached-state checks. Incomplete
or ambiguous registration remains `Unsupported`.
A fixed call with compiled global name `constant`, no namespace fallback and one
raw `'__COMPILER_HALT_OFFSET__'` string argument now uses the same filename-local
offset or absent-registration `Error`. The
[fixed-call ledger](../../coverage/semantics/halt-fixed-review.json) records four
new exact source agreements and reached main/include/eval call fronts. A bare
`constant` call in an ordinary namespace also uses that path when its compiled
primary name has no user-function target and its compiled fallback is global
`constant`. The
namespaced user function takes priority when present. The
[namespace-call ledger](../../coverage/semantics/halt-namespace-review.json)
records main/child filename isolation, the absent Error and its trace, and
three reached fallback fronts. A fixed compiled-global `constant($name)` with
one ordinary CV argument carrying the exact HALT name also uses the
filename-local offset or absent-registration Error. Its captured string can be
plain or an authenticated carrier; the Error trace retains the argument. The
[CV-constant ledger](../../coverage/semantics/halt-constant-cv-review.json)
records main, child and eval source isolation and reached call fronts. A direct
fixed compiled-global call with one raw `name:` argument containing the exact
HALT string also follows that filename-local lookup. The named slot is
authenticated by the existing CONFIG call shape; an unknown name fails during
argument binding before HALT lookup. The
[named-call ledger](../../coverage/semantics/halt-named-review.json) records the
positive and absent sources, original Error trace and wrong-name control. A
single unpack of a source-authenticated singleton array literal also admits the
exact HALT string with either positional key `0` or named key `name`. The
compiled array value and completed pack receipt must agree; wrong or duplicate
named arguments fail during binding before the lookup. The
[literal-pack ledger](../../coverage/semantics/halt-pack-review.json) records
filename-local results, Error traces and the unpack boundaries. An ordinary
variable expression holding a singleton array may also supply key `0` or
`name`: its live array identity must equal the completed pack's array. A direct
item uses its captured HALT string; a reference-backed item uses the current
value of the array's retained cell, which can survive rebinding or unsetting
the original variable name. The captured pack item and sent argument must
match that value. COW separation, key changes and two calls at one compiled
site use the corresponding live array and fresh receipt. The
[CV-pack ledger](../../coverage/semantics/halt-cv-pack-review.json) and
[alias-pack ledger](../../coverage/semantics/halt-alias-pack-review.json) record
the separate source and reached checks. Other fixed argument shapes, selected
or owning packed calls, multiple, multi-item or Traversable packs, indirect
array leaves, general call-site cache history and ambiguous HALT registration
remain partial. The
[lookup ledger](../../coverage/semantics/halt-lookup-review.json) binds two original
sources and their reached state checks, keeping counterfactual history/source
projections separate from execution.

## File preambles and tick plans

The checked file parser retains a CLI shebang as `ENCODEDPROGRAM` metadata. The
tick planner now reads that program's checked statements, including lexical
`declare(ticks=1)`, just as it does for `PROGRAM`. A shebang is suppressed from
output but advances `__LINE__`. Included shebang files use their opened path
for `__FILE__`, return to the caller, and keep their own tick plan. A leading
BOM takes the existing `PROGRAM` route with an `InlineHTML` node that emits its
raw bytes; it is an affected control, not a new encoded-program rule. Eval uses
its separate parser mode: a BOM raises `ParseError`, while a hash-prefixed line
is a comment and advances the eval line.

Seven [preamble source cases](../../tests/semantics/source_preamble_sources.py)
compare exact pinned-native streams and statuses, including finite-provider
include and an encoded tick include. The [reached fixture](../../tests/semantics/source_preamble_state.py)
checks the actual file-mode AST shapes and source-line tick markers. The
[review ledger](../../coverage/semantics/source-preamble-tick-review.json)
keeps earlier failed harness attempts separate. The COMP163 cut did not admit a HALT
payload combined with a preamble; wider encodings and file-provider forms
remain partial.

## Raw shebang HALT offsets

A checked file with a raw shebang keeps the preamble in `ENCODEDPROGRAM` and
retains the terminal `HaltCompiler` node's original end-file byte position.
For the raw/raw, BOM-free, nonempty-preamble shape with no alternate original
buffer, the source compiler now uses that position plus one as
`__COMPILER_HALT_OFFSET__`. The offset includes shebang bytes. Main and included
units each use their own file identity and filename-local HALT registration;
direct reads and selected `defined`/`constant` CV queries use the existing
lookup routes. Plain and BOM files continue through `PROGRAM`.

The [HALT preamble sources](../../tests/semantics/halt_preamble_sources.py)
compare six exact pinned-native streams, including an included child return.
The [reached fixture](../../tests/semantics/halt_preamble_state.py) checks the
file-mode AST offsets and rejects altered encoding metadata. The
[review ledger](../../coverage/semantics/halt-preamble-review.json) preserves
the original file-mode refusal and later unrelated builtin refusal. Converted
encodings, BOM metadata and other HALT/preamble combinations remain outside
this bounded offset rule.

## Encoding declarations

With Zend multibyte disabled, each parser-literal `encoding` item produces a
Warning128 before compilation. Checked declarations may contain mixed or repeated
directives, integer/float/string literals or literal concatenation, multiline
headers and ordinary bodies. The foreign token stream supplies
`declareHeaderCloseLine` and `declareHeaderCloseTokenPos`; semantic guards check
unique fields and statement/item/body ranges. Parser warnings use the closing
line, while compiler diagnostics retain the first item's line.

Warning order follows header-close tokens, then item tokens within each header.
This covers anonymous-class arguments before method bodies and a declaration
inside another header's closure value before the enclosing header reduces.
Repeated encoding items share the header position without sharing their item
key. Missing, partial, duplicated or inconsistent receipts refuse explicitly.
Receipt-less legacy ASTs retain the old single-line route only when both new
fields are absent. Checked integers are explicit lexical input facts, not proof
that edited metadata came from original source bytes.

Compilation processes the directives and body in order. An encoding declaration
after a non-declare statement, or inside a namespace or block, raises the
first-statement fatal after the complete parser-warning prefix. A preceding
declare body does not prevent another root encoding declaration. A successful
encoding directive has no runtime effect; its body executes through ordinary
source work, including returns from included and eval units. Mixed strict/tick
directives retain their existing rules and are disjoint from encoding-free
runtime declarations.

Comment-only bodies can contain a synthetic `NStmtNop` whose start token is one
past its end token. The range guard admits that empty span only for Nops, keeping
both endpoints after the header and inside the declaration. Ordinary inverted
statement spans remain Unsupported.

Five [source cases](../../tests/semantics/encoding_placement_sources.py) compare
exact pinned-native diagnostics, exits and source identities. The
[checked-AST fixture](../../tests/semantics/encoding_placement_state.py)
authenticates late and nested occurrence paths and rejects a missing parent
occurrence. The [review ledger](../../coverage/semantics/encoding-placement-review.json)
preserves earlier failed checks. The
[list/body sources](../../tests/semantics/encoding_list_sources.py),
[compiler/body fixture](../../tests/semantics/encoding_list_state.py) and
[independent dynamic fixture](../../tests/semantics/encoding_list_dynamic_state.py)
cover recursive warning order, compiler precedence, body scheduling, origin
guards, budget resume and dynamic return values. Their
[review ledger](../../coverage/semantics/encoding-list-review.json) retains exact
tested cuts and earlier failures. The
[header sources](../../tests/semantics/encoding_header_sources.py),
[compiler fixture](../../tests/semantics/encoding_header_state.py) and
[independent reached fixture](../../tests/semantics/encoding_header_review_state.py)
extend these checks to multiline headers, nested reductions and dynamic source
identity. The [header ledger](../../coverage/semantics/encoding-header-review.json)
binds those results and the fresh syntax/metadata gates.

Rejected eval/file replies can separately carry completed header reductions:
declaration start/close positions and checked `DeclareItem` lists. The foreign
PHP-Parser hook records a complete header before its body; it can therefore retain
an inner reduction even when an outer header or body never completes. Authored
rules check ordered close positions, item/name/value spans and source identity,
then emit the encoding-literal prefix. A nonliteral encoding stops that header's
remaining items and all later reductions, after already completed nested headers.
The compiler never receives a partial program; earlier unknown/strict directives
contribute no compiler diagnostics when parsing fails.

Warning128 uses the current reporting/display state and bypasses error handlers.
The subsequent catchable ParseError/CompileError retains a failed-source record
and file entry without an accepted source/code/binding. Its lifecycle handle is
installed before a zero-budget continuation can expose the new Throwable.
Failed once parses remain once hits; ordinary reinclusion parses a fresh unit.
The [originals](../../tests/semantics/rejected_encoding_sources.py),
[prefix/once fixture](../../tests/semantics/rejected_encoding_state.py) and
[independent fixture](../../tests/semantics/rejected_header_review_state.py)
passed 22 exact comparisons, one separate refusal and 214/375 SL conditions at
the COMP168 cut.
The [review](../../coverage/semantics/encoding-rejection-review.json) retains their
actual cuts and failures.

For rejected sources, foreign lexing now collects bad-character/comment errors
before grammar reduction. The earliest reported byte position must equal a real
token boundary. The parser receives the preceding tokens and an EOF marker at
that same ordinal, then uses its throwing handler: an earlier syntax error still
prevents all later reductions. This retains completed and nested headers without
certifying incomplete headers, scanning raw bytes or recovering beyond a fault.
Control bytes inside strings/comments remain ordinary tokens. Accepted parsing,
the header receipt schema and authored runtime rules are unchanged.

The [lexical originals](../../tests/semantics/lexical_header_sources.py) pass
32 exact eval/file comparisons; [independent controls](../../tests/lexical_header_service_review.py)
cover EOF/lookahead, malformed/reversed boundaries and mode-specific scanner
behavior. The former comment-preemption control is now an agreement; three
selected legacy sources and 220 reached conditions pass. Their
[review](../../coverage/semantics/encoding-lexical-review.json) keeps the actual
cuts and earlier fixture failure. Errors not reported by that foreign lexer
still use exact prefix admission; differing native/foreign prefixes refuse.
Multibyte conversion and wider source behavior remain partial.

When the existing main parser rejects a file, the semantic CLI can obtain its
rejection from the same checked file service. Accepted main parsing is unchanged.
Authored module 446 validates unit 0, source bytes and the existing header receipt,
emits its literal warning prefix, then reports the main ParseError or CompileError.
Warning 128, Parse 4 and Compile 64 have independent startup masks. Display 0 suppresses
events; stdout display prepends a newline to each event. The exit status is 255,
even with zero VM steps. Earlier echo, unknown-declare and strict-type statements
neither execute nor contribute compiler diagnostics after parsing fails.

This result is terminal before `PROGRAM` installation: `FILES` names unit 0, while
sources, code, declaration history, user objects and tasks remain empty. It is
checked against startup/display/precision, file, destruction and heap predicates.
It is not a resumable installed VM state: existing publication-history guards
continue to reject entry through `$drive`. No placeholder program or `PDENTER`
record is invented. The original fixture's positive VM-history expectation failed
and remains preserved; its correction explicitly checks refusal instead.

The [main originals](../../tests/semantics/main_rejected_sources.py) pass 37 exact
profiles from 15 byte-identical native sources, including repeated/nested headers,
lexical faults, masks, stdout display and BOM/CRLF positions. Independent
[service](../../tests/main_rejected_source_review.py) and
[terminal-state](../../tests/semantics/main_rejected_review_state.py) checks cover
filename/source identity, typed malformed receipts, empty compilation state and
VM reentry refusal. Their 28 controls and 240 SL conditions pass, as do two retained
accepted include/eval sources. The [review](../../coverage/semantics/main-source-rejection-review.json)
retains actual cuts, the original failure and remaining profile limits.
