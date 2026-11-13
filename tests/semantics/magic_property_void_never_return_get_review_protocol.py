#!/usr/bin/env python3
"""Check anonymous NEVER fallthrough diagnostics and actual Get cleanup."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_nullable_literal_return_get_review_protocol as shared


CATALOGUE = Path(__file__).with_name('magic_property_void_never_return_get_review_cases.json')
ROW = json.loads(CATALOGUE.read_text())['cases'][2]
SOURCE = ROW['source']
assert hashlib.sha256(SOURCE.encode()).hexdigest() == ROW['source_sha256']

CHECKS = [
    'S.FRAMES = [pframe]',
    'S.HELD = eps',
    'pframe.CONTEXT = eps',
    'pframe.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_caller*',
    'ppropertyget.OBJECT = n_receiver /\\ ppropertyget.METHOD = porigin_method /\\ ppropertyget.DECL = eps',
    'ppropertyget.NAME = $ptascii("value") /\\ pframe.ORIGIN = (ppropertyget.SITE)',
    'pcallcontext.FUNCTION = porigin_method',
    '$property_get_method(S,n_receiver) = (pmethoddesc)',
    'pfunction = pmethoddesc.FUNCTION',
    'pfunction.ORIGIN = porigin_method /\\ pfunction.CODE.STRICT /\\ pfunction.ENV.STRICT',
    'pfunction.ENDLINE = 6 /\\ ~pfunction.SIGNATURE.BYREF',
    'pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "never"]))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam]',
    'psparam.NAME = $ptascii("incoming") /\\ psparam.TYPE = [(PTBRANCH ([PTBUILTIN "mixed"]))]',
    '$class_at(S.CLASSES,pmethoddesc.OWNER) = (pclassdesc)',
    'pclassdesc.PARENT = eps /\\ pclassdesc.ORIGIN = ppropertyget.CLASS',
    'porigin_method = PORIGIN n_unit pcpath_method',
    '$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_method ++ [PCFIELD 5])) = (NIdentifier (BYTES text_return) metadata_return)',
    '$ptlc($base64(text_return)) = $ptascii("never")',
    'ptcontext = {NAMESPACE pfunction.ENV.NAMESPACE, IMPORTS pfunction.ENV.CLASSES, SCOPE PTKNOWN pclassdesc.NAME eps, POSITION PTRETURN, OWNER pclassdesc.NAME, MEMBER pmethoddesc.NAME, FILE $call_sourcefile(S.FILES,porigin_method), LINE pfunction.LINE}',
    '$ptype_normalize(NIdentifier (BYTES text_return) metadata_return,ptcontext) = PTOK pfunction.SIGNATURE.RETURNS eps',
    '$ppmethod_get_declaration_signature(pfunction.SIGNATURE) /\\ ~$ppmethod_get_signature(pfunction.SIGNATURE)',
    '$ppmethod_get_decl_return(pfunction.SIGNATURE.RETURNS)',
    '~$ppmethod_get_scalar_return(pfunction.SIGNATURE.RETURNS)',
    '~$ppmethod_get_scalar_return([(PTBRANCH ([PTBUILTIN "void"]))])',
    '~$ppmethod_get_decl_return([(PTBRANCH ([PTBUILTIN "never"])),(PTBRANCH ([PTBUILTIN "null"]))])',
    '~$ppmethod_get_decl_return([(PTBRANCH ([PTBUILTIN "void"])),(PTBRANCH ([PTBUILTIN "null"]))])',
    '~$ppmethod_get_decl_return([(PTBRANCH ([PTBUILTIN "array"]))])',
    '$property_get_return_type_source(NIdentifier (BYTES text_return) metadata_return,pfunction.SIGNATURE.RETURNS,ptcontext,true)',
    '~$property_get_return_type_source(NIdentifier (BYTES text_return) metadata_return,pfunction.SIGNATURE.RETURNS,ptcontext,false)',
    '~$property_get_return_type_source(NIdentifier (BYTES "dm9pZA==") metadata_return,pfunction.SIGNATURE.RETURNS,ptcontext,true)',
    '$property_get_method_source(S,pmethoddesc,true) /\\ ~$property_empty_get_source(S,pmethoddesc)',
    '~$property_get_method_source(S[.SOURCES = eps],pmethoddesc,true)',
    '$property_get_string_method(S,pmethoddesc) /\\ $property_get_string_source(S,ppropertyget)',
    '$property_get_context(S,pcallcontext) /\\ $property_get_frame(S,pcallcontext,pframe)',
    '$typed_fallthrough(pfunction) = TYPE_FALLTHROUGH porigin_method',
    '$call_task_valid(S,TYPE_FALLTHROUGH porigin_method)',
    '~$call_task_valid(S,TYPE_FALLTHROUGH ppropertyget.SITE)',
    '$call_function_kind(S) = $ptascii("method")',
    '$call_function_kind(S[.CURRENT = (pcallcontext[.FUNCTION = ppropertyget.SITE])]) = $ptascii("function")',
    '$call_function_name(S,pfunction) = pfunction.NAME',
    'pfunction.NAME = pclassdesc.NAME ++ $ptascii("::") ++ pmethoddesc.NAME',
    '$c_string($call_function_name(S,pfunction)) = $ptascii("class@anonymous")',
    '$return_function_name(S,pfunction) = $ptascii("class@anonymous::__get")',
    '$lookup(S.ENV,$ptascii("incoming")) = (n_formal)',
    'S.STORE[n_formal] = DEFINED pvalue_name',
    '$string_bytes(pvalue_name) = ($ptascii("value"))',
    'S_caller = $constant_frame_scope(S,pframe,eps)',
    '$lookup(S_caller.ENV,$ptascii("destination")) = (n_destination)',
    'S.STORE[n_destination] = DEFINED (PINT 42)',
    '$lookup(S_caller.ENV,$ptascii("selector")) = (n_selector)',
    'S.STORE[n_selector] = DEFINED pvalue_selector',
    '$string_bytes(pvalue_selector) = ($ptascii("value"))',
    '$call_receiver_roots(pcallcontext) = eps /\\ $task_nodes(PROPERTY_GET_RESULT ppropertyget) = [HOBJECT n_receiver]',
    '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 2',
    'S.EVENTS = [OUTPUT $ptascii("ENTER;")]',
    '$call_descriptors_valid(S) /\\ $class_state_valid(S) /\\ $property_state_valid(S) /\\ $heap_valid($heap_graph(S))',
    'preqbytes_message = $ptascii("class@anonymous(): never-returning method must not implicitly return")',
    'S_error = S[.COMPLETION = THROWN "TypeError" preqbytes_message 6]',
    'PhpStep: S ~> S_error',
    'S_zero = $drive_steps(S,0)',
    'S_zero = S[.COMPLETION = BUDGET]',
    'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
    'S_one.COMPLETION = BUDGET',
    'S_one.TODO = (THROW_SEARCH n_error) :: ptask_throw*',
    'S_one.OBJECTS[n_error] = THROWABLE pthrowable',
    'pthrowable.KIND = "TypeError"',
    '$string_bytes($throwable_field(S_one,n_error,"message")) = (preqbytes_message)',
    '$throwable_field(S_one,n_error,"line") = PINT 6',
    '$string_bytes($throwable_field(S_one,n_error,"file")) = ($call_sourcefile(S.FILES,porigin_method))',
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
    'S_release_one.COMPLETION = BUDGET /\\ S_release_one.TODO = S_release.TODO',
    '$heap_owners($heap_graph(S_release_one),HOBJECT n_receiver) = 1',
    'S_done = $drive_steps(S_release_one[.COMPLETION = NORMAL],4096)',
    'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.HELD = eps',
    'S_done.EVENTS = [OUTPUT $ptascii("ENTER;"),OUTPUT preqbytes_message,OUTPUT $ptascii(";"),OUTPUT $ptascii("KEEP;"),OUTPUT $ptascii("NAME_KEEP;"),OUTPUT $ptascii("DONE;")]',
    'S_done.STORE[n_destination] = DEFINED (PINT 42) /\\ S_done.STORE[n_selector] = DEFINED pvalue_selector',
    '$heap_owners($heap_graph(S_done),HOBJECT n_receiver) = 1',
    '~$property_get_guard_tasks(S_done.TODO,n_receiver,ppropertyget.NAME) /\\ ~$property_get_guard_frames(S_done.FRAMES,n_receiver,ppropertyget.NAME)',
    '$call_descriptors_valid(S_done) /\\ $class_state_valid(S_done) /\\ $property_state_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
    '$drive_steps(S,4096) = S_done',
]

CASES = {'anonymous-never-get-fallthrough-error-cleanup': {
    'source': SOURCE,
    'stage': ('S.CURRENT = (pcallcontext) '
              '-- if pcallcontext.TARGET = PROPERTY_GET_TARGET n_receiver porigin_method '
              '-- if S.TODO = (TYPE_FALLTHROUGH porigin_method) :: ptask_tail*'),
    'checks': CHECKS,
}}


if __name__ == '__main__':
    # Reuse only the source-stage renderer and Get THROW_SEARCH seeker.
    protocol.run(CASES, (Path(__file__), CATALOGUE, Path(shared.__file__), shared.CATALOGUE),
                 fixture_renderer=shared.render, runner_flags=('--sl',))
