#!/usr/bin/env python3
"""A supplied throw retires Generator DATA before the protected reference graph."""
from pathlib import Path
from types import SimpleNamespace

import array_generator_reference_cache_cases as cases
import list_missing_warning_protocol as shared
from array_aggregate_unpack_state_review import initial, seek
from array_generator_unpack_state_review import budget, finish, owners, public

CASE = 'array-generator-reference-cache-body-throw'
PEER = SimpleNamespace(CASES={CASE: cases.CASES[CASE]}, __file__=cases.__file__)

HELPERS = shared.HELPERS + r'''
dec $generator_reference_echo(pstate, ptbytes) : bool
def $generator_reference_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $generator_reference_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 220) = true
  -- if S.TODO = (ARRAY_GENERATOR parraygenerator "ready") :: ptask*
  -- if S.OBJECTS[parraygenerator.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_PAUSED
def $list_warning_frontier(S, 221) = true
  -- if S.TODO = (THROW_VALUE porigin z) :: ptask*
  -- if S.CURRENT = (pcallcontext)
def $list_warning_frontier(S, 222) = $generator_reference_echo(S, $ptascii("F:"))
def $list_warning_frontier(S, 223) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ARRAY_GENERATOR parraygenerator "next") :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 224) = true
  -- if S.TODO = (GENERATOR_STORAGE_STEP pgenstorage) :: ptask*
  -- if pgenstorage.NEXT = 1
def $list_warning_frontier(S, 225) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ARRAY_GENERATOR parraygenerator "data-released") :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 226) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ARRAY_GENERATOR parraygenerator "input-released") :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 227) = $generator_reference_echo(S, $ptascii("C:"))
'''


def graph(state):
    return [
        f'{state}.ARRAYS[n_row].ITEMS = [ENTRY (KINT 0) (ALIAS n_leaf),ENTRY (KINT 1) (DIRECT (PINT 7))]',
        f'{state}.STORE[n_leaf] = DEFINED (PINT 2)',
        f'$node_children({state}, HARRAY n_row) = [HCELL n_leaf]',
        f'$node_children({state}, HCELL n_leaf) = eps',
    ]


def conditions(name, program, path, stdout):
    assert name == CASE
    checks = initial(program, path) + seek('S_initial', 220, 'S_first') + [
        'S_first.TODO = (ARRAY_GENERATOR parraygenerator "ready") :: ptask_tail*',
        'parraygenerator.OBJECT = n_object', 'parraygenerator.ARRAY = n_target',
        'S_first.OBJECTS[n_object] = GENERATOR pgenerator_first',
        'pgenerator_first.PHASE = GENERATOR_PAUSED',
        'pgenerator_first.VALUE = (PARRAY n_row)', 'pgenerator_first.REFCELL = eps',
        '~$generator_reference_producer(S_first, pgenerator_first)',
        '$lookup(S_first.ENV, $ptascii("it")) = eps',
        '$lookup(S_first.ENV, $ptascii("row")) = (n_row_cell)',
        'S_first.STORE[n_row_cell] = DEFINED (PARRAY n_row)',
        '$lookup(S_first.ENV, $ptascii("leaf")) = (n_leaf)',
        '$lookup(S_first.ENV, $ptascii("watch")) = (n_watch)',
        'S_first.STORE[n_watch] = DEFINED (POBJECT n_observer)',
        '$lookup(S_first.ENV, $ptascii("second")) = (n_second)',
        'S_first.STORE[n_second] = DEFINED (POBJECT n_exception)',
        '$lookup(S_first.ENV, $ptascii("dest")) = (n_dest)',
        '$lookup(S_first.ENV, $ptascii("later")) = (n_later)',
        'S_first.STORE[n_dest] = DEFINED (PINT 99)',
        'S_first.STORE[n_later] = DEFINED (PINT 7)',
        'S_first.ARRAYS[n_target].ITEMS = [ENTRY (KINT 4) (DIRECT (PINT 8))]',
        '$string_bytes($generator_cached_value(S_first, n_object, true)) = ($ptascii("ref"))',
        '$array_generator_ready(S_first, parraygenerator)',
        '$array_iterator_value(S_first, KNOWN (PARRAY n_row)) = eps',
        '$array_generator_value(S_first, parraygenerator) = (PARRAY n_row)',
        '$weakref_get(S_first, n_observer) = POBJECT n_object',
        owners('S_first', 'HOBJECT n_object', 1), owners('S_first', 'HARRAY n_row', 2),
        owners('S_first', 'HCELL n_leaf', 2), owners('S_first', 'HARRAY n_target', 1),
        'PhpStep: S_first ~> S_insert',
        'S_insert.TODO = (ARRAY_GENERATOR parraygenerator "next") :: ptask_tail*',
        '$entry_lookup(S_insert.ARRAYS[n_target].ITEMS, KSTRING ($ptascii("ref"))) = (DIRECT (PARRAY n_row))',
        'S_insert.OBJECTS[n_object] = GENERATOR pgenerator_first',
        owners('S_insert', 'HARRAY n_row', 3), owners('S_insert', 'HCELL n_leaf', 2),
    ] + graph('S_first') + public('S_first') + public('S_insert') + budget('S_first', 'S_insert_budget')
    checks += seek('S_insert', 221, 'S_throw') + [
        'S_throw.TODO = (THROW_VALUE porigin_throw z_throw) :: ptask_throw*',
        'S_throw.OBJECTS[n_object] = GENERATOR pgenerator_running',
        'pgenerator_running.PHASE = GENERATOR_RUNNING',
        'pgenerator_running.VALUE = (PARRAY n_row)',
        'S_throw_global = $global_table_view(S_throw)',
        '$lookup(S_throw_global.ENV, $ptascii("row")) = eps',
        '$lookup(S_throw_global.ENV, $ptascii("leaf")) = eps',
        '$list_warning_outputs(S_throw.EVENTS) = $ptascii("P:1;B;N;")',
        owners('S_throw', 'HOBJECT n_object', 1), owners('S_throw', 'HARRAY n_row', 2),
        owners('S_throw', 'HCELL n_leaf', 1), owners('S_throw', 'HARRAY n_target', 1),
    ] + graph('S_throw') + public('S_throw')
    checks += seek('S_throw', 222, 'S_finally') + [
        'S_finally.OBJECTS[n_object] = GENERATOR pgenerator_finally',
        'pgenerator_finally.PHASE = GENERATOR_RUNNING',
        'pgenerator_finally.VALUE = (PARRAY n_row)',
        'S_finally_global = $global_table_view(S_finally)',
        '$lookup(S_finally_global.ENV, $ptascii("row")) = eps',
        '$lookup(S_finally_global.ENV, $ptascii("leaf")) = eps',
        '$weakref_get(S_finally, n_observer) = POBJECT n_object',
        owners('S_finally', 'HOBJECT n_object', 1), owners('S_finally', 'HARRAY n_row', 2),
        owners('S_finally', 'HCELL n_leaf', 1),
    ] + public('S_finally')
    checks += seek('S_finally', 223, 'S_pending') + [
        'S_pending.TODO = (THROW_SEARCH n_exception) :: (ARRAY_GENERATOR parraygenerator "next") :: ptask_tail*',
        'S_pending.OBJECTS[n_object] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED', 'pgenerator_closed.FRAME = eps',
        'pgenerator_closed.VALUE = (PARRAY n_row)', 'pgenerator_closed.REFCELL = eps',
        'pgenerator_closed.RETURN = eps',
        'S_pending.OBJECTS[n_exception] = THROWABLE pthrowable',
        '$string_bytes($throwable_field(S_pending, n_exception, "message")) = ($ptascii("supplied"))',
        '$throwable_field(S_pending, n_exception, "previous") = PNULL',
        '$throwable_field(S_pending, n_exception, "trace") = PARRAY n_trace',
        'S_pending.ARRAYS[n_trace].ITEMS = eps',
        '$array_generator_ready(S_pending, parraygenerator)',
        '$list_warning_outputs(S_pending.EVENTS) = $ptascii("P:1;B;N;F:1::;")',
        owners('S_pending', 'HOBJECT n_object', 1), owners('S_pending', 'HARRAY n_target', 1),
        owners('S_pending', 'HARRAY n_row', 2), owners('S_pending', 'HCELL n_leaf', 1),
    ] + public('S_pending')
    checks += seek('S_pending', 224, 'S_storage') + [
        'S_storage.TODO = (GENERATOR_STORAGE_STEP pgenstorage) :: ptask_storage_tail*',
        'pgenstorage.OBJECT = n_object', 'pgenstorage.NEXT = 1',
        '$generator_storage_valid(S_storage, pgenstorage)',
        'S_storage.OBJECTS[n_object] = GENERATOR pgenerator_closed',
        '$node_children(S_storage, HOBJECT n_object) = [HARRAY n_row]',
        owners('S_storage', 'HOBJECT n_object', 1), owners('S_storage', 'HARRAY n_row', 2),
        owners('S_storage', 'HCELL n_leaf', 1),
        # Storage-pin ownership does not assert a PHP weak-get observation.
        'PhpStep: S_storage ~> S_transfer',
        'S_transfer = $generator_storage_release(S_storage[.TODO = (GENERATOR_STORAGE_STEP pgenstorage[.NEXT = 2]) :: ptask_storage_tail*], $destruction_values([HARRAY n_row]))',
        '$node_children(S_transfer, HOBJECT n_object) = eps',
        'S_transfer.OBJECTS[n_object] = GENERATOR pgenerator_closed',
        owners('S_transfer', 'HOBJECT n_object', 1), owners('S_transfer', 'HARRAY n_row', 2),
        owners('S_transfer', 'HCELL n_leaf', 1),
    ] + public('S_storage') + public('S_transfer') + budget('S_storage', 'S_storage_budget')
    checks += seek('S_transfer', 225, 'S_data') + [
        'S_data.TODO = (THROW_SEARCH n_exception) :: (ARRAY_GENERATOR parraygenerator "data-released") :: ptask_tail*',
        '~((HOBJECT n_object) <- S_data.ALLOCATIONS)',
        '$weakref_get(S_data, n_observer) = PNULL',
        '$array_generator_history(S_data, parraygenerator)',
        '~$array_generator_source(S_data, parraygenerator)',
        '$array_generator_valid(S_data, parraygenerator, "data-released")',
        # Historical VALUE is retained metadata; it contributes no Gen edge.
        'S_data.OBJECTS[n_object] = GENERATOR pgenerator_closed',
        owners('S_data', 'HOBJECT n_object', 0), owners('S_data', 'HARRAY n_target', 1),
        owners('S_data', 'HARRAY n_row', 1), owners('S_data', 'HCELL n_leaf', 1),
    ] + graph('S_data') + public('S_data')
    checks += seek('S_data', 226, 'S_input') + [
        'S_input.TODO = (THROW_SEARCH n_exception) :: (ARRAY_GENERATOR parraygenerator "input-released") :: ptask_tail*',
        '$array_generator_nodes(parraygenerator, "input-released") = [HARRAY n_target]',
        '$operand_nodes(parraygenerator.INPUT) = eps',
        'PhpStep: S_input ~> S_raw',
        'S_raw.TODO = (THROW_SEARCH n_exception) :: ptask_tail*',
        owners('S_raw', 'HARRAY n_target', 0), owners('S_raw', 'HARRAY n_row', 1),
        owners('S_raw', 'HCELL n_leaf', 1),
    ] + public('S_input') + budget('S_input', 'S_discard_budget')
    checks += seek('S_input', 227, 'S_caught') + [
        '$lookup(S_caught.ENV, $ptascii("e")) = (n_caught)',
        'S_caught.STORE[n_caught] = DEFINED (POBJECT n_exception)',
        'S_caught.STORE[n_second] = DEFINED (POBJECT n_exception)',
        'S_caught.STORE[n_dest] = DEFINED (PINT 99)',
        'S_caught.STORE[n_later] = DEFINED (PINT 7)',
        '$weakref_get(S_caught, n_observer) = PNULL',
        *[f'~(({node}) <- S_caught.ALLOCATIONS)' for node in [
            'HOBJECT n_object', 'HARRAY n_target', 'HARRAY n_row', 'HCELL n_leaf',
        ]],
        owners('S_caught', 'HARRAY n_row', 0), owners('S_caught', 'HCELL n_leaf', 0),
    ] + public('S_caught')
    return checks + finish('S_caught', stdout, [
        'HOBJECT n_object', 'HOBJECT n_exception', 'HOBJECT n_observer',
        'HARRAY n_target', 'HARRAY n_row', 'HCELL n_leaf',
    ])


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(PEER, conditions, HELPERS, extra_inputs=(
        Path(__file__),
        Path(__file__).with_name('array_aggregate_unpack_state_review.py'),
        Path(__file__).with_name('array_generator_unpack_state_review.py'),
    )) else 1)
