#!/usr/bin/env python3
"""Reach captured cell delivery after changed keys, closure and caught throws."""
import argparse
import json
from pathlib import Path

import generator_call_unpack_state as base

CATALOG = Path(__file__).with_name('generator_captured_cell_sink_cases.json')
SOURCES = {row['id']: row['source'] for row in json.loads(CATALOG.read_bytes())}
VALID = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']


def normal(source, owners, data_owners, before, after=(), done=()):
    return {
        'source': SOURCES[source],
        'stage': 'S.TODO = (GENERATOR_UNPACK pgeneratorunpack "byref") :: ptask_tail*',
        'checks': [
            'n_data = pgeneratorunpack.OBJECT',
            'S.OBJECTS[n_data] = GENERATOR pgenerator',
            'pgeneratorunpack.CELL = (n_raw)',
            'pgeneratorunpack.HOLD = KNOWN (PINT 11)',
            'pgeneratorunpack.KEY = (PINT 0)', 'pgeneratorunpack.INDEX = (0)',
            'pgeneratorunpack.COUNT = 0',
            'pgeneratorunpack.CALL.SENT = {SLOTS eps, NAMED eps}',
            'S.STORE[n_raw] = DEFINED (PINT 22)',
            '$lookup(S.ENV, $ptascii("a")) = (n_raw)',
            '$lookup(S.ENV, $ptascii("old")) = (n_raw)',
            '$generator_unpack_reference_source(S, pgeneratorunpack)',
            '$generator_unpack_capture_mode(S, pgeneratorunpack)',
            '$generator_unpack_reference_stage(S, pgeneratorunpack)',
            '~$generator_unpack_warning_same(S, pgeneratorunpack)',
            '$generator_unpack_reference_delivery(S, pgeneratorunpack) = (PINT 22)',
            '$generator_unpack_reference_delivery(S, pgeneratorunpack[.CELL = eps]) = eps',
            '$generator_unpack_reference_delivery(S, pgeneratorunpack[.CELL = (|S.STORE|)]) = eps',
            '$generator_unpack_reference_delivery(S[.ALLOCATIONS = eps], pgeneratorunpack) = eps',
            '$generator_unpack_reference_delivery(S[.STORE = $set_cell(S.STORE, n_raw, UNDEFINED)], pgeneratorunpack) = eps',
            '~$generator_unpack_reference_stage(S, pgeneratorunpack[.HOLD = REFERENCE n_raw])',
            '$task_nodes(GENERATOR_UNPACK pgeneratorunpack "byref") = '
            '[HOBJECT n_data] ++ $operand_nodes(pgeneratorunpack.INPUT) ++ '
            '$unpack_call_roots(pgeneratorunpack.CALL)',
            '~((HCELL n_raw) <- $task_nodes(GENERATOR_UNPACK pgeneratorunpack "byref"))',
            f'$heap_owners($heap_graph(S), HCELL n_raw) = {owners}',
            f'$heap_owners($heap_graph(S), HOBJECT n_data) = {data_owners}',
            *before, *VALID, *ZERO,
            'S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
            'S_one = S_one_budget[.COMPLETION = NORMAL]',
            'S_one.TODO = (GENERATOR_UNPACK pgeneratorunpack_next "next") :: ptask_tail*',
            'n_fresh = |S.STORE|', 'n_fresh =/= n_raw', 'n_fresh <- S_one.REFCELLS',
            'S_one.STORE[n_fresh] = DEFINED (PINT 22)',
            'S_one.STORE[n_raw] = DEFINED (PINT 22)',
            'S_one.OBJECTS = S.OBJECTS', 'S_one.EVENTS = S.EVENTS',
            'pgeneratorunpack_next.CALL.SENT = {SLOTS '
            '([NAMED_SENT (REFERENCE n_fresh)]), NAMED eps}',
            'pgeneratorunpack_next.COUNT = 1', 'pgeneratorunpack_next.CELL = eps',
            'pgeneratorunpack_next.HOLD = KNOWN PNULL',
            'pgeneratorunpack_next.KEY = eps', 'pgeneratorunpack_next.INDEX = eps',
            '$heap_owners($heap_graph(S_one), HCELL n_fresh) = 1',
            f'$heap_owners($heap_graph(S_one), HCELL n_raw) = {owners}',
            f'$heap_owners($heap_graph(S_one), HOBJECT n_data) = {data_owners}',
            '$generator_unpack_valid(S_one, pgeneratorunpack_next, "next")',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
            '$drive_steps(S_zero[.COMPLETION = NORMAL], 1) = S_one_budget',
            *after,
            'S_done = $drive(S_one, 4000)', 'S_done.COMPLETION = NORMAL',
            '$drive(S, 4000) = S_done', 'S_done.TODO = eps', 'S_done.FRAMES = eps',
            'S_done.CURRENT = eps', 'S_done.HELD = eps',
            '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
            '$heap_owners($heap_graph(S_done), HOBJECT n_data) = 0',
            '$heap_owners($heap_graph(S_done), HCELL n_fresh) = 0',
            '$heap_owners($heap_graph(S_done), HCELL n_raw) = 2',
            '$ordinary_reference_value(S_done, n_raw) = (PINT 22)',
            *done,
        ],
    }


CLOSED = ['pgenerator.PHASE = GENERATOR_CLOSED', 'pgenerator.FRAME = eps',
          'pgenerator.REFCELL = eps', 'pgenerator.KEY = eps',
          '$generator_unpack_reference_value(S, pgeneratorunpack) = eps']
CASES = {
    'replacement-string-key-keeps-captured-cell-and-positional-target': normal(
        'replacement-string-key-keeps-original-positional-target', 3, 2,
        ['pgenerator.PHASE = GENERATOR_PAUSED', 'pgenerator.REFCELL = (n_cache)',
         'n_raw =/= n_cache', 'pgenerator.INDEX = 0',
         'pgenerator.KEY = (PSTRING_CARRIER INTERNED_STRING $ptascii("second"))',
         '$generator_unpack_reference_value(S, pgeneratorunpack) = (PINT 11)',
         '$heap_owners($heap_graph(S), HCELL n_cache) = 3',
         'S_runtime = $string_request(S, $ptascii("bc"))',
         'S_runtime.RESULT = KNOWN pvalue_runtime',
         '$iterator_unpack_scalar_operand(S_runtime, KNOWN pvalue_runtime)',
         '$generator_unpack_reference_delivery(S_runtime[.STORE = '
         '$set_cell(S_runtime.STORE, n_raw, DEFINED pvalue_runtime)], pgeneratorunpack) = eps'],
        after=['n_fresh =/= n_cache',
               '$heap_owners($heap_graph(S_one), HCELL n_cache) = 3'],
        done=['$heap_owners($heap_graph(S_done), HCELL n_cache) = 1',
              '$ordinary_reference_value(S_done, n_cache) = (PINT 11)']),
    'temporary-input-closed-generator-keeps-live-outside-cell': normal(
        'temporary-input-closed-generator-live-cell', 2, 3,
        [*CLOSED, 'pgeneratorunpack.INPUT = KNOWN (POBJECT n_data)']),
    'caught-producer-exception-leaves-normal-warning-and-old-cell': normal(
        'handler-catches-producer-throw-before-cell-delivery', 2, 2,
        [*CLOSED, 'S.COMPLETION = NORMAL']),
    'byval-equal-cache-ordinary-used-yield-still-delivers': {
        'source': SOURCES['byval-equal-cache-used-yield-continues-normally'],
        'stage': 'S.TODO = (GENERATOR_UNPACK pgeneratorunpack "byref") :: ptask_tail*',
        'checks': [
            'n_data = pgeneratorunpack.OBJECT',
            'S.OBJECTS[n_data] = GENERATOR pgenerator',
            'pgenerator.PHASE = GENERATOR_PAUSED', 'pgenerator.PARKED = eps',
            'pgenerator.DELEGATE = eps',
            'pgenerator.REFCELL = eps', 'pgeneratorunpack.CELL = eps',
            'pgenerator.KEY = (PINT 0)', 'pgeneratorunpack.KEY = (PINT 0)',
            'pgenerator.INDEX = 0', 'pgeneratorunpack.INDEX = (0)',
            'pgeneratorunpack.HOLD = KNOWN (PINT 11)',
            '$generator_unpack_reference_source(S, pgeneratorunpack)',
            '$generator_unpack_reference_stage(S, pgeneratorunpack)',
            '$generator_unpack_warning_same(S, pgeneratorunpack)',
            '$generator_unpack_reference_delivery(S, pgeneratorunpack) = (PINT 11)',
            '$heap_owners($heap_graph(S), HOBJECT n_data) = 2',
            *VALID, *ZERO,
            'S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
            'S_one = S_one_budget[.COMPLETION = NORMAL]',
            'S_one.TODO = (GENERATOR_UNPACK pgeneratorunpack_next "next") :: ptask_tail*',
            'n_fresh = |S.STORE|', 'n_fresh <- S_one.REFCELLS',
            'S_one.STORE[n_fresh] = DEFINED (PINT 11)',
            'pgeneratorunpack_next.CALL.SENT = {SLOTS '
            '([NAMED_SENT (REFERENCE n_fresh)]), NAMED eps}',
            'pgeneratorunpack_next.COUNT = 1', 'pgeneratorunpack_next.CELL = eps',
            'pgeneratorunpack_next.HOLD = KNOWN PNULL',
            'pgeneratorunpack_next.KEY = eps', 'pgeneratorunpack_next.INDEX = eps',
            '$heap_owners($heap_graph(S_one), HCELL n_fresh) = 1',
            'S_one.OBJECTS = S.OBJECTS', 'S_one.EVENTS = S.EVENTS',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
            '$drive_steps(S_zero[.COMPLETION = NORMAL], 1) = S_one_budget',
            'S_done = $drive(S_one, 4000)', 'S_done.COMPLETION = NORMAL',
            '$drive(S, 4000) = S_done', 'S_done.TODO = eps', 'S_done.FRAMES = eps',
            'S_done.CURRENT = eps', 'S_done.HELD = eps',
            '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
            '$heap_owners($heap_graph(S_done), HOBJECT n_data) = 0',
            '$heap_owners($heap_graph(S_done), HCELL n_fresh) = 0',
        ],
    },
    'byval-handler-delegation-preserves-explicit-refusal': {
        'source': SOURCES['byval-handler-enters-yield-from-boundary'],
        'stage': 'S.TODO = (GENERATOR_UNPACK pgeneratorunpack "byref") :: ptask_tail*',
        'checks': [
            'n_data = pgeneratorunpack.OBJECT',
            'S.OBJECTS[n_data] = GENERATOR pgenerator',
            'pgenerator.PHASE = GENERATOR_DELEGATING',
            'pgenerator.DELEGATE = (pgeneratorfrom)',
            'pgenerator.REFCELL = eps', 'pgeneratorunpack.CELL = eps',
            'pgeneratorunpack.HOLD = KNOWN (PINT 11)',
            '$generator_unpack_reference_source(S, pgeneratorunpack)',
            '$generator_unpack_reference_stage(S, pgeneratorunpack)',
            '~$generator_unpack_warning_same(S, pgeneratorunpack)',
            '$generator_unpack_reference_delivery(S, pgeneratorunpack) = eps',
            *VALID, *ZERO,
            'S_one = $drive_steps(S, 1)',
            'S_one = S[.COMPLETION = UNSUPPORTED '
            '"Generator unpack reference payload changed during warning"]',
            '$generator_unpack_reference_blocked(S_one)',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
            '$drive_steps(S_one, 1) = S_one', '$drive(S_one, 10) = S_one',
        ],
    },
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    base.CASES = CASES
    base.INPUTS = [Path(__file__), CATALOG, Path(base.__file__)]
    raise SystemExit(0 if base.run(parser.parse_args().case) else 1)
