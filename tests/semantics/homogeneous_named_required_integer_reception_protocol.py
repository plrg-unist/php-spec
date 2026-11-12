#!/usr/bin/env python3
"""Named required integer reception borrows cells and keeps sent value copies."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('homogeneous_named_required_integer_reception_cases.json')
SOURCES = {}
for row in json.loads(CATALOGUE.read_text()):
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
    SOURCES[row['id']] = row['source']

CASES = {}
for mode in ('value', 'reference'):
    reference = mode == 'reference'
    checks = [
        'n_bits = 4609434218613702656 /\\ i = 1',
        '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
        '|pfunction.SIGNATURE.PARAMETERS| = 1',
        '$lossy_required_integer_parameters(pfunction.SIGNATURE.PARAMETERS)',
        'S.CURRENT = (pcallcontext)',
        'pcallcontext.ARGC = 1 /\\ pcallcontext.HOLES = eps /\\ pcallcontext.NAMED = eps',
        'pcallcontext.CALLSITE = (porigin_call)',
        '$call_argument_source(S, porigin_call) = PCALLARGUMENTS phpType7* n_field',
        '|phpType7*| = 1 /\\ $lossy_named_arguments(phpType7*)',
        '$named_call_valid(S, porigin, (porigin_call))',
        '$named_call_shape(S, porigin, (porigin_call)) = {SLOTS ([NAMED_SENT (KNOWN PNULL)]), NAMED eps}',
        '$lookup(S.ENV, pfunction.SIGNATURE.PARAMETERS[0].NAME) = (n_cell)',
        'S.GLOBALTABLE = (psymboltable_global)',
        '$lookup(psymboltable_global.ENV, $ptascii("xNamed183")) = (n_global)',
        'S.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
        '$lossy_named_parameter_source_valid(S, LOSSY_NAMED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z)',
        '$lossy_mixed_parameter_ready(S, 0, n_cell, n_bits)',
        '$task_nodes(LOSSY_NAMED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z) = eps',
        '~$lossy_named_parameter_metadata(S[.CURRENT = (pcallcontext[.ARGC = 0])], porigin, 0, z)',
        '~$lossy_named_parameter_metadata(S[.CURRENT = (pcallcontext[.ARGC = 2])], porigin, 0, z)',
        '~$lossy_named_parameter_metadata(S[.CURRENT = (pcallcontext[.HOLES = [0]])], porigin, 0, z)',
        '~$lossy_named_parameter_source_valid(S, LOSSY_NAMED_PARAMETER_RECEIVE porigin 1 n_cell n_bits i z)',
        '~$lossy_named_parameter_source_valid(S, LOSSY_NAMED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i $(z + 1))',
        'S.CODE = [pcode]',
        'S_strict = S[.CODE = [pcode[.STRICT = true]]]',
        '$typed_caller_strict(S_strict)',
        '~$lossy_named_parameter_metadata(S_strict, porigin, 0, z)',
        'psparam = pfunction.SIGNATURE.PARAMETERS[0]',
        '~$lossy_required_integer_parameters([psparam[.REQUIRED = false]])',
        '~$lossy_required_integer_parameters([psparam[.VARIADIC = true]])',
        'S_changed = S[.STORE[n_cell] = DEFINED (PINT 47)]',
        '$lossy_named_parameter_source_valid(S_changed, LOSSY_NAMED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z)',
    ]
    if reference:
        checks += [
            'pfunction.SIGNATURE.PARAMETERS[0].BYREF /\\ n_cell = n_global',
            'n_cell <- S.REFCELLS /\\ $heap_owners($heap_graph(S), HCELL n_cell) = 2',
            '$lossy_positional_reference_parameter_ready(S, 0, n_cell)',
            '$lossy_mixed_parameter_ready(S_changed, 0, n_cell, n_bits)',
            'S_unmarked = S[.REFCELLS = eps]',
            '~$lossy_mixed_parameter_ready(S_unmarked, 0, n_cell, n_bits)',
        ]
    else:
        checks += [
            '~pfunction.SIGNATURE.PARAMETERS[0].BYREF /\\ n_cell =/= n_global',
            'S.STORE[n_cell] = DEFINED (PFLOAT n_bits)',
            '~(n_cell <- S.REFCELLS) /\\ $heap_owners($heap_graph(S), HCELL n_cell) = 1',
            '~$lossy_positional_reference_parameter_ready(S, 0, n_cell)',
            '~$lossy_mixed_parameter_ready(S_changed, 0, n_cell, n_bits)',
            'PhpStep: S_changed ~> S_refused',
            'S_refused.COMPLETION = UNSUPPORTED text_refused',
            'S_refused.STORE = S_changed.STORE /\\ S_refused.TODO = S_changed.TODO',
        ]
    checks += [
        'S_budget = $drive(S, 0)',
        'S_budget.COMPLETION = BUDGET /\\ S_budget.STORE = S.STORE /\\ S_budget.TODO = S.TODO',
        '$call_descriptors_valid(S_budget)',
        '$drive(S_budget[.COMPLETION = NORMAL], 1) = $drive(S, 1)',
        'PhpStep: S ~> S_body',
        'S_body.TODO = $call_receive_body(S, pfunction)',
        'S_body.STORE[n_cell] = DEFINED (PINT 1)',
        'S_body.EVENTS = S.EVENTS',
        '$call_descriptors_valid(S_body) /\\ $heap_valid($heap_graph(S_body))',
        'S_done = $drive_steps(S_body, 2000)',
        'S_done.COMPLETION = NORMAL /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps',
        '$lookup(S_done.ENV, $ptascii("gotNamed183")) = (n_got)',
        'S_done.STORE[n_got] = DEFINED (PINT 1)',
        '$heap_valid($heap_graph(S_done))',
    ]
    if reference:
        checks += [
            'S_done.STORE[n_global] = DEFINED (PINT 1)',
            '$heap_owners($heap_graph(S_done), HCELL n_global) = 1',
        ]
    else:
        checks += [
            'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
            '~((HCELL n_cell) <- S_done.ALLOCATIONS)',
        ]
    CASES['named-required-integer-unary-' + mode] = {
        'source': SOURCES['unary-' + mode],
        'stage': 'S.TODO = [LOSSY_NAMED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
        'checks': checks,
    }

CASES['named-required-integer-value-order'] = {
    'source': SOURCES['reverse-order'],
    'stage': 'S.TODO = [LOSSY_NAMED_PARAMETER_RECEIVE porigin n n_cell n_bits i z]',
    'checks': [
        'n = 0 /\\ n_bits = 4609434218613702656 /\\ i = 1',
        '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
        '|pfunction.SIGNATURE.PARAMETERS| = 2 /\\ $lossy_positional_parameters(pfunction.SIGNATURE.PARAMETERS)',
        'S.CURRENT = (pcallcontext)',
        'pcallcontext.ARGC = 2 /\\ pcallcontext.HOLES = eps',
        'pcallcontext.CALLSITE = (porigin_call)',
        '$call_argument_source(S, porigin_call) = PCALLARGUMENTS phpType7* n_field',
        '$named_arg_target(pfunction, phpType7*[0], 0) = NAMED_POSITION 1',
        '$named_arg_target(pfunction, phpType7*[1], 1) = NAMED_POSITION 0',
        '$lookup(S.ENV, pfunction.SIGNATURE.PARAMETERS[1].NAME) = (n_second)',
        'n_cell =/= n_second /\\ S.STORE[n_second] = DEFINED (PFLOAT 4612811918334230528)',
        '$heap_owners($heap_graph(S), HCELL n_cell) = 1 /\\ $heap_owners($heap_graph(S), HCELL n_second) = 1',
        'S.GLOBALTABLE = (psymboltable_global)',
        '$lookup(psymboltable_global.ENV, $ptascii("xNamed183")) = (n_x)',
        '$lookup(psymboltable_global.ENV, $ptascii("yNamed183")) = (n_y)',
        'S.STORE[n_x] = DEFINED (PFLOAT 4616752568008179712) /\\ S.STORE[n_y] = DEFINED (PFLOAT 4615063718147915776)',
        '$lossy_named_parameter_source_valid(S, LOSSY_NAMED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z)',
        'PhpStep: S ~> S_next',
        'S_next.TODO = [TYPE_RECEIVE porigin 1]',
        'S_next.STORE[n_cell] = DEFINED (PINT 1)',
        '$lossy_named_parameter_capture(S_next) = (ptask_second)',
        'ptask_second = LOSSY_NAMED_PARAMETER_RECEIVE porigin 1 n_second 4612811918334230528 2 z_second',
        'S_second_pause = $seek(S_next, 2000)',
        'S_second_pause.COMPLETION = NORMAL \\/ S_second_pause.COMPLETION = BUDGET',
        'S_second = S_second_pause[.COMPLETION = NORMAL]',
        'S_second.TODO = [ptask_second]',
        'S_second.STORE[n_cell] = DEFINED (PINT 1) /\\ S_second.STORE[n_second] = DEFINED (PFLOAT 4612811918334230528)',
        'S_second.STORE[n_x] = DEFINED (PFLOAT 4617878467915022336) /\\ S_second.STORE[n_y] = DEFINED (PFLOAT 4619004367821864960)',
        '$lossy_named_parameter_source_valid(S_second, ptask_second)',
        '$lossy_mixed_parameter_ready(S_second, 1, n_second, 4612811918334230528)',
        '$task_nodes(ptask_second) = eps',
        'S_previous_changed = S_second[.STORE[n_cell] = DEFINED (PFLOAT 4616752568008179712)]',
        '$lossy_named_parameter_source_valid(S_previous_changed, ptask_second)',
        'PhpStep: S_second ~> S_body',
        'S_body.TODO = $call_receive_body(S_second, pfunction)',
        'S_body.STORE[n_cell] = DEFINED (PINT 1) /\\ S_body.STORE[n_second] = DEFINED (PINT 2)',
        'S_body.STORE[n_x] = S_second.STORE[n_x] /\\ S_body.STORE[n_y] = S_second.STORE[n_y]',
        '$call_descriptors_valid(S_body) /\\ $heap_valid($heap_graph(S_body))',
    ],
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE))
