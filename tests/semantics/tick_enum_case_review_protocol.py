#!/usr/bin/env python3
"""Reach genuine EnumCase ticks before the pending enum declaration executes."""
import argparse
import json

import fiber_state_review as review
import tick_enum_case_review_cases as sources


def output(*chunks):
    return '[' + ', '.join('OUTPUT $ptascii(' + json.dumps(chunk) + ')'
                           for chunk in chunks) + ']'


def valid(state):
    return [f'$call_descriptors_valid({state})',
            f'$heap_valid($heap_graph({state}))', f'$tick_state_valid({state})']


PAUSE = [
    'S_paused = $drive_steps(S, 0)', 'S_paused.COMPLETION = BUDGET',
    'S_paused.TODO = S.TODO', 'S_paused.CURRENT = S.CURRENT',
    'S_paused.FRAMES = S.FRAMES', 'S_paused.CLASSES = S.CLASSES',
    'S_paused.CLASSNAMES = S.CLASSNAMES',
    'S_paused.DECLARATIONS = S.DECLARATIONS',
    'S_paused.TICKCOUNT = S.TICKCOUNT', 'S_paused.EVENTS = S.EVENTS',
    *valid('S_paused'), 'S_done = $drive(S, 4000)',
    '$drive(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
    'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
    'S_done.CURRENT = eps', 'S_done.FRAMES = eps', *valid('S_done'),
]


def case_prefix(index, line, class_name):
    return [
        'porigin = PORIGIN n pcpath',
        f'pcpath = [PCINDEX {index}, PCFIELD 4, PCINDEX 1]',
        f'porigin_enum = PORIGIN n ([PCINDEX {index}])',
        '$origin_node(S.SOURCES, porigin_enum) = (NStmtEnum phpType14 phpType3 phpType50 phpType42 phpType23 metadata)',
        'ptask_tail* = (ORIGIN_RETURN (porigin_enum)) :: (STMT (NStmtEnum phpType14 phpType3 phpType50 phpType42 phpType23 metadata)) :: ptask_after*',
        'S.ORIGIN = (porigin)',
        '$class_at(S.CLASSES, porigin_enum) = (pclassdesc)',
        'pclassdesc.KIND = "enum"', '~pclassdesc.EARLY',
        f'$class_named(S.CLASSNAMES, $ptascii("{class_name}")) = eps',
        '$enum_case_descriptor(S, porigin) = (pclassconstantdesc)',
        'pclassconstantdesc.OWNER = porigin_enum',
        'pclassconstantdesc.INITIALIZER = porigin',
        'pclassconstantdesc.NAME = $ptascii("A")',
        'ptickmarker.FREQUENCY = 1', f'ptickmarker.LINE = {line}',
        '$tick_marker_valid(S, porigin, ptickmarker)',
        '$tick_marker(S, porigin_enum) = eps',
        '$origin_child((porigin_enum), [PCFIELD 4, PCINDEX 2]) = (porigin_case_b)',
        '$tick_marker(S, porigin_case_b) = eps',
        '$lookup(S.ENV, $ptascii("n")) = (n_count)',
        'S.STORE[n_count] = DEFINED (PINT 0)',
        'S.CLASSCONSTANTCACHE = eps', 'S.CLASSCONSTANTINIT = eps',
        'S.TICKCOUNT = 0', 'S.FRAMES = eps', *valid('S'),
    ]


review.CASES = {
    'backed-case-prefix-keeps-enum-uninstalled-until-after-the-callback': {
        'source': sources.CASES['review-backed-case-tick-precedes-installation-and-uses-value-line'][0].decode(),
        'stage': 'S.TODO = (TICK porigin ptickmarker) :: ptask_tail* -- if S.CURRENT = eps -- if S.EVENTS = eps',
        'checks': [
            *case_prefix(4, 19, 'tickavailable40'), *PAUSE,
            '$class_named(S_done.CLASSNAMES, $ptascii("tickavailable40")) = (porigin_enum)',
            'S_done.STORE[n_count] = DEFINED (PINT 3)',
            'S_done.TICKCOUNT = 0',
            'S_done.EVENTS = ' + output('T', '[19]', 'N', '7', 'T', 'Z', 'T'),
        ],
    },
    'case-prefix-callback-abort-skips-the-pending-enum-declaration': {
        'source': sources.CASES['review-case-callback-abort-prevents-enum-installation'][0].decode(),
        'stage': 'S.TODO = (TICK porigin ptickmarker) :: ptask_tail* -- if S.CURRENT = eps -- if S.EVENTS = eps',
        'checks': [
            *case_prefix(5, 18, 'tickaborted40'), *PAUSE,
            '$class_named(S_done.CLASSNAMES, $ptascii("tickaborted40")) = eps',
            'S_done.STORE[n_count] = DEFINED (PINT 1)',
            'S_done.CLASSCONSTANTCACHE = eps', 'S_done.CLASSCONSTANTINIT = eps',
            'S_done.TICKCOUNT = 0',
            'S_done.EVENTS = ' + output('T', 'C', 'N'),
        ],
    },
}

DERIVED_GUARDS = {name: 0 for name in review.CASES}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case, process_seconds=240) else 1)
