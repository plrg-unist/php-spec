#!/usr/bin/env python3
"""Check scalar Get declaration contexts, value return coercion and receiver ownership."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
import closure_call_protocol as protocol

CATALOGUE = ROOT / 'tests/semantics/magic_property_scalar_return_get_cases.json'
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']

checks = [
    'S.ORIGIN = (porigin_return)',
    'S.FRAMES = pframe :: eps',
    'pframe.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_caller*',
    'pcallcontext.FUNCTION = porigin_method /\\ ppropertyget.METHOD = porigin_method',
    'ppropertyget.OBJECT = n_receiver /\\ ppropertyget.NAME = $ptascii("integer") /\\ ppropertyget.DECL = eps',
    '$property_get_method(S,n_receiver) = (pmethoddesc)',
    'pfunction = pmethoddesc.FUNCTION',
    'pfunction.ORIGIN = porigin_method /\\ ~pfunction.CODE.STRICT',
    'S.EVENTS = [OUTPUT $ptascii("integer"),OUTPUT $ptascii(":" )]',
    '$property_get_context(S,pcallcontext) /\\ $property_get_frame(S,pcallcontext,pframe)',
    '$property_get_string_source(S,ppropertyget) /\\ $property_get_history(S,ppropertyget)',
    '$typed_return_task_valid(S,z_return) /\\ $call_task_valid(S,RETURN_VALUE z_return)',
    '~$typed_return_task_valid(S,$(z_return + 1))',
    '~$typed_return_task_valid(S[.ORIGIN = (ppropertyget.SITE)],z_return)',
    '$call_receiver_roots(pcallcontext) = eps',
    '$task_nodes(PROPERTY_GET_RESULT ppropertyget) = [HOBJECT n_receiver]',
    '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 2',
    '$call_descriptors_valid(S) /\\ $class_state_valid(S) /\\ $property_state_valid(S) /\\ $heap_valid($heap_graph(S))',
    'porigin_method = PORIGIN n_unit pcpath_method',
]
for index, name, kind in [
    (0, 'ReturnIntGet', 'int'), (1, 'ReturnFloatGet', 'float'),
    (2, 'ReturnBoolGet', 'bool'), (3, 'ReturnStringGet', 'string'),
    (4, 'ReturnMixedGet', 'mixed'),
]:
    v = lambda stem: stem + '_' + kind
    desc, method, function, parameter, raw, context = map(
        v, ('pclassdesc', 'pmethoddesc', 'pfunction', 'psparam', 'phpType18', 'ptcontext'))
    checks += [
        '$class_at(S.CLASSES,PORIGIN n_unit ([PCINDEX ' + str(index) + '])) = (' + desc + ')',
        desc + '.NAME = $ptascii("' + name + '") /\\ ' + desc + '.PARENT = eps',
        '$method_origin(' + desc + '.METHODS,PORIGIN n_unit ([PCINDEX ' + str(index) + ',PCFIELD 5,PCINDEX 0])) = (' + method + ')',
        function + ' = ' + method + '.FUNCTION',
        function + '.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "' + kind + '"]))]',
        function + '.SIGNATURE.PARAMETERS = [' + parameter + '] /\\ ' + parameter + '.TYPE =/= eps',
        '$origin_node(S.SOURCES,PORIGIN n_unit ([PCINDEX ' + str(index) + ',PCFIELD 5,PCINDEX 0,PCFIELD 5])) = (' + raw + ')',
        raw + ' = NIdentifier (BYTES ' + v('text_return') + ') ' + v('metadata_return'),
        context + ' = {NAMESPACE ' + function + '.ENV.NAMESPACE, IMPORTS ' + function + '.ENV.CLASSES, SCOPE PTKNOWN ' + desc + '.NAME eps, POSITION PTRETURN, OWNER ' + desc + '.NAME, MEMBER ' + method + '.NAME, FILE $call_sourcefile(S.FILES,' + function + '.ORIGIN), LINE ' + function + '.LINE}',
        '$ptype_normalize(' + raw + ',' + context + ') = PTOK ' + function + '.SIGNATURE.RETURNS eps',
        '$property_get_return_type_source(' + raw + ',' + function + '.SIGNATURE.RETURNS,' + context + ',true)',
        '~$property_get_return_type_source(' + raw + ',' + function + '.SIGNATURE.RETURNS,' + context + ',false)',
        '$ppmethod_get_declaration_signature(' + function + '.SIGNATURE) /\\ ~$ppmethod_get_signature(' + function + '.SIGNATURE)',
        '$property_get_method_source(S,' + method + ',true) /\\ ~$property_empty_get_source(S,' + method + ')',
        '$property_get_string_method(S,' + method + ')',
        '$typed_fallthrough(' + function + ') = TYPE_FALLTHROUGH ' + function + '.ORIGIN',
    ]
checks += [
    '~$property_get_return_type_source(NUnionType (SEQUENCE ([phpType18_int])) metadata_return_int,pfunction_int.SIGNATURE.RETURNS,ptcontext_int,true)',
    '~$property_get_return_type_source(NNullableType phpType18_int metadata_return_int,pfunction_int.SIGNATURE.RETURNS,ptcontext_int,true)',
    '~$property_get_return_type_source(NIdentifier (BYTES "dm9pZA==") metadata_return_int,pfunction_int.SIGNATURE.RETURNS,ptcontext_int,true)',
    '~$property_get_return_type_source(ABSENT,pfunction_int.SIGNATURE.RETURNS,ptcontext_int,true)',
    '~$property_get_return_type_source(phpType18_int,pfunction_bool.SIGNATURE.RETURNS,ptcontext_int,true)',
    '~$ppmethod_get_declaration_signature(pfunction.SIGNATURE[.BYREF = true])',
    'pfunction.SIGNATURE.PARAMETERS = [psparam]',
    '~$ppmethod_get_declaration_signature(pfunction.SIGNATURE[.PARAMETERS = [psparam[.TYPE = eps]]])',
    '~$ppmethod_get_scalar_return([(PTBRANCH ([PTBUILTIN "void"]))])',
    '~$ppmethod_get_scalar_return([(PTBRANCH ([PTBUILTIN "never"]))])',
    '~$ppmethod_get_scalar_return([(PTBRANCH ([PTBUILTIN "int"])),(PTBRANCH ([PTBUILTIN "null"]))])',
    '~$property_get_method_source(S[.SOURCES = eps],pmethoddesc,true)',
    '~$property_get_string_source(S,ppropertyget[.DECL = (porigin_method)])',
    '~$property_get_this_source(S,ppropertyget) /\\ ~$property_get_indirect_source(S,ppropertyget) /\\ $property_get_factory(S,ppropertyget) = eps',
    '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PBOOL true,false,false) = TYPEINTEGER (PBOOL true)',
    '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PBOOL true,true,false) = TYPEREJECT',
    'S_verified = $typed_return_checked(S,z_return,false)',
    'S_verified.COMPLETION = NORMAL /\\ S_verified.RESULT = KNOWN (PINT 1)',
    'S_verified.STORE = S.STORE /\\ S_verified.EVENTS = S.EVENTS',
    'PhpStep: S ~> S_unwind',
    'S_unwind.TODO = (RETURN_UNWIND (KNOWN (PINT 1)) (porigin_return)) :: ptask_tail*',
    'S_unwind.RESULT = KNOWN PNULL /\\ S_unwind.BASE = BASE_VALUE (KNOWN PNULL)',
    'S_unwind.STORE = S.STORE /\\ S_unwind.EVENTS = S.EVENTS',
    '$call_descriptors_valid(S_unwind) /\\ $property_state_valid(S_unwind) /\\ $heap_valid($heap_graph(S_unwind))',
]

CASES = {'scalar-return-get-headers-and-int-conversion': {
    'source': ROW['source'],
    'stage': ('S.CURRENT = (pcallcontext) '
              '-- if pcallcontext.TARGET = PROPERTY_GET_TARGET n_receiver porigin_method '
              '-- if S.TODO = (RETURN_VALUE z_return) :: ptask_tail* '
              '-- if S.RESULT = KNOWN (PBOOL true)'),
    'checks': checks,
}, 'scalar-return-get-int-result-copy': {
    'source': ROW['source'],
    'stage': ('S.CURRENT = eps /\\ S.FRAMES = eps '
              '-- if S.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail* '
              '-- if ppropertyget.NAME = $ptascii("integer") '
              '-- if S.RESULT = KNOWN (PINT 1)'),
    'checks': [
        'n_receiver = ppropertyget.OBJECT',
        '$property_get_method(S,n_receiver) = (pmethoddesc)',
        'pmethoddesc.FUNCTION.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "int"]))]',
        '$property_get_method_source(S,pmethoddesc,true) /\\ ~$property_empty_get_source(S,pmethoddesc)',
        '$property_get_string_source(S,ppropertyget) /\\ $property_get_history(S,ppropertyget)',
        '$property_get_valid(S,ppropertyget,true) /\\ $property_get_tail_valid(S,ppropertyget)',
        '$call_task_valid(S,PROPERTY_GET_RESULT ppropertyget)',
        '$property_get_name_result_supported(S,ppropertyget,KNOWN (PINT 1))',
        '$property_get_verify_desc(S,ppropertyget) = eps',
        '$task_nodes(PROPERTY_GET_RESULT ppropertyget) = [HOBJECT n_receiver]',
        '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 2',
        '$call_descriptors_valid(S) /\\ $class_state_valid(S) /\\ $property_state_valid(S) /\\ $heap_valid($heap_graph(S))',
        'PhpStep: S ~> S_copy',
        'S_copy.TODO = (PROPERTY_GET_COPY ppropertyget (KNOWN (PINT 1))) :: ptask_tail*',
        'S_copy.RESULT = KNOWN PNULL /\\ S_copy.BASE = BASE_VALUE (KNOWN PNULL)',
        '$task_nodes(PROPERTY_GET_COPY ppropertyget (KNOWN (PINT 1))) = eps',
        '$heap_owners($heap_graph(S_copy),HOBJECT n_receiver) = 1',
        '$call_task_valid(S_copy,PROPERTY_GET_COPY ppropertyget (KNOWN (PINT 1)))',
        '$call_descriptors_valid(S_copy) /\\ $property_state_valid(S_copy) /\\ $heap_valid($heap_graph(S_copy))',
        'S_zero = $drive_steps(S,0)',
        'S_zero = S[.COMPLETION = BUDGET]',
        'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
        'S_one.COMPLETION = BUDGET /\\ S_one.TODO = S_copy.TODO',
        'S_one.RESULT = S_copy.RESULT /\\ S_one.BASE = S_copy.BASE',
        '$heap_owners($heap_graph(S_one),HOBJECT n_receiver) = 1',
        '$call_descriptors_valid(S_one) /\\ $property_state_valid(S_one) /\\ $heap_valid($heap_graph(S_one))',
        'S_done = $drive_steps(S_one[.COMPLETION = NORMAL],4096)',
        'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.HELD = eps',
        'S_done.EVENTS = [OUTPUT $ptascii("integer"),OUTPUT $ptascii(":"),OUTPUT $ptascii("I;"),OUTPUT $ptascii("floating"),OUTPUT $ptascii(":"),OUTPUT $ptascii("2"),OUTPUT $ptascii(";"),OUTPUT $ptascii("boolean"),OUTPUT $ptascii(":"),OUTPUT $ptascii("B;"),OUTPUT $ptascii("string"),OUTPUT $ptascii(":"),OUTPUT $ptascii("ok"),OUTPUT $ptascii(";"),OUTPUT $ptascii("mixed"),OUTPUT $ptascii(":"),OUTPUT $ptascii("M;DONE;")]',
        '$call_descriptors_valid(S_done) /\\ $class_state_valid(S_done) /\\ $property_state_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
    ],
}}

if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__), CATALOGUE), runner_flags=('--sl',))
