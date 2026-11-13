#!/usr/bin/env python3
"""Check source-authenticated quiet void/never Get and saved receiver cleanup."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('magic_property_void_never_quiet_get_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
assert all(hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256'] for row in ROWS)

HELPERS = r'''
dec $quiet_bottom_stage(pstate,nat) : bool
def $quiet_bottom_stage(S,0) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_tail*
  -- if S.RESULT = KNOWN PNULL
def $quiet_bottom_stage(S,1) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce true) :: ptask_tail*
  -- if ppropertycoalesce.PROPERTY = (porigin_property)
  -- if S.RESULT = KNOWN PNULL
def $quiet_bottom_stage(S,2) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n_error) :: (PROPERTY_COALESCE_RESULT ppropertycoalesce true) :: ptask_tail*
def $quiet_bottom_stage(S,n) = false -- otherwise
dec $quiet_bottom_seek(pstate,nat,nat) : pstate
def $quiet_bottom_seek(S,n_stage,n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $quiet_bottom_seek(S,n_stage,n) = S -- if $quiet_bottom_stage(S,n_stage) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $quiet_bottom_seek(S,n_stage,0) = S -- if ~$quiet_bottom_stage(S,n_stage) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $quiet_bottom_seek(S,n_stage,n) = $quiet_bottom_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$quiet_bottom_stage(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''

CASES = {
    'void-quiet-get-null-result-private-rhs-and-skip': {
        'source': ROWS[0]['source'],
        'stage': ('S.CURRENT = (pcallcontext) '
                  '-- if pcallcontext.TARGET = PROPERTY_EMPTY_TARGET ppropertyempty true '
                  '-- if S.TODO = (TYPE_FALLTHROUGH porigin_method) :: ptask_return*'),
        'checks': [
            r'S.FRAMES = [pframe]',
            r'S.HELD = eps',
            r'pframe.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_caller*',
            r'ppropertyempty.GET = porigin_method /\ ppropertyempty.PROPERTY = eps /\ ppropertyempty.NAME = $ptascii("probe")',
            r'n_receiver = ppropertyempty.OBJECT',
            r'$property_get_method(S,n_receiver) = (pmethoddesc)',
            r'pfunction = pmethoddesc.FUNCTION',
            r'pfunction.ORIGIN = porigin_method /\ pfunction.ENDLINE = 5 /\ ~pfunction.SIGNATURE.BYREF',
            r'pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "void"]))]',
            r'pfunction.SIGNATURE.PARAMETERS = [psparam]',
            r'$(|psparam.TYPE| = 2) /\ "string" <- $ptmasks(psparam.TYPE) /\ "null" <- $ptmasks(psparam.TYPE)',
            r'$class_at(S.CLASSES,pmethoddesc.OWNER) = (pclassdesc)',
            r'pclassdesc.NAME = $ptascii("QuietVoidRead") /\ pclassdesc.PARENT = eps',
            r'porigin_method = PORIGIN n_unit pcpath_method',
            r'$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_method ++ [PCFIELD 5])) = (NIdentifier (BYTES text_return) metadata_return)',
            r'$ptlc($base64(text_return)) = $ptascii("void")',
            r'ptcontext = {NAMESPACE pfunction.ENV.NAMESPACE, IMPORTS pfunction.ENV.CLASSES, SCOPE PTKNOWN pclassdesc.NAME eps, POSITION PTRETURN, OWNER pclassdesc.NAME, MEMBER pmethoddesc.NAME, FILE $call_sourcefile(S.FILES,porigin_method), LINE pfunction.LINE}',
            r'$ptype_normalize(NIdentifier (BYTES text_return) metadata_return,ptcontext) = PTOK pfunction.SIGNATURE.RETURNS eps',
            r'$property_get_return_type_source(NIdentifier (BYTES text_return) metadata_return,pfunction.SIGNATURE.RETURNS,ptcontext,true)',
            r'~$property_get_return_type_source(NIdentifier (BYTES text_return) metadata_return,pfunction.SIGNATURE.RETURNS,ptcontext,false)',
            r'$property_quiet_get_source(S,pmethoddesc) /\ ~$property_empty_get_source(S,pmethoddesc)',
            r'$property_empty_method_source(S,pmethoddesc,true) /\ $property_coalesce_method_source(S,pmethoddesc,true)',
            r'~$property_quiet_get_source(S[.SOURCES = eps],pmethoddesc)',
            r'~$property_quiet_get_source(S,pmethoddesc[.FUNCTION = pfunction[.ENDLINE = 99]])',
            r'~$property_quiet_get_source(S,pmethoddesc[.FUNCTION = pfunction[.SIGNATURE = pfunction.SIGNATURE[.BYREF = true]]])',
            r'$typed_fallthrough_valid(S,porigin_method) /\ $call_task_valid(S,TYPE_FALLTHROUGH porigin_method)',
            r'$reference_empty_task(S,pfunction.ENDLINE) = RETURN_NULL',
            r'$property_empty_context(S,pcallcontext) /\ $property_empty_get_active(S,n_receiver,ppropertyempty.NAME)',
            r'$call_function_kind(S) = $ptascii("method")',
            r'$call_function_kind(S[.CURRENT = (pcallcontext[.FUNCTION = ppropertyempty.SITE])]) = $ptascii("function")',
            r'$call_function_kind(S[.CURRENT = (pcallcontext[.TARGET = PROPERTY_EMPTY_TARGET ppropertyempty false])]) = $ptascii("function")',
            r'$call_receiver_roots(pcallcontext) = eps /\ $task_nodes(PROPERTY_EMPTY_RESULT ppropertyempty true) = [HOBJECT n_receiver]',
            r'S_caller = $constant_frame_scope(S,pframe,eps)',
            r'$lookup(S_caller.ENV,$ptascii("receiver")) = (n_receiver_cell)',
            r'$lookup(S_caller.ENV,$ptascii("selector")) = (n_selector)',
            r'$lookup(S_caller.ENV,$ptascii("written")) = (n_written)',
            r'S.STORE[n_receiver_cell] = DEFINED (POBJECT n_receiver) /\ S.STORE[n_written] = DEFINED (PINT 42)',
            r'S.STORE[n_selector] = DEFINED pvalue_selector',
            r'$string_bytes(pvalue_selector) = ($ptascii("probe"))',
            r'$heap_owners($heap_graph(S),HOBJECT n_receiver) = 2',
            r'S.EVENTS = [OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;")]',
            r'PhpStep: S ~> S_null',
            r'S_null.TODO = RETURN_NULL :: ptask_return*',
            r'S_null.STORE = S.STORE /\ S_null.EVENTS = S.EVENTS /\ S_null.ALLOCATIONS = S.ALLOCATIONS',
            r'S_zero = $drive_steps(S,0)',
            r'S_zero = S[.COMPLETION = BUDGET]',
            r'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
            r'S_one.COMPLETION = BUDGET /\ S_one.TODO = S_null.TODO',
            r'S_result_found = $quiet_bottom_seek(S_one[.COMPLETION = NORMAL],0,2000)',
            r'S_result_found.COMPLETION = NORMAL \/ S_result_found.COMPLETION = BUDGET',
            r'S_result = S_result_found[.COMPLETION = NORMAL]',
            r'S_result.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_caller*',
            r'S_result.RESULT = KNOWN PNULL /\ $property_empty_valid(S_result,ppropertyempty)',
            r'$property_magic_cv_result_supported(S_result,ppropertyempty.SITE,ppropertyempty.LINE,true,S_result.RESULT)',
            r'$property_empty_guard(S_result,n_receiver,ppropertyempty.NAME) /\ $heap_owners($heap_graph(S_result),HOBJECT n_receiver) = 2',
            r'PhpStep: S_result ~> S_truth',
            r'S_truth.RESULT = KNOWN (PBOOL true) /\ S_truth.TODO = ptask_caller*',
            r'~$property_empty_guard(S_truth,n_receiver,ppropertyempty.NAME) /\ $heap_owners($heap_graph(S_truth),HOBJECT n_receiver) = 1',
            r'S_private_found = $quiet_bottom_seek(S_result,1,4000)',
            r'S_private_found.COMPLETION = NORMAL \/ S_private_found.COMPLETION = BUDGET',
            r'S_private = S_private_found[.COMPLETION = NORMAL]',
            r'S_private.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce true) :: (ORIGIN_RETURN (porigin_parent)) :: (PROPERTY_COALESCE_ASSIGN_VALUE porigin_parent pbase_pending 0 eps) :: ptask_private*',
            r'ppropertycoalesce.OBJECT = n_receiver /\ ppropertycoalesce.NAME = $ptascii("value")',
            r'S_private.RESULT = KNOWN PNULL',
            r'$property_coalesce_valid(S_private,ppropertycoalesce) /\ $call_task_valid(S_private,PROPERTY_COALESCE_RESULT ppropertycoalesce true)',
            r'$task_nodes(PROPERTY_COALESCE_RESULT ppropertycoalesce true) = [HOBJECT n_receiver] /\ $base_nodes(pbase_pending) = eps',
            r'$heap_owners($heap_graph(S_private),HOBJECT n_receiver) = 2 /\ S_private.STORE[n_written] = DEFINED (PINT 42)',
            r'PhpStep: S_private ~> S_release',
            r'S_release.TODO = (ORIGIN_RETURN (porigin_parent)) :: (PROPERTY_COALESCE_ASSIGN_VALUE porigin_parent pbase_pending 0 eps) :: ptask_private*',
            r'S_release.RESULT = KNOWN PNULL /\ S_release.BASE = BASE_VALUE (KNOWN PNULL)',
            r'$heap_owners($heap_graph(S_release),HOBJECT n_receiver) = 1 /\ S_release.EVENTS = S_private.EVENTS',
            r'S_done = $drive_steps(S_private,4096)',
            r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.HELD = eps',
            r'S_done.STORE[n_receiver_cell] = DEFINED (POBJECT n_receiver) /\ S_done.STORE[n_written] = DEFINED (PINT 9) /\ S_done.STORE[n_selector] = DEFINED pvalue_selector',
            r'S_done.EVENTS = [OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;"),OUTPUT $ptascii("EMPTY;"),OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;"),OUTPUT $ptascii("RHS;"),OUTPUT $ptascii("FALL;"),OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;"),OUTPUT $ptascii("RHS;"),OUTPUT $ptascii("S;"),OUTPUT $ptascii("ASSIGN;"),OUTPUT $ptascii("SET;"),OUTPUT $ptascii("I;"),OUTPUT $ptascii("RHS;"),OUTPUT $ptascii("SKIP;"),OUTPUT $ptascii("NAME_KEEP;"),OUTPUT $ptascii("DONE;")]',
            r'$heap_owners($heap_graph(S_done),HOBJECT n_receiver) = 1 /\ $value_nodes(PNULL) = eps',
            r'$call_descriptors_valid(S_done) /\ $class_state_valid(S_done) /\ $property_state_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
            r'$drive_steps(S,4096) = S_done /\ $drive_steps(S_one[.COMPLETION = NORMAL],4096) = S_done',
        ],
    },
    'never-quiet-get-method-error-coalesce-unwind': {
        'source': ROWS[1]['source'],
        'stage': ('S.CURRENT = (pcallcontext) '
                  '-- if pcallcontext.TARGET = PROPERTY_COALESCE_TARGET ppropertycoalesce true '
                  '-- if S.TODO = (TYPE_FALLTHROUGH porigin_method) :: ptask_return*'),
        'checks': [
            r'S.FRAMES = [pframe]',
            r'S.HELD = eps',
            r'pframe.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce true) :: ptask_caller*',
            r'ppropertycoalesce.GET = (porigin_method) /\ ppropertycoalesce.PROPERTY = eps /\ ppropertycoalesce.NAME = $ptascii("lost")',
            r'n_receiver = ppropertycoalesce.OBJECT',
            r'$property_get_method(S,n_receiver) = (pmethoddesc)',
            r'pfunction = pmethoddesc.FUNCTION',
            r'pfunction.ORIGIN = porigin_method /\ pfunction.ENDLINE = 8 /\ ~pfunction.SIGNATURE.BYREF',
            r'pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "never"]))]',
            r'$class_at(S.CLASSES,pmethoddesc.OWNER) = (pclassdesc)',
            r'pclassdesc.PARENT = eps /\ pclassdesc.ORIGIN = ppropertycoalesce.CLASS',
            r'porigin_method = PORIGIN n_unit pcpath_method',
            r'$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_method ++ [PCFIELD 5])) = (NIdentifier (BYTES text_return) metadata_return)',
            r'$ptlc($base64(text_return)) = $ptascii("never")',
            r'ptcontext = {NAMESPACE pfunction.ENV.NAMESPACE, IMPORTS pfunction.ENV.CLASSES, SCOPE PTKNOWN pclassdesc.NAME eps, POSITION PTRETURN, OWNER pclassdesc.NAME, MEMBER pmethoddesc.NAME, FILE $call_sourcefile(S.FILES,porigin_method), LINE pfunction.LINE}',
            r'$ptype_normalize(NIdentifier (BYTES text_return) metadata_return,ptcontext) = PTOK pfunction.SIGNATURE.RETURNS eps',
            r'$property_quiet_get_source(S,pmethoddesc) /\ ~$property_empty_get_source(S,pmethoddesc)',
            r'~$property_quiet_get_source(S[.SOURCES = eps],pmethoddesc)',
            r'~$property_quiet_get_source(S,pmethoddesc[.FUNCTION = pfunction[.ENDLINE = 99]])',
            r'$typed_fallthrough_valid(S,porigin_method) /\ $call_task_valid(S,TYPE_FALLTHROUGH porigin_method)',
            r'~$call_task_valid(S,TYPE_FALLTHROUGH ppropertycoalesce.SITE)',
            r'$property_coalesce_context(S,pcallcontext)',
            r'$call_function_kind(S) = $ptascii("method")',
            r'$call_function_kind(S[.CURRENT = (pcallcontext[.FUNCTION = ppropertycoalesce.SITE])]) = $ptascii("function")',
            r'$call_function_kind(S[.CURRENT = (pcallcontext[.TARGET = PROPERTY_COALESCE_TARGET ppropertycoalesce false])]) = $ptascii("function")',
            r'$call_function_name(S,pfunction) = pfunction.NAME',
            r'pfunction.NAME = pclassdesc.NAME ++ $ptascii("::") ++ pmethoddesc.NAME',
            r'$c_string($call_function_name(S,pfunction)) = $ptascii("class@anonymous")',
            r'$return_function_name(S,pfunction) = $ptascii("class@anonymous::__get")',
            r'$call_receiver_roots(pcallcontext) = eps /\ $task_nodes(PROPERTY_COALESCE_RESULT ppropertycoalesce true) = [HOBJECT n_receiver]',
            r'S_caller = $constant_frame_scope(S,pframe,eps)',
            r'$lookup(S_caller.ENV,$ptascii("receiver")) = (n_receiver_cell)',
            r'$lookup(S_caller.ENV,$ptascii("destination")) = (n_destination)',
            r'$lookup(S_caller.ENV,$ptascii("selector")) = (n_selector)',
            r'S.STORE[n_destination] = DEFINED (PINT 42) /\ S.STORE[n_receiver_cell] = DEFINED (POBJECT n_receiver)',
            r'S.STORE[n_selector] = DEFINED pvalue_selector',
            r'$string_bytes(pvalue_selector) = ($ptascii("changed"))',
            r'$heap_owners($heap_graph(S),HOBJECT n_receiver) = 2',
            r'S.EVENTS = [OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;")]',
            r'preqbytes_message = $ptascii("class@anonymous(): never-returning method must not implicitly return")',
            r'S_error = S[.COMPLETION = THROWN "TypeError" preqbytes_message 8]',
            r'PhpStep: S ~> S_error',
            r'S_zero = $drive_steps(S,0)',
            r'S_zero = S[.COMPLETION = BUDGET]',
            r'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
            r'S_one.COMPLETION = BUDGET',
            r'S_one.TODO = (THROW_SEARCH n_error) :: ptask_throw*',
            r'S_one.OBJECTS[n_error] = THROWABLE pthrowable',
            r'pthrowable.KIND = "TypeError"',
            r'$string_bytes($throwable_field(S_one,n_error,"message")) = (preqbytes_message)',
            r'$throwable_field(S_one,n_error,"line") = PINT 8 /\ $throwable_field(S_one,n_error,"previous") = PNULL',
            r'$string_bytes($throwable_field(S_one,n_error,"file")) = ($call_sourcefile(S.FILES,porigin_method))',
            r'S_one.EVENTS = S.EVENTS /\ S_one.STORE[n_destination] = DEFINED (PINT 42)',
            r'S_unwind_found = $quiet_bottom_seek(S_one[.COMPLETION = NORMAL],2,2000)',
            r'S_unwind_found.COMPLETION = NORMAL \/ S_unwind_found.COMPLETION = BUDGET',
            r'S_unwind = S_unwind_found[.COMPLETION = NORMAL]',
            r'S_unwind.TODO = (THROW_SEARCH n_error) :: (PROPERTY_COALESCE_RESULT ppropertycoalesce true) :: ptask_caller*',
            r'$property_coalesce_throw_tail(S_unwind,ppropertycoalesce,true)',
            r'$heap_owners($heap_graph(S_unwind),HOBJECT n_receiver) = 2',
            r'PhpStep: S_unwind ~> S_release',
            r'S_release.TODO = (THROW_SEARCH n_error) :: ptask_caller*',
            r'S_release.RESULT = KNOWN PNULL /\ S_release.BASE = BASE_VALUE (KNOWN PNULL)',
            r'$heap_owners($heap_graph(S_release),HOBJECT n_receiver) = 1',
            r'S_release.STORE[n_destination] = DEFINED (PINT 42) /\ S_release.STORE[n_selector] = DEFINED pvalue_selector',
            r'S_done = $drive_steps(S_unwind,4096)',
            r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.HELD = eps',
            r'S_done.STORE[n_destination] = DEFINED (PINT 42) /\ S_done.STORE[n_selector] = DEFINED pvalue_selector',
            r'S_done.EVENTS = [OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;"),OUTPUT preqbytes_message,OUTPUT $ptascii(";"),OUTPUT $ptascii("8"),OUTPUT $ptascii(";"),OUTPUT $ptascii("ROOT;"),OUTPUT $ptascii("KEEP;"),OUTPUT $ptascii("NAME_CHANGED;"),OUTPUT $ptascii("DONE;")]',
            r'$heap_owners($heap_graph(S_done),HOBJECT n_receiver) = 1',
            r'~$property_empty_get_active(S_done,n_receiver,ppropertycoalesce.NAME)',
            r'$call_descriptors_valid(S_done) /\ $class_state_valid(S_done) /\ $property_state_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
            r'$drive_steps(S,4096) = S_done /\ $drive_steps(S_one[.COMPLETION = NORMAL],4096) = S_done',
        ],
    },
}


def render(case, fixture, filename):
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
    return text, len(case['checks']) + 6


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE), runner_flags=('--sl',), fixture_renderer=render)
