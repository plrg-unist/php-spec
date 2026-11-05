#!/usr/bin/env python3
"""Reach borrowed-cell capture, live reads, distinct cells and refusal roots."""
import argparse
import json
from pathlib import Path

import generator_call_unpack_state as base

CATALOG = Path(__file__).with_name('generator_reference_sink_review_cases.json')
SOURCES = {row['id']: row['source'] for row in json.loads(CATALOG.read_bytes())}
VALID = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']
CACHE = [
    'n_data = pgeneratorunpack.OBJECT',
    'S.OBJECTS[n_data] = GENERATOR pgenerator',
    'pgenerator.PHASE = GENERATOR_PAUSED', 'pgenerator.VALUE = eps',
    'pgenerator.REFCELL = (n_raw)', 'pgeneratorunpack.CELL = (n_raw)',
    'pgeneratorunpack.HOLD = KNOWN (PINT 11)',
    'pgeneratorunpack.KEY = (PINT 0)', 'pgeneratorunpack.INDEX = (0)',
    'pgenerator.KEY = (PINT 0)', 'pgenerator.INDEX = 0',
    '$generator_reference_producer(S, pgenerator)',
    '$generator_unpack_reference_source(S, pgeneratorunpack)',
    '$generator_unpack_capture_mode(S, pgeneratorunpack)',
    '$generator_unpack_reference_stage(S, pgeneratorunpack)',
    '$generator_unpack_warning_same(S, pgeneratorunpack)',
    '$heap_owners($heap_graph(S), HOBJECT n_data) = 2',
    '$task_nodes(GENERATOR_UNPACK pgeneratorunpack "byref") = '
    '[HOBJECT n_data] ++ $operand_nodes(pgeneratorunpack.INPUT) ++ '
    '$unpack_call_roots(pgeneratorunpack.CALL)',
]
FRESH = [
    'S_one.TODO = (GENERATOR_UNPACK pgeneratorunpack_next "next") :: ptask_tail*',
    'n_fresh = |S.STORE|', 'n_fresh =/= n_raw', 'n_fresh <- S_one.REFCELLS',
    'pgeneratorunpack_next.CALL.SENT = {SLOTS ([NAMED_SENT '
    '(REFERENCE n_fresh)]), NAMED eps}',
    'pgeneratorunpack_next.COUNT = 1', 'pgeneratorunpack_next.CELL = eps',
    'pgeneratorunpack_next.HOLD = KNOWN PNULL',
    'pgeneratorunpack_next.KEY = eps', 'pgeneratorunpack_next.INDEX = eps',
    'S_one.OBJECTS = S.OBJECTS', 'S_one.EVENTS = S.EVENTS',
    '$heap_owners($heap_graph(S_one), HCELL n_fresh) = 1',
    '$generator_unpack_valid(S_one, pgeneratorunpack_next, "next")',
    '~$generator_unpack_valid(S_one, pgeneratorunpack_next[.CELL = (n_raw)], "next")',
    '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
    '$drive_steps(S_zero[.COMPLETION = NORMAL], 1) = S_one_budget',
]
DONE = [
    'S_done = $drive(S_one, 4000)', 'S_done.COMPLETION = NORMAL',
    '$drive(S, 4000) = S_done', 'S_done.TODO = eps', 'S_done.FRAMES = eps',
    'S_done.CURRENT = eps', 'S_done.HELD = eps',
    '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    '$heap_owners($heap_graph(S_done), HOBJECT n_data) = 0',
    '$heap_owners($heap_graph(S_done), HCELL n_fresh) = 0',
]

CASES = {
    'warning-cursor-borrows-source-cell-without-extra-owner': {
        'source': SOURCES['retained-cell-alias-write'],
        'stage': 'S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail* '
                 '-- if perrorcall.RESUME = GENERATOR_UNPACK pgeneratorunpack "byref"',
        'checks': [*CACHE, 'S.STORE[n_raw] = DEFINED (PINT 11)',
                   '$lookup(S.ENV, $ptascii("v95")) = (n_raw)',
                   '$lookup(S.ENV, $ptascii("alias95")) = (n_raw)',
                   '$heap_owners($heap_graph(S), HCELL n_raw) = 4',
                   'perrorcall.LEVEL = 2', 'perrorcall.LINE = 5',
                   '$error_call_valid(S, perrorcall)',
                   '~$generator_unpack_capture_mode(S, pgeneratorunpack[.CELL = eps])',
                   '~$generator_unpack_capture_mode(S, pgeneratorunpack[.CELL = (|S.STORE|)])',
                   '~$generator_unpack_valid(S, pgeneratorunpack[.CELL = eps], "byref")',
                   '~$error_call_valid(S, perrorcall[.RESUME = GENERATOR_UNPACK '
                   'pgeneratorunpack[.CELL = (|S.STORE|)] "byref"])',
                   '~$error_call_valid(S, perrorcall[.MESSAGE = $ptascii("other")])',
                   *VALID, *ZERO, *ONE,
                   'S_one.TODO = (API_CALLBACK_SEND papiargcursor) :: ptask_tail*',
                   'papiargcursor.CALL = API_ERROR perrorcall',
                   'papiargcursor.INDEX = 0',
                   '$generator_unpack_count(S_one.TODO) = 1',
                   '$api_cursor_valid(S_one, papiargcursor)',
                   '$heap_owners($heap_graph(S_one), HCELL n_raw) = 4',
                   '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 2',
                   'S_one.STORE = S.STORE', 'S_one.OBJECTS = S.OBJECTS',
                   '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
                   '$drive_steps(S_zero[.COMPLETION = NORMAL], 1) = S_one_budget'],
    },
}
for name in ('retained-cell-alias-write', 'temporary-cell-alias-write'):
    CASES[name + '-rereads-old-cell-into-distinct-private-cell'] = {
        'source': SOURCES[name],
        'stage': 'S.TODO = (GENERATOR_UNPACK pgeneratorunpack "byref") :: ptask_tail*',
        'checks': [*CACHE, 'S.STORE[n_raw] = DEFINED (PINT 22)',
                   '$generator_unpack_reference_value(S, pgeneratorunpack) = (PINT 22)',
                   '$lookup(S.ENV, $ptascii("v95")) = (n_raw)',
                   '$lookup(S.ENV, $ptascii("alias95")) = (n_raw)',
                   '$heap_owners($heap_graph(S), HCELL n_raw) = 4',
                   *VALID, *ZERO, *ONE, *FRESH,
                   'S_one.STORE[n_fresh] = DEFINED (PINT 22)',
                   'S_one.STORE[n_raw] = DEFINED (PINT 22)',
                   '$heap_owners($heap_graph(S_one), HCELL n_raw) = 4',
                   *DONE, 'S_done.STORE[n_raw] = DEFINED (PINT 22)',
                   '$heap_owners($heap_graph(S_done), HCELL n_raw) = 2'],
    }

CASES['global-name-replacement-does-not-redirect-captured-cell'] = {
    'source': SOURCES['retained-global-source-name-replaced'],
    'stage': 'S.TODO = (GENERATOR_UNPACK pgeneratorunpack "byref") :: ptask_tail*',
    'checks': [*CACHE, '$lookup(S.ENV, $ptascii("v95")) = (n_new)',
               '$lookup(S.ENV, $ptascii("alias95")) = (n_raw)',
               'n_new =/= n_raw', 'S.STORE[n_new] = DEFINED (PINT 44)',
               'S.STORE[n_raw] = DEFINED (PINT 22)',
               'pgenerator.FRAME = (pframe_saved)',
               'pframe_saved.LOCALS = (psymboltable_saved)',
               '$lookup(psymboltable_saved.ENV, $ptascii("v95")) = (n_raw)',
               '$heap_owners($heap_graph(S), HCELL n_raw) = 3',
               *VALID, *ZERO, *ONE, *FRESH,
               'S_one.STORE[n_fresh] = DEFINED (PINT 22)',
               'S_one.STORE[n_new] = DEFINED (PINT 44)',
               '$heap_owners($heap_graph(S_one), HCELL n_raw) = 3',
               *DONE, 'S_done.STORE[n_raw] = DEFINED (PINT 22)',
               'S_done.STORE[n_new] = DEFINED (PINT 44)',
               '$heap_owners($heap_graph(S_done), HCELL n_raw) = 1'],
}
CASES['handler-null-write-replaces-initial-integer-at-delivery'] = {
    'source': SOURCES['live-nonowning-type-matrix'],
    'stage': 'S.TODO = (GENERATOR_UNPACK pgeneratorunpack "byref") :: ptask_tail* '
             '-- if pgeneratorunpack.CELL = (n_raw) '
             '-- if S.STORE[n_raw] = DEFINED PNULL',
    'checks': [*CACHE, '$generator_unpack_reference_value(S, pgeneratorunpack) = (PNULL)',
               *VALID, *ZERO, *ONE, *FRESH,
               'S_one.STORE[n_fresh] = DEFINED PNULL',
               'S_one.STORE[n_raw] = DEFINED PNULL', *DONE],
}
CASES['replacement-cache-cell-delivers-old-value-with-equal-key-index'] = {
    'source': SOURCES['same-key-index-value-replacement-cell'],
    'stage': 'S.TODO = (GENERATOR_UNPACK pgeneratorunpack "byref") :: ptask_tail*',
    'checks': ['n_data = pgeneratorunpack.OBJECT',
               'S.OBJECTS[n_data] = GENERATOR pgenerator',
               'pgeneratorunpack.CELL = (n_raw)', 'pgenerator.REFCELL = (n_cache)',
               'n_raw =/= n_cache', 'pgeneratorunpack.HOLD = KNOWN (PINT 11)',
               'pgeneratorunpack.KEY = (PINT 0)', 'pgeneratorunpack.INDEX = (0)',
               'pgenerator.KEY = (PINT 0)', 'pgenerator.INDEX = 0',
               'S.STORE[n_raw] = DEFINED (PINT 22)',
               'S.STORE[n_cache] = DEFINED (PINT 11)',
               '$generator_unpack_capture_mode(S, pgeneratorunpack)',
               '$generator_unpack_reference_stage(S, pgeneratorunpack)',
               '~$generator_unpack_warning_same(S, pgeneratorunpack)',
               '$heap_owners($heap_graph(S), HCELL n_raw) = 3',
               '$heap_owners($heap_graph(S), HCELL n_cache) = 3',
               '$generator_unpack_reference_delivery(S, pgeneratorunpack) = (PINT 22)',
               *VALID, *ZERO, *ONE, *FRESH,
               'n_fresh =/= n_cache',
               'S_one.STORE[n_fresh] = DEFINED (PINT 22)',
               '$heap_owners($heap_graph(S_one), HCELL n_raw) = 3',
               '$heap_owners($heap_graph(S_one), HCELL n_cache) = 3',
               *DONE, 'S_done.STORE[n_cache] = DEFINED (PINT 11)',
               '$heap_owners($heap_graph(S_done), HCELL n_raw) = 2',
               '$heap_owners($heap_graph(S_done), HCELL n_cache) = 1'],
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    base.CASES = CASES
    base.INPUTS = [Path(__file__), CATALOG, Path(base.__file__)]
    raise SystemExit(0 if base.run(parser.parse_args().case) else 1)
