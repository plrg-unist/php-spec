# Fibers

Module 281 models live PHP 8.5.10 Fibers: constructor selection, direct
`start`, `suspend`, `resume`, `throw`, status, `getCurrent` and `getReturn`.
The first milestone covers existing declared nongenerator user callbacks with
by-value parameters. Selection is cached when the constructor receives its callback;
later changes to a referenced method name do not select another function.
Callable validation precedes the repeated-constructor status error. Callback
receive is weak because the Fiber enters through an internal call.

The model moves each VM continuation, local symbol table, frames, scratch owners
and live reporting mask. Heap storage, references, globals, handler registries,
INI and allocation counters remain shared. A saved main continuation does not
copy the shared global symbol table. Fresh callbacks take their reporting mask
from current INI; resumed callbacks restore their saved live mask. Nested waiting
Fibers remain running and cannot be resumed as suspended Fibers.

The raw constructor callback has its genuine function-name owner. Cached target,
permission and dynamic-construction certificates own nothing. Suspended tasks,
locals and saved frames retain their actual values. Waiting C API frames retain
their receiver and original `start`/`resume`/`throw` arguments. A parked static
`suspend` continuation retains its original argument without a Fiber self-owner.
The stored return value remains owned by the terminated Fiber; later array writes
from `getReturn` use ordinary copy-on-write and reference rules.

Each activation by `start`, `resume` or `throw` consumes a fresh global stamp;
`suspend` and terminal transfers back to the caller retain that activation stamp.
Admission checks the active caller chain, each saved stack and exact
source/task/function/line/argument metadata. Mapped `start` slots authenticate C
callback named preflight with a null callsite. Dynamic `new $class` retains only
its authenticated nonowning birth certificate after its temporary construction
marker retires. Termination clears callback/cache/continuation data. Caught
injection keeps the exact Throwable; uncaught callback exceptions cross the Fiber
root once. Traces include waiting Fiber API frames and their original buffers.
Callback name errors arise before a callback frame exists; their file and line
come from the waiting `Fiber::start` caller, and the failed Fiber terminates.
Global Generator ownership is checked on the actual machine. Parked Fiber views
retain their own task/frame checks and exclude active Generator resume markers;
an unrelated Generator can run while a Fiber remains suspended.

The primary engine routes are `Zend/zend_fibers.c`: VM capture/restore 123–155,
fresh entry 567–636, transfer 639–711, constructor 872–893, APIs 895–1098 and
object destruction 769–816.

## Validation

`tests/semantics/fiber_review.py` preserves original bytes, native/profile
identity and exact native/model streams. `fiber_state_review.py` seeks real
source states in production SL mode and checks continuation ownership, malformed
records, budget resumption and completion. Raw reports stay in ignored `.tools`.
No engine divergence or portability claim is made by these focused results.
Thirty normal originals, three zero-agreement Unsupported controls and thirteen
source-derived states/782 conditions retain the mixed cuts below.

| Checks | Accepted cut and raw report |
| --- | --- |
| First two original sources | `466ba2ba6` with recorded working-tree corrections, `fiber-review-9m0ul0ob` |
| Remaining sources: 23 normal agreements | `6fbdfdc25`, `fiber-review-xfvffr3u` |
| Affected nested source: allocated Fiber argument | `f6c30c7f6`, `fiber-review-caky5lmf` |
| Deferred/literal named holes and entry-error provenance: two normal originals | `29f6ba481`, `fiber-review-c9g38gpt` |
| Four independent states, 166 conditions | `d515fd003`, `fiber-state-review-m4i2tuy4` passing rows only |
| Three corrected independent states, 149 conditions | `d515fd003` with fixture corrections published in `c18091bdd`; `fiber-state-review-ssrq4m18` dynamic row and `fiber-state-review-znwx84k9` |
| Affected nested preflight state, 56 conditions | `6e053c12c`, `fiber-state-review-i4_ozv12` |
| Reporting/INI and parked-handler states, 137 conditions | `949d94782`, `fiber-state-review-_egc0_sx` |
| Named-default and entry-error states, 172 conditions | `6dc7900c4`, `fiber-state-review-8tppvo5a` |
| Actual constant-NEW identity transfer and separate running Generator: two normal originals | `5b720fd10`, `fiber-review-yxlc_qs5` |
| Autoload and active-Generator helper transfer controls: no agreement | `5b720fd10`, `fiber-review-yxlc_qs5` |
| Separate running Generator with parked Fiber, 102 conditions | `5e81060c6`, `fiber-state-review-1pzg3rap` |
| Module AL checks | `ae3c73e1d`, `fiber-al-hmn8wukf`, 264 modules; entry-error cut `29f6ba481`, `fiber-al-n_s2keum`; prior preflight cut `6e053c12c`, `fiber-al-csrau3ee` |
| Actual-parent AL checks, 271 modules | `07c427f3e`, `fiber-al-wvfym0ir`, preserving accepted `0e1252529`; prior interaction cut `5b720fd10`, `fiber-al-nu57_5eg` |

Sources use 100000 steps, 60 seconds per model and a 75-second process cap;
state checks use 4000-step seek/resume budgets and 120 seconds per case. Runs are
serial. The profile uses PHP 8.5.10 CLI NTS 64-bit with `LC_ALL=C`, `TZ=UTC`;
commands, exits, exact working-tree inputs and executed binary hashes are in each
report. Native preparation uses a 75-second subprocess cap. Reproduce selected
cases with repeated `--case`
arguments; `--native-report` reuses exact matching native originals.

Original compiler failures, the source dispatch failures in
`fiber-review-mslnabzj`, `fiber-review-fhy6k1o_`, `fiber-review-u0pcirvf` and
`fiber-review-hkzhd_y9`, and unsuccessful state rows retain zero credit. The
initial nested source/state failures remain in `fiber-review-xfvffr3u` and
`fiber-state-review-m4i2tuy4`; their affected successful checks above replace only
those rows. The two named continuation checks first rejected full admission in
`fiber-state-review-zfq15mg_`: their saved `start` buffer guard lost the optional
argument-name type. The affected checks above validate the corrected correlation,
including changed or missing raw names. That failure and the fixture parse failure
in `fiber-state-review-07w9vwmt` retain zero credit and their original raw inputs.
The named-default original using ordinary `define()` remains an explicit builtin
body boundary in `fiber-review-igz0sgwl`, with no Fiber events or agreement.
The const-initialized original's first failure in `fiber-review-62uis9p4`
preserves its successful default prefix and the missing-line error-path stop.
The affected successful original above keeps that earlier failure at zero credit.

## Required follow-ons

Force-close and request/fatal cleanup, deprecated constructor callable stages,
core internal callback bodies, reference forwarding, API callable/FCC entry,
`start` unpacking and switching during initialization/source loading remain
required. The first transfer domain rejects active or saved constant/default and
autoload initialization, and active Generator execution, including switches in
their helper calls. Their shared pending flags and parked ownership remain
required consumers. Actual late Fiber-shutdown/frameless switching restrictions need
their own stages; ordinary registered shutdown callbacks and destructors are not
blanket blocked at this pin. Property and broader object consumers remain tracked
separately. Full core and paused return verification are not closed by this cut.
