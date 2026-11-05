#!/usr/bin/env python3
"""Reach a string reexit while copied warning retval storage frees sibling fields."""
import hashlib
import json
from pathlib import Path
import subprocess
import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_call_repeated_cleanup_exit_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROW = next(r for r in json.loads(INPUT_BYTES[CATALOG]) if r['id'] == 'i105-fake-copy-child-string-reexit')
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']
STAGE = ('S.TODO = [EXIT_UNWIND 29] -- if S.FRAMES = [pframe_cleanup] '
         '-- if S.CURRENT = (pcallcontext_child) '
         '-- if pcallcontext_child.TARGET = METHOD_TARGET n_child porigin_child '
         '-- if $object_name(S, n_child) = $ptascii("ChildRepeat105A") '
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
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: [EXIT_UNWIND 29]
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
S.EXITSTATUS = 29
S.ACTIVEFIBER = eps
S.SOURCEPENDING = eps
S.CLOSURECALLRETAINED = eps
S.DESTRUCTION.ABANDONED = eps
S.ERRORHANDLER.CALLBACK = eps
S.DESTRUCTION.CALLS = [pdestructorcall_child]
pdestructorcall_child.OBJECT = n_child
pdestructorcall_child.USER
pdestructorcall_child.PENDING = eps
S.DESTRUCTION.OPERATIONS = [pdestructionoperation]
pdestructionoperation.COMPLETION = EXITED 29
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
S.OBJECTS[n_copy] = BOUNDFAKECLOSURE pboundfake
pboundfake.SOURCE = n_source
$target_receiver(S, CLOSURE_TARGET n_source) = (n_old)
$object_name(S, n_maker) = $ptascii("MakerRepeat105A")
$object_name(S, n_old) = $ptascii("MakerRepeat105A")
S.GLOBALTABLE = (psymboltable_global)
$lookup(psymboltable_global.ENV, $ptascii("source")) = (n_source_cell)
S.STORE[n_source_cell] = DEFINED PNULL
$lookup(psymboltable_global.ENV, $ptascii("weakReturn")) = (n_weak_return_cell)
S.STORE[n_weak_return_cell] = DEFINED (POBJECT n_weak_return)
S.OBJECTS[n_weak_return] = WEAKREFERENCE (n_return)
$weakref_get(S, n_weak_return) = PNULL
$object_name(S, n_return) = $ptascii("ReturnRepeat105A")
$lookup(psymboltable_global.ENV, $ptascii("weakChild")) = (n_weak_child_cell)
S.STORE[n_weak_child_cell] = DEFINED (POBJECT n_weak_child)
$weakref_get(S, n_weak_child) = POBJECT n_child
$lookup(psymboltable_global.ENV, $ptascii("weakAfter")) = (n_weak_after_cell)
S.STORE[n_weak_after_cell] = DEFINED (POBJECT n_weak_after)
$weakref_get(S, n_weak_after) = POBJECT n_after
$object_name(S, n_after) = $ptascii("AfterRepeat105A")
$instance_storage_for(S, n_return) = (pinstancestorage)
pinstancestorage.CALLER = eps
pinstancestorage.ORIGIN = (pclosurecall.SITE)
pinstancestorage.CONSTCONTEXT = eps
pinstancestorage.USER
pinstancestorage.NEXT = 1
|pinstancestorage.SLOTS| = 2
pinstancestorage.SLOTS[0].STATE = PROP_VALUE (DIRECT (POBJECT n_child))
pinstancestorage.SLOTS[1].STATE = PROP_VALUE (DIRECT (POBJECT n_after))
$objectprops_at(S.OBJECTPROPS, n_return) = (ppropertyslot*)
ppropertyslot*[0].STATE = PROP_UNSET
ppropertyslot*[1].STATE = PROP_VALUE (DIRECT (POBJECT n_after))
(INSTANCE_STORAGE_STEP pinstancestorage) <- ptask_cleanup_tail*
H = $heap_graph(S)
$heap_valid(H)
$heap_owners(H, HOBJECT n_return) = 1
$heap_owners(H, HOBJECT n_child) = 2
$heap_owners(H, HOBJECT n_after) = 1
$heap_owners(H, HOBJECT n_copy) = 1
$heap_owners(H, HOBJECT n_maker) = 2
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
$closure_call_copy_cleanup_exit_tail(S_scope, [(INSTANCE_STORAGE_STEP pinstancestorage), (DESTRUCTOR_OPERATION_EXIT pdestructionoperation), (ERROR_HANDLER_CLEAN perrorcall)], pdestructionoperation, perrorcall)
~$closure_call_copy_cleanup_exit_tail(S_scope, [(INSTANCE_STORAGE_STEP pinstancestorage[.HANDLE = 0]), (DESTRUCTOR_OPERATION_EXIT pdestructionoperation), (ERROR_HANDLER_CLEAN perrorcall)], pdestructionoperation, perrorcall)
~$closure_call_copy_cleanup_exit_tail(S_scope, [(INSTANCE_STORAGE_STEP pinstancestorage[.NEXT = 3]), (DESTRUCTOR_OPERATION_EXIT pdestructionoperation), (ERROR_HANDLER_CLEAN perrorcall)], pdestructionoperation, perrorcall)
~$closure_call_copy_cleanup_exit_tail(S_scope, [(INSTANCE_STORAGE_STEP pinstancestorage[.ORIGIN = eps]), (DESTRUCTOR_OPERATION_EXIT pdestructionoperation), (ERROR_HANDLER_CLEAN perrorcall)], pdestructionoperation, perrorcall)
$closure_call_copy_cleanup_exit(S_scope) = ((pdestructorcall_child, pdestructionoperation))
S_scope.DESTRUCTION.CALLS = pdestructorcall_child :: pdestructorcall_tail*
S_scope.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*
pdestructionoperation_new = pdestructionoperation[.COMPLETION = EXITED 29]
pdestructorcall_new = pdestructorcall_child[.OPERATION = (pdestructionoperation_new)]
PhpStep: S ~> S_raw
S_raw.COMPLETION = NORMAL
S_raw.EXITSTATUS = 29
S_raw.CURRENT = eps
S_raw.FRAMES = eps
S_raw.ORIGIN = S_scope.ORIGIN
S_raw.TODO = (DESTRUCTOR_RESULT pdestructorcall_new) :: $destructor_operation_tasks(ptask_cleanup_tail*, pdestructionoperation, pdestructionoperation_new)
(INSTANCE_STORAGE_STEP pinstancestorage) <- S_raw.TODO
(DESTRUCTOR_OPERATION_EXIT pdestructionoperation_new) <- S_raw.TODO
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
$heap_owners(H_changed, HOBJECT n_return) = 1
$heap_owners(H_changed, HOBJECT n_child) = 1
$heap_owners(H_changed, HOBJECT n_after) = 1
$call_descriptors_valid(S_changed)
S_pause = $drive(S, 0)
S_pause.COMPLETION = BUDGET
S_pause[.COMPLETION = NORMAL] = S
S_api_reached = $api_seek(S, 128)
S_api_reached.COMPLETION = NORMAL \/ S_api_reached.COMPLETION = BUDGET
S_api = S_api_reached[.COMPLETION = NORMAL]
S_api.EXITSTATUS = 29
S_api.CLOSURECALLRETAINED = [pclosurebinding]
S_api.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: [EXIT_UNWIND 29]
pdestructionrelease.JOBS = $destruction_values([HCELL n_prefix_cell, HOBJECT n_maker, HOBJECT n_prefix, HOBJECT n_pending, HOBJECT n_source])
S_api.DESTRUCTION.CALLS = eps
S_api.DESTRUCTION.OPERATIONS = eps
S_api.DESTRUCTION.CLEANUPS = eps
S_api.DESTRUCTION.ABANDONED = eps
S_api.ERRORHANDLER.CALLBACK = (perrorcall.CALLBACK)
S_api.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("AFTER|")]
~((HOBJECT n_return) <- S_api.ALLOCATIONS)
~((HOBJECT n_child) <- S_api.ALLOCATIONS)
~((HOBJECT n_after) <- S_api.ALLOCATIONS)
$weakref_get(S_api, n_weak_return) = PNULL
$weakref_get(S_api, n_weak_child) = PNULL
$weakref_get(S_api, n_weak_after) = PNULL
n_after <- S_api.DESTRUCTION.CALLED
$closure_call_retained_valid(S_api)
H_api = $heap_graph(S_api)
$heap_valid(H_api)
$heap_owners(H_api, HOBJECT n_copy) = 1
$heap_owners(H_api, HOBJECT n_maker) = 2
$heap_owners(H_api, HOBJECT n_prefix) = 2
$heap_owners(H_api, HOBJECT n_pending) = 1
$call_descriptors_valid(S_api)
S_done = $drive(S, 4000)
$drive(S_api, 4000) = S_done
S_done.COMPLETION = EXITED 29
S_done.EXITSTATUS = 29
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
~((HOBJECT n_return) <- S_done.ALLOCATIONS)
~((HOBJECT n_child) <- S_done.ALLOCATIONS)
~((HOBJECT n_after) <- S_done.ALLOCATIONS)
~((HOBJECT n_source) <- S_done.ALLOCATIONS)
~((HOBJECT n_old) <- S_done.ALLOCATIONS)
~((HOBJECT n_prefix) <- S_done.ALLOCATIONS)
~((HOBJECT n_pending) <- S_done.ALLOCATIONS)
~((HCELL n_prefix_cell) <- S_done.ALLOCATIONS)
H_done = $heap_graph(S_done)
$heap_valid(H_done)
$heap_owners(H_done, HOBJECT n_copy) = 1
$heap_owners(H_done, HOBJECT n_maker) = 1
$closure_call_retained_valid(S_done)
$call_descriptors_valid(S_done)
'''.splitlines() if line.strip()]
CASES = {'i105-fake-child-string-reexit-owner': {'source': ROW['source'], 'stage': STAGE, 'checks': CHECKS}}

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
    report.update(author_inputs={str(p): hashlib.sha256(data).hexdigest() for p, data in INPUT_BYTES.items()},
                  author_inputs_stable=stable, head_stable=head_stable,
                  passed=passed and stable and head_stable)
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if report['passed'] else 1)
