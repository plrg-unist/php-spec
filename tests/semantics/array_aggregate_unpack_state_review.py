#!/usr/bin/env python3
"""Aggregate acquisition roots, getter failure and sole CLOSED return cleanup."""
import base64
import json

import array_aggregate_unpack_review_cases as cases
import list_missing_warning_protocol as shared
from array_generator_unpack_state_review import budget, finish, owners, public

HELPERS = shared.HELPERS + r'''
dec $array_agg_review_echo(pstate, ptbytes) : bool
def $array_agg_review_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask_tail*
  -- if $base64(text) = n_prefix*
def $array_agg_review_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 100) = true
  -- if S.TODO = (ARRAY_UNPACK n phpType13* z) :: ptask_tail*
def $list_warning_frontier(S, 101) = true
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ARRAY_AGGREGATE parrayaggregate) :: ptask_tail*
  -- if $array_agg_review_echo(S, $ptascii("G;"))
def $list_warning_frontier(S, 102) = true
  -- if S.TODO = (ARRAY_AGGREGATE parrayaggregate) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 103) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ARRAY_AGGREGATE parrayaggregate) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 104) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ARRAY_GENERATOR parraygenerator "data-released") :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 105) = $array_agg_review_echo(S, $ptascii("C:"))
def $list_warning_frontier(S, 106) = $array_agg_review_echo(S, $ptascii("E:"))
def $list_warning_frontier(S, 107) = $array_agg_review_echo(S, $ptascii("D:"))
def $list_warning_frontier(S, 108) = $array_agg_review_echo(S, $ptascii("R:"))
def $list_warning_frontier(S, 109) = true
  -- if S.TODO = (THROW_VALUE porigin z) :: ptask_body*
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (ARRAY_AGGREGATE parrayaggregate) :: ptask_tail*
'''


def seek(start, stage, state):
    return [f'{state}_found = $list_warning_seek({start}, {stage}, 3000)',
            rf'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$list_warning_frontier({state}, {stage})']


def initial(program, path):
    return ['S_initial = $php_run(' + program + ', 0, '
            + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
            'S_initial.COMPLETION = BUDGET']


def output(state, value):
    return f'$list_warning_outputs({state}.EVENTS) = $ptascii({json.dumps(value)})'


def row(state, array, value):
    return f'{state}.ARRAYS[{array}].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT {value}))]'


def entry(program, path, line, entries):
    return initial(program, path) + seek('S_initial', 100, 'S_pre') + [
        'S_pre.TODO = (ARRAY_UNPACK n_target phpType13* z) :: ptask_tail*',
        f'z = {line}', 'S_pre.RESULT = VARIABLE ($ptascii("agg")) z',
        '$lookup(S_pre.ENV, $ptascii("agg")) = (n_agg)',
        '$lookup(S_pre.ENV, $ptascii("hold")) = (n_hold)',
        'S_pre.STORE[n_agg] = DEFINED (POBJECT n_object)',
        'S_pre.STORE[n_hold] = DEFINED (POBJECT n_object)',
        '$lookup(S_pre.ENV, $ptascii("dest")) = (n_dest)',
        '$lookup(S_pre.ENV, $ptascii("later")) = (n_later)',
        'S_pre.STORE[n_dest] = DEFINED (PINT 99)', 'S_pre.STORE[n_later] = DEFINED (PINT 7)',
        f'S_pre.ARRAYS[n_target].ITEMS = {entries}',
        '$array_aggregate_plan(S_pre) = (parrayaggregate)',
        'parrayaggregate.ARRAY = n_target', 'parrayaggregate.OBJECT = n_object',
        'parrayaggregate.INPUT = S_pre.RESULT', 'parrayaggregate.TAIL = phpType13*',
        'parrayaggregate.LINE = z', 'S_pre.ORIGIN = (parrayaggregate.SITE)',
        '$array_aggregate_source(S_pre, parrayaggregate)',
        '$array_aggregate_receiver(S_pre, parrayaggregate)',
        '$array_aggregate_builder(S_pre, parrayaggregate)',
        owners('S_pre', 'HOBJECT n_object', 2), owners('S_pre', 'HARRAY n_target', 1),
        'PhpStep: S_pre ~> S_called',
        'S_called.TODO = (CALL_ARGS (AGGREGATE_METHOD_TARGET n_object parrayaggregate.METHOD) eps 0 eps (parrayaggregate.SITE) z) :: (ARRAY_AGGREGATE parrayaggregate) :: ptask_tail*',
        '$target_nodes(AGGREGATE_METHOD_TARGET n_object parrayaggregate.METHOD) = eps',
        '$task_nodes(ARRAY_AGGREGATE parrayaggregate) = [HARRAY n_target]',
        '$array_aggregate_valid(S_called, parrayaggregate)',
        owners('S_called', 'HOBJECT n_object', 2), owners('S_called', 'HARRAY n_target', 1),
        'S_called.ITERATORS = S_pre.ITERATORS', 'S_called.NEXTITER = S_pre.NEXTITER',
    ] + public('S_pre') + public('S_called')


def source_controls(state):
    return [
        f'~$array_aggregate_source({state}[.CODE = eps], parrayaggregate)',
        f'~$array_aggregate_source({state}[.SOURCES = eps], parrayaggregate)',
        f'~$array_aggregate_source({state}, parrayaggregate[.LINE = $(z + 1)])',
        f'~$array_aggregate_source({state}, parrayaggregate[.METHOD = PORIGIN 0 eps])',
        f'~$array_aggregate_source({state}, parrayaggregate[.TAIL = eps])',
        f'~$array_aggregate_source({state}, parrayaggregate[.INPUT = KNOWN (POBJECT n_object)])',
    ]


def self_return(program, path, stdout):
    checks = entry(program, path, 11, '[ENTRY (KINT 0) (DIRECT (PINT 8))]')
    checks += source_controls('S_pre') + [
        '$lookup(S_pre.ENV, $ptascii("calls")) = (n_calls)',
        'S_pre.STORE[n_calls] = DEFINED (PINT 0)',
    ] + seek('S_called', 101, 'S_getter') + [
        'S_getter.CURRENT = (pcallcontext)',
        'pcallcontext.TARGET = AGGREGATE_METHOD_TARGET n_object parrayaggregate.METHOD',
        'pcallcontext.RECEIVER = (n_object)', 'pcallcontext.INSTANCE = eps',
        '$call_receiver_roots(pcallcontext) = eps',
        'S_getter.FRAMES = pframe :: eps',
        'pframe.TODO = (ARRAY_AGGREGATE parrayaggregate) :: ptask_tail*',
        'S_getter.STORE[n_calls] = DEFINED (PINT 1)',
        owners('S_getter', 'HOBJECT n_object', 2),
        owners('S_getter', 'HARRAY n_target', 1),
    ] + public('S_getter')
    checks += seek('S_getter', 102, 'S_return') + [
        'S_return.RESULT = KNOWN (POBJECT n_object)',
        '$array_aggregate_valid(S_return, parrayaggregate)',
        '$array_aggregate_self(S_return, parrayaggregate)',
        '$array_aggregate_ready(S_return, parrayaggregate)',
        '$array_aggregate_iterator(S_return, parrayaggregate) = eps',
        '$array_aggregate_generator(S_return, parrayaggregate) = eps',
        owners('S_return', 'HOBJECT n_object', 3),
        owners('S_return', 'HARRAY n_target', 1),
        'S_return.STORE[n_agg] = DEFINED (POBJECT n_object)',
        'S_return.STORE[n_hold] = DEFINED (POBJECT n_object)',
        'S_rebound = S_return[.STORE[n_agg] = DEFINED (PINT 42)]',
        '$heap_valid($heap_graph(S_rebound))', '$call_descriptors_valid(S_rebound)',
        '$array_aggregate_source(S_rebound, parrayaggregate)',
        '~$array_aggregate_self(S_rebound, parrayaggregate)',
        '~$array_aggregate_ready(S_rebound, parrayaggregate)',
        'PhpStep: S_rebound ~> S_refused',
        'S_refused = S_rebound[.COMPLETION = UNSUPPORTED "array Aggregate unpack return outside admitted domain"]',
        '$array_aggregate_blocked(S_refused)', '$drive_steps(S_refused, 1) = S_refused',
        'PhpStep: S_return ~> S_error',
        'S_error.COMPLETION = THROWN "Exception" ($ptascii("Objects returned by ArrayAggregateSelf::getIterator() must be traversable or implement interface Iterator")) 11',
        'S_error.RESULT = KNOWN PNULL', 'S_error.STORE = S_return.STORE',
        'S_error.ARRAYS = S_return.ARRAYS', 'S_error.OBJECTS = S_return.OBJECTS',
        owners('S_error', 'HOBJECT n_object', 2),
        owners('S_error', 'HARRAY n_target', 1),
    ] + public('S_return') + budget('S_return', 'S_reject_budget')
    checks += seek('S_return', 103, 'S_pending') + [
        'S_pending.TODO = (THROW_SEARCH n_error) :: (ARRAY_AGGREGATE parrayaggregate) :: ptask_tail*',
        '$throwable_field(S_pending, n_error, "line") = PINT 11',
        '$throwable_field(S_pending, n_error, "previous") = PNULL',
        '$throwable_field(S_pending, n_error, "trace") = PARRAY n_trace',
        'S_pending.ARRAYS[n_trace].ITEMS = eps',
        owners('S_pending', 'HOBJECT n_object', 2),
        owners('S_pending', 'HARRAY n_target', 1),
        'S_pending.STORE[n_dest] = DEFINED (PINT 99)',
        'S_pending.STORE[n_later] = DEFINED (PINT 7)',
        'PhpStep: S_pending ~> S_dropped',
        'S_dropped.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
        owners('S_dropped', 'HARRAY n_target', 0),
    ] + public('S_pending')
    checks += seek('S_pending', 106, 'S_caught') + [
        '~((HARRAY n_target) <- S_caught.ALLOCATIONS)',
        'S_caught.STORE[n_calls] = DEFINED (PINT 1)',
        'S_caught.STORE[n_agg] = DEFINED (POBJECT n_object)',
        'S_caught.STORE[n_hold] = DEFINED (POBJECT n_object)',
        'S_caught.STORE[n_dest] = DEFINED (PINT 99)',
        'S_caught.STORE[n_later] = DEFINED (PINT 7)',
        owners('S_caught', 'HOBJECT n_object', 2),
    ] + public('S_caught')
    return checks + finish('S_caught', stdout, ['HOBJECT n_object', 'HARRAY n_target'])


def getter_throw(program, path, stdout):
    checks = entry(program, path, 13, '[ENTRY (KINT 0) (DIRECT (PARRAY n_old))]')
    checks += [
        '$lookup(S_pre.ENV, $ptascii("row")) = (n_row)',
        '$lookup(S_pre.ENV, $ptascii("before")) = (n_before)',
        'S_pre.STORE[n_row] = DEFINED (PARRAY n_old)',
        'S_pre.STORE[n_before] = DEFINED (PARRAY n_old)', row('S_pre', 'n_old', 2),
        owners('S_pre', 'HARRAY n_old', 3),
        '$lookup(S_pre.ENV, $ptascii("watch")) = (n_watch_cell)',
        'S_pre.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
        'S_pre.OBJECTS[n_watch] = WEAKREFERENCE (n_object)',
        '$lookup(S_pre.ENV, $ptascii("second")) = (n_second_cell)',
        'S_pre.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        '$throwable_field(S_pre, n_second, "trace") = PARRAY n_trace',
        'S_pre.ARRAYS[n_trace].ITEMS = eps',
    ] + seek('S_called', 101, 'S_getter') + [
        'S_getter.CURRENT = (pcallcontext)',
        'pcallcontext.TARGET = AGGREGATE_METHOD_TARGET n_object parrayaggregate.METHOD',
        '$call_receiver_roots(pcallcontext) = eps',
        owners('S_getter', 'HOBJECT n_object', 2),
        owners('S_getter', 'HARRAY n_old', 3),
    ] + public('S_getter')
    checks += seek('S_getter', 109, 'S_throw') + [
        'S_throw.CURRENT = (pcallcontext)',
        'S_throw.FRAMES = pframe :: eps',
        'pframe.TODO = (ARRAY_AGGREGATE parrayaggregate) :: ptask_tail*',
        'S_throw.RESULT = KNOWN (POBJECT n_second)',
        'S_throw.STORE[n_row] = DEFINED (PARRAY n_new)',
        'n_new =/= n_old', row('S_throw', 'n_new', 44), row('S_throw', 'n_old', 2),
        owners('S_throw', 'HOBJECT n_object', 1),
        owners('S_throw', 'HARRAY n_target', 1),
        owners('S_throw', 'HARRAY n_old', 2), owners('S_throw', 'HARRAY n_new', 1),
        '$weakref_get(S_throw, n_watch) = POBJECT n_object',
        output('S_throw', 'P;G;'),
    ] + public('S_throw')
    checks += seek('S_throw', 103, 'S_pending') + [
        'S_pending.TODO = (THROW_SEARCH n_second) :: (ARRAY_AGGREGATE parrayaggregate) :: ptask_tail*',
        '$array_aggregate_valid(S_pending, parrayaggregate)',
        '$lookup(S_pending.ENV, $ptascii("agg")) = eps',
        'S_pending.STORE[n_hold] = DEFINED (POBJECT n_object)',
        'S_pending.STORE[n_dest] = DEFINED (PINT 99)',
        'S_pending.STORE[n_later] = DEFINED (PINT 7)',
        '$throwable_field(S_pending, n_second, "trace") = PARRAY n_trace',
        'S_pending.ARRAYS[n_trace].ITEMS = eps',
        '$throwable_field(S_pending, n_second, "previous") = PNULL',
        owners('S_pending', 'HOBJECT n_object', 1),
        owners('S_pending', 'HARRAY n_target', 1),
        owners('S_pending', 'HARRAY n_old', 2),
        'S_pending.ITERATORS = S_pre.ITERATORS', 'S_pending.NEXTITER = S_pre.NEXTITER',
        'S_object_builder = S_pending[.ARRAYS[n_target].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_object))]]',
        '$heap_valid($heap_graph(S_object_builder))', '$call_descriptors_valid(S_object_builder)',
        '$array_aggregate_valid(S_object_builder, parrayaggregate)',
        '~$array_aggregate_builder(S_object_builder, parrayaggregate)',
        'PhpStep: S_object_builder ~> S_builder_refused',
        'S_builder_refused = S_object_builder[.COMPLETION = UNSUPPORTED "array Aggregate abrupt receiver or builder outside admitted domain"]',
        '$array_aggregate_blocked(S_builder_refused)',
        '$drive_steps(S_builder_refused, 1) = S_builder_refused',
        '~$array_aggregate_blocked(S_pending[.COMPLETION = UNSUPPORTED "array Aggregate abrupt receiver or builder outside admitted domain"])',
        'PhpStep: S_pending ~> S_dropped',
        'S_dropped.TODO = (THROW_SEARCH n_second) :: ptask_tail*',
        owners('S_dropped', 'HARRAY n_target', 0),
    ] + public('S_pending') + budget('S_pending', 'S_throw_budget')
    checks += seek('S_pending', 105, 'S_caught') + [
        '~((HARRAY n_target) <- S_caught.ALLOCATIONS)',
        owners('S_caught', 'HARRAY n_old', 1),
        owners('S_caught', 'HARRAY n_new', 1),
        owners('S_caught', 'HOBJECT n_object', 1),
        'S_caught.STORE[n_before] = DEFINED (PARRAY n_old)',
        'S_caught.STORE[n_row] = DEFINED (PARRAY n_new)',
        '$lookup(S_caught.ENV, $ptascii("e")) = (n_caught)',
        'S_caught.STORE[n_caught] = DEFINED (POBJECT n_second)',
    ] + public('S_caught')
    checks += seek('S_caught', 107, 'S_dead') + [
        '~((HOBJECT n_object) <- S_dead.ALLOCATIONS)',
        '$weakref_get(S_dead, n_watch) = PNULL',
        'S_dead.STORE[n_dest] = DEFINED (PINT 99)',
        'S_dead.STORE[n_later] = DEFINED (PINT 7)',
    ] + public('S_dead')
    return checks + finish('S_dead', stdout, ['HOBJECT n_object', 'HARRAY n_target',
        'HARRAY n_old', 'HARRAY n_new', 'HOBJECT n_second', 'HOBJECT n_watch'])


def closed_return(program, path, stdout):
    checks = entry(program, path, 16, '[ENTRY (KINT 0) (DIRECT (PARRAY n_prefix))]')
    checks += [
        '$lookup(S_pre.ENV, $ptascii("before")) = (n_before)',
        'S_pre.STORE[n_before] = DEFINED (PARRAY n_prefix)', row('S_pre', 'n_prefix', 3),
        '$lookup(S_pre.ENV, $ptascii("generator")) = (n_generator_cell)',
        'S_pre.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)',
        'S_pre.OBJECTS[n_generator] = GENERATOR pgenerator',
        'pgenerator.PHASE = GENERATOR_CLOSED', 'pgenerator.FRAME = eps',
        'pgenerator.VALUE = (PARRAY n_cached)', 'pgenerator.REFCELL = eps',
        'pgenerator.KEY = (PINT 0)', 'pgenerator.RETURN = (PNULL)',
        'n_cached =/= n_prefix', row('S_pre', 'n_cached', 2),
        '$heap_count(HARRAY n_cached, $pools_nodes(S_pre.POOLS)) = 0',
        owners('S_pre', 'HARRAY n_cached', 1), owners('S_pre', 'HARRAY n_prefix', 2),
        owners('S_pre', 'HOBJECT n_generator', 1),
        '$lookup(S_pre.ENV, $ptascii("watch")) = (n_watch_cell)',
        'S_pre.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
        'S_pre.OBJECTS[n_watch] = WEAKREFERENCE (n_generator)',
        '$weakref_get(S_pre, n_watch) = POBJECT n_generator',
    ] + seek('S_called', 102, 'S_return') + [
        'S_return.RESULT = KNOWN (POBJECT n_generator)',
        '$lookup(S_return.ENV, $ptascii("generator")) = eps',
        'S_return.OBJECTS[n_generator] = GENERATOR pgenerator',
        '$array_aggregate_ready(S_return, parrayaggregate)',
        '$array_aggregate_iterator(S_return, parrayaggregate) = eps',
        '$array_aggregate_generator(S_return, parrayaggregate) = (parraygenerator)',
        'parraygenerator.ARRAY = n_target', 'parraygenerator.OBJECT = n_generator',
        'parraygenerator.FUNCTION = pgenerator.FUNCTION',
        'parraygenerator.INPUT = parrayaggregate.INPUT',
        'parraygenerator.SITE = parrayaggregate.SITE', 'parraygenerator.LINE = 16',
        'parraygenerator.TAIL = parrayaggregate.TAIL',
        owners('S_return', 'HOBJECT n_generator', 1),
        owners('S_return', 'HARRAY n_cached', 1),
        owners('S_return', 'HARRAY n_prefix', 2),
        '$weakref_get(S_return, n_watch) = POBJECT n_generator',
        'PhpStep: S_return ~> S_rejected',
        'S_rejected.TODO = (ARRAY_GENERATOR parraygenerator "data-released") :: ptask_tail*',
        'S_rejected.COMPLETION = THROWN "Exception" ($ptascii("Cannot traverse an already closed generator")) 16',
        'S_rejected.RESULT = KNOWN PNULL',
        '$array_generator_nodes(parraygenerator, "data-released") = [HARRAY n_target]',
        owners('S_rejected', 'HOBJECT n_generator', 0),
        owners('S_rejected', 'HARRAY n_cached', 1),
        owners('S_rejected', 'HARRAY n_prefix', 2),
        '(HOBJECT n_generator) <- S_rejected.ALLOCATIONS',
    ] + public('S_return') + budget('S_return', 'S_closed_budget')
    checks += seek('S_return', 104, 'S_pending') + [
        'S_pending.TODO = (THROW_SEARCH n_error) :: (ARRAY_GENERATOR parraygenerator "data-released") :: ptask_tail*',
        '~((HOBJECT n_generator) <- S_pending.ALLOCATIONS)',
        '~((HARRAY n_cached) <- S_pending.ALLOCATIONS)',
        'S_pending.OBJECTS[n_generator] = GENERATOR pgenerator',
        '$weakref_get(S_pending, n_watch) = PNULL',
        '$array_generator_history(S_pending, parraygenerator)',
        '~$array_generator_source(S_pending, parraygenerator)',
        '$array_generator_valid(S_pending, parraygenerator, "data-released")',
        '$throwable_field(S_pending, n_error, "line") = PINT 16',
        '$throwable_field(S_pending, n_error, "previous") = PNULL',
        '$throwable_field(S_pending, n_error, "trace") = PARRAY n_trace',
        'S_pending.ARRAYS[n_trace].ITEMS = eps',
        owners('S_pending', 'HARRAY n_target', 1),
        owners('S_pending', 'HARRAY n_prefix', 2),
        row('S_pending', 'n_prefix', 3),
        output('S_pending', 'B;F;P;G;'),
        'S_pending.STORE[n_dest] = DEFINED (PINT 99)',
        'S_pending.STORE[n_later] = DEFINED (PINT 7)',
        'PhpStep: S_pending ~> S_input_released',
        'S_input_released.TODO = (THROW_SEARCH n_error) :: (ARRAY_GENERATOR parraygenerator "input-released") :: ptask_tail*',
        'PhpStep: S_input_released ~> S_dropped',
        'S_dropped.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
        owners('S_dropped', 'HARRAY n_target', 0),
    ] + public('S_pending') + public('S_input_released')
    checks += seek('S_pending', 106, 'S_caught') + [
        '~((HARRAY n_target) <- S_caught.ALLOCATIONS)',
        owners('S_caught', 'HARRAY n_prefix', 1),
        'S_caught.STORE[n_before] = DEFINED (PARRAY n_prefix)',
        'S_caught.STORE[n_dest] = DEFINED (PINT 99)',
        'S_caught.STORE[n_later] = DEFINED (PINT 7)',
        '$weakref_get(S_caught, n_watch) = PNULL',
    ] + public('S_caught')
    return checks + finish('S_caught', stdout, ['HOBJECT n_object', 'HOBJECT n_generator',
        'HARRAY n_target', 'HARRAY n_cached', 'HARRAY n_prefix', 'HOBJECT n_watch'])


def conditions(name, program, path, stdout):
    if name.endswith('self-return'):
        return self_return(program, path, stdout)
    if name.endswith('getter-supplied-throw'):
        return getter_throw(program, path, stdout)
    assert name.endswith('closed-owning-return')
    return closed_return(program, path, stdout)


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
