#!/usr/bin/env python3
"""Check early real static copies during an owning warning-retval destructor."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_call_warning_retval_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {r['id']: r for r in json.loads(INPUT_BYTES[CATALOG])}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


PARK_STAGE = (
    'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
    '-- if pconfigcall.KIND = INTRINSIC_FIBER_RESUME '
    '-- if pconfigcall.OWNER = (n_fiber) '
    '-- if S.ACTIVEFIBER = eps '
    '-- if S.OBJECTS[n_fiber] = FIBER pfiber '
    '-- if pfiber.STATUS = FIBER_SUSPENDED')

PARK = checks(r'''
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
S.ACTIVEFIBER = eps
S.GENERATORINPUTS = eps
S.GC.ACTIVE = eps
pfiber.VM = (pfibervm)
pfibervm.CURRENT = (pcallcontext_dtor)
pfibervm.FRAMES = pframe_emit :: pframe_tail*
pframe_emit.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: ptask_emit*
pframe_emit.CONTEXT = (pcallcontext_run)
pfibervm.DESTRUCTORCLEANUPS = pdestructioncleanup :: pdestructioncleanup_tail*
pdestructioncleanup.SOURCE = ERROR_HANDLER_RESULT perrorcall
~pdestructioncleanup.RELEASED
pdestructioncleanup.CALLER = (pcallcontext_run)
perrorcall.RESUME = CLOSURE_CALL_COPY_REFERENCE pclosurecall n_copy n_done pnamedargs n_base
n_done = 0
pnamedargs = {SLOTS eps, NAMED eps}
pfibervm.DESTRUCTOROPERATIONS = pdestructionoperation :: pdestructionoperation_tail*
pdestructionoperation.SOURCE = ERROR_HANDLER_RESULT perrorcall
pdestructionoperation.CLEANUP = (pdestructioncleanup)
pdestructorcall.OPERATION = (pdestructionoperation)
pfibervm.DESTRUCTORCALLS = pdestructorcall :: pdestructorcall_tail*
pdestructorcall.CALLER = (pcallcontext_run)
pdestructorcall.OBJECT = n_retval
pcallcontext_dtor.TARGET = pdestructorcall.TARGET
pcallcontext_dtor.INSTANCE = eps
pcallcontext_dtor.RECEIVER = (n_retval)
pcallcontext_dtor.WRAPPER = eps
pcallcontext_dtor.ARGC = 0
S.OBJECTS[n_retval] = INSTANCE porigin_retval
(HOBJECT n_retval) <- S.ALLOCATIONS
$object_name(S, n_retval) = $ptascii("Returned98A")
$node_children(S, HOBJECT n_retval) = eps
n_retval <- S.DESTRUCTION.CALLED
pcallcontext_dtor.LEXICAL_CLASS = (porigin_retval)
pcallcontext_dtor.CALLED_CLASS = (porigin_retval)
S.OBJECTS[n_copy] = REALCLOSURE porigin_function eps pstaticcell_copies*
pstaticcell_copies* = [pstaticcell_copy]
$closure_binding_at(S.CLOSUREBINDINGS, n_copy) = (pclosurebinding)
n_source = pclosurebinding.SOURCE
$(n_source < n_copy)
S.OBJECTS[n_source] = REALCLOSURE porigin_function eps pstaticcell_sources*
pstaticcell_sources* = [pstaticcell_source]
pstaticcell_source.ORIGIN = pstaticcell_copy.ORIGIN
n_source_counter = pstaticcell_source.CELL
n_copy_counter = pstaticcell_copy.CELL
n_source_counter =/= n_copy_counter
$(n_source_counter < n_base)
$(n_copy_counter < n_base)
S.STORE[n_source_counter] = DEFINED (PINT 2)
S.STORE[n_copy_counter] = DEFINED (PINT 1)
n_source_counter <- S.REFCELLS
n_copy_counter <- S.REFCELLS
S.STATICS = eps
$target_function(S, CLOSURE_TARGET n_copy) = (pfunction)
pfunction.ORIGIN = porigin_function
$function_generator(S, pfunction)
~pfunction.SIGNATURE.BYREF
~$closure_static(S, pfunction)
$call_parameter_at(pfunction.SIGNATURE.PARAMETERS, 0) = (psparam)
psparam.BYREF
psparam.NAME = $ptascii("token")
pclosurecall.SOURCE = n_source
pclosurecall.SITE = pclosurebinding.SITE
pclosurecall.FIRST = (POBJECT n_maker)
pclosurecall.RECEIVER = (n_maker)
pclosurecall.RAW = [(KINT 1, KNOWN (POBJECT n_token))]
pclosurecall.SENT = {SLOTS ([NAMED_SENT (KNOWN (POBJECT n_token))]), NAMED eps}
pclosurecall.ERROR = eps
pclosurecall.PACKS = eps
pclosurecall.INDEX = 2
pclosurebinding.RECEIVER = (n_maker)
$closure_call_copy_binding(S, pclosurebinding)
$target_receiver(S, CLOSURE_TARGET n_source) = (n_old)
$object_name(S, n_old) = $ptascii("Origin98A")
$object_name(S, n_maker) = $ptascii("Active98A")
$object_name(S, n_token) = $ptascii("Token98A")
(HOBJECT n_source) <- S.ALLOCATIONS
(HOBJECT n_copy) <- S.ALLOCATIONS
(HOBJECT n_old) <- S.ALLOCATIONS
(HOBJECT n_maker) <- S.ALLOCATIONS
(HOBJECT n_token) <- S.ALLOCATIONS
$lookup(S.ENV, $ptascii("source")) = (n_source_cell)
S.STORE[n_source_cell] = DEFINED PNULL
$lookup(S.ENV, $ptascii("maker")) = (n_maker_cell)
S.STORE[n_maker_cell] = DEFINED PNULL
$lookup(S.ENV, $ptascii("g")) = (n_g_cell)
S.STORE[n_g_cell] = DEFINED PNULL
$lookup(S.ENV, $ptascii("warningCount")) = (n_count)
S.STORE[n_count] = DEFINED (PINT 1)
$lookup(S.ENV, $ptascii("probe")) = eps
$lookup(S.ENV, $ptascii("seed")) = eps
$lookup(S.ENV, $ptascii("weakReturned")) = (n_weak_cell)
S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)
$weakref_get(S, n_weak) = POBJECT n_retval
S.ERRORHANDLER.CALLBACK = eps
$task_nodes(ERROR_HANDLER_CLEAN perrorcall) = [HOBJECT n_copy, HOBJECT n_maker, HOBJECT n_token, HOBJECT n_source]
$eager_cleanup_marker(pframe_emit.TODO, ERROR_HANDLER_RESULT perrorcall)
$heap_count(HOBJECT n_copy, $fiber_vm_nodes(pfibervm)) = 1
$heap_count(HOBJECT n_source, $fiber_vm_nodes(pfibervm)) = 1
$heap_count(HOBJECT n_maker, $fiber_vm_nodes(pfibervm)) = 1
$heap_count(HOBJECT n_token, $fiber_vm_nodes(pfibervm)) = 1
S_live = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]
S_live.DESTRUCTION.CALLS = pfibervm.DESTRUCTORCALLS
S_live.DESTRUCTION.RELEASES = pfibervm.DESTRUCTORRELEASES
S_live.DESTRUCTION.FRAMES = pfibervm.DESTRUCTORFRAMES
S_live.DESTRUCTION.OPERATIONS = pfibervm.DESTRUCTOROPERATIONS
S_live.DESTRUCTION.CLEANUPS = pfibervm.DESTRUCTORCLEANUPS
$generator_resume_ids(S_live.TODO) = eps
$generator_saved_ids(S_live.FRAMES) = eps
$fiber_generator_transfer(S_live)
$fiber_transfer_domain(S_live)
$destructor_call_live(S_live, pdestructorcall)
$eager_cleanup_valid(S_live, pdestructioncleanup)
$call_current_valid(S_live)
$call_frames_valid(S_live, S_live.FRAMES)
~$closure_call_copy_warning_context(S_live, pcallcontext_dtor)
S_emit = $eager_cleanup_caller_scope(S_live, pdestructioncleanup)
S_emit.CURRENT = (pcallcontext_run)
S_emit.ORIGIN = (pclosurecall.SITE)
$closure_call_copy_reference_valid(S_emit, pclosurecall, n_copy, n_done, pnamedargs, n_base)
$error_cleanup_valid(S_emit, perrorcall)
$eager_operation_source_valid(S_emit, pdestructionoperation)
H = $heap_graph(S)
$heap_owners(H, HOBJECT n_retval) = 2
$heap_owners(H, HOBJECT n_copy) = 1
$heap_owners(H, HOBJECT n_source) = 1
$heap_owners(H, HOBJECT n_old) = 1
$heap_owners(H, HOBJECT n_maker) = 2
$heap_owners(H, HOBJECT n_token) = 1
$heap_owners(H, HCELL n_source_counter) = 1
$heap_owners(H, HCELL n_copy_counter) = 1
$heap_valid(H)
S_no_cleanup = S_emit[.DESTRUCTION.CLEANUPS = eps]
~$error_cleanup_valid(S_no_cleanup, perrorcall)
~$eager_operation_source_valid(S_no_cleanup, pdestructionoperation)
S_dead_source = S_emit[.ALLOCATIONS = $destruction_node_delete(S_emit.ALLOCATIONS, HOBJECT n_source)]
~$closure_call_copy_reference_valid(S_dead_source, pclosurecall, n_copy, n_done, pnamedargs, n_base)
S_dead_copy = S_emit[.ALLOCATIONS = $destruction_node_delete(S_emit.ALLOCATIONS, HOBJECT n_copy)]
~$closure_call_copy_reference_valid(S_dead_copy, pclosurecall, n_copy, n_done, pnamedargs, n_base)
S_alias = S_emit[.STORE = $set_cell(S_emit.STORE, n_copy_counter, DEFINED (POBJECT n_token))]
$closure_call_copy_result_valid(S_alias, pclosurecall, n_copy)
$closure_call_task_valid(S_alias, pclosurecall)
~$closure_call_copy_forward_valid(S_alias, pclosurecall, n_copy, 1, {SLOTS ([NAMED_SENT (REFERENCE n_copy_counter)]), NAMED eps}, 0)
S_zero = $drive_steps(S, 0)
S_zero.COMPLETION = BUDGET
S_zero.TODO = S.TODO
S_zero.OBJECTS = S.OBJECTS
S_zero.ALLOCATIONS = S.ALLOCATIONS
''')

CASES = {
    'i98-real-warning-retval-parked-static': {'source': ROWS['i98-real-call-reference-warning-retval-fiber-static']['source'], 'stage': PARK_STAGE, 'checks': PARK},
}


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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    raise SystemExit(0 if run(parser.parse_args().case) else 1)
