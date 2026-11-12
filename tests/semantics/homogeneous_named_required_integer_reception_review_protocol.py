#!/usr/bin/env python3
"""Uniform named required calls preserve live references and abrupt priority."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('homogeneous_named_required_integer_reception_cases.json')
SOURCES = {}
for row in json.loads(CATALOGUE.read_text()):
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
    SOURCES[row['id']] = row['source']

# Retain initial setup and the REF invocation/result, omitting the earlier VAL call.
order = SOURCES['reverse-order']
order = order[:order.index('$gotNamed183 = valueNamed183(')] + order[order.index('$gotNamed183 = referenceNamed183('):]
assert hashlib.sha256(order.encode()).hexdigest() == '29a15c08a57202441487248d8917706c84b17a4d56dc7f7a5295cbe3ab2dc5db'
shared = SOURCES['same-cell']
shared = shared[:shared.index('$gotNamed183 = valueNamed183(')] + shared[shared.index('$gotNamed183 = referenceNamed183('):]
assert hashlib.sha256(shared.encode()).hexdigest() == '4d754e3570c7a22466f57732a9574700cec429ad4c737c8db388b052083b12bc'

# Isolate one original pending call per fixture, retaining its setup and catch.
pending = SOURCES['pending-second']
prefix = pending[:pending.index('try { $destinationNamed183 = valueNamed183(')]
pending_value = pending[:pending.index('\n$xNamed183 = 1.5;\n$yNamed183 = 2.5;\n$countNamed183 = 0;\ntry { $destinationNamed183 = referenceNamed183(')] + '\n'
pending_reference = prefix + pending[pending.index('try { $destinationNamed183 = referenceNamed183('):]
assert hashlib.sha256(pending_value.encode()).hexdigest() == '3c54e122bf8ff9ec06dace4a906113250cbb5e3c864d1664dee606b2c543e6e4'
assert hashlib.sha256(pending_reference.encode()).hexdigest() == 'ed2685477503d881405771761f2e2887ad27e2bd7d5569c7d50761ef9d3acec3'

# Keep both required-hole catches and normal prefix receives; omit later throws.
missing = SOURCES['missing-priority']
missing = missing[:missing.index('\n$xNamed183 = 1.5;\n$throwNamed183 = true;')] + '\n'
assert hashlib.sha256(missing.encode()).hexdigest() == 'c1ca127d2f5a1892b9e4c701c8ce522badf78fffcae6832ad69ebd0de964a49d'

CASES = {
    'named-required-integer-reference-order': {
        'source': order,
        'stage': 'S.TODO = [LOSSY_NAMED_PARAMETER_RECEIVE porigin n n_cell n_bits i z]',
        'checks': [
            'n = 0 /\\ n_bits = 4609434218613702656 /\\ i = 1',
            '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
            '|pfunction.SIGNATURE.PARAMETERS| = 2 /\\ $lossy_positional_reference_parameters(pfunction.SIGNATURE.PARAMETERS)',
            'S.CURRENT = (pcallcontext)',
            'pcallcontext.ARGC = 2 /\\ pcallcontext.HOLES = eps /\\ pcallcontext.NAMED = eps',
            'pcallcontext.CALLSITE = (porigin_call)',
            '$call_argument_source(S, porigin_call) = PCALLARGUMENTS phpType7* n_field',
            '$named_arg_target(pfunction, phpType7*[0], 0) = NAMED_POSITION 1',
            '$named_arg_target(pfunction, phpType7*[1], 1) = NAMED_POSITION 0',
            '$lookup(S.ENV, pfunction.SIGNATURE.PARAMETERS[0].NAME) = (n_cell)',
            '$lookup(S.ENV, pfunction.SIGNATURE.PARAMETERS[1].NAME) = (n_second)',
            'n_cell =/= n_second',
            'S.STORE[n_cell] = DEFINED (PFLOAT 4616752568008179712) /\\ S.STORE[n_second] = DEFINED (PFLOAT 4615063718147915776)',
            'n_cell <- S.REFCELLS /\\ n_second <- S.REFCELLS',
            '$heap_owners($heap_graph(S), HCELL n_cell) = 2 /\\ $heap_owners($heap_graph(S), HCELL n_second) = 2',
            '$lossy_named_parameter_source_valid(S, LOSSY_NAMED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z)',
            'PhpStep: S ~> S_next',
            'S_next.TODO = [TYPE_RECEIVE porigin 1]',
            'S_next.STORE[n_cell] = DEFINED (PINT 1)',
            '$lossy_named_parameter_capture(S_next) = (ptask_second)',
            'ptask_second = LOSSY_NAMED_PARAMETER_RECEIVE porigin 1 n_second 4615063718147915776 3 z_second',
            'S_second_pause = $seek(S_next, 2000)',
            'S_second_pause.COMPLETION = NORMAL \\/ S_second_pause.COMPLETION = BUDGET',
            'S_second = S_second_pause[.COMPLETION = NORMAL]',
            'S_second.TODO = [ptask_second]',
            'S_second.STORE[n_cell] = DEFINED (PFLOAT 4617878467915022336) /\\ S_second.STORE[n_second] = DEFINED (PFLOAT 4619004367821864960)',
            '$lossy_named_parameter_source_valid(S_second, ptask_second)',
            '$lossy_mixed_parameter_ready(S_second, 1, n_second, 4615063718147915776)',
            '~$lossy_parameter_ready(S_second, n_second, 4615063718147915776)',
            '$task_nodes(ptask_second) = eps',
            'PhpStep: S_second ~> S_body',
            'S_body.TODO = $call_receive_body(S_second, pfunction)',
            'S_body.STORE[n_cell] = DEFINED (PFLOAT 4617878467915022336) /\\ S_body.STORE[n_second] = DEFINED (PINT 3)',
            '$call_descriptors_valid(S_body) /\\ $heap_valid($heap_graph(S_body))',
            'S_done = $drive_steps(S_body, 2000)',
            'S_done.COMPLETION = NORMAL /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.TODO = eps',
            '$lookup(S_done.ENV, $ptascii("gotNamed183")) = (n_got)',
            'S_done.STORE[n_got] = DEFINED (PINT 3)',
            'S_done.STORE[n_cell] = DEFINED (PFLOAT 4617878467915022336) /\\ S_done.STORE[n_second] = DEFINED (PINT 3)',
            '$heap_owners($heap_graph(S_done), HCELL n_cell) = 1 /\\ $heap_owners($heap_graph(S_done), HCELL n_second) = 1',
            '$call_descriptors_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
        ],
    },
    'named-required-integer-reference-shared': {
        'source': shared,
        'stage': 'S.TODO = [LOSSY_NAMED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
        'checks': [
            'n_bits = 4609434218613702656 /\\ i = 1',
            '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
            '$lossy_positional_reference_parameters(pfunction.SIGNATURE.PARAMETERS)',
            'S.CURRENT = (pcallcontext)',
            'pcallcontext.ARGC = 2 /\\ pcallcontext.HOLES = eps',
            '$lookup(S.ENV, pfunction.SIGNATURE.PARAMETERS[0].NAME) = (n_cell)',
            '$lookup(S.ENV, pfunction.SIGNATURE.PARAMETERS[1].NAME) = (n_cell)',
            'S.STORE[n_cell] = DEFINED (PFLOAT 4615063718147915776)',
            'n_cell <- S.REFCELLS /\\ $heap_owners($heap_graph(S), HCELL n_cell) = 3',
            'S.GLOBALTABLE = (psymboltable_global)',
            '$lookup(psymboltable_global.ENV, $ptascii("countNamed183")) = (n_count)',
            'S.STORE[n_count] = DEFINED (PINT 1)',
            '$lossy_named_parameter_source_valid(S, LOSSY_NAMED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z)',
            '$task_nodes(LOSSY_NAMED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z) = eps',
            'PhpStep: S ~> S_next',
            'S_next.TODO = [TYPE_RECEIVE porigin 1]',
            'S_next.STORE[n_cell] = DEFINED (PINT 1)',
            '$lossy_named_parameter_capture(S_next) = eps',
            'PhpStep: S_next ~> S_body',
            'S_body.TODO = $call_receive_body(S_next, pfunction)',
            'S_body.EVENTS = S.EVENTS /\\ S_body.STORE[n_count] = DEFINED (PINT 1)',
            '$call_descriptors_valid(S_body) /\\ $heap_valid($heap_graph(S_body))',
            'S_done = $drive_steps(S_body, 2000)',
            'S_done.COMPLETION = NORMAL /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.TODO = eps',
            'S_done.STORE[n_cell] = DEFINED (PINT 1) /\\ $heap_owners($heap_graph(S_done), HCELL n_cell) = 1',
            'S_done.STORE[n_count] = DEFINED (PINT 1)',
            '$lookup(S_done.ENV, $ptascii("gotNamed183")) = (n_got)',
            'S_done.STORE[n_got] = DEFINED (PINT 1)',
            '$call_descriptors_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
        ],
    },
    'named-required-integer-missing-prefix': {
        'source': missing,
        'stage': 'S.TODO = [LOSSY_NAMED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
        'checks': [
            'n_bits = 4609434218613702656 /\\ i = 1',
            '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
            '|pfunction.SIGNATURE.PARAMETERS| = 2 /\\ $lossy_positional_parameters(pfunction.SIGNATURE.PARAMETERS)',
            'S.CURRENT = (pcallcontext)',
            'pcallcontext.ARGC = 1 /\\ pcallcontext.HOLES = eps',
            '$lookup(S.ENV, pfunction.SIGNATURE.PARAMETERS[1].NAME) = eps',
            'S.GLOBALTABLE = (psymboltable_global)',
            '$lookup(psymboltable_global.ENV, $ptascii("xNamed183")) = (n_global)',
            'S.STORE[n_cell] = DEFINED (PFLOAT n_bits) /\\ S.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
            '$lossy_named_parameter_source_valid(S, LOSSY_NAMED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z)',
            'PhpStep: S ~> S_missing',
            'S_missing.TODO = [TYPE_RECEIVE porigin 1]',
            'S_missing.STORE[n_cell] = DEFINED (PINT 1)',
            '$lossy_named_parameter_capture(S_missing) = eps',
            'PhpStep: S_missing ~> S_error',
            'S_error.COMPLETION = THROWN "ArgumentCountError" ptbytes_missing z_missing',
            'S_error.STORE = S_missing.STORE /\\ S_error.EVENTS = S_missing.EVENTS',
            'S_reference_pause = $seek($drive_steps(S_error, 0), 2000)',
            'S_reference_pause.COMPLETION = NORMAL \\/ S_reference_pause.COMPLETION = BUDGET',
            'S_reference = S_reference_pause[.COMPLETION = NORMAL]',
            'S_reference.TODO = [LOSSY_NAMED_PARAMETER_RECEIVE porigin_reference 0 n_global 4609434218613702656 1 z_reference]',
            'porigin_reference =/= porigin',
            '$function_at(S_reference.FUNCTIONS, porigin_reference) = (pfunction_reference)',
            '$lossy_positional_reference_parameters(pfunction_reference.SIGNATURE.PARAMETERS)',
            'S_reference.CURRENT = (pcallcontext_reference)',
            'pcallcontext_reference.ARGC = 1 /\\ pcallcontext_reference.HOLES = eps',
            'S_reference.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
            '$lossy_named_parameter_source_valid(S_reference, LOSSY_NAMED_PARAMETER_RECEIVE porigin_reference 0 n_global 4609434218613702656 1 z_reference)',
            'PhpStep: S_reference ~> S_reference_missing',
            'S_reference_missing.TODO = [TYPE_RECEIVE porigin_reference 1]',
            'S_reference_missing.STORE[n_global] = DEFINED (PINT 1)',
            '$lossy_named_parameter_capture(S_reference_missing) = eps',
            'PhpStep: S_reference_missing ~> S_reference_error',
            'S_reference_error.COMPLETION = THROWN "ArgumentCountError" ptbytes_reference z_reference_missing',
            'S_reference_error.STORE = S_reference_missing.STORE /\\ S_reference_error.EVENTS = S_reference_missing.EVENTS',
            'S_done = $drive_steps(S_reference_error, 2000)',
            'S_done.COMPLETION = NORMAL /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.TODO = eps',
            'S_done.STORE[n_global] = DEFINED (PINT 1)',
            '$lookup(S_done.ENV, $ptascii("destinationNamed183")) = (n_destination)',
            'S_done.STORE[n_destination] = DEFINED (PINT 91)',
            '$call_descriptors_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
        ],
    },
}

for mode in ('value', 'reference'):
    reference = mode == 'reference'
    checks = [
        '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
        '|pfunction.SIGNATURE.PARAMETERS| = 2',
        'S.CURRENT = (pcallcontext)',
        'pcallcontext.ARGC = 2 /\\ pcallcontext.HOLES = eps',
        '$lookup(S.ENV, pfunction.SIGNATURE.PARAMETERS[0].NAME) = (n_first)',
        'S.GLOBALTABLE = (psymboltable_global)',
        '$lookup(psymboltable_global.ENV, $ptascii("xNamed183")) = (n_x)',
        '$lookup(psymboltable_global.ENV, $ptascii("yNamed183")) = (n_y)',
        'S.STORE[n_x] = DEFINED (PFLOAT 4617878467915022336) /\\ S.STORE[n_y] = DEFINED (PFLOAT 4619004367821864960)',
        '$lossy_named_parameter_source_valid(S, perrorcall.RESUME)',
        '$lossy_mixed_parameter_ready(S, 1, n_cell, n_bits)',
        '$error_call_valid(S, perrorcall) /\\ $call_descriptors_valid(S)',
        '~$call_task_valid(S, perrorcall.RESUME)',
        '$task_nodes(perrorcall.RESUME) = eps',
        '$heap_count(HOBJECT n_exception, $tasks_nodes(S.TODO)) = 1',
        '$throwable_previous_id(S, n_exception) = eps',
        'S_skip = $return_discard(S[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*], ERROR_HANDLER_RESULT perrorcall)',
        'S_skip.STORE = S.STORE /\\ S_skip.OBJECTS = S.OBJECTS',
    ]
    if reference:
        checks += [
            'n_bits = 4616752568008179712 /\\ i = 4',
            '$lossy_positional_reference_parameters(pfunction.SIGNATURE.PARAMETERS)',
            'n_first = n_x /\\ n_cell = n_y',
            'n_first <- S.REFCELLS /\\ n_cell <- S.REFCELLS',
            '$heap_owners($heap_graph(S), HCELL n_first) = 2 /\\ $heap_owners($heap_graph(S), HCELL n_cell) = 2',
            '~$lossy_parameter_ready(S, n_cell, n_bits)',
        ]
    else:
        checks += [
            'n_bits = 4612811918334230528 /\\ i = 2',
            '$lossy_positional_parameters(pfunction.SIGNATURE.PARAMETERS)',
            'n_first =/= n_x /\\ n_cell =/= n_y',
            'S.STORE[n_first] = DEFINED (PINT 1) /\\ S.STORE[n_cell] = DEFINED (PFLOAT n_bits)',
            '~(n_first <- S.REFCELLS) /\\ ~(n_cell <- S.REFCELLS)',
            '$heap_owners($heap_graph(S), HCELL n_first) = 1 /\\ $heap_owners($heap_graph(S), HCELL n_cell) = 1',
        ]
    checks += [
        'S_done = $drive_steps(S, 2000)',
        'S_done.COMPLETION = NORMAL /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.TODO = eps',
        'S_done.STORE[n_x] = DEFINED (PFLOAT 4617878467915022336) /\\ S_done.STORE[n_y] = DEFINED (PFLOAT 4619004367821864960)',
        '$lookup(S_done.ENV, $ptascii("destinationNamed183")) = (n_destination)',
        'S_done.STORE[n_destination] = DEFINED (PINT 91)',
        '$lookup(S_done.ENV, $ptascii("originalNamed183")) = (n_original)',
        '$lookup(S_done.ENV, $ptascii("caughtNamed183")) = (n_caught)',
        'S_done.STORE[n_original] = DEFINED (POBJECT n_exception) /\\ S_done.STORE[n_caught] = DEFINED (POBJECT n_exception)',
        '$throwable_previous_id(S_done, n_exception) = eps',
        '$call_descriptors_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
    ]
    if reference:
        checks += ['$heap_owners($heap_graph(S_done), HCELL n_x) = 1 /\\ $heap_owners($heap_graph(S_done), HCELL n_y) = 1']
    else:
        checks += ['~((HCELL n_first) <- S_done.ALLOCATIONS) /\\ ~((HCELL n_cell) <- S_done.ALLOCATIONS)']
    CASES['named-required-integer-pending-' + mode] = {
        'source': pending_reference if reference else pending_value,
        'stage': ('S.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail* '
                  '-- if perrorcall.RESUME = LOSSY_NAMED_PARAMETER_RECEIVE porigin 1 n_cell n_bits i z '
                  '-- if S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin'),
        'checks': checks,
    }

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE))
