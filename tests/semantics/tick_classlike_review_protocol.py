#!/usr/bin/env python3
"""Reach class-like emitter adjacency and uncalled-method declarable effects."""
import argparse
import json

import fiber_state_review as review
import tick_classlike_review_cases as sources
import tick_classlike_sources as author


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
    'S_paused.TICKCOUNT = S.TICKCOUNT', 'S_paused.EVENTS = S.EVENTS',
    *valid('S_paused'), 'S_done = $drive(S, 4000)',
    '$drive(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
    'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
    'S_done.CURRENT = eps', 'S_done.FRAMES = eps', *valid('S_done'),
]

name = 'review-early-interface-keeps-adjacent-declare-tick-suppressed'
review.CASES = {
    'early-interface-preserves-suppressed-later-declare-marker': {
        'source': sources.CASES[name][0].decode(),
        'stage': 'S.TODO = (TICK porigin ptickmarker) :: ptask_tail* -- if S.CURRENT = eps -- if S.EVENTS = ' + output('T', 'Z'),
        'checks': [
            'porigin = PORIGIN n pcpath', 'pcpath = [PCINDEX 5]',
            'porigin_interface = PORIGIN n ([PCINDEX 3])',
            'porigin_declare = PORIGIN n ([PCINDEX 4])',
            '$class_at(S.CLASSES, porigin_interface) = (pclassdesc)',
            'pclassdesc.KIND = "interface"', 'pclassdesc.EARLY',
            '$class_named(S.CLASSNAMES, $ptascii("tickinterface39")) = (porigin_interface)',
            '$tick_marker(S, porigin_interface) = eps',
            '$tick_marker(S, porigin_declare) = eps',
            'ptickmarker.FREQUENCY = 2', 'ptickmarker.LINE = 7',
            '$tick_marker_valid(S, porigin, ptickmarker)', 'S.TICKCOUNT = 0',
            '$code_at(S.CODE, n) = (pcode)',
            '$source_unit(S.SOURCES, n) = (pcunit)',
            'T_missing = $tick_full_plan(pcunit.AST, pcode.EXPRESSIONS, pcode.NAMES, pcode.REDIRECTS, eps)',
            'T_missing.DEPENDENCY = ("tick class declaration compiler facts")',
            'S_forged = S[.CLASSES = $trait_class_set(S.CLASSES, pclassdesc[.EARLY = false])]',
            '~$call_descriptors_valid(S_forged)',
            *valid('S'), *PAUSE,
            'S_done.TICKCOUNT = 1', 'S_done.EVENTS = ' + output('T', 'Z'),
        ],
    },
}

name = 'review-trait-uncalled-method-declarables-affect-following-markers'
review.CASES['uncalled-trait-method-compiles-frequency-without-runtime-body'] = {
    'source': sources.CASES[name][0].decode(),
    'stage': 'S.TODO = (TICK porigin ptickmarker) :: ptask_tail* -- if S.CURRENT = eps -- if S.EVENTS = ' + output('T', 'Z'),
    'checks': [
        'porigin = PORIGIN n pcpath', 'pcpath = [PCINDEX 4]',
        'porigin_trait = PORIGIN n ([PCINDEX 3])',
        '$class_at(S.CLASSES, porigin_trait) = (pclassdesc)',
        'pclassdesc.KIND = "trait"', 'pclassdesc.EARLY',
        '$class_named(S.CLASSNAMES, $ptascii("ticktrait39")) = (porigin_trait)',
        '$tick_marker(S, porigin_trait) = eps',
        '$origin_child((porigin_trait), [PCFIELD 2, PCINDEX 0, PCFIELD 6, PCINDEX 0]) = (porigin_method_declare)',
        '$tick_marker(S, porigin_method_declare) = (ptickmarker_method)',
        'ptickmarker_method.FREQUENCY = 2', 'ptickmarker_method.LINE = 6',
        'ptickmarker.FREQUENCY = 2', 'ptickmarker.LINE = 8',
        '$tick_marker_valid(S, porigin, ptickmarker)', 'S.TICKCOUNT = 0',
        *valid('S'), *PAUSE,
        'S_done.TICKCOUNT = 0', 'S_done.EVENTS = ' + output('T', 'Z', 'W', 'T'),
    ],
}

name = 'review-empty-enum-emitter-breaks-adjacency-without-outer-tick'
review.CASES['enum-emitter-enables-following-declare-without-an-enum-marker'] = {
    'source': sources.CASES[name][0].decode(),
    'stage': 'S.TODO = (TICK porigin ptickmarker) :: ptask_tail* -- if S.CURRENT = eps -- if ptickmarker.FREQUENCY = 3 -- if S.EVENTS = ' + output('T', 'P'),
    'checks': [
        'porigin = PORIGIN n pcpath', 'pcpath = [PCINDEX 6]',
        'porigin_enum = PORIGIN n ([PCINDEX 5])',
        '$class_at(S.CLASSES, porigin_enum) = (pclassdesc)',
        'pclassdesc.KIND = "enum"', '~pclassdesc.EARLY',
        '$class_named(S.CLASSNAMES, $ptascii("tickemptyenum39")) = (porigin_enum)',
        '$tick_marker(S, porigin_enum) = eps',
        '$origin_child((porigin_enum), [PCFIELD 4, PCINDEX 0, PCFIELD 6, PCINDEX 0]) = (porigin_method_declare)',
        '$tick_marker(S, porigin_method_declare) = (ptickmarker_method)',
        'ptickmarker_method.FREQUENCY = 2',
        'ptickmarker.FREQUENCY = 3', 'ptickmarker.LINE = 10',
        '$tick_marker_valid(S, porigin, ptickmarker)', 'S.TICKCOUNT = 1',
        'S_after = $drive_steps(S, 1)', 'S_after.COMPLETION = BUDGET',
        'S_after.TODO = ptask_tail*', 'S_after.TICKCOUNT = 2',
        'S_after.EVENTS = S.EVENTS', *valid('S_after'),
        *valid('S'), *PAUSE,
        'S_done.TICKCOUNT = 0', 'S_done.EVENTS = ' + output('T', 'P', 'Z', 'T'),
    ],
}

name = 'conditional-class-tick-sees-activation-before-callback-abort'
review.CASES['conditional-class-is-installed-before-its-header-tick-and-abort'] = {
    'source': author.CASES[name][0].decode(),
    'stage': 'S.TODO = (TICK porigin ptickmarker) :: ptask_tail* -- if S.CURRENT = eps -- if S.EVENTS = ' + output('T'),
    'checks': [
        'porigin = PORIGIN n pcpath',
        'pcpath = [PCINDEX 4, PCFIELD 0, PCINDEX 0, PCFIELD 1, PCINDEX 0]',
        '$origin_node(S.SOURCES, porigin) = (NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 phpType23 metadata)',
        '$class_at(S.CLASSES, porigin) = (pclassdesc)',
        'pclassdesc.KIND = "class"', '~pclassdesc.EARLY', 'pclassdesc.LINE = 18',
        '$class_named(S.CLASSNAMES, $ptascii("ticklate39")) = (porigin)',
        'ptickmarker.FREQUENCY = 1', 'ptickmarker.LINE = 18',
        '$tick_marker_valid(S, porigin, ptickmarker)',
        '$lookup(S.ENV, $ptascii("n")) = (n_count)',
        'S.STORE[n_count] = DEFINED (PINT 1)',
        'S.TICKCOUNT = 0', 'S.FRAMES = eps',
        *valid('S'), *PAUSE,
        '$class_named(S_done.CLASSNAMES, $ptascii("ticklate39")) = (porigin)',
        'S_done.EVENTS = ' + output('T', 'T', '[18]', '7', 'C', 'T', 'Z', 'T'),
    ],
}

DERIVED_GUARDS = {name: 0 for name in review.CASES}
DERIVED_GUARDS['early-interface-preserves-suppressed-later-declare-marker'] = 2


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case, process_seconds=240) else 1)
