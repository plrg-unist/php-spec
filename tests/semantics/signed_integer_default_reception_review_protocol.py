#!/usr/bin/env python3
"""Signed default syntax retains exact provenance and real throw cleanup."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('signed_integer_default_reception_cases.json')
SOURCES = {}
for row in json.loads(CATALOGUE.read_text()):
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
    SOURCES[row['id']] = row['source']

# Retain fresh setup and the REF invocation/result, omitting the earlier mixed
# call and its histories. This selected source has no native agreement credit.
leading = SOURCES['signed-leading-holes']
leading = leading[:leading.index('$gotReceive186 = mixedReceive186(')] + leading[leading.index('$gotReceive186 = referenceReceive186('):]
assert hashlib.sha256(leading.encode()).hexdigest() == '8ad3385fee7f022abd141c7b679001fa513eb7b8b0846f65d2a995748fd4d1c1'

CASES = {
    'signed-default-integer-reference-leading': {
        'source': leading,
        'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z]',
        'checks': [
            'n_bits = 4609434218613702656 /\\ i = 1',
            '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
            '$lossy_optional_integer_mode(pfunction.SIGNATURE.PARAMETERS, true) /\\ ~$lossy_optional_integer_mode(pfunction.SIGNATURE.PARAMETERS, false)',
            'psparam_a = pfunction.SIGNATURE.PARAMETERS[0]',
            'psparam_b = pfunction.SIGNATURE.PARAMETERS[1]',
            'psparam_c = pfunction.SIGNATURE.PARAMETERS[2]',
            'psparam_a.DEFAULT = PSDEFAULT expression_a "int"',
            'expression_a = NExprUnaryMinus (NExprUnaryPlus (NScalarInt (INTEGER 7) metadata_integer) metadata_plus) metadata_minus',
            '$psnumber(expression_a) = PSINTEGER $(-7)',
            '$lossy_optional_integer_header(S, pfunction, pfunction.SIGNATURE.PARAMETERS, 0)',
            'psparam_simplified = psparam_a[.DEFAULT = PSDEFAULT (NScalarInt (INTEGER $(-7)) metadata_minus) "int"]',
            '$psnumber(NScalarInt (INTEGER $(-7)) metadata_minus) = PSINTEGER $(-7)',
            '~$lossy_optional_integer_header(S, pfunction, [psparam_simplified, psparam_b, psparam_c], 0)',
            '~$lossy_optional_integer_header(S[.POOLS = eps], pfunction, pfunction.SIGNATURE.PARAMETERS, 0)',
            'S.CURRENT = (pcallcontext)',
            'pcallcontext.ARGC = 3 /\\ pcallcontext.HOLES = [0, 1] /\\ pcallcontext.NAMED = eps',
            'pcallcontext.CALLSITE = (porigin_call)',
            '$call_argument_source(S, porigin_call) = PCALLARGUMENTS phpType7* n_field',
            '|phpType7*| = 1 /\\ $lossy_named_arguments(phpType7*)',
            '$named_call_valid(S, porigin, (porigin_call))',
            '$named_call_shape(S, porigin, (porigin_call)) = {SLOTS ([NAMED_HOLE, NAMED_HOLE, NAMED_SENT (KNOWN PNULL)]), NAMED eps}',
            '$lookup(S.ENV, psparam_a.NAME) = (n_a)',
            '$lookup(S.ENV, psparam_b.NAME) = (n_b)',
            '$lookup(S.ENV, psparam_c.NAME) = (n_cell)',
            'S.STORE[n_a] = DEFINED (PINT $(-7)) /\\ S.STORE[n_b] = DEFINED (PINT $(-11))',
            '~(n_a <- S.REFCELLS) /\\ ~(n_b <- S.REFCELLS)',
            '$heap_owners($heap_graph(S), HCELL n_a) = 1 /\\ $heap_owners($heap_graph(S), HCELL n_b) = 1',
            'S.STORE[n_cell] = DEFINED (PFLOAT 4615063718147915776)',
            'n_cell <- S.REFCELLS /\\ $heap_owners($heap_graph(S), HCELL n_cell) = 2',
            '$lossy_mixed_parameter_source_valid(S, LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z)',
            '$lossy_mixed_parameter_ready(S, 2, n_cell, n_bits)',
            '$task_nodes(LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z) = eps',
            'z_hole = $default_parameter_line(S, porigin, 0)',
            'ptask_hole = LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_a n_bits i z_hole',
            'S_hole = S[.STORE[n_a] = DEFINED (PFLOAT n_bits)][.REFCELLS = n_a :: S.REFCELLS][.ORIGIN = ($default_parameter_origin(S, porigin, 0))][.TODO = [ptask_hole]]',
            '$lossy_positional_reference_parameter_ready(S_hole, 0, n_a)',
            '$typed_receive_valid(S_hole[.TODO = [TYPE_RECEIVE porigin 0]][.ORIGIN = (porigin)], porigin, 0)',
            '~$lossy_mixed_parameter_metadata(S_hole, porigin, 0, z_hole)',
            '~$lossy_mixed_parameter_source_valid(S_hole, ptask_hole)',
            'PhpStep: S ~> S_body',
            'S_body.TODO = $call_receive_body(S, pfunction)',
            'S_body.STORE[n_cell] = DEFINED (PINT 1) /\\ S_body.STORE[n_a] = DEFINED (PINT $(-7)) /\\ S_body.STORE[n_b] = DEFINED (PINT $(-11))',
            'S_body.EVENTS = S.EVENTS',
            '$call_descriptors_valid(S_body) /\\ $heap_valid($heap_graph(S_body))',
            'S_done = $drive_steps(S_body, 2000)',
            'S_done.COMPLETION = NORMAL /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.TODO = eps',
            '~((HCELL n_a) <- S_done.ALLOCATIONS) /\\ ~((HCELL n_b) <- S_done.ALLOCATIONS)',
            'S_done.STORE[n_cell] = DEFINED (PINT 1) /\\ $heap_owners($heap_graph(S_done), HCELL n_cell) = 1',
            '$lookup(S_done.ENV, $ptascii("gotReceive186")) = (n_got)',
            'S_done.STORE[n_got] = DEFINED (PINT 1)',
            '$call_descriptors_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
        ],
    },
    'signed-default-integer-pending-late': {
        'source': SOURCES['signed-pending-late'],
        'stage': 'S.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail* -- if perrorcall.RESUME = LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z -- if S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin',
        'checks': [
            'n_bits = 4609434218613702656 /\\ i = 1',
            '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
            '$lossy_optional_integer_header(S, pfunction, pfunction.SIGNATURE.PARAMETERS, 0)',
            '~pfunction.SIGNATURE.PARAMETERS[0].REQUIRED /\\ ~pfunction.SIGNATURE.PARAMETERS[0].BYREF /\\ pfunction.SIGNATURE.PARAMETERS[1].BYREF /\\ ~pfunction.SIGNATURE.PARAMETERS[2].BYREF',
            'pcallcontext.ARGC = 3 /\\ pcallcontext.HOLES = [0, 1]',
            '$lookup(S.ENV, pfunction.SIGNATURE.PARAMETERS[0].NAME) = (n_a)',
            '$lookup(S.ENV, pfunction.SIGNATURE.PARAMETERS[1].NAME) = (n_b)',
            'S.STORE[n_a] = DEFINED (PINT $(-7)) /\\ S.STORE[n_b] = DEFINED (PINT $(-11))',
            '~(n_a <- S.REFCELLS) /\\ ~(n_b <- S.REFCELLS)',
            '$heap_owners($heap_graph(S), HCELL n_a) = 1 /\\ $heap_owners($heap_graph(S), HCELL n_b) = 1',
            'S.STORE[n_cell] = DEFINED (PFLOAT n_bits) /\\ ~(n_cell <- S.REFCELLS)',
            '$heap_owners($heap_graph(S), HCELL n_cell) = 1',
            '$lossy_mixed_parameter_source_valid(S, perrorcall.RESUME)',
            '$error_call_valid(S, perrorcall) /\\ $call_descriptors_valid(S)',
            '$task_nodes(perrorcall.RESUME) = eps',
            '$heap_count(HOBJECT n_exception, $tasks_nodes(S.TODO)) = 1',
            'PhpStep: S ~> S_skip',
            'S_skip.STORE = S.STORE /\\ S_skip.OBJECTS = S.OBJECTS',
            'S_reference_pause = $seek(S_skip, 2000)',
            'S_reference_pause.COMPLETION = NORMAL \\/ S_reference_pause.COMPLETION = BUDGET',
            'S_reference = S_reference_pause[.COMPLETION = NORMAL]',
            'S_reference.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall_reference) :: ptask_reference_tail*',
            'perrorcall_reference.RESUME = LOSSY_MIXED_PARAMETER_RECEIVE porigin_reference 2 n_reference 4609434218613702656 1 z_reference',
            'porigin_reference =/= porigin',
            '$function_at(S_reference.FUNCTIONS, porigin_reference) = (pfunction_reference)',
            '$lossy_optional_integer_header(S_reference, pfunction_reference, pfunction_reference.SIGNATURE.PARAMETERS, 0)',
            '$lossy_optional_integer_mode(pfunction_reference.SIGNATURE.PARAMETERS, true) /\\ ~$lossy_optional_integer_mode(pfunction_reference.SIGNATURE.PARAMETERS, false)',
            'S_reference.CURRENT = (pcallcontext_reference)',
            'pcallcontext_reference.ARGC = 3 /\\ pcallcontext_reference.HOLES = [0, 1]',
            '$lookup(S_reference.ENV, pfunction_reference.SIGNATURE.PARAMETERS[0].NAME) = (n_a_reference)',
            '$lookup(S_reference.ENV, pfunction_reference.SIGNATURE.PARAMETERS[1].NAME) = (n_b_reference)',
            'S_reference.STORE[n_a_reference] = DEFINED (PINT $(-7)) /\\ S_reference.STORE[n_b_reference] = DEFINED (PINT $(-11))',
            '~(n_a_reference <- S_reference.REFCELLS) /\\ ~(n_b_reference <- S_reference.REFCELLS)',
            '$heap_owners($heap_graph(S_reference), HCELL n_a_reference) = 1 /\\ $heap_owners($heap_graph(S_reference), HCELL n_b_reference) = 1',
            '~((HCELL n_a) <- S_reference.ALLOCATIONS) /\\ ~((HCELL n_b) <- S_reference.ALLOCATIONS) /\\ ~((HCELL n_cell) <- S_reference.ALLOCATIONS)',
            'S_reference.STORE[n_reference] = DEFINED (PFLOAT 4615063718147915776)',
            'n_reference <- S_reference.REFCELLS /\\ $heap_owners($heap_graph(S_reference), HCELL n_reference) = 2',
            '$lossy_mixed_parameter_source_valid(S_reference, perrorcall_reference.RESUME)',
            '$error_call_valid(S_reference, perrorcall_reference) /\\ $call_descriptors_valid(S_reference)',
            '$task_nodes(perrorcall_reference.RESUME) = eps',
            '$heap_count(HOBJECT n_exception, $tasks_nodes(S_reference.TODO)) = 1',
            'S_done = $drive_steps(S_reference, 2000)',
            'S_done.COMPLETION = NORMAL /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.TODO = eps',
            '~((HCELL n_a_reference) <- S_done.ALLOCATIONS) /\\ ~((HCELL n_b_reference) <- S_done.ALLOCATIONS)',
            'S_done.STORE[n_reference] = DEFINED (PFLOAT 4615063718147915776) /\\ $heap_owners($heap_graph(S_done), HCELL n_reference) = 1',
            '$lookup(S_done.ENV, $ptascii("destinationReceive186")) = (n_destination)',
            'S_done.STORE[n_destination] = DEFINED (PINT 91)',
            '$lookup(S_done.ENV, $ptascii("originalReceive186")) = (n_original)',
            '$lookup(S_done.ENV, $ptascii("caughtReceive186")) = (n_caught)',
            'S_done.STORE[n_original] = DEFINED (POBJECT n_exception) /\\ S_done.STORE[n_caught] = DEFINED (POBJECT n_exception)',
            '$throwable_previous_id(S_done, n_exception) = eps',
            '$call_descriptors_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
        ],
    },
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE))
