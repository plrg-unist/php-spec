#!/usr/bin/env python3
"""Bound start capture across a genuine running parent and named entry buffer."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('fiber_start_capture_cases.json')
SOURCE_BYTES = CATALOG.read_bytes()
SOURCE = next(row['source'] for row in json.loads(SOURCE_BYTES)
              if row['id'] == 'author-bound-start-nested-parent-original-buffer')

CASES = {
    'bound-start-keeps-real-parent-and-original-named-buffer': {
        'source': SOURCE,
        'stage': ('S.TODO = (FIBER_ENTER n_target pnamedargs) :: ptask_tail* '
                  '-- if S.FIBERCALLERS = [pfibercaller_inner, pfibercaller_outer] '
                  '-- if pfibercaller_inner.VM.TODO = (FIBER_WAIT pfiberapi) :: '
                  '(FIBER_START_CAPTURE_RESULT n_capture pfiberstart false) :: ptask_saved*'),
        'checks': [
            'S.ACTIVEFIBER = (n_target)', 'S.CURRENT = eps', 'S.FRAMES = eps',
            'pfibercaller_inner.OBJECT = n_target',
            'pfibercaller_inner.API = pfiberapi',
            'pfibercaller_inner.PREVIOUS = (n_parent)',
            'pfibercaller_outer.OBJECT = n_parent',
            'pfibercaller_outer.PREVIOUS = eps',
            'pfiberapi.OBJECT = n_target', 'pfiberapi.KIND = eps',
            'pfiberapi.SENT = eps', 'pfiberapi.START = (pnamedargs)',
            'pfiberstart.OBJECT = n_target', 'pfiberstart.SENT = pnamedargs',
            'pnamedargs.SLOTS = eps',
            'pnamedargs.NAMED = [($ptascii("value"), KNOWN (PSTRING $ptascii("V")))]',
            'pfiberapi.SITE = pfiberstart.SITE',
            'pfiberapi.LINE = pfiberstart.LINE',
            'S.OBJECTS[n_capture] = FIBERAPICLOSURE pfibercapture',
            'pfibercapture.KIND = INTRINSIC_FIBER_START',
            'pfibercapture.INPUT = (n_target)',
            '$node_children(S, HOBJECT n_capture) = [HOBJECT n_target]',
            '$task_nodes(FIBER_START_CAPTURE_RESULT n_capture pfiberstart false) = [HOBJECT n_capture]',
            '$fiber_caller_api_nodes(pfibercaller_inner) = eps',
            '$fiber_at(S, n_parent) = (pfiber_parent)',
            'pfiber_parent.RAW = POBJECT n_parent_capture',
            '$node_children(S, HOBJECT n_parent_capture) = [HOBJECT n_capture]',
            'psymboltable_global = $fiber_globals(S)',
            '$lookup(psymboltable_global.ENV, $ptascii("start")) = (n_global_start)',
            '$node_children(S, HCELL n_global_start) = [HOBJECT n_capture]',
            '$lookup(pfibercaller_inner.VM.TABLE.ENV, $ptascii("start")) = (n_local_start)',
            'n_local_start =/= n_global_start',
            '$node_children(S, HCELL n_local_start) = [HOBJECT n_capture]',
            'H = $heap_graph(S)', '$heap_owners(H, HOBJECT n_capture) = 4',
            '$heap_owners(H, HOBJECT n_target) = 2',
            '$heap_owners(H, HOBJECT n_parent) = 2',
            'S_wait = $fiber_vm_restore(S, pfibercaller_inner.VM)'
            '[.ACTIVEFIBER = (n_parent)][.FIBERCALLERS = [pfibercaller_outer]]',
            '$fiber_start_capture_result_valid(S_wait, n_capture, pfiberstart, false)',
            '$fiber_api_valid(S_wait, pfiberapi)', '$fiber_wait_valid(S_wait, pfiberapi)',
            '$fiber_vm_valid(S, pfibercaller_inner.VM, (n_parent), [pfibercaller_outer])',
            '$fiber_caller_api_trace(S_wait, pfiberapi) = [ptraceframe]',
            'ptraceframe.FUNCTION = $ptascii("start")',
            'ptraceframe.FILE = $call_sourcefile(S_wait.FILES, pfiberstart.SITE)',
            'ptraceframe.LINE = pfiberstart.LINE', *review.VALID,
            'pfiberapi_line = pfiberapi[.LINE = $(pfiberapi.LINE + 1)]',
            'pfiberstart_line = pfiberstart[.LINE = pfiberapi_line.LINE]',
            'pfibercaller_line = pfibercaller_inner[.API = pfiberapi_line]'
            '[.VM.TODO = (FIBER_WAIT pfiberapi_line) :: '
            '(FIBER_START_CAPTURE_RESULT n_capture pfiberstart_line false) :: ptask_saved*]',
            'S_line = S[.FIBERCALLERS = [pfibercaller_line, pfibercaller_outer]]',
            '$heap_graph(S_line) = H', '~$call_descriptors_valid(S_line)',
            'S_wait_line = $fiber_vm_restore(S_line, pfibercaller_line.VM)'
            '[.ACTIVEFIBER = (n_parent)][.FIBERCALLERS = [pfibercaller_outer]]',
            '~$fiber_api_valid(S_wait_line, pfiberapi_line)',
            'pfiberapi_receiver = pfiberapi[.OBJECT = n_parent]',
            'pfiberstart_receiver = pfiberstart[.OBJECT = n_parent]',
            'S_receiver = S_wait[.TODO = (FIBER_WAIT pfiberapi_receiver) :: '
            '(FIBER_START_CAPTURE_RESULT n_capture pfiberstart_receiver false) :: ptask_saved*]',
            '$heap_graph(S_receiver) = $heap_graph(S_wait)',
            '~$fiber_start_capture_result_valid(S_receiver, n_capture, pfiberstart_receiver, false)',
            '~$fiber_api_valid(S_receiver, pfiberapi_receiver)',
            '~$fiber_start_capture_result_valid(S_wait, n_capture, pfiberstart, true)',
            '~$fiber_api_valid(S_wait, pfiberapi[.SEQUENCE = S.FIBERSEQ])',
            'S_duplicate = S_wait[.TODO = (FIBER_WAIT pfiberapi) :: '
            '(FIBER_START_CAPTURE_RESULT n_capture pfiberstart false) :: '
            '(FIBER_START_CAPTURE_RESULT n_capture pfiberstart false) :: ptask_saved*]',
            '~$fiber_api_valid(S_duplicate, pfiberapi)',
            'S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
            'S_zero[.COMPLETION = NORMAL] = S',
            'S_step = $drive_steps(S, 1)', 'S_step.COMPLETION = BUDGET',
            'S_one = S_step[.COMPLETION = NORMAL]',
            'S_one.ACTIVEFIBER = (n_target)',
            'S_one.FIBERCALLERS = S.FIBERCALLERS',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
            'S_done = $drive(S_one, 4000)', *review.DONE,
            'S_done.EVENTS = [OUTPUT $ptascii("P|"), OUTPUT $ptascii("T"), '
            'OUTPUT $ptascii("V"), OUTPUT $ptascii("|"), OUTPUT $ptascii("C"), '
            'OUTPUT $ptascii("Y"), OUTPUT $ptascii("|"), OUTPUT $ptascii("1"), '
            'OUTPUT $ptascii("|"), OUTPUT $ptascii("1"), OUTPUT $ptascii("|"), '
            'OUTPUT $ptascii("17"), OUTPUT $ptascii("|"), OUTPUT $ptascii("19")]',
            '~((HOBJECT n_capture) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_target) <- S_done.ALLOCATIONS)',
        ],
    },
}

if __name__ == '__main__':
    review.ROOT = ROOT
    review.CASES = CASES
    review.__file__ = str(Path(__file__).resolve())
    passed = review.run(list(CASES))
    assert CATALOG.read_bytes() == SOURCE_BYTES, 'Bound start source catalog changed during run'
    raise SystemExit(0 if passed else 1)
