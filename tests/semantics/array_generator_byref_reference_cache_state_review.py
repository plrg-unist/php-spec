#!/usr/bin/env python3
"""A supplied throw retires the yielded outer cell before its copied row."""
from pathlib import Path
from types import SimpleNamespace

import array_generator_byref_reference_cache_cases as cases
import list_missing_warning_protocol as shared
from array_aggregate_unpack_state_review import initial, seek
from array_generator_unpack_state_review import budget, finish, owners, public

CASE = 'array-generator-byref-reference-cache-body-throw'
PEER = SimpleNamespace(CASES={CASE: cases.CASES[CASE]}, __file__=cases.__file__)

HELPERS = shared.HELPERS + r'''
dec $generator_byref_reference_echo(pstate, ptbytes) : bool
def $generator_byref_reference_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $generator_byref_reference_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 240) = true
  -- if S.TODO = (ARRAY_GENERATOR parraygenerator "ready") :: ptask*
  -- if S.OBJECTS[parraygenerator.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_PAUSED
def $list_warning_frontier(S, 241) = true
  -- if S.TODO = (THROW_VALUE porigin z) :: ptask*
  -- if S.CURRENT = (pcallcontext)
def $list_warning_frontier(S, 242) = $generator_byref_reference_echo(S, $ptascii("F:"))
def $list_warning_frontier(S, 243) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ARRAY_GENERATOR parraygenerator "next") :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 245) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ARRAY_GENERATOR parraygenerator "data-released") :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 246) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ARRAY_GENERATOR parraygenerator "input-released") :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 247) = $generator_byref_reference_echo(S, $ptascii("C:"))
'''


def graph(state):
    return [
        f'{state}.ARRAYS[n_row].ITEMS = [ENTRY (KINT 0) (ALIAS n_leaf),ENTRY (KINT 1) (DIRECT (PINT 7))]',
        f'{state}.STORE[n_leaf] = DEFINED (PINT 2)',
        f'$node_children({state}, HARRAY n_row) = [HCELL n_leaf]',
        f'$node_children({state}, HCELL n_leaf) = eps',
    ]


def outer(state):
    return [
        f'{state}.STORE[n_outer] = DEFINED (PARRAY n_row)',
        f'$node_children({state}, HCELL n_outer) = [HARRAY n_row]',
    ]


def conditions(name, program, path, stdout):
    assert name == CASE
    checks = initial(program, path) + seek('S_initial', 240, 'S_first') + [
        'S_first.TODO = (ARRAY_GENERATOR parraygenerator "ready") :: ptask_tail*',
        'parraygenerator.OBJECT = n_object', 'parraygenerator.ARRAY = n_target',
        'S_first.OBJECTS[n_object] = GENERATOR pgenerator_first',
        'pgenerator_first.PHASE = GENERATOR_PAUSED',
        'pgenerator_first.VALUE = eps', 'pgenerator_first.REFCELL = (n_outer)',
        '$generator_reference_producer(S_first, pgenerator_first)',
        'pgenerator_first.FRAME = (pframe_first)',
        'pframe_first.LOCALS = (psymboltable_first)',
        '$lookup(psymboltable_first.ENV, $ptascii("row")) = (n_outer)',
        '$lookup(S_first.ENV, $ptascii("it")) = eps',
        '$lookup(S_first.ENV, $ptascii("row")) = (n_outer)',
        'S_first.STORE[n_outer] = DEFINED (PARRAY n_row)',
        '$lookup(S_first.ENV, $ptascii("leaf")) = (n_leaf)',
        'n_outer =/= n_leaf',
        'n_outer <- S_first.REFCELLS', 'n_leaf <- S_first.REFCELLS',
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
        '$array_iterator_reference_cell(S_first, n_outer) = (PARRAY n_row)',
        '$array_iterator_value(S_first, REFERENCE n_outer) = eps',
        '$array_generator_value(S_first, parraygenerator) = (PARRAY n_row)',
        '$weakref_get(S_first, n_observer) = POBJECT n_object',
        owners('S_first', 'HOBJECT n_object', 1), owners('S_first', 'HCELL n_outer', 3),
        owners('S_first', 'HARRAY n_row', 1), owners('S_first', 'HCELL n_leaf', 2),
        owners('S_first', 'HARRAY n_target', 1),
        'PhpStep: S_first ~> S_insert',
        'S_insert.TODO = (ARRAY_GENERATOR parraygenerator "next") :: ptask_tail*',
        '$entry_lookup(S_insert.ARRAYS[n_target].ITEMS, KSTRING ($ptascii("ref"))) = (DIRECT (PARRAY n_row))',
        'S_insert.OBJECTS[n_object] = GENERATOR pgenerator_first',
        'S_insert.STORE = S_first.STORE',
        owners('S_insert', 'HCELL n_outer', 3), owners('S_insert', 'HARRAY n_row', 2),
        owners('S_insert', 'HCELL n_leaf', 2),
    ] + graph('S_first') + outer('S_first') + public('S_first') + public('S_insert') + budget('S_first', 'S_insert_budget')
    # A metadata-only helper refusal: the inner scalar cell remains ordinary,
    # but removing the outer reference marker cannot authorize a yield read.
    checks += [
        'S_unmarked = S_first[.REFCELLS = [n_leaf]]',
        '$heap_graph(S_unmarked) = $heap_graph(S_first)',
        '$array_iterator_reference_table(S_unmarked, n_row)',
        '$array_iterator_reference_cell(S_unmarked, n_outer) = eps',
        '$array_generator_value(S_unmarked, parraygenerator) = eps',
    ]
    checks += seek('S_insert', 241, 'S_throw') + [
        'S_throw.TODO = (THROW_VALUE porigin_throw z_throw) :: ptask_throw*',
        'S_throw.OBJECTS[n_object] = GENERATOR pgenerator_running',
        'pgenerator_running.PHASE = GENERATOR_RUNNING',
        'pgenerator_running.VALUE = eps', 'pgenerator_running.REFCELL = (n_outer)',
        '$lookup(S_throw.ENV, $ptascii("row")) = (n_outer)',
        'S_throw_global = $global_table_view(S_throw)',
        '$lookup(S_throw_global.ENV, $ptascii("row")) = eps',
        '$lookup(S_throw_global.ENV, $ptascii("leaf")) = eps',
        '$list_warning_outputs(S_throw.EVENTS) = $ptascii("P:1;B;N;")',
        owners('S_throw', 'HOBJECT n_object', 1), owners('S_throw', 'HCELL n_outer', 2),
        owners('S_throw', 'HARRAY n_row', 2), owners('S_throw', 'HCELL n_leaf', 1),
        owners('S_throw', 'HARRAY n_target', 1),
    ] + graph('S_throw') + outer('S_throw') + public('S_throw')
    checks += seek('S_throw', 242, 'S_finally') + [
        'S_finally.OBJECTS[n_object] = GENERATOR pgenerator_finally',
        'pgenerator_finally.PHASE = GENERATOR_RUNNING',
        'pgenerator_finally.VALUE = eps', 'pgenerator_finally.REFCELL = (n_outer)',
        'S_finally_global = $global_table_view(S_finally)',
        '$lookup(S_finally_global.ENV, $ptascii("row")) = eps',
        '$lookup(S_finally_global.ENV, $ptascii("leaf")) = eps',
        '$weakref_get(S_finally, n_observer) = POBJECT n_object',
        owners('S_finally', 'HOBJECT n_object', 1), owners('S_finally', 'HCELL n_outer', 2),
        owners('S_finally', 'HARRAY n_row', 2), owners('S_finally', 'HCELL n_leaf', 1),
    ] + outer('S_finally') + public('S_finally')
    checks += seek('S_finally', 243, 'S_pending') + [
        'S_pending.TODO = (THROW_SEARCH n_exception) :: (ARRAY_GENERATOR parraygenerator "next") :: ptask_tail*',
        'S_pending.OBJECTS[n_object] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED', 'pgenerator_closed.FRAME = eps',
        'pgenerator_closed.VALUE = eps', 'pgenerator_closed.REFCELL = (n_outer)',
        'pgenerator_closed.RETURN = eps',
        '$node_children(S_pending, HOBJECT n_object) = [HCELL n_outer]',
        'S_pending.OBJECTS[n_exception] = THROWABLE pthrowable',
        '$string_bytes($throwable_field(S_pending, n_exception, "message")) = ($ptascii("supplied"))',
        '$throwable_field(S_pending, n_exception, "previous") = PNULL',
        '$throwable_field(S_pending, n_exception, "trace") = PARRAY n_trace',
        'S_pending.ARRAYS[n_trace].ITEMS = eps',
        '$array_generator_ready(S_pending, parraygenerator)',
        '$list_warning_outputs(S_pending.EVENTS) = $ptascii("P:1;B;N;F:1::;")',
        owners('S_pending', 'HOBJECT n_object', 1), owners('S_pending', 'HCELL n_outer', 1),
        owners('S_pending', 'HARRAY n_target', 1), owners('S_pending', 'HARRAY n_row', 2),
        owners('S_pending', 'HCELL n_leaf', 1),
    ] + outer('S_pending') + public('S_pending')
    # The actual quiet DATA retirement removes the outer cell. Its historical
    # REFCELL field is source metadata, while the builder still owns the row.
    checks += seek('S_pending', 245, 'S_data') + [
        'S_data.TODO = (THROW_SEARCH n_exception) :: (ARRAY_GENERATOR parraygenerator "data-released") :: ptask_tail*',
        '~((HOBJECT n_object) <- S_data.ALLOCATIONS)',
        '~((HCELL n_outer) <- S_data.ALLOCATIONS)',
        '$weakref_get(S_data, n_observer) = PNULL',
        '$array_generator_history(S_data, parraygenerator)',
        '~$array_generator_source(S_data, parraygenerator)',
        '$array_generator_valid(S_data, parraygenerator, "data-released")',
        '$array_generator_builder(S_data, parraygenerator)',
        'S_data.OBJECTS[n_object] = GENERATOR pgenerator_closed',
        owners('S_data', 'HOBJECT n_object', 0), owners('S_data', 'HCELL n_outer', 0),
        owners('S_data', 'HARRAY n_target', 1), owners('S_data', 'HARRAY n_row', 1),
        owners('S_data', 'HCELL n_leaf', 1),
    ] + graph('S_data') + public('S_data')
    checks += seek('S_data', 246, 'S_input') + [
        'S_input.TODO = (THROW_SEARCH n_exception) :: (ARRAY_GENERATOR parraygenerator "input-released") :: ptask_tail*',
        '$array_generator_nodes(parraygenerator, "input-released") = [HARRAY n_target]',
        '$operand_nodes(parraygenerator.INPUT) = eps',
        'PhpStep: S_input ~> S_raw',
        'S_raw.TODO = (THROW_SEARCH n_exception) :: ptask_tail*',
        owners('S_raw', 'HARRAY n_target', 0), owners('S_raw', 'HCELL n_outer', 0),
        owners('S_raw', 'HARRAY n_row', 1), owners('S_raw', 'HCELL n_leaf', 1),
    ] + public('S_input') + budget('S_input', 'S_discard_budget')
    checks += seek('S_input', 247, 'S_caught') + [
        '$lookup(S_caught.ENV, $ptascii("e")) = (n_caught)',
        'S_caught.STORE[n_caught] = DEFINED (POBJECT n_exception)',
        'S_caught.STORE[n_second] = DEFINED (POBJECT n_exception)',
        'S_caught.STORE[n_dest] = DEFINED (PINT 99)',
        'S_caught.STORE[n_later] = DEFINED (PINT 7)',
        '$weakref_get(S_caught, n_observer) = PNULL',
        *[f'~(({node}) <- S_caught.ALLOCATIONS)' for node in [
            'HOBJECT n_object', 'HCELL n_outer', 'HARRAY n_target', 'HARRAY n_row', 'HCELL n_leaf',
        ]],
        owners('S_caught', 'HARRAY n_row', 0), owners('S_caught', 'HCELL n_leaf', 0),
    ] + public('S_caught')
    return checks + finish('S_caught', stdout, [
        'HOBJECT n_object', 'HCELL n_outer', 'HOBJECT n_exception', 'HOBJECT n_observer',
        'HARRAY n_target', 'HARRAY n_row', 'HCELL n_leaf',
    ])


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(PEER, conditions, HELPERS, extra_inputs=(
        Path(__file__),
        Path(__file__).with_name('array_aggregate_unpack_state_review.py'),
        Path(__file__).with_name('array_generator_unpack_state_review.py'),
    )) else 1)
