#!/usr/bin/env python3
"""Source-reached Get RV aliases its receiver through strict comparison/RHS."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('magic_property_object_return_get_cases.json')
ROW = json.loads(CATALOGUE.read_text())['cases'][1]
SOURCE = ROW['source']
assert hashlib.sha256(SOURCE.encode()).hexdigest() == ROW['source_sha256']

CHECKS = [
    'S.CURRENT = eps /\\ S.FRAMES = eps /\\ S.HELD = eps',
    'n_receiver = ppropertyget.OBJECT',
    'n_value = n_receiver',
    'ppropertyget.NAME = $ptascii("same") /\\ ppropertyget.DECL = eps',
    '$property_get_method(S,n_receiver) = (pmethoddesc)',
    'pfunction = pmethoddesc.FUNCTION',
    'pfunction.ORIGIN = ppropertyget.METHOD /\\ pfunction.ENDLINE = 8 /\\ ~pfunction.SIGNATURE.BYREF',
    'pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "object"]))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam]',
    'psparam.NAME = $ptascii("incoming") /\\ psparam.TYPE = [(PTBRANCH ([PTBUILTIN "string"]))]',
    '$ppmethod_get_decl_return(pfunction.SIGNATURE.RETURNS) /\\ ~$ppmethod_get_scalar_return(pfunction.SIGNATURE.RETURNS)',
    '~$ppmethod_get_decl_return([(PTBRANCH ([PTBUILTIN "object"])),(PTBRANCH ([PTBUILTIN "null"]))])',
    '$property_get_method_source(S,pmethoddesc,true) /\\ ~$property_empty_get_source(S,pmethoddesc)',
    '~$property_get_method_source(S[.SOURCES = eps],pmethoddesc,true)',
    '~$property_get_method_source(S,pmethoddesc[.FUNCTION = pfunction[.ENDLINE = 9]],true)',
    '$property_get_string_source(S,ppropertyget) /\\ $property_get_string_echo_site(S,ppropertyget.SITE) = eps',
    '$property_get_verify_desc(S,ppropertyget) = eps',
    '$(n_receiver < |S.OBJECTS|) /\\ (HOBJECT n_receiver) <- S.ALLOCATIONS',
    'S.OBJECTS[n_receiver] = INSTANCE ppropertyget.CLASS',
    '$eager_property_class_valid(S,S.OBJECTS[n_receiver]) /\\ ~$instance_storage_freeing(S,n_receiver)',
    '$eager_property_class_valid(S,STDINSTANCE)',
    '$property_get_name_result_supported(S,ppropertyget,KNOWN (POBJECT n_receiver))',
    '~$property_get_name_result_supported(S[.ALLOCATIONS = eps],ppropertyget,KNOWN (POBJECT n_receiver))',
    '~$property_get_name_result_supported(S,ppropertyget,KNOWN (POBJECT (|S.OBJECTS|)))',
    '$property_get_valid(S,ppropertyget,true) /\\ $property_get_tail_valid(S,ppropertyget)',
    '~$property_get_valid(S,ppropertyget[.LINE = $(ppropertyget.LINE + 1)],true)',
    '$lookup($global_table_view(S).ENV,$ptascii("receiver")) = (n_cell)',
    'S.STORE[n_cell] = DEFINED PNULL',
    'S.EVENTS = [OUTPUT $ptascii("GET;")]',
    '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 2',
    '$task_nodes(PROPERTY_GET_RESULT ppropertyget) = [HOBJECT n_receiver]',
    '$task_nodes(PROPERTY_GET_COPY ppropertyget (KNOWN (POBJECT n_receiver))) = [HOBJECT n_receiver]',
    '$property_get_guard_tasks(S.TODO,n_receiver,ppropertyget.NAME)',
    '$call_descriptors_valid(S) /\\ $class_state_valid(S) /\\ $property_state_valid(S) /\\ $heap_valid($heap_graph(S))',
    'PhpStep: S ~> S_copy',
    'S_copy.TODO = (PROPERTY_GET_COPY ppropertyget (KNOWN (POBJECT n_receiver))) :: (ORIGIN_RETURN (porigin_binary)) :: (BINARY_LEFT IDENTICAL expression_rhs z) :: ptask_tail*',
    'S_copy.RESULT = KNOWN PNULL /\\ S_copy.BASE = BASE_VALUE (KNOWN PNULL)',
    'S_copy.STORE = S.STORE /\\ S_copy.EVENTS = S.EVENTS',
    '$heap_owners($heap_graph(S_copy),HOBJECT n_receiver) = 1',
    '~$property_get_guard_tasks(S_copy.TODO,n_receiver,ppropertyget.NAME)',
    'PhpStep: S_copy ~> S_value',
    'S_value.RESULT = KNOWN (POBJECT n_receiver) /\\ S_value.BASE = BASE_VALUE (KNOWN PNULL)',
    '$heap_owners($heap_graph(S_value),HOBJECT n_receiver) = 1',
    'PhpStep: S_value ~> S_origin',
    'S_origin.ORIGIN = (porigin_binary)',
    'S_origin.TODO = (BINARY_LEFT IDENTICAL expression_rhs z) :: ptask_tail*',
    'PhpStep: S_origin ~> S_rhs',
    'S_rhs.TODO = [$at_task($origin_child((porigin_binary),[PCFIELD 1]),EVAL expression_rhs),BINARY_RIGHT IDENTICAL (KNOWN (POBJECT n_receiver)) z] ++ ptask_tail*',
    'S_rhs.RESULT = KNOWN PNULL /\\ S_rhs.EVENTS = S.EVENTS',
    '$task_nodes(BINARY_RIGHT IDENTICAL (KNOWN (POBJECT n_receiver)) z) = [HOBJECT n_receiver]',
    '$heap_owners($heap_graph(S_rhs),HOBJECT n_receiver) = 1',
    '(HOBJECT n_receiver) <- S_rhs.ALLOCATIONS',
    '$call_descriptors_valid(S_rhs) /\\ $heap_valid($heap_graph(S_rhs))',
    'S_zero = $drive_steps(S,0)',
    'S_zero = S[.COMPLETION = BUDGET]',
    'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
    'S_one.COMPLETION = BUDGET',
    'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: S_copy.TODO',
    'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_receiver)]',
    'pdestructionoperation.SOURCE = PROPERTY_GET_RESULT ppropertyget',
    'pdestructionoperation.VALUE = KNOWN PNULL /\\ pdestructionoperation.PENDING = eps',
    '$task_nodes(DESTRUCTOR_RELEASE pdestructionrelease) = [HOBJECT n_receiver]',
    '$heap_owners($heap_graph(S_one),HOBJECT n_receiver) = 2 /\\ $native_rc(S_one,HOBJECT n_receiver) = 2',
    'S_one.NATIVEEXCESS = eps /\\ S_one.EVENTS = S.EVENTS',
    '~(n_receiver <- S_one.DESTRUCTION.CALLED)',
    '$call_descriptors_valid(S_one) /\\ $heap_valid($heap_graph(S_one))',
    'PhpStep: S_one[.COMPLETION = NORMAL] ~> S_unheld',
    'S_unheld.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_empty) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: S_copy.TODO',
    'pdestructionrelease_empty.JOBS = eps',
    '$heap_owners($heap_graph(S_unheld),HOBJECT n_receiver) = 1 /\\ $native_rc(S_unheld,HOBJECT n_receiver) = 1',
    'S_unheld.EVENTS = S.EVENTS /\\ ~(n_receiver <- S_unheld.DESTRUCTION.CALLED)',
    'PhpStep: S_unheld ~> S_exit',
    'S_exit.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: S_copy.TODO',
    'PhpStep: S_exit ~> S_ready',
    'S_ready.TODO = S_copy.TODO /\\ S_ready.RESULT = KNOWN PNULL /\\ S_ready.BASE = BASE_VALUE (KNOWN PNULL)',
    'S_ready.EVENTS = S.EVENTS /\\ S_ready.STORE[n_cell] = DEFINED PNULL',
    'S_ready.DESTRUCTION.OPERATIONS = eps /\\ S_ready.DESTRUCTION.RELEASES = eps /\\ S_ready.DESTRUCTION.CALLS = eps',
    '$heap_owners($heap_graph(S_ready),HOBJECT n_receiver) = 1',
    '~(n_receiver <- S_ready.DESTRUCTION.CALLED)',
    '$call_descriptors_valid(S_ready) /\\ $heap_valid($heap_graph(S_ready))',
    'S_done = $drive_steps(S_one[.COMPLETION = NORMAL],4096)',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.HELD = eps',
    'S_done.DESTRUCTION.PHASE = DESTRUCTION_DONE /\\ S_done.DESTRUCTION.OPERATIONS = eps /\\ S_done.DESTRUCTION.CALLS = eps',
    'S_done.EVENTS = [OUTPUT $ptascii("GET;"),OUTPUT $ptascii("RHS;"),OUTPUT $ptascii("RECEIVER;"),OUTPUT $ptascii("OBJECT;"),OUTPUT $ptascii("DONE;")]',
    'S_done.STORE[n_cell] = DEFINED PNULL',
    '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
    '$heap_owners($heap_graph(S_done),HOBJECT n_receiver) = 0',
    '~$property_get_guard_tasks(S_done.TODO,n_receiver,ppropertyget.NAME) /\\ ~$property_get_guard_frames(S_done.FRAMES,n_receiver,ppropertyget.NAME)',
    '$call_descriptors_valid(S_done) /\\ $class_state_valid(S_done) /\\ $property_state_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
    '$drive_steps(S,4096) = S_done',
]
CASES = {'object-get-receiver-rv-transfer': {
    'source': SOURCE,
    'stage': ('S.TODO = (PROPERTY_GET_RESULT ppropertyget) :: (ORIGIN_RETURN (porigin_binary)) :: (BINARY_LEFT IDENTICAL expression_rhs z) :: ptask_tail* '
              '-- if S.RESULT = KNOWN (POBJECT n_value)'),
    'checks': CHECKS,
}}
ECHO_SOURCE = SOURCE.split('$receiver = new SelfObjectGet;',1)[0] + '''$receiver = new SelfObjectGet;
echo $receiver->same;
'''
INTERNAL_SOURCE = '''<?php
class InternalObjectGet {
    public function __get(string $incoming): mixed {
        echo "GET;";
        return new Exception("payload");
    }
}
$receiver = new InternalObjectGet;
$receiver->inside;
'''
for name, source, echo in [('object-get-echo-refusal',ECHO_SOURCE,True),
                           ('object-get-internal-kind-refusal',INTERNAL_SOURCE,False)]:
    CASES[name] = {
        'source': source,
        'stage': ('S.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_caller* '
                  '-- if S.RESULT = KNOWN (POBJECT n_value)'),
        'checks': [
            'S.CURRENT = eps /\\ S.FRAMES = eps',
            '$property_get_method(S,ppropertyget.OBJECT) = (pmethoddesc)',
            '$property_get_method_source(S,pmethoddesc,true)',
            '$property_get_string_source(S,ppropertyget)',
            '$property_get_verify_desc(S,ppropertyget) = eps',
            '$(n_value < |S.OBJECTS|) /\\ (HOBJECT n_value) <- S.ALLOCATIONS',
            ('$eager_property_class_valid(S,S.OBJECTS[n_value]) /\\ ~$instance_storage_freeing(S,n_value)'
             if echo else '~$eager_property_class_valid(S,S.OBJECTS[n_value])'),
            ('$property_get_string_echo_site(S,ppropertyget.SITE) = (porigin_echo)'
             if echo else '$property_get_string_echo_site(S,ppropertyget.SITE) = eps'),
            '~$property_get_name_result_supported(S,ppropertyget,KNOWN (POBJECT n_value))',
            '$property_get_valid(S,ppropertyget,true) /\\ $property_get_tail_valid(S,ppropertyget)',
            'S.EVENTS = [OUTPUT $ptascii("GET;")]',
            'PhpStep: S ~> S_refused',
            'S_refused = S[.COMPLETION = UNSUPPORTED "CV-name magic getter result or conversion"]',
            '$heap_owners($heap_graph(S_refused),HOBJECT n_value) = $heap_owners($heap_graph(S),HOBJECT n_value)',
            '$call_descriptors_valid(S) /\\ $heap_valid($heap_graph(S))',
        ],
    }
    if not echo:
        CASES[name]['checks'] += [
            'S.OBJECTS[n_value] = THROWABLE pthrowable',
            'pthrowable.KIND = "Exception"',
            '$string_bytes($throwable_field(S,n_value,"message")) = ($ptascii("payload"))',
        ]

if __name__ == '__main__':
    protocol.run(CASES,(Path(__file__),CATALOGUE),runner_flags=('--sl',))
