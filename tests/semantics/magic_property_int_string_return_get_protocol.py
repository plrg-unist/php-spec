#!/usr/bin/env python3
"""Check both int|string Get headers and weak Boolean return conversion."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
import closure_call_protocol as protocol

CATALOGUE = ROOT / 'tests/semantics/magic_property_int_string_return_get_cases.json'
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']


def outputs(parts):
    return '[' + ','.join('OUTPUT $ptascii(' + json.dumps(part) + ')' for part in parts) + ']'


prefix = ['text', ':', 'T;', 'boolean', ':']
final = prefix + ['W;', 'text', ':', '9', ';', 'boolean', ':', 'ZERO;',
                  'boolean', ':', 'D;', 'bad', ':',
                  'UnionIntStringGet::__get(): Return value must be of type string|int, null returned',
                  ';', 'KEEP;', 'DONE;']
checks = [
    'S.ORIGIN = (porigin_return)',
    'S.FRAMES = [pframe]',
    'pframe.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_caller*',
    'ppropertyget.OBJECT = n_receiver /\\ ppropertyget.METHOD = porigin_method /\\ ppropertyget.DECL = eps',
    'ppropertyget.NAME = $ptascii("boolean")',
    '$property_get_method(S,n_receiver) = (pmethoddesc)',
    'pfunction = pmethoddesc.FUNCTION',
    'pfunction.ORIGIN = porigin_method /\\ ~pfunction.CODE.STRICT',
    'S.EVENTS = ' + outputs(prefix),
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
for index, order in enumerate((('int', 'string'), ('string', 'int'))):
    suffix = '_' + str(index)
    desc, method, function, parameter, raw, context = (
        name + suffix for name in ('pclassdesc', 'pmethoddesc', 'pfunction',
                                  'psparam', 'phpType18', 'ptcontext'))
    identifiers = ['NIdentifier (BYTES text_return_' + str(i) + suffix + ') metadata_return_' + str(i) + suffix
                   for i in range(2)]
    constructor = 'NUnionType (SEQUENCE ([' + ','.join(identifiers) + '])) metadata_union' + suffix
    branches = '[' + ','.join('(PTBRANCH ([PTBUILTIN "' + kind + '"]))' for kind in order) + ']'
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
        context + ' = {NAMESPACE ' + function + '.ENV.NAMESPACE, IMPORTS ' + function + '.ENV.CLASSES, SCOPE PTKNOWN ' + desc + '.NAME eps, POSITION PTRETURN, OWNER ' + desc + '.NAME, MEMBER ' + method + '.NAME, FILE $call_sourcefile(S.FILES,' + function + '.ORIGIN), LINE ' + function + '.LINE}',
        '$ptype_normalize(' + raw + ',' + context + ') = PTOK ' + function + '.SIGNATURE.RETURNS eps',
        '$property_get_return_type_source(' + raw + ',' + function + '.SIGNATURE.RETURNS,' + context + ',true)',
        '~$property_get_return_type_source(' + raw + ',' + function + '.SIGNATURE.RETURNS,' + context + ',false)',
        '$ppmethod_get_declaration_signature(' + function + '.SIGNATURE) /\\ ~$ppmethod_get_signature(' + function + '.SIGNATURE)',
        '$property_get_method_source(S,' + method + ',true) /\\ ~$property_empty_get_source(S,' + method + ')',
        '$property_get_string_method(S,' + method + ')',
        '$pttypename(' + function + '.SIGNATURE.RETURNS) = $ptascii("string|int")',
        '~$typed_exact(' + function + '.SIGNATURE.RETURNS,PBOOL true) /\\ ~$typed_exact(' + function + '.SIGNATURE.RETURNS,PNULL)',
    ]
int_node = 'NIdentifier (BYTES text_return_0_0) metadata_return_0_0'
string_node = 'NIdentifier (BYTES text_return_1_0) metadata_return_1_0'
checks += [
    '~$property_get_return_type_source(phpType18_0,pfunction_1.SIGNATURE.RETURNS,ptcontext_0,true)',
    '~$property_get_return_type_source(NUnionType (SEQUENCE ([' + int_node + ',' + int_node + '])) metadata_union_0,pfunction.SIGNATURE.RETURNS,ptcontext_0,true)',
    '~$property_get_return_type_source(NUnionType (SEQUENCE ([' + int_node + ',' + string_node + ',' + int_node + '])) metadata_union_0,pfunction.SIGNATURE.RETURNS,ptcontext_0,true)',
    '~$property_get_return_type_source(NNullableType (' + int_node + ') metadata_union_0,pfunction.SIGNATURE.RETURNS,ptcontext_0,true)',
    '~$ppmethod_get_scalar_return([(PTBRANCH ([PTBUILTIN "int"])),(PTBRANCH ([PTBUILTIN "int"]))])',
    '~$ppmethod_get_scalar_return([(PTBRANCH ([PTBUILTIN "int"])),(PTBRANCH ([PTBUILTIN "float"]))])',
    '~$ppmethod_get_scalar_return([(PTBRANCH ([PTBUILTIN "int"])),(PTBRANCH ([PTBUILTIN "string"])),(PTBRANCH ([PTBUILTIN "null"]))])',
    '~$ppmethod_get_scalar_return([(PTBRANCH ([PTBUILTIN "int"])),(PTBRANCH ([PTBUILTIN "false"]))])',
    '~$ppmethod_get_declaration_signature(pfunction.SIGNATURE[.BYREF = true])',
    'pfunction.SIGNATURE.PARAMETERS = [psparam]',
    '~$ppmethod_get_declaration_signature(pfunction.SIGNATURE[.PARAMETERS = [psparam[.TYPE = eps]]])',
    '~$property_get_method_source(S[.SOURCES = eps],pmethoddesc,true)',
    '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PBOOL true,false,false) = TYPEINTEGER (PBOOL true)',
    '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PBOOL true,true,false) = TYPEREJECT',
    '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PNULL,false,false) = TYPEREJECT',
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
    'S_done.EVENTS = ' + outputs(final),
    '$call_descriptors_valid(S_done) /\\ $class_state_valid(S_done) /\\ $property_state_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
    '$drive_steps(S,4096) = S_done',
]
false_checks = [
    'S.ORIGIN = (porigin_return)',
    'S.FRAMES = [pframe]',
    'pframe.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_caller*',
    'S.EVENTS = ' + outputs(prefix + ['W;', 'text', ':', '9', ';', 'boolean', ':']),
    '$property_get_method(S,n_receiver) = (pmethoddesc)',
    'pfunction = pmethoddesc.FUNCTION',
    'pfunction.ORIGIN = porigin_method /\\ ~pfunction.CODE.STRICT',
    'pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "string"])),(PTBRANCH ([PTBUILTIN "int"]))]',
    '$property_get_context(S,pcallcontext) /\\ $property_get_frame(S,pcallcontext,pframe)',
    '$typed_return_task_valid(S,z_return)',
    '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PBOOL false,false,false) = TYPEINTEGER (PBOOL false)',
    '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PBOOL false,true,false) = TYPEREJECT',
    'S_checked = $typed_return_checked(S,z_return,false)',
    'S_checked.COMPLETION = NORMAL /\\ S_checked.RESULT = KNOWN (PINT 0)',
    'S_checked.STORE = S.STORE /\\ S_checked.EVENTS = S.EVENTS',
    'PhpStep: S ~> S_unwind',
    'S_unwind.TODO = (RETURN_UNWIND (KNOWN (PINT 0)) (porigin_return)) :: ptask_tail*',
    'S_zero = $drive_steps(S,0)',
    'S_zero = S[.COMPLETION = BUDGET]',
    'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
    'S_one.COMPLETION = BUDGET /\\ S_one.TODO = S_unwind.TODO',
    'S_done = $drive_steps(S_one[.COMPLETION = NORMAL],4096)',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.HELD = eps',
    'S_done.EVENTS = ' + outputs(final),
    '$call_descriptors_valid(S_done) /\\ $class_state_valid(S_done) /\\ $property_state_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
    '$drive_steps(S,4096) = S_done',
]
CASES = {}
for label, value, conditions in (('true', 'true', checks), ('false', 'false', false_checks)):
    CASES['int-string-return-get-weak-' + label] = {
        'source': ROW['source'],
        'stage': ('S.CURRENT = (pcallcontext) '
                  '-- if pcallcontext.TARGET = PROPERTY_GET_TARGET n_receiver porigin_method '
                  '-- if S.TODO = (RETURN_VALUE z_return) :: ptask_tail* '
                  '-- if S.RESULT = KNOWN (PBOOL ' + value + ')'),
        'checks': conditions,
    }

if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__), CATALOGUE), runner_flags=('--sl',))
