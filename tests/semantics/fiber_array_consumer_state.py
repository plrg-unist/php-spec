#!/usr/bin/env python3
"""Real nested array transfers and constructor warning continuations."""
import argparse
import json
from pathlib import Path
import fiber_state_review as review

ROOT = Path(__file__).resolve().parents[2]
CATALOG = Path(__file__).with_name('fiber_array_consumer_cases.json')
SOURCE_BYTES = CATALOG.read_bytes()
SOURCES = {row['id']: row['source'] for row in json.loads(SOURCE_BYTES)}
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
FINISH = ['S_done = $drive(S, 4000)', *review.DONE]

CASES = {
    'array-nested-wait-authenticates-real-receiver-and-parent': {
        'source': SOURCES['author-fiber-array-nested-wait-and-class-static-selection'],
        'stage': ('S.TODO = (FIBER_CONTINUE pfiberapi_continue) :: ptask_child* '
                  '-- if S.FIBERCALLERS = [pfibercaller, pfibercaller_outer] '
                  '-- if pfibercaller.API.KIND = (INTRINSIC_FIBER_RESUME) '
                  '-- if pfibercaller.VM.TODO = (FIBER_WAIT pfibercaller.API) :: '
                  '(FIBER_ARRAY_RESULT pfiberarray pconfigcall) :: ptask_saved*'),
        'checks': [
            'S.ACTIVEFIBER = (n_receiver)', 'pfibercaller.OBJECT = n_receiver',
            'pfibercaller.PREVIOUS = (n_parent)', '~pfibercaller.VM.GLOBAL',
            'pfibercaller_outer.OBJECT = n_parent', 'pfibercaller_outer.PREVIOUS = eps',
            'pfibercaller_outer.VM.GLOBAL',
            'pfibercaller_outer.API.KIND = eps',
            'pconfigcall.KIND = INTRINSIC_FIBER_RESUME',
            'pconfigcall.OWNER = (n_receiver)', 'pconfigcall.SELECTION = eps',
            'pconfigcall.INDEX = 1', 'pconfigcall.NAMED', 'pconfigcall.PACKS = eps',
            'pconfigcall.SENT = [NAMED_SENT (KNOWN (PSTRING ($ptascii("R"))))]',
            'pfiberarray.KIND = pconfigcall.KIND', 'pfiberarray.NAME = $ptascii("resume")',
            'pfiberarray.INPUT = (n_receiver)', 'pfiberarray.SITE = pconfigcall.SITE',
            'pfiberarray.LINE = pconfigcall.LINE', 'n_array = pfiberarray.ARRAY',
            'pfiberarray.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_receiver)), ENTRY (KINT 1) (DIRECT (PSTRING ($ptascii("resume"))))]',
            '~((HARRAY n_array) <- S.ALLOCATIONS)',
            'pfibercaller.API.OBJECT = n_receiver', 'pfibercaller.API.START = eps',
            'pfibercaller.API.SENT = (PSTRING ($ptascii("R")))',
            'pfiberapi_continue.KIND = (INTRINSIC_FIBER_SUSPEND)',
            'pfiberapi_continue.OBJECT = n_receiver',
            'ptask_child* = (FIBER_ARRAY_RESULT pfiberarray_suspend pconfigcall_suspend) :: ptask_child_tail*',
            'pfiberarray_suspend.INPUT = eps', 'pconfigcall_suspend.OWNER = eps',
            '$fiber_array_source_valid(S, pfiberarray_suspend)',
            '$fiber_array_result_valid(S, pfiberarray_suspend, pconfigcall_suspend)',
            '$fiber_continue_valid(S, pfiberapi_continue)',
            'S_wait = $fiber_vm_restore(S, pfibercaller.VM)[.ACTIVEFIBER = (n_parent)][.FIBERCALLERS = [pfibercaller_outer]]',
            '$fiber_array_source_valid(S_wait, pfiberarray)',
            '$fiber_array_config_matches(pfiberarray, pconfigcall)',
            '$fiber_array_result_valid(S_wait, pfiberarray, pconfigcall)',
            '$fiber_api_valid(S_wait, pfibercaller.API)',
            '$fiber_wait_valid(S_wait, pfibercaller.API)',
            '$fiber_vm_valid(S, pfibercaller.VM, (n_parent), [pfibercaller_outer])',
            '$fiber_callers_valid(S, (n_receiver), S.FIBERCALLERS, eps)',
            '$task_nodes(FIBER_ARRAY_RESULT pfiberarray pconfigcall) = eps',
            '$fiber_api_nodes(pfibercaller.API) = [HOBJECT n_receiver]',
            '$fiber_caller_api_nodes(pfibercaller) = [HOBJECT n_receiver]',
            'H = $heap_graph(S)', '$heap_owners(H, HOBJECT n_receiver) = 1',
            '$heap_owners(H, HOBJECT n_parent) = 2', '$heap_owners(H, HARRAY n_array) = 0',
            *review.VALID,
            'pfiberarray_receiver = pfiberarray[.INPUT = (n_parent)]',
            'pfibercaller_receiver = pfibercaller[.VM.TODO = (FIBER_WAIT pfibercaller.API) :: (FIBER_ARRAY_RESULT pfiberarray_receiver pconfigcall) :: ptask_saved*]',
            'S_receiver = S[.FIBERCALLERS = [pfibercaller_receiver, pfibercaller_outer]]',
            '$heap_graph(S_receiver) = H',
            '~$fiber_array_source_valid(S_receiver, pfiberarray_receiver)',
            '~$fiber_callers_valid(S_receiver, (n_receiver), S_receiver.FIBERCALLERS, eps)',
            '~$call_descriptors_valid(S_receiver)',
            'pconfigcall_line = pconfigcall[.LINE = $(pconfigcall.LINE + 1)]',
            'pfiberarray_line = pfiberarray[.LINE = pconfigcall_line.LINE]',
            'pfiberapi_line = pfibercaller.API[.LINE = pconfigcall_line.LINE]',
            'pfibercaller_line = pfibercaller[.API = pfiberapi_line][.VM.TODO = (FIBER_WAIT pfiberapi_line) :: (FIBER_ARRAY_RESULT pfiberarray_line pconfigcall_line) :: ptask_saved*]',
            'S_line = S[.FIBERCALLERS = [pfibercaller_line, pfibercaller_outer]]',
            '$heap_graph(S_line) = H', '~$fiber_array_source_valid(S_line, pfiberarray_line)',
            '~$fiber_callers_valid(S_line, (n_receiver), S_line.FIBERCALLERS, eps)',
            '~$call_descriptors_valid(S_line)',
            'pfibercaller_missing = pfibercaller[.VM.TODO = (FIBER_WAIT pfibercaller.API) :: ptask_saved*]',
            'S_missing = S[.FIBERCALLERS = [pfibercaller_missing, pfibercaller_outer]]',
            '$heap_graph(S_missing) = H',
            'S_wait_missing = $fiber_vm_restore(S_missing, pfibercaller_missing.VM)[.ACTIVEFIBER = (n_parent)][.FIBERCALLERS = [pfibercaller_outer]]',
            '~$fiber_api_valid(S_wait_missing, pfibercaller.API)',
            '~$call_descriptors_valid(S_missing)',
            'pfibercaller_extra = pfibercaller[.VM.TODO = (FIBER_WAIT pfibercaller.API) :: (FIBER_ARRAY_RESULT pfiberarray pconfigcall) :: (FIBER_ARRAY_RESULT pfiberarray pconfigcall) :: ptask_saved*]',
            'S_extra = S[.FIBERCALLERS = [pfibercaller_extra, pfibercaller_outer]]',
            '$heap_graph(S_extra) = H', '~$call_descriptors_valid(S_extra)',
            'pfibercaller_previous = pfibercaller[.PREVIOUS = (n_receiver)]',
            'S_previous = S[.FIBERCALLERS = [pfibercaller_previous, pfibercaller_outer]]',
            '$heap_graph(S_previous) = H',
            '~$fiber_callers_valid(S_previous, (n_receiver), S_previous.FIBERCALLERS, eps)',
            '~$call_descriptors_valid(S_previous)',
            *ZERO, *FINISH,
            '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
        ],
    },
    'array-constructor-keeps-parser-authority-through-warning': {
        'source': SOURCES['author-fiber-array-constructor-warning-parse-and-ready-order'],
        'stage': ('S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: '
                  '(FIBER_ARRAY_RESULT pfiberarray pconfigcall) :: ptask_tail* '
                  '-- if perrorcall.RESUME = API_CALLABLE_RESULT papiquery 1 '
                  '-- if pconfigcall.KIND = INTRINSIC_FIBER_CONSTRUCT'),
        'checks': [
            'S.ACTIVEFIBER = (n_runner)', 'S.ORIGIN = (pconfigcall.SITE)',
            'S.FIBERCALLERS = [pfibercaller]',
            'pfibercaller.OBJECT = n_runner', 'pfibercaller.PREVIOUS = eps',
            'pconfigcall.OWNER = (n_receiver)', 'pconfigcall.SELECTION = eps',
            'pconfigcall.INDEX = 1', 'pconfigcall.NAMED', 'pconfigcall.PACKS = eps',
            'pconfigcall.SENT = [NAMED_SENT (KNOWN (PSTRING ($ptascii("self::callback"))))]',
            'pfiberarray.KIND = pconfigcall.KIND', 'pfiberarray.INPUT = (n_receiver)',
            'pfiberarray.NAME = $ptascii("__construct")', 'n_array = pfiberarray.ARRAY',
            '~((HARRAY n_array) <- S.ALLOCATIONS)',
            '$fiber_at(S, n_receiver) = (pfiber_receiver)',
            'pfiber_receiver.READY', 'pfiber_receiver.STATUS = FIBER_INIT',
            'papiquery.SOURCE = CONFIG_INVOKE pconfigcall',
            'papiquery.VALUE = PSTRING ($ptascii("self::callback"))',
            'perrorcall.LEVEL = 8192', 'perrorcall.LINE = pconfigcall.LINE',
            'papiquery.LINE = pconfigcall.LINE',
            '$fiber_capture_config_task(perrorcall.RESUME, pconfigcall)',
            '$fiber_capture_config_task(ERROR_HANDLER_INVOKE perrorcall, pconfigcall)',
            '$fiber_capture_config_task(ERROR_HANDLER_RESULT perrorcall, pconfigcall)',
            '$fiber_capture_config_task(ERROR_HANDLER_CLEAN perrorcall, pconfigcall)',
            '$fiber_array_config_pair(S.TODO, pconfigcall) = (pfiberarray)',
            '$fiber_array_source_valid(S, pfiberarray)',
            '$fiber_array_selected(S, pfiberarray, pconfigcall)',
            '$fiber_array_result_valid(S, pfiberarray, pconfigcall)',
            '$config_selected_valid(S, pconfigcall)', '$config_invoke_valid(S, pconfigcall)',
            '$api_source_valid(S, papiquery)', '$api_query_valid(S, papiquery, 1)',
            '$error_call_valid(S, perrorcall)',
            '$config_nodes(pconfigcall) = [HOBJECT n_receiver]',
            '$task_nodes(FIBER_ARRAY_RESULT pfiberarray pconfigcall) = eps',
            'H = $heap_graph(S)', '$heap_owners(H, HOBJECT n_receiver) = 1',
            '$heap_owners(H, HARRAY n_array) = 0', *review.VALID,
            'papiquery_value = papiquery[.VALUE = PNULL]',
            'perrorcall_value = perrorcall[.RESUME = API_CALLABLE_RESULT papiquery_value 1]',
            'S_value = S[.TODO = (ERROR_HANDLER_INVOKE perrorcall_value) :: (FIBER_ARRAY_RESULT pfiberarray pconfigcall) :: ptask_tail*]',
            '$heap_graph(S_value) = H', '~$api_source_valid(S_value, papiquery_value)',
            '~$error_call_valid(S_value, perrorcall_value)', '~$call_descriptors_valid(S_value)',
            'pfiberarray_receiver = pfiberarray[.INPUT = (n_runner)]',
            'S_receiver = S[.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: (FIBER_ARRAY_RESULT pfiberarray_receiver pconfigcall) :: ptask_tail*]',
            '$heap_graph(S_receiver) = H',
            '~$fiber_array_selected(S_receiver, pfiberarray_receiver, pconfigcall)',
            '~$config_invoke_valid(S_receiver, pconfigcall)', '~$call_descriptors_valid(S_receiver)',
            'pconfigcall_line = pconfigcall[.LINE = $(pconfigcall.LINE + 1)]',
            'pfiberarray_line = pfiberarray[.LINE = pconfigcall_line.LINE]',
            'papiquery_line = papiquery[.SOURCE = CONFIG_INVOKE pconfigcall_line][.LINE = pconfigcall_line.LINE]',
            'perrorcall_line = perrorcall[.RESUME = API_CALLABLE_RESULT papiquery_line 1][.LINE = pconfigcall_line.LINE][.EVENT = $api_warning_event(S, papiquery_line, perrorcall.MESSAGE)]',
            'S_line = S[.TODO = (ERROR_HANDLER_INVOKE perrorcall_line) :: (FIBER_ARRAY_RESULT pfiberarray_line pconfigcall_line) :: ptask_tail*]',
            '$heap_graph(S_line) = H', '~$fiber_array_source_valid(S_line, pfiberarray_line)',
            '~$api_source_valid(S_line, papiquery_line)', '~$call_descriptors_valid(S_line)',
            'S_missing = S[.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*]',
            '$heap_graph(S_missing) = H', '~$config_invoke_valid(S_missing, pconfigcall)',
            '~$api_source_valid(S_missing, papiquery)', '~$call_descriptors_valid(S_missing)',
            'S_extra = S[.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: (FIBER_ARRAY_RESULT pfiberarray pconfigcall) :: (FIBER_ARRAY_RESULT pfiberarray pconfigcall) :: ptask_tail*]',
            '$heap_graph(S_extra) = H', '~$config_invoke_valid(S_extra, pconfigcall)',
            '~$call_descriptors_valid(S_extra)', *ZERO, *FINISH,
            '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
        ],
    },
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', action='append', choices=CASES)
    args = parser.parse_args()
    review.ROOT = ROOT
    review.CASES = CASES
    review.__file__ = str(Path(__file__).resolve())
    passed = review.run(args.case or list(CASES))
    assert CATALOG.read_bytes() == SOURCE_BYTES, 'Array consumer originals changed during run'
    raise SystemExit(0 if passed else 1)
