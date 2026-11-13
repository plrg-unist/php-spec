#!/usr/bin/env python3
"""Independent singleton-Echo Get history, saved tail and ownership in fixture SL_mode."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol


CATALOGUE = Path(__file__).with_name('magic_property_string_echo_get_review_cases.json')
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == (
    '54bb7edfbcc24598aa54dae0bbf99f5ed4b381a216a2d2510074424ef08ad709')


REACHED = [
    'S.RESULT = KNOWN (PINT 17) /\\ S.HELD = eps',
    '$call_task_valid(S,RETURN_VALUE z_return)',
    'S.FRAMES = [pframe]',
    'pframe.CONTEXT = eps',
    'pframe.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*',
    'ppropertyget.OBJECT = n_receiver /\\ ppropertyget.METHOD = porigin_get',
    'ppropertyget.NAME = $ptascii("12") /\\ ppropertyget.LINE = 10 /\\ ppropertyget.DECL = eps',
    'pframe.ORIGIN = (ppropertyget.SITE)',
    'S.OBJECTS[n_receiver] = INSTANCE ppropertyget.CLASS',
    '$class_at(S.CLASSES,ppropertyget.CLASS) = (pclassdesc)',
    '$property_get_method(S,n_receiver) = (pmethoddesc_get)',
    'pfunction = pmethoddesc_get.FUNCTION',
    'pfunction.ORIGIN = porigin_get /\\ pmethoddesc_get.OWNER = pclassdesc.ORIGIN',
    'pfunction.SIGNATURE.PARAMETERS = [psparam]',
    'psparam.TYPE = [(PTBRANCH ([PTBUILTIN "string"]))] /\\ psparam.NAME = $ptascii("incoming")',
    '~pfunction.SIGNATURE.BYREF /\\ pfunction.SIGNATURE.RETURNS = eps',
    'pfunction.ENV.NAMESPACE = eps /\\ pfunction.ENV.CLASSES = eps /\\ ~pfunction.ENV.STRICT',
    '$ppmethod_get_declaration_signature(pfunction.SIGNATURE) /\\ ~$ppmethod_get_signature(pfunction.SIGNATURE)',
    '$property_empty_get_source(S,pmethoddesc_get) /\\ $property_get_string_method(S,pmethoddesc_get)',
    '$property_get_string_source(S,ppropertyget) /\\ $property_get_history(S,ppropertyget)',
    '$property_get_cv_name_source(S,ppropertyget) /\\ $property_get_valid(S,ppropertyget,true)',
    '$property_get_frame(S,pcallcontext,pframe)',
    '$property_get_entered(S,S.CURRENT,S.FRAMES,pcallcontext.TARGET,ppropertyget.SITE)',
    '$property_get_context(S,pcallcontext) /\\ $named_receives_ready(S,pfunction)',
    '$target_function(S,pcallcontext.TARGET) = (pfunction)',
    '$target_nodes(pcallcontext.TARGET) = eps /\\ $target_instance(pcallcontext.TARGET) = eps /\\ $call_receiver_roots(pcallcontext) = eps',
    '$task_nodes(PROPERTY_GET_RESULT ppropertyget) = [HOBJECT n_receiver]',
    '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 2',
    '$lookup(S.ENV,$ptascii("incoming")) = (n_formal)',
    'S.STORE[n_formal] = DEFINED (PINT 9)',
    'S_caller = $constant_frame_scope(S,pframe,eps)',
    '$lookup(S_caller.ENV,$ptascii("reader")) = (n_reader_cell)',
    'S.STORE[n_reader_cell] = DEFINED (POBJECT n_receiver)',
    '$lookup(S_caller.ENV,$ptascii("name")) = (n_name_cell)',
    'S.STORE[n_name_cell] = DEFINED pvalue_name',
    '$string_bytes(pvalue_name) = ($ptascii("12"))',
    'ptask_tail* = (ORIGIN_RETURN (porigin_echo)) :: (AT porigin_site (EMIT z_emit)) :: ptask_after*',
    'porigin_site = ppropertyget.SITE',
    'porigin_site = PORIGIN n_unit pcpath_site',
    'porigin_echo = PORIGIN n_unit pcpath_echo',
    'pcpath_site = pcpath_echo ++ [PCFIELD 0,PCINDEX 0]',
    '$origin_node(S.SOURCES,porigin_site) = (expression_property)',
    '$origin_node(S.SOURCES,porigin_echo) = (NStmtEcho (SEQUENCE ([expression_property])) metadata_echo)',
    '$property_get_string_echo_site(S,porigin_site) = (porigin_echo)',
    '$property_get_string_consumer_site(S,porigin_site,expression_property)',
    'z_emit = $echo_expression_line(S[.ORIGIN = (porigin_site)],expression_property) /\\ z_emit = 10',
    '$property_get_string_tail(S,ppropertyget,ptask_tail*)',
    '$property_get_string_tasks(S,ppropertyget,pframe.TODO)',
    'S_pending = S_caller[.TODO = (CALL_ARGS (PROPERTY_GET_TARGET n_receiver porigin_get) eps 1 ([KNOWN (PSTRING ppropertyget.NAME)]) (porigin_site) ppropertyget.LINE) :: pframe.TODO][.ORIGIN = (porigin_site)][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    '$property_get_capture_tail(S_pending,ppropertyget) = ptask_tail*',
    '$property_get_capture(S_pending,ppropertyget) /\\ $property_get_pending_call(S_pending,pcallcontext.TARGET,porigin_site)',
    '$property_get_factory(S,ppropertyget) = eps /\\ ~$property_get_this_source(S,ppropertyget) /\\ ~$property_get_indirect_source(S,ppropertyget)',
    '~$property_get_owned_source(S,ppropertyget) /\\ ~$property_get_reference_source(S,ppropertyget)',
    'S.EVENTS = [OUTPUT $ptascii("STR;")]',
    '$call_descriptors_valid(S) /\\ $class_state_valid(S) /\\ $property_state_valid(S) /\\ $heap_valid($heap_graph(S))',
]


CONTROLS = [
    '~$property_get_string_consumer(NStmtEcho (SEQUENCE ([expression_property])) metadata_echo,expression_property)',
    '~$property_get_string_consumer_site(S,porigin_echo,expression_property)',
    '~$property_get_string_consumer_site(S,porigin_site,NScalarInt (INTEGER 7) eps)',
    '$property_get_string_echo_site(S,porigin_echo) = eps',
    '$property_get_string_echo_site(S,PORIGIN n_unit (pcpath_echo ++ [PCFIELD 0,PCINDEX 1])) = eps',
    '$property_get_string_echo_site(S[.SOURCES = eps],porigin_site) = eps',
    'S.SOURCES = [pcunit]',
    'pcunit.ID = n_unit',
    'pcunit.AST = PROGRAM statement_all*',
    'pcpath_echo = [PCINDEX n_echo]',
    'n_after = $nabs($(|statement_all*| - n_echo - 1))',
    'pcunit_comma = $pcsource(n_unit,PROGRAM (statement_all*[0:n_echo] ++ [NStmtEcho (SEQUENCE ([expression_property,expression_property])) metadata_echo] ++ statement_all*[$nabs($(n_echo + 1)):n_after]))',
    'S_comma = S[.SOURCES = [pcunit_comma]]',
    '$property_get_string_echo_site(S_comma,porigin_site) = eps',
    '~$property_get_string_consumer_site(S_comma,porigin_site,expression_property)',
    '~$property_get_string_tail(S_comma,ppropertyget,ptask_tail*)',
    '~$property_get_string_tail(S,ppropertyget,eps)',
    '~$property_get_string_tail(S,ppropertyget,(ORIGIN_RETURN (porigin_echo)) :: (EMIT z_emit) :: ptask_after*)',
    '~$property_get_string_tail(S,ppropertyget,(ORIGIN_RETURN (porigin_site)) :: (AT porigin_site (EMIT z_emit)) :: ptask_after*)',
    '~$property_get_string_tail(S,ppropertyget,(ORIGIN_RETURN (porigin_echo)) :: (AT porigin_echo (EMIT z_emit)) :: ptask_after*)',
    '~$property_get_string_tail(S,ppropertyget,(ORIGIN_RETURN (porigin_echo)) :: (AT porigin_site (EMIT $(z_emit + 1))) :: ptask_after*)',
    '~$property_get_string_tail(S,ppropertyget,(ORIGIN_RETURN (porigin_echo)) :: DISCARD :: ptask_after*)',
    '~$property_get_string_tail(S,ppropertyget,(AT porigin_site (EMIT z_emit)) :: ptask_after*)',
    '~$property_get_string_tasks(S,ppropertyget,[(PROPERTY_GET_RESULT ppropertyget)])',
    '~$property_get_string_tasks(S,ppropertyget,(PROPERTY_GET_RESULT ppropertyget) :: (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*)',
    '$property_get_string_tasks(S,ppropertyget,(PROPERTY_GET_COPY ppropertyget (KNOWN (PINT 17))) :: ptask_tail*)',
    '~$property_get_tail_valid(S_pending[.TODO = [(PROPERTY_GET_RESULT ppropertyget)]],ppropertyget)',
    '~$property_get_capture(S_pending[.TODO = [(CALL_ARGS (PROPERTY_GET_TARGET n_receiver porigin_get) eps 1 ([KNOWN (PSTRING ppropertyget.NAME)]) (porigin_site) ppropertyget.LINE),(PROPERTY_GET_RESULT ppropertyget)]],ppropertyget)',
    '~$property_get_capture(S_pending,ppropertyget[.NAME = $ptascii("different")])',
    '~$property_get_string_source(S,ppropertyget[.DECL = (porigin_get)])',
    '~$property_get_string_source(S,ppropertyget[.SITE = porigin_get])',
    '~$property_get_string_source(S,ppropertyget[.CLASS = porigin_site])',
    '~$property_get_history(S[.SOURCES = eps],ppropertyget) /\\ ~$property_get_history(S[.CODE = eps],ppropertyget)',
    '~$property_get_valid(S,ppropertyget[.OBJECT = (|S.OBJECTS|)],true)',
    '~$property_get_valid(S[.ALLOCATIONS = eps],ppropertyget,true)',
    '~$property_get_valid(S,ppropertyget[.METHOD = porigin_site],true)',
    'pmethoddesc_owner = pmethoddesc_get[.OWNER = porigin_site]',
    'S_owner = S[.CLASSES = [pclassdesc[.METHODS = [pmethoddesc_owner]]]]',
    '~$property_get_string_source(S_owner,ppropertyget)',
    'pmethoddesc_int = pmethoddesc_get[.FUNCTION = pfunction[.SIGNATURE = pfunction.SIGNATURE[.PARAMETERS = [psparam[.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]]]]]]',
    'S_int = S[.CLASSES = [pclassdesc[.METHODS = [pmethoddesc_int]]]]',
    '~$property_get_history(S_int,ppropertyget)',
    'pmethoddesc_ref = pmethoddesc_get[.FUNCTION = pfunction[.SIGNATURE = pfunction.SIGNATURE[.BYREF = true]]]',
    'S_ref = S[.CLASSES = [pclassdesc[.METHODS = [pmethoddesc_ref]]]]',
    '~$property_get_history(S_ref,ppropertyget)',
    '$ppmethod_get_signature(pfunction.SIGNATURE[.PARAMETERS = [psparam[.TYPE = eps]]])',
    '~$property_get_string_method(S,pmethoddesc_get[.FUNCTION = pfunction[.SIGNATURE = pfunction.SIGNATURE[.PARAMETERS = [psparam[.TYPE = eps]]]]])',
    'pmethoddesc_env = pmethoddesc_get[.FUNCTION = pfunction[.ENV = pfunction.ENV[.NAMESPACE = $ptascii("Forged")]]]',
    'S_env = S[.CLASSES = [pclassdesc[.METHODS = [pmethoddesc_env]]]]',
    '~$class_state_valid(S_env)',
    'pmethoddesc_return = pmethoddesc_get[.FUNCTION = pfunction[.SIGNATURE = pfunction.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "int"]))]]]]',
    'S_return = S[.CLASSES = [pclassdesc[.METHODS = [pmethoddesc_return]]]]',
    '~$property_get_history(S_return,ppropertyget)',
    '~$property_get_context(S,pcallcontext[.TARGET = PROPERTY_GET_TARGET n_receiver porigin_site])',
    '~$named_receives_ready(S,pfunction[.ORIGIN = porigin_site])',
    '$property_get_name_result_supported(S,ppropertyget,KNOWN (PINT 17))',
    '~$property_get_name_result_supported(S,ppropertyget,KNOWN PNULL)',
    '~$property_get_name_result_supported(S,ppropertyget,KNOWN (PBOOL false))',
    '~$property_get_name_result_supported(S,ppropertyget,KNOWN (PSTRING ($ptascii("17"))))',
    '~$property_get_name_result_supported(S,ppropertyget,KNOWN (POBJECT n_receiver))',
    '~$property_get_name_result_supported(S,ppropertyget,REFERENCE n_formal)',
]


RESUME = [
    'S_zero = $drive_steps(S,0)',
    'S_zero.COMPLETION = BUDGET /\\ S_zero[.COMPLETION = NORMAL] = S',
    'S_one = $drive_steps(S,1)',
    'S_one.COMPLETION = BUDGET',
    'S_done = $drive_steps(S,4096)',
    '$drive_steps(S_one[.COMPLETION = NORMAL],4095) = S_done',
    '$drive_steps(S_zero[.COMPLETION = NORMAL],4096) = S_done',
    'S_done.COMPLETION = NORMAL',
    'S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.HELD = eps',
    'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("17"),OUTPUT $ptascii(";DONE;")]',
    '$call_descriptors_valid(S_done) /\\ $property_state_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
]


CASES = {
    ROW['id']: {
        'source': ROW['source'],
        'stage': ('S.CURRENT = (pcallcontext) '
                  '-- if pcallcontext.TARGET = PROPERTY_GET_TARGET n_receiver porigin_get '
                  '-- if S.TODO = (RETURN_VALUE z_return) :: ptask_return* '
                  '-- if S.RESULT = KNOWN (PINT 17)'),
        'checks': REACHED + CONTROLS + RESUME,
    },
}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    protocol.run({name: case for name, case in CASES.items()
                  if not args.case or name in args.case}, (Path(__file__), CATALOGUE),
                 runner_flags=('--sl',))
