#!/usr/bin/env python3
"""Authenticate bounded canonical-string Get entry and its ordinary saved tail."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('magic_property_string_read_get_cases.json')
row = json.loads(CATALOGUE.read_text())['cases'][0]
assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

CASES = {
    'string-read-get-entry-and-tail': {
        'source': row['source'],
        'stage': ('S.CURRENT = eps /\\ S.FRAMES = eps '
                  '-- if S.TODO = (PROPERTY_NAME (POBJECT n_receiver) z_property) :: '
                  '(DIM_FETCH z_property) :: (ORIGIN_RETURN (porigin_parent)) :: '
                  '(BINARY_LEFT IDENTICAL expression_rhs z_rhs) :: ptask_tail*'),
        'checks': [
            'S.ORIGIN = (porigin_site)',
            'S.EVENTS = eps /\\ z_property = 11 /\\ z_rhs = 11',
            '$property_get_method(S,n_receiver) = (pmethoddesc)',
            'pfunction = pmethoddesc.FUNCTION',
            'pfunction.SIGNATURE.PARAMETERS = [psparam]',
            'psparam.TYPE = [(PTBRANCH ([PTBUILTIN "string"]))]',
            '~pfunction.SIGNATURE.BYREF /\\ pfunction.SIGNATURE.RETURNS = eps',
            '$property_empty_get_source(S,pmethoddesc) /\\ $property_get_string_method(S,pmethoddesc)',
            '$ppmethod_get_declaration_signature(pfunction.SIGNATURE) /\\ ~$ppmethod_get_signature(pfunction.SIGNATURE)',
            '$ppmethod_get_signature(pfunction.SIGNATURE[.PARAMETERS = [psparam[.TYPE = eps]]])',
            'S.OBJECTS[n_receiver] = INSTANCE porigin_class',
            'ppropertyget = {SITE porigin_site, NAME $ptascii("12"), LINE z_property, OBJECT n_receiver, CLASS porigin_class, METHOD pfunction.ORIGIN, DECL eps}',
            '$property_get_string_source(S,ppropertyget) /\\ $property_get_cv_name_source(S,ppropertyget)',
            '$property_get_history(S,ppropertyget) /\\ $property_get_valid(S,ppropertyget,true)',
            'ptask_read* = (ORIGIN_RETURN (porigin_parent)) :: (BINARY_LEFT IDENTICAL expression_rhs z_rhs) :: ptask_tail*',
            '$property_get_string_tail(S,ppropertyget,ptask_read*)',
            '$property_get_plan(S) = (ppropertyget)',
            '$property_get_factory(S,ppropertyget) = eps /\\ ~$property_get_this_source(S,ppropertyget) /\\ ~$property_get_indirect_source(S,ppropertyget)',
            '~$property_ref_demand(S)',
            '$property_get_base_count(S.TODO,n_receiver,porigin_site) = 0 /\\ $property_get_input_count(S.TODO,n_receiver,porigin_site) = 0',
            '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 2',
            '$call_descriptors_valid(S) /\\ $class_state_valid(S) /\\ $property_state_valid(S) /\\ $heap_valid($heap_graph(S))',
            '~$property_get_string_method(S[.SOURCES = eps],pmethoddesc)',
            '~$property_get_string_method(S,pmethoddesc[.FUNCTION = pfunction[.SIGNATURE = pfunction.SIGNATURE[.BYREF = true]]])',
            '~$property_get_string_method(S,pmethoddesc[.FUNCTION = pfunction[.SIGNATURE = pfunction.SIGNATURE[.PARAMETERS = [psparam[.TYPE = eps]]]]])',
            '~$property_get_string_method(S,pmethoddesc[.FUNCTION = pfunction[.SIGNATURE = pfunction.SIGNATURE[.PARAMETERS = [psparam[.TYPE = [(PTBRANCH ([PTBUILTIN "mixed"]))]]]]]])',
            '~$property_get_string_source(S,ppropertyget[.DECL = (pfunction.ORIGIN)])',
            '~$property_get_string_source(S,ppropertyget[.CLASS = pfunction.ORIGIN])',
            '~$property_get_string_source(S,ppropertyget[.SITE = pfunction.ORIGIN])',
            '$origin_node(S.SOURCES,porigin_site) = (expression)',
            '$property_get_string_consumer(NExprBinaryOpIdentical expression expression_rhs eps,expression)',
            '$property_get_string_consumer(NStmtExpression expression eps,expression)',
            '~$property_get_string_consumer(NExprAssignRef (NExprVariable (BYTES "eA==") eps) expression eps,expression)',
            '~$property_get_string_consumer(NExprAssignOpPlus expression expression_rhs eps,expression)',
            '~$property_get_string_consumer(NExprEmpty expression eps,expression)',
            '~$property_get_string_consumer(NExprBinaryOpCoalesce expression expression_rhs eps,expression)',
            '~$property_get_string_tail(S,ppropertyget,[ORIGIN_RETURN (porigin_parent),DISCARD])',
            '~$property_get_string_tail(S,ppropertyget,[ORIGIN_RETURN (porigin_parent),BINARY_LEFT IDENTICAL expression_rhs $(z_rhs + 1)])',
            '$property_get_plan(S[.TODO = [PROPERTY_NAME (POBJECT n_receiver) z_property,DIM_FETCH z_property,ORIGIN_RETURN (porigin_parent),DISCARD]]) = eps',
            '$property_get_name_result_supported(S,ppropertyget,KNOWN (PINT 7))',
            '$property_get_name_result_supported(S,ppropertyget,KNOWN PNULL)',
            '~$property_get_name_result_supported(S,ppropertyget,KNOWN (POBJECT n_receiver))',
            'PhpStep: S ~> S_call',
            'S_call.TODO = (CALL_ARGS (PROPERTY_GET_TARGET n_receiver pfunction.ORIGIN) eps 1 ([KNOWN (PSTRING ($ptascii("12")))]) (porigin_site) z_property) :: (PROPERTY_GET_RESULT ppropertyget) :: ptask_read*',
            '$property_get_capture_tail(S_call,ppropertyget) = ptask_read*',
            '$property_get_string_tasks(S_call,ppropertyget,S_call.TODO)',
            '$property_get_tail_valid(S_call,ppropertyget) /\\ $property_get_capture(S_call,ppropertyget)',
            '$property_get_pending_call(S_call,PROPERTY_GET_TARGET n_receiver pfunction.ORIGIN,porigin_site)',
            '$target_function(S_call,PROPERTY_GET_TARGET n_receiver pfunction.ORIGIN) = (pfunction)',
            '$target_nodes(PROPERTY_GET_TARGET n_receiver pfunction.ORIGIN) = eps',
            '$task_nodes(PROPERTY_GET_RESULT ppropertyget) = [HOBJECT n_receiver]',
            '$heap_owners($heap_graph(S_call),HOBJECT n_receiver) = 2',
            '$call_descriptors_valid(S_call) /\\ $property_state_valid(S_call) /\\ $heap_valid($heap_graph(S_call))',
            '~$property_get_string_tasks(S_call,ppropertyget,[PROPERTY_GET_RESULT ppropertyget,ORIGIN_RETURN (porigin_parent),DISCARD])',
            '~$property_get_tail_valid(S_call[.TODO = [PROPERTY_GET_RESULT ppropertyget]],ppropertyget)',
            '~$property_get_capture(S_call[.TODO = [PROPERTY_GET_RESULT ppropertyget]],ppropertyget)',
            'S_zero = $drive_steps(S_call,0)',
            'S_zero = S_call[.COMPLETION = BUDGET]',
            'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
            'S_one.COMPLETION = BUDGET',
            'S_one.TODO = [TYPE_RECEIVE pfunction.ORIGIN 0]',
            'S_one.CURRENT = (pcallcontext)',
            'pcallcontext.TARGET = PROPERTY_GET_TARGET n_receiver pfunction.ORIGIN',
            '$property_get_context(S_one,pcallcontext) /\\ $named_receives_ready(S_one,pfunction)',
            '$typed_receive_valid(S_one,pfunction.ORIGIN,0)',
            '$call_descriptors_valid(S_one) /\\ $property_state_valid(S_one) /\\ $heap_valid($heap_graph(S_one))',
            'S_done = $drive_steps(S_one[.COMPLETION = NORMAL],2000)',
            'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps',
            'S_done.EVENTS = [OUTPUT $ptascii("S;"),OUTPUT $ptascii("G:"),OUTPUT $ptascii("12"),OUTPUT $ptascii(";"),OUTPUT $ptascii("CV;"),OUTPUT $ptascii("S;"),OUTPUT $ptascii("G:"),OUTPUT $ptascii("literal"),OUTPUT $ptascii(";"),OUTPUT $ptascii("LIT;")]',
            '$call_descriptors_valid(S_done) /\\ $property_state_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
        ],
    },
}

if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__), CATALOGUE), runner_flags=('--sl',))
