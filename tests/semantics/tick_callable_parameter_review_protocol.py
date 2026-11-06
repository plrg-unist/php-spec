#!/usr/bin/env python3
"""Reach an inherited method default's Tick with its lexical scope preserved."""
import argparse
import json

import fiber_state_review as review
import tick_callable_parameter_review_cases as sources


def output(*chunks):
    return '[' + ', '.join('OUTPUT $ptascii(' + json.dumps(chunk) + ')'
                           for chunk in chunks) + ']'


def valid(state):
    return [f'$call_descriptors_valid({state})',
            f'$heap_valid($heap_graph({state}))', f'$tick_state_valid({state})']


review.CASES = {
    'inherited-method-default-tick-keeps-lexical-scope-through-callback-abort': {
        'source': sources.SOURCE.decode(),
        'stage': 'S.TODO = (TICK porigin ptickmarker) :: ptask_tail* -- if S.CURRENT = (pcallcontext) -- if S.EVENTS = ' + output('F', 'A'),
        'checks': [
            'porigin_parent = PORIGIN 0 ([PCINDEX 2])',
            'porigin_child = PORIGIN 0 ([PCINDEX 3])',
            'porigin_method = PORIGIN 0 ([PCINDEX 2, PCFIELD 5, PCINDEX 2])',
            'porigin_closure = PORIGIN 0 ([PCINDEX 2, PCFIELD 5, PCINDEX 2, PCFIELD 4, PCINDEX 0, PCFIELD 6])',
            '$origin_child((porigin_closure), [PCFIELD 6, PCINDEX 0, PCFIELD 1, PCINDEX 0]) = (porigin)',
            '$class_method_origin(S.CLASSES, porigin_method) = (pmethoddesc)',
            'pmethoddesc.OWNER = porigin_parent', '~pmethoddesc.STATIC',
            'pmethoddesc.FUNCTION.DEFAULTS = [pdefault]',
            'pdefault.ORIGIN = porigin_closure', 'pdefault.KIND = PDDEFERRED',
            'pcallcontext.FUNCTION = porigin_closure',
            'pcallcontext.LEXICAL_CLASS = (porigin_parent)',
            'pcallcontext.CALLED_CLASS = (porigin_parent)', 'pcallcontext.RECEIVER = eps',
            'S_global = $global_table_view(S)',
            '$lookup(S_global.ENV, $ptascii("receiver")) = (n_cell_receiver)',
            'S.STORE[n_cell_receiver] = DEFINED (POBJECT n_receiver)',
            'S.OBJECTS[n_receiver] = INSTANCE porigin_child',
            '$objectprops_at(S.OBJECTPROPS, n_receiver) = (ppropertyslot_all*)',
            '$property_slot_at(ppropertyslot_all*, $ptascii("value")) = (ppropertyslot_value)',
            'ppropertyslot_value.STATE = PROP_VALUE (DIRECT (PINT 9))',
            '$lookup(S_global.ENV, $ptascii("a")) = (n_cell_a)',
            '$lookup(S_global.ENV, $ptascii("b")) = (n_cell_b)',
            'S.STORE[n_cell_a] = DEFINED (POBJECT n_a)',
            'S.STORE[n_cell_b] = DEFINED (POBJECT n_b)', 'n_a =/= n_b',
            'pcallcontext.TARGET = CLOSURE_TARGET n_a',
            '$closure_scope_at(S.CLOSURESCOPES, n_a) = (pclosurescope)',
            'pclosurescope.LEXICAL = porigin_parent /\\ pclosurescope.CALLED = porigin_parent',
            'pclosurescope.RECEIVER = eps',
            '$parameter_callable_record(S.PARAMETERCLOSURES, n_a) = (pparameterclosure)',
            'pparameterclosure.FUNCTION = porigin_method', 'pparameterclosure.INDEX = 0',
            'pparameterclosure.SCOPE = (porigin_parent)',
            '$parameter_callable_records_valid(S, S.PARAMETERCLOSURES)',
            'S.DEFAULTCACHE = eps', 'S.CONSTCONTEXT = eps',
            '$lookup(S_global.ENV, $ptascii("n")) = (n_count)',
            'S.STORE[n_count] = DEFINED (PINT 0)',
            'ptickmarker.FREQUENCY = 1', 'ptickmarker.LINE = 14',
            '$tick_marker_valid(S, porigin, ptickmarker)', 'S.TICKCOUNT = 0', *valid('S'),
            'S_paused = $drive_steps(S, 0)',
            'S_paused = S[.COMPLETION = BUDGET]', *valid('S_paused'),
            'S_done = $drive(S, 4000)',
            '$drive(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
            'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
            'S_done.CURRENT = eps', 'S_done.FRAMES = eps', *valid('S_done'),
            'S_done.STORE[n_count] = DEFINED (PINT 2)',
            'S_done.STORE[n_cell_receiver] = DEFINED (POBJECT n_receiver)',
            'S_done.OBJECTS[n_receiver] = S.OBJECTS[n_receiver]',
            '$objectprops_at(S_done.OBJECTPROPS, n_receiver) = (ppropertyslot_all*)',
            '$closure_scope_at(S_done.CLOSURESCOPES, n_a) = (pclosurescope)',
            'S_done.PARAMETERCLOSURES = S.PARAMETERCLOSURES',
            '$parameter_callable_records_valid(S_done, S_done.PARAMETERCLOSURES)',
            'S_done.DEFAULTCACHE = eps', 'S_done.TICKCOUNT = 0',
            'S_done.EVENTS = ' + output('F', 'A', 'T', '9', 'C', 'A', 'T', '9', 'Parent50', '2', 'Z'),
        ],
    },
}

DERIVED_GUARDS = {name: 0 for name in review.CASES}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case, process_seconds=240) else 1)
