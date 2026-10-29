#!/usr/bin/env python3
"""Genuine BYVAL snapshots, field retirement and ordinary reference COW."""
from pathlib import Path
from types import SimpleNamespace

import array_iterator_byval_fields_cases as cases
import list_missing_warning_protocol as shared
from array_aggregate_unpack_state_review import initial, seek
from array_generator_unpack_state_review import budget, finish, owners, public, singleton
from array_iterator_fields_state import HELPERS, fields, first_items, pool, row_items

SELECTED = ('array-iterator-byval-fields-last-data',
            'array-iterator-byval-fields-key-throw',
            'array-iterator-byval-fields-no-destructor',
            'array-iterator-byref-fields-no-destructor')
AUTHOR = SimpleNamespace(CASES={name: cases.CASES[name] for name in SELECTED},
                         __file__=cases.__file__)
HELPERS += r'''
def $list_warning_frontier(S, 849) = $a64_echo(S, $ptascii("K:"))
def $list_warning_frontier(S, 850) = $a64_echo(S, $ptascii("S:"))
'''


def bindings(state, names):
    return [f'$lookup({state}.ENV, $ptascii("{name}")) = (n_{name})'
            for name in names]


def reference_guards():
    checks = [
        '~$array_iterator_byref_current(S_cache, parrayiterator_cache)',
        '$array_iterator_value(S_cache, REFERENCE n_marker) = (PINT 0)',
        '$array_iterator_current_value(S_cache, parrayiterator_cache, REFERENCE n_marker) = eps',
    ]
    for label, value in [('pure', 'n_constant'), ('reference', 'n_old')]:
        state = 'S_bad_' + label
        iterator = 'parrayiterator_bad_' + label
        checks += [
            f'{iterator} = parrayiterator_cache[.CURRENT = REFERENCE n_marker]',
            f'{state} = S_cache[.STORE[n_marker] = DEFINED (PARRAY {value})][.TODO = (ARRAY_ITERATOR {iterator} "key-start") :: ptask_cache*]',
            f'$array_iterator_reference_cell({state}, n_marker) = (PARRAY {value})',
            f'$array_iterator_valid({state}, {iterator}, "key-start")',
            f'$array_iterator_owned_field({state}, {iterator})',
            f'$array_iterator_current_value({state}, {iterator}, REFERENCE n_marker) = eps',
            f'~$array_iterator_ready({state}, {iterator})',
        ] + public(state)
    return checks


def destructor_case(name, program, path, stdout):
    normal = name == SELECTED[0]
    checks = initial(program, path) + seek('S_initial', 840, 'S_pre') + [
        'S_pre.TODO = (ARRAY_ITERATOR parrayiterator_pre "current-start") :: ptask_pre*',
        'parrayiterator_pre.OBJECT = n_object', 'parrayiterator_pre.ARRAY = n_target',
        '$lookup(S_pre.ENV, $ptascii("it")) = eps',
        '$lookup(S_pre.ENV, $ptascii("pool")) = (n_pool_cv)',
    ] + bindings('S_pre', ['saved', 'leaf', 'other', 'marker', 'dest', 'tail', 'watch']) + [
        'S_pre.STORE[n_saved] = DEFINED (PARRAY n_first)',
        'S_pre.STORE[n_pool_cv] = DEFINED (PARRAY n_constant)',
        'S_pre.STORE[n_watch] = DEFINED (POBJECT n_observer)',
        'S_pre.ARRAYS[n_constant].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_pool_child)),ENTRY (KINT 1) (DIRECT (PINT 17))]',
        'n_pool_roots = $heap_count(HARRAY n_constant, $pools_nodes(S_pre.POOLS))',
        'n_pool_child_roots = $heap_count(HARRAY n_pool_child, $pools_nodes(S_pre.POOLS))',
        '$(n_pool_roots > 0)',
    ] + fields('S_pre', 'n_first', 'n_constant', 'n_old', direct=True) + [
        first_items('S_pre', 'n_first', 'n_child'), row_items('S_pre', 'n_old', 'n_child'),
        singleton('S_pre', 'n_child', 3),
        owners('S_pre', 'HARRAY n_old', 1), owners('S_pre', 'HARRAY n_child', 2),
        '$array_iterator_ready(S_pre, parrayiterator_pre)',
    ] + pool('S_pre', 2) + public('S_pre')
    checks += seek('S_pre', 841, 'S_cache') + [
        'S_cache.TODO = (ARRAY_ITERATOR parrayiterator_cache "key-start") :: ptask_cache*',
        'parrayiterator_cache.CURRENT = KNOWN (PARRAY n_old)',
        '$array_iterator_current_value(S_cache, parrayiterator_cache, KNOWN (PARRAY n_old)) = (PARRAY n_old)',
        '$array_iterator_ready(S_cache, parrayiterator_cache)',
        owners('S_cache', 'HARRAY n_old', 2), owners('S_cache', 'HARRAY n_child', 2),
        owners('S_cache', 'HOBJECT n_object', 1),
    ] + fields('S_cache', 'n_first', 'n_constant', 'n_old', direct=True) + public('S_cache')
    checks += reference_guards()
    checks += seek('S_cache', 842, 'S_key') + fields('S_key', 'n_first', 'n_second', 'n_new') + [
        'S_key.FRAMES = pframe_key :: pframe_tail*',
        'pframe_key.TODO = (ARRAY_ITERATOR parrayiterator_key "key") :: ptask_key*',
        'parrayiterator_key.CURRENT = KNOWN (PARRAY n_old)',
        'S_key.ARRAYS[n_second].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_second_child)),ENTRY (KINT 1) (DIRECT (PINT 17))]',
        singleton('S_key', 'n_second_child', 22), row_items('S_key', 'n_new', 'n_new_child'),
        singleton('S_key', 'n_new_child', 11), 'n_new =/= n_old',
        'n_new_child_roots = $heap_count(HARRAY n_new_child, $pools_nodes(S_key.POOLS))',
        '$(n_new_child_roots > 0)',
        'S_key_global = $global_table_view(S_key)',
        '$lookup(S_key_global.ENV, $ptascii("escaped")) = (n_outer)',
        owners('S_key', 'HARRAY n_old', 1), owners('S_key', 'HARRAY n_child', 2),
        owners('S_key', 'HCELL n_outer', 2),
    ] + pool('S_key', 1) + public('S_key')
    if normal:
        checks += seek('S_key', 843, 'S_insert_ready') + [
            'S_insert_ready.TODO = (ARRAY_ITERATOR parrayiterator_insert "insert") :: ptask_insert*',
            'parrayiterator_insert.CURRENT = KNOWN (PARRAY n_old)',
            'PhpStep: S_insert_ready ~> S_insert',
            'S_insert.ARRAYS[n_target].ITEMS = [ENTRY (KINT 4) (DIRECT (PINT 8)),ENTRY (KSTRING ($ptascii("row"))) (DIRECT (PARRAY n_old))]',
            owners('S_insert', 'HARRAY n_old', 1),
        ] + public('S_insert') + budget('S_insert_ready', 'S_insert_budget')
        checks += seek('S_insert', 844, 'S_finish') + [
            'S_finish.TODO = (ARRAY_ITERATOR parrayiterator_finish "finish") :: ptask_finish*',
            'parrayiterator_finish.CURRENT = KNOWN PNULL',
            'PhpStep: S_finish ~> S_release',
            'S_release.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (ARRAY_ITERATOR_RELEASE parrayiterator_finish "normal") :: ptask_finish*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_object)]',
            '$array_iterator_release_builder(S_release, parrayiterator_finish)',
            '~$array_iterator_destructor_byref_current(S_release, parrayiterator_finish)',
        ] + seek('S_release', 845, 'S_dtor')
    else:
        checks += seek('S_key', 845, 'S_dtor') + ['~((HARRAY n_old) <- S_dtor.ALLOCATIONS)']
    checks += [owners('S_dtor', 'HARRAY n_child', 2 if normal else 1),
               '$weakref_get(S_dtor, n_observer) = POBJECT n_object'] + public('S_dtor')
    checks += seek('S_dtor', 846, 'S_mutated') + fields('S_mutated', 'n_first_private', 'n_second', 'n_new') + [
        first_items('S_mutated', 'n_first_private', 'n_first_child'), singleton('S_mutated', 'n_first_child', 44),
        row_items('S_mutated', 'n_new', 'n_row_child'), singleton('S_mutated', 'n_row_child', 55),
        first_items('S_mutated', 'n_first', 'n_child'), singleton('S_mutated', 'n_child', 3),
        'n_first_private =/= n_first', 'n_row_child =/= n_new_child',
        singleton('S_mutated', 'n_new_child', 11),
        '(HARRAY n_new_child) <- S_mutated.ALLOCATIONS',
        'S_mutated.STORE[n_leaf] = DEFINED (PINT 31)',
        'S_mutated.STORE[n_other] = DEFINED (PINT 42)',
        'S_mutated.STORE[n_marker] = DEFINED (PINT 1)',
        'S_mutated.STORE[n_dest] = DEFINED (PINT 99)',
        owners('S_mutated', 'HARRAY n_child', 2 if normal else 1),
    ] + public('S_mutated')
    state = 'S_read' if normal else 'S_caught'
    checks += seek('S_mutated', 847 if normal else 848, state) + [
        f'~((HOBJECT n_object) <- {state}.ALLOCATIONS)',
        f'~((HARRAY n_first_private) <- {state}.ALLOCATIONS)',
        f'~((HARRAY n_first_child) <- {state}.ALLOCATIONS)',
        f'~((HARRAY n_second) <- {state}.ALLOCATIONS)',
        f'~((HARRAY n_second_child) <- {state}.ALLOCATIONS)',
        f'$weakref_get({state}, n_observer) = PNULL',
        f'$lookup({state}.ENV, $ptascii("escaped")) = (n_outer)',
        owners(state, 'HCELL n_outer', 1), owners(state, 'HCELL n_marker', 1),
        row_items(state, 'n_new', 'n_row_child'), singleton(state, 'n_row_child', 55),
    ]
    if normal:
        checks += [f'{state}.STORE[n_dest] = DEFINED (PARRAY n_target)',
                   f'{state}.STORE[n_tail] = DEFINED (PINT 21)',
                   f'{state}.ARRAYS[n_target].ITEMS = [ENTRY (KINT 4) (DIRECT (PINT 8)),ENTRY (KSTRING ($ptascii("row"))) (DIRECT (PARRAY n_old)),ENTRY (KINT 5) (DIRECT (PINT 20))]',
                   row_items(state, 'n_old', 'n_child'), owners(state, 'HARRAY n_child', 2)]
    else:
        checks += bindings(state, ['first_error', 'e']) + [
            f'{state}.STORE[n_first_error] = DEFINED (POBJECT n_original)',
            f'{state}.STORE[n_e] = DEFINED (POBJECT n_original)',
            f'$throwable_field({state}, n_original, "previous") = PNULL',
            f'{state}.STORE[n_dest] = DEFINED (PINT 99)',
            f'{state}.STORE[n_tail] = DEFINED (PINT 20)',
            f'~((HARRAY n_target) <- {state}.ALLOCATIONS)',
        ]
    checks += public(state) + finish(state, stdout, [
        'HOBJECT n_object', 'HOBJECT n_observer', 'HCELL n_outer',
        'HCELL n_leaf', 'HCELL n_other', 'HCELL n_marker', 'HARRAY n_first',
        'HARRAY n_child', 'HARRAY n_old', 'HARRAY n_second', 'HARRAY n_second_child',
        'HARRAY n_first_private', 'HARRAY n_first_child', 'HARRAY n_new',
        'HARRAY n_row_child', 'HARRAY n_target',
    ] + ([] if normal else ['HOBJECT n_original']))
    checks += ['(HARRAY n_new_child) <- S_done.ALLOCATIONS',
               singleton('S_done', 'n_new_child', 11),
               owners('S_done', 'HARRAY n_new_child', 'n_new_child_roots')] + pool('S_done', 0)
    return checks


def no_destructor(name, program, path, stdout):
    reference = name == SELECTED[3]
    checks = initial(program, path) + seek('S_initial', 841, 'S_cache') + [
        'S_cache.TODO = (ARRAY_ITERATOR parrayiterator_cache "key-start") :: ptask_cache*',
        'parrayiterator_cache.OBJECT = n_object', 'parrayiterator_cache.ARRAY = n_target',
        'parrayiterator_cache.CURRENT = ' + ('REFERENCE n_outer' if reference else 'KNOWN (PARRAY n_old)'),
        '~$array_iterator_destructor(S_cache, n_object)',
        '$lookup(S_cache.ENV, $ptascii("it")) = eps',
    ] + bindings('S_cache', ['saved', 'marker', 'leaf', 'watch']) + [
        'S_cache.STORE[n_saved] = DEFINED (PARRAY n_old)',
        'S_cache.STORE[n_watch] = DEFINED (POBJECT n_observer)',
        'S_cache.ARRAYS[n_old].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_child)),ENTRY (KINT 1) (ALIAS n_leaf)]',
        singleton('S_cache', 'n_child', 3),
        owners('S_cache', 'HARRAY n_old', 4 if reference else 5), owners('S_cache', 'HARRAY n_child', 1),
        '$array_iterator_ready(S_cache, parrayiterator_cache)',
    ] + fields('S_cache', 'n_old', 'n_old', 'n_old', direct=not reference) + public('S_cache')
    checks += seek('S_cache', 849, 'S_key') + fields('S_key', 'n_first', 'n_second', 'n_row', direct=not reference) + [
        'S_key.CURRENT = (pcallcontext_key)',
        'S_key.FRAMES = pframe_key :: pframe_key_tail*',
        'pframe_key.TODO = (ARRAY_ITERATOR parrayiterator_cache "key") :: ptask_key_tail*',
        '$array_iterator_frame(S_key, pcallcontext_key, pframe_key)',
        '$array_iterator_current_value(S_key, parrayiterator_cache, ' + ('REFERENCE n_outer' if reference else 'KNOWN (PARRAY n_old)') + ') = (PARRAY ' + ('n_row' if reference else 'n_old') + ')',
        'S_key.ARRAYS[n_first].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_first_child)),ENTRY (KINT 1) (ALIAS n_leaf)]',
        'S_key.ARRAYS[n_second].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_second_child)),ENTRY (KINT 1) (ALIAS n_leaf)]',
        'S_key.ARRAYS[n_row].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_row_child)),ENTRY (KINT 1) (ALIAS n_leaf)]',
        singleton('S_key', 'n_first_child', 33), singleton('S_key', 'n_second_child', 44),
        singleton('S_key', 'n_row_child', 55), owners('S_key', 'HARRAY n_old', 1 if reference else 2),
        owners('S_key', 'HCELL n_leaf', 5),
    ] + seek('S_key', 847, 'S_read') + [
        '$lookup(S_read.ENV, $ptascii("dest")) = (n_dest)',
        'S_read.STORE[n_dest] = DEFINED (PARRAY n_target)',
        'S_read.ARRAYS[n_target].ITEMS = [ENTRY (KSTRING ($ptascii("row"))) (DIRECT (PARRAY ' + ('n_row' if reference else 'n_old') + '))]',
        '$weakref_get(S_read, n_observer) = PNULL',
        owners('S_read', 'HARRAY n_old', 1 if reference else 2), owners('S_read', 'HCELL n_leaf', 3 if reference else 2),
        owners('S_read', 'HARRAY n_child', 1),
    ] + [f'~(({node}) <- S_read.ALLOCATIONS)' for node in [
        'HOBJECT n_object', 'HARRAY n_first', 'HARRAY n_first_child',
        'HARRAY n_second', 'HARRAY n_second_child',
    ] + (['HCELL n_outer'] if reference else ['HARRAY n_row', 'HARRAY n_row_child'])] + public('S_read')
    checks += seek('S_read', 850, 'S_split') + [
        '$lookup(S_split.ENV, $ptascii("leaf")) = eps',
        'S_split.ARRAYS[n_target].ITEMS = [ENTRY (KSTRING ($ptascii("row"))) (DIRECT (PARRAY n_detached))]',
        'S_split.ARRAYS[n_detached].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_detached_child)),ENTRY (KINT 1) (' + ('ALIAS n_leaf' if reference else 'DIRECT (PINT 66)') + ')]',
        singleton('S_split', 'n_detached_child', 77), singleton('S_split', 'n_child', 3),
        'n_detached =/= n_old', 'n_detached_child =/= n_child',
        'S_split.STORE[n_leaf] = DEFINED (PINT ' + ('66' if reference else '8') + ')',
        owners('S_split', 'HCELL n_leaf', 2 if reference else 1), owners('S_split', 'HARRAY n_child', 1),
    ] + (['n_detached = n_row', 'n_detached_child = n_row_child'] if reference else []) + public('S_split') + finish('S_split', stdout, [
        'HOBJECT n_object', 'HOBJECT n_observer', 'HCELL n_leaf', 'HCELL n_marker',
        'HARRAY n_old', 'HARRAY n_child', 'HARRAY n_first', 'HARRAY n_first_child',
        'HARRAY n_second', 'HARRAY n_second_child',
        'HARRAY n_target', 'HARRAY n_detached', 'HARRAY n_detached_child',
    ] + (['HCELL n_outer'] if reference else ['HARRAY n_row', 'HARRAY n_row_child']))
    return checks


def conditions(name, program, path, stdout):
    if name in SELECTED[2:]:
        return no_destructor(name, program, path, stdout)
    return destructor_case(name, program, path, stdout)


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(AUTHOR, conditions, HELPERS, model_timeout=300,
        extra_inputs=(Path(__file__), Path(__file__).with_name('array_iterator_fields_state.py'),
                      Path(__file__).with_name('array_aggregate_unpack_state_review.py'),
                      Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
