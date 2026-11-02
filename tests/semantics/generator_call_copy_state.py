#!/usr/bin/env python3
"""Check real copied Generator entry, API retirement and bound Fiber owners."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_call_copy_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {r['id']: r for r in json.loads(INPUT_BYTES[CATALOG])}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


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
$function_generator(S, pfunction)
~$closure_static(S, pfunction)
~$closure_call_reference_formal(pfunction.SIGNATURE.PARAMETERS)
$class_named(S.CLASSNAMES, $ptlc($ptascii("@ACTIVE@"))) = (porigin_active)
pclosurebinding.LEXICAL = (porigin_active)
pclosurebinding.CALLED = (porigin_active)
pclosurebinding.RECEIVER = (n_maker)
S.OBJECTS[n_maker] = INSTANCE porigin_active
(HOBJECT n_maker) <- S.ALLOCATIONS
$closure_scope_at(S.CLOSURESCOPES, n_copy) = eps
$closure_call_copy_site(S, pclosurebinding.SITE)
$closure_call_copy_binding(S, pclosurebinding)
$closure_binding_source_valid(S, pclosurebinding)
$closure_callable(S, n_copy)
$node_children(S, HOBJECT n_copy) = [HOBJECT n_maker]
$target_receiver(S, CLOSURE_TARGET n_copy) = (n_maker)
$target_lexical_class(S, CLOSURE_TARGET n_copy) = (porigin_active)
$target_called_class(S, CLOSURE_TARGET n_copy) = (porigin_active)
$call_selected_valid(S, CLOSURE_TARGET n_copy, (pclosurebinding.SITE))
'''

API_STAGE = (
    'S.TODO = (GENERATOR_CREATE porigin_function) :: ptask_tail* '
    '-- if S.CURRENT = (pcallcontext) '
    '-- if pcallcontext.TARGET = CLOSURE_TARGET n_copy '
    '-- if S.FRAMES = pframe_api :: pframe_tail* '
    '-- if pframe_api.TODO = (CLOSURE_CALL_COPY_RESULT pclosurecall n_copy) :: ptask_api*')

API = checks(COPY.replace('@ACTIVE@', 'Active92A')) + checks(r'''
S.COMPLETION = NORMAL
pcallcontext.INSTANCE = (n_copy)
pcallcontext.FUNCTION = porigin_function
pcallcontext.RECEIVER = (n_maker)
pcallcontext.LEXICAL_CLASS = (porigin_active)
pcallcontext.CALLED_CLASS = (porigin_active)
pcallcontext.CALLSITE = (pclosurebinding.SITE)
pcallcontext.WRAPPER = eps
pcallcontext.ARGC = 1
pclosurecall.SOURCE = n_source
pclosurecall.SITE = pclosurebinding.SITE
pclosurecall.FIRST = (POBJECT n_maker)
pclosurecall.RECEIVER = (n_maker)
pclosurecall.RAW = [(KINT 1, KNOWN (POBJECT n_token))]
pclosurecall.SENT = {SLOTS ([NAMED_SENT (KNOWN (POBJECT n_token))]), NAMED eps}
pclosurecall.INDEX = 2
pclosurecall.PACKS = eps
pclosurecall.ERROR = eps
$closure_call_copy_required(S, pfunction, pclosurecall)
$closure_call_copy_kind(S, pfunction, pclosurecall, n_maker)
$closure_call_copy_result_valid(S, pclosurecall, n_copy)
$task_nodes(CLOSURE_CALL_COPY_RESULT pclosurecall n_copy) = [HOBJECT n_copy, HOBJECT n_maker, HOBJECT n_token, HOBJECT n_source]
$call_current_valid(S)
$generator_creation_supported(S, pcallcontext)
S.GLOBALTABLE = (psymboltable_root)
$lookup(psymboltable_root.ENV, $ptascii("source")) = (n_source_cell)
S.STORE[n_source_cell] = DEFINED (POBJECT n_source)
$lookup(psymboltable_root.ENV, $ptascii("maker")) = (n_maker_cell)
S.STORE[n_maker_cell] = DEFINED (POBJECT n_maker)
$lookup(psymboltable_root.ENV, $ptascii("old")) = (n_old_cell)
S.STORE[n_old_cell] = DEFINED (POBJECT n_old)
$target_receiver(S, CLOSURE_TARGET n_source) = (n_old)
$lookup(psymboltable_root.ENV, $ptascii("token")) = (n_token_cell)
S.STORE[n_token_cell] = DEFINED (POBJECT n_token)
$object_name(S, n_token) = $ptascii("Token92A")
H = $heap_graph(S)
$heap_owners(H, HOBJECT n_source) = 2
$heap_owners(H, HOBJECT n_copy) = 2
$heap_owners(H, HOBJECT n_old) = 2
$heap_owners(H, HOBJECT n_maker) = 3
$heap_owners(H, HOBJECT n_token) = 3
$eval_trace_preparser(S, (pcallcontext), pframe_api) = [ptraceframe_api]
ptraceframe_api.FUNCTION = $ptascii("call")
ptraceframe_api.CLASS = ($ptascii("Closure"))
ptraceframe_api.ARGS = [(KINT 0, POBJECT n_maker), (KINT 1, POBJECT n_token)]
$trace_context(S, S.ENV, (pcallcontext)) = [ptraceframe_body]
ptraceframe_body.FILE = eps
ptraceframe_body.LINE = $(-1)
ptraceframe_body.CLASS = ($ptascii("Active92A"))
pclosurebinding_bad_source = pclosurebinding[.SOURCE = n_copy]
~$closure_call_copy_binding(S, pclosurebinding_bad_source)
pclosurebinding_bad_site = pclosurebinding[.SITE = porigin_function]
~$closure_call_copy_binding(S, pclosurebinding_bad_site)
pclosurebinding_bad_scope = pclosurebinding[.LEXICAL = eps]
~$closure_call_copy_binding(S, pclosurebinding_bad_scope)
pclosurebinding_bad_called = pclosurebinding[.CALLED = eps]
~$closure_call_copy_binding(S, pclosurebinding_bad_called)
pclosurebinding_bad_receiver = pclosurebinding[.RECEIVER = (n_old)]
~$closure_call_copy_binding(S, pclosurebinding_bad_receiver)
~$closure_call_copy_site(S[.CODE = eps], pclosurebinding.SITE)
S_dead_source = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HOBJECT n_source)]
~$closure_call_copy_kind(S_dead_source, pfunction, pclosurecall, n_maker)
S_dead_receiver = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HOBJECT n_maker)]
~$closure_call_copy_kind(S_dead_receiver, pfunction, pclosurecall, n_maker)
pcallcontext_bad_instance = pcallcontext[.INSTANCE = (n_source)]
~$call_current_valid(S[.CURRENT = (pcallcontext_bad_instance)])
$heap_valid(H)
''')


def park():
    return ('S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
            '-- if pconfigcall.KIND = INTRINSIC_FIBER_THROW '
            '-- if pconfigcall.OWNER = (n_fiber) '
            '-- if S.ACTIVEFIBER = eps '
            '-- if S.OBJECTS[n_fiber] = FIBER pfiber '
            '-- if pfiber.STATUS = FIBER_SUSPENDED')


LOCATE = r'''
S.COMPLETION = NORMAL
$lookup(S.ENV, $ptascii("g")) = (n_generator_cell)
S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)
S.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.CLOSURE = (n_copy)
pgenerator.FUNCTION = porigin_function
'''

BODY = r'''
S.CURRENT = eps
S.FRAMES = eps
S.GENERATORINPUTS = eps
S.GC.ACTIVE = eps
pgenerator.PHASE = GENERATOR_RUNNING
pgenerator.FRAME = eps
pgenerator.CREATION = eps
pgenerator.ACCESS = eps
pgenerator.DELEGATE = eps
pfiber.VM = (pfibervm)
pfibervm.CURRENT = (pcallcontext)
pcallcontext.TARGET = CLOSURE_TARGET n_copy
pcallcontext.INSTANCE = (n_copy)
pcallcontext.FUNCTION = porigin_function
pcallcontext.RECEIVER = (n_maker)
pcallcontext.LEXICAL_CLASS = (porigin_active)
pcallcontext.CALLED_CLASS = (porigin_active)
pcallcontext.CALLSITE = (pclosurebinding.SITE)
pcallcontext.WRAPPER = eps
$call_context_roots((pcallcontext)) = [HOBJECT n_copy]
$call_receiver_roots(pcallcontext) = eps
pfibervm.FRAMES = pframe_resume :: pframe_tail*
pframe_resume.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_resume*
pgeneratorop.OBJECT = n_generator
pgeneratorop.NAME = "throw"
pgeneratorop.ARGUMENTS = [POBJECT n_input]
pgeneratorop.LOOP = eps
~pgeneratorop.STARTPACK
~pgeneratorop.BORROWED
$lookup(pfibervm.TABLE.ENV, $ptascii("token")) = eps
$lookup(S.ENV, $ptascii("maker")) = eps
$lookup(S.ENV, $ptascii("weakMaker")) = (n_weak_maker_cell)
S.STORE[n_weak_maker_cell] = DEFINED (POBJECT n_weak_maker)
$weakref_get(S, n_weak_maker) = POBJECT n_maker
$lookup(S.ENV, $ptascii("weakSource")) = (n_weak_source_cell)
S.STORE[n_weak_source_cell] = DEFINED (POBJECT n_weak_source)
$lookup(S.ENV, $ptascii("weakToken")) = (n_weak_token_cell)
S.STORE[n_weak_token_cell] = DEFINED (POBJECT n_weak_token)
$lookup(S.ENV, $ptascii("weakFirst")) = (n_weak_first_cell)
S.STORE[n_weak_first_cell] = DEFINED (POBJECT n_weak_first)
$weakref_get(S, n_weak_first) = POBJECT n_input
S_live = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]
$generator_creation_resume_owner(S_live) = (n_generator)
$fiber_generator_real_closure_valid(S_live, pgenerator, pcallcontext)
$fiber_generator_callee_valid(S_live, pgenerator, pcallcontext)
$fiber_generator_transfer(S_live)
$call_current_valid(S_live)
$closure_evidence_current(S_live) = (CLOSURE_BINDING pclosurebinding)
$eval_trace_preparser(S_live, (pcallcontext), pframe_resume) = eps
H = $heap_graph(S)
$heap_owners(H, HOBJECT n_copy) = 1
$heap_owners(H, HOBJECT n_maker) = 1
pcallcontext_bad_receiver = pcallcontext[.RECEIVER = (n_source)]
~$fiber_generator_real_closure_valid(S_live[.CURRENT = (pcallcontext_bad_receiver)], pgenerator, pcallcontext_bad_receiver)
pcallcontext_bad_called = pcallcontext[.CALLED_CLASS = eps]
~$fiber_generator_real_closure_valid(S_live[.CURRENT = (pcallcontext_bad_called)], pgenerator, pcallcontext_bad_called)
S_no_owner = S_live[.FRAMES = eps]
~$fiber_generator_real_closure_valid(S_no_owner, pgenerator, pcallcontext)
pgenerator_bad_phase = pgenerator[.PHASE = GENERATOR_FRESH]
S_bad_phase = S_live[.OBJECTS = $object_set(S_live.OBJECTS, n_generator, GENERATOR pgenerator_bad_phase)]
~$fiber_generator_real_closure_valid(S_bad_phase, pgenerator_bad_phase, pcallcontext)
S_dead_receiver = S_live[.ALLOCATIONS = $destruction_node_delete(S_live.ALLOCATIONS, HOBJECT n_maker)]
~$fiber_generator_real_closure_valid(S_dead_receiver, pgenerator, pcallcontext)
$heap_valid(H)
'''

REFERENCE = checks(LOCATE) + checks(COPY.replace('@ACTIVE@', 'Active92B')) + checks(BODY) + checks(r'''
pfunction.SIGNATURE.BYREF
~pgeneratorop.ADVANCE
pgenerator.VALUE = eps
pgenerator.REFCELL = (n_cache)
n_cache <- S.REFCELLS
S.STORE[n_cache] = DEFINED (POBJECT n_token)
$object_name(S, n_token) = $ptascii("Token92B")
$weakref_get(S, n_weak_token) = POBJECT n_token
$lookup(pfibervm.TABLE.ENV, $ptascii("e")) = eps
$lookup(S.ENV, $ptascii("source")) = (n_source_cell)
S.STORE[n_source_cell] = DEFINED (POBJECT n_source)
(HOBJECT n_source) <- S.ALLOCATIONS
$weakref_get(S, n_weak_source) = POBJECT n_source
$target_receiver(S, CLOSURE_TARGET n_source) = eps
$heap_owners(H, HOBJECT n_source) = 1
$heap_owners(H, HCELL n_cache) = 1
$heap_owners(H, HOBJECT n_token) = 1
$heap_owners(H, HOBJECT n_input) = 1
$fiber_generator_cached_reference_valid(S_live, pgenerator, pcallcontext)
$fiber_generator_throw_valid(S_live, pgeneratorop, pgenerator, pcallcontext)
S_bad_cache = S_live[.STORE = $set_cell(S_live.STORE, n_cache, UNDEFINED)]
~$fiber_generator_cached_reference_valid(S_bad_cache, pgenerator, pcallcontext)
pgeneratorop_no_input = pgeneratorop[.ARGUMENTS = eps]
~$fiber_generator_throw_valid(S_live, pgeneratorop_no_input, pgenerator, pcallcontext)
''')

FRESH = checks(LOCATE) + checks(COPY.replace('@ACTIVE@', 'Active92C')) + checks(BODY) + checks(r'''
~pfunction.SIGNATURE.BYREF
pgeneratorop.ADVANCE
pgenerator.FIRST
pgenerator.VALUE = eps
pgenerator.REFCELL = eps
pgenerator.KEY = eps
$lookup(S.ENV, $ptascii("source")) = eps
~((HOBJECT n_source) <- S.ALLOCATIONS)
$weakref_get(S, n_weak_source) = PNULL
~$closure_callable(S, n_source)
$weakref_get(S, n_weak_token) = PNULL
$heap_owners(H, HOBJECT n_source) = 0
$heap_owners(H, HOBJECT n_input) = 2
$task_nodes(GENERATOR_RESUME pgeneratorop) = [HOBJECT n_generator, HOBJECT n_input, HOBJECT n_input]
$fiber_generator_fresh_throw_valid(S_live, pgeneratorop, pgenerator, pcallcontext)
pgeneratorop_warm = pgeneratorop[.ADVANCE = false]
~$fiber_generator_fresh_throw_valid(S_live, pgeneratorop_warm, pgenerator, pcallcontext)
pgeneratorop_no_input = pgeneratorop[.ARGUMENTS = eps]
~$fiber_generator_fresh_throw_valid(S_live, pgeneratorop_no_input, pgenerator, pcallcontext)
''')

UNUSED_STAGE = (
    'S.TODO = (CLOSURE_CALL_COPY_RESULT pclosurecall n_copy) :: ptask_tail* '
    '-- if S.CURRENT = eps '
    '-- if S.RESULT = KNOWN (POBJECT n_generator) '
    '-- if S.OBJECTS[n_generator] = GENERATOR pgenerator')

UNUSED = checks(COPY.replace('@ACTIVE@', 'Maker92D')) + checks(r'''
S.COMPLETION = NORMAL
S.FRAMES = eps
pgenerator.PHASE = GENERATOR_FRESH
pgenerator.CLOSURE = (n_copy)
pgenerator.FUNCTION = porigin_function
pgenerator.FRAME = (pframe_generator)
pframe_generator.CONTEXT = (pcallcontext)
pcallcontext.TARGET = CLOSURE_TARGET n_copy
pcallcontext.INSTANCE = (n_copy)
pcallcontext.RECEIVER = (n_maker)
pcallcontext.WRAPPER = eps
pclosurecall.SOURCE = n_source
pclosurecall.FIRST = (POBJECT n_maker)
pclosurecall.RAW = [(KINT 1, KNOWN (POBJECT n_token))]
$target_receiver(S, CLOSURE_TARGET n_source) = (n_old)
$object_name(S, n_token) = $ptascii("Token92D")
$closure_call_copy_discarded(ptask_tail*)
$call_task_valid(S, CLOSURE_CALL_COPY_RESULT pclosurecall n_copy)
$generator_closure_valid(S, pgenerator)
H = $heap_graph(S)
$heap_owners(H, HOBJECT n_generator) = 1
$heap_owners(H, HOBJECT n_copy) = 2
$heap_owners(H, HOBJECT n_maker) = 2
$heap_owners(H, HOBJECT n_token) = 2
$heap_owners(H, HOBJECT n_source) = 1
$heap_owners(H, HOBJECT n_old) = 1
S_one = $drive_steps(S, 1)
S_one.COMPLETION = BUDGET
S_one.RESULT = KNOWN PNULL
S_one.BASE = BASE_VALUE (KNOWN PNULL)
S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_release*
pdestructionrelease.JOBS = $destruction_values([HOBJECT n_copy, HOBJECT n_maker, HOBJECT n_token, HOBJECT n_generator, HOBJECT n_source])
$heap_owners($heap_graph(S_one), HOBJECT n_generator) = 1
S_done = $drive_steps(S, 2400)
S_done = $drive_steps(S_one[.COMPLETION = NORMAL], 2400)
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.CURRENT = eps
S_done.FRAMES = eps
~((HOBJECT n_generator) <- S_done.ALLOCATIONS)
~((HOBJECT n_copy) <- S_done.ALLOCATIONS)
~((HOBJECT n_maker) <- S_done.ALLOCATIONS)
~((HOBJECT n_token) <- S_done.ALLOCATIONS)
~((HOBJECT n_source) <- S_done.ALLOCATIONS)
~((HOBJECT n_old) <- S_done.ALLOCATIONS)
n_token <- S_done.DESTRUCTION.CALLED
n_maker <- S_done.DESTRUCTION.CALLED
n_old <- S_done.DESTRUCTION.CALLED
$heap_valid($heap_graph(S_done))
''')

CASES = {
    'i92-copy-api-entry': {'source': ROWS['i92-real-call-copy-scope-value-send']['source'], 'stage': API_STAGE, 'checks': API},
    'i92-copy-reference-throw': {'source': ROWS['i92-real-call-copy-reference-warm-throw-abort']['source'], 'stage': park(), 'checks': REFERENCE},
    'i92-copy-fresh-throw': {'source': ROWS['i92-real-call-copy-fresh-throw-abort']['source'], 'stage': park(), 'checks': FRESH},
    'i92-copy-unused-result': {'source': ROWS['i92-real-call-copy-unused-result-cleanup']['source'], 'stage': UNUSED_STAGE, 'checks': UNUSED},
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
        passed = review.run(selected, process_seconds=300)
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
