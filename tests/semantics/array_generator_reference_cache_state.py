#!/usr/bin/env python3
"""A retained scalar alias survives Generator VALUE, spread and selected COW."""
from pathlib import Path
from types import SimpleNamespace

import array_generator_reference_cache_cases as cases
import list_missing_warning_protocol as shared
from array_aggregate_unpack_state_review import initial, seek
from array_generator_unpack_state_review import budget, finish, owners, public

CASE = 'array-generator-reference-cache-alias-retained'
AUTHOR = SimpleNamespace(CASES={CASE: cases.CASES[CASE]}, __file__=cases.__file__)

HELPERS = shared.HELPERS + r'''
dec $generator_reference_cache_echo(pstate, ptbytes) : bool
def $generator_reference_cache_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $generator_reference_cache_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 210) = true
  -- if S.TODO = (ARRAY_UNPACK n phpType13* z) :: ptask*
def $list_warning_frontier(S, 211) = true
  -- if S.TODO = (ARRAY_GENERATOR parraygenerator "ready") :: ptask*
  -- if S.OBJECTS[parraygenerator.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_PAUSED
def $list_warning_frontier(S, 212) = true
  -- if S.TODO = (ARRAY_GENERATOR parraygenerator "next") :: ptask*
def $list_warning_frontier(S, 213) = true
  -- if S.TODO = (ARRAY_GENERATOR parraygenerator "ready") :: ptask*
  -- if S.OBJECTS[parraygenerator.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_CLOSED
def $list_warning_frontier(S, 214) = true
  -- if S.TODO = (ARRAY_GENERATOR parraygenerator "data-released") :: ptask*
def $list_warning_frontier(S, 215) = true
  -- if S.TODO = (ARRAY_GENERATOR parraygenerator "input-released") :: ptask*
def $list_warning_frontier(S, 216) = $generator_reference_cache_echo(S, $ptascii("D:"))
def $list_warning_frontier(S, 217) = $generator_reference_cache_echo(S, $ptascii("R:"))
'''


def row(state, value, second=7):
    return [
        f'{state}.ARRAYS[n_row].ITEMS = [ENTRY (KINT 0) (ALIAS n_leaf),ENTRY (KINT 1) (DIRECT (PINT {second}))]',
        f'{state}.STORE[n_leaf] = DEFINED (PINT {value})',
        f'$node_children({state}, HARRAY n_row) = [HCELL n_leaf]',
        f'$node_children({state}, HCELL n_leaf) = eps',
    ]


def conditions(name, program, path, stdout):
    assert name == CASE
    checks = initial(program, path) + seek('S_initial', 210, 'S_pre') + [
        'S_pre.TODO = (ARRAY_UNPACK n_target phpType13* z) :: ptask_tail*',
        'S_pre.RESULT = VARIABLE ($ptascii("it")) z',
        '$lookup(S_pre.ENV, $ptascii("it")) = (n_it)',
        'S_pre.STORE[n_it] = DEFINED (POBJECT n_object)',
        '$lookup(S_pre.ENV, $ptascii("watch")) = (n_watch_cell)',
        'S_pre.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
        'S_pre.OBJECTS[n_watch] = WEAKREFERENCE (n_object)',
        '$weakref_get(S_pre, n_watch) = POBJECT n_object',
        '$lookup(S_pre.ENV, $ptascii("leaf")) = (n_leaf)',
        'n_leaf <- S_pre.REFCELLS',
        '$lookup(S_pre.ENV, $ptascii("row")) = (n_row_cell)',
        'S_pre.STORE[n_row_cell] = DEFINED (PARRAY n_row)',
        'S_pre.ARRAYS[n_target].ITEMS = [ENTRY (KINT 4) (DIRECT (PINT 8))]',
        '$array_generator_plan(S_pre) = (parraygenerator)',
        'parraygenerator.OBJECT = n_object',
        'parraygenerator.ARRAY = n_target',
        '$array_generator_builder(S_pre, parraygenerator)',
        '$array_iterator_reference_table(S_pre, n_row)',
        '$array_iterator_value(S_pre, KNOWN (PARRAY n_row)) = eps',
        'PhpStep: S_pre ~> S_active',
        'S_active.TODO = (ARRAY_GENERATOR parraygenerator "rewind") :: ptask_tail*',
        owners('S_active', 'HOBJECT n_object', 2),
    ] + row('S_pre', 2) + public('S_pre') + budget('S_pre', 'S_start_budget')
    checks += seek('S_active', 211, 'S_cache') + [
        'S_cache.TODO = (ARRAY_GENERATOR parraygenerator "ready") :: ptask_tail*',
        'S_cache.OBJECTS[n_object] = GENERATOR pgenerator_cache',
        'pgenerator_cache.VALUE = (PARRAY n_row)',
        'pgenerator_cache.REFCELL = eps',
        'pgenerator_cache.PHASE = GENERATOR_PAUSED',
        '~$generator_reference_producer(S_cache, pgenerator_cache)',
        '$array_generator_value(S_cache, parraygenerator) = (PARRAY n_row)',
        '$array_generator_cache(S_cache, parraygenerator)',
        '$array_generator_ready(S_cache, parraygenerator)',
        '$weakref_get(S_cache, n_watch) = POBJECT n_object',
        '$lookup(S_cache.ENV, $ptascii("it")) = eps',
        '~((HCELL n_it) <- S_cache.ALLOCATIONS)',
        owners('S_cache', 'HOBJECT n_object', 1),
        owners('S_cache', 'HARRAY n_row', 2),
        owners('S_cache', 'HCELL n_leaf', 2),
        'PhpStep: S_cache ~> S_insert',
        'S_insert.TODO = (ARRAY_GENERATOR parraygenerator "next") :: ptask_tail*',
        '$entry_lookup(S_insert.ARRAYS[n_target].ITEMS, KSTRING ($ptascii("ref"))) = (DIRECT (PARRAY n_row))',
        '$array_generator_builder(S_insert, parraygenerator)',
        '~$array_null_const_items(S_insert, S_insert.ARRAYS[n_target].ITEMS, [n_target])',
        '$array_iterator_reference_items(S_insert, n_target, S_insert.ARRAYS[n_target].ITEMS, [n_target])',
        owners('S_insert', 'HARRAY n_row', 3),
        owners('S_insert', 'HCELL n_leaf', 2),
    ] + row('S_cache', 2) + public('S_cache') + public('S_insert') + budget('S_cache', 'S_insert_budget')
    checks += seek('S_insert', 213, 'S_closed') + [
        'S_closed.OBJECTS[n_object] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED',
        'pgenerator_closed.VALUE = (PARRAY n_row)',
        'pgenerator_closed.FRAME = eps',
        'pgenerator_closed.REFCELL = eps',
        '$array_generator_ready(S_closed, parraygenerator)',
        '$weakref_get(S_closed, n_watch) = POBJECT n_object',
        owners('S_closed', 'HOBJECT n_object', 1),
        owners('S_closed', 'HARRAY n_row', 3),
        owners('S_closed', 'HCELL n_leaf', 2),
    ] + row('S_closed', 3) + public('S_closed')
    checks += seek('S_closed', 214, 'S_data') + [
        '~((HOBJECT n_object) <- S_data.ALLOCATIONS)',
        '$array_generator_history(S_data, parraygenerator)',
        '$weakref_get(S_data, n_watch) = PNULL',
        owners('S_data', 'HARRAY n_row', 2),
        owners('S_data', 'HCELL n_leaf', 2),
    ] + public('S_data')
    checks += seek('S_data', 215, 'S_input') + [
        '$array_generator_nodes(parraygenerator, "input-released") = [HARRAY n_target]',
    ] + seek('S_input', 216, 'S_spread') + [
        '$lookup(S_spread.ENV, $ptascii("out")) = (n_out)',
        'S_spread.STORE[n_out] = DEFINED (PARRAY n_target)',
        '$entry_lookup(S_spread.ARRAYS[n_target].ITEMS, KSTRING ($ptascii("ref"))) = (DIRECT (PARRAY n_row))',
        '$weakref_get(S_spread, n_watch) = PNULL',
        '$duplicate_item(S_spread, n_row, ALIAS n_leaf) = ALIAS n_leaf',
        owners('S_spread', 'HARRAY n_row', 2),
        owners('S_spread', 'HCELL n_leaf', 2),
    ] + row('S_spread', 3) + public('S_spread')
    checks += seek('S_spread', 217, 'S_read') + [
        'S_read.STORE[n_row_cell] = DEFINED (PARRAY n_row)',
        'S_read.STORE[n_out] = DEFINED (PARRAY n_target)',
        '$entry_lookup(S_read.ARRAYS[n_target].ITEMS, KSTRING ($ptascii("ref"))) = (DIRECT (PARRAY n_copy))',
        'n_copy =/= n_row',
        'S_read.ARRAYS[n_copy].ITEMS = [ENTRY (KINT 0) (ALIAS n_leaf),ENTRY (KINT 1) (DIRECT (PINT 88))]',
        '$node_children(S_read, HARRAY n_copy) = [HCELL n_leaf]',
        owners('S_read', 'HARRAY n_row', 1),
        owners('S_read', 'HARRAY n_copy', 1),
        owners('S_read', 'HARRAY n_target', 1),
        owners('S_read', 'HCELL n_leaf', 3),
    ] + row('S_read', 44) + public('S_read')
    return checks + finish('S_read', stdout, [
        'HOBJECT n_object', 'HOBJECT n_watch', 'HCELL n_leaf',
        'HARRAY n_row', 'HARRAY n_copy', 'HARRAY n_target',
    ])


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(AUTHOR, conditions, HELPERS, extra_inputs=(
        Path(__file__), Path(__file__).with_name('array_aggregate_unpack_state_review.py'),
        Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
