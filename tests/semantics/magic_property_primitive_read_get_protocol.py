#!/usr/bin/env python3
"""Check ordinary typed Get primitive returns, copy ownership and bounded value refusals."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
import closure_call_protocol as protocol

CATALOGUE = ROOT / 'tests/semantics/magic_property_primitive_read_get_cases.json'
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']

CASES = {'primitive-read-get-null-copy-and-values': {
    'source': ROW['source'],
    'stage': ('S.CURRENT = eps /\\ S.FRAMES = eps '
              '-- if S.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail* '
              '-- if S.RESULT = KNOWN PNULL'),
    'checks': [
        'S.HELD = eps /\\ S.ORIGIN = (ppropertyget.SITE)',
        'ppropertyget.NAME = $ptascii("null") /\\ ppropertyget.LINE = 13 /\\ ppropertyget.DECL = eps',
        'n_receiver = ppropertyget.OBJECT',
        'S.OBJECTS[n_receiver] = INSTANCE ppropertyget.CLASS',
        '$class_at(S.CLASSES,ppropertyget.CLASS) = (pclassdesc)',
        'pclassdesc.NAME = $ptascii("PrimitiveReadGet") /\\ pclassdesc.PARENT = eps',
        '$property_get_method(S,n_receiver) = (pmethoddesc)',
        'pfunction = pmethoddesc.FUNCTION',
        'pmethoddesc.OWNER = ppropertyget.CLASS /\\ pfunction.ORIGIN = ppropertyget.METHOD',
        'pfunction.SIGNATURE.PARAMETERS = [psparam]',
        'psparam.TYPE = [(PTBRANCH ([PTBUILTIN "string"]))] /\\ psparam.NAME = $ptascii("incoming")',
        '~pfunction.SIGNATURE.BYREF /\\ pfunction.SIGNATURE.RETURNS = eps',
        '$property_empty_get_source(S,pmethoddesc) /\\ $property_get_string_method(S,pmethoddesc)',
        '$property_get_string_source(S,ppropertyget)',
        '~$property_get_cv_name_source(S,ppropertyget)',
        '$property_get_source(S,ppropertyget) /\\ $property_get_history(S,ppropertyget)',
        '$property_get_valid(S,ppropertyget,true) /\\ $property_get_tail_valid(S,ppropertyget)',
        '$property_get_string_tail(S,ppropertyget,ptask_tail*)',
        '$call_task_valid(S,PROPERTY_GET_RESULT ppropertyget)',
        '$property_get_verify_desc(S,ppropertyget) = eps',
        'S.EVENTS = [OUTPUT $ptascii("null"),OUTPUT $ptascii(":" )]',
        '$lookup(S.ENV,$ptascii("reader")) = (n_reader)',
        'S.STORE[n_reader] = DEFINED (POBJECT n_receiver)',
        '$task_nodes(PROPERTY_GET_RESULT ppropertyget) = [HOBJECT n_receiver]',
        '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 2',
        '$target_nodes(PROPERTY_GET_TARGET n_receiver pfunction.ORIGIN) = eps',
        '$value_nodes(PNULL) = eps /\\ $operand_nodes(KNOWN PNULL) = eps',
        '$value_nodes(PBOOL true) = eps /\\ $value_nodes(PFLOAT 4609434218613702656) = eps',
        '$value_nodes(PSTRING_CARRIER INTERNED_STRING eps) = eps',
        '$string_carrier_valid(S,PSTRING_CARRIER INTERNED_STRING eps)',
        '$property_get_name_result_supported(S,ppropertyget,KNOWN PNULL)',
        '$property_get_name_result_supported(S,ppropertyget,KNOWN (PBOOL true))',
        '$property_get_name_result_supported(S,ppropertyget,KNOWN (PBOOL false))',
        '$property_get_name_result_supported(S,ppropertyget,KNOWN (PFLOAT 4609434218613702656))',
        '$property_get_name_result_supported(S,ppropertyget,KNOWN (PSTRING_CARRIER INTERNED_STRING eps))',
        '$property_get_name_result_supported(S,ppropertyget,KNOWN (PINT 7))',
        '$call_descriptors_valid(S) /\\ $class_state_valid(S) /\\ $property_state_valid(S) /\\ $heap_valid($heap_graph(S))',
        '$property_get_primitive_result(PNULL)',
        '$property_get_primitive_result(PBOOL true) /\\ $property_get_primitive_result(PBOOL false)',
        '$property_get_primitive_result(PFLOAT 4609434218613702656)',
        '$property_get_primitive_result(PFLOAT 9223372036854775808)',
        '$property_get_primitive_result(PSTRING_CARRIER INTERNED_STRING eps)',
        '$property_get_primitive_result(PSTRING_CARRIER INTERNED_STRING ($ptascii("0012")))',
        '~$property_get_primitive_result(PINT 7)',
        '~$property_get_primitive_result(PFLOAT 9218868437227405312)',
        '~$property_get_primitive_result(PFLOAT 9221120237041090560)',
        '~$property_get_primitive_result(PFLOAT 18446744073709551616)',
        '~$property_get_primitive_result(PSTRING_CARRIER INTERNED_STRING ([0]))',
        '~$property_get_primitive_result(PSTRING_CARRIER INTERNED_STRING ([256]))',
        '~$property_get_primitive_result(PSTRING eps)',
        'S_request = $string_request(S,$ptascii("0012"))',
        'S_request.RESULT = KNOWN pvalue_request',
        '$string_carrier_valid(S_request,pvalue_request)',
        '~$property_get_primitive_result(pvalue_request)',
        '~$property_get_name_result_supported(S_request,ppropertyget,KNOWN pvalue_request)',
        '~$property_get_name_result_supported(S,ppropertyget,KNOWN (PARRAY 0))',
        '~$property_get_name_result_supported(S,ppropertyget,KNOWN (POBJECT n_receiver))',
        '~$property_get_name_result_supported(S,ppropertyget,REFERENCE n_reader)',
        '~$property_get_string_source(S,ppropertyget[.DECL = (pfunction.ORIGIN)])',
        '~$property_get_valid(S,ppropertyget[.DECL = (pfunction.ORIGIN)],true)',
        'PhpStep: S ~> S_copy',
        'S_copy.TODO = (PROPERTY_GET_COPY ppropertyget (KNOWN PNULL)) :: ptask_tail*',
        'S_copy.RESULT = KNOWN PNULL /\\ S_copy.BASE = BASE_VALUE (KNOWN PNULL)',
        '$task_nodes(PROPERTY_GET_COPY ppropertyget (KNOWN PNULL)) = eps',
        '$heap_owners($heap_graph(S_copy),HOBJECT n_receiver) = 1',
        '$property_get_valid(S_copy,ppropertyget,false) /\\ $property_get_tail_valid(S_copy,ppropertyget)',
        '$call_task_valid(S_copy,PROPERTY_GET_COPY ppropertyget (KNOWN PNULL))',
        '$call_descriptors_valid(S_copy) /\\ $class_state_valid(S_copy) /\\ $property_state_valid(S_copy) /\\ $heap_valid($heap_graph(S_copy))',
        'S_zero = $drive_steps(S,0)',
        'S_zero = S[.COMPLETION = BUDGET]',
        'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
        'S_one.COMPLETION = BUDGET',
        'S_one.TODO = S_copy.TODO /\\ S_one.RESULT = S_copy.RESULT /\\ S_one.BASE = S_copy.BASE',
        '$heap_owners($heap_graph(S_one),HOBJECT n_receiver) = 1',
        '$call_descriptors_valid(S_one) /\\ $property_state_valid(S_one) /\\ $heap_valid($heap_graph(S_one))',
        'S_done = $drive_steps(S_one[.COMPLETION = NORMAL],4096)',
        'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.HELD = eps',
        'S_done.EVENTS = [OUTPUT $ptascii("null"),OUTPUT $ptascii(":"),OUTPUT $ptascii("N;"),OUTPUT $ptascii("true"),OUTPUT $ptascii(":"),OUTPUT $ptascii("1"),OUTPUT $ptascii(";"),OUTPUT $ptascii("false"),OUTPUT $ptascii(":"),OUTPUT $ptascii("D;"),OUTPUT $ptascii("float"),OUTPUT $ptascii(":"),OUTPUT $ptascii("1.5"),OUTPUT $ptascii(";"),OUTPUT $ptascii("empty"),OUTPUT $ptascii(":"),OUTPUT $ptascii("E;"),OUTPUT $ptascii("DONE;")]',
        '$call_descriptors_valid(S_done) /\\ $class_state_valid(S_done) /\\ $property_state_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
    ],
}}

if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__), CATALOGUE), runner_flags=('--sl',))
