#!/usr/bin/env python3
"""Reach initialized plain properties before a committed-assignment Tick abort."""
import argparse
import json

import fiber_state_review as review
import tick_property_review_cases as sources


def output(*chunks):
    return '[' + ', '.join('OUTPUT $ptascii(' + json.dumps(chunk) + ')'
                           for chunk in chunks) + ']'


def valid(state):
    return [f'$call_descriptors_valid({state})',
            f'$heap_valid($heap_graph({state}))', f'$tick_state_valid({state})']


review.CASES = {
    'initialized-property-slots-survive-the-assignment-tick-callback-abort': {
        'source': sources.CASES['review-property-defaults-are-readable-before-assignment-tick-abort'][0].decode(),
        'stage': 'S.TODO = (TICK porigin ptickmarker) :: ptask_tail* -- if S.CURRENT = eps -- if S.EVENTS = ' + output('T'),
        'checks': [
            'porigin = PORIGIN n pcpath',
            'pcpath = [PCINDEX 5, PCFIELD 0, PCINDEX 0]',
            'porigin_class = PORIGIN n ([PCINDEX 4])',
            '$class_at(S.CLASSES, porigin_class) = (pclassdesc)',
            'pclassdesc.KIND = "class"', 'pclassdesc.EARLY',
            '$class_named(S.CLASSNAMES, $ptascii("tickproperty42")) = (porigin_class)',
            '$origin_child((porigin_class), [PCFIELD 5, PCINDEX 0]) = (porigin_property)',
            '$origin_node(S.SOURCES, porigin_property) = (NStmtProperty (SEQUENCE eps) phpType24 phpType18 phpType56 (SEQUENCE eps) metadata)',
            '$tick_marker(S, porigin_class) = eps',
            '$tick_marker(S, porigin_property) = eps',
            'ptickmarker.FREQUENCY = 1', 'ptickmarker.LINE = 18',
            '$tick_marker_valid(S, porigin, ptickmarker)', 'S.TICKCOUNT = 0',
            '$lookup(S.ENV, $ptascii("n")) = (n_count)',
            'S.STORE[n_count] = DEFINED (PINT 1)',
            '$lookup(S.ENV, $ptascii("object")) = (n_cell)',
            'S.STORE[n_cell] = DEFINED (POBJECT n_object)',
            'S.OBJECTS[n_object] = INSTANCE porigin_class',
            'HOBJECT n_object <- S.ALLOCATIONS',
            '$objectprops_at(S.OBJECTPROPS, n_object) = (ppropertyslot*)',
            '$property_slot_at(ppropertyslot*, $ptascii("first")) = (ppropertyslot_first)',
            '$property_slot_at(ppropertyslot*, $ptascii("second")) = (ppropertyslot_second)',
            'ppropertyslot_first.STATE = PROP_VALUE (DIRECT (PINT 1))',
            'ppropertyslot_second.STATE = PROP_VALUE (DIRECT (PINT 2))',
            *valid('S'),
            'S_paused = $drive_steps(S, 0)',
            'S_paused = S[.COMPLETION = BUDGET]', *valid('S_paused'),
            'S_done = $drive(S, 4000)',
            '$drive(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
            'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
            'S_done.CURRENT = eps', 'S_done.FRAMES = eps', *valid('S_done'),
            'S_done.STORE[n_count] = DEFINED (PINT 6)',
            'S_done.STORE[n_cell] = DEFINED (POBJECT n_object)',
            'S_done.OBJECTS[n_object] = INSTANCE porigin_class',
            'HOBJECT n_object <- S_done.ALLOCATIONS',
            '$objectprops_at(S_done.OBJECTPROPS, n_object) = (ppropertyslot*)',
            'S_done.EVENTS = ' + output('T', 'T', '2', 'C', 'T', '1', 'T', '2', 'T', 'Z', 'T'),
        ],
    },
}

DERIVED_GUARDS = {name: 0 for name in review.CASES}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case, process_seconds=240) else 1)
