#!/usr/bin/env python3
"""Reach integer reexit while a copied warning retval frees its Child."""
import hashlib
import json
from pathlib import Path
import subprocess
import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_call_repeated_cleanup_exit_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROW = next(r for r in json.loads(INPUT_BYTES[CATALOG]) if r['id'] == 'i105-real-owning-child-integer-reexit-independent')
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']
STAGE = ('S.TODO = [EXIT_UNWIND 53] -- if S.FRAMES = [pframe_cleanup] '
         '-- if S.CURRENT = (pcallcontext_child) '
         '-- if pcallcontext_child.TARGET = METHOD_TARGET n_child porigin_child '
         '-- if $object_name(S, n_child) = $ptascii("ChildClean105D") '
         '-- if pframe_cleanup.TODO = (DESTRUCTOR_RESULT pdestructorcall_child) :: ptask_cleanup_tail* '
         '-- if pdestructorcall_child.OPERATION = (pdestructionoperation) '
         '-- if pdestructionoperation.SOURCE = ERROR_HANDLER_RESULT perrorcall '
         '-- if perrorcall.RESUME = CLOSURE_CALL_COPY_REFERENCE pclosurecall n_copy n_done pnamedargs n_base')
API_STAGE = r'''dec $api_stage(pstate) : bool
def $api_stage(S) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.DESTRUCTION.OPERATIONS = eps /\ S.DESTRUCTION.CLEANUPS = eps
  -- if S.CLOSURECALLRETAINED = [pclosurebinding]
  -- if pclosurebinding.RECEIVER = (n_maker)
  -- if n_source = pclosurebinding.SOURCE
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: [EXIT_UNWIND 53]
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
S.EXITSTATUS = 53
S.ACTIVEFIBER = eps
S.FIBERCALLERS = eps
S.SOURCEPENDING = eps
S.CLOSURECALLRETAINED = eps
S.DESTRUCTION.ABANDONED = eps
S.ERRORHANDLER.CALLBACK = eps
S.DESTRUCTION.CALLS = [pdestructorcall_child]
pdestructorcall_child.OBJECT = n_child
pdestructorcall_child.USER
pdestructorcall_child.CALLER = eps
pdestructorcall_child.SITE = eps
pdestructorcall_child.PENDING = eps
S.DESTRUCTION.OPERATIONS = [pdestructionoperation]
pdestructionoperation.COMPLETION = EXITED 41
pdestructionoperation.PENDING = eps
pdestructionoperation.CLEANUP = (pdestructioncleanup)
S.DESTRUCTION.CLEANUPS = [pdestructioncleanup]
pdestructioncleanup.SOURCE = ERROR_HANDLER_RESULT perrorcall
~pdestructioncleanup.RELEASED
n_done = 1
pclosurecall.FIRST = (POBJECT n_maker)
pclosurecall.RAW = [(KINT 1, KNOWN (POBJECT n_prefix)), (KINT 2, KNOWN (POBJECT n_pending))]
pnamedargs.SLOTS = [NAMED_SENT (REFERENCE n_prefix_cell)]
pnamedargs.NAMED = eps
S.STORE[n_prefix_cell] = DEFINED (POBJECT n_prefix)
$closure_call_copy_row(S, n_copy) = (pclosurebinding)
n_source = pclosurebinding.SOURCE
pclosurebinding.RECEIVER = (n_maker)
S.OBJECTS[n_copy] = REALCLOSURE porigin_function pitem* eps
$closure_items_nodes(pitem*) = [HOBJECT n_capture]
$node_children(S, HOBJECT n_copy) = [HOBJECT n_capture, HOBJECT n_maker]
$target_receiver(S, CLOSURE_TARGET n_source) = (n_old)
$object_name(S, n_maker) = $ptascii("MakerClean105D")
$object_name(S, n_old) = $ptascii("OldClean105D")
S.GLOBALTABLE = (psymboltable_global)
$lookup(psymboltable_global.ENV, $ptascii("source")) = (n_source_cell)
S.STORE[n_source_cell] = DEFINED PNULL
$lookup(psymboltable_global.ENV, $ptascii("weakRetval")) = (n_weak_retval_cell)
S.STORE[n_weak_retval_cell] = DEFINED (POBJECT n_weak_retval)
S.OBJECTS[n_weak_retval] = WEAKREFERENCE (n_retval)
$weakref_get(S, n_weak_retval) = PNULL
$object_name(S, n_retval) = $ptascii("RetvalClean105D")
$lookup(psymboltable_global.ENV, $ptascii("weakChild")) = (n_weak_child_cell)
S.STORE[n_weak_child_cell] = DEFINED (POBJECT n_weak_child)
$weakref_get(S, n_weak_child) = POBJECT n_child
$instance_storage_for(S, n_retval) = (pinstancestorage)
pinstancestorage.CALLER = eps
pinstancestorage.ORIGIN = (pclosurecall.SITE)
pinstancestorage.CONSTCONTEXT = eps
pinstancestorage.USER
pinstancestorage.NOTIFY = eps
pinstancestorage.NEXT = 1
|pinstancestorage.SLOTS| = 1
pinstancestorage.SLOTS[0].STATE = PROP_VALUE (DIRECT (POBJECT n_child))
$objectprops_at(S.OBJECTPROPS, n_retval) = (ppropertyslot*)
ppropertyslot*[0].STATE = PROP_UNSET
(INSTANCE_STORAGE_STEP pinstancestorage) <- ptask_cleanup_tail*
H = $heap_graph(S)
$heap_valid(H)
$heap_owners(H, HOBJECT n_retval) = 1
$heap_owners(H, HOBJECT n_child) = 2
$heap_owners(H, HOBJECT n_copy) = 1
$heap_owners(H, HOBJECT n_maker) = 2
$heap_owners(H, HOBJECT n_capture) = 2
$heap_owners(H, HOBJECT n_source) = 1
$heap_owners(H, HOBJECT n_old) = 1
$heap_owners(H, HOBJECT n_prefix) = 2
$heap_owners(H, HOBJECT n_pending) = 1
$heap_owners(H, HCELL n_prefix_cell) = 1
$call_descriptors_valid(S)
S_scope = $restore_frame(S)
S_scope.CURRENT = eps
S_scope.FRAMES = eps
S_scope.ORIGIN = (pclosurecall.SITE)
S_scope.TODO = (DESTRUCTOR_RESULT pdestructorcall_child) :: ptask_cleanup_tail*
$instance_storage_valid(S_scope, pinstancestorage)
$closure_call_copy_cleanup_exit(S_scope) = ((pdestructorcall_child, pdestructionoperation))
S_scope.DESTRUCTION.CALLS = pdestructorcall_child :: pdestructorcall_tail*
S_scope.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*
pdestructionoperation_new = pdestructionoperation[.COMPLETION = EXITED 53]
pdestructorcall_new = pdestructorcall_child[.OPERATION = (pdestructionoperation_new)]
PhpStep: S ~> S_raw
S_raw.COMPLETION = NORMAL
S_raw.EXITSTATUS = 53
S_raw.CURRENT = eps
S_raw.FRAMES = eps
S_raw.ORIGIN = S_scope.ORIGIN
S_raw.TODO = (DESTRUCTOR_RESULT pdestructorcall_new) :: $destructor_operation_tasks(ptask_cleanup_tail*, pdestructionoperation, pdestructionoperation_new)
(INSTANCE_STORAGE_STEP pinstancestorage) <- S_raw.TODO
(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_new) <- S_raw.TODO
~((DESTRUCTOR_OPERATION_EXIT pdestructionoperation) <- S_raw.TODO)
S_raw.DESTRUCTION.CALLS = pdestructorcall_new :: pdestructorcall_tail*
S_raw.DESTRUCTION.OPERATIONS = pdestructionoperation_new :: pdestructionoperation_tail*
S_raw.DESTRUCTION.CLEANUPS = S_scope.DESTRUCTION.CLEANUPS
S_raw.DESTRUCTION.RELEASES = S_scope.DESTRUCTION.RELEASES
S_raw.CLOSURECALLRETAINED = eps
S_raw.ERRORHANDLER.CALLBACK = eps
S_raw.EVENTS = S.EVENTS
S_changed = $literal_reference_debt_step(S, $sensitive_trace_freeze($source_exception_transition(S, $throwable_transition(S, S_raw))))
H_changed = $heap_graph(S_changed)
$heap_valid(H_changed)
$heap_owners(H_changed, HOBJECT n_retval) = 1
$heap_owners(H_changed, HOBJECT n_child) = 2
S_changed.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_receiver) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_receiver) :: S_raw.TODO
S_changed.DESTRUCTION.RELEASES = pdestructionrelease_receiver :: S_raw.DESTRUCTION.RELEASES
pdestructionoperation_receiver.SOURCE = EXIT_UNWIND 53
pdestructionoperation_receiver.COMPLETION = NORMAL
pdestructionoperation_receiver.PENDING = eps
(HOBJECT n_child) <- $destruction_job_nodes(pdestructionrelease_receiver.JOBS)
$call_descriptors_valid(S_changed)
S_pause = $drive(S, 0)
S_pause.COMPLETION = BUDGET
S_pause[.COMPLETION = NORMAL] = S
S_api_reached = $api_seek(S, 128)
S_api_reached.COMPLETION = NORMAL \/ S_api_reached.COMPLETION = BUDGET
S_api = S_api_reached[.COMPLETION = NORMAL]
S_api.EXITSTATUS = 53
S_api.CLOSURECALLRETAINED = [pclosurebinding]
S_api.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: [EXIT_UNWIND 53]
pdestructionrelease.JOBS = $destruction_values([HCELL n_prefix_cell, HOBJECT n_maker, HOBJECT n_prefix, HOBJECT n_pending, HOBJECT n_source])
S_api.DESTRUCTION.CALLS = eps
S_api.DESTRUCTION.OPERATIONS = eps
S_api.DESTRUCTION.CLEANUPS = eps
S_api.DESTRUCTION.ABANDONED = eps
S_api.ERRORHANDLER.CALLBACK = (perrorcall.CALLBACK)
S_api.EVENTS = S.EVENTS
~((HOBJECT n_retval) <- S_api.ALLOCATIONS)
~((HOBJECT n_child) <- S_api.ALLOCATIONS)
$weakref_get(S_api, n_weak_retval) = PNULL
$weakref_get(S_api, n_weak_child) = PNULL
$closure_call_retained_valid(S_api)
H_api = $heap_graph(S_api)
$heap_valid(H_api)
$heap_owners(H_api, HOBJECT n_copy) = 1
$heap_owners(H_api, HOBJECT n_capture) = 2
$heap_owners(H_api, HOBJECT n_maker) = 2
$heap_owners(H_api, HOBJECT n_prefix) = 2
$heap_owners(H_api, HOBJECT n_pending) = 1
$call_descriptors_valid(S_api)
S_done = $drive(S, 4000)
$drive(S_api, 4000) = S_done
S_done.COMPLETION = EXITED 53
S_done.EXITSTATUS = 53
S_done.SHUTDOWN.PHASE = SHUTDOWN_DONE
S_done.TODO = eps
S_done.CURRENT = eps
S_done.FRAMES = eps
S_done.HELD = eps
S_done.CLOSURECALLRETAINED = [pclosurebinding]
S_done.DESTRUCTION.CALLS = eps
S_done.DESTRUCTION.OPERATIONS = eps
S_done.DESTRUCTION.CLEANUPS = eps
S_done.DESTRUCTION.RELEASES = eps
S_done.DESTRUCTION.ABANDONED = eps
~$closure_call_copy_created(S_done.OBJECTS, n_copy)
~((HOBJECT n_retval) <- S_done.ALLOCATIONS)
~((HOBJECT n_child) <- S_done.ALLOCATIONS)
~((HOBJECT n_source) <- S_done.ALLOCATIONS)
~((HOBJECT n_old) <- S_done.ALLOCATIONS)
~((HOBJECT n_prefix) <- S_done.ALLOCATIONS)
~((HOBJECT n_pending) <- S_done.ALLOCATIONS)
~((HCELL n_prefix_cell) <- S_done.ALLOCATIONS)
H_done = $heap_graph(S_done)
$heap_valid(H_done)
$heap_owners(H_done, HOBJECT n_copy) = 1
$heap_owners(H_done, HOBJECT n_capture) = 1
$heap_owners(H_done, HOBJECT n_maker) = 1
$closure_call_retained_valid(S_done)
$call_descriptors_valid(S_done)
'''.splitlines() if line.strip()]
CASES = {'i105-real-child-integer-reexit-independent': {'source': ROW['source'], 'stage': STAGE, 'checks': CHECKS}}

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
