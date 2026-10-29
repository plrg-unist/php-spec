#!/usr/bin/env python3
"""Check finite keyword factory ancestry at source-reached Generator states."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_keyword_chain_cases.json')
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

CLOSE_SIBLING = checks(r'''
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
pgenclose.FRAME = (pframe_saved)
pgenclose.CONTEXT = pcallcontext_generator
S_select = $generator_close_frame_scope(S, pframe_saved)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base76A"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Mid76A"))) = (porigin_mid)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Leaf76A"))) = (porigin_leaf)
$class_method_origin(S.CLASSES, pgenerator.FUNCTION) = (pmethoddesc_body)
pmethoddesc_body.STATIC
pmethoddesc_body.VISIBILITY = PROPERTY_PROTECTED
pmethoddesc_body.OWNER = porigin_base
pgeneratorcreation.CREATOR.LEXICAL_CLASS = (porigin_mid)
pgeneratorcreation.CREATOR.CALLED_CLASS = (porigin_leaf)
$class_method_origin(S.CLASSES, pgeneratorcreation.CREATOR.FUNCTION) = (pmethoddesc_make)
pmethoddesc_make.OWNER = porigin_mid
pgeneratorcreation.CREATOR_TARGET = SCOPED_TARGET porigin_mid pgeneratorcreation.CREATOR.FUNCTION porigin_leaf eps poperand_make
pgeneratorcreation.ANCESTORS = [pgenfactorycapture]
pgenfactorycapture.CONTEXT.LEXICAL_CLASS = (porigin_leaf)
pgenfactorycapture.CONTEXT.CALLED_CLASS = (porigin_leaf)
$class_method_origin(S.CLASSES, pgenfactorycapture.CONTEXT.FUNCTION) = (pmethoddesc_outer)
pmethoddesc_outer.OWNER = porigin_leaf
pgenfactorycapture.TARGET = SCOPED_TARGET porigin_leaf pgenfactorycapture.CONTEXT.FUNCTION porigin_leaf eps poperand_outer
pgeneratorcreation.CALLEE = SCOPED_TARGET porigin_base pgenerator.FUNCTION porigin_leaf eps poperand_body
pcallcontext_generator.TARGET = pgeneratorcreation.CALLEE
pcallcontext_generator.CALLSITE = (pgeneratorcreation.SITE)
pcallcontext_generator.FUNCTION = pgenerator.FUNCTION
pcallcontext_generator.LEXICAL_CLASS = (porigin_base)
pcallcontext_generator.CALLED_CLASS = (porigin_leaf)
pcallcontext_generator.RECEIVER = eps
pcallcontext_generator.INSTANCE = eps
$generator_creator_valid(S, pgeneratorcreation)
$generator_creation_scope_valid(S, pgeneratorcreation)
$generator_creation_record_valid(S, pgenerator)
$generator_close_enter_valid(S, pgenclose)
$lookup(S.ENV, $ptascii("other")) = (n_other_cell)
S.STORE[n_other_cell] = DEFINED (POBJECT n_other)
n_other =/= pgenclose.OBJECT
S.OBJECTS[n_other] = GENERATOR pgenerator_other
pgenerator_other.PHASE = GENERATOR_FRESH
pgenerator_other.CREATION = (pgeneratorcreation_other)
pgeneratorcreation_other.ANCESTORS = [pgenfactorycapture_other]
pgenerator_other.FRAME = (pframe_other)
pframe_other.CONTEXT = (pcallcontext_other)
pcallcontext_other = pcallcontext_generator
pgenfactorycapture_other.CONTEXT.CALLSITE =/= pgenfactorycapture.CONTEXT.CALLSITE
$generator_creation_object_selected(S_select, n_other, pcallcontext_generator)
$generator_creation_close_owner(S_select) = (pgenclose.OBJECT)
$generator_creation_owner(S_select) = (pgenclose.OBJECT)
$generator_creation_selected(S_select, pcallcontext_generator.TARGET, pgeneratorcreation.SITE)
pgeneratorcreation_no_chain = pgeneratorcreation[.ANCESTORS = eps]
~$generator_creator_valid(S, pgeneratorcreation_no_chain)
S_missing = S_select[.OBJECTS = $object_set(S_select.OBJECTS, pgenclose.OBJECT, GENERATOR pgenerator[.CREATION = (pgeneratorcreation_no_chain)])]
$generator_creation_owner(S_missing) = (pgenclose.OBJECT)
$generator_creation_object_selected(S_missing, n_other, pcallcontext_generator)
~$generator_creation_selected(S_missing, pcallcontext_generator.TARGET, pgeneratorcreation.SITE)
pgenfactorycapture_wrong_target = pgenfactorycapture[.TARGET = SCOPED_TARGET porigin_leaf pgeneratorcreation.CREATOR.FUNCTION porigin_leaf eps (KNOWN (PSTRING ($ptascii("Leaf76A"))))]
$target_function(S, pgenfactorycapture_wrong_target.TARGET) = (pmethoddesc_make.FUNCTION)
pgeneratorcreation_wrong_target = pgeneratorcreation[.ANCESTORS = [pgenfactorycapture_wrong_target]]
~$generator_creator_valid(S, pgeneratorcreation_wrong_target)
pgeneratorcreation_wrong_forward = pgeneratorcreation[.CREATOR = pgeneratorcreation.CREATOR[.CALLED_CLASS = (porigin_mid)]][.CREATOR_TARGET = SCOPED_TARGET porigin_mid pgeneratorcreation.CREATOR.FUNCTION porigin_mid eps poperand_make][.CALLEE = SCOPED_TARGET porigin_base pgenerator.FUNCTION porigin_mid eps poperand_body]
$target_function(S, pgeneratorcreation_wrong_forward.CREATOR_TARGET) = (pmethoddesc_make.FUNCTION)
$target_function(S, pgeneratorcreation_wrong_forward.CALLEE) = (pmethoddesc_body.FUNCTION)
~$generator_creator_valid(S, pgeneratorcreation_wrong_forward)
~$generator_creation_scope_valid(S, pgeneratorcreation_wrong_forward)
S_unallocated = S_select[.ALLOCATIONS = $destruction_node_delete(S_select.ALLOCATIONS, HOBJECT pgenclose.OBJECT)]
$generator_creation_owner(S_unallocated) = (pgenclose.OBJECT)
~$generator_creation_selected(S_unallocated, pcallcontext_generator.TARGET, pgeneratorcreation.SITE)
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
''')

DEEP_STAGE = (
    'S.FRAMES = pframe_resume :: pframe_tail* '
    '-- if pframe_resume.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_resume* '
    '-- if pgeneratorop.NAME = "next" '
    '-- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator '
    '-- if pgenerator.VALUE = (PINT 8) '
    '-- if pgenerator.CREATION = (pgeneratorcreation)')

DEEP_CACHE = checks(r'''
S.COMPLETION = NORMAL
S.CURRENT = (pcallcontext_generator)
pgenerator.PHASE = GENERATOR_RUNNING
~pgenerator.FIRST
pgenerator.REFCELL = eps
pgeneratorcreation.ANCESTORS = [pgenfactorycapture_mid, pgenfactorycapture_leaf, pgenfactorycapture_outer]
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base76B"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Mid76B"))) = (porigin_mid)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Leaf76B"))) = (porigin_leaf)
pgeneratorcreation.CREATOR.LEXICAL_CLASS = (porigin_base)
pgeneratorcreation.CREATOR.CALLED_CLASS = (porigin_leaf)
pgenfactorycapture_mid.CONTEXT.LEXICAL_CLASS = (porigin_mid)
pgenfactorycapture_mid.CONTEXT.CALLED_CLASS = (porigin_leaf)
pgenfactorycapture_leaf.CONTEXT.LEXICAL_CLASS = (porigin_leaf)
pgenfactorycapture_leaf.CONTEXT.CALLED_CLASS = (porigin_leaf)
pgenfactorycapture_outer.CONTEXT.LEXICAL_CLASS = (porigin_leaf)
pgenfactorycapture_outer.CONTEXT.CALLED_CLASS = (porigin_leaf)
$class_method_origin(S.CLASSES, pgeneratorcreation.CREATOR.FUNCTION) = (pmethoddesc_step)
$class_method_origin(S.CLASSES, pgenfactorycapture_mid.CONTEXT.FUNCTION) = (pmethoddesc_mid)
$class_method_origin(S.CLASSES, pgenfactorycapture_leaf.CONTEXT.FUNCTION) = (pmethoddesc_leaf)
$class_method_origin(S.CLASSES, pgenfactorycapture_outer.CONTEXT.FUNCTION) = (pmethoddesc_outer)
pmethoddesc_step.OWNER = porigin_base
pmethoddesc_mid.OWNER = porigin_mid
pmethoddesc_leaf.OWNER = porigin_leaf
pmethoddesc_outer.OWNER = porigin_leaf
pcallcontext_generator.TARGET = pgeneratorcreation.CALLEE
pcallcontext_generator.CALLSITE = (pgeneratorcreation.SITE)
pcallcontext_generator.FUNCTION = pgenerator.FUNCTION
pcallcontext_generator.LEXICAL_CLASS = (porigin_base)
pcallcontext_generator.CALLED_CLASS = (porigin_leaf)
pcallcontext_generator.INSTANCE = eps
pcallcontext_generator.RECEIVER = eps
$lookup(S.ENV, $ptascii("slot")) = (n_slot)
n_slot <- S.REFCELLS
S.STORE[n_slot] = DEFINED (PINT 11)
$heap_owners($heap_graph(S), HCELL n_slot) = 2
$generator_creator_valid(S, pgeneratorcreation)
$generator_creation_scope_valid(S, pgeneratorcreation)
$generator_creation_record_valid(S, pgenerator)
$generator_creation_owner(S) = (pgeneratorop.OBJECT)
$generator_creation_selected(S, pcallcontext_generator.TARGET, pgeneratorcreation.SITE)
$call_current_valid(S)
pgeneratorcreation_dropped = pgeneratorcreation[.ANCESTORS = [pgenfactorycapture_mid, pgenfactorycapture_outer]]
~$generator_creator_valid(S, pgeneratorcreation_dropped)
pgeneratorcreation_swapped = pgeneratorcreation[.ANCESTORS = [pgenfactorycapture_leaf, pgenfactorycapture_mid, pgenfactorycapture_outer]]
~$generator_creator_valid(S, pgeneratorcreation_swapped)
pgeneratorcreation_extra = pgeneratorcreation[.ANCESTORS = [pgenfactorycapture_mid, pgenfactorycapture_leaf, pgenfactorycapture_outer, pgenfactorycapture_outer]]
~$generator_creator_valid(S, pgeneratorcreation_extra)
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
''')

RETIRED_STAGE = (
    'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
    '-- if pconfigcall.KIND = INTRINSIC_WEAKREF_GET '
    '-- if $lookup(S.ENV, $ptascii("g")) = (n_generator_cell) '
    '-- if S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator) '
    '-- if S.OBJECTS[n_generator] = GENERATOR pgenerator '
    '-- if pgenerator.PHASE = GENERATOR_FRESH')

RETIRED_ROOT = checks(r'''
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
pgenerator.CREATION = (pgeneratorcreation)
pgeneratorcreation.ANCESTORS = [pgenfactorycapture]
$class_named(S.CLASSNAMES, $ptlc($ptascii("Maker76C"))) = (porigin_maker)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Leaf76C"))) = (porigin_leaf)
pgeneratorcreation.CREATOR.LEXICAL_CLASS = (porigin_maker)
pgeneratorcreation.CREATOR.CALLED_CLASS = (porigin_leaf)
pgenfactorycapture.CONTEXT.LEXICAL_CLASS = (porigin_maker)
pgenfactorycapture.CONTEXT.CALLED_CLASS = (porigin_leaf)
pgenfactorycapture.TARGET = METHOD_TARGET n_maker pgenfactorycapture.CONTEXT.FUNCTION
$lookup(S.ENV, $ptascii("weakMaker")) = (n_weak_cell)
S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)
S.OBJECTS[n_weak] = WEAKREFERENCE (n_maker)
$weakref_get(S, n_weak) = PNULL
~((HOBJECT n_maker) <- S.ALLOCATIONS)
$object_body(S.OBJECTS[n_maker]) = INSTANCE porigin_leaf
$target_function(S, pgenfactorycapture.TARGET) = eps
~((HOBJECT n_maker) <- $node_children(S, HOBJECT n_generator))
$lookup(S.ENV, $ptascii("input")) = (n_input)
S.STORE[n_input] = DEFINED (PINT 9)
pgenerator.FRAME = (pframe_generator)
pframe_generator.LOCALS = (psymboltable_generator)
$lookup(psymboltable_generator.ENV, $ptascii("item")) = (n_item)
S.STORE[n_item] = DEFINED (PINT 5)
pframe_generator.CONTEXT = (pcallcontext_generator)
pcallcontext_generator.TARGET = pgeneratorcreation.CALLEE
pcallcontext_generator.CALLSITE = (pgeneratorcreation.SITE)
pcallcontext_generator.FUNCTION = pgenerator.FUNCTION
pcallcontext_generator.INSTANCE = eps
pcallcontext_generator.RECEIVER = eps
$call_context_roots((pcallcontext_generator)) = eps
$generator_creator_valid(S, pgeneratorcreation)
$generator_creation_scope_valid(S, pgeneratorcreation)
$generator_creation_record_valid(S, pgenerator)
$generator_creation_object_selected(S, n_generator, pcallcontext_generator)
S_view = $generator_frame_scope(S, pframe_generator)
$generator_creation_owner(S_view) = eps
$generator_creation_selected(S_view, pcallcontext_generator.TARGET, pgeneratorcreation.SITE)
$call_current_valid(S_view)
pgeneratorcreation_no_chain = pgeneratorcreation[.ANCESTORS = eps]
~$generator_creator_valid(S, pgeneratorcreation_no_chain)
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
''')

CASES = {
    'i76-parent-close-actual-owner-sibling': {
        'source': ROWS['i76-parent-two-link-fresh-sibling-close']['source'],
        'stage': CLOSE_STAGE,
        'checks': CLOSE_SIBLING,
    },
    'i76-deep-three-ancestor-cache': {
        'source': ROWS['i76-deep-static-override-reference-cache']['source'],
        'stage': DEEP_STAGE,
        'checks': DEEP_CACHE,
    },
    'i76-retired-instance-root-borrowed-history': {
        'source': ROWS['i76-retired-instance-root-static-leaf']['source'],
        'stage': RETIRED_STAGE,
        'checks': RETIRED_ROOT,
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
