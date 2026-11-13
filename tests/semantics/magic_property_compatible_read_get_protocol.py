#!/usr/bin/env python3
"""Check compatible Get header sources, typed entry, receiver ownership and saved reads."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
import closure_call_protocol as protocol

CATALOGUE = ROOT / 'tests/semantics/magic_property_compatible_read_get_cases.json'
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']

checks = [
    'S.ORIGIN = (porigin_site)',
    'S.EVENTS = eps',
    'porigin_site = PORIGIN n_unit pcpath_site',
    '$property_get_method(S,n_receiver) = (pmethoddesc)',
    'pmethoddesc.OWNER = PORIGIN n_unit ([PCINDEX 0])',
    'ppropertyget = {SITE porigin_site, NAME $ptascii("12"), LINE z_property, OBJECT n_receiver, CLASS pmethoddesc.OWNER, METHOD pmethoddesc.FUNCTION.ORIGIN, DECL eps}',
    '$property_get_cv_name_source(S,ppropertyget)',
    '$origin_node(S.SOURCES,porigin_site) = (expression)',
    '$property_get_string_consumer_site(S,porigin_site,expression)',
    '$property_get_string_tail(S,ppropertyget,(ORIGIN_RETURN (porigin_parent)) :: (BINARY_LEFT IDENTICAL expression_rhs z_rhs) :: ptask_tail*)',
    '$property_get_string_source(S,ppropertyget)',
    '$property_get_pending(S) /\\ $property_get_plan(S) = (ppropertyget)',
    '$property_get_history(S,ppropertyget) /\\ $property_get_valid(S,ppropertyget,true)',
    '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 2',
    '$call_descriptors_valid(S) /\\ $class_state_valid(S) /\\ $property_state_valid(S) /\\ $heap_valid($heap_graph(S))',
]
for tag, index, expected in [
    ('nullable', 0, '[(PTBRANCH ([PTBUILTIN "string"])),(PTBRANCH ([PTBUILTIN "null"]))]'),
    ('union', 1, '[(PTBRANCH ([PTBUILTIN "int"])),(PTBRANCH ([PTBUILTIN "string"]))]'),
    ('mixed', 2, '[(PTBRANCH ([PTBUILTIN "mixed"]))]'),
]:
    v = lambda name: name + '_' + tag
    desc, method, function, parameter, raw, context = map(v, ('pclassdesc', 'pmethoddesc', 'pfunction', 'psparam', 'phpType18', 'ptcontext'))
    checks += [
        '$class_at(S.CLASSES,PORIGIN n_unit ([PCINDEX ' + str(index) + '])) = (' + desc + ')',
        '$method_origin(' + desc + '.METHODS,PORIGIN n_unit ([PCINDEX ' + str(index) + ',PCFIELD 5,PCINDEX 0])) = (' + method + ')',
        function + ' = ' + method + '.FUNCTION',
        function + '.SIGNATURE.PARAMETERS = [' + parameter + ']',
        parameter + '.TYPE = ' + expected,
        '~' + parameter + '.BYREF /\\ ~' + parameter + '.VARIADIC /\\ ' + parameter + '.REQUIRED /\\ ' + parameter + '.DEFAULT = PSNONE',
        '$origin_node(S.SOURCES,PORIGIN n_unit ([PCINDEX ' + str(index) + ',PCFIELD 5,PCINDEX 0,PCFIELD 4,PCINDEX 0])) = (NParam (SEQUENCE eps) (INTEGER 0) ' + raw + ' (BOOLEAN false) (BOOLEAN false) (NExprVariable (BYTES ' + v('text_parameter') + ') ' + v('metadata_name') + ') ABSENT (SEQUENCE eps) ' + v('metadata_param') + ')',
        context + ' = {NAMESPACE ' + function + '.ENV.NAMESPACE, IMPORTS ' + function + '.ENV.CLASSES, SCOPE PTKNOWN ' + desc + '.NAME eps, POSITION PTPARAMETER, OWNER ' + desc + '.NAME, MEMBER ' + method + '.NAME, FILE $call_sourcefile(S.FILES,' + function + '.ORIGIN), LINE $psline(' + v('metadata_param') + ')}',
        '$ptype_normalize(' + raw + ',' + context + ') = PTOK ' + parameter + '.TYPE eps',
        '$property_empty_get_source(S,' + method + ')',
        '$property_get_string_method(S,' + method + ')',
        '$ppmethod_get_declaration_signature(' + function + '.SIGNATURE) /\\ ~$ppmethod_get_signature(' + function + '.SIGNATURE)',
        '$typed_exact(' + parameter + '.TYPE,PSTRING ($ptascii("12")))',
        '$typed_conversion(' + parameter + '.TYPE,PSTRING ($ptascii("12")),false) = TYPEVALUE (PSTRING ($ptascii("12")))',
    ]

checks += [
    '~$property_get_string_method(S[.SOURCES = eps],pmethoddesc)',
    'pfunction = pmethoddesc.FUNCTION',
    'pfunction.SIGNATURE.PARAMETERS = [psparam]',
    '~$property_get_string_method(S,pmethoddesc[.FUNCTION = pfunction[.SIGNATURE = pfunction.SIGNATURE[.BYREF = true]]])',
    '~$property_get_string_method(S,pmethoddesc[.FUNCTION = pfunction[.SIGNATURE = pfunction.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "int"]))]]]])',
    '~$property_get_string_source(S,ppropertyget[.DECL = (pfunction.ORIGIN)])',
    '~$property_get_string_source(S,ppropertyget[.CLASS = pfunction.ORIGIN])',
    '~$property_get_string_source(S,ppropertyget[.SITE = pfunction.ORIGIN])',
    '~$property_ref_demand(S)',
    '$property_get_factory(S,ppropertyget) = eps /\\ ~$property_get_this_source(S,ppropertyget) /\\ ~$property_get_indirect_source(S,ppropertyget)',
    '$property_get_name_result_supported(S,ppropertyget,KNOWN (PINT 7))',
    '~$property_get_name_result_supported(S,ppropertyget,KNOWN PNULL)',
    '~$property_get_name_result_supported(S,ppropertyget,KNOWN (POBJECT n_receiver))',
    '~$property_get_string_tail(S,ppropertyget,eps)',
    '~$property_get_string_tail(S,ppropertyget,[ORIGIN_RETURN (porigin_parent),DISCARD])',
    '~$property_get_string_tail(S,ppropertyget,[ORIGIN_RETURN (porigin_parent),BINARY_LEFT IDENTICAL expression_rhs $(z_rhs + 1)])',
    'ptask_read* = (ORIGIN_RETURN (porigin_parent)) :: (BINARY_LEFT IDENTICAL expression_rhs z_rhs) :: ptask_tail*',
    'PhpStep: S ~> S_call',
    'S_call.TODO = (CALL_ARGS (PROPERTY_GET_TARGET n_receiver pfunction.ORIGIN) eps 1 ([KNOWN (PSTRING ($ptascii("12")))]) (porigin_site) z_property) :: (PROPERTY_GET_RESULT ppropertyget) :: ptask_read*',
    '$property_get_capture(S_call,ppropertyget) /\\ $property_get_tail_valid(S_call,ppropertyget)',
    '$property_get_capture_tail(S_call,ppropertyget) = ptask_read*',
    '$property_get_pending_call(S_call,PROPERTY_GET_TARGET n_receiver pfunction.ORIGIN,porigin_site)',
    '$target_nodes(PROPERTY_GET_TARGET n_receiver pfunction.ORIGIN) = eps',
    '$task_nodes(PROPERTY_GET_RESULT ppropertyget) = [HOBJECT n_receiver]',
    '$heap_owners($heap_graph(S_call),HOBJECT n_receiver) = 2',
    '$call_descriptors_valid(S_call) /\\ $property_state_valid(S_call) /\\ $heap_valid($heap_graph(S_call))',
    'S_zero = $drive_steps(S_call,0)',
    'S_zero = S_call[.COMPLETION = BUDGET]',
    'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
    'S_one.COMPLETION = BUDGET /\\ S_one.TODO = [TYPE_RECEIVE pfunction.ORIGIN 0]',
    'S_one.CURRENT = (pcallcontext)',
    '$property_get_context(S_one,pcallcontext) /\\ $named_receives_ready(S_one,pfunction)',
    '$typed_receive_valid(S_one,pfunction.ORIGIN,0)',
    '$call_descriptors_valid(S_one) /\\ $property_state_valid(S_one) /\\ $heap_valid($heap_graph(S_one))',
    'S_received = $drive_steps(S_one[.COMPLETION = NORMAL],1)',
    'S_received.COMPLETION = BUDGET',
    '$lookup(S_received.ENV,$ptascii("incoming")) = (n_formal)',
    'S_received.STORE[n_formal] = DEFINED pvalue_name',
    '$string_bytes(pvalue_name) = ($ptascii("12"))',
    '$call_descriptors_valid(S_received) /\\ $property_state_valid(S_received) /\\ $heap_valid($heap_graph(S_received))',
    'S_done = $drive_steps(S_received[.COMPLETION = NORMAL],2000)',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps',
    'S_done.EVENTS = [OUTPUT $ptascii("NSTR;"),OUTPUT $ptascii("NNULL;"),OUTPUT $ptascii("VALUE;"),OUTPUT $ptascii("USTR;"),OUTPUT $ptascii("UINT;"),OUTPUT $ptascii("11"),OUTPUT $ptascii(";"),OUTPUT $ptascii("MSTR;"),OUTPUT $ptascii("MBOOL;"),OUTPUT $ptascii("DONE;")]',
    '$call_descriptors_valid(S_done) /\\ $property_state_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
]

CASES = {'compatible-read-get-entry-and-headers': {
    'source': ROW['source'],
    'stage': ('S.CURRENT = eps /\\ S.FRAMES = eps '
              '-- if S.TODO = (PROPERTY_NAME (POBJECT n_receiver) z_property) :: '
              '(DIM_FETCH z_property) :: (ORIGIN_RETURN (porigin_parent)) :: '
              '(BINARY_LEFT IDENTICAL expression_rhs z_rhs) :: ptask_tail*'),
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__), CATALOGUE), runner_flags=('--sl',))
