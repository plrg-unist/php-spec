#!/usr/bin/env python3
"""Check source-reached rebound Closure method Generator creation."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_closure_method_cases.json')
INPUT_BYTES = {path: path.read_bytes() for path in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


SECOND_CREATE_STAGE = (
    'S.TODO = (GENERATOR_CREATE porigin_body) :: ptask_tail* '
    '-- if S.CURRENT = (pcallcontext_generator) '
    '-- if pcallcontext_generator.FUNCTION = porigin_body '
    '-- if S.FRAMES = pframe_creator :: pframe_tail* '
    '-- if S_global = $global_table_view(S) '
    '-- if $lookup(S_global.ENV, $ptascii("g")) = (n_first_cell) '
    '-- if S_global.STORE[n_first_cell] = DEFINED (POBJECT n_first) '
    '-- if (HOBJECT n_first) <- S.ALLOCATIONS '
    '-- if S.OBJECTS[n_first] = GENERATOR pgenerator_first '
    '-- if pgenerator_first.PHASE = GENERATOR_FRESH '
    '-- if pgenerator_first.FRAME = (pframe_first) '
    '-- if pframe_first.CONTEXT = (pcallcontext_generator) '
    '-- if pgenerator_first.CREATION = (pgeneratorcreation_first)')

SECOND_CREATE = checks(r'''
S.COMPLETION = NORMAL
pcallcontext_generator.TARGET = METHOD_TARGET n_receiver porigin_body
pcallcontext_generator.CALLSITE = (porigin_site)
pcallcontext_generator.RECEIVER = (n_receiver)
pcallcontext_generator.INSTANCE = eps
pgenerator_first.CLOSURE = eps
pgeneratorcreation_first.CALLEE = pcallcontext_generator.TARGET
pgeneratorcreation_first.SITE = porigin_site
pgeneratorcreation_first.CLOSURE = (CLOSURE_BINDING pclosurebinding_first)
pframe_creator.ORIGIN = (porigin_site)
pframe_creator.CONTEXT = (pcallcontext_creator)
S_creator = $constant_frame_scope(S, pframe_creator, pframe_tail*)
$call_current_valid(S_creator)
$closure_evidence_current(S_creator) = (CLOSURE_BINDING pclosurebinding_second)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Mid79A"))) = (porigin_mid)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Leaf79A"))) = (porigin_leaf)
S.OBJECTS[n_receiver] = INSTANCE porigin_leaf
(HOBJECT n_receiver) <- S.ALLOCATIONS
pclosurebinding_first.LEXICAL = (porigin_mid)
pclosurebinding_second.LEXICAL = (porigin_mid)
n_factory_first = pclosurebinding_first.OBJECT
n_factory_second = pclosurebinding_second.OBJECT
n_factory_first =/= n_factory_second
pgeneratorcreation_first.CREATOR_TARGET = CLOSURE_TARGET n_factory_first
$closure_evidence_valid(S, CLOSURE_BINDING pclosurebinding_first)
$closure_evidence_valid(S, CLOSURE_BINDING pclosurebinding_second)
$generator_creation_object_selected(S, n_first, pcallcontext_generator)
$generator_context_retained(S, pcallcontext_generator)
$generator_method_scope_kind(S, porigin_body, porigin_site)
$generator_creation_owner(S) = eps
~$generator_creation_method_source(S, pcallcontext_generator.TARGET, porigin_site)
$generator_creation_required(S, pcallcontext_generator)
$generator_creation_selected(S, pcallcontext_generator.TARGET, porigin_site)
~$generator_creation_method_retained(S, pcallcontext_generator.TARGET, porigin_site)
$generator_creation_method_live_capture(S, pcallcontext_generator.TARGET, porigin_site) = (pgeneratorcreation_second)
pgeneratorcreation_second.CREATOR_TARGET = CLOSURE_TARGET n_factory_second
$generator_creator_valid(S, pgeneratorcreation_second)
$generator_creation_scope_valid(S, pgeneratorcreation_second)
$generator_creation_capture(S, pcallcontext_generator) = (pgeneratorcreation_second)
$call_current_valid(S)
pcallcontext_creator_wrong = pcallcontext_creator[.LEXICAL_CLASS = (porigin_leaf)]
pframe_creator_wrong = pframe_creator[.CONTEXT = (pcallcontext_creator_wrong)]
S_wrong = S[.FRAMES = pframe_creator_wrong :: pframe_tail*]
$generator_creation_selected(S_wrong, pcallcontext_generator.TARGET, porigin_site)
~$generator_creation_method_retained(S_wrong, pcallcontext_generator.TARGET, porigin_site)
$generator_creation_method_live_capture(S_wrong, pcallcontext_generator.TARGET, porigin_site) = eps
~$call_current_valid(S_wrong)
''')

CLOSE_STAGE = (
    'S.TODO = (GENERATOR_CLOSE_ENTER pgenclose) :: ptask_tail* '
    '-- if S.OBJECTS[pgenclose.OBJECT] = GENERATOR pgenerator '
    '-- if pgenerator.CREATION = (pgeneratorcreation) '
    '-- if $lookup(S.ENV, $ptascii("other")) = (n_other_cell) '
    '-- if S.STORE[n_other_cell] = DEFINED (POBJECT n_other) '
    '-- if S.OBJECTS[n_other] = GENERATOR pgenerator_other '
    '-- if pgenerator_other.PHASE = GENERATOR_FRESH '
    '-- if pgenerator_other.CREATION = (pgeneratorcreation_other)')

CLOSE_SIBLING = checks(r'''
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
pgenclose.FRAME = (pframe_generator)
pgenclose.CONTEXT = pcallcontext_generator
S_view = $generator_close_frame_scope(S, pframe_generator)
pgenerator.CLOSURE = eps
pgeneratorcreation.CLOSURE = (CLOSURE_BINDING pclosurebinding)
pgeneratorcreation_other.CLOSURE = (CLOSURE_BINDING pclosurebinding_other)
pgeneratorcreation.ANCESTORS = eps
pgeneratorcreation_other.ANCESTORS = eps
pgeneratorcreation.CALLEE = METHOD_TARGET n_receiver pgenerator.FUNCTION
pgeneratorcreation_other.CALLEE = pgeneratorcreation.CALLEE
pgeneratorcreation_other.SITE = pgeneratorcreation.SITE
pcallcontext_generator.TARGET = pgeneratorcreation.CALLEE
pcallcontext_generator.CALLSITE = (pgeneratorcreation.SITE)
pcallcontext_generator.RECEIVER = (n_receiver)
pgenerator_other.FRAME = (pframe_other)
pframe_other.CONTEXT = (pcallcontext_generator)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Mid79A"))) = (porigin_mid)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Leaf79A"))) = (porigin_leaf)
S.OBJECTS[n_receiver] = INSTANCE porigin_leaf
(HOBJECT n_receiver) <- S.ALLOCATIONS
pclosurebinding.LEXICAL = (porigin_mid)
pclosurebinding_other.LEXICAL = (porigin_mid)
n_factory = pclosurebinding.OBJECT
n_factory_other = pclosurebinding_other.OBJECT
n_factory =/= n_factory_other
pgeneratorcreation.CREATOR_TARGET = CLOSURE_TARGET n_factory
pgeneratorcreation_other.CREATOR_TARGET = CLOSURE_TARGET n_factory_other
~((HOBJECT n_factory) <- S.ALLOCATIONS)
~((HOBJECT n_factory_other) <- S.ALLOCATIONS)
$closure_evidence_valid(S, CLOSURE_BINDING pclosurebinding)
$closure_evidence_valid(S, CLOSURE_BINDING pclosurebinding_other)
$lookup(S.ENV, $ptascii("weakCapture")) = (n_weak_capture_cell)
S.STORE[n_weak_capture_cell] = DEFINED (POBJECT n_weak_capture)
S.OBJECTS[n_weak_capture] = WEAKREFERENCE (n_capture)
$weakref_get(S, n_weak_capture) = PNULL
~((HOBJECT n_capture) <- S.ALLOCATIONS)
$heap_owners($heap_graph(S), HOBJECT n_receiver) = 2
$heap_count(HOBJECT n_receiver, $task_nodes(GENERATOR_CLOSE_ENTER pgenclose)) = 1
~$generator_creation_method_source(S, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
$generator_creator_valid(S, pgeneratorcreation)
$generator_creator_valid(S, pgeneratorcreation_other)
$generator_creation_scope_valid(S, pgeneratorcreation)
$generator_creation_scope_valid(S, pgeneratorcreation_other)
$generator_creation_record_valid(S, pgenerator)
$generator_creation_record_valid(S, pgenerator_other)
$generator_close_enter_valid(S, pgenclose)
$generator_creation_owner(S_view) = (pgenclose.OBJECT)
$generator_creation_selected(S_view, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
$generator_creation_object_selected(S, n_other, pcallcontext_generator)
pgenerator_missing = pgenerator[.CREATION = eps]
S_missing = S_view[.OBJECTS = $object_set(S_view.OBJECTS, pgenclose.OBJECT, GENERATOR pgenerator_missing)]
$generator_creation_owner(S_missing) = (pgenclose.OBJECT)
$generator_creation_object_selected(S_missing, n_other, pcallcontext_generator)
~$generator_creation_selected(S_missing, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
~$generator_creation_method_retained(S_missing, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
~$call_current_valid(S_missing)
''')

THROW_STAGE = (
    'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
    '-- if pconfigcall.KIND = INTRINSIC_FIBER_THROW '
    '-- if pconfigcall.OWNER = (n_fiber) '
    '-- if S.OBJECTS[n_fiber] = FIBER pfiber '
    '-- if pfiber.STATUS = FIBER_SUSPENDED')

TEMPORARY_ABORT = checks(r'''
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
S.ACTIVEFIBER = eps
$lookup(S.ENV, $ptascii("g")) = (n_generator_cell)
S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)
S.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_RUNNING
pgenerator.FRAME = eps
pgenerator.CLOSURE = eps
pgenerator.VALUE = eps
pgenerator.REFCELL = eps
pgenerator.CREATION = (pgeneratorcreation)
pgeneratorcreation.CLOSURE = (CLOSURE_CALL porigin_call n_factory n_receiver porigin_leaf)
pgeneratorcreation.CREATOR_TARGET = CLOSURE_CALL_TARGET n_factory n_receiver
pgeneratorcreation.CREATOR.CALLSITE = (porigin_call)
pgeneratorcreation.ANCESTORS = eps
pgeneratorcreation.CALLEE = METHOD_TARGET n_receiver pgenerator.FUNCTION
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base79C"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Leaf79C"))) = (porigin_leaf)
S.OBJECTS[n_receiver] = INSTANCE porigin_leaf
(HOBJECT n_receiver) <- S.ALLOCATIONS
~((HOBJECT n_factory) <- S.ALLOCATIONS)
$closure_evidence_valid(S, CLOSURE_CALL porigin_call n_factory n_receiver porigin_leaf)
$generator_creator_valid(S, pgeneratorcreation)
$generator_creation_scope_valid(S, pgeneratorcreation)
$generator_creation_record_valid(S, pgenerator)
$heap_owners($heap_graph(S), HOBJECT n_receiver) = 1
pfiber.VM = (pfibervm)
~pfibervm.GLOBAL
pfibervm.CURRENT = (pcallcontext_generator)
pfibervm.FRAMES = pframe_generator :: pframe_tail*
pframe_generator.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_generator*
pgeneratorop.OBJECT = n_generator
pgeneratorop.NAME = "current"
pgeneratorop.ARGUMENTS = eps
~pgeneratorop.ADVANCE
pcallcontext_generator.TARGET = pgeneratorcreation.CALLEE
pcallcontext_generator.CALLSITE = (pgeneratorcreation.SITE)
pcallcontext_generator.RECEIVER = (n_receiver)
S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]
$fiber_vm_valid(S, pfibervm, (n_fiber), eps)
$call_current_valid(S_view)
$fiber_generator_body_id(S_view) = (n_generator)
$generator_creation_owner(S_view) = (n_generator)
$generator_creation_method_live_capture(S_view, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE) = eps
$generator_creation_selected(S_view, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
$heap_count(HOBJECT n_receiver, $fiber_vm_nodes(pfibervm)) = 1
pgenerator_missing = pgenerator[.CREATION = eps]
S_missing = $generator_set(S_view, n_generator, pgenerator_missing)
$generator_creation_owner(S_missing) = (n_generator)
~$generator_creation_selected(S_missing, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
~$call_current_valid(S_missing)
$fiber_generator_body_id(S_missing) = eps
''')

FRESH_STAGE = (
    'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
    '-- if pconfigcall.KIND = INTRINSIC_WEAKREF_GET '
    '-- if $lookup(S.ENV, $ptascii("g")) = (n_generator_cell) '
    '-- if S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator) '
    '-- if S.OBJECTS[n_generator] = GENERATOR pgenerator '
    '-- if pgenerator.PHASE = GENERATOR_FRESH '
    '-- if pgenerator.CREATION = (pgeneratorcreation)')

RETIRED_STATIC = checks(r'''
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
pgenerator.CLOSURE = eps
pgenerator.FRAME = (pframe_generator)
pframe_generator.CONTEXT = (pcallcontext_generator)
pgeneratorcreation.CLOSURE = (CLOSURE_BINDING pclosurebinding)
pgeneratorcreation.ANCESTORS = eps
pgeneratorcreation.CALLEE = STATIC_METHOD_TARGET porigin_leaf pgenerator.FUNCTION
pcallcontext_generator.TARGET = pgeneratorcreation.CALLEE
pcallcontext_generator.CALLSITE = (pgeneratorcreation.SITE)
pcallcontext_generator.RECEIVER = eps
$class_named(S.CLASSNAMES, $ptlc($ptascii("Mid79D"))) = (porigin_mid)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Leaf79D"))) = (porigin_leaf)
pclosurebinding.LEXICAL = (porigin_mid)
pclosurebinding.CALLED = (porigin_leaf)
pclosurebinding.RECEIVER = (n_maker)
S.OBJECTS[n_maker] = INSTANCE porigin_leaf
~((HOBJECT n_maker) <- S.ALLOCATIONS)
n_factory = pclosurebinding.OBJECT
pgeneratorcreation.CREATOR_TARGET = CLOSURE_TARGET n_factory
~((HOBJECT n_factory) <- S.ALLOCATIONS)
$closure_evidence_valid(S, CLOSURE_BINDING pclosurebinding)
$lookup(S.ENV, $ptascii("weakMaker")) = (n_weak_maker_cell)
S.STORE[n_weak_maker_cell] = DEFINED (POBJECT n_weak_maker)
S.OBJECTS[n_weak_maker] = WEAKREFERENCE (n_maker)
$weakref_get(S, n_weak_maker) = PNULL
$lookup(S.ENV, $ptascii("weakCapture")) = (n_weak_capture_cell)
S.STORE[n_weak_capture_cell] = DEFINED (POBJECT n_weak_capture)
S.OBJECTS[n_weak_capture] = WEAKREFERENCE (n_capture)
$weakref_get(S, n_weak_capture) = PNULL
~((HOBJECT n_capture) <- S.ALLOCATIONS)
$target_nodes(pcallcontext_generator.TARGET) = eps
$call_context_roots((pcallcontext_generator)) = eps
$heap_count(HOBJECT n_maker, $node_children(S, HOBJECT n_generator)) = 0
~$generator_creation_method_source(S, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
$generator_creation_required(S, pcallcontext_generator)
$generator_creator_valid(S, pgeneratorcreation)
$generator_creation_scope_valid(S, pgeneratorcreation)
$generator_creation_record_valid(S, pgenerator)
$generator_creation_object_selected(S, n_generator, pcallcontext_generator)
S_view = $generator_frame_scope(S, pframe_generator)
$call_saved_context_valid(S_view, pframe_generator)
$generator_creation_method_live_capture(S_view, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE) = eps
$generator_creation_selected(S_view, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
pgenerator_missing = pgenerator[.CREATION = eps]
S_missing = $generator_set(S_view, n_generator, pgenerator_missing)
~$generator_creation_selected(S_missing, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
~$call_saved_context_valid(S_missing, pframe_generator)
''')

CASES = {
    'i79-second-live-creation': {'source': ROWS['i79-bound-private-close']['source'], 'stage': SECOND_CREATE_STAGE, 'checks': SECOND_CREATE},
    'i79-close-with-fresh-sibling': {'source': ROWS['i79-bound-private-close']['source'], 'stage': CLOSE_STAGE, 'checks': CLOSE_SIBLING},
    'i79-temporary-call-fiber-abort': {'source': ROWS['i79-temporary-call-nullsafe-abort']['source'], 'stage': THROW_STAGE, 'checks': TEMPORARY_ABORT},
    'i79-retired-static-selector': {'source': ROWS['i79-static-object-selector']['source'], 'stage': FRESH_STAGE, 'checks': RETIRED_STATIC},
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
