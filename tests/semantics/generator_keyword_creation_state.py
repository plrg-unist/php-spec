#!/usr/bin/env python3
"""Check retained keyword Generator scope at source-reached Fiber states."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_keyword_creation_cases.json')
INPUT_BYTES = {path: path.read_bytes() for path in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


PARK_STAGE = (
    'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
    '-- if pconfigcall.KIND = INTRINSIC_WEAKREF_GET '
    '-- if $lookup(S.ENV, $ptascii("f")) = (n_fiber_cell) '
    '-- if S.STORE[n_fiber_cell] = DEFINED (POBJECT n_fiber) '
    '-- if S.OBJECTS[n_fiber] = FIBER pfiber '
    '-- if pfiber.STATUS = FIBER_SUSPENDED '
    '-- if $lookup(S.ENV, $ptascii("other")) = (n_other_cell) '
    '-- if S.STORE[n_other_cell] = DEFINED (POBJECT n_other)')

RESUME_STAGE = (
    'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
    '-- if pconfigcall.KIND = INTRINSIC_FIBER_RESUME '
    '-- if pconfigcall.OWNER = (n_fiber) '
    '-- if S.OBJECTS[n_fiber] = FIBER pfiber '
    '-- if pfiber.STATUS = FIBER_SUSPENDED '
    '-- if pfiber.VM = (pfibervm) '
    '-- if pfibervm.TODO = (FIBER_CONTINUE pfiberapi) :: ptask_saved* '
    '-- if pfiberapi.SENT = (pvalue_sent) '
    '-- if $string_bytes(pvalue_sent) = ($ptascii("after75"))')

PRIVATE_SELF = checks(r'''
S.COMPLETION = NORMAL
S.ACTIVEFIBER = eps
S.CURRENT = eps
S.FRAMES = eps
$lookup(S.ENV, $ptascii("g")) = (n_generator_cell)
S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)
$lookup(S.ENV, $ptascii("other")) = (n_other_cell)
S.STORE[n_other_cell] = DEFINED (POBJECT n_other)
n_other =/= n_generator
S.OBJECTS[n_generator] = GENERATOR pgenerator
S.OBJECTS[n_other] = GENERATOR pgenerator_other
pgenerator.PHASE = GENERATOR_RUNNING
pgenerator_other.PHASE = GENERATOR_FRESH
pgenerator.FIRST
pgenerator.VALUE = eps
pgenerator.REFCELL = eps
pgenerator.CREATION = (pgeneratorcreation)
pgenerator_other.CREATION = (pgeneratorcreation_other)
pgeneratorcreation.CREATOR.CALLSITE = (porigin_creator_site)
pgenerator_other.FRAME = (pframe_other)
pframe_other.CONTEXT = (pcallcontext_other)
pgeneratorcreation_other.SITE = pgeneratorcreation.SITE
pgeneratorcreation_other.CREATOR.CALLSITE = (porigin_other_callsite)
porigin_other_callsite =/= porigin_creator_site
pcallcontext_other.TARGET = pgeneratorcreation_other.CALLEE
$class_named(S.CLASSNAMES, $ptlc($ptascii("Mid75Throw"))) = (porigin_mid)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Leaf75Throw"))) = (porigin_leaf)
$class_method_origin(S.CLASSES, pgenerator.FUNCTION) = (pmethoddesc)
pmethoddesc.STATIC
pmethoddesc.VISIBILITY = PROPERTY_PRIVATE
pmethoddesc.OWNER = porigin_mid
$target_function(S, pgeneratorcreation.CALLEE) = (pmethoddesc.FUNCTION)
$method_accessible(S, pmethoddesc, (porigin_mid))
pgeneratorcreation.CREATOR.LEXICAL_CLASS = (porigin_mid)
pgeneratorcreation.CREATOR.CALLED_CLASS = (porigin_leaf)
pgeneratorcreation.CALLEE = SCOPED_TARGET porigin_mid pgenerator.FUNCTION porigin_leaf eps poperand_selector
pgeneratorcreation.CREATOR_TARGET = SCOPED_TARGET porigin_leaf pgeneratorcreation.CREATOR.FUNCTION porigin_leaf eps poperand_creator
$generator_creator_valid(S, pgeneratorcreation)
$generator_creation_scope_valid(S, pgeneratorcreation)
$generator_creation_record_valid(S, pgenerator)
$generator_creation_record_valid(S, pgenerator_other)
pfiber.VM = (pfibervm)
~pfibervm.GLOBAL
pfibervm.CURRENT = (pcallcontext_generator)
pfibervm.FRAMES = pframe_generator :: pframe_tail*
pframe_generator.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_generator*
pgeneratorop.OBJECT = n_generator
pgeneratorop.NAME = "throw"
pgeneratorop.ARGUMENTS = [POBJECT n_given]
pgeneratorop.ADVANCE
$task_nodes(GENERATOR_RESUME pgeneratorop) = [HOBJECT n_generator, HOBJECT n_given]
$lookup(S.ENV, $ptascii("old")) = (n_item)
$lookup(S.ENV, $ptascii("slot")) = (n_input)
n_item =/= n_input
n_item <- S.REFCELLS
S.STORE[n_item] = DEFINED (PINT 7)
S.STORE[n_input] = DEFINED (PINT 9)
$lookup(pfibervm.TABLE.ENV, $ptascii("item")) = (n_item)
pframe_other.LOCALS = (psymboltable_other)
$lookup(psymboltable_other.ENV, $ptascii("item")) = (n_item)
$heap_owners($heap_graph(S), HCELL n_item) = 4
$heap_count(HCELL n_item, $fiber_vm_nodes(pfibervm)) = 2
$lookup(S.ENV, $ptascii("weakGiven")) = (n_weak_given_cell)
S.STORE[n_weak_given_cell] = DEFINED (POBJECT n_weak_given)
S.OBJECTS[n_weak_given] = WEAKREFERENCE (n_given)
$weakref_get(S, n_weak_given) = POBJECT n_given
$heap_owners($heap_graph(S), HOBJECT n_given) = 1
pframe_generator.CONTEXT = (pcallcontext_callback)
pcallcontext_generator.TARGET = pgeneratorcreation.CALLEE
pcallcontext_generator.CALLSITE = (pgeneratorcreation.SITE)
pcallcontext_generator.FUNCTION = pgenerator.FUNCTION
pcallcontext_generator.LEXICAL_CLASS = (porigin_mid)
pcallcontext_generator.CALLED_CLASS = (porigin_leaf)
pcallcontext_generator.INSTANCE = eps
pcallcontext_generator.RECEIVER = eps
pcallcontext_other = pcallcontext_generator
$call_context_roots((pcallcontext_generator)) = eps
S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]
$generator_creation_owner(S_view) = (n_generator)
$generator_creation_resume_owner(S_view) = (n_generator)
$generator_creation_context_valid(S_view, pgenerator, pcallcontext_generator)
$generator_creation_object_selected(S_view, n_generator, pcallcontext_generator)
$generator_creation_object_selected(S_view, n_other, pcallcontext_generator)
$generator_creation_selected(S_view, pcallcontext_generator.TARGET, pgeneratorcreation.SITE)
$generator_record_valid(S_view, pgenerator)
$call_current_valid(S_view)
$fiber_vm_valid(S, pfibervm, (n_fiber), eps)
$fiber_generator_body_id(S_view) = (n_generator)
pgeneratorcreation_bad_called = pgeneratorcreation[.CREATOR = pgeneratorcreation.CREATOR[.CALLED_CLASS = (porigin_mid)]]
~$generator_creator_valid(S, pgeneratorcreation_bad_called)
pgeneratorcreation_bad_requested = pgeneratorcreation[.CALLEE = SCOPED_TARGET porigin_leaf pgenerator.FUNCTION porigin_leaf eps (KNOWN (PSTRING ($ptascii("Leaf75Throw"))))]
$target_function(S, pgeneratorcreation_bad_requested.CALLEE) = (pmethoddesc.FUNCTION)
~$generator_creation_scope_valid(S, pgeneratorcreation_bad_requested)
pgeneratorcreation_bad_target = pgeneratorcreation[.CREATOR_TARGET = STATIC_METHOD_TARGET porigin_leaf pgeneratorcreation.CREATOR.FUNCTION]
$function_at($all_functions(S), pgeneratorcreation.CREATOR.FUNCTION) = (pfunction_creator)
$target_function(S, pgeneratorcreation_bad_target.CREATOR_TARGET) = (pfunction_creator)
~$generator_creator_valid(S, pgeneratorcreation_bad_target)
pgeneratorcreation_bad_site = pgeneratorcreation[.SITE = porigin_creator_site]
~$generator_creation_scope_valid(S, pgeneratorcreation_bad_site)
S_missing = S_view[.OBJECTS = $object_set(S_view.OBJECTS, n_generator, GENERATOR pgenerator[.CREATION = eps])]
$generator_creation_owner(S_missing) = (n_generator)
~$generator_creation_object_selected(S_missing, n_generator, pcallcontext_generator)
$generator_creation_object_selected(S_missing, n_other, pcallcontext_generator)
~$generator_creation_selected(S_missing, pcallcontext_generator.TARGET, pgeneratorcreation.SITE)
~$call_current_valid(S_missing)
$fiber_generator_body_id(S_missing) = eps
S_corrupt = S_view[.OBJECTS = $object_set(S_view.OBJECTS, n_generator, GENERATOR pgenerator[.CREATION = (pgeneratorcreation_bad_called)])]
~$generator_creation_selected(S_corrupt, pcallcontext_generator.TARGET, pgeneratorcreation.SITE)
~$call_current_valid(S_corrupt)
$fiber_generator_body_id(S_corrupt) = eps
S_function = S_view[.OBJECTS = $object_set(S_view.OBJECTS, n_generator, GENERATOR pgenerator[.FUNCTION = pgeneratorcreation.CREATOR.FUNCTION])]
$generator_creation_resume_owner(S_function) = (n_generator)
$generator_creation_owner(S_function) = (n_generator)
$generator_creation_object_selected(S_function, n_other, pcallcontext_generator)
~$generator_creation_selected(S_function, pcallcontext_generator.TARGET, pgeneratorcreation.SITE)
~$call_current_valid(S_function)
S_unallocated = S_view[.ALLOCATIONS = $destruction_node_delete(S_view.ALLOCATIONS, HOBJECT n_generator)]
$generator_creation_owner(S_unallocated) = (n_generator)
~$generator_creation_selected(S_unallocated, pcallcontext_generator.TARGET, pgeneratorcreation.SITE)
pcallcontext_name = pcallcontext_generator[.NAME = $ptascii("forged75")]
S_name = S_view[.CURRENT = (pcallcontext_name)]
~$call_current_valid(S_name)
~$fiber_vm_valid(S, pfibervm[.CURRENT = (pcallcontext_name)], (n_fiber), eps)
pcallcontext_receiver = pcallcontext_generator[.RECEIVER = (n_fiber)]
S_receiver = S_view[.CURRENT = (pcallcontext_receiver)]
~$call_current_valid(S_receiver)
~$fiber_vm_valid(S, pfibervm[.CURRENT = (pcallcontext_receiver)], (n_fiber), eps)
pcallcontext_site = pcallcontext_generator[.CALLSITE = (porigin_creator_site)]
S_site = S_view[.CURRENT = (pcallcontext_site)]
~$call_current_valid(S_site)
~$fiber_vm_valid(S, pfibervm[.CURRENT = (pcallcontext_site)], (n_fiber), eps)
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
''')

LATE_STATIC = checks(r'''
S.COMPLETION = NORMAL
S.ACTIVEFIBER = eps
S.CURRENT = eps
S.FRAMES = eps
$lookup(S.ENV, $ptascii("g")) = (n_generator_cell)
S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)
S.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_RUNNING
~pgenerator.FIRST
pgenerator.VALUE = (POBJECT n_token)
pgenerator.REFCELL = eps
pgenerator.CREATION = (pgeneratorcreation)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Mid75Next"))) = (porigin_mid)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Leaf75Next"))) = (porigin_leaf)
$class_method_origin(S.CLASSES, pgeneratorcreation.CREATOR.FUNCTION) = (pmethoddesc_make)
pmethoddesc_make.STATIC
pmethoddesc_make.OWNER = porigin_mid
$class_method_origin(S.CLASSES, pgenerator.FUNCTION) = (pmethoddesc_body)
pmethoddesc_body.STATIC
pmethoddesc_body.OWNER = porigin_leaf
pgeneratorcreation.CREATOR.LEXICAL_CLASS = (porigin_mid)
pgeneratorcreation.CREATOR.CALLED_CLASS = (porigin_leaf)
pgeneratorcreation.CREATOR_TARGET = SCOPED_TARGET porigin_leaf pgeneratorcreation.CREATOR.FUNCTION porigin_leaf eps poperand_creator
pgeneratorcreation.CALLEE = SCOPED_TARGET porigin_leaf pgenerator.FUNCTION porigin_leaf eps poperand_selector
$target_function(S, pgeneratorcreation.CALLEE) = (pmethoddesc_body.FUNCTION)
$generator_creator_valid(S, pgeneratorcreation)
$generator_creation_scope_valid(S, pgeneratorcreation)
$generator_creation_record_valid(S, pgenerator)
pfiber.VM = (pfibervm)
~pfibervm.GLOBAL
pfibervm.CURRENT = (pcallcontext_generator)
pfibervm.FRAMES = pframe_generator :: pframe_tail*
pframe_generator.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_generator*
pgeneratorop.OBJECT = n_generator
pgeneratorop.NAME = "next"
~pgeneratorop.ADVANCE
pcallcontext_generator.TARGET = pgeneratorcreation.CALLEE
pcallcontext_generator.CALLSITE = (pgeneratorcreation.SITE)
pcallcontext_generator.FUNCTION = pgenerator.FUNCTION
pcallcontext_generator.LEXICAL_CLASS = (porigin_leaf)
pcallcontext_generator.CALLED_CLASS = (porigin_leaf)
pcallcontext_generator.RECEIVER = eps
pcallcontext_generator.INSTANCE = eps
$call_context_roots((pcallcontext_generator)) = eps
$lookup(S.ENV, $ptascii("input")) = (n_input)
S.STORE[n_input] = DEFINED (PINT 9)
$lookup(S.ENV, $ptascii("weakToken")) = (n_weak_cell)
S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)
S.OBJECTS[n_weak] = WEAKREFERENCE (n_token)
$weakref_get(S, n_weak) = POBJECT n_token
$lookup(pfibervm.TABLE.ENV, $ptascii("item")) = eps
$node_children(S, HOBJECT n_generator) = [HOBJECT n_token]
$heap_owners($heap_graph(S), HOBJECT n_token) = 1
$lookup(S.ENV, $ptascii("producer")) = (n_producer_cell)
S.STORE[n_producer_cell] = DEFINED pvalue_producer
$string_bytes(pvalue_producer) = ($ptascii("Mid75Next"))
S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]
$generator_creation_owner(S_view) = (n_generator)
$generator_creation_object_selected(S_view, n_generator, pcallcontext_generator)
$generator_creation_selected(S_view, pcallcontext_generator.TARGET, pgeneratorcreation.SITE)
$call_current_valid(S_view)
$fiber_vm_valid(S, pfibervm, (n_fiber), eps)
$fiber_generator_body_id(S_view) = (n_generator)
$effective_method(S, porigin_mid, $ptascii("body"), |S.CLASSES|) = (pmethoddesc_mid_body)
pgeneratorcreation_bad_requested = pgeneratorcreation[.CALLEE = SCOPED_TARGET porigin_mid pmethoddesc_mid_body.FUNCTION.ORIGIN porigin_leaf eps (KNOWN (PSTRING ($ptascii("Mid75Next"))))]
$target_function(S, pgeneratorcreation_bad_requested.CALLEE) = (pmethoddesc_mid_body.FUNCTION)
~$generator_creation_scope_valid(S, pgeneratorcreation_bad_requested)
pgeneratorcreation_bad_called = pgeneratorcreation[.CREATOR = pgeneratorcreation.CREATOR[.CALLED_CLASS = (porigin_mid)]]
~$generator_creator_valid(S, pgeneratorcreation_bad_called)
pcallcontext_lexical = pcallcontext_generator[.LEXICAL_CLASS = (porigin_mid)]
~$call_current_valid(S_view[.CURRENT = (pcallcontext_lexical)])
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
''')

CLOSE_ENTER_STAGE = (
    'S.TODO = (GENERATOR_CLOSE_ENTER pgenclose) :: ptask_tail* '
    '-- if S.OBJECTS[pgenclose.OBJECT] = GENERATOR pgenerator '
    '-- if pgenerator.CREATION = (pgeneratorcreation)')

CLOSE_DONE_STAGE = (
    'S.FRAMES = pframe_close :: pframe_tail* '
    '-- if pframe_close.TODO = (GENERATOR_CLOSE_DONE pgenclose) :: ptask_close* '
    '-- if S.OBJECTS[pgenclose.OBJECT] = GENERATOR pgenerator '
    '-- if pgenerator.CREATION = (pgeneratorcreation)')

CLOSE_COMMON = checks(r'''
S.COMPLETION = NORMAL
S.OBJECTS[pgenclose.OBJECT] = GENERATOR pgenerator
pgenerator.CREATION = (pgeneratorcreation)
n_generator = pgenclose.OBJECT
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base75Close"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Mid75Close"))) = (porigin_mid)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Leaf75Close"))) = (porigin_leaf)
$class_method_origin(S.CLASSES, pgeneratorcreation.CREATOR.FUNCTION) = (pmethoddesc_make)
pmethoddesc_make.STATIC
pmethoddesc_make.OWNER = porigin_mid
$class_method_origin(S.CLASSES, pgenerator.FUNCTION) = (pmethoddesc_body)
pmethoddesc_body.STATIC
pmethoddesc_body.VISIBILITY = PROPERTY_PROTECTED
pmethoddesc_body.OWNER = porigin_base
pgeneratorcreation.CREATOR.LEXICAL_CLASS = (porigin_mid)
pgeneratorcreation.CREATOR.CALLED_CLASS = (porigin_leaf)
pgeneratorcreation.CREATOR_TARGET = STATIC_METHOD_TARGET porigin_leaf pgeneratorcreation.CREATOR.FUNCTION
pgeneratorcreation.CALLEE = SCOPED_TARGET porigin_base pgenerator.FUNCTION porigin_leaf eps poperand_selector
$target_function(S, pgeneratorcreation.CREATOR_TARGET) = (pmethoddesc_make.FUNCTION)
$target_function(S, pgeneratorcreation.CALLEE) = (pmethoddesc_body.FUNCTION)
$generator_creator_valid(S, pgeneratorcreation)
$generator_creation_scope_valid(S, pgeneratorcreation)
$generator_creation_record_valid(S, pgenerator)
$lookup(S_main.ENV, $ptascii("other")) = (n_other_cell)
S.STORE[n_other_cell] = DEFINED (POBJECT n_other)
n_other =/= n_generator
S.OBJECTS[n_other] = GENERATOR pgenerator_other
pgenerator_other.PHASE = GENERATOR_FRESH
pgenerator_other.CREATION = (pgeneratorcreation_other)
pgenerator_other.FRAME = (pframe_other)
pframe_other.CONTEXT = (pcallcontext_other)
pcallcontext_other = pcallcontext_generator
$generator_creation_record_valid(S, pgenerator_other)
$lookup(S_main.ENV, $ptascii("weakMaker")) = (n_weak_maker_cell)
S.STORE[n_weak_maker_cell] = DEFINED (POBJECT n_weak_maker)
S.OBJECTS[n_weak_maker] = WEAKREFERENCE (n_maker)
$weakref_get(S, n_weak_maker) = PNULL
~((HOBJECT n_maker) <- S.ALLOCATIONS)
~((HOBJECT n_maker) <- $node_children(S, HOBJECT n_generator))
$lookup(S_main.ENV, $ptascii("selector")) = (n_selector_cell)
S.STORE[n_selector_cell] = DEFINED (PINT 99)
$generator_creation_close_owner(S_select) = (n_generator)
$generator_creation_owner(S_select) = (n_generator)
$generator_creation_object_selected(S_select, n_other, pcallcontext_generator)
$generator_creation_object_selected(S_select, n_generator, pcallcontext_generator)
$generator_creation_selected(S_select, pcallcontext_generator.TARGET, pgeneratorcreation.SITE)
S_missing = S_select[.OBJECTS = $object_set(S_select.OBJECTS, n_generator, GENERATOR pgenerator[.CREATION = eps])]
$generator_creation_owner(S_missing) = (n_generator)
~$generator_creation_selected(S_missing, pcallcontext_generator.TARGET, pgeneratorcreation.SITE)
pgeneratorcreation_bad_called = pgeneratorcreation[.CREATOR = pgeneratorcreation.CREATOR[.CALLED_CLASS = (porigin_mid)]]
S_corrupt = S_select[.OBJECTS = $object_set(S_select.OBJECTS, n_generator, GENERATOR pgenerator[.CREATION = (pgeneratorcreation_bad_called)])]
~$generator_creation_selected(S_corrupt, pcallcontext_generator.TARGET, pgeneratorcreation.SITE)
S_unallocated = S_select[.ALLOCATIONS = $destruction_node_delete(S_select.ALLOCATIONS, HOBJECT n_generator)]
$generator_creation_owner(S_unallocated) = (n_generator)
~$generator_creation_selected(S_unallocated, pcallcontext_generator.TARGET, pgeneratorcreation.SITE)
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
''')

CLOSE_ENTER = checks(r'''
S.CURRENT = eps
S.FRAMES = eps
pgenclose.FRAME = (pframe_saved)
pgenclose.CONTEXT = pcallcontext_generator
pcallcontext_generator.TARGET = pgeneratorcreation.CALLEE
pcallcontext_generator.CALLSITE = (pgeneratorcreation.SITE)
pcallcontext_generator.FUNCTION = pgenerator.FUNCTION
pcallcontext_generator.LEXICAL_CLASS = (porigin_base)
pcallcontext_generator.CALLED_CLASS = (porigin_leaf)
pcallcontext_generator.RECEIVER = eps
pcallcontext_generator.INSTANCE = eps
$call_context_roots((pcallcontext_generator)) = eps
S_main = S
S_select = $generator_close_frame_scope(S, pframe_saved)
$generator_close_enter_valid(S, pgenclose)
''')

CLOSE_DONE = checks(r'''
S.CURRENT = (pcallcontext_generator)
pgenclose.CONTEXT = pcallcontext_generator
pcallcontext_generator.TARGET = pgeneratorcreation.CALLEE
pcallcontext_generator.CALLSITE = (pgeneratorcreation.SITE)
pcallcontext_generator.FUNCTION = pgenerator.FUNCTION
pcallcontext_generator.LEXICAL_CLASS = (porigin_base)
pcallcontext_generator.CALLED_CLASS = (porigin_leaf)
pcallcontext_generator.RECEIVER = eps
pcallcontext_generator.INSTANCE = eps
$call_context_roots((pcallcontext_generator)) = eps
S_main = $constant_frame_scope(S, pframe_close, pframe_tail*)
S_select = S
$generator_close_done_valid(S_main, pgenclose)
$call_current_valid(S)
''')

CLOSE_ENTER_NEGATIVE = checks(r'''
S_outer_missing = S[.OBJECTS = $object_set(S.OBJECTS, n_generator, GENERATOR pgenerator[.CREATION = eps])]
~$generator_close_frame_valid(S_outer_missing, pgenerator[.CREATION = eps], pframe_saved)
~$generator_close_enter_valid(S_outer_missing, pgenclose)
''')

CLOSE_DONE_NEGATIVE = checks(r'''
S_active_missing = S[.OBJECTS = $object_set(S.OBJECTS, n_generator, GENERATOR pgenerator[.CREATION = eps])]
~$call_current_valid(S_active_missing)
''')

CASES = {
    'i75-private-self-retained-scope-and-actual-owner': {
        'source': ROWS['i75-self-private-reference-throw-duplicate-frames']['source'],
        'stage': PARK_STAGE,
        'checks': PRIVATE_SELF,
    },
    'i75-late-static-leaf-selection': {
        'source': ROWS['i75-static-byval-override-next-two-stage']['source'],
        'stage': RESUME_STAGE,
        'checks': LATE_STATIC,
    },
    'i75-parent-close-enter-actual-owner': {
        'source': ROWS['i75-parent-keyword-force-close-owner']['source'],
        'stage': CLOSE_ENTER_STAGE,
        'checks': [*CLOSE_ENTER, *CLOSE_COMMON, *CLOSE_ENTER_NEGATIVE],
    },
    'i75-parent-close-done-actual-owner': {
        'source': ROWS['i75-parent-keyword-force-close-owner']['source'],
        'stage': CLOSE_DONE_STAGE,
        'checks': [*CLOSE_DONE, *CLOSE_COMMON, *CLOSE_DONE_NEGATIVE],
    },
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
