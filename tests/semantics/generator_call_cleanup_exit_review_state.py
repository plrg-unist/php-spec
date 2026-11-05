#!/usr/bin/env python3
"""Check pending exit through a warning retval child destructor and CLEAN."""
import hashlib
import json
from pathlib import Path
import subprocess
import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_call_cleanup_exit_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROW = next(r for r in json.loads(INPUT_BYTES[CATALOG]) if r['id'] == 'i103-real-owning-retval-child-exit-independent')
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']
STAGE = "S.CURRENT = (pcallcontext_child) -- if pcallcontext_child.TARGET = METHOD_TARGET n_child porigin_child -- if $object_name(S, n_child) = $ptascii(\"ChildClean103D\")"
API_STAGE = r'''dec $api_stage(pstate) : bool
def $api_stage(S) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.DESTRUCTION.OPERATIONS = eps /\ S.DESTRUCTION.CLEANUPS = eps
  -- if S.CLOSURECALLRETAINED = [pclosurebinding]
  -- if pclosurebinding.RECEIVER = (n_maker)
  -- if n_source = pclosurebinding.SOURCE
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: [EXIT_UNWIND 41]
  -- if pdestructionrelease.JOBS = [(DESTRUCTION_VALUE (HCELL n_prefix_cell)), (DESTRUCTION_VALUE (HOBJECT n_maker)), (DESTRUCTION_VALUE (HOBJECT n_prefix)), (DESTRUCTION_VALUE (HOBJECT n_pending)), (DESTRUCTION_VALUE (HOBJECT n_source))]
def $api_stage(S) = false -- otherwise
dec $api_seek(pstate, nat) : pstate
def $api_seek(S, n) = S -- if $api_stage(S)
def $api_seek(S, n) = $api_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$api_stage(S)
  -- if $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $api_seek(S, n) = S -- otherwise
'''
CHECKS = [line.strip() for line in r'''
S.COMPLETION = NORMAL
S.EXITSTATUS = 41
S.ACTIVEFIBER = eps
S.FIBERCALLERS = eps
S.SOURCEPENDING = eps
S.CONSTCONTEXT = eps
S.CLOSURECALLRETAINED = eps
S.DESTRUCTION.ABANDONED = eps
S.ERRORHANDLER.CALLBACK = eps
$destructor_context_call(pcallcontext_child, S.CURRENT, S.FRAMES) = (pdestructorcall_child)
$destructor_context_valid(S, pcallcontext_child)
pdestructorcall_child.OBJECT = n_child
pdestructorcall_child.USER
pdestructorcall_child.CALLER = eps
pdestructorcall_child.SITE = eps
pdestructorcall_child.PENDING = eps
pdestructorcall_child.OPERATION = (pdestructionoperation)
S.DESTRUCTION.CALLS = [pdestructorcall_child]
S.DESTRUCTION.OPERATIONS = [pdestructionoperation]
S.DESTRUCTION.FRAMES = eps
pdestructionoperation.COMPLETION = EXITED 41
pdestructionoperation.PENDING = eps
pdestructionoperation.SOURCE = ERROR_HANDLER_RESULT perrorcall
pdestructionoperation.CLEANUP = (pdestructioncleanup)
S.DESTRUCTION.CLEANUPS = [pdestructioncleanup]
pdestructioncleanup.SOURCE = ERROR_HANDLER_RESULT perrorcall
~pdestructioncleanup.RELEASED
perrorcall.RESUME = CLOSURE_CALL_COPY_REFERENCE pclosurecall n_copy n_done pnamedargs n_base
n_done = 1
$string_bytes(perrorcall.CALLBACK) = ($ptascii("Warn103D"))
pclosurecall.FIRST = (POBJECT n_maker)
pclosurecall.RAW = [(KINT 1, KNOWN (POBJECT n_prefix)), (KINT 2, KNOWN (POBJECT n_pending))]
pnamedargs.SLOTS = [NAMED_SENT (REFERENCE n_prefix_cell)]
pnamedargs.NAMED = eps
S.STORE[n_prefix_cell] = DEFINED (POBJECT n_prefix)
n_prefix_cell <- S.REFCELLS
$(n_prefix_cell >= n_base)
(HCELL n_prefix_cell) <- S.ALLOCATIONS
$closure_call_copy_row(S, n_copy) = (pclosurebinding)
n_source = pclosurebinding.SOURCE
pclosurebinding.OBJECT = n_copy
pclosurebinding.RECEIVER = (n_maker)
pdestructorcall_child.ORIGIN = (pclosurecall.SITE)
S.OBJECTS[n_copy] = REALCLOSURE porigin_function pitem* eps
$closure_items_nodes(pitem*) = [HOBJECT n_capture]
$node_children(S, HOBJECT n_copy) = [HOBJECT n_capture, HOBJECT n_maker]
$target_receiver(S, CLOSURE_TARGET n_source) = (n_old)
$object_name(S, n_old) = $ptascii("OldClean103D")
$object_name(S, n_maker) = $ptascii("MakerClean103D")
$object_name(S, n_prefix) = $ptascii("PrefixClean103D")
$object_name(S, n_pending) = $ptascii("PendingClean103D")
$object_name(S, n_capture) = $ptascii("CaptureClean103D")
S.GLOBALTABLE = (psymboltable_global)
$lookup(psymboltable_global.ENV, $ptascii("source")) = (n_source_cell)
S.STORE[n_source_cell] = DEFINED PNULL
$lookup(psymboltable_global.ENV, $ptascii("weakRetval")) = (n_weak_retval_cell)
S.STORE[n_weak_retval_cell] = DEFINED (POBJECT n_weak_retval)
S.OBJECTS[n_weak_retval] = WEAKREFERENCE (n_retval)
$weakref_get(S, n_weak_retval) = PNULL
$object_name(S, n_retval) = $ptascii("RetvalClean103D")
$instance_storage_for(S, n_retval) = (pinstancestorage)
$instance_storage_freeing(S, n_retval)
pinstancestorage.OBJECT = n_retval
pinstancestorage.CALLER = eps
pinstancestorage.ORIGIN = (pclosurecall.SITE)
pinstancestorage.CONSTCONTEXT = eps
pinstancestorage.USER
pinstancestorage.NOTIFY = eps
pinstancestorage.NEXT = 1
|pinstancestorage.SLOTS| = 1
pinstancestorage.SLOTS[0].NAME = $ptascii("child")
pinstancestorage.SLOTS[0].STATE = PROP_VALUE (VALUE (POBJECT n_child))
$objectprops_at(S.OBJECTPROPS, n_retval) = (ppropertyslot*)
ppropertyslot*[0].STATE = PROP_UNSET
(HOBJECT n_retval) <- S.ALLOCATIONS
n_retval <- S.DESTRUCTION.CALLED
n_child <- S.DESTRUCTION.CALLED
$lookup(psymboltable_global.ENV, $ptascii("weakChild")) = (n_weak_child_cell)
S.STORE[n_weak_child_cell] = DEFINED (POBJECT n_weak_child)
$weakref_get(S, n_weak_child) = POBJECT n_child
$lookup(psymboltable_global.ENV, $ptascii("weakSource")) = (n_weak_source_cell)
S.STORE[n_weak_source_cell] = DEFINED (POBJECT n_weak_source)
$weakref_get(S, n_weak_source) = POBJECT n_source
$lookup(psymboltable_global.ENV, $ptascii("weakOld")) = (n_weak_old_cell)
S.STORE[n_weak_old_cell] = DEFINED (POBJECT n_weak_old)
$weakref_get(S, n_weak_old) = POBJECT n_old
$lookup(psymboltable_global.ENV, $ptascii("weakMaker")) = (n_weak_maker_cell)
S.STORE[n_weak_maker_cell] = DEFINED (POBJECT n_weak_maker)
$weakref_get(S, n_weak_maker) = POBJECT n_maker
$lookup(psymboltable_global.ENV, $ptascii("weakCapture")) = (n_weak_capture_cell)
S.STORE[n_weak_capture_cell] = DEFINED (POBJECT n_weak_capture)
$weakref_get(S, n_weak_capture) = POBJECT n_capture
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
$heap_owners($heap_graph(S), HOBJECT n_retval) = 1
$heap_owners($heap_graph(S), HOBJECT n_child) = 2
$heap_owners($heap_graph(S), HOBJECT n_copy) = 1
$heap_owners($heap_graph(S), HOBJECT n_maker) = 2
$heap_owners($heap_graph(S), HOBJECT n_capture) = 2
$heap_owners($heap_graph(S), HOBJECT n_source) = 1
$heap_owners($heap_graph(S), HOBJECT n_old) = 1
$heap_owners($heap_graph(S), HOBJECT n_prefix) = 2
$heap_owners($heap_graph(S), HOBJECT n_pending) = 1
$heap_owners($heap_graph(S), HCELL n_prefix_cell) = 1
S_emit = $eager_cleanup_history(S, pdestructioncleanup)
S_view = $closure_call_copy_warning_history(S_emit, perrorcall)
S_view.TODO = (ERROR_HANDLER_CLEAN perrorcall) :: ptask_view_tail*
S_view = S_emit[.TODO = S_view.TODO]
$eager_removed($tasks_nodes(S_emit.TODO), $tasks_nodes(S_view.TODO)) = eps
$eager_removed($tasks_nodes(S_view.TODO), $tasks_nodes(S_emit.TODO)) = eps
$call_task_valid(S_view, perrorcall.RESUME)
$error_call_valid(S_emit, perrorcall)
$eager_cleanup_valid(S, pdestructioncleanup)
S_extra = S_emit[.HELD = (HCELL n_prefix_cell) :: S_emit.HELD]
S_extra_view = $closure_call_copy_warning_history(S_extra, perrorcall)
S_extra_view.HELD = S_extra.HELD
~$call_task_valid(S_extra_view, perrorcall.RESUME)
pclosurecall_bad_source = pclosurecall[.SOURCE = n_copy]
~$call_task_valid(S_view, CLOSURE_CALL_COPY_REFERENCE pclosurecall_bad_source n_copy n_done pnamedargs n_base)
pnamedargs_bad = pnamedargs[.SLOTS = [NAMED_SENT (REFERENCE n_source_cell)]]
~$call_task_valid(S_view, CLOSURE_CALL_COPY_REFERENCE pclosurecall n_copy n_done pnamedargs_bad n_base)
$closure_call_copy_cancel_pending(S_view, CLOSURE_CALL_COPY_RESULT pclosurecall n_copy)
pgenerator_history = {FUNCTION porigin_function, FRAME eps, PHASE GENERATOR_CLOSED, FIRST false, PENDING_INIT false, PARKED eps, INDEX $(-1), VALUE eps, REFCELL eps, KEY eps, BORROWED eps, RETURN eps, CLOSURE (n_copy), DELEGATE eps, ACCESS eps, CREATION eps}
S_history = S_view[.OBJECTS = S_view.OBJECTS ++ [GENERATOR pgenerator_history]]
$closure_call_copy_result_valid(S_history, pclosurecall, n_copy)
~$closure_call_copy_cancel_pending(S_history, CLOSURE_CALL_COPY_RESULT pclosurecall n_copy)
S_pause = $drive(S, 0)
S_pause.COMPLETION = BUDGET
S_pause[.COMPLETION = NORMAL] = S
S_api_reached = $api_seek(S, 128)
S_api_reached.COMPLETION = NORMAL \/ S_api_reached.COMPLETION = BUDGET
S_api = S_api_reached[.COMPLETION = NORMAL]
S_api.EXITSTATUS = 41
S_api.CURRENT = eps
S_api.FRAMES = eps
S_api.CLOSURECALLRETAINED = [pclosurebinding]
S_api.DESTRUCTION.CALLS = eps
S_api.DESTRUCTION.OPERATIONS = eps
S_api.DESTRUCTION.CLEANUPS = eps
S_api.DESTRUCTION.ABANDONED = eps
S_api.ERRORHANDLER.CALLBACK = (perrorcall.CALLBACK)
S_api.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: [EXIT_UNWIND 41]
pdestructionrelease.JOBS = $destruction_values([HCELL n_prefix_cell, HOBJECT n_maker, HOBJECT n_prefix, HOBJECT n_pending, HOBJECT n_source])
$weakref_get(S_api, n_weak_retval) = PNULL
$weakref_get(S_api, n_weak_child) = PNULL
~((HOBJECT n_retval) <- S_api.ALLOCATIONS)
~((HOBJECT n_child) <- S_api.ALLOCATIONS)
$instance_storage_for(S_api, n_retval) = eps
$instance_storage_for(S_api, n_child) = eps
S_api.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("CHILD|")]
$closure_call_retained_valid(S_api)
$call_descriptors_valid(S_api)
$heap_valid($heap_graph(S_api))
S_done = $drive(S, 4000)
$drive(S_api, 4000) = S_done
S_done.COMPLETION = EXITED 41
S_done.EXITSTATUS = 41
S_done.TODO = eps
S_done.CURRENT = eps
S_done.FRAMES = eps
S_done.HELD = eps
S_done.SHUTDOWN.PHASE = SHUTDOWN_DONE
S_done.CLOSURECALLRETAINED = [pclosurebinding]
S_done.DESTRUCTION.CALLS = eps
S_done.DESTRUCTION.OPERATIONS = eps
S_done.DESTRUCTION.CLEANUPS = eps
S_done.DESTRUCTION.RELEASES = eps
S_done.DESTRUCTION.ABANDONED = eps
$closure_call_retained_valid(S_done)
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
~$closure_call_copy_created(S_done.OBJECTS, n_copy)
~((HOBJECT n_retval) <- S_done.ALLOCATIONS)
~((HOBJECT n_child) <- S_done.ALLOCATIONS)
~((HOBJECT n_source) <- S_done.ALLOCATIONS)
~((HOBJECT n_old) <- S_done.ALLOCATIONS)
~((HOBJECT n_prefix) <- S_done.ALLOCATIONS)
~((HOBJECT n_pending) <- S_done.ALLOCATIONS)
~((HCELL n_prefix_cell) <- S_done.ALLOCATIONS)
(HOBJECT n_copy) <- S_done.ALLOCATIONS
(HOBJECT n_capture) <- S_done.ALLOCATIONS
(HOBJECT n_maker) <- S_done.ALLOCATIONS
n_retval <- S_done.DESTRUCTION.CALLED
n_child <- S_done.DESTRUCTION.CALLED
n_old <- S_done.DESTRUCTION.CALLED
n_prefix <- S_done.DESTRUCTION.CALLED
n_pending <- S_done.DESTRUCTION.CALLED
n_capture <- S_done.DESTRUCTION.CALLED
n_maker <- S_done.DESTRUCTION.CALLED
$heap_owners($heap_graph(S_done), HOBJECT n_copy) = 1
$heap_owners($heap_graph(S_done), HOBJECT n_capture) = 1
$heap_owners($heap_graph(S_done), HOBJECT n_maker) = 1
'''.splitlines() if line.strip()]
CASES = {'i103-real-child-cleanup-pending-exit-independent': {'source': ROW['source'], 'stage': STAGE, 'checks': CHECKS}}

if __name__ == '__main__':
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=review.ROOT, text=True).strip()
    review.CASES = CASES
    original = review.recorded
    raw = None
    def recorded(command, directory, stem, environment, cap):
        global raw
        raw = directory.parent
        if stem == 'model':
            fixture = Path(command[-1])
            text = fixture.read_text()
            anchor = 'def $stage(S) = false -- otherwise\n'
            assert text.count(anchor) == 1
            fixture.write_text(text.replace(anchor, API_STAGE + anchor))
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
