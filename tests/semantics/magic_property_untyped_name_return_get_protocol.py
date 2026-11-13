#!/usr/bin/env python3
"""Check untyped-name Get return verification and preserve legacy routing."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol


CATALOGUE = Path(__file__).with_name('magic_property_untyped_name_return_get_cases.json')
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']
SOURCE = ROW['source'].split('$numeric = new UntypedNameNumericGet;', 1)[0] + '''class LegacyUntypedNameGet {
    public function __get($incoming) { return "legacy"; }
}
$numeric = new UntypedNameNumericGet;
$selector = "numeric";
echo $numeric->$selector === 3.5 ? "FLOAT;" : "BAD_FLOAT;";
echo $selector === "numeric" ? "KEEP;" : "BAD_SELECTOR;";
echo "DONE;";
'''

HELPERS = r'''
dec $scalar_union_get_result(pstate) : bool
def $scalar_union_get_result(S) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*
  -- if S.RESULT = KNOWN (PFLOAT 4615063718147915776)
def $scalar_union_get_result(S) = false -- otherwise
dec $scalar_union_get_seek(pstate,nat) : pstate
def $scalar_union_get_seek(S,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $scalar_union_get_seek(S,n) = S
  -- if $scalar_union_get_result(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $scalar_union_get_seek(S,0) = S
  -- if ~$scalar_union_get_result(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $scalar_union_get_seek(S,n) = $scalar_union_get_seek($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$scalar_union_get_result(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''

CHECKS = [
    'S.ORIGIN = (porigin_return)',
    'pvalue_string = PSTRING_CARRIER INTERNED_STRING ($ptascii("3.5"))',
    'S.RESULT = KNOWN pvalue_string /\\ z_return = 5',
    'S.FRAMES = [pframe]',
    'pframe.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_caller*',
    'ppropertyget.OBJECT = n_receiver /\\ ppropertyget.METHOD = porigin_method /\\ ppropertyget.DECL = eps',
    'ppropertyget.NAME = $ptascii("numeric") /\\ pframe.ORIGIN = (ppropertyget.SITE)',
    '$property_get_method(S,n_receiver) = (pmethoddesc)',
    'pfunction = pmethoddesc.FUNCTION',
    'pfunction.ORIGIN = porigin_method /\\ ~pfunction.CODE.STRICT /\\ ~pfunction.ENV.STRICT',
    '~pfunction.SIGNATURE.BYREF /\\ pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "float"])),(PTBRANCH ([PTBUILTIN "int"]))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam]',
    'psparam.TYPE = eps /\\ psparam.NAME = $ptascii("incoming")',
    '$class_at(S.CLASSES,pmethoddesc.OWNER) = (pclassdesc)',
    'pclassdesc.PARENT = eps /\\ pclassdesc.ORIGIN = ppropertyget.CLASS',
    'porigin_method = PORIGIN n_unit pcpath_method',
    '$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_method ++ [PCFIELD 5])) = (NUnionType (SEQUENCE ([NIdentifier (BYTES text_first) metadata_first,NIdentifier (BYTES text_second) metadata_second])) metadata_union)',
    'phpType18_return = NUnionType (SEQUENCE ([NIdentifier (BYTES text_first) metadata_first,NIdentifier (BYTES text_second) metadata_second])) metadata_union',
    '$ptlc($base64(text_first)) = $ptascii("float") /\\ $ptlc($base64(text_second)) = $ptascii("int")',
    'ptcontext = {NAMESPACE pfunction.ENV.NAMESPACE, IMPORTS pfunction.ENV.CLASSES, SCOPE PTKNOWN pclassdesc.NAME eps, POSITION PTRETURN, OWNER pclassdesc.NAME, MEMBER pmethoddesc.NAME, FILE $call_sourcefile(S.FILES,porigin_method), LINE pfunction.LINE}',
    '$ptype_normalize(phpType18_return,ptcontext) = PTOK pfunction.SIGNATURE.RETURNS eps',
    '$pttypename(pfunction.SIGNATURE.RETURNS) = $ptascii("int|float")',
    '$ppmethod_get_declaration_signature(pfunction.SIGNATURE) /\\ ~$ppmethod_get_signature(pfunction.SIGNATURE)',
    '$property_get_return_type_source(phpType18_return,pfunction.SIGNATURE.RETURNS,ptcontext,true)',
    '~$property_get_return_type_source(phpType18_return,pfunction.SIGNATURE.RETURNS,ptcontext,false)',
    '$property_get_method_source(S,pmethoddesc,true) /\\ ~$property_empty_get_source(S,pmethoddesc)',
    '~$property_get_method_source(S[.SOURCES = eps],pmethoddesc,true)',
    '$property_get_string_source(S,ppropertyget) /\\ $property_get_cv_name_source(S,ppropertyget)',
    '$property_get_context(S,pcallcontext) /\\ $property_get_frame(S,pcallcontext,pframe)',
    '$typed_return_task_valid(S,z_return) /\\ $call_task_valid(S,RETURN_VALUE z_return)',
    '~$typed_return_task_valid(S,$(z_return + 1))',
    '$lookup(S.ENV,$ptascii("incoming")) = (n_formal)',
    'S.STORE[n_formal] = DEFINED pvalue_name',
    '$string_bytes(pvalue_name) = ($ptascii("numeric"))',
    '$string_carrier_valid(S,pvalue_string)',
    'pvalue_float = PFLOAT 4615063718147915776',
    '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,pvalue_string,true,false) = TYPEREJECT',
    '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,pvalue_string,false,false) = TYPEVALUE pvalue_float',
    '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PSTRING_CARRIER INTERNED_STRING ($ptascii("12")),false,false) = TYPEVALUE (PINT 12)',
    '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PBOOL true,false,false) = TYPEINTEGER (PBOOL true)',
    '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PBOOL true,true,false) = TYPEREJECT',
    '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PNULL,false,false) = TYPEREJECT',
    'S_checked = $typed_return_checked(S,z_return,false)',
    'S_checked.COMPLETION = NORMAL /\\ S_checked.RESULT = KNOWN pvalue_float',
    'S_checked.STORE = S.STORE /\\ S_checked.EVENTS = S.EVENTS',
    '$value_nodes(pvalue_string) = eps /\\ $operand_nodes(S.RESULT) = eps',
    '$task_nodes(PROPERTY_GET_RESULT ppropertyget) = [HOBJECT n_receiver] /\\ $call_receiver_roots(pcallcontext) = eps',
    '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 2 /\\ S.EVENTS = [OUTPUT $ptascii("numeric"),OUTPUT $ptascii(":")]',
    '$call_descriptors_valid(S) /\\ $class_state_valid(S) /\\ $property_state_valid(S) /\\ $heap_valid($heap_graph(S))',
    'PhpStep: S ~> S_unwind',
    'S_unwind.TODO = (RETURN_UNWIND (KNOWN pvalue_float) (porigin_return)) :: ptask_return*',
    'S_unwind.RESULT = KNOWN PNULL /\\ S_unwind.BASE = BASE_VALUE (KNOWN PNULL)',
    'S_unwind.STORE = S.STORE /\\ S_unwind.EVENTS = S.EVENTS',
    'S_zero = $drive_steps(S,0)',
    'S_zero = S[.COMPLETION = BUDGET]',
    'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
    'S_one.COMPLETION = BUDGET /\\ S_one.TODO = S_unwind.TODO',
    'S_result_found = $scalar_union_get_seek(S_one[.COMPLETION = NORMAL],2000)',
    'S_result_found.COMPLETION = NORMAL \\/ S_result_found.COMPLETION = BUDGET',
    'S_result = S_result_found[.COMPLETION = NORMAL]',
    '$scalar_union_get_result(S_result)',
    'S_result.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_caller*',
    '$property_get_valid(S_result,ppropertyget,true) /\\ $property_get_tail_valid(S_result,ppropertyget)',
    '$property_get_name_result_supported(S_result,ppropertyget,KNOWN pvalue_float)',
    '$property_get_verify_desc(S_result,ppropertyget) = eps',
    '$heap_owners($heap_graph(S_result),HOBJECT n_receiver) = 2',
    'PhpStep: S_result ~> S_copy',
    'S_copy.TODO = (PROPERTY_GET_COPY ppropertyget (KNOWN pvalue_float)) :: ptask_caller*',
    'S_copy.RESULT = KNOWN PNULL /\\ S_copy.BASE = BASE_VALUE (KNOWN PNULL)',
    '$task_nodes(PROPERTY_GET_COPY ppropertyget (KNOWN pvalue_float)) = eps',
    '$heap_owners($heap_graph(S_copy),HOBJECT n_receiver) = 1',
    '~$property_get_guard_tasks(S_copy.TODO,n_receiver,ppropertyget.NAME)',
    'S_copy_one = $drive_steps(S_result,1)',
    'S_copy_one.COMPLETION = BUDGET /\\ S_copy_one.TODO = S_copy.TODO',
    '$heap_owners($heap_graph(S_copy_one),HOBJECT n_receiver) = 1',
    'S_done = $drive_steps(S_copy_one[.COMPLETION = NORMAL],4096)',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.HELD = eps',
    'S_done.EVENTS = [OUTPUT $ptascii("numeric"),OUTPUT $ptascii(":"),OUTPUT $ptascii("FLOAT;"),OUTPUT $ptascii("KEEP;"),OUTPUT $ptascii("DONE;")]',
    '$heap_owners($heap_graph(S_done),HOBJECT n_receiver) = 1',
    '$call_descriptors_valid(S_done) /\\ $class_state_valid(S_done) /\\ $property_state_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
    '$drive_steps(S,4096) = S_done',
]

# Canonical raw and normalized guards, including the exact changed historical inputs.
float_node = 'NIdentifier (BYTES text_first) metadata_first'
int_node = 'NIdentifier (BYTES text_second) metadata_second'
node = lambda encoded: 'NIdentifier (BYTES "' + encoded + '") metadata_first'
string_node, bool_node, null_node, true_node, false_node, unknown_node = map(
    node, ('c3RyaW5n', 'Ym9vbA==', 'bnVsbA==', 'dHJ1ZQ==', 'ZmFsc2U=', 'VW5rbm93bg=='))
raw = lambda nodes: '[' + ','.join(nodes) + ']'
CHECKS += [
    'S.HELD = eps /\\ pframe.CONTEXT = eps',
    '$ppmethod_get_scalar_union_prefix(' + raw([float_node,int_node]) + ') = pfunction.SIGNATURE.RETURNS',
    '$ppmethod_get_scalar_union_source(' + raw([float_node,int_node]) + ')',
    '~$ppmethod_get_scalar_union_source(eps)',
    '~$ppmethod_get_scalar_union_source(' + raw([float_node]) + ')',
    '$ppmethod_get_scalar_union_source(' + raw([float_node,int_node,string_node]) + ')',
    '$ppmethod_get_scalar_union_source(' + raw([null_node,string_node,int_node,float_node,bool_node]) + ')',
    '~$ppmethod_get_scalar_union_source(' + raw([float_node,int_node,float_node]) + ')',
    '~$ppmethod_get_scalar_union_source(' + raw([true_node,false_node]) + ')',
    '~$ppmethod_get_scalar_union_source(' + raw([bool_node,true_node]) + ')',
    '~$ppmethod_get_scalar_union_source(' + raw([bool_node,false_node]) + ')',
    '$ppmethod_get_scalar_union_prefix(' + raw([float_node,int_node,unknown_node]) + ') = pfunction.SIGNATURE.RETURNS',
    '~$ppmethod_get_scalar_union_source(' + raw([float_node,int_node,unknown_node]) + ')',
    '~$property_get_return_type_source(NUnionType (SEQUENCE (' + raw([float_node,int_node,string_node]) + ')) metadata_union,pfunction.SIGNATURE.RETURNS,ptcontext,true)',
    '~$property_get_return_type_source(NUnionType (SEQUENCE (' + raw([float_node,int_node,unknown_node]) + ')) metadata_union,pfunction.SIGNATURE.RETURNS,ptcontext,true)',
    '$ppmethod_get_scalar_return([(PTBRANCH ([PTBUILTIN "int"])),(PTBRANCH ([PTBUILTIN "float"]))])',
    '$ppmethod_get_scalar_return([(PTBRANCH ([PTBUILTIN "int"])),(PTBRANCH ([PTBUILTIN "false"]))])',
    '$ppmethod_get_scalar_return([(PTBRANCH ([PTBUILTIN "int"])),(PTBRANCH ([PTBUILTIN "string"])),(PTBRANCH ([PTBUILTIN "null"]))])',
    '$ppmethod_get_scalar_return([(PTBRANCH ([PTBUILTIN "bool"]))])',
    '$ppmethod_get_scalar_return([(PTBRANCH ([PTBUILTIN "mixed"]))])',
    '~$ppmethod_get_scalar_return([(PTBRANCH ([PTBUILTIN "mixed"])),(PTBRANCH ([PTBUILTIN "null"]))])',
    '~$ppmethod_get_scalar_return([(PTBRANCH ([PTBUILTIN "true"])),(PTBRANCH ([PTBUILTIN "false"]))])',
    '~$ppmethod_get_scalar_return([(PTBRANCH ([PTBUILTIN "bool"])),(PTBRANCH ([PTBUILTIN "true"]))])',
    '~$ppmethod_get_scalar_return([(PTBRANCH ([PTBUILTIN "bool"])),(PTBRANCH ([PTBUILTIN "false"]))])',
    '~$ppmethod_get_scalar_return([(PTBRANCH ([PTBUILTIN "int"])),(PTBRANCH ([PTBUILTIN "int"]))])',
    '~$ppmethod_get_scalar_return([(PTBRANCH ([PTBUILTIN "array"]))])',
    '~$ppmethod_get_scalar_return([(PTBRANCH ([PTBUILTIN "void"]))])',
    '~$ppmethod_get_scalar_return([(PTBRANCH ([PTBUILTIN "never"]))])',
    '~$ppmethod_get_scalar_return([(PTBRANCH ([PTCLASS ($ptascii("Unseen"))]))])',
    '~$ppmethod_get_scalar_return([(PTBRANCH ([PTBUILTIN "int",PTBUILTIN "string"]))])',
    '$typed_reference_conversion(S,[(PTBRANCH ([PTBUILTIN "int"])),(PTBRANCH ([PTBUILTIN "false"]))],PBOOL false,false,false) = TYPEVALUE (PBOOL false)',
    '$typed_reference_conversion(S,[(PTBRANCH ([PTBUILTIN "int"])),(PTBRANCH ([PTBUILTIN "false"]))],PBOOL true,false,false) = TYPEINTEGER (PBOOL true)',
]

# Fresh source-authenticated untyped formal and the unchanged legacy route.
CHECKS += [
    '$property_empty_get_name_type(ABSENT,eps)',
    '~$property_empty_get_name_type(ABSENT,[(PTBRANCH ([PTBUILTIN "string"]))])',
    '$property_get_string_method(S,pmethoddesc)',
    '~psparam.BYREF /\\ ~psparam.VARIADIC /\\ psparam.REQUIRED /\\ psparam.DEFAULT = PSNONE',
    '$ppmethod_get_declaration_signature(pfunction.SIGNATURE[.PARAMETERS = [psparam[.TYPE = eps]]])',
    '~$ppmethod_get_declaration_signature(pfunction.SIGNATURE[.PARAMETERS = [psparam[.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]]]])',
    '~$ppmethod_get_declaration_signature(pfunction.SIGNATURE[.BYREF = true])',
    '~$ppmethod_get_declaration_signature(pfunction.SIGNATURE[.PARAMETERS = eps])',
    '~$ppmethod_get_declaration_signature(pfunction.SIGNATURE[.PARAMETERS = [psparam,psparam]])',
    '~$ppmethod_get_declaration_signature(pfunction.SIGNATURE[.PARAMETERS = [psparam[.BYREF = true]]])',
    '~$ppmethod_get_declaration_signature(pfunction.SIGNATURE[.PARAMETERS = [psparam[.VARIADIC = true]]])',
    '~$ppmethod_get_declaration_signature(pfunction.SIGNATURE[.PARAMETERS = [psparam[.REQUIRED = false]]])',
    '~$ppmethod_get_declaration_signature(pfunction.SIGNATURE[.PARAMETERS = [psparam[.DEFAULT = PSDEFAULTUNSUPPORTED "control"]]])',
    '$class_at(S.CLASSES,PORIGIN n_unit ([PCINDEX 1])) = (pclassdesc_legacy)',
    '$method_origin(pclassdesc_legacy.METHODS,PORIGIN n_unit ([PCINDEX 1,PCFIELD 5,PCINDEX 0])) = (pmethoddesc_legacy)',
    'pmethoddesc_legacy.FUNCTION.SIGNATURE.PARAMETERS = [psparam_legacy]',
    'psparam_legacy.TYPE = eps /\\ pmethoddesc_legacy.FUNCTION.SIGNATURE.RETURNS = eps',
    '$ppmethod_get_declaration_signature(pmethoddesc_legacy.FUNCTION.SIGNATURE)',
    '$property_get_method_source(S,pmethoddesc_legacy,true) /\\ $property_empty_get_source(S,pmethoddesc_legacy)',
    '~$property_get_string_method(S,pmethoddesc_legacy)',
]

# The historical recipes' complete signature projection ignores parameter NAME.
for index, kinds in enumerate((('int',),('true',),('false',),('int','string'),
                               ('string','int'),('int','null'),('null','int'),('true','null'),
                               ('false','null'),('float','int','string'))):
    branches = '[' + ','.join('(PTBRANCH ([PTBUILTIN "' + kind + '"]))' for kind in kinds) + ']'
    signature = 'pssignature_projection_' + str(index)
    CHECKS += [
        signature + ' = pfunction.SIGNATURE[.RETURNS = ' + branches + ']',
        '$ppmethod_get_declaration_signature(' + signature + '[.PARAMETERS = [psparam[.TYPE = eps]]])',
    ]

CASES = {'named-untyped-name-get-weak-numeric-return-copy': {
    'source': SOURCE,
    'stage': ('S.CURRENT = (pcallcontext) '
              '-- if pcallcontext.TARGET = PROPERTY_GET_TARGET n_receiver porigin_method '
              '-- if S.TODO = (RETURN_VALUE z_return) :: ptask_tail* '
              '-- if S.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("3.5")))'),
    'checks': CHECKS,
}}


def render(case,fixture,filename):
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
    return text,len(case['checks']) + 6


if __name__ == '__main__':
    protocol.run(CASES,(Path(__file__),CATALOGUE),fixture_renderer=render,
                 runner_flags=('--sl',))
