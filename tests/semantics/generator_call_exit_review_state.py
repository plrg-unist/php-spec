#!/usr/bin/env python3
"""Check named-default exit, failed-constructor suppression and copied API ownership."""
import hashlib
import json
from pathlib import Path
import subprocess
import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_call_exit_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROW = next(r for r in json.loads(INPUT_BYTES[CATALOG]) if r['id'] == 'i102-real-named-default-exit-independent')
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']
STAGE = "S.TODO = (EXIT_INVOKE pexitcall) :: ptask_tail* -- if S.CURRENT = (pcallcontext_ctor) -- if pcallcontext_ctor.TARGET = METHOD_TARGET n_default porigin_ctor -- if $object_name(S, n_default) = $ptascii(\"ExitDefault102D\") -- if S.FRAMES = [pframe_receive, pframe_api]"
CHECKS = [line.strip() for line in r'''
S.COMPLETION = NORMAL
S.ACTIVEFIBER = eps
S.FIBERCALLERS = eps
S.SOURCEPENDING = eps
S.CONSTCONTEXT = eps
S.CLOSURECALLRETAINED = eps
S.DESTRUCTION.RELEASES = eps
S.DESTRUCTION.CALLS = eps
S.DESTRUCTION.OPERATIONS = eps
S.DESTRUCTION.CLEANUPS = eps
S.ERRORHANDLER.CALLBACK = eps
pexitcall.SENT = [KNOWN (PINT 31)]
$call_task_valid(S, EXIT_INVOKE pexitcall)
$default_ctor_context_valid(S, pcallcontext_ctor)
pframe_receive.CONTEXT = (pcallcontext_receive)
pcallcontext_receive.TARGET = CLOSURE_TARGET n_copy
pcallcontext_receive.RECEIVER = (n_maker)
$call_receiver_roots(pcallcontext_receive) = eps
pframe_receive.TODO = (DEFAULT_CTOR_RESULT pdefaultctor) :: ptask_default_tail*
pdefaultctor.NEW.OBJECT = n_default
pframe_api.CONTEXT = eps
pframe_api.TODO = (CLOSURE_CALL_COPY_RESULT pclosurecall n_copy) :: ptask_api_tail*
$closure_call_copy_row(S, n_copy) = (pclosurebinding)
pclosurebinding.OBJECT = n_copy
n_source = pclosurebinding.SOURCE
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
$object_name(S, n_old) = $ptascii("OldDefault102D")
$object_name(S, n_maker) = $ptascii("MakerDefault102D")
$object_name(S, n_pending) = $ptascii("PendingDefault102D")
$object_name(S, n_capture) = $ptascii("CaptureDefault102D")
$object_name(S, n_default) = $ptascii("ExitDefault102D")
S.GLOBALTABLE = (psymboltable_global)
$lookup(psymboltable_global.ENV, $ptascii("source")) = (n_source_cell)
S.STORE[n_source_cell] = DEFINED PNULL
$lookup(psymboltable_global.ENV, $ptascii("generator")) = (n_generator_cell)
S.STORE[n_generator_cell] = DEFINED PNULL
$lookup(psymboltable_global.ENV, $ptascii("weakSource")) = (n_weak_source_cell)
S.STORE[n_weak_source_cell] = DEFINED (POBJECT n_weak_source)
$lookup(psymboltable_global.ENV, $ptascii("weakOld")) = (n_weak_old_cell)
S.STORE[n_weak_old_cell] = DEFINED (POBJECT n_weak_old)
$lookup(psymboltable_global.ENV, $ptascii("weakPending")) = (n_weak_pending_cell)
S.STORE[n_weak_pending_cell] = DEFINED (POBJECT n_weak_pending)
$lookup(psymboltable_global.ENV, $ptascii("weakMaker")) = (n_weak_maker_cell)
S.STORE[n_weak_maker_cell] = DEFINED (POBJECT n_weak_maker)
$lookup(psymboltable_global.ENV, $ptascii("weakCapture")) = (n_weak_capture_cell)
S.STORE[n_weak_capture_cell] = DEFINED (POBJECT n_weak_capture)
$lookup(psymboltable_global.ENV, $ptascii("weakDefault")) = (n_weak_default_cell)
S.STORE[n_weak_default_cell] = DEFINED (POBJECT n_weak_default)
$weakref_get(S, n_weak_source) = POBJECT n_source
$weakref_get(S, n_weak_old) = POBJECT n_old
$weakref_get(S, n_weak_pending) = POBJECT n_pending
$weakref_get(S, n_weak_maker) = POBJECT n_maker
$weakref_get(S, n_weak_capture) = POBJECT n_capture
$weakref_get(S, n_weak_default) = POBJECT n_default
~(n_default <- S.DESTRUCTION.CALLED)
$closure_call_copy_result_valid(S, pclosurecall, n_copy)
$closure_call_copy_cancel_pending(S, CLOSURE_CALL_COPY_RESULT pclosurecall n_copy)
~$closure_call_copy_created(S.OBJECTS, n_copy)
~$closure_call_copy_exit_head(S)
$closure_call_copy_exit_frames(S, S.FRAMES)
$closure_call_copy_exit_pending(S)
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
$heap_owners($heap_graph(S), HOBJECT n_copy) = 2
$heap_owners($heap_graph(S), HOBJECT n_source) = 1
$heap_owners($heap_graph(S), HOBJECT n_old) = 1
$heap_owners($heap_graph(S), HOBJECT n_capture) = 2
$heap_owners($heap_graph(S), HOBJECT n_maker) = 2
$heap_owners($heap_graph(S), HOBJECT n_pending) = 2
$heap_owners($heap_graph(S), HOBJECT n_default) = 2
pclosurecall_bad_site = pclosurecall[.SITE = PORIGIN 999 eps]
pframe_bad_site = pframe_api[.TODO = (CLOSURE_CALL_COPY_RESULT pclosurecall_bad_site n_copy) :: ptask_api_tail*]
S_bad_site = S[.FRAMES = [pframe_receive, pframe_bad_site]]
$closure_call_copy_row(S_bad_site, n_copy) = (pclosurebinding)
~$closure_call_copy_exit_pending(S_bad_site)
S_already = S[.CLOSURECALLRETAINED = [pclosurebinding]]
$closure_call_retained_valid(S_already)
~$closure_call_copy_exit_pending(S_already)
pgenerator_history = {FUNCTION porigin_function, FRAME eps, PHASE GENERATOR_CLOSED, FIRST false, PENDING_INIT false, PARKED eps, INDEX $(-1), VALUE eps, REFCELL eps, KEY eps, BORROWED eps, RETURN eps, CLOSURE (n_copy), DELEGATE eps, ACCESS eps, CREATION eps}
S_history = S[.OBJECTS = S.OBJECTS ++ [GENERATOR pgenerator_history]]
$closure_call_copy_row(S_history, n_copy) = (pclosurebinding)
$closure_call_copy_result_valid(S_history, pclosurecall, n_copy)
~$closure_call_copy_exit_pending(S_history)
S_pause = $drive(S, 0)
S_pause.COMPLETION = BUDGET
S_pause[.COMPLETION = NORMAL] = S
S_one = $drive(S, 1)
S_one.COMPLETION = BUDGET
S_one.EXITSTATUS = 31
S_one.CURRENT = S.CURRENT
S_one.FRAMES = S.FRAMES
S_one.CLOSURECALLRETAINED = eps
S_one.TODO = [EXIT_UNWIND 31]
$exit_unwind_valid(S_one, 31)
n_default <- S_one.DESTRUCTION.CALLED
$weakref_get(S_one, n_weak_default) = POBJECT n_default
$call_descriptors_valid(S_one)
$heap_valid($heap_graph(S_one))
S_after_ctor = $drive(S_one[.COMPLETION = NORMAL], 1)
S_after_ctor.COMPLETION = BUDGET
S_after_ctor.EXITSTATUS = 31
S_after_ctor.CURRENT = (pcallcontext_after_ctor)
pcallcontext_after_ctor.TARGET = CLOSURE_TARGET n_copy
S_after_ctor.FRAMES = [pframe_api]
S_after_ctor.TODO = [EXIT_UNWIND 31]
S_after_ctor.CLOSURECALLRETAINED = eps
$weakref_get(S_after_ctor, n_weak_default) = PNULL
~((HOBJECT n_default) <- S_after_ctor.ALLOCATIONS)
$call_descriptors_valid(S_after_ctor)
$heap_valid($heap_graph(S_after_ctor))
S_api = $drive(S_after_ctor[.COMPLETION = NORMAL], 1)
S_api.COMPLETION = BUDGET
S_api.EXITSTATUS = 31
S_api.CURRENT = eps
S_api.FRAMES = eps
S_api.CLOSURECALLRETAINED = [pclosurebinding]
S_api.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (EXIT_UNWIND 31) :: eps
pdestructionrelease.JOBS = $destruction_values([HOBJECT n_maker, HOBJECT n_pending, HOBJECT n_source])
$closure_call_retained_nodes(S_api.CLOSURECALLRETAINED) = [HOBJECT n_copy]
$closure_call_retained_valid(S_api)
$call_descriptors_valid(S_api)
$heap_valid($heap_graph(S_api))
$heap_owners($heap_graph(S_api), HOBJECT n_copy) = 1
$heap_owners($heap_graph(S_api), HOBJECT n_capture) = 2
$heap_owners($heap_graph(S_api), HOBJECT n_maker) = 2
$heap_owners($heap_graph(S_api), HOBJECT n_pending) = 1
$heap_owners($heap_graph(S_api), HOBJECT n_source) = 1
S_done = $drive(S, 4000)
$drive(S_api[.COMPLETION = NORMAL], 4000) = S_done
S_done.COMPLETION = EXITED 31
S_done.EXITSTATUS = 31
S_done.TODO = eps
S_done.CURRENT = eps
S_done.FRAMES = eps
S_done.HELD = eps
S_done.CLOSURECALLRETAINED = [pclosurebinding]
S_done.SHUTDOWN.PHASE = SHUTDOWN_DONE
$closure_call_retained_valid(S_done)
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
~$closure_call_copy_created(S_done.OBJECTS, n_copy)
~((HOBJECT n_source) <- S_done.ALLOCATIONS)
~((HOBJECT n_old) <- S_done.ALLOCATIONS)
~((HOBJECT n_pending) <- S_done.ALLOCATIONS)
~((HOBJECT n_default) <- S_done.ALLOCATIONS)
(HOBJECT n_copy) <- S_done.ALLOCATIONS
(HOBJECT n_maker) <- S_done.ALLOCATIONS
(HOBJECT n_capture) <- S_done.ALLOCATIONS
n_default <- S_done.DESTRUCTION.CALLED
n_old <- S_done.DESTRUCTION.CALLED
n_pending <- S_done.DESTRUCTION.CALLED
n_maker <- S_done.DESTRUCTION.CALLED
n_capture <- S_done.DESTRUCTION.CALLED
$heap_owners($heap_graph(S_done), HOBJECT n_copy) = 1
$heap_owners($heap_graph(S_done), HOBJECT n_maker) = 1
$heap_owners($heap_graph(S_done), HOBJECT n_capture) = 1
'''.splitlines() if line.strip()]
CASES = {'i102-default-exit-ctor-independent': {'source': ROW['source'], 'stage': STAGE, 'checks': CHECKS}}

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

