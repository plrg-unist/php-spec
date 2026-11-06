#!/usr/bin/env python3
"""Reach a short GET's nested Tick with the real getter return still pending."""
import argparse
import json

import fiber_state_review as review
import tick_short_get_review_cases as sources


def output(*chunks):
    return '[' + ', '.join('OUTPUT $ptascii(' + json.dumps(chunk) + ')'
                           for chunk in chunks) + ']'


def valid(state):
    return [f'$call_descriptors_valid({state})',
            f'$heap_valid($heap_graph({state}))', f'$tick_state_valid({state})']


review.CASES = {
    'short-get-nested-tick-retains-receiver-until-callback-unwind': {
        'source': sources.SOURCE.decode(),
        'stage': 'S.TODO = (TICK porigin ptickmarker) :: ptask_tail* -- if S.CURRENT = (pcallcontext) -- if S.EVENTS = ' + output('G'),
        'checks': [
            'porigin_class = PORIGIN 0 ([PCINDEX 2])',
            'porigin_property = PORIGIN 0 ([PCINDEX 2, PCFIELD 5, PCINDEX 1])',
            'porigin_hook = PORIGIN 0 ([PCINDEX 2, PCFIELD 5, PCINDEX 1, PCFIELD 4, PCINDEX 0])',
            '$origin_child((porigin_hook), [PCFIELD 5, PCFIELD 0]) = (porigin_closure)',
            '$origin_child((porigin_closure), [PCFIELD 6, PCINDEX 0, PCFIELD 1, PCINDEX 0]) = (porigin)',
            'pcallcontext.FUNCTION = porigin_closure',
            'pcallcontext.TARGET = CLOSURE_TARGET n_closure',
            'S.FRAMES = pframe_hook :: pframe_tail*',
            'pframe_hook.CONTEXT = (pcallcontext_hook)',
            'pcallcontext_hook.TARGET = PROPERTY_HOOK_TARGET ppropertyhook',
            'pcallcontext_hook.FUNCTION = porigin_hook',
            'ppropertyhook.HOOK = porigin_hook', 'n_object = ppropertyhook.OBJECT',
            'pcallcontext.RECEIVER = (n_object)',
            'pcallcontext_hook.RECEIVER = (n_object)',
            '$property_hook_context_valid(S, pcallcontext_hook)',
            '$property_hook_function(S, ppropertyhook) = (pfunction_hook)',
            '$arrow_line(pfunction_hook.CODE.EXPRESSIONS, pfunction_hook.BODY) = (z_return)',
            '(RETURN_VALUE z_return) <- pframe_hook.TODO',
            '$closure_scope_at(S.CLOSURESCOPES, n_closure) = (pclosurescope)',
            'pclosurescope.RECEIVER = (n_object)',
            'pclosurescope.LEXICAL = porigin_class',
            '$closure_source_class(S, porigin_closure) = (porigin_class)',
            'S.CLASSES = [pclassdesc]',
            'S_no_properties = S[.CLASSES = [pclassdesc[.PROPERTIES = eps]]]',
            '$closure_source_class(S_no_properties, porigin_closure) = eps',
            'S.OBJECTS[n_object] = INSTANCE porigin_class',
            'HOBJECT n_object <- S.ALLOCATIONS',
            '~(n_object <- S.DESTRUCTION.CALLED)',
            '$($heap_owners($heap_graph(S), HOBJECT n_object) > 0)',
            '$objectprops_at(S.OBJECTPROPS, n_object) = (ppropertyslot_all*)',
            '$property_slot_at(ppropertyslot_all*, $ptascii("other")) = (ppropertyslot_other)',
            'ppropertyslot_other.STATE = PROP_VALUE (DIRECT (PINT 7))',
            '$tick_marker(S, porigin_property) = eps',
            '$tick_marker(S, porigin_hook) = eps',
            'ptickmarker.FREQUENCY = 1', 'ptickmarker.LINE = 14',
            '$tick_marker_valid(S, porigin, ptickmarker)', 'S.TICKCOUNT = 0',
            'S_global = $global_table_view(S)',
            '$lookup(S_global.ENV, $ptascii("object")) = (n_cell_object)',
            'S.STORE[n_cell_object] = DEFINED (POBJECT n_object)',
            '$lookup(S_global.ENV, $ptascii("n")) = (n_count)',
            'S.STORE[n_count] = DEFINED (PINT 0)', *valid('S'),
            'S_paused = $drive_steps(S, 0)',
            'S_paused = S[.COMPLETION = BUDGET]', *valid('S_paused'),
            'S_done = $drive(S, 4000)',
            '$drive(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
            'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
            'S_done.CURRENT = eps', 'S_done.FRAMES = eps', *valid('S_done'),
            'S_done.STORE[n_count] = DEFINED (PINT 2)',
            'n_object <- S_done.DESTRUCTION.CALLED',
            '~((HOBJECT n_object) <- S_done.ALLOCATIONS)',
            'S_done.TICKCOUNT = 0',
            'S_done.EVENTS = ' + output('G', 'T', '7', 'R', 'D', 'C', 'G', 'T', '7', '7', 'D', 'Z'),
        ],
    },
}

DERIVED_GUARDS = {name: 1 for name in review.CASES}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case, process_seconds=240) else 1)
