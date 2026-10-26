#!/usr/bin/env python3
"""Aggregate return transfer, retired receiver history and child-consumer COW."""
import array_aggregate_unpack_cases as cases
import list_missing_warning_protocol as shared
from array_aggregate_unpack_state_review import HELPERS, initial, seek
from array_generator_unpack_state_review import budget, finish, owners, public

HELPERS += r'''
def $list_warning_frontier(S, 110) = true
  -- if S.TODO = (ARRAY_ITERATOR parrayiterator "key-start") :: ptask*
def $list_warning_frontier(S, 111) = true
  -- if S.TODO = (ARRAY_ITERATOR parrayiterator "insert") :: ptask*
def $list_warning_frontier(S, 114) = true
  -- if S.TODO = (ARRAY_GENERATOR parraygenerator "ready") :: ptask*
  -- if S.OBJECTS[parraygenerator.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_PAUSED
def $list_warning_frontier(S, 115) = $array_agg_review_echo(S, $ptascii("D:"))
def $list_warning_frontier(S, 116) = $array_agg_review_echo(S, $ptascii("N;"))
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (GENERATOR_RESUME pgeneratorop) :: (ARRAY_GENERATOR parraygenerator "next") :: ptask*
def $list_warning_frontier(S, 117) = true
  -- if S.TODO = (ARRAY_GENERATOR parraygenerator "ready") :: ptask*
  -- if S.OBJECTS[parraygenerator.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_CLOSED
def $list_warning_frontier(S, 118) = true
  -- if S.TODO = (ARRAY_GENERATOR parraygenerator "data-released") :: ptask*
def $list_warning_frontier(S, 119) = true
  -- if S.TODO = (ARRAY_GENERATOR parraygenerator "input-released") :: ptask*
'''


def pair(state, array, first, second=7):
    return f'{state}.ARRAYS[{array}].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT {first})), ENTRY (KINT 1) (DIRECT (PINT {second}))]'


def entry(program, path, iterator):
    prefix = '[ENTRY (KSTRING ($ptascii("slot"))) (DIRECT (PINT 8)),ENTRY (KSTRING ($ptascii("prefix"))) (DIRECT (PARRAY n_old))]' if iterator else '[ENTRY (KSTRING ($ptascii("prefix"))) (DIRECT (PARRAY n_old))]'
    return initial(program, path) + seek('S_initial', 100, 'S_pre') + [
        'S_pre.TODO = (ARRAY_UNPACK n_target phpType13* z) :: ptask_tail*',
        'S_pre.RESULT = VARIABLE ($ptascii("agg")) z',
        '$array_aggregate_plan(S_pre) = (parrayaggregate)',
        'parrayaggregate.ARRAY = n_target', 'parrayaggregate.LINE = z',
        'parrayaggregate.INPUT = S_pre.RESULT', 'parrayaggregate.TAIL = phpType13*',
        'n_aggregate = parrayaggregate.OBJECT',
        '$lookup(S_pre.ENV, $ptascii("agg")) = (n_agg)',
        '$lookup(S_pre.ENV, $ptascii("hold")) = (n_hold)',
        'S_pre.STORE[n_agg] = DEFINED (POBJECT n_aggregate)',
        'S_pre.STORE[n_hold] = DEFINED (POBJECT n_aggregate)',
        '$lookup(S_pre.ENV, $ptascii("row")) = (n_row)',
        'S_pre.STORE[n_row] = DEFINED (PARRAY n_old)', pair('S_pre', 'n_old', 2),
        f'S_pre.ARRAYS[n_target].ITEMS = {prefix}',
        '$heap_count(HARRAY n_old, $pools_nodes(S_pre.POOLS)) = 0',
        owners('S_pre', 'HOBJECT n_aggregate', 2), owners('S_pre', 'HARRAY n_old', 2),
        owners('S_pre', 'HARRAY n_target', 1),
        'PhpStep: S_pre ~> S_call',
        'S_call.TODO = (CALL_ARGS (AGGREGATE_METHOD_TARGET n_aggregate parrayaggregate.METHOD) eps 0 eps (parrayaggregate.SITE) z) :: (ARRAY_AGGREGATE parrayaggregate) :: ptask_tail*',
        '$target_nodes(AGGREGATE_METHOD_TARGET n_aggregate parrayaggregate.METHOD) = eps',
        '$task_nodes(ARRAY_AGGREGATE parrayaggregate) = [HARRAY n_target]',
        'S_call.ITERATORS = S_pre.ITERATORS', 'S_call.NEXTITER = S_pre.NEXTITER',
        owners('S_call', 'HOBJECT n_aggregate', 2),
    ] + public('S_pre') + public('S_call') + budget('S_pre', 'S_call_budget') + seek('S_call', 101, 'S_getter') + [
        'S_getter.CURRENT = (pcallcontext)',
        'pcallcontext.TARGET = AGGREGATE_METHOD_TARGET n_aggregate parrayaggregate.METHOD',
        'pcallcontext.RECEIVER = (n_aggregate)', 'pcallcontext.INSTANCE = eps',
        '$call_receiver_roots(pcallcontext) = eps',
        'S_getter.FRAMES = pframe_getter :: eps',
        'pframe_getter.TODO = (ARRAY_AGGREGATE parrayaggregate) :: ptask_tail*',
        owners('S_getter', 'HOBJECT n_aggregate', 2), owners('S_getter', 'HARRAY n_target', 1),
    ] + public('S_getter') + seek('S_getter', 102, 'S_return') + [
        'S_return.RESULT = KNOWN (POBJECT n_child)', 'n_child =/= n_aggregate',
        '$lookup(S_return.ENV, $ptascii("agg")) = eps',
        '~((HCELL n_agg) <- S_return.ALLOCATIONS)',
        'S_return.STORE[n_hold] = DEFINED (POBJECT n_aggregate)',
        '$array_aggregate_valid(S_return, parrayaggregate)',
        '$array_aggregate_ready(S_return, parrayaggregate)',
        '~$array_aggregate_self(S_return, parrayaggregate)',
        owners('S_return', 'HOBJECT n_aggregate', 1), owners('S_return', 'HOBJECT n_child', 1),
        owners('S_return', 'HARRAY n_target', 1),
    ] + public('S_return')


def iterator_checks(program, path, stdout):
    checks = entry(program, path, True) + [
        '$array_aggregate_iterator(S_return, parrayaggregate) = (parrayiterator)',
        '$array_aggregate_generator(S_return, parrayaggregate) = eps',
        'parrayiterator.INPUT = parrayaggregate.INPUT', 'parrayiterator.OBJECT = n_child',
        'parrayiterator.ITERATOR = S_return.NEXTITER',
        'S_return.STORE[n_row] = DEFINED (PARRAY n_current)', pair('S_return', 'n_current', 11),
        'n_current =/= n_old', owners('S_return', 'HARRAY n_old', 1),
        owners('S_return', 'HARRAY n_current', 1),
        'PhpStep: S_return ~> S_promoted',
        'S_promoted = S_return[.ITERATORS = S_return.ITERATORS ++ [OBJECTITER parrayiterator.ITERATOR n_child 0 false]][.NEXTITER = $(S_return.NEXTITER + 1)][.TODO = (ARRAY_ITERATOR parrayiterator "rewind-start") :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$array_iterator_valid(S_promoted, parrayiterator, "rewind-start")',
        owners('S_promoted', 'HOBJECT n_child', 1), owners('S_promoted', 'HOBJECT n_aggregate', 1),
    ] + public('S_promoted') + budget('S_return', 'S_promote_budget') + seek('S_promoted', 110, 'S_cache') + [
        'S_cache.TODO = (ARRAY_ITERATOR parrayiterator_cache "key-start") :: ptask_tail*',
        'parrayiterator_cache = parrayiterator[.CURRENT = KNOWN (PARRAY n_current)]',
        '$array_iterator_ready(S_cache, parrayiterator_cache)',
        owners('S_cache', 'HARRAY n_current', 2), owners('S_cache', 'HARRAY n_old', 1),
    ] + public('S_cache') + seek('S_cache', 111, 'S_key') + [
        'S_key.TODO = (ARRAY_ITERATOR parrayiterator_key "insert") :: ptask_tail*',
        'parrayiterator_key.CURRENT = parrayiterator_cache.CURRENT',
        'parrayiterator_key.KEY = KNOWN pvalue_key',
        '$string_bytes(pvalue_key) = ($ptascii("slot"))',
        'S_key.STORE[n_row] = DEFINED (PARRAY n_live)', 'n_live =/= n_current',
        pair('S_key', 'n_live', 44), pair('S_key', 'n_current', 11),
        owners('S_key', 'HARRAY n_current', 1), owners('S_key', 'HARRAY n_live', 1),
        'PhpStep: S_key ~> S_insert',
        'S_insert.TODO = (ARRAY_ITERATOR parrayiterator_key[.CURRENT = KNOWN PNULL][.KEY = KNOWN PNULL] "next-start") :: ptask_tail*',
        '$entry_lookup(S_insert.ARRAYS[n_target].ITEMS, KSTRING ($ptascii("slot"))) = (DIRECT (PARRAY n_current))',
        owners('S_insert', 'HARRAY n_current', 1),
    ] + public('S_insert') + seek('S_insert', 108, 'S_read') + [
        'S_read.ITERATORS = eps', '~((HOBJECT n_child) <- S_read.ALLOCATIONS)',
        '$lookup(S_read.ENV, $ptascii("before")) = (n_before)',
        'S_read.STORE[n_before] = DEFINED (PARRAY n_target)',
        '$lookup(S_read.ENV, $ptascii("out")) = (n_out)',
        'S_read.STORE[n_out] = DEFINED (PARRAY n_out_array)', 'n_out_array =/= n_target',
        '$entry_lookup(S_read.ARRAYS[n_out_array].ITEMS, KSTRING ($ptascii("slot"))) = (DIRECT (PARRAY n_changed))',
        'n_changed =/= n_current', pair('S_read', 'n_changed', 55), pair('S_read', 'n_current', 11),
        pair('S_read', 'n_old', 2), pair('S_read', 'n_live', 44),
        owners('S_read', 'HARRAY n_old', 2), owners('S_read', 'HOBJECT n_aggregate', 1),
    ] + public('S_read')
    return checks + finish('S_read', stdout, ['HOBJECT n_aggregate', 'HOBJECT n_child', 'HARRAY n_target',
        'HARRAY n_out_array', 'HARRAY n_old', 'HARRAY n_current', 'HARRAY n_live', 'HARRAY n_changed'])


def generator_checks(program, path, stdout):
    checks = entry(program, path, False) + [
        '$array_aggregate_generator(S_return, parrayaggregate) = (parraygenerator)',
        '$array_aggregate_iterator(S_return, parrayaggregate) = eps',
        'parraygenerator.INPUT = parrayaggregate.INPUT', 'parraygenerator.OBJECT = n_child',
        'S_return.OBJECTS[n_child] = GENERATOR pgenerator_initial',
        'pgenerator_initial.PHASE = GENERATOR_FRESH', 'pgenerator_initial.FRAME = (pframe_generator)',
        'pframe_generator.LOCALS = (psymboltable_generator)',
        '$lookup(psymboltable_generator.ENV, $ptascii("local")) = (n_local)',
        'S_return.STORE[n_local] = DEFINED (PARRAY n_old)',
        owners('S_return', 'HCELL n_local', 1), owners('S_return', 'HARRAY n_old', 3),
        'PhpStep: S_return ~> S_promoted',
        'S_promoted = S_return[.TODO = (ARRAY_GENERATOR parraygenerator "rewind") :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$array_generator_nodes(parraygenerator, "rewind") = [HARRAY n_target,HOBJECT n_child]',
        '$array_generator_valid(S_promoted, parraygenerator, "rewind")',
        owners('S_promoted', 'HOBJECT n_child', 1),
    ] + public('S_promoted') + budget('S_return', 'S_promote_budget') + seek('S_promoted', 115, 'S_retired') + [
        '~((HOBJECT n_aggregate) <- S_retired.ALLOCATIONS)',
        '~((HCELL n_hold) <- S_retired.ALLOCATIONS)', '$lookup(S_retired.ENV, $ptascii("hold")) = eps',
        '$lookup(S_return.ENV, $ptascii("watch")) = (n_watch)',
        'S_retired.STORE[n_watch] = DEFINED (POBJECT n_observer)',
        '$weakref_get(S_retired, n_observer) = PNULL',
        'S_retired.STORE[n_local] = DEFINED (PARRAY n_old)', owners('S_retired', 'HARRAY n_old', 3),
    ] + public('S_retired') + seek('S_retired', 114, 'S_first') + [
        'S_first.TODO = (ARRAY_GENERATOR parraygenerator "ready") :: ptask_tail*',
        'S_first.OBJECTS[n_child] = GENERATOR pgenerator_first',
        'pgenerator_first.VALUE = (PARRAY n_old)', 'pgenerator_first.REFCELL = eps',
        '$string_bytes($generator_cached_value(S_first, n_child, true)) = ($ptascii("first"))',
        '$array_generator_ready(S_first, parraygenerator)', owners('S_first', 'HOBJECT n_child', 1),
        owners('S_first', 'HARRAY n_old', 4),
        'PhpStep: S_first ~> S_insert',
        'S_insert.TODO = (ARRAY_GENERATOR parraygenerator "next") :: ptask_tail*',
        '$entry_lookup(S_insert.ARRAYS[n_target].ITEMS, KSTRING ($ptascii("first"))) = (DIRECT (PARRAY n_old))',
        owners('S_insert', 'HARRAY n_old', 5),
    ] + public('S_insert') + seek('S_insert', 116, 'S_next_body') + [
        'S_next_body.OBJECTS[n_child] = GENERATOR pgenerator_running',
        'pgenerator_running.PHASE = GENERATOR_RUNNING', 'pgenerator_running.VALUE = (PARRAY n_old)',
        'S_next_body.STORE[n_local] = DEFINED (PARRAY n_old)', owners('S_next_body', 'HARRAY n_old', 5),
    ] + public('S_next_body') + seek('S_next_body', 117, 'S_closed') + [
        'S_closed.TODO = (ARRAY_GENERATOR parraygenerator "ready") :: ptask_tail*',
        'S_closed.OBJECTS[n_child] = GENERATOR pgenerator_closed',
        'pgenerator_closed.VALUE = (PARRAY n_last)', 'pgenerator_closed.REFCELL = eps', pair('S_closed', 'n_last', 33),
        '$entry_lookup(S_closed.ARRAYS[n_target].ITEMS, KSTRING ($ptascii("second"))) = (DIRECT (PARRAY n_last))',
        'S_closed.STORE[n_row] = DEFINED (PARRAY n_final)', pair('S_closed', 'n_final', 66),
        'n_final =/= n_old', '~((HCELL n_local) <- S_closed.ALLOCATIONS)',
        owners('S_closed', 'HARRAY n_old', 2), owners('S_closed', 'HARRAY n_last', 2),
        owners('S_closed', 'HOBJECT n_child', 1), '$array_generator_ready(S_closed, parraygenerator)',
    ] + public('S_closed') + seek('S_closed', 118, 'S_data') + [
        '~((HOBJECT n_child) <- S_data.ALLOCATIONS)',
        owners('S_data', 'HARRAY n_last', 1), owners('S_data', 'HARRAY n_old', 2),
        owners('S_data', 'HARRAY n_target', 1), '$array_generator_history(S_data, parraygenerator)',
        '~$array_generator_source(S_data, parraygenerator)',
    ] + public('S_data') + seek('S_data', 119, 'S_input') + [
        '$array_generator_valid(S_input, parraygenerator, "input-released")',
        '$array_generator_nodes(parraygenerator, "input-released") = [HARRAY n_target]',
    ] + public('S_input')
    return checks + finish('S_input', stdout, ['HOBJECT n_aggregate', 'HOBJECT n_child', 'HOBJECT n_observer',
        'HARRAY n_target', 'HARRAY n_old', 'HARRAY n_last', 'HARRAY n_final'])


def conditions(name, program, path, stdout):
    return iterator_checks(program, path, stdout) if name.endswith('fresh-iterator') else generator_checks(program, path, stdout)


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
