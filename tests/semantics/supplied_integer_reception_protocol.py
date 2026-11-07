#!/usr/bin/env python3
"""Supplied integer reception, handler transport and malformed continuations."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('supplied_integer_reception_cases.json')
SOURCES = {}
for row in json.loads(CATALOGUE.read_text()):
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
    SOURCES[row['id']] = row['source']

CASES = {
    'supplied-lossy-receive-singleton': {
        'source': SOURCES['supplied-integer-receive-normal'],
        'stage': 'S.TODO = [LOSSY_PARAMETER_RECEIVE porigin n_cell n_bits i z]',
        'checks': [
            'ptask = LOSSY_PARAMETER_RECEIVE porigin n_cell n_bits i z',
            '$lossy_parameter_source_valid(S, ptask)',
            '$lossy_parameter_ready(S, n_cell, n_bits)',
            '$call_task_valid(S, ptask)',
            '$call_descriptors_valid(S)',
            '$task_nodes(ptask) = eps',
            '$heap_owners($heap_graph(S), HCELL n_cell) = 1',
            'S.STORE[n_cell] = DEFINED (PFLOAT n_bits)',
            'i = 1',
            'S_bad = S[.TODO = [ptask, ptask]]',
            '$lossy_parameter_source_valid(S_bad, ptask)',
            '~$call_task_valid(S_bad, ptask)',
            '~$call_tasks_valid(S_bad, S_bad.TODO)',
            '~$call_descriptors_valid(S_bad)',
            'S_rejected = $drive(S_bad, 1)',
            'S_rejected.COMPLETION = UNSUPPORTED text',
            'S_rejected.STORE = S_bad.STORE /\\ S_rejected.TODO = S_bad.TODO',
            'S_budget = $drive(S, 0)',
            'S_budget.COMPLETION = BUDGET',
            'S_budget.STORE = S.STORE /\\ S_budget.TODO = S.TODO',
            '$call_descriptors_valid(S_budget)',
            '$drive(S_budget[.COMPLETION = NORMAL], 1) = $drive(S, 1)',
            'PhpStep: S ~> S_body',
            'S_body.STORE[n_cell] = DEFINED (PINT i)',
            '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
            'S_body.TODO = $call_receive_body(S, pfunction)',
            'S_body.ORIGIN = (porigin)',
        ],
    },
    'supplied-lossy-receive-handler': {
        'source': SOURCES['supplied-integer-receive-normal'],
        'stage': ('S.CURRENT = (pcallcontext_handler) '
                  '-- if $function_at(S.FUNCTIONS, pcallcontext_handler.FUNCTION) = (pfunction_handler) '
                  '-- if pfunction_handler.NAME = $ptascii("warning175") '
                  '-- if S.FRAMES = pframe :: pframe_tail* '
                  '-- if pframe.TODO = [ERROR_HANDLER_RESULT perrorcall] '
                  '-- if perrorcall.RESUME = LOSSY_PARAMETER_RECEIVE porigin n_cell n_bits i z '
                  '-- if S.GLOBALTABLE = (psymboltable_global) '
                  '-- if $lookup(psymboltable_global.ENV, $ptascii("source175")) = (n_global) '
                  '-- if S.STORE[n_global] = DEFINED (PINT 41)'),
        'checks': [
            'S_scope = $constant_frame_scope(S, pframe, pframe_tail*)',
            'ptask = LOSSY_PARAMETER_RECEIVE porigin n_cell n_bits i z',
            '$lossy_parameter_source_valid(S_scope, ptask)',
            '$error_call_valid(S_scope, perrorcall)',
            '$call_task_valid(S_scope, ERROR_HANDLER_RESULT perrorcall)',
            '$call_tasks_valid(S_scope, S_scope.TODO)',
            '~$call_task_valid(S_scope, ptask)',
            '$call_descriptors_valid(S)',
            'S.STORE[n_cell] = DEFINED (PFLOAT n_bits)',
            'n_cell =/= n_global',
            '$heap_owners($heap_graph(S), HCELL n_cell) = 1',
            '$task_nodes(ptask) = eps',
        ],
    },
    'supplied-lossy-receive-throw': {
        'source': SOURCES['supplied-integer-receive-pending'],
        'stage': ('S.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail* '
                  '-- if perrorcall.RESUME = LOSSY_PARAMETER_RECEIVE porigin n_cell n_bits i z '
                  '-- if S.CURRENT = (pcallcontext) '
                  '-- if pcallcontext.FUNCTION = porigin'),
        'checks': [
            'ptask = LOSSY_PARAMETER_RECEIVE porigin n_cell n_bits i z',
            '$lossy_parameter_source_valid(S, ptask)',
            '$error_call_valid(S, perrorcall)',
            '$call_task_valid(S, ERROR_HANDLER_RESULT perrorcall)',
            '~$call_task_valid(S, ptask)',
            '$call_descriptors_valid(S)',
            '$task_nodes(ptask) = eps',
            'S.STORE[n_cell] = DEFINED (PFLOAT n_bits)',
            '$heap_owners($heap_graph(S), HCELL n_cell) = 1',
            '$heap_count(HOBJECT n_exception, $tasks_nodes(S.TODO)) = 1',
            'S.GLOBALTABLE = (psymboltable_global)',
            '$lookup(psymboltable_global.ENV, $ptascii("original175")) = (n_original)',
            'S.STORE[n_original] = DEFINED (POBJECT n_exception)',
            'S_skip = $return_discard(S[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*], ERROR_HANDLER_RESULT perrorcall)',
            'S_skip.TODO = (THROW_SEARCH n_exception) :: ptask_tail*',
            'S_skip.STORE = S.STORE /\\ S_skip.OBJECTS = S.OBJECTS',
            'S_skip.ERRORHANDLER.CALLBACK = (perrorcall.CALLBACK)',
        ],
    },
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE))
