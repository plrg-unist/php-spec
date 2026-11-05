#!/usr/bin/env python3
"""Reach a getter body Tick with its caller read still awaiting the result."""
import argparse
import json

import fiber_state_review as review
import tick_hook_review_cases as sources


def output(*chunks):
    return '[' + ', '.join('OUTPUT $ptascii(' + json.dumps(chunk) + ')'
                           for chunk in chunks) + ']'


def valid(state):
    return [f'$call_descriptors_valid({state})',
            f'$heap_valid($heap_graph({state}))', f'$tick_state_valid({state})']


review.CASES = {
    'getter-body-tick-abort-preserves-the-receiver-and-later-read': {
        'source': sources.CASES['review-getter-body-tick-callback-abort-preserves-backing-value'][0].decode(),
        'stage': 'S.TODO = (TICK porigin ptickmarker) :: ptask_tail* -- if S.CURRENT = (pcallcontext) -- if S.EVENTS = ' + output('T', 'T', 'G'),
        'checks': [
            'porigin = PORIGIN n pcpath',
            'porigin_class = PORIGIN n ([PCINDEX 4])',
            'porigin_property = PORIGIN n ([PCINDEX 4, PCFIELD 5, PCINDEX 1])',
            'porigin_hook = PORIGIN n ([PCINDEX 4, PCFIELD 5, PCINDEX 1, PCFIELD 4, PCINDEX 0])',
            '$origin_child((porigin_hook), [PCFIELD 5, PCINDEX 0, PCFIELD 1, PCINDEX 0]) = (porigin)',
            'S.CURRENT = (pcallcontext)',
            'pcallcontext.TARGET = PROPERTY_HOOK_TARGET ppropertyhook',
            'pcallcontext.FUNCTION = porigin_hook',
            'ppropertyhook.HOOK = porigin_hook',
            'n_object = ppropertyhook.OBJECT',
            'pcallcontext.RECEIVER = (n_object)',
            '$property_hook_function(S, ppropertyhook) = (pfunction)',
            'pfunction.ORIGIN = porigin_hook',
            '$property_hook_context_valid(S, pcallcontext)',
            '$class_named(S.CLASSNAMES, $ptascii("tickhook43")) = (porigin_class)',
            'S.OBJECTS[n_object] = INSTANCE porigin_class',
            'HOBJECT n_object <- S.ALLOCATIONS',
            '$objectprops_at(S.OBJECTPROPS, n_object) = (ppropertyslot*)',
            '$property_slot_at(ppropertyslot*, $ptascii("value")) = (ppropertyslot_value)',
            '$property_slot_at(ppropertyslot*, $ptascii("other")) = (ppropertyslot_other)',
            'ppropertyslot_value.STATE = PROP_VALUE (DIRECT (PINT 7))',
            'ppropertyslot_other.STATE = PROP_VALUE (DIRECT (PINT 9))',
            '$tick_marker(S, porigin_class) = eps',
            '$tick_marker(S, porigin_property) = eps',
            '$tick_marker(S, porigin_hook) = eps',
            'ptickmarker.FREQUENCY = 1', 'ptickmarker.LINE = 18',
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
            'S_done.EVENTS = ' + output('T', 'T', 'G', 'T', '9', 'C', 'T', 'G', 'T', '7', 'T', 'Z', 'T'),
        ],
    },
}

review.CASES['property-group-tick-abort-skips-the-pending-class-activation'] = {
    'source': sources.CASES['review-property-tick-abort-prevents-non-early-class-activation'][0].decode(),
    'stage': 'S.TODO = (TICK porigin ptickmarker) :: ptask_tail* -- if S.CURRENT = eps -- if S.EVENTS = eps',
    'checks': [
        'porigin = PORIGIN n pcpath',
        'pcpath = [PCINDEX 6, PCFIELD 5, PCINDEX 1]',
        'porigin_class = PORIGIN n ([PCINDEX 6])',
        'porigin_interface = PORIGIN n ([PCINDEX 5])',
        '$origin_node(S.SOURCES, porigin_class) = (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata)',
        'ptask_tail* = (ORIGIN_RETURN (porigin_class)) :: (STMT (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata)) :: ptask_after*',
        'S.ORIGIN = (porigin)',
        '$class_at(S.CLASSES, porigin_class) = (pclassdesc)',
        'pclassdesc.KIND = "class"', '~pclassdesc.EARLY',
        '$class_named(S.CLASSNAMES, $ptascii("tickpendinggroup43")) = eps',
        '$class_named(S.CLASSNAMES, $ptascii("tickgroupready43")) = (porigin_interface)',
        '$tick_marker(S, porigin_class) = eps',
        '$origin_child((porigin_class), [PCFIELD 5, PCINDEX 0]) = (porigin_constant)',
        '$tick_marker(S, porigin_constant) = eps',
        'ptickmarker.FREQUENCY = 1', 'ptickmarker.LINE = 25',
        '$tick_marker_valid(S, porigin, ptickmarker)', 'S.TICKCOUNT = 0',
        '$lookup(S.ENV, $ptascii("n")) = (n_count)',
        'S.STORE[n_count] = DEFINED (PINT 0)', *valid('S'),
        'S_paused = $drive_steps(S, 0)',
        'S_paused = S[.COMPLETION = BUDGET]', *valid('S_paused'),
        'S_done = $drive(S, 4000)',
        '$drive(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
        'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
        'S_done.CURRENT = eps', 'S_done.FRAMES = eps', *valid('S_done'),
        '$class_named(S_done.CLASSNAMES, $ptascii("tickpendinggroup43")) = eps',
        '$class_named(S_done.CLASSNAMES, $ptascii("tickgroupready43")) = (porigin_interface)',
        'S_done.STORE[n_count] = DEFINED (PINT 1)',
        'S_done.EVENTS = ' + output('T', '[25]', 'N', 'C', 'N'),
    ],
}

DERIVED_GUARDS = {name: 0 for name in review.CASES}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case, process_seconds=240) else 1)
