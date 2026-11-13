#!/usr/bin/env python3
"""Independent primitive Get returns, copy ownership and generic-CV refusal."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol


CATALOGUE = Path(__file__).with_name('magic_property_primitive_read_get_review_cases.json')
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == (
    '9a0f9035b663fa9f1614756f20c4d42a9e494c415c1123ead6bdb69598d251f1')

HELPERS = r'''
dec $primitive_read_found(pstate, pvalue) : bool
def $primitive_read_found(S, pvalue) = true
  -- if S.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*
  -- if S.RESULT = KNOWN pvalue
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $primitive_read_found(S, pvalue) = false -- otherwise
dec $primitive_read_seek(pstate, pvalue, nat) : pstate
def $primitive_read_seek(S, pvalue, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $primitive_read_seek(S, pvalue, n) = S
  -- if $primitive_read_found(S, pvalue)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $primitive_read_seek(S, pvalue, 0) = S
  -- if ~$primitive_read_found(S, pvalue)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $primitive_read_seek(S, pvalue, n) = $primitive_read_seek($drive_steps(S[.COMPLETION = NORMAL],1), pvalue, $nabs($(n - 1)))
  -- if $(n > 0) /\ ~$primitive_read_found(S, pvalue)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''

REACHED = [
    'S.CURRENT = eps /\\ S.FRAMES = eps /\\ S.HELD = eps',
    'S.RESULT = KNOWN PNULL /\\ S.BASE = BASE_VALUE (KNOWN PNULL)',
    'S.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*',
    'n_receiver = ppropertyget.OBJECT',
    'ppropertyget.DECL = eps',
    'ppropertyget.NAME = $ptascii("12") /\\ ppropertyget.LINE = 21',
    'S.ORIGIN = (ppropertyget.SITE)',
    'S.OBJECTS[n_receiver] = INSTANCE ppropertyget.CLASS',
    '$property_get_method(S,n_receiver) = (pmethoddesc_get)',
    'pfunction = pmethoddesc_get.FUNCTION',
    'pfunction.ORIGIN = ppropertyget.METHOD /\\ pmethoddesc_get.OWNER = ppropertyget.CLASS',
    'pfunction.SIGNATURE.PARAMETERS = [psparam]',
    'psparam.TYPE = [(PTBRANCH ([PTBUILTIN "int"])),(PTBRANCH ([PTBUILTIN "string"]))]',
    '~pfunction.SIGNATURE.BYREF /\\ pfunction.SIGNATURE.RETURNS = eps',
    '$property_empty_get_source(S,pmethoddesc_get) /\\ $property_get_string_method(S,pmethoddesc_get)',
    '$property_get_source(S,ppropertyget) /\\ $property_get_string_source(S,ppropertyget)',
    '$property_get_cv_name_source(S,ppropertyget)',
    '$property_get_history(S,ppropertyget) /\\ $property_get_valid(S,ppropertyget,true)',
    '$property_get_tail_valid(S,ppropertyget) /\\ $property_get_string_tasks(S,ppropertyget,S.TODO)',
    '$property_get_verify_desc(S,ppropertyget) = eps',
    '$call_task_valid(S,PROPERTY_GET_RESULT ppropertyget)',
    '$property_get_name_result_supported(S,ppropertyget,S.RESULT)',
    '$task_nodes(PROPERTY_GET_RESULT ppropertyget) = [HOBJECT n_receiver]',
    '$value_nodes(PNULL) = eps /\\ $operand_nodes(S.RESULT) = eps',
    '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 2',
    '$lookup(S.ENV,$ptascii("reader")) = (n_receiver_cell)',
    'S.STORE[n_receiver_cell] = DEFINED (POBJECT n_receiver)',
    '$lookup(S.ENV,$ptascii("selector")) = (n_selector_cell)',
    'S.STORE[n_selector_cell] = DEFINED pvalue_selector',
    '$string_bytes(pvalue_selector) = ($ptascii("12"))',
    'S.EVENTS = eps',
    '$call_descriptors_valid(S) /\\ $class_state_valid(S) /\\ $property_state_valid(S) /\\ $heap_valid($heap_graph(S))',
    'PhpStep: S ~> S_copy',
    'S_copy.TODO = (PROPERTY_GET_COPY ppropertyget (KNOWN PNULL)) :: ptask_tail*',
    'S_copy.RESULT = KNOWN PNULL /\\ S_copy.BASE = BASE_VALUE (KNOWN PNULL)',
    '$call_task_valid(S_copy,PROPERTY_GET_COPY ppropertyget (KNOWN PNULL))',
    '$task_nodes(PROPERTY_GET_COPY ppropertyget (KNOWN PNULL)) = eps',
    '$heap_owners($heap_graph(S_copy),HOBJECT n_receiver) = 1',
    'PhpStep: S_copy ~> S_after',
    'S_after.TODO = ptask_tail* /\\ S_after.RESULT = KNOWN PNULL',
    '$heap_owners($heap_graph(S_after),HOBJECT n_receiver) = 1',
    '$call_descriptors_valid(S_after) /\\ $property_state_valid(S_after) /\\ $heap_valid($heap_graph(S_after))',
]

CONTROLS = [
    '~$property_get_name_result_supported(S,ppropertyget,KNOWN (PFLOAT 9218868437227405312))',
    '~$property_get_name_result_supported(S,ppropertyget,KNOWN (PFLOAT 9221120237041090560))',
    '~$property_get_name_result_supported(S,ppropertyget,KNOWN (PFLOAT 18446744073709551616))',
    '$string_carrier_valid(S,PSTRING_CARRIER INTERNED_STRING ([0]))',
    '~$property_get_name_result_supported(S,ppropertyget,KNOWN (PSTRING_CARRIER INTERNED_STRING ([0])))',
    '~$property_get_name_result_supported(S,ppropertyget,KNOWN (PSTRING_CARRIER INTERNED_STRING ([256])))',
    '~$property_get_name_result_supported(S,ppropertyget,KNOWN (PSTRING ($ptascii("0012"))))',
    'S_request = S[.STRINGDATA = S.STRINGDATA ++ [($ptascii("0012"))]]',
    'pvalue_request = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ($ptascii("0012"))',
    '$string_carrier_valid(S_request,pvalue_request)',
    '~$property_get_name_result_supported(S_request,ppropertyget,KNOWN pvalue_request)',
    '~$property_get_name_result_supported(S,ppropertyget,KNOWN (PARRAY 0))',
    '~$property_get_name_result_supported(S,ppropertyget,KNOWN (POBJECT n_receiver))',
    '~$property_get_name_result_supported(S,ppropertyget,REFERENCE n_receiver_cell)',
    '~$property_get_string_source(S,ppropertyget[.DECL = (ppropertyget.METHOD)])',
    '~$property_get_name_result_supported(S,ppropertyget[.DECL = (ppropertyget.METHOD)],KNOWN PNULL)',
]

RESULTS = [
    'S_bool_found = $primitive_read_seek(S_after,PBOOL false,2000)',
    r'S_bool_found.COMPLETION = NORMAL \/ S_bool_found.COMPLETION = BUDGET',
    'S_bool = S_bool_found[.COMPLETION = NORMAL]',
    'S_bool.TODO = (PROPERTY_GET_RESULT ppropertyget_bool) :: ptask_bool*',
    'S_bool.RESULT = KNOWN (PBOOL false) /\\ ppropertyget_bool.NAME = $ptascii("flag")',
    'ppropertyget_bool.OBJECT = n_receiver /\\ ppropertyget_bool.METHOD = ppropertyget.METHOD',
    '$property_get_string_source(S_bool,ppropertyget_bool) /\\ $property_get_tail_valid(S_bool,ppropertyget_bool)',
    '$property_get_name_result_supported(S_bool,ppropertyget_bool,S_bool.RESULT)',
    '$operand_nodes(S_bool.RESULT) = eps /\\ $heap_owners($heap_graph(S_bool),HOBJECT n_receiver) = 2',
    'S_bool.EVENTS = [OUTPUT $ptascii("N;")]',
    'S_float_found = $primitive_read_seek(S_bool,PFLOAT 9223372036854775808,2000)',
    r'S_float_found.COMPLETION = NORMAL \/ S_float_found.COMPLETION = BUDGET',
    'S_float = S_float_found[.COMPLETION = NORMAL]',
    'S_float.TODO = (PROPERTY_GET_RESULT ppropertyget_float) :: ptask_float*',
    'S_float.RESULT = KNOWN (PFLOAT 9223372036854775808) /\\ ppropertyget_float.NAME = $ptascii("zero")',
    '$float_decode(9223372036854775808) = FINITE 1 0 n_zero_den',
    '$(n_zero_den > 0)',
    '$property_get_string_source(S_float,ppropertyget_float) /\\ $property_get_tail_valid(S_float,ppropertyget_float)',
    '$property_get_name_result_supported(S_float,ppropertyget_float,S_float.RESULT)',
    '$operand_nodes(S_float.RESULT) = eps /\\ $heap_owners($heap_graph(S_float),HOBJECT n_receiver) = 2',
    'S_float.EVENTS = [OUTPUT $ptascii("N;"),OUTPUT $ptascii("F;")]',
    'pvalue_text = PSTRING_CARRIER INTERNED_STRING ($ptascii("0012"))',
    'S_text_found = $primitive_read_seek(S_float,pvalue_text,2000)',
    r'S_text_found.COMPLETION = NORMAL \/ S_text_found.COMPLETION = BUDGET',
    'S_text = S_text_found[.COMPLETION = NORMAL]',
    'S_text.TODO = (PROPERTY_GET_RESULT ppropertyget_text) :: ptask_text*',
    'S_text.RESULT = KNOWN pvalue_text /\\ ppropertyget_text.NAME = $ptascii("text")',
    '$string_carrier_valid(S_text,pvalue_text)',
    '$property_get_string_source(S_text,ppropertyget_text) /\\ $property_get_tail_valid(S_text,ppropertyget_text)',
    '$property_get_name_result_supported(S_text,ppropertyget_text,S_text.RESULT)',
    '$operand_nodes(S_text.RESULT) = eps /\\ $heap_owners($heap_graph(S_text),HOBJECT n_receiver) = 2',
    'S_text.EVENTS = [OUTPUT $ptascii("N;"),OUTPUT $ptascii("F;"),OUTPUT $ptascii("-0"),OUTPUT $ptascii(";")]',
    '$call_descriptors_valid(S_text) /\\ $property_state_valid(S_text) /\\ $heap_valid($heap_graph(S_text))',
]

RESUME = [
    'S_zero = $drive_steps(S_text,0)',
    'S_zero.COMPLETION = BUDGET /\\ S_zero[.COMPLETION = NORMAL] = S_text',
    'S_one = $drive_steps(S_text,1)',
    'S_one.COMPLETION = BUDGET',
    'S_one.TODO = (PROPERTY_GET_COPY ppropertyget_text (KNOWN pvalue_text)) :: ptask_text*',
    'S_done = $drive_steps(S_text,4096)',
    '$drive_steps(S_one[.COMPLETION = NORMAL],4095) = S_done',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
    'S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.HELD = eps',
    'S_done.EVENTS = S_text.EVENTS ++ [OUTPUT $ptascii("0012"),OUTPUT $ptascii(";"),OUTPUT $ptascii("NAME;"),OUTPUT $ptascii("DONE;")]',
    '$heap_owners($heap_graph(S_done),HOBJECT n_receiver) = 1',
    '$call_descriptors_valid(S_done) /\\ $property_state_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
]

UNTYPED_SOURCE = ('<?php $plain = new class { public function __get($incoming) '
                  '{ $incoming = 8; return null; } }; $selector = "12"; '
                  '$plain->$selector; echo "DONE;";')
UNTYPED = [
    'S.CURRENT = eps /\\ S.FRAMES = eps /\\ S.HELD = eps',
    'S.RESULT = KNOWN PNULL /\\ S.BASE = BASE_VALUE (KNOWN PNULL)',
    'S.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*',
    'ppropertyget.NAME = $ptascii("12") /\\ ppropertyget.DECL = eps',
    'ppropertyget.OBJECT = n_receiver',
    '$property_get_method(S,n_receiver) = (pmethoddesc)',
    'pfunction = pmethoddesc.FUNCTION',
    'pfunction.SIGNATURE.PARAMETERS = [psparam]',
    'psparam.TYPE = eps /\\ ~pfunction.SIGNATURE.BYREF /\\ pfunction.SIGNATURE.RETURNS = eps',
    '$ppmethod_get_signature(pfunction.SIGNATURE)',
    'pfunction.ORIGIN = PORIGIN n_unit pcpath_get',
    '$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_get ++ [PCFIELD 4,PCINDEX 0])) = (NParam (SEQUENCE eps) (INTEGER 0) ABSENT (BOOLEAN false) (BOOLEAN false) (NExprVariable (BYTES text_parameter) metadata_name) ABSENT (SEQUENCE eps) metadata_parameter)',
    '$property_empty_get_source(S,pmethoddesc)',
    '~$property_get_string_method(S,pmethoddesc) /\\ ~$property_get_string_source(S,ppropertyget)',
    '$property_get_cv_name_source(S,ppropertyget) /\\ $property_get_source(S,ppropertyget)',
    '$property_get_history(S,ppropertyget) /\\ $property_get_valid(S,ppropertyget,true)',
    '$property_get_verify_desc(S,ppropertyget) = eps /\\ $property_get_tail_valid(S,ppropertyget)',
    '$call_task_valid(S,PROPERTY_GET_RESULT ppropertyget)',
    '~$property_get_name_result_supported(S,ppropertyget,S.RESULT)',
    '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 2',
    'S.EVENTS = eps',
    '$call_descriptors_valid(S) /\\ $property_state_valid(S) /\\ $heap_valid($heap_graph(S))',
    'S_refused = $property_get_complete(S,ppropertyget,S.RESULT)',
    'S_refused.COMPLETION = UNSUPPORTED "CV-name magic getter result or conversion"',
    'S_refused[.COMPLETION = NORMAL] = S',
    'PhpStep: S ~> S_refused',
]

CASES = {
    ROW['id']: {'source': ROW['source'], 'checks': REACHED + CONTROLS + RESULTS + RESUME},
    'genuine-untyped-cv-get-keeps-null-refusal': {
        'source': UNTYPED_SOURCE,
        'stage': ('S.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail* '
                  '-- if S.RESULT = KNOWN PNULL'),
        'checks': UNTYPED,
    },
}


def render(case, fixture, filename):
    if case is not CASES[ROW['id']]:
        return None
    text = (HELPERS + '\ndec $main() : bool\ndef $main() = true\n'
            '  -- if S_initial = $php_run(' + fixture + ',0,' + filename + ')\n'
            '  -- if S_initial.COMPLETION = NORMAL \\/ S_initial.COMPLETION = BUDGET\n'
            '  -- if S_found = $primitive_read_seek(S_initial,PNULL,2000)\n'
            '  -- if S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET\n'
            '  -- if S = S_found[.COMPLETION = NORMAL]\n'
            '  -- if $primitive_read_found(S,PNULL)\n')
    text += ''.join('  -- ' + ('' if check.startswith('PhpStep:') else 'if ') + check + '\n'
                    for check in case['checks'])
    return text, len(case['checks']) + 6


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    protocol.run({name: case for name, case in CASES.items()
                  if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE), fixture_renderer=render,
                 runner_flags=('--sl',))
