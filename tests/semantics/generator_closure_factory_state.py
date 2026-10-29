#!/usr/bin/env python3
"""Check source-reached borrowed Closure factory evidence for Generators."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_closure_factory_cases.json')
INPUT_BYTES = {path: path.read_bytes() for path in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


FRESH_STAGE = (
    'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
    '-- if pconfigcall.KIND = INTRINSIC_WEAKREF_GET '
    '-- if $lookup(S.ENV, $ptascii("g")) = (n_generator_cell) '
    '-- if S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator) '
    '-- if S.OBJECTS[n_generator] = GENERATOR pgenerator '
    '-- if pgenerator.PHASE = GENERATOR_FRESH '
    '-- if pgenerator.CREATION = (pgeneratorcreation)')

STATIC_CLOSURE = checks(r'''
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
pgenerator.CLOSURE = eps
pgenerator.FRAME = (pframe_generator)
pframe_generator.CONTEXT = (pcallcontext_generator)
pgeneratorcreation.CLOSURE = (CLOSURE_SCOPE pclosurescope)
pgeneratorcreation.ANCESTORS = eps
n_factory = pclosurescope.OBJECT
pgeneratorcreation.CREATOR_TARGET = CLOSURE_TARGET n_factory
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base78A"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Leaf78A"))) = (porigin_leaf)
pclosurescope.LEXICAL = porigin_base
pclosurescope.CALLED = porigin_leaf
pclosurescope.RECEIVER = eps
pgeneratorcreation.CREATOR.LEXICAL_CLASS = (porigin_base)
pgeneratorcreation.CREATOR.CALLED_CLASS = (porigin_leaf)
$closure_evidence_valid(S, CLOSURE_SCOPE pclosurescope)
~((HOBJECT n_factory) <- S.ALLOCATIONS)
$heap_count(HOBJECT n_factory, $node_children(S, HOBJECT n_generator)) = 0
$lookup(S.ENV, $ptascii("weak")) = (n_weak_cell)
S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)
S.OBJECTS[n_weak] = WEAKREFERENCE (n_token)
$weakref_get(S, n_weak) = PNULL
~((HOBJECT n_token) <- S.ALLOCATIONS)
pgeneratorcreation.CALLEE = SCOPED_TARGET porigin_leaf pgenerator.FUNCTION porigin_leaf eps poperand_body
pcallcontext_generator.TARGET = pgeneratorcreation.CALLEE
pcallcontext_generator.CALLSITE = (pgeneratorcreation.SITE)
$generator_creator_closure_target(S, pgeneratorcreation.CREATOR_TARGET, pgeneratorcreation.CREATOR, CLOSURE_SCOPE pclosurescope)
$generator_creator_valid(S, pgeneratorcreation)
$generator_creation_scope_valid(S, pgeneratorcreation)
$generator_creation_record_valid(S, pgenerator)
$generator_creation_object_selected(S, n_generator, pcallcontext_generator)
S_view = $generator_frame_scope(S, pframe_generator)
$call_saved_context_valid(S_view, pframe_generator)
$generator_creation_selected(S_view, pcallcontext_generator.TARGET, pgeneratorcreation.SITE)
pgeneratorcreation_missing = pgeneratorcreation[.CLOSURE = eps]
~$generator_creator_valid(S, pgeneratorcreation_missing)
pgeneratorcreation_wrong_called = pgeneratorcreation[.CREATOR = pgeneratorcreation.CREATOR[.CALLED_CLASS = (porigin_base)]]
~$generator_creator_valid(S, pgeneratorcreation_wrong_called)
pclosurescope_wrong_called = pclosurescope[.CALLED = porigin_base]
pgeneratorcreation_coherent_wrong_called = pgeneratorcreation_wrong_called[.CLOSURE = (CLOSURE_SCOPE pclosurescope_wrong_called)]
$closure_evidence_valid(S, CLOSURE_SCOPE pclosurescope_wrong_called)
$generator_creator_valid(S, pgeneratorcreation_coherent_wrong_called)
~$generator_creation_scope_valid(S, pgeneratorcreation_coherent_wrong_called)
pgenerator_missing = pgenerator[.CREATION = eps]
S_missing = $generator_set(S_view, n_generator, pgenerator_missing)
~$generator_creation_selected(S_missing, pcallcontext_generator.TARGET, pgeneratorcreation.SITE)
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
''')

CLOSE_STAGE = (
    'S.TODO = (GENERATOR_CLOSE_ENTER pgenclose) :: ptask_tail* '
    '-- if S.OBJECTS[pgenclose.OBJECT] = GENERATOR pgenerator '
    '-- if pgenerator.CREATION = (pgeneratorcreation)')

BOUND_CLOSURE = checks(r'''
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
pgenclose.FRAME = (pframe_generator)
pgenclose.CONTEXT = pcallcontext_generator
S_view = $generator_close_frame_scope(S, pframe_generator)
pgeneratorcreation.CLOSURE = (CLOSURE_BINDING pclosurebinding)
pgeneratorcreation.ANCESTORS = eps
n_factory = pclosurebinding.OBJECT
pgeneratorcreation.CREATOR_TARGET = CLOSURE_TARGET n_factory
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base78B"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Leaf78B"))) = (porigin_leaf)
pclosurebinding.LEXICAL = (porigin_base)
pclosurebinding.CALLED = (porigin_leaf)
pclosurebinding.RECEIVER = (n_receiver)
S.OBJECTS[n_receiver] = INSTANCE porigin_leaf
(HOBJECT n_receiver) <- S.ALLOCATIONS
~((HOBJECT n_factory) <- S.ALLOCATIONS)
$closure_evidence_valid(S, CLOSURE_BINDING pclosurebinding)
pgeneratorcreation.CREATOR.LEXICAL_CLASS = (porigin_base)
pgeneratorcreation.CREATOR.CALLED_CLASS = (porigin_leaf)
pgeneratorcreation.CALLEE = SCOPED_TARGET porigin_base pgenerator.FUNCTION porigin_leaf (n_receiver) poperand_body
pcallcontext_generator.TARGET = pgeneratorcreation.CALLEE
pcallcontext_generator.RECEIVER = (n_receiver)
pcallcontext_generator.CALLSITE = (pgeneratorcreation.SITE)
$call_context_roots((pcallcontext_generator)) = [HOBJECT n_receiver]
$heap_owners($heap_graph(S), HOBJECT n_receiver) = 1
$heap_count(HOBJECT n_receiver, $task_nodes(GENERATOR_CLOSE_ENTER pgenclose)) = 1
$generator_creator_receiver(S, pgeneratorcreation.CREATOR_TARGET, pgeneratorcreation.CLOSURE) = (n_receiver)
$generator_creator_valid(S, pgeneratorcreation)
$generator_creation_scope_valid(S, pgeneratorcreation)
$generator_creation_record_valid(S, pgenerator)
$generator_close_enter_valid(S, pgenclose)
$generator_creation_owner(S_view) = (pgenclose.OBJECT)
$generator_creation_selected(S_view, pcallcontext_generator.TARGET, pgeneratorcreation.SITE)
$closure_evidence_body(S, pclosurebinding.SOURCE) = (pgeneratorcreation.CREATOR.FUNCTION)
pgeneratorcreation_wrong_target = pgeneratorcreation[.CREATOR_TARGET = CLOSURE_TARGET pclosurebinding.SOURCE]
~$generator_creator_valid(S, pgeneratorcreation_wrong_target)
pclosurebinding_wrong_receiver = pclosurebinding[.RECEIVER = eps]
pgeneratorcreation_wrong_receiver = pgeneratorcreation[.CLOSURE = (CLOSURE_BINDING pclosurebinding_wrong_receiver)]
~$generator_creator_valid(S, pgeneratorcreation_wrong_receiver)
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

TEMPORARY_CALL = checks(r'''
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
pgenerator.FRAME = eps
pgenerator.RETURN = (PINT 79)
pgeneratorcreation.CLOSURE = (CLOSURE_CALL porigin_call n_factory n_receiver porigin_leaf)
pgeneratorcreation.ANCESTORS = eps
pgeneratorcreation.CREATOR_TARGET = CLOSURE_CALL_TARGET n_factory n_receiver
pgeneratorcreation.CREATOR.CALLSITE = (porigin_call)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base78C"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Leaf78C"))) = (porigin_leaf)
S.OBJECTS[n_receiver] = INSTANCE porigin_leaf
~((HOBJECT n_factory) <- S.ALLOCATIONS)
~((HOBJECT n_receiver) <- S.ALLOCATIONS)
pgeneratorcreation.CREATOR.LEXICAL_CLASS = (porigin_leaf)
pgeneratorcreation.CREATOR.CALLED_CLASS = (porigin_leaf)
$closure_evidence_valid(S, CLOSURE_CALL porigin_call n_factory n_receiver porigin_leaf)
$generator_creator_closure_target(S, pgeneratorcreation.CREATOR_TARGET, pgeneratorcreation.CREATOR, CLOSURE_CALL porigin_call n_factory n_receiver porigin_leaf)
pgeneratorcreation.CALLEE = SCOPED_TARGET porigin_leaf pgenerator.FUNCTION porigin_leaf (n_receiver) poperand_body
$generator_creator_valid(S, pgeneratorcreation)
$generator_creation_scope_valid(S, pgeneratorcreation)
$generator_creation_record_valid(S, pgenerator)
pgeneratorcreation_wrong_site = pgeneratorcreation[.CLOSURE = (CLOSURE_CALL pgeneratorcreation.SITE n_factory n_receiver porigin_leaf)]
~$generator_creator_valid(S, pgeneratorcreation_wrong_site)
pgeneratorcreation_wrong_object = pgeneratorcreation[.CREATOR_TARGET = CLOSURE_CALL_TARGET n_receiver n_receiver]
~$generator_creator_valid(S, pgeneratorcreation_wrong_object)
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
''')

ANCESTOR_CLOSURE = checks(r'''
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
pgenerator.FRAME = (pframe_generator)
pframe_generator.CONTEXT = (pcallcontext_generator)
pgeneratorcreation.CLOSURE = eps
pgeneratorcreation.ANCESTORS = [pgenfactorycapture]
pgenfactorycapture.CLOSURE = (CLOSURE_SCOPE pclosurescope)
n_factory = pclosurescope.OBJECT
pgenfactorycapture.TARGET = CLOSURE_TARGET n_factory
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base78D"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Mid78D"))) = (porigin_mid)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Leaf78D"))) = (porigin_leaf)
pclosurescope.LEXICAL = porigin_mid
pclosurescope.CALLED = porigin_leaf
pclosurescope.RECEIVER = eps
pgenfactorycapture.CONTEXT.LEXICAL_CLASS = (porigin_mid)
pgenfactorycapture.CONTEXT.CALLED_CLASS = (porigin_leaf)
$closure_evidence_valid(S, CLOSURE_SCOPE pclosurescope)
~((HOBJECT n_factory) <- S.ALLOCATIONS)
$heap_count(HOBJECT n_factory, $node_children(S, HOBJECT n_generator)) = 0
$lookup(S.ENV, $ptascii("weak")) = (n_weak_cell)
S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)
S.OBJECTS[n_weak] = WEAKREFERENCE (n_token)
$weakref_get(S, n_weak) = PNULL
~((HOBJECT n_token) <- S.ALLOCATIONS)
pgeneratorcreation.CREATOR.LEXICAL_CLASS = (porigin_mid)
pgeneratorcreation.CREATOR.CALLED_CLASS = (porigin_leaf)
pgeneratorcreation.CREATOR_TARGET = SCOPED_TARGET porigin_mid pgeneratorcreation.CREATOR.FUNCTION porigin_leaf eps poperand_bridge
pgeneratorcreation.CALLEE = SCOPED_TARGET porigin_base pgenerator.FUNCTION porigin_leaf eps poperand_body
pcallcontext_generator.TARGET = pgeneratorcreation.CALLEE
pcallcontext_generator.CALLSITE = (pgeneratorcreation.SITE)
$generator_creator_valid(S, pgeneratorcreation)
$generator_creation_scope_valid(S, pgeneratorcreation)
$generator_creation_record_valid(S, pgenerator)
$generator_creation_object_selected(S, n_generator, pcallcontext_generator)
S_view = $generator_frame_scope(S, pframe_generator)
$call_saved_context_valid(S_view, pframe_generator)
$generator_creation_selected(S_view, pcallcontext_generator.TARGET, pgeneratorcreation.SITE)
pgeneratorcreation_no_ancestor = pgeneratorcreation[.ANCESTORS = eps]
~$generator_creator_valid(S, pgeneratorcreation_no_ancestor)
pgenfactorycapture_missing = pgenfactorycapture[.CLOSURE = eps]
pgeneratorcreation_missing = pgeneratorcreation[.ANCESTORS = [pgenfactorycapture_missing]]
~$generator_creator_valid(S, pgeneratorcreation_missing)
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
''')

CASES = {
    'i78-retired-static-closure-scope': {
        'source': ROWS['i78-lexical-static-closure-factory']['source'],
        'stage': FRESH_STAGE,
        'checks': STATIC_CLOSURE,
    },
    'i78-bound-close-receiver': {
        'source': ROWS['i78-bound-instance-closure-factory']['source'],
        'stage': CLOSE_STAGE,
        'checks': BOUND_CLOSURE,
    },
    'i78-retired-temporary-call': {
        'source': ROWS['i78-temporary-call-closure-factory']['source'],
        'stage': RETIRED_STAGE,
        'checks': TEMPORARY_CALL,
    },
    'i78-closure-ancestor-stop': {
        'source': ROWS['i78-closure-method-bridge-dependency']['source'],
        'stage': FRESH_STAGE,
        'checks': ANCESTOR_CLOSURE,
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
