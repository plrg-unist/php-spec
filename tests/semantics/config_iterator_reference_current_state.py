#!/usr/bin/env python3
"""Selected CONFIG cells, post-key sends, and temporary cache ownership."""
from pathlib import Path
from types import SimpleNamespace

import config_iterator_reference_current_cases as cases
import list_missing_warning_protocol as shared
from array_generator_unpack_state_review import budget, finish, initial, owners, public, seek

SELECTED = ('config-reference-current-selected-global-cells',
            'config-reference-current-owning-value-repair')
SOURCES = SimpleNamespace(CASES={name: cases.CASES[name] for name in SELECTED},
                          __file__=cases.__file__)
HELPERS = shared.HELPERS + r'''
def $list_warning_frontier(S, 960) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "current") :: ptask_tail*
  -- if pconfigiterator.ITEMS = eps
def $list_warning_frontier(S, 961) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "send") :: ptask_tail*
  -- if pconfigiterator.ITEMS = eps
def $list_warning_frontier(S, 962) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "send") :: ptask_tail*
  -- if |pconfigiterator.ITEMS| = 1
def $list_warning_frontier(S, 963) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "finish") :: ptask_tail*
def $list_warning_frontier(S, 964) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "input-release") :: ptask_tail*
def $list_warning_frontier(S, 965) = true
  -- if S.TODO = (CONFIG_ITERATOR pconfigiterator "ready") :: ptask_tail*
def $list_warning_frontier(S, 966) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask_tail*
  -- if $base64(text) = $ptascii("Q")
'''


def bound(state, names):
    return [f'$lookup({state}.ENV, $ptascii("{name}")) = (n_{name})' for name in names]


def string(state, cell, value):
    return [f'{state}.STORE[{cell}] = DEFINED pvalue_{cell}_{state}',
            f'$string_bytes(pvalue_{cell}_{state}) = ($ptascii("{value}"))']


def selected(program, path, stdout):
    checks = initial(program, path) + seek('S_initial', 960, 'S_return') + [
        'S_return.TODO = (CONFIG_ITERATOR pconfigiterator "current") :: ptask_tail*',
        'pconfigiterator.OBJECT = n_object', 'pconfigiterator.CALL = pconfigcall',
        'pconfigcall.SELECTION = (n_selection)', 'pconfigcall.OWNER = (n_callee)',
        'pconfigiterator.ITEMS = eps', 'pconfigiterator.CURRENT = KNOWN PNULL',
        'S_return.RESULT = REFERENCE n_name',
        '$config_iterator_current_value(S_return, pconfigiterator, S_return.RESULT) = (PINT 0)',
        '$config_iterator_byref_current(S_return, pconfigiterator)',
        '$config_iterator_valid(S_return, pconfigiterator, "current")',
    ] + bound('S_return', ['name', 'held', 'fresh', 'it', 'keep', 'call', 'keepCall', 'result']) + [
        'S_return.STORE[n_name] = DEFINED (PINT 0)',
        'S_return.STORE[n_it] = DEFINED (POBJECT n_object)',
        'S_return.STORE[n_keep] = DEFINED (POBJECT n_object)',
        'S_return.STORE[n_call] = DEFINED (POBJECT n_callee)',
        'S_return.STORE[n_keepCall] = DEFINED (POBJECT n_callee)',
        'S_return.SELECTEDCALLS[n_selection] = pselectedcall',
        '$selected_entry_valid(S_return, pselectedcall)',
        owners('S_return', 'HCELL n_name', 2),
        *public('S_return'),
        'PhpStep: S_return ~> S_cache',
        'S_cache.TODO = (CONFIG_ITERATOR pconfigiterator_cache "key-start") :: ptask_tail*',
        'pconfigiterator_cache = pconfigiterator[.CURRENT = REFERENCE n_name]',
        'S_cache.RESULT = KNOWN PNULL', 'S_cache.BASE = BASE_VALUE (KNOWN PNULL)',
        '$config_iterator_valid(S_cache, pconfigiterator_cache, "key-start")',
        '$config_iterator_current_receipt(S_cache, pconfigiterator_cache, REFERENCE n_name)',
        '~$config_iterator_current_string(S_cache, pconfigiterator_cache)',
        '$config_iterator_current_value(S_cache, pconfigiterator_cache, KNOWN (PINT 0)) = eps',
        '$config_iterator_current_value(S_cache, pconfigiterator_cache[.OBJECT = |S_cache.OBJECTS|], REFERENCE n_name) = eps',
        '~$config_iterator_current_receipt(S_cache, pconfigiterator_cache[.OBJECT = |S_cache.OBJECTS|], REFERENCE n_name)',
        '$config_iterator_current_value(S_cache[.REFCELLS = eps], pconfigiterator_cache, REFERENCE n_name) = eps',
        owners('S_cache', 'HCELL n_name', 2),
        '$task_nodes(CONFIG_ITERATOR pconfigiterator_cache "key-start") = [HCELL n_name, HOBJECT n_object] ++ $config_nodes(pconfigcall)',
    ] + public('S_cache') + seek('S_cache', 961, 'S_send0') + [
        'S_send0.TODO = (CONFIG_ITERATOR pconfigiterator_send0 "send") :: ptask_tail*',
        'pconfigiterator_send0.CURRENT = REFERENCE n_name',
        'pconfigiterator_send0.KEY = KNOWN (PINT 0)',
        'pconfigiterator_send0.ITEMS = eps',
        'S_send0.STORE[n_it] = DEFINED (PINT 99)',
        'S_send0.STORE[n_keep] = DEFINED (POBJECT n_object)',
        'S_send0.STORE[n_call] = DEFINED (POBJECT n_new_callee)',
        'n_new_callee =/= n_callee',
        'S_send0.SELECTEDCALLS[n_selection] = pselectedcall',
        '$selected_entry_valid(S_send0, pselectedcall)',
    ] + string('S_send0', 'n_name', 'precision') + [
        '$config_iterator_current_value(S_send0, pconfigiterator_send0, REFERENCE n_name) = (pvalue_option)',
        '$string_bytes(pvalue_option) = ($ptascii("precision"))',
        '$config_iterator_current_string(S_send0, pconfigiterator_send0)',
        'PhpStep: S_send0 ~> S_sent0',
        'S_sent0.TODO = (CONFIG_ITERATOR pconfigiterator_sent0 "next-start") :: ptask_tail*',
        'pconfigiterator_sent0 = pconfigiterator_send0[.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_option)]][.CURRENT = KNOWN PNULL][.KEY = KNOWN PNULL]',
        owners('S_sent0', 'HCELL n_name', 1),
        '$config_iterator_valid(S_sent0, pconfigiterator_sent0, "next-start")',
    ] + public('S_sent0') + seek('S_sent0', 962, 'S_send1') + [
        'S_send1.TODO = (CONFIG_ITERATOR pconfigiterator_send1 "send") :: ptask_tail*',
        'pconfigiterator_send1.CURRENT = REFERENCE n_held',
        'pconfigiterator_send1.KEY = KNOWN (PINT 1)',
        'pconfigiterator_send1.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_option)]',
        '$lookup(S_send1.ENV, $ptascii("value")) = (n_fresh)',
        '$lookup(S_send1.ENV, $ptascii("held")) = (n_held)',
        'n_fresh =/= n_held',
    ] + string('S_send1', 'n_name', 'serialize_precision') + string('S_send1', 'n_held', '17') + string('S_send1', 'n_fresh', '23') + [
        '$config_iterator_current_value(S_send1, pconfigiterator_send1, REFERENCE n_held) = (pvalue_value)',
        '$string_bytes(pvalue_value) = ($ptascii("17"))',
        owners('S_send1', 'HCELL n_held', 2),
        owners('S_send1', 'HCELL n_fresh', 2),
        'S_int = S_send1[.STORE[n_held] = DEFINED (PINT 17)]',
        '$config_iterator_valid(S_int, pconfigiterator_send1, "send")',
        '~$config_iterator_current_string(S_int, pconfigiterator_send1)',
        'PhpStep: S_int ~> S_refused',
        'S_refused.COMPLETION = UNSUPPORTED "CONFIG Iterator unpack current outside string domain"',
        'pconfigiterator_unknown = pconfigiterator_send1[.KEY = KNOWN (PSTRING ($ptascii("unknown66")))]',
        'S_unknown = S_int[.TODO = (CONFIG_ITERATOR pconfigiterator_unknown "send") :: ptask_tail*]',
        '$config_iterator_valid(S_unknown, pconfigiterator_unknown, "send")',
        '$intrinsic_argument(S_unknown, pconfigcall.SITE, 0) = ((expression, true, eps, porigin_argument, z_argument))',
        'PhpStep: S_unknown ~> S_error',
        'S_error.COMPLETION = THROWN "Error" ($ptascii("Unknown named parameter $unknown66")) z_argument',
        'S_last = S_send1[.ENV = $unbind(S_send1.ENV, $ptascii("held"))]',
        owners('S_last', 'HCELL n_held', 1),
        '$config_iterator_valid(S_last, pconfigiterator_send1, "send")',
        'S_pruned_pause = $drive_steps(S_last, 1)',
        'S_pruned_pause.COMPLETION = BUDGET',
        'S_pruned = S_pruned_pause[.COMPLETION = NORMAL]',
        '~((HCELL n_held) <- S_pruned.ALLOCATIONS)',
        '~(n_held <- S_pruned.REFCELLS)',
        '$config_iterator_current_receipt(S_pruned, pconfigiterator_send1, REFERENCE n_held)',
        '$config_iterator_current_value(S_pruned, pconfigiterator_send1, REFERENCE n_held) = eps',
    ] + public('S_last') + public('S_pruned') + budget('S_send1', 'S_send_budget') + seek('S_send1', 965, 'S_ready') + [
        'S_ready.TODO = (CONFIG_ITERATOR pconfigiterator_ready "ready") :: ptask_ready*',
        'pconfigiterator_ready.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_option), ENTRY (KINT 1) (DIRECT pvalue_value)]',
        'pconfigiterator_ready.CURRENT = KNOWN PNULL',
        '$config_iterator_valid(S_ready, pconfigiterator_ready, "ready")',
        '$useriter_cursor_count(S_ready.ITERATORS, pconfigiterator_ready.ITERATOR) = 0',
        'S_ready.PRECISIONINI = $ptascii("14")',
    ] + string('S_ready', 'n_held', '19') + string('S_ready', 'n_fresh', '29') + [
        owners('S_ready', 'HOBJECT n_object', 1),
        'S_ready.STORE[n_result] = DEFINED (PINT 99)',
        'PhpStep: S_ready ~> S_api',
        'S_api.PRECISIONINI = $ptascii("17")',
        'S_api.RESULT = KNOWN pvalue_old', '$string_bytes(pvalue_old) = ($ptascii("14"))',
    ] + public('S_ready') + public('S_api') + finish('S_api', stdout, [
        'HOBJECT n_object', 'HCELL n_name', 'HCELL n_held', 'HCELL n_fresh'])
    return checks


def temporary(program, path, stdout):
    checks = initial(program, path) + seek('S_initial', 960, 'S_return') + [
        'S_return.TODO = (CONFIG_ITERATOR pconfigiterator "current") :: ptask_tail*',
        'pconfigiterator.OBJECT = n_object', 'S_return.RESULT = REFERENCE n_slot',
        '$lookup(S_return.ENV, $ptascii("slot")) = (n_slot)',
        '$lookup(S_return.ENV, $ptascii("watch")) = (n_watch_cell)',
        'S_return.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
        'S_return.STORE[n_slot] = DEFINED (POBJECT n_payload)',
        '$config_iterator_current_value(S_return, pconfigiterator, S_return.RESULT) = (POBJECT n_payload)',
        '$config_iterator_owning_input(pconfigiterator)',
        owners('S_return', 'HCELL n_slot', 2), owners('S_return', 'HOBJECT n_payload', 1),
        owners('S_return', 'HOBJECT n_object', 2),
        'PhpStep: S_return ~> S_cache',
        'S_cache.TODO = (CONFIG_ITERATOR pconfigiterator_cache "key-start") :: ptask_tail*',
        'pconfigiterator_cache = pconfigiterator[.CURRENT = REFERENCE n_slot]',
        '$config_iterator_valid(S_cache, pconfigiterator_cache, "key-start")',
        '~$config_iterator_current_string(S_cache, pconfigiterator_cache)',
        '$task_nodes(CONFIG_ITERATOR pconfigiterator_cache "key-start") = [HCELL n_slot, HOBJECT n_object, HOBJECT n_object]',
    ] + public('S_cache') + seek('S_cache', 966, 'S_key') + [
        'S_key.CURRENT = (pcallcontext_key)', 'S_key.FRAMES = pframe_key :: pframe_tail*',
        'pframe_key.TODO = (CONFIG_ITERATOR pconfigiterator_cache "key") :: ptask_tail*',
        '$config_iterator_frame(S_key, pcallcontext_key, pframe_key)',
        '$config_iterator_current_receipt(S_key, pconfigiterator_cache, REFERENCE n_slot)',
        '~((HOBJECT n_payload) <- S_key.ALLOCATIONS)', 'n_payload <- S_key.DESTRUCTION.CALLED',
        '$config_iterator_current_value(S_key, pconfigiterator_cache, REFERENCE n_slot) = (pvalue_option)',
        '$string_bytes(pvalue_option) = ($ptascii("precision"))',
        'S_key.PRECISIONINI = $ptascii("14")',
    ] + seek('S_key', 963, 'S_finish') + [
        'S_finish.TODO = (CONFIG_ITERATOR pconfigiterator_finish "finish") :: ptask_finish*',
        'pconfigiterator_finish.ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_option), ENTRY (KINT 1) (DIRECT pvalue_value)]',
        '$string_bytes(pvalue_value) = ($ptascii("21"))',
        owners('S_finish', 'HOBJECT n_object', 2), owners('S_finish', 'HCELL n_slot', 1),
    ] + string('S_finish', 'n_slot', '23') + public('S_finish') + seek('S_finish', 964, 'S_input') + [
        'S_input.TODO = (CONFIG_ITERATOR pconfigiterator_finish "input-release") :: ptask_finish*',
        owners('S_input', 'HOBJECT n_object', 1),
        '$config_iterator_valid(S_input, pconfigiterator_finish, "input-release")',
        '$weakref_get(S_input, n_watch) = POBJECT n_object',
    ] + seek('S_input', 965, 'S_ready') + [
        'S_ready.TODO = (CONFIG_ITERATOR pconfigiterator_finish "ready") :: ptask_finish*',
        '$config_iterator_valid(S_ready, pconfigiterator_finish, "ready")',
        '$config_iterator_retired_scope(S_ready, pconfigiterator_finish)',
        '~$config_iterator_scope(S_ready, pconfigiterator_finish)',
        '$config_iterator_byref_current(S_ready, pconfigiterator_finish)',
        '~((HOBJECT n_object) <- S_ready.ALLOCATIONS)',
        '$weakref_get(S_ready, n_watch) = PNULL',
        'S_ready.PRECISIONINI = $ptascii("14")',
        'PhpStep: S_ready ~> S_api',
        'S_api.PRECISIONINI = $ptascii("21")',
    ] + public('S_ready') + budget('S_input', 'S_input_budget') + finish('S_api', stdout, [
        'HOBJECT n_object', 'HOBJECT n_payload', 'HOBJECT n_watch', 'HCELL n_slot'])
    return checks


def conditions(name, program, path, stdout):
    return (selected if name == SELECTED[0] else temporary)(program, path, stdout)


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(SOURCES, conditions, HELPERS, model_timeout=300,
        extra_inputs=(Path(__file__), Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
