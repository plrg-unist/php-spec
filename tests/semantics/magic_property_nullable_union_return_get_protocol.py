#!/usr/bin/env python3
"""Check raw nullable unions, weak return conversion and defining-context authority."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
import closure_call_protocol as protocol

CATALOGUE = ROOT / 'tests/semantics/magic_property_nullable_union_return_get_cases.json'
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']

checks = [
    'S.ORIGIN = (porigin_return)',
    'S.FRAMES = [pframe]',
    'pframe.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_caller*',
    'ppropertyget.OBJECT = n_receiver /\\ ppropertyget.METHOD = porigin_method /\\ ppropertyget.DECL = eps',
    'ppropertyget.NAME = $ptascii("value")',
    '$property_get_method(S,n_receiver) = (pmethoddesc)',
    'pfunction = pmethoddesc.FUNCTION',
    'pfunction.ORIGIN = porigin_method /\\ ~pfunction.CODE.STRICT',
    'S.EVENTS = [OUTPUT $ptascii("nil"),OUTPUT $ptascii(":"),OUTPUT $ptascii("IN;"),OUTPUT $ptascii("value"),OUTPUT $ptascii(":" )]',
    '$property_get_context(S,pcallcontext) /\\ $property_get_frame(S,pcallcontext,pframe)',
    'S_get = S[.ORIGIN = pframe.ORIGIN][.TODO = pframe.TODO]',
    '$property_get_string_source(S_get,ppropertyget) /\\ $property_get_history(S_get,ppropertyget) /\\ $property_get_tail_valid(S_get,ppropertyget)',
    '$typed_return_task_valid(S,z_return) /\\ $call_task_valid(S,RETURN_VALUE z_return)',
    '~$typed_return_task_valid(S,$(z_return + 1))',
    '~$typed_return_task_valid(S[.ORIGIN = (ppropertyget.SITE)],z_return)',
    '$call_receiver_roots(pcallcontext) = eps',
    '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 2',
    '$call_descriptors_valid(S) /\\ $class_state_valid(S) /\\ $property_state_valid(S) /\\ $heap_valid($heap_graph(S))',
    'porigin_method = PORIGIN n_unit pcpath_method',
]
for index, kind in enumerate(('int', 'float', 'bool', 'string')):
    v = lambda stem: stem + '_' + kind
    desc, method, function, parameter, raw, context = map(
        v, ('pclassdesc', 'pmethoddesc', 'pfunction', 'psparam', 'phpType18', 'ptcontext'))
    order = ('null', kind) if index % 2 else (kind, 'null')
    identifiers = ['NIdentifier (BYTES text_return_' + str(i) + '_' + kind
                   + ') metadata_return_' + str(i) + '_' + kind for i in range(2)]
    constructor = 'NUnionType (SEQUENCE ([' + ','.join(identifiers) + '])) ' + v('metadata_union')
    branches = '[' + ','.join('(PTBRANCH ([PTBUILTIN "' + part + '"]))' for part in order) + ']'
    checks += [
        '$class_at(S.CLASSES,PORIGIN n_unit ([PCINDEX ' + str(index) + '])) = (' + desc + ')',
        desc + '.PARENT = eps',
        '$method_origin(' + desc + '.METHODS,PORIGIN n_unit ([PCINDEX ' + str(index) + ',PCFIELD 5,PCINDEX 0])) = (' + method + ')',
        function + ' = ' + method + '.FUNCTION',
        function + '.SIGNATURE.RETURNS = ' + branches,
        function + '.SIGNATURE.PARAMETERS = [' + parameter + ']',
        parameter + '.TYPE =/= eps',
        '$origin_node(S.SOURCES,PORIGIN n_unit ([PCINDEX ' + str(index) + ',PCFIELD 5,PCINDEX 0,PCFIELD 5])) = (' + constructor + ')',
        raw + ' = ' + constructor,
        '$ptlc($base64(text_return_0_' + kind + ')) = $ptascii("' + order[0] + '")',
        '$ptlc($base64(text_return_1_' + kind + ')) = $ptascii("' + order[1] + '")',
        context + ' = {NAMESPACE ' + function + '.ENV.NAMESPACE, IMPORTS ' + function + '.ENV.CLASSES, SCOPE PTKNOWN ' + desc + '.NAME eps, POSITION PTRETURN, OWNER ' + desc + '.NAME, MEMBER ' + method + '.NAME, FILE $call_sourcefile(S.FILES,' + function + '.ORIGIN), LINE ' + function + '.LINE}',
        '$ptype_normalize(' + raw + ',' + context + ') = PTOK ' + function + '.SIGNATURE.RETURNS eps',
        '$property_get_return_type_source(' + raw + ',' + function + '.SIGNATURE.RETURNS,' + context + ',true)',
        '~$property_get_return_type_source(' + raw + ',' + function + '.SIGNATURE.RETURNS,' + context + ',false)',
        '$ppmethod_get_declaration_signature(' + function + '.SIGNATURE) /\\ ~$ppmethod_get_signature(' + function + '.SIGNATURE)',
        '$property_get_method_source(S,' + method + ',true) /\\ ~$property_empty_get_source(S,' + method + ')',
        '$property_get_string_method(S,' + method + ')',
        '$typed_exact(' + function + '.SIGNATURE.RETURNS,PNULL)',
    ]
int_node = 'NIdentifier (BYTES text_return_0_int) metadata_return_0_int'
null_node = 'NIdentifier (BYTES text_return_1_int) metadata_return_1_int'
checks += [
    '~$property_get_return_type_source(NUnionType (SEQUENCE ([' + null_node + ',' + int_node + '])) metadata_union_int,pfunction_int.SIGNATURE.RETURNS,ptcontext_int,true)',
    '~$property_get_return_type_source(NUnionType (SEQUENCE ([' + int_node + ',' + int_node + '])) metadata_union_int,pfunction_int.SIGNATURE.RETURNS,ptcontext_int,true)',
    '~$property_get_return_type_source(NUnionType (SEQUENCE ([' + int_node + ',' + null_node + ',' + null_node + '])) metadata_union_int,pfunction_int.SIGNATURE.RETURNS,ptcontext_int,true)',
    '~$property_get_return_type_source(' + int_node + ',pfunction_int.SIGNATURE.RETURNS,ptcontext_int,true)',
    '~$ppmethod_get_scalar_return([(PTBRANCH ([PTBUILTIN "int"])),(PTBRANCH ([PTBUILTIN "float"]))])',
    '~$ppmethod_get_scalar_return([(PTBRANCH ([PTBUILTIN "mixed"])),(PTBRANCH ([PTBUILTIN "null"]))])',
    '~$ppmethod_get_scalar_return([(PTBRANCH ([PTBUILTIN "void"])),(PTBRANCH ([PTBUILTIN "null"]))])',
    '$ppmethod_get_scalar_return([(PTBRANCH ([PTBUILTIN "true"])),(PTBRANCH ([PTBUILTIN "null"]))])',
    '$ppmethod_get_scalar_return([(PTBRANCH ([PTBUILTIN "null"])),(PTBRANCH ([PTBUILTIN "false"]))])',
    '~$ppmethod_get_scalar_return([(PTBRANCH ([PTBUILTIN "int"])),(PTBRANCH ([PTBUILTIN "string"])),(PTBRANCH ([PTBUILTIN "null"]))])',
    '~$ppmethod_get_declaration_signature(pfunction.SIGNATURE[.BYREF = true])',
    'pfunction.SIGNATURE.PARAMETERS = [psparam]',
    '~$ppmethod_get_declaration_signature(pfunction.SIGNATURE[.PARAMETERS = [psparam[.TYPE = eps]]])',
    '~$property_get_method_source(S[.SOURCES = eps],pmethoddesc,true)',
    '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PBOOL true,false,false) = TYPEINTEGER (PBOOL true)',
    '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PBOOL true,true,false) = TYPEREJECT',
    '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PNULL,true,false) = TYPEVALUE PNULL',
    'S_checked = $typed_return_checked(S,z_return,false)',
    'S_checked.COMPLETION = NORMAL /\\ S_checked.RESULT = KNOWN (PINT 1)',
    'S_checked.STORE = S.STORE /\\ S_checked.EVENTS = S.EVENTS',
    'PhpStep: S ~> S_unwind',
    'S_unwind.TODO = (RETURN_UNWIND (KNOWN (PINT 1)) (porigin_return)) :: ptask_tail*',
    'S_unwind.RESULT = KNOWN PNULL /\\ S_unwind.BASE = BASE_VALUE (KNOWN PNULL)',
    '$heap_owners($heap_graph(S_unwind),HOBJECT n_receiver) = 2',
    'S_zero = $drive_steps(S,0)',
    'S_zero = S[.COMPLETION = BUDGET]',
    'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
    'S_one.COMPLETION = BUDGET /\\ S_one.TODO = S_unwind.TODO',
    'S_one.RESULT = S_unwind.RESULT /\\ S_one.BASE = S_unwind.BASE',
    'S_done = $drive_steps(S_one[.COMPLETION = NORMAL],4096)',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.HELD = eps',
    'S_done.EVENTS = [OUTPUT $ptascii("nil"),OUTPUT $ptascii(":"),OUTPUT $ptascii("IN;"),OUTPUT $ptascii("value"),OUTPUT $ptascii(":"),OUTPUT $ptascii("IV;"),OUTPUT $ptascii("nil"),OUTPUT $ptascii(":"),OUTPUT $ptascii("FN;"),OUTPUT $ptascii("value"),OUTPUT $ptascii(":"),OUTPUT $ptascii("2"),OUTPUT $ptascii(";"),OUTPUT $ptascii("nil"),OUTPUT $ptascii(":"),OUTPUT $ptascii("BN;"),OUTPUT $ptascii("value"),OUTPUT $ptascii(":"),OUTPUT $ptascii("BV;"),OUTPUT $ptascii("nil"),OUTPUT $ptascii(":"),OUTPUT $ptascii("SN;"),OUTPUT $ptascii("value"),OUTPUT $ptascii(":"),OUTPUT $ptascii("kept"),OUTPUT $ptascii(";"),OUTPUT $ptascii("nil"),OUTPUT $ptascii(":"),OUTPUT $ptascii("DROP;DONE;")]',
    '$call_descriptors_valid(S_done) /\\ $class_state_valid(S_done) /\\ $property_state_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
    '$drive_steps(S,4096) = S_done',
]

CASES = {'nullable-union-return-get-headers-and-weak-conversion': {
    'source': ROW['source'],
    'stage': ('S.CURRENT = (pcallcontext) '
              '-- if pcallcontext.TARGET = PROPERTY_GET_TARGET n_receiver porigin_method '
              '-- if S.TODO = (RETURN_VALUE z_return) :: ptask_tail* '
              '-- if S.RESULT = KNOWN (PBOOL true)'),
    'checks': checks,
}}

if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__), CATALOGUE), runner_flags=('--sl',))
