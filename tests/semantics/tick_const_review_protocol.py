#!/usr/bin/env python3
"""Reach one complete constant-group Tick before callback observation or abort."""
import argparse
import json

import fiber_state_review as review
import tick_const_review_cases as sources


def output(*chunks):
    return '[' + ', '.join('OUTPUT $ptascii(' + json.dumps(chunk) + ')'
                           for chunk in chunks) + ']'


def valid(state):
    return [f'$call_descriptors_valid({state})',
            f'$heap_valid($heap_graph({state}))', f'$tick_state_valid({state})']


PAUSE = [
    'S_paused = $drive_steps(S, 0)', 'S_paused.COMPLETION = BUDGET',
    'S_paused.TODO = S.TODO', 'S_paused.CURRENT = S.CURRENT',
    'S_paused.FRAMES = S.FRAMES', 'S_paused.USERCONSTANTS = S.USERCONSTANTS',
    'S_paused.CONSTCONTEXT = S.CONSTCONTEXT',
    'S_paused.TICKCOUNT = S.TICKCOUNT', 'S_paused.EVENTS = S.EVENTS',
    *valid('S_paused'), 'S_done = $drive(S, 4000)',
    '$drive(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
    'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
    'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
    'S_done.CONSTCONTEXT = eps', *valid('S_done'),
]

name = 'review-constant-closure-order-keeps-final-initializer-marker-line'
review.CASES = {
    'complete-closure-group-uses-last-declaration-receipt-and-one-marker': {
        'source': sources.CASES[name][0].decode(),
        'stage': 'S.TODO = (TICK porigin ptickmarker) :: ptask_tail* -- if S.CURRENT = eps -- if S.EVENTS = ' + output('[4]'),
        'checks': [
            'porigin = PORIGIN n pcpath', 'pcpath = [PCINDEX 3]',
            '$origin_node(S.SOURCES, porigin) = (NStmtConst (SEQUENCE eps) (SEQUENCE ([phpType46_first, phpType46_last])) metadata)',
            '$origin_child((porigin), [PCFIELD 1, PCINDEX 0]) = (porigin_first)',
            '$origin_child((porigin), [PCFIELD 1, PCINDEX 1]) = (porigin_last)',
            '$constant_declaration(S, porigin_first) = (($ptascii("TickFirst38"), 7))',
            '$constant_declaration(S, porigin_last) = (($ptascii("TickLast38"), 10))',
            '$tick_marker(S, porigin_first) = eps', '$tick_marker(S, porigin_last) = eps',
            'ptickmarker.FREQUENCY = 1', 'ptickmarker.LINE = 10',
            '$tick_marker_valid(S, porigin, ptickmarker)',
            '$origin_child((porigin_first), [PCFIELD 1, PCFIELD 6, PCINDEX 0]) = (porigin_declare_first)',
            '$origin_child((porigin_last), [PCFIELD 1, PCFIELD 6, PCINDEX 0]) = (porigin_declare_last)',
            '$tick_marker(S, porigin_declare_first) = (ptickmarker_first)',
            '$tick_marker(S, porigin_declare_last) = (ptickmarker_last)',
            'ptickmarker_first.FREQUENCY = 2', 'ptickmarker_last.FREQUENCY = 1',
            'S.USERCONSTANTS = [puserconstant_first, puserconstant_last]',
            'puserconstant_first.NAME = $ptascii("TickFirst38")',
            'puserconstant_last.NAME = $ptascii("TickLast38")',
            'puserconstant_first.ORIGIN = porigin_first', 'puserconstant_last.ORIGIN = porigin_last',
            'puserconstant_first.VALUE = POBJECT n_first',
            'puserconstant_last.VALUE = POBJECT n_last',
            '$origin_child((porigin_first), [PCFIELD 1]) = (porigin_site_first)',
            '$origin_child((porigin_last), [PCFIELD 1]) = (porigin_site_last)',
            'puserconstant_first.CLASS = PVCLOSURE n_first porigin_site_first',
            'puserconstant_last.CLASS = PVCLOSURE n_last porigin_site_last',
            'S.CONSTCONTEXT = eps', 'S.FRAMES = eps', 'S.TICKCOUNT = 0',
            # Derived missing-receipt guard on this real source plan. Retain its
            # names/redirects while removing the compiled operand receipt map.
            '$code_at(S.CODE, n) = (pcode)',
            '$source_unit(S.SOURCES, n) = (pcunit)',
            'T_missing = $tick_code_plan(pcunit.AST, eps, pcode.NAMES, pcode.REDIRECTS)',
            'T_missing.DEPENDENCY = ("tick global constant declaration descriptor")',
            *valid('S'), *PAUSE,
            'S_done.USERCONSTANTS = S.USERCONSTANTS',
            'S_done.EVENTS = ' + output('[4]', '[10]', 'Z', '[11]'),
        ],
    },
}

name = 'review-constant-group-commits-before-tick-aborts-later-declaration'
review.CASES['group-commits-both-values-before-callback-aborts-next-declaration'] = {
    'source': sources.CASES[name][0].decode(),
    'stage': 'S.TODO = (TICK porigin ptickmarker) :: ptask_tail* -- if S.CURRENT = eps -- if S.EVENTS = eps -- if |S.USERCONSTANTS| = 2',
    'checks': [
        'porigin = PORIGIN n pcpath', 'pcpath = [PCINDEX 6]',
        '$origin_node(S.SOURCES, porigin) = (NStmtConst (SEQUENCE eps) (SEQUENCE ([phpType46_A, phpType46_B])) metadata)',
        '$origin_child((porigin), [PCFIELD 1, PCINDEX 0]) = (porigin_A)',
        '$origin_child((porigin), [PCFIELD 1, PCINDEX 1]) = (porigin_B)',
        '$tick_marker(S, porigin_A) = eps', '$tick_marker(S, porigin_B) = eps',
        'ptickmarker.FREQUENCY = 1', 'ptickmarker.LINE = 22',
        '$tick_marker_valid(S, porigin, ptickmarker)',
        'S.USERCONSTANTS = [puserconstant_A, puserconstant_B]',
        'puserconstant_A.NAME = $ptascii("TickA38")',
        'puserconstant_B.NAME = $ptascii("TickB38")',
        'puserconstant_A.ORIGIN = porigin_A', 'puserconstant_B.ORIGIN = porigin_B',
        'puserconstant_A.VALUE = PINT 1', 'puserconstant_B.VALUE = PINT 2',
        '$user_constant_at(S.USERCONSTANTS, $ptascii("TickLate38")) = eps',
        'porigin_late = PORIGIN n ([PCINDEX 7])',
        '$origin_node(S.SOURCES, porigin_late) = (statement_late)',
        'ptask_tail* = (ORIGIN_RETURN porigin_restore?) :: (AT porigin_late (STMT statement_late)) :: ptask_after*',
        '$lookup(S.ENV, $ptascii("count")) = (n_count)',
        'S.STORE[n_count] = DEFINED (PINT 1)',
        'S.CONSTCONTEXT = eps', 'S.FRAMES = eps', 'S.TICKCOUNT = 0',
        *valid('S'), *PAUSE,
        'S_done.USERCONSTANTS = S.USERCONSTANTS',
        '$user_constant_at(S_done.USERCONSTANTS, $ptascii("TickLate38")) = eps',
        'S_done.EVENTS = ' + output('1', '2', 'C', '1', '2', 'N', 'Z'),
    ],
}

DERIVED_GUARDS = {
    'complete-closure-group-uses-last-declaration-receipt-and-one-marker': 1,
    'group-commits-both-values-before-callback-aborts-next-declaration': 0,
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case, process_seconds=240) else 1)
