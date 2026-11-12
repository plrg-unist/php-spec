#!/usr/bin/env python3
"""Shared reference reception, saved conversion, and original handler throws."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('supplied_reference_integer_reception_cases.json')
SOURCES = {}
for row in json.loads(CATALOGUE.read_text()):
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
    SOURCES[row['id']] = row['source']

CASES = {
    'supplied-ref-lossy-receive-finish': {
        'source': SOURCES['supplied-reference-integer-receive-normal'],
        'stage': 'S.TODO = [LOSSY_REFERENCE_PARAMETER_RECEIVE porigin n_cell n_bits i z]',
        'checks': [
            'ptask = LOSSY_REFERENCE_PARAMETER_RECEIVE porigin n_cell n_bits i z',
            '$lossy_reference_parameter_source_valid(S, ptask)',
            '$lossy_reference_parameter_ready(S, n_cell)',
            '$call_task_valid(S, ptask)',
            '$call_descriptors_valid(S)',
            '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
            'pfunction.SIGNATURE.PARAMETERS = [psparam]',
            'psparam.BYREF /\\ ~pfunction.SIGNATURE.BYREF',
            '$lookup(S.ENV, psparam.NAME) = (n_cell)',
            'S.GLOBALTABLE = (psymboltable_global)',
            '$lookup(psymboltable_global.ENV, $ptascii("source176")) = (n_cell)',
            'n_cell <- S.REFCELLS',
            'S.STORE[n_cell] = DEFINED (PINT 41)',
            'n_bits = 4609434218613702656 /\\ i = 1',
            '$task_nodes(ptask) = eps',
            '$heap_owners($heap_graph(S), HCELL n_cell) = 2',
            '$heap_valid($heap_graph(S))',
            '~$lossy_reference_parameter_source_valid(S, LOSSY_REFERENCE_PARAMETER_RECEIVE porigin n_cell n_bits 2 z)',
            '~$lossy_reference_parameter_source_valid(S, LOSSY_REFERENCE_PARAMETER_RECEIVE porigin n_cell n_bits i $(z + 1))',
            'n_missing = |S.STORE|',
            '~$lossy_reference_parameter_source_valid(S, LOSSY_REFERENCE_PARAMETER_RECEIVE porigin n_missing n_bits i z)',
            '~$lossy_reference_parameter_source_valid(S[.ORIGIN = (porigin)], ptask)',
            '$lossy_reference_parameter_ready(S[.STORE[n_cell] = DEFINED PNULL], n_cell)',
            '$lossy_reference_parameter_ready(S[.STORE[n_cell] = DEFINED (PBOOL false)], n_cell)',
            '$lossy_reference_parameter_ready(S[.STORE[n_cell] = DEFINED (PFLOAT 4612811918334230528)], n_cell)',
            'S_undefined = S[.STORE[n_cell] = UNDEFINED]',
            '$lossy_reference_parameter_source_valid(S_undefined, ptask)',
            '~$lossy_reference_parameter_ready(S_undefined, n_cell)',
            'PhpStep: S_undefined ~> S_undefined_refused',
            'S_undefined_refused.COMPLETION = UNSUPPORTED text_undefined',
            'S_undefined_refused.STORE = S_undefined.STORE /\\ S_undefined_refused.TODO = S_undefined.TODO',
            'S_unmarked = S[.REFCELLS = eps]',
            '$lossy_reference_parameter_source_valid(S_unmarked, ptask)',
            '~$lossy_reference_parameter_ready(S_unmarked, n_cell)',
            'S_held = S[.HELD = [HCELL n_cell]]',
            '$lossy_reference_parameter_source_valid(S_held, ptask)',
            '$heap_owners($heap_graph(S_held), HCELL n_cell) = 3',
            '~$lossy_reference_parameter_ready(S_held, n_cell)',
            'S_blocked = S[.OUTPUTBLOCKED = true]',
            '$lossy_reference_parameter_source_valid(S_blocked, ptask)',
            '~$lossy_reference_parameter_ready(S_blocked, n_cell)',
            'S_duplicate = S[.TODO = [ptask, ptask]]',
            '$lossy_reference_parameter_source_valid(S_duplicate, ptask)',
            '~$call_task_valid(S_duplicate, ptask)',
            '~$call_descriptors_valid(S_duplicate)',
            'S_rejected = $drive(S_duplicate, 1)',
            'S_rejected.COMPLETION = UNSUPPORTED text_duplicate',
            'S_rejected.STORE = S_duplicate.STORE /\\ S_rejected.TODO = eps',
            'S_budget = $drive(S, 0)',
            'S_budget.COMPLETION = BUDGET',
            'S_budget.STORE = S.STORE /\\ S_budget.TODO = S.TODO',
            '$call_descriptors_valid(S_budget)',
            '$drive(S_budget[.COMPLETION = NORMAL], 1) = $drive(S, 1)',
            'PhpStep: S ~> S_body',
            'S_body.STORE[n_cell] = DEFINED (PINT i)',
            'S_body.ENV = S.ENV /\\ S_body.GLOBALTABLE = S.GLOBALTABLE',
            'S_body.ALLOCATIONS = S.ALLOCATIONS /\\ S_body.REFCELLS = S.REFCELLS',
            'S_body.TODO = $call_receive_body(S, pfunction)',
            'S_body.ORIGIN = (porigin)',
            '$heap_owners($heap_graph(S_body), HCELL n_cell) = 2',
            '$call_descriptors_valid(S_body) /\\ $heap_valid($heap_graph(S_body))',
            'S_done = $drive_steps(S_body, 10000)',
            'S_done.COMPLETION = NORMAL /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps',
            '$lookup(S_done.ENV, $ptascii("source176")) = (n_cell)',
            'S_done.STORE[n_cell] = DEFINED (PINT 1)',
            'n_cell <- S_done.REFCELLS',
            '$heap_owners($heap_graph(S_done), HCELL n_cell) = 1',
            '$heap_valid($heap_graph(S_done))',
        ],
    },
    'supplied-ref-lossy-receive-handler': {
        'source': SOURCES['supplied-reference-integer-receive-normal'],
        'stage': ('S.CURRENT = (pcallcontext_handler) '
                  '-- if $function_at(S.FUNCTIONS, pcallcontext_handler.FUNCTION) = (pfunction_handler) '
                  '-- if pfunction_handler.NAME = $ptascii("warning176") '
                  '-- if S.FRAMES = pframe :: pframe_tail* '
                  '-- if pframe.TODO = [ERROR_HANDLER_RESULT perrorcall] '
                  '-- if perrorcall.RESUME = LOSSY_REFERENCE_PARAMETER_RECEIVE porigin n_cell n_bits i z '
                  '-- if S.STORE[n_cell] = DEFINED (PINT 41)'),
        'checks': [
            'S_scope = $constant_frame_scope(S, pframe, pframe_tail*)',
            'ptask = LOSSY_REFERENCE_PARAMETER_RECEIVE porigin n_cell n_bits i z',
            '$lossy_reference_parameter_source_valid(S_scope, ptask)',
            '$error_call_valid(S_scope, perrorcall)',
            '$call_task_valid(S_scope, ERROR_HANDLER_RESULT perrorcall)',
            '~$call_task_valid(S_scope, ptask)',
            '$call_descriptors_valid(S)',
            '$lookup(S.ENV, $ptascii("source176")) = (n_cell)',
            'S.GLOBALTABLE = (psymboltable_global)',
            '$lookup(psymboltable_global.ENV, $ptascii("source176")) = (n_cell)',
            '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
            '$lookup(S_scope.ENV, pfunction.SIGNATURE.PARAMETERS[0].NAME) = (n_cell)',
            'n_cell <- S.REFCELLS',
            '$heap_owners($heap_graph(S), HCELL n_cell) = 3',
            '$task_nodes(ptask) = eps',
            '$heap_valid($heap_graph(S))',
        ],
    },
    'supplied-ref-lossy-receive-throw': {
        'source': SOURCES['supplied-reference-integer-receive-pending'],
        'stage': ('S.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail* '
                  '-- if perrorcall.RESUME = LOSSY_REFERENCE_PARAMETER_RECEIVE porigin n_cell n_bits i z '
                  '-- if S.CURRENT = (pcallcontext) '
                  '-- if pcallcontext.FUNCTION = porigin'),
        'checks': [
            'ptask = LOSSY_REFERENCE_PARAMETER_RECEIVE porigin n_cell n_bits i z',
            '$lossy_reference_parameter_source_valid(S, ptask)',
            '$error_call_valid(S, perrorcall)',
            '$call_task_valid(S, ERROR_HANDLER_RESULT perrorcall)',
            '~$call_task_valid(S, ptask)',
            '$call_descriptors_valid(S)',
            'S.STORE[n_cell] = DEFINED (PINT 41)',
            'n_cell <- S.REFCELLS',
            '$task_nodes(ptask) = eps',
            '$heap_owners($heap_graph(S), HCELL n_cell) = 2',
            '$heap_count(HOBJECT n_exception, $tasks_nodes(S.TODO)) = 1',
            'S.GLOBALTABLE = (psymboltable_global)',
            '$lookup(psymboltable_global.ENV, $ptascii("source176")) = (n_cell)',
            '$lookup(psymboltable_global.ENV, $ptascii("original176")) = (n_original)',
            'S.STORE[n_original] = DEFINED (POBJECT n_exception)',
            'S_skip = $return_discard(S[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*], ERROR_HANDLER_RESULT perrorcall)',
            'S_skip.TODO = (THROW_SEARCH n_exception) :: ptask_tail*',
            'S_skip.STORE = S.STORE /\\ S_skip.OBJECTS = S.OBJECTS',
            'S_skip.ERRORHANDLER.CALLBACK = (perrorcall.CALLBACK)',
            'S_done = $drive_steps(S, 10000)',
            'S_done.COMPLETION = NORMAL /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps',
            '$lookup(S_done.ENV, $ptascii("caught176")) = (n_caught)',
            'S_done.STORE[n_caught] = DEFINED (POBJECT n_exception)',
            '$lookup(S_done.ENV, $ptascii("source176")) = (n_cell)',
            'S_done.STORE[n_cell] = DEFINED (PINT 41)',
            '$lookup(S_done.ENV, $ptascii("destination176")) = (n_destination)',
            'S_done.STORE[n_destination] = DEFINED (PINT 91)',
            'S_done.OBJECTS = S.OBJECTS',
            '(HCELL n_cell) <- S_done.ALLOCATIONS',
            '$heap_owners($heap_graph(S_done), HCELL n_cell) = 1',
            '$heap_valid($heap_graph(S_done))',
        ],
    },
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE))
