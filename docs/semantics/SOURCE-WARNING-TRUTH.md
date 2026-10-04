# Warning callbacks and truth decisions

Module209 resumes source-certified missing-CV decisions with the original null,
even when an error handler defines the same variable. It covers `if`/`elseif`,
`while`/`do`/`for`, both Boolean and keyword short-circuit operators, Boolean NOT,
and full/shorthand ternary conditions. It retains the genuine consumer, source,
line and saved caller; it does not evaluate the source expression again.

Short-circuit AND skips its right operand after the original false read; OR
still evaluates its right operand. A thrown callback prevents the decision,
branch, right operand or destination assignment. Folded Boolean redirects keep
the checked expression origin through conversion and restore their prior origin
afterward. In the ordinary profile, BOOL/BOOL_NOT use temporary results before a
separate assignment, so callbacks observe an undefined destination before that
assignment overwrites their mutation.

The pinned sources are `JMPZ`, `JMPNZ`, `JMPZ_EX`, `JMPNZ_EX`, `JMP_SET`, `BOOL`
and `BOOL_NOT` in `vendor/php-src/Zend/zend_vm_def.h`, the undefined-CV helpers in
`Zend/zend_execute.c`, and assignment/short-circuit compilation in
`Zend/zend_compile.c`. Private author evidence is mixed: six normal tuples at `1e8e9131` plus two
normal tuples and the separate cast Unsupported control at `1a358f6a`, with
four225 state assertions. The original overlapping-certificate interpreter
failure remains preserved. Independent model3/three160 passes retain native
originals; a phase-name recording collision required only the branch model's
raw recording to be recovered. No full fresh source campaign is claimed. Original
checked fixtures/AL retain explicit generation/current-execution provenance.
The [ledger](../../coverage/semantics/warning-truth-review.json) locates originals.

The PIPE composition at `0d88103d` preserves installed held operands and static
references. Its normal source1/69 passes original-null ternary selection while
the handler defines the same main CV, drops the source object and changes raw
INI bytes. An independent throwing callback passes its original source tuple
and corrected96 state checks; the original wrong INSTANCE premise is retained.
These gates use finite-v2 with explicit include_path `.:`, separate from ordinary13.

The current constants composition preserves accepted183/184 caches and unwind
hooks. At `8c74e624`, author source1/95 passes cache publication, copy separation and
original-null branch choice. Independent source1/89 checks cache survival across
throw, the unchanged destination and restored raw handler. Each gate retains its
full original tuple and process records. The preserved `823be298` projection
composes the disjoint current201 discarded-getter fix without a gate replay.

Cast, selected-arm copy, SEND, other warning producers and broader reporting
remain separate obligations. Paused return validation is not part of this slice.
Eligible producers outside the admitted continuations stay `Unsupported`.
No-handler or mask-miss reads retain ordinary default reporting.

With built local tools, prepare then run the actual generated report:

```sh
python3 -B tests/semantics/warning_truth_prepare.py
python3 -B tests/semantics/warning_truth_run.py .tools/warning-truth/PREPARED/report.json
```

The fixed selection uses ordinary13, serial native45s/model90s/finite300s limits
and 1260s/1230s phase limits. Original streams, exits and owned cleanup stay outside
Git. Tools are reused; fresh combined offline rebuild and complete core are open.

For the affected current PIPE interaction only:

```sh
python3 -B tests/semantics/warning_truth_pipe_prepare.py
python3 -B tests/semantics/warning_truth_pipe_run.py .tools/warning-truth-pipe/PREPARED/report.json
```

This selection is source1/state1, with 150s/330s phase limits and unchanged
45s/90s/300s producer limits. Source-equivalent publication adds no fresh execution.

For the current deferred-array cache/COW interaction only:

```sh
python3 -B tests/semantics/warning_truth_constant_prepare.py
python3 -B tests/semantics/warning_truth_constant_run.py .tools/warning-truth-pipe/PREPARED/report.json
```

This fixed selection uses one source and one95 fixture with the same finite-v2
profile and150s/330s phases. These commands require the project-local regular
compiler at `.tools/spectec/bin/p4spectec`; `scripts/build-deps.sh` provisions it.
The recorded gates reused that binary and establish no new offline rebuild.

The tested211 composition at `38cab574` adds an inherited array handler
normal path and an inherited string-handler throw. The original null still
chooses the false branch after live mutation; a thrown handler preserves the
old folded-BOOL assignment destination and restores its raw registration. The
author source1/93 passes with its original tuple and process records. Independent
source1/107 checks an inherited class-string handler selected from a strict instance
emitter: reception rejects the warning integer before its string-typed parameter
body runs, suppresses the destination assignment and restores the raw handler.
Genuine receiver, called-class, saved consumer and header controls retain the
actual emitting frame. Both gates keep their original results at `38cab574`;
source-equivalent publication adds no fresh execution credit.

For this current method-handler interaction only:

```sh
python3 -B tests/semantics/warning_truth_handler_prepare.py
python3 -B tests/semantics/warning_truth_handler_run.py .tools/warning-truth-pipe/PREPARED/report.json
```

This is one source and one93 fixture under the same finite-v2 profile and
150s/330s phases. Each earlier gate keeps its actual tested revision.
