#!/usr/bin/env python3
"""Reach borrowed source cells and distinct delivered reference-cell owners."""
import argparse
import json
from pathlib import Path

import generator_call_unpack_state as base

CATALOG = Path(__file__).with_name('generator_reference_sink_cases.json')
SOURCES = {row['id']: row['source'] for row in json.loads(CATALOG.read_bytes())}


def group(source, old, current, count, owners, final_owners, before=(), after=(), done=()):
    return {
        'source': SOURCES[source],
        'stage': 'S.TODO = (GENERATOR_UNPACK pgeneratorunpack "byref") :: ptask_tail* '
                 f'-- if pgeneratorunpack.COUNT = {count}',
        'checks': [
            'n_data = pgeneratorunpack.OBJECT',
            'S.OBJECTS[n_data] = GENERATOR pgenerator',
            'pgenerator.PHASE = GENERATOR_PAUSED', 'pgenerator.VALUE = eps',
            'pgenerator.REFCELL = (n_source)', 'pgeneratorunpack.CELL = (n_source)',
            f'pgeneratorunpack.HOLD = KNOWN (PINT {old})',
            f'$ordinary_reference_value(S, n_source) = (PINT {current})',
            '$iterator_unpack_scalar_operand(S, REFERENCE n_source)',
            f'$generator_unpack_reference_value(S, pgeneratorunpack) = (PINT {current})',
            'pgeneratorunpack.KEY = pgenerator.KEY',
            'pgeneratorunpack.INDEX = (pgenerator.INDEX)',
            '$generator_unpack_capture_mode(S, pgeneratorunpack)',
            '$generator_unpack_reference_stage(S, pgeneratorunpack)',
            '$generator_unpack_warning_same(S, pgeneratorunpack)',
            '~$generator_unpack_capture_mode(S, pgeneratorunpack[.CELL = eps])',
            '~$generator_unpack_capture_mode(S, pgeneratorunpack[.CELL = (|S.STORE|)])',
            '~$generator_unpack_warning_same(S, pgeneratorunpack[.CELL = eps])',
            '~$generator_unpack_warning_same(S, pgeneratorunpack[.CELL = (|S.STORE|)])',
            '~$generator_unpack_reference_stage(S, pgeneratorunpack[.HOLD = REFERENCE n_source])',
            '$task_nodes(GENERATOR_UNPACK pgeneratorunpack "byref") = '
            '[HOBJECT n_data] ++ $operand_nodes(pgeneratorunpack.INPUT) ++ '
            '$unpack_call_roots(pgeneratorunpack.CALL)',
            '~((HCELL n_source) <- $task_nodes(GENERATOR_UNPACK pgeneratorunpack "byref"))',
            f'$heap_owners($heap_graph(S), HCELL n_source) = {owners}',
            '$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))',
            *before,
            'S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
            'S_zero[.COMPLETION = NORMAL] = S',
            'S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
            'S_one = S_one_budget[.COMPLETION = NORMAL]',
            'S_one.TODO = (GENERATOR_UNPACK pgeneratorunpack_next "next") :: ptask_tail*',
            'n_fresh = |S.STORE|', 'n_fresh =/= n_source',
            'n_fresh <- S_one.REFCELLS',
            f'S_one.STORE[n_fresh] = DEFINED (PINT {current})',
            'S_one.OBJECTS = S.OBJECTS', 'S_one.EVENTS = S.EVENTS',
            'pgeneratorunpack_next.CELL = eps',
            'pgeneratorunpack_next.HOLD = KNOWN PNULL',
            'pgeneratorunpack_next.KEY = eps', 'pgeneratorunpack_next.INDEX = eps',
            f'pgeneratorunpack_next.COUNT = {count + 1}',
            '$heap_owners($heap_graph(S_one), HCELL n_fresh) = 1',
            f'$heap_owners($heap_graph(S_one), HCELL n_source) = {owners}',
            '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
            '$drive_steps(S_zero[.COMPLETION = NORMAL], 1) = S_one_budget',
            *after,
            'S_done = $drive(S_one, 4000)', 'S_done.COMPLETION = NORMAL',
            'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps',
            'S_done.HELD = eps', '$call_descriptors_valid(S_done)',
            '$heap_valid($heap_graph(S_done))',
            '$heap_owners($heap_graph(S_done), HOBJECT n_data) = 0',
            '$heap_owners($heap_graph(S_done), HCELL n_fresh) = 0',
            f'$heap_owners($heap_graph(S_done), HCELL n_source) = {final_owners}',
            *done,
        ],
    }


SINGLE = ['pgeneratorunpack.CALL.SENT = {SLOTS eps, NAMED eps}']
SINGLE_AFTER = ['pgeneratorunpack_next.CALL.SENT = {SLOTS '
                '([NAMED_SENT (REFERENCE n_fresh)]), NAMED eps}']
CASES = {
    'temporary-source-cell-retires-before-private-delivery': group(
        'temporary-local-cell-default', 11, 11, 0, 2, 0,
        before=SINGLE, after=SINGLE_AFTER,
        done=['~((HCELL n_source) <- S_done.ALLOCATIONS)',
              '$ordinary_reference_value(S_done, n_source) = eps']),
    'alias-write-rereads-source-cell-without-owning-designation': group(
        'warning-writes-outside-alias', 11, 22, 0, 4, 2,
        before=[*SINGLE, '$lookup(S.ENV, $ptascii("v")) = (n_source)',
                '$lookup(S.ENV, $ptascii("alias")) = (n_source)'],
        after=SINGLE_AFTER,
        done=['$ordinary_reference_value(S_done, n_source) = (PINT 22)',
              '$lookup(S_done.ENV, $ptascii("v")) = (n_source)',
              '$lookup(S_done.ENV, $ptascii("alias")) = (n_source)']),
    'global-name-rebind-keeps-old-dereferenced-cell': group(
        'warning-rebinds-global-name', 11, 22, 0, 3, 1,
        before=[*SINGLE, '$lookup(S.ENV, $ptascii("old")) = (n_source)',
                '$lookup(S.ENV, $ptascii("v")) = (n_new)',
                '$lookup(S.ENV, $ptascii("other")) = (n_new)',
                'n_new =/= n_source',
                '$ordinary_reference_value(S, n_new) = (PINT 44)',
                '~$generator_unpack_warning_same(S, pgeneratorunpack[.CELL = (n_new)])'],
        after=[*SINGLE_AFTER, 'n_fresh =/= n_new'],
        done=['$ordinary_reference_value(S_done, n_source) = (PINT 22)',
              '$ordinary_reference_value(S_done, n_new) = (PINT 44)',
              '$lookup(S_done.ENV, $ptascii("v")) = (n_new)',
              '$lookup(S_done.ENV, $ptascii("old")) = (n_source)']),
    'second-warning-keeps-earlier-private-cell': group(
        'two-sends-share-source-not-private-cells', 30, 31, 1, 4, 2,
        before=['pgeneratorunpack.CALL.SENT = {SLOTS '
                '([NAMED_SENT (REFERENCE n_first)]), NAMED eps}',
                'n_first =/= n_source', 'S.STORE[n_first] = DEFINED (PINT 11)',
                '$heap_owners($heap_graph(S), HCELL n_first) = 1'],
        after=['n_fresh =/= n_first', 'S_one.STORE[n_first] = DEFINED (PINT 11)',
               'pgeneratorunpack_next.CALL.SENT = {SLOTS '
               '([NAMED_SENT (REFERENCE n_first), NAMED_SENT (REFERENCE n_fresh)]), NAMED eps}',
               '$heap_owners($heap_graph(S_one), HCELL n_first) = 1'],
        done=['$ordinary_reference_value(S_done, n_source) = (PINT 31)',
              '$heap_owners($heap_graph(S_done), HCELL n_first) = 0']),
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    base.CASES = CASES
    base.INPUTS = [Path(__file__), CATALOG, Path(base.__file__)]
    raise SystemExit(0 if base.run(parser.parse_args().case) else 1)
