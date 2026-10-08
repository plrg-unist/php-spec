#!/usr/bin/env python3
"""Independent bound C-root cache, waiting caller and retirement checks."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('fiber_bound_core_cases.json')
SOURCE_BYTES = CATALOG.read_bytes()
SOURCES = {row['id']: row['source'] for row in json.loads(SOURCE_BYTES)}
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
FINISH = ['S_done = $drive(S, 4000)', *review.DONE]
CAPTURE = [
    'S.OBJECTS[n_capture] = FIBERAPICLOSURE pfibercapture',
    'pfibercapture.INPUT = (n_receiver)', '$fiber_bound_kind(pfibercapture.KIND)',
    '$fiber_capture_live(S, n_capture)', '$fiber_capture_core_live(S, n_capture)',
    '$node_children(S, HOBJECT n_capture) = [HOBJECT n_receiver]',
    '$fiber_at(S, n_runner) = (pfiber_runner)',
    'pfiber_runner.RAW = POBJECT n_capture',
    'pfiber_runner.TARGET = (FIBER_API_TARGET n_capture)',
    '$fiber_cached_target_valid(S, pfiber_runner)',
    'n_owner? = (n_receiver)', 'n_selection? = (n_capture)',
    '$fiber_core_binding(S, pfiber_runner) = (n_owner?, n_selection?)',
]

CASES = {
    'bound-core-selection-keeps-raw-binding-and-borrowed-receiver': {
        'source': SOURCES['peer-bound-core-defined-return-keeps-last-receiver'],
        'stage': ('S.TODO = [CONFIG_INVOKE pconfigcall, '
                  'FIBER_API_CORE_RESULT n_runner n_capture pconfigcall, FIBER_FINISH n_runner] '
                  '-- if pconfigcall.KIND = INTRINSIC_FIBER_RETURN '
                  '-- if pconfigcall.OWNER = (n_receiver)'),
        'checks': [
            *CAPTURE, 'S.ACTIVEFIBER = (n_runner)',
            'S.CURRENT = eps', 'S.FRAMES = eps',
            'pconfigcall.SELECTION = (n_capture)', 'pconfigcall.SENT = eps',
            'pconfigcall.PACKS = eps', '~pconfigcall.NAMED',
            'pfiber_runner.ENTRY = ({SLOTS eps, NAMED eps})',
            '$config_nodes(pconfigcall) = eps',
            '$task_nodes(FIBER_API_CORE_RESULT n_runner n_capture pconfigcall) = [HOBJECT n_capture]',
            '$target_nodes(FIBER_API_TARGET n_capture) = eps',
            'H = $heap_graph(S)', '$heap_owners(H, HOBJECT n_receiver) = 1',
            '$heap_owners(H, HOBJECT n_capture) = 2',
            '$fiber_core_result_valid(S, n_runner, pconfigcall)',
            '$fiber_api_core_result_valid(S, n_runner, n_capture, pconfigcall)',
            '$fiber_core_config_valid(S, pconfigcall)',
            '$config_selected_valid(S, pconfigcall)', '$config_invoke_valid(S, pconfigcall)',
            '$config_trace_frames(S, pconfigcall, eps) = [ptraceframe]',
            'ptraceframe.FILE = eps', 'ptraceframe.LINE = $(-1)',
            'ptraceframe.CLASS = ($ptascii("Fiber"))',
            'ptraceframe.FUNCTION = $ptascii("getReturn")',
            'ptraceframe.TYPE = ($ptascii("->"))',
            'pconfigcall_owner = pconfigcall[.OWNER = (n_runner)]',
            'S_owner = S[.TODO = [CONFIG_INVOKE pconfigcall_owner, '
            'FIBER_API_CORE_RESULT n_runner n_capture pconfigcall_owner, FIBER_FINISH n_runner]]',
            '$heap_graph(S_owner) = H',
            '~$fiber_core_result_valid(S_owner, n_runner, pconfigcall_owner)',
            '~$fiber_api_core_result_valid(S_owner, n_runner, n_capture, pconfigcall_owner)',
            '~$call_descriptors_valid(S_owner)',
            'pconfigcall_selection = pconfigcall[.SELECTION = (n_runner)]',
            'S_selection = S[.TODO = [CONFIG_INVOKE pconfigcall_selection, '
            'FIBER_API_CORE_RESULT n_runner n_capture pconfigcall_selection, FIBER_FINISH n_runner]]',
            '$heap_graph(S_selection) = H',
            '~$fiber_core_result_valid(S_selection, n_runner, pconfigcall_selection)',
            '~$call_descriptors_valid(S_selection)',
            'S_target = $fiber_put(S, n_runner, pfiber_runner[.TARGET = (FIBER_API_TARGET n_runner)])',
            '$heap_graph(S_target) = H',
            '~$fiber_cache_valid(S_target, n_runner, pfiber_runner[.TARGET = (FIBER_API_TARGET n_runner)])',
            '~$call_descriptors_valid(S_target)',
            'S_duplicate = S[.TODO = [CONFIG_INVOKE pconfigcall, '
            'FIBER_API_CORE_RESULT n_runner n_capture pconfigcall, '
            'FIBER_API_CORE_RESULT n_runner n_capture pconfigcall, FIBER_FINISH n_runner]]',
            '~$fiber_core_result_valid(S_duplicate, n_runner, pconfigcall)',
            'S_hidden = S[.TODO = [CONFIG_INVOKE pconfigcall, '
            'AT pconfigcall.SITE (FIBER_API_CORE_RESULT n_runner n_capture pconfigcall), FIBER_FINISH n_runner]]',
            '~$generator_flat_tasks(S_hidden.TODO)',
            '~$fiber_core_result_valid(S_hidden, n_runner, pconfigcall)',
            *review.VALID, *ZERO, *FINISH,
            'S_done.EVENTS = [OUTPUT $ptascii("1"), OUTPUT $ptascii("|"), '
            'OUTPUT $ptascii("1"), OUTPUT $ptascii("|"), OUTPUT $ptascii("23"), '
            'OUTPUT $ptascii("|"), OUTPUT $ptascii("1")]',
            '~((HOBJECT n_capture) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
        ],
    },
    'bound-core-nested-wait-keeps-real-runner-and-parent-chain': {
        'source': SOURCES['peer-bound-core-nested-running-callers'],
        'stage': ('S.FIBERCALLERS = [pfibercaller, pfibercaller_runner, pfibercaller_parent] '
                  '-- if pfibercaller.API.KIND = (INTRINSIC_FIBER_RESUME) '
                  '-- if pfibercaller.VM.TODO = [FIBER_WAIT pfibercaller.API, '
                  'FIBER_API_CORE_RESULT n_runner n_capture pconfigcall, FIBER_FINISH n_runner] '
                  '-- if pconfigcall.OWNER = (n_receiver) '
                  '-- if S.TODO = (FIBER_CONTINUE pfiberapi_continue) :: ptask_child*'),
        'checks': [
            *CAPTURE, 'S.ACTIVEFIBER = (n_receiver)',
            'pfibercaller.OBJECT = n_receiver', 'pfibercaller.PREVIOUS = (n_runner)',
            'pfibercaller_runner.OBJECT = n_runner', 'pfibercaller_runner.PREVIOUS = (n_parent)',
            'pfibercaller_parent.OBJECT = n_parent', 'pfibercaller_parent.PREVIOUS = eps',
            '~pfibercaller.VM.GLOBAL', '~pfibercaller_runner.VM.GLOBAL',
            'pfibercaller_parent.VM.GLOBAL',
            'pfibercaller.API.SENT = (PSTRING $ptascii("argument"))',
            'pconfigcall.SENT = [NAMED_SENT (KNOWN (PSTRING $ptascii("argument")))]',
            '$fiber_caller_api_nodes(pfibercaller) = eps',
            '$fiber_api_nodes(pfibercaller.API) = [HOBJECT n_receiver]',
            '$heap_count(HOBJECT n_receiver, $fiber_vm_nodes(pfibercaller.VM)) = 0',
            '$heap_count(HOBJECT n_capture, $fiber_vm_nodes(pfibercaller.VM)) = 1',
            'H = $heap_graph(S)', '$heap_owners(H, HOBJECT n_receiver) = 2',
            '$heap_owners(H, HOBJECT n_capture) = 2',
            '$heap_owners(H, HOBJECT n_runner) = 3', '$heap_owners(H, HOBJECT n_parent) = 2',
            'S_wait = $fiber_vm_restore(S, pfibercaller.VM)[.ACTIVEFIBER = (n_runner)]'
            '[.FIBERCALLERS = [pfibercaller_runner, pfibercaller_parent]]',
            '$fiber_core_result_valid(S_wait, n_runner, pconfigcall)',
            '$fiber_api_core_result_valid(S_wait, n_runner, n_capture, pconfigcall)',
            '$fiber_bound_core_call(S_wait, pfibercaller.API) = (pconfigcall)',
            '$fiber_api_valid(S_wait, pfibercaller.API)', '$fiber_wait_valid(S_wait, pfibercaller.API)',
            '$fiber_vm_valid(S, pfibercaller.VM, (n_runner), [pfibercaller_runner, pfibercaller_parent])',
            '$fiber_caller_api_trace(S_wait, pfibercaller.API) = [ptraceframe]',
            'ptraceframe.FILE = eps', 'ptraceframe.LINE = $(-1)',
            'ptraceframe.FUNCTION = $ptascii("resume")', 'ptraceframe.TYPE = ($ptascii("->"))',
            'pfiberapi_line = pfibercaller.API[.LINE = $(pfibercaller.API.LINE + 1)]',
            'pconfigcall_line = pconfigcall[.LINE = pfiberapi_line.LINE]',
            'pfibercaller_line = pfibercaller[.API = pfiberapi_line]'
            '[.VM.TODO = [FIBER_WAIT pfiberapi_line, '
            'FIBER_API_CORE_RESULT n_runner n_capture pconfigcall_line, FIBER_FINISH n_runner]]',
            'S_line = S[.FIBERCALLERS = [pfibercaller_line, pfibercaller_runner, pfibercaller_parent]]',
            '$heap_graph(S_line) = H', '~$call_descriptors_valid(S_line)',
            'S_wait_line = $fiber_vm_restore(S_line, pfibercaller_line.VM)[.ACTIVEFIBER = (n_runner)]'
            '[.FIBERCALLERS = [pfibercaller_runner, pfibercaller_parent]]',
            '$fiber_bound_core_call(S_wait_line, pfiberapi_line) = eps',
            'pfibercaller_header = pfibercaller[.VM.TODO = [FIBER_WAIT pfibercaller.API, '
            'FIBER_API_CORE_RESULT n_parent n_capture pconfigcall, FIBER_FINISH n_parent]]',
            'S_header = S[.FIBERCALLERS = [pfibercaller_header, pfibercaller_runner, pfibercaller_parent]]',
            '$heap_graph(S_header) = H', '~$call_descriptors_valid(S_header)',
            'S_wait_header = $fiber_vm_restore(S_header, pfibercaller_header.VM)[.ACTIVEFIBER = (n_runner)]'
            '[.FIBERCALLERS = [pfibercaller_runner, pfibercaller_parent]]',
            '$fiber_bound_core_call(S_wait_header, pfibercaller.API) = eps',
            'pfibercaller_tail = pfibercaller[.VM.TODO = [FIBER_WAIT pfibercaller.API, '
            'FIBER_API_CORE_RESULT n_runner n_capture pconfigcall]]',
            '~$fiber_vm_valid(S, pfibercaller_tail.VM, (n_runner), [pfibercaller_runner, pfibercaller_parent])',
            'pfiberapi_sequence = pfibercaller.API[.SEQUENCE = S.FIBERSEQ]',
            'S_wait_sequence = S_wait[.TODO = [FIBER_WAIT pfiberapi_sequence, '
            'FIBER_API_CORE_RESULT n_runner n_capture pconfigcall, FIBER_FINISH n_runner]]',
            '$fiber_bound_core_call(S_wait_sequence, pfiberapi_sequence) = eps',
            *review.VALID, *ZERO, *FINISH,
            'S_done.EVENTS = [OUTPUT $ptascii("P|"), OUTPUT $ptascii("C"), '
            'OUTPUT $ptascii("1"), OUTPUT $ptascii("1"), OUTPUT $ptascii("1"), '
            'OUTPUT $ptascii("|"), OUTPUT $ptascii("R"), OUTPUT $ptascii("|"), '
            'OUTPUT $ptascii("1"), OUTPUT $ptascii("|"), OUTPUT $ptascii("31"), '
            'OUTPUT $ptascii("|"), OUTPUT $ptascii("17")]',
            '~((HOBJECT n_capture) <- S_done.ALLOCATIONS)',
        ],
    },
    'bound-core-raw-retirement-precedes-original-start-argument': {
        'source': SOURCES['author-bound-core-last-capture-retirement'],
        'stage': ('S.TODO = [FIBER_FINISH n_runner] '
                  '-- if S.ACTIVEFIBER = (n_runner) '
                  '-- if S.FIBERCALLERS = [pfibercaller] '
                  '-- if $fiber_at(S, n_runner) = (pfiber_runner) '
                  '-- if pfiber_runner.RAW = POBJECT n_capture '
                  '-- if S.OBJECTS[n_capture] = FIBERAPICLOSURE pfibercapture '
                  '-- if pfibercapture.INPUT = (n_receiver)'),
        'checks': [
            *CAPTURE, 'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ORIGIN = eps',
            'pfiber_runner.STATUS = FIBER_RUNNING', 'pfiber_runner.VM = eps',
            '$fiber_core_count(S.TODO) = 0', '$task_nodes(FIBER_FINISH n_runner) = eps',
            '$node_children(S, HOBJECT n_runner) = [HOBJECT n_capture]',
            'pfibercaller.OBJECT = n_runner', 'pfibercaller.PREVIOUS = eps',
            'pfibercaller.API.START = (pnamedargs)',
            'pnamedargs.SLOTS = [NAMED_SENT (KNOWN (POBJECT n_arg))]',
            'pnamedargs.NAMED = eps',
            '$fiber_caller_api_nodes(pfibercaller) = [HOBJECT n_runner, HOBJECT n_arg]',
            'H = $heap_graph(S)', '$heap_owners(H, HOBJECT n_capture) = 1',
            '$heap_owners(H, HOBJECT n_receiver) = 1', '$heap_owners(H, HOBJECT n_arg) = 1',
            '$heap_count(HOBJECT n_arg, $fiber_caller_api_nodes(pfibercaller)) = 1',
            '$heap_count(HOBJECT n_arg, $tasks_nodes(S.TODO)) = 0',
            '$fiber_at(S, n_receiver) = (pfiber_receiver)',
            'pfiber_receiver.STATUS = FIBER_SUSPENDED',
            '~(n_arg <- S.DESTRUCTION.CALLED)',
            '$fiber_finish_valid(S, n_runner)',
            *review.VALID, *ZERO, *FINISH,
            'S_done.EVENTS = [OUTPUT $ptascii("B|"), OUTPUT $ptascii("F|"), '
            'OUTPUT $ptascii("D"), OUTPUT $ptascii("0"), OUTPUT $ptascii("0"), '
            'OUTPUT $ptascii("|"), OUTPUT $ptascii("1"), OUTPUT $ptascii("1")]',
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
    assert CATALOG.read_bytes() == SOURCE_BYTES, 'Bound core source catalog changed during run'
    raise SystemExit(0 if passed else 1)
