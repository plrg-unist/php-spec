#!/usr/bin/env python3
"""Check the saved warning cursor and detached reference-formal snapshot."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_call_warning_fiber_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROW = next(r for r in json.loads(INPUT_BYTES[CATALOG])
           if r['id'] == 'i97-call-reference-warning-fiber-alias-snapshot-independent')
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256'] == '248975edebac7540dd8c0e14f282e3eee831653c01f564ef12ae984cca259ee6'


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


COPY = r'''

S.OBJECTS[n_copy] = REALCLOSURE porigin_function eps eps
(HOBJECT n_copy) <- S.ALLOCATIONS
$closure_binding_at(S.CLOSUREBINDINGS, n_copy) = (pclosurebinding)
pclosurebinding.OBJECT = n_copy
n_source = pclosurebinding.SOURCE
$(n_source < n_copy)
S.OBJECTS[n_source] = REALCLOSURE porigin_function eps eps
(HOBJECT n_source) <- S.ALLOCATIONS
$function_at(S.CLOSURETEMPLATES, porigin_function) = (pfunction)
pfunction.SIGNATURE.BYREF
$call_parameter_at(pfunction.SIGNATURE.PARAMETERS, 0) = (psparam)
psparam.BYREF
psparam.NAME = $ptascii("slot")
$function_generator(S, pfunction)
~$closure_static(S, pfunction)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Maker97R"))) = (porigin_maker)
pclosurebinding.LEXICAL = (porigin_maker)
pclosurebinding.CALLED = (porigin_maker)
pclosurebinding.RECEIVER = (n_maker)
S.OBJECTS[n_maker] = INSTANCE porigin_maker
(HOBJECT n_maker) <- S.ALLOCATIONS
$closure_scope_at(S.CLOSURESCOPES, n_copy) = eps
$closure_call_copy_site(S, pclosurebinding.SITE)
$closure_call_copy_binding(S, pclosurebinding)
$closure_binding_source_valid(S, pclosurebinding)
$closure_callable(S, n_copy)
$node_children(S, HOBJECT n_copy) = [HOBJECT n_maker]
$target_receiver(S, CLOSURE_TARGET n_copy) = (n_maker)
$target_receiver(S, CLOSURE_TARGET n_source) = eps
$target_function(S, CLOSURE_TARGET n_source) = (pfunction)
$call_selected_valid(S, CLOSURE_TARGET n_copy, (pclosurebinding.SITE))
pclosurecall.SOURCE = n_source
pclosurecall.SITE = pclosurebinding.SITE
pclosurecall.FIRST = (POBJECT n_maker)
pclosurecall.RECEIVER = (n_maker)
pclosurecall.RAW = [(KINT 1, KNOWN (POBJECT n_token))]
pclosurecall.INDEX = 2
pclosurecall.ERROR = eps
pclosurecall.PACKS = eps
$object_name(S, n_token) = $ptascii("Token97R")
'''

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
S.GENERATORINPUTS = eps
S.GC.ACTIVE = eps
pfiber.VM = (pfibervm)
pfibervm.CURRENT = (pcallcontext_handler)
pfibervm.FRAMES = pframe_emit :: pframe_tail*
pframe_emit.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_emit*
perrorcall.RESUME = CLOSURE_CALL_COPY_REFERENCE pclosurecall n_copy n_done pnamedargs n_base
n_done = 0
pnamedargs = {SLOTS eps, NAMED eps}
perrorcall.LEVEL = 2
perrorcall.TARGET = (pcallcontext_handler.TARGET)
''') + checks(COPY) + checks(r'''

pclosurecall.SENT = {SLOTS ([NAMED_SENT (KNOWN (POBJECT n_token))]), NAMED eps}
pframe_emit.LOCALS = (psymboltable_emit)
$lookup(psymboltable_emit.ENV, $ptascii("alias")) = (n_root)
S.STORE[n_root] = DEFINED (PINT 97)
n_root <- S.REFCELLS
$(n_root < n_base)
$lookup(S.ENV, $ptascii("alias")) = eps
$lookup(S.ENV, $ptascii("slot")) = eps
$lookup(S.ENV, $ptascii("source")) = (n_source_cell)
S.STORE[n_source_cell] = DEFINED PNULL
$lookup(S.ENV, $ptascii("maker")) = (n_maker_cell)
S.STORE[n_maker_cell] = DEFINED PNULL
$lookup(S.ENV, $ptascii("g")) = (n_g_cell)
S.STORE[n_g_cell] = DEFINED PNULL
S.ERRORHANDLER.CALLBACK = eps
$heap_count(HOBJECT n_copy, $fiber_vm_nodes(pfibervm)) = 1
$heap_count(HOBJECT n_source, $fiber_vm_nodes(pfibervm)) = 1
$heap_count(HOBJECT n_maker, $fiber_vm_nodes(pfibervm)) = 1
$heap_count(HOBJECT n_token, $fiber_vm_nodes(pfibervm)) = 1
$task_nodes(perrorcall.RESUME) = [HOBJECT n_copy, HOBJECT n_maker, HOBJECT n_token, HOBJECT n_source]
$api_pending_task(perrorcall.RESUME)
$api_pending_task(ERROR_HANDLER_RESULT perrorcall)
S_live = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]
$lookup(S_live.ENV, $ptascii("slot")) = eps
$generator_resume_ids(S_live.TODO) = eps
$generator_saved_ids(S_live.FRAMES) = eps
$fiber_generator_transfer(S_live)
$fiber_transfer_domain(S_live)
$closure_call_copy_warning_context(S_live, pcallcontext_handler)
$ordinary_internal_callback_context(S_live, pcallcontext_handler)
$error_context_call(S_live, pcallcontext_handler) = (perrorcall)
$call_current_valid(S_live)
S_emit = $api_saved_frame_scope($constant_frame_scope(S_live, pframe_emit, pframe_tail*), pframe_emit, pframe_tail*)
$closure_call_copy_reference_valid(S_emit, pclosurecall, n_copy, n_done, pnamedargs, n_base)
$error_entered_call_valid(S_emit, perrorcall)
H = $heap_graph(S)
$heap_owners(H, HOBJECT n_copy) = 1
$heap_owners(H, HOBJECT n_source) = 1
$heap_owners(H, HOBJECT n_maker) = 2
$heap_owners(H, HOBJECT n_token) = 1
$heap_owners(H, HCELL n_root) = 1
$heap_valid(H)
S_dead_source = S_emit[.ALLOCATIONS = $destruction_node_delete(S_emit.ALLOCATIONS, HOBJECT n_source)]
~$closure_call_copy_reference_valid(S_dead_source, pclosurecall, n_copy, n_done, pnamedargs, n_base)
S_dead_maker = S_emit[.ALLOCATIONS = $destruction_node_delete(S_emit.ALLOCATIONS, HOBJECT n_maker)]
~$closure_call_copy_reference_valid(S_dead_maker, pclosurecall, n_copy, n_done, pnamedargs, n_base)
S_dead_copy = S_emit[.ALLOCATIONS = $destruction_node_delete(S_emit.ALLOCATIONS, HOBJECT n_copy)]
~$closure_call_copy_reference_valid(S_dead_copy, pclosurecall, n_copy, n_done, pnamedargs, n_base)
perrorcall_bad = perrorcall[.TARGET = (CLOSURE_TARGET n_source)]
pframe_bad = pframe_emit[.TODO = (ERROR_HANDLER_RESULT perrorcall_bad) :: ptask_emit*]
S_bad = S_live[.FRAMES = pframe_bad :: pframe_tail*]
~$closure_call_copy_warning_context(S_bad, pcallcontext_handler)
S_no_frame = S_live[.FRAMES = eps]
~$closure_call_copy_warning_context(S_no_frame, pcallcontext_handler)
S_alias = S_emit[.STORE = $set_cell(S_emit.STORE, n_root, DEFINED (POBJECT n_token))]
$closure_call_copy_result_valid(S_alias, pclosurecall, n_copy)
$closure_call_task_valid(S_alias, pclosurecall)
~$closure_call_copy_forward_valid(S_alias, pclosurecall, n_copy, 1, {SLOTS ([NAMED_SENT (REFERENCE n_root)]), NAMED eps}, 0)
S_zero = $drive_steps(S, 0)
S_zero.COMPLETION = BUDGET
S_zero.TODO = S.TODO
S_one = $drive_steps(S, 1)
S_one.COMPLETION = BUDGET
S_done = $drive_steps(S, 4800)
S_done = $drive_steps(S_one[.COMPLETION = NORMAL], 4800)
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.CURRENT = eps
S_done.FRAMES = eps
S_done.ACTIVEFIBER = eps
S_done.FIBERCALLERS = eps
~((HOBJECT n_copy) <- S_done.ALLOCATIONS)
~((HOBJECT n_source) <- S_done.ALLOCATIONS)
~((HOBJECT n_maker) <- S_done.ALLOCATIONS)
~((HOBJECT n_token) <- S_done.ALLOCATIONS)
n_maker <- S_done.DESTRUCTION.CALLED
n_token <- S_done.DESTRUCTION.CALLED
$heap_valid($heap_graph(S_done))
''')

API_STAGE = (
    'S.TODO = (GENERATOR_CREATE porigin_function) :: ptask_tail* '
    '-- if S.CURRENT = (pcallcontext) '
    '-- if pcallcontext.TARGET = CLOSURE_TARGET n_copy '
    '-- if S.FRAMES = pframe_api :: pframe_tail* '
    '-- if pframe_api.TODO = (CLOSURE_CALL_COPY_RESULT pclosurecall n_copy) :: ptask_api*')

API = checks(COPY) + checks(r'''

S.COMPLETION = NORMAL
pcallcontext.FUNCTION = porigin_function
pcallcontext.INSTANCE = (n_copy)
pcallcontext.RECEIVER = (n_maker)
pcallcontext.LEXICAL_CLASS = (porigin_maker)
pcallcontext.CALLED_CLASS = (porigin_maker)
pcallcontext.CALLSITE = (pclosurebinding.SITE)
pcallcontext.WRAPPER = eps
pcallcontext.ARGC = 1
pclosurecall.SENT = {SLOTS ([NAMED_SENT (REFERENCE n_formal)]), NAMED eps}
$lookup(S.ENV, $ptascii("slot")) = (n_formal)
S.STORE[n_formal] = DEFINED (POBJECT n_token)
n_formal <- S.REFCELLS
pframe_api.LOCALS = (psymboltable_emit)
$lookup(psymboltable_emit.ENV, $ptascii("alias")) = (n_root)
S.STORE[n_root] = DEFINED (PINT 97)
n_root <- S.REFCELLS
n_root =/= n_formal
S.GLOBALTABLE = (psymboltable_root)
$lookup(psymboltable_root.ENV, $ptascii("source")) = (n_source_cell)
S.STORE[n_source_cell] = DEFINED PNULL
$lookup(psymboltable_root.ENV, $ptascii("maker")) = (n_maker_cell)
S.STORE[n_maker_cell] = DEFINED PNULL
$lookup(psymboltable_root.ENV, $ptascii("g")) = (n_g_cell)
S.STORE[n_g_cell] = DEFINED PNULL
$lookup(psymboltable_root.ENV, $ptascii("slot")) = eps
$lookup(psymboltable_root.ENV, $ptascii("alias")) = eps
$call_reference_operand_valid(S, REFERENCE n_formal)
$closure_call_copy_result_valid(S, pclosurecall, n_copy)
$call_current_valid(S)
$generator_creation_supported(S, pcallcontext)
H = $heap_graph(S)
$heap_owners(H, HOBJECT n_source) = 1
$heap_owners(H, HOBJECT n_copy) = 2
$heap_owners(H, HOBJECT n_maker) = 2
$heap_owners(H, HOBJECT n_token) = 2
$heap_owners(H, HCELL n_formal) = 1
$heap_owners(H, HCELL n_root) = 1
$heap_valid(H)
n_generator = |S.OBJECTS|
S_one = $drive_steps(S, 1)
S_one.COMPLETION = BUDGET
S_one.RESULT = KNOWN (POBJECT n_generator)
S_one.TODO = (CLOSURE_CALL_COPY_RESULT pclosurecall n_copy) :: ptask_api*
S_one.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.FUNCTION = porigin_function
pgenerator.CLOSURE = (n_copy)
pgenerator.PHASE = GENERATOR_FRESH
~pgenerator.FIRST
pgenerator.FRAME = (pframe_generator)
pframe_generator.CONTEXT = (pcallcontext)
pframe_generator.LOCALS = (psymboltable_generator)
$lookup(psymboltable_generator.ENV, $ptascii("slot")) = (n_formal)
S_one.STORE[n_formal] = DEFINED (POBJECT n_token)
$generator_frame_valid(S_one, pgenerator, pframe_generator)
$heap_valid($heap_graph(S_one))
''')

CASES = {
    'i97-reference-warning-saved-api-independent': {'source': ROW['source'], 'stage': PARK_STAGE, 'checks': PARK},
    'i97-reference-warning-fresh-formal-independent': {'source': ROW['source'], 'stage': API_STAGE, 'checks': API},
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
    stable = INPUT_BYTES == {path: path.read_bytes() for path in INPUT_BYTES}
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=review.ROOT, text=True).strip()
    path = raw / 'report.json'
    report = json.loads(path.read_bytes())
    report.update(peer_inputs={str(p): hashlib.sha256(data).hexdigest() for p, data in INPUT_BYTES.items()},
                  peer_inputs_stable=stable, head_stable=head_stable,
                  passed=passed and stable and head_stable)
    path.write_text(json.dumps(report, indent=2) + '\n')
    return report['passed']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    raise SystemExit(0 if run(parser.parse_args().case) else 1)
