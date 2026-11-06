#!/usr/bin/env python3
"""Escaped block SET Closures authenticate exact hook roles and captured values."""
import argparse
import json

import fiber_state_review as review
import tick_set_closure_sources as sources


def output(*chunks):
    return '[' + ', '.join('OUTPUT $ptascii(' + json.dumps(chunk) + ')'
                           for chunk in chunks) + ']'


def valid(state):
    return [f'$call_descriptors_valid({state})',
            f'$heap_valid($heap_graph({state}))', f'$tick_state_valid({state})']


review.CASES = {
    'escaped-block-setter-tick-keeps-role-snapshot-consumer-and-receiver-authority': {
        'source': sources.SOURCE.decode(),
        'stage': 'S.TODO = (TICK porigin ptickmarker) :: ptask_tail* -- if S.CURRENT = (pcallcontext) -- if S.EVENTS = ' + output('R', 'A', 'TickSetChildA53'),
        'checks': [
            'porigin_a = PORIGIN 0 ([PCINDEX 3])',
            'porigin_child_a = PORIGIN 0 ([PCINDEX 4])',
            'porigin_trait = PORIGIN 0 ([PCINDEX 5])',
            'porigin_b = PORIGIN 0 ([PCINDEX 6])',
            'porigin_child_b = PORIGIN 0 ([PCINDEX 7])',
            'porigin_property_a = PORIGIN 0 ([PCINDEX 3, PCFIELD 5, PCINDEX 1, PCFIELD 3, PCINDEX 0])',
            'porigin_get_a = PORIGIN 0 ([PCINDEX 3, PCFIELD 5, PCINDEX 1, PCFIELD 4, PCINDEX 0])',
            'porigin_set_a = PORIGIN 0 ([PCINDEX 3, PCFIELD 5, PCINDEX 1, PCFIELD 4, PCINDEX 1])',
            'porigin_property_trait = PORIGIN 0 ([PCINDEX 5, PCFIELD 2, PCINDEX 0, PCFIELD 3, PCINDEX 0])',
            'porigin_set_trait = PORIGIN 0 ([PCINDEX 5, PCFIELD 2, PCINDEX 0, PCFIELD 4, PCINDEX 0])',
            '$origin_child((porigin_set_a), [PCFIELD 5, PCINDEX 2, PCFIELD 0, PCFIELD 1]) = (porigin_closure_a)',
            '$origin_child((porigin_set_trait), [PCFIELD 5, PCINDEX 2, PCFIELD 0, PCFIELD 1]) = (porigin_closure_b)',
            '$origin_child((porigin_closure_a), [PCFIELD 6, PCINDEX 2, PCFIELD 1, PCINDEX 0]) = (porigin)',
            'S.CLASSES = [pclassdesc_a, pclassdesc_child_a, pclassdesc_trait, pclassdesc_b, pclassdesc_child_b]',
            '$hook_property_at(pclassdesc_a.PROPERTIES, porigin_property_a) = (ppropertydesc_a)',
            '$property_hook_origin(S, ppropertydesc_a) = (porigin_get_a)',
            '$property_set_origin(S, ppropertydesc_a) = (porigin_set_a)',
            '$hook_property_at(pclassdesc_trait.PROPERTIES, porigin_property_trait) = (ppropertydesc_trait)',
            '$property_set_origin(S, ppropertydesc_trait) = (porigin_set_trait)',
            '$property_hook_origin(S, ppropertydesc_trait) = eps',
            '$hook_property_at(pclassdesc_b.PROPERTIES, TRAIT_MEMBER_ORIGIN porigin_b porigin_property_trait) = (ppropertydesc_b)',
            '$property_set_origin(S, ppropertydesc_b) = (porigin_set_b)',
            'porigin_set_b = TRAIT_ORIGIN porigin_b porigin_set_trait ptbytes_set',
            'ptbytes_set = $property_set_name($ptascii("value"))',
            '$property_hook_origin(S, ppropertydesc_b) = eps',
            '$closure_source_class(S, porigin_closure_a) = (porigin_a)',
            '$closure_source_class(S, porigin_closure_b) = (porigin_trait)',
            '$trait_closure_source_matches(S, porigin_closure_b, porigin_b)',
            '$class_link_at(S.LINKEDPARENTS, porigin_child_a) = (SOURCE_PARENT porigin_a)',
            '$class_link_at(S.LINKEDPARENTS, porigin_child_b) = (SOURCE_PARENT porigin_b)',
            'S_global = $global_table_view(S)',
            '$lookup(S_global.ENV, $ptascii("a")) = (n_cell_a)',
            '$lookup(S_global.ENV, $ptascii("b")) = (n_cell_b)',
            'S.STORE[n_cell_a] = DEFINED (POBJECT n_a)',
            'S.STORE[n_cell_b] = DEFINED (POBJECT n_b)', 'n_a =/= n_b',
            'S.OBJECTS[n_a] = REALCLOSURE porigin_closure_a ([(DIRECT (PINT 5))]) eps',
            'S.OBJECTS[n_b] = REALCLOSURE porigin_closure_b ([(DIRECT (PINT 9))]) eps',
            '$lookup(S.ENV, $ptascii("value")) = (n_capture)',
            'S.STORE[n_capture] = DEFINED (PINT 5)',
            '$closure_scope_at(S.CLOSURESCOPES, n_a) = (pclosurescope_a)',
            '$closure_scope_at(S.CLOSURESCOPES, n_b) = (pclosurescope_b)',
            'pclosurescope_a.LEXICAL = porigin_a', 'pclosurescope_a.CALLED = porigin_child_a',
            'pclosurescope_b.LEXICAL = porigin_b', 'pclosurescope_b.CALLED = porigin_child_b',
            'pclosurescope_a.RECEIVER = (n_left)', 'pclosurescope_b.RECEIVER = (n_right)',
            'pcallcontext.FUNCTION = porigin_closure_a',
            'pcallcontext.TARGET = CLOSURE_TARGET n_a',
            'pcallcontext.LEXICAL_CLASS = (porigin_a)',
            'pcallcontext.CALLED_CLASS = (porigin_child_a)', 'pcallcontext.RECEIVER = (n_left)',
            'S.OBJECTS[n_left] = INSTANCE porigin_child_a',
            'S.OBJECTS[n_right] = INSTANCE porigin_child_b',
            '$objectprops_at(S.OBJECTPROPS, n_left) = (ppropertyslot_left*)',
            '$property_slot_at(ppropertyslot_left*, $ptascii("value")) = (ppropertyslot_value_a)',
            'ppropertyslot_value_a.STATE = PROP_VALUE (DIRECT (PINT 5))',
            '$objectprops_at(S.OBJECTPROPS, n_right) = (ppropertyslot_right*)',
            '$property_slot_at(ppropertyslot_right*, $ptascii("value")) = (ppropertyslot_value_b)',
            'ppropertyslot_value_b.STATE = PROP_VALUE (DIRECT (PINT 9))',
            '$lookup(S_global.ENV, $ptascii("left")) = eps',
            '$lookup(S_global.ENV, $ptascii("right")) = eps',
            'S.FRAMES = [pframe_main]', 'pframe_main.CONTEXT = eps',
            '$lookup(S_global.ENV, $ptascii("n")) = (n_count)',
            '$lookup(S_global.ENV, $ptascii("seen")) = (n_seen)',
            'S.STORE[n_count] = DEFINED (PINT 0)', 'S.STORE[n_seen] = DEFINED (PINT 10)',
            'ptickmarker.FREQUENCY = 1', 'ptickmarker.LINE = 16',
            '$tick_marker_valid(S, porigin, ptickmarker)', 'S.TICKCOUNT = 0',
            'S_missing = S[.CLASSES = [pclassdesc_a, pclassdesc_child_a, pclassdesc_trait, pclassdesc_b[.PROPERTIES = eps], pclassdesc_child_b]]',
            '$closure_source_class(S_missing, porigin_closure_a) = (porigin_a)',
            '$closure_source_class(S_missing, porigin_closure_b) = (porigin_trait)',
            '~$trait_closure_source_matches(S_missing, porigin_closure_b, porigin_b)',
            *valid('S'),
            'S_paused = $drive_steps(S, 0)',
            'S_paused = S[.COMPLETION = BUDGET]', *valid('S_paused'),
            'S_done = $drive(S, 4000)',
            '$drive(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
            'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
            'S_done.CURRENT = eps', 'S_done.FRAMES = eps', *valid('S_done'),
            'S_done.STORE[n_count] = DEFINED (PINT 2)',
            'S_done.STORE[n_seen] = DEFINED (PINT 18)',
            'n_left <- S_done.DESTRUCTION.CALLED', 'n_right <- S_done.DESTRUCTION.CALLED',
            '~((HOBJECT n_left) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_right) <- S_done.ALLOCATIONS)', 'S_done.TICKCOUNT = 0',
            'S_done.EVENTS = ' + output('R', 'A', 'TickSetChildA53', 'T', '10', 'C', 'B', 'TickSetChildB53', 'T', '18', '9', '2', 'a', 'b', 'Z'),
        ],
    },
}

DERIVED_GUARDS = {name: 1 for name in review.CASES}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case, process_seconds=240) else 1)
