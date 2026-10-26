#!/usr/bin/env python3
"""Iterator current caches distinguish array copies from live reference payloads."""
import base64
import json

import array_iterator_unpack_cases as cases
import list_missing_warning_protocol as shared
from array_iterator_unpack_state_review import HELPERS, budget, owners, public, seek, source_controls
from array_literal_float_wrapped_mixed_cv_state_review import pair


def frame(state, desc):
    return [f'{state}.TODO = (ARRAY_ITERATOR {desc} "key-start") :: ptask_{state}*',
            f'$array_iterator_valid({state}, {desc}, "key-start")',
            f'$array_iterator_ready({state}, {desc})',
            f'$array_iterator_source({state}, {desc})',
            f'$lookup({state}.ENV, $ptascii("it")) = eps',
            owners(state, 'HOBJECT n_object', 1), owners(state, 'HARRAY n_target', 1),
            f'$heap_count(HOBJECT n_object, $array_iterator_nodes({desc})) = 1',
            f'$heap_count(HARRAY n_target, $array_iterator_nodes({desc})) = 1'] + public(state)


def insert(state, desc, result, key, value):
    return [f'{state}.TODO = (ARRAY_ITERATOR {desc} "insert") :: ptask_{state}*',
            f'$array_iterator_source({state}, {desc})', f'$array_iterator_ready({state}, {desc})',
            f'$array_iterator_valid({state}, {desc}, "insert")',
            f'PhpStep: {state} ~> {result}',
            f'{result}.TODO = (ARRAY_ITERATOR {desc}[.CURRENT = KNOWN PNULL][.KEY = KNOWN PNULL] "next-start") :: ptask_{state}*',
            f'$entry_lookup({result}.ARRAYS[n_target].ITEMS, {key}) = (DIRECT (PARRAY {value}))',
            f'{result}.STORE = {state}.STORE', f'{result}.OBJECTS = {state}.OBJECTS',
            f'{result}.ITERATORS = {state}.ITERATORS',
            f'$array_iterator_nodes({desc}[.CURRENT = KNOWN PNULL][.KEY = KNOWN PNULL]) = [HARRAY n_target,HOBJECT n_object]'] + public(result) + budget(state, result, result + '_driven')


def conditions(name, program, path, stdout):
    reference = name.endswith('reference-current')
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 10, 'S') + [
        '$array_iterator_plan(S) = (parrayiterator)', 'parrayiterator.LINE = 11',
        'parrayiterator.ARRAY = n_target', 'parrayiterator.OBJECT = n_object',
        'parrayiterator.INPUT = VARIABLE ($ptascii("it")) 11',
        'parrayiterator.CURRENT = KNOWN PNULL', 'parrayiterator.KEY = KNOWN PNULL',
        '$lookup(S.ENV, $ptascii("row")) = (n_row)', 'S.STORE[n_row] = DEFINED (PARRAY n_old)',
        '$lookup(S.ENV, $ptascii("it")) = (n_it)', 'S.STORE[n_it] = DEFINED (POBJECT n_object)',
        '$lookup(S.ENV, $ptascii("tail")) = (n_tail)', 'S.STORE[n_tail] = DEFINED (PINT 7)',
        '$heap_count(HARRAY n_old, $pools_nodes(S.POOLS)) = 0', pair('S', 'n_old', 2, 7),
        owners('S', 'HOBJECT n_object', 1), owners('S', 'HARRAY n_target', 1),
    ] + source_controls('S', 'parrayiterator') + public('S') + [
        'PhpStep: S ~> S_active',
        'S_active.TODO = (ARRAY_ITERATOR parrayiterator "rewind-start") :: ptask_after*',
        '$task_nodes(ARRAY_ITERATOR parrayiterator "rewind-start") = [HARRAY n_target,HOBJECT n_object]',
        '$iterator_lookup(S_active.ITERATORS, parrayiterator.ITERATOR) = (OBJECTITER parrayiterator.ITERATOR n_object 0 false)',
        owners('S_active', 'HOBJECT n_object', 2),
    ] + budget('S', 'S_active', 'S_started') + seek('S_started', 11, 'S_cache') + frame('S_cache', 'parrayiterator_cache') + [
        'parrayiterator_cache.SITE = parrayiterator.SITE',
        'parrayiterator_cache.ITERATOR = parrayiterator.ITERATOR',
        'parrayiterator_cache.KEY = KNOWN PNULL',
        'S_cache.STORE[n_row] = DEFINED (PARRAY n_old)', pair('S_cache', 'n_old', 2, 7),
        '$lookup(S_cache.ENV, $ptascii("i")) = (n_i)', 'S_cache.STORE[n_i] = DEFINED (PINT 0)',
        '$array_iterator_source(S_cache, parrayiterator)',
        '~((HCELL n_it) <- S_cache.ALLOCATIONS)',
    ]
    if reference:
        checks += [
            'parrayiterator_cache.CURRENT = REFERENCE n_row', 'n_row <- S_cache.REFCELLS',
            '$lookup(S_cache.ENV, $ptascii("outside")) = (n_row)',
            '$lookup(S_cache.ENV, $ptascii("before")) = (n_before)',
            'S_cache.STORE[n_before] = DEFINED (PARRAY n_old)',
            owners('S_cache', 'HCELL n_row', 3), owners('S_cache', 'HARRAY n_old', 2),
            '$heap_count(HCELL n_row, $array_iterator_nodes(parrayiterator_cache)) = 1',
            '$heap_count(HARRAY n_old, $array_iterator_nodes(parrayiterator_cache)) = 0',
        ]
    else:
        checks += [
            'parrayiterator_cache.CURRENT = KNOWN (PARRAY n_old)',
            owners('S_cache', 'HCELL n_row', 1), owners('S_cache', 'HARRAY n_old', 2),
            '$heap_count(HARRAY n_old, $array_iterator_nodes(parrayiterator_cache)) = 1',
            '$heap_count(HCELL n_row, $array_iterator_nodes(parrayiterator_cache)) = 0',
        ]
    checks += seek('S_cache', 12, 'S_key') + [
        'S_key.TODO = (ARRAY_ITERATOR parrayiterator_key "insert") :: ptask_key*',
        '$array_iterator_source(S_key, parrayiterator_key)', '$array_iterator_ready(S_key, parrayiterator_key)',
        'parrayiterator_key.SITE = parrayiterator.SITE', 'parrayiterator_key.CURRENT = parrayiterator_cache.CURRENT',
        '$lookup(S_key.ENV, $ptascii("it")) = eps',
    ]
    if reference:
        checks += [
            '$lookup(S_key.ENV, $ptascii("row")) = (n_rebound)', 'n_rebound =/= n_row',
            'S_key.STORE[n_rebound] = DEFINED (PARRAY n_rebound_value)', pair('S_key', 'n_rebound_value', 88, 7),
            '~$array_immutable(S_key, n_rebound_value)',
            '$heap_count(HARRAY n_rebound_value, $pools_nodes(S_key.POOLS)) = 1',
            '$array_iterator_value(S_key, KNOWN (PARRAY n_rebound_value)) = (PARRAY n_rebound_value)',
            'S_key.STORE[n_row] = DEFINED (PARRAY n_value)', 'n_value =/= n_old', pair('S_key', 'n_value', 44, 7),
            'parrayiterator_key.KEY = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("answer")))',
            '$array_iterator_value(S_key, parrayiterator_key.CURRENT) = (PARRAY n_value)',
            owners('S_key', 'HCELL n_row', 2), owners('S_key', 'HARRAY n_value', 1), owners('S_key', 'HARRAY n_old', 1),
        ] + insert('S_key', 'parrayiterator_key', 'S_next', 'KSTRING ($ptascii("answer"))', 'n_value') + [
            owners('S_next', 'HCELL n_row', 1), owners('S_next', 'HARRAY n_value', 2),
            '$heap_count(HCELL n_row, $tasks_nodes(S_next.TODO)) = 0',
        ]
        start = 'S_next_driven'
    else:
        checks += [
            'S_key.STORE[n_row] = DEFINED (PARRAY n_value)', 'n_value =/= n_old', pair('S_key', 'n_value', 44, 7),
            'parrayiterator_key.KEY = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("8")))',
            '$array_iterator_key(PSTRING_CARRIER INTERNED_STRING ($ptascii("8"))) = eps',
            owners('S_key', 'HARRAY n_old', 1), owners('S_key', 'HARRAY n_value', 1),
        ] + insert('S_key', 'parrayiterator_key', 'S_next', 'KINT 5', 'n_old') + [
            owners('S_next', 'HARRAY n_old', 1), '$heap_count(HARRAY n_old, $tasks_nodes(S_next.TODO)) = 0',
        ] + seek('S_next_driven', 11, 'S_cache_two') + frame('S_cache_two', 'parrayiterator_two') + [
            'parrayiterator_two.CURRENT = KNOWN (PARRAY n_value)', 'S_cache_two.STORE[n_i] = DEFINED (PINT 1)',
            owners('S_cache_two', 'HARRAY n_value', 2),
        ] + seek('S_cache_two', 12, 'S_key_two') + [
            'S_key_two.TODO = (ARRAY_ITERATOR parrayiterator_key_two "insert") :: ptask_two*',
            'parrayiterator_key_two.CURRENT = KNOWN (PARRAY n_value)',
            'parrayiterator_key_two.KEY = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("slot")))',
        ] + insert('S_key_two', 'parrayiterator_key_two', 'S_next_two', 'KSTRING ($ptascii("slot"))', 'n_value') + [
            owners('S_next_two', 'HARRAY n_value', 2),
        ] + seek('S_next_two_driven', 11, 'S_cache_three') + frame('S_cache_three', 'parrayiterator_three') + [
            'parrayiterator_three.CURRENT = KNOWN (PARRAY n_value)', 'S_cache_three.STORE[n_i] = DEFINED (PINT 2)',
            owners('S_cache_three', 'HARRAY n_value', 3),
        ] + seek('S_cache_three', 12, 'S_key_three') + [
            'S_key_three.TODO = (ARRAY_ITERATOR parrayiterator_key_three "insert") :: ptask_three*',
            'parrayiterator_key_three.KEY = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("08")))',
            '$array_iterator_key(PSTRING_CARRIER INTERNED_STRING ($ptascii("08"))) = (KSTRING ($ptascii("08")))',
        ] + insert('S_key_three', 'parrayiterator_key_three', 'S_next_three', 'KSTRING ($ptascii("08"))', 'n_value') + [
            owners('S_next_three', 'HARRAY n_value', 3),
        ]
        start = 'S_next_three_driven'
    checks += seek(start, 16, 'S_read') + [
        'S_read.ITERATORS = eps', '~((HOBJECT n_object) <- S_read.ALLOCATIONS)',
        'S_read.STORE[n_tail] = DEFINED (PINT 8)',
        '$lookup(S_read.ENV, $ptascii("out")) = (n_out)', 'S_read.STORE[n_out] = DEFINED (PARRAY n_result)',
    ] + public('S_read')
    if reference:
        checks += [
            'n_result = n_target', '$entry_lookup(S_read.ARRAYS[n_result].ITEMS, KSTRING ($ptascii("answer"))) = (DIRECT (PARRAY n_value))',
            pair('S_read', 'n_value', 55, 7), pair('S_read', 'n_old', 2, 7),
            'S_read.STORE[n_row] = DEFINED (PARRAY n_outside_value)', 'n_outside_value =/= n_value',
            pair('S_read', 'n_outside_value', 44, 66), pair('S_read', 'n_rebound_value', 88, 7),
            '$lookup(S_read.ENV, $ptascii("seen")) = (n_seen)', 'S_read.STORE[n_seen] = DEFINED (PINT 44)',
        ]
        retired = ['n_target', 'n_old', 'n_value', 'n_outside_value']
    else:
        checks += [
            'n_result =/= n_target', '$lookup(S_read.ENV, $ptascii("copy")) = (n_copy)', 'S_read.STORE[n_copy] = DEFINED (PARRAY n_target)',
            '$entry_lookup(S_read.ARRAYS[n_result].ITEMS, KINT 5) = (DIRECT (PARRAY n_copy_old))', 'n_copy_old =/= n_old',
            '$entry_lookup(S_read.ARRAYS[n_result].ITEMS, KSTRING ($ptascii("slot"))) = (DIRECT (PARRAY n_copy_value))', 'n_copy_value =/= n_value',
            '$entry_lookup(S_read.ARRAYS[n_result].ITEMS, KSTRING ($ptascii("08"))) = (DIRECT (PARRAY n_value))',
            pair('S_read', 'n_copy_old', 2, 55), pair('S_read', 'n_copy_value', 66, 7),
            pair('S_read', 'n_old', 2, 7), pair('S_read', 'n_value', 44, 7),
            owners('S_read', 'HARRAY n_old', 1), owners('S_read', 'HARRAY n_value', 4),
        ]
        retired = ['n_target', 'n_result', 'n_old', 'n_value', 'n_copy_old', 'n_copy_value']
    checks += [
        '$drive_steps(S_read, 0) = S_read[.COMPLETION = BUDGET]',
        'S_split = $drive_steps(S_read, 1)', 'S_split.COMPLETION = BUDGET',
        'S_done = $drive_steps(S_split[.COMPLETION = NORMAL], 4000)',
        'S_done.COMPLETION = NORMAL', 'S_done.EXITSTATUS = 0', 'S_done.TODO = eps',
        'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps', 'S_done.ITERATORS = eps',
        'S_done.POOLS = S_read.POOLS',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '~((HCELL n_row) <- S_done.ALLOCATIONS)', '~((HCELL n_tail) <- S_done.ALLOCATIONS)',
    ] + [f'~((HARRAY {node}) <- S_done.ALLOCATIONS)' for node in retired] + public('S_done')
    if reference:
        checks += ['(HARRAY n_rebound_value) <- S_done.ALLOCATIONS',
                   owners('S_done', 'HARRAY n_rebound_value', 1), pair('S_done', 'n_rebound_value', 88, 7)]
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
