#!/usr/bin/env python3
"""Check live BF storage and detached formals across a retired method source."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_fake_string_call_cases.json')
INPUT_BYTES = {p: p.read_bytes() for p in (Path(__file__), CATALOG, Path(review.__file__))}
ROW = next(r for r in json.loads(INPUT_BYTES[CATALOG])
           if r['id'] == 'i95-fake-bound-call-shared-static-warning')
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


SOURCE = r'''
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
S.OBJECTS[n_source] = BOUNDFAKECLOSURE pboundfake_source
(HOBJECT n_source) <- S.ALLOCATIONS
n_original = pboundfake_source.SOURCE
$(n_original < n_source)
S.OBJECTS[n_original] = METHODCLOSURE porigin_function porigin_capture porigin_requested pmethodcapture?
pboundfake_source.ORIGINAL = (pclosurescope_original)
pclosurescope_original.OBJECT = n_original
pclosurescope_original.CREATION = eps
pclosurescope_original.RECEIVER = (n_old)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base95B"))) = (porigin_base)
pclosurescope_original.LEXICAL = porigin_base
pclosurescope_original.CALLED = porigin_base
pboundfake_source.SCOPE = BIND_CLASS porigin_base
pboundfake_source.CALLED = BIND_CLASS porigin_base
pboundfake_source.RECEIVER = (n_middle)
S.OBJECTS[n_old] = INSTANCE porigin_base
S.OBJECTS[n_middle] = INSTANCE porigin_base
(HOBJECT n_middle) <- S.ALLOCATIONS
~((HOBJECT n_original) <- S.ALLOCATIONS)
~((HOBJECT n_old) <- S.ALLOCATIONS)
$closure_scope_at(S.CLOSURESCOPES, n_original) = eps
$closure_scope_at(S.CLOSURESCOPES, n_source) = eps
$closure_binding_at(S.CLOSUREBINDINGS, n_source) = eps
~$closure_callable(S, n_original)
$closure_binding_api_site(S, pboundfake_source.SITE)
~$closure_call_fake_copy_binding(S, pboundfake_source)
$bound_fake_valid(S, n_source)
$class_method_origin(S.CLASSES, porigin_function) = (pmethoddesc)
pfunction = pmethoddesc.FUNCTION
pmethoddesc.OWNER = porigin_base
~pmethoddesc.STATIC
$function_generator(S, pfunction)
~pfunction.SIGNATURE.BYREF
$call_parameter_at(pfunction.SIGNATURE.PARAMETERS, 0) = (psparam)
psparam.BYREF
$target_function(S, CLOSURE_TARGET n_source) = (pfunction)
$node_children(S, HOBJECT n_source) = [HOBJECT n_middle]
$lookup(S.ENV, $ptascii("source")) = (n_source_cell)
S.STORE[n_source_cell] = DEFINED (POBJECT n_source)
$lookup(S.ENV, $ptascii("original")) = eps
$lookup(S.ENV, $ptascii("old")) = eps
$lookup(S.ENV, $ptascii("middle")) = eps
$lookup(S.ENV, $ptascii("weakOriginal")) = (n_weak_original_cell)
S.STORE[n_weak_original_cell] = DEFINED (POBJECT n_weak_original)
$weakref_get(S, n_weak_original) = PNULL
$lookup(S.ENV, $ptascii("weakOld")) = (n_weak_old_cell)
S.STORE[n_weak_old_cell] = DEFINED (POBJECT n_weak_old)
$weakref_get(S, n_weak_old) = PNULL
S.STATICS = [pstaticcell_counter]
n_counter = pstaticcell_counter.CELL
n_counter <- S.REFCELLS
$static_roots(S.STATICS) = [HCELL n_counter]
'''

LIVE_STAGE = (
    'S.TODO = (GENERATOR_STORAGE_STEP pgenstorage) :: ptask_tail* '
    '-- if pgenstorage.NEXT = 1 '
    '-- if S.CURRENT = eps '
    '-- if S.OBJECTS[pgenstorage.OBJECT] = GENERATOR pgenerator '
    '-- if pgenerator.CLOSURE = (n_source) '
    '-- if $lookup(S.ENV, $ptascii("source")) = (n_cell) '
    '-- if S.STORE[n_cell] = DEFINED (POBJECT n_source)')

LIVE = checks(SOURCE) + checks(r'''
n_generator = pgenstorage.OBJECT
pgenerator.PHASE = GENERATOR_CLOSED
pgenerator.FRAME = eps
pgenerator.FUNCTION = porigin_function
$generator_storage_closure_borrowed(S, pgenerator)
$generator_captured_factory_scope(S, n_source) = (pclosurescope_source)
pclosurescope_source.OBJECT = n_source
pclosurescope_source.LEXICAL = porigin_base
pclosurescope_source.CALLED = porigin_base
pclosurescope_source.RECEIVER = (n_middle)
$generator_captured_factory_valid(S, pclosurescope_source, porigin_function)
~$generator_storage_method_history(S, pgenerator)
$generator_storage_history(S, pgenerator)
$generator_closure_valid(S, pgenerator)
$generator_storage_valid(S, pgenstorage)
$generator_storage_remaining(pgenerator, 1) = eps
$node_children(S, HOBJECT n_generator) = eps
S.STORE[n_counter] = DEFINED (PINT 1)
H = $heap_graph(S)
$heap_owners(H, HOBJECT n_generator) = 1
$heap_owners(H, HOBJECT n_source) = 1
$heap_owners(H, HOBJECT n_middle) = 1
$heap_owners(H, HOBJECT n_original) = 0
$heap_owners(H, HOBJECT n_old) = 0
$heap_owners(H, HCELL n_counter) = 1
S_no_storage = S[.TODO = ptask_tail*]
$generator_storage_record(S_no_storage, pgenerator) = eps
~$generator_storage_closure_borrowed(S_no_storage, pgenerator)
$generator_storage_history(S_no_storage, pgenerator)
$class_at(S.CLASSES, porigin_base) = (pclassdesc)
$method_named(pclassdesc.METHODS, $ptascii("__construct")) = (pmethoddesc_other)
pgenerator_bad_function = pgenerator[.FUNCTION = pmethoddesc_other.FUNCTION.ORIGIN]
~$generator_storage_history(S, pgenerator_bad_function)
$call_descriptors_valid(S)
$heap_valid(H)
''')

FORWARD_STAGE = (
    'S.TODO = (CLOSURE_CALL_COPY_FORWARD pclosurecall n_copy n_done pnamedargs n_base) :: ptask_tail* '
    '-- if n_done = 1')

FORWARD = checks(r'''
S.OBJECTS[n_copy] = BOUNDFAKECLOSURE pboundfake_copy
n_source = pboundfake_copy.SOURCE
''') + checks(SOURCE) + checks(r'''
$(n_source < n_copy)
(HOBJECT n_copy) <- S.ALLOCATIONS
pboundfake_copy.ORIGINAL = eps
pboundfake_copy.SCOPE = BIND_CLASS porigin_base
pboundfake_copy.CALLED = BIND_CLASS porigin_base
pboundfake_copy.RECEIVER = (n_maker)
S.OBJECTS[n_maker] = INSTANCE porigin_base
$closure_scope_at(S.CLOSURESCOPES, n_copy) = eps
$closure_binding_at(S.CLOSUREBINDINGS, n_copy) = eps
$closure_call_fake_copy_binding(S, pboundfake_copy)
$closure_call_copy_row(S, n_copy) = (pclosurebinding_copy)
pclosurebinding_copy.SOURCE = n_source
pclosurebinding_copy.RECEIVER = (n_maker)
$target_function(S, CLOSURE_TARGET n_copy) = (pfunction)
$node_children(S, HOBJECT n_copy) = [HOBJECT n_maker]
S.STORE[n_counter] = DEFINED (PINT 2)
$(n_counter < n_base)
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
$object_name(S, n_token) = $ptascii("Token95B")
$closure_call_copy_forward_valid(S, pclosurecall, n_copy, n_done, pnamedargs, n_base)
$lookup(S.ENV, $ptascii("warningCount")) = (n_count)
S.STORE[n_count] = DEFINED (PINT 1)
H = $heap_graph(S)
$heap_owners(H, HOBJECT n_copy) = 1
$heap_owners(H, HOBJECT n_source) = 2
$heap_owners(H, HOBJECT n_middle) = 1
$heap_owners(H, HOBJECT n_original) = 0
$heap_owners(H, HOBJECT n_old) = 0
$heap_owners(H, HOBJECT n_maker) = 3
$heap_owners(H, HOBJECT n_token) = 2
$heap_owners(H, HCELL n_formal) = 1
$heap_owners(H, HCELL n_counter) = 1
pnamedargs_alias = {SLOTS ([NAMED_SENT (REFERENCE n_counter)]), NAMED eps}
S_alias = S[.STORE = $set_cell(S.STORE, n_counter, DEFINED (POBJECT n_token))]
$closure_call_copy_result_valid(S_alias, pclosurecall, n_copy)
~$closure_call_copy_forward_valid(S_alias, pclosurecall, n_copy, n_done, pnamedargs_alias, 0)
pclosurescope_bad = pclosurescope_original[.OBJECT = n_copy]
pboundfake_bad_original = pboundfake_source[.ORIGINAL = (pclosurescope_bad)]
S_bad_original = S[.OBJECTS = $object_set(S.OBJECTS, n_source, BOUNDFAKECLOSURE pboundfake_bad_original)]
~$closure_call_fake_copy_binding(S_bad_original, pboundfake_copy)
pboundfake_cycle = pboundfake_source[.SOURCE = n_copy]
S_cycle = S[.OBJECTS = $object_set(S.OBJECTS, n_source, BOUNDFAKECLOSURE pboundfake_cycle)]
~$closure_call_fake_copy_binding(S_cycle, pboundfake_copy)
pboundfake_bad_site = pboundfake_copy[.SITE = porigin_function]
~$closure_call_fake_copy_binding(S, pboundfake_bad_site)
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

CASES = {
    'i95-live-bound-source-storage': {'source': ROW['source'], 'stage': LIVE_STAGE, 'checks': LIVE},
    'i95-bound-source-reference-forward': {'source': ROW['source'], 'stage': FORWARD_STAGE, 'checks': FORWARD},
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
