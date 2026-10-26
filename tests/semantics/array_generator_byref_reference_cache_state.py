#!/usr/bin/env python3
"""A by-reference Generator keeps the outer cell separate from copied inner aliases."""
from pathlib import Path
from types import SimpleNamespace

import array_generator_byref_reference_cache_cases as cases
import list_missing_warning_protocol as shared
from array_aggregate_unpack_state_review import initial, seek
from array_generator_unpack_state_review import budget, finish, owners, public

SELECTED = ('array-generator-byref-reference-cache-rebound',
            'array-generator-byref-reference-cache-dropped')
AUTHOR = SimpleNamespace(CASES={name: cases.CASES[name] for name in SELECTED}, __file__=cases.__file__)

HELPERS = shared.HELPERS + r'''
dec $byref_cache_echo(pstate, ptbytes) : bool
def $byref_cache_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $byref_cache_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 300) = true
  -- if S.TODO = (ARRAY_UNPACK n phpType13* z) :: ptask*
def $list_warning_frontier(S, 301) = true
  -- if S.TODO = (ARRAY_GENERATOR parraygenerator "ready") :: ptask*
  -- if S.OBJECTS[parraygenerator.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_PAUSED
def $list_warning_frontier(S, 302) = true
  -- if S.TODO = (ARRAY_GENERATOR parraygenerator "next") :: ptask*
def $list_warning_frontier(S, 303) = true
  -- if S.TODO = (ARRAY_GENERATOR parraygenerator "ready") :: ptask*
  -- if S.OBJECTS[parraygenerator.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_CLOSED
def $list_warning_frontier(S, 304) = true
  -- if S.TODO = (ARRAY_GENERATOR parraygenerator "data-released") :: ptask*
def $list_warning_frontier(S, 305) = $byref_cache_echo(S, $ptascii("D:"))
def $list_warning_frontier(S, 306) = $byref_cache_echo(S, $ptascii("S:"))
def $list_warning_frontier(S, 307) = $byref_cache_echo(S, $ptascii("R:"))
'''


def old_row(state, first=2, second=7):
    return [
        f'{state}.ARRAYS[n_old].ITEMS = [ENTRY (KINT 0) (ALIAS n_leaf),ENTRY (KINT 1) (DIRECT (PINT {second}))]',
        f'{state}.STORE[n_leaf] = DEFINED (PINT {first})',
        f'$node_children({state}, HARRAY n_old) = [HCELL n_leaf]',
    ]


def new_row(state, first=11):
    return [
        f'{state}.ARRAYS[n_new].ITEMS = [ENTRY (KINT 0) (ALIAS n_other),ENTRY (KINT 1) (DIRECT (PINT 19))]',
        f'{state}.STORE[n_other] = DEFINED (PINT {first})',
        f'$node_children({state}, HARRAY n_new) = [HCELL n_other]',
    ]


def common(program, path, leaf_at_close, other_at_close):
    checks = initial(program, path) + seek('S_initial', 300, 'S_pre') + [
        'S_pre.TODO = (ARRAY_UNPACK n_target phpType13* z) :: ptask_tail*',
        'S_pre.RESULT = VARIABLE ($ptascii("it")) z',
        '$lookup(S_pre.ENV, $ptascii("it")) = (n_it)',
        'S_pre.STORE[n_it] = DEFINED (POBJECT n_object)',
        'S_pre.ARRAYS[n_target].ITEMS = [ENTRY (KINT 4) (DIRECT (PINT 8))]',
        '$array_generator_plan(S_pre) = (parraygenerator)',
        'parraygenerator.OBJECT = n_object', 'parraygenerator.ARRAY = n_target',
        '$array_generator_builder(S_pre, parraygenerator)',
        'PhpStep: S_pre ~> S_active',
        'S_active.TODO = (ARRAY_GENERATOR parraygenerator "rewind") :: ptask_tail*',
    ] + public('S_pre') + public('S_active') + budget('S_pre', 'S_start_budget')
    checks += seek('S_active', 301, 'S_cache') + [
        'S_cache.TODO = (ARRAY_GENERATOR parraygenerator "ready") :: ptask_tail*',
        'S_cache.OBJECTS[n_object] = GENERATOR pgenerator_cache',
        'pgenerator_cache.PHASE = GENERATOR_PAUSED',
        'pgenerator_cache.VALUE = eps', 'pgenerator_cache.REFCELL = (n_outer)',
        '$generator_reference_producer(S_cache, pgenerator_cache)',
        '$lookup(S_cache.ENV, $ptascii("row")) = (n_outer)',
        '$array_iterator_reference_cell(S_cache, n_outer) = (PARRAY n_old)',
        '$array_iterator_value(S_cache, REFERENCE n_outer) = eps',
        '$array_iterator_reference_table(S_cache, n_old)',
        '$array_generator_value(S_cache, parraygenerator) = (PARRAY n_old)',
        '$array_generator_ready(S_cache, parraygenerator)',
        '$lookup(S_cache.ENV, $ptascii("leaf")) = (n_leaf)',
        'n_leaf <- S_cache.REFCELLS',
        '$lookup(S_cache.ENV, $ptascii("it")) = eps',
        '$node_children(S_cache, HCELL n_outer) = [HARRAY n_old]',
        owners('S_cache', 'HOBJECT n_object', 1),
        owners('S_cache', 'HARRAY n_old', 1),
        'PhpStep: S_cache ~> S_insert',
        'S_insert.TODO = (ARRAY_GENERATOR parraygenerator "next") :: ptask_tail*',
        '$entry_lookup(S_insert.ARRAYS[n_target].ITEMS, KSTRING ($ptascii("ref"))) = (DIRECT (PARRAY n_old))',
        '$array_generator_builder(S_insert, parraygenerator)',
        '~$array_null_const_items(S_insert, S_insert.ARRAYS[n_target].ITEMS, [n_target])',
        '$array_iterator_reference_items(S_insert, n_target, S_insert.ARRAYS[n_target].ITEMS, [n_target])',
        owners('S_insert', 'HARRAY n_old', 2),
    ] + old_row('S_cache') + public('S_cache') + public('S_insert') + budget('S_cache', 'S_insert_budget')
    checks += seek('S_insert', 303, 'S_closed') + [
        'S_closed.OBJECTS[n_object] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED', 'pgenerator_closed.FRAME = eps',
        'pgenerator_closed.VALUE = eps', 'pgenerator_closed.REFCELL = (n_outer)',
        'S_closed.STORE[n_outer] = DEFINED (PARRAY n_new)',
        'n_new =/= n_old',
        '$lookup(S_closed.ENV, $ptascii("row")) = (n_outer)',
        '$lookup(S_closed.ENV, $ptascii("other")) = (n_other)',
        '$node_children(S_closed, HCELL n_outer) = [HARRAY n_new]',
        '$entry_lookup(S_closed.ARRAYS[n_target].ITEMS, KSTRING ($ptascii("ref"))) = (DIRECT (PARRAY n_old))',
        '$array_generator_builder(S_closed, parraygenerator)',
        '$array_generator_ready(S_closed, parraygenerator)',
        owners('S_closed', 'HOBJECT n_object', 1),
        owners('S_closed', 'HARRAY n_old', 1),
        owners('S_closed', 'HARRAY n_new', 1),
    ] + old_row('S_closed', leaf_at_close) + new_row('S_closed', other_at_close) + public('S_closed') + budget('S_closed', 'S_close_budget')
    checks += seek('S_closed', 304, 'S_data') + [
        'S_data.TODO = (ARRAY_GENERATOR parraygenerator "data-released") :: ptask_tail*',
        '~((HOBJECT n_object) <- S_data.ALLOCATIONS)',
        '$array_generator_history(S_data, parraygenerator)',
        '$array_generator_builder(S_data, parraygenerator)',
        'S_data.STORE[n_outer] = DEFINED (PARRAY n_new)',
        '$entry_lookup(S_data.ARRAYS[n_target].ITEMS, KSTRING ($ptascii("ref"))) = (DIRECT (PARRAY n_old))',
        owners('S_data', 'HARRAY n_old', 1),
        owners('S_data', 'HARRAY n_new', 1),
    ] + public('S_data')
    return checks


def rebound(program, path, stdout):
    checks = common(program, path, 3, 11) + [
        '$lookup(S_data.ENV, $ptascii("watch")) = (n_watch)',
        'S_data.STORE[n_watch] = DEFINED (POBJECT n_observer)',
        '$weakref_get(S_data, n_observer) = PNULL',
    ] + seek('S_data', 305, 'S_echo') + [
        '$lookup(S_echo.ENV, $ptascii("out")) = (n_out)',
        'S_echo.STORE[n_out] = DEFINED (PARRAY n_target)',
        '$entry_lookup(S_echo.ARRAYS[n_target].ITEMS, KSTRING ($ptascii("ref"))) = (DIRECT (PARRAY n_old))',
        'S_echo.STORE[n_outer] = DEFINED (PARRAY n_new)',
        '$weakref_get(S_echo, n_observer) = PNULL',
    ] + old_row('S_echo', 3) + new_row('S_echo') + public('S_echo')
    checks += seek('S_echo', 307, 'S_read') + [
        'S_read.STORE[n_out] = DEFINED (PARRAY n_target)',
        '$entry_lookup(S_read.ARRAYS[n_target].ITEMS, KSTRING ($ptascii("ref"))) = (DIRECT (PARRAY n_old))',
        'S_read.STORE[n_outer] = DEFINED (PARRAY n_new)',
        '$node_children(S_read, HCELL n_outer) = [HARRAY n_new]',
        owners('S_read', 'HARRAY n_old', 1),
        owners('S_read', 'HARRAY n_new', 1),
    ] + old_row('S_read', 44, 88) + new_row('S_read', 66) + public('S_read')
    return checks + finish('S_read', stdout, [
        'HOBJECT n_object', 'HOBJECT n_observer', 'HCELL n_outer', 'HCELL n_leaf',
        'HCELL n_other', 'HARRAY n_old', 'HARRAY n_new', 'HARRAY n_target',
    ])


def dropped(program, path, stdout):
    checks = common(program, path, 2, 9) + seek('S_data', 306, 'S_saved') + [
        '$lookup(S_saved.ENV, $ptascii("out")) = (n_out)',
        '$lookup(S_saved.ENV, $ptascii("saved")) = (n_saved)',
        'S_saved.STORE[n_out] = DEFINED (PARRAY n_target)',
        'S_saved.STORE[n_saved] = DEFINED (PARRAY n_old)',
        '$entry_lookup(S_saved.ARRAYS[n_target].ITEMS, KSTRING ($ptascii("ref"))) = (DIRECT (PARRAY n_old))',
        'S_saved.STORE[n_outer] = DEFINED (PARRAY n_new)',
        owners('S_saved', 'HARRAY n_old', 2),
    ] + old_row('S_saved') + new_row('S_saved', 9) + public('S_saved')
    checks += seek('S_saved', 307, 'S_read') + [
        'S_read.STORE[n_out] = DEFINED (PARRAY n_target)',
        'S_read.STORE[n_saved] = DEFINED (PARRAY n_old)',
        '$entry_lookup(S_read.ARRAYS[n_target].ITEMS, KSTRING ($ptascii("ref"))) = (DIRECT (PARRAY n_copy))',
        r'n_copy =/= n_old /\ n_copy =/= n_new',
        'S_read.ARRAYS[n_copy].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 2)),ENTRY (KINT 1) (DIRECT (PINT 88))]',
        '$node_children(S_read, HARRAY n_copy) = eps',
        'S_read.STORE[n_outer] = DEFINED (PARRAY n_new)',
        'S_read.STORE[n_leaf] = DEFINED (PINT 44)',
        owners('S_read', 'HARRAY n_old', 1),
        owners('S_read', 'HARRAY n_copy', 1),
        owners('S_read', 'HARRAY n_new', 1),
        owners('S_read', 'HCELL n_leaf', 1),
    ] + old_row('S_read', 44) + new_row('S_read', 9) + public('S_read')
    return checks + finish('S_read', stdout, [
        'HOBJECT n_object', 'HCELL n_outer', 'HCELL n_leaf', 'HCELL n_other',
        'HARRAY n_old', 'HARRAY n_copy', 'HARRAY n_new', 'HARRAY n_target',
    ])


def conditions(name, program, path, stdout):
    return (rebound if name == SELECTED[0] else dropped)(program, path, stdout)


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(AUTHOR, conditions, HELPERS, extra_inputs=(
        Path(__file__), Path(__file__).with_name('array_aggregate_unpack_state_review.py'),
        Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
