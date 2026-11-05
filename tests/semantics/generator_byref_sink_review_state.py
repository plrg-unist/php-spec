#!/usr/bin/env python3
"""Review warning capture and fresh cells at genuine Generator unpack cuts."""
import argparse
import json
from pathlib import Path

import generator_call_unpack_state as base

CATALOG = Path(__file__).with_name('generator_byref_sink_cases.json')
NEGATIVES = Path(__file__).with_name('generator_byref_sink_negative_cases.json')
SOURCES = {row['id']: row['source'] for row in json.loads(CATALOG.read_bytes())}
VALID = ['$call_descriptors_valid(S)', '$heap_valid($heap_graph(S))']
ZERO = ['S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
        'S_zero[.COMPLETION = NORMAL] = S']
ONE = ['S_one_budget = $drive_steps(S, 1)', 'S_one_budget.COMPLETION = BUDGET',
       'S_one = S_one_budget[.COMPLETION = NORMAL]']
DONE = ['S_done = $drive(S_one, 4000)', 'S_done.COMPLETION = NORMAL',
        '$drive(S, 4000) = S_done',
        'S_done.TODO = eps', 'S_done.FRAMES = eps', 'S_done.CURRENT = eps',
        'S_done.HELD = eps', '$call_descriptors_valid(S_done)',
        '$heap_valid($heap_graph(S_done))',
        '$heap_owners($heap_graph(S_done), HOBJECT n_data) = 0']
CAPTURE = [
    'n_data = pgeneratorunpack.OBJECT',
    'S.OBJECTS[n_data] = GENERATOR pgenerator',
    'pgenerator.PHASE = GENERATOR_PAUSED', 'pgenerator.REFCELL = eps',
    'pgenerator.VALUE = (PINT 11)', 'pgeneratorunpack.HOLD = KNOWN (PINT 11)',
    'pgeneratorunpack.KEY = pgenerator.KEY',
    'pgeneratorunpack.INDEX = (pgenerator.INDEX)',
    '$generator_unpack_reference_source(S, pgeneratorunpack)',
    '$generator_unpack_reference_stage(S, pgeneratorunpack)',
    '$generator_unpack_warning_same(S, pgeneratorunpack)',
    '$heap_owners($heap_graph(S), HOBJECT n_data) = 2',
]
FRESH = [
    'S_one.TODO = (GENERATOR_UNPACK pgeneratorunpack_next "next") :: ptask_tail*',
    'n_fresh = |S.STORE|', 'n_fresh <- S_one.REFCELLS',
    'S_one.STORE[n_fresh] = DEFINED (PINT 11)',
    'S_one.OBJECTS = S.OBJECTS', 'S_one.EVENTS = S.EVENTS',
    'pgeneratorunpack_next.HOLD = KNOWN PNULL',
    'pgeneratorunpack_next.KEY = eps', 'pgeneratorunpack_next.INDEX = eps',
    'pgeneratorunpack_next.COUNT = $(pgeneratorunpack.COUNT + 1)',
    '$heap_owners($heap_graph(S_one), HCELL n_fresh) = 1',
    '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 2',
    '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
    '$drive_steps(S_zero[.COMPLETION = NORMAL], 1) = S_one_budget',
]

CASES = {}
for name in ('retained-scalar-default', 'temporary-scalar-default'):
    CASES[name + '-fresh-private-cell'] = {
        'source': SOURCES[name],
        'stage': 'S.TODO = (GENERATOR_UNPACK pgeneratorunpack "byref") :: ptask_tail*',
        'checks': [*CAPTURE, 'pgeneratorunpack.COUNT = 0',
                   'pgeneratorunpack.CALL.SENT = {SLOTS eps, NAMED eps}',
                   '$lookup(S.ENV, $ptascii("v")) = (n_source)',
                   'S.STORE[n_source] = DEFINED (PINT 11)',
                   *VALID, *ZERO, *ONE, *FRESH,
                   'n_fresh =/= n_source',
                   'pgeneratorunpack_next.CALL.SENT = {SLOTS ([NAMED_SENT '
                   '(REFERENCE n_fresh)]), NAMED eps}',
                   'S_one.STORE[n_source] = DEFINED (PINT 11)',
                   *DONE, 'S_done.STORE[n_source] = DEFINED (PINT 11)',
                   '$heap_owners($heap_graph(S_done), HCELL n_fresh) = 0'],
    }

CASES['handler-invoke-exact-source-and-warning-authority'] = {
    'source': SOURCES['retained-scalar-handler-snapshot'],
    'stage': 'S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail* '
             '-- if perrorcall.RESUME = GENERATOR_UNPACK pgeneratorunpack "byref"',
    'checks': [*CAPTURE, 'perrorcall.LEVEL = 2', 'perrorcall.TARGET = eps',
               'perrorcall.LINE = 5',
               'perrorcall.MESSAGE = $generator_unpack_warning_message(S, pgeneratorunpack)',
               'perrorcall.EVENT = DIAGNOSTIC "Warning" perrorcall.MESSAGE 5',
               '$error_call_valid(S, perrorcall)',
               '~$generator_unpack_warning_same(S, pgeneratorunpack[.INDEX = '
               '($(pgenerator.INDEX + 1))])',
               '~$error_call_valid(S, perrorcall[.LEVEL = 8])',
               '~$error_call_valid(S, perrorcall[.LINE = 0])',
               '~$error_call_valid(S, perrorcall[.MESSAGE = $ptascii("other")])',
               '~$error_call_valid(S, perrorcall[.EVENT = DIAGNOSTIC "Notice" '
               'perrorcall.MESSAGE 5])',
               '~$error_call_valid(S[.ORIGIN = eps], perrorcall)',
               '~$generator_unpack_reference_stage(S, pgeneratorunpack[.COUNT = 2])',
               '~$generator_unpack_reference_stage(S, pgeneratorunpack[.KEY = (PBOOL true)])',
               '~$generator_unpack_reference_stage(S, pgeneratorunpack[.HOLD = '
               'KNOWN (POBJECT n_data)])',
               '~$generator_unpack_reference_stage(S, pgeneratorunpack[.HOLD = KNOWN PUNDEFINED])',
               '~$generator_unpack_valid(S, pgeneratorunpack[.INDEX = eps], "byref")',
               '~$generator_unpack_valid(S[.TODO = ptask_tail*], pgeneratorunpack, "byref")',
               *VALID, *ZERO,
               'S_done = $drive(S, 4000)', 'S_done.COMPLETION = NORMAL',
               '$drive(S_zero[.COMPLETION = NORMAL], 4000) = S_done',
               '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))'],
}
CASES['handler-global-write-keeps-captured-value-and-fresh-cell'] = {
    'source': SOURCES['retained-scalar-handler-snapshot'],
    'stage': 'S.TODO = (GENERATOR_UNPACK pgeneratorunpack "byref") :: ptask_tail*',
    'checks': [*CAPTURE, '$lookup(S.ENV, $ptascii("v")) = (n_source)',
               'S.STORE[n_source] = DEFINED (PINT 22)',
               *VALID, *ZERO, *ONE, *FRESH, 'n_fresh =/= n_source',
               'pgeneratorunpack_next.CALL.SENT = {SLOTS ([NAMED_SENT '
               '(REFERENCE n_fresh)]), NAMED eps}',
               'S_one.STORE[n_source] = DEFINED (PINT 22)',
               *DONE, 'S_done.STORE[n_source] = DEFINED (PINT 22)',
               '$heap_owners($heap_graph(S_done), HCELL n_fresh) = 0'],
}
CASES['callback-send-keeps-authenticated-generator-resume'] = {
    'source': SOURCES['retained-scalar-handler-snapshot'],
    'stage': 'S.TODO = (API_CALLBACK_SEND papiargcursor) :: ptask_tail* '
             '-- if papiargcursor.CALL = API_ERROR perrorcall '
             '-- if perrorcall.RESUME = GENERATOR_UNPACK pgeneratorunpack "byref"',
    'checks': [*CAPTURE, 'papiargcursor.INDEX = 0', 'papiargcursor.SENT = eps',
               '$generator_unpack_count(S.TODO) = 1',
               '$error_call_valid(S, perrorcall)', '$api_cursor_valid(S, papiargcursor)',
               *VALID, *ZERO, *ONE,
               'S_one.TODO = (API_CALLBACK_SEND papiargcursor_next) :: ptask_tail*',
               'papiargcursor_next = papiargcursor[.INDEX = 1][.SENT = [KNOWN (PINT 2)]]',
               '$generator_unpack_count(S_one.TODO) = 1',
               '$api_cursor_valid(S_one, papiargcursor_next)',
               '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
               '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 2', *DONE],
}
CASES['second-position-keeps-earlier-byvalue-send'] = {
    'source': SOURCES['retained-second-position'],
    'stage': 'S.TODO = (GENERATOR_UNPACK pgeneratorunpack "byref") :: ptask_tail*',
    'checks': [*CAPTURE, 'pgeneratorunpack.COUNT = 1',
               'pgeneratorunpack.CALL.SENT = {SLOTS ([NAMED_SENT '
               '(KNOWN (PINT 5))]), NAMED eps}',
               '$generator_unpack_reference_target(S, pgeneratorunpack, NAMED_POSITION 1)',
               '~$generator_unpack_reference_target(S, pgeneratorunpack, NAMED_POSITION 0)',
               '~$generator_unpack_reference_target(S, pgeneratorunpack, NAMED_POSITION 2)',
               *VALID, *ZERO, *ONE, *FRESH,
               'pgeneratorunpack_next.CALL.SENT = {SLOTS ([NAMED_SENT '
               '(KNOWN (PINT 5)), NAMED_SENT (REFERENCE n_fresh)]), NAMED eps}',
               *DONE, '$heap_owners($heap_graph(S_done), HCELL n_fresh) = 0'],
}
CASES['second-reference-warning-retains-first-private-cell'] = {
    'source': SOURCES['temporary-two-reference-destinations'],
    'stage': 'S.TODO = (GENERATOR_UNPACK pgeneratorunpack "byref") :: ptask_tail* '
             '-- if pgeneratorunpack.COUNT = 1',
    'checks': [*CAPTURE,
               'pgeneratorunpack.INPUT = KNOWN (POBJECT n_data)',
               'pgeneratorunpack.CALL.SENT = {SLOTS ([NAMED_SENT '
               '(REFERENCE n_first)]), NAMED eps}',
               'n_first <- S.REFCELLS', 'S.STORE[n_first] = DEFINED (PINT 5)',
               '$heap_owners($heap_graph(S), HCELL n_first) = 1',
               *VALID, *ZERO, *ONE, *FRESH, 'n_fresh =/= n_first',
               'S_one.STORE[n_first] = DEFINED (PINT 5)',
               '$heap_owners($heap_graph(S_one), HCELL n_first) = 1',
               'pgeneratorunpack_next.CALL.SENT = {SLOTS ([NAMED_SENT '
               '(REFERENCE n_first), NAMED_SENT (REFERENCE n_fresh)]), NAMED eps}',
               *DONE, '$heap_owners($heap_graph(S_done), HCELL n_first) = 0',
               '$heap_owners($heap_graph(S_done), HCELL n_fresh) = 0'],
}
CASES['throwing-warning-keeps-real-cursor-and-throwable-at-explicit-stop'] = {
    'source': next(row['source'] for row in json.loads(NEGATIVES.read_bytes())
                   if row['id'] == 'warning-handler-throw'),
    'stage': 'S.TODO = (THROW_SEARCH n_error) :: (ERROR_HANDLER_RESULT perrorcall) '
             ':: ptask_tail* -- if perrorcall.RESUME = '
             'GENERATOR_UNPACK pgeneratorunpack "byref"',
    'checks': [*CAPTURE, '$throwable_live(S, n_error)',
               '$error_call_valid(S, perrorcall)', *VALID, *ZERO,
               'S_one = $drive_steps(S, 1)',
               'S_one.COMPLETION = UNSUPPORTED '
               '"Generator unpack pending reference warning exception"',
               'S_one.TODO = (THROW_SEARCH n_error) :: '
               '(GENERATOR_UNPACK pgeneratorunpack "byref") :: ptask_tail*',
               'S_one.OBJECTS = S.OBJECTS', 'S_one.STORE = S.STORE',
               'S_one.ARRAYS = S.ARRAYS', 'S_one.ALLOCATIONS = S.ALLOCATIONS',
               'S_one.EVENTS = S.EVENTS', '$throwable_live(S_one, n_error)',
               '$heap_owners($heap_graph(S_one), HOBJECT n_data) = 2',
               '$call_descriptors_valid(S_one)', '$heap_valid($heap_graph(S_one))',
               '$generator_unpack_reference_blocked(S_one)',
               '~$generator_unpack_reference_blocked(S_one[.COMPLETION = '
               'UNSUPPORTED "other"])',
               '~$generator_unpack_reference_blocked(S_one[.COMPILESTOP = true])',
               '~$generator_unpack_reference_blocked(S_one[.ORIGIN = eps])',
               '~$generator_unpack_reference_blocked(S_one[.TODO = '
               '(THROW_SEARCH n_error) :: ptask_tail*])',
               '~$generator_unpack_reference_blocked(S_one[.TODO = '
               '(THROW_SEARCH n_data) :: (GENERATOR_UNPACK pgeneratorunpack "byref") '
               ':: ptask_tail*])',
               '$drive_steps(S_one, 1) = S_one', '$drive(S_one, 10) = S_one'],
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    base.CASES = CASES
    base.INPUTS = [Path(__file__), CATALOG, NEGATIVES, Path(base.__file__)]
    raise SystemExit(0 if base.run(parser.parse_args().case) else 1)
