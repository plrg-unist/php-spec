#!/usr/bin/env python3
"""Check fake copy entry, shared method statics and ignored-result cleanup."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_fake_call_copy_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {r['id']: r for r in json.loads(INPUT_BYTES[CATALOG])}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


COPY = r'''
S.COMPLETION = NORMAL
S.OBJECTS[n_copy] = BOUNDFAKECLOSURE pboundfake_copy
(HOBJECT n_copy) <- S.ALLOCATIONS
n_source = pboundfake_copy.SOURCE
$(n_source < n_copy)
pboundfake_copy.ORIGINAL = (pclosurescope_original)
pclosurescope_original.OBJECT = n_source
pclosurescope_original.CREATION = eps
pclosurescope_original.RECEIVER = (n_old)
$class_named(S.CLASSNAMES, $ptlc($ptascii("@BASE@"))) = (porigin_base)
pboundfake_copy.SCOPE = BIND_CLASS porigin_base
pboundfake_copy.CALLED = BIND_CLASS porigin_base
pboundfake_copy.RECEIVER = (n_maker)
n_old =/= n_maker
S.OBJECTS[n_maker] = INSTANCE porigin_base
S.OBJECTS[n_old] = INSTANCE porigin_base
$closure_scope_at(S.CLOSURESCOPES, n_copy) = eps
$closure_binding_at(S.CLOSUREBINDINGS, n_copy) = eps
$closure_call_copy_site(S, pboundfake_copy.SITE)
$closure_call_fake_copy_binding(S, pboundfake_copy)
$bound_fake_valid(S, n_copy)
$closure_call_copy_row(S, n_copy) = (pclosurebinding_copy)
pclosurebinding_copy.OBJECT = n_copy
pclosurebinding_copy.SOURCE = n_source
pclosurebinding_copy.SITE = pboundfake_copy.SITE
pclosurebinding_copy.LEXICAL = (porigin_base)
pclosurebinding_copy.CALLED = (porigin_base)
pclosurebinding_copy.RECEIVER = (n_maker)
~$closure_call_copy_binding(S, pclosurebinding_copy)
$target_function(S, CLOSURE_TARGET n_copy) = (pfunction)
porigin_function = pfunction.ORIGIN
$class_method_origin(S.CLASSES, porigin_function) = (pmethoddesc)
pmethoddesc.OWNER = porigin_base
~pmethoddesc.STATIC
$function_generator(S, pfunction)
$closure_callable(S, n_copy)
$node_children(S, HOBJECT n_copy) = [HOBJECT n_maker]
$target_lexical_class(S, CLOSURE_TARGET n_copy) = (porigin_base)
$target_called_class(S, CLOSURE_TARGET n_copy) = (porigin_base)
$target_receiver(S, CLOSURE_TARGET n_copy) = (n_maker)
$call_selected_valid(S, CLOSURE_TARGET n_copy, (pboundfake_copy.SITE))
'''

API_STAGE = (
    'S.TODO = (GENERATOR_CREATE porigin_function) :: ptask_tail* '
    '-- if S.CURRENT = (pcallcontext) '
    '-- if pcallcontext.TARGET = CLOSURE_TARGET n_copy '
    '-- if S.FRAMES = pframe_api :: pframe_tail* '
    '-- if pframe_api.TODO = (CLOSURE_CALL_COPY_RESULT pclosurecall n_copy) :: ptask_api*')

API = checks(COPY.replace('@BASE@', 'Base94A')) + checks(r'''
S.OBJECTS[n_source] = METHODCLOSURE porigin_function porigin_capture porigin_requested pmethodcapture?
$closure_call_fake_method(S, n_source, pfunction)
~$closure_call_real(S, n_source)
~pfunction.SIGNATURE.BYREF
~$closure_call_reference_formal(pfunction.SIGNATURE.PARAMETERS)
pcallcontext.FUNCTION = porigin_function
pcallcontext.TARGET = CLOSURE_TARGET n_copy
pcallcontext.INSTANCE = (n_copy)
pcallcontext.LEXICAL_CLASS = (porigin_base)
pcallcontext.CALLED_CLASS = (porigin_base)
pcallcontext.RECEIVER = (n_maker)
pcallcontext.CALLSITE = (pboundfake_copy.SITE)
pcallcontext.WRAPPER = eps
pcallcontext.ARGC = 1
pclosurecall.SOURCE = n_source
pclosurecall.SITE = pboundfake_copy.SITE
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
$call_context_roots((pcallcontext)) = [HOBJECT n_copy]
$call_receiver_roots(pcallcontext) = eps
$call_current_valid(S)
$generator_creation_supported(S, pcallcontext)
S.GLOBALTABLE = (psymboltable_root)
$lookup(psymboltable_root.ENV, $ptascii("source")) = (n_source_cell)
S.STORE[n_source_cell] = DEFINED (POBJECT n_source)
$lookup(psymboltable_root.ENV, $ptascii("old")) = (n_old_cell)
S.STORE[n_old_cell] = DEFINED (POBJECT n_old)
$lookup(psymboltable_root.ENV, $ptascii("maker")) = (n_maker_cell)
S.STORE[n_maker_cell] = DEFINED (POBJECT n_maker)
$lookup(psymboltable_root.ENV, $ptascii("token")) = (n_token_cell)
S.STORE[n_token_cell] = DEFINED (POBJECT n_token)
$object_name(S, n_token) = $ptascii("Token94A")
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
pboundfake_bad_scope = pboundfake_copy[.SCOPE = BIND_UNSCOPED]
~$closure_call_fake_copy_binding(S, pboundfake_bad_scope)
pboundfake_bad_called = pboundfake_copy[.CALLED = BIND_UNSCOPED]
~$closure_call_fake_copy_binding(S, pboundfake_bad_called)
pboundfake_old = pboundfake_copy[.RECEIVER = (n_old)]
S_old = S[.OBJECTS = $object_set(S.OBJECTS, n_copy, BOUNDFAKECLOSURE pboundfake_old)]
$closure_call_fake_copy_binding(S_old, pboundfake_old)
~$closure_call_copy_result_valid(S_old, pclosurecall, n_copy)
~$call_current_valid(S_old)
S_dead_source = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HOBJECT n_source)]
~$closure_call_copy_kind(S_dead_source, pfunction, pclosurecall, n_maker)
S_dead_receiver = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HOBJECT n_maker)]
~$closure_call_copy_kind(S_dead_receiver, pfunction, pclosurecall, n_maker)
~$closure_call_copy_site(S[.CODE = eps], pboundfake_copy.SITE)
$heap_valid(H)
''')

STATIC_STAGE = (
    'S.TODO = (CLOSURE_CALL_COPY_FORWARD pclosurecall n_copy n_done pnamedargs n_base) :: ptask_tail* '
    '-- if n_done = 1')

STATIC = checks(COPY.replace('@BASE@', 'Base94B')) + checks(r'''
S.CURRENT = eps
S.FRAMES = eps
S.OBJECTS[n_source] = METHODCLOSURE porigin_function porigin_capture porigin_requested pmethodcapture?
$closure_call_fake_method(S, n_source, pfunction)
~pfunction.SIGNATURE.BYREF
$call_parameter_at(pfunction.SIGNATURE.PARAMETERS, 0) = (psparam)
psparam.BYREF
S.STATICS = [pstaticcell_counter]
n_counter = pstaticcell_counter.CELL
S.STORE[n_counter] = DEFINED (PINT 2)
n_counter <- S.REFCELLS
$(n_counter < n_base)
$static_roots(S.STATICS) = [HCELL n_counter]
pclosurecall.SOURCE = n_source
pclosurecall.SITE = pboundfake_copy.SITE
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
$(n_base <= n_formal)
n_formal =/= n_counter
$object_name(S, n_token) = $ptascii("Token94B")
$closure_call_copy_forward_valid(S, pclosurecall, n_copy, n_done, pnamedargs, n_base)
$task_nodes(CLOSURE_CALL_COPY_FORWARD pclosurecall n_copy n_done pnamedargs n_base) = [HOBJECT n_copy, HOBJECT n_maker, HOBJECT n_token, HOBJECT n_source, HCELL n_formal]
$lookup(S.ENV, $ptascii("warningCount")) = (n_count)
S.STORE[n_count] = DEFINED (PINT 1)
$lookup(S.ENV, $ptascii("source")) = (n_source_cell)
S.STORE[n_source_cell] = DEFINED (POBJECT n_source)
$lookup(S.ENV, $ptascii("seed")) = eps
$lookup(S.ENV, $ptascii("old")) = eps
H = $heap_graph(S)
$heap_owners(H, HOBJECT n_copy) = 1
$heap_owners(H, HOBJECT n_source) = 2
$heap_owners(H, HOBJECT n_old) = 1
$heap_owners(H, HOBJECT n_maker) = 3
$heap_owners(H, HOBJECT n_token) = 2
$heap_owners(H, HCELL n_formal) = 1
$heap_owners(H, HCELL n_counter) = 1
pnamedargs_alias = {SLOTS ([NAMED_SENT (REFERENCE n_counter)]), NAMED eps}
S_alias = S[.STORE = $set_cell(S.STORE, n_counter, DEFINED (POBJECT n_token))]
$closure_call_copy_result_valid(S_alias, pclosurecall, n_copy)
~$closure_call_copy_forward_valid(S_alias, pclosurecall, n_copy, n_done, pnamedargs_alias, 0)
S_one = $drive_steps(S, 1)
S_one.COMPLETION = BUDGET
S_one.CURRENT = (pcallcontext_copy)
pcallcontext_copy.TARGET = CLOSURE_TARGET n_copy
pcallcontext_copy.INSTANCE = (n_copy)
pcallcontext_copy.RECEIVER = (n_maker)
pcallcontext_copy.WRAPPER = eps
$lookup(S_one.ENV, $ptascii("token")) = (n_formal)
$state_static_at(S_one, pstaticcell_counter.ORIGIN) = (n_counter)
S_one.STATICS = S.STATICS
$heap_owners($heap_graph(S_one), HOBJECT n_copy) = 2
$heap_valid(H)
''')

UNUSED_STAGE = (
    'S.TODO = (CLOSURE_CALL_COPY_RESULT pclosurecall n_copy) :: ptask_tail* '
    '-- if S.CURRENT = eps '
    '-- if S.RESULT = KNOWN (POBJECT n_generator) '
    '-- if S.OBJECTS[n_generator] = GENERATOR pgenerator')

UNUSED = checks(COPY.replace('@BASE@', 'Base94C')) + checks(r'''
S.OBJECTS[n_source] = ARRAYMETHODCLOSURE pcalltarget_selected parrayselection pmethodcapture?
S.FRAMES = eps
pgenerator.PHASE = GENERATOR_FRESH
~pgenerator.FIRST
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
$object_name(S, n_token) = $ptascii("Token94C")
$closure_call_copy_discarded(ptask_tail*)
$call_task_valid(S, CLOSURE_CALL_COPY_RESULT pclosurecall n_copy)
$closure_call_copy_return_valid(S, n_copy, n_generator)
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
    'i94-fake-copy-api-entry': {'source': ROWS['i94-fake-method-call-value-send']['source'], 'stage': API_STAGE, 'checks': API},
    'i94-fake-copy-shared-statics': {'source': ROWS['i94-fake-method-call-static-reference-warning']['source'], 'stage': STATIC_STAGE, 'checks': STATIC},
    'i94-fake-copy-unused-result': {'source': ROWS['i94-fake-array-method-call-unused-result']['source'], 'stage': UNUSED_STAGE, 'checks': UNUSED},
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
