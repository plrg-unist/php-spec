#!/usr/bin/env python3
"""Check raw selected-method Generator entry, factory history and real owners."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_raw_method_factory_cases.json')
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
    '-- if S.ACTIVEFIBER = eps '
    '-- if S.OBJECTS[n_fiber] = FIBER pfiber '
    '-- if pfiber.STATUS = FIBER_SUSPENDED')

ARRAY_DIRECT = checks(r'''
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
S.FIBERCALLERS = eps
S.GENERATORINPUTS = eps
$lookup(S.ENV, $ptascii("g")) = (n_generator_cell)
S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)
S.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_RUNNING
pgenerator.FRAME = eps
pgenerator.CLOSURE = eps
pgenerator.CREATION = eps
pgenerator.VALUE = eps
pgenerator.REFCELL = eps
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base87A"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Child87A"))) = (porigin_child)
pfiber.VM = (pfibervm)
pfibervm.CURRENT = (pcallcontext_generator)
pfibervm.FRAMES = pframe_current :: pframe_tail*
pframe_current.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_resume*
pgeneratorop.OBJECT = n_generator
pgeneratorop.NAME = "current"
pcallcontext_generator.TARGET = ARRAY_METHOD_TARGET (METHOD_TARGET n_maker pgenerator.FUNCTION) parrayselection
pcallcontext_generator.CALLSITE = (parrayselection.SITE)
pcallcontext_generator.INSTANCE = eps
pcallcontext_generator.FUNCTION = pgenerator.FUNCTION
pcallcontext_generator.LEXICAL_CLASS = (porigin_base)
pcallcontext_generator.CALLED_CLASS = (porigin_child)
pcallcontext_generator.RECEIVER = (n_maker)
pcallcontext_generator.WRAPPER = eps
parrayselection.REQUESTED = porigin_child
parrayselection.NAME = $ptascii("stream")
S.OBJECTS[n_maker] = INSTANCE porigin_child
(HOBJECT n_maker) <- S.ALLOCATIONS
$lookup(S.ENV, $ptascii("maker")) = eps
$lookup(S.ENV, $ptascii("route")) = eps
n_selection = 0
S.ARRAYS[n_selection].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_maker)), ENTRY (KINT 1) (DIRECT pvalue_method)]
$string_bytes(pvalue_method) = ($ptascii("stream"))
~((HARRAY n_selection) <- S.ALLOCATIONS)
$call_context_roots((pcallcontext_generator)) = [HOBJECT n_maker]
$node_children(S, HOBJECT n_generator) = eps
H = $heap_graph(S)
$heap_owners(H, HOBJECT n_maker) = 1
$heap_owners(H, HARRAY n_selection) = 0
$heap_count(HOBJECT n_maker, $fiber_vm_nodes(pfibervm)) = 1
S_live = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]
$class_method_origin(S.CLASSES, pgenerator.FUNCTION) = (pmethoddesc)
$generator_raw_method_selected(S_live, pcallcontext_generator.TARGET, parrayselection.SITE) = (pmethoddesc)
$generator_creation_supported(S_live, pcallcontext_generator)
~$generator_creation_required(S_live, pcallcontext_generator)
$fiber_generator_raw_method_valid(S_live, pgenerator, pcallcontext_generator)
$fiber_generator_callee_valid(S_live, pgenerator, pcallcontext_generator)
$fiber_generator_body_id(S_live) = (n_generator)
$fiber_generator_transfer(S_live)
$call_current_valid(S_live)
S_dead = S_live[.ALLOCATIONS = $destruction_node_delete(S_live.ALLOCATIONS, HOBJECT n_maker)]
$generator_raw_method_selected(S_dead, pcallcontext_generator.TARGET, parrayselection.SITE) = (pmethoddesc)
~$generator_creation_supported(S_dead, pcallcontext_generator)
~$fiber_generator_raw_method_valid(S_dead, pgenerator, pcallcontext_generator)
parrayselection_bad_name = parrayselection[.NAME = $ptascii("missing")]
$generator_raw_method_selected(S_live, ARRAY_METHOD_TARGET (METHOD_TARGET n_maker pgenerator.FUNCTION) parrayselection_bad_name, parrayselection.SITE) = eps
parrayselection_bad_line = parrayselection[.LINE = 0]
$generator_raw_method_selected(S_live, ARRAY_METHOD_TARGET (METHOD_TARGET n_maker pgenerator.FUNCTION) parrayselection_bad_line, parrayselection.SITE) = eps
n_unbounded = |S.OBJECTS|
$generator_raw_method_selected(S_live, ARRAY_METHOD_TARGET (METHOD_TARGET n_unbounded pgenerator.FUNCTION) parrayselection, parrayselection.SITE) = eps
$generator_raw_method_selected(S_live, ARRAY_METHOD_TARGET (CLOSURE_TARGET n_unbounded) parrayselection, parrayselection.SITE) = eps
$generator_raw_method_selected(S_live, pcallcontext_generator.TARGET, pgenerator.FUNCTION) = eps
pcallcontext_bad_called = pcallcontext_generator[.CALLED_CLASS = (porigin_base)]
~$fiber_generator_raw_method_valid(S_live[.CURRENT = (pcallcontext_bad_called)], pgenerator, pcallcontext_bad_called)
pcallcontext_bad_receiver = pcallcontext_generator[.RECEIVER = eps]
~$fiber_generator_raw_method_valid(S_live[.CURRENT = (pcallcontext_bad_receiver)], pgenerator, pcallcontext_bad_receiver)
~$fiber_generator_raw_method_valid(S_live[.FRAMES = eps], pgenerator, pcallcontext_generator)
~$fiber_generator_raw_method_valid(S_live, pgenerator[.PHASE = GENERATOR_CLOSED], pcallcontext_generator)
$call_descriptors_valid(S)
$heap_valid(H)
S_budget = $drive(S, 0)
S_budget.COMPLETION = BUDGET
S_budget.OBJECTS = S.OBJECTS
S_done = $drive_steps(S, 1600)
$drive_steps(S_budget[.COMPLETION = NORMAL], 1600) = S_done
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.FRAMES = eps
S_done.CURRENT = eps
~((HOBJECT n_maker) <- S_done.ALLOCATIONS)
n_maker <- S_done.DESTRUCTION.CALLED
$heap_valid($heap_graph(S_done))
''')

CLOSE_STAGE = (
    'S.TODO = (GENERATOR_CLOSE_ENTER pgenclose) :: ptask_tail* '
    '-- if S.OBJECTS[pgenclose.OBJECT] = GENERATOR pgenerator '
    '-- if pgenerator.CREATION = (pgeneratorcreation)')

CLOSE = checks(r'''
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
pgenclose.FRAME = (pframe_generator)
pgenclose.CONTEXT = pcallcontext_generator
S_view = $generator_close_frame_scope(S, pframe_generator)
pgenerator.CLOSURE = eps
pgeneratorcreation.CLOSURE = eps
pgeneratorcreation.ANCESTORS = eps
pgeneratorcreation.CREATOR.LEXICAL_CLASS = (porigin_base)
pgeneratorcreation.CREATOR.CALLED_CLASS = (porigin_child)
pgeneratorcreation.CREATOR.CALLSITE = (porigin_creator_site)
$class_method_origin(S.CLASSES, pgeneratorcreation.CREATOR.FUNCTION) = (pmethoddesc_factory)
pmethoddesc_factory.OWNER = porigin_base
~$function_generator(S, pmethoddesc_factory.FUNCTION)
$generator_raw_method_selected(S, pgeneratorcreation.CREATOR_TARGET, porigin_creator_site) = (pmethoddesc_factory)
pcallcontext_generator.TARGET = pgeneratorcreation.CALLEE
pcallcontext_generator.CALLSITE = (pgeneratorcreation.SITE)
pcallcontext_generator.FUNCTION = pgenerator.FUNCTION
$generator_creator_valid(S, pgeneratorcreation)
$generator_creation_scope_valid(S, pgeneratorcreation)
$generator_creation_record_valid(S, pgenerator)
$generator_close_enter_valid(S, pgenclose)
$generator_creation_owner(S_view) = (pgenclose.OBJECT)
$generator_creation_selected(S_view, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
pgeneratorcreation_bad_called = pgeneratorcreation[.CREATOR = pgeneratorcreation.CREATOR[.CALLED_CLASS = (porigin_base)]]
~$generator_creator_valid(S, pgeneratorcreation_bad_called)
pgeneratorcreation_bad_lexical = pgeneratorcreation[.CREATOR = pgeneratorcreation.CREATOR[.LEXICAL_CLASS = (porigin_child)]]
~$generator_creator_valid(S, pgeneratorcreation_bad_lexical)
$generator_raw_method_selected(S, pgeneratorcreation.CREATOR_TARGET, pgeneratorcreation.SITE) = eps
pgenerator_missing = pgenerator[.CREATION = eps]
S_missing = $generator_set(S_view, pgenclose.OBJECT, pgenerator_missing)
$generator_creation_owner(S_missing) = (pgenclose.OBJECT)
~$generator_creation_selected(S_missing, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
''')

STRING_FACTORY = CLOSE + checks(r'''
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base87B"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Child87B"))) = (porigin_child)
pgeneratorcreation.CREATOR_TARGET = STRING_METHOD_TARGET (STATIC_METHOD_TARGET porigin_child pmethoddesc_factory.FUNCTION.ORIGIN) pstringselection
pstringselection.SITE = porigin_creator_site
pstringselection.REQUESTED = porigin_child
pstringselection.ORIGINAL = $ptascii("Child87B::make")
pmethoddesc_factory.STATIC
pgeneratorcreation.CALLEE = SCOPED_TARGET porigin_base pgenerator.FUNCTION porigin_child eps poperand_body
pcallcontext_generator.RECEIVER = eps
$lookup(S.ENV, $ptascii("route")) = eps
$target_nodes(pgeneratorcreation.CREATOR_TARGET) = eps
$call_context_roots((pcallcontext_generator)) = eps
pstringselection_bad = pstringselection[.ORIGINAL = $ptascii("Other87B::bad")]
pgeneratorcreation_bad_string = pgeneratorcreation[.CREATOR_TARGET = STRING_METHOD_TARGET (STATIC_METHOD_TARGET porigin_child pmethoddesc_factory.FUNCTION.ORIGIN) pstringselection_bad]
~$generator_creator_valid(S, pgeneratorcreation_bad_string)
pstringselection_bad_site = pstringselection[.SITE = pgeneratorcreation.SITE]
$generator_raw_method_selected(S, STRING_METHOD_TARGET (STATIC_METHOD_TARGET porigin_child pmethoddesc_factory.FUNCTION.ORIGIN) pstringselection_bad_site, porigin_creator_site) = eps
''')

ARRAY_FACTORY = CLOSE + checks(r'''
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base87C"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Child87C"))) = (porigin_child)
pgeneratorcreation.CREATOR_TARGET = ARRAY_METHOD_TARGET (METHOD_TARGET n_maker pmethoddesc_factory.FUNCTION.ORIGIN) parrayselection
parrayselection.SITE = porigin_creator_site
parrayselection.REQUESTED = porigin_child
parrayselection.NAME = $ptascii("make")
~pmethoddesc_factory.STATIC
pgeneratorcreation.CALLEE = SCOPED_TARGET porigin_base pgenerator.FUNCTION porigin_child (n_maker) poperand_body
pcallcontext_generator.RECEIVER = (n_maker)
S.OBJECTS[n_maker] = INSTANCE porigin_child
(HOBJECT n_maker) <- S.ALLOCATIONS
$lookup(S.ENV, $ptascii("maker")) = eps
$lookup(S.ENV, $ptascii("route")) = eps
n_selection = 0
S.ARRAYS[n_selection].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_maker)), ENTRY (KINT 1) (DIRECT pvalue_method)]
$string_bytes(pvalue_method) = ($ptascii("make"))
~((HARRAY n_selection) <- S.ALLOCATIONS)
$heap_owners($heap_graph(S), HARRAY n_selection) = 0
$heap_owners($heap_graph(S), HOBJECT n_maker) = 1
$call_context_roots((pcallcontext_generator)) = [HOBJECT n_maker]
$heap_count(HOBJECT n_maker, $task_nodes(GENERATOR_CLOSE_ENTER pgenclose)) = 1
parrayselection_bad = parrayselection[.NAME = $ptascii("body")]
pgeneratorcreation_bad_name = pgeneratorcreation[.CREATOR_TARGET = ARRAY_METHOD_TARGET (METHOD_TARGET n_maker pmethoddesc_factory.FUNCTION.ORIGIN) parrayselection_bad]
~$generator_creator_valid(S, pgeneratorcreation_bad_name)
''')

RETIRED_FACTORY = CLOSE + checks(r'''
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base87E"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Child87E"))) = (porigin_child)
pgeneratorcreation.CREATOR_TARGET = ARRAY_METHOD_TARGET (SCOPE_METHOD_TARGET (METHOD_TARGET n_maker pmethoddesc_factory.FUNCTION.ORIGIN) pcallableaccess) parrayselection
parrayselection.SITE = porigin_creator_site
parrayselection.REQUESTED = porigin_child
parrayselection.NAME = $ptascii("make")
pcallableaccess.SITE = (porigin_creator_site)
pcallableaccess.SCOPE = (porigin_base)
pcallableaccess.OBJECT
pcallableaccess.CREATION = eps
$generator_raw_method_scope_source(S, pcallableaccess, porigin_creator_site)
~$generator_raw_method_scope_source(S, pcallableaccess[.CREATION = (pgeneratorcreation.CREATOR)], porigin_creator_site)
pmethoddesc_factory.VISIBILITY = PROPERTY_PRIVATE
~pmethoddesc_factory.STATIC
pgeneratorcreation.CALLEE = SCOPED_TARGET porigin_base pgenerator.FUNCTION porigin_child eps poperand_body
pcallcontext_generator.RECEIVER = eps
S.OBJECTS[n_maker] = INSTANCE porigin_child
~((HOBJECT n_maker) <- S.ALLOCATIONS)
n_maker <- S.DESTRUCTION.CALLED
$lookup(S.ENV, $ptascii("maker")) = eps
$generator_raw_method_base(pgeneratorcreation.CREATOR_TARGET) = (METHOD_TARGET n_maker pmethoddesc_factory.FUNCTION.ORIGIN)
$target_function(S, pgeneratorcreation.CREATOR_TARGET) = eps
~$call_selected_valid(S, pgeneratorcreation.CREATOR_TARGET, (porigin_creator_site))
$method_class_selected(S, porigin_child, $ptascii("make"), (porigin_base)) = (pmethoddesc_factory)
$effective_method(S, porigin_child, $ptascii("make"), |S.CLASSES|) = (pmethoddesc_other)
pmethoddesc_other.FUNCTION.ORIGIN =/= pmethoddesc_factory.FUNCTION.ORIGIN
n_selection = 0
S.ARRAYS[n_selection].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_maker)), ENTRY (KINT 1) (DIRECT pvalue_method)]
$string_bytes(pvalue_method) = ($ptascii("make"))
~((HARRAY n_selection) <- S.ALLOCATIONS)
$heap_owners($heap_graph(S), HARRAY n_selection) = 0
$heap_owners($heap_graph(S), HOBJECT n_maker) = 0
$call_context_roots((pcallcontext_generator)) = eps
pcallableaccess_bad_scope = pcallableaccess[.SCOPE = (porigin_child)]
pgeneratorcreation_bad_scope = pgeneratorcreation[.CREATOR_TARGET = ARRAY_METHOD_TARGET (SCOPE_METHOD_TARGET (METHOD_TARGET n_maker pmethoddesc_factory.FUNCTION.ORIGIN) pcallableaccess_bad_scope) parrayselection]
~$generator_creator_valid(S, pgeneratorcreation_bad_scope)
pcallableaccess_bad_site = pcallableaccess[.SITE = (pgeneratorcreation.SITE)]
pgeneratorcreation_bad_site = pgeneratorcreation[.CREATOR_TARGET = ARRAY_METHOD_TARGET (SCOPE_METHOD_TARGET (METHOD_TARGET n_maker pmethoddesc_factory.FUNCTION.ORIGIN) pcallableaccess_bad_site) parrayselection]
~$generator_creator_valid(S, pgeneratorcreation_bad_site)
n_unbounded = |S.OBJECTS|
pgeneratorcreation_unbounded = pgeneratorcreation[.CREATOR_TARGET = ARRAY_METHOD_TARGET (SCOPE_METHOD_TARGET (METHOD_TARGET n_unbounded pmethoddesc_factory.FUNCTION.ORIGIN) pcallableaccess) parrayselection]
~$generator_creator_valid(S, pgeneratorcreation_unbounded)
''')

FRESH_STAGE = (
    'S.TODO = (GENERATOR_ARGS pgeneratorop eps eps) :: ptask_tail* '
    '-- if pgeneratorop.NAME = "current" '
    '-- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator '
    '-- if pgenerator.PHASE = GENERATOR_FRESH')

STRING_DIRECT = checks(r'''
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
pgenerator.CLOSURE = eps
pgenerator.CREATION = eps
pgenerator.VALUE = eps
pgenerator.REFCELL = eps
pgenerator.FRAME = (pframe_generator)
pframe_generator.CONTEXT = (pcallcontext_generator)
pcallcontext_generator.TARGET = STRING_METHOD_TARGET (STATIC_METHOD_TARGET porigin_child pgenerator.FUNCTION) pstringselection
pcallcontext_generator.CALLSITE = (pstringselection.SITE)
pcallcontext_generator.INSTANCE = eps
pcallcontext_generator.RECEIVER = eps
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base87D"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Child87D"))) = (porigin_child)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Other87D"))) = (porigin_other)
pcallcontext_generator.LEXICAL_CLASS = (porigin_base)
pcallcontext_generator.CALLED_CLASS = (porigin_child)
pstringselection.REQUESTED = porigin_child
pstringselection.ORIGINAL = $ptascii("Child87D::stream")
$lookup(S.ENV, $ptascii("route")) = (n_route)
S.STORE[n_route] = DEFINED pvalue_route
$string_bytes(pvalue_route) = ($ptascii("Other87D::bad"))
$class_method_origin(S.CLASSES, pgenerator.FUNCTION) = (pmethoddesc)
S_view = $generator_frame_scope(S, pframe_generator)
$generator_raw_method_selected(S_view, pcallcontext_generator.TARGET, pstringselection.SITE) = (pmethoddesc)
$generator_creation_supported(S_view, pcallcontext_generator)
~$generator_creation_required(S_view, pcallcontext_generator)
$call_current_valid(S_view)
$call_context_roots((pcallcontext_generator)) = eps
$effective_method(S, porigin_other, $ptascii("bad"), |S.CLASSES|) = (pmethoddesc_other)
$function_generator(S, pmethoddesc_other.FUNCTION)
pstringselection_other = pstringselection[.REQUESTED = porigin_other][.ORIGINAL = $ptascii("Other87D::bad")]
pcalltarget_other = STRING_METHOD_TARGET (STATIC_METHOD_TARGET porigin_other pmethoddesc_other.FUNCTION.ORIGIN) pstringselection_other
$generator_raw_method_selected(S_view, pcalltarget_other, pstringselection.SITE) = (pmethoddesc_other)
pmethoddesc_other.FUNCTION.ORIGIN =/= pgenerator.FUNCTION
pcallcontext_other = pcallcontext_generator[.TARGET = pcalltarget_other]
~$call_current_valid(S_view[.CURRENT = (pcallcontext_other)])
pstringselection_bad = pstringselection[.ORIGINAL = $ptascii("Other87D::bad")]
$generator_raw_method_selected(S_view, STRING_METHOD_TARGET (STATIC_METHOD_TARGET porigin_child pgenerator.FUNCTION) pstringselection_bad, pstringselection.SITE) = eps
$generator_raw_method_selected(S_view, pcallcontext_generator.TARGET, pgenerator.FUNCTION) = eps
$generator_raw_method_base(CLOSURE_TARGET pgeneratorop.OBJECT) = eps
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
S_done = $drive_steps(S, 1600)
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.CURRENT = eps
S_done.FRAMES = eps
$heap_valid($heap_graph(S_done))
''')

CASES = {
    'i87-raw-array-direct-parked': {
        'source': ROWS['i87-raw-array-direct-fiber']['source'],
        'stage': PARK_STAGE, 'checks': ARRAY_DIRECT},
    'i87-raw-string-static-factory-close': {
        'source': ROWS['i87-raw-string-static-factory']['source'],
        'stage': CLOSE_STAGE, 'checks': STRING_FACTORY},
    'i87-raw-array-protected-factory-close': {
        'source': ROWS['i87-raw-array-protected-factory']['source'],
        'stage': CLOSE_STAGE, 'checks': ARRAY_FACTORY},
    'i87-raw-string-direct-fresh': {
        'source': ROWS['i87-raw-string-direct-retarget']['source'],
        'stage': FRESH_STAGE, 'checks': STRING_DIRECT},
    'i87-raw-array-private-retired-factory-close': {
        'source': ROWS['i87-raw-array-retired-static-factory']['source'],
        'stage': CLOSE_STAGE, 'checks': RETIRED_FACTORY},
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
