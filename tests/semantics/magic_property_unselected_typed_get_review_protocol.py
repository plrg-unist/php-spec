#!/usr/bin/env python3
"""Check terminal Isset never calls its typed Get companion during cleanup."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol


CATALOGUE = Path(__file__).with_name('magic_property_unselected_typed_get_review_cases.json')
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']

HELPERS = r'''
dec $unselected_get_dtor(pstate,nat) : bool
def $unselected_get_dtor(S,n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n
def $unselected_get_dtor(S,n) = false -- otherwise
dec $unselected_get_seek_dtor(pstate,nat,nat) : pstate
def $unselected_get_seek_dtor(S,n_object,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $unselected_get_seek_dtor(S,n_object,n) = S
  -- if $unselected_get_dtor(S,n_object)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $unselected_get_seek_dtor(S,n_object,0) = S
  -- if ~$unselected_get_dtor(S,n_object)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $unselected_get_seek_dtor(S,n_object,n) = $unselected_get_seek_dtor($drive_steps(S[.COMPLETION = NORMAL],1),n_object,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$unselected_get_dtor(S,n_object)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $unselected_get_catch(pstate) : bool
def $unselected_get_catch(S) = true
  -- if S.TODO = (CATCH_BIND porigin n_index n_error) :: ptask_tail*
def $unselected_get_catch(S) = false -- otherwise
dec $unselected_get_seek_catch(pstate,nat) : pstate
def $unselected_get_seek_catch(S,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $unselected_get_seek_catch(S,n) = S
  -- if $unselected_get_catch(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $unselected_get_seek_catch(S,0) = S
  -- if ~$unselected_get_catch(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $unselected_get_seek_catch(S,n) = $unselected_get_seek_catch($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$unselected_get_catch(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET

dec $unselected_get_result(pstate) : bool
def $unselected_get_result(S) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask_tail*
  -- if ppropertyisset.NAME = $ptascii("drop")
  -- if S.RESULT = KNOWN (PBOOL true)
def $unselected_get_result(S) = false -- otherwise
dec $unselected_get_seek_result(pstate,nat) : pstate
def $unselected_get_seek_result(S,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $unselected_get_seek_result(S,n) = S
  -- if $unselected_get_result(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $unselected_get_seek_result(S,0) = S
  -- if ~$unselected_get_result(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $unselected_get_seek_result(S,n) = $unselected_get_seek_result($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$unselected_get_result(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''

CHECKS = ['$call_task_valid(S,RETURN_VALUE z_return) /\\ S.RESULT = KNOWN (PBOOL true)',
 'ppropertyisset.PROPERTY = eps /\\ ppropertyisset.NAME = $ptascii("drop")',
 'n_receiver = ppropertyisset.OBJECT',
 'S.OBJECTS[n_receiver] = INSTANCE ppropertyisset.CLASS',
 '(HOBJECT n_receiver) <- S.ALLOCATIONS /\\ ~$instance_storage_freeing(S,n_receiver)',
 '$property_isset_method(S,n_receiver) = (pmethoddesc_isset)',
 '$property_get_method(S,n_receiver) = (pmethoddesc_get)',
 'pmethoddesc_get.OWNER = pmethoddesc_isset.OWNER',
 'pfunction_get = pmethoddesc_get.FUNCTION',
 'pfunction_get.ENDLINE = 9 /\\ pfunction_get.ORIGIN =/= pcallcontext.FUNCTION',
 'pfunction_get.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "never"]))] /\\ ~pfunction_get.SIGNATURE.BYREF',
 '$class_at(S.CLASSES,pmethoddesc_get.OWNER) = (pclassdesc)',
 'pclassdesc.PARENT = eps /\\ pclassdesc.ORIGIN = ppropertyisset.CLASS',
 '$c_string(pclassdesc.NAME) = $ptascii("class@anonymous")',
 'pfunction_get.ORIGIN = PORIGIN n_unit pcpath_get',
 '$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_get ++ [PCFIELD 5])) = (NIdentifier (BYTES text_return) '
 'metadata_return)',
 '$ptlc($base64(text_return)) = $ptascii("never")',
 'ptcontext = {NAMESPACE pfunction_get.ENV.NAMESPACE, IMPORTS pfunction_get.ENV.CLASSES, SCOPE PTKNOWN pclassdesc.NAME '
 'eps, POSITION PTRETURN, OWNER pclassdesc.NAME, MEMBER pmethoddesc_get.NAME, FILE '
 '$call_sourcefile(S.FILES,pfunction_get.ORIGIN), LINE pfunction_get.LINE}',
 '$ptype_normalize(NIdentifier (BYTES text_return) metadata_return,ptcontext) = PTOK pfunction_get.SIGNATURE.RETURNS '
 'eps',
 '$property_get_return_type_source(NIdentifier (BYTES text_return) '
 'metadata_return,pfunction_get.SIGNATURE.RETURNS,ptcontext,true)',
 '~$property_get_return_type_source(NIdentifier (BYTES text_return) '
 'metadata_return,pfunction_get.SIGNATURE.RETURNS,ptcontext,false)',
 '$property_get_method_source(S,pmethoddesc_get,true) /\\ ~$property_empty_get_source(S,pmethoddesc_get)',
 '$property_quiet_get_source(S,pmethoddesc_get)',
 '$property_empty_method_source(S,pmethoddesc_get,true) /\\ $property_coalesce_method_source(S,pmethoddesc_get,true)',
 '~$property_get_method_source(S[.SOURCES = eps],pmethoddesc_get,true)',
 '~$property_get_method_source(S,pmethoddesc_get[.FUNCTION = pfunction_get[.ENDLINE = 99]],true)',
 '$target_function(S,METHOD_TARGET n_receiver pfunction_get.ORIGIN) = (pfunction_get)',
 '$property_isset_function(S,ppropertyisset) = (pmethoddesc_isset.FUNCTION)',
 'pcallcontext.FUNCTION = pmethoddesc_isset.FUNCTION.ORIGIN',
 'S.FRAMES = [pframe]',
 'pframe.CONTEXT = eps /\\ pframe.ORIGIN = (ppropertyisset.SITE)',
 'pframe.TODO = (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask_caller*',
 '$property_isset_source(S,ppropertyisset) /\\ ~$property_isset_empty(S,ppropertyisset)',
 '$property_magic_cv_source(S,ppropertyisset.SITE,ppropertyisset.LINE)',
 '$property_isset_missing_source(S,ppropertyisset)',
 '$property_isset_bool_pair(S,ppropertyisset) /\\ ~$property_isset_untyped(S,ppropertyisset)',
 '$property_isset_frame(S,pcallcontext,pframe,ppropertyisset)',
 '$property_isset_context(S,pcallcontext) /\\ $property_isset_entered(S,S.CURRENT,S.FRAMES,ppropertyisset)',
 '$property_isset_guard(S,S.CURRENT,S.FRAMES,n_receiver,ppropertyisset.NAME)',
 '~$property_empty_get_active(S,n_receiver,ppropertyisset.NAME)',
 '~$property_get_guard_tasks(S.TODO,n_receiver,ppropertyisset.NAME) /\\ '
 '~$property_get_guard_frames(S.FRAMES,n_receiver,ppropertyisset.NAME)',
 '$task_nodes(PROPERTY_ISSET_RESULT ppropertyisset) = [HOBJECT n_receiver]',
 '$target_nodes(pcallcontext.TARGET) = eps /\\ $target_instance(pcallcontext.TARGET) = eps /\\ '
 '$call_receiver_roots(pcallcontext) = eps',
 '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 1',
 'S_caller = $constant_frame_scope(S,pframe,eps)',
 '$property_isset_valid(S_caller,ppropertyisset) /\\ ~$property_isset_capture(S_caller,ppropertyisset)',
 '~$property_isset_bool_pair(S_caller[.SOURCES = eps],ppropertyisset)',
 '~$property_isset_valid(S_caller,ppropertyisset[.LINE = $(ppropertyisset.LINE + 1)])',
 '~$property_isset_valid(S_caller,ppropertyisset[.METHOD = pfunction_get.ORIGIN])',
 '~$property_isset_valid(S_caller,ppropertyisset[.OBJECT = (|S.OBJECTS|)])',
 '$property_effective_desc(S,n_receiver,ppropertyisset.NAME) = eps',
 '$lookup(S_caller.ENV,$ptascii("reader")) = (n_reader)',
 '$lookup(S_caller.ENV,$ptascii("selector")) = (n_selector)',
 '$lookup(S_caller.ENV,$ptascii("destination")) = (n_destination)',
 'S.STORE[n_reader] = DEFINED PNULL /\\ S.STORE[n_destination] = DEFINED (PINT 42)',
 'S.STORE[n_selector] = DEFINED pvalue_selector',
 '$string_bytes(pvalue_selector) = ($ptascii("drop"))',
 'S.EVENTS = [OUTPUT $ptascii("I:"),OUTPUT $ptascii("yes"),OUTPUT $ptascii(";"),OUTPUT $ptascii("YES;"),OUTPUT '
 '$ptascii("I:"),OUTPUT eps,OUTPUT $ptascii(";"),OUTPUT $ptascii("NO;"),OUTPUT $ptascii("I:"),OUTPUT '
 '$ptascii("drop"),OUTPUT $ptascii(";")]',
 '$call_descriptors_valid(S) /\\ $class_state_valid(S) /\\ $property_state_valid(S) /\\ $heap_valid($heap_graph(S))',
 'S_zero = $drive_steps(S,0)',
 'S_zero = S[.COMPLETION = BUDGET]',
 'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
 'S_one.COMPLETION = BUDGET',
 'S_result_found = $unselected_get_seek_result(S_one[.COMPLETION = NORMAL],2000)',
 'S_result_found.COMPLETION = NORMAL \\/ S_result_found.COMPLETION = BUDGET',
 'S_result = S_result_found[.COMPLETION = NORMAL]',
 'S_result.TODO = (PROPERTY_ISSET_RESULT ppropertyisset) :: ptask_result*',
 'S_result.RESULT = KNOWN (PBOOL true) /\\ S_result.CURRENT = eps /\\ S_result.FRAMES = eps',
 '$call_task_valid(S_result,PROPERTY_ISSET_RESULT ppropertyisset)',
 '~$property_isset_guard(S_result,S_result.CURRENT,S_result.FRAMES,n_receiver,ppropertyisset.NAME)',
 '$heap_owners($heap_graph(S_result),HOBJECT n_receiver) = 1',
 'S_result.EVENTS = S.EVENTS /\\ S_result.STORE[n_destination] = DEFINED (PINT 42)',
 'PhpStep: S_result ~> S_value',
 'S_value.TODO = ptask_result* /\\ S_value.RESULT = KNOWN (PBOOL true)',
 '$heap_owners($heap_graph(S_value),HOBJECT n_receiver) = 0',
 'S_value.EVENTS = S.EVENTS /\\ S_value.STORE[n_destination] = DEFINED (PINT 42)',
 'S_result_zero = $drive_steps(S_result,0)',
 'S_result_zero = S_result[.COMPLETION = BUDGET]',
 'S_result_one = $drive_steps(S_result_zero[.COMPLETION = NORMAL],1)',
 'S_result_one.COMPLETION = BUDGET',
 'S_receiver_found = $unselected_get_seek_dtor(S_result_one[.COMPLETION = NORMAL],n_receiver,2000)',
 'S_receiver_found.COMPLETION = NORMAL \\/ S_receiver_found.COMPLETION = BUDGET',
 'S_receiver = S_receiver_found[.COMPLETION = NORMAL]',
 '$unselected_get_dtor(S_receiver,n_receiver)',
 'S_receiver.CURRENT = (pcallcontext_receiver)',
 '$destructor_context_call(pcallcontext_receiver,S_receiver.CURRENT,S_receiver.FRAMES) = (pdestructorcall_receiver)',
 'pdestructorcall_receiver.OPERATION = (pdestructionoperation_receiver)',
 'pdestructionoperation_receiver.SOURCE = PROPERTY_ISSET_RESULT ppropertyisset',
 'pdestructionoperation_receiver.PENDING = eps /\\ pdestructionoperation_receiver.VALUE = KNOWN (PBOOL true)',
 '~$property_isset_guard(S_receiver,S_receiver.CURRENT,S_receiver.FRAMES,n_receiver,ppropertyisset.NAME)',
 '~$property_empty_get_active(S_receiver,n_receiver,ppropertyisset.NAME)',
 'S_receiver.EVENTS = S.EVENTS',
 '$call_descriptors_valid(S_receiver) /\\ $heap_valid($heap_graph(S_receiver))',
 'S_catch_found = $unselected_get_seek_catch(S_receiver,2000)',
 'S_catch_found.COMPLETION = NORMAL \\/ S_catch_found.COMPLETION = BUDGET',
 'S_catch = S_catch_found[.COMPLETION = NORMAL]',
 'S_catch.TODO = (CATCH_BIND porigin_try n_catch n_error) :: ptask_catch*',
 'S_catch.CURRENT = eps /\\ S_catch.FRAMES = eps /\\ S_catch.GLOBALTABLE = eps',
 '$call_task_valid(S_catch,CATCH_BIND porigin_try n_catch n_error)',
 '$string_bytes($throwable_field(S_catch,n_error,"message")) = ($ptascii("terminal-isset"))',
 '$throwable_field(S_catch,n_error,"previous") = PNULL',
 'S_catch.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("RECEIVER;")]',
 'PhpStep: S_catch ~> S_bound',
 '$lookup(S_bound.ENV,$ptascii("failure")) = (n_failure)',
 'S_bound.STORE[n_failure] = DEFINED (POBJECT n_error)',
 '(HOBJECT n_error) <- S_bound.ALLOCATIONS /\\ ~((HOBJECT n_receiver) <- S_bound.ALLOCATIONS)',
 '$call_descriptors_valid(S_bound) /\\ $heap_valid($heap_graph(S_bound))',
 'S_done = $drive_steps(S_bound,4096)',
 'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.HELD = '
 'eps',
 'S_done.DESTRUCTION.PHASE = DESTRUCTION_DONE /\\ S_done.DESTRUCTION.OPERATIONS = eps /\\ S_done.DESTRUCTION.CALLS = '
 'eps',
 'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("RECEIVER;"),OUTPUT $ptascii("terminal-isset"),OUTPUT '
 '$ptascii(";"),OUTPUT $ptascii("NO_PREVIOUS;"),OUTPUT $ptascii("KEEP;"),OUTPUT $ptascii("CLEARED;"),OUTPUT '
 '$ptascii("NAME_KEEP;"),OUTPUT $ptascii("DONE;")]',
 'S_done.STORE[n_reader] = DEFINED PNULL /\\ S_done.STORE[n_destination] = DEFINED (PINT 42)',
 'S_done.STORE[n_selector] = DEFINED pvalue_selector',
 '$lookup(S_done.ENV,$ptascii("failure")) = eps /\\ ~((HOBJECT n_error) <- S_done.ALLOCATIONS)',
 '$call_descriptors_valid(S_done) /\\ $class_state_valid(S_done) /\\ $property_state_valid(S_done) /\\ '
 '$heap_valid($heap_graph(S_done))',
 '$drive_steps(S_catch,4096) = S_done',
 '$drive_steps(S_receiver,4096) = S_done',
 '$drive_steps(S_result_one[.COMPLETION = NORMAL],4096) = S_done',
 '$drive_steps(S_result,4096) = S_done',
 '$drive_steps(S,4096) = S_done']

CASES = {'anonymous-never-get-companion-normal-result-receiver-throw': {
    'source': ROW['source'],
    'stage': 'S.CURRENT = (pcallcontext) -- if pcallcontext.TARGET = PROPERTY_ISSET_TARGET ppropertyisset -- if ppropertyisset.NAME = $ptascii("drop") -- if S.TODO = (RETURN_VALUE z_return) :: ptask_return* -- if S.RESULT = KNOWN (PBOOL true)',
    'checks': CHECKS,
}}


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
    protocol.run(CASES,(Path(__file__),CATALOGUE),runner_flags=('--sl',),
                 fixture_renderer=render)
