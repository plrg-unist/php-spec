#!/usr/bin/env python3
"""A real C-root constructor parser keeps its warning continuation across parking."""
import json
from pathlib import Path
import fiber_state_review as review

ROOT = Path(__file__).resolve().parents[2]
CATALOG = Path(__file__).with_name('fiber_constructor_capture_cases.json')
SOURCE_BYTES = CATALOG.read_bytes()
SOURCE = next(row['source'] for row in json.loads(SOURCE_BYTES)
              if row['id'] == 'author-fiber-ctor-core-compound-warning-suspends')

CASES = {
    'ctor-core-compound-parser-keeps-real-warning-and-caller': {
        'source': SOURCE,
        'stage': ('S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: '
                  '(FIBER_API_CORE_RESULT n_runner n_capture pconfigcall) :: ptask_tail* '
                  '-- if perrorcall.RESUME = API_CALLABLE_RESULT papiquery 1 '
                  '-- if pconfigcall.KIND = INTRINSIC_FIBER_CONSTRUCT'),
        'checks': [
            'ptask_tail* = [FIBER_FINISH n_runner]',
            'S.ACTIVEFIBER = (n_runner)', 'S.CURRENT = eps', 'S.FRAMES = eps',
            'S.ORIGIN = (pconfigcall.SITE)',
            'S.FIBERCALLERS = [pfibercaller]',
            '$fiber_at(S, n_runner) = (pfiber_runner)',
            'pfiber_runner.RAW = POBJECT n_capture',
            'pfiber_runner.TARGET = (FIBER_API_TARGET n_capture)',
            'pfiber_runner.ENTRY = ({SLOTS pconfigcall.SENT, NAMED eps})',
            'S.OBJECTS[n_capture] = FIBERAPICLOSURE pfibercapture',
            'pfibercapture.KIND = INTRINSIC_FIBER_CONSTRUCT',
            'pfibercapture.INPUT = (n_receiver)',
            'pconfigcall.OWNER = (n_receiver)',
            'pconfigcall.SELECTION = (n_capture)',
            'pconfigcall.SENT = [NAMED_SENT (KNOWN (PARRAY n_buffer))]',
            'pconfigcall.INDEX = 1', 'pconfigcall.PACKS = eps', '~pconfigcall.NAMED',
            '$fiber_at(S, n_receiver) = (pfiber_receiver)',
            'pfiber_receiver.READY', 'pfiber_receiver.STATUS = FIBER_INIT',
            'papiquery.SOURCE = CONFIG_INVOKE pconfigcall',
            'papiquery.VALUE = PARRAY n_buffer',
            'papiquery.OUTER = (papiclass_outer)',
            'papiquery.CLASS.REQUESTED =/= papiclass_outer.REQUESTED',
            'papiquery.SCOPE = eps', 'papiquery.CALLED = eps', 'papiquery.THIS = eps',
            'perrorcall.LINE = pconfigcall.LINE',
            'papiquery.LINE = pconfigcall.LINE', 'perrorcall.LEVEL = 8192',
            'pfibercaller.OBJECT = n_runner', 'pfibercaller.API.OBJECT = n_runner',
            'pfibercaller.PREVIOUS = eps',
            'pfibercaller.API.START = (pnamedargs)',
            'pnamedargs.SLOTS = eps',
            'pnamedargs.NAMED = [($ptascii("callback"), KNOWN (PARRAY n_buffer))]',
            '$fiber_capture_core_live(S, n_capture)',
            '$fiber_capture_config_task(API_CALLABLE_RESULT papiquery 1, pconfigcall)',
            '$fiber_capture_config_task(ERROR_HANDLER_INVOKE perrorcall, pconfigcall)',
            '$fiber_capture_config_task(ERROR_HANDLER_RESULT perrorcall, pconfigcall)',
            '$fiber_capture_config_task(ERROR_HANDLER_CLEAN perrorcall, pconfigcall)',
            '~$config_selected_valid(S, pconfigcall)',
            '$config_invoke_valid(S, pconfigcall)',
            '$fiber_api_core_result_valid(S, n_runner, n_capture, pconfigcall)',
            '$api_source_valid(S, papiquery)', '$api_query_valid(S, papiquery, 1)',
            '$error_call_valid(S, perrorcall)',
            '$node_children(S, HOBJECT n_capture) = [HOBJECT n_receiver]',
            '$config_nodes(pconfigcall) = [HARRAY n_buffer]',
            '$task_nodes(FIBER_API_CORE_RESULT n_runner n_capture pconfigcall) = [HOBJECT n_capture]',
            'H = $heap_graph(S)', '$heap_owners(H, HOBJECT n_capture) = 2',
            '$heap_owners(H, HOBJECT n_receiver) = 1',
            '$heap_owners(H, HOBJECT n_runner) = 2',
            '$heap_owners(H, HARRAY n_buffer) = 2',
            *review.VALID,
            'papiquery_value = papiquery[.VALUE = PNULL]',
            'perrorcall_value = perrorcall[.RESUME = API_CALLABLE_RESULT papiquery_value 1]',
            'S_value = S[.TODO = [ERROR_HANDLER_INVOKE perrorcall_value, FIBER_API_CORE_RESULT n_runner n_capture pconfigcall, FIBER_FINISH n_runner]]',
            '$heap_graph(S_value) = H',
            '~$api_source_valid(S_value, papiquery_value)',
            '~$error_call_valid(S_value, perrorcall_value)', '~$call_descriptors_valid(S_value)',
            'pconfigcall_owner = pconfigcall[.OWNER = (n_runner)]',
            'papiquery_owner = papiquery[.SOURCE = CONFIG_INVOKE pconfigcall_owner]',
            'perrorcall_owner = perrorcall[.RESUME = API_CALLABLE_RESULT papiquery_owner 1]',
            'S_owner = S[.TODO = [ERROR_HANDLER_INVOKE perrorcall_owner, FIBER_API_CORE_RESULT n_runner n_capture pconfigcall_owner, FIBER_FINISH n_runner]]',
            '$heap_graph(S_owner) = H',
            '~$fiber_api_core_result_valid(S_owner, n_runner, n_capture, pconfigcall_owner)',
            '~$api_source_valid(S_owner, papiquery_owner)', '~$call_descriptors_valid(S_owner)',
            'pconfigcall_line = pconfigcall[.LINE = $(pconfigcall.LINE + 1)]',
            'papiquery_line = papiquery[.SOURCE = CONFIG_INVOKE pconfigcall_line][.LINE = pconfigcall_line.LINE]',
            'perrorcall_line = perrorcall[.RESUME = API_CALLABLE_RESULT papiquery_line 1][.LINE = pconfigcall_line.LINE][.EVENT = $api_warning_event(S, papiquery_line, perrorcall.MESSAGE)]',
            'S_line = S[.TODO = [ERROR_HANDLER_INVOKE perrorcall_line, FIBER_API_CORE_RESULT n_runner n_capture pconfigcall_line, FIBER_FINISH n_runner]]',
            '$heap_graph(S_line) = H',
            '~$fiber_api_core_result_valid(S_line, n_runner, n_capture, pconfigcall_line)',
            '~$api_source_valid(S_line, papiquery_line)', '~$call_descriptors_valid(S_line)',
            'S_missing = S[.TODO = [ERROR_HANDLER_INVOKE perrorcall, FIBER_CAPTURE_RELEASE n_capture pconfigcall.SITE, FIBER_FINISH n_runner]]',
            '$heap_graph(S_missing) = H',
            '~$fiber_api_core_result_valid(S_missing, n_runner, n_capture, pconfigcall)',
            '~$config_invoke_valid(S_missing, pconfigcall)', '~$call_descriptors_valid(S_missing)',
            'S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
            'S_zero[.COMPLETION = NORMAL] = S',
            'S_done = $drive(S, 4000)', *review.DONE,
            'S_done.EVENTS = [OUTPUT $ptascii("W"), OUTPUT $ptascii("1"), OUTPUT $ptascii("1"), OUTPUT $ptascii("|"), OUTPUT $ptascii("R"), OUTPUT $ptascii("P"), OUTPUT $ptascii("|"), OUTPUT $ptascii("9"), OUTPUT $ptascii("|"), OUTPUT $ptascii("Cannot call constructor twice"), OUTPUT $ptascii("|"), OUTPUT $ptascii("__construct"), OUTPUT $ptascii("->"), OUTPUT $ptascii("0"), OUTPUT $ptascii("0"), OUTPUT $ptascii("|"), OUTPUT $ptascii("resume"), OUTPUT $ptascii("->"), OUTPUT $ptascii("1"), OUTPUT $ptascii("1"), OUTPUT $ptascii("|"), OUTPUT $ptascii("1"), OUTPUT $ptascii("1"), OUTPUT $ptascii("1")]',
            '~((HOBJECT n_capture) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
        ],
    },
}

if __name__ == '__main__':
    review.ROOT = ROOT
    review.CASES = CASES
    review.__file__ = str(Path(__file__).resolve())
    passed = review.run(list(CASES))
    assert CATALOG.read_bytes() == SOURCE_BYTES, 'Constructor capture catalog changed during run'
    raise SystemExit(0 if passed else 1)
