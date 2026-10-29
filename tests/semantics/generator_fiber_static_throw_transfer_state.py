#!/usr/bin/env python3
"""Check source-reached static Generator THROW scopes, roots and admission."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_fiber_static_throw_transfer_cases.json')
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
    '-- if pfiber.STATUS = FIBER_SUSPENDED')
COMMON = checks(r'''
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
pgenerator.DELEGATE = eps
pgenerator.RETURN = eps
~pgenerator.PENDING_INIT
$lookup(S.ENV, $ptascii("weakGiven")) = (n_weak_given_cell)
S.STORE[n_weak_given_cell] = DEFINED (POBJECT n_weak_given)
S.OBJECTS[n_weak_given] = WEAKREFERENCE (n_given)
$node_children(S, HOBJECT n_weak_given) = eps
$class_method_origin(S.CLASSES, pgenerator.FUNCTION) = (pmethoddesc)
pmethoddesc.STATIC
pfunction = pmethoddesc.FUNCTION
''')
SAVED = checks(r'''
pgenerator.PHASE = GENERATOR_RUNNING
pgenerator.FRAME = eps
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
~pgeneratorop.STARTPACK
~pgeneratorop.BORROWED
$task_nodes(GENERATOR_RESUME pgeneratorop) = [HOBJECT n_generator, HOBJECT n_given]
pcallcontext_generator.FUNCTION = pgenerator.FUNCTION
pcallcontext_generator.INSTANCE = eps
pcallcontext_generator.RECEIVER = eps
pcallcontext_generator.LEXICAL_CLASS = (porigin_parent)
pcallcontext_generator.CALLED_CLASS = (porigin_leaf)
$target_nodes(pcallcontext_generator.TARGET) = eps
$call_context_roots((pcallcontext_generator)) = eps
S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]
$generator_record_valid(S_view, pgenerator)
$call_current_valid(S_view)
$fiber_vm_valid(S, pfibervm, (n_fiber), eps)
$fiber_generator_static_target(pcallcontext_generator.TARGET, pgenerator.FUNCTION)
$fiber_generator_callee_valid(S_view, pgenerator, pcallcontext_generator)
$fiber_generator_cached_reference_valid(S_view, pgenerator, pcallcontext_generator)
$fiber_generator_body_id(S_view) = (n_generator)
$fiber_transfer_domain(S_view)
$generator_saved_fiber_ids(S) = [n_generator]
$generator_owners_valid(S)
''')
FRESH = checks(r'''
pgenerator.FIRST
pgenerator.VALUE = eps
pgenerator.REFCELL = eps
pgeneratorop.ADVANCE
$node_children(S, HOBJECT n_generator) = eps
$heap_owners($heap_graph(S), HOBJECT n_given) = 1
$fiber_generator_fresh_throw_valid(S_view, pgeneratorop, pgenerator, pcallcontext_generator)
~$fiber_generator_throw_valid(S_view, pgeneratorop, pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop[.ARGUMENTS = eps], pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop[.ARGUMENTS = [POBJECT n_fiber]], pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop[.NAME = "current"][.ARGUMENTS = eps], pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop[.ADVANCE = false], pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop, pgenerator[.FIRST = false], pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop, pgenerator[.VALUE = (PINT 7)], pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop, pgenerator[.REFCELL = (n_generator_cell)], pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop, pgenerator[.CLOSURE = (n_fiber)], pcallcontext_generator)
''')
STATIC = checks(r'''
pcallcontext_generator.TARGET = STATIC_METHOD_TARGET porigin_leaf pgenerator.FUNCTION
''')
SCOPED = checks(r'''
pcallcontext_generator.TARGET = SCOPED_TARGET porigin_leaf pgenerator.FUNCTION porigin_leaf eps poperand_selector
$operand_nodes(poperand_selector) = eps
pcallcontext_generator.CALLSITE = (porigin_creator)
$origin_node(S.SOURCES, porigin_creator) = (NExprStaticCall phpType19_class phpType20_method (SEQUENCE phpType7*) metadata_creator)
~$ppscoped_keyword(phpType19_class)
$generator_creation_target(S_view, pcallcontext_generator.TARGET, (porigin_creator))
~$generator_creation_target(S_view, SCOPED_TARGET porigin_leaf pgenerator.FUNCTION porigin_leaf (n_fiber) poperand_selector, (porigin_creator))
''')
AUTHENTICATION = checks(r'''
~$fiber_generator_callee_valid(S_view, pgenerator[.CLOSURE = (n_fiber)], pcallcontext_generator)
~$fiber_generator_callee_valid(S_view, pgenerator, pcallcontext_generator[.INSTANCE = (n_fiber)])
~$fiber_generator_callee_valid(S_view, pgenerator, pcallcontext_generator[.RECEIVER = (n_fiber)])
~$fiber_generator_static_target(METHOD_TARGET n_fiber pgenerator.FUNCTION, pgenerator.FUNCTION)
~$fiber_generator_static_target(pgenerator.FUNCTION, pgenerator.FUNCTION)
~$fiber_generator_static_target(CLOSURE_TARGET n_fiber, pgenerator.FUNCTION)
pcallcontext_badname = pcallcontext_generator[.NAME = $ptascii("forged72")]
S_badname = S_view[.CURRENT = (pcallcontext_badname)]
~$call_current_valid(S_badname)
~$fiber_vm_valid(S, pfibervm[.CURRENT = (pcallcontext_badname)], (n_fiber), eps)
$fiber_generator_body_id(S_badname) = eps
pcallcontext_badlexical = pcallcontext_generator[.LEXICAL_CLASS = (porigin_leaf)]
S_badlexical = S_view[.CURRENT = (pcallcontext_badlexical)]
~$call_current_valid(S_badlexical)
~$fiber_vm_valid(S, pfibervm[.CURRENT = (pcallcontext_badlexical)], (n_fiber), eps)
pcallcontext_badcalled = pcallcontext_generator[.CALLED_CLASS = (porigin_parent)]
S_badcalled = S_view[.CURRENT = (pcallcontext_badcalled)]
~$call_current_valid(S_badcalled)
~$fiber_vm_valid(S, pfibervm[.CURRENT = (pcallcontext_badcalled)], (n_fiber), eps)
pcallcontext_receiver = pcallcontext_generator[.RECEIVER = (n_fiber)]
~$fiber_vm_valid(S, pfibervm[.CURRENT = (pcallcontext_receiver)], (n_fiber), eps)
S_line = S_view[.FRAMES = pframe_generator[.TODO = (GENERATOR_RESUME pgeneratorop[.LINE = 0]) :: ptask_generator*] :: pframe_tail*]
$fiber_generator_body_id(S_line) = eps
S_duplicate = S_view[.FRAMES = pframe_generator :: pframe_generator :: pframe_tail*]
$fiber_generator_body_id(S_duplicate) = eps
''')
SCOPED_AUTH = checks(r'''
~$fiber_generator_static_target(SCOPED_TARGET porigin_leaf pgenerator.FUNCTION porigin_leaf (n_fiber) poperand_selector, pgenerator.FUNCTION)
pcallcontext_requested = pcallcontext_generator[.TARGET = SCOPED_TARGET porigin_parent pgenerator.FUNCTION porigin_leaf eps poperand_selector]
S_requested = S_view[.CURRENT = (pcallcontext_requested)]
~$call_current_valid(S_requested)
~$fiber_vm_valid(S, pfibervm[.CURRENT = (pcallcontext_requested)], (n_fiber), eps)
pcallcontext_called = pcallcontext_generator[.TARGET = SCOPED_TARGET porigin_leaf pgenerator.FUNCTION porigin_parent eps poperand_selector][.CALLED_CLASS = (porigin_parent)]
S_called = S_view[.CURRENT = (pcallcontext_called)]
~$call_current_valid(S_called)
~$fiber_vm_valid(S, pfibervm[.CURRENT = (pcallcontext_called)], (n_fiber), eps)
pcallcontext_selector = pcallcontext_generator[.TARGET = SCOPED_TARGET porigin_leaf pgenerator.FUNCTION porigin_leaf eps (KNOWN (PSTRING ($ptascii("Parent72Copy"))))]
S_selector = S_view[.CURRENT = (pcallcontext_selector)]
~$call_current_valid(S_selector)
~$fiber_vm_valid(S, pfibervm[.CURRENT = (pcallcontext_selector)], (n_fiber), eps)
pcallcontext_parent = pcallcontext_generator[.TARGET = SCOPED_TARGET porigin_parent pgenerator.FUNCTION porigin_parent eps (KNOWN (PSTRING ($ptascii("Parent72Copy"))))][.CALLED_CLASS = (porigin_parent)]
S_parent = S_view[.CURRENT = (pcallcontext_parent)]
$target_function(S_parent, pcallcontext_parent.TARGET) = (pfunction)
$fiber_generator_static_target(pcallcontext_parent.TARGET, pgenerator.FUNCTION)
~$call_current_valid(S_parent)
~$fiber_vm_valid(S, pfibervm[.CURRENT = (pcallcontext_parent)], (n_fiber), eps)
$fiber_generator_body_id(S_parent) = eps
''')
SELECTOR = checks(r'''
$lookup(S.ENV, $ptascii("weakSelector")) = (n_weak_selector_cell)
S.STORE[n_weak_selector_cell] = DEFINED (POBJECT n_weak_selector)
S.OBJECTS[n_weak_selector] = WEAKREFERENCE (n_selector)
$weakref_get(S, n_weak_selector) = PNULL
~((HOBJECT n_selector) <- S.ALLOCATIONS)
n_selector <- S.DESTRUCTION.CALLED
$heap_owners($heap_graph(S), HOBJECT n_selector) = 0
$heap_count(HOBJECT n_selector, $fiber_vm_nodes(pfibervm)) = 0
''')
FRESH_COPY = checks(r'''
~pfunction.SIGNATURE.BYREF
$lookup(S.ENV, $ptascii("input")) = (n_input)
S.STORE[n_input] = DEFINED (PINT 9)
$lookup(pfibervm.TABLE.ENV, $ptascii("item")) = (n_item)
S.STORE[n_item] = DEFINED (PINT 5)
n_item =/= n_input
~(n_item <- S.REFCELLS)
$heap_owners($heap_graph(S), HCELL n_item) = 1
''')
FRESH_REFERENCE = checks(r'''
pfunction.SIGNATURE.BYREF
$generator_reference_producer(S, pgenerator)
$lookup(S.ENV, $ptascii("old")) = (n_item)
$lookup(S.ENV, $ptascii("slot")) = (n_input)
S.STORE[n_item] = DEFINED (PINT 7)
S.STORE[n_input] = DEFINED (PINT 9)
n_item =/= n_input
n_item <- S.REFCELLS
$lookup(pfibervm.TABLE.ENV, $ptascii("item")) = (n_item)
pframe_generator.LOCALS = (psymboltable_callback)
$lookup(psymboltable_callback.ENV, $ptascii("old")) = (n_item)
$heap_owners($heap_graph(S), HCELL n_item) = 3
$heap_count(HCELL n_item, $fiber_vm_nodes(pfibervm)) = 2
''')
PENDING_VALUE = checks(r'''
~pfunction.SIGNATURE.BYREF
~pgenerator.FIRST
~pgeneratorop.ADVANCE
pgenerator.REFCELL = eps
$lookup(S.ENV, $ptascii("weakToken")) = (n_weak_token_cell)
S.STORE[n_weak_token_cell] = DEFINED (POBJECT n_weak_token)
S.OBJECTS[n_weak_token] = WEAKREFERENCE (n_token)
pgenerator.VALUE = (POBJECT n_token)
$weakref_get(S, n_weak_token) = POBJECT n_token
$lookup(pfibervm.TABLE.ENV, $ptascii("item")) = (n_item)
S.STORE[n_item] = DEFINED (POBJECT n_token)
~(n_item <- S.REFCELLS)
$node_children(S, HOBJECT n_generator) = [HOBJECT n_token]
$heap_owners($heap_graph(S), HOBJECT n_token) = 2
$heap_owners($heap_graph(S), HCELL n_item) = 1
$heap_count(HCELL n_item, $fiber_vm_nodes(pfibervm)) = 1
$heap_owners($heap_graph(S), HOBJECT n_given) = 2
$fiber_generator_throw_valid(S_view, pgeneratorop, pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_view, pgeneratorop, pgenerator, pcallcontext_generator)
''')
# The frozen source's PRIME expression is an authentic existing CURRENT site.
CURRENT_LINE = next(i for i,line in enumerate(ROWS['i72-primed-static-byval-token-finally']['source'].splitlines(),1) if line.startswith("echo 'PRIME|'"))
THROW_BOUNDARY = checks(r'''
porigin_current = PORIGIN 0 [(PCINDEX 12), (PCFIELD 0), (PCINDEX 1), (PCFIELD 0), (PCFIELD 0)]
$generator_source_method(S_view, porigin_current, $ptascii("current"))
''') + [f'pgeneratorop_current = pgeneratorop[.NAME = "current"][.ARGUMENTS = eps][.SITE = porigin_current][.LINE = {CURRENT_LINE}]'] + checks(r'''
S_current = S_view[.FRAMES = pframe_generator[.TODO = (GENERATOR_RESUME pgeneratorop_current) :: ptask_generator*][.ORIGIN = (porigin_current)] :: pframe_tail*]
$generator_resumption_valid(S_current, pgeneratorop_current)
$generator_resume_pairs(S_current, S_current.CURRENT, S_current.FRAMES)
$call_current_valid(S_current)
$fiber_generator_callee_valid(S_current, pgenerator, pcallcontext_generator)
$fiber_generator_cached_reference_valid(S_current, pgenerator, pcallcontext_generator)
$fiber_generator_body_id(S_current) = eps
S_next = S_view[.FRAMES = pframe_generator[.TODO = (GENERATOR_RESUME pgeneratorop[.NAME = "next"][.ARGUMENTS = eps]) :: ptask_generator*] :: pframe_tail*]
$fiber_generator_body_id(S_next) = eps
S_send = S_view[.FRAMES = pframe_generator[.TODO = (GENERATOR_RESUME pgeneratorop[.NAME = "send"][.ARGUMENTS = [PINT 3]]) :: ptask_generator*] :: pframe_tail*]
$fiber_generator_body_id(S_send) = eps
$effective_method(S, porigin_leaf, $ptascii("__destruct"), |S.CLASSES|) = (pmethoddesc_destruct)
~pmethoddesc_destruct.STATIC
pgenerator_destruct = pgenerator[.FUNCTION = pmethoddesc_destruct.FUNCTION.ORIGIN]
pcallcontext_destruct = pcallcontext_generator[.FUNCTION = pmethoddesc_destruct.FUNCTION.ORIGIN][.TARGET = STATIC_METHOD_TARGET porigin_leaf pmethoddesc_destruct.FUNCTION.ORIGIN][.NAME = pmethoddesc_destruct.FUNCTION.NAME]
S_destruct = $generator_set(S_view, n_generator, pgenerator_destruct)[.CURRENT = (pcallcontext_destruct)]
$fiber_generator_static_target(pcallcontext_destruct.TARGET, pgenerator_destruct.FUNCTION)
$target_function(S_destruct, pcallcontext_destruct.TARGET) = eps
~$fiber_generator_callee_valid(S_destruct, pgenerator_destruct, pcallcontext_destruct)
~$generator_record_valid(S_destruct, pgenerator_destruct)
$fiber_generator_body_id(S_destruct) = eps
''')
CLOSED_REFERENCE = checks(r'''
pfunction.SIGNATURE.BYREF
pgenerator.PHASE = GENERATOR_CLOSED
pgenerator.FRAME = eps
pgenerator.VALUE = eps
pgenerator.REFCELL = (n_item)
n_item <- S.REFCELLS
$lookup(S.ENV, $ptascii("weakToken")) = (n_weak_token_cell)
S.STORE[n_weak_token_cell] = DEFINED (POBJECT n_weak_token)
S.OBJECTS[n_weak_token] = WEAKREFERENCE (n_token)
S.STORE[n_item] = DEFINED (POBJECT n_token)
$weakref_get(S, n_weak_token) = POBJECT n_token
$node_children(S, HOBJECT n_generator) = [HCELL n_item]
$heap_owners($heap_graph(S), HCELL n_item) = 1
$heap_owners($heap_graph(S), HOBJECT n_token) = 1
$lookup(S.ENV, $ptascii("stop")) = (n_stop_cell)
S.STORE[n_stop_cell] = DEFINED (POBJECT n_stop)
$throwable_previous_id(S, n_stop) = (n_given)
$heap_owners($heap_graph(S), HOBJECT n_given) = 1
$weakref_get(S, n_weak_given) = POBJECT n_given
$generator_saved_fiber_ids(S) = eps
$generator_owners_valid(S)
''')
ENDING = checks(r'''
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
''')
TOKEN_END = checks(r'''
n_token <- S_done.DESTRUCTION.CALLED
~((HOBJECT n_token) <- S_done.ALLOCATIONS)
''')

def scope(parent,leaf):
    return [f'$class_named(S.CLASSNAMES, $ptlc($ptascii("{parent}"))) = (porigin_parent)',
            f'$class_named(S.CLASSNAMES, $ptlc($ptascii("{leaf}"))) = (porigin_leaf)',
            'pmethoddesc.OWNER = porigin_parent']

CACHE_SOURCE = ROWS['i72-primed-scoped-byref-local-abrupt']['source']
CACHE_LINE = next(i for i,line in enumerate(CACHE_SOURCE.splitlines(),1) if line.startswith("echo 'CACHE|'"))
CASES = {
    'i72-fresh-scoped-copy-scope-authentication':
        {'source': ROWS['i72-fresh-scoped-byval-inherited-catch']['source'],
         'stage': PARK_STAGE,
         'checks': [*COMMON, *scope('Parent72Copy','Leaf72Copy'), *SAVED, *FRESH, *SCOPED, *FRESH_COPY, *AUTHENTICATION, *SCOPED_AUTH, *ENDING]},
    'i72-primed-static-value-pending-finally':
        {'source': ROWS['i72-primed-static-byval-token-finally']['source'],
         'stage': PARK_STAGE,
         'checks': [*COMMON, *scope('Parent72Value','Leaf72Value'), *SAVED, *STATIC, *SELECTOR, *PENDING_VALUE, *AUTHENTICATION, *THROW_BOUNDARY, *ENDING, *TOKEN_END]},
    'i72-fresh-static-reference-parameter':
        {'source': ROWS['i72-fresh-static-byref-parameter-catch']['source'],
         'stage': PARK_STAGE,
         'checks': [*COMMON, *scope('Parent72Ref','Leaf72Ref'), *SAVED, *FRESH, *STATIC, *SELECTOR, *FRESH_REFERENCE, *AUTHENTICATION, *ENDING]},
    'i72-closed-scoped-sole-reference-cache':
        {'source': CACHE_SOURCE,
         'stage': 'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
                  '-- if pconfigcall.KIND = INTRINSIC_WEAKREF_GET '
                  f'-- if pconfigcall.LINE = {CACHE_LINE}',
         'checks': [*COMMON, *scope('Parent72Abrupt','Leaf72Abrupt'), *CLOSED_REFERENCE, *ENDING, *TOKEN_END]},
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
