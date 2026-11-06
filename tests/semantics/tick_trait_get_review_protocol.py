#!/usr/bin/env python3
"""Escaped Trait GET Closures retain physical source and distinct consumers."""
import argparse
import json

import fiber_state_review as review
import tick_trait_get_sources as sources


def output(*chunks):
    return '[' + ', '.join('OUTPUT $ptascii(' + json.dumps(chunk) + ')'
                           for chunk in chunks) + ']'


def valid(state):
    return [f'$call_descriptors_valid({state})',
            f'$heap_valid($heap_graph({state}))', f'$tick_state_valid({state})']


review.CASES = {
    'escaped-trait-getter-tick-keeps-source-consumers-and-called-child-distinct': {
        'source': sources.SOURCE.decode(),
        'stage': 'S.TODO = (TICK porigin ptickmarker) :: ptask_tail* -- if S.CURRENT = (pcallcontext) -- if S.EVENTS = ' + output('R', 'A', 'TickChildA52'),
        'checks': [
            'porigin_trait = PORIGIN 0 ([PCINDEX 3])',
            'porigin_a = PORIGIN 0 ([PCINDEX 4])',
            'porigin_child = PORIGIN 0 ([PCINDEX 5])',
            'porigin_b = PORIGIN 0 ([PCINDEX 6])',
            'porigin_property = PORIGIN 0 ([PCINDEX 3, PCFIELD 2, PCINDEX 0, PCFIELD 3, PCINDEX 0])',
            'porigin_hook_raw = PORIGIN 0 ([PCINDEX 3, PCFIELD 2, PCINDEX 0, PCFIELD 4, PCINDEX 0])',
            '$origin_child((porigin_hook_raw), [PCFIELD 5]) = (porigin_closure)',
            '$origin_child((porigin_closure), [PCFIELD 6, PCINDEX 2, PCFIELD 1, PCINDEX 0]) = (porigin)',
            'S.CLASSES = [pclassdesc_trait, pclassdesc_a, pclassdesc_child, pclassdesc_b]',
            'pclassdesc_trait.KIND = "trait"',
            '$hook_property_at(pclassdesc_a.PROPERTIES, TRAIT_MEMBER_ORIGIN porigin_a porigin_property) = (ppropertydesc_a)',
            '$hook_property_at(pclassdesc_b.PROPERTIES, TRAIT_MEMBER_ORIGIN porigin_b porigin_property) = (ppropertydesc_b)',
            '$property_hook_origin(S, ppropertydesc_a) = (porigin_hook_a)',
            '$property_hook_origin(S, ppropertydesc_b) = (porigin_hook_b)',
            'porigin_hook_a = TRAIT_ORIGIN porigin_a porigin_hook_raw ptbytes_hook',
            'porigin_hook_b = TRAIT_ORIGIN porigin_b porigin_hook_raw ptbytes_hook',
            'ptbytes_hook = $hook_name($ptascii("callback"))',
            '$closure_source_class(S, porigin_closure) = (porigin_trait)',
            '$trait_closure_source_matches(S, porigin_closure, porigin_a)',
            '$trait_closure_source_matches(S, porigin_closure, porigin_b)',
            '$class_link_at(S.LINKEDPARENTS, porigin_child) = (SOURCE_PARENT porigin_a)',
            'S_global = $global_table_view(S)',
            '$lookup(S_global.ENV, $ptascii("a")) = (n_cell_a)',
            '$lookup(S_global.ENV, $ptascii("b")) = (n_cell_b)',
            'S.STORE[n_cell_a] = DEFINED (POBJECT n_a)',
            'S.STORE[n_cell_b] = DEFINED (POBJECT n_b)', 'n_a =/= n_b',
            '$closure_scope_at(S.CLOSURESCOPES, n_a) = (pclosurescope_a)',
            '$closure_scope_at(S.CLOSURESCOPES, n_b) = (pclosurescope_b)',
            'pclosurescope_a.LEXICAL = porigin_a', 'pclosurescope_a.CALLED = porigin_child',
            'pclosurescope_b.LEXICAL = porigin_b', 'pclosurescope_b.CALLED = porigin_b',
            'pclosurescope_a.RECEIVER = (n_left)', 'pclosurescope_b.RECEIVER = (n_right)',
            'pcallcontext.FUNCTION = porigin_closure',
            'pcallcontext.TARGET = CLOSURE_TARGET n_a',
            'pcallcontext.LEXICAL_CLASS = (porigin_a)',
            'pcallcontext.CALLED_CLASS = (porigin_child)', 'pcallcontext.RECEIVER = (n_left)',
            'S.OBJECTS[n_left] = INSTANCE porigin_child',
            'S.OBJECTS[n_right] = INSTANCE porigin_b',
            'HOBJECT n_left <- S.ALLOCATIONS', 'HOBJECT n_right <- S.ALLOCATIONS',
            '$lookup(S_global.ENV, $ptascii("left")) = eps',
            '$lookup(S_global.ENV, $ptascii("right")) = eps',
            'S.FRAMES = [pframe_main]', 'pframe_main.CONTEXT = eps',
            '$lookup(S_global.ENV, $ptascii("n")) = (n_count)',
            '$lookup(S_global.ENV, $ptascii("seen")) = (n_seen)',
            'S.STORE[n_count] = DEFINED (PINT 0)', 'S.STORE[n_seen] = DEFINED (PINT 7)',
            'ptickmarker.FREQUENCY = 1', 'ptickmarker.LINE = 13',
            '$tick_marker_valid(S, porigin, ptickmarker)', 'S.TICKCOUNT = 0',
            'S_missing = S[.CLASSES = [pclassdesc_trait, pclassdesc_a[.PROPERTIES = eps], pclassdesc_child, pclassdesc_b]]',
            '$closure_source_class(S_missing, porigin_closure) = (porigin_trait)',
            '$trait_closure_source_matches(S_missing, porigin_closure, porigin_b)',
            '~$trait_closure_source_matches(S_missing, porigin_closure, porigin_a)',
            *valid('S'),
            'S_paused = $drive_steps(S, 0)',
            'S_paused = S[.COMPLETION = BUDGET]', *valid('S_paused'),
            'S_done = $drive(S, 4000)',
            '$drive(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
            'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
            'S_done.CURRENT = eps', 'S_done.FRAMES = eps', *valid('S_done'),
            'S_done.STORE[n_count] = DEFINED (PINT 2)',
            'n_left <- S_done.DESTRUCTION.CALLED', 'n_right <- S_done.DESTRUCTION.CALLED',
            '~((HOBJECT n_left) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_right) <- S_done.ALLOCATIONS)', 'S_done.TICKCOUNT = 0',
            'S_done.EVENTS = ' + output('R', 'A', 'TickChildA52', 'T', '7', 'C', 'B', 'TickConsumerB52', 'T', '9', '9', '2', 'a', 'b', 'Z'),
        ],
    },
}

DERIVED_GUARDS = {name: 1 for name in review.CASES}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case, process_seconds=240) else 1)
