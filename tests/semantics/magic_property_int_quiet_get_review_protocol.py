#!/usr/bin/env python3
"""Check typed quiet Get errors while the saved receiver is its last owner."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol


CATALOGUE = Path(__file__).with_name('magic_property_int_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

HELPERS = r'''
dec $quiet_get_dtor(pstate,nat) : bool
def $quiet_get_dtor(S,n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n
def $quiet_get_dtor(S,n) = false -- otherwise
dec $quiet_get_seek_dtor(pstate,nat,nat) : pstate
def $quiet_get_seek_dtor(S,n_object,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $quiet_get_seek_dtor(S,n_object,n) = S
  -- if $quiet_get_dtor(S,n_object)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $quiet_get_seek_dtor(S,n_object,0) = S
  -- if ~$quiet_get_dtor(S,n_object)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $quiet_get_seek_dtor(S,n_object,n) = $quiet_get_seek_dtor($drive_steps(S[.COMPLETION = NORMAL],1),n_object,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$quiet_get_dtor(S,n_object)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
dec $quiet_get_catch(pstate) : bool
def $quiet_get_catch(S) = true
  -- if S.TODO = (CATCH_BIND porigin n_index n_error) :: ptask_tail*
def $quiet_get_catch(S) = false -- otherwise
dec $quiet_get_seek_catch(pstate,nat) : pstate
def $quiet_get_seek_catch(S,n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $quiet_get_seek_catch(S,n) = S
  -- if $quiet_get_catch(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $quiet_get_seek_catch(S,0) = S
  -- if ~$quiet_get_catch(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $quiet_get_seek_catch(S,n) = $quiet_get_seek_catch($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$quiet_get_catch(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def case(mode, row, line, endline, given):
    prefix = 'property_' + mode
    target = 'PROPERTY_' + mode.upper() + '_TARGET pquiet'
    marker = 'PROPERTY_' + mode.upper() + '_RESULT pquiet true'
    message = 'class@anonymous::__get(): Return value must be of type int, ' + given + ' returned'
    receiver_message = 'receiver-' + mode
    stage = ('S.CURRENT = (pcallcontext) -- if pcallcontext.TARGET = ' + target + ' true '
             '-- if S.TODO = ' + ('(TYPE_FALLTHROUGH porigin_get)' if mode == 'coalesce'
                                 else '(RETURN_VALUE z_return)') + ' :: ptask_return*')
    checks = [
        'pquiet.PROPERTY = eps /\\ pquiet.NAME = $ptascii("gone")',
        'n_receiver = pquiet.OBJECT',
        'S.OBJECTS[n_receiver] = INSTANCE pquiet.CLASS',
        '(HOBJECT n_receiver) <- S.ALLOCATIONS /\\ ~$instance_storage_freeing(S,n_receiver)',
        '$property_get_method(S,n_receiver) = (pmethoddesc)',
        'pfunction = pmethoddesc.FUNCTION',
        'pfunction.ORIGIN = pcallcontext.FUNCTION /\\ pfunction.ENDLINE = ' + str(endline),
        'pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "int"]))] /\\ ~pfunction.SIGNATURE.BYREF',
        'pfunction.DEFAULTS = eps /\\ pfunction.CODE.STRICT',
        '$class_at(S.CLASSES,pmethoddesc.OWNER) = (pclassdesc)',
        'pclassdesc.PARENT = eps /\\ pclassdesc.ORIGIN = pquiet.CLASS',
        '$c_string(pclassdesc.NAME) = $ptascii("class@anonymous")',
        'pfunction.ORIGIN = PORIGIN n_unit pcpath_method',
        '$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_method ++ [PCFIELD 5])) = (NIdentifier (BYTES text_return) metadata_return)',
        '$ptlc($base64(text_return)) = $ptascii("int")',
        'ptcontext = {NAMESPACE pfunction.ENV.NAMESPACE, IMPORTS pfunction.ENV.CLASSES, SCOPE PTKNOWN pclassdesc.NAME eps, POSITION PTRETURN, OWNER pclassdesc.NAME, MEMBER pmethoddesc.NAME, FILE $call_sourcefile(S.FILES,pfunction.ORIGIN), LINE pfunction.LINE}',
        '$ptype_normalize(NIdentifier (BYTES text_return) metadata_return,ptcontext) = PTOK pfunction.SIGNATURE.RETURNS eps',
        '$property_get_return_type_source(NIdentifier (BYTES text_return) metadata_return,pfunction.SIGNATURE.RETURNS,ptcontext,true)',
        '~$property_get_return_type_source(NIdentifier (BYTES text_return) metadata_return,pfunction.SIGNATURE.RETURNS,ptcontext,false)',
        '$property_get_method_source(S,pmethoddesc,true) /\\ ~$property_empty_get_source(S,pmethoddesc)',
        '$' + prefix + '_method_source(S,pmethoddesc,true) /\\ ~$' + prefix + '_method_source(S,pmethoddesc,false)',
        '~$' + prefix + '_method_source(S[.SOURCES = eps],pmethoddesc,true)',
        '~$' + prefix + '_method_source(S,pmethoddesc[.FUNCTION = pfunction[.ENDLINE = 99]],true)',
        '$return_function_name(S,pfunction) = $ptascii("class@anonymous::__get")',
        '$c_string(pfunction.NAME) = $ptascii("class@anonymous")',
        '$return_function_name(S,pfunction[.ENDLINE = 99]) = pfunction.NAME',
        'pcallcontext_bad = pcallcontext[.FUNCTION = pquiet.ISSET]',
        '$return_function_name(S[.CURRENT = (pcallcontext_bad)],pfunction) = pfunction.NAME',
        'pcallcontext_isset = pcallcontext[.TARGET = ' + target + ' false]',
        '$return_function_name(S[.CURRENT = (pcallcontext_isset)],pfunction) = $call_function_name(S[.CURRENT = (pcallcontext_isset)],pfunction)',
        'S.FRAMES = [pframe]',
        'pframe.CONTEXT = eps /\\ pframe.ORIGIN = (pquiet.SITE)',
        'pframe.TODO = (' + marker + ') :: ptask_caller*',
        '$' + prefix + '_context(S,pcallcontext)',
        '$' + prefix + '_entered(S,S.CURRENT,S.FRAMES,pquiet,true)',
        '$property_empty_get_active(S,n_receiver,pquiet.NAME)',
        '$task_nodes(' + marker + ') = [HOBJECT n_receiver]',
        '$target_nodes(pcallcontext.TARGET) = eps /\\ $target_instance(pcallcontext.TARGET) = eps /\\ $call_receiver_roots(pcallcontext) = eps',
        '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 1',
        'S_caller = $constant_frame_scope(S,pframe,eps)',
        '$' + prefix + '_valid(S_caller,pquiet) /\\ ~$' + prefix + '_capture(S_caller,pquiet)',
        '~$' + prefix + '_valid(S_caller,pquiet[.LINE = $(pquiet.LINE + 1)])',
        '~$' + prefix + '_valid(S_caller[.SOURCES = eps],pquiet)',
        '$lookup(S_caller.ENV,$ptascii("reader")) = (n_reader)',
        '$lookup(S_caller.ENV,$ptascii("selector")) = (n_selector)',
        '$lookup(S_caller.ENV,$ptascii("destination")) = (n_destination)',
        'S.STORE[n_reader] = DEFINED PNULL /\\ S.STORE[n_destination] = DEFINED (PINT 42)',
        'S.STORE[n_selector] = DEFINED pvalue_selector',
        '$string_bytes(pvalue_selector) = ($ptascii("gone"))',
        '~$property_magic_cv_result_supported(S_caller,pquiet.SITE,pquiet.LINE,true,KNOWN PNULL)',
        '$property_magic_cv_result_supported(S_caller,pquiet.SITE,pquiet.LINE,true,KNOWN (PINT 0))',
        '~$property_magic_cv_result_supported(S_caller,pquiet.SITE,pquiet.LINE,false,KNOWN (PINT 0))',
        'S.EVENTS = [OUTPUT $ptascii("ISSET;"),OUTPUT $ptascii("GET;")]',
        '$call_descriptors_valid(S) /\\ $class_state_valid(S) /\\ $property_state_valid(S) /\\ $heap_valid($heap_graph(S))',
        'S_zero = $drive_steps(S,0)',
        'S_zero = S[.COMPLETION = BUDGET]',
        'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
        'S_one.COMPLETION = BUDGET',
        'S_receiver_found = $quiet_get_seek_dtor(S_one[.COMPLETION = NORMAL],n_receiver,2000)',
        'S_receiver_found.COMPLETION = NORMAL \\/ S_receiver_found.COMPLETION = BUDGET',
        'S_receiver = S_receiver_found[.COMPLETION = NORMAL]',
        '$quiet_get_dtor(S_receiver,n_receiver)',
        'S_receiver.CURRENT = (pcallcontext_receiver)',
        '$destructor_context_call(pcallcontext_receiver,S_receiver.CURRENT,S_receiver.FRAMES) = (pdestructorcall_receiver)',
        'pdestructorcall_receiver.OPERATION = (pdestructionoperation_receiver)',
        'pdestructionoperation_receiver.PENDING = (n_type_error)',
        'pdestructionoperation_receiver.SOURCE = THROW_SEARCH n_type_error',
        'pdestructionoperation_receiver.VALUE = KNOWN PNULL',
        'S_receiver.OBJECTS[n_type_error] = THROWABLE pthrowable_type_error',
        'pthrowable_type_error.KIND = "TypeError"',
        '$string_bytes($throwable_field(S_receiver,n_type_error,"message")) = ($ptascii("' + message + '"))',
        '$throwable_field(S_receiver,n_type_error,"line") = PINT ' + str(line),
        '$throwable_field(S_receiver,n_type_error,"previous") = PNULL',
        '~$property_empty_get_active(S_receiver,n_receiver,pquiet.NAME)',
        'S_receiver.EVENTS = S.EVENTS',
        '$call_descriptors_valid(S_receiver) /\\ $heap_valid($heap_graph(S_receiver))',
        'S_catch_found = $quiet_get_seek_catch(S_receiver,2000)',
        'S_catch_found.COMPLETION = NORMAL \\/ S_catch_found.COMPLETION = BUDGET',
        'S_catch = S_catch_found[.COMPLETION = NORMAL]',
        'S_catch.TODO = (CATCH_BIND porigin_try n_catch n_receiver_error) :: ptask_catch*',
        'S_catch.CURRENT = eps /\\ S_catch.FRAMES = eps /\\ S_catch.GLOBALTABLE = eps',
        '$call_task_valid(S_catch,CATCH_BIND porigin_try n_catch n_receiver_error)',
        '$throwable_field(S_catch,n_receiver_error,"previous") = POBJECT n_type_error',
        '$string_bytes($throwable_field(S_catch,n_receiver_error,"message")) = ($ptascii("' + receiver_message + '"))',
        'S_catch.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("RECEIVER;")]',
        'PhpStep: S_catch ~> S_bound',
        '$lookup(S_bound.ENV,$ptascii("failure")) = (n_failure)',
        'S_bound.STORE[n_failure] = DEFINED (POBJECT n_receiver_error)',
        '(HOBJECT n_receiver_error) <- S_bound.ALLOCATIONS /\\ (HOBJECT n_type_error) <- S_bound.ALLOCATIONS',
        '~((HOBJECT n_receiver) <- S_bound.ALLOCATIONS)',
        '$call_descriptors_valid(S_bound) /\\ $heap_valid($heap_graph(S_bound))',
        'S_done = $drive_steps(S_bound,4096)',
        'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.HELD = eps',
        'S_done.DESTRUCTION.PHASE = DESTRUCTION_DONE /\\ S_done.DESTRUCTION.OPERATIONS = eps /\\ S_done.DESTRUCTION.CALLS = eps',
        'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("RECEIVER;"),OUTPUT $ptascii("' + receiver_message + '"),OUTPUT $ptascii(";"),OUTPUT $ptascii("' + message + '"),OUTPUT $ptascii(";"),OUTPUT $ptascii("' + str(line) + '"),OUTPUT $ptascii(";"),OUTPUT $ptascii("KEEP;"),OUTPUT $ptascii("CLEARED;"),OUTPUT $ptascii("NAME_KEEP;"),OUTPUT $ptascii("DONE;")]',
        'S_done.STORE[n_reader] = DEFINED PNULL /\\ S_done.STORE[n_destination] = DEFINED (PINT 42)',
        'S_done.STORE[n_selector] = DEFINED pvalue_selector',
        '$lookup(S_done.ENV,$ptascii("failure")) = eps',
        '~((HOBJECT n_receiver_error) <- S_done.ALLOCATIONS) /\\ ~((HOBJECT n_type_error) <- S_done.ALLOCATIONS)',
        '$call_descriptors_valid(S_done) /\\ $class_state_valid(S_done) /\\ $property_state_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
        '$drive_steps(S_catch,4096) = S_done',
        '$drive_steps(S_receiver,4096) = S_done',
        '$drive_steps(S_one[.COMPLETION = NORMAL],4096) = S_done',
        '$drive_steps(S,4096) = S_done',
    ]
    if mode == 'empty':
        checks.insert(0, '$call_task_valid(S,RETURN_VALUE z_return) /\\ z_return = 9 /\\ S.RESULT = KNOWN PNULL')
        checks.insert(35, '$property_empty_guard(S,n_receiver,pquiet.NAME)')
        checks.append('~$property_empty_guard(S_receiver,n_receiver,pquiet.NAME)')
    else:
        checks.insert(0, '$call_task_valid(S,TYPE_FALLTHROUGH porigin_get)')
        checks.insert(8, 'porigin_get = pfunction.ORIGIN')
        checks.insert(35, '~$property_isset_guard(S,S.CURRENT,S.FRAMES,n_receiver,pquiet.NAME)')
        checks.append('~$property_isset_guard(S_receiver,S_receiver.CURRENT,S_receiver.FRAMES,n_receiver,pquiet.NAME)')
    record = 'pproperty' + mode
    return {'source': row['source'], 'stage': stage.replace('pquiet', record),
            'checks': [check.replace('pquiet', record) for check in checks]}


CASES = {
    'anonymous-int-empty-return-error-receiver-cleanup': case('empty', ROWS[2], 9, 10, 'null'),
    'anonymous-int-coalesce-fallthrough-error-receiver-cleanup': case('coalesce', ROWS[1], 10, 10, 'none'),
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
    protocol.run({name: case for name, case in CASES.items()
                  if not args.case or name in args.case}, (Path(__file__),CATALOGUE),
                 runner_flags=('--sl',), fixture_renderer=render)
