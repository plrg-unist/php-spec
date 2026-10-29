#!/usr/bin/env python3
"""Check source-reached array/string method factory Generator authority."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_array_string_factory_cases.json')
INPUT_BYTES = {path: path.read_bytes() for path in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


CLOSE_SIBLING_STAGE = (
    'S.TODO = (GENERATOR_CLOSE_ENTER pgenclose) :: ptask_tail* '
    '-- if S.OBJECTS[pgenclose.OBJECT] = GENERATOR pgenerator '
    '-- if pgenerator.CREATION = (pgeneratorcreation) '
    '-- if $lookup(S.ENV, $ptascii("other")) = (n_other_cell) '
    '-- if S.STORE[n_other_cell] = DEFINED (POBJECT n_other) '
    '-- if S.OBJECTS[n_other] = GENERATOR pgenerator_other '
    '-- if pgenerator_other.PHASE = GENERATOR_FRESH '
    '-- if pgenerator_other.CREATION = (pgeneratorcreation_other)')

ARRAY_CLOSE_SIBLING = checks(r'''
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
pgenclose.FRAME = (pframe_generator)
pgenclose.CONTEXT = pcallcontext_generator
n_generator = pgenclose.OBJECT
S_view = $generator_close_frame_scope(S, pframe_generator)
pgenerator.CLOSURE = eps
pgeneratorcreation.CLOSURE = (CLOSURE_SCOPE pclosurescope)
pgeneratorcreation_other.CLOSURE = (CLOSURE_SCOPE pclosurescope_other)
pgeneratorcreation.ANCESTORS = eps
pgeneratorcreation_other.ANCESTORS = eps
pgeneratorcreation.CALLEE = SCOPED_TARGET porigin_mid pgenerator.FUNCTION porigin_leaf eps poperand_body
pgeneratorcreation_other.CALLEE = pgeneratorcreation.CALLEE
pgeneratorcreation_other.SITE = pgeneratorcreation.SITE
pcallcontext_generator.TARGET = pgeneratorcreation.CALLEE
pcallcontext_generator.CALLSITE = (pgeneratorcreation.SITE)
pgenerator_other.FRAME = (pframe_other)
pframe_other.CONTEXT = (pcallcontext_generator)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Mid81A"))) = (porigin_mid)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Leaf81A"))) = (porigin_leaf)
pclosurescope.LEXICAL = porigin_mid
pclosurescope.CALLED = porigin_leaf
pclosurescope.RECEIVER = (n_maker)
pclosurescope_other.LEXICAL = porigin_mid
pclosurescope_other.CALLED = porigin_leaf
pclosurescope_other.RECEIVER = (n_maker)
S.OBJECTS[n_maker] = INSTANCE porigin_leaf
~((HOBJECT n_maker) <- S.ALLOCATIONS)
n_factory = pclosurescope.OBJECT
n_factory_other = pclosurescope_other.OBJECT
S.OBJECTS[n_factory] = ARRAYMETHODCLOSURE pcalltarget_factory parrayselection_factory pmethodcapture_factory?
S.OBJECTS[n_factory_other] = ARRAYMETHODCLOSURE pcalltarget_factory_other parrayselection_factory_other pmethodcapture_factory_other?
$lookup(S.ENV, $ptascii("callback")) = eps
$lookup(S.ENV, $ptascii("receiver")) = eps
$lookup(S.ENV, $ptascii("method")) = eps
~$closure_scope_row_valid(S, pclosurescope)
~$array_target_identity(S, pcalltarget_factory, parrayselection_factory)
S_lookup = S[.ALLOCATIONS = S.ALLOCATIONS ++ [HOBJECT n_factory, HOBJECT n_maker]]
$closure_scope_row_valid(S_lookup, pclosurescope)
$array_target_identity(S_lookup, pcalltarget_factory, parrayselection_factory)
$target_function(S_lookup, pcalltarget_factory) = (pfunction_factory)
pfunction_factory.ORIGIN = pgeneratorcreation.CREATOR.FUNCTION
n_factory =/= n_factory_other
pgeneratorcreation.CREATOR_TARGET = CLOSURE_TARGET n_factory
pgeneratorcreation_other.CREATOR_TARGET = CLOSURE_TARGET n_factory_other
~((HOBJECT n_factory) <- S.ALLOCATIONS)
~((HOBJECT n_factory_other) <- S.ALLOCATIONS)
~$closure_evidence_valid(S, CLOSURE_SCOPE pclosurescope)
~$closure_evidence_valid(S, CLOSURE_SCOPE pclosurescope_other)
~$closure_callable(S, n_factory)
~$closure_callable(S, n_factory_other)
$generator_captured_factory_valid(S, pclosurescope, pgeneratorcreation.CREATOR.FUNCTION)
$generator_captured_factory_valid(S, pclosurescope_other, pgeneratorcreation_other.CREATOR.FUNCTION)
$generator_creator_closure_target(S, pgeneratorcreation.CREATOR_TARGET, pgeneratorcreation.CREATOR, CLOSURE_SCOPE pclosurescope)
$generator_creator_closure_target(S, pgeneratorcreation_other.CREATOR_TARGET, pgeneratorcreation_other.CREATOR, CLOSURE_SCOPE pclosurescope_other)
$lookup(S.ENV, $ptascii("weakMaker")) = (n_weak_maker_cell)
S.STORE[n_weak_maker_cell] = DEFINED (POBJECT n_weak_maker)
S.OBJECTS[n_weak_maker] = WEAKREFERENCE (n_maker)
$weakref_get(S, n_weak_maker) = PNULL
$heap_count(HOBJECT n_maker, $node_children(S, HOBJECT n_generator)) = 0
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
~$generator_captured_factory_valid(S, pclosurescope, pgenerator.FUNCTION)
parrayselection_wrong_name = parrayselection_factory[.NAME = $ptascii("body")]
S_wrong_name = S[.OBJECTS = $object_set(S.OBJECTS, n_factory, ARRAYMETHODCLOSURE pcalltarget_factory parrayselection_wrong_name pmethodcapture_factory?)]
~$generator_captured_factory_valid(S_wrong_name, pclosurescope, pgeneratorcreation.CREATOR.FUNCTION)
S_recursive = S[.OBJECTS = $object_set(S.OBJECTS, n_factory, ARRAYMETHODCLOSURE (CLOSURE_TARGET n_factory) parrayselection_factory pmethodcapture_factory?)]
~$generator_captured_factory_valid(S_recursive, pclosurescope, pgeneratorcreation.CREATOR.FUNCTION)
pclosurescope_wrong_receiver = pclosurescope[.RECEIVER = eps]
~$generator_captured_factory_valid(S, pclosurescope_wrong_receiver, pgeneratorcreation.CREATOR.FUNCTION)
pgeneratorcreation_wrong_receiver = pgeneratorcreation[.CLOSURE = (CLOSURE_SCOPE pclosurescope_wrong_receiver)]
~$generator_creator_valid(S, pgeneratorcreation_wrong_receiver)
pclosurescope_wrong_lexical = pclosurescope[.LEXICAL = porigin_leaf]
~$generator_captured_factory_valid(S, pclosurescope_wrong_lexical, pgeneratorcreation.CREATOR.FUNCTION)
pgeneratorcreation_wrong_factory = pgeneratorcreation[.CLOSURE = (CLOSURE_SCOPE pclosurescope_other)]
~$generator_creator_valid(S, pgeneratorcreation_wrong_factory)
pgenerator_missing = pgenerator[.CREATION = eps]
S_missing = S_view[.OBJECTS = $object_set(S_view.OBJECTS, pgenclose.OBJECT, GENERATOR pgenerator_missing)]
$generator_creation_owner(S_missing) = (pgenclose.OBJECT)
$generator_creation_object_selected(S_missing, n_other, pcallcontext_generator)
~$generator_creation_selected(S_missing, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
~$call_current_valid(S_missing)
''')

CLOSE_STAGE = (
    'S.TODO = (GENERATOR_CLOSE_ENTER pgenclose) :: ptask_tail* '
    '-- if S.OBJECTS[pgenclose.OBJECT] = GENERATOR pgenerator '
    '-- if pgenerator.CREATION = (pgeneratorcreation)')

ARRAY_CLOSE = checks(r'''
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
pgenclose.FRAME = (pframe_generator)
pgenclose.CONTEXT = pcallcontext_generator
S_view = $generator_close_frame_scope(S, pframe_generator)
pgenerator.CLOSURE = eps
pgeneratorcreation.CLOSURE = (CLOSURE_SCOPE pclosurescope)
pgeneratorcreation.ANCESTORS = eps
n_factory = pclosurescope.OBJECT
pgeneratorcreation.CREATOR_TARGET = CLOSURE_TARGET n_factory
S.OBJECTS[n_factory] = ARRAYMETHODCLOSURE pcalltarget_factory parrayselection_factory pmethodcapture_factory?
$target_function(S, pcalltarget_factory) = (pfunction_factory)
pfunction_factory.ORIGIN = pgeneratorcreation.CREATOR.FUNCTION
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base81B"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Mid81B"))) = (porigin_mid)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Leaf81B"))) = (porigin_leaf)
pclosurescope.LEXICAL = porigin_mid
pclosurescope.CALLED = porigin_leaf
pclosurescope.RECEIVER = (n_maker)
S.OBJECTS[n_maker] = INSTANCE porigin_leaf
(HOBJECT n_maker) <- S.ALLOCATIONS
~((HOBJECT n_factory) <- S.ALLOCATIONS)
$lookup(S.ENV, $ptascii("weakFactory")) = (n_weak_factory_cell)
S.STORE[n_weak_factory_cell] = DEFINED (POBJECT n_weak_factory)
S.OBJECTS[n_weak_factory] = WEAKREFERENCE (n_factory)
$weakref_get(S, n_weak_factory) = PNULL
pgeneratorcreation.CALLEE = SCOPED_TARGET porigin_base pgenerator.FUNCTION porigin_leaf (n_maker) poperand_body
pcallcontext_generator.TARGET = pgeneratorcreation.CALLEE
pcallcontext_generator.CALLSITE = (pgeneratorcreation.SITE)
pcallcontext_generator.RECEIVER = (n_maker)
$call_context_roots((pcallcontext_generator)) = [HOBJECT n_maker]
$lookup(S.ENV, $ptascii("callback")) = eps
~$closure_scope_row_valid(S, pclosurescope)
$array_site_valid(S, parrayselection_factory, true)
$array_target_identity(S, pcalltarget_factory, parrayselection_factory)
~$generator_captured_factory_valid(S, pclosurescope, pgenerator.FUNCTION)
$heap_count(HOBJECT n_maker, $task_nodes(GENERATOR_CLOSE_ENTER pgenclose)) = 1
~$closure_evidence_valid(S, CLOSURE_SCOPE pclosurescope)
$generator_captured_factory_valid(S, pclosurescope, pgeneratorcreation.CREATOR.FUNCTION)
$generator_creator_closure_target(S, pgeneratorcreation.CREATOR_TARGET, pgeneratorcreation.CREATOR, CLOSURE_SCOPE pclosurescope)
$generator_creator_receiver(S, pgeneratorcreation.CREATOR_TARGET, pgeneratorcreation.CLOSURE) = (n_maker)
$generator_creator_valid(S, pgeneratorcreation)
$generator_creation_scope_valid(S, pgeneratorcreation)
$generator_creation_record_valid(S, pgenerator)
$generator_close_enter_valid(S, pgenclose)
$generator_creation_owner(S_view) = (pgenclose.OBJECT)
$generator_creation_selected(S_view, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
pgeneratorcreation_wrong_target = pgeneratorcreation[.CREATOR_TARGET = CLOSURE_TARGET n_maker]
~$generator_creator_valid(S, pgeneratorcreation_wrong_target)
pclosurescope_wrong_receiver = pclosurescope[.RECEIVER = eps]
~$generator_captured_factory_valid(S, pclosurescope_wrong_receiver, pgeneratorcreation.CREATOR.FUNCTION)
pgeneratorcreation_wrong_receiver = pgeneratorcreation[.CLOSURE = (CLOSURE_SCOPE pclosurescope_wrong_receiver)]
~$generator_creator_valid(S, pgeneratorcreation_wrong_receiver)
pgenerator_missing = pgenerator[.CREATION = eps]
S_missing = S_view[.OBJECTS = $object_set(S_view.OBJECTS, pgenclose.OBJECT, GENERATOR pgenerator_missing)]
$generator_creation_owner(S_missing) = (pgenclose.OBJECT)
~$generator_creation_selected(S_missing, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
''')

FRESH_STAGE = (
    'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
    '-- if pconfigcall.KIND = INTRINSIC_WEAKREF_GET '
    '-- if $lookup(S.ENV, $ptascii("g")) = (n_generator_cell) '
    '-- if S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator) '
    '-- if S.OBJECTS[n_generator] = GENERATOR pgenerator '
    '-- if pgenerator.PHASE = GENERATOR_FRESH '
    '-- if pgenerator.CREATION = (pgeneratorcreation)')

STRING_LATE_STATIC = checks(r'''
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
S.OBJECTS[n_factory] = STRINGMETHODCLOSURE pcalltarget_factory pstringselection_factory
$target_function(S, pcalltarget_factory) = (pfunction_factory)
pfunction_factory.ORIGIN = pgeneratorcreation.CREATOR.FUNCTION
$class_named(S.CLASSNAMES, $ptlc($ptascii("Mid81C"))) = (porigin_mid)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Leaf81C"))) = (porigin_leaf)
pclosurescope.LEXICAL = porigin_mid
pclosurescope.CALLED = porigin_leaf
pclosurescope.RECEIVER = eps
$lookup(S.ENV, $ptascii("name")) = eps
pstringselection_factory.ORIGINAL = $ptascii("Leaf81C::make")
pstringselection_factory.REQUESTED = porigin_leaf
$string_site_valid(S, pstringselection_factory, true)
$string_target_identity(S, pcalltarget_factory, pstringselection_factory)
~$closure_scope_row_valid(S, pclosurescope)
~$generator_captured_factory_valid(S, pclosurescope, pgenerator.FUNCTION)
~((HOBJECT n_factory) <- S.ALLOCATIONS)
$lookup(S.ENV, $ptascii("weakFactory")) = (n_weak_factory_cell)
S.STORE[n_weak_factory_cell] = DEFINED (POBJECT n_weak_factory)
S.OBJECTS[n_weak_factory] = WEAKREFERENCE (n_factory)
$weakref_get(S, n_weak_factory) = PNULL
$heap_count(HOBJECT n_factory, $node_children(S, HOBJECT n_generator)) = 0
~$closure_evidence_valid(S, CLOSURE_SCOPE pclosurescope)
$generator_captured_factory_valid(S, pclosurescope, pgeneratorcreation.CREATOR.FUNCTION)
pgeneratorcreation.CALLEE = SCOPED_TARGET porigin_leaf pgenerator.FUNCTION porigin_leaf eps poperand_body
pcallcontext_generator.TARGET = pgeneratorcreation.CALLEE
pcallcontext_generator.CALLSITE = (pgeneratorcreation.SITE)
pcallcontext_generator.RECEIVER = eps
$generator_creator_valid(S, pgeneratorcreation)
$generator_creation_scope_valid(S, pgeneratorcreation)
$generator_creation_record_valid(S, pgenerator)
$generator_creation_object_selected(S, n_generator, pcallcontext_generator)
S_view = $generator_frame_scope(S, pframe_generator)
$call_saved_context_valid(S_view, pframe_generator)
$generator_creation_selected(S_view, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
$effective_method(S, porigin_mid, $ptascii("body"), |S.CLASSES|) = (pmethoddesc_mid_body)
pgeneratorcreation_wrong_selection = pgeneratorcreation[.CALLEE = SCOPED_TARGET porigin_mid pmethoddesc_mid_body.FUNCTION.ORIGIN porigin_mid eps (KNOWN (PSTRING ($ptascii("Mid81C"))))]
$target_function(S, pgeneratorcreation_wrong_selection.CALLEE) = (pmethoddesc_mid_body.FUNCTION)
$generator_creator_valid(S, pgeneratorcreation_wrong_selection)
~$generator_creation_scope_valid(S, pgeneratorcreation_wrong_selection)
pgeneratorcreation_wrong_called = pgeneratorcreation[.CREATOR = pgeneratorcreation.CREATOR[.CALLED_CLASS = (porigin_mid)]]
~$generator_creator_valid(S, pgeneratorcreation_wrong_called)
pstringselection_wrong_name = pstringselection_factory[.ORIGINAL = $ptascii("Mid81C::make")]
S_wrong_name = S[.OBJECTS = $object_set(S.OBJECTS, n_factory, STRINGMETHODCLOSURE pcalltarget_factory pstringselection_wrong_name)]
~$generator_captured_factory_valid(S_wrong_name, pclosurescope, pgeneratorcreation.CREATOR.FUNCTION)
pstringselection_wrong_site = pstringselection_factory[.SITE = pgeneratorcreation.SITE]
S_wrong_site = S[.OBJECTS = $object_set(S.OBJECTS, n_factory, STRINGMETHODCLOSURE pcalltarget_factory pstringselection_wrong_site)]
~$generator_captured_factory_valid(S_wrong_site, pclosurescope, pgeneratorcreation.CREATOR.FUNCTION)
pclosurescope_wrong_called = pclosurescope[.CALLED = porigin_mid]
~$generator_captured_factory_valid(S, pclosurescope_wrong_called, pgeneratorcreation.CREATOR.FUNCTION)
pgenerator_missing = pgenerator[.CREATION = eps]
S_missing = $generator_set(S_view, n_generator, pgenerator_missing)
~$generator_creation_selected(S_missing, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
~$call_saved_context_valid(S_missing, pframe_generator)
''')

CASES = {
    'i81-array-close-sibling': {'source': ROWS['i81-array-static-sibling']['source'], 'stage': CLOSE_SIBLING_STAGE, 'checks': ARRAY_CLOSE_SIBLING},
    'i81-array-close': {'source': ROWS['i81-array-protected-close']['source'], 'stage': CLOSE_STAGE, 'checks': ARRAY_CLOSE},
    'i81-string-late-static': {'source': ROWS['i81-string-late-static']['source'], 'stage': FRESH_STAGE, 'checks': STRING_LATE_STATIC},
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
