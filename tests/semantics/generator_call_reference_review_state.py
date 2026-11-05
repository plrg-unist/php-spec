#!/usr/bin/env python3
"""Check copied reference-formal separation and real parked cache owners."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_call_reference_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROW = next(r for r in json.loads(INPUT_BYTES[CATALOG]) if r['id'] == 'i93-real-call-reference-cv-snapshot-send-independent')
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256'] == '1ca72527ea6abb505d4107b1f547664c2ee4440d06fa178cea770e12857484fc'


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
$function_at(S.CLOSURETEMPLATES, porigin_function) = (pfunction)
pfunction.SIGNATURE.BYREF
$call_parameter_at(pfunction.SIGNATURE.PARAMETERS, 0) = (psparam)
psparam.BYREF
psparam.NAME = $ptascii("slot")
$function_generator(S, pfunction)
~$closure_static(S, pfunction)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Maker93R"))) = (porigin_maker)
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
'''

API_STAGE = (
    'S.TODO = (GENERATOR_CREATE porigin_function) :: ptask_tail* '
    '-- if S.CURRENT = (pcallcontext) '
    '-- if pcallcontext.TARGET = CLOSURE_TARGET n_copy '
    '-- if S.FRAMES = pframe_api :: pframe_tail* '
    '-- if pframe_api.TODO = (CLOSURE_CALL_COPY_RESULT pclosurecall n_copy) :: ptask_api*')

API = checks(COPY) + checks(r'''
S.COMPLETION = NORMAL
pcallcontext.INSTANCE = (n_copy)
pcallcontext.FUNCTION = porigin_function
pcallcontext.RECEIVER = (n_maker)
pcallcontext.LEXICAL_CLASS = (porigin_maker)
pcallcontext.CALLED_CLASS = (porigin_maker)
pcallcontext.CALLSITE = (pclosurebinding.SITE)
pcallcontext.WRAPPER = eps
pcallcontext.ARGC = 1
pclosurecall.SOURCE = n_source
pclosurecall.SITE = pclosurebinding.SITE
pclosurecall.FIRST = (POBJECT n_maker)
pclosurecall.RECEIVER = (n_maker)
pclosurecall.RAW = [(KINT 1, KNOWN (POBJECT n_token))]
pclosurecall.SENT = {SLOTS ([NAMED_SENT (REFERENCE n_formal)]), NAMED eps}
pclosurecall.INDEX = 2
pclosurecall.ERROR = eps
pclosurecall.PACKS = eps
$lookup(S.ENV, $ptascii("slot")) = (n_formal)
S.STORE[n_formal] = DEFINED (POBJECT n_token)
n_formal <- S.REFCELLS
S.GLOBALTABLE = (psymboltable_root)
$lookup(psymboltable_root.ENV, $ptascii("slot")) = (n_root)
$lookup(psymboltable_root.ENV, $ptascii("alias")) = (n_root)
S.STORE[n_root] = DEFINED (POBJECT n_token)
n_root <- S.REFCELLS
n_formal =/= n_root
$lookup(psymboltable_root.ENV, $ptascii("source")) = (n_source_cell)
S.STORE[n_source_cell] = DEFINED (POBJECT n_source)
$lookup(psymboltable_root.ENV, $ptascii("maker")) = (n_maker_cell)
S.STORE[n_maker_cell] = DEFINED (POBJECT n_maker)
$object_name(S, n_token) = $ptascii("Token93R")
$call_reference_operand_valid(S, REFERENCE n_formal)
$closure_call_copy_result_valid(S, pclosurecall, n_copy)
$call_task_valid(S, CLOSURE_CALL_COPY_RESULT pclosurecall n_copy)
$task_nodes(CLOSURE_CALL_COPY_RESULT pclosurecall n_copy) = [HOBJECT n_copy, HOBJECT n_maker, HOBJECT n_token, HOBJECT n_source]
$call_current_valid(S)
$generator_creation_supported(S, pcallcontext)
H = $heap_graph(S)
$heap_owners(H, HCELL n_root) = 2
$heap_owners(H, HCELL n_formal) = 1
$heap_owners(H, HOBJECT n_token) = 3
$heap_owners(H, HOBJECT n_copy) = 2
$heap_owners(H, HOBJECT n_maker) = 3
$heap_owners(H, HOBJECT n_source) = 2
pclosurebinding_bad_source = pclosurebinding[.SOURCE = n_copy]
~$closure_call_copy_binding(S, pclosurebinding_bad_source)
pclosurebinding_bad_called = pclosurebinding[.CALLED = eps]
~$closure_call_copy_binding(S, pclosurebinding_bad_called)
pclosurebinding_bad_receiver = pclosurebinding[.RECEIVER = (n_source)]
~$closure_call_copy_binding(S, pclosurebinding_bad_receiver)
S_dead_copy = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HOBJECT n_copy)]
~$closure_call_copy_binding(S_dead_copy, pclosurebinding)
S_dead_maker = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HOBJECT n_maker)]
~$closure_call_copy_binding(S_dead_maker, pclosurebinding)
$heap_valid(H)
''')

PARK_STAGE = (
    'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
    '-- if pconfigcall.KIND = INTRINSIC_FIBER_THROW '
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
$lookup(S.ENV, $ptascii("g")) = (n_generator_cell)
S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)
S.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.CLOSURE = (n_copy)
pgenerator.FUNCTION = porigin_function
''') + checks(COPY) + checks(r'''
pgenerator.PHASE = GENERATOR_RUNNING
pgenerator.FRAME = eps
pgenerator.CREATION = eps
pgenerator.ACCESS = eps
pgenerator.VALUE = eps
pgenerator.REFCELL = (n_cache)
n_cache <- S.REFCELLS
S.STORE[n_cache] = DEFINED (POBJECT n_token)
$object_name(S, n_token) = $ptascii("Token93R")
pfiber.VM = (pfibervm)
pfibervm.CURRENT = (pcallcontext_generator)
pcallcontext_generator.TARGET = CLOSURE_TARGET n_copy
pcallcontext_generator.FUNCTION = porigin_function
pcallcontext_generator.INSTANCE = (n_copy)
pcallcontext_generator.RECEIVER = (n_maker)
pcallcontext_generator.LEXICAL_CLASS = (porigin_maker)
pcallcontext_generator.CALLED_CLASS = (porigin_maker)
pcallcontext_generator.CALLSITE = (pclosurebinding.SITE)
pcallcontext_generator.WRAPPER = eps
pcallcontext_generator.ARGC = 1
$call_context_roots((pcallcontext_generator)) = [HOBJECT n_copy]
$call_receiver_roots(pcallcontext_generator) = eps
pfibervm.FRAMES = pframe_send :: pframe_tail*
pframe_send.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_send*
pgeneratorop.OBJECT = n_generator
pgeneratorop.NAME = "send"
pgeneratorop.ARGUMENTS = [POBJECT n_input]
~pgeneratorop.ADVANCE
~pgeneratorop.BORROWED
~pgeneratorop.STARTPACK
pgeneratorop.LOOP = eps
$lookup(pfibervm.TABLE.ENV, $ptascii("slot")) = eps
$lookup(pfibervm.TABLE.ENV, $ptascii("token")) = eps
$lookup(pfibervm.TABLE.ENV, $ptascii("received")) = eps
$lookup(S.ENV, $ptascii("slot")) = eps
$lookup(S.ENV, $ptascii("alias")) = eps
$lookup(S.ENV, $ptascii("source")) = eps
$lookup(S.ENV, $ptascii("maker")) = eps
~((HOBJECT n_source) <- S.ALLOCATIONS)
~$closure_callable(S, n_source)
$lookup(S.ENV, $ptascii("weakCopy")) = (n_weak_copy_cell)
S.STORE[n_weak_copy_cell] = DEFINED (POBJECT n_weak_copy)
$weakref_get(S, n_weak_copy) = POBJECT n_copy
$lookup(S.ENV, $ptascii("weakSource")) = (n_weak_source_cell)
S.STORE[n_weak_source_cell] = DEFINED (POBJECT n_weak_source)
$weakref_get(S, n_weak_source) = PNULL
$lookup(S.ENV, $ptascii("weakMaker")) = (n_weak_maker_cell)
S.STORE[n_weak_maker_cell] = DEFINED (POBJECT n_weak_maker)
$weakref_get(S, n_weak_maker) = POBJECT n_maker
$lookup(S.ENV, $ptascii("weakToken")) = (n_weak_token_cell)
S.STORE[n_weak_token_cell] = DEFINED (POBJECT n_weak_token)
$weakref_get(S, n_weak_token) = POBJECT n_token
$lookup(S.ENV, $ptascii("weakReplacement")) = (n_weak_replacement_cell)
S.STORE[n_weak_replacement_cell] = DEFINED (POBJECT n_weak_replacement)
S.OBJECTS[n_weak_replacement] = WEAKREFERENCE (n_replacement)
$weakref_get(S, n_weak_replacement) = PNULL
~((HOBJECT n_replacement) <- S.ALLOCATIONS)
$lookup(S.ENV, $ptascii("weakInput")) = (n_weak_input_cell)
S.STORE[n_weak_input_cell] = DEFINED (POBJECT n_weak_input)
$weakref_get(S, n_weak_input) = POBJECT n_input
$object_name(S, n_input) = $ptascii("Input93R")
S_live = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]
$generator_creation_resume_owner(S_live) = (n_generator)
$fiber_generator_real_closure_valid(S_live, pgenerator, pcallcontext_generator)
$fiber_generator_callee_valid(S_live, pgenerator, pcallcontext_generator)
$fiber_generator_cached_reference_valid(S_live, pgenerator, pcallcontext_generator)
$fiber_generator_body_id(S_live) = (n_generator)
$fiber_generator_transfer(S_live)
$call_current_valid(S_live)
$eval_trace_preparser(S_live, (pcallcontext_generator), pframe_send) = eps
H = $heap_graph(S)
$heap_owners(H, HOBJECT n_copy) = 1
$heap_owners(H, HOBJECT n_maker) = 1
$heap_owners(H, HOBJECT n_source) = 0
$heap_owners(H, HOBJECT n_replacement) = 0
$heap_owners(H, HCELL n_cache) = 1
$heap_owners(H, HOBJECT n_token) = 1
$heap_owners(H, HOBJECT n_input) = 1
$heap_count(HCELL n_cache, $fiber_vm_nodes(pfibervm)) = 0
$heap_count(HOBJECT n_maker, $fiber_vm_nodes(pfibervm)) = 0
$heap_count(HOBJECT n_copy, $fiber_vm_nodes(pfibervm)) = 1
$heap_count(HOBJECT n_input, $fiber_vm_nodes(pfibervm)) = 1
pgenerator_bad_copy = pgenerator[.CLOSURE = (n_source)]
S_bad_copy = S_live[.OBJECTS = $object_set(S_live.OBJECTS, n_generator, GENERATOR pgenerator_bad_copy)]
~$fiber_generator_real_closure_valid(S_bad_copy, pgenerator_bad_copy, pcallcontext_generator)
pcallcontext_bad_called = pcallcontext_generator[.CALLED_CLASS = eps]
S_bad_called = S_live[.CURRENT = (pcallcontext_bad_called)]
~$fiber_generator_real_closure_valid(S_bad_called, pgenerator, pcallcontext_bad_called)
S_no_owner = S_live[.FRAMES = eps]
$fiber_generator_body_id(S_no_owner) = eps
~$fiber_generator_real_closure_valid(S_no_owner, pgenerator, pcallcontext_generator)
S_bad_cache = S_live[.STORE = $set_cell(S_live.STORE, n_cache, UNDEFINED)]
~$fiber_generator_cached_reference_valid(S_bad_cache, pgenerator, pcallcontext_generator)
S_zero = $drive_steps(S, 0)
S_zero.COMPLETION = BUDGET
S_zero.TODO = S.TODO
S_one = $drive_steps(S, 1)
S_one.COMPLETION = BUDGET
S_two = $drive_steps(S_one[.COMPLETION = NORMAL], 1)
S_two.COMPLETION = BUDGET
S_two = $drive_steps(S, 2)
S_done = $drive_steps(S, 4800)
S_done = $drive_steps(S_one[.COMPLETION = NORMAL], 4800)
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.CURRENT = eps
S_done.FRAMES = eps
S_done.ACTIVEFIBER = eps
S_done.FIBERCALLERS = eps
S_done.FIBERCLOSERS = eps
~((HOBJECT n_generator) <- S_done.ALLOCATIONS)
~((HOBJECT n_copy) <- S_done.ALLOCATIONS)
~((HOBJECT n_maker) <- S_done.ALLOCATIONS)
~((HOBJECT n_source) <- S_done.ALLOCATIONS)
~((HOBJECT n_replacement) <- S_done.ALLOCATIONS)
~((HOBJECT n_token) <- S_done.ALLOCATIONS)
~((HOBJECT n_input) <- S_done.ALLOCATIONS)
~((HCELL n_cache) <- S_done.ALLOCATIONS)
n_maker <- S_done.DESTRUCTION.CALLED
n_replacement <- S_done.DESTRUCTION.CALLED
n_token <- S_done.DESTRUCTION.CALLED
n_input <- S_done.DESTRUCTION.CALLED
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
''')

CASES = {
    'i93-copy-reference-cell-separation-independent': {'source': ROW['source'], 'stage': API_STAGE, 'checks': API},
    'i93-copy-reference-cache-parked-independent': {'source': ROW['source'], 'stage': PARK_STAGE, 'checks': PARK},
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
