#!/usr/bin/env python3
"""Real DATA destruction retains the builder and original spread callsite."""
from pathlib import Path
import array_iterator_data_destructor_cases as cases
import list_missing_warning_protocol as shared
from array_aggregate_unpack_state_review import initial, seek
from array_generator_unpack_state_review import budget, finish, owners, public

CONDITION_INPUTS = tuple(Path(__file__).with_name(name) for name in (
    'array_iterator_data_destructor_state.py',
    'array_iterator_data_destructor_state_review.py',
    'array_aggregate_unpack_state_review.py',
    'array_generator_unpack_state_review.py',
))

HELPERS = shared.HELPERS + r'''
dec $array_data_echo(pstate, ptbytes) : bool
def $array_data_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $array_data_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 170) = ($array_iterator_plan(S) =/= eps)
def $list_warning_frontier(S, 171) = true
  -- if S.TODO = (ARRAY_ITERATOR parrayiterator "finish") :: ptask*
def $list_warning_frontier(S, 172) = $array_data_echo(S, $ptascii("D:"))
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
def $list_warning_frontier(S, 173) = true
  -- if S.TODO = (ARRAY_ITERATOR_RELEASE parrayiterator "normal") :: ptask*
def $list_warning_frontier(S, 174) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ARRAY_ITERATOR_RELEASE parrayiterator "normal") :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 175) = $array_data_echo(S, $ptascii("R:"))
def $list_warning_frontier(S, 176) = $array_data_echo(S, $ptascii("C:"))
'''


def pair(state, array, first, second=7):
    return f'{state}.ARRAYS[{array}].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT {first})),ENTRY (KINT 1) (DIRECT (PINT {second}))]'


def entry(program, path):
    return initial(program, path) + seek('S_initial', 170, 'S_pre') + [
        '$array_iterator_plan(S_pre) = (parrayiterator)',
        'S_pre.TODO = (ARRAY_UNPACK n_target phpType13* z) :: ptask_tail*',
        'parrayiterator.ARRAY = n_target', 'parrayiterator.LINE = z',
        'parrayiterator.INPUT = S_pre.RESULT', 'parrayiterator.TAIL = phpType13*',
        'n_object = parrayiterator.OBJECT',
        '$lookup(S_pre.ENV, $ptascii("it")) = (n_it)',
        'S_pre.STORE[n_it] = DEFINED (POBJECT n_object)',
        '$lookup(S_pre.ENV, $ptascii("row")) = (n_row)',
        'S_pre.STORE[n_row] = DEFINED (PARRAY n_old)', pair('S_pre', 'n_old', 2),
        '$lookup(S_pre.ENV, $ptascii("dest")) = (n_dest)',
        '$lookup(S_pre.ENV, $ptascii("tail")) = (n_tail)',
        '$lookup(S_pre.ENV, $ptascii("watch")) = (n_watch)',
        'S_pre.STORE[n_watch] = DEFINED (POBJECT n_observer)',
        'S_pre.STORE[n_dest] = DEFINED (PINT 99)', 'S_pre.STORE[n_tail] = DEFINED (PINT 7)',
        'S_pre.ARRAYS[n_target].ITEMS = [ENTRY (KINT 4) (DIRECT (PINT 8))]',
        '$array_iterator_destructor(S_pre, n_object)',
        owners('S_pre', 'HARRAY n_old', 1), owners('S_pre', 'HOBJECT n_object', 1),
    ] + public('S_pre') + seek('S_pre', 171, 'S_finish') + [
        'S_finish.TODO = (ARRAY_ITERATOR parrayiterator "finish") :: ptask_tail*',
        '$array_iterator_valid(S_finish, parrayiterator, "finish")',
        '$array_iterator_ready(S_finish, parrayiterator)',
        'parrayiterator.CURRENT = KNOWN PNULL', 'parrayiterator.KEY = KNOWN PNULL',
        '$lookup(S_finish.ENV, $ptascii("it")) = eps', '~((HCELL n_it) <- S_finish.ALLOCATIONS)',
        '$entry_lookup(S_finish.ARRAYS[n_target].ITEMS, KSTRING ($ptascii("row"))) = (DIRECT (PARRAY n_old))',
        owners('S_finish', 'HOBJECT n_object', 1), owners('S_finish', 'HARRAY n_old', 2),
        'PhpStep: S_finish ~> S_raw',
        'S_raw.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (ARRAY_ITERATOR_RELEASE parrayiterator "normal") :: ptask_tail*',
        'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_object)]',
        'pdestructionrelease.CALLER = eps', 'pdestructionrelease.ORIGIN = $origin_child((parrayiterator.SITE), [PCFIELD 1])',
        'pdestructionrelease.USER', 'S_raw.ORIGIN = $origin_child((parrayiterator.SITE), [PCFIELD 1])',
        'S_raw.ITERATORS = eps', '$task_nodes(ARRAY_ITERATOR_RELEASE parrayiterator "normal") = [HARRAY n_target]',
        '$array_iterator_release_valid(S_raw, parrayiterator, "normal")',
        '~$array_iterator_release_valid(S_raw, parrayiterator, "abrupt")',
        '$destructor_source_line(S_raw) = parrayiterator.LINE',
        owners('S_raw', 'HARRAY n_target', 1), owners('S_raw', 'HARRAY n_old', 2),
        owners('S_raw', 'HOBJECT n_object', 1),
    ] + public('S_raw') + budget('S_finish', 'S_finish_budget') + seek('S_finish', 172, 'S_dtor') + [
        'S_dtor.CURRENT = (pcallcontext_d)',
        '$destructor_context_call(pcallcontext_d, S_dtor.CURRENT, S_dtor.FRAMES) = (pdestructorcall)',
        'pdestructorcall.OBJECT = n_object', 'pdestructorcall.SITE = $origin_child((parrayiterator.SITE), [PCFIELD 1])',
        'pdestructorcall.LINE = parrayiterator.LINE', 'pdestructorcall.USER',
        'pdestructorcall.PENDING = eps', 'pdestructorcall.OPERATION = eps',
        '$destructor_call_live(S_dtor, pdestructorcall)',
        '$weakref_get(S_dtor, n_observer) = POBJECT n_object',
        'S_dtor.STORE[n_dest] = DEFINED (PINT 99)', 'S_dtor.STORE[n_tail] = DEFINED (PINT 7)',
        'S_dtor.STORE[n_row] = DEFINED (PARRAY n_old)', pair('S_dtor', 'n_old', 2),
        owners('S_dtor', 'HARRAY n_target', 1), owners('S_dtor', 'HARRAY n_old', 2),
    ] + public('S_dtor')


def retired_receiver(state):
    return [
        f'~((HOBJECT n_object) <- {state}.ALLOCATIONS)', f'$weakref_get({state}, n_observer) = PNULL',
        f'{state}.STORE[n_dest] = DEFINED (PINT 99)', f'{state}.STORE[n_tail] = DEFINED (PINT 20)',
        f'{state}.STORE[n_row] = DEFINED (PARRAY n_live)', 'n_live =/= n_old', pair(state, 'n_live', 44),
        owners(state, 'HARRAY n_old', 1), owners(state, 'HARRAY n_live', 1),
        f'$array_iterator_release_valid({state}, parrayiterator, "normal")',
        f'~$array_iterator_source({state}, parrayiterator)',
    ] + public(state)


def normal(program, path, stdout):
    checks = entry(program, path) + seek('S_dtor', 173, 'S_released') + retired_receiver('S_released') + [
        'S_released.TODO = (ARRAY_ITERATOR_RELEASE parrayiterator "normal") :: ptask_tail*',
        '$array_iterator_release_builder(S_released, parrayiterator)',
        'PhpStep: S_released ~> S_next',
        'S_next.TODO = (ARRAY_NEXT n_target phpType13*) :: ptask_tail*',
        'S_next.ORIGIN = $origin_next_item((parrayiterator.SITE), phpType13*)',
        'S_next.STORE[n_tail] = DEFINED (PINT 20)', 'S_next.STORE[n_dest] = DEFINED (PINT 99)',
    ] + budget('S_released', 'S_continue_budget') + seek('S_released', 175, 'S_read') + [
        'S_read.STORE[n_dest] = DEFINED (PARRAY n_target)', 'S_read.STORE[n_tail] = DEFINED (PINT 21)',
        '$entry_lookup(S_read.ARRAYS[n_target].ITEMS, KINT 5) = (DIRECT (PINT 20))',
        '$entry_lookup(S_read.ARRAYS[n_target].ITEMS, KSTRING ($ptascii("row"))) = (DIRECT (PARRAY n_old))',
        pair('S_read', 'n_old', 2), pair('S_read', 'n_live', 44),
    ] + public('S_read')
    return checks + finish('S_read', stdout, ['HOBJECT n_object', 'HOBJECT n_observer', 'HARRAY n_target', 'HARRAY n_old', 'HARRAY n_live'])


def normal_throw(program, path, stdout):
    checks = entry(program, path) + [
        '$lookup(S_pre.ENV, $ptascii("second")) = (n_second)',
        'S_pre.STORE[n_second] = DEFINED (POBJECT n_exception)',
    ] + seek('S_dtor', 174, 'S_pending') + retired_receiver('S_pending') + [
        'S_pending.TODO = (THROW_SEARCH n_exception) :: (ARRAY_ITERATOR_RELEASE parrayiterator "normal") :: ptask_tail*',
        '$throwable_field(S_pending, n_exception, "previous") = PNULL',
        '$throwable_field(S_pending, n_exception, "trace") = PARRAY n_trace', 'S_pending.ARRAYS[n_trace].ITEMS = eps',
        '$string_bytes($throwable_field(S_pending, n_exception, "message")) = ($ptascii("dtor"))',
        'PhpStep: S_pending ~> S_discard',
        'S_discard.TODO = (THROW_SEARCH n_exception) :: ptask_tail*',
        owners('S_discard', 'HARRAY n_target', 0), owners('S_discard', 'HARRAY n_old', 1),
    ] + budget('S_pending', 'S_discard_budget') + seek('S_pending', 176, 'S_caught') + [
        'S_caught.STORE[n_dest] = DEFINED (PINT 99)', 'S_caught.STORE[n_tail] = DEFINED (PINT 20)',
        '~((HARRAY n_target) <- S_caught.ALLOCATIONS)', '~((HARRAY n_old) <- S_caught.ALLOCATIONS)',
        '~((HOBJECT n_object) <- S_caught.ALLOCATIONS)', '$weakref_get(S_caught, n_observer) = PNULL',
    ] + public('S_caught')
    return checks + finish('S_caught', stdout, ['HOBJECT n_object', 'HOBJECT n_observer', 'HOBJECT n_exception', 'HARRAY n_trace', 'HARRAY n_target', 'HARRAY n_old', 'HARRAY n_live'])


def conditions(name, program, path, stdout):
    return normal_throw(program, path, stdout) if name.endswith('normal-throw') else normal(program, path, stdout)


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS, extra_inputs=CONDITION_INPUTS) else 1)
