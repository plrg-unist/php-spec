"""Source-reached C result lifetime and before-handler name priority."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

SOURCES = {row['id']: row['source'] for row in json.loads(
    Path(__file__).with_name('fiber_review_cases.json').read_text())}
VALID = review.VALID
DONE = review.DONE
PAUSE = ['S_paused = $drive(S, 0)', 'S_paused.COMPLETION = BUDGET',
         'S_paused[.COMPLETION = NORMAL] = S',
         'S_done = $drive(S, 4000)',
         '$drive(S_paused[.COMPLETION = NORMAL], 4000) = S_done']

CASES = {
    'defined-c-result-precedes-fiber-result-store': {
        'source': SOURCES['review-fiber-core-reporting-query-null-casefold'],
        'stage': 'S.TODO = [FIBER_CORE_RESULT n pconfigcall, FIBER_FINISH n] -- if S.RESULT = KNOWN (PINT 9)',
        'checks': [
            'S.ACTIVEFIBER = (n)', '$fiber_at(S, n) = (pfiber)',
            'pfiber.TARGET = (FIBER_REPORTING_TARGET)',
            'pfiber.STATUS = FIBER_RUNNING', 'pfiber.ENTRY = ({SLOTS eps, NAMED eps})',
            '~pfiber.RETURNED', 'pfiber.VALUE = PNULL', 'pfiber.FINISH = eps',
            'S.CURRENT = eps', 'S.FRAMES = eps', 'S.ORIGIN = (pconfigcall.SITE)',
            'S.FIBERCALLERS = [pfibercaller]',
            'pfibercaller.API.KIND = eps', 'pfibercaller.API.START = ({SLOTS eps, NAMED eps})',
            'pconfigcall.SENT = eps', '~pconfigcall.NAMED',
            'pconfigcall.OWNER = eps', 'pconfigcall.SELECTION = eps', 'pconfigcall.PACKS = eps',
            '$heap_owners($heap_graph(S), HOBJECT n) = 2',
            '$task_nodes(FIBER_CORE_RESULT n pconfigcall) = eps',
            '$fiber_core_result_valid(S, n, pconfigcall)',
            '$fiber_core_count(S.TODO) = 1',
            'pconfigcall_bad = pconfigcall[.LINE = 0]',
            'S_bad = S[.TODO = [FIBER_CORE_RESULT n pconfigcall_bad, FIBER_FINISH n]]',
            '$heap_graph(S_bad) = $heap_graph(S)',
            '~$call_task_valid(S_bad, FIBER_CORE_RESULT n pconfigcall_bad)',
            '~$call_descriptors_valid(S_bad)',
            'S_duplicate = S[.TODO = [FIBER_CORE_RESULT n pconfigcall, FIBER_CORE_RESULT n pconfigcall, FIBER_FINISH n]]',
            '$heap_graph(S_duplicate) = $heap_graph(S)',
            '~$fiber_core_result_valid(S_duplicate, n, pconfigcall)',
            '~$call_descriptors_valid(S_duplicate)',
            *VALID,
            'S_one = $drive_steps(S, 1)', 'S_one.COMPLETION = BUDGET',
            'S_one.TODO = [FIBER_FINISH n]', 'S_one.ORIGIN = eps',
            'S_one.RESULT = KNOWN (PINT 9)',
            'S_one.OBJECTS = S.OBJECTS', 'S_one.FIBERCALLERS = S.FIBERCALLERS',
            '$call_descriptors_valid(S_one[.COMPLETION = NORMAL])',
            *PAUSE, *DONE,
            'S_done.OBJECTS[n] = FIBER pfiber_done',
            '~((HOBJECT n) <- S_done.ALLOCATIONS)',
            'pfiber_done.STATUS = FIBER_TERMINATED', 'pfiber_done.RETURNED',
            '~pfiber_done.FAILED', 'pfiber_done.VALUE = PINT 9',
            'pfiber_done.RAW = PNULL', 'pfiber_done.TARGET = eps',
            'pfiber_done.ENTRY = eps', 'pfiber_done.FINISH = eps',
            'S_done.REPORTING = 9', 'S_done.REPORTINGINI = $ptascii("9")',
        ],
    },
    'unknown-name-fails-before-entered-c-arity-and-type': {
        'source': SOURCES['review-fiber-core-reporting-unknown-name-before-arity-and-type'],
        'stage': 'S.TODO = [FIBER_ENTER n pnamedargs, FIBER_FINISH n] -- if $fiber_at(S, n) = (pfiber) -- if pfiber.TARGET = (FIBER_REPORTING_TARGET)',
        'checks': [
            'S.ACTIVEFIBER = (n)', 'S.ORIGIN = eps',
            'S.CURRENT = eps', 'S.FRAMES = eps',
            'pfiber.ENTRY = (pnamedargs)', '~pfiber.RETURNED',
            'pnamedargs.SLOTS = [NAMED_SENT (KNOWN (PARRAY n_array)), NAMED_SENT (KNOWN (PINT 7))]',
            'pnamedargs.NAMED = [($ptascii("unknown"), KNOWN (PINT 8))]',
            'S.FIBERCALLERS = [pfibercaller]',
            'pfibercaller.API.START = (pnamedargs)', 'pfibercaller.API.KIND = eps',
            '$fiber_enter_valid(S, n, pnamedargs)',
            '$fiber_core_count(S.TODO) = 0',
            '$fiber_core_name_error(INTRINSIC_ERROR_REPORTING, pnamedargs.SLOTS, pnamedargs.NAMED) = ($ptascii("Unknown named parameter $unknown"))',
            'pconfigcall_forged = {SITE pfibercaller.API.SITE, KIND INTRINSIC_ERROR_REPORTING, INDEX 2, SENT pnamedargs.SLOTS, NAMED false, OWNER eps, SELECTION eps, LINE pfibercaller.API.LINE, PACKS eps}',
            'S_forged = S[.TODO = [FIBER_CORE_RESULT n pconfigcall_forged, FIBER_FINISH n]][.ORIGIN = (pconfigcall_forged.SITE)]',
            '$heap_graph(S_forged) = $heap_graph(S)',
            '~$fiber_core_result_valid(S_forged, n, pconfigcall_forged)',
            '~$call_descriptors_valid(S_forged)',
            *VALID,
            'S_one = $drive_steps(S, 1)', 'S_one.COMPLETION = BUDGET',
            'S_one.TODO = [THROW_SEARCH n_error, FIBER_FINISH n]',
            '$throwable_member(S_one, n_error)',
            '$throwable_field(S_one, n_error, "message") = PSTRING $ptascii("Unknown named parameter $unknown")',
            '$throwable_field(S_one, n_error, "line") = PINT pfibercaller.API.LINE',
            '$throwable_field(S_one, n_error, "trace") = PARRAY n_trace',
            'S_one.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_frame))]',
            '$entry_lookup(S_one.ARRAYS[n_frame].ITEMS, KSTRING $ptascii("function")) = (DIRECT (PSTRING $ptascii("start")))',
            '$entry_lookup(S_one.ARRAYS[n_frame].ITEMS, KSTRING $ptascii("class")) = (DIRECT (PSTRING $ptascii("Fiber")))',
            '$fiber_core_count(S_one.TODO) = 0',
            'S_one.REPORTING = 30719', 'S_one.REPORTINGINI = S.REPORTINGINI',
            '$call_descriptors_valid(S_one[.COMPLETION = NORMAL])',
            *PAUSE, *DONE,
        ],
    },
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', default=[])
    args = parser.parse_args()
    assert not args.case or set(args.case) <= CASES.keys(), 'unknown core Fiber case'
    review.CASES = CASES
    review.__file__ = str(Path(__file__).resolve())
    selected = args.case or list(CASES)
    raise SystemExit(0 if all(review.run([name]) for name in selected) else 1)
