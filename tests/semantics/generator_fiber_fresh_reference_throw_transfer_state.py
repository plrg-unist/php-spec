#!/usr/bin/env python3
"""Check a reached fresh named by-reference THROW parameter/local cells and saved-VM authentication."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_fiber_fresh_reference_throw_transfer_cases.json')
INPUT_BYTES = {path: path.read_bytes() for path in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]

PARK_STAGE = (
    'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
    '-- if pconfigcall.KIND = INTRINSIC_FIBER_RESUME '
    '-- if pconfigcall.OWNER = (n_fiber) '
    '-- if S.OBJECTS[n_fiber] = FIBER pfiber '
    '-- if pfiber.STATUS = FIBER_SUSPENDED '
    '-- if $lookup(S.ENV, $ptascii("g")) = (n_generator_cell) '
    '-- if S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator) '
    '-- if S.OBJECTS[n_generator] = GENERATOR pgenerator '
    '-- if pgenerator.REFCELL = eps')
COMMON = checks(r"""
S.COMPLETION = NORMAL
S.ACTIVEFIBER = eps
S.CURRENT = eps
S.FRAMES = eps
S.FIBERCALLERS = eps
S.FIBERCLOSERS = eps
$lookup(S.ENV, $ptascii("g")) = (n_generator_cell)
S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)
S.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.CLOSURE = eps
pgenerator.VALUE = eps
pgenerator.DELEGATE = eps
pgenerator.RETURN = eps
~pgenerator.PENDING_INIT
$lookup(S.ENV, $ptascii("weakGiven")) = (n_weak_given_cell)
S.STORE[n_weak_given_cell] = DEFINED (POBJECT n_weak_given)
S.OBJECTS[n_weak_given] = WEAKREFERENCE (n_given)
$node_children(S, HOBJECT n_weak_given) = eps
$function_at(S.FUNCTIONS, pgenerator.FUNCTION) = (pfunction)
pfunction.SIGNATURE.BYREF
$generator_reference_producer(S, pgenerator)
""")
FRESH = checks(r"""
pgenerator.PHASE = GENERATOR_RUNNING
pgenerator.FIRST
pgenerator.FRAME = eps
pgenerator.REFCELL = eps
$node_children(S, HOBJECT n_generator) = eps
$weakref_get(S, n_weak_given) = POBJECT n_given
$throwable_member(S, n_given)
pfiber.VM = (pfibervm)
~pfibervm.GLOBAL
pfibervm.CURRENT = (pcallcontext_generator)
pfibervm.FRAMES = pframe_generator :: pframe_tail*
pframe_generator.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_generator*
pframe_generator.CONTEXT = (pcallcontext_callback)
pgeneratorop.OBJECT = n_generator
pgeneratorop.NAME = "throw"
pgeneratorop.ARGUMENTS = [POBJECT n_given]
pgeneratorop.LOOP = eps
pgeneratorop.ADVANCE
~pgeneratorop.STARTPACK
~pgeneratorop.BORROWED
$task_nodes(GENERATOR_RESUME pgeneratorop) = [HOBJECT n_generator, HOBJECT n_given]
$heap_owners($heap_graph(S), HOBJECT n_given) = 1
pcallcontext_generator.FUNCTION = pgenerator.FUNCTION
pcallcontext_generator.TARGET = pgenerator.FUNCTION
pcallcontext_generator.INSTANCE = eps
pcallcontext_generator.RECEIVER = eps
pcallcontext_generator.LEXICAL_CLASS = eps
pcallcontext_generator.CALLED_CLASS = eps
S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]
$generator_record_valid(S_view, pgenerator)
$call_current_valid(S_view)
$fiber_vm_valid(S, pfibervm, (n_fiber), eps)
$fiber_generator_callee_valid(S_view, pgenerator, pcallcontext_generator)
$fiber_generator_cached_reference_valid(S_view, pgenerator, pcallcontext_generator)
$fiber_generator_fresh_throw_valid(S_view, pgeneratorop, pgenerator, pcallcontext_generator)
~$fiber_generator_throw_valid(S_view, pgeneratorop, pgenerator, pcallcontext_generator)
$fiber_generator_body_id(S_view) = (n_generator)
$fiber_transfer_domain(S_view)
$generator_saved_fiber_ids(S) = [n_generator]
$generator_owners_valid(S)
""")
PARAMETER = checks(r"""
pfunction.NAME = $ptascii("Work71Catch")
$lookup(S.ENV, $ptascii("old")) = (n_item)
$lookup(S.ENV, $ptascii("slot")) = (n_new)
S.STORE[n_item] = DEFINED (PINT 7)
S.STORE[n_new] = DEFINED (PINT 9)
n_item =/= n_new
n_item <- S.REFCELLS
$lookup(pfibervm.TABLE.ENV, $ptascii("item")) = (n_item)
pframe_generator.LOCALS = (psymboltable_callback)
$lookup(psymboltable_callback.ENV, $ptascii("old")) = (n_item)
$heap_owners($heap_graph(S), HCELL n_item) = 3
$heap_count(HCELL n_item, $fiber_vm_nodes(pfibervm)) = 2
""")
AUTHENTICATION = checks(r"""
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop[.NAME = "current"][.ARGUMENTS = eps], pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop[.NAME = "next"][.ARGUMENTS = eps], pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop[.NAME = "send"][.ARGUMENTS = [PINT 3]], pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop[.ARGUMENTS = eps], pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop[.ARGUMENTS = [POBJECT n_fiber]], pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop[.ADVANCE = false], pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop, pgenerator[.FIRST = false], pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop, pgenerator[.VALUE = (PINT 7)], pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop, pgenerator[.REFCELL = (n_item)], pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop, pgenerator[.CLOSURE = (n_fiber)], pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop, pgenerator, pcallcontext_generator[.INSTANCE = (n_fiber)])
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop, pgenerator, pcallcontext_generator[.TARGET = METHOD_TARGET n_fiber pgenerator.FUNCTION])
pcallcontext_badname = pcallcontext_generator[.NAME = $ptascii("forged71")]
S_badname = S_view[.CURRENT = (pcallcontext_badname)]
$fiber_generator_fresh_throw_valid(S_badname, pgeneratorop, pgenerator, pcallcontext_badname)
~$call_current_valid(S_badname)
~$fiber_vm_valid(S, pfibervm[.CURRENT = (pcallcontext_badname)], (n_fiber), eps)
pcallcontext_receiver = pcallcontext_generator[.RECEIVER = (n_fiber)]
S_receiver = S_view[.CURRENT = (pcallcontext_receiver)]
$fiber_generator_fresh_throw_valid(S_receiver, pgeneratorop, pgenerator, pcallcontext_receiver)
~$call_current_valid(S_receiver)
~$fiber_vm_valid(S, pfibervm[.CURRENT = (pcallcontext_receiver)], (n_fiber), eps)
pcallcontext_site = pcallcontext_generator[.CALLSITE = (pgeneratorop.SITE)]
S_site = S_view[.CURRENT = (pcallcontext_site)]
~$call_current_valid(S_site)
~$fiber_vm_valid(S, pfibervm[.CURRENT = (pcallcontext_site)], (n_fiber), eps)
pgenerator_bogus = pgenerator[.FUNCTION = pcallcontext_callback.FUNCTION]
pcallcontext_bogus = pcallcontext_generator[.FUNCTION = pcallcontext_callback.FUNCTION][.TARGET = pcallcontext_callback.FUNCTION]
S_bogus = $generator_set(S_view, n_generator, pgenerator_bogus)[.CURRENT = (pcallcontext_bogus)]
$fiber_generator_fresh_throw_valid(S_bogus, pgeneratorop, pgenerator_bogus, pcallcontext_bogus)
~$generator_record_valid(S_bogus, pgenerator_bogus)
S_noadvance = S_view[.FRAMES = pframe_generator[.TODO = (GENERATOR_RESUME pgeneratorop[.ADVANCE = false]) :: ptask_generator*] :: pframe_tail*]
$fiber_generator_body_id(S_noadvance) = eps
S_line = S_view[.FRAMES = pframe_generator[.TODO = (GENERATOR_RESUME pgeneratorop[.LINE = $(pgeneratorop.LINE + 1)]) :: ptask_generator*] :: pframe_tail*]
$fiber_generator_body_id(S_line) = eps
S_duplicate = S_view[.FRAMES = pframe_generator :: pframe_generator :: pframe_tail*]
$fiber_generator_body_id(S_duplicate) = eps
""")
LOCAL_OBJECTS = checks(r"""
pfunction.NAME = $ptascii("Work71Local")
$lookup(S.ENV, $ptascii("factory")) = (n_factory)
S.STORE[n_factory] = DEFINED pvalue_factory
$string_bytes(pvalue_factory) = ($ptascii("Other71Local"))
$lookup(S.ENV, $ptascii("token")) = (n_input)
S.STORE[n_input] = DEFINED (POBJECT n_new)
$object_name(S, n_new) = $ptascii("New71Local")
$lookup(S.ENV, $ptascii("weakOld")) = (n_weak_old_cell)
S.STORE[n_weak_old_cell] = DEFINED (POBJECT n_weak_old)
S.OBJECTS[n_weak_old] = WEAKREFERENCE (n_old)
$weakref_get(S, n_weak_old) = POBJECT n_old
$object_name(S, n_old) = $ptascii("Old71Local")
$heap_owners($heap_graph(S), HOBJECT n_old) = 1
$heap_owners($heap_graph(S), HOBJECT n_new) = 1
""")
LOCAL_FRESH = checks(r"""
$lookup(pfibervm.TABLE.ENV, $ptascii("item")) = (n_item)
S.STORE[n_item] = DEFINED (POBJECT n_old)
n_item =/= n_input
~(n_item <- S.REFCELLS)
$heap_owners($heap_graph(S), HCELL n_item) = 1
pcallcontext_generator.CALLSITE = (porigin_creator)
$dynamic_site(S_view, (porigin_creator))
$dynamic_fixed_name(S_view, porigin_creator) = eps
$call_selected_valid(S_view, pgenerator.FUNCTION, (porigin_creator))
""")
LOCAL_CLOSED = checks(r"""
pgenerator.PHASE = GENERATOR_CLOSED
pgenerator.FRAME = eps
pgenerator.REFCELL = (n_item)
n_item <- S.REFCELLS
S.STORE[n_item] = DEFINED (POBJECT n_old)
n_item =/= n_input
$node_children(S, HOBJECT n_generator) = [HCELL n_item]
$heap_owners($heap_graph(S), HCELL n_item) = 1
~((HOBJECT n_given) <- S.ALLOCATIONS)
$weakref_get(S, n_weak_given) = PNULL
~(n_old <- S.DESTRUCTION.CALLED)
$generator_saved_fiber_ids(S) = eps
$generator_owners_valid(S)
""")
ENDING = checks(r"""
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
S_zero = $drive_steps(S, 0)
S_zero.COMPLETION = BUDGET
S_zero[.COMPLETION = NORMAL] = S
S_one_budget = $drive_steps(S, 1)
S_one_budget.COMPLETION = BUDGET
S_one = S_one_budget[.COMPLETION = NORMAL]
$drive_steps(S, 2) = $drive_steps(S_one, 1)
S_done = $drive_steps(S_one, 4000)
$drive_steps(S, 4000) = S_done
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.FRAMES = eps
S_done.CURRENT = eps
S_done.ACTIVEFIBER = eps
S_done.FIBERCALLERS = eps
S_done.FIBERCLOSERS = eps
~((HOBJECT n_given) <- S_done.ALLOCATIONS)
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
""")
OBJECTS_END = checks(r"""
n_old <- S_done.DESTRUCTION.CALLED
n_new <- S_done.DESTRUCTION.CALLED
~((HOBJECT n_old) <- S_done.ALLOCATIONS)
~((HOBJECT n_new) <- S_done.ALLOCATIONS)
""")
LOCAL_SOURCE = ROWS['i71-fresh-dynamic-named-local-copy-finally']['source']
CACHE_LINE = next(i for i,line in enumerate(LOCAL_SOURCE.splitlines(),1) if line.startswith("echo 'CACHE|'"))
CASES = {
    'i71-parameter-pre-yield-cell-authentication':
        {'source': ROWS['i71-fresh-named-reference-parameter-catch']['source'],
         'stage': PARK_STAGE,
         'checks': [*COMMON, *FRESH, *PARAMETER, *AUTHENTICATION, *ENDING]},
    'i71-dynamic-local-before-reference-promotion':
        {'source': LOCAL_SOURCE, 'stage': PARK_STAGE,
         'checks': [*COMMON, *FRESH, *LOCAL_OBJECTS, *LOCAL_FRESH, *ENDING, *OBJECTS_END]},
    'i71-closed-sole-local-reference-cache':
        {'source': LOCAL_SOURCE,
         'stage': 'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
                  '-- if pconfigcall.KIND = INTRINSIC_WEAKREF_GET '
                  f'-- if pconfigcall.LINE = {CACHE_LINE}',
         'checks': [*COMMON, *LOCAL_OBJECTS, *LOCAL_CLOSED, *ENDING, *OBJECTS_END]},
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
    stable = INPUT_BYTES == {path: path.read_bytes() for path in INPUT_BYTES}
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=review.ROOT, text=True).strip()
    report_path = raw / 'report.json'
    report = json.loads(report_path.read_bytes())
    report.update(author_inputs={str(path): hashlib.sha256(data).hexdigest() for path, data in INPUT_BYTES.items()},
                  author_inputs_stable=stable, head_stable=head_stable,
                  passed=passed and stable and head_stable)
    report_path.write_text(json.dumps(report, indent=2) + '\n')
    return report['passed']

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    raise SystemExit(0 if run(parser.parse_args().case) else 1)
