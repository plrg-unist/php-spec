#!/usr/bin/env python3
"""Independent canonical-string ordinary Get history and ownership in fixture SL_mode."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol


CATALOGUE = Path(__file__).with_name('magic_property_string_read_get_review_cases.json')
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
SOURCE = ROW['source']
assert hashlib.sha256(SOURCE.encode()).hexdigest() == (
    'd63913e690a5dcbed15741cdd53bf81df66888ba8c171542c81b5e3a6bd980f8')


REACHED = [
    'S.RESULT = KNOWN (PINT 13) /\\ S.HELD = eps',
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
    'psparam.TYPE = [(PTBRANCH ([PTBUILTIN "string"]))] /\\ psparam.NAME = $ptascii("selected")',
    '~pfunction.SIGNATURE.BYREF /\\ pfunction.SIGNATURE.RETURNS = eps',
    'pfunction.ENV.NAMESPACE = eps /\\ pfunction.ENV.CLASSES = eps /\\ ~pfunction.ENV.STRICT',
    '$ppmethod_get_declaration_signature(pfunction.SIGNATURE) /\\ ~$ppmethod_get_signature(pfunction.SIGNATURE)',
    '$property_empty_get_source(S,pmethoddesc_get)',
    '$property_get_string_method(S,pmethoddesc_get)',
    '$property_get_string_source(S,ppropertyget)',
    '$property_get_cv_name_source(S,ppropertyget) /\\ $property_get_history(S,ppropertyget)',
    '$property_get_valid(S,ppropertyget,true)',
    '$property_get_frame(S,pcallcontext,pframe)',
    '$property_get_entered(S,S.CURRENT,S.FRAMES,pcallcontext.TARGET,ppropertyget.SITE)',
    '$property_get_context(S,pcallcontext)',
    '$named_receives_ready(S,pfunction)',
    '$target_function(S,pcallcontext.TARGET) = (pfunction)',
    '$target_nodes(pcallcontext.TARGET) = eps /\\ $target_instance(pcallcontext.TARGET) = eps /\\ $call_receiver_roots(pcallcontext) = eps',
    '$task_nodes(PROPERTY_GET_RESULT ppropertyget) = [HOBJECT n_receiver]',
    '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 2',
    '$lookup(S.ENV,$ptascii("selected")) = (n_formal)',
    'S.STORE[n_formal] = DEFINED (PINT 9)',
    'S_caller = $constant_frame_scope(S,pframe,eps)',
    '$lookup(S_caller.ENV,$ptascii("reader")) = (n_reader_cell)',
    'S.STORE[n_reader_cell] = DEFINED (POBJECT n_receiver)',
    '$lookup(S_caller.ENV,$ptascii("name")) = (n_name_cell)',
    'S.STORE[n_name_cell] = DEFINED pvalue_name',
    '$string_bytes(pvalue_name) = ($ptascii("12"))',
    'S_pending = S_caller[.TODO = (CALL_ARGS (PROPERTY_GET_TARGET n_receiver porigin_get) eps 1 ([KNOWN (PSTRING ppropertyget.NAME)]) (ppropertyget.SITE) ppropertyget.LINE) :: pframe.TODO][.ORIGIN = (ppropertyget.SITE)][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
    '$property_get_capture_tail(S_pending,ppropertyget) = ptask_tail*',
    '$property_get_capture(S_pending,ppropertyget)',
    '$property_get_pending_call(S_pending,pcallcontext.TARGET,ppropertyget.SITE)',
    '$property_get_string_tail(S,ppropertyget,ptask_tail*)',
    '$property_get_string_tasks(S,ppropertyget,pframe.TODO)',
    '$property_get_factory(S,ppropertyget) = eps /\\ ~$property_get_this_source(S,ppropertyget) /\\ ~$property_get_indirect_source(S,ppropertyget)',
    'S.EVENTS = [OUTPUT $ptascii("NUM;")]',
    '$call_descriptors_valid(S) /\\ $property_state_valid(S) /\\ $heap_valid($heap_graph(S))',
]


CONTROLS = [
    'ptask_tail* = (ORIGIN_RETURN (porigin_parent)) :: (BINARY_LEFT IDENTICAL expression_rhs z_rhs) :: ptask_after*',
    '$origin_node(S.SOURCES,ppropertyget.SITE) = (expression_property)',
    '$origin_node(S.SOURCES,porigin_parent) = (pcnode_parent)',
    '$property_get_string_consumer(pcnode_parent,expression_property)',
    '~$property_get_string_consumer(NExprAssign expression_property expression_rhs eps,expression_property)',
    '~$property_get_string_consumer(NExprAssignRef expression_property expression_rhs eps,expression_property)',
    '~$property_get_string_consumer(NExprBinaryOpPlus expression_property expression_rhs eps,expression_property)',
    '~$property_get_string_tail(S,ppropertyget,eps)',
    '~$property_get_string_tail(S,ppropertyget,(ORIGIN_RETURN (porigin_parent)) :: (BINARY_LEFT ADD expression_rhs z_rhs) :: ptask_after*)',
    '~$property_get_string_tail(S,ppropertyget,(ORIGIN_RETURN (porigin_parent)) :: (BINARY_LEFT IDENTICAL expression_rhs $(z_rhs + 1)) :: ptask_after*)',
    '~$property_get_string_tail(S,ppropertyget,(ORIGIN_RETURN (porigin_parent)) :: DISCARD :: ptask_after*)',
    '~$property_get_string_tasks(S,ppropertyget,[(PROPERTY_GET_RESULT ppropertyget)])',
    '~$property_get_tail_valid(S_pending[.TODO = [(PROPERTY_GET_RESULT ppropertyget)]],ppropertyget)',
    '~$property_get_string_tasks(S,ppropertyget,(PROPERTY_GET_RESULT ppropertyget) :: (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*)',
    '$property_get_string_tasks(S,ppropertyget,(PROPERTY_GET_COPY ppropertyget (KNOWN (PINT 13))) :: ptask_tail*)',
    '~$property_get_capture(S_pending[.TODO = [(CALL_ARGS (PROPERTY_GET_TARGET n_receiver porigin_get) eps 1 ([KNOWN (PSTRING ppropertyget.NAME)]) (ppropertyget.SITE) ppropertyget.LINE),(PROPERTY_GET_RESULT ppropertyget)]],ppropertyget)',
    '~$property_get_string_source(S,ppropertyget[.DECL = (porigin_get)])',
    '~$property_get_string_source(S,ppropertyget[.SITE = porigin_get])',
    '~$property_get_string_source(S,ppropertyget[.CLASS = ppropertyget.SITE])',
    'pclassdesc.ORIGIN = PORIGIN n_unit pcpath_owner',
    'n_owner = $nabs($(|pcpath_owner| - 1))',
    'pcpath_new = pcpath_owner[0:n_owner]',
    'pcpath_owner = pcpath_new ++ [PCFIELD 0]',
    'porigin_new = PORIGIN n_unit pcpath_new',
    '$anonymous_new_descriptor(S,porigin_new) = (pclassdesc)',
    'pmethoddesc_env = pmethoddesc_get[.FUNCTION = pfunction[.ENV = pfunction.ENV[.NAMESPACE = $ptascii("Forged")]]]',
    'S_env = S[.CLASSES = [pclassdesc[.METHODS = [pmethoddesc_env]]]]',
    '$anonymous_new_descriptor(S_env,porigin_new) = eps /\\ ~$class_state_valid(S_env)',
    'pmethoddesc_int = pmethoddesc_get[.FUNCTION = pfunction[.SIGNATURE = pfunction.SIGNATURE[.PARAMETERS = [psparam[.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]]]]]]',
    'S_int = S[.CLASSES = [pclassdesc[.METHODS = [pmethoddesc_int]]]]',
    '~$property_get_history(S_int,ppropertyget)',
    'pmethoddesc_ref = pmethoddesc_get[.FUNCTION = pfunction[.SIGNATURE = pfunction.SIGNATURE[.BYREF = true]]]',
    'S_ref = S[.CLASSES = [pclassdesc[.METHODS = [pmethoddesc_ref]]]]',
    '~$property_get_history(S_ref,ppropertyget)',
    '~$property_get_history(S[.SOURCES = eps],ppropertyget)',
    '~$property_get_history(S[.CODE = eps],ppropertyget)',
    '~$property_get_valid(S,ppropertyget[.OBJECT = (|S.OBJECTS|)],true)',
    '~$property_get_valid(S,ppropertyget[.METHOD = ppropertyget.SITE],true)',
    '~$property_get_capture(S_pending,ppropertyget[.NAME = $ptascii("again")])',
    '~$property_get_context(S,pcallcontext[.TARGET = PROPERTY_GET_TARGET n_receiver ppropertyget.SITE])',
    '~$named_receives_ready(S,pfunction[.ORIGIN = ppropertyget.SITE])',
    '~$named_receives_ready(S[.CURRENT = (pcallcontext[.TARGET = PROPERTY_GET_TARGET n_receiver ppropertyget.SITE])],pfunction)',
    '$property_get_name_result_supported(S,ppropertyget,KNOWN (PINT 13))',
    '$property_get_name_result_supported(S,ppropertyget,KNOWN PNULL)',
    '$typed_exact(psparam.TYPE,PSTRING ($ptascii("12")))',
    '$typed_conversion(psparam.TYPE,PSTRING ($ptascii("12")),true) = TYPEVALUE (PSTRING ($ptascii("12")))',
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
    'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("VALUE;"),OUTPUT $ptascii("OTHER;"),OUTPUT $ptascii("DONE;")]',
    '$call_descriptors_valid(S_done) /\\ $property_state_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
]


CASES = {
    ROW['id']: {
        'source': SOURCE,
        'stage': ('S.CURRENT = (pcallcontext) '
                  '-- if pcallcontext.TARGET = PROPERTY_GET_TARGET n_receiver porigin_get '
                  '-- if S.TODO = (RETURN_VALUE z_return) :: ptask_return* '
                  '-- if S.RESULT = KNOWN (PINT 13)'),
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
