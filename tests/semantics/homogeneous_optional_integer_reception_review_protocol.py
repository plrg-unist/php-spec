#!/usr/bin/env python3
"""Homogeneous optional references retain writeback, sharing and pending throws."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('homogeneous_optional_integer_reception_cases.json')
SOURCES = {}
for row in json.loads(CATALOGUE.read_text()):
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
    SOURCES[row['id']] = row['source']

# Retain setup and the positional REF call, omitting the other three calls.
reference = SOURCES['supplied-optional']
call = 'referenceHomoTail($aHomoTail, $xHomoTail);\n'
reference = (reference[:reference.index('valueHomoTail($aHomoTail, $xHomoTail);')]
             + reference[reference.index(call):reference.index(call) + len(call)])
assert hashlib.sha256(reference.encode()).hexdigest() == 'afda352107bf5007bb1d60a5189bde312f1283273c042a276bd582f97edd0ab9'

# Retain setup and the last two named-c throws, omitting four earlier calls.
pending = SOURCES['pending-optional']
pending = (pending[:pending.index('$xHomoTail = 1.5;\ntry { $destinationHomoTail = valueHomoTail($aHomoTail, $xHomoTail); }')]
           + pending[pending.index('$xHomoTail = 1.5;\ntry { $destinationHomoTail = valueHomoTail(cHomoTail: $xHomoTail, aHomoTail: $aHomoTail); }'):])
assert hashlib.sha256(pending.encode()).hexdigest() == '61548309538f792b49fe4e43d32fe5b6576ebf87c6271d34630cb1d118dd686a'

# Retain setup and the shared-a/c REF call, omitting the required-hole and VAL calls.
shared = SOURCES['named-optional-hole']
call = 'referenceHomoTail(cHomoTail: $xHomoTail, aHomoTail: $xHomoTail);\n'
shared = (shared[:shared.index('try { valueHomoTail(cHomoTail: $xHomoTail); }')]
          + shared[shared.index(call):shared.index(call) + len(call)])
assert hashlib.sha256(shared.encode()).hexdigest() == '8009f4974f9ae69c206b1a6f1632963cc9936a811cd2f5efe496021156d65540'

CASES = {
    'homogeneous-optional-integer-reference-writeback': {
        'source': reference,
        'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 1 n_cell n_bits i z]',
        'checks': [
            'n_bits = 4609434218613702656 /\\ i = 1',
            '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
            '$lossy_optional_integer_mode(pfunction.SIGNATURE.PARAMETERS, true) /\\ ~$lossy_optional_integer_mode(pfunction.SIGNATURE.PARAMETERS, false)',
            'S.CURRENT = (pcallcontext)',
            'pcallcontext.ARGC = 2 /\\ pcallcontext.HOLES = eps /\\ pcallcontext.NAMED = eps',
            '$lookup(S.ENV, pfunction.SIGNATURE.PARAMETERS[0].NAME) = (n_a)',
            'S.STORE[n_a] = DEFINED (PINT 2)',
            '$lookup(S.ENV, pfunction.SIGNATURE.PARAMETERS[1].NAME) = (n_cell)',
            '$lookup(S.ENV, pfunction.SIGNATURE.PARAMETERS[2].NAME) = eps',
            'S.STORE[n_cell] = DEFINED (PFLOAT 4615063718147915776)',
            'n_cell <- S.REFCELLS /\\ $heap_owners($heap_graph(S), HCELL n_cell) = 2',
            '$lossy_mixed_parameter_source_valid(S, LOSSY_MIXED_PARAMETER_RECEIVE porigin 1 n_cell n_bits i z)',
            '$lossy_mixed_parameter_ready(S, 1, n_cell, n_bits)',
            '~$lossy_parameter_ready(S, n_cell, n_bits)',
            '$call_task_valid(S, LOSSY_MIXED_PARAMETER_RECEIVE porigin 1 n_cell n_bits i z)',
            '$task_nodes(LOSSY_MIXED_PARAMETER_RECEIVE porigin 1 n_cell n_bits i z) = eps',
            'S.GLOBALTABLE = (psymboltable_global)',
            '$lookup(psymboltable_global.ENV, $ptascii("xHomoTail")) = (n_cell)',
            'PhpStep: S ~> S_last',
            'S_last.TODO = [TYPE_RECEIVE porigin 2]',
            'S_last.STORE[n_cell] = DEFINED (PINT 1) /\\ S_last.STORE[n_a] = DEFINED (PINT 2)',
            'PhpStep: S_last ~> S_default',
            'S_default.TODO = [DEFAULT_RECEIVE porigin 2]',
            'PhpStep: S_default ~> S_body',
            'S_body.TODO = $call_receive_body(S_default, pfunction)',
            '$lookup(S_body.ENV, pfunction.SIGNATURE.PARAMETERS[2].NAME) = (n_c)',
            'S_body.STORE[n_c] = DEFINED (PINT 11)',
            '~(n_c <- S_body.REFCELLS) /\\ $heap_owners($heap_graph(S_body), HCELL n_c) = 1',
            '$heap_owners($heap_graph(S_body), HCELL n_cell) = 2',
            'S_body.EVENTS = S.EVENTS',
            '$call_descriptors_valid(S_body) /\\ $heap_valid($heap_graph(S_body))',
            'S_done = $drive_steps(S_body, 10000)',
            'S_done.COMPLETION = NORMAL /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.TODO = eps',
            '~((HCELL n_c) <- S_done.ALLOCATIONS)',
            'S_done.STORE[n_cell] = DEFINED (PINT 1) /\\ $heap_owners($heap_graph(S_done), HCELL n_cell) = 1',
            '$lookup(S_done.ENV, $ptascii("xHomoTail")) = (n_cell)',
            '$call_descriptors_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
        ],
    },
    'homogeneous-optional-integer-named-pending-modes': {
        'source': pending,
        'stage': 'S.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail* -- if perrorcall.RESUME = LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z -- if S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin',
        'checks': [
            'n_bits = 4609434218613702656 /\\ i = 1',
            '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
            'pfunction.SIGNATURE.PARAMETERS = [psparam_a, psparam_b, psparam_c]',
            '~psparam_a.BYREF /\\ ~psparam_b.BYREF /\\ ~psparam_c.BYREF',
            'pcallcontext.ARGC = 3 /\\ pcallcontext.HOLES = [1] /\\ pcallcontext.NAMED = eps',
            '$lookup(S.ENV, psparam_a.NAME) = (n_a)',
            '$lookup(S.ENV, psparam_b.NAME) = (n_b)',
            'S.STORE[n_a] = DEFINED (PINT 2) /\\ S.STORE[n_b] = DEFINED (PINT 7)',
            '~(n_b <- S.REFCELLS) /\\ $heap_owners($heap_graph(S), HCELL n_b) = 1',
            'S.STORE[n_cell] = DEFINED (PFLOAT n_bits)',
            '~(n_cell <- S.REFCELLS) /\\ $heap_owners($heap_graph(S), HCELL n_cell) = 1',
            'S.GLOBALTABLE = (psymboltable_global)',
            '$lookup(psymboltable_global.ENV, $ptascii("xHomoTail")) = (n_global)',
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
            '~$lossy_optional_integer_mode(pfunction.SIGNATURE.PARAMETERS, true)',
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
            'pfunction_reference.SIGNATURE.PARAMETERS[0].BYREF /\\ pfunction_reference.SIGNATURE.PARAMETERS[1].BYREF /\\ pfunction_reference.SIGNATURE.PARAMETERS[2].BYREF',
            '~$lossy_optional_integer_mode(pfunction_reference.SIGNATURE.PARAMETERS, false)',
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
            '$lookup(S_done.ENV, $ptascii("originalHomoTail")) = (n_original)',
            '$lookup(S_done.ENV, $ptascii("caughtHomoTail")) = (n_caught)',
            'S_done.STORE[n_original] = DEFINED (POBJECT n_exception)',
            'S_done.STORE[n_caught] = DEFINED (POBJECT n_exception)',
            '$throwable_previous_id(S_done, n_exception) = eps',
            '$lookup(S_done.ENV, $ptascii("destinationHomoTail")) = (n_destination)',
            'S_done.STORE[n_destination] = DEFINED (PINT 91)',
            '~$lossy_mixed_parameter_source_valid(S_done, perrorcall_reference.RESUME)',
            '$call_descriptors_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
        ],
    },
    'homogeneous-optional-integer-shared-reference': {
        'source': shared,
        'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
        'checks': [
            'n_bits = 4609434218613702656 /\\ i = 1',
            '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
            '$lossy_optional_integer_mode(pfunction.SIGNATURE.PARAMETERS, true) /\\ ~$lossy_optional_integer_mode(pfunction.SIGNATURE.PARAMETERS, false)',
            'S.CURRENT = (pcallcontext)',
            'pcallcontext.ARGC = 3 /\\ pcallcontext.HOLES = [1] /\\ pcallcontext.NAMED = eps',
            '$lookup(S.ENV, pfunction.SIGNATURE.PARAMETERS[0].NAME) = (n_cell)',
            '$lookup(S.ENV, pfunction.SIGNATURE.PARAMETERS[2].NAME) = (n_cell)',
            '$lookup(S.ENV, pfunction.SIGNATURE.PARAMETERS[1].NAME) = (n_b)',
            'S.STORE[n_b] = DEFINED (PINT 7)',
            '~(n_b <- S.REFCELLS) /\\ $heap_owners($heap_graph(S), HCELL n_b) = 1',
            'n_cell <- S.REFCELLS /\\ $heap_owners($heap_graph(S), HCELL n_cell) = 3',
            'S.STORE[n_cell] = DEFINED (PFLOAT 4615063718147915776)',
            'S.GLOBALTABLE = (psymboltable_global)',
            '$lookup(psymboltable_global.ENV, $ptascii("countHomoTail")) = (n_count)',
            'S.STORE[n_count] = DEFINED (PINT 1)',
            '$lossy_mixed_parameter_source_valid(S, LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z)',
            'z_hole = $default_parameter_line(S, porigin, 1)',
            'ptask_hole = LOSSY_MIXED_PARAMETER_RECEIVE porigin 1 n_b n_bits i z_hole',
            'S_hole = S[.STORE[n_b] = DEFINED (PFLOAT n_bits)][.REFCELLS = n_b :: S.REFCELLS][.ORIGIN = ($default_parameter_origin(S, porigin, 1))][.TODO = [ptask_hole]]',
            '$lossy_positional_reference_parameter_ready(S_hole, 1, n_b)',
            '$typed_receive_valid(S_hole[.TODO = [TYPE_RECEIVE porigin 1]][.ORIGIN = (porigin)], porigin, 1)',
            '~$lossy_mixed_parameter_metadata(S_hole, porigin, 1, z_hole)',
            '~$lossy_mixed_parameter_source_valid(S_hole, ptask_hole)',
            '$lossy_mixed_parameter_ready(S, 0, n_cell, n_bits)',
            '$task_nodes(LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z) = eps',
            'PhpStep: S ~> S_b',
            'S_b.TODO = [TYPE_RECEIVE porigin 1]',
            'S_b.STORE[n_cell] = DEFINED (PINT 1) /\\ S_b.STORE[n_b] = DEFINED (PINT 7)',
            '$lossy_mixed_parameter_capture(S_b) = eps',
            'PhpStep: S_b ~> S_c',
            'S_c.TODO = [TYPE_RECEIVE porigin 2]',
            '$lossy_mixed_parameter_capture(S_c) = eps',
            'S_c.STORE[n_cell] = DEFINED (PINT 1)',
            'PhpStep: S_c ~> S_body',
            'S_body.TODO = $call_receive_body(S_c, pfunction)',
            'S_body.EVENTS = S.EVENTS /\\ S_body.STORE[n_count] = DEFINED (PINT 1)',
            '$call_descriptors_valid(S_body) /\\ $heap_valid($heap_graph(S_body))',
            'S_done = $drive_steps(S_body, 10000)',
            'S_done.COMPLETION = NORMAL /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.TODO = eps',
            '$lookup(S_done.ENV, $ptascii("xHomoTail")) = (n_cell)',
            'S_done.STORE[n_cell] = DEFINED (PINT 1) /\\ $heap_owners($heap_graph(S_done), HCELL n_cell) = 1',
            'S_done.STORE[n_count] = DEFINED (PINT 1) /\\ ~((HCELL n_b) <- S_done.ALLOCATIONS)',
            '$call_descriptors_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
        ],
    },
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE))
