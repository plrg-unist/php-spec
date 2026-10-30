#!/usr/bin/env python3
"""Check direct magic entry, receiver rebinding and completed packed payloads."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_direct_magic_cases.json')
INPUT_BYTES = {path: path.read_bytes() for path in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


FRESH_STAGE = (
    'S.TODO = (GENERATOR_ARGS pgeneratorop eps eps) :: ptask_tail* '
    '-- if pgeneratorop.NAME = "current" '
    '-- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator '
    '-- if pgenerator.PHASE = GENERATOR_FRESH '
    '-- if pgenerator.CREATION = (pgeneratorcreation)')

FRESH = checks(r"""
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
pgenerator.FRAME = (pframe_generator)
pframe_generator.CONTEXT = (pcallcontext_generator)
pframe_generator.LOCALS = (psymboltable)
pgenerator.VALUE = eps
pgenerator.CLOSURE = eps
pgeneratorcreation.CLOSURE = eps
pgeneratorcreation.ANCESTORS = eps
pgeneratorcreation.CALLEE = MAGIC_METHOD_TARGET pmagicmethodcall n_arguments ([PINT 85])
pgeneratorcreation.CREATOR_TARGET = pgeneratorcreation.CALLEE
pgeneratorcreation.SITE = pmagicmethodcall.SITE
pgeneratorcreation.CREATOR.FUNCTION = pmagicmethodcall.METHOD
pgeneratorcreation.CREATOR.CALLSITE = (pmagicmethodcall.SITE)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base85A"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Child85A"))) = (porigin_child)
pgeneratorcreation.CREATOR.LEXICAL_CLASS = (porigin_base)
pgeneratorcreation.CREATOR.CALLED_CLASS = (porigin_child)
pmagicmethodcall.CLASS = porigin_child
pmagicmethodcall.OBJECT = n_maker
pmagicmethodcall.NAME = $ptascii("open")
pmagicmethodcall.CALLER = eps
pmagicmethodcall.OWNER = 0
S.OBJECTS[n_maker] = INSTANCE porigin_child
(HOBJECT n_maker) <- S.ALLOCATIONS
(HARRAY n_arguments) <- S.ALLOCATIONS
S.ARRAYS[n_arguments].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 85))]
$lookup(S.ENV, $ptascii("maker")) = eps
$lookup(psymboltable.ENV, $ptascii("arguments")) = (n_arguments_cell)
S.STORE[n_arguments_cell] = DEFINED (PARRAY n_arguments)
pcallcontext_generator.TARGET = pgeneratorcreation.CALLEE
pcallcontext_generator.FUNCTION = pgenerator.FUNCTION
pcallcontext_generator.RECEIVER = (n_maker)
pcallcontext_generator.LEXICAL_CLASS = (porigin_base)
pcallcontext_generator.CALLED_CLASS = (porigin_child)
$magic_method_descriptor(S, pmagicmethodcall)
~$magic_method_entered(S, S.CURRENT, S.FRAMES, pmagicmethodcall, n_arguments, [PINT 85])
$target_function(S, pgeneratorcreation.CALLEE) = eps
~$generator_creator_valid(S, pgeneratorcreation)
$generator_creation_scope_valid(S, pgeneratorcreation)
$generator_creation_record_valid(S, pgenerator)
H = $heap_graph(S)
$heap_valid(H)
$heap_owners(H, HOBJECT n_maker) = 1
$heap_owners(H, HARRAY n_arguments) = 1
S_view = $generator_frame_scope(S, pframe_generator)
$generator_creation_required(S_view, pcallcontext_generator)
$generator_creation_owner(S_view) = eps
$generator_creation_selected(S_view, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
$generator_magic_context_valid(S_view, pcallcontext_generator)
$magic_method_entered(S_view, S_view.CURRENT, S_view.FRAMES, pmagicmethodcall, n_arguments, [PINT 85])
$generator_creation_supported(S_view, pcallcontext_generator)
$call_current_valid(S_view)
$call_saved_context_valid(S_view, pframe_generator)
pcallcontext_bad_lexical = pcallcontext_generator[.LEXICAL_CLASS = (porigin_child)]
S_bad_lexical = S_view[.CURRENT = (pcallcontext_bad_lexical)]
~$generator_magic_context_valid(S_bad_lexical, pcallcontext_bad_lexical)
pcallcontext_bad_called = pcallcontext_generator[.CALLED_CLASS = (porigin_base)]
S_bad_called = S_view[.CURRENT = (pcallcontext_bad_called)]
~$generator_magic_context_valid(S_bad_called, pcallcontext_bad_called)
pcallcontext_bad_line = pcallcontext_generator[.LINE = $(-1)]
S_bad_line = S_view[.CURRENT = (pcallcontext_bad_line)]
~$generator_magic_context_valid(S_bad_line, pcallcontext_bad_line)
S_dead_receiver = S_view[.ALLOCATIONS = $destruction_node_delete(S_view.ALLOCATIONS, HOBJECT n_maker)]
$generator_creation_record_valid(S_dead_receiver, pgenerator)
$generator_creation_selected(S_dead_receiver, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
~$generator_magic_context_valid(S_dead_receiver, pcallcontext_generator)
$target_function(S_dead_receiver, pgeneratorcreation.CALLEE) = eps
pgenerator_missing = pgenerator[.CREATION = eps]
S_missing = $generator_set(S_view, pgeneratorop.OBJECT, pgenerator_missing)
~$generator_creation_selected(S_missing, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
~$generator_magic_context_valid(S_missing, pcallcontext_generator)
$generator_creation_capture(S_missing, pcallcontext_generator) = eps
n_unbounded_array = |S.ARRAYS|
pcalltarget_unbounded = MAGIC_METHOD_TARGET pmagicmethodcall n_unbounded_array ([PINT 85])
pgeneratorcreation_unbounded = pgeneratorcreation[.CALLEE = pcalltarget_unbounded][.CREATOR_TARGET = pcalltarget_unbounded]
~$generator_creation_scope_valid(S, pgeneratorcreation_unbounded)
pcalltarget_bad_count = MAGIC_METHOD_TARGET pmagicmethodcall n_arguments eps
pgeneratorcreation_bad_count = pgeneratorcreation[.CALLEE = pcalltarget_bad_count][.CREATOR_TARGET = pcalltarget_bad_count]
~$generator_creation_scope_valid(S, pgeneratorcreation_bad_count)
pgeneratorcreation_bad_lexical = pgeneratorcreation[.CREATOR = pgeneratorcreation.CREATOR[.LEXICAL_CLASS = (porigin_child)]]
~$generator_creation_scope_valid(S, pgeneratorcreation_bad_lexical)
$call_descriptors_valid(S)
""")

COMPLETED_STAGE = (
    'S.TODO = (GENERATOR_ARGS pgeneratorop eps eps) :: ptask_tail* '
    '-- if pgeneratorop.NAME = "getreturn" '
    '-- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator '
    '-- if pgenerator.PHASE = GENERATOR_CLOSED '
    '-- if pgenerator.CREATION = (pgeneratorcreation)')

COMPLETED = checks(r"""
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
(HOBJECT pgeneratorop.OBJECT) <- S.ALLOCATIONS
pgenerator.FRAME = eps
pgenerator.CLOSURE = eps
pgenerator.RETURN = (PINT 86)
pgeneratorcreation.CLOSURE = eps
pgeneratorcreation.ANCESTORS = eps
pgeneratorcreation.CALLEE = MAGIC_STATIC_METHOD_TARGET pmagicstaticmethodcall n_arguments ([POBJECT n_payload])
pgeneratorcreation.CREATOR_TARGET = pgeneratorcreation.CALLEE
pgeneratorcreation.CREATOR.FUNCTION = pmagicstaticmethodcall.METHOD
pgeneratorcreation.CREATOR.CALLSITE = (pmagicstaticmethodcall.SITE)
pgeneratorcreation.SITE = pmagicstaticmethodcall.SITE
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base85B"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Child85B"))) = (porigin_child)
pgeneratorcreation.CREATOR.LEXICAL_CLASS = (porigin_base)
pgeneratorcreation.CREATOR.CALLED_CLASS = (porigin_child)
pmagicstaticmethodcall.CLASS = porigin_child
pmagicstaticmethodcall.NAME = $ptascii("open")
pmagicstaticmethodcall.CALLER = eps
pmagicstaticmethodcall.OWNER = 0
$(n_arguments < |S.ARRAYS|)
~((HARRAY n_arguments) <- S.ALLOCATIONS)
~((HOBJECT n_payload) <- S.ALLOCATIONS)
n_payload <- S.DESTRUCTION.CALLED
$object_name(S, n_payload) = $ptascii("Payload85B")
H = $heap_graph(S)
$heap_owners(H, HARRAY n_arguments) = 0
$heap_owners(H, HOBJECT n_payload) = 0
$heap_count(HOBJECT n_payload, $node_children(S, HOBJECT pgeneratorop.OBJECT)) = 0
$lookup(S.ENV, $ptascii("weakPayload")) = (n_weak_cell)
S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)
$weakref_get(S, n_weak) = PNULL
$magic_static_method_descriptor(S, pmagicstaticmethodcall)
~$magic_static_method_pending(S, pmagicstaticmethodcall, n_arguments, [POBJECT n_payload])
~$magic_static_method_entered(S, S.CURRENT, S.FRAMES, pmagicstaticmethodcall, n_arguments, [POBJECT n_payload])
$target_function(S, pgeneratorcreation.CALLEE) = eps
$effective_method(S, porigin_child, $ptascii("__callstatic"), |S.CLASSES|) = (pmethoddesc)
pmethoddesc.OWNER = porigin_base
pmethoddesc.STATIC
$function_generator(S, pmethoddesc.FUNCTION)
$target_function(S, STATIC_METHOD_TARGET porigin_child pmagicstaticmethodcall.METHOD) = (pmethoddesc.FUNCTION)
~$generator_creator_valid(S, pgeneratorcreation)
$generator_creation_scope_valid(S, pgeneratorcreation)
$generator_creation_record_valid(S, pgenerator)
pgeneratorcreation_bad_scope = pgeneratorcreation[.CREATOR = pgeneratorcreation.CREATOR[.CALLED_CLASS = (porigin_base)]]
~$generator_creation_scope_valid(S, pgeneratorcreation_bad_scope)
pmagicstatic_bad_class = pmagicstaticmethodcall[.CLASS = porigin_base]
pcalltarget_bad_class = MAGIC_STATIC_METHOD_TARGET pmagicstatic_bad_class n_arguments ([POBJECT n_payload])
pgeneratorcreation_bad_class = pgeneratorcreation[.CALLEE = pcalltarget_bad_class][.CREATOR_TARGET = pcalltarget_bad_class][.CREATOR = pgeneratorcreation.CREATOR[.CALLED_CLASS = (porigin_base)]]
~$generator_creation_scope_valid(S, pgeneratorcreation_bad_class)
n_unbounded_array = |S.ARRAYS|
pcalltarget_unbounded = MAGIC_STATIC_METHOD_TARGET pmagicstaticmethodcall n_unbounded_array ([POBJECT n_payload])
pgeneratorcreation_unbounded = pgeneratorcreation[.CALLEE = pcalltarget_unbounded][.CREATOR_TARGET = pcalltarget_unbounded]
~$generator_creation_scope_valid(S, pgeneratorcreation_unbounded)
pcalltarget_bad_count = MAGIC_STATIC_METHOD_TARGET pmagicstaticmethodcall n_arguments eps
pgeneratorcreation_bad_count = pgeneratorcreation[.CALLEE = pcalltarget_bad_count][.CREATOR_TARGET = pcalltarget_bad_count]
~$generator_creation_scope_valid(S, pgeneratorcreation_bad_count)
$call_descriptors_valid(S)
$heap_valid(H)
S_done = $drive_steps(S, 800)
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.CURRENT = eps
S_done.FRAMES = eps
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
""")

CLOSE_STAGE = (
    'S.TODO = (GENERATOR_CLOSE_ENTER pgenclose) :: ptask_tail* '
    '-- if S.OBJECTS[pgenclose.OBJECT] = GENERATOR pgenerator '
    '-- if pgenerator.CREATION = (pgeneratorcreation)')

REBOUND = checks(r"""
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
pgenclose.FRAME = (pframe_generator)
pgenclose.CONTEXT = pcallcontext_generator
pgenerator.FRAME = eps
pgenerator.PHASE = GENERATOR_CLOSING
pgenerator.CLOSURE = eps
pgeneratorcreation.CLOSURE = eps
pgeneratorcreation.ANCESTORS = eps
pgeneratorcreation.CALLEE = MAGIC_METHOD_TARGET pmagicmethodcall n_arguments ([PINT 85])
pgeneratorcreation.CREATOR_TARGET = pgeneratorcreation.CALLEE
pgeneratorcreation.SITE = pmagicmethodcall.SITE
pgeneratorcreation.CREATOR.FUNCTION = pmagicmethodcall.METHOD
pgeneratorcreation.CREATOR.CALLSITE = (pmagicmethodcall.SITE)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Old85C"))) = (porigin_old)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Other85C"))) = (porigin_other)
pgeneratorcreation.CREATOR.LEXICAL_CLASS = (porigin_old)
pgeneratorcreation.CREATOR.CALLED_CLASS = (porigin_old)
pmagicmethodcall.CLASS = porigin_old
pmagicmethodcall.OBJECT = n_old
pmagicmethodcall.NAME = $ptascii("open")
S.OBJECTS[n_old] = INSTANCE porigin_old
(HOBJECT n_old) <- S.ALLOCATIONS
(HARRAY n_arguments) <- S.ALLOCATIONS
$lookup(S.ENV, $ptascii("maker")) = (n_maker_cell)
S.STORE[n_maker_cell] = DEFINED (POBJECT n_other)
S.OBJECTS[n_other] = INSTANCE porigin_other
n_old =/= n_other
$magic_method_descriptor(S, pmagicmethodcall)
$generator_creation_record_valid(S, pgenerator)
S_view = $generator_close_frame_scope(S, pframe_generator)
S_view.CURRENT = (pcallcontext_generator)
pcallcontext_generator.TARGET = pgeneratorcreation.CALLEE
pcallcontext_generator.FUNCTION = pgenerator.FUNCTION
pcallcontext_generator.RECEIVER = (n_old)
$generator_creation_owner(S_view) = (pgenclose.OBJECT)
$generator_creation_selected(S_view, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
$generator_magic_context_valid(S_view, pcallcontext_generator)
$magic_method_entered(S_view, S_view.CURRENT, S_view.FRAMES, pmagicmethodcall, n_arguments, [PINT 85])
$call_current_valid(S_view)
$generator_close_enter_valid(S, pgenclose)
H = $heap_graph(S)
$heap_valid(H)
$heap_owners(H, HOBJECT n_old) = 1
$heap_owners(H, HOBJECT n_other) = 1
$heap_owners(H, HARRAY n_arguments) = 1
$heap_count(HOBJECT n_old, $task_nodes(GENERATOR_CLOSE_ENTER pgenclose)) = 1
$effective_method(S, porigin_other, $ptascii("__call"), |S.CLASSES|) = (pmethoddesc_other)
$function_generator(S, pmethoddesc_other.FUNCTION)
pmagicmethodcall_other = pmagicmethodcall[.OBJECT = n_other][.CLASS = porigin_other][.METHOD = pmethoddesc_other.FUNCTION.ORIGIN]
$magic_method_descriptor(S, pmagicmethodcall_other)
pcalltarget_other = MAGIC_METHOD_TARGET pmagicmethodcall_other n_arguments ([PINT 85])
pgeneratorcreation_other = pgeneratorcreation[.CALLEE = pcalltarget_other][.CREATOR_TARGET = pcalltarget_other][.CREATOR = pgeneratorcreation.CREATOR[.FUNCTION = pmethoddesc_other.FUNCTION.ORIGIN][.LEXICAL_CLASS = (porigin_other)][.CALLED_CLASS = (porigin_other)]]
$generator_creation_scope_valid(S, pgeneratorcreation_other)
pgenerator_wrong = pgenerator[.CREATION = (pgeneratorcreation_other)]
~$generator_creation_record_valid(S, pgenerator_wrong)
S_wrong = $generator_set(S_view, pgenclose.OBJECT, pgenerator_wrong)
~$generator_creation_selected(S_wrong, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
~$magic_method_entered(S_wrong, S_wrong.CURRENT, S_wrong.FRAMES, pmagicmethodcall, n_arguments, [PINT 85])
pgenerator_missing = pgenerator[.CREATION = eps]
S_missing = $generator_set(S_view, pgenclose.OBJECT, pgenerator_missing)
$generator_creation_owner(S_missing) = (pgenclose.OBJECT)
~$generator_magic_context_valid(S_missing, pcallcontext_generator)
$call_descriptors_valid(S)
""")

CASES = {
    'i85-direct-magic-fresh-instance': {
        'source': ROWS['i85-direct-magic-instance-close']['source'],
        'stage': FRESH_STAGE, 'checks': FRESH},
    'i85-direct-magic-completed-static': {
        'source': ROWS['i85-direct-magic-static-payload-return-observed']['source'],
        'stage': COMPLETED_STAGE, 'checks': COMPLETED},
    'i85-direct-magic-rebound-close': {
        'source': ROWS['i85-direct-magic-rebound-receiver']['source'],
        'stage': CLOSE_STAGE, 'checks': REBOUND},
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
