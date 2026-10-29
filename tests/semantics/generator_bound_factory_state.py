#!/usr/bin/env python3
"""Check live bound factory evidence and retired Generator creation scopes."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_bound_factory_cases.json')
INPUT_BYTES = {path: path.read_bytes() for path in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


LIVE_STAGE = (
    'S.CURRENT = (pcallcontext) '
    '-- if pcallcontext.TARGET = CLOSURE_TARGET n_factory '
    '-- if S.OBJECTS[n_factory] = BOUNDFAKECLOSURE pboundfake '
    '-- if S.ORIGIN = (porigin_site) '
    '-- if $origin_node(S.SOURCES, porigin_site) = (NExprStaticCall phpType19 phpType20 phpType6 metadata)')

LIVE = checks(r'''
S.COMPLETION = NORMAL
(HOBJECT n_factory) <- S.ALLOCATIONS
pboundfake.ORIGINAL = (pclosurescope_original)
n_source = pboundfake.SOURCE
S.OBJECTS[n_source] = METHODCLOSURE pcallcontext.FUNCTION porigin_capture porigin_old eps
$class_named(S.CLASSNAMES, $ptlc($ptascii("Mid82"))) = (porigin_factory)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Old82"))) = (porigin_old)
$class_named(S.CLASSNAMES, $ptlc($ptascii("New82"))) = (porigin_called)
pboundfake.SCOPE = BIND_CLASS porigin_factory
pboundfake.CALLED = BIND_CLASS porigin_called
pboundfake.RECEIVER = (n_maker)
pcallcontext.RECEIVER = (n_maker)
pcallcontext.LEXICAL_CLASS = (porigin_factory)
pcallcontext.CALLED_CLASS = (porigin_called)
S.OBJECTS[n_maker] = INSTANCE porigin_called
(HOBJECT n_maker) <- S.ALLOCATIONS
pclosurescope_original.OBJECT = n_source
pclosurescope_original.LEXICAL = porigin_factory
pclosurescope_original.CALLED = porigin_old
pclosurescope_original.RECEIVER = (n_old)
S.OBJECTS[n_old] = INSTANCE porigin_old
~((HOBJECT n_source) <- S.ALLOCATIONS)
~((HOBJECT n_old) <- S.ALLOCATIONS)
$closure_scope_at(S.CLOSURESCOPES, n_source) = eps
$closure_scope_at(S.CLOSURESCOPES, n_factory) = eps
$closure_binding_at(S.CLOSUREBINDINGS, n_factory) = eps
$bound_fake_valid(S, n_factory)
$call_current_valid(S)
$target_function(S, CLOSURE_TARGET n_factory) = (pfunction_factory)
pfunction_factory.ORIGIN = pcallcontext.FUNCTION
~$function_generator(S, pfunction_factory)
$closure_evidence_current(S) = eps
$generator_factory_evidence_current(S) = (CLOSURE_SCOPE pclosurescope)
pclosurescope.OBJECT = n_factory
pclosurescope.LEXICAL = porigin_factory
pclosurescope.CALLED = porigin_called
pclosurescope.RECEIVER = (n_maker)
pclosurescope.CREATION = eps
~$closure_evidence_valid(S, CLOSURE_SCOPE pclosurescope)
$generator_captured_factory_valid(S, pclosurescope, pcallcontext.FUNCTION)
$heap_owners($heap_graph(S), HOBJECT n_source) = 0
$heap_owners($heap_graph(S), HOBJECT n_old) = 0
$effective_method(S, porigin_factory, $ptascii("body"), |S.CLASSES|) = (pmethoddesc_body)
pcallcontext_bad_function = pcallcontext[.FUNCTION = pmethoddesc_body.FUNCTION.ORIGIN]
$generator_factory_evidence_current(S[.CURRENT = (pcallcontext_bad_function)]) = eps
pcallcontext_bad_lexical = pcallcontext[.LEXICAL_CLASS = (porigin_old)]
$generator_factory_evidence_current(S[.CURRENT = (pcallcontext_bad_lexical)]) = eps
pcallcontext_bad_called = pcallcontext[.CALLED_CLASS = (porigin_old)]
$generator_factory_evidence_current(S[.CURRENT = (pcallcontext_bad_called)]) = eps
pcallcontext_bad_receiver = pcallcontext[.RECEIVER = (n_old)]
$generator_factory_evidence_current(S[.CURRENT = (pcallcontext_bad_receiver)]) = eps
$generator_factory_evidence_current(S[.ALLOCATIONS = eps]) = eps
pboundfake_missing_history = pboundfake[.ORIGINAL = eps]
S_missing_history = S[.OBJECTS = $object_set(S.OBJECTS, n_factory, BOUNDFAKECLOSURE pboundfake_missing_history)]
$generator_factory_evidence_current(S_missing_history) = eps
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
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
pgeneratorcreation.CLOSURE = (CLOSURE_SCOPE pclosurescope)
pgeneratorcreation.ANCESTORS = eps
n_factory = pclosurescope.OBJECT
pgeneratorcreation.CREATOR_TARGET = CLOSURE_TARGET n_factory
S.OBJECTS[n_factory] = BOUNDFAKECLOSURE pboundfake
n_source = pboundfake.SOURCE
pboundfake.ORIGINAL = (pclosurescope_original)
S.OBJECTS[n_source] = METHODCLOSURE pgeneratorcreation.CREATOR.FUNCTION porigin_capture porigin_old eps
pboundfake.SCOPE = BIND_CLASS pclosurescope.LEXICAL
pboundfake.CALLED = BIND_CLASS pclosurescope.CALLED
pboundfake.RECEIVER = (n_maker)
pclosurescope.RECEIVER = (n_maker)
pclosurescope.CREATION = eps
pclosurescope_original.OBJECT = n_source
pclosurescope_original.LEXICAL = pclosurescope.LEXICAL
pclosurescope_original.CALLED = porigin_old
pclosurescope_original.RECEIVER = (n_old)
pclosurescope_original.CREATION = eps
S.OBJECTS[n_old] = INSTANCE porigin_old
S.OBJECTS[n_maker] = INSTANCE pclosurescope.CALLED
~((HOBJECT n_source) <- S.ALLOCATIONS)
~((HOBJECT n_factory) <- S.ALLOCATIONS)
~((HOBJECT n_old) <- S.ALLOCATIONS)
$closure_scope_at(S.CLOSURESCOPES, n_source) = eps
$closure_scope_at(S.CLOSURESCOPES, n_factory) = eps
$lookup(S.ENV, $ptascii("source")) = eps
$lookup(S.ENV, $ptascii("bound")) = eps
$lookup(S.ENV, $ptascii("old")) = eps
$lookup(S.ENV, $ptascii("new")) = eps
~$bound_fake_valid(S, n_factory)
~$closure_callable(S, n_factory)
~$closure_evidence_valid(S, CLOSURE_SCOPE pclosurescope)
$generator_captured_factory_valid(S, pclosurescope, pgeneratorcreation.CREATOR.FUNCTION)
$generator_captured_factory_valid(S, pclosurescope_original, pgeneratorcreation.CREATOR.FUNCTION)
$generator_creator_closure_target(S, pgeneratorcreation.CREATOR_TARGET, pgeneratorcreation.CREATOR, CLOSURE_SCOPE pclosurescope)
$generator_creator_receiver(S, pgeneratorcreation.CREATOR_TARGET, pgeneratorcreation.CLOSURE) = (n_maker)
pcallcontext_generator.TARGET = pgeneratorcreation.CALLEE
pcallcontext_generator.CALLSITE = (pgeneratorcreation.SITE)
$heap_owners($heap_graph(S), HOBJECT n_source) = 0
$heap_owners($heap_graph(S), HOBJECT n_factory) = 0
$heap_owners($heap_graph(S), HOBJECT n_old) = 0
$generator_creator_valid(S, pgeneratorcreation)
$generator_creation_scope_valid(S, pgeneratorcreation)
$generator_creation_record_valid(S, pgenerator)
$generator_close_enter_valid(S, pgenclose)
$generator_creation_owner(S_view) = (pgenclose.OBJECT)
$generator_creation_selected(S_view, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
pgeneratorcreation_original = pgeneratorcreation[.CLOSURE = (CLOSURE_SCOPE pclosurescope_original)]
~$generator_creator_valid(S, pgeneratorcreation_original)
pboundfake_missing_history = pboundfake[.ORIGINAL = eps]
S_missing_history = S[.OBJECTS = $object_set(S.OBJECTS, n_factory, BOUNDFAKECLOSURE pboundfake_missing_history)]
~$generator_captured_factory_valid(S_missing_history, pclosurescope, pgeneratorcreation.CREATOR.FUNCTION)
pboundfake_bad_site = pboundfake[.SITE = pgeneratorcreation.SITE]
S_bad_site = S[.OBJECTS = $object_set(S.OBJECTS, n_factory, BOUNDFAKECLOSURE pboundfake_bad_site)]
~$generator_captured_factory_valid(S_bad_site, pclosurescope, pgeneratorcreation.CREATOR.FUNCTION)
pgenerator_missing = pgenerator[.CREATION = eps]
S_missing = $generator_set(S_view, pgenclose.OBJECT, pgenerator_missing)
$generator_creation_owner(S_missing) = (pgenclose.OBJECT)
~$generator_creation_selected(S_missing, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
''')

STATIC_CLOSE = CLOSE + checks(r'''
$class_named(S.CLASSNAMES, $ptlc($ptascii("Mid82"))) = (porigin_factory)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Old82"))) = (porigin_old)
$class_named(S.CLASSNAMES, $ptlc($ptascii("New82"))) = (porigin_called)
pclosurescope.LEXICAL = porigin_factory
pclosurescope.CALLED = porigin_called
pgeneratorcreation.CALLEE = SCOPED_TARGET porigin_factory pgenerator.FUNCTION porigin_called eps poperand_body
pcallcontext_generator.RECEIVER = eps
~((HOBJECT n_maker) <- S.ALLOCATIONS)
$heap_owners($heap_graph(S), HOBJECT n_maker) = 0
$heap_count(HOBJECT n_maker, $node_children(S, HOBJECT pgenclose.OBJECT)) = 0
$heap_count(HOBJECT n_maker, $task_nodes(GENERATOR_CLOSE_ENTER pgenclose)) = 0
''')

PROTECTED_CLOSE = CLOSE + checks(r'''
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base82B"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Mid82B"))) = (porigin_factory)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Old82B"))) = (porigin_old)
$class_named(S.CLASSNAMES, $ptlc($ptascii("New82B"))) = (porigin_called)
pclosurescope.LEXICAL = porigin_factory
pclosurescope.CALLED = porigin_called
pgeneratorcreation.CALLEE = SCOPED_TARGET porigin_base pgenerator.FUNCTION porigin_called (n_maker) poperand_body
pcallcontext_generator.RECEIVER = (n_maker)
(HOBJECT n_maker) <- S.ALLOCATIONS
$call_context_roots((pcallcontext_generator)) = [HOBJECT n_maker]
$heap_count(HOBJECT n_maker, $task_nodes(GENERATOR_CLOSE_ENTER pgenclose)) = 1
pclosurescope_no_receiver = pclosurescope[.RECEIVER = eps]
~$generator_captured_factory_valid(S, pclosurescope_no_receiver, pgeneratorcreation.CREATOR.FUNCTION)
''')

FRESH_STAGE = (
    'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
    '-- if pconfigcall.KIND = INTRINSIC_WEAKREF_GET '
    '-- if $lookup(S.ENV, $ptascii("g")) = (n_generator_cell) '
    '-- if S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator) '
    '-- if S.OBJECTS[n_generator] = GENERATOR pgenerator '
    '-- if pgenerator.PHASE = GENERATOR_FRESH '
    '-- if pgenerator.CREATION = (pgeneratorcreation)')

STATIC_CALLED = checks(r'''
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
S.OBJECTS[n_factory] = BOUNDFAKECLOSURE pboundfake
n_source = pboundfake.SOURCE
pboundfake.ORIGINAL = (pclosurescope_original)
S.OBJECTS[n_source] = METHODCLOSURE pgeneratorcreation.CREATOR.FUNCTION porigin_capture porigin_leaf eps
$class_named(S.CLASSNAMES, $ptlc($ptascii("Mid82C"))) = (porigin_mid)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Leaf82C"))) = (porigin_leaf)
pboundfake.SCOPE = BIND_CLASS porigin_mid
pboundfake.CALLED = BIND_CLASS porigin_mid
pboundfake.RECEIVER = eps
pclosurescope.LEXICAL = porigin_mid
pclosurescope.CALLED = porigin_mid
pclosurescope.RECEIVER = eps
pclosurescope.CREATION = eps
pclosurescope_original.OBJECT = n_source
pclosurescope_original.LEXICAL = porigin_mid
pclosurescope_original.CALLED = porigin_leaf
pclosurescope_original.RECEIVER = eps
~((HOBJECT n_source) <- S.ALLOCATIONS)
~((HOBJECT n_factory) <- S.ALLOCATIONS)
$closure_scope_at(S.CLOSURESCOPES, n_source) = eps
$closure_scope_at(S.CLOSURESCOPES, n_factory) = eps
~$bound_fake_valid(S, n_factory)
~$closure_evidence_valid(S, CLOSURE_SCOPE pclosurescope)
S_lookup = S[.ALLOCATIONS = S.ALLOCATIONS ++ [HOBJECT n_factory]]
$bound_fake_valid(S_lookup, n_factory)
$target_called_class(S_lookup, CLOSURE_TARGET n_factory) = (porigin_mid)
$target_receiver(S_lookup, CLOSURE_TARGET n_factory) = eps
$generator_captured_factory_valid(S, pclosurescope, pgeneratorcreation.CREATOR.FUNCTION)
$generator_captured_factory_valid(S, pclosurescope_original, pgeneratorcreation.CREATOR.FUNCTION)
$heap_owners($heap_graph(S), HOBJECT n_source) = 0
$heap_owners($heap_graph(S), HOBJECT n_factory) = 0
pgeneratorcreation.CALLEE = SCOPED_TARGET porigin_mid pgenerator.FUNCTION porigin_mid eps poperand_body
pcallcontext_generator.TARGET = pgeneratorcreation.CALLEE
pcallcontext_generator.CALLSITE = (pgeneratorcreation.SITE)
pcallcontext_generator.RECEIVER = eps
pcallcontext_generator.CALLED_CLASS = (porigin_mid)
$generator_creator_valid(S, pgeneratorcreation)
$generator_creation_scope_valid(S, pgeneratorcreation)
$generator_creation_record_valid(S, pgenerator)
$generator_creation_object_selected(S, n_generator, pcallcontext_generator)
S_view = $generator_frame_scope(S, pframe_generator)
$call_saved_context_valid(S_view, pframe_generator)
$generator_creation_selected(S_view, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
pclosurescope_bad_called = pclosurescope[.CALLED = porigin_leaf]
~$generator_captured_factory_valid(S, pclosurescope_bad_called, pgeneratorcreation.CREATOR.FUNCTION)
pgeneratorcreation_bad_called = pgeneratorcreation[.CREATOR = pgeneratorcreation.CREATOR[.CALLED_CLASS = (porigin_leaf)]]
~$generator_creator_valid(S, pgeneratorcreation_bad_called)
pgeneratorcreation_original = pgeneratorcreation[.CLOSURE = (CLOSURE_SCOPE pclosurescope_original)]
~$generator_creator_valid(S, pgeneratorcreation_original)
$effective_method(S, porigin_leaf, $ptascii("body"), |S.CLASSES|) = (pmethoddesc_leaf_body)
pgeneratorcreation_wrong_selection = pgeneratorcreation[.CALLEE = SCOPED_TARGET porigin_leaf pmethoddesc_leaf_body.FUNCTION.ORIGIN porigin_leaf eps (KNOWN (PSTRING ($ptascii("Leaf82C"))))]
$target_function(S, pgeneratorcreation_wrong_selection.CALLEE) = (pmethoddesc_leaf_body.FUNCTION)
$generator_creator_valid(S, pgeneratorcreation_wrong_selection)
~$generator_creation_scope_valid(S, pgeneratorcreation_wrong_selection)
pgenerator_missing = pgenerator[.CREATION = eps]
S_missing = $generator_set(S_view, n_generator, pgenerator_missing)
~$generator_creation_selected(S_missing, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
~$call_saved_context_valid(S_missing, pframe_generator)
''')

CASES = {
    'i82-live-bound-mint': {'source': ROWS['i82-bind-compatible-static']['source'], 'stage': LIVE_STAGE, 'checks': LIVE},
    'i82-bound-static-close': {'source': ROWS['i82-bind-compatible-static']['source'], 'stage': CLOSE_STAGE, 'checks': STATIC_CLOSE},
    'i82-bound-protected-close': {'source': ROWS['i82-bind-protected-close']['source'], 'stage': CLOSE_STAGE, 'checks': PROTECTED_CLOSE},
    'i82-bound-static-called': {'source': ROWS['i82-bind-static-called-scope']['source'], 'stage': FRESH_STAGE, 'checks': STATIC_CALLED},
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
