#!/usr/bin/env python3
"""Source-reached immutable literal and mutable empty GC root eligibility."""
import argparse
import json
from pathlib import Path
import shutdown_state_review as runner

SOURCES = {row['id']: row['source'] for row in json.loads(
    Path(__file__).with_name('cycle_collection_review_cases.json').read_text())}

CASES = {
    'literal-empty-table-is-not-a-potential-root': {
        'source': SOURCES['immutable-empty-literal-does-not-create-black-buffer-hole'],
        'stage': 'S.TODO = (GC_TRACE pgccall) :: ptask_tail* '
                 '-- if pgccall.PASS = 0 -- if S.GC.NEXT = 2',
        'checks': [
            'S.TODO = (GC_TRACE pgccall) :: ptask_tail*',
            'pgccall.PASS = 0', 'S.GC.NEXT = 2',
            '$lookup(S.ENV, $ptascii("tmp")) = (n_cell)',
            'S.STORE[n_cell] = DEFINED (PARRAY n_array)',
            'S.ARRAYS[n_array].ITEMS = eps',
            '(HARRAY n_array) <- S.ALLOCATIONS',
            '$gc_literal_empty_pools(S, S.POOLS, n_array)',
            '$gc_immutable_array(S, n_array)',
            '~$gc_possible_root(S, HARRAY n_array)',
            '~((HARRAY n_array) <- $gc_nodes(S.GC.BUFFER))',
            '$gc_nodes(S.GC.BUFFER) = [HOBJECT n_a, HOBJECT n_b, HOBJECT n_c]',
            '$gc_decrement(S, S.GC, HARRAY n_array) = S.GC',
            '$gc_state_valid(S)', '$call_descriptors_valid(S)',
            '$heap_valid($heap_graph(S))',
            'S_bad = S[.GC = $gc_buffer_add(S.GC, HARRAY n_array)]',
            '(HARRAY n_array) <- $gc_nodes(S_bad.GC.BUFFER)',
            '$heap_valid($heap_graph(S_bad))',
            '~$gc_buffer_valid(S_bad, S_bad.GC)',
            '~$gc_state_valid(S_bad)', '~$call_descriptors_valid(S_bad)',
            'S_paused = $drive(S, 0)', 'S_paused.COMPLETION = BUDGET',
            'S_paused[.COMPLETION = NORMAL] = S',
            'S_step = $drive_steps(S, 1)', 'S_step.COMPLETION = BUDGET',
            '$drive_steps(S_paused[.COMPLETION = NORMAL], 1) = S_step',
            'S_next = S_step[.COMPLETION = NORMAL]',
            'S_next.TODO = (GC_DTORS pgcplan) :: ptask_tail*',
            'pgcplan.INDEX = 0', '|pgcplan.COUNTED| = 3',
            '~((HARRAY n_array) <- pgcplan.CANDIDATES)',
            '$gc_state_valid(S_next)', '$call_descriptors_valid(S_next)',
            '$heap_valid($heap_graph(S_next))',
        ],
    },
    'mutated-runtime-empty-table-keeps-real-buffer-eligibility': {
        'source': SOURCES['mutated-null-cast-array-retains-black-buffer-hole'],
        'stage': 'S.TODO = (GC_TRACE pgccall) :: ptask_tail* '
                 '-- if pgccall.PASS = 0 -- if S.GC.NEXT = 2',
        'checks': [
            'S.TODO = (GC_TRACE pgccall) :: ptask_tail*',
            'S.GC.IMMUTABLE = [n_immutable]',
            '$lookup(S.ENV, $ptascii("tmp")) = (n_cell)',
            'S.STORE[n_cell] = DEFINED (PARRAY n_array)',
            'n_array =/= n_immutable',
            'S.ARRAYS[n_immutable] = $array_empty()',
            'S.ARRAYS[n_array].ITEMS = eps',
            'S.ARRAYS[n_array] =/= $array_empty()',
            '(HARRAY n_array) <- S.ALLOCATIONS',
            '~$gc_literal_empty_pools(S, S.POOLS, n_array)',
            '~$gc_immutable_array(S, n_array)',
            '~$array_immutable(S, n_array)',
            '$gc_possible_root(S, HARRAY n_array)',
            '$gc_nodes(S.GC.BUFFER) = [HOBJECT n_a, HARRAY n_array, HOBJECT n_b, HOBJECT n_c]',
            '$gc_state_valid(S)', '$call_descriptors_valid(S)',
            '$heap_valid($heap_graph(S))',
            'S_bad = S[.GC = $gc_buffer_remove(S.GC, HARRAY n_array)][.GC.IMMUTABLE = S.GC.IMMUTABLE ++ [n_array]]',
            '~((HARRAY n_array) <- $gc_nodes(S_bad.GC.BUFFER))',
            '$heap_valid($heap_graph(S_bad))',
            '~$gc_immutable_flag_valid(S_bad, n_array)',
            '~$gc_state_valid(S_bad)', '~$call_descriptors_valid(S_bad)',
            'S_paused = $drive(S, 0)', 'S_paused.COMPLETION = BUDGET',
            'S_paused[.COMPLETION = NORMAL] = S',
            'S_step = $drive_steps(S, 1)', 'S_step.COMPLETION = BUDGET',
            '$drive_steps(S_paused[.COMPLETION = NORMAL], 1) = S_step',
            'S_next = S_step[.COMPLETION = NORMAL]',
            'S_next.TODO = (GC_DTORS pgcplan) :: ptask_tail*',
            'pgcplan.DTORS = [HOBJECT n_a, HOBJECT n_c, HOBJECT n_b]',
            '~((HARRAY n_array) <- pgcplan.CANDIDATES)',
            '$gc_state_valid(S_next)', '$call_descriptors_valid(S_next)',
            '$heap_valid($heap_graph(S_next))',
        ],
    },
}
runner.CASES = CASES
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if runner.run(args.case) else 1)
