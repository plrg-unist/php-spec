#!/usr/bin/env python3
"""Reach an authenticated semicolon namespace header before its body task."""
import argparse
import json

import fiber_state_review as review
import tick_namespace_review_cases as sources


def ascii_text(value):
    return '$ptascii(' + json.dumps(value) + ')'


def output(*chunks):
    return '[' + ', '.join('OUTPUT ' + ascii_text(chunk) for chunk in chunks) + ']'


def valid(state):
    return [f'$call_descriptors_valid({state})',
            f'$heap_valid($heap_graph({state}))', f'$tick_state_valid({state})']


review.CASES = {
    'semicolon-namespace-header-tick-aborts-before-the-pending-body': {
        'source': sources.CASES['review-unbracketed-header-line-and-abort-before-pending-body-class'][0].decode(),
        'stage': 'S.TODO = (TICK porigin ptickmarker) :: ptask_tail* -- if S.CURRENT = eps -- if S.EVENTS = eps',
        'checks': [
            'porigin = PORIGIN n pcpath', 'pcpath = [PCINDEX 1]',
            '$origin_node(S.SOURCES, porigin) = (statement)',
            'statement = NStmtNamespace phpType44 phpType23 metadata',
            '$plstyle(metadata) = 1', '$source_line(metadata) = 23',
            '$plcompileline(statement) = 24',
            'S.ORIGIN = (porigin)',
            'porigin_first = PORIGIN n ([PCINDEX 0])',
            '$tick_marker(S, porigin_first) = eps',
            'porigin_barrier = PORIGIN n ([PCINDEX 0, PCFIELD 1, PCINDEX 6])',
            'porigin_pending = PORIGIN n ([PCINDEX 1, PCFIELD 1, PCINDEX 0])',
            '$origin_node(S.SOURCES, porigin_pending) = (statement_pending)',
            'ptask_tail* = (ORIGIN_RETURN porigin_saved?) :: (AT porigin_pending (STMT statement_pending)) :: ptask_after*',
            '$class_named(S.CLASSNAMES, ' + ascii_text(r'first46\barrier46') + ') = (porigin_barrier)',
            '$class_at(S.CLASSES, porigin_barrier) = (pclassdesc)',
            '~pclassdesc.EARLY',
            '$class_named(S.CLASSNAMES, ' + ascii_text(r'second46\pending46') + ') = eps',
            '$class_at(S.CLASSES, porigin_pending) = (pclassdesc_pending)',
            '~pclassdesc_pending.EARLY',
            'ptickmarker.FREQUENCY = 1', 'ptickmarker.LINE = 24',
            '$tick_marker_valid(S, porigin, ptickmarker)', 'S.TICKCOUNT = 0',
            '$lookup(S.ENV, $ptascii("n")) = (n_count)',
            'S.STORE[n_count] = DEFINED (PINT 0)', *valid('S'),
            'S_paused = $drive_steps(S, 0)',
            'S_paused = S[.COMPLETION = BUDGET]', *valid('S_paused'),
            'S_done = $drive(S, 4000)',
            '$drive(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
            'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
            'S_done.CURRENT = eps', 'S_done.FRAMES = eps', *valid('S_done'),
            '$class_named(S_done.CLASSNAMES, ' + ascii_text(r'first46\barrier46') + ') = (porigin_barrier)',
            '$class_named(S_done.CLASSNAMES, ' + ascii_text(r'second46\pending46') + ') = eps',
            'S_done.STORE[n_count] = DEFINED (PINT 1)',
            'S_done.EVENTS = ' + output('T', '[24]', 'N', 'C', 'N'),
        ],
    },
}

DERIVED_GUARDS = {name: 0 for name in review.CASES}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case, process_seconds=240) else 1)
