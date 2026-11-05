#!/usr/bin/env python3
"""Check required-hole cleanup at the restored API cursor after general receive cancellation."""
import hashlib
import json
from pathlib import Path
import subprocess
import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_call_mapping_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROW = next(r for r in json.loads(INPUT_BYTES[CATALOG]) if r['id'] == 'i100-real-named-hole-required-independent')
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']
STAGE = ('S.TODO = (THROW_SEARCH n_throw) :: (CLOSURE_CALL_COPY_RESULT pclosurecall n_copy) :: ptask_tail* '
         '-- if S.CURRENT = eps -- if S.FRAMES = eps')
CHECKS = [line.strip() for line in r'''
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
S.ACTIVEFIBER = eps
S.FIBERCALLERS = eps
S.CONSTCONTEXT = eps
S.SOURCEPENDING = eps
S.CLOSURECALLRETAINED = eps
S.DESTRUCTION.RELEASES = eps
S.DESTRUCTION.CALLS = eps
S.DESTRUCTION.OPERATIONS = eps
S.DESTRUCTION.CLEANUPS = eps
S.ERRORHANDLER.CALLBACK = eps
$closure_call_copy_row(S, n_copy) = (pclosurebinding)
n_source = pclosurebinding.SOURCE
pclosurebinding.OBJECT = n_copy
pclosurebinding.RECEIVER = (n_maker)
pclosurecall.FIRST = (POBJECT n_maker)
pclosurecall.ERROR = eps
pclosurecall.RAW = [(KSTRING $ptascii("second"), KNOWN (POBJECT n_pending))]
pclosurecall.SENT.SLOTS = [NAMED_HOLE, NAMED_SENT (KNOWN (POBJECT n_pending))]
pclosurecall.SENT.NAMED = eps
S.OBJECTS[n_copy] = REALCLOSURE porigin_function pitem* eps
$closure_items_nodes(pitem*) = [HOBJECT n_capture]
$target_receiver(S, CLOSURE_TARGET n_source) = (n_old)
$node_children(S, HOBJECT n_copy) = [HOBJECT n_capture, HOBJECT n_maker]
$object_name(S, n_old) = $ptascii("OldCancel100H")
$object_name(S, n_maker) = $ptascii("MakerCancel100H")
$object_name(S, n_pending) = $ptascii("PendingCancel100H")
$object_name(S, n_capture) = $ptascii("CaptureCancel100H")
$lookup(S.ENV, $ptascii("source")) = (n_source_cell)
S.STORE[n_source_cell] = DEFINED PNULL
$lookup(S.ENV, $ptascii("generator")) = (n_generator_cell)
S.STORE[n_generator_cell] = DEFINED PNULL
$target_function(S, CLOSURE_TARGET n_copy) = (pfunction)
$function_generator(S, pfunction)
$closure_call_copy_result_valid(S, pclosurecall, n_copy)
$closure_call_copy_cancel_pending(S, CLOSURE_CALL_COPY_RESULT pclosurecall n_copy)
~$closure_call_copy_created(S.OBJECTS, n_copy)
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
$heap_owners($heap_graph(S), HOBJECT n_copy) = 1
$heap_owners($heap_graph(S), HOBJECT n_source) = 1
$heap_owners($heap_graph(S), HOBJECT n_capture) = 2
$lookup(S.ENV, $ptascii("weakSource")) = (n_weak_source_cell)
S.STORE[n_weak_source_cell] = DEFINED (POBJECT n_weak_source)
$weakref_get(S, n_weak_source) = POBJECT n_source
$lookup(S.ENV, $ptascii("weakOld")) = (n_weak_old_cell)
S.STORE[n_weak_old_cell] = DEFINED (POBJECT n_weak_old)
$weakref_get(S, n_weak_old) = POBJECT n_old
$lookup(S.ENV, $ptascii("weakPending")) = (n_weak_pending_cell)
S.STORE[n_weak_pending_cell] = DEFINED (POBJECT n_weak_pending)
$weakref_get(S, n_weak_pending) = POBJECT n_pending
$lookup(S.ENV, $ptascii("weakMaker")) = (n_weak_maker_cell)
S.STORE[n_weak_maker_cell] = DEFINED (POBJECT n_weak_maker)
$weakref_get(S, n_weak_maker) = POBJECT n_maker
$lookup(S.ENV, $ptascii("weakCapture")) = (n_weak_capture_cell)
S.STORE[n_weak_capture_cell] = DEFINED (POBJECT n_weak_capture)
$weakref_get(S, n_weak_capture) = POBJECT n_capture
$throwable_field(S, n_throw, "previous") = PNULL
$throwable_field(S, n_throw, "trace") = PARRAY n_trace
pnode_trace* = $heap_reach([HARRAY n_trace], eps, $heap_graph(S).EDGES)
~((HOBJECT n_source) <- pnode_trace*)
~((HOBJECT n_old) <- pnode_trace*)
~((HOBJECT n_copy) <- pnode_trace*)
~((HOBJECT n_capture) <- pnode_trace*)
S.OBJECTS[n_throw] = THROWABLE pthrowable
pthrowable.KIND = "ArgumentCountError"
(HOBJECT n_pending) <- pnode_trace*
(HOBJECT n_maker) <- pnode_trace*
$heap_owners($heap_graph(S), HOBJECT n_maker) = 3
$heap_owners($heap_graph(S), HOBJECT n_pending) = 3
pclosurecall_bad_site = pclosurecall[.SITE = PORIGIN 999 eps]
~$closure_call_copy_cancel_pending(S, CLOSURE_CALL_COPY_RESULT pclosurecall_bad_site n_copy)
S_already = S[.CLOSURECALLRETAINED = [pclosurebinding]]
$closure_call_retained_valid(S_already)
~$closure_call_copy_cancel_pending(S_already, CLOSURE_CALL_COPY_RESULT pclosurecall n_copy)
pgenerator_history = {FUNCTION porigin_function, FRAME eps, PHASE GENERATOR_CLOSED, FIRST false, PENDING_INIT false, PARKED eps, INDEX $(-1), VALUE eps, REFCELL eps, KEY eps, BORROWED eps, RETURN eps, CLOSURE (n_copy), DELEGATE eps, ACCESS eps, CREATION eps}
S_history = S[.OBJECTS = S.OBJECTS ++ [GENERATOR pgenerator_history]]
$closure_call_copy_result_valid(S_history, pclosurecall, n_copy)
~$closure_call_copy_cancel_pending(S_history, CLOSURE_CALL_COPY_RESULT pclosurecall n_copy)
S_pop = S[.TODO = (THROW_SEARCH n_throw) :: ptask_tail*]
S_cancel = $return_discard(S_pop, CLOSURE_CALL_COPY_RESULT pclosurecall n_copy)
S_cancel.CLOSURECALLRETAINED = [pclosurebinding]
S_cancel.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (THROW_SEARCH n_throw) :: ptask_tail*
pdestructionrelease.JOBS = $destruction_values([HOBJECT n_maker, HOBJECT n_pending, HOBJECT n_source])
$closure_call_retained_nodes(S_cancel.CLOSURECALLRETAINED) = [HOBJECT n_copy]
$closure_call_retained_valid(S_cancel)
$heap_owners($heap_graph(S_cancel), HOBJECT n_copy) = 1
$heap_owners($heap_graph(S_cancel), HOBJECT n_source) = 1
$heap_owners($heap_graph(S_cancel), HOBJECT n_capture) = 2
$heap_valid($heap_graph(S_cancel))
$heap_owners($heap_graph(S_cancel), HOBJECT n_maker) = 3
$heap_owners($heap_graph(S_cancel), HOBJECT n_pending) = 3
S_pause = $drive(S, 0)
S_pause.COMPLETION = BUDGET
S_pause.TODO = S.TODO
S_pause.CLOSURECALLRETAINED = eps
S_one = $drive(S, 1)
S_one.COMPLETION = BUDGET
S_one.CLOSURECALLRETAINED = [pclosurebinding]
S_done = $drive(S, 4000)
S_pause[.COMPLETION = NORMAL] = S
$drive(S_one[.COMPLETION = NORMAL], 4000) = S_done
S_done.COMPLETION = NORMAL
S_done.EXITSTATUS = 0
S_done.TODO = eps
S_done.CURRENT = eps
S_done.FRAMES = eps
S_done.HELD = eps
S_done.CLOSURECALLRETAINED = [pclosurebinding]
S_done.SHUTDOWN.PHASE = SHUTDOWN_DONE
$closure_call_retained_valid(S_done)
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
~((HOBJECT n_source) <- S_done.ALLOCATIONS)
~((HOBJECT n_old) <- S_done.ALLOCATIONS)
~((HOBJECT n_pending) <- S_done.ALLOCATIONS)
(HOBJECT n_copy) <- S_done.ALLOCATIONS
(HOBJECT n_maker) <- S_done.ALLOCATIONS
(HOBJECT n_capture) <- S_done.ALLOCATIONS
n_old <- S_done.DESTRUCTION.CALLED
n_pending <- S_done.DESTRUCTION.CALLED
n_maker <- S_done.DESTRUCTION.CALLED
n_capture <- S_done.DESTRUCTION.CALLED
$heap_owners($heap_graph(S_done), HOBJECT n_copy) = 1
$heap_owners($heap_graph(S_done), HOBJECT n_maker) = 1
$heap_owners($heap_graph(S_done), HOBJECT n_capture) = 1
~((HOBJECT n_throw) <- S_done.ALLOCATIONS)
'''.splitlines() if line.strip()]
CASES = {'i100-required-hole-throw-independent': {'source': ROW['source'], 'stage': STAGE, 'checks': CHECKS}}

if __name__ == '__main__':
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=review.ROOT, text=True).strip()
    review.CASES = CASES
    original = review.recorded
    raw = None
    def recorded(command, directory, stem, environment, cap):
        global raw
        raw = directory.parent
        return original(command, directory, stem, environment, cap)
    review.recorded = recorded
    try:
        passed = review.run(list(CASES), process_seconds=600)
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
    raise SystemExit(0 if report['passed'] else 1)
