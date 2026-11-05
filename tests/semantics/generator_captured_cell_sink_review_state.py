#!/usr/bin/env python3
"""Reach saved-cell delivery through changed Generator caches and phases."""
import argparse
import json
from pathlib import Path

import generator_call_unpack_state as base

CATALOG = Path(__file__).with_name('generator_captured_cell_sink_review_cases.json')
SOURCES = {row['id']: row['source'] for row in json.loads(CATALOG.read_bytes())}
VALID = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']
CAPTURE = [
    'n_data = pgeneratorunpack.OBJECT',
    'S.OBJECTS[n_data] = GENERATOR pgenerator',
    'pgeneratorunpack.CELL = (n_raw)',
    'pgeneratorunpack.HOLD = KNOWN (PINT 11)',
    'pgeneratorunpack.KEY = (PINT 0)', 'pgeneratorunpack.INDEX = (0)',
    'S.STORE[n_raw] = DEFINED (PINT 22)',
    '$ordinary_reference_value(S, n_raw) = (PINT 22)',
    '$generator_unpack_reference_source(S, pgeneratorunpack)',
    '$generator_unpack_capture_mode(S, pgeneratorunpack)',
    '$generator_unpack_reference_stage(S, pgeneratorunpack)',
    '$generator_unpack_reference_delivery(S, pgeneratorunpack) = (PINT 22)',
    '~$generator_unpack_warning_same(S, pgeneratorunpack)',
    '$generator_unpack_valid(S, pgeneratorunpack, "byref")',
    '$task_nodes(GENERATOR_UNPACK pgeneratorunpack "byref") = '
    '[HOBJECT n_data] ++ $operand_nodes(pgeneratorunpack.INPUT) ++ '
    '$unpack_call_roots(pgeneratorunpack.CALL)',
]
FRESH = [
    'S_one.TODO = (GENERATOR_UNPACK pgeneratorunpack_next "next") :: ptask_tail*',
    'n_fresh = |S.STORE|', 'n_fresh =/= n_raw',
    'S_one.STORE[n_fresh] = DEFINED (PINT 22)',
    'S_one.STORE[n_raw] = DEFINED (PINT 22)',
    'n_fresh <- S_one.REFCELLS',
    'pgeneratorunpack_next.CALL.SENT = {SLOTS ([NAMED_SENT '
    '(REFERENCE n_fresh)]), NAMED eps}',
    'pgeneratorunpack_next.COUNT = 1',
    'pgeneratorunpack_next.CELL = eps',
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
    '$drive(S, 4000) = S_done', 'S_done.TODO = eps',
    'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
    '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    '$heap_owners($heap_graph(S_done), HOBJECT n_data) = 0',
    '$heap_owners($heap_graph(S_done), HCELL n_fresh) = 0',
    'S_done.STORE[n_raw] = DEFINED (PINT 22)',
    '$heap_owners($heap_graph(S_done), HCELL n_raw) = 2',
]

CASES = {
    'replacement-cache-delivers-old-cell-without-phantom-owner': {
        'source': SOURCES['same-key-index-value-replacement-cell'],
        'stage': 'S.TODO = (GENERATOR_UNPACK pgeneratorunpack "byref") :: ptask_tail*',
        'checks': [*CAPTURE,
                   'pgenerator.PHASE = GENERATOR_PAUSED',
                   'pgenerator.KEY = (PINT 0)', 'pgenerator.INDEX = 0',
                   'pgenerator.REFCELL = (n_cache)', 'n_raw =/= n_cache',
                   'S.STORE[n_cache] = DEFINED (PINT 11)',
                   '$generator_unpack_reference_value(S, pgeneratorunpack) = (PINT 11)',
                   '$heap_owners($heap_graph(S), HCELL n_raw) = 3',
                   '$heap_owners($heap_graph(S), HCELL n_cache) = 3',
                   '$heap_owners($heap_graph(S), HOBJECT n_data) = 2',
                   '$generator_unpack_reference_delivery(S[.ALLOCATIONS = eps], pgeneratorunpack) = eps',
                   '$generator_unpack_reference_delivery(S[.REFCELLS = eps], pgeneratorunpack) = eps',
                   '$generator_unpack_reference_delivery(S[.LITERALREFDEBTS = n_raw :: S.LITERALREFDEBTS], pgeneratorunpack) = eps',
                   '$generator_unpack_reference_delivery(S[.STORE[n_raw] = UNDEFINED], pgeneratorunpack) = eps',
                   '$generator_unpack_reference_delivery(S[.STORE[n_raw] = DEFINED (POBJECT n_data)], pgeneratorunpack) = eps',
                   '~$generator_unpack_valid(S, pgeneratorunpack[.CELL = (|S.STORE|)], "byref")',
                   '~$generator_unpack_valid(S, pgeneratorunpack[.CELL = eps], "byref")',
                   *VALID, *ZERO, *ONE, *FRESH,
                   'n_fresh =/= n_cache',
                   '$heap_owners($heap_graph(S_one), HCELL n_raw) = 3',
                   '$heap_owners($heap_graph(S_one), HCELL n_cache) = 3',
                   *DONE, 'S_done.STORE[n_cache] = DEFINED (PINT 11)',
                   '$heap_owners($heap_graph(S_done), HCELL n_cache) = 1'],
    },
    'changed-key-and-largest-index-do-not-redirect-prechecked-send': {
        'source': SOURCES['same-cell-new-key-and-largest-index'],
        'stage': 'S.TODO = (GENERATOR_UNPACK pgeneratorunpack "byref") :: ptask_tail*',
        'checks': [*CAPTURE,
                   'pgenerator.PHASE = GENERATOR_PAUSED',
                   'pgenerator.KEY = (PINT 100)', 'pgenerator.INDEX = 100',
                   'pgenerator.REFCELL = (n_raw)',
                   '$heap_owners($heap_graph(S), HCELL n_raw) = 4',
                   *VALID, *ZERO, *ONE, *FRESH,
                   '$heap_owners($heap_graph(S_one), HCELL n_raw) = 4',
                   *DONE],
    },
    'closed-producer-still-delivers-live-captured-cell': {
        'source': SOURCES['closed-generator-live-captured-cell'],
        'stage': 'S.TODO = (GENERATOR_UNPACK pgeneratorunpack "byref") :: ptask_tail*',
        'checks': [*CAPTURE,
                   'pgenerator.PHASE = GENERATOR_CLOSED',
                   'pgenerator.FRAME = eps', 'pgenerator.REFCELL = eps',
                   'pgenerator.KEY = eps', 'pgenerator.VALUE = eps',
                   '$generator_unpack_reference_value(S, pgeneratorunpack) = eps',
                   '$heap_owners($heap_graph(S), HCELL n_raw) = 2',
                   *VALID, *ZERO, *ONE, *FRESH,
                   '$heap_owners($heap_graph(S_one), HCELL n_raw) = 2',
                   *DONE],
    },
    'used-yield-keeps-saved-source-cell-and-normal-next-continuation': {
        'source': SOURCES['callback-reaches-used-yield'],
        'stage': 'S.TODO = (ERROR_HANDLER_CLEAN perrorcall) :: ptask_tail* '
                 '-- if perrorcall.RESUME = GENERATOR_UNPACK pgeneratorunpack "byref" '
                 '-- if S.DESTRUCTION.CLEANUPS = pdestructioncleanup :: pdestructioncleanup_tail* '
                 '-- if pdestructioncleanup.RELEASED',
        'checks': [*CAPTURE,
                   'pgenerator.PHASE = GENERATOR_PAUSED',
                   'pgenerator.KEY = (PINT 100)', 'pgenerator.INDEX = 100',
                   'pgenerator.PARKED = eps',
                   'pgenerator.REFCELL = (n_raw)',
                   '$generator_unpack_warning_hold(S, pgeneratorunpack) = '
                   '(pgeneratorunpack[.HOLD = KNOWN (PINT 22)][.KEY = (PINT 100)][.INDEX = (100)])',
                   '$error_call_valid(S, perrorcall)',
                   '~$error_call_valid(S, perrorcall[.MESSAGE = $ptascii("other")])',
                   '$heap_owners($heap_graph(S), HCELL n_raw) = 4',
                   *VALID, *ZERO, *ONE,
                   'S_one.TODO = (GENERATOR_UNPACK pgeneratorunpack "byref") :: ptask_tail*',
                   'S_one.STORE = S.STORE', 'S_one.OBJECTS = S.OBJECTS',
                   'S_one.EVENTS = S.EVENTS',
                   '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
                   '$drive_steps(S_zero[.COMPLETION = NORMAL], 1) = S_one_budget',
                   'S_fresh_budget = $drive_steps(S_one, 1)',
                   'S_fresh_budget.COMPLETION = BUDGET',
                   'S_fresh = S_fresh_budget[.COMPLETION = NORMAL]',
                   'S_fresh.TODO = (GENERATOR_UNPACK pgeneratorunpack_next "next") :: ptask_tail*',
                   'n_fresh = |S.STORE|', 'n_fresh =/= n_raw',
                   'S_fresh.STORE[n_fresh] = DEFINED (PINT 22)',
                   '$heap_owners($heap_graph(S_fresh), HCELL n_fresh) = 1',
                   'S_done = $drive(S_fresh, 4000)',
                   'S_done.COMPLETION = NORMAL', '$drive(S, 4000) = S_done',
                   '$heap_owners($heap_graph(S_done), HCELL n_fresh) = 0',
                   '$heap_owners($heap_graph(S_done), HCELL n_raw) = 2',
                   '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))'],
    },
    'running-producer-copies-cell-before-ordinary-next-error': {
        'source': SOURCES['running-generator-in-suspended-fiber'],
        'stage': 'S.TODO = (GENERATOR_UNPACK pgeneratorunpack "byref") :: ptask_tail*',
        'checks': [*CAPTURE,
                   'pgenerator.PHASE = GENERATOR_RUNNING',
                   '$lookup(S.ENV, $ptascii("f96")) = (n_fiber_cell)',
                   'S.STORE[n_fiber_cell] = DEFINED (POBJECT n_fiber)',
                   'S.OBJECTS[n_fiber] = FIBER pfiber',
                   'pfiber.STATUS = FIBER_SUSPENDED',
                   *VALID, *ZERO, *ONE, *FRESH,
                   'S_error_budget = $drive_steps(S_one, 1)',
                   'S_error_budget.COMPLETION = BUDGET',
                   'S_error = S_error_budget[.COMPLETION = NORMAL]',
                   'S_error.TODO = (THROW_SEARCH n_error) :: '
                   '(GENERATOR_UNPACK pgeneratorunpack_next "next") :: ptask_tail*',
                   '$throwable_field(S_error, n_error, "message") = '
                   'PSTRING $ptascii("Cannot resume an already running generator")',
                   '$heap_owners($heap_graph(S_error), HCELL n_fresh) = 1',
                   '$call_descriptors_valid(S_error)', '$heap_valid($heap_graph(S_error))',
                   *DONE,
                   '$heap_owners($heap_graph(S_done), HOBJECT n_fiber) = 0'],
    },
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    base.CASES = CASES
    base.INPUTS = [Path(__file__), CATALOG, Path(base.__file__)]
    raise SystemExit(0 if base.run(parser.parse_args().case) else 1)
