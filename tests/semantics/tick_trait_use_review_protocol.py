#!/usr/bin/env python3
"""Reach the imported method's source Tick through callback abort and retry."""
import argparse
import json

import fiber_state_review as review
import tick_trait_use_review_cases as sources


def output(*chunks):
    return '[' + ', '.join('OUTPUT $ptascii(' + json.dumps(chunk) + ')'
                           for chunk in chunks) + ']'


def valid(state):
    return [f'$call_descriptors_valid({state})',
            f'$heap_valid($heap_graph({state}))', f'$tick_state_valid({state})']


review.CASES = {
    'imported-method-source-tick-preserves-receiver-through-abort-and-retry': {
        'source': sources.CASES['review-imported-method-tick-abort-preserves-receiver-and-retry'][0].decode(),
        'stage': 'S.TODO = (TICK porigin ptickmarker) :: ptask_tail* -- if S.CURRENT = (pcallcontext) -- if S.EVENTS = ' + output('T', 'T', 'M'),
        'checks': [
            'porigin = PORIGIN n pcpath',
            'porigin_trait = PORIGIN n ([PCINDEX 4])',
            'porigin_class = PORIGIN n ([PCINDEX 5])',
            'porigin_method = PORIGIN n ([PCINDEX 4, PCFIELD 2, PCINDEX 0])',
            '$origin_child((porigin_method), [PCFIELD 6, PCINDEX 0, PCFIELD 1, PCINDEX 0]) = (porigin)',
            'S.CURRENT = (pcallcontext)',
            'pcallcontext.FUNCTION = TRAIT_ORIGIN porigin_class porigin_method ($ptascii("run"))',
            '$origin_source(pcallcontext.FUNCTION) = porigin_method',
            'pcallcontext.TARGET = METHOD_TARGET n_object pcallcontext.FUNCTION',
            'pcallcontext.RECEIVER = (n_object)',
            'pcallcontext.LEXICAL_CLASS = (porigin_class)',
            'pcallcontext.CALLED_CLASS = (porigin_class)',
            '$class_at(S.CLASSES, porigin_class) = (pclassdesc)',
            'pclassdesc.KIND = "class"', '~pclassdesc.EARLY',
            '$class_named(S.CLASSNAMES, $ptascii("tickuse44")) = (porigin_class)',
            '$class_named(S.CLASSNAMES, $ptascii("tickmethod44")) = (porigin_trait)',
            'S.OBJECTS[n_object] = INSTANCE porigin_class',
            'HOBJECT n_object <- S.ALLOCATIONS',
            '$objectprops_at(S.OBJECTPROPS, n_object) = (ppropertyslot*)',
            '$property_slot_at(ppropertyslot*, $ptascii("value")) = (ppropertyslot_value)',
            '$property_slot_at(ppropertyslot*, $ptascii("other")) = (ppropertyslot_other)',
            'ppropertyslot_value.STATE = PROP_VALUE (DIRECT (PINT 7))',
            'ppropertyslot_other.STATE = PROP_VALUE (DIRECT (PINT 9))',
            '$origin_child((porigin_class), [PCFIELD 5, PCINDEX 0]) = (porigin_use)',
            '$tick_marker(S, porigin_use) = eps',
            '$tick_marker(S, porigin_class) = eps',
            '$tick_marker(S, porigin_trait) = eps',
            '$tick_marker(S, porigin_method) = eps',
            'ptickmarker.FREQUENCY = 1', 'ptickmarker.LINE = 16',
            '$tick_marker_valid(S, porigin, ptickmarker)', 'S.TICKCOUNT = 0',
            'S_global = $global_table_view(S)',
            '$lookup(S_global.ENV, $ptascii("n")) = (n_count)',
            'S.STORE[n_count] = DEFINED (PINT 2)',
            '$lookup(S_global.ENV, $ptascii("object")) = (n_cell)',
            'S.STORE[n_cell] = DEFINED (POBJECT n_object)', *valid('S'),
            'S_paused = $drive_steps(S, 0)',
            'S_paused = S[.COMPLETION = BUDGET]', *valid('S_paused'),
            'S_done = $drive(S, 4000)',
            '$drive(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
            'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
            'S_done.CURRENT = eps', 'S_done.FRAMES = eps', *valid('S_done'),
            'S_done.STORE[n_count] = DEFINED (PINT 7)',
            'S_done.STORE[n_cell] = DEFINED (POBJECT n_object)',
            'S_done.OBJECTS[n_object] = INSTANCE porigin_class',
            'HOBJECT n_object <- S_done.ALLOCATIONS',
            '$objectprops_at(S_done.OBJECTPROPS, n_object) = (ppropertyslot*)',
            'S_done.EVENTS = ' + output('T', 'T', 'M', 'T', '9', 'C', 'T', 'M', 'T', '7', 'T', 'Z', 'T'),
        ],
    },
}

DERIVED_GUARDS = {name: 0 for name in review.CASES}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case, process_seconds=240) else 1)
