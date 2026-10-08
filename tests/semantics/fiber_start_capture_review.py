#!/usr/bin/env python3
"""Independent source-reached bound start selection, buffers and retirement."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('fiber_start_capture_cases.json')
SOURCE_BYTES = CATALOG.read_bytes()
SOURCES = {r['id']: r['source'] for r in json.loads(SOURCE_BYTES)}
STAGE = ('S.FIBERCALLERS = [pfibercaller] '
         '-- if pfiberapi = pfibercaller.API '
         '-- if pfibercaller.VM.TODO = (FIBER_WAIT pfiberapi) :: '
         '(FIBER_START_CAPTURE_RESULT n_capture pfiberstart b_invoke) :: ptask_saved* '
         '-- if S.TODO = [FIBER_ENTER n_receiver pnamedargs, FIBER_FINISH n_receiver] ')
COMMON = [
    'S.ACTIVEFIBER = (n_receiver)', 'S.CURRENT = eps', 'S.FRAMES = eps',
    'pfibercaller.OBJECT = n_receiver', 'pfibercaller.PREVIOUS = eps',
    'pfibercaller.VM.GLOBAL',
    'S.OBJECTS[n_capture] = FIBERAPICLOSURE pfibercapture',
    'pfibercapture.KIND = INTRINSIC_FIBER_START',
    'pfibercapture.INPUT = (n_receiver)', '$fiber_capture_live(S, n_capture)',
    '~$fiber_capture_core_live(S, n_capture)',
    '$node_children(S, HOBJECT n_capture) = [HOBJECT n_receiver]',
    'pfiberstart.OBJECT = n_receiver', 'pfiberstart.SENT = pnamedargs',
    'pfiberapi.KIND = eps', 'pfiberapi.SENT = eps', 'pfiberapi.START = (pnamedargs)',
    'pfiberapi.SITE = pfiberstart.SITE', 'pfiberapi.LINE = pfiberstart.LINE',
    '$task_nodes(FIBER_ENTER n_receiver pnamedargs) = eps',
    '$task_nodes(FIBER_WAIT pfiberapi) = eps',
    '$fiber_at(S, n_receiver) = (pfiber)', 'pfiber.STATUS = FIBER_RUNNING',
    'S_wait = $fiber_vm_restore(S, pfibercaller.VM)[.ACTIVEFIBER = eps][.FIBERCALLERS = eps]',
    '$fiber_start_capture_result_valid(S_wait, n_capture, pfiberstart, b_invoke)',
    '$fiber_api_valid(S_wait, pfiberapi)', '$fiber_wait_valid(S_wait, pfiberapi)',
    '$fiber_vm_valid(S, pfibercaller.VM, eps, eps)',
    'H = $heap_graph(S)',
]
LINE_FORGERY = [
    'pfiberapi_line = pfiberapi[.LINE = $(pfiberapi.LINE + 1)]',
    'pfiberstart_line = pfiberstart[.LINE = pfiberapi_line.LINE]',
    'pfibercaller_line = pfibercaller[.API = pfiberapi_line]'
    '[.VM.TODO = (FIBER_WAIT pfiberapi_line) :: '
    '(FIBER_START_CAPTURE_RESULT n_capture pfiberstart_line b_invoke) :: ptask_saved*]',
    'S_line = S[.FIBERCALLERS = [pfibercaller_line]]',
    '$heap_graph(S_line) = H', '~$call_descriptors_valid(S_line)',
    'S_wait_line = $fiber_vm_restore(S_line, pfibercaller_line.VM)'
    '[.ACTIVEFIBER = eps][.FIBERCALLERS = eps]',
    '~$fiber_start_capture_result_valid(S_wait_line, n_capture, pfiberstart_line, b_invoke)',
    '~$fiber_api_valid(S_wait_line, pfiberapi_line)',
    'pfiberapi_sequence = pfiberapi[.SEQUENCE = S.FIBERSEQ]',
    'S_wait_sequence = S_wait[.TODO = (FIBER_WAIT pfiberapi_sequence) :: '
    '(FIBER_START_CAPTURE_RESULT n_capture pfiberstart b_invoke) :: ptask_saved*]',
    '~$fiber_api_valid(S_wait_sequence, pfiberapi_sequence)',
]
FINISH = [*review.VALID, 'S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
          'S_zero[.COMPLETION = NORMAL] = S', 'S_done = $drive(S, 4000)', *review.DONE]

CASES = {
    'bound-start-named-wait-keeps-selected-receiver': {
        'source': SOURCES['peer-bound-start-dynamic-capture-named-selection'],
        'stage': STAGE + '-- if b_invoke = false',
        'checks': [
            *COMMON,
            'pfibercapture.NAME = $ptascii("StArT")',
            'pnamedargs.SLOTS = eps',
            'pnamedargs.NAMED = [($ptascii("value"), KNOWN (POBJECT n_other))]',
            'psymboltable_global = $fiber_globals(S)',
            '$lookup(psymboltable_global.ENV, $ptascii("selected")) = (n_selected)',
            'S.STORE[n_selected] = DEFINED (POBJECT n_other)',
            '$fiber_at(S, n_other) = (pfiber_other)', 'pfiber_other.STATUS = FIBER_INIT',
            '$fiber_caller_api_nodes(pfibercaller) = [HOBJECT n_other]',
            '$fiber_api_nodes(pfiberapi) = [HOBJECT n_receiver, HOBJECT n_other]',
            '$heap_count(HOBJECT n_receiver, $fiber_vm_nodes(pfibercaller.VM)) = 0',
            '$heap_count(HOBJECT n_capture, $fiber_vm_nodes(pfibercaller.VM)) = 1',
            '$heap_owners(H, HOBJECT n_receiver) = 2',
            '$heap_owners(H, HOBJECT n_capture) = 2',
            '$fiber_caller_api_trace(S_wait, pfiberapi) = [ptraceframe]',
            'ptraceframe.FUNCTION = $ptascii("start")',
            'ptraceframe.FILE = $call_sourcefile(S.FILES, pfiberstart.SITE)',
            'ptraceframe.LINE = pfiberstart.LINE',
            'ptraceframe.TYPE = ($ptascii("->"))',
            'pfiberstart_other = pfiberstart[.OBJECT = n_other]',
            'pfiberapi_other = pfiberapi[.OBJECT = n_other]',
            'pfibercaller_other = pfibercaller[.OBJECT = n_other][.API = pfiberapi_other]'
            '[.VM.TODO = (FIBER_WAIT pfiberapi_other) :: '
            '(FIBER_START_CAPTURE_RESULT n_capture pfiberstart_other false) :: ptask_saved*]',
            'S_other = S[.FIBERCALLERS = [pfibercaller_other]]',
            '$heap_graph(S_other) = H', '~$call_descriptors_valid(S_other)',
            'S_wait_other = $fiber_vm_restore(S_other, pfibercaller_other.VM)'
            '[.ACTIVEFIBER = eps][.FIBERCALLERS = eps]',
            '~$fiber_start_capture_result_valid(S_wait_other, n_capture, pfiberstart_other, false)',
            *LINE_FORGERY,
            'S_duplicate = S_wait[.TODO = (FIBER_WAIT pfiberapi) :: '
            '(FIBER_START_CAPTURE_RESULT n_capture pfiberstart false) :: '
            '(FIBER_START_CAPTURE_RESULT n_capture pfiberstart false) :: ptask_saved*]',
            '~$fiber_start_capture_result_valid(S_duplicate, n_capture, pfiberstart, false)',
            'S_hidden = S_wait[.TODO = (FIBER_WAIT pfiberapi) :: '
            '(AT pfiberstart.SITE (FIBER_START_CAPTURE_RESULT n_capture pfiberstart false)) :: ptask_saved*]',
            '~$generator_flat_tasks(S_hidden.TODO)',
            *FINISH,
            'S_done.EVENTS = [OUTPUT $ptascii("O"), OUTPUT $ptascii("1"), OUTPUT $ptascii("|"), '
            'OUTPUT $ptascii("Y"), OUTPUT $ptascii("|"), OUTPUT $ptascii("1"), '
            'OUTPUT $ptascii("0"), OUTPUT $ptascii("1"), OUTPUT $ptascii("|"), OUTPUT $ptascii("47")]',
            '~((HOBJECT n_capture) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
        ],
    },
    'bound-start-invoke-wait-keeps-both-buffers-through-retirement': {
        'source': SOURCES['peer-bound-start-last-capture-closes-before-payload-retirement'],
        'stage': STAGE + '-- if b_invoke = true',
        'checks': [
            *COMMON,
            'pnamedargs.SLOTS = [NAMED_SENT (KNOWN (POBJECT n_payload))]',
            'pnamedargs.NAMED = eps',
            '$fiber_caller_api_nodes(pfibercaller) = [HOBJECT n_payload]',
            '$fiber_api_nodes(pfiberapi) = [HOBJECT n_receiver, HOBJECT n_payload]',
            '$task_nodes(FIBER_START_CAPTURE_RESULT n_capture pfiberstart true) = '
            '[HOBJECT n_capture, HOBJECT n_capture, HOBJECT n_payload]',
            '$heap_count(HOBJECT n_receiver, $fiber_vm_nodes(pfibercaller.VM)) = 0',
            '$heap_count(HOBJECT n_capture, $fiber_vm_nodes(pfibercaller.VM)) = 2',
            '$heap_count(HOBJECT n_payload, $fiber_vm_nodes(pfibercaller.VM)) = 1',
            '$heap_owners(H, HOBJECT n_capture) = 3',
            '$heap_owners(H, HOBJECT n_receiver) = 1',
            '$heap_owners(H, HOBJECT n_payload) = 2',
            '$fiber_caller_api_trace(S_wait, pfiberapi) = [ptraceframe, ptraceframe_invoke]',
            'ptraceframe.FUNCTION = $ptascii("start")',
            'ptraceframe_invoke.FUNCTION = $ptascii("__invoke")',
            'ptraceframe.FILE = $call_sourcefile(S.FILES, pfiberstart.SITE)',
            'ptraceframe_invoke.FILE = ptraceframe.FILE',
            'ptraceframe.LINE = pfiberstart.LINE', 'ptraceframe_invoke.LINE = pfiberstart.LINE',
            'ptraceframe.TYPE = ($ptascii("->"))', 'ptraceframe_invoke.TYPE = ptraceframe.TYPE',
            'S_wrong_invoke = S_wait[.TODO = (FIBER_WAIT pfiberapi) :: '
            '(FIBER_START_CAPTURE_RESULT n_capture pfiberstart false) :: ptask_saved*]',
            '~$fiber_start_capture_result_valid(S_wrong_invoke, n_capture, pfiberstart, false)',
            *LINE_FORGERY, *FINISH,
            'S_done.EVENTS = [OUTPUT $ptascii("Y"), OUTPUT $ptascii("|"), OUTPUT $ptascii("1"), '
            'OUTPUT $ptascii("|"), OUTPUT $ptascii("F|"), OUTPUT $ptascii("D"), '
            'OUTPUT $ptascii("0"), OUTPUT $ptascii("1"), OUTPUT $ptascii("|"), '
            'OUTPUT $ptascii("1"), OUTPUT $ptascii("1")]',
            '~((HOBJECT n_capture) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_payload) <- S_done.ALLOCATIONS)',
        ],
    },
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', action='append', default=[], choices=CASES)
    args = parser.parse_args()
    review.ROOT = ROOT
    review.CASES = CASES
    review.__file__ = str(Path(__file__).resolve())
    passed = review.run(args.case)
    assert CATALOG.read_bytes() == SOURCE_BYTES, 'Start capture catalog changed during run'
    raise SystemExit(0 if passed else 1)
