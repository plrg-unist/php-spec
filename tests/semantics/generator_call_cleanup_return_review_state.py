#!/usr/bin/env python3
"""Independent real Closure review of normal warning retval cleanup."""
import hashlib
import json
from pathlib import Path
import subprocess
import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_call_cleanup_return_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROW = next(r for r in json.loads(INPUT_BYTES[CATALOG])
           if r['id'] == 'i107-real-captured-warning-return-gen-close')
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256'] == 'a539e717ddc632bc2829a072420ac3e476c431d9aef7dc17166c46edac010410'
STAGE = (
    'S.TODO = (ERROR_HANDLER_CLEAN perrorcall) :: ptask_tail* '
    '-- if perrorcall.RESUME = CLOSURE_CALL_COPY_REFERENCE pclosurecall n_copy 1 pnamedargs n_base '
    '-- if S.DESTRUCTION.CLEANUPS = pdestructioncleanup :: pdestructioncleanup_tail* '
    '-- if pdestructioncleanup.SOURCE = ERROR_HANDLER_RESULT perrorcall '
    '-- if pclosurecall.FIRST = (POBJECT n_maker) '
    '-- if $object_name(S, n_maker) = $ptascii("Maker107R")')
CHECKS = [line.strip() for line in r'''
S.COMPLETION = NORMAL
S.ACTIVEFIBER = eps
S.CURRENT = eps
S.FRAMES = eps
S.CLOSURECALLRETAINED = eps
S.ERRORHANDLER.CALLBACK = eps
S.DESTRUCTION.CALLS = eps
S.DESTRUCTION.OPERATIONS = eps
~pdestructioncleanup.RELEASED
pclosurecall.RAW = [(KINT 1, KNOWN (POBJECT n_prefix)), (KINT 2, KNOWN (POBJECT n_pending))]
pnamedargs.SLOTS = [NAMED_SENT (REFERENCE n_prefix_cell)]
pnamedargs.NAMED = eps
S.STORE[n_prefix_cell] = DEFINED (POBJECT n_prefix)
n_prefix_cell <- S.REFCELLS
$closure_call_copy_row(S, n_copy) = (pclosurebinding)
pclosurebinding.SOURCE = n_source
pclosurebinding.RECEIVER = (n_maker)
S.OBJECTS[n_copy] = REALCLOSURE porigin_function pitem* eps
$closure_items_nodes(pitem*) = [HOBJECT n_capture]
$node_children(S, HOBJECT n_copy) = [HOBJECT n_capture, HOBJECT n_maker]
$target_receiver(S, CLOSURE_TARGET n_source) = (n_old)
$object_name(S, n_old) = $ptascii("Old107R")
$object_name(S, n_prefix) = $ptascii("Prefix107R")
$object_name(S, n_pending) = $ptascii("Pending107R")
$object_name(S, n_capture) = $ptascii("Capture107R")
$lookup(S.ENV, $ptascii("source")) = (n_source_cell)
S.STORE[n_source_cell] = DEFINED PNULL
$lookup(S.ENV, $ptascii("generator")) = (n_generator_cell)
S.STORE[n_generator_cell] = DEFINED PNULL
$lookup(S.ENV, $ptascii("weakRetval")) = (n_weak_retval_cell)
S.STORE[n_weak_retval_cell] = DEFINED (POBJECT n_weak_retval)
S.OBJECTS[n_weak_retval] = WEAKREFERENCE (n_retval)
$weakref_get(S, n_weak_retval) = PNULL
$lookup(S.ENV, $ptascii("weakChild")) = (n_weak_child_cell)
S.STORE[n_weak_child_cell] = DEFINED (POBJECT n_weak_child)
S.OBJECTS[n_weak_child] = WEAKREFERENCE (n_child)
$weakref_get(S, n_weak_child) = PNULL
$lookup(S.ENV, $ptascii("weakAfter")) = (n_weak_after_cell)
S.STORE[n_weak_after_cell] = DEFINED (POBJECT n_weak_after)
S.OBJECTS[n_weak_after] = WEAKREFERENCE (n_after)
$weakref_get(S, n_weak_after) = PNULL
$instance_storage_for(S, n_retval) = eps
~((HOBJECT n_retval) <- S.ALLOCATIONS)
~((HOBJECT n_child) <- S.ALLOCATIONS)
~((HOBJECT n_after) <- S.ALLOCATIONS)
$call_descriptors_valid(S)
H = $heap_graph(S)
$heap_valid(H)
$heap_owners(H, HOBJECT n_copy) = 1
$heap_owners(H, HOBJECT n_source) = 1
$heap_owners(H, HOBJECT n_old) = 1
$heap_owners(H, HOBJECT n_maker) = 2
$heap_owners(H, HOBJECT n_capture) = 2
$heap_owners(H, HOBJECT n_prefix) = 2
$heap_owners(H, HOBJECT n_pending) = 1
$heap_owners(H, HCELL n_prefix_cell) = 1
$error_cleanup_valid(S, perrorcall)
pclosurecall_bad = pclosurecall[.SOURCE = n_copy]
~$call_task_valid(S, CLOSURE_CALL_COPY_REFERENCE pclosurecall_bad n_copy 1 pnamedargs n_base)
S_bad_copy = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HOBJECT n_copy)]
~$error_cleanup_valid(S_bad_copy, perrorcall)
S_paused = $drive(S, 0)
S_paused.COMPLETION = BUDGET
S_paused[.COMPLETION = NORMAL] = S
PhpStep: S ~> S_restored
S_restored.TODO = (CLOSURE_CALL_COPY_REFERENCE pclosurecall n_copy 1 pnamedargs n_base) :: ptask_tail*
S_restored.DESTRUCTION.CLEANUPS = pdestructioncleanup_tail*
S_restored.DESTRUCTION.CALLS = eps
S_restored.DESTRUCTION.OPERATIONS = eps
S_restored.ERRORHANDLER.CALLBACK = (perrorcall.CALLBACK)
$string_bytes(perrorcall.CALLBACK) = $ptascii("Warn107R")
S_restored.STORE[n_source_cell] = DEFINED PNULL
$call_task_valid(S_restored, CLOSURE_CALL_COPY_REFERENCE pclosurecall n_copy 1 pnamedargs n_base)
PhpStep: S_restored ~> S_wrapped
S_wrapped.TODO = (CLOSURE_CALL_COPY_FORWARD pclosurecall n_copy 2 pnamedargs_wrapped n_base) :: ptask_tail*
pnamedargs_wrapped.SLOTS = [NAMED_SENT (REFERENCE n_prefix_cell), NAMED_SENT (REFERENCE n_pending_cell)]
pnamedargs_wrapped.NAMED = eps
n_pending_cell =/= n_prefix_cell
S_wrapped.STORE[n_pending_cell] = DEFINED (POBJECT n_pending)
n_pending_cell <- S_wrapped.REFCELLS
$call_task_valid(S_wrapped, CLOSURE_CALL_COPY_FORWARD pclosurecall n_copy 2 pnamedargs_wrapped n_base)
$heap_valid($heap_graph(S_wrapped))
S_done = $drive(S_paused[.COMPLETION = NORMAL], 4800)
S_done.COMPLETION = NORMAL
S_done.SHUTDOWN.PHASE = SHUTDOWN_DONE
S_done.TODO = eps
S_done.CURRENT = eps
S_done.FRAMES = eps
S_done.DESTRUCTION.CLEANUPS = eps
S_done.DESTRUCTION.OPERATIONS = eps
S_done.CLOSURECALLRETAINED = eps
S_done.SOURCEPENDING = eps
S_done.HELD = eps
~((HOBJECT n_copy) <- S_done.ALLOCATIONS)
~((HOBJECT n_source) <- S_done.ALLOCATIONS)
~((HOBJECT n_old) <- S_done.ALLOCATIONS)
~((HOBJECT n_maker) <- S_done.ALLOCATIONS)
~((HOBJECT n_prefix) <- S_done.ALLOCATIONS)
~((HOBJECT n_pending) <- S_done.ALLOCATIONS)
~((HOBJECT n_capture) <- S_done.ALLOCATIONS)
$heap_valid($heap_graph(S_done))
(OUTPUT $ptascii("BODY|")) <- S_done.EVENTS
(OUTPUT $ptascii("FIN|")) <- S_done.EVENTS
(OUTPUT $ptascii("SHUT|")) <- S_done.EVENTS
'''.splitlines() if line.strip()]

CASES = {'i107-real-normal-cleanup-independent': {'source': ROW['source'], 'stage': STAGE, 'checks': CHECKS}}

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
    report.update(peer_inputs={str(p): hashlib.sha256(data).hexdigest() for p, data in INPUT_BYTES.items()},
                  peer_inputs_stable=stable, head_stable=head_stable,
                  passed=passed and stable and head_stable)
    path.write_text(json.dumps(report, indent=2) + '\n')
    return report['passed']

if __name__ == '__main__':
    raise SystemExit(0 if run(None) else 1)
