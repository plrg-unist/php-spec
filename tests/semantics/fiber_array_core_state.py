#!/usr/bin/env python3
"""Raw-array START and constructor callbacks retain real buffers and callers."""
import argparse
import json
from pathlib import Path
import fiber_state_review as review

ROOT = Path(__file__).resolve().parents[2]
CATALOG = Path(__file__).with_name('fiber_array_core_cases.json')
SOURCE_BYTES = CATALOG.read_bytes()
SOURCES = {row['id']: row['source'] for row in json.loads(SOURCE_BYTES)}
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
FINISH = ['S_done = $drive(S, 4000)', *review.DONE]


def events(*pieces):
    return 'S_done.EVENTS = [' + ', '.join(
        'OUTPUT $ptascii(' + json.dumps(piece) + ')' for piece in pieces) + ']'


CASES = {
    'raw-array-start-borrows-receiver-through-real-parent-chain': {
        'source': SOURCES['author-fiber-raw-array-start-named-buffer-and-real-parent'],
        'stage': ('S.TODO = (FIBER_ENTER n_receiver pnamedargs) :: ptask_finish* '
                  '-- if ptask_finish* = [FIBER_FINISH n_receiver] '
                  '-- if S.FIBERCALLERS = [pfibercaller, pfibercaller_runner, pfibercaller_parent] '
                  '-- if pfiberapi = pfibercaller.API '
                  '-- if pfibercaller.VM.TODO = (FIBER_WAIT pfiberapi) :: '
                  '(FIBER_ARRAY_CORE_START_RESULT n_runner pfiberstart) :: ptask_saved*'),
        'checks': [
            'ptask_saved* = [FIBER_FINISH n_runner]',
            'S.ACTIVEFIBER = (n_receiver)', 'S.CURRENT = eps', 'S.FRAMES = eps',
            'pfibercaller.OBJECT = n_receiver', 'pfibercaller.PREVIOUS = (n_runner)',
            'pfibercaller_runner.OBJECT = n_runner',
            'pfibercaller_runner.PREVIOUS = (n_parent)',
            'pfibercaller_parent.OBJECT = n_parent',
            'pfibercaller_parent.PREVIOUS = eps', 'pfibercaller_parent.VM.GLOBAL',
            '$fiber_at(S, n_runner) = (pfiber_runner)',
            'pfiber_runner.TARGET = (FIBER_ARRAY_TARGET pfiberrawapi)',
            'pfiber_runner.RAW = PARRAY n_callback',
            'pfiber_runner.CALL = (pconfigcall_constructor)',
            'pconfigcall_constructor.OWNER = (n_runner)',
            'pfiberrawapi.KIND = INTRINSIC_FIBER_START',
            'pfiberrawapi.INPUT = (n_receiver)',
            'pfiberrawapi.NAME = $ptascii("StArT")',
            'pfiberrawapi.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_receiver)), '
            'ENTRY (KINT 1) (DIRECT (PSTRING ($ptascii("StArT"))))]',
            '$fiber_raw_cached_valid(S, pfiber_runner)',
            '$target_nodes(FIBER_ARRAY_TARGET pfiberrawapi) = eps',
            '$node_children(S, HARRAY n_callback) = [HOBJECT n_receiver]',
            '$fiber_at(S, n_receiver) = (pfiber_receiver)',
            'pfiber_receiver.STATUS = FIBER_RUNNING',
            'pfiber_receiver.ENTRY = (pnamedargs)',
            'pfiberstart.OBJECT = n_receiver', 'pfiberstart.INDEX = 2',
            'pfiberstart.SENT = pnamedargs', 'pnamedargs.SLOTS = eps',
            'pnamedargs.NAMED = [($ptascii("value"), KNOWN (PSTRING ($ptascii("7")))), '
            '($ptascii("tag"), KNOWN (PSTRING ($ptascii("X"))))]',
            'pfiber_runner.ENTRY = (pnamedargs)',
            'pfiberapi.OBJECT = n_receiver', 'pfiberapi.KIND = eps',
            'pfiberapi.START = (pnamedargs)', 'pfiberapi.SENT = eps',
            'pfiberapi.SITE = pfiberstart.SITE', 'pfiberapi.LINE = pfiberstart.LINE',
            'pfibercaller_runner.API.START = (pnamedargs)',
            'pfibercaller_runner.API.SITE = pfiberstart.SITE',
            'pfibercaller_runner.API.LINE = pfiberstart.LINE',
            '$task_nodes(FIBER_ARRAY_CORE_START_RESULT n_runner pfiberstart) = eps',
            '$fiber_api_nodes(pfiberapi) = [HOBJECT n_receiver]',
            '$fiber_caller_api_nodes(pfibercaller) = eps',
            '$heap_count(HOBJECT n_receiver, $fiber_vm_nodes(pfibercaller.VM)) = 0',
            'psymboltable_global = $fiber_globals(S)',
            '$lookup(psymboltable_global.ENV, $ptascii("target")) = (n_target_cell)',
            '$node_children(S, HCELL n_target_cell) = [HOBJECT n_receiver]',
            '$lookup(psymboltable_global.ENV, $ptascii("runner")) = (n_runner_cell)',
            '$node_children(S, HCELL n_runner_cell) = [HOBJECT n_runner]',
            '$lookup(pfibercaller_runner.VM.TABLE.ENV, $ptascii("runner")) = (n_local_runner)',
            'n_local_runner =/= n_runner_cell',
            '$node_children(S, HCELL n_local_runner) = [HOBJECT n_runner]',
            '$fiber_at(S, n_parent) = (pfiber_parent)',
            'pfiber_parent.RAW = POBJECT n_parent_capture',
            '$node_children(S, HOBJECT n_parent_capture) = [HOBJECT n_runner]',
            '$fiber_caller_api_nodes(pfibercaller_runner) = [HOBJECT n_runner]',
            'H = $heap_graph(S)', '$heap_owners(H, HOBJECT n_receiver) = 2',
            '$heap_owners(H, HOBJECT n_runner) = 4',
            '$heap_owners(H, HOBJECT n_parent) = 2',
            'S_wait = $fiber_vm_restore(S, pfibercaller.VM)[.ACTIVEFIBER = (n_runner)]'
            '[.FIBERCALLERS = [pfibercaller_runner, pfibercaller_parent]]',
            '$fiber_start_core_actor(S_wait)',
            '$fiber_core_callback_kind(S_wait, pfiber_runner) = eps',
            '$fiber_raw_outer_valid(S_wait, n_runner)',
            '$fiber_raw_start_valid(S_wait, n_runner, pfiberstart)',
            '$fiber_raw_start_wait_valid(S_wait, pfiberapi)',
            '$fiber_api_valid(S_wait, pfiberapi)', '$fiber_wait_valid(S_wait, pfiberapi)',
            '$fiber_vm_valid(S, pfibercaller.VM, (n_runner), '
            '[pfibercaller_runner, pfibercaller_parent])',
            '$fiber_caller_api_trace(S_wait, pfiberapi) = [ptraceframe]',
            'ptraceframe.FUNCTION = $ptascii("start")',
            'ptraceframe.FILE = eps', 'ptraceframe.LINE = $(-1)',
            'ptraceframe.ARGS = [(KSTRING ($ptascii("value")), PSTRING ($ptascii("7"))), '
            '(KSTRING ($ptascii("tag")), PSTRING ($ptascii("X")))]',
            *review.VALID,
            'pfiberrawapi_input = pfiberrawapi[.INPUT = (n_parent)]',
            'S_input = $fiber_put(S, n_runner, pfiber_runner'
            '[.TARGET = (FIBER_ARRAY_TARGET pfiberrawapi_input)])',
            '$heap_graph(S_input) = H',
            '~$fiber_raw_cached_valid(S_input, pfiber_runner'
            '[.TARGET = (FIBER_ARRAY_TARGET pfiberrawapi_input)])',
            '~$call_descriptors_valid(S_input)',
            'pfiberstart_line = pfiberstart[.LINE = $(pfiberstart.LINE + 1)]',
            'pfiberapi_line = pfiberapi[.LINE = pfiberstart_line.LINE]',
            'pfibercaller_line = pfibercaller[.API = pfiberapi_line]'
            '[.VM.TODO = [FIBER_WAIT pfiberapi_line, '
            'FIBER_ARRAY_CORE_START_RESULT n_runner pfiberstart_line, FIBER_FINISH n_runner]]',
            'S_line = S[.FIBERCALLERS = '
            '[pfibercaller_line, pfibercaller_runner, pfibercaller_parent]]',
            '$heap_graph(S_line) = H', '~$call_descriptors_valid(S_line)',
            'S_wait_line = $fiber_vm_restore(S_line, pfibercaller_line.VM)'
            '[.ACTIVEFIBER = (n_runner)]'
            '[.FIBERCALLERS = [pfibercaller_runner, pfibercaller_parent]]',
            '~$fiber_raw_start_wait_valid(S_wait_line, pfiberapi_line)',
            'pfibercaller_header = pfibercaller[.VM.TODO = [FIBER_WAIT pfiberapi, '
            'FIBER_ARRAY_CORE_START_RESULT n_parent pfiberstart, FIBER_FINISH n_parent]]',
            'S_header = S[.FIBERCALLERS = '
            '[pfibercaller_header, pfibercaller_runner, pfibercaller_parent]]',
            '$heap_graph(S_header) = H', '~$call_descriptors_valid(S_header)',
            'pfibercaller_previous = pfibercaller[.PREVIOUS = (n_parent)]',
            'S_previous = S[.FIBERCALLERS = '
            '[pfibercaller_previous, pfibercaller_runner, pfibercaller_parent]]',
            '$heap_graph(S_previous) = H', '~$call_descriptors_valid(S_previous)',
            'pfibercaller_missing = pfibercaller[.VM.TODO = '
            '[FIBER_WAIT pfiberapi, FIBER_FINISH n_runner]]',
            'S_missing = S[.FIBERCALLERS = '
            '[pfibercaller_missing, pfibercaller_runner, pfibercaller_parent]]',
            '$fiber_caller_api_nodes(pfibercaller_missing) = [HOBJECT n_receiver]',
            '$heap_owners($heap_graph(S_missing), HOBJECT n_receiver) = 3',
            '~$call_descriptors_valid(S_missing)',
            *ZERO, *FINISH,
            events('P|', '7', '|', 'D', '|', 'X', '|', '1', '|', '1', '|',
                   'Y', '|', '1', '|', 'R', '|', '1', '|', '29', '|', '19'),
        ],
    },
    'raw-array-constructor-keeps-parser-warning-and-original-buffer': {
        'source': SOURCES['author-fiber-raw-array-constructor-warning-parks-real-root'],
        'stage': ('S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: '
                  '(FIBER_CORE_RESULT n_runner pconfigcall) :: ptask_tail* '
                  '-- if perrorcall.RESUME = API_CALLABLE_RESULT papiquery 1 '
                  '-- if pconfigcall.KIND = INTRINSIC_FIBER_CONSTRUCT'),
        'checks': [
            'ptask_tail* = [FIBER_FINISH n_runner]',
            'S.ACTIVEFIBER = (n_runner)', 'S.CURRENT = eps', 'S.FRAMES = eps',
            'S.ORIGIN = (pconfigcall.SITE)', 'S.FIBERCALLERS = [pfibercaller]',
            '$fiber_at(S, n_runner) = (pfiber_runner)',
            'pfiber_runner.RAW = PARRAY n_callback',
            'pfiber_runner.TARGET = (FIBER_ARRAY_TARGET pfiberrawapi)',
            'pfiber_runner.CALL = (pconfigcall_constructor)',
            'pconfigcall_constructor.OWNER = (n_runner)',
            'pfiber_runner.ENTRY = ({SLOTS pconfigcall.SENT, NAMED eps})',
            'pfiberrawapi.KIND = INTRINSIC_FIBER_CONSTRUCT',
            'pfiberrawapi.INPUT = (n_receiver)',
            'pfiberrawapi.NAME = $ptascii("__construct")',
            'pconfigcall.OWNER = (n_receiver)', 'pconfigcall.SELECTION = (n_runner)',
            'pconfigcall.SENT = [NAMED_SENT (KNOWN (PARRAY n_buffer))]',
            'pconfigcall.INDEX = 1', 'pconfigcall.PACKS = eps', '~pconfigcall.NAMED',
            '$fiber_at(S, n_receiver) = (pfiber_receiver)',
            'pfiber_receiver.READY', 'pfiber_receiver.STATUS = FIBER_INIT',
            'papiquery.SOURCE = CONFIG_INVOKE pconfigcall',
            'papiquery.VALUE = PARRAY n_buffer', 'papiquery.OUTER = (papiclass_outer)',
            'papiquery.CLASS.REQUESTED =/= papiclass_outer.REQUESTED',
            'papiquery.SCOPE = eps', 'papiquery.CALLED = eps', 'papiquery.THIS = eps',
            'papiquery.LINE = pconfigcall.LINE', 'perrorcall.LINE = pconfigcall.LINE',
            'perrorcall.LEVEL = 8192',
            'pfibercaller.OBJECT = n_runner', 'pfibercaller.API.OBJECT = n_runner',
            'pfibercaller.PREVIOUS = eps', 'pfibercaller.API.START = (pnamedargs)',
            'pnamedargs.SLOTS = eps',
            'pnamedargs.NAMED = [($ptascii("callback"), KNOWN (PARRAY n_buffer))]',
            '$fiber_raw_cached_valid(S, pfiber_runner)',
            '$fiber_core_site_valid(S, pconfigcall)',
            '$fiber_core_result_valid(S, n_runner, pconfigcall)',
            '$fiber_core_config_valid(S, pconfigcall)',
            '~$config_selected_valid(S, pconfigcall)',
            '$selected_task_nonce(CONFIG_INVOKE pconfigcall) = eps',
            '$selected_task_nonce(ERROR_HANDLER_INVOKE perrorcall) = eps',
            '$config_invoke_valid(S, pconfigcall)',
            '$api_source_valid(S, papiquery)', '$api_query_valid(S, papiquery, 1)',
            '$error_call_valid(S, perrorcall)',
            '$target_nodes(FIBER_ARRAY_TARGET pfiberrawapi) = eps',
            '$node_children(S, HARRAY n_callback) = [HOBJECT n_receiver]',
            '$config_nodes(pconfigcall) = [HARRAY n_buffer]',
            '$task_nodes(FIBER_CORE_RESULT n_runner pconfigcall) = eps',
            'H = $heap_graph(S)', '$heap_owners(H, HOBJECT n_receiver) = 1',
            '$heap_owners(H, HOBJECT n_runner) = 2',
            '$heap_owners(H, HARRAY n_buffer) = 2', *review.VALID,
            'papiquery_value = papiquery[.VALUE = PNULL]',
            'perrorcall_value = perrorcall[.RESUME = API_CALLABLE_RESULT papiquery_value 1]',
            'S_value = S[.TODO = [ERROR_HANDLER_INVOKE perrorcall_value, '
            'FIBER_CORE_RESULT n_runner pconfigcall, FIBER_FINISH n_runner]]',
            '$heap_graph(S_value) = H', '~$api_source_valid(S_value, papiquery_value)',
            '~$error_call_valid(S_value, perrorcall_value)', '~$call_descriptors_valid(S_value)',
            'pconfigcall_owner = pconfigcall[.OWNER = (n_runner)]',
            'papiquery_owner = papiquery[.SOURCE = CONFIG_INVOKE pconfigcall_owner]',
            'perrorcall_owner = perrorcall[.RESUME = API_CALLABLE_RESULT papiquery_owner 1]',
            'S_owner = S[.TODO = [ERROR_HANDLER_INVOKE perrorcall_owner, '
            'FIBER_CORE_RESULT n_runner pconfigcall_owner, FIBER_FINISH n_runner]]',
            '$heap_graph(S_owner) = H',
            '~$fiber_core_result_valid(S_owner, n_runner, pconfigcall_owner)',
            '~$api_source_valid(S_owner, papiquery_owner)', '~$call_descriptors_valid(S_owner)',
            'pconfigcall_line = pconfigcall[.LINE = $(pconfigcall.LINE + 1)]',
            'papiquery_line = papiquery[.SOURCE = CONFIG_INVOKE pconfigcall_line]'
            '[.LINE = pconfigcall_line.LINE]',
            'perrorcall_line = perrorcall[.RESUME = API_CALLABLE_RESULT papiquery_line 1]'
            '[.LINE = pconfigcall_line.LINE]'
            '[.EVENT = $api_warning_event(S, papiquery_line, perrorcall.MESSAGE)]',
            'S_line = S[.TODO = [ERROR_HANDLER_INVOKE perrorcall_line, '
            'FIBER_CORE_RESULT n_runner pconfigcall_line, FIBER_FINISH n_runner]]',
            '$heap_graph(S_line) = H',
            '~$fiber_core_result_valid(S_line, n_runner, pconfigcall_line)',
            '~$api_source_valid(S_line, papiquery_line)', '~$call_descriptors_valid(S_line)',
            'S_missing = S[.TODO = [ERROR_HANDLER_INVOKE perrorcall, DISCARD, '
            'FIBER_FINISH n_runner]]',
            '$heap_graph(S_missing) = H',
            '~$fiber_core_result_valid(S_missing, n_runner, pconfigcall)',
            '~$config_invoke_valid(S_missing, pconfigcall)', '~$call_descriptors_valid(S_missing)',
            *ZERO, *FINISH,
            events('W', '1', '1', '|', 'R', 'P', '|', '9', '|',
                   'Cannot call constructor twice', '|', '__construct', '.', '0', '0', '|',
                   'resume', '.', '1', '1', '|', '1', '|', '1'),
            '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
        ],
    },
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=CASES)
    args = parser.parse_args()
    review.ROOT = ROOT
    review.CASES = CASES
    review.__file__ = str(Path(__file__).resolve())
    passed = review.run(args.case or list(CASES))
    assert CATALOG.read_bytes() == SOURCE_BYTES, 'Raw-array callback originals changed during run'
    raise SystemExit(0 if passed else 1)
