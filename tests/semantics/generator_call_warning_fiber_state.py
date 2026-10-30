#!/usr/bin/env python3
"""Check copied static ownership while a reference warning is parked in a Fiber."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_call_warning_fiber_cases.json')
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

COMMON = r'''
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
S.ACTIVEFIBER = eps
S.FIBERCALLERS = eps
S.GENERATORINPUTS = eps
S.GC.ACTIVE = eps
pfiber.VM = (pfibervm)
pfibervm.CURRENT = (pcallcontext_handler)
pfibervm.FRAMES = pframe_emit :: pframe_tail*
pframe_emit.CONTEXT = (pcallcontext_run)
pframe_emit.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_emit*
perrorcall.RESUME = CLOSURE_CALL_COPY_REFERENCE pclosurecall n_copy n_done pnamedargs n_base
n_done = 0
pnamedargs = {SLOTS eps, NAMED eps}
perrorcall.TARGET = (pcallcontext_handler.TARGET)
perrorcall.LEVEL = 2
perrorcall.SITE = pclosurecall.SITE
perrorcall.LINE = pclosurecall.LINE
pcallcontext_handler.INSTANCE = eps
pcallcontext_handler.RECEIVER = eps
pcallcontext_handler.WRAPPER = eps
pcallcontext_handler.ARGC = 4
pclosurecall.SOURCE = n_source
pclosurecall.FIRST = (POBJECT n_maker)
pclosurecall.RECEIVER = (n_maker)
pclosurecall.RAW = [(KINT 1, KNOWN (POBJECT n_token))]
pclosurecall.SENT = {SLOTS ([NAMED_SENT (KNOWN (POBJECT n_token))]), NAMED eps}
pclosurecall.INDEX = 2
pclosurecall.ERROR = eps
pclosurecall.PACKS = eps
$(n_source < n_copy)
(HOBJECT n_source) <- S.ALLOCATIONS
(HOBJECT n_copy) <- S.ALLOCATIONS
(HOBJECT n_maker) <- S.ALLOCATIONS
(HOBJECT n_token) <- S.ALLOCATIONS
$target_function(S, CLOSURE_TARGET n_copy) = (pfunction)
pfunction.ORIGIN = porigin_function
pcallcontext_handler.FUNCTION =/= porigin_function
$function_generator(S, pfunction)
~pfunction.SIGNATURE.BYREF
$call_parameter_at(pfunction.SIGNATURE.PARAMETERS, 0) = (psparam)
psparam.BYREF
psparam.NAME = $ptascii("token")
$target_receiver(S, CLOSURE_TARGET n_source) = (n_old)
n_old =/= n_maker
S.OBJECTS[n_maker] = INSTANCE porigin_maker
S.OBJECTS[n_old] = INSTANCE porigin_old
(HOBJECT n_old) <- S.ALLOCATIONS
$closure_call_copy_row(S, n_copy) = (pclosurebinding)
pclosurebinding.OBJECT = n_copy
pclosurebinding.SOURCE = n_source
pclosurebinding.SITE = pclosurecall.SITE
pclosurebinding.RECEIVER = (n_maker)
pclosurebinding.LEXICAL = (porigin_maker)
pclosurebinding.CALLED = (porigin_maker)
$closure_call_copy_site(S, pclosurecall.SITE)
$lookup(S.ENV, $ptascii("source")) = (n_source_cell)
S.STORE[n_source_cell] = DEFINED PNULL
$lookup(S.ENV, $ptascii("maker")) = (n_maker_cell)
S.STORE[n_maker_cell] = DEFINED PNULL
$lookup(S.ENV, $ptascii("g")) = (n_g_cell)
S.STORE[n_g_cell] = DEFINED PNULL
$lookup(S.ENV, $ptascii("warningCount")) = (n_count)
S.STORE[n_count] = DEFINED (PINT 1)
$lookup(S.ENV, $ptascii("seed")) = eps
$lookup(S.ENV, $ptascii("probe")) = eps
$lookup(S.ENV, $ptascii("old")) = eps
$lookup(S.ENV, $ptascii("weakSource")) = (n_weak_source_cell)
S.STORE[n_weak_source_cell] = DEFINED (POBJECT n_weak_source)
$weakref_get(S, n_weak_source) = POBJECT n_source
$lookup(S.ENV, $ptascii("weakOld")) = (n_weak_old_cell)
S.STORE[n_weak_old_cell] = DEFINED (POBJECT n_weak_old)
$weakref_get(S, n_weak_old) = POBJECT n_old
$lookup(S.ENV, $ptascii("weakToken")) = (n_weak_token_cell)
S.STORE[n_weak_token_cell] = DEFINED (POBJECT n_weak_token)
$weakref_get(S, n_weak_token) = POBJECT n_token
S.ERRORHANDLER.CALLBACK = eps
$task_nodes(perrorcall.RESUME) = [HOBJECT n_copy, HOBJECT n_maker, HOBJECT n_token, HOBJECT n_source]
$heap_count(HOBJECT n_copy, $fiber_vm_nodes(pfibervm)) = 1
$heap_count(HOBJECT n_source, $fiber_vm_nodes(pfibervm)) = 1
$heap_count(HOBJECT n_maker, $fiber_vm_nodes(pfibervm)) = 1
$heap_count(HOBJECT n_token, $fiber_vm_nodes(pfibervm)) = 1
S_live = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]
$generator_resume_ids(S_live.TODO) = eps
$generator_saved_ids(S_live.FRAMES) = eps
$fiber_generator_transfer(S_live)
$fiber_transfer_domain(S_live)
$closure_call_copy_warning_context(S_live, pcallcontext_handler)
$ordinary_internal_callback_context(S_live, pcallcontext_handler)
$error_context_call(S_live, pcallcontext_handler) = (perrorcall)
$call_current_valid(S_live)
$call_frames_valid(S_live, S_live.FRAMES)
S_emit = $api_saved_frame_scope($constant_frame_scope(S_live, pframe_emit, pframe_tail*), pframe_emit, pframe_tail*)
$closure_call_copy_reference_valid(S_emit, pclosurecall, n_copy, n_done, pnamedargs, n_base)
$call_task_valid(S_emit, perrorcall.RESUME)
$error_entered_call_valid(S_emit, perrorcall)
perrorcall.MESSAGE = $closure_call_reference_message(S_emit, pclosurecall, n_done)
$lookup(S_emit.ENV, $ptascii("source")) = (n_source_cell)
$lookup(S_emit.ENV, $ptascii("maker")) = (n_maker_cell)
H = $heap_graph(S)
$heap_owners(H, HOBJECT n_copy) = 1
$heap_owners(H, HOBJECT n_source) = 1
$heap_owners(H, HOBJECT n_old) = 1
$heap_owners(H, HOBJECT n_maker) = 2
$heap_owners(H, HOBJECT n_token) = 1
$heap_valid(H)
pclosurecall_bad_line = pclosurecall[.LINE = 0]
~$closure_call_copy_reference_valid(S_emit, pclosurecall_bad_line, n_copy, n_done, pnamedargs, n_base)
pclosurecall_bad_first = pclosurecall[.FIRST = (POBJECT n_old)]
~$closure_call_copy_reference_valid(S_emit, pclosurecall_bad_first, n_copy, n_done, pnamedargs, n_base)
S_dead_copy = S_emit[.ALLOCATIONS = $destruction_node_delete(S_emit.ALLOCATIONS, HOBJECT n_copy)]
~$closure_call_copy_reference_valid(S_dead_copy, pclosurecall, n_copy, n_done, pnamedargs, n_base)
S_dead_source = S_emit[.ALLOCATIONS = $destruction_node_delete(S_emit.ALLOCATIONS, HOBJECT n_source)]
~$closure_call_copy_reference_valid(S_dead_source, pclosurecall, n_copy, n_done, pnamedargs, n_base)
S_dead_maker = S_emit[.ALLOCATIONS = $destruction_node_delete(S_emit.ALLOCATIONS, HOBJECT n_maker)]
~$closure_call_copy_reference_valid(S_dead_maker, pclosurecall, n_copy, n_done, pnamedargs, n_base)
perrorcall_wrong = perrorcall[.TARGET = (CLOSURE_TARGET n_source)]
pframe_wrong = pframe_emit[.TODO = (ERROR_HANDLER_RESULT perrorcall_wrong) :: ptask_emit*]
S_wrong = S_live[.FRAMES = pframe_wrong :: pframe_tail*]
~$closure_call_copy_warning_context(S_wrong, pcallcontext_handler)
~$closure_call_copy_warning_context(S_live[.FRAMES = eps], pcallcontext_handler)
S_zero = $drive_steps(S, 0)
S_zero.COMPLETION = BUDGET
S_zero.TODO = S.TODO
S_zero.OBJECTS = S.OBJECTS
S_zero.ALLOCATIONS = S.ALLOCATIONS
'''

REAL = checks(COMMON) + checks(r'''
S.OBJECTS[n_source] = REALCLOSURE porigin_function eps pstaticcell_sources*
S.OBJECTS[n_copy] = REALCLOSURE porigin_function eps pstaticcell_copies*
~$closure_static(S, pfunction)
pstaticcell_sources* = [pstaticcell_source]
pstaticcell_copies* = [pstaticcell_copy]
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
$heap_owners(H, HCELL n_source_counter) = 1
$heap_owners(H, HCELL n_copy_counter) = 1
$heap_count(HCELL n_copy_counter, $node_children(S, HOBJECT n_copy)) = 1
$closure_call_copy_binding(S, pclosurebinding)
S.CLOSUREBINDINGS = [pclosurebinding]
$object_name(S, n_old) = $ptascii("Origin97A")
$object_name(S, n_maker) = $ptascii("Active97A")
S_alias = S_emit[.STORE = $set_cell(S_emit.STORE, n_copy_counter, DEFINED (POBJECT n_token))]
$closure_call_copy_result_valid(S_alias, pclosurecall, n_copy)
$closure_call_task_valid(S_alias, pclosurecall)
~$closure_call_copy_forward_valid(S_alias, pclosurecall, n_copy, 1, {SLOTS ([NAMED_SENT (REFERENCE n_copy_counter)]), NAMED eps}, 0)
pclosurebinding_old = pclosurebinding[.RECEIVER = (n_old)][.LEXICAL = (porigin_old)][.CALLED = (porigin_old)]
S_old = S_emit[.CLOSUREBINDINGS = [pclosurebinding_old]]
$closure_call_copy_binding(S_old, pclosurebinding_old)
~$closure_call_copy_reference_valid(S_old, pclosurecall, n_copy, n_done, pnamedargs, n_base)
''')

FAKE = checks(COMMON) + checks(r'''
S.OBJECTS[n_source] = METHODCLOSURE porigin_function porigin_capture porigin_requested pmethodcapture?
S.OBJECTS[n_copy] = BOUNDFAKECLOSURE pboundfake_copy
pboundfake_copy.SOURCE = n_source
pboundfake_copy.SITE = pclosurecall.SITE
pboundfake_copy.SCOPE = BIND_CLASS porigin_maker
pboundfake_copy.CALLED = BIND_CLASS porigin_maker
pboundfake_copy.RECEIVER = (n_maker)
porigin_old = porigin_maker
S.CLOSUREBINDINGS = eps
$closure_call_fake_method(S, n_source, pfunction)
$class_method_origin(S.CLASSES, porigin_function) = (pmethoddesc)
~pmethoddesc.STATIC
$closure_call_fake_copy_binding(S, pboundfake_copy)
$bound_fake_valid(S, n_copy)
$node_children(S, HOBJECT n_copy) = [HOBJECT n_maker]
S.STATICS = [pstaticcell_counter]
n_counter = pstaticcell_counter.CELL
$(n_counter < n_base)
n_counter <- S.REFCELLS
S.STORE[n_counter] = DEFINED (PINT 2)
$static_roots(S.STATICS) = [HCELL n_counter]
$heap_owners(H, HCELL n_counter) = 1
$object_name(S, n_old) = $ptascii("Base97B")
$object_name(S, n_maker) = $ptascii("Base97B")
S_alias = S_emit[.STORE = $set_cell(S_emit.STORE, n_counter, DEFINED (POBJECT n_token))]
$closure_call_copy_result_valid(S_alias, pclosurecall, n_copy)
$closure_call_task_valid(S_alias, pclosurecall)
~$closure_call_copy_forward_valid(S_alias, pclosurecall, n_copy, 1, {SLOTS ([NAMED_SENT (REFERENCE n_counter)]), NAMED eps}, 0)
pboundfake_old = pboundfake_copy[.RECEIVER = (n_old)]
S_old = S_emit[.OBJECTS = $object_set(S_emit.OBJECTS, n_copy, BOUNDFAKECLOSURE pboundfake_old)]
$closure_call_fake_copy_binding(S_old, pboundfake_old)
~$closure_call_copy_reference_valid(S_old, pclosurecall, n_copy, n_done, pnamedargs, n_base)
''')

CASES = {
    'i97-real-copy-warning-parked-statics': {'source': ROWS['i97-real-copy-reference-warning-fiber-isolated-static']['source'], 'stage': PARK_STAGE, 'checks': REAL},
    'i97-fake-copy-warning-parked-statics': {'source': ROWS['i97-fake-copy-reference-warning-fiber-shared-static']['source'], 'stage': PARK_STAGE, 'checks': FAKE},
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
