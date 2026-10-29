#!/usr/bin/env python3
"""Check source-reached receiver-bearing Generator creation and Fiber states."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_keyword_receiver_cases.json')
INPUT_BYTES = {path: path.read_bytes() for path in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


CLOSE_STAGE = (
    'S.TODO = (GENERATOR_CLOSE_ENTER pgenclose) :: ptask_tail* '
    '-- if S.OBJECTS[pgenclose.OBJECT] = GENERATOR pgenerator '
    '-- if pgenerator.CREATION = (pgeneratorcreation)')

CLOSE_RECEIVER = checks(r'''
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
pgenclose.FRAME = (pframe_saved)
pgenclose.CONTEXT = pcallcontext_generator
S_view = $generator_close_frame_scope(S, pframe_saved)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base77A"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Mid77A"))) = (porigin_mid)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Leaf77A"))) = (porigin_leaf)
$class_method_origin(S.CLASSES, pgenerator.FUNCTION) = (pmethoddesc_body)
~pmethoddesc_body.STATIC
pmethoddesc_body.VISIBILITY = PROPERTY_PROTECTED
pmethoddesc_body.OWNER = porigin_base
pgeneratorcreation.CREATOR.LEXICAL_CLASS = (porigin_mid)
pgeneratorcreation.CREATOR.CALLED_CLASS = (porigin_leaf)
$class_method_origin(S.CLASSES, pgeneratorcreation.CREATOR.FUNCTION) = (pmethoddesc_make)
pmethoddesc_make.OWNER = porigin_mid
pgeneratorcreation.ANCESTORS = eps
pgeneratorcreation.CREATOR_TARGET = METHOD_TARGET n_receiver_a pgeneratorcreation.CREATOR.FUNCTION
pgeneratorcreation.CALLEE = SCOPED_TARGET porigin_base pgenerator.FUNCTION porigin_leaf (n_receiver_a) poperand_body
pcallcontext_generator.TARGET = pgeneratorcreation.CALLEE
pcallcontext_generator.CALLSITE = (pgeneratorcreation.SITE)
pcallcontext_generator.FUNCTION = pgenerator.FUNCTION
pcallcontext_generator.LEXICAL_CLASS = (porigin_base)
pcallcontext_generator.CALLED_CLASS = (porigin_leaf)
pcallcontext_generator.RECEIVER = (n_receiver_a)
pcallcontext_generator.INSTANCE = eps
S.OBJECTS[n_receiver_a] = INSTANCE porigin_leaf
(HOBJECT n_receiver_a) <- S.ALLOCATIONS
$call_context_roots((pcallcontext_generator)) = [HOBJECT n_receiver_a]
$heap_owners($heap_graph(S), HOBJECT n_receiver_a) = 1
$heap_count(HOBJECT n_receiver_a, $task_nodes(GENERATOR_CLOSE_ENTER pgenclose)) = 1
$generator_retained_scoped_target(S, pgeneratorcreation.CALLEE, pmethoddesc_body)
$generator_creator_valid(S, pgeneratorcreation)
$generator_creation_scope_valid(S, pgeneratorcreation)
$generator_creation_record_valid(S, pgenerator)
$generator_close_enter_valid(S, pgenclose)
$generator_creation_owner(S_view) = (pgenclose.OBJECT)
$generator_creation_selected(S_view, pcallcontext_generator.TARGET, pgeneratorcreation.SITE)
$lookup(S.ENV, $ptascii("other")) = (n_other_cell)
S.STORE[n_other_cell] = DEFINED (POBJECT n_other)
n_other =/= pgenclose.OBJECT
S.OBJECTS[n_other] = GENERATOR pgenerator_other
pgenerator_other.PHASE = GENERATOR_FRESH
pgenerator_other.CREATION = (pgeneratorcreation_other)
pgenerator_other.FRAME = (pframe_other)
pframe_other.CONTEXT = (pcallcontext_other)
pcallcontext_other.RECEIVER = (n_receiver_b)
n_receiver_b =/= n_receiver_a
S.OBJECTS[n_receiver_b] = INSTANCE porigin_leaf
(HOBJECT n_receiver_b) <- S.ALLOCATIONS
pgeneratorcreation_other.CREATOR_TARGET = METHOD_TARGET n_receiver_b pgeneratorcreation_other.CREATOR.FUNCTION
$target_function(S, METHOD_TARGET n_receiver_b pgeneratorcreation.CREATOR.FUNCTION) = (pmethoddesc_make.FUNCTION)
pgeneratorcreation_wrong_root = pgeneratorcreation[.CREATOR_TARGET = METHOD_TARGET n_receiver_b pgeneratorcreation.CREATOR.FUNCTION]
$generator_creator_valid(S, pgeneratorcreation_wrong_root)
~$generator_creation_scope_valid(S, pgeneratorcreation_wrong_root)
pgenerator_missing = pgenerator[.CREATION = eps]
S_missing = S_view[.OBJECTS = $object_set(S_view.OBJECTS, pgenclose.OBJECT, GENERATOR pgenerator_missing)]
$generator_creation_owner(S_missing) = (pgenclose.OBJECT)
~$generator_creation_selected(S_missing, pcallcontext_generator.TARGET, pgeneratorcreation.SITE)
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
''')

RETIRED_STAGE = (
    'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
    '-- if pconfigcall.KIND = INTRINSIC_WEAKREF_GET '
    '-- if $lookup(S.ENV, $ptascii("g")) = (n_generator_cell) '
    '-- if S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator) '
    '-- if S.OBJECTS[n_generator] = GENERATOR pgenerator '
    '-- if pgenerator.PHASE = GENERATOR_CLOSED '
    '-- if pgenerator.CREATION = (pgeneratorcreation)')

RETIRED_RECEIVER = checks(r'''
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
pgenerator.FRAME = eps
pgenerator.RETURN = (PINT 77)
pgenerator.CLOSURE = eps
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base77B"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Mid77B"))) = (porigin_mid)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Leaf77B"))) = (porigin_leaf)
$class_method_origin(S.CLASSES, pgenerator.FUNCTION) = (pmethoddesc_body)
pmethoddesc_body.OWNER = porigin_base
pgeneratorcreation.CALLEE = SCOPED_TARGET porigin_base pgenerator.FUNCTION porigin_leaf (n_receiver) poperand_body
S.OBJECTS[n_receiver] = INSTANCE porigin_leaf
~((HOBJECT n_receiver) <- S.ALLOCATIONS)
~((HOBJECT n_receiver) <- $node_children(S, HOBJECT n_generator))
$lookup(S.ENV, $ptascii("weak")) = (n_weak_cell)
S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)
S.OBJECTS[n_weak] = WEAKREFERENCE (n_receiver)
$weakref_get(S, n_weak) = PNULL
$target_function(S, pgeneratorcreation.CALLEE) = eps
$generator_retained_scoped_target(S, pgeneratorcreation.CALLEE, pmethoddesc_body)
pgeneratorcreation.ANCESTORS = [pgenfactorycapture_mid, pgenfactorycapture_leaf, pgenfactorycapture_make]
pgeneratorcreation.CREATOR_TARGET = SCOPED_TARGET porigin_mid pgeneratorcreation.CREATOR.FUNCTION porigin_leaf (n_receiver) poperand_step
$class_method_origin(S.CLASSES, pgeneratorcreation.CREATOR.FUNCTION) = (pmethoddesc_step)
$target_function(S, pgeneratorcreation.CREATOR_TARGET) = eps
$generator_retained_scoped_target(S, pgeneratorcreation.CREATOR_TARGET, pmethoddesc_step)
$target_receiver(S, pgenfactorycapture_mid.TARGET) = (n_receiver)
$target_receiver(S, pgenfactorycapture_leaf.TARGET) = (n_receiver)
pgenfactorycapture_make.TARGET = METHOD_TARGET n_receiver pgenfactorycapture_make.CONTEXT.FUNCTION
$target_function(S, pgenfactorycapture_make.TARGET) = eps
$generator_creator_valid(S, pgeneratorcreation)
$generator_creation_scope_valid(S, pgeneratorcreation)
$generator_creation_record_valid(S, pgenerator)
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
''')

FIBER_STAGE = (
    'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
    '-- if pconfigcall.KIND = INTRINSIC_FIBER_RESUME '
    '-- if pconfigcall.OWNER = (n_fiber) '
    '-- if S.OBJECTS[n_fiber] = FIBER pfiber '
    '-- if pfiber.STATUS = FIBER_SUSPENDED '
    '-- if $lookup(S.ENV, $ptascii("g")) = (n_generator_cell) '
    '-- if S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator) '
    '-- if S.OBJECTS[n_generator] = GENERATOR pgenerator '
    '-- if pgenerator.CREATION = (pgeneratorcreation)')

FIBER_RECEIVER = checks(r'''
S.COMPLETION = NORMAL
S.ACTIVEFIBER = eps
S.CURRENT = eps
S.FRAMES = eps
pgenerator.PHASE = GENERATOR_RUNNING
pgenerator.FRAME = eps
pgenerator.FIRST
pgenerator.VALUE = eps
pgenerator.REFCELL = eps
pgenerator.CLOSURE = eps
pfiber.VM = (pfibervm)
~pfibervm.GLOBAL
pfibervm.CURRENT = (pcallcontext_generator)
pfibervm.FRAMES = pframe_resume :: pframe_tail*
$fiber_vm_valid(S, pfibervm, (n_fiber), eps)
pframe_resume.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_resume*
pgeneratorop.OBJECT = n_generator
pgeneratorop.NAME = "throw"
pgeneratorop.ARGUMENTS = [POBJECT n_given]
pgeneratorop.ADVANCE
~pgeneratorop.BORROWED
$throwable_member(S, n_given)
$task_nodes(GENERATOR_RESUME pgeneratorop) = [HOBJECT n_generator, HOBJECT n_given]
$heap_owners($heap_graph(S), HOBJECT n_given) = 1
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base77C"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Leaf77C"))) = (porigin_leaf)
$class_method_origin(S.CLASSES, pgenerator.FUNCTION) = (pmethoddesc_body)
pmethoddesc_body.OWNER = porigin_base
pgeneratorcreation.CREATOR_TARGET = METHOD_TARGET n_receiver pgeneratorcreation.CREATOR.FUNCTION
pgeneratorcreation.ANCESTORS = eps
pgeneratorcreation.CALLEE = SCOPED_TARGET porigin_leaf pgenerator.FUNCTION porigin_leaf (n_receiver) poperand_body
pcallcontext_generator.TARGET = pgeneratorcreation.CALLEE
pcallcontext_generator.CALLSITE = (pgeneratorcreation.SITE)
pcallcontext_generator.FUNCTION = pgenerator.FUNCTION
pcallcontext_generator.LEXICAL_CLASS = (porigin_base)
pcallcontext_generator.CALLED_CLASS = (porigin_leaf)
pcallcontext_generator.INSTANCE = eps
pcallcontext_generator.RECEIVER = (n_receiver)
$call_context_roots((pcallcontext_generator)) = [HOBJECT n_receiver]
$heap_owners($heap_graph(S), HOBJECT n_receiver) = 1
$generator_creation_record_valid(S, pgenerator)
S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]
$call_current_valid(S_view)
$fiber_generator_receiver_target(S_view, pgenerator, pcallcontext_generator)
$fiber_generator_callee_valid(S_view, pgenerator, pcallcontext_generator)
$fiber_generator_body_id(S_view) = (n_generator)
$fiber_generator_fresh_throw_valid(S_view, pgeneratorop, pgenerator, pcallcontext_generator)
~$fiber_generator_throw_valid(S_view, pgeneratorop, pgenerator, pcallcontext_generator)
$generator_creation_owner(S_view) = (n_generator)
$generator_creation_selected(S_view, pcallcontext_generator.TARGET, pgeneratorcreation.SITE)
pcallcontext_wrong_receiver = pcallcontext_generator[.RECEIVER = eps]
$generator_creation_required(S_view, pcallcontext_wrong_receiver)
~$fiber_generator_receiver_target(S_view, pgenerator, pcallcontext_wrong_receiver)
~$call_current_valid(S_view[.CURRENT = (pcallcontext_wrong_receiver)])
pgenerator_missing = pgenerator[.CREATION = eps]
S_missing = $generator_set(S_view, n_generator, pgenerator_missing)
$generator_creation_required(S_missing, pcallcontext_generator)
~$generator_creation_context_valid(S_missing, pgenerator_missing, pcallcontext_generator)
~$fiber_generator_receiver_target(S_missing, pgenerator_missing, pcallcontext_generator)
~$fiber_generator_callee_valid(S_missing, pgenerator_missing, pcallcontext_generator)
$generator_owners_valid(S)
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
''')

CASES = {
    'i77-close-actual-receiver-sibling': {
        'source': ROWS['i77-parent-instance-fresh-sibling-close']['source'],
        'stage': CLOSE_STAGE,
        'checks': CLOSE_RECEIVER,
    },
    'i77-completed-borrowed-receiver-history': {
        'source': ROWS['i77-late-static-instance-chain-complete']['source'],
        'stage': RETIRED_STAGE,
        'checks': RETIRED_RECEIVER,
    },
    'i77-fresh-throw-fiber-receiver': {
        'source': ROWS['i77-receiver-fresh-throw-fiber']['source'],
        'stage': FIBER_STAGE,
        'checks': FIBER_RECEIVER,
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
