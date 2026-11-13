#!/usr/bin/env python3
"""Check absent Boolean Get values and weak literal-false return rejection."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol


CATALOGUE = Path(__file__).with_name('magic_property_bool_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

HELPERS = r'''
dec $bool_review_get_dtor(pstate,nat) : bool
def $bool_review_get_dtor(S,n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n
def $bool_review_get_dtor(S,n) = false -- otherwise
dec $bool_review_get_seek_dtor(pstate,nat,nat) : pstate
def $bool_review_get_seek_dtor(S,n_object,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $bool_review_get_seek_dtor(S,n_object,n) = S
  -- if $bool_review_get_dtor(S,n_object)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $bool_review_get_seek_dtor(S,n_object,0) = S
  -- if ~$bool_review_get_dtor(S,n_object)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $bool_review_get_seek_dtor(S,n_object,n) = $bool_review_get_seek_dtor($drive_steps(S[.COMPLETION = NORMAL],1),n_object,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$bool_review_get_dtor(S,n_object)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $bool_review_get_catch(pstate) : bool
def $bool_review_get_catch(S) = true
  -- if S.TODO = (CATCH_BIND porigin n_index n_error) :: ptask_tail*
def $bool_review_get_catch(S) = false -- otherwise
dec $bool_review_get_seek_catch(pstate,nat) : pstate
def $bool_review_get_seek_catch(S,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $bool_review_get_seek_catch(S,n) = S
  -- if $bool_review_get_catch(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $bool_review_get_seek_catch(S,0) = S
  -- if ~$bool_review_get_catch(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $bool_review_get_seek_catch(S,n) = $bool_review_get_seek_catch($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$bool_review_get_catch(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''

LEGACY = ['S.CURRENT = eps /\\ S.FRAMES = eps /\\ S.HELD = eps',
 'ppropertyempty.PROPERTY = eps /\\ ppropertyempty.NAME = eps /\\ ppropertyempty.LINE = 8',
 'S.RESULT = KNOWN (PBOOL false)',
 'n_receiver = ppropertyempty.OBJECT',
 'S.OBJECTS[n_receiver] = INSTANCE ppropertyempty.CLASS',
 '(HOBJECT n_receiver) <- S.ALLOCATIONS /\\ ~$instance_storage_freeing(S,n_receiver)',
 '$property_get_method(S,n_receiver) = (pmethoddesc)',
 'pfunction = pmethoddesc.FUNCTION',
 'pfunction.ORIGIN = ppropertyempty.GET /\\ pfunction.ENDLINE = 5',
 'pfunction.SIGNATURE.RETURNS = eps /\\ ~pfunction.SIGNATURE.BYREF /\\ ~pfunction.CODE.STRICT',
 'pfunction.SIGNATURE.PARAMETERS = [psparam]',
 'psparam.TYPE = [(PTBRANCH ([PTBUILTIN "mixed"]))]',
 '$class_at(S.CLASSES,pmethoddesc.OWNER) = (pclassdesc)',
 'pclassdesc.ORIGIN = ppropertyempty.CLASS /\\ pclassdesc.PARENT = eps',
 '$c_string(pclassdesc.NAME) = $ptascii("class@anonymous")',
 'ptcontext = {NAMESPACE pfunction.ENV.NAMESPACE, IMPORTS pfunction.ENV.CLASSES, SCOPE PTKNOWN pclassdesc.NAME eps, '
 'POSITION PTRETURN, OWNER pclassdesc.NAME, MEMBER pmethoddesc.NAME, FILE $call_sourcefile(S.FILES,pfunction.ORIGIN), '
 'LINE pfunction.LINE}',
 '$property_get_return_type_source(ABSENT,eps,ptcontext,true) /\\ '
 '$property_get_return_type_source(ABSENT,eps,ptcontext,false)',
 '$property_get_method_source(S,pmethoddesc,true) /\\ $property_empty_get_source(S,pmethoddesc)',
 '$property_quiet_get_source(S,pmethoddesc)',
 '~$property_get_method_source(S[.SOURCES = eps],pmethoddesc,true)',
 '~$property_get_method_source(S,pmethoddesc[.FUNCTION = pfunction[.ENDLINE = 99]],true)',
 '$property_empty_valid(S,ppropertyempty) /\\ $call_task_valid(S,PROPERTY_EMPTY_RESULT ppropertyempty true)',
 '~$property_empty_valid(S[.SOURCES = eps],ppropertyempty)',
 '~$property_empty_valid(S,ppropertyempty[.LINE = 9])',
 '$property_magic_cv_source(S,ppropertyempty.SITE,ppropertyempty.LINE)',
 'S_get_result = S',
 'porigin_yes = ppropertyempty.SITE',
 'z_yes = ppropertyempty.LINE',
 '$property_magic_cv_result_supported(S_get_result,porigin_yes,z_yes,true,KNOWN (PBOOL false))',
 '$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,true,KNOWN (PBOOL true))',
 '$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,true,KNOWN (PINT 7))',
 '$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,false,KNOWN (PBOOL false))',
 '~$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,false,KNOWN (PINT 7))',
 '$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,true,KNOWN PNULL)',
 '$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,true,KNOWN (PFLOAT 0))',
 '~$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,true,KNOWN (POBJECT n_receiver))',
 '$property_empty_truth(S,PBOOL false) = (true)',
 '$task_nodes(PROPERTY_EMPTY_RESULT ppropertyempty true) = [HOBJECT n_receiver]',
 '$property_empty_guard(S,n_receiver,ppropertyempty.NAME) /\\ '
 '~$property_empty_get_active(S,n_receiver,ppropertyempty.NAME)',
 '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 2',
 '$lookup(S.ENV,$ptascii("reader")) = (n_reader)',
 '$lookup(S.ENV,$ptascii("selector")) = (n_selector)',
 'S.STORE[n_reader] = DEFINED (POBJECT n_receiver)',
 'S.STORE[n_selector] = DEFINED pvalue_selector',
 '$string_bytes(pvalue_selector) = (eps)',
 'S.EVENTS = [OUTPUT $ptascii("I:"),OUTPUT eps,OUTPUT $ptascii(";"),OUTPUT $ptascii("G:"),OUTPUT eps,OUTPUT '
 '$ptascii(";")]',
 '$call_descriptors_valid(S) /\\ $class_state_valid(S) /\\ $property_state_valid(S) /\\ $heap_valid($heap_graph(S))',
 'PhpStep: S ~> S_truth',
 'S_truth.TODO = ptask_caller* /\\ S_truth.RESULT = KNOWN (PBOOL true) /\\ S_truth.BASE = BASE_VALUE (KNOWN PNULL)',
 'S_truth.STORE = S.STORE /\\ S_truth.EVENTS = S.EVENTS',
 '$heap_owners($heap_graph(S_truth),HOBJECT n_receiver) = 1',
 '~$property_empty_guard(S_truth,n_receiver,ppropertyempty.NAME)',
 'S_zero = $drive_steps(S,0)',
 'S_zero = S[.COMPLETION = BUDGET]',
 'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
 'S_one.COMPLETION = BUDGET /\\ S_one.TODO = S_truth.TODO /\\ S_one.RESULT = S_truth.RESULT',
 '$heap_owners($heap_graph(S_one),HOBJECT n_receiver) = 1',
 'S_done = $drive_steps(S_one[.COMPLETION = NORMAL],4096)',
 'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.HELD = '
 'eps',
 'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("EMPTY;"),OUTPUT $ptascii("I:"),OUTPUT eps,OUTPUT $ptascii(";"),OUTPUT '
 '$ptascii("G:"),OUTPUT eps,OUTPUT $ptascii(";"),OUTPUT $ptascii("FALSE;"),OUTPUT $ptascii("I:"),OUTPUT '
 '$ptascii("yes"),OUTPUT $ptascii(";"),OUTPUT $ptascii("G:"),OUTPUT $ptascii("yes"),OUTPUT $ptascii(";"),OUTPUT '
 '$ptascii("NONEMPTY;"),OUTPUT $ptascii("I:"),OUTPUT $ptascii("yes"),OUTPUT $ptascii(";"),OUTPUT $ptascii("G:"),OUTPUT '
 '$ptascii("yes"),OUTPUT $ptascii(";"),OUTPUT $ptascii("TRUE;"),OUTPUT $ptascii("I:"),OUTPUT $ptascii("skip"),OUTPUT '
 '$ptascii(";"),OUTPUT $ptascii("RHS;"),OUTPUT $ptascii("FALLBACK;"),OUTPUT $ptascii("NAME_KEEP;"),OUTPUT '
 '$ptascii("DONE;")]',
 'S_done.STORE[n_reader] = DEFINED (POBJECT n_receiver)',
 'S_done.STORE[n_selector] = DEFINED pvalue_final',
 '$string_bytes(pvalue_final) = ($ptascii("skip"))',
 '$lookup(S_done.ENV,$ptascii("reader")) = (n_reader)',
 '$heap_owners($heap_graph(S_done),HOBJECT n_receiver) = 1 /\\ (HOBJECT n_receiver) <- S_done.ALLOCATIONS',
 '~$destructor_operational(S_done) /\\ ~$destructor_ready(S_done)',
 'S_done.DESTRUCTION.PHASE = DESTRUCTION_PENDING /\\ S_done.DESTRUCTION.OPERATIONS = eps /\\ S_done.DESTRUCTION.CALLS '
 '= eps',
 '$call_descriptors_valid(S_done) /\\ $class_state_valid(S_done) /\\ $property_state_valid(S_done) /\\ '
 '$heap_valid($heap_graph(S_done))',
 '$drive_steps(S_truth,4096) = S_done',
 '$drive_steps(S,4096) = S_done']

FALSE_ERROR = ['$call_task_valid(S,RETURN_VALUE z_return) /\\ z_return = 9 /\\ S.RESULT = KNOWN (PINT 1)',
 'ppropertycoalesce.PROPERTY = eps /\\ ppropertycoalesce.NAME = $ptascii("gone")',
 'n_receiver = ppropertycoalesce.OBJECT',
 'S.OBJECTS[n_receiver] = INSTANCE ppropertycoalesce.CLASS',
 '(HOBJECT n_receiver) <- S.ALLOCATIONS /\\ ~$instance_storage_freeing(S,n_receiver)',
 '$property_get_method(S,n_receiver) = (pmethoddesc)',
 'pfunction = pmethoddesc.FUNCTION',
 'pfunction.ORIGIN = pcallcontext.FUNCTION /\\ pfunction.ENDLINE = 10',
 'pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "false"]))] /\\ ~pfunction.SIGNATURE.BYREF',
 'pfunction.DEFAULTS = eps /\\ ~pfunction.CODE.STRICT',
 '$class_at(S.CLASSES,pmethoddesc.OWNER) = (pclassdesc)',
 'pclassdesc.PARENT = eps /\\ pclassdesc.ORIGIN = ppropertycoalesce.CLASS',
 '$c_string(pclassdesc.NAME) = $ptascii("class@anonymous")',
 'pfunction.ORIGIN = PORIGIN n_unit pcpath_method',
 '$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_method ++ [PCFIELD 5])) = (NIdentifier (BYTES text_return) '
 'metadata_return)',
 '$ptlc($base64(text_return)) = $ptascii("false")',
 'ptcontext = {NAMESPACE pfunction.ENV.NAMESPACE, IMPORTS pfunction.ENV.CLASSES, SCOPE PTKNOWN pclassdesc.NAME eps, '
 'POSITION PTRETURN, OWNER pclassdesc.NAME, MEMBER pmethoddesc.NAME, FILE $call_sourcefile(S.FILES,pfunction.ORIGIN), '
 'LINE pfunction.LINE}',
 '$ptype_normalize(NIdentifier (BYTES text_return) metadata_return,ptcontext) = PTOK pfunction.SIGNATURE.RETURNS eps',
 '$property_get_return_type_source(NIdentifier (BYTES text_return) '
 'metadata_return,pfunction.SIGNATURE.RETURNS,ptcontext,true)',
 '~$property_get_return_type_source(NIdentifier (BYTES text_return) '
 'metadata_return,pfunction.SIGNATURE.RETURNS,ptcontext,false)',
 '$property_get_method_source(S,pmethoddesc,true) /\\ ~$property_empty_get_source(S,pmethoddesc)',
 '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PINT 1,false,false) = TYPEREJECT',
 '$typed_reference_conversion(S,[(PTBRANCH ([PTBUILTIN "bool"]))],PINT 1,false,false) = TYPEBOOL (PINT 1)',
 '$property_coalesce_method_source(S,pmethoddesc,true) /\\ ~$property_coalesce_method_source(S,pmethoddesc,false)',
 '~$property_coalesce_method_source(S[.SOURCES = eps],pmethoddesc,true)',
 '~$property_coalesce_method_source(S,pmethoddesc[.FUNCTION = pfunction[.ENDLINE = 99]],true)',
 '$return_function_name(S,pfunction) = $ptascii("class@anonymous::__get")',
 '$c_string(pfunction.NAME) = $ptascii("class@anonymous")',
 '$return_function_name(S,pfunction[.ENDLINE = 99]) = pfunction.NAME',
 'pcallcontext_bad = pcallcontext[.FUNCTION = ppropertycoalesce.ISSET]',
 '$return_function_name(S[.CURRENT = (pcallcontext_bad)],pfunction) = pfunction.NAME',
 'pcallcontext_isset = pcallcontext[.TARGET = PROPERTY_COALESCE_TARGET ppropertycoalesce false]',
 '$return_function_name(S[.CURRENT = (pcallcontext_isset)],pfunction) = $call_function_name(S[.CURRENT = '
 '(pcallcontext_isset)],pfunction)',
 'S.FRAMES = [pframe]',
 'pframe.CONTEXT = eps /\\ pframe.ORIGIN = (ppropertycoalesce.SITE)',
 'pframe.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce true) :: ptask_caller*',
 '~$property_isset_guard(S,S.CURRENT,S.FRAMES,n_receiver,ppropertycoalesce.NAME)',
 '$property_coalesce_context(S,pcallcontext)',
 '$property_coalesce_entered(S,S.CURRENT,S.FRAMES,ppropertycoalesce,true)',
 '$property_empty_get_active(S,n_receiver,ppropertycoalesce.NAME)',
 '$task_nodes(PROPERTY_COALESCE_RESULT ppropertycoalesce true) = [HOBJECT n_receiver]',
 '$target_nodes(pcallcontext.TARGET) = eps /\\ $target_instance(pcallcontext.TARGET) = eps /\\ '
 '$call_receiver_roots(pcallcontext) = eps',
 '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 1',
 'S_caller = $constant_frame_scope(S,pframe,eps)',
 '$property_coalesce_valid(S_caller,ppropertycoalesce) /\\ ~$property_coalesce_capture(S_caller,ppropertycoalesce)',
 '~$property_coalesce_valid(S_caller,ppropertycoalesce[.LINE = $(ppropertycoalesce.LINE + 1)])',
 '~$property_coalesce_valid(S_caller[.SOURCES = eps],ppropertycoalesce)',
 '$lookup(S_caller.ENV,$ptascii("reader")) = (n_reader)',
 '$lookup(S_caller.ENV,$ptascii("selector")) = (n_selector)',
 '$lookup(S_caller.ENV,$ptascii("destination")) = (n_destination)',
 'S.STORE[n_reader] = DEFINED PNULL /\\ S.STORE[n_destination] = DEFINED (PINT 42)',
 'S.STORE[n_selector] = DEFINED pvalue_selector',
 '$string_bytes(pvalue_selector) = ($ptascii("gone"))',
 '$property_magic_cv_result_supported(S_caller,ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,KNOWN PNULL)',
 '$property_magic_cv_result_supported(S_caller,ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,KNOWN (PINT 0))',
 '~$property_magic_cv_result_supported(S_caller,ppropertycoalesce.SITE,ppropertycoalesce.LINE,false,KNOWN (PINT 0))',
 'S.EVENTS = [OUTPUT $ptascii("ISSET;"),OUTPUT $ptascii("GET;")]',
 '$call_descriptors_valid(S) /\\ $class_state_valid(S) /\\ $property_state_valid(S) /\\ $heap_valid($heap_graph(S))',
 'S_zero = $drive_steps(S,0)',
 'S_zero = S[.COMPLETION = BUDGET]',
 'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
 'S_one.COMPLETION = BUDGET',
 'S_receiver_found = $bool_review_get_seek_dtor(S_one[.COMPLETION = NORMAL],n_receiver,2000)',
 'S_receiver_found.COMPLETION = NORMAL \\/ S_receiver_found.COMPLETION = BUDGET',
 'S_receiver = S_receiver_found[.COMPLETION = NORMAL]',
 '$bool_review_get_dtor(S_receiver,n_receiver)',
 'S_receiver.CURRENT = (pcallcontext_receiver)',
 '$destructor_context_call(pcallcontext_receiver,S_receiver.CURRENT,S_receiver.FRAMES) = (pdestructorcall_receiver)',
 'pdestructorcall_receiver.OPERATION = (pdestructionoperation_receiver)',
 'pdestructionoperation_receiver.PENDING = (n_type_error)',
 'pdestructionoperation_receiver.SOURCE = THROW_SEARCH n_type_error',
 'pdestructionoperation_receiver.VALUE = KNOWN PNULL',
 'S_receiver.OBJECTS[n_type_error] = THROWABLE pthrowable_type_error',
 'pthrowable_type_error.KIND = "TypeError"',
 '$string_bytes($throwable_field(S_receiver,n_type_error,"message")) = ($ptascii("class@anonymous::__get(): Return '
 'value must be of type false, int returned"))',
 '$throwable_field(S_receiver,n_type_error,"line") = PINT 9',
 '$throwable_field(S_receiver,n_type_error,"previous") = PNULL',
 '~$property_empty_get_active(S_receiver,n_receiver,ppropertycoalesce.NAME)',
 'S_receiver.EVENTS = S.EVENTS',
 '$call_descriptors_valid(S_receiver) /\\ $heap_valid($heap_graph(S_receiver))',
 'S_catch_found = $bool_review_get_seek_catch(S_receiver,2000)',
 'S_catch_found.COMPLETION = NORMAL \\/ S_catch_found.COMPLETION = BUDGET',
 'S_catch = S_catch_found[.COMPLETION = NORMAL]',
 'S_catch.TODO = (CATCH_BIND porigin_try n_catch n_receiver_error) :: ptask_catch*',
 'S_catch.CURRENT = eps /\\ S_catch.FRAMES = eps /\\ S_catch.GLOBALTABLE = eps',
 '$call_task_valid(S_catch,CATCH_BIND porigin_try n_catch n_receiver_error)',
 '$throwable_field(S_catch,n_receiver_error,"previous") = POBJECT n_type_error',
 '$string_bytes($throwable_field(S_catch,n_receiver_error,"message")) = ($ptascii("receiver-false"))',
 'S_catch.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("RECEIVER;")]',
 'PhpStep: S_catch ~> S_bound',
 '$lookup(S_bound.ENV,$ptascii("failure")) = (n_failure)',
 'S_bound.STORE[n_failure] = DEFINED (POBJECT n_receiver_error)',
 '(HOBJECT n_receiver_error) <- S_bound.ALLOCATIONS /\\ (HOBJECT n_type_error) <- S_bound.ALLOCATIONS',
 '~((HOBJECT n_receiver) <- S_bound.ALLOCATIONS)',
 '$call_descriptors_valid(S_bound) /\\ $heap_valid($heap_graph(S_bound))',
 'S_done = $drive_steps(S_bound,4096)',
 'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.HELD = '
 'eps',
 'S_done.DESTRUCTION.PHASE = DESTRUCTION_DONE /\\ S_done.DESTRUCTION.OPERATIONS = eps /\\ S_done.DESTRUCTION.CALLS = '
 'eps',
 'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("RECEIVER;"),OUTPUT $ptascii("receiver-false"),OUTPUT '
 '$ptascii(";"),OUTPUT $ptascii("class@anonymous::__get(): Return value must be of type false, int returned"),OUTPUT '
 '$ptascii(";"),OUTPUT $ptascii("9"),OUTPUT $ptascii(";"),OUTPUT $ptascii("KEEP;"),OUTPUT $ptascii("CLEARED;"),OUTPUT '
 '$ptascii("NAME_KEEP;"),OUTPUT $ptascii("DONE;")]',
 'S_done.STORE[n_reader] = DEFINED PNULL /\\ S_done.STORE[n_destination] = DEFINED (PINT 42)',
 'S_done.STORE[n_selector] = DEFINED pvalue_selector',
 '$lookup(S_done.ENV,$ptascii("failure")) = eps',
 '~((HOBJECT n_receiver_error) <- S_done.ALLOCATIONS) /\\ ~((HOBJECT n_type_error) <- S_done.ALLOCATIONS)',
 '$call_descriptors_valid(S_done) /\\ $class_state_valid(S_done) /\\ $property_state_valid(S_done) /\\ '
 '$heap_valid($heap_graph(S_done))',
 '$drive_steps(S_catch,4096) = S_done',
 '$drive_steps(S_receiver,4096) = S_done',
 '$drive_steps(S_one[.COMPLETION = NORMAL],4096) = S_done',
 '$drive_steps(S,4096) = S_done',
 '~$property_isset_guard(S_receiver,S_receiver.CURRENT,S_receiver.FRAMES,n_receiver,ppropertycoalesce.NAME)']

CASES = {
    'absent-quiet-get-cv-bool-result-and-resume': {'source': ROWS[0]['source'],
        'stage': 'S.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_caller* -- if ppropertyempty.NAME = eps -- if S.RESULT = KNOWN (PBOOL false)', 'checks': LEGACY},
    'weak-false-quiet-get-int-error-pending-cleanup': {'source': ROWS[1]['source'],
        'stage': 'S.CURRENT = (pcallcontext) -- if pcallcontext.TARGET = PROPERTY_COALESCE_TARGET ppropertycoalesce true -- if S.TODO = (RETURN_VALUE z_return) :: ptask_return*', 'checks': FALSE_ERROR},
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
                 (Path(__file__),CATALOGUE),runner_flags=('--sl',),fixture_renderer=render)
