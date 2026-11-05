#!/usr/bin/env python3
"""Reach canonical elided-branch plans and a retained effect under a CONST result."""
import argparse
import json

import fiber_state_review as review
import tick_elision_review_cases as sources


def output(raw):
    return '[' + ', '.join('OUTPUT $ptascii(' + json.dumps(chr(byte)) + ')'
                           for byte in raw) + ']'


def valid(state):
    return [f'$call_descriptors_valid({state})',
            f'$heap_valid($heap_graph({state}))', f'$tick_state_valid({state})']


PAUSE = [
    'S_paused = $drive_steps(S, 0)', 'S_paused.COMPLETION = BUDGET',
    'S_paused.TODO = S.TODO', 'S_paused.CURRENT = S.CURRENT',
    'S_paused.FRAMES = S.FRAMES', 'S_paused.TICKCOUNT = S.TICKCOUNT',
    'S_paused.EVENTS = S.EVENTS', *valid('S_paused'),
    'S_done = $drive(S, 4000)',
    '$drive(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
    'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
    'S_done.CURRENT = eps', 'S_done.FRAMES = eps', *valid('S_done'),
]

name = 'review-array-prepass-erases-unselected-diagnostic'
review.CASES = {
    'prepass-selected-arm-omits-unselected-diagnostic-and-markers': {
        'source': sources.CASES[name][0].decode(),
        'stage': 'S.CODE = [pcode] -- if S.EVENTS = eps',
        'checks': [
            'pcpath_ternary = [PCINDEX 2, PCFIELD 1, PCINDEX 0, PCFIELD 0, PCFIELD 1, PCFIELD 0, PCINDEX 0, PCFIELD 1]',
            'pcpath_selected = pcpath_ternary ++ [PCFIELD 1]',
            'pcpath_bad = pcpath_ternary ++ [PCFIELD 2, PCFIELD 0]',
            '$origin_node(S.SOURCES, PORIGIN pcode.UNIT pcpath_ternary) = (NExprTernary expression_cond phpType5 expression_false metadata)',
            '$origin_node(S.SOURCES, PORIGIN pcode.UNIT pcpath_bad) = (NExprClosure phpType14 phpType4_1 phpType4_2 phpType16 phpType21 phpType18 (SEQUENCE statement*) metadata_bad)',
            '$code_redirect(pcode.REDIRECTS, pcpath_ternary) = ((pcpath_selected, false))',
            '$code_expression(pcode.EXPRESSIONS, pcpath_ternary) = ((z, true))',
            '$compiled_effects(S, PORIGIN pcode.UNIT pcpath_ternary) = [CODEEFFECT pcpath_selected]',
            '$code_expression(pcode.EXPRESSIONS, pcpath_bad) = eps',
            '$tick_marker(S, PORIGIN pcode.UNIT (pcpath_bad ++ [PCFIELD 6, PCINDEX 0])) = eps',
            '$tick_source_plan(S, pcode.UNIT) = (T)',
            'T.DEPENDENCY = eps', 'T.FREQUENCY = 0', 'T.MARKERS = eps',
            *valid('S'), *PAUSE,
            'S_done.EVENTS = ' + output(sources.CASES[name][1]),
        ],
    },
}

name = 'review-constant-logical-aliases-preserve-prior-tick'
review.CASES['constant-logical-aliases-preserve-real-opcode-adjacency'] = {
    'source': sources.CASES[name][0].decode(),
    'stage': 'S.TODO = (TICK porigin ptickmarker) :: ptask_tail* -- if S.CURRENT = eps -- if S.EVENTS = ' + output(b'PTZ'),
    'checks': [
        'porigin = PORIGIN n pcpath', '$code_at(S.CODE, n) = (pcode)',
        'pcpath = [PCINDEX 2, PCFIELD 1, PCINDEX 5]',
        'ptickmarker.FREQUENCY = 1', 'ptickmarker.LINE = 10',
        'S.TICKCOUNT = 0', '$tick_marker_valid(S, porigin, ptickmarker)',
        '$tick_source_plan(S, n) = (T)', 'T.DEPENDENCY = eps',
        '|T.MARKERS| = 2',
        *['$tick_marker(S, PORIGIN n ([PCINDEX 2, PCFIELD 1, PCINDEX ' + str(index) + '])) = eps'
          for index in range(1, 5)],
        'S_bad = S[.TODO = (TICK porigin ptickmarker[.LINE = 9]) :: ptask_tail*]',
        '~$call_descriptors_valid(S_bad)',
        *valid('S'), *PAUSE,
        'S_done.EVENTS = ' + output(sources.CASES[name][1]),
    ],
}

name = 'review-retained-print-does-not-publish-skipped-redirect'
review.CASES['retained-print-survives-constant-result-without-skipped-redirect'] = {
    'source': sources.CASES[name][0].decode(),
    'stage': 'S.TODO = (AT porigin_print EVAL_EFFECT) :: ptask_tail* -- if S.CURRENT = eps -- if S.EVENTS = ' + output(b'PT'),
    'checks': [
        'porigin_print = PORIGIN n pcpath_print', '$code_at(S.CODE, n) = (pcode)',
        'pcpath_logical = [PCINDEX 2, PCFIELD 1, PCINDEX 1, PCFIELD 0, PCFIELD 1, PCFIELD 0, PCINDEX 0, PCFIELD 1]',
        'pcpath_print = pcpath_logical ++ [PCFIELD 0]',
        'pcpath_skipped = pcpath_logical ++ [PCFIELD 1]',
        '$origin_node(S.SOURCES, porigin_print) = (NExprPrint expression metadata)',
        '$compiled_read(S, PORIGIN n pcpath_logical) = (PBOOL true)',
        '$compiled_effects(S, PORIGIN n pcpath_logical) = [CODEEFFECT pcpath_print]',
        '$code_expression(pcode.EXPRESSIONS, pcpath_skipped) = eps',
        '$code_redirect(pcode.REDIRECTS, pcpath_skipped) = eps',
        '$tick_source_plan(S, n) = (T)', 'T.DEPENDENCY = eps',
        '|T.MARKERS| = 3',
        '$tick_marker(S, PORIGIN n ([PCINDEX 2, PCFIELD 1, PCINDEX 1])) = (ptickmarker)',
        'ptickmarker.FREQUENCY = 1', 'ptickmarker.LINE = 6',
        *valid('S'), *PAUSE,
        'S_done.EVENTS = ' + output(sources.CASES[name][1]),
    ],
}

DERIVED_GUARDS = {
    'prepass-selected-arm-omits-unselected-diagnostic-and-markers': 0,
    'constant-logical-aliases-preserve-real-opcode-adjacency': 1,
    'retained-print-survives-constant-result-without-skipped-redirect': 0,
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case, process_seconds=240) else 1)
