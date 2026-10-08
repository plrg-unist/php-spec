#!/usr/bin/env python3
"""C-root bound API authentication through the cached collector's real caller."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('fiber_bound_core_cases.json')
SOURCE_BYTES = CATALOG.read_bytes()
SOURCE = next(row['source'] for row in json.loads(SOURCE_BYTES)
              if row['id'] == 'author-bound-core-idle-collector-transfer')

CASES = {
    'bound-core-collector-restores-runner-and-real-outer-caller': {
        'source': SOURCE,
        'stage': ('S.TODO = [GC_WORKER_PUBLIC pfiberapi] '
                  '-- if pfiberapi.KIND = (INTRINSIC_FIBER_RESUME) '
                  '-- if S.FIBERCALLERS = [pfibercaller_inner, pfibercaller_outer] '
                  '-- if pfibercaller_inner.VM.TODO = [FIBER_WAIT pfiberapi, '
                  'FIBER_API_CORE_RESULT n_runner n_capture pconfigcall, FIBER_FINISH n_runner]'),
        'checks': [
            'S.ACTIVEFIBER = (pfiberapi.OBJECT)', 'S.GC.WORKER = S.ACTIVEFIBER',
            'S.GC.ACTIVE = eps', 'S.GC.PLAN = eps',
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ORIGIN = eps',
            'pfiberapi.START = eps', 'pfiberapi.SENT = (PINT 123)',
            'pfibercaller_inner.OBJECT = pfiberapi.OBJECT',
            'pfibercaller_inner.API = pfiberapi',
            'pfibercaller_inner.PREVIOUS = (n_runner)',
            'pfibercaller_outer.OBJECT = n_runner',
            'pfibercaller_outer.PREVIOUS = eps',
            'pfibercaller_outer.API.KIND = eps',
            'pfibercaller_outer.API.START = (pnamedargs)',
            'pnamedargs.SLOTS = [NAMED_SENT (KNOWN (PINT 123))]',
            'pconfigcall.KIND = INTRINSIC_FIBER_RESUME',
            'pconfigcall.OWNER = (pfiberapi.OBJECT)',
            'pconfigcall.SELECTION = (n_capture)',
            'pconfigcall.SENT = [NAMED_SENT (KNOWN (PINT 123))]',
            '$fiber_at(S, n_runner) = (pfiber_runner)',
            'pfiber_runner.STATUS = FIBER_RUNNING', 'pfiber_runner.VM = eps',
            'pfiber_runner.RAW = POBJECT n_capture',
            'pfiber_runner.TARGET = (FIBER_API_TARGET n_capture)',
            'S.OBJECTS[n_capture] = FIBERAPICLOSURE pfibercapture',
            'pfibercapture.INPUT = (pfiberapi.OBJECT)',
            '$fiber_core_binding(S, pfiber_runner) = (pconfigcall.OWNER, pconfigcall.SELECTION)',
            '$node_children(S, HOBJECT n_capture) = [HOBJECT pfiberapi.OBJECT]',
            '$task_nodes(GC_WORKER_PUBLIC pfiberapi) = eps',
            '$task_nodes(FIBER_API_CORE_RESULT n_runner n_capture pconfigcall) = [HOBJECT n_capture]',
            '$fiber_caller_api_nodes(pfibercaller_inner) = eps',
            '$heap_owners($heap_graph(S), HOBJECT pfiberapi.OBJECT) = 4',
            '$heap_owners($heap_graph(S), HOBJECT n_capture) = 2',
            '$heap_owners($heap_graph(S), HOBJECT n_runner) = 2',
            'S_caller = $fiber_vm_restore(S, pfibercaller_inner.VM)'
            '[.ACTIVEFIBER = (n_runner)][.FIBERCALLERS = [pfibercaller_outer]]',
            '$fiber_bound_core_call(S_caller, pfiberapi) = (pconfigcall)',
            '$fiber_api_core_result_valid(S_caller, n_runner, n_capture, pconfigcall)',
            '$fiber_api_valid(S, pfiberapi)', '$gc_worker_public_valid(S, pfiberapi)',
            '$gc_state_valid(S)', *review.VALID,
            'pfiberapi_line = pfiberapi[.LINE = $(pfiberapi.LINE + 1)]',
            'pconfigcall_line = pconfigcall[.LINE = pfiberapi_line.LINE]',
            'S_line = S[.TODO = [GC_WORKER_PUBLIC pfiberapi_line]]'
            '[.FIBERCALLERS = [pfibercaller_inner[.API = pfiberapi_line]'
            '[.VM.TODO = [FIBER_WAIT pfiberapi_line, '
            'FIBER_API_CORE_RESULT n_runner n_capture pconfigcall_line, '
            'FIBER_FINISH n_runner]], pfibercaller_outer]]',
            '$heap_graph(S_line) = $heap_graph(S)',
            '~$fiber_api_valid(S_line, pfiberapi_line)',
            '~$gc_worker_public_valid(S_line, pfiberapi_line)',
            '~$call_descriptors_valid(S_line)',
            'S_previous = S[.FIBERCALLERS = '
            '[pfibercaller_inner[.PREVIOUS = eps], pfibercaller_outer]]',
            '$heap_graph(S_previous) = $heap_graph(S)',
            '~$fiber_api_valid(S_previous, pfiberapi)',
            '~$gc_worker_public_valid(S_previous, pfiberapi)',
            '~$fiber_api_valid(S[.FIBERCALLERS = eps], pfiberapi)',
            'S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
            'S_zero[.COMPLETION = NORMAL] = S',
            'S_step = $drive_steps(S, 1)', 'S_step.COMPLETION = BUDGET',
            'S_one = S_step[.COMPLETION = NORMAL]',
            'S_one.ACTIVEFIBER = (n_runner)',
            'S_one.FIBERCALLERS = [pfibercaller_outer]',
            'S_one.TODO = [FIBER_API_CORE_RESULT n_runner n_capture pconfigcall, FIBER_FINISH n_runner]',
            'S_one.GC.WORKER = (pfiberapi.OBJECT)',
            '$fiber_at(S_one, pfiberapi.OBJECT) = (pfiber_idle)',
            'pfiber_idle.STATUS = FIBER_SUSPENDED',
            '$heap_owners($heap_graph(S_one), HOBJECT n_capture) = 2',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
            'S_done = $drive(S_one, 4000)', *review.DONE,
            'S_done.EVENTS = [OUTPUT $ptascii("D|"), OUTPUT $ptascii("1"), '
            'OUTPUT $ptascii("|"), OUTPUT $ptascii("1"), OUTPUT $ptascii("|"), '
            'OUTPUT $ptascii("idle"), OUTPUT $ptascii("|"), '
            'OUTPUT $ptascii("1"), OUTPUT $ptascii("|"), OUTPUT $ptascii("END")]',
            'S_done.GC.WORKER = eps',
            '~((HOBJECT pfiberapi.OBJECT) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_capture) <- S_done.ALLOCATIONS)',
        ],
    },
}

if __name__ == '__main__':
    review.ROOT = ROOT
    review.CASES = CASES
    review.__file__ = str(Path(__file__).resolve())
    passed = review.run(list(CASES))
    assert CATALOG.read_bytes() == SOURCE_BYTES, 'Bound C-root source catalog changed during run'
    raise SystemExit(0 if passed else 1)
