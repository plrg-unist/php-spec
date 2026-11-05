#!/usr/bin/env python3
"""Reach lazy nested list plans and committed writes before an abrupt list target."""
import argparse
import json

import fiber_state_review as review
import tick_list_review_cases as sources


def output(*chunks):
    return '[' + ', '.join('OUTPUT $ptascii(' + json.dumps(chunk) + ')'
                           for chunk in chunks) + ']'


def valid(state):
    return [f'$call_descriptors_valid({state})',
            f'$heap_valid($heap_graph({state}))', f'$tick_state_valid({state})']


PAUSE = [
    'S_paused = $drive_steps(S, 0)', 'S_paused.COMPLETION = BUDGET',
    'S_paused.TODO = S.TODO', 'S_paused.CURRENT = S.CURRENT',
    'S_paused.FRAMES = S.FRAMES', 'S_paused.ITERATORS = S.ITERATORS',
    'S_paused.TICKCOUNT = S.TICKCOUNT', 'S_paused.EVENTS = S.EVENTS',
    *valid('S_paused'), 'S_done = $drive(S, 4000)',
    '$drive(S_paused[.COMPLETION = NORMAL], 4000) = S_done',
    'S_done.COMPLETION = NORMAL', 'S_done.TODO = eps',
    'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
    'S_done.ITERATORS = eps', *valid('S_done'),
]

name = 'review-empty-foreach-list-compiles-key-before-nested-target'
review.CASES = {
    'empty-foreach-list-retains-key-then-nested-target-frequency': {
        'source': sources.CASES[name][0].decode(),
        'stage': 'S.TODO = (TICK porigin ptickmarker) :: ptask_tail* -- if S.CURRENT = eps -- if S.EVENTS = ' + output('P', 'T'),
        'checks': [
            'porigin = PORIGIN n pcpath',
            'pcpath = [PCINDEX 3, PCFIELD 1, PCINDEX 1]',
            '$origin_node(S.SOURCES, porigin) = (NStmtForeach expression_iterable ABSENT (BOOLEAN false) expression_pattern phpType23_body (BOOLEAN false) metadata_foreach)',
            'ptickmarker.FREQUENCY = 2', 'ptickmarker.LINE = 7',
            '$tick_marker_valid(S, porigin, ptickmarker)',
            '$origin_child((porigin), [PCFIELD 3, PCFIELD 0, PCINDEX 0, PCFIELD 0, PCFIELD 0, PCFIELD 6, PCINDEX 0]) = (porigin_key_declare)',
            '$origin_child((porigin), [PCFIELD 3, PCFIELD 0, PCINDEX 0, PCFIELD 1, PCFIELD 0, PCINDEX 0, PCFIELD 1, PCFIELD 1, PCFIELD 0, PCFIELD 6, PCINDEX 0]) = (porigin_target_declare)',
            '$tick_marker(S, porigin_key_declare) = (ptickmarker_key)',
            '$tick_marker(S, porigin_target_declare) = (ptickmarker_target)',
            'ptickmarker_key.FREQUENCY = 3', 'ptickmarker_target.FREQUENCY = 2',
            'S.ITERATORS = eps', 'S.TICKCOUNT = 0',
            '$lookup(S.ENV, $ptascii("out")) = (n_out_cell)',
            'S.STORE[n_out_cell] = DEFINED (PARRAY n_out)',
            'S.ARRAYS[n_out].ITEMS = eps',
            # One derived compiler refusal: change only the inner byref bit,
            # recompile that AST, then use its own published compiler facts.
            '$source_unit(S.SOURCES, n) = (pcunit)',
            '$pcprogram(pcunit.AST) = [statement_fn, statement_out, statement_register, statement_declare]',
            'statement_declare = NStmtDeclare phpType48_directives (SEQUENCE ([statement_P, statement_foreach, statement_Z])) metadata_declare',
            'statement_foreach = NStmtForeach expression_iterable ABSENT (BOOLEAN false) expression_pattern phpType23_body (BOOLEAN false) metadata_foreach',
            'expression_pattern = NExprList (SEQUENCE ([phpType13_outer])) metadata_pattern',
            'phpType13_outer = NArrayItem expression_key expression_nested (BOOLEAN false) (BOOLEAN false) metadata_outer',
            'expression_nested = NExprList (SEQUENCE ([(NArrayItem ABSENT expression_target (BOOLEAN false) (BOOLEAN false) metadata_inner)])) metadata_nested',
            'expression_nested_bad = NExprList (SEQUENCE ([(NArrayItem ABSENT expression_target (BOOLEAN true) (BOOLEAN false) metadata_inner)])) metadata_nested',
            'expression_pattern_bad = NExprList (SEQUENCE ([(NArrayItem expression_key expression_nested_bad (BOOLEAN false) (BOOLEAN false) metadata_outer)])) metadata_pattern',
            '$list_pattern(expression_pattern_bad) = (phpType13_bad*)',
            '$list_references(phpType13_bad*)',
            'statement_foreach_bad = NStmtForeach expression_iterable ABSENT (BOOLEAN false) expression_pattern_bad phpType23_body (BOOLEAN false) metadata_foreach',
            'program_bad = PROGRAM ([statement_fn, statement_out, statement_register, (NStmtDeclare phpType48_directives (SEQUENCE ([statement_P, statement_foreach_bad, statement_Z])) metadata_declare)])',
            'P_bad = $ppstart(n, program_bad, $ptascii("derived-list-reference-37.php"))',
            'pcodeexpr_bad* = $compiled_operands(P_bad, P_bad.EXPRESSIONS)',
            'pcpath_target = pcpath ++ [PCFIELD 3, PCFIELD 0, PCINDEX 0, PCFIELD 1, PCFIELD 0, PCINDEX 0, PCFIELD 1]',
            '$code_expression(pcodeexpr_bad*, pcpath_target) = ((9, false))',
            'T_bad = $tick_code_plan(program_bad, pcodeexpr_bad*, $compiled_names(P_bad.NAMES), $compiled_redirects(P_bad.REDIRECTS))',
            'T_bad.DEPENDENCY = ("tick declaration or callable in an unmodeled expression compilation order")',
            *valid('S'), *PAUSE,
            'S_done.EVENTS = ' + output('P', 'T', 'Z', 'T'),
        ],
    },
}

name = 'review-defined-list-target-throw-preserves-earlier-write'
review.CASES['list-target-tick-retains-earlier-write-and-pending-tail-before-throw'] = {
    'source': sources.CASES[name][0].decode(),
    'stage': 'S.TODO = (TICK porigin ptickmarker) :: ptask_tail* -- if S.CURRENT = (pcallcontext) -- if S.EVENTS = ' + output('V'),
    'checks': [
        'porigin = PORIGIN n pcpath',
        'pcpath_foreach = [PCINDEX 3, PCFIELD 0, PCINDEX 0, PCFIELD 1, PCINDEX 0]',
        'porigin_foreach = PORIGIN n pcpath_foreach',
        'pcpath = pcpath_foreach ++ [PCFIELD 3, PCFIELD 0, PCINDEX 1, PCFIELD 1, PCFIELD 1, PCFIELD 0, PCFIELD 6, PCINDEX 0, PCFIELD 1, PCINDEX 0]',
        '$origin_node(S.SOURCES, porigin_foreach) = (NStmtForeach expression_iterable ABSENT (BOOLEAN false) expression_pattern (SEQUENCE ([statement_body])) (BOOLEAN false) metadata)',
        'statement_foreach = NStmtForeach expression_iterable ABSENT (BOOLEAN false) expression_pattern (SEQUENCE ([statement_body])) (BOOLEAN false) metadata',
        '$list_pattern(expression_pattern) = ([phpType13_first, phpType13_second, phpType13_last])',
        '$origin_child((porigin_foreach), [PCFIELD 3, PCFIELD 0, PCINDEX 1, PCFIELD 0]) = (porigin_key_second)',
        '$code_expression_at_source(S, porigin_key_second, eps) = (z_next)',
        '$origin_child((porigin_foreach), [PCFIELD 4, PCINDEX 0]) = (porigin_body)',
        'S.ITERATORS = [ITERATOR n_iterator n_array false ([(CURSOR n_array 1)])]',
        '$entry_lookup(S.ARRAYS[n_array].ITEMS, KINT 0) = (DIRECT (PARRAY n_row))',
        '$entry_lookup(S.ARRAYS[n_row].ITEMS, KSTRING $ptascii("b")) = (DIRECT (PINT 20))',
        'S.FRAMES = [pframe_caller]', 'pframe_caller.CONTEXT = eps',
        '(LIST_NEXT (KNOWN (PARRAY n_row)) 2 ([phpType13_last]) z_next) <- pframe_caller.TODO',
        '(AT porigin_body (STMT statement_body)) <- pframe_caller.TODO',
        '(FOREACH_NEXT n_iterator (HARRAY n_array) statement_foreach (porigin_foreach) 7) <- pframe_caller.TODO',
        '$heap_count(HARRAY n_row, $tasks_nodes(pframe_caller.TODO)) = 1',
        '$heap_count(HARRAY n_array, $tasks_nodes(pframe_caller.TODO)) = 1',
        '$heap_owners($heap_prune($heap_graph(S)), HARRAY n_array) = 2',
        'S_global = $global_table_view(S)',
        '$lookup(S_global.ENV, $ptascii("out")) = (n_out_cell)',
        'S.STORE[n_out_cell] = DEFINED (PARRAY n_out)',
        '$entry_lookup(S.ARRAYS[n_out].ITEMS, KSTRING $ptascii("first")) = (DIRECT (PINT 10))',
        '$entry_lookup(S.ARRAYS[n_out].ITEMS, KSTRING $ptascii("second")) = eps',
        '$entry_lookup(S.ARRAYS[n_out].ITEMS, KSTRING $ptascii("last")) = eps',
        'ptickmarker.FREQUENCY = 1', 'ptickmarker.LINE = 11',
        '$tick_marker_valid(S, porigin, ptickmarker)',
        '$tick_marker(S, porigin_foreach) = (ptickmarker_foreach)',
        'ptickmarker_foreach.FREQUENCY = 2', 'ptickmarker_foreach.LINE = 7',
        *valid('S'), *PAUSE,
        '$heap_owners($heap_prune($heap_graph(S_done)), HARRAY n_array) = 1',
        '$lookup(S_done.ENV, $ptascii("out")) = (n_out_done_cell)',
        'S_done.STORE[n_out_done_cell] = DEFINED (PARRAY n_out_done)',
        '$entry_lookup(S_done.ARRAYS[n_out_done].ITEMS, KSTRING $ptascii("first")) = (DIRECT (PINT 10))',
        '$entry_lookup(S_done.ARRAYS[n_out_done].ITEMS, KSTRING $ptascii("second")) = eps',
        '$entry_lookup(S_done.ARRAYS[n_out_done].ITEMS, KSTRING $ptascii("last")) = eps',
        'S_done.EVENTS = ' + output('V', 'T', 'C', '10', 'S', 'L', 'Z'),
    ],
}

DERIVED_GUARDS = {
    'empty-foreach-list-retains-key-then-nested-target-frequency': 1,
    'list-target-tick-retains-earlier-write-and-pending-tail-before-throw': 0,
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case, process_seconds=240) else 1)
