#!/usr/bin/env python3
"""Check retval-destructor cleanup and the following copied reference snapshot."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_call_warning_retval_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROW = next(r for r in json.loads(INPUT_BYTES[CATALOG])
           if r['id'] == 'i98-fake-from-reference-warning-retval-fiber-snapshot-independent')
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256'] == '1a3b6997c9b3cb01df29d4a963e883d9f716eabd1dde2eed7eaa1b86bef1540f'


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


COPY = r'''

S.OBJECTS[n_copy] = BOUNDFAKECLOSURE pboundfake_copy
(HOBJECT n_copy) <- S.ALLOCATIONS
n_source = pboundfake_copy.SOURCE
$(n_source < n_copy)
S.OBJECTS[n_source] = FROMCALLABLECLOSURE pfrommethod
(HOBJECT n_source) <- S.ALLOCATIONS
pfrommethod.ARRAY
~pfrommethod.STATIC
$from_receiver(pfrommethod) = (n_old)
$target_function(S, CLOSURE_TARGET n_copy) = (pfunction)
pfunction.ORIGIN = pfrommethod.FUNCTION
porigin_function = pfunction.ORIGIN
$function_generator(S, pfunction)
pfunction.SIGNATURE.BYREF
$call_parameter_at(pfunction.SIGNATURE.PARAMETERS, 0) = (psparam)
psparam.BYREF
psparam.NAME = $ptascii("slot")
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base98R"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Child98R"))) = (porigin_child)
$class_method_origin(S.CLASSES, porigin_function) = (pmethoddesc)
pmethoddesc.OWNER = porigin_base
pmethoddesc.VISIBILITY = PROPERTY_PRIVATE
~pmethoddesc.STATIC
pboundfake_copy.SCOPE = BIND_CLASS porigin_base
pboundfake_copy.CALLED = BIND_CLASS porigin_base
pboundfake_copy.RECEIVER = (n_maker)
pboundfake_copy.ORIGINAL = (pclosurescope_original)
pclosurescope_original.OBJECT = n_source
pclosurescope_original.LEXICAL = porigin_base
pclosurescope_original.CALLED = porigin_child
pclosurescope_original.RECEIVER = (n_old)
pclosurescope_original.CREATION = eps
S.OBJECTS[n_old] = INSTANCE porigin_child
S.OBJECTS[n_maker] = INSTANCE porigin_base
(HOBJECT n_maker) <- S.ALLOCATIONS
(HOBJECT n_old) <- S.ALLOCATIONS
$closure_binding_at(S.CLOSUREBINDINGS, n_copy) = eps
$closure_scope_at(S.CLOSURESCOPES, n_copy) = eps
$closure_call_copy_site(S, pboundfake_copy.SITE)
$closure_call_fake_method(S, n_source, pfunction)
$closure_call_fake_copy_binding(S, pboundfake_copy)
$bound_fake_valid(S, n_copy)
$closure_call_copy_row(S, n_copy) = (pclosurebinding_copy)
pclosurebinding_copy.SOURCE = n_source
pclosurebinding_copy.RECEIVER = (n_maker)
$node_children(S, HOBJECT n_copy) = [HOBJECT n_maker]
pclosurecall.SOURCE = n_source
pclosurecall.SITE = pboundfake_copy.SITE
pclosurecall.FIRST = (POBJECT n_maker)
pclosurecall.RECEIVER = (n_maker)
pclosurecall.RAW = [(KINT 1, KNOWN (POBJECT n_token))]
pclosurecall.INDEX = 2
pclosurecall.ERROR = eps
pclosurecall.PACKS = eps
$object_name(S, n_token) = $ptascii("Token98R")
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
pfibervm.CURRENT = (pcallcontext_dtor)
pfibervm.FRAMES = pframe_emit :: pframe_tail*
pframe_emit.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: ptask_emit*
pfibervm.DESTRUCTORCLEANUPS = pdestructioncleanup :: pdestructioncleanup_tail*
pdestructioncleanup.SOURCE = ERROR_HANDLER_RESULT perrorcall
~pdestructioncleanup.RELEASED
perrorcall.RESUME = CLOSURE_CALL_COPY_REFERENCE pclosurecall n_copy n_done pnamedargs n_base
n_done = 0
pnamedargs = {SLOTS eps, NAMED eps}
pfibervm.DESTRUCTOROPERATIONS = pdestructionoperation :: pdestructionoperation_tail*
pdestructionoperation.SOURCE = ERROR_HANDLER_RESULT perrorcall
pdestructionoperation.CLEANUP = (pdestructioncleanup)
pdestructorcall.OPERATION = (pdestructionoperation)
pfibervm.DESTRUCTORCALLS = pdestructorcall :: pdestructorcall_tail*
''') + checks(COPY) + checks(r'''

pclosurecall.SENT = {SLOTS ([NAMED_SENT (KNOWN (POBJECT n_token))]), NAMED eps}
pframe_emit.CONTEXT = (pcallcontext_run)
pdestructioncleanup.CALLER = (pcallcontext_run)
pdestructioncleanup.ORIGIN = (pclosurecall.SITE)
pdestructioncleanup.CONSTCONTEXT = eps
pdestructorcall.CALLER = (pcallcontext_run)
pdestructorcall.OBJECT = n_retval
$class_named(S.CLASSNAMES, $ptlc($ptascii("Returned98R"))) = (porigin_retval)
S.OBJECTS[n_retval] = INSTANCE porigin_retval
(HOBJECT n_retval) <- S.ALLOCATIONS
n_retval <- S.DESTRUCTION.CALLED
pcallcontext_dtor.TARGET = pdestructorcall.TARGET
pcallcontext_dtor.INSTANCE = eps
pcallcontext_dtor.RECEIVER = (n_retval)
pcallcontext_dtor.LEXICAL_CLASS = (porigin_retval)
pcallcontext_dtor.CALLED_CLASS = (porigin_retval)
pcallcontext_dtor.WRAPPER = eps
pcallcontext_dtor.ARGC = 0
$objectprops_at(S.OBJECTPROPS, n_retval) = (ppropertyslot*)
$property_slot_at(ppropertyslot*, $ptascii("token")) = (ppropertyslot_token)
ppropertyslot_token.STATE = PROP_VALUE (DIRECT (POBJECT n_token))
$node_children(S, HOBJECT n_retval) = [HOBJECT n_token]
pframe_emit.LOCALS = (psymboltable_emit)
$lookup(psymboltable_emit.ENV, $ptascii("alias")) = (n_root)
S.STORE[n_root] = DEFINED (PINT 98)
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
$lookup(S.ENV, $ptascii("weakRetval")) = (n_weak_cell)
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
$heap_owners(H, HOBJECT n_token) = 2
$heap_owners(H, HCELL n_root) = 1
$heap_valid(H)
S_no_cleanup = S_emit[.DESTRUCTION.CLEANUPS = eps]
~$error_cleanup_valid(S_no_cleanup, perrorcall)
~$eager_operation_source_valid(S_no_cleanup, pdestructionoperation)
pclosurecall_bad = pclosurecall[.SOURCE = n_copy]
perrorcall_bad = perrorcall[.RESUME = CLOSURE_CALL_COPY_REFERENCE pclosurecall_bad n_copy n_done pnamedargs n_base]
pdestructioncleanup_bad = pdestructioncleanup[.SOURCE = ERROR_HANDLER_RESULT perrorcall_bad]
~$eager_cleanup_valid(S_live, pdestructioncleanup_bad)
S_dead_source = S_emit[.ALLOCATIONS = $destruction_node_delete(S_emit.ALLOCATIONS, HOBJECT n_source)]
~$closure_call_copy_reference_valid(S_dead_source, pclosurecall, n_copy, n_done, pnamedargs, n_base)
S_dead_copy = S_emit[.ALLOCATIONS = $destruction_node_delete(S_emit.ALLOCATIONS, HOBJECT n_copy)]
~$closure_call_copy_reference_valid(S_dead_copy, pclosurecall, n_copy, n_done, pnamedargs, n_base)
pboundfake_cycle = pboundfake_copy[.SOURCE = n_copy]
S_cycle = S_emit[.OBJECTS = $object_set(S_emit.OBJECTS, n_copy, BOUNDFAKECLOSURE pboundfake_cycle)]
~$closure_call_fake_copy_binding(S_cycle, pboundfake_cycle)
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
~((HOBJECT n_retval) <- S_done.ALLOCATIONS)
~((HOBJECT n_copy) <- S_done.ALLOCATIONS)
~((HOBJECT n_source) <- S_done.ALLOCATIONS)
~((HOBJECT n_old) <- S_done.ALLOCATIONS)
~((HOBJECT n_maker) <- S_done.ALLOCATIONS)
~((HOBJECT n_token) <- S_done.ALLOCATIONS)
n_retval <- S_done.DESTRUCTION.CALLED
n_old <- S_done.DESTRUCTION.CALLED
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
pcallcontext.LEXICAL_CLASS = (porigin_base)
pcallcontext.CALLED_CLASS = (porigin_base)
pcallcontext.CALLSITE = (pboundfake_copy.SITE)
pcallcontext.WRAPPER = eps
pcallcontext.ARGC = 1
pclosurecall.SENT = {SLOTS ([NAMED_SENT (REFERENCE n_formal)]), NAMED eps}
$lookup(S.ENV, $ptascii("slot")) = (n_formal)
S.STORE[n_formal] = DEFINED (POBJECT n_token)
n_formal <- S.REFCELLS
pframe_api.LOCALS = (psymboltable_emit)
$lookup(psymboltable_emit.ENV, $ptascii("alias")) = (n_root)
S.STORE[n_root] = DEFINED (PINT 98)
n_root <- S.REFCELLS
n_root =/= n_formal
S.GLOBALTABLE = (psymboltable_root)
$lookup(psymboltable_root.ENV, $ptascii("source")) = (n_source_cell)
S.STORE[n_source_cell] = DEFINED PNULL
$lookup(psymboltable_root.ENV, $ptascii("maker")) = (n_maker_cell)
S.STORE[n_maker_cell] = DEFINED PNULL
$lookup(psymboltable_root.ENV, $ptascii("weakRetval")) = (n_weak_cell)
S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)
$weakref_get(S, n_weak) = PNULL
$lookup(psymboltable_root.ENV, $ptascii("alias")) = eps
$lookup(psymboltable_root.ENV, $ptascii("slot")) = eps
S.DESTRUCTION.CLEANUPS = eps
S.DESTRUCTION.OPERATIONS = eps
S.DESTRUCTION.CALLS = eps
$call_reference_operand_valid(S, REFERENCE n_formal)
$closure_call_copy_result_valid(S, pclosurecall, n_copy)
$call_current_valid(S)
$generator_creation_supported(S, pcallcontext)
H = $heap_graph(S)
$heap_owners(H, HOBJECT n_copy) = 2
$heap_owners(H, HOBJECT n_source) = 1
$heap_owners(H, HOBJECT n_old) = 1
$heap_owners(H, HOBJECT n_maker) = 2
$heap_owners(H, HOBJECT n_token) = 2
$heap_owners(H, HCELL n_formal) = 1
$heap_owners(H, HCELL n_root) = 1
$heap_valid(H)
n_generator = |S.OBJECTS|
S_one = $drive_steps(S, 1)
S_one.COMPLETION = BUDGET
S_one.RESULT = KNOWN PNULL
S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (CLOSURE_CALL_COPY_RESULT pclosurecall n_copy) :: ptask_api*
pdestructionrelease.JOBS = $destruction_values([HCELL n_formal, HOBJECT n_copy])
pdestructionframe.VALUE = KNOWN (POBJECT n_generator)
pdestructionframe.PENDING = eps
pdestructionframe.FUNCTION = porigin_function
S_one.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.FUNCTION = porigin_function
pgenerator.CLOSURE = (n_copy)
pgenerator.PHASE = GENERATOR_FRESH
~pgenerator.FIRST
pgenerator.FRAME = (pframe_generator)
pframe_generator.CONTEXT = (pcallcontext)
pframe_generator.LOCALS = (psymboltable_generator)
$lookup(psymboltable_generator.ENV, $ptascii("slot")) = (n_formal)
$generator_frame_valid(S_one, pgenerator, pframe_generator)
$call_task_valid(S_one, DESTRUCTOR_FRAME_EXIT pdestructionframe)
$task_nodes(DESTRUCTOR_FRAME_EXIT pdestructionframe) = [HOBJECT n_generator]
$heap_owners($heap_graph(S_one), HOBJECT n_generator) = 1
$heap_valid($heap_graph(S_one))
''')

CASES = {
    'i98-retval-dtor-saved-copy-independent': {'source': ROW['source'], 'stage': PARK_STAGE, 'checks': PARK},
    'i98-retval-dtor-fresh-formal-independent': {'source': ROW['source'], 'stage': API_STAGE, 'checks': API},
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
        passed = review.run(selected, process_seconds=900)
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
