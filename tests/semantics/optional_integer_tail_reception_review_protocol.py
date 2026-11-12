#!/usr/bin/env python3
"""Optional-c throws retain named default holes and value/reference modes."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('optional_integer_tail_reception_cases.json')
row = next(row for row in json.loads(CATALOGUE.read_text()) if row['id'] == 'pending-optional')
assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

CASES = {
    'optional-integer-named-pending-modes': {
        'source': row['source'],
        'stage': ('S.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail* '
                  '-- if perrorcall.RESUME = LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z '
                  '-- if S.CURRENT = (pcallcontext) '
                  '-- if pcallcontext.FUNCTION = porigin'),
        'checks': [
            'n_bits = 4609434218613702656 /\\ i = 1',
            '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
            'pfunction.SIGNATURE.PARAMETERS = [psparam_a, psparam_b, psparam_c]',
            '~psparam_a.BYREF /\\ psparam_b.BYREF /\\ ~psparam_c.BYREF',
            'pcallcontext.ARGC = 3 /\\ pcallcontext.HOLES = [1] /\\ pcallcontext.NAMED = eps',
            '$lookup(S.ENV, psparam_a.NAME) = (n_a)',
            '$lookup(S.ENV, psparam_b.NAME) = (n_b)',
            'S.STORE[n_a] = DEFINED (PINT 2) /\\ S.STORE[n_b] = DEFINED (PINT 7)',
            '~(n_b <- S.REFCELLS) /\\ $heap_owners($heap_graph(S), HCELL n_b) = 1',
            'S.STORE[n_cell] = DEFINED (PFLOAT n_bits)',
            '~(n_cell <- S.REFCELLS) /\\ $heap_owners($heap_graph(S), HCELL n_cell) = 1',
            'S.GLOBALTABLE = (psymboltable_global)',
            '$lookup(psymboltable_global.ENV, $ptascii("xTail")) = (n_global)',
            'S.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
            '$lossy_mixed_parameter_source_valid(S, perrorcall.RESUME)',
            '$lossy_mixed_parameter_ready(S, 2, n_cell, n_bits)',
            '$error_call_valid(S, perrorcall) /\\ $call_descriptors_valid(S)',
            '~$call_task_valid(S, perrorcall.RESUME)',
            '$task_nodes(perrorcall.RESUME) = eps',
            '$heap_count(HOBJECT n_exception, $tasks_nodes(S.TODO)) = 1',
            '$throwable_previous_id(S, n_exception) = eps',
            '$lossy_optional_integer_header(S, pfunction, pfunction.SIGNATURE.PARAMETERS, 0)',
            '~$lossy_optional_integer_header(S, pfunction, [psparam_a], 0)',
            '~$lossy_optional_integer_header(S, pfunction, [psparam_b, psparam_c], 0)',
            '~$lossy_optional_integer_header(S, pfunction, [psparam_a, psparam_b, psparam_a], 0)',
            '~$lossy_optional_integer_header(S, pfunction, [psparam_a, psparam_b[.VARIADIC = true], psparam_c], 0)',
            '~$lossy_optional_integer_mode([psparam_a[.BYREF = true], psparam_b, psparam_c[.BYREF = true]], false)',
            '~$lossy_optional_integer_mode([psparam_a, psparam_b[.BYREF = false], psparam_c], true)',
            'pfunction.DEFAULTS = [pdefault_b, pdefault_c]',
            'psparam_b.DEFAULT = PSDEFAULT (NScalarInt (INTEGER 7) metadata_b) "int"',
            '~$lossy_optional_integer_header(S, pfunction[.DEFAULTS = [pdefault_b[.KIND = PDDEFERRED], pdefault_c]], pfunction.SIGNATURE.PARAMETERS, 0)',
            '~$lossy_optional_integer_header(S, pfunction[.DEFAULTS = [pdefault_b[.INDEX = 0], pdefault_c]], pfunction.SIGNATURE.PARAMETERS, 0)',
            '~$lossy_optional_integer_header(S, pfunction[.DEFAULTS = [pdefault_b[.ORIGIN = pdefault_c.ORIGIN], pdefault_c]], pfunction.SIGNATURE.PARAMETERS, 0)',
            '~$lossy_optional_integer_header(S, pfunction, [psparam_a, psparam_b[.DEFAULT = PSNONE], psparam_c], 0)',
            '~$lossy_optional_integer_header(S, pfunction, [psparam_a, psparam_b[.DEFAULT = PSDEFAULT (NScalarInt (INTEGER 8) metadata_b) "int"], psparam_c], 0)',
            '~$lossy_optional_integer_header(S[.POOLS = eps], pfunction, pfunction.SIGNATURE.PARAMETERS, 0)',
            'S_skip = $return_discard(S[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*], ERROR_HANDLER_RESULT perrorcall)',
            'S_skip.STORE = S.STORE /\\ S_skip.OBJECTS = S.OBJECTS',
            'S_reference_pause = $seek(S_skip, 2000)',
            'S_reference_pause.COMPLETION = NORMAL \\/ S_reference_pause.COMPLETION = BUDGET',
            'S_reference = S_reference_pause[.COMPLETION = NORMAL]',
            'S_reference.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall_reference) :: ptask_reference_tail*',
            'perrorcall_reference.RESUME = LOSSY_MIXED_PARAMETER_RECEIVE porigin_reference 2 n_reference n_bits_reference i_reference z_reference',
            'porigin_reference =/= porigin /\\ n_reference = n_global',
            '$function_at(S_reference.FUNCTIONS, porigin_reference) = (pfunction_reference)',
            'pfunction_reference.SIGNATURE.PARAMETERS[0].BYREF /\\ ~pfunction_reference.SIGNATURE.PARAMETERS[1].BYREF /\\ pfunction_reference.SIGNATURE.PARAMETERS[2].BYREF',
            'S_reference.CURRENT = (pcallcontext_reference)',
            'pcallcontext_reference.ARGC = 3 /\\ pcallcontext_reference.HOLES = [1]',
            '$lookup(S_reference.ENV, pfunction_reference.SIGNATURE.PARAMETERS[1].NAME) = (n_default_reference)',
            'S_reference.STORE[n_default_reference] = DEFINED (PINT 7)',
            '~(n_default_reference <- S_reference.REFCELLS) /\\ $heap_owners($heap_graph(S_reference), HCELL n_default_reference) = 1',
            '~((HCELL n_cell) <- S_reference.ALLOCATIONS) /\\ ~((HCELL n_b) <- S_reference.ALLOCATIONS)',
            'S_reference.STORE[n_reference] = DEFINED (PFLOAT 4615063718147915776)',
            'n_bits_reference = 4609434218613702656 /\\ i_reference = 1',
            'n_reference <- S_reference.REFCELLS /\\ $heap_owners($heap_graph(S_reference), HCELL n_reference) = 2',
            '$lossy_mixed_parameter_source_valid(S_reference, perrorcall_reference.RESUME)',
            '$lossy_mixed_parameter_ready(S_reference, 2, n_reference, n_bits_reference)',
            '~$lossy_parameter_ready(S_reference, n_reference, n_bits_reference)',
            '$error_call_valid(S_reference, perrorcall_reference) /\\ $call_descriptors_valid(S_reference)',
            '$task_nodes(perrorcall_reference.RESUME) = eps',
            '$heap_count(HOBJECT n_exception, $tasks_nodes(S_reference.TODO)) = 1',
            '$throwable_previous_id(S_reference, n_exception) = eps',
            'S_reference_skip = $return_discard(S_reference[.TODO = (THROW_SEARCH n_exception) :: ptask_reference_tail*], ERROR_HANDLER_RESULT perrorcall_reference)',
            'S_reference_skip.STORE = S_reference.STORE /\\ S_reference_skip.OBJECTS = S_reference.OBJECTS',
            'S_done = $drive_steps(S_reference, 10000)',
            'S_done.COMPLETION = NORMAL /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.TODO = eps',
            '~((HCELL n_default_reference) <- S_done.ALLOCATIONS)',
            'S_done.STORE[n_reference] = DEFINED (PFLOAT 4615063718147915776)',
            '$heap_owners($heap_graph(S_done), HCELL n_reference) = 1',
            '$lookup(S_done.ENV, $ptascii("originalTail")) = (n_original)',
            '$lookup(S_done.ENV, $ptascii("caughtTail")) = (n_caught)',
            'S_done.STORE[n_original] = DEFINED (POBJECT n_exception)',
            'S_done.STORE[n_caught] = DEFINED (POBJECT n_exception)',
            '$throwable_previous_id(S_done, n_exception) = eps',
            '$lookup(S_done.ENV, $ptascii("destinationTail")) = (n_destination)',
            'S_done.STORE[n_destination] = DEFINED (PINT 91)',
            '~$lossy_mixed_parameter_source_valid(S_done, perrorcall_reference.RESUME)',
            '$call_descriptors_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
        ],
    },
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE))
