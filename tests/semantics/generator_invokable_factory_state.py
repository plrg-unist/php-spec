#!/usr/bin/env python3
"""Check implicit Generator producers and retired ordinary factory targets."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_invokable_factory_cases.json')
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
pgeneratorcreation.CREATOR_TARGET = METHOD_TARGET n_maker porigin_invoke
pgeneratorcreation.CREATOR.FUNCTION = porigin_invoke
pgeneratorcreation.CREATOR.LEXICAL_CLASS = (porigin_factory)
pgeneratorcreation.CREATOR.CALLED_CLASS = (porigin_called)
pgeneratorcreation.CREATOR.CALLSITE = (porigin_call)
S.OBJECTS[n_maker] = INSTANCE porigin_called
$origin_node(S.SOURCES, porigin_call) = (NExprFuncCall expression (SEQUENCE phpType7*) metadata)
$ppcall_dynamic(expression)
~$ppfirstclass(phpType7*)
$firstclass_evaluated(S, porigin_call)
$dynamic_fixed_name(S, porigin_call) = eps
$generator_implicit_invoke_target(S, METHOD_TARGET n_maker porigin_invoke, porigin_call)
$generator_creation_method_source(S, METHOD_TARGET n_maker porigin_invoke, porigin_call)
~$generator_creator_method_site(S, porigin_call, $ptascii("__invoke"))
$class_method_origin(S.CLASSES, porigin_invoke) = (pmethoddesc_invoke)
pmethoddesc_invoke.OWNER = porigin_factory
pmethoddesc_invoke.NAME = $ptascii("__invoke")
~pmethoddesc_invoke.STATIC
$lookup(S.ENV, $ptascii("maker")) = eps
pcallcontext_generator.TARGET = pgeneratorcreation.CALLEE
pcallcontext_generator.CALLSITE = (pgeneratorcreation.SITE)
$generator_creator_valid(S, pgeneratorcreation)
$generator_creation_scope_valid(S, pgeneratorcreation)
$generator_creation_record_valid(S, pgenerator)
$generator_close_enter_valid(S, pgenclose)
$generator_creation_owner(S_view) = (pgenclose.OBJECT)
$generator_creation_selected(S_view, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
~$generator_implicit_invoke_target(S, METHOD_TARGET |S.OBJECTS| porigin_invoke, porigin_call)
~$generator_implicit_invoke_target(S, METHOD_TARGET pgenclose.OBJECT porigin_invoke, porigin_call)
~$generator_implicit_invoke_target(S, STATIC_METHOD_TARGET porigin_called porigin_invoke, porigin_call)
~$generator_implicit_invoke_target(S, METHOD_TARGET n_maker porigin_invoke, pgeneratorcreation.SITE)
~$generator_implicit_invoke_target(S[.CODE = eps], METHOD_TARGET n_maker porigin_invoke, porigin_call)
pgeneratorcreation_bad_called = pgeneratorcreation[.CREATOR = pgeneratorcreation.CREATOR[.CALLED_CLASS = (porigin_factory)]]
~$generator_creator_valid(S, pgeneratorcreation_bad_called)
pgenerator_missing = pgenerator[.CREATION = eps]
S_missing = $generator_set(S_view, pgenclose.OBJECT, pgenerator_missing)
$generator_creation_owner(S_missing) = (pgenclose.OBJECT)
~$generator_creation_selected(S_missing, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
''')

STATIC_CLOSE = CLOSE + checks(r'''
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base83"))) = (porigin_factory)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Child83"))) = (porigin_called)
pgeneratorcreation.CALLEE = SCOPED_TARGET porigin_factory pgenerator.FUNCTION porigin_called eps poperand_body
pcallcontext_generator.RECEIVER = eps
~((HOBJECT n_maker) <- S.ALLOCATIONS)
$heap_owners($heap_graph(S), HOBJECT n_maker) = 0
$heap_count(HOBJECT n_maker, $task_nodes(GENERATOR_CLOSE_ENTER pgenclose)) = 0
$object_invoke_method(S, n_maker) = eps
~$generator_creation_target(S, METHOD_TARGET n_maker porigin_invoke, (porigin_call))
S_lookup = S[.ALLOCATIONS = S.ALLOCATIONS ++ [HOBJECT n_maker]]
$object_invoke_method(S_lookup, n_maker) = (pmethoddesc_invoke)
$effective_method(S, porigin_called, $ptascii("body"), |S.CLASSES|) = (pmethoddesc_wrong)
pmethoddesc_wrong.FUNCTION.ORIGIN =/= pgenerator.FUNCTION
~$generator_implicit_invoke_target(S, METHOD_TARGET n_maker pmethoddesc_wrong.FUNCTION.ORIGIN, porigin_call)
''')

PROTECTED_CLOSE = CLOSE + checks(r'''
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base83B"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Mid83B"))) = (porigin_factory)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Child83B"))) = (porigin_called)
pgeneratorcreation.CALLEE = SCOPED_TARGET porigin_base pgenerator.FUNCTION porigin_called (n_maker) poperand_body
pcallcontext_generator.RECEIVER = (n_maker)
(HOBJECT n_maker) <- S.ALLOCATIONS
$object_invoke_method(S, n_maker) = (pmethoddesc_invoke)
$call_context_roots((pcallcontext_generator)) = [HOBJECT n_maker]
$heap_count(HOBJECT n_maker, $task_nodes(GENERATOR_CLOSE_ENTER pgenclose)) = 1
$heap_owners($heap_graph(S), HOBJECT n_maker) = 1
pgeneratorcreation_bad_receiver = pgeneratorcreation[.CREATOR_TARGET = METHOD_TARGET pgenclose.OBJECT porigin_invoke]
~$generator_creator_valid(S, pgeneratorcreation_bad_receiver)
''')

FRESH_STAGE = (
    'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
    '-- if pconfigcall.KIND = INTRINSIC_WEAKREF_GET '
    '-- if $lookup(S.ENV, $ptascii("g")) = (n_generator_cell) '
    '-- if S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator) '
    '-- if S.OBJECTS[n_generator] = GENERATOR pgenerator '
    '-- if pgenerator.PHASE = GENERATOR_FRESH '
    '-- if pgenerator.CREATION = (pgeneratorcreation)')

FORWARD = checks(r'''
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
pgenerator.CLOSURE = eps
pgenerator.FRAME = (pframe_generator)
pframe_generator.CONTEXT = (pcallcontext_generator)
pgeneratorcreation.CLOSURE = eps
pgeneratorcreation.ANCESTORS = [pgenfactorycapture]
pgenfactorycapture.CLOSURE = eps
pgenfactorycapture.TARGET = METHOD_TARGET n_maker porigin_invoke
pgenfactorycapture.CONTEXT.FUNCTION = porigin_invoke
pgenfactorycapture.CONTEXT.CALLSITE = (porigin_call)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base83C"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Mid83C"))) = (porigin_mid)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Child83C"))) = (porigin_child)
pgenfactorycapture.CONTEXT.LEXICAL_CLASS = (porigin_mid)
pgenfactorycapture.CONTEXT.CALLED_CLASS = (porigin_child)
S.OBJECTS[n_maker] = INSTANCE porigin_child
~((HOBJECT n_maker) <- S.ALLOCATIONS)
$lookup(S.ENV, $ptascii("maker")) = eps
$heap_owners($heap_graph(S), HOBJECT n_maker) = 0
$object_invoke_method(S, n_maker) = eps
$generator_implicit_invoke_target(S, pgenfactorycapture.TARGET, porigin_call)
$generator_creation_method_source(S, pgenfactorycapture.TARGET, porigin_call)
pgeneratorcreation.CREATOR_TARGET = SCOPED_TARGET porigin_mid pgeneratorcreation.CREATOR.FUNCTION porigin_child eps poperand_forward
pgeneratorcreation.CREATOR.LEXICAL_CLASS = (porigin_mid)
pgeneratorcreation.CREATOR.CALLED_CLASS = (porigin_child)
$class_method_origin(S.CLASSES, pgeneratorcreation.CREATOR.FUNCTION) = (pmethoddesc_forward)
pmethoddesc_forward.OWNER = porigin_mid
pmethoddesc_forward.NAME = $ptascii("forward")
pmethoddesc_forward.STATIC
pgeneratorcreation.CALLEE = SCOPED_TARGET porigin_base pgenerator.FUNCTION porigin_child eps poperand_body
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
pgeneratorcreation_erased = pgeneratorcreation[.ANCESTORS = eps]
~$generator_creator_valid(S, pgeneratorcreation_erased)
pgenfactorycapture_bad_called = pgenfactorycapture[.CONTEXT = pgenfactorycapture.CONTEXT[.CALLED_CLASS = (porigin_mid)]]
pgeneratorcreation_bad_called = pgeneratorcreation[.ANCESTORS = [pgenfactorycapture_bad_called]]
~$generator_creator_valid(S, pgeneratorcreation_bad_called)
pgenfactorycapture_bad_target = pgenfactorycapture[.TARGET = METHOD_TARGET n_maker pgeneratorcreation.CREATOR.FUNCTION]
pgeneratorcreation_bad_target = pgeneratorcreation[.ANCESTORS = [pgenfactorycapture_bad_target]]
~$generator_creator_valid(S, pgeneratorcreation_bad_target)
pgenerator_missing = pgenerator[.CREATION = eps]
S_missing = $generator_set(S_view, n_generator, pgenerator_missing)
~$generator_creation_selected(S_missing, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
''')

DIRECT_STAGE = (
    'S.TODO = (GENERATOR_CLOSE_ENTER pgenclose) :: ptask_tail* '
    '-- if S.OBJECTS[pgenclose.OBJECT] = GENERATOR pgenerator '
    '-- if pgenerator.CREATION = eps')

DIRECT = checks(r'''
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
pgenerator.CLOSURE = eps
pgenclose.FRAME = (pframe_generator)
pgenclose.CONTEXT = pcallcontext_generator
S_view = $generator_close_frame_scope(S, pframe_generator)
pcallcontext_generator.TARGET = METHOD_TARGET n_maker pgenerator.FUNCTION
pcallcontext_generator.FUNCTION = pgenerator.FUNCTION
pcallcontext_generator.CALLSITE = (PORIGIN n_unit pcpath)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base83D"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Mid83D"))) = (porigin_mid)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Leaf83D"))) = (porigin_leaf)
pcallcontext_generator.LEXICAL_CLASS = (porigin_mid)
pcallcontext_generator.CALLED_CLASS = (porigin_leaf)
pcallcontext_generator.RECEIVER = (n_maker)
S.OBJECTS[n_maker] = INSTANCE porigin_leaf
(HOBJECT n_maker) <- S.ALLOCATIONS
$lookup(S.ENV, $ptascii("maker")) = eps
$origin_node(S.SOURCES, PORIGIN n_unit pcpath) = (NExprFuncCall expression (SEQUENCE phpType7*) metadata)
$goto_source_owner($all_functions(S), n_unit, pcpath) = (pfunction_open)
$class_method_origin(S.CLASSES, pfunction_open.ORIGIN) = (pmethoddesc_open)
pmethoddesc_open.OWNER = porigin_base
pmethoddesc_open.NAME = $ptascii("open")
$object_invoke_method(S, n_maker) = (pmethoddesc_invoke)
pmethoddesc_invoke.OWNER = porigin_mid
pmethoddesc_invoke.FUNCTION.ORIGIN = pgenerator.FUNCTION
$function_generator(S, pmethoddesc_invoke.FUNCTION)
$generator_implicit_invoke_target(S, pcallcontext_generator.TARGET, PORIGIN n_unit pcpath)
$generator_creation_method_source(S, pcallcontext_generator.TARGET, PORIGIN n_unit pcpath)
$generator_creation_target(S, pcallcontext_generator.TARGET, (PORIGIN n_unit pcpath))
~$generator_creator_method_site(S, PORIGIN n_unit pcpath, $ptascii("__invoke"))
$generator_creation_supported(S_view, pcallcontext_generator)
~$generator_creation_required(S_view, pcallcontext_generator)
$effective_method(S, porigin_base, $ptascii("__invoke"), |S.CLASSES|) = (pmethoddesc_base_invoke)
$function_generator(S, pmethoddesc_base_invoke.FUNCTION)
~$generator_implicit_invoke_target(S, METHOD_TARGET n_maker pmethoddesc_base_invoke.FUNCTION.ORIGIN, PORIGIN n_unit pcpath)
~$generator_implicit_invoke_target(S, pcallcontext_generator.TARGET, pgenclose.SITE)
S_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HOBJECT n_maker)]
$generator_implicit_invoke_target(S_dead, pcallcontext_generator.TARGET, PORIGIN n_unit pcpath)
~$generator_creation_target(S_dead, pcallcontext_generator.TARGET, (PORIGIN n_unit pcpath))
$call_context_roots((pcallcontext_generator)) = [HOBJECT n_maker]
$heap_count(HOBJECT n_maker, $task_nodes(GENERATOR_CLOSE_ENTER pgenclose)) = 1
$heap_owners($heap_graph(S), HOBJECT n_maker) = 1
$generator_close_enter_valid(S, pgenclose)
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
''')

CASES = {
    'i83-static-factory-close': {'source': ROWS['i83-implicit-static']['source'], 'stage': CLOSE_STAGE, 'checks': STATIC_CLOSE},
    'i83-protected-factory-close': {'source': ROWS['i83-implicit-protected-close']['source'], 'stage': CLOSE_STAGE, 'checks': PROTECTED_CLOSE},
    'i83-forward-factory-fresh': {'source': ROWS['i83-implicit-forward-chain']['source'], 'stage': FRESH_STAGE, 'checks': FORWARD},
    'i83-direct-invoke-close': {'source': ROWS['i83-implicit-direct-generator']['source'], 'stage': DIRECT_STAGE, 'checks': DIRECT},
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
