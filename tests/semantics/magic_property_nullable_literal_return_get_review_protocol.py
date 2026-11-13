#!/usr/bin/env python3
"""Independent strict nullable-literal Get rejection and receiver cleanup."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol


CATALOGUE = Path(__file__).with_name('magic_property_nullable_literal_return_get_review_cases.json')
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']

# Retain the exact first owner/body from the independent original. The reduced
# caller selects its throwing branch; this state fixture claims no source credit.
SOURCE = ROW['source'].split('$nullableTrue = new class {', 1)[0] + '''$selector = "bad";
$destination = 42;
try {
    $destination = $nullableFalse->$selector === false;
} catch (TypeError $failure) {
    echo "TYPE;";
}
echo $destination === 42 ? "KEEP;" : "BAD_STORE;";
echo $selector === "bad" ? "NAME_KEEP;" : "BAD_SELECTOR;";
echo "DONE;";
'''

HELPERS = r'''
dec $nullable_literal_get_unwind(pstate) : bool
def $nullable_literal_get_unwind(S) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n_error) :: (PROPERTY_GET_RESULT ppropertyget) :: ptask_tail*
def $nullable_literal_get_unwind(S) = false -- otherwise
dec $nullable_literal_get_seek_unwind(pstate, nat) : pstate
def $nullable_literal_get_seek_unwind(S, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $nullable_literal_get_seek_unwind(S, n) = S
  -- if $nullable_literal_get_unwind(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $nullable_literal_get_seek_unwind(S, 0) = S
  -- if ~$nullable_literal_get_unwind(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $nullable_literal_get_seek_unwind(S, n) = $nullable_literal_get_seek_unwind($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$nullable_literal_get_unwind(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''

CHECKS = [
    'S.ORIGIN = (porigin_return)',
    'S.RESULT = KNOWN (PINT 0)',
    'S.FRAMES = [pframe]',
    'pframe.CONTEXT = eps /\\ S.HELD = eps',
    'pframe.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_caller*',
    'ppropertyget.OBJECT = n_receiver /\\ ppropertyget.METHOD = porigin_method /\\ ppropertyget.DECL = eps',
    'ppropertyget.NAME = $ptascii("bad") /\\ pframe.ORIGIN = (ppropertyget.SITE)',
    '$property_get_method(S,n_receiver) = (pmethoddesc)',
    'pfunction = pmethoddesc.FUNCTION',
    'pfunction.ORIGIN = porigin_method /\\ pfunction.CODE.STRICT /\\ pfunction.ENV.STRICT',
    '~pfunction.SIGNATURE.BYREF /\\ pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "false"])),(PTBRANCH ([PTBUILTIN "null"]))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam]',
    'psparam.NAME = $ptascii("incoming") /\\ psparam.TYPE = [(PTBRANCH ([PTBUILTIN "mixed"]))]',
    '$class_at(S.CLASSES,pmethoddesc.OWNER) = (pclassdesc)',
    'pclassdesc.PARENT = eps /\\ pclassdesc.ORIGIN = ppropertyget.CLASS',
    'porigin_method = PORIGIN n_unit pcpath_method',
    '$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_method ++ [PCFIELD 5])) = (NNullableType (NIdentifier (BYTES text_return) metadata_return) metadata_nullable)',
    'phpType18_return = NNullableType (NIdentifier (BYTES text_return) metadata_return) metadata_nullable',
    '$ptlc($base64(text_return)) = $ptascii("false")',
    'ptcontext = {NAMESPACE pfunction.ENV.NAMESPACE, IMPORTS pfunction.ENV.CLASSES, SCOPE PTKNOWN pclassdesc.NAME eps, POSITION PTRETURN, OWNER pclassdesc.NAME, MEMBER pmethoddesc.NAME, FILE $call_sourcefile(S.FILES,porigin_method), LINE pfunction.LINE}',
    '$ptype_normalize(phpType18_return,ptcontext) = PTOK pfunction.SIGNATURE.RETURNS eps',
    '$pttypename(pfunction.SIGNATURE.RETURNS) = $ptascii("?false")',
    '$ppmethod_get_scalar_return(pfunction.SIGNATURE.RETURNS)',
    '$typed_exact(pfunction.SIGNATURE.RETURNS,PNULL) /\\ $typed_exact(pfunction.SIGNATURE.RETURNS,PBOOL false)',
    '~$typed_exact(pfunction.SIGNATURE.RETURNS,PBOOL true)',
    'phpType18_union = NUnionType (SEQUENCE ([NIdentifier (BYTES text_return) metadata_return,NIdentifier (BYTES "bnVsbA==") metadata_return])) metadata_nullable',
    '$ptype_normalize(phpType18_union,ptcontext) = PTOK pfunction.SIGNATURE.RETURNS eps',
    '$property_get_return_type_source(phpType18_union,pfunction.SIGNATURE.RETURNS,ptcontext,true)',
    'phpType18_reverse = NUnionType (SEQUENCE ([NIdentifier (BYTES "bnVsbA==") metadata_return,NIdentifier (BYTES text_return) metadata_return])) metadata_nullable',
    '$ptype_normalize(phpType18_reverse,ptcontext) = PTOK ptbranch_reverse* eps',
    'ptbranch_reverse* = [(PTBRANCH ([PTBUILTIN "null"])),(PTBRANCH ([PTBUILTIN "false"]))]',
    '$property_get_return_type_source(phpType18_reverse,ptbranch_reverse*,ptcontext,true)',
    '~$property_get_return_type_source(phpType18_reverse,pfunction.SIGNATURE.RETURNS,ptcontext,true)',
    '~$property_get_return_type_source(NIdentifier (BYTES text_return) metadata_return,pfunction.SIGNATURE.RETURNS,ptcontext,true)',
    '~$ppmethod_get_scalar_return([(PTBRANCH ([PTBUILTIN "true"])),(PTBRANCH ([PTBUILTIN "false"]))])',
    '~$ppmethod_get_scalar_return([(PTBRANCH ([PTBUILTIN "null"])),(PTBRANCH ([PTBUILTIN "null"]))])',
    '$property_get_return_type_source(phpType18_return,pfunction.SIGNATURE.RETURNS,ptcontext,true)',
    '~$property_get_return_type_source(phpType18_return,pfunction.SIGNATURE.RETURNS,ptcontext,false)',
    '$property_get_method_source(S,pmethoddesc,true) /\\ ~$property_empty_get_source(S,pmethoddesc)',
    '$property_get_string_source(S,ppropertyget) /\\ $property_get_cv_name_source(S,ppropertyget)',
    '$property_get_context(S,pcallcontext) /\\ $property_get_frame(S,pcallcontext,pframe)',
    'S_get = S[.ORIGIN = pframe.ORIGIN][.TODO = pframe.TODO]',
    '$property_get_history(S_get,ppropertyget) /\\ $property_get_tail_valid(S_get,ppropertyget)',
    '$typed_return_task_valid(S,z_return) /\\ $call_task_valid(S,RETURN_VALUE z_return)',
    'z_return = 8',
    '~$typed_return_task_valid(S,$(z_return + 1))',
    '~$typed_return_task_valid(S[.ORIGIN = (ppropertyget.SITE)],z_return)',
    '~$property_get_method_source(S[.SOURCES = eps],pmethoddesc,true)',
    '~$ppmethod_get_declaration_signature(pfunction.SIGNATURE[.BYREF = true])',
    '$ppmethod_get_declaration_signature(pfunction.SIGNATURE[.PARAMETERS = [psparam[.TYPE = eps]]])',
    '$property_get_guard_frames(S.FRAMES,n_receiver,ppropertyget.NAME)',
    '$call_receiver_roots(pcallcontext) = eps /\\ $task_nodes(PROPERTY_GET_RESULT ppropertyget) = [HOBJECT n_receiver]',
    '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 2',
    '$lookup(S.ENV,$ptascii("incoming")) = (n_formal)',
    'S.STORE[n_formal] = DEFINED (PBOOL true)',
    'S_caller = $constant_frame_scope(S,pframe,eps)',
    '$lookup(S_caller.ENV,$ptascii("destination")) = (n_destination)',
    'S.STORE[n_destination] = DEFINED (PINT 42)',
    '$lookup(S_caller.ENV,$ptascii("selector")) = (n_selector)',
    'S.STORE[n_selector] = DEFINED pvalue_selector',
    '$string_bytes(pvalue_selector) = ($ptascii("bad"))',
    'S.EVENTS = [OUTPUT $ptascii("ENTER;")]',
    '$call_descriptors_valid(S) /\\ $class_state_valid(S) /\\ $property_state_valid(S) /\\ $heap_valid($heap_graph(S))',
    '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PINT 0,true,false) = TYPEREJECT',
    '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PINT 0,false,false) = TYPEREJECT',
    '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PBOOL false,true,false) = TYPEVALUE (PBOOL false)',
    '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PBOOL false,false,false) = TYPEVALUE (PBOOL false)',
    '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PNULL,true,false) = TYPEVALUE PNULL',
    '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PNULL,false,false) = TYPEVALUE PNULL',
    '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PBOOL true,true,false) = TYPEREJECT',
    '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PBOOL true,false,false) = TYPEREJECT',
    'preqbytes_message = $c_string(pclassdesc.NAME) ++ $ptascii("::") ++ pmethoddesc.NAME ++ $ptascii("(): Return value must be of type ?false, int returned")',
    'preqbytes_message = $ptascii("class@anonymous::__get(): Return value must be of type ?false, int returned")',
    'S_error = $typed_return_checked(S,z_return,false)',
    'S_error = S[.COMPLETION = THROWN "TypeError" preqbytes_message z_return]',
    'PhpStep: S ~> S_error',
    'S_zero = $drive_steps(S,0)',
    'S_zero = S[.COMPLETION = BUDGET]',
    'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
    'S_one.COMPLETION = BUDGET',
    'S_one.TODO = (THROW_SEARCH n_error) :: ptask_throw*',
    'S_one.OBJECTS[n_error] = THROWABLE pthrowable',
    'pthrowable.KIND = "TypeError" /\\ pthrowable.FILEORIGIN = (porigin_return)',
    '$string_bytes($throwable_field(S_one,n_error,"message")) = (preqbytes_message)',
    '$throwable_field(S_one,n_error,"line") = PINT z_return',
    'S_one.CURRENT = S.CURRENT /\\ S_one.FRAMES = S.FRAMES /\\ S_one.EVENTS = S.EVENTS',
    'S_one.STORE[n_destination] = DEFINED (PINT 42) /\\ S_one.STORE[n_selector] = DEFINED pvalue_selector',
    '$heap_owners($heap_graph(S_one),HOBJECT n_receiver) = 2',
    'S_found = $nullable_literal_get_seek_unwind(S_one[.COMPLETION = NORMAL],2000)',
    'S_found.COMPLETION = NORMAL \\/ S_found.COMPLETION = BUDGET',
    'S_unwind = S_found[.COMPLETION = NORMAL]',
    '$nullable_literal_get_unwind(S_unwind)',
    'S_unwind.TODO = (THROW_SEARCH n_error) :: (PROPERTY_GET_RESULT ppropertyget) :: ptask_caller*',
    '$property_get_guard_tasks(S_unwind.TODO,n_receiver,ppropertyget.NAME)',
    '$heap_owners($heap_graph(S_unwind),HOBJECT n_receiver) = 2',
    'PhpStep: S_unwind ~> S_release',
    'S_release.TODO = (THROW_SEARCH n_error) :: (PROPERTY_GET_COPY ppropertyget (KNOWN PNULL)) :: ptask_caller*',
    'S_release.RESULT = KNOWN PNULL /\\ S_release.BASE = BASE_VALUE (KNOWN PNULL)',
    '~$property_get_guard_tasks(S_release.TODO,n_receiver,ppropertyget.NAME)',
    '$heap_owners($heap_graph(S_release),HOBJECT n_receiver) = 1',
    'S_release.STORE[n_destination] = DEFINED (PINT 42) /\\ S_release.STORE[n_selector] = DEFINED pvalue_selector',
    '$call_descriptors_valid(S_release) /\\ $property_state_valid(S_release) /\\ $heap_valid($heap_graph(S_release))',
    'S_release_one = $drive_steps(S_unwind,1)',
    'S_release_one.COMPLETION = BUDGET',
    'S_release_one.TODO = S_release.TODO /\\ S_release_one.RESULT = S_release.RESULT /\\ S_release_one.BASE = S_release.BASE',
    'S_release_one.EVENTS = S_release.EVENTS',
    '$heap_owners($heap_graph(S_release_one),HOBJECT n_receiver) = 1',
    '~$property_get_guard_tasks(S_release_one.TODO,n_receiver,ppropertyget.NAME)',
    'S_done = $drive_steps(S_release_one[.COMPLETION = NORMAL],4096)',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.HELD = eps',
    'S_done.EVENTS = [OUTPUT $ptascii("ENTER;"),OUTPUT $ptascii("TYPE;"),OUTPUT $ptascii("KEEP;"),OUTPUT $ptascii("NAME_KEEP;"),OUTPUT $ptascii("DONE;")]',
    'S_done.STORE[n_destination] = DEFINED (PINT 42) /\\ S_done.STORE[n_selector] = DEFINED pvalue_selector',
    '$lookup(S_done.ENV,$ptascii("failure")) = (n_failure)',
    'S_done.STORE[n_failure] = DEFINED (POBJECT n_error)',
    '$heap_owners($heap_graph(S_done),HOBJECT n_receiver) = 1',
    '~$property_get_guard_tasks(S_done.TODO,n_receiver,ppropertyget.NAME) /\\ ~$property_get_guard_frames(S_done.FRAMES,n_receiver,ppropertyget.NAME)',
    '$call_descriptors_valid(S_done) /\\ $class_state_valid(S_done) /\\ $property_state_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
    '$drive_steps(S,4096) = S_done',
]

CASES = {'anonymous-strict-nullable-literal-return-get-error': {
    'source': SOURCE,
    'stage': ('S.CURRENT = (pcallcontext) '
              '-- if pcallcontext.TARGET = PROPERTY_GET_TARGET n_receiver porigin_method '
              '-- if S.TODO = (RETURN_VALUE z_return) :: ptask_tail* '
              '-- if S.RESULT = KNOWN (PINT 0)'),
    'checks': CHECKS,
}}


def render(case, fixture, filename):
    # Use the common source/checked-AST path and its ordinary source-state seeker.
    stage = case['stage']
    text = (HELPERS + '\ndec $stage(pstate) : bool\n'
            'def $stage(S) = true -- if ' + stage + '\n'
            'def $stage(S) = false -- otherwise\n'
            'dec $seek(pstate, nat) : pstate\n'
            'def $seek(S,n) = S -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET\n'
            'def $seek(S,n) = S -- if $stage(S) -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
            'def $seek(S,0) = S -- if ~$stage(S) -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
            'def $seek(S,n) = $seek($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1))) '
            '-- if $(n > 0) /\\ ~$stage(S) -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
            'dec $main() : bool\ndef $main() = true\n'
            '  -- if S_initial = $php_run(' + fixture + ',0,' + filename + ')\n'
            '  -- if S_initial.COMPLETION = NORMAL \\/ S_initial.COMPLETION = BUDGET\n'
            '  -- if S_found_initial = $seek(S_initial,2000)\n'
            '  -- if S_found_initial.COMPLETION = NORMAL \\/ S_found_initial.COMPLETION = BUDGET\n'
            '  -- if S = S_found_initial[.COMPLETION = NORMAL]\n'
            '  -- if ' + stage + '\n')
    text += ''.join('  -- ' + ('' if check.startswith('PhpStep:') else 'if ') + check + '\n'
                    for check in case['checks'])
    return text, len(case['checks']) + 6


if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__), CATALOGUE), fixture_renderer=render,
                 runner_flags=('--sl',))
