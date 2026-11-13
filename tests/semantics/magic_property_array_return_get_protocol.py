#!/usr/bin/env python3
"""Source-reached array Get ownership, COW and embedded-reference preservation."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('magic_property_array_return_get_cases.json')
ROW = json.loads(CATALOGUE.read_text())['cases'][1]
SOURCE = ROW['source']
assert hashlib.sha256(SOURCE.encode()).hexdigest() == ROW['source_sha256']

CHECKS = [
    'S.CURRENT = eps /\\ S.FRAMES = eps /\\ S.HELD = eps',
    'n_receiver = ppropertyget.OBJECT',
    'ppropertyget.DECL = eps',
    'ppropertyget.NAME = $ptascii("items")',
    '$property_get_method(S,n_receiver) = (pmethoddesc)',
    'pfunction = pmethoddesc.FUNCTION',
    'pfunction.ORIGIN = ppropertyget.METHOD /\\ ~pfunction.SIGNATURE.BYREF',
    'pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "mixed"]))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam]',
    'psparam.NAME = $ptascii("incoming") /\\ psparam.TYPE = [(PTBRANCH ([PTBUILTIN "string"]))]',
    '$ppmethod_get_decl_return([(PTBRANCH ([PTBUILTIN "array"]))])',
    '~$ppmethod_get_scalar_return([(PTBRANCH ([PTBUILTIN "array"]))])',
    '$ppmethod_get_declaration_signature(pfunction.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "array"]))]])',
    '~$ppmethod_get_decl_return([(PTBRANCH ([PTBUILTIN "array"])),(PTBRANCH ([PTBUILTIN "null"]))])',
    '$property_get_method_source(S,pmethoddesc,true) /\\ ~$property_empty_get_source(S,pmethoddesc)',
    '$property_get_string_source(S,ppropertyget) /\\ $property_get_string_echo_site(S,ppropertyget.SITE) = eps',
    '$property_get_valid(S,ppropertyget,true) /\\ $property_get_tail_valid(S,ppropertyget)',
    '$property_get_verify_desc(S,ppropertyget) = eps',
    '$property_get_name_result_supported(S,ppropertyget,KNOWN (PARRAY n_array))',
    '~$property_get_name_result_supported(S[.ALLOCATIONS = eps],ppropertyget,KNOWN (PARRAY n_array))',
    '~$property_get_name_result_supported(S,ppropertyget,KNOWN (PARRAY (|S.ARRAYS|)))',
    '~$property_get_method_source(S[.SOURCES = eps],pmethoddesc,true)',
    '$lookup($global_table_view(S).ENV,$ptascii("source")) = (n_source)',
    'S.STORE[n_source] = DEFINED (PARRAY n_array)',
    '$lookup($global_table_view(S).ENV,$ptascii("cell")) = (n_cell)',
    'S.STORE[n_cell] = DEFINED (PINT 7)',
    'S.ARRAYS[n_array].ITEMS = [(ENTRY (KINT 0) (DIRECT (PINT 1))),(ENTRY (KINT 1) (ALIAS n_cell))]',
    'S.ARRAYS[n_array].NEXT = 2',
    '(HARRAY n_array) <- S.ALLOCATIONS /\\ (HOBJECT n_receiver) <- S.ALLOCATIONS',
    '$heap_owners($heap_graph(S),HARRAY n_array) = 2',
    '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 2',
    '$task_nodes(PROPERTY_GET_RESULT ppropertyget) = [HOBJECT n_receiver]',
    '$task_nodes(PROPERTY_GET_COPY ppropertyget (KNOWN (PARRAY n_array))) = [HARRAY n_array]',
    '$task_nodes(PROPERTY_GET_DROP ppropertyget (PARRAY n_array)) = [HARRAY n_array]',
    'S.EVENTS = [OUTPUT $ptascii("GET;")]',
    '$call_descriptors_valid(S) /\\ $class_state_valid(S) /\\ $property_state_valid(S) /\\ $heap_valid($heap_graph(S))',
    'PhpStep: S ~> S_copy',
    'S_copy.TODO = (PROPERTY_GET_COPY ppropertyget (KNOWN (PARRAY n_array))) :: ptask_caller*',
    'S_copy.RESULT = KNOWN PNULL /\\ S_copy.BASE = BASE_VALUE (KNOWN PNULL)',
    'S_copy.STORE = S.STORE /\\ S_copy.EVENTS = S.EVENTS',
    '$heap_owners($heap_graph(S_copy),HARRAY n_array) = 2',
    '$heap_owners($heap_graph(S_copy),HOBJECT n_receiver) = 1',
    '~$property_get_guard_tasks(S_copy.TODO,n_receiver,ppropertyget.NAME)',
    '$call_descriptors_valid(S_copy) /\\ $property_state_valid(S_copy) /\\ $heap_valid($heap_graph(S_copy))',
    'PhpStep: S_copy ~> S_read',
    'S_read.TODO = ptask_caller* /\\ S_read.RESULT = KNOWN (PARRAY n_array)',
    'S_read.BASE = BASE_VALUE (KNOWN PNULL)',
    'S_read.STORE = S.STORE /\\ S_read.EVENTS = S.EVENTS',
    '$heap_owners($heap_graph(S_read),HARRAY n_array) = 2',
    '$heap_owners($heap_graph(S_read),HOBJECT n_receiver) = 1',
    'S_zero = $drive_steps(S,0)',
    'S_zero = S[.COMPLETION = BUDGET]',
    'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
    'S_one.COMPLETION = BUDGET /\\ S_one.TODO = S_copy.TODO',
    '$heap_owners($heap_graph(S_one),HARRAY n_array) = 2',
    '$heap_owners($heap_graph(S_one),HOBJECT n_receiver) = 1',
    'S_done = $drive_steps(S_one[.COMPLETION = NORMAL],4096)',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.HELD = eps',
    'S_done.EVENTS = [OUTPUT $ptascii("GET;"),OUTPUT $ptascii("COPY_REF;"),OUTPUT $ptascii("SOURCE;"),OUTPUT $ptascii("ALIAS;")]',
    'S_done.STORE[n_source] = DEFINED (PARRAY n_new)',
    'n_new =/= n_array',
    'S_done.ARRAYS[n_new].ITEMS = [(ENTRY (KINT 0) (DIRECT (PINT 99))),(ENTRY (KINT 1) (ALIAS n_cell))]',
    'S_done.STORE[n_cell] = DEFINED (PINT 8)',
    '~((HARRAY n_array) <- S_done.ALLOCATIONS)',
    '$heap_owners($heap_graph(S_done),HARRAY n_array) = 0',
    '$heap_owners($heap_graph(S_done),HARRAY n_new) = 1',
    '$heap_owners($heap_graph(S_done),HOBJECT n_receiver) = 1',
    '$call_descriptors_valid(S_done) /\\ $class_state_valid(S_done) /\\ $property_state_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
    '$drive_steps(S,4096) = S_done',
]
CASES = {'mixed-array-get-cow-and-reference': {
    'source': SOURCE,
    'stage': ('S.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_caller* '
              '-- if S.RESULT = KNOWN (PARRAY n_array)'),
    'checks': CHECKS,
}}
ECHO_SOURCE = json.loads(CATALOGUE.read_text())['cases'][0]['source'].split('$receiver = new ArrayReturnGet;', 1)[0] + '''$receiver = new ArrayReturnGet;
echo $receiver->good;
'''
CASES['array-get-echo-refusal'] = {
    'source': ECHO_SOURCE,
    'stage': ('S.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_caller* '
              '-- if S.RESULT = KNOWN (PARRAY n_array)'),
    'checks': [
        'S.CURRENT = eps /\\ S.FRAMES = eps',
        '$property_get_method(S,ppropertyget.OBJECT) = (pmethoddesc)',
        'pmethoddesc.FUNCTION.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "array"]))]',
        '$property_get_method_source(S,pmethoddesc,true)',
        '$property_get_string_source(S,ppropertyget)',
        '$property_get_string_echo_site(S,ppropertyget.SITE) = (porigin_echo)',
        '$property_get_valid(S,ppropertyget,true) /\\ $property_get_tail_valid(S,ppropertyget)',
        '$(n_array < |S.ARRAYS|) /\\ (HARRAY n_array) <- S.ALLOCATIONS',
        '~$property_get_name_result_supported(S,ppropertyget,KNOWN (PARRAY n_array))',
        'S.EVENTS = [OUTPUT $ptascii("good"),OUTPUT $ptascii(":")]',
        'PhpStep: S ~> S_refused',
        'S_refused = S[.COMPLETION = UNSUPPORTED "CV-name magic getter result or conversion"]',
        '$heap_owners($heap_graph(S_refused),HARRAY n_array) = $heap_owners($heap_graph(S),HARRAY n_array)',
        '$call_descriptors_valid(S) /\\ $heap_valid($heap_graph(S))',
    ],
}

if __name__ == '__main__':
    protocol.run(CASES,(Path(__file__),CATALOGUE),runner_flags=('--sl',))
