#!/usr/bin/env python3
"""Check retired magic factories, actual receivers and completed payloads."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_magic_factory_cases.json')
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
pgeneratorcreation.CREATOR_TARGET = MAGIC_METHOD_TARGET pmagicmethodcall n_arguments ([PINT 84])
pgeneratorcreation.CREATOR.FUNCTION = pmagicmethodcall.METHOD
pgeneratorcreation.CREATOR.CALLSITE = (pmagicmethodcall.SITE)
pgeneratorcreation.CREATOR.LEXICAL_CLASS = (porigin_base)
pgeneratorcreation.CREATOR.CALLED_CLASS = (porigin_child)
pmagicmethodcall.CLASS = porigin_child
pmagicmethodcall.OBJECT = n_maker
pmagicmethodcall.NAME = $ptascii("open")
pmagicmethodcall.CALLER = eps
pmagicmethodcall.OWNER = 0
|pmagicmethodcall.ARGUMENTS| = 1
S.OBJECTS[n_maker] = INSTANCE porigin_child
$(n_arguments < |S.ARRAYS|)
~((HARRAY n_arguments) <- S.ALLOCATIONS)
S.ARRAYS[n_arguments].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 84))]
$magic_method_descriptor(S, pmagicmethodcall)
~$magic_method_pending(S, pmagicmethodcall, n_arguments, [PINT 84])
~$magic_method_entered(S, S.CURRENT, S.FRAMES, pmagicmethodcall, n_arguments, [PINT 84])
$target_function(S, pgeneratorcreation.CREATOR_TARGET) = eps
$effective_method(S, porigin_child, $ptascii("__call"), |S.CLASSES|) = (pmethoddesc_factory)
pmethoddesc_factory.OWNER = porigin_base
pmethoddesc_factory.FUNCTION.ORIGIN = pmagicmethodcall.METHOD
~$function_generator(S, pmethoddesc_factory.FUNCTION)
$generator_creator_receiver(S, pgeneratorcreation.CREATOR_TARGET, eps) = (n_maker)
$lookup(S.ENV, $ptascii("maker")) = eps
pcallcontext_generator.TARGET = pgeneratorcreation.CALLEE
pcallcontext_generator.CALLSITE = (pgeneratorcreation.SITE)
$generator_creator_valid(S, pgeneratorcreation)
$generator_creation_scope_valid(S, pgeneratorcreation)
$generator_creation_record_valid(S, pgenerator)
$generator_close_enter_valid(S, pgenclose)
$generator_creation_owner(S_view) = (pgenclose.OBJECT)
$generator_creation_selected(S_view, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
$heap_owners($heap_graph(S), HARRAY n_arguments) = 0
pmagicmethodcall_bad_name = pmagicmethodcall[.NAME = $ptascii("other")]
pgeneratorcreation_bad_name = pgeneratorcreation[.CREATOR_TARGET = MAGIC_METHOD_TARGET pmagicmethodcall_bad_name n_arguments ([PINT 84])]
~$generator_creator_valid(S, pgeneratorcreation_bad_name)
pmagicmethodcall_bad_method = pmagicmethodcall[.METHOD = pgenerator.FUNCTION]
pgeneratorcreation_bad_method = pgeneratorcreation[.CREATOR_TARGET = MAGIC_METHOD_TARGET pmagicmethodcall_bad_method n_arguments ([PINT 84])]
~$generator_creator_valid(S, pgeneratorcreation_bad_method)
pmagicmethodcall_bad_site = pmagicmethodcall[.SITE = pgeneratorcreation.SITE]
pgeneratorcreation_bad_site = pgeneratorcreation[.CREATOR_TARGET = MAGIC_METHOD_TARGET pmagicmethodcall_bad_site n_arguments ([PINT 84])]
~$generator_creator_valid(S, pgeneratorcreation_bad_site)
n_unbounded_object = |S.OBJECTS|
pmagicmethodcall_unbounded = pmagicmethodcall[.OBJECT = n_unbounded_object]
pgeneratorcreation_unbounded_object = pgeneratorcreation[.CREATOR_TARGET = MAGIC_METHOD_TARGET pmagicmethodcall_unbounded n_arguments ([PINT 84])]
~$generator_creator_valid(S, pgeneratorcreation_unbounded_object)
n_unbounded_array = |S.ARRAYS|
pgeneratorcreation_unbounded_array = pgeneratorcreation[.CREATOR_TARGET = MAGIC_METHOD_TARGET pmagicmethodcall n_unbounded_array ([PINT 84])]
~$generator_creator_valid(S, pgeneratorcreation_unbounded_array)
pgeneratorcreation_bad_count = pgeneratorcreation[.CREATOR_TARGET = MAGIC_METHOD_TARGET pmagicmethodcall n_arguments eps]
~$generator_creator_valid(S, pgeneratorcreation_bad_count)
pgeneratorcreation_bad_called = pgeneratorcreation[.CREATOR = pgeneratorcreation.CREATOR[.CALLED_CLASS = (porigin_base)]]
~$generator_creator_valid(S, pgeneratorcreation_bad_called)
pgenerator_missing = pgenerator[.CREATION = eps]
S_missing = $generator_set(S_view, pgenclose.OBJECT, pgenerator_missing)
$generator_creation_owner(S_missing) = (pgenclose.OBJECT)
~$generator_creation_selected(S_missing, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
''')

STATIC_CLOSE = CLOSE + checks(r'''
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base84"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Child84"))) = (porigin_child)
pgeneratorcreation.CALLEE = SCOPED_TARGET porigin_base pgenerator.FUNCTION porigin_child eps poperand_body
pcallcontext_generator.RECEIVER = eps
~((HOBJECT n_maker) <- S.ALLOCATIONS)
n_maker <- S.DESTRUCTION.CALLED
$heap_owners($heap_graph(S), HOBJECT n_maker) = 0
$heap_count(HOBJECT n_maker, $task_nodes(GENERATOR_CLOSE_ENTER pgenclose)) = 0
''')

PROTECTED_CLOSE = CLOSE + checks(r'''
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base84B"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Child84B"))) = (porigin_child)
pgeneratorcreation.CALLEE = SCOPED_TARGET porigin_base pgenerator.FUNCTION porigin_child (n_maker) poperand_body
pcallcontext_generator.RECEIVER = (n_maker)
(HOBJECT n_maker) <- S.ALLOCATIONS
$call_context_roots((pcallcontext_generator)) = [HOBJECT n_maker]
$heap_count(HOBJECT n_maker, $task_nodes(GENERATOR_CLOSE_ENTER pgenclose)) = 1
$heap_owners($heap_graph(S), HOBJECT n_maker) = 1
pmagicmethodcall_bad_receiver = pmagicmethodcall[.OBJECT = pgenclose.OBJECT]
pgeneratorcreation_bad_receiver = pgeneratorcreation[.CREATOR_TARGET = MAGIC_METHOD_TARGET pmagicmethodcall_bad_receiver n_arguments ([PINT 84])]
~$generator_creator_valid(S, pgeneratorcreation_bad_receiver)
''')

COMPLETED_STAGE = (
    'S.TODO = (GENERATOR_ARGS pgeneratorop eps eps) :: ptask_tail* '
    '-- if pgeneratorop.NAME = "getreturn" '
    '-- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator '
    '-- if pgenerator.PHASE = GENERATOR_CLOSED '
    '-- if pgenerator.CREATION = (pgeneratorcreation)')

COMPLETED = checks(r'''
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
(HOBJECT pgeneratorop.OBJECT) <- S.ALLOCATIONS
pgenerator.FRAME = eps
pgenerator.CLOSURE = eps
pgenerator.RETURN = (PINT 85)
pgeneratorcreation.CLOSURE = eps
pgeneratorcreation.ANCESTORS = eps
pgeneratorcreation.CREATOR_TARGET = MAGIC_STATIC_METHOD_TARGET pmagicstaticmethodcall n_arguments ([POBJECT n_payload])
pgeneratorcreation.CREATOR.FUNCTION = pmagicstaticmethodcall.METHOD
pgeneratorcreation.CREATOR.CALLSITE = (pmagicstaticmethodcall.SITE)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base84C"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Child84C"))) = (porigin_child)
pgeneratorcreation.CREATOR.LEXICAL_CLASS = (porigin_base)
pgeneratorcreation.CREATOR.CALLED_CLASS = (porigin_child)
pmagicstaticmethodcall.CLASS = porigin_child
pmagicstaticmethodcall.NAME = $ptascii("open")
pmagicstaticmethodcall.CALLER = eps
pmagicstaticmethodcall.OWNER = 0
|pmagicstaticmethodcall.ARGUMENTS| = 1
$(n_arguments < |S.ARRAYS|)
~((HARRAY n_arguments) <- S.ALLOCATIONS)
~((HOBJECT n_payload) <- S.ALLOCATIONS)
n_payload <- S.DESTRUCTION.CALLED
$object_name(S, n_payload) = $ptascii("Payload84C")
$heap_owners($heap_graph(S), HARRAY n_arguments) = 0
$heap_owners($heap_graph(S), HOBJECT n_payload) = 0
$heap_count(HOBJECT n_payload, $node_children(S, HOBJECT pgeneratorop.OBJECT)) = 0
$lookup(S.ENV, $ptascii("weak")) = (n_weak_cell)
S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)
$weakref_get(S, n_weak) = PNULL
$magic_static_method_descriptor(S, pmagicstaticmethodcall)
~$magic_static_method_pending(S, pmagicstaticmethodcall, n_arguments, [POBJECT n_payload])
~$magic_static_method_entered(S, S.CURRENT, S.FRAMES, pmagicstaticmethodcall, n_arguments, [POBJECT n_payload])
$target_function(S, pgeneratorcreation.CREATOR_TARGET) = eps
$effective_method(S, porigin_child, $ptascii("__callstatic"), |S.CLASSES|) = (pmethoddesc_factory)
pmethoddesc_factory.OWNER = porigin_base
pmethoddesc_factory.STATIC
$target_function(S, STATIC_METHOD_TARGET porigin_child pmagicstaticmethodcall.METHOD) = (pmethoddesc_factory.FUNCTION)
$generator_creator_receiver(S, pgeneratorcreation.CREATOR_TARGET, eps) = eps
pgeneratorcreation.CALLEE = SCOPED_TARGET porigin_base pgenerator.FUNCTION porigin_child eps poperand_body
$generator_creator_valid(S, pgeneratorcreation)
$generator_creation_scope_valid(S, pgeneratorcreation)
$generator_creation_record_valid(S, pgenerator)
pmagicstaticmethodcall_bad_name = pmagicstaticmethodcall[.NAME = $ptascii("other")]
pgeneratorcreation_bad_name = pgeneratorcreation[.CREATOR_TARGET = MAGIC_STATIC_METHOD_TARGET pmagicstaticmethodcall_bad_name n_arguments ([POBJECT n_payload])]
~$generator_creator_valid(S, pgeneratorcreation_bad_name)
pmagicstaticmethodcall_bad_method = pmagicstaticmethodcall[.METHOD = pgenerator.FUNCTION]
pgeneratorcreation_bad_method = pgeneratorcreation[.CREATOR_TARGET = MAGIC_STATIC_METHOD_TARGET pmagicstaticmethodcall_bad_method n_arguments ([POBJECT n_payload])]
~$generator_creator_valid(S, pgeneratorcreation_bad_method)
pmagicstaticmethodcall_bad_class = pmagicstaticmethodcall[.CLASS = porigin_base]
pgeneratorcreation_bad_class = pgeneratorcreation[.CREATOR_TARGET = MAGIC_STATIC_METHOD_TARGET pmagicstaticmethodcall_bad_class n_arguments ([POBJECT n_payload])][.CREATOR = pgeneratorcreation.CREATOR[.CALLED_CLASS = (porigin_base)]]
~$generator_creator_valid(S, pgeneratorcreation_bad_class)
n_unbounded_array = |S.ARRAYS|
pgeneratorcreation_unbounded_array = pgeneratorcreation[.CREATOR_TARGET = MAGIC_STATIC_METHOD_TARGET pmagicstaticmethodcall n_unbounded_array ([POBJECT n_payload])]
~$generator_creator_valid(S, pgeneratorcreation_unbounded_array)
pgeneratorcreation_bad_count = pgeneratorcreation[.CREATOR_TARGET = MAGIC_STATIC_METHOD_TARGET pmagicstaticmethodcall n_arguments eps]
~$generator_creator_valid(S, pgeneratorcreation_bad_count)
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
S_done = $drive_steps(S, 800)
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.CURRENT = eps
S_done.FRAMES = eps
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
''')

FRESH_STAGE = (
    'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
    '-- if pconfigcall.KIND = INTRINSIC_WEAKREF_GET '
    '-- if $lookup(S.ENV, $ptascii("g")) = (n_generator_cell) '
    '-- if S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator) '
    '-- if S.OBJECTS[n_generator] = GENERATOR pgenerator '
    '-- if pgenerator.PHASE = GENERATOR_FRESH '
    '-- if pgenerator.CREATION = (pgeneratorcreation)')

REBOUND = checks(r'''
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
pgenerator.CLOSURE = eps
pgenerator.FRAME = (pframe_generator)
pframe_generator.CONTEXT = (pcallcontext_generator)
pgeneratorcreation.CLOSURE = eps
pgeneratorcreation.ANCESTORS = eps
pgeneratorcreation.CREATOR_TARGET = MAGIC_METHOD_TARGET pmagicmethodcall n_arguments ([PINT 84])
pgeneratorcreation.CREATOR.FUNCTION = pmagicmethodcall.METHOD
pgeneratorcreation.CREATOR.CALLSITE = (pmagicmethodcall.SITE)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base84D"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Old84D"))) = (porigin_old)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Other84D"))) = (porigin_other)
pgeneratorcreation.CREATOR.LEXICAL_CLASS = (porigin_base)
pgeneratorcreation.CREATOR.CALLED_CLASS = (porigin_old)
pmagicmethodcall.CLASS = porigin_old
pmagicmethodcall.NAME = $ptascii("open")
pmagicmethodcall.OBJECT = n_old
S.OBJECTS[n_old] = INSTANCE porigin_old
~((HOBJECT n_old) <- S.ALLOCATIONS)
n_old <- S.DESTRUCTION.CALLED
~((HARRAY n_arguments) <- S.ALLOCATIONS)
$heap_owners($heap_graph(S), HOBJECT n_old) = 0
$heap_owners($heap_graph(S), HARRAY n_arguments) = 0
$lookup(S.ENV, $ptascii("maker")) = (n_new_cell)
S.STORE[n_new_cell] = DEFINED (POBJECT n_new)
n_new =/= n_old
S.OBJECTS[n_new] = INSTANCE porigin_other
(HOBJECT n_new) <- S.ALLOCATIONS
$lookup(S.ENV, $ptascii("weakOld")) = (n_weak_cell)
S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)
$weakref_get(S, n_weak) = PNULL
$magic_method_descriptor(S, pmagicmethodcall)
$target_function(S, pgeneratorcreation.CREATOR_TARGET) = eps
pgeneratorcreation.CALLEE = SCOPED_TARGET porigin_base pgenerator.FUNCTION porigin_old eps poperand_body
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
$effective_method(S, porigin_other, $ptascii("__call"), |S.CLASSES|) = (pmethoddesc_other)
pmagicmethodcall_other = pmagicmethodcall[.OBJECT = n_new][.CLASS = porigin_other][.METHOD = pmethoddesc_other.FUNCTION.ORIGIN]
$magic_method_descriptor(S, pmagicmethodcall_other)
pgeneratorcreation_other = pgeneratorcreation[.CREATOR_TARGET = MAGIC_METHOD_TARGET pmagicmethodcall_other n_arguments ([PINT 84])]
~$generator_creator_valid(S, pgeneratorcreation_other)
pmethodcapture_other = pgeneratorcreation.CREATOR[.FUNCTION = pmethoddesc_other.FUNCTION.ORIGIN][.LEXICAL_CLASS = (porigin_other)][.CALLED_CLASS = (porigin_other)]
pgeneratorcreation_consistent_other = pgeneratorcreation_other[.CREATOR = pmethodcapture_other]
~$generator_creator_valid(S, pgeneratorcreation_consistent_other)
pgenerator_missing = pgenerator[.CREATION = eps]
S_missing = $generator_set(S_view, n_generator, pgenerator_missing)
~$generator_creation_selected(S_missing, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
''')

CASES = {
    'i84-magic-static-close': {'source': ROWS['i84-magic-static-retired']['source'], 'stage': CLOSE_STAGE, 'checks': STATIC_CLOSE},
    'i84-magic-protected-close': {'source': ROWS['i84-magic-protected-close']['source'], 'stage': CLOSE_STAGE, 'checks': PROTECTED_CLOSE},
    'i84-magic-static-completed-payload': {'source': ROWS['i84-magic-static-payload-return']['source'], 'stage': COMPLETED_STAGE, 'checks': COMPLETED},
    'i84-magic-rebound-receiver-fresh': {'source': ROWS['i84-magic-argument-rebind']['source'], 'stage': FRESH_STAGE, 'checks': REBOUND},
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
