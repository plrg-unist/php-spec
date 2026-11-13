#!/usr/bin/env python3
"""Check a direct object result through receiver and payload exceptions."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol


CATALOGUE = Path(__file__).with_name('magic_property_object_return_get_review_cases.json')
ROW = json.loads(CATALOGUE.read_text())['cases'][2]
SOURCE = ROW['source']
assert hashlib.sha256(SOURCE.encode()).hexdigest() == ROW['source_sha256']

HELPERS = r'''
dec $object_get_dtor(pstate,nat) : bool
def $object_get_dtor(S,n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n
def $object_get_dtor(S,n) = false -- otherwise
dec $object_get_seek_dtor(pstate,nat,nat) : pstate
def $object_get_seek_dtor(S,n_object,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $object_get_seek_dtor(S,n_object,n) = S
  -- if $object_get_dtor(S,n_object)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $object_get_seek_dtor(S,n_object,0) = S
  -- if ~$object_get_dtor(S,n_object)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $object_get_seek_dtor(S,n_object,n) = $object_get_seek_dtor($drive_steps(S[.COMPLETION = NORMAL],1),n_object,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$object_get_dtor(S,n_object)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $object_get_catch(pstate) : bool
def $object_get_catch(S) = true
  -- if S.TODO = (CATCH_BIND porigin n_index n_error) :: ptask_tail*
def $object_get_catch(S) = false -- otherwise
dec $object_get_seek_catch(pstate,nat) : pstate
def $object_get_seek_catch(S,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $object_get_seek_catch(S,n) = S
  -- if $object_get_catch(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $object_get_seek_catch(S,0) = S
  -- if ~$object_get_catch(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $object_get_seek_catch(S,n) = $object_get_seek_catch($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$object_get_catch(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''

CHECKS = [
    'S.CURRENT = eps /\\ S.FRAMES = eps /\\ S.HELD = eps',
    'ppropertyget.NAME = $ptascii("gone") /\\ ppropertyget.DECL = eps',
    'n_receiver = ppropertyget.OBJECT',
    '$property_get_method(S,n_receiver) = (pmethoddesc)',
    'pfunction = pmethoddesc.FUNCTION',
    'pfunction.ORIGIN = ppropertyget.METHOD /\\ pfunction.ENDLINE = 14',
    'pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "mixed"]))] /\\ ~pfunction.SIGNATURE.BYREF',
    'pfunction.SIGNATURE.PARAMETERS = [psparam]',
    'psparam.TYPE = [(PTBRANCH ([PTBUILTIN "string"]))] /\\ psparam.NAME = $ptascii("incoming")',
    '$class_at(S.CLASSES,pmethoddesc.OWNER) = (pclassdesc)',
    'pclassdesc.PARENT = eps /\\ pclassdesc.ORIGIN = ppropertyget.CLASS',
    'pfunction.ORIGIN = PORIGIN n_unit pcpath_method',
    '$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_method ++ [PCFIELD 5])) = (NIdentifier (BYTES text_return) metadata_return)',
    '$ptlc($base64(text_return)) = $ptascii("mixed")',
    'ptcontext = {NAMESPACE pfunction.ENV.NAMESPACE, IMPORTS pfunction.ENV.CLASSES, SCOPE PTKNOWN pclassdesc.NAME eps, POSITION PTRETURN, OWNER pclassdesc.NAME, MEMBER pmethoddesc.NAME, FILE $call_sourcefile(S.FILES,pfunction.ORIGIN), LINE pfunction.LINE}',
    '$ptype_normalize(NIdentifier (BYTES text_return) metadata_return,ptcontext) = PTOK pfunction.SIGNATURE.RETURNS eps',
    '$ppmethod_get_decl_return([(PTBRANCH ([PTBUILTIN "object"]))]) /\\ ~$ppmethod_get_scalar_return([(PTBRANCH ([PTBUILTIN "object"]))])',
    '~$ppmethod_get_decl_return([(PTBRANCH ([PTBUILTIN "object"])),(PTBRANCH ([PTBUILTIN "null"]))])',
    '$property_get_return_type_source(NIdentifier (BYTES text_return) metadata_return,pfunction.SIGNATURE.RETURNS,ptcontext,true)',
    '~$property_get_return_type_source(NIdentifier (BYTES text_return) metadata_return,pfunction.SIGNATURE.RETURNS,ptcontext,false)',
    '~$property_get_return_type_source(NIdentifier (BYTES text_return) metadata_return,[(PTBRANCH ([PTBUILTIN "object"]))],ptcontext,true)',
    '$property_get_method_source(S,pmethoddesc,true) /\\ ~$property_empty_get_source(S,pmethoddesc)',
    '~$property_get_method_source(S[.SOURCES = eps],pmethoddesc,true)',
    '~$property_get_method_source(S,pmethoddesc[.FUNCTION = pfunction[.ENDLINE = 15]],true)',
    '$property_get_string_source(S,ppropertyget)',
    '~$property_get_valid(S,ppropertyget[.LINE = $(ppropertyget.LINE + 1)],true)',
    '$property_get_string_echo_site(S,ppropertyget.SITE) = eps',
    '$property_get_verify_desc(S,ppropertyget) = eps',
    '$property_get_name_result_supported(S,ppropertyget,KNOWN (POBJECT n_payload))',
    '~$property_get_name_result_supported(S,ppropertyget,KNOWN (POBJECT (|S.OBJECTS|)))',
    '~$property_get_name_result_supported(S[.ALLOCATIONS = eps],ppropertyget,KNOWN (POBJECT n_payload))',
    '~$property_get_primitive_result(POBJECT n_payload)',
    'n_payload =/= n_receiver',
    'S.OBJECTS[n_payload] = INSTANCE porigin_payload',
    '$eager_property_class_valid(S,S.OBJECTS[n_payload]) /\\ ~$instance_storage_freeing(S,n_payload)',
    '$property_get_string_source(S[.CLASSES = [pclassdesc]],ppropertyget)',
    '~$property_get_name_result_supported(S[.CLASSES = [pclassdesc]],ppropertyget,KNOWN (POBJECT n_payload))',
    '(HOBJECT n_receiver) <- S.ALLOCATIONS /\\ (HOBJECT n_payload) <- S.ALLOCATIONS',
    '$heap_owners($heap_graph(S),HOBJECT n_payload) = 1',
    '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 1',
    '$lookup(S.ENV,$ptascii("reader")) = (n_reader)',
    '$lookup(S.ENV,$ptascii("payload")) = (n_payload_cell)',
    'S.STORE[n_reader] = DEFINED PNULL /\\ S.STORE[n_payload_cell] = DEFINED PNULL',
    'S.EVENTS = [OUTPUT $ptascii("GET;")]',
    '$call_descriptors_valid(S) /\\ $class_state_valid(S) /\\ $property_state_valid(S) /\\ $heap_valid($heap_graph(S))',
    'PhpStep: S ~> S_copy',
    'S_copy.TODO = (PROPERTY_GET_COPY ppropertyget (KNOWN (POBJECT n_payload))) :: ptask_caller*',
    'S_copy.RESULT = KNOWN PNULL /\\ S_copy.BASE = BASE_VALUE (KNOWN PNULL)',
    '$task_nodes(PROPERTY_GET_COPY ppropertyget (KNOWN (POBJECT n_payload))) = [HOBJECT n_payload]',
    '$heap_owners($heap_graph(S_copy),HOBJECT n_payload) = 1',
    '$heap_owners($heap_graph(S_copy),HOBJECT n_receiver) = 0',
    '~$property_get_guard_tasks(S_copy.TODO,n_receiver,ppropertyget.NAME)',
    'S_zero = $drive_steps(S,0)',
    'S_zero = S[.COMPLETION = BUDGET]',
    'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
    'S_one.COMPLETION = BUDGET',
    'S_receiver_found = $object_get_seek_dtor(S_one[.COMPLETION = NORMAL],n_receiver,2000)',
    'S_receiver_found.COMPLETION = NORMAL \\/ S_receiver_found.COMPLETION = BUDGET',
    'S_receiver = S_receiver_found[.COMPLETION = NORMAL]',
    '$object_get_dtor(S_receiver,n_receiver)',
    'S_receiver.CURRENT = (pcallcontext_receiver)',
    '$destructor_context_call(pcallcontext_receiver,S_receiver.CURRENT,S_receiver.FRAMES) = (pdestructorcall_receiver)',
    'pdestructorcall_receiver.OPERATION = (pdestructionoperation_receiver)',
    'pdestructionoperation_receiver.SOURCE = PROPERTY_GET_RESULT ppropertyget',
    'pdestructionoperation_receiver.VALUE = KNOWN PNULL /\\ pdestructionoperation_receiver.PENDING = eps',
    '$heap_owners($heap_graph(S_receiver),HOBJECT n_payload) = 1',
    'S_receiver.EVENTS = S.EVENTS',
    '$call_descriptors_valid(S_receiver) /\\ $heap_valid($heap_graph(S_receiver))',
    'S_payload_found = $object_get_seek_dtor(S_receiver,n_payload,2000)',
    'S_payload_found.COMPLETION = NORMAL \\/ S_payload_found.COMPLETION = BUDGET',
    'S_payload = S_payload_found[.COMPLETION = NORMAL]',
    '$object_get_dtor(S_payload,n_payload)',
    'S_payload.CURRENT = (pcallcontext_payload)',
    '$destructor_context_call(pcallcontext_payload,S_payload.CURRENT,S_payload.FRAMES) = (pdestructorcall_payload)',
    'pdestructorcall_payload.OPERATION = (pdestructionoperation_payload)',
    'pdestructionoperation_payload.PENDING = (n_receiver_error)',
    'pdestructionoperation_payload.SOURCE = THROW_SEARCH n_receiver_error',
    '$string_bytes($throwable_field(S_payload,n_receiver_error,"message")) = ($ptascii("receiver-object"))',
    '~((HOBJECT n_receiver) <- S_payload.ALLOCATIONS) /\\ (HOBJECT n_payload) <- S_payload.ALLOCATIONS',
    'S_payload.EVENTS = [OUTPUT $ptascii("GET;"),OUTPUT $ptascii("RECEIVER;")]',
    '~$property_get_guard_tasks(S_payload.TODO,n_receiver,ppropertyget.NAME) /\\ ~$property_get_guard_frames(S_payload.FRAMES,n_receiver,ppropertyget.NAME)',
    '$call_descriptors_valid(S_payload) /\\ $heap_valid($heap_graph(S_payload))',
    'S_payload_zero = $drive_steps(S_payload,0)',
    'S_payload_zero = S_payload[.COMPLETION = BUDGET]',
    'S_payload_one = $drive_steps(S_payload_zero[.COMPLETION = NORMAL],1)',
    'S_payload_one.COMPLETION = BUDGET',
    'S_catch_found = $object_get_seek_catch(S_payload_one[.COMPLETION = NORMAL],2000)',
    'S_catch_found.COMPLETION = NORMAL \\/ S_catch_found.COMPLETION = BUDGET',
    'S_catch = S_catch_found[.COMPLETION = NORMAL]',
    'S_catch.TODO = (CATCH_BIND porigin_try n_catch n_payload_error) :: ptask_catch*',
    'S_catch.CURRENT = eps /\\ S_catch.FRAMES = eps /\\ S_catch.GLOBALTABLE = eps',
    '$call_task_valid(S_catch,CATCH_BIND porigin_try n_catch n_payload_error)',
    '$throwable_field(S_catch,n_payload_error,"previous") = POBJECT n_receiver_error',
    '$string_bytes($throwable_field(S_catch,n_payload_error,"message")) = ($ptascii("payload-object"))',
    '$throwable_field(S_catch,n_receiver_error,"previous") = PNULL',
    'S_catch.EVENTS = [OUTPUT $ptascii("GET;"),OUTPUT $ptascii("RECEIVER;"),OUTPUT $ptascii("PAYLOAD;")]',
    'PhpStep: S_catch ~> S_bound',
    '$lookup(S_bound.ENV,$ptascii("failure")) = (n_failure)',
    'S_bound.STORE[n_failure] = DEFINED (POBJECT n_payload_error)',
    '(HOBJECT n_payload_error) <- S_bound.ALLOCATIONS /\\ (HOBJECT n_receiver_error) <- S_bound.ALLOCATIONS',
    '$call_descriptors_valid(S_bound) /\\ $heap_valid($heap_graph(S_bound))',
    'S_done = $drive_steps(S_bound,4096)',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.HELD = eps',
    'S_done.DESTRUCTION.OPERATIONS = eps /\\ S_done.DESTRUCTION.CALLS = eps',
    'S_done.DESTRUCTION.PHASE = DESTRUCTION_DONE /\\ S_done.GLOBALTABLE = eps',
    'S_done.EVENTS = [OUTPUT $ptascii("GET;"),OUTPUT $ptascii("RECEIVER;"),OUTPUT $ptascii("PAYLOAD;"),OUTPUT $ptascii("payload-object"),OUTPUT $ptascii(";"),OUTPUT $ptascii("receiver-object"),OUTPUT $ptascii(";"),OUTPUT $ptascii("CLEARED;"),OUTPUT $ptascii("DONE;")]',
    '$lookup(S_done.ENV,$ptascii("failure")) = eps',
    '~((HOBJECT n_payload_error) <- S_done.ALLOCATIONS) /\\ ~((HOBJECT n_receiver_error) <- S_done.ALLOCATIONS)',
    'S_done.STORE[n_reader] = DEFINED PNULL /\\ S_done.STORE[n_payload_cell] = DEFINED PNULL',
    '~((HOBJECT n_receiver) <- S_done.ALLOCATIONS) /\\ ~((HOBJECT n_payload) <- S_done.ALLOCATIONS)',
    '~$property_get_guard_tasks(S_done.TODO,n_receiver,ppropertyget.NAME) /\\ ~$property_get_guard_frames(S_done.FRAMES,n_receiver,ppropertyget.NAME)',
    '$call_descriptors_valid(S_done) /\\ $class_state_valid(S_done) /\\ $property_state_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
    '$drive_steps(S_catch,4096) = S_done',
    '$drive_steps(S_payload,4096) = S_done',
    '$drive_steps(S,4096) = S_done',
]

CASES = {'anonymous-object-get-pending-payload-cleanup': {
    'source': SOURCE,
    'stage': ('S.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_caller* '
              '-- if S.RESULT = KNOWN (POBJECT n_payload)'),
    'checks': CHECKS,
}}


def render(case, fixture, filename):
    stage = case['stage']
    text = (HELPERS + '\ndec $stage(pstate) : bool\n'
            'def $stage(S) = true -- if ' + stage + '\n'
            'def $stage(S) = false -- otherwise\n'
            'dec $seek(pstate,nat) : pstate\n'
            'def $seek(S,n) = S -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET\n'
            'def $seek(S,n) = S -- if $stage(S) -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
            'def $seek(S,0) = S -- if ~$stage(S) -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
            'def $seek(S,n) = $seek($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1))) '
            '-- if $(n > 0) /\\ ~$stage(S) -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
            'dec $main() : bool\ndef $main() = true\n'
            '  -- if S_initial = $php_run(' + fixture + ',0,' + filename + ')\n'
            '  -- if S_initial.COMPLETION = NORMAL \\/ S_initial.COMPLETION = BUDGET\n'
            '  -- if S_found = $seek(S_initial,2000)\n'
            '  -- if S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET\n'
            '  -- if S = S_found[.COMPLETION = NORMAL]\n'
            '  -- if ' + stage + '\n')
    text += ''.join('  -- ' + ('' if check.startswith('PhpStep:') else 'if ') + check + '\n'
                    for check in case['checks'])
    return text, len(case['checks']) + 6


if __name__ == '__main__':
    protocol.run(CASES,(Path(__file__),CATALOGUE),runner_flags=('--sl',),
                 fixture_renderer=render)
