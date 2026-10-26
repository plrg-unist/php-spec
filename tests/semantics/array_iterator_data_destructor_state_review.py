#!/usr/bin/env python3
"""Abrupt DATA retirement, protected builder, replacement Throwable and callsite."""
import base64
import json
import array_iterator_data_destructor_review_cases as cases
import list_missing_warning_protocol as shared
from array_aggregate_unpack_state_review import initial, seek
from array_generator_unpack_state_review import budget, finish, owners, public
from array_iterator_data_destructor_state import HELPERS, CONDITION_INPUTS

HELPERS += r'''
def $list_warning_frontier(S, 180) = ($array_iterator_plan(S) =/= eps)
def $list_warning_frontier(S, 181) = true
  -- if S.TODO = (ARRAY_ITERATOR parrayiterator "key-start") :: ptask*
def $list_warning_frontier(S, 182) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ARRAY_ITERATOR parrayiterator text) :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 183) = $array_data_echo(S, $ptascii("D:"))
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
def $list_warning_frontier(S, 184) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ARRAY_ITERATOR_RELEASE parrayiterator text) :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 185) = $array_data_echo(S, $ptascii("E:"))
def $list_warning_frontier(S, 186) = $array_data_echo(S, $ptascii("D;"))
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
def $list_warning_frontier(S, 187) = $array_data_echo(S, $ptascii("T:"))
'''


def pair(state, array, first):
    return f'{state}.ARRAYS[{array}].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT {first})),ENTRY (KINT 1) (DIRECT (PINT 7))]'


def entry(program, path, row=True):
    checks = initial(program, path) + seek('S_initial', 180, 'S_pre') + [
        'S_pre.TODO = (ARRAY_UNPACK n_target phpType13* z) :: ptask_tail*',
        '$array_iterator_plan(S_pre) = (parrayiterator)',
        'parrayiterator.ARRAY = n_target', 'parrayiterator.LINE = z',
        'parrayiterator.INPUT = S_pre.RESULT', 'parrayiterator.TAIL = phpType13*',
        'n_object = parrayiterator.OBJECT',
        '$lookup(S_pre.ENV, $ptascii("it")) = (n_it)',
        'S_pre.STORE[n_it] = DEFINED (POBJECT n_object)',
        '$lookup(S_pre.ENV, $ptascii("dest")) = (n_dest)',
        '$lookup(S_pre.ENV, $ptascii("tail")) = (n_tail)',
        'S_pre.STORE[n_dest] = DEFINED (PINT 99)', 'S_pre.STORE[n_tail] = DEFINED (PINT 7)',
        '$array_iterator_destructor(S_pre, n_object)',
        owners('S_pre', 'HARRAY n_target', 1), owners('S_pre', 'HOBJECT n_object', 1),
    ]
    if row:
        checks += [
            '$lookup(S_pre.ENV, $ptascii("row")) = (n_row)',
            'S_pre.STORE[n_row] = DEFINED (PARRAY n_old)', pair('S_pre', 'n_old', 2),
            'S_pre.ARRAYS[n_target].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_old))]',
            '$lookup(S_pre.ENV, $ptascii("watch")) = (n_watch)',
            'S_pre.STORE[n_watch] = DEFINED (POBJECT n_observer)',
            owners('S_pre', 'HARRAY n_old', 2),
        ]
    else:
        checks += ['S_pre.ARRAYS[n_target].ITEMS = [ENTRY (KINT 4) (DIRECT (PINT 8))]', 'z = 16']
    return checks + public('S_pre')


def blocked_controls():
    return [
        'parrayiterator_bad = parrayiterator_cached[.CURRENT = KNOWN (POBJECT n_object)]',
        'S_bad = S_cache[.TODO = (ARRAY_ITERATOR parrayiterator_bad "key-start") :: ptask_tail*]',
        '$heap_valid($heap_graph(S_bad))', '$array_iterator_valid(S_bad, parrayiterator_bad, "key-start")',
        '~$array_iterator_ready(S_bad, parrayiterator_bad)',
        'PhpStep: S_bad ~> S_refused',
        'S_refused = S_bad[.COMPLETION = UNSUPPORTED "array Iterator unpack state outside quiet payload domain"]',
        '$array_iterator_blocked(S_refused)', '$drive_steps(S_refused, 2) = S_refused',
        '~$array_iterator_blocked(S_refused[.COMPILESTOP = true])',
        '~$array_iterator_blocked(S_refused[.ORIGIN = eps])',
        '~$array_iterator_blocked(S_cache[.COMPLETION = UNSUPPORTED "array Iterator unpack state outside quiet payload domain"])',
        'S_bad_result = S_cache[.TODO = (ARRAY_ITERATOR parrayiterator "current") :: ptask_tail*][.RESULT = KNOWN (POBJECT n_object)]',
        '$heap_valid($heap_graph(S_bad_result))', '$array_iterator_valid(S_bad_result, parrayiterator, "current")',
        '$array_iterator_ready(S_bad_result, parrayiterator)', '$array_iterator_value(S_bad_result, S_bad_result.RESULT) = eps',
        'PhpStep: S_bad_result ~> S_refused_result',
        'S_refused_result = S_bad_result[.COMPLETION = UNSUPPORTED "array Iterator unpack callback result outside quiet payload domain"]',
        '$array_iterator_blocked(S_refused_result)', '$drive_steps(S_refused_result, 2) = S_refused_result',
    ]


def pending_builder_control():
    return [
        'S_bad_builder = S_pending[.ARRAYS[n_target].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_object))]]',
        '$heap_valid($heap_graph(S_bad_builder))',
        '$array_iterator_valid(S_bad_builder, parrayiterator_pending, text_pending)',
        '~$array_iterator_ready(S_bad_builder, parrayiterator_pending)',
        'PhpStep: S_bad_builder ~> S_bad_builder_refused',
        'S_bad_builder_refused = S_bad_builder[.COMPLETION = UNSUPPORTED "array Iterator unpack abrupt payload outside quiet domain"]',
        '$array_iterator_blocked(S_bad_builder_refused)', '$drive_steps(S_bad_builder_refused, 2) = S_bad_builder_refused',
    ]


def release_controls(mode):
    return [
        'S_bad_release = S_released[.ARRAYS[n_target].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_exception))]]',
        '$heap_valid($heap_graph(S_bad_release))',
        f'$array_iterator_release_valid(S_bad_release, parrayiterator_release, "{mode}")',
        '~$array_iterator_release_builder(S_bad_release, parrayiterator_release)',
        'PhpStep: S_bad_release ~> S_release_refused',
        'S_release_refused = S_bad_release[.COMPLETION = UNSUPPORTED "array Iterator release builder outside quiet domain"]',
        '$array_iterator_blocked(S_release_refused)', '$drive_steps(S_release_refused, 2) = S_release_refused',
        f'~$array_iterator_release_valid(S_released[.ORIGIN = (parrayiterator.SITE)], parrayiterator_release, "{mode}")',
        f'~$array_iterator_release_valid(S_released, parrayiterator_release[.LINE = $(parrayiterator.LINE + 1)], "{mode}")',
        f'~$array_iterator_release_valid(S_released, parrayiterator_release[.CURRENT = KNOWN (PINT 1)], "{mode}")',
        f'~$array_iterator_release_valid(S_released, parrayiterator_release, "invalid")',
    ]


def abrupt(program, path, stdout, replacement):
    checks = entry(program, path)
    if replacement:
        checks += [
            '$lookup(S_pre.ENV, $ptascii("first")) = (n_first)',
            '$lookup(S_pre.ENV, $ptascii("second")) = (n_second)',
            'S_pre.STORE[n_first] = DEFINED (POBJECT n_original)',
            'S_pre.STORE[n_second] = DEFINED (POBJECT n_replacement)',
        ]
    checks += seek('S_pre', 181, 'S_cache') + [
        'S_cache.TODO = (ARRAY_ITERATOR parrayiterator_cached "key-start") :: ptask_tail*',
        'parrayiterator_cached = parrayiterator[.CURRENT = KNOWN (PARRAY n_old)]',
        '$array_iterator_ready(S_cache, parrayiterator_cached)',
        '~((HCELL n_it) <- S_cache.ALLOCATIONS)', '$lookup(S_cache.ENV, $ptascii("it")) = eps',
        '$weakref_get(S_cache, n_observer) = POBJECT n_object',
        owners('S_cache', 'HOBJECT n_object', 1), owners('S_cache', 'HARRAY n_old', 3),
    ] + public('S_cache')
    if not replacement:
        checks += blocked_controls()
    checks += seek('S_cache', 182, 'S_pending') + [
        'S_pending.TODO = (THROW_SEARCH n_original) :: (ARRAY_ITERATOR parrayiterator_pending text_pending) :: ptask_tail*',
        'parrayiterator_pending.CURRENT = KNOWN (PARRAY n_old)',
        '$array_iterator_ready(S_pending, parrayiterator_pending)',
        '$throwable_field(S_pending, n_original, "previous") = PNULL',
        '$throwable_field(S_pending, n_original, "trace") = PARRAY n_original_trace',
        'S_pending.ARRAYS[n_original_trace].ITEMS = eps',
        owners('S_pending', 'HARRAY n_target', 1), owners('S_pending', 'HARRAY n_old', 3),
        owners('S_pending', 'HOBJECT n_object', 1),
    ] + public('S_pending')
    if replacement:
        checks += ['text_pending = "key"', 'n_exception = n_replacement']
    else:
        checks += ['z = 18', 'text_pending = "insert"', 'n_exception = n_original',
            '$string_bytes($throwable_field(S_pending, n_original, "message")) = ($ptascii("Keys must be of type int|string during array unpacking"))']
        checks += pending_builder_control()
    checks += [
        'S_popped = S_pending[.TODO = (THROW_SEARCH n_original) :: ptask_tail*]',
        'PhpStep: S_pending ~> S_raw',
        'S_raw = $array_iterator_discard(S_popped, parrayiterator_pending, text_pending)',
        'parrayiterator_release = parrayiterator_pending[.CURRENT = KNOWN PNULL][.KEY = KNOWN PNULL]',
        'S_raw.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (THROW_SEARCH n_original) :: (ARRAY_ITERATOR_RELEASE parrayiterator_release "abrupt") :: ptask_tail*',
        'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HARRAY n_old),DESTRUCTION_VALUE (HOBJECT n_object)]',
        'pdestructionrelease.USER',
        'pdestructionrelease.ORIGIN = $origin_child((parrayiterator.SITE), [PCFIELD 1])',
        'S_raw.ITERATORS = eps',
        '$task_nodes(ARRAY_ITERATOR_RELEASE parrayiterator_release "abrupt") = [HARRAY n_target]',
        '$array_iterator_release_valid(S_raw, parrayiterator_release, "abrupt")',
        owners('S_raw', 'HARRAY n_target', 1), owners('S_raw', 'HARRAY n_old', 3),
    ] + public('S_raw') + budget('S_pending', 'S_release_budget') + seek('S_pending', 183, 'S_dtor') + [
        'S_dtor.CURRENT = (pcallcontext_d)',
        '$destructor_context_call(pcallcontext_d, S_dtor.CURRENT, S_dtor.FRAMES) = (pdestructorcall)',
        'pdestructorcall.OBJECT = n_object', 'pdestructorcall.USER',
        'pdestructorcall.SITE = $origin_child((parrayiterator.SITE), [PCFIELD 1])',
        'pdestructorcall.LINE = parrayiterator.LINE', 'pdestructorcall.PENDING = (n_original)',
        '$destructor_call_live(S_dtor, pdestructorcall)', 'n_object <- S_dtor.DESTRUCTION.CALLED',
        '$weakref_get(S_dtor, n_observer) = POBJECT n_object', 'S_dtor.ITERATORS = eps',
        'S_dtor.STORE[n_dest] = DEFINED (PINT 99)', 'S_dtor.STORE[n_tail] = DEFINED (PINT 7)',
        'S_dtor.STORE[n_row] = DEFINED (PARRAY n_old)', pair('S_dtor', 'n_old', 2),
        owners('S_dtor', 'HARRAY n_target', 1), owners('S_dtor', 'HARRAY n_old', 2),
    ] + public('S_dtor') + seek('S_dtor', 184, 'S_released') + [
        'S_released.TODO = (THROW_SEARCH n_exception) :: (ARRAY_ITERATOR_RELEASE parrayiterator_release "abrupt") :: ptask_tail*',
        '~((HOBJECT n_object) <- S_released.ALLOCATIONS)', '$weakref_get(S_released, n_observer) = PNULL',
        '$array_iterator_release_valid(S_released, parrayiterator_release, "abrupt")',
        '~$array_iterator_source(S_released, parrayiterator_release)',
        'S_released.STORE[n_dest] = DEFINED (PINT 99)', 'S_released.STORE[n_tail] = DEFINED (PINT 20)',
        'S_released.STORE[n_row] = DEFINED (PARRAY n_live)', 'n_live =/= n_old', pair('S_released', 'n_live', 44),
        owners('S_released', 'HARRAY n_target', 1), owners('S_released', 'HARRAY n_old', 1),
        '$throwable_field(S_released, n_original, "previous") = PNULL',
    ] + public('S_released')
    if replacement:
        checks += ['$throwable_field(S_released, n_exception, "previous") = POBJECT n_original',
            '$throwable_field(S_released, n_exception, "trace") = PARRAY n_trace', 'S_released.ARRAYS[n_trace].ITEMS = eps']
    else:
        checks += release_controls('abrupt')
    checks += [
        'PhpStep: S_released ~> S_discard',
        'S_discard.TODO = (THROW_SEARCH n_exception) :: ptask_tail*',
        owners('S_discard', 'HARRAY n_target', 0), owners('S_discard', 'HARRAY n_old', 1),
    ] + budget('S_released', 'S_cancel_budget') + seek('S_released', 185, 'S_caught') + [
        '~((HARRAY n_target) <- S_caught.ALLOCATIONS)', '~((HARRAY n_old) <- S_caught.ALLOCATIONS)',
        '~((HOBJECT n_object) <- S_caught.ALLOCATIONS)', '$weakref_get(S_caught, n_observer) = PNULL',
        'S_caught.STORE[n_dest] = DEFINED (PINT 99)', 'S_caught.STORE[n_tail] = DEFINED (PINT 20)',
    ] + public('S_caught')
    retired = ['HOBJECT n_object', 'HOBJECT n_observer', 'HOBJECT n_original', 'HARRAY n_original_trace',
        'HARRAY n_target', 'HARRAY n_old', 'HARRAY n_live']
    if replacement:
        retired += ['HOBJECT n_replacement', 'HARRAY n_trace']
    return checks + finish('S_caught', stdout, retired)


def split_trace(program, path, stdout):
    checks = entry(program, path, False) + seek('S_pre', 171, 'S_finish') + [
        'S_finish.TODO = (ARRAY_ITERATOR parrayiterator "finish") :: ptask_tail*',
        '$array_iterator_ready(S_finish, parrayiterator)',
        '~((HCELL n_it) <- S_finish.ALLOCATIONS)',
        '$entry_lookup(S_finish.ARRAYS[n_target].ITEMS, KSTRING ($ptascii("row"))) = (DIRECT (PINT 5))',
    ] + public('S_finish') + seek('S_finish', 186, 'S_dtor') + [
        'S_dtor.CURRENT = (pcallcontext_d)',
        '$destructor_context_call(pcallcontext_d, S_dtor.CURRENT, S_dtor.FRAMES) = (pdestructorcall)',
        'pdestructorcall.OBJECT = n_object', 'pdestructorcall.USER', 'pdestructorcall.PENDING = eps',
        'pdestructorcall.SITE = $origin_child((parrayiterator.SITE), [PCFIELD 1])', 'pdestructorcall.LINE = 16',
        'S_dtor.STORE[n_dest] = DEFINED (PINT 99)', 'S_dtor.STORE[n_tail] = DEFINED (PINT 7)',
        owners('S_dtor', 'HARRAY n_target', 1),
    ] + public('S_dtor') + seek('S_dtor', 184, 'S_released') + [
        'S_released.TODO = (THROW_SEARCH n_exception) :: (ARRAY_ITERATOR_RELEASE parrayiterator "normal") :: ptask_tail*',
        '$array_iterator_release_valid(S_released, parrayiterator, "normal")',
        '~((HOBJECT n_object) <- S_released.ALLOCATIONS)',
        'S_released.STORE[n_dest] = DEFINED (PINT 99)', 'S_released.STORE[n_tail] = DEFINED (PINT 7)',
        '$throwable_field(S_released, n_exception, "previous") = PNULL',
        '$throwable_field(S_released, n_exception, "line") = PINT 9',
        '$string_bytes($throwable_field(S_released, n_exception, "message")) = ($ptascii("fresh"))',
        '$throwable_field(S_released, n_exception, "trace") = PARRAY n_trace',
        'S_released.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_frame))]',
        '$entry_lookup(S_released.ARRAYS[n_frame].ITEMS, KSTRING ($ptascii("function"))) = (DIRECT pvalue_function)',
        '$string_bytes(pvalue_function) = ($ptascii("__destruct"))',
        '$entry_lookup(S_released.ARRAYS[n_frame].ITEMS, KSTRING ($ptascii("class"))) = (DIRECT pvalue_class)',
        '$string_bytes(pvalue_class) = ($ptascii("ArrayDataSplitTrace"))',
        '$entry_lookup(S_released.ARRAYS[n_frame].ITEMS, KSTRING ($ptascii("type"))) = (DIRECT pvalue_type)',
        '$string_bytes(pvalue_type) = ($ptascii("->"))',
        '$entry_lookup(S_released.ARRAYS[n_frame].ITEMS, KSTRING ($ptascii("line"))) = (DIRECT (PINT 16))',
        '$entry_lookup(S_released.ARRAYS[n_frame].ITEMS, KSTRING ($ptascii("file"))) = (DIRECT pvalue_file)',
        '$string_bytes(pvalue_file) = ($base64(' + json.dumps(base64.b64encode(bytes(path)).decode()) + '))',
        '$entry_lookup(S_released.ARRAYS[n_frame].ITEMS, KSTRING ($ptascii("args"))) = (DIRECT (PARRAY n_args))',
        'S_released.ARRAYS[n_args].ITEMS = eps',
        owners('S_released', 'HARRAY n_target', 1),
        'PhpStep: S_released ~> S_discard',
        'S_discard.TODO = (THROW_SEARCH n_exception) :: ptask_tail*', owners('S_discard', 'HARRAY n_target', 0),
    ] + public('S_released') + budget('S_released', 'S_cancel_budget') + seek('S_released', 187, 'S_caught') + [
        '~((HARRAY n_target) <- S_caught.ALLOCATIONS)', 'S_caught.STORE[n_dest] = DEFINED (PINT 99)',
        'S_caught.STORE[n_tail] = DEFINED (PINT 7)',
    ] + public('S_caught')
    return checks + finish('S_caught', stdout, ['HOBJECT n_object', 'HOBJECT n_exception', 'HARRAY n_target',
        'HARRAY n_trace', 'HARRAY n_frame', 'HARRAY n_args'])


def conditions(name, program, path, stdout):
    if name.endswith('split-trace'):
        return split_trace(program, path, stdout)
    return abrupt(program, path, stdout, name.endswith('replacement-throw'))


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS, extra_inputs=CONDITION_INPUTS) else 1)
