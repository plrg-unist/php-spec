#!/usr/bin/env python3
"""Mixed CV sends retain formal order, genuine supplied authority and cleanup."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('mixed_cv_integer_reception_cases.json')
SOURCES = {}
for row in json.loads(CATALOGUE.read_text()):
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
    SOURCES[row['id']] = row['source']

# Retain fresh setup and the REF call/result; move its named b to a positional
# second slot, preserving the same shared CV. This derived source has no native
# agreement credit and exercises two recursive positional-prefix steps.
shared = SOURCES['required-shared-modes']
selected = shared.index('$gotReceive185 = referenceReceive185(')
shared = shared[:shared.index('$gotReceive185 = valueReceive185(')] + shared[selected:shared.index('$xReceive185 = 1.5;', selected)]
shared = shared.replace('referenceReceive185($xReceive185, cReceive185: $xReceive185, bReceive185: $xReceive185)', 'referenceReceive185($xReceive185, $xReceive185, cReceive185: $xReceive185)')
assert hashlib.sha256(shared.encode()).hexdigest() == '4e28a0251e81c576f6a93d941d699631c95c21b3823590b50dd2f9810fe4d46e'

# Omit the normal VAL-prefix call/catch and its following duplicate reset.
# Keep both required-hole catches, the REF-prefix receive and original throw.
missing = SOURCES['required-missing-priority']
missing = missing[:missing.index('try { valueReceive185($xReceive185, bReceive185:')] + missing[missing.index('try { referenceReceive185($quietReceive185,'):]
assert hashlib.sha256(missing.encode()).hexdigest() == '27c29f7d105f74d98d262e2f834271d204b4d16435c7348b05db883f003c5969'

# Retain fresh setup and only the opposite mixed-mode all-optional call/result.
opposite = SOURCES['all-optional-shared']
opposite = opposite[:opposite.index('$gotReceive185 = valueReceive185(')] + opposite[opposite.index('$gotReceive185 = referenceFirstReceive185('):]
assert hashlib.sha256(opposite.encode()).hexdigest() == '0a6c409f7d57fd5fa6e7b3d8863af31735a358e5cd60e8eee8181d92aa5bf121'

CASES = {
    'mixed-cv-integer-reference-two-prefix': {
        'source': shared,
        'stage': 'S.TODO = [LOSSY_NAMED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
        'checks': [
            'n_bits = 4609434218613702656 /\\ i = 1',
            '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
            '|pfunction.SIGNATURE.PARAMETERS| = 3 /\\ $lossy_positional_reference_parameters(pfunction.SIGNATURE.PARAMETERS)',
            'S.CURRENT = (pcallcontext)',
            'pcallcontext.ARGC = 3 /\\ pcallcontext.HOLES = eps /\\ pcallcontext.NAMED = eps',
            'pcallcontext.CALLSITE = (porigin_call)',
            '$call_argument_source(S, porigin_call) = PCALLARGUMENTS [phpType7_a, phpType7_b, phpType7_c] n_field',
            '$lossy_positional_arguments([phpType7_a, phpType7_b]) /\\ $lossy_named_arguments([phpType7_c])',
            '$lossy_named_tail_arguments([phpType7_a, phpType7_b, phpType7_c])',
            '~$lossy_named_tail_arguments(eps) /\\ ~$lossy_named_tail_arguments([phpType7_a, phpType7_b])',
            '$lossy_named_tail_arguments([phpType7_c]) /\\ ~$lossy_named_tail_arguments([phpType7_c, phpType7_a])',
            '$named_arg_target(pfunction, phpType7_a, 0) = NAMED_POSITION 0',
            '$named_arg_target(pfunction, phpType7_b, 1) = NAMED_POSITION 1',
            '$named_arg_target(pfunction, phpType7_c, 2) = NAMED_POSITION 2',
            '$named_call_valid(S, porigin, (porigin_call))',
            '$named_call_shape(S, porigin, (porigin_call)) = {SLOTS ([NAMED_SENT (KNOWN PNULL), NAMED_SENT (KNOWN PNULL), NAMED_SENT (KNOWN PNULL)]), NAMED eps}',
            '$lookup(S.ENV, pfunction.SIGNATURE.PARAMETERS[0].NAME) = (n_cell)',
            '$lookup(S.ENV, pfunction.SIGNATURE.PARAMETERS[1].NAME) = (n_cell)',
            '$lookup(S.ENV, pfunction.SIGNATURE.PARAMETERS[2].NAME) = (n_cell)',
            'S.STORE[n_cell] = DEFINED (PFLOAT 4615063718147915776)',
            'n_cell <- S.REFCELLS /\\ $heap_owners($heap_graph(S), HCELL n_cell) = 4',
            'S.GLOBALTABLE = (psymboltable_global)',
            '$lookup(psymboltable_global.ENV, $ptascii("xReceive185")) = (n_cell)',
            '$lookup(psymboltable_global.ENV, $ptascii("countReceive185")) = (n_count)',
            'S.STORE[n_count] = DEFINED (PINT 1)',
            '$lossy_named_parameter_source_valid(S, LOSSY_NAMED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z)',
            '~$lossy_positional_parameter_metadata(S, porigin, 0, z)',
            '~$lossy_positional_reference_parameter_metadata(S, porigin, 0, z)',
            '~$lossy_mixed_parameter_metadata(S, porigin, 0, z)',
            '$task_nodes(LOSSY_NAMED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z) = eps',
            'PhpStep: S ~> S_b',
            'S_b.TODO = [TYPE_RECEIVE porigin 1] /\\ S_b.STORE[n_cell] = DEFINED (PINT 1)',
            '$lossy_named_parameter_capture(S_b) = eps',
            'PhpStep: S_b ~> S_c',
            'S_c.TODO = [TYPE_RECEIVE porigin 2] /\\ S_c.STORE[n_cell] = DEFINED (PINT 1)',
            '$lossy_named_parameter_capture(S_c) = eps',
            'PhpStep: S_c ~> S_body',
            'S_body.TODO = $call_receive_body(S_c, pfunction)',
            'S_body.EVENTS = S.EVENTS /\\ S_body.STORE[n_count] = DEFINED (PINT 1)',
            '$call_descriptors_valid(S_body) /\\ $heap_valid($heap_graph(S_body))',
            'S_done = $drive_steps(S_body, 2000)',
            'S_done.COMPLETION = NORMAL /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.TODO = eps',
            'S_done.STORE[n_cell] = DEFINED (PINT 1) /\\ $heap_owners($heap_graph(S_done), HCELL n_cell) = 1',
            'S_done.STORE[n_count] = DEFINED (PINT 1)',
            '$lookup(S_done.ENV, $ptascii("gotReceive185")) = (n_got)',
            'S_done.STORE[n_got] = DEFINED (PINT 1)',
            '$call_descriptors_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
        ],
    },
    'mixed-cv-integer-required-missing-throw': {
        'source': missing,
        'stage': 'S.TODO = [LOSSY_NAMED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
        'checks': [
            'n_bits = 4609434218613702656 /\\ i = 1',
            '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
            '|pfunction.SIGNATURE.PARAMETERS| = 3 /\\ $lossy_positional_reference_parameters(pfunction.SIGNATURE.PARAMETERS)',
            'S.CURRENT = (pcallcontext)',
            'pcallcontext.ARGC = 2 /\\ pcallcontext.HOLES = eps',
            '$lookup(S.ENV, pfunction.SIGNATURE.PARAMETERS[1].NAME) = (n_b)',
            'S.STORE[n_b] = DEFINED (PINT 2)',
            '$lookup(S.ENV, pfunction.SIGNATURE.PARAMETERS[2].NAME) = eps',
            'S.STORE[n_cell] = DEFINED (PFLOAT 4615063718147915776)',
            '$lossy_named_parameter_source_valid(S, LOSSY_NAMED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z)',
            'PhpStep: S ~> S_b',
            'S_b.TODO = [TYPE_RECEIVE porigin 1] /\\ S_b.STORE[n_cell] = DEFINED (PINT 1)',
            'PhpStep: S_b ~> S_c',
            'S_c.TODO = [TYPE_RECEIVE porigin 2]',
            '$lossy_named_parameter_capture(S_c) = eps',
            'PhpStep: S_c ~> S_error',
            'S_error.COMPLETION = THROWN "ArgumentCountError" ptbytes_missing z_missing',
            'S_error.STORE = S_c.STORE /\\ S_error.EVENTS = S_c.EVENTS',
            'S_done = $drive_steps(S_error, 2000)',
            'S_done.COMPLETION = NORMAL /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.TODO = eps',
            'S_done.STORE[n_cell] = DEFINED (PFLOAT 4615063718147915776)',
            '$lookup(S_done.ENV, $ptascii("destinationReceive185")) = (n_destination)',
            'S_done.STORE[n_destination] = DEFINED (PINT 91)',
            '$lookup(S_done.ENV, $ptascii("originalReceive185")) = (n_original)',
            '$lookup(S_done.ENV, $ptascii("caughtReceive185")) = (n_caught)',
            'S_done.STORE[n_original] = DEFINED (POBJECT n_exception)',
            'S_done.STORE[n_caught] = DEFINED (POBJECT n_exception)',
            '$throwable_previous_id(S_done, n_exception) = eps',
            '$call_descriptors_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
        ],
    },
    'mixed-cv-integer-all-optional-opposite': {
        'source': opposite,
        'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin n n_first n_bits i z]',
        'checks': [
            'n = 0 /\\ n_bits = 4609434218613702656 /\\ i = 1',
            '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
            '$lossy_optional_integer_header(S, pfunction, pfunction.SIGNATURE.PARAMETERS, 0)',
            '~pfunction.SIGNATURE.PARAMETERS[0].REQUIRED /\\ pfunction.SIGNATURE.PARAMETERS[0].BYREF /\\ ~pfunction.SIGNATURE.PARAMETERS[2].BYREF',
            'S.CURRENT = (pcallcontext)',
            'pcallcontext.ARGC = 3 /\\ pcallcontext.HOLES = [1]',
            '$lookup(S.ENV, pfunction.SIGNATURE.PARAMETERS[0].NAME) = (n_first)',
            '$lookup(S.ENV, pfunction.SIGNATURE.PARAMETERS[1].NAME) = (n_b)',
            '$lookup(S.ENV, pfunction.SIGNATURE.PARAMETERS[2].NAME) = (n_third)',
            'n_first =/= n_third /\\ S.STORE[n_first] = DEFINED (PFLOAT 4615063718147915776)',
            'n_first <- S.REFCELLS /\\ $heap_owners($heap_graph(S), HCELL n_first) = 2',
            'S.STORE[n_third] = DEFINED (PFLOAT n_bits) /\\ ~(n_third <- S.REFCELLS)',
            '$heap_owners($heap_graph(S), HCELL n_third) = 1',
            'S.STORE[n_b] = DEFINED (PINT 11) /\\ ~(n_b <- S.REFCELLS)',
            '$heap_owners($heap_graph(S), HCELL n_b) = 1',
            '$lossy_mixed_parameter_source_valid(S, LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_first n_bits i z)',
            'PhpStep: S ~> S_b',
            'S_b.TODO = [TYPE_RECEIVE porigin 1] /\\ S_b.STORE[n_first] = DEFINED (PINT 1)',
            '$lossy_mixed_parameter_capture(S_b) = eps',
            'PhpStep: S_b ~> S_c',
            'S_c.TODO = [TYPE_RECEIVE porigin 2]',
            '$lossy_mixed_parameter_capture(S_c) = (ptask_c)',
            'ptask_c = LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_third 4609434218613702656 1 z_c',
            'S_second_pause = $seek(S_c, 2000)',
            'S_second_pause.COMPLETION = NORMAL \\/ S_second_pause.COMPLETION = BUDGET',
            'S_second = S_second_pause[.COMPLETION = NORMAL]',
            'S_second.TODO = [ptask_c]',
            'S_second.STORE[n_first] = DEFINED (PFLOAT 4616752568008179712)',
            'S_second.STORE[n_third] = DEFINED (PFLOAT n_bits)',
            '$lossy_mixed_parameter_source_valid(S_second, ptask_c)',
            '$lossy_mixed_parameter_ready(S_second, 2, n_third, n_bits)',
            '$task_nodes(ptask_c) = eps',
            'PhpStep: S_second ~> S_body',
            'S_body.TODO = $call_receive_body(S_second, pfunction)',
            'S_body.STORE[n_first] = DEFINED (PFLOAT 4616752568008179712) /\\ S_body.STORE[n_third] = DEFINED (PINT 1)',
            'S_body.STORE[n_b] = DEFINED (PINT 11) /\\ ~(n_b <- S_body.REFCELLS)',
            '$call_descriptors_valid(S_body) /\\ $heap_valid($heap_graph(S_body))',
            'S_done = $drive_steps(S_body, 2000)',
            'S_done.COMPLETION = NORMAL /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.TODO = eps',
            'S_done.STORE[n_first] = DEFINED (PFLOAT 4616752568008179712) /\\ $heap_owners($heap_graph(S_done), HCELL n_first) = 1',
            '~((HCELL n_b) <- S_done.ALLOCATIONS) /\\ ~((HCELL n_third) <- S_done.ALLOCATIONS)',
            '$lookup(S_done.ENV, $ptascii("gotReceive185")) = (n_got)',
            'S_done.STORE[n_got] = DEFINED (PINT 1)',
            '$call_descriptors_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
        ],
    },
    'mixed-cv-integer-pending-late': {
        'source': SOURCES['pending-late'],
        'stage': 'S.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail* -- if perrorcall.RESUME = LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z -- if S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin',
        'checks': [
            'n_bits = 4609434218613702656 /\\ i = 1',
            '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
            'pfunction.SIGNATURE.PARAMETERS[0].REQUIRED /\\ pfunction.SIGNATURE.PARAMETERS[1].BYREF /\\ ~pfunction.SIGNATURE.PARAMETERS[2].BYREF',
            'pcallcontext.ARGC = 3 /\\ pcallcontext.HOLES = [1]',
            '$lookup(S.ENV, pfunction.SIGNATURE.PARAMETERS[0].NAME) = (n_a)',
            '$lookup(S.ENV, pfunction.SIGNATURE.PARAMETERS[1].NAME) = (n_b)',
            'S.STORE[n_a] = DEFINED (PINT 2) /\\ S.STORE[n_b] = DEFINED (PINT 11)',
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
            '~pfunction_reference.SIGNATURE.PARAMETERS[0].REQUIRED /\\ pfunction_reference.SIGNATURE.PARAMETERS[1].BYREF /\\ pfunction_reference.SIGNATURE.PARAMETERS[2].BYREF',
            'S_reference.CURRENT = (pcallcontext_reference)',
            'pcallcontext_reference.ARGC = 3 /\\ pcallcontext_reference.HOLES = [1]',
            '$lookup(S_reference.ENV, pfunction_reference.SIGNATURE.PARAMETERS[0].NAME) = (n_a_reference)',
            '$lookup(S_reference.ENV, pfunction_reference.SIGNATURE.PARAMETERS[1].NAME) = (n_b_reference)',
            'S_reference.STORE[n_a_reference] = DEFINED (PINT 2) /\\ S_reference.STORE[n_b_reference] = DEFINED (PINT 11)',
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
            '$lookup(S_done.ENV, $ptascii("destinationReceive185")) = (n_destination)',
            'S_done.STORE[n_destination] = DEFINED (PINT 91)',
            '$lookup(S_done.ENV, $ptascii("originalReceive185")) = (n_original)',
            '$lookup(S_done.ENV, $ptascii("caughtReceive185")) = (n_caught)',
            'S_done.STORE[n_original] = DEFINED (POBJECT n_exception) /\\ S_done.STORE[n_caught] = DEFINED (POBJECT n_exception)',
            '$throwable_previous_id(S_done, n_exception) = eps',
            '$call_descriptors_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
        ],
    },
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE))
