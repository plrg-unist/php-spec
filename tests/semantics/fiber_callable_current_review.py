#!/usr/bin/env python3
"""Collector destructor maker receipts after actual receiver retirement."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import fiber_state_review as review

CATALOG = Path(__file__).with_name('fiber_callable_cases.json')
SOURCE_BYTES = CATALOG.read_bytes()
SOURCE = next(row['source'] for row in json.loads(SOURCE_BYTES)
              if row['id'] == 'current-collector-destructor-scoped-private-static-cache')
CASE = 'collector-destructor-receipt-borrows-retired-receiver'
CASES = {CASE: {
    'source': SOURCE,
    'stage': ('S.TODO = (FIBER_ARGS pfiberstart) :: ptask_tail* '
              '-- if S.CURRENT = eps '
              '-- if pfiberstart.INDEX = 1 '
              '-- if $fiber_at(S, pfiberstart.OBJECT) = (pfiber) '
              '-- if pfiber.TARGET = (FIBER_METHOD_TARGET pfibercallable)'),
    'checks': [
        'n = pfiberstart.OBJECT', 'pfiber.STATUS = FIBER_INIT',
        'pfiber.READY', 'pfiber.GC = eps',
        'S.ACTIVEFIBER = eps', 'S.FIBERCALLERS = eps', 'S.FRAMES = eps',
        'papiquery = pfibercallable.QUERY',
        'papiquery.SOURCE = CONFIG_INVOKE pconfigcall',
        'pconfigcall.OWNER = (n)', 'pfiber.CALL = (pconfigcall)',
        'pfiber.RAW = PSTRING $ptascii("self::task")',
        'papiquery.VALUE = pfiber.RAW', 'pfibercallable.STATIC',
        'pfibercallable.NAME = $ptascii("task")',
        'pfiber.CAPTURE = (pmethodcapture)',
        'pfiber.PRODUCER = (pshutdownproducer)',
        'pfibercallable.CAPTURE = pfiber.CAPTURE',
        'pfibercallable.PRODUCER = pfiber.PRODUCER',
        'pshutdownproducer.INTERNAL', 'pshutdownproducer.SITE = eps',
        'pmethodcapture.CALLSITE = eps',
        'pshutdownproducer.TARGET = METHOD_TARGET n_receiver porigin_maker',
        'pmethodcapture.FUNCTION = porigin_maker',
        'S.OBJECTS[n_receiver] = INSTANCE porigin_class',
        'n_receiver <- S.DESTRUCTION.CALLED',
        '~((HOBJECT n_receiver) <- S.ALLOCATIONS)',
        'papiquery.THIS = (n_receiver)',
        'papiquery.CLASS.RECEIVER = (n_receiver)',
        '$heap_owners($heap_graph(S), HOBJECT n_receiver) = 0',
        '$target_nodes(FIBER_METHOD_TARGET pfibercallable) = eps',
        '$fiber_callback_nodes(pfiber) = eps',
        '$node_children(S, HOBJECT n) = eps',
        '$target_function(S, pshutdownproducer.TARGET) = eps',
        'S_history = $fiber_producer_view(S, pfiber.PRODUCER)',
        '$target_function(S_history, pshutdownproducer.TARGET) = (pfunction_maker)',
        'pfunction_maker.ORIGIN = porigin_maker',
        '$fiber_callable_this_valid(S, pfiber, papiquery)',
        '$fiber_callable_capture_valid(S, pfiber, pconfigcall)',
        '$fiber_callable_receipt_valid(S, pfibercallable)',
        '$fiber_cache_valid(S, n, pfiber)',
        'S.GC.WORKER = eps', '$gc_worker_state_valid(S)',
        'pshutdownproducer_bad = pshutdownproducer[.INTERNAL = false]',
        'pfibercallable_bad = pfibercallable[.PRODUCER = (pshutdownproducer_bad)]',
        'pfiber_bad = pfiber[.PRODUCER = (pshutdownproducer_bad)][.TARGET = (FIBER_METHOD_TARGET pfibercallable_bad)]',
        'S_bad = $fiber_put(S, n, pfiber_bad)',
        '$heap_graph(S_bad) = $heap_graph(S)',
        '~$fiber_producer_valid(S_bad, pfiber_bad)',
        '~$fiber_callable_receipt_valid(S_bad, pfibercallable_bad)',
        '~$call_descriptors_valid(S_bad)',
        'pfibercallable_line = pfibercallable[.QUERY = papiquery[.LINE = $(papiquery.LINE + 1)]]',
        'S_line = $fiber_put(S, n, pfiber[.TARGET = (FIBER_METHOD_TARGET pfibercallable_line)])',
        '$heap_graph(S_line) = $heap_graph(S)',
        '~$fiber_callable_receipt_valid(S_line, pfibercallable_line)',
        '~$call_descriptors_valid(S_line)',
        *review.VALID,
        'S_paused = $drive(S, 0)', 'S_paused.COMPLETION = BUDGET',
        'S_paused[.COMPLETION = NORMAL] = S',
        'S_one = $drive_steps(S, 1)', 'S_one.COMPLETION = BUDGET',
        'S_one.ACTIVEFIBER = (n)',
        'S_one.TODO = [FIBER_ENTER n pnamedargs, FIBER_FINISH n]',
        'pnamedargs.SLOTS = [NAMED_SENT (KNOWN (PSTRING $ptascii("17")))]',
        'pnamedargs.NAMED = eps', 'S_one.GC.WORKER = eps',
        '$fiber_enter_valid(S_one[.COMPLETION = NORMAL], n, pnamedargs)',
        '$call_descriptors_valid(S_one[.COMPLETION = NORMAL])',
        'S_done = $drive(S, 4000)', *review.DONE,
        'S_done.EVENTS = [OUTPUT $ptascii("G"), OUTPUT eps, OUTPUT $ptascii("|"), OUTPUT $ptascii("D"), OUTPUT eps, OUTPUT $ptascii("|"), OUTPUT $ptascii("C|"), OUTPUT $ptascii("1"), OUTPUT $ptascii("|"), OUTPUT $ptascii("T"), OUTPUT $ptascii("17"), OUTPUT $ptascii("|"), OUTPUT $ptascii("18")]',
        'S_done.OBJECTS[n] = FIBER pfiber_done',
        'pfiber_done.STATUS = FIBER_TERMINATED',
        'pfiber_done.RETURNED', 'pfiber_done.VALUE = PINT 18',
    ],
}}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    review.CASES = CASES
    review.__file__ = __file__
    assert set(args.case or []) <= CASES.keys()
    passed = all(review.run([name]) for name in args.case or [CASE])
    assert CATALOG.read_bytes() == SOURCE_BYTES, 'Fiber callable source catalog changed during run'
    raise SystemExit(0 if passed else 1)
