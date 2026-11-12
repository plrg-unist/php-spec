#!/usr/bin/env python3
"""Binary default provenance, omitted-reference cells and real throw cleanup."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('binary_integer_default_reception_cases.json')
SOURCES = {}
for row in json.loads(CATALOGUE.read_text()):
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
    SOURCES[row['id']] = row['source']

# Keep fresh setup and only the leading REF call; the removed calls and their
# histories have no source credit in this independently derived fixture.
source = SOURCES['binary-precision-modes']
start = source.index('$gotReceive187 = referenceReceive187(')
end = source.index('$xReceive187 = 1.5;', start)
leading = source[:source.index('$gotReceive187 = valueFirstReceive187(')] + source[start:end]
assert hashlib.sha256(leading.encode()).hexdigest() == '759f84003a2ab00fdd3d60491a8c0b711e4f51d0556bc7f8521c0ab789b9fab5'

CASES = {
    'binary-default-reference-leading': {
        'source': leading,
        'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z]',
        'checks': [
            r'n_bits = 4609434218613702656 /\ i = 1',
            '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
            'pfunction.SIGNATURE.PARAMETERS = [psparam_a, psparam_b, psparam_c, psparam_d, psparam_e]',
            r'$lossy_optional_integer_mode(pfunction.SIGNATURE.PARAMETERS, true) /\ ~$lossy_optional_integer_mode(pfunction.SIGNATURE.PARAMETERS, false)',
            'psparam_a.DEFAULT = PSDEFAULT expression_a "int"',
            'expression_a = NExprBinaryOpPlus expression_left expression_right metadata_binary',
            '$psnumber(expression_a) = PSNONNUMERIC',
            '$lossy_optional_integer_default(expression_a) = ($(-7))',
            '$default_parameter_origin(S, porigin, 0) = PORIGIN n_unit pcpath_parameter',
            'pcpath_default = pcpath_parameter ++ [PCFIELD 6]',
            'porigin_default = PORIGIN n_unit pcpath_default',
            '$origin_node(S.SOURCES, porigin_default) = (expression_a)',
            '$default_at(pfunction.DEFAULTS, 0) = ({INDEX 0, ORIGIN porigin_default, KIND PDSTORED})',
            '$compiled_read(S, porigin_default) = (PINT $(-7))',
            '$lossy_optional_integer_header(S, pfunction, pfunction.SIGNATURE.PARAMETERS, 0)',
            'expression_same = NScalarInt (INTEGER $(-7)) metadata_binary',
            '$lossy_optional_integer_default(expression_same) = ($(-7))',
            '~$lossy_optional_integer_tail(S, pfunction, [psparam_a[.DEFAULT = PSDEFAULT expression_same "int"]], 0)',
            'S_wrong_value = S[.POOLS = [{UNIT n_unit, CONSTANTS ([(PCONSTANT pcpath_default (PINT 7))])}]]',
            '$compiled_read(S_wrong_value, porigin_default) = (PINT 7)',
            '~$lossy_optional_integer_tail(S_wrong_value, pfunction, [psparam_a], 0)',
            'S.CURRENT = (pcallcontext)',
            r'pcallcontext.ARGC = 3 /\ pcallcontext.HOLES = [0, 1] /\ pcallcontext.NAMED = eps',
            'pcallcontext.CALLSITE = (porigin_call)',
            '$named_call_valid(S, porigin, (porigin_call))',
            '$named_call_shape(S, porigin, (porigin_call)) = {SLOTS ([NAMED_HOLE, NAMED_HOLE, NAMED_SENT (KNOWN PNULL)]), NAMED eps}',
            '$lookup(S.ENV, psparam_a.NAME) = (n_a)',
            '$lookup(S.ENV, psparam_b.NAME) = (n_b)',
            '$lookup(S.ENV, psparam_c.NAME) = (n_cell)',
            r'S.STORE[n_a] = DEFINED (PINT $(-7)) /\ S.STORE[n_b] = DEFINED (PINT $(-11))',
            r'~(n_a <- S.REFCELLS) /\ ~(n_b <- S.REFCELLS)',
            r'$heap_owners($heap_graph(S), HCELL n_a) = 1 /\ $heap_owners($heap_graph(S), HCELL n_b) = 1',
            r'$lookup(S.ENV, psparam_d.NAME) = eps /\ $lookup(S.ENV, psparam_e.NAME) = eps',
            'S.STORE[n_cell] = DEFINED (PFLOAT 4615063718147915776)',
            r'n_cell <- S.REFCELLS /\ $heap_owners($heap_graph(S), HCELL n_cell) = 2',
            '$lossy_mixed_parameter_source_valid(S, LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z)',
            '$task_nodes(LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z) = eps',
            'z_hole = $default_parameter_line(S, porigin, 0)',
            'ptask_hole = LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_a n_bits i z_hole',
            'S_hole = S[.STORE[n_a] = DEFINED (PFLOAT n_bits)][.REFCELLS = n_a :: S.REFCELLS][.ORIGIN = ($default_parameter_origin(S, porigin, 0))][.TODO = [ptask_hole]]',
            '$lossy_positional_reference_parameter_ready(S_hole, 0, n_a)',
            '$typed_receive_valid(S_hole[.TODO = [TYPE_RECEIVE porigin 0]][.ORIGIN = (porigin)], porigin, 0)',
            '~$lossy_mixed_parameter_source_valid(S_hole, ptask_hole)',
            'PhpStep: S ~> S_next',
            r'S_next.TODO = [TYPE_RECEIVE porigin 3] /\ S_next.STORE[n_cell] = DEFINED (PINT 1)',
            'PhpStep: S_next ~> S_default_d',
            'S_default_d.TODO = [DEFAULT_RECEIVE porigin 3]',
            'PhpStep: S_default_d ~> S_d',
            'S_d.TODO = [TYPE_RECEIVE porigin 4]',
            'PhpStep: S_d ~> S_default_e',
            'S_default_e.TODO = [DEFAULT_RECEIVE porigin 4]',
            'PhpStep: S_default_e ~> S_body',
            'S_body.TODO = $call_receive_body(S_default_e, pfunction)',
            '$lookup(S_body.ENV, psparam_d.NAME) = (n_d)',
            '$lookup(S_body.ENV, psparam_e.NAME) = (n_e)',
            r'S_body.STORE[n_d] = DEFINED (PINT $(-9223372036854775808)) /\ S_body.STORE[n_e] = DEFINED (PINT 9223372036854775807)',
            r'~(n_d <- S_body.REFCELLS) /\ ~(n_e <- S_body.REFCELLS)',
            r'$heap_owners($heap_graph(S_body), HCELL n_d) = 1 /\ $heap_owners($heap_graph(S_body), HCELL n_e) = 1',
            r'S_body.EVENTS = S.EVENTS /\ $call_descriptors_valid(S_body) /\ $heap_valid($heap_graph(S_body))',
            'S_done = $drive_steps(S_body, 2000)',
            r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
            r'~((HCELL n_a) <- S_done.ALLOCATIONS) /\ ~((HCELL n_b) <- S_done.ALLOCATIONS) /\ ~((HCELL n_d) <- S_done.ALLOCATIONS) /\ ~((HCELL n_e) <- S_done.ALLOCATIONS)',
            r'S_done.STORE[n_cell] = DEFINED (PINT 1) /\ $heap_owners($heap_graph(S_done), HCELL n_cell) = 1',
            '$lookup(S_done.ENV, $ptascii("gotReceive187")) = (n_got)',
            'S_done.STORE[n_got] = DEFINED (PINT 1)',
            r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
        ],
    },
    'binary-default-required-pending': {
        'source': SOURCES['binary-required-pending'],
        'stage': 'S.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall) :: ptask_tail* -- if perrorcall.RESUME = LOSSY_MIXED_PARAMETER_RECEIVE porigin 2 n_cell n_bits i z -- if S.CURRENT = (pcallcontext) -- if pcallcontext.FUNCTION = porigin',
        'checks': [
            r'n_bits = 4609434218613702656 /\ i = 1',
            '$function_at(S.FUNCTIONS, porigin) = (pfunction)',
            '$lossy_optional_integer_header(S, pfunction, pfunction.SIGNATURE.PARAMETERS, 0)',
            r'pfunction.SIGNATURE.PARAMETERS[0].REQUIRED /\ ~pfunction.SIGNATURE.PARAMETERS[0].BYREF /\ pfunction.SIGNATURE.PARAMETERS[1].BYREF /\ ~pfunction.SIGNATURE.PARAMETERS[2].BYREF',
            r'pcallcontext.ARGC = 3 /\ pcallcontext.HOLES = [1]',
            '$lookup(S.ENV, pfunction.SIGNATURE.PARAMETERS[0].NAME) = (n_a)',
            '$lookup(S.ENV, pfunction.SIGNATURE.PARAMETERS[1].NAME) = (n_b)',
            r'S.STORE[n_a] = DEFINED (PINT 2) /\ S.STORE[n_b] = DEFINED (PINT $(-11))',
            r'~(n_a <- S.REFCELLS) /\ ~(n_b <- S.REFCELLS)',
            r'$heap_owners($heap_graph(S), HCELL n_a) = 1 /\ $heap_owners($heap_graph(S), HCELL n_b) = 1',
            r'S.STORE[n_cell] = DEFINED (PFLOAT n_bits) /\ ~(n_cell <- S.REFCELLS)',
            '$heap_owners($heap_graph(S), HCELL n_cell) = 1',
            '$lossy_mixed_parameter_source_valid(S, perrorcall.RESUME)',
            r'$error_call_valid(S, perrorcall) /\ $call_descriptors_valid(S)',
            '$task_nodes(perrorcall.RESUME) = eps',
            '$heap_count(HOBJECT n_exception, $tasks_nodes(S.TODO)) = 1',
            'PhpStep: S ~> S_skip',
            r'S_skip.STORE = S.STORE /\ S_skip.OBJECTS = S.OBJECTS',
            'S_reference_pause = $seek(S_skip, 2000)',
            r'S_reference_pause.COMPLETION = NORMAL \/ S_reference_pause.COMPLETION = BUDGET',
            'S_reference = S_reference_pause[.COMPLETION = NORMAL]',
            'S_reference.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall_reference) :: ptask_reference_tail*',
            'perrorcall_reference.RESUME = LOSSY_MIXED_PARAMETER_RECEIVE porigin_reference 2 n_reference 4609434218613702656 1 z_reference',
            'porigin_reference =/= porigin',
            '$function_at(S_reference.FUNCTIONS, porigin_reference) = (pfunction_reference)',
            '$lossy_optional_integer_header(S_reference, pfunction_reference, pfunction_reference.SIGNATURE.PARAMETERS, 0)',
            r'pfunction_reference.SIGNATURE.PARAMETERS[0].REQUIRED /\ pfunction_reference.SIGNATURE.PARAMETERS[0].BYREF /\ pfunction_reference.SIGNATURE.PARAMETERS[1].BYREF /\ pfunction_reference.SIGNATURE.PARAMETERS[2].BYREF',
            'S_reference.CURRENT = (pcallcontext_reference)',
            r'pcallcontext_reference.ARGC = 3 /\ pcallcontext_reference.HOLES = [1]',
            '$lookup(S_reference.ENV, pfunction_reference.SIGNATURE.PARAMETERS[0].NAME) = (n_a_reference)',
            '$lookup(S_reference.ENV, pfunction_reference.SIGNATURE.PARAMETERS[1].NAME) = (n_b_reference)',
            r'S_reference.STORE[n_a_reference] = DEFINED (PINT 2) /\ S_reference.STORE[n_b_reference] = DEFINED (PINT $(-11))',
            r'n_a_reference <- S_reference.REFCELLS /\ ~(n_b_reference <- S_reference.REFCELLS)',
            r'$heap_owners($heap_graph(S_reference), HCELL n_a_reference) = 2 /\ $heap_owners($heap_graph(S_reference), HCELL n_b_reference) = 1',
            r'~((HCELL n_a) <- S_reference.ALLOCATIONS) /\ ~((HCELL n_b) <- S_reference.ALLOCATIONS) /\ ~((HCELL n_cell) <- S_reference.ALLOCATIONS)',
            'S_reference.STORE[n_reference] = DEFINED (PFLOAT 4615063718147915776)',
            r'n_reference <- S_reference.REFCELLS /\ $heap_owners($heap_graph(S_reference), HCELL n_reference) = 2',
            '$lossy_mixed_parameter_source_valid(S_reference, perrorcall_reference.RESUME)',
            r'$error_call_valid(S_reference, perrorcall_reference) /\ $call_descriptors_valid(S_reference)',
            '$task_nodes(perrorcall_reference.RESUME) = eps',
            '$heap_count(HOBJECT n_exception, $tasks_nodes(S_reference.TODO)) = 1',
            'S_done = $drive_steps(S_reference, 2000)',
            r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
            '~((HCELL n_b_reference) <- S_done.ALLOCATIONS)',
            r'S_done.STORE[n_reference] = DEFINED (PFLOAT 4615063718147915776) /\ $heap_owners($heap_graph(S_done), HCELL n_reference) = 1',
            '$lookup(S_done.ENV, $ptascii("destinationReceive187")) = (n_destination)',
            'S_done.STORE[n_destination] = DEFINED (PINT 91)',
            '$lookup(S_done.ENV, $ptascii("originalReceive187")) = (n_original)',
            '$lookup(S_done.ENV, $ptascii("caughtReceive187")) = (n_caught)',
            r'S_done.STORE[n_original] = DEFINED (POBJECT n_exception) /\ S_done.STORE[n_caught] = DEFINED (POBJECT n_exception)',
            '$throwable_previous_id(S_done, n_exception) = eps',
            r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
        ],
    },
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE))
