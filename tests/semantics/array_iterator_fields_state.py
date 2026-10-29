#!/usr/bin/env python3
"""Selected property references, distinct COW graphs and abrupt field cleanup."""
from pathlib import Path
from types import SimpleNamespace

import array_iterator_fields_cases as cases
import list_missing_warning_protocol as shared
from array_aggregate_unpack_state_review import initial, seek
from array_generator_unpack_state_review import budget, finish, owners, public, singleton

SELECTED = ('array-iterator-fields-last-data', 'array-iterator-fields-key-throw')
AUTHOR = SimpleNamespace(CASES={name: cases.CASES[name] for name in SELECTED},
                         __file__=cases.__file__)

HELPERS = shared.HELPERS + r'''
dec $a64_echo(pstate, ptbytes) : bool
def $a64_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $a64_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 840) = true
  -- if S.TODO = (ARRAY_ITERATOR parrayiterator "current-start") :: ptask*
def $list_warning_frontier(S, 841) = true
  -- if S.TODO = (ARRAY_ITERATOR parrayiterator "key-start") :: ptask*
def $list_warning_frontier(S, 842) = $a64_echo(S, $ptascii("Q:"))
def $list_warning_frontier(S, 843) = true
  -- if S.TODO = (ARRAY_ITERATOR parrayiterator "insert") :: ptask*
def $list_warning_frontier(S, 844) = true
  -- if S.TODO = (ARRAY_ITERATOR parrayiterator "finish") :: ptask*
def $list_warning_frontier(S, 845) = $a64_echo(S, $ptascii("D:"))
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
def $list_warning_frontier(S, 846) = $a64_echo(S, $ptascii("M:"))
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
def $list_warning_frontier(S, 847) = $a64_echo(S, $ptascii("R:"))
def $list_warning_frontier(S, 848) = $a64_echo(S, $ptascii("E:"))
'''


def fields(state, first, second, row, direct=False):
    tag = state.lower()
    checks = [f'$objectprops_record_at({state}.OBJECTPROPS, n_object) = (pobjectprops_{tag})']
    for name, value in [('first', f'DIRECT (PARRAY {first})'),
                        ('second', f'DIRECT (PARRAY {second})'),
                        ('row', f'DIRECT (PARRAY {row})' if direct else 'ALIAS n_outer'),
                        ('mark', 'ALIAS n_marker')]:
        checks += [f'$property_slot_at(pobjectprops_{tag}.SLOTS, $ptascii("{name}")) = (ppropertyslot_{tag}_{name})',
                   f'ppropertyslot_{tag}_{name}.STATE = PROP_VALUE ({value})']
    checks += [f'$node_children({state}, HOBJECT n_object) = [HARRAY {first},HARRAY {second},'
               + (f'HARRAY {row}' if direct else 'HCELL n_outer') + ',HCELL n_marker]']
    if not direct:
        checks += [f'{state}.STORE[n_outer] = DEFINED (PARRAY {row})']
    return checks


def first_items(state, root, child):
    return f'{state}.ARRAYS[{root}].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY {child})),ENTRY (KINT 1) (ALIAS n_leaf),ENTRY (KINT 2) (DIRECT (PINT 7))]'


def row_items(state, root, child):
    return f'{state}.ARRAYS[{root}].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY {child})),ENTRY (KINT 1) (ALIAS n_other),ENTRY (KINT 2) (DIRECT (PINT 19))]'


def pool(state, extra):
    return ([f'{state}.POOLS = S_pre.POOLS'] if state != 'S_pre' else []) + [
            f'{state}.ARRAYS[n_constant].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_pool_child)),ENTRY (KINT 1) (DIRECT (PINT 17))]',
            singleton(state, 'n_pool_child', 13),
            f'(HARRAY n_constant) <- {state}.ALLOCATIONS',
            f'(HARRAY n_pool_child) <- {state}.ALLOCATIONS',
            owners(state, 'HARRAY n_constant', f'$(n_pool_roots + {extra})'),
            owners(state, 'HARRAY n_pool_child', '$(n_pool_child_roots + 1)')]


def common(program, path):
    checks = initial(program, path) + seek('S_initial', 840, 'S_pre') + [
        'S_pre.TODO = (ARRAY_ITERATOR parrayiterator_pre "current-start") :: ptask_pre*',
        'parrayiterator_pre.OBJECT = n_object', 'parrayiterator_pre.ARRAY = n_target',
        'parrayiterator_pre.CURRENT = KNOWN PNULL',
        '$lookup(S_pre.ENV, $ptascii("it")) = eps',
    ]
    for name in ['saved', 'pool', 'leaf', 'other', 'marker', 'dest', 'tail', 'watch']:
        identifier = 'n_pool_cv' if name == 'pool' else 'n_' + name
        checks += [f'$lookup(S_pre.ENV, $ptascii("{name}")) = ({identifier})']
    checks += [
        'S_pre.STORE[n_saved] = DEFINED (PARRAY n_first)',
        'S_pre.STORE[n_pool_cv] = DEFINED (PARRAY n_constant)',
    ]
    checks += fields('S_pre', 'n_first', 'n_constant', 'n_old', direct=True) + [
        first_items('S_pre', 'n_first', 'n_child'),
        row_items('S_pre', 'n_old', 'n_child'),
        singleton('S_pre', 'n_child', 3),
        'S_pre.STORE[n_marker] = DEFINED (PINT 0)',
        '$array_iterator_reference_cell(S_pre, n_marker) = (PINT 0)',
        'S_pre.STORE[n_watch] = DEFINED (POBJECT n_observer)',
        'S_pre.STORE[n_dest] = DEFINED (PINT 99)',
        'S_pre.STORE[n_tail] = DEFINED (PINT 7)',
        '$node_children(S_pre, HARRAY n_constant) = [HARRAY n_pool_child]',
        'n_pool_roots = $heap_count(HARRAY n_constant, $pools_nodes(S_pre.POOLS))',
        'n_pool_child_roots = $heap_count(HARRAY n_pool_child, $pools_nodes(S_pre.POOLS))',
        '$(n_pool_roots > 0)',
        '$array_iterator_ready(S_pre, parrayiterator_pre)',
        owners('S_pre', 'HARRAY n_first', 2), owners('S_pre', 'HARRAY n_child', 2),
        owners('S_pre', 'HCELL n_marker', 2),
    ] + pool('S_pre', 2) + public('S_pre')
    checks += seek('S_pre', 841, 'S_cache') + fields('S_cache', 'n_first', 'n_constant', 'n_old') + [
        'S_cache.TODO = (ARRAY_ITERATOR parrayiterator_cached "key-start") :: ptask_cache*',
        'parrayiterator_cached.CURRENT = REFERENCE n_outer',
        '$array_iterator_current_value(S_cache, parrayiterator_cached, REFERENCE n_outer) = (PARRAY n_old)',
        '$array_iterator_ready(S_cache, parrayiterator_cached)',
        owners('S_cache', 'HOBJECT n_object', 1), owners('S_cache', 'HCELL n_outer', 2),
        owners('S_cache', 'HARRAY n_child', 2),
        'S_bad_pool = S_cache[.ARRAYS[n_constant].ITEMS = [ENTRY (KINT 0) (ALIAS n_marker)]]',
        '~$array_iterator_owned_field(S_bad_pool, parrayiterator_cached)',
    ] + public('S_cache')
    checks += seek('S_cache', 842, 'S_key') + fields('S_key', 'n_first', 'n_second', 'n_new') + [
        'S_key.ARRAYS[n_second].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_second_child)),ENTRY (KINT 1) (DIRECT (PINT 17))]',
        singleton('S_key', 'n_second_child', 22), row_items('S_key', 'n_new', 'n_new_child'),
        singleton('S_key', 'n_new_child', 11),
        'n_second =/= n_constant', 'n_second_child =/= n_pool_child',
        '~((HARRAY n_old) <- S_key.ALLOCATIONS)',
        'S_key_global = $global_table_view(S_key)',
        '$lookup(S_key_global.ENV, $ptascii("escaped")) = (n_outer)',
        'n_new_child_roots = $heap_count(HARRAY n_new_child, $pools_nodes(S_key.POOLS))',
        '$(n_new_child_roots > 0)',
        owners('S_key', 'HARRAY n_child', 1),
        owners('S_key', 'HCELL n_outer', 3),
    ] + pool('S_key', 1) + public('S_key')
    return checks


def mutated(start, row_root):
    return seek(start, 846, 'S_mutated') + fields('S_mutated', 'n_first_private', 'n_second', row_root) + [
        first_items('S_mutated', 'n_first_private', 'n_first_child'),
        singleton('S_mutated', 'n_first_child', 44),
        row_items('S_mutated', row_root, 'n_row_child'),
        singleton('S_mutated', 'n_row_child', 55),
        'n_first_private =/= n_first', 'n_first_child =/= n_child',
        'n_row_child =/= n_new_child',
        singleton('S_mutated', 'n_new_child', 11),
        first_items('S_mutated', 'n_first', 'n_child'), singleton('S_mutated', 'n_child', 3),
        'S_mutated.STORE[n_leaf] = DEFINED (PINT 31)',
        'S_mutated.STORE[n_other] = DEFINED (PINT 42)',
        'S_mutated.STORE[n_marker] = DEFINED (PINT 1)',
        'S_mutated.STORE[n_tail] = DEFINED (PINT 20)',
        'S_mutated.STORE[n_dest] = DEFINED (PINT 99)',
        '$weakref_get(S_mutated, n_observer) = POBJECT n_object',
        owners('S_mutated', 'HARRAY n_child', 1),
        owners('S_mutated', 'HARRAY n_first_private', 1),
        owners('S_mutated', 'HCELL n_outer', 2),
    ] + pool('S_mutated', 1) + public('S_mutated')


def retired(state, row_root):
    return [f'~((HOBJECT n_object) <- {state}.ALLOCATIONS)',
            f'~((HARRAY n_first_private) <- {state}.ALLOCATIONS)',
            f'~((HARRAY n_first_child) <- {state}.ALLOCATIONS)',
            f'~((HARRAY n_second) <- {state}.ALLOCATIONS)',
            f'~((HARRAY n_second_child) <- {state}.ALLOCATIONS)',
            f'$weakref_get({state}, n_observer) = PNULL',
            f'$lookup({state}.ENV, $ptascii("escaped")) = (n_outer)',
            f'{state}.STORE[n_outer] = DEFINED (PARRAY {row_root})',
            owners(state, 'HCELL n_outer', 1), owners(state, 'HCELL n_marker', 1)]


def conditions(name, program, path, stdout):
    normal = name == SELECTED[0]
    checks = common(program, path)
    if normal:
        checks += seek('S_key', 843, 'S_insert_ready') + [
            'S_insert_ready.TODO = (ARRAY_ITERATOR parrayiterator_insert "insert") :: ptask_insert*',
            'parrayiterator_insert.CURRENT = REFERENCE n_outer',
            '$array_iterator_current_value(S_insert_ready, parrayiterator_insert, REFERENCE n_outer) = (PARRAY n_new)',
            'PhpStep: S_insert_ready ~> S_insert',
            'S_insert.ARRAYS[n_target].ITEMS = [ENTRY (KINT 4) (DIRECT (PINT 8)),ENTRY (KSTRING ($ptascii("row"))) (DIRECT (PARRAY n_new))]',
            owners('S_insert', 'HARRAY n_new', 2),
            owners('S_insert', 'HARRAY n_new_child', '$(n_new_child_roots + 1)'),
        ] + public('S_insert') + budget('S_insert_ready', 'S_insert_budget')
        checks += seek('S_insert', 844, 'S_finish') + [
            'S_finish.TODO = (ARRAY_ITERATOR parrayiterator_finish "finish") :: ptask_finish*',
            'PhpStep: S_finish ~> S_release',
            'S_release.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (ARRAY_ITERATOR_RELEASE parrayiterator_finish "normal") :: ptask_finish*',
            'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_object)]',
        ] + seek('S_release', 845, 'S_dtor')
    else:
        checks += ['S_key_global.STORE[n_dest] = DEFINED (PINT 99)'] + seek('S_key', 845, 'S_dtor')
    checks += [owners('S_dtor', 'HCELL n_outer', 2),
               '$weakref_get(S_dtor, n_observer) = POBJECT n_object'] + public('S_dtor')
    row_root = 'n_row_private' if normal else 'n_new'
    checks += mutated('S_dtor', row_root)
    if normal:
        checks += ['n_row_private =/= n_new', row_items('S_mutated', 'n_new', 'n_new_child'),
                   owners('S_mutated', 'HARRAY n_new', 1)]
    else:
        checks += [owners('S_mutated', 'HARRAY n_new', 1),
                   owners('S_mutated', 'HARRAY n_new_child', 'n_new_child_roots')]
    state = 'S_read' if normal else 'S_caught'
    checks += seek('S_mutated', 847 if normal else 848, state) + retired(state, row_root) + [
        f'{state}.STORE[n_leaf] = DEFINED (PINT 31)',
        f'{state}.STORE[n_other] = DEFINED (PINT 42)',
        row_items(state, row_root, 'n_row_child'), singleton(state, 'n_row_child', 55),
    ]
    if normal:
        checks += [f'{state}.STORE[n_dest] = DEFINED (PARRAY n_target)',
                   f'{state}.STORE[n_tail] = DEFINED (PINT 21)',
                   f'{state}.ARRAYS[n_target].ITEMS = [ENTRY (KINT 4) (DIRECT (PINT 8)),ENTRY (KSTRING ($ptascii("row"))) (DIRECT (PARRAY n_new)),ENTRY (KINT 5) (DIRECT (PINT 20))]',
                   row_items(state, 'n_new', 'n_new_child')]
    else:
        checks += [f'$lookup({state}.ENV, $ptascii("first_error")) = (n_error)',
                   f'{state}.STORE[n_error] = DEFINED (POBJECT n_original)',
                   f'$lookup({state}.ENV, $ptascii("e")) = (n_caught)',
                   f'{state}.STORE[n_caught] = DEFINED (POBJECT n_original)',
                   f'$throwable_field({state}, n_original, "previous") = PNULL',
                   f'~((HARRAY n_target) <- {state}.ALLOCATIONS)',
                   f'{state}.STORE[n_dest] = DEFINED (PINT 99)',
                   f'{state}.STORE[n_tail] = DEFINED (PINT 20)']
    checks += pool(state, 1) + public(state) + finish(state, stdout, [
        'HOBJECT n_object', 'HOBJECT n_observer', 'HCELL n_outer',
        'HCELL n_leaf', 'HCELL n_other', 'HCELL n_marker', 'HARRAY n_first',
        'HARRAY n_child', 'HARRAY n_old', 'HARRAY n_second', 'HARRAY n_second_child',
        'HARRAY n_first_private', 'HARRAY n_first_child', 'HARRAY n_new',
        'HARRAY n_row_child', 'HARRAY n_target',
    ] + (['HARRAY n_row_private'] if normal else ['HOBJECT n_original']))
    checks += [
        '(HARRAY n_new_child) <- S_done.ALLOCATIONS',
        singleton('S_done', 'n_new_child', 11),
        owners('S_done', 'HARRAY n_new_child', 'n_new_child_roots'),
    ] + pool('S_done', 0)
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(AUTHOR, conditions, HELPERS, model_timeout=300, extra_inputs=(
        Path(__file__), Path(__file__).with_name('array_aggregate_unpack_state_review.py'),
        Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
