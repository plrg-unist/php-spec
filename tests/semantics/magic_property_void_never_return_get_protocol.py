#!/usr/bin/env python3
"""Source-reached void Get fallthrough, NULL copy and receiver retirement."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('magic_property_void_never_return_get_cases.json')
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']
SOURCE = ROW['source'].split('$receiver = new VoidReturnGet;', 1)[0] + '''$receiver = new VoidReturnGet;
$selector = "fall";
echo $receiver->$selector === null ? "FALL;" : "BAD_FALL;";
echo $selector === "fall" ? "KEEP;" : "BAD_NAME;";
echo "DONE;";
'''
HELPERS = r'''
dec $scalar_union_get_result(pstate) : bool
def $scalar_union_get_result(S) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*
  -- if S.RESULT = KNOWN (PNULL)
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
    'S.FRAMES = [pframe]',
    'pframe.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_caller*',
    'ppropertyget.NAME = $ptascii("fall") /\\ ppropertyget.METHOD = porigin_method /\\ ppropertyget.DECL = eps',
    'pframe.ORIGIN = (ppropertyget.SITE)',
    '$property_get_method(S,ppropertyget.OBJECT) = (pmethoddesc)',
    'pfunction = pmethoddesc.FUNCTION',
    'pfunction.ORIGIN = porigin_method /\\ pfunction.ENDLINE = 6',
    'pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "void"]))] /\\ ~pfunction.SIGNATURE.BYREF',
    'pfunction.SIGNATURE.PARAMETERS = [psparam]',
    'psparam.TYPE = eps /\\ psparam.NAME = $ptascii("incoming")',
    '$class_at(S.CLASSES,pmethoddesc.OWNER) = (pclassdesc)',
    'porigin_method = PORIGIN n_unit pcpath_method',
    '$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_method ++ [PCFIELD 5])) = (NIdentifier (BYTES text_return) metadata_return)',
    '$ptlc($base64(text_return)) = $ptascii("void")',
    'ptcontext = {NAMESPACE pfunction.ENV.NAMESPACE, IMPORTS pfunction.ENV.CLASSES, SCOPE PTKNOWN pclassdesc.NAME eps, POSITION PTRETURN, OWNER pclassdesc.NAME, MEMBER pmethoddesc.NAME, FILE $call_sourcefile(S.FILES,porigin_method), LINE pfunction.LINE}',
    '$ptype_normalize(NIdentifier (BYTES text_return) metadata_return,ptcontext) = PTOK pfunction.SIGNATURE.RETURNS eps',
    '$property_get_return_type_source(NIdentifier (BYTES text_return) metadata_return,pfunction.SIGNATURE.RETURNS,ptcontext,true)',
    '~$property_get_return_type_source(NIdentifier (BYTES text_return) metadata_return,pfunction.SIGNATURE.RETURNS,ptcontext,false)',
    '$ppmethod_get_decl_return(pfunction.SIGNATURE.RETURNS) /\\ ~$ppmethod_get_scalar_return(pfunction.SIGNATURE.RETURNS)',
    '$ppmethod_get_decl_return([(PTBRANCH ([PTBUILTIN "never"]))]) /\\ ~$ppmethod_get_scalar_return([(PTBRANCH ([PTBUILTIN "never"]))])',
    '~$ppmethod_get_decl_return([(PTBRANCH ([PTBUILTIN "void"])),(PTBRANCH ([PTBUILTIN "null"]))])',
    '~$ppmethod_get_decl_return([(PTBRANCH ([PTBUILTIN "never"])),(PTBRANCH ([PTBUILTIN "int"]))])',
    '$ppmethod_get_declaration_signature(pfunction.SIGNATURE) /\\ ~$ppmethod_get_signature(pfunction.SIGNATURE)',
    '$property_get_method_source(S,pmethoddesc,true) /\\ ~$property_empty_get_source(S,pmethoddesc)',
    '$property_get_string_method(S,pmethoddesc)',
    '~$property_get_method_source(S[.SOURCES = eps],pmethoddesc,true)',
    '$property_get_context(S,pcallcontext) /\\ $property_get_frame(S,pcallcontext,pframe)',
    '$typed_fallthrough(pfunction) = TYPE_FALLTHROUGH porigin_method',
    '$typed_fallthrough_valid(S,porigin_method) /\\ $call_task_valid(S,TYPE_FALLTHROUGH porigin_method)',
    '$call_function_kind(S) = $ptascii("method")',
    '$reference_empty_task(S,pfunction.ENDLINE) = RETURN_NULL',
    '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PNULL,false,false) = TYPEREJECT',
    '$lookup(S.ENV,$ptascii("incoming")) = (n_formal)',
    'S.STORE[n_formal] = DEFINED pvalue_name',
    '$string_bytes(pvalue_name) = ($ptascii("fall"))',
    'S_caller = $constant_frame_scope(S,pframe,eps)',
    '$lookup(S_caller.ENV,$ptascii("selector")) = (n_selector)',
    'S.STORE[n_selector] = DEFINED pvalue_selector',
    '$string_bytes(pvalue_selector) = ($ptascii("fall"))',
    '$task_nodes(PROPERTY_GET_RESULT ppropertyget) = [HOBJECT ppropertyget.OBJECT] /\\ $call_receiver_roots(pcallcontext) = eps',
    '$heap_owners($heap_graph(S),HOBJECT ppropertyget.OBJECT) = 2',
    'S.EVENTS = [OUTPUT $ptascii("fall"),OUTPUT $ptascii(":")]',
    '$call_descriptors_valid(S) /\\ $class_state_valid(S) /\\ $property_state_valid(S) /\\ $heap_valid($heap_graph(S))',
    'PhpStep: S ~> S_null',
    'S_null.TODO = RETURN_NULL :: ptask_tail*',
    'S_null.STORE = S.STORE /\\ S_null.EVENTS = S.EVENTS',
    '$heap_owners($heap_graph(S_null),HOBJECT ppropertyget.OBJECT) = 2',
    'S_zero = $drive_steps(S,0)',
    'S_zero = S[.COMPLETION = BUDGET]',
    'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
    'S_one.COMPLETION = BUDGET /\\ S_one.TODO = S_null.TODO',
    'S_result_found = $scalar_union_get_seek(S_one[.COMPLETION = NORMAL],2000)',
    'S_result_found.COMPLETION = NORMAL \\/ S_result_found.COMPLETION = BUDGET',
    'S_result = S_result_found[.COMPLETION = NORMAL]',
    '$scalar_union_get_result(S_result)',
    'S_result.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_caller*',
    '$property_get_valid(S_result,ppropertyget,true) /\\ $property_get_tail_valid(S_result,ppropertyget)',
    '$property_get_verify_desc(S_result,ppropertyget) = eps',
    '$property_get_name_result_supported(S_result,ppropertyget,KNOWN PNULL)',
    'S_result.EVENTS = S.EVENTS',
    'PhpStep: S_result ~> S_copy',
    'S_copy.TODO = (PROPERTY_GET_COPY ppropertyget (KNOWN PNULL)) :: ptask_caller*',
    '$task_nodes(PROPERTY_GET_COPY ppropertyget (KNOWN PNULL)) = eps',
    '$heap_owners($heap_graph(S_copy),HOBJECT ppropertyget.OBJECT) = 1',
    '~$property_get_guard_tasks(S_copy.TODO,ppropertyget.OBJECT,ppropertyget.NAME)',
    'S_copy_one = $drive_steps(S_result,1)',
    'S_copy_one.COMPLETION = BUDGET /\\ S_copy_one.TODO = S_copy.TODO',
    '$heap_owners($heap_graph(S_copy_one),HOBJECT ppropertyget.OBJECT) = 1',
    'S_done = $drive_steps(S_copy_one[.COMPLETION = NORMAL],4096)',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.HELD = eps',
    'S_done.EVENTS = [OUTPUT $ptascii("fall"),OUTPUT $ptascii(":"),OUTPUT $ptascii("FALL;"),OUTPUT $ptascii("KEEP;"),OUTPUT $ptascii("DONE;")]',
    'S_done.STORE[n_selector] = DEFINED pvalue_selector',
    '$heap_owners($heap_graph(S_done),HOBJECT ppropertyget.OBJECT) = 1',
    '$call_descriptors_valid(S_done) /\\ $class_state_valid(S_done) /\\ $property_state_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
    '$drive_steps(S,4096) = S_done',
]
CASES = {'named-void-return-get-fallthrough-copy': {
    'source': SOURCE,
    'stage': ('S.CURRENT = (pcallcontext) '
              '-- if pcallcontext.TARGET = PROPERTY_GET_TARGET n_receiver porigin_method '
              '-- if S.TODO = (TYPE_FALLTHROUGH porigin_method) :: ptask_tail*'),
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
