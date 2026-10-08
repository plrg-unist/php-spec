#!/usr/bin/env python3
"""Bound API capture ownership across the collector's authentic C-loop transfer."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('fiber_bound_api_cases.json')
SOURCE_BYTES = CATALOG.read_bytes()
SOURCE = next(row['source'] for row in json.loads(SOURCE_BYTES)
              if row['id'] == 'peer-bound-idle-collector-calls')

CASES = {
    'bound-collector-throw-authenticates-saved-invoke-owner': {
        'source': SOURCE,
        'stage': ('S.TODO = [GC_WORKER_PUBLIC pfiberapi] '
                  '-- if pfiberapi.KIND = (INTRINSIC_FIBER_THROW) '
                  '-- if S.FIBERCALLERS = [pfibercaller] '
                  '-- if pfibercaller.VM.TODO = (FIBER_WAIT pfiberapi) :: '
                  '(FIBER_CAPTURE_RESULT n_capture pconfigcall true) :: ptask_tail*'),
        'checks': [
            'S.ACTIVEFIBER = (pfiberapi.OBJECT)', 'S.GC.WORKER = S.ACTIVEFIBER',
            'S.GC.ACTIVE = eps', 'S.GC.PLAN = eps', 'S.GC.NEXT = 1',
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ORIGIN = eps',
            'S.RESULT = KNOWN PNULL', 'S.BASE = BASE_VALUE (KNOWN PNULL)',
            'pfibercaller.OBJECT = pfiberapi.OBJECT', 'pfibercaller.API = pfiberapi',
            'pfibercaller.PREVIOUS = eps', 'pfibercaller.VM.GLOBAL',
            'pfibercaller.VM.CURRENT = eps', 'pfibercaller.VM.FRAMES = eps',
            'pfiberapi.START = eps', 'pfiberapi.SENT = (POBJECT n_error)',
            'pconfigcall.KIND = INTRINSIC_FIBER_THROW',
            'pconfigcall.OWNER = (pfiberapi.OBJECT)', 'pconfigcall.SELECTION = (n_capture)',
            'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_error))]',
            'S.OBJECTS[n_capture] = FIBERAPICLOSURE pfibercapture',
            'pfibercapture.KIND = INTRINSIC_FIBER_THROW',
            'pfibercapture.INPUT = (pfiberapi.OBJECT)', '$fiber_capture_live(S, n_capture)',
            '$node_children(S, HOBJECT n_capture) = [HOBJECT pfiberapi.OBJECT]',
            '$fiber_at(S, pfiberapi.OBJECT) = (pfiber)',
            'pfiber.GC = (pgcworker)', 'pgcworker.GUARD = eps',
            'pfiber.STATUS = FIBER_RUNNING', 'pfiber.VM = eps',
            'pfiber.SEQUENCE = pfiberapi.SEQUENCE',
            '$gc_worker_cache_valid(S, pfiberapi.OBJECT, pfiber)',
            '$throwable_member(S, n_error)',
            '$task_nodes(GC_WORKER_PUBLIC pfiberapi) = [HOBJECT n_error]',
            '$fiber_caller_api_nodes(pfibercaller) = [HOBJECT n_error]',
            '$task_nodes(FIBER_CAPTURE_RESULT n_capture pconfigcall true) = '
            '[HOBJECT n_capture, HOBJECT n_capture, HOBJECT n_error]',
            '$heap_count(HOBJECT pfiberapi.OBJECT, $fiber_caller_api_nodes(pfibercaller)) = 0',
            '$heap_count(HOBJECT n_error, $fiber_vm_nodes(pfibercaller.VM)) = 1',
            '$heap_owners($heap_graph(S), HOBJECT pfiberapi.OBJECT) = 4',
            '$heap_owners($heap_graph(S), HOBJECT n_capture) = 3',
            '$heap_owners($heap_graph(S), HOBJECT n_error) = 3',
            'S_caller = $fiber_vm_restore(S, pfibercaller.VM)[.ACTIVEFIBER = eps][.FIBERCALLERS = eps]',
            '$fiber_capture_result_valid(S_caller, n_capture, pconfigcall, true)',
            '$fiber_api_valid(S_caller, pfiberapi)', '$fiber_wait_valid(S_caller, pfiberapi)',
            '$fiber_api_valid(S, pfiberapi)', '$gc_worker_public_valid(S, pfiberapi)',
            '$fiber_caller_wait(S, pfibercaller)', '$gc_state_valid(S)', *review.VALID,
            'pfiberapi_line = pfiberapi[.LINE = $(pfiberapi.LINE + 1)]',
            'pconfigcall_line = pconfigcall[.LINE = pfiberapi_line.LINE]',
            'S_line = S[.TODO = [GC_WORKER_PUBLIC pfiberapi_line]]'
            '[.FIBERCALLERS = [pfibercaller[.API = pfiberapi_line]'
            '[.VM.TODO = (FIBER_WAIT pfiberapi_line) :: '
            '(FIBER_CAPTURE_RESULT n_capture pconfigcall_line true) :: ptask_tail*]]]',
            '$heap_graph(S_line) = $heap_graph(S)',
            '~$fiber_api_valid(S_line, pfiberapi_line)',
            '~$gc_worker_public_valid(S_line, pfiberapi_line)',
            '~$call_descriptors_valid(S_line)',
            'S_object = S[.FIBERCALLERS = [pfibercaller[.OBJECT = n_capture]]]',
            '$heap_graph(S_object) = $heap_graph(S)',
            '~$fiber_api_valid(S_object, pfiberapi)',
            '~$gc_worker_public_valid(S_object, pfiberapi)',
            'S_tail = S[.FIBERCALLERS = [pfibercaller[.VM.TODO = '
            '(FIBER_WAIT pfiberapi) :: ptask_tail*]]]',
            '~$fiber_api_valid(S_tail, pfiberapi)',
            '~$gc_worker_public_valid(S_tail, pfiberapi)',
            'S_extra = S[.TODO = [GC_WORKER_PUBLIC pfiberapi, GC_WORKER_IDLE pfiberapi.OBJECT]]',
            '$heap_graph(S_extra) = $heap_graph(S)',
            '~$fiber_api_valid(S_extra, pfiberapi)',
            '~$gc_worker_public_valid(S_extra, pfiberapi)',
            '~$call_descriptors_valid(S_extra)',
            '~$fiber_api_valid(S[.FIBERCALLERS = eps], pfiberapi)',
            '~$gc_worker_public_valid(S[.ACTIVEFIBER = eps], pfiberapi)',
            'S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
            'S_zero[.COMPLETION = NORMAL] = S',
            'S_step = $drive_steps(S, 1)', 'S_step.COMPLETION = BUDGET',
            'S_one = S_step[.COMPLETION = NORMAL]',
            'S_one.ACTIVEFIBER = eps', 'S_one.FIBERCALLERS = eps',
            'S_one.GC.WORKER = (pfiberapi.OBJECT)',
            '$fiber_at(S_one, pfiberapi.OBJECT) = (pfiber_idle)',
            'pfiber_idle.STATUS = FIBER_SUSPENDED', 'pfiber_idle.VM = (pfibervm_idle)',
            'pfibervm_idle.TODO = [GC_WORKER_IDLE pfiberapi.OBJECT]',
            '$fiber_saved_nodes(pfiber_idle.VM) = eps',
            'S_one.TODO = (THROW_SEARCH n_error) :: '
            '(FIBER_CAPTURE_RESULT n_capture pconfigcall true) :: ptask_tail*',
            '$fiber_capture_result_valid(S_one, n_capture, pconfigcall, true)',
            '$heap_owners($heap_graph(S_one), HOBJECT n_error) = 2',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
            'S_done = $drive(S_one, 4000)', *review.DONE,
            'S_done.EVENTS = [OUTPUT $ptascii("D|"), OUTPUT $ptascii("1"), '
            'OUTPUT $ptascii("|"), OUTPUT $ptascii("1"), OUTPUT $ptascii("|"), '
            'OUTPUT $ptascii("idle"), OUTPUT $ptascii("|"), '
            'OUTPUT $ptascii("1"), OUTPUT $ptascii("|"), OUTPUT $ptascii("END")]',
            'S_done.GC.WORKER = (pfiberapi.OBJECT)',
            '$heap_owners($heap_graph(S_done), HOBJECT pfiberapi.OBJECT) = 1',
            '~((HOBJECT n_capture) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_error) <- S_done.ALLOCATIONS)',
        ],
    },
}

if __name__ == '__main__':
    review.ROOT = ROOT
    review.CASES = CASES
    review.__file__ = str(Path(__file__).resolve())
    passed = review.run(list(CASES))
    assert CATALOG.read_bytes() == SOURCE_BYTES, 'Bound Fiber source catalog changed during run'
    raise SystemExit(0 if passed else 1)
