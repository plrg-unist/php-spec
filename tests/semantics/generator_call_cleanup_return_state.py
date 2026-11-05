#!/usr/bin/env python3
"""Reach normal owning warning retval cleanup before copied Generator creation."""
import hashlib
import json
from pathlib import Path
import subprocess
import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_call_cleanup_return_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROW = next(r for r in json.loads(INPUT_BYTES[CATALOG])
           if r['id'] == 'i107-fake-owned-warning-return-gen-current')
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']

STAGE = (
    'S.TODO = (ERROR_HANDLER_CLEAN perrorcall) :: ptask_tail* '
    '-- if perrorcall.RESUME = CLOSURE_CALL_COPY_REFERENCE pclosurecall n_copy n_done pnamedargs n_base '
    '-- if n_done = 1 '
    '-- if pclosurecall.FIRST = (POBJECT n_maker) '
    '-- if $object_name(S, n_maker) = $ptascii("MakerReturn107A")')

CHECKS = [line.strip() for line in r'''
S.COMPLETION = NORMAL
S.EXITSTATUS = 0
S.ACTIVEFIBER = eps
S.SOURCEPENDING = eps
S.CLOSURECALLRETAINED = eps
S.CURRENT = eps
S.FRAMES = eps
S.ERRORHANDLER.CALLBACK = eps
S.DESTRUCTION.ABANDONED = eps
S.DESTRUCTION.CALLS = eps
S.DESTRUCTION.OPERATIONS = eps
S.DESTRUCTION.CLEANUPS = pdestructioncleanup :: pdestructioncleanup_tail*
pdestructioncleanup.SOURCE = ERROR_HANDLER_RESULT perrorcall
~pdestructioncleanup.RELEASED
pclosurecall.RAW = [(KINT 1, KNOWN (POBJECT n_prefix)), (KINT 2, KNOWN (POBJECT n_pending))]
pnamedargs.SLOTS = [NAMED_SENT (REFERENCE n_prefix_cell)]
pnamedargs.NAMED = eps
S.STORE[n_prefix_cell] = DEFINED (POBJECT n_prefix)
n_prefix_cell <- S.REFCELLS
S.OBJECTS[n_copy] = BOUNDFAKECLOSURE pboundfake
$closure_call_copy_row(S, n_copy) = (pclosurebinding)
n_source = pclosurebinding.SOURCE
pboundfake.SOURCE = n_source
pclosurebinding.RECEIVER = (n_maker)
$target_receiver(S, CLOSURE_TARGET n_source) = (n_old)
$target_function(S, CLOSURE_TARGET n_copy) = (pfunction)
$function_generator(S, pfunction)
$lookup(S.ENV, $ptascii("source")) = (n_source_cell)
S.STORE[n_source_cell] = DEFINED PNULL
$lookup(S.ENV, $ptascii("weakReturn")) = (n_weak_return_cell)
S.STORE[n_weak_return_cell] = DEFINED (POBJECT n_weak_return)
S.OBJECTS[n_weak_return] = WEAKREFERENCE (n_return)
$weakref_get(S, n_weak_return) = PNULL
$lookup(S.ENV, $ptascii("weakChild")) = (n_weak_child_cell)
S.STORE[n_weak_child_cell] = DEFINED (POBJECT n_weak_child)
S.OBJECTS[n_weak_child] = WEAKREFERENCE (n_child)
$weakref_get(S, n_weak_child) = PNULL
$lookup(S.ENV, $ptascii("weakAfter")) = (n_weak_after_cell)
S.STORE[n_weak_after_cell] = DEFINED (POBJECT n_weak_after)
S.OBJECTS[n_weak_after] = WEAKREFERENCE (n_after)
$weakref_get(S, n_weak_after) = PNULL
$instance_storage_for(S, n_return) = eps
~((HOBJECT n_return) <- S.ALLOCATIONS)
~((HOBJECT n_child) <- S.ALLOCATIONS)
~((HOBJECT n_after) <- S.ALLOCATIONS)
H = $heap_graph(S)
$heap_valid(H)
$call_descriptors_valid(S)
$heap_owners(H, HOBJECT n_copy) = 1
$heap_owners(H, HOBJECT n_source) = 1
$heap_owners(H, HOBJECT n_maker) = 2
$heap_owners(H, HOBJECT n_prefix) = 2
$heap_owners(H, HOBJECT n_pending) = 1
$call_task_valid(S, ERROR_HANDLER_CLEAN perrorcall)
S_bad_cleanup = S[.DESTRUCTION.CLEANUPS = eps]
~$call_task_valid(S_bad_cleanup, ERROR_HANDLER_CLEAN perrorcall)
PhpStep: S ~> S_restored
S_restored.TODO = (CLOSURE_CALL_COPY_REFERENCE pclosurecall n_copy n_done pnamedargs n_base) :: ptask_tail*
S_restored.DESTRUCTION.CLEANUPS = pdestructioncleanup_tail*
S_restored.ERRORHANDLER.CALLBACK = (perrorcall.CALLBACK)
S_restored.CLOSURECALLRETAINED = eps
S_restored.STORE[n_source_cell] = DEFINED PNULL
$closure_call_copy_reference_valid(S_restored, pclosurecall, n_copy, n_done, pnamedargs, n_base)
$call_descriptors_valid(S_restored)
$heap_valid($heap_graph(S_restored))
pnamedargs_bad = pnamedargs[.SLOTS = [NAMED_SENT (REFERENCE n_source_cell)]]
~$closure_call_copy_reference_valid(S_restored, pclosurecall, n_copy, n_done, pnamedargs_bad, n_base)
PhpStep: S_restored ~> S_reference
S_reference.TODO = (CLOSURE_CALL_COPY_FORWARD pclosurecall n_copy 2 pnamedargs_next n_base) :: ptask_tail*
pnamedargs_next.SLOTS = [NAMED_SENT (REFERENCE n_prefix_cell), NAMED_SENT (REFERENCE n_pending_cell)]
pnamedargs_next.NAMED = eps
S_reference.STORE[n_pending_cell] = DEFINED (POBJECT n_pending)
n_pending_cell = |S_restored.STORE|
n_pending_cell =/= n_prefix_cell
n_pending_cell <- S_reference.REFCELLS
(HCELL n_pending_cell) <- S_reference.ALLOCATIONS
S_reference.CLOSURECALLRETAINED = eps
$call_descriptors_valid(S_reference)
$heap_valid($heap_graph(S_reference))
S_pause = $drive(S, 0)
S_pause.COMPLETION = BUDGET
S_pause[.COMPLETION = NORMAL] = S
S_done = $drive(S_pause[.COMPLETION = NORMAL], 4000)
S_done.COMPLETION = NORMAL
S_done.EXITSTATUS = 0
S_done.SHUTDOWN.PHASE = SHUTDOWN_DONE
S_done.TODO = eps
S_done.CURRENT = eps
S_done.FRAMES = eps
S_done.HELD = eps
S_done.CLOSURECALLRETAINED = eps
S_done.DESTRUCTION.CALLS = eps
S_done.DESTRUCTION.OPERATIONS = eps
S_done.DESTRUCTION.CLEANUPS = eps
S_done.DESTRUCTION.RELEASES = eps
S_done.DESTRUCTION.ABANDONED = eps
S_done.ERRORHANDLER.CALLBACK = (perrorcall.CALLBACK)
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
~((HOBJECT n_return) <- S_done.ALLOCATIONS)
~((HOBJECT n_child) <- S_done.ALLOCATIONS)
~((HOBJECT n_after) <- S_done.ALLOCATIONS)
~((HOBJECT n_source) <- S_done.ALLOCATIONS)
~((HOBJECT n_old) <- S_done.ALLOCATIONS)
~((HOBJECT n_maker) <- S_done.ALLOCATIONS)
~((HOBJECT n_prefix) <- S_done.ALLOCATIONS)
~((HOBJECT n_pending) <- S_done.ALLOCATIONS)
~((HOBJECT n_copy) <- S_done.ALLOCATIONS)
~((HCELL n_prefix_cell) <- S_done.ALLOCATIONS)
~((HCELL n_pending_cell) <- S_done.ALLOCATIONS)
$weakref_get(S_done, n_weak_return) = PNULL
$weakref_get(S_done, n_weak_child) = PNULL
$weakref_get(S_done, n_weak_after) = PNULL
(OUTPUT $ptascii("BODY|")) <- S_done.EVENTS
(OUTPUT $ptascii("GEN-FIN|")) <- S_done.EVENTS
(OUTPUT $ptascii("CALLER-FIN|")) <- S_done.EVENTS
'''.splitlines() if line.strip()]

CASES = {'i107-fake-return-restores-copy-reference': {'source': ROW['source'], 'stage': STAGE, 'checks': CHECKS}}

def run(selected):
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=review.ROOT, text=True).strip()
    review.CASES = CASES
    original = review.recorded
    raw = None
    def recorded(command, directory, stem, environment, cap):
        nonlocal raw
        raw = directory.parent
        return original(command, directory, stem, environment, cap)
    review.recorded = recorded
    try:
        passed = review.run(selected, process_seconds=600)
    finally:
        review.recorded = original
    stable = INPUT_BYTES == {p: p.read_bytes() for p in INPUT_BYTES}
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=review.ROOT, text=True).strip()
    path = raw / 'report.json'
    report = json.loads(path.read_bytes())
    report.update(author_inputs={str(p): hashlib.sha256(data).hexdigest() for p, data in INPUT_BYTES.items()},
                  author_inputs_stable=stable, head_stable=head_stable,
                  passed=passed and stable and head_stable)
    path.write_text(json.dumps(report, indent=2) + '\n')
    return report['passed']

if __name__ == '__main__':
    raise SystemExit(0 if run(None) else 1)
