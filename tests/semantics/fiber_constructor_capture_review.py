#!/usr/bin/env python3
"""Independent constructor-capture parser ownership and C-root retirement checks."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('fiber_constructor_capture_cases.json')
SOURCE_BYTES = CATALOG.read_bytes()
SOURCES = {row['id']: row['source'] for row in json.loads(SOURCE_BYTES)}
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
FINISH = ['S_done = $drive(S, 4000)', *review.DONE]
CAPTURE = [
    'S.OBJECTS[n_capture] = FIBERAPICLOSURE pfibercapture',
    'pfibercapture.KIND = INTRINSIC_FIBER_CONSTRUCT',
    'pfibercapture.INPUT = (n_receiver)', '$fiber_capture_live(S, n_capture)',
    '$node_children(S, HOBJECT n_capture) = [HOBJECT n_receiver]',
    'pconfigcall.OWNER = (n_receiver)', 'pconfigcall.SELECTION = (n_capture)',
    '$fiber_capture_config_tag(pconfigcall)', 'pconfigcall.INDEX = 1',
    'pconfigcall.PACKS = eps', '~pconfigcall.NAMED',
    '$fiber_at(S, n_receiver) = (pfiber_receiver)', 'pfiber_receiver.READY',
    'H = $heap_graph(S)',
]


def events(*pieces):
    return 'S_done.EVENTS = [' + ', '.join('OUTPUT $ptascii(' + json.dumps(x) + ')' for x in pieces) + ']'


CASES = {
    'constructor-warning-keeps-direct-capture-owner-and-source': {
        'source': SOURCES['peer-fiber-ctor-capture-keyword-warning-before-status'],
        'stage': ('S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_capture* '
                  '-- if perrorcall.RESUME = API_CALLABLE_RESULT papiquery 1 '
                  '-- if papiquery.SOURCE = CONFIG_INVOKE pconfigcall '
                  '-- if ptask_capture* = (FIBER_CAPTURE_RESULT n_capture pconfigcall false) :: ptask_tail*'),
        'checks': [
            *CAPTURE, 'S.ACTIVEFIBER = eps', 'S.CURRENT = (pcallcontext)',
            'S.EVENTS = eps', 'pfiber_receiver.STATUS = FIBER_INIT',
            'papiquery.VALUE = PSTRING $ptascii("self::callback")',
            'pconfigcall.SENT = [NAMED_SENT (KNOWN papiquery.VALUE)]',
            'papiquery.SCOPE =/= eps', 'papiquery.CALLED = papiquery.SCOPE',
            'papiquery.THIS = eps', 'papiquery.LINE = pconfigcall.LINE',
            'perrorcall.SITE = pconfigcall.SITE', 'perrorcall.LINE = pconfigcall.LINE',
            'perrorcall.LEVEL = 8192', 'perrorcall.TARGET = eps',
            '$fiber_capture_config_task(perrorcall.RESUME, pconfigcall)',
            '$fiber_capture_config_task(ERROR_HANDLER_INVOKE perrorcall, pconfigcall)',
            '$fiber_capture_config_selected(S, pconfigcall)',
            '$fiber_capture_result_valid(S, n_capture, pconfigcall, false)',
            '$config_invoke_valid(S, pconfigcall)', '$api_query_valid(S, papiquery, 1)',
            '$error_call_valid(S, perrorcall)', '$call_task_valid(S, ERROR_HANDLER_INVOKE perrorcall)',
            '$task_nodes(API_CALLABLE_RESULT papiquery 1) = eps',
            '$task_nodes(FIBER_CAPTURE_RESULT n_capture pconfigcall false) = [HOBJECT n_capture]',
            'psymboltable_global = $fiber_globals(S)',
            '$lookup(psymboltable_global.ENV, $ptascii("ctor")) = (n_global_ctor)',
            '$node_children(S, HCELL n_global_ctor) = [HOBJECT n_capture]',
            '$lookup(S.ENV, $ptascii("ctor")) = (n_local_ctor)',
            'n_local_ctor =/= n_global_ctor',
            '$node_children(S, HCELL n_local_ctor) = [HOBJECT n_capture]',
            '$heap_owners(H, HOBJECT n_capture) = 3', '$heap_owners(H, HOBJECT n_receiver) = 2',
            'papiquery_scope = papiquery[.SCOPE = eps]',
            'perrorcall_scope = perrorcall[.RESUME = API_CALLABLE_RESULT papiquery_scope 1]',
            'S_scope = S[.TODO = (ERROR_HANDLER_INVOKE perrorcall_scope) :: ptask_capture*]',
            '$heap_graph(S_scope) = H',
            '$fiber_capture_config_task(ERROR_HANDLER_INVOKE perrorcall_scope, pconfigcall)',
            '~$api_query_valid(S_scope, papiquery_scope, 1)', '~$call_descriptors_valid(S_scope)',
            'papiquery_value = papiquery[.VALUE = PSTRING $ptascii("self::other")]',
            'perrorcall_value = perrorcall[.RESUME = API_CALLABLE_RESULT papiquery_value 1]',
            'S_value = S[.TODO = (ERROR_HANDLER_INVOKE perrorcall_value) :: ptask_capture*]',
            '$heap_graph(S_value) = H',
            '~$fiber_capture_config_task(ERROR_HANDLER_INVOKE perrorcall_value, pconfigcall)',
            '~$api_query_valid(S_value, papiquery_value, 1)', '~$call_descriptors_valid(S_value)',
            'pconfigcall_line = pconfigcall[.LINE = $(pconfigcall.LINE + 1)]',
            'papiquery_line = papiquery[.SOURCE = CONFIG_INVOKE pconfigcall_line][.LINE = pconfigcall_line.LINE]',
            'perrorcall_line = perrorcall[.RESUME = API_CALLABLE_RESULT papiquery_line 1]'
            '[.LINE = pconfigcall_line.LINE][.EVENT = DIAGNOSTIC "Deprecated" perrorcall.MESSAGE pconfigcall_line.LINE]',
            'S_line = S[.TODO = (ERROR_HANDLER_INVOKE perrorcall_line) :: '
            '(FIBER_CAPTURE_RESULT n_capture pconfigcall_line false) :: ptask_tail*]',
            '$heap_graph(S_line) = H', '~$config_invoke_valid(S_line, pconfigcall_line)',
            '~$api_query_valid(S_line, papiquery_line, 1)', '~$call_descriptors_valid(S_line)',
            'S_missing = S[.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*]',
            '~$fiber_capture_config_selected(S_missing, pconfigcall)', '~$call_descriptors_valid(S_missing)',
            'S_duplicate = S[.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: '
            '(FIBER_CAPTURE_RESULT n_capture pconfigcall false) :: ptask_capture*]',
            '~$fiber_capture_config_selected(S_duplicate, pconfigcall)', '~$call_descriptors_valid(S_duplicate)',
            'S_hidden = S[.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: '
            '(AT pconfigcall.SITE (FIBER_CAPTURE_RESULT n_capture pconfigcall false)) :: ptask_tail*]',
            '~$generator_flat_tasks(S_hidden.TODO)', '~$call_descriptors_valid(S_hidden)',
            *review.VALID, *ZERO, *FINISH,
            events('W', '1', '1', '|', 'E|', 'W', '1', '1', '|', 'warning', '|', '1', '1'),
            '~((HOBJECT n_capture) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
        ],
    },
    'constructor-core-last-raw-retires-before-error-argument': {
        'source': SOURCES['peer-fiber-ctor-capture-core-last-raw-error-retirement'],
        'stage': ('S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_core* '
                  '-- if pconfigcall.KIND = INTRINSIC_FIBER_CONSTRUCT '
                  '-- if pconfigcall.OWNER = (n_receiver) '
                  '-- if ptask_core* = [FIBER_API_CORE_RESULT n_runner n_capture pconfigcall, FIBER_FINISH n_runner]'),
        'checks': [
            *CAPTURE, 'S.ACTIVEFIBER = (n_runner)', 'S.CURRENT = eps', 'S.FRAMES = eps',
            'pfiber_receiver.STATUS = FIBER_SUSPENDED',
            'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_arg))]',
            '$fiber_at(S, n_runner) = (pfiber_runner)', 'pfiber_runner.STATUS = FIBER_RUNNING',
            'pfiber_runner.RAW = POBJECT n_capture',
            'pfiber_runner.TARGET = (FIBER_API_TARGET n_capture)',
            'pfiber_runner.ENTRY = ({SLOTS pconfigcall.SENT, NAMED eps})',
            '$fiber_capture_core_live(S, n_capture)', '$fiber_cached_target_valid(S, pfiber_runner)',
            '$node_children(S, HOBJECT n_runner) = [HOBJECT n_capture]',
            '$fiber_core_binding(S, pfiber_runner) = (pconfigcall.OWNER, pconfigcall.SELECTION)',
            'S.FIBERCALLERS = [pfibercaller]', 'pfibercaller.OBJECT = n_runner',
            'pfibercaller.PREVIOUS = eps', 'pfibercaller.VM.GLOBAL',
            'pfibercaller.API.START = ({SLOTS pconfigcall.SENT, NAMED eps})',
            '$fiber_caller_api_nodes(pfibercaller) = [HOBJECT n_runner, HOBJECT n_arg]',
            '$config_nodes(pconfigcall) = [HOBJECT n_arg]',
            '$task_nodes(FIBER_API_CORE_RESULT n_runner n_capture pconfigcall) = [HOBJECT n_capture]',
            '$heap_owners(H, HOBJECT n_arg) = 2', '$heap_owners(H, HOBJECT n_capture) = 2',
            '$heap_owners(H, HOBJECT n_receiver) = 1', '$heap_owners(H, HOBJECT n_runner) = 2',
            '~(n_arg <- S.DESTRUCTION.CALLED)', '~$api_special(S, POBJECT n_arg)',
            '$fiber_callback_resolution(S, POBJECT n_arg) = HANDLERRESOLVED pcalltarget',
            '$fiber_core_result_valid(S, n_runner, pconfigcall)',
            '$fiber_api_core_result_valid(S, n_runner, n_capture, pconfigcall)',
            '$fiber_core_config_valid(S, pconfigcall)',
            '~$config_selected_valid(S, pconfigcall)', '$config_invoke_valid(S, pconfigcall)',
            '$config_trace_frames(S, pconfigcall, [POBJECT n_arg]) = [ptraceframe]',
            'ptraceframe.FILE = eps', 'ptraceframe.LINE = $(-1)',
            'ptraceframe.FUNCTION = $ptascii("__construct")',
            'ptraceframe.CLASS = ($ptascii("Fiber"))', 'ptraceframe.TYPE = ($ptascii("->"))',
            'pconfigcall_owner = pconfigcall[.OWNER = (n_runner)]',
            'S_owner = S[.TODO = [CONFIG_INVOKE pconfigcall_owner, '
            'FIBER_API_CORE_RESULT n_runner n_capture pconfigcall_owner, FIBER_FINISH n_runner]]',
            '$heap_graph(S_owner) = H', '~$fiber_core_config_valid(S_owner, pconfigcall_owner)',
            '~$call_descriptors_valid(S_owner)',
            'pconfigcall_line = pconfigcall[.LINE = $(pconfigcall.LINE + 1)]',
            'S_line = S[.TODO = [CONFIG_INVOKE pconfigcall_line, '
            'FIBER_API_CORE_RESULT n_runner n_capture pconfigcall_line, FIBER_FINISH n_runner]]',
            '$heap_graph(S_line) = H', '~$config_invoke_valid(S_line, pconfigcall_line)',
            '~$call_descriptors_valid(S_line)',
            'S_tail = S[.TODO = [CONFIG_INVOKE pconfigcall, FIBER_API_CORE_RESULT n_runner n_capture pconfigcall]]',
            '$heap_graph(S_tail) = H', '~$fiber_core_result_valid(S_tail, n_runner, pconfigcall)',
            '~$call_descriptors_valid(S_tail)',
            'S_missing = S[.TODO = [CONFIG_INVOKE pconfigcall, FIBER_FINISH n_runner]]',
            '~$fiber_core_config_valid(S_missing, pconfigcall)', '~$call_descriptors_valid(S_missing)',
            'S_target = $fiber_put(S, n_runner, pfiber_runner[.TARGET = (FIBER_API_TARGET n_runner)])',
            '$heap_graph(S_target) = H', '~$fiber_core_config_valid(S_target, pconfigcall)',
            '~$call_descriptors_valid(S_target)',
            *review.VALID, *ZERO, *FINISH,
            events('F|', 'E|', 'D', '1', '1', '|', '1', '1', '1'),
            '~((HOBJECT n_capture) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_arg) <- S_done.ALLOCATIONS)', 'n_arg <- S_done.DESTRUCTION.CALLED',
        ],
    },
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    assert not args.case or set(args.case) <= CASES.keys()
    review.ROOT = ROOT
    review.CASES = CASES
    review.__file__ = str(Path(__file__).resolve())
    passed = all(review.run([name]) for name in args.case or list(CASES))
    assert CATALOG.read_bytes() == SOURCE_BYTES, 'Constructor capture catalog changed during run'
    raise SystemExit(0 if passed else 1)
