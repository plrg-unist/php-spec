#!/usr/bin/env python3
"""Reach const-created Closure body ticks with pending return or callback abort."""
import argparse
import json

import fiber_state_review as review
import tick_class_const_review_cases as sources


def output(*chunks):
    return '[' + ', '.join('OUTPUT $ptascii(' + json.dumps(chunk) + ')'
                           for chunk in chunks) + ']'


def valid(state):
    return [f'$call_descriptors_valid({state})',
            f'$heap_valid($heap_graph({state}))', f'$tick_state_valid({state})']


PAUSE = [
    'S_paused = $drive_steps(S, 0)',
    'S_paused = S[.COMPLETION = BUDGET]', *valid('S_paused'),
    'S_done = $drive(S, 4000)',
    '$drive(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
    'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
    'S_done.CURRENT = eps', 'S_done.FRAMES = eps', *valid('S_done'),
]


def body_tick(line, class_name):
    return [
        'porigin = PORIGIN n pcpath',
        'porigin_class = PORIGIN n ([PCINDEX 4])',
        'porigin_closure = PORIGIN n ([PCINDEX 4, PCFIELD 5, PCINDEX 0, PCFIELD 3, PCINDEX 1, PCFIELD 1])',
        '$origin_child((porigin_closure), [PCFIELD 6, PCINDEX 0, PCFIELD 1, PCINDEX 0]) = (porigin)',
        'S.CURRENT = (pcallcontext)', 'pcallcontext.FUNCTION = porigin_closure',
        '$class_at(S.CLASSES, porigin_class) = (pclassdesc)',
        'pclassdesc.KIND = "class"', 'pclassdesc.EARLY',
        f'$class_named(S.CLASSNAMES, $ptascii("{class_name}")) = (porigin_class)',
        '$class_constant_desc(pclassdesc.CONSTANTS, $ptascii("F")) = (pclassconstantdesc)',
        '~pclassconstantdesc.FOLDED',
        '$default_cache_at(S.CLASSCONSTANTCACHE, pclassconstantdesc.ORIGIN) = (pdefaultcache)',
        'pdefaultcache.VALUE = POBJECT n_object',
        'pdefaultcache.CLASS = PVCLOSURE n_object porigin_closure',
        'pcallcontext.TARGET = CLOSURE_TARGET n_object',
        'S.OBJECTS[n_object] = CONSTANTCLOSURE porigin_closure (REALCLOSURE porigin_closure eps eps)',
        '$constant_callable_record(S.CONSTANTCLOSURES, n_object) = (pconstantclosure)',
        '$constant_callable_record_valid(S, pconstantclosure)',
        'S.CLASSCONSTANTINIT = eps',
        '$tick_marker(S, porigin_class) = eps',
        '$origin_child((porigin_class), [PCFIELD 5, PCINDEX 0]) = (porigin_group)',
        '$tick_marker(S, porigin_group) = eps',
        'ptickmarker.FREQUENCY = 1', f'ptickmarker.LINE = {line}',
        '$tick_marker_valid(S, porigin, ptickmarker)', 'S.TICKCOUNT = 0',
        'S_global = $global_table_view(S)',
        '$lookup(S_global.ENV, $ptascii("n")) = (n_count)',
        'S.STORE[n_count] = DEFINED (PINT 2)',
        *valid('S'), *PAUSE,
        '$default_cache_at(S_done.CLASSCONSTANTCACHE, pclassconstantdesc.ORIGIN) = (pdefaultcache)',
        'S_done.OBJECTS[n_object] = S.OBJECTS[n_object]',
        '$constant_callable_record_valid(S_done, pconstantclosure)',
        f'$class_named(S_done.CLASSNAMES, $ptascii("{class_name}")) = (porigin_class)',
        'S_done.CLASSCONSTANTINIT = eps', 'S_done.TICKCOUNT = 0',
    ]


review.CASES = {
    'const-closure-body-tick-resumes-to-the-real-return-value': {
        'source': sources.CASES['review-invoked-const-closure-tick-reads-installed-sibling-constant'][0].decode(),
        'stage': 'S.TODO = (TICK porigin ptickmarker) :: ptask_tail* -- if S.CURRENT = (pcallcontext) -- if S.EVENTS = ' + output('T', 'T', 'V'),
        'checks': [
            *body_tick(13, 'tickconstinvoke41'),
            'S_done.STORE[n_count] = DEFINED (PINT 5)',
            'S_done.EVENTS = ' + output('T', 'T', 'V', 'T', '7', '9', 'T', 'Z', 'T'),
        ],
    },
    'const-closure-body-tick-abort-preserves-cache-and-skips-return': {
        'source': sources.CASES['review-invoked-const-closure-callback-abort-skips-return-output'][0].decode(),
        'stage': 'S.TODO = (TICK porigin ptickmarker) :: ptask_tail* -- if S.CURRENT = (pcallcontext) -- if S.EVENTS = ' + output('T', 'T', 'V'),
        'checks': [
            *body_tick(16, 'tickconstabort41'),
            'S_done.STORE[n_count] = DEFINED (PINT 6)',
            'S_done.EVENTS = ' + output('T', 'T', 'V', 'T', '7', 'C', 'T', '7', 'T', 'Z', 'T'),
        ],
    },
}

DERIVED_GUARDS = {name: 0 for name in review.CASES}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case, process_seconds=240) else 1)
