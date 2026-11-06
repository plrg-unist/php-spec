#!/usr/bin/env python3
"""Reach a received default Closure's Tick after its global write commits."""
import argparse
import json

import fiber_state_review as review
import tick_parameter_review_cases as sources


def output(*chunks):
    return '[' + ', '.join('OUTPUT $ptascii(' + json.dumps(chunk) + ')'
                           for chunk in chunks) + ']'


def valid(state):
    return [f'$call_descriptors_valid({state})',
            f'$heap_valid($heap_graph({state}))', f'$tick_state_valid({state})']


review.CASES = {
    'received-default-closure-tick-sees-write-before-abort-and-fresh-retry': {
        'source': sources.SOURCE.decode(),
        'stage': 'S.TODO = (TICK porigin ptickmarker) :: ptask_tail* -- if S.CURRENT = (pcallcontext) -- if S.EVENTS = ' + output('F'),
        'checks': [
            'porigin_make = PORIGIN 0 ([PCINDEX 3])',
            'porigin_closure = PORIGIN 0 ([PCINDEX 3, PCFIELD 3, PCINDEX 0, PCFIELD 6])',
            '$origin_child((porigin_closure), [PCFIELD 6, PCINDEX 1, PCFIELD 1, PCINDEX 0]) = (porigin)',
            'pcallcontext.FUNCTION = porigin_closure',
            '$function_at(S.FUNCTIONS, porigin_make) = (pfunction)',
            'pfunction.DEFAULTS = [pdefault]',
            'pdefault.ORIGIN = porigin_closure', 'pdefault.KIND = PDDEFERRED',
            '$tick_marker(S, porigin_make) = eps',
            'S_global = $global_table_view(S)',
            '$lookup(S_global.ENV, $ptascii("a")) = (n_cell_a)',
            '$lookup(S_global.ENV, $ptascii("b")) = (n_cell_b)',
            'S.STORE[n_cell_a] = DEFINED (POBJECT n_a)',
            'S.STORE[n_cell_b] = DEFINED (POBJECT n_b)', 'n_a =/= n_b',
            'pcallcontext.TARGET = CLOSURE_TARGET n_a',
            'S.OBJECTS[n_a] = CONSTANTCLOSURE porigin_closure (REALCLOSURE porigin_closure eps eps)',
            'S.OBJECTS[n_b] = CONSTANTCLOSURE porigin_closure (REALCLOSURE porigin_closure eps eps)',
            '$parameter_callable_record(S.PARAMETERCLOSURES, n_a) = (pparameterclosure_a)',
            '$parameter_callable_record(S.PARAMETERCLOSURES, n_b) = (pparameterclosure_b)',
            'pparameterclosure_a.FUNCTION = porigin_make /\\ pparameterclosure_b.FUNCTION = porigin_make',
            'pparameterclosure_a.INDEX = 0 /\\ pparameterclosure_b.INDEX = 0',
            '$parameter_callable_records_valid(S, S.PARAMETERCLOSURES)',
            'S.DEFAULTCACHE = eps', 'S.CONSTCONTEXT = eps',
            '$lookup(S_global.ENV, $ptascii("v")) = (n_value)',
            'S.STORE[n_value] = DEFINED (PINT 9)',
            '$lookup(S_global.ENV, $ptascii("n")) = (n_count)',
            'S.STORE[n_count] = DEFINED (PINT 0)',
            'ptickmarker.FREQUENCY = 1', 'ptickmarker.LINE = 12',
            '$tick_marker_valid(S, porigin, ptickmarker)', 'S.TICKCOUNT = 0',
            *valid('S'),
            'S_paused = $drive_steps(S, 0)',
            'S_paused = S[.COMPLETION = BUDGET]', *valid('S_paused'),
            'S_done = $drive(S, 4000)',
            '$drive(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
            'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
            'S_done.CURRENT = eps', 'S_done.FRAMES = eps', *valid('S_done'),
            'S_done.STORE[n_value] = DEFINED (PINT 9)',
            'S_done.STORE[n_count] = DEFINED (PINT 2)',
            'S_done.OBJECTS[n_a] = S.OBJECTS[n_a]',
            'S_done.OBJECTS[n_b] = S.OBJECTS[n_b]',
            'S_done.PARAMETERCLOSURES = S.PARAMETERCLOSURES',
            '$parameter_callable_records_valid(S_done, S_done.PARAMETERCLOSURES)',
            'S_done.DEFAULTCACHE = eps', 'S_done.TICKCOUNT = 0',
            'S_done.EVENTS = ' + output('F', 'T', '9', 'C', 'T', '9', '7', '2', 'Z'),
        ],
    },
}

DERIVED_GUARDS = {name: 0 for name in review.CASES}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case, process_seconds=240) else 1)
