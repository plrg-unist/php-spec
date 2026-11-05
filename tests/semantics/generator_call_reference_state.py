#!/usr/bin/env python3
"""Check early copied static cells, detached formals and reference warning traces."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_call_reference_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {r['id']: r for r in json.loads(INPUT_BYTES[CATALOG])}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


FORWARD_STAGE = (
    'S.TODO = (CLOSURE_CALL_COPY_FORWARD pclosurecall n_copy n_done pnamedargs n_base) :: ptask_tail* '
    '-- if n_done = 1')

COMMON = r'''
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
S.OBJECTS[n_copy] = REALCLOSURE porigin_function eps pstaticcell_copies*
pstaticcell_copies* = [pstaticcell_copy]
$closure_binding_at(S.CLOSUREBINDINGS, n_copy) = (pclosurebinding)
n_source = pclosurebinding.SOURCE
$(n_source < n_copy)
S.OBJECTS[n_source] = REALCLOSURE porigin_function eps pstaticcell_originals*
pstaticcell_originals* = [pstaticcell_source]
pstaticcell_copy.ORIGIN = pstaticcell_source.ORIGIN
n_source_counter = pstaticcell_source.CELL
n_copy_counter = pstaticcell_copy.CELL
S.STORE[n_source_counter] = DEFINED (PINT 2)
n_source_counter <- S.REFCELLS
n_copy_counter <- S.REFCELLS
(HCELL n_source_counter) <- S.ALLOCATIONS
(HCELL n_copy_counter) <- S.ALLOCATIONS
$(n_source_counter < n_base)
$(n_copy_counter < n_base)
(HOBJECT n_source) <- S.ALLOCATIONS
(HOBJECT n_copy) <- S.ALLOCATIONS
$function_at(S.CLOSURETEMPLATES, porigin_function) = (pfunction)
$function_generator(S, pfunction)
~pfunction.SIGNATURE.BYREF
$call_parameter_at(pfunction.SIGNATURE.PARAMETERS, 0) = (psparam)
psparam.BYREF
psparam.NAME = $ptascii("token")
~$closure_static(S, pfunction)
pclosurecall.SOURCE = n_source
pclosurecall.SITE = pclosurebinding.SITE
pclosurecall.ERROR = eps
pclosurecall.PACKS = eps
pclosurecall.INDEX = 2
pclosurecall.FIRST = (POBJECT n_maker)
pclosurecall.RECEIVER = (n_maker)
pclosurecall.RAW = [(KINT 1, KNOWN (POBJECT n_token))]
pclosurecall.SENT = {SLOTS ([NAMED_SENT (KNOWN (POBJECT n_token))]), NAMED eps}
pnamedargs = {SLOTS ([NAMED_SENT (REFERENCE n_formal)]), NAMED eps}
S.STORE[n_formal] = DEFINED (POBJECT n_token)
n_formal <- S.REFCELLS
(HCELL n_formal) <- S.ALLOCATIONS
$(n_base <= n_formal)
$call_reference_operand_valid(S, REFERENCE n_formal)
pclosurebinding.RECEIVER = (n_maker)
S.OBJECTS[n_maker] = INSTANCE porigin_maker
pclosurebinding.LEXICAL = (porigin_maker)
pclosurebinding.CALLED = (porigin_maker)
$closure_call_copy_binding(S, pclosurebinding)
$closure_call_copy_forward_valid(S, pclosurecall, n_copy, n_done, pnamedargs, n_base)
$call_task_valid(S, CLOSURE_CALL_COPY_FORWARD pclosurecall n_copy n_done pnamedargs n_base)
$task_nodes(CLOSURE_CALL_COPY_FORWARD pclosurecall n_copy n_done pnamedargs n_base) = [HOBJECT n_copy, HOBJECT n_maker, HOBJECT n_token, HOBJECT n_source, HCELL n_formal]
$lookup(S.ENV, $ptascii("warningCount")) = (n_count)
S.STORE[n_count] = DEFINED (PINT 1)
$lookup(S.ENV, $ptascii("weakSource")) = (n_weak_source_cell)
S.STORE[n_weak_source_cell] = DEFINED (POBJECT n_weak_source)
$weakref_get(S, n_weak_source) = POBJECT n_source
$lookup(S.ENV, $ptascii("weakOld")) = (n_weak_old_cell)
S.STORE[n_weak_old_cell] = DEFINED (POBJECT n_weak_old)
$weakref_get(S, n_weak_old) = POBJECT n_old
$target_receiver(S, CLOSURE_TARGET n_source) = (n_old)
$lookup(S.ENV, $ptascii("weakToken")) = (n_weak_token_cell)
S.STORE[n_weak_token_cell] = DEFINED (POBJECT n_weak_token)
$weakref_get(S, n_weak_token) = POBJECT n_token
H = $heap_graph(S)
$heap_owners(H, HOBJECT n_copy) = 1
$heap_owners(H, HOBJECT n_maker) = 3
$heap_owners(H, HOBJECT n_token) = 2
$heap_owners(H, HCELL n_formal) = 1
$heap_owners(H, HOBJECT n_old) = 1
H_original = $heap_graph(S[.TODO = (CLOSURE_CALL_COPY_RESULT pclosurecall n_copy) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)])
pnode_original* = $heap_reach(H_original.ROOTS, eps, H_original.EDGES)
~((HCELL n_formal) <- pnode_original*)
(HCELL n_copy_counter) <- pnode_original*
(HCELL n_source_counter) <- pnode_original*
pnamedargs_alias = {SLOTS ([NAMED_SENT (REFERENCE n_copy_counter)]), NAMED eps}
~$closure_call_copy_forward_valid(S, pclosurecall, n_copy, n_done, pnamedargs_alias, n_base)
S_alias = S[.STORE = $set_cell(S.STORE, n_copy_counter, DEFINED (POBJECT n_token))]
$closure_call_copy_result_valid(S_alias, pclosurecall, n_copy)
$closure_call_task_valid(S_alias, pclosurecall)
~$closure_call_copy_forward_valid(S_alias, pclosurecall, n_copy, n_done, pnamedargs_alias, 0)
n_base_late = $(n_formal + 1)
~$closure_call_copy_forward_valid(S, pclosurecall, n_copy, n_done, pnamedargs, n_base_late)
n_base_unbounded = $(|S.STORE| + 1)
~$closure_call_copy_forward_valid(S, pclosurecall, n_copy, n_done, pnamedargs, n_base_unbounded)
pclosurecall_bad_raw = pclosurecall[.RAW = [(KINT 1, KNOWN (PINT 0))]]
~$closure_call_copy_forward_valid(S, pclosurecall_bad_raw, n_copy, n_done, pnamedargs, n_base)
S_dead_source = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HOBJECT n_source)]
~$closure_call_copy_forward_valid(S_dead_source, pclosurecall, n_copy, n_done, pnamedargs, n_base)
S_one = $drive_steps(S, 1)
S_one.COMPLETION = BUDGET
S_one.CURRENT = (pcallcontext_copy)
pcallcontext_copy.TARGET = CLOSURE_TARGET n_copy
pcallcontext_copy.INSTANCE = (n_copy)
pcallcontext_copy.RECEIVER = (n_maker)
pcallcontext_copy.WRAPPER = eps
S_one.FRAMES = pframe_api :: pframe_tail*
pframe_api.TODO = (CLOSURE_CALL_COPY_RESULT pclosurecall_prepared n_copy) :: ptask_tail*
pclosurecall_prepared.SENT = pnamedargs
pclosurecall_prepared.RAW = pclosurecall.RAW
$lookup(S_one.ENV, $ptascii("token")) = (n_formal)
$heap_owners($heap_graph(S_one), HOBJECT n_copy) = 2
$heap_valid(H)
'''

SINGLETON = checks(COMMON) + checks(r'''
n_source_counter =/= n_copy_counter
S.STORE[n_copy_counter] = DEFINED (PINT 1)
$lookup(S.ENV, $ptascii("seed")) = eps
$lookup(S.ENV, $ptascii("source")) = (n_source_cell)
S.STORE[n_source_cell] = DEFINED (POBJECT n_source)
$object_name(S, n_maker) = $ptascii("Active93A")
$object_name(S, n_old) = $ptascii("Origin93A")
$heap_owners(H, HOBJECT n_source) = 2
$heap_owners(H, HCELL n_source_counter) = 1
$heap_owners(H, HCELL n_copy_counter) = 1
''')

SHARED = checks(COMMON) + checks(r'''
n_source_counter = n_copy_counter
S.STORE[n_copy_counter] = DEFINED (PINT 2)
$lookup(S.ENV, $ptascii("seed")) = (n_seed_cell)
S.STORE[n_seed_cell] = DEFINED (POBJECT n_seed)
S.OBJECTS[n_seed] = GENERATOR pgenerator_seed
pgenerator_seed.FUNCTION = porigin_function
pgenerator_seed.CLOSURE = (n_source)
pgenerator_seed.PHASE = GENERATOR_PAUSED
pgenerator_seed.FRAME =/= eps
$object_name(S, n_maker) = $ptascii("Active93B")
$object_name(S, n_old) = $ptascii("Origin93B")
$heap_owners(H, HOBJECT n_source) = 3
$heap_owners(H, HCELL n_copy_counter) = 3
''')

RETURN_STAGE = 'S.TODO = (CLOSURE_CALL_COPY_RETURN n_copy n_generator) :: ptask_tail*'

TEMPORARY = checks(r'''
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
S.RESULT = KNOWN PNULL
S.BASE = BASE_VALUE (KNOWN PNULL)
S.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_FRESH
pgenerator.CLOSURE = (n_copy)
pgenerator.VALUE = eps
pgenerator.REFCELL = eps
~pgenerator.FIRST
pgenerator.FRAME = (pframe_generator)
pframe_generator.CONTEXT = (pcallcontext)
pframe_generator.LOCALS = (psymboltable_generator)
pcallcontext.TARGET = CLOSURE_TARGET n_copy
pcallcontext.INSTANCE = (n_copy)
pcallcontext.WRAPPER = eps
$lookup(psymboltable_generator.ENV, $ptascii("token")) = (n_formal)
S.STORE[n_formal] = DEFINED (POBJECT n_token)
S.OBJECTS[n_copy] = REALCLOSURE pgenerator.FUNCTION eps pstaticcell_copies*
pstaticcell_copies* = [pstaticcell_copy]
n_copy_counter = pstaticcell_copy.CELL
S.STORE[n_copy_counter] = DEFINED (PINT 1)
$closure_binding_at(S.CLOSUREBINDINGS, n_copy) = (pclosurebinding)
n_source = pclosurebinding.SOURCE
pclosurebinding.RECEIVER = (n_maker)
pcallcontext.RECEIVER = (n_maker)
pcallcontext.CALLSITE = (pclosurebinding.SITE)
$closure_call_copy_binding(S, pclosurebinding)
$closure_call_copy_return_valid(S, n_copy, n_generator)
$call_task_valid(S, CLOSURE_CALL_COPY_RETURN n_copy n_generator)
$task_nodes(CLOSURE_CALL_COPY_RETURN n_copy n_generator) = [HOBJECT n_generator]
$object_name(S, n_maker) = $ptascii("Active93C")
$object_name(S, n_token) = $ptascii("Token93C")
$lookup(S.ENV, $ptascii("weakSource")) = (n_weak_source_cell)
S.STORE[n_weak_source_cell] = DEFINED (POBJECT n_weak_source)
$weakref_get(S, n_weak_source) = PNULL
$lookup(S.ENV, $ptascii("weakOld")) = (n_weak_old_cell)
S.STORE[n_weak_old_cell] = DEFINED (POBJECT n_weak_old)
S.OBJECTS[n_weak_old] = WEAKREFERENCE (n_old)
$weakref_get(S, n_weak_old) = PNULL
~((HOBJECT n_source) <- S.ALLOCATIONS)
~((HOBJECT n_old) <- S.ALLOCATIONS)
n_old <- S.DESTRUCTION.CALLED
H = $heap_graph(S)
$heap_owners(H, HOBJECT n_generator) = 1
$heap_owners(H, HOBJECT n_copy) = 1
$heap_owners(H, HOBJECT n_maker) = 2
$heap_owners(H, HOBJECT n_token) = 1
$heap_owners(H, HCELL n_formal) = 1
$heap_owners(H, HCELL n_copy_counter) = 1
$heap_owners(H, HOBJECT n_source) = 0
$heap_owners(H, HOBJECT n_old) = 0
pcallcontext_bad_site = pcallcontext[.CALLSITE = (pgenerator.FUNCTION)]
pframe_bad_site = pframe_generator[.CONTEXT = (pcallcontext_bad_site)]
pgenerator_bad_site = pgenerator[.FRAME = (pframe_bad_site)]
S_bad_site = S[.OBJECTS = $object_set(S.OBJECTS, n_generator, GENERATOR pgenerator_bad_site)]
~$closure_call_copy_return_valid(S_bad_site, n_copy, n_generator)
pgenerator_bad_phase = pgenerator[.PHASE = GENERATOR_CLOSED]
S_bad_phase = S[.OBJECTS = $object_set(S.OBJECTS, n_generator, GENERATOR pgenerator_bad_phase)]
~$closure_call_copy_return_valid(S_bad_phase, n_copy, n_generator)
~$closure_call_copy_return_valid(S, n_source, n_generator)
S_dead_copy = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HOBJECT n_copy)]
~$closure_call_copy_return_valid(S_dead_copy, n_copy, n_generator)
S_dead_generator = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HOBJECT n_generator)]
~$closure_call_copy_return_valid(S_dead_generator, n_copy, n_generator)
n_unbounded = |S.OBJECTS|
~$closure_call_copy_return_valid(S, n_copy, n_unbounded)
S_one = $drive_steps(S, 1)
S_one.COMPLETION = BUDGET
S_one.RESULT = KNOWN (POBJECT n_generator)
S_one.TODO = ptask_tail*
$heap_owners($heap_graph(S_one), HOBJECT n_generator) = 1
S_done = $drive_steps(S, 4000)
S_done = $drive_steps(S_one[.COMPLETION = NORMAL], 4000)
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.CURRENT = eps
S_done.FRAMES = eps
~((HOBJECT n_generator) <- S_done.ALLOCATIONS)
~((HOBJECT n_copy) <- S_done.ALLOCATIONS)
~((HOBJECT n_maker) <- S_done.ALLOCATIONS)
~((HOBJECT n_token) <- S_done.ALLOCATIONS)
n_maker <- S_done.DESTRUCTION.CALLED
n_token <- S_done.DESTRUCTION.CALLED
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
''')

TRACE_STAGE = (
    'S.TODO = (GETTER_INVOKE pgettercall) :: ptask_getter* '
    '-- if pgettercall.METHOD = GET_TRACE '
    '-- if S.CURRENT = (pcallcontext) '
    '-- if S.OBJECTS[pgettercall.RECEIVER] = THROWABLE pthrowable')

TRACE = checks(r'''
S.COMPLETION = NORMAL
S.SOURCEPENDING = eps
S.FRAMES = pframe_emit :: pframe_tail*
pframe_emit.TODO = (ERROR_HANDLER_RESULT perrorcall) :: ptask_emit*
perrorcall.RESUME = CLOSURE_CALL_COPY_REFERENCE pclosurecall n_copy n_done pnamedargs n_base
n_done = 0
pnamedargs = {SLOTS eps, NAMED eps}
perrorcall.TARGET = (pcallcontext.TARGET)
perrorcall.LEVEL = 2
n_error = pgettercall.RECEIVER
$throwable_member(S, n_error)
(HOBJECT n_error) <- S.ALLOCATIONS
$closure_call_copy_warning_context(S, pcallcontext)
$ordinary_internal_callback_context(S, pcallcontext)
pclosurecall.FIRST = (POBJECT n_maker)
pclosurecall.RAW = [(KINT 1, KNOWN (POBJECT n_token))]
$lookup(S.ENV, $ptascii("severity")) = (n_severity)
S.STORE[n_severity] = DEFINED (PINT 2)
$lookup(S.ENV, $ptascii("message")) = (n_message)
S.STORE[n_message] = DEFINED pvalue_message
$lookup(S.ENV, $ptascii("file")) = (n_file)
S.STORE[n_file] = DEFINED pvalue_file
$lookup(S.ENV, $ptascii("line")) = (n_line)
S.STORE[n_line] = DEFINED (PINT pclosurecall.LINE)
$trace_context(S, S.ENV, S.CURRENT) = [ptraceframe_handler, ptraceframe_api]
ptraceframe_handler.FILE = eps
ptraceframe_handler.LINE = $(-1)
ptraceframe_handler.FUNCTION = $ptascii("Warning93T")
ptraceframe_handler.CLASS = eps
ptraceframe_handler.TYPE = eps
ptraceframe_handler.HASARGS
ptraceframe_handler.ARGS = [(KINT 0, PINT 2), (KINT 1, pvalue_message), (KINT 2, pvalue_file), (KINT 3, PINT pclosurecall.LINE)]
ptraceframe_api.FILE = $call_sourcefile(S.FILES, pclosurecall.SITE)
ptraceframe_api.LINE = pclosurecall.LINE
ptraceframe_api.FUNCTION = $ptascii("call")
ptraceframe_api.CLASS = ($ptascii("Closure"))
ptraceframe_api.TYPE = ($ptascii("->"))
ptraceframe_api.HASARGS
ptraceframe_api.ARGS = [(KINT 0, POBJECT n_maker), (KINT 1, POBJECT n_token)]
$eval_exception_trace_raw(S) = [ptraceframe_handler, ptraceframe_api]
S_emit = $api_saved_frame_scope($constant_frame_scope(S, pframe_emit, pframe_tail*), pframe_emit, pframe_tail*)
S_emit.SOURCEPENDING = eps
$closure_call_copy_reference_valid(S_emit, pclosurecall, n_copy, n_done, pnamedargs, n_base)
$heap_count(HOBJECT n_copy, $task_nodes(ERROR_HANDLER_RESULT perrorcall)) = 1
$heap_count(HOBJECT n_copy, $task_nodes(ERROR_HANDLER_INVOKE perrorcall)) = 1
$closure_call_copy_pending(ERROR_HANDLER_RESULT perrorcall)
$closure_call_copy_pending(ERROR_HANDLER_INVOKE perrorcall)
~$closure_call_copy_pending(CLOSURE_CALL_REFERENCE pclosurecall n_done pnamedargs n_base)
S_throw = S_emit[.TODO = (THROW_SEARCH n_error) :: pframe_emit.TODO]
S_stop = $source_exception_transition(S_emit, S_throw)
S_stop.COMPLETION = NORMAL
S_stop.TODO = S_throw.TODO
S_stop.ALLOCATIONS = S_throw.ALLOCATIONS
perrorcall_bad = perrorcall[.TARGET = (CLOSURE_TARGET pclosurecall.SOURCE)]
pframe_bad = pframe_emit[.TODO = (ERROR_HANDLER_RESULT perrorcall_bad) :: ptask_emit*]
S_bad = S[.FRAMES = pframe_bad :: pframe_tail*]
~$closure_call_copy_warning_context(S_bad, pcallcontext)
S_no_owner = S[.FRAMES = eps]
~$closure_call_copy_warning_context(S_no_owner, pcallcontext)
''')

CASES = {
    'i93-copy-static-singleton': {'source': ROWS['i93-real-call-reference-singleton-static-warning']['source'], 'stage': FORWARD_STAGE, 'checks': SINGLETON},
    'i93-copy-static-shared': {'source': ROWS['i93-real-call-reference-shared-static-warning']['source'], 'stage': FORWARD_STAGE, 'checks': SHARED},
    'i93-copy-static-temporary': {'source': ROWS['i93-real-call-reference-temporary-static-warning']['source'], 'stage': RETURN_STAGE, 'checks': TEMPORARY},
    'i93-copy-warning-trace': {'source': ROWS['i93-real-call-reference-warning-trace']['source'], 'stage': TRACE_STAGE, 'checks': TRACE},
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
