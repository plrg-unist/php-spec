#!/usr/bin/env python3
"""Independent captured-start C-root caller, buffer and retirement checks."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('fiber_start_core_cases.json')
SOURCE_BYTES = CATALOG.read_bytes()
SOURCES = {row['id']: row['source'] for row in json.loads(SOURCE_BYTES)}
STAGE = ('S.FIBERCALLERS = pfibercaller :: pfibercaller_tail* '
         '-- if pfiberapi = pfibercaller.API '
         '-- if pfibercaller.VM.TODO = (FIBER_WAIT pfiberapi) :: '
         '(FIBER_START_CORE_RESULT n_runner n_capture pfiberstart) :: ptask_saved* '
         '-- if ptask_saved* = [FIBER_FINISH n_runner] '
         '-- if S.TODO = [FIBER_ENTER n_receiver pnamedargs, FIBER_FINISH n_receiver]')
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
FINISH = ['S_done = $drive(S, 4000)', *review.DONE]
COMMON = [
    'S.ACTIVEFIBER = (n_receiver)', 'S.CURRENT = eps', 'S.FRAMES = eps',
    'pfibercaller.OBJECT = n_receiver', 'pfibercaller.PREVIOUS = (n_runner)',
    '~pfibercaller.VM.GLOBAL', 'pfibercaller.VM.TABLE = $empty_table()',
    'pfibercaller.VM.CURRENT = eps', 'pfibercaller.VM.FRAMES = eps',
    'S.OBJECTS[n_capture] = FIBERAPICLOSURE pfibercapture',
    'pfibercapture.KIND = INTRINSIC_FIBER_START', 'pfibercapture.INPUT = (n_receiver)',
    '$fiber_capture_live(S, n_capture)', '$fiber_start_core_live(S, n_capture)',
    '~$fiber_capture_core_live(S, n_capture)',
    '$node_children(S, HOBJECT n_capture) = [HOBJECT n_receiver]',
    '$fiber_at(S, n_runner) = (pfiber_runner)', 'pfiber_runner.STATUS = FIBER_RUNNING',
    'pfiber_runner.RAW = POBJECT n_capture',
    'pfiber_runner.TARGET = (FIBER_API_TARGET n_capture)',
    '$fiber_cached_target_valid(S, pfiber_runner)',
    '$fiber_core_callback_kind(S, pfiber_runner) = eps',
    'pfiber_runner.ENTRY = (pnamedargs)', 'pfiberstart.SENT = pnamedargs',
    'pfiberstart.OBJECT = n_receiver', 'pfiberapi.KIND = eps', 'pfiberapi.SENT = eps',
    'pfiberapi.START = (pnamedargs)', 'pfiberapi.SITE = pfiberstart.SITE',
    'pfiberapi.LINE = pfiberstart.LINE',
    '$fiber_caller_api_nodes(pfibercaller) = $wrapper_roots(pfiberapi.START)',
    '$fiber_api_nodes(pfiberapi) = [HOBJECT n_receiver] ++ $wrapper_roots(pfiberapi.START)',
    '$task_nodes(FIBER_START_CORE_RESULT n_runner n_capture pfiberstart) = [HOBJECT n_capture]',
    '$heap_count(HOBJECT n_receiver, $fiber_vm_nodes(pfibercaller.VM)) = 0',
    '$heap_count(HOBJECT n_capture, $fiber_vm_nodes(pfibercaller.VM)) = 1',
    'S_wait = $fiber_vm_restore(S, pfibercaller.VM)[.ACTIVEFIBER = (n_runner)]'
    '[.FIBERCALLERS = pfibercaller_tail*]',
    '$fiber_start_core_actor(S_wait)',
    '$fiber_start_core_tasks(S_wait, n_runner, n_capture, pfiberstart)',
    '$fiber_start_core_result_valid(S_wait, n_runner, n_capture, pfiberstart)',
    '$fiber_start_core_wait_valid(S_wait, pfiberapi)',
    '$fiber_api_valid(S_wait, pfiberapi)', '$fiber_wait_valid(S_wait, pfiberapi)',
    '$fiber_vm_valid(S, pfibercaller.VM, (n_runner), pfibercaller_tail*)',
    '$fiber_caller_api_trace(S_wait, pfiberapi) = [ptraceframe]',
    'ptraceframe.FILE = eps', 'ptraceframe.LINE = $(-1)',
    'ptraceframe.FUNCTION = $ptascii("start")',
    'ptraceframe.CLASS = ($ptascii("Fiber"))', 'ptraceframe.TYPE = ($ptascii("->"))',
    'H = $heap_graph(S)',
]

def events(*pieces):
    return 'S_done.EVENTS = [' + ', '.join('OUTPUT $ptascii(' + json.dumps(x) + ')' for x in pieces) + ']'

CASES = {
    'start-core-real-parent-keeps-raw-binding-and-caller-chain': {
        'source': SOURCES['peer-bound-start-core-real-parent-chain'],
        'stage': STAGE + ' -- if pfibercaller_tail* = [pfibercaller_runner, pfibercaller_parent]',
        'checks': [
            *COMMON, 'pnamedargs.SLOTS = eps',
            'pnamedargs.NAMED = [($ptascii("value"), KNOWN (PSTRING $ptascii("V")))]',
            'pfibercaller_runner.OBJECT = n_runner', 'pfibercaller_runner.PREVIOUS = (n_parent)',
            'pfibercaller_parent.OBJECT = n_parent', 'pfibercaller_parent.PREVIOUS = eps',
            '~pfibercaller_runner.VM.GLOBAL', 'pfibercaller_parent.VM.GLOBAL',
            'pfibercaller_runner.API.START = (pnamedargs)',
            'pfibercaller_runner.API.SITE = pfiberstart.SITE',
            'pfibercaller_runner.API.LINE = pfiberstart.LINE',
            '$heap_owners(H, HOBJECT n_capture) = 2', '$heap_owners(H, HOBJECT n_receiver) = 2',
            '$fiber_at(S, n_parent) = (pfiber_parent)',
            'pfiber_parent.RAW = POBJECT n_parent_capture',
            '$node_children(S, HOBJECT n_parent_capture) = [HOBJECT n_runner]',
            'psymboltable_global = $fiber_globals(S)',
            '$lookup(psymboltable_global.ENV, $ptascii("runner")) = (n_global_runner)',
            '$node_children(S, HCELL n_global_runner) = [HOBJECT n_runner]',
            '$lookup(pfibercaller_runner.VM.TABLE.ENV, $ptascii("runner")) = (n_local_runner)',
            'n_local_runner =/= n_global_runner',
            '$node_children(S, HCELL n_local_runner) = [HOBJECT n_runner]',
            '$fiber_caller_api_nodes(pfibercaller_runner) = [HOBJECT n_runner]',
            '$heap_owners(H, HOBJECT n_runner) = 4', '$heap_owners(H, HOBJECT n_parent) = 2',
            'pfiberapi_line = pfiberapi[.LINE = $(pfiberapi.LINE + 1)]',
            'pfiberstart_line = pfiberstart[.LINE = pfiberapi_line.LINE]',
            'pfibercaller_line = pfibercaller[.API = pfiberapi_line][.VM.TODO = '
            '[FIBER_WAIT pfiberapi_line, FIBER_START_CORE_RESULT n_runner n_capture pfiberstart_line, FIBER_FINISH n_runner]]',
            'S_line = S[.FIBERCALLERS = pfibercaller_line :: pfibercaller_tail*]',
            '$heap_graph(S_line) = H', '~$call_descriptors_valid(S_line)',
            'S_wait_line = $fiber_vm_restore(S_line, pfibercaller_line.VM)[.ACTIVEFIBER = (n_runner)]'
            '[.FIBERCALLERS = pfibercaller_tail*]',
            '~$fiber_start_core_wait_valid(S_wait_line, pfiberapi_line)',
            'pfiberapi_receiver = pfiberapi[.OBJECT = n_runner]',
            'pfiberstart_receiver = pfiberstart[.OBJECT = n_runner]',
            'pfibercaller_receiver = pfibercaller[.OBJECT = n_runner][.API = pfiberapi_receiver][.VM.TODO = '
            '[FIBER_WAIT pfiberapi_receiver, FIBER_START_CORE_RESULT n_runner n_capture pfiberstart_receiver, FIBER_FINISH n_runner]]',
            'S_receiver = S[.FIBERCALLERS = pfibercaller_receiver :: pfibercaller_tail*]',
            '$heap_graph(S_receiver) = H', '~$call_descriptors_valid(S_receiver)',
            'S_wait_receiver = $fiber_vm_restore(S_receiver, pfibercaller_receiver.VM)[.ACTIVEFIBER = (n_runner)]'
            '[.FIBERCALLERS = pfibercaller_tail*]',
            '~$fiber_start_core_wait_valid(S_wait_receiver, pfiberapi_receiver)',
            'pfibercaller_header = pfibercaller[.VM.TODO = '
            '[FIBER_WAIT pfiberapi, FIBER_START_CORE_RESULT n_parent n_capture pfiberstart, FIBER_FINISH n_parent]]',
            'S_header = S[.FIBERCALLERS = pfibercaller_header :: pfibercaller_tail*]',
            '$heap_graph(S_header) = H', '~$call_descriptors_valid(S_header)',
            'S_target = $fiber_put(S, n_runner, pfiber_runner[.TARGET = (FIBER_API_TARGET n_runner)])',
            '$heap_graph(S_target) = H', '~$call_descriptors_valid(S_target)',
            'S_wait_removed = S_wait[.TODO = [FIBER_WAIT pfiberapi, FIBER_FINISH n_runner]]',
            '~$fiber_start_core_wait_valid(S_wait_removed, pfiberapi)',
            '~$fiber_api_valid(S_wait_removed, pfiberapi)', '~$call_descriptors_valid(S_wait_removed)',
            'S_wait_tail = S_wait[.TODO = [FIBER_WAIT pfiberapi, FIBER_START_CORE_RESULT n_runner n_capture pfiberstart]]',
            '~$fiber_start_core_wait_valid(S_wait_tail, pfiberapi)',
            'pfiberapi_sequence = pfiberapi[.SEQUENCE = S.FIBERSEQ]',
            'S_wait_sequence = S_wait[.TODO = [FIBER_WAIT pfiberapi_sequence, '
            'FIBER_START_CORE_RESULT n_runner n_capture pfiberstart, FIBER_FINISH n_runner]]',
            '~$fiber_start_core_wait_valid(S_wait_sequence, pfiberapi_sequence)',
            'S_wait_hidden = S_wait[.TODO = [FIBER_WAIT pfiberapi, '
            'AT pfiberstart.SITE (FIBER_START_CORE_RESULT n_runner n_capture pfiberstart), FIBER_FINISH n_runner]]',
            '~$generator_flat_tasks(S_wait_hidden.TODO)',
            '~$fiber_start_core_wait_valid(S_wait_hidden, pfiberapi)',
            *review.VALID, *ZERO, *FINISH,
            events('P|', 'T', '1', 'V', '|', 'R', '1', 'Y', '|', 'CY', '|', '17', '|', '19'),
            '~((HOBJECT n_capture) <- S_done.ALLOCATIONS)',
        ],
    },
    'start-core-last-raw-retires-before-original-payload': {
        'source': SOURCES['peer-bound-start-core-last-raw-before-payload-retirement'],
        'stage': STAGE + ' -- if pfibercaller_tail* = [pfibercaller_runner]',
        'checks': [
            *COMMON, 'pnamedargs.SLOTS = [NAMED_SENT (KNOWN (POBJECT n_arg))]',
            'pnamedargs.NAMED = eps', 'pfibercaller_runner.OBJECT = n_runner',
            'pfibercaller_runner.PREVIOUS = eps', 'pfibercaller_runner.VM.GLOBAL',
            'pfibercaller_runner.API.START = (pnamedargs)',
            '$fiber_caller_api_nodes(pfibercaller) = [HOBJECT n_arg]',
            '$fiber_caller_api_nodes(pfibercaller_runner) = [HOBJECT n_runner, HOBJECT n_arg]',
            '$heap_count(HOBJECT n_arg, $fiber_vm_nodes(pfibercaller.VM)) = 0',
            '$heap_count(HOBJECT n_arg, $tasks_nodes(S.TODO)) = 0',
            '$heap_count(HOBJECT n_arg, $task_nodes(FIBER_START_CORE_RESULT n_runner n_capture pfiberstart)) = 0',
            '$heap_owners(H, HOBJECT n_arg) = 2', '$heap_owners(H, HOBJECT n_capture) = 2',
            '$heap_owners(H, HOBJECT n_receiver) = 1', '$heap_owners(H, HOBJECT n_runner) = 2',
            '~(n_arg <- S.DESTRUCTION.CALLED)',
            '$node_children(S, HOBJECT n_runner) = [HOBJECT n_capture]',
            *review.VALID, *ZERO, *FINISH,
            events('F|', 'D', '1', '1', '|', '1', '|', 'Y', '|', '1', '1'),
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
    assert CATALOG.read_bytes() == SOURCE_BYTES, 'Start core catalog changed during run'
    raise SystemExit(0 if passed else 1)
