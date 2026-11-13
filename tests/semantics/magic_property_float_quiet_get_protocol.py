#!/usr/bin/env python3
"""Check quiet float Get conversion, CV range admission and result lifetime."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol


CATALOGUE = Path(__file__).with_name('magic_property_float_quiet_get_cases.json')
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']

HELPERS = r'''
dec $quiet_float_result(pstate) : bool
def $quiet_float_result(S) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_tail*
  -- if S.RESULT = KNOWN (PFLOAT 0)
def $quiet_float_result(S) = false -- otherwise
dec $quiet_float_seek_result(pstate,nat) : pstate
def $quiet_float_seek_result(S,n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $quiet_float_seek_result(S,n) = S -- if $quiet_float_result(S) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $quiet_float_seek_result(S,0) = S -- if ~$quiet_float_result(S) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $quiet_float_seek_result(S,n) = $quiet_float_seek_result($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$quiet_float_result(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''

CASES = {
    'float-empty-get-weak-conversion-and-resume': {
        'source': ROW['source'],
        'stage': ('S.CURRENT = (pcallcontext) '
                  '-- if pcallcontext.TARGET = PROPERTY_EMPTY_TARGET ppropertyempty true '
                  '-- if S.TODO = (RETURN_VALUE z_return) :: ptask_return* '
                  '-- if S.RESULT = KNOWN pvalue_raw'),
        'checks': [
            'S.ORIGIN = (porigin_return)',
            'z_return = 4',
            'n_receiver = ppropertyempty.OBJECT',
            'ppropertyempty.PROPERTY = eps /\\ ppropertyempty.NAME = $ptascii("zero")',
            'S.OBJECTS[n_receiver] = INSTANCE ppropertyempty.CLASS',
            '(HOBJECT n_receiver) <- S.ALLOCATIONS /\\ ~$instance_storage_freeing(S,n_receiver)',
            '$property_get_method(S,n_receiver) = (pmethoddesc)',
            'pfunction = pmethoddesc.FUNCTION',
            'pfunction.ORIGIN = pcallcontext.FUNCTION /\\ pfunction.ORIGIN = ppropertyempty.GET',
            'pfunction.ENDLINE = 4 /\\ ~pfunction.CODE.STRICT',
            'pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "float"]))] /\\ ~pfunction.SIGNATURE.BYREF',
            '$class_at(S.CLASSES,pmethoddesc.OWNER) = (pclassdesc)',
            'pclassdesc.NAME = $ptascii("QuietFloatRead") /\\ pclassdesc.PARENT = eps',
            'pfunction.ORIGIN = PORIGIN n_unit pcpath_method',
            '$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_method ++ [PCFIELD 5])) = (NIdentifier (BYTES text_return) metadata_return)',
            '$ptlc($base64(text_return)) = $ptascii("float")',
            'ptcontext = {NAMESPACE pfunction.ENV.NAMESPACE, IMPORTS pfunction.ENV.CLASSES, SCOPE PTKNOWN pclassdesc.NAME eps, POSITION PTRETURN, OWNER pclassdesc.NAME, MEMBER pmethoddesc.NAME, FILE $call_sourcefile(S.FILES,pfunction.ORIGIN), LINE pfunction.LINE}',
            '$ptype_normalize(NIdentifier (BYTES text_return) metadata_return,ptcontext) = PTOK pfunction.SIGNATURE.RETURNS eps',
            '$property_get_return_type_source(NIdentifier (BYTES text_return) metadata_return,pfunction.SIGNATURE.RETURNS,ptcontext,true)',
            '~$property_get_return_type_source(NIdentifier (BYTES text_return) metadata_return,pfunction.SIGNATURE.RETURNS,ptcontext,false)',
            '$property_get_method_source(S,pmethoddesc,true) /\\ ~$property_empty_get_source(S,pmethoddesc)',
            '$property_quiet_get_source(S,pmethoddesc)',
            '$property_empty_method_source(S,pmethoddesc,true) /\\ $property_coalesce_method_source(S,pmethoddesc,true)',
            '~$property_empty_method_source(S,pmethoddesc,false)',
            '~$property_quiet_get_source(S[.SOURCES = eps],pmethoddesc)',
            '~$property_quiet_get_source(S,pmethoddesc[.FUNCTION = pfunction[.ENDLINE = 99]])',
            '$return_function_name(S,pfunction) = $ptascii("QuietFloatRead::__get")',
            'S.FRAMES = [pframe]',
            'pframe.CONTEXT = eps /\\ pframe.ORIGIN = (ppropertyempty.SITE)',
            'pframe.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_caller*',
            '$property_empty_context(S,pcallcontext) /\\ $property_empty_entered(S,S.CURRENT,S.FRAMES,ppropertyempty,true)',
            '$property_empty_get_active(S,n_receiver,ppropertyempty.NAME) /\\ $property_empty_guard(S,n_receiver,ppropertyempty.NAME)',
            '$task_nodes(PROPERTY_EMPTY_RESULT ppropertyempty true) = [HOBJECT n_receiver]',
            '$target_nodes(pcallcontext.TARGET) = eps /\\ $target_instance(pcallcontext.TARGET) = eps /\\ $call_receiver_roots(pcallcontext) = eps',
            '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 2',
            'S_caller = $constant_frame_scope(S,pframe,eps)',
            '$property_empty_valid(S_caller,ppropertyempty)',
            '~$property_empty_valid(S_caller,ppropertyempty[.LINE = $(ppropertyempty.LINE + 1)])',
            '$lookup(S_caller.ENV,$ptascii("receiver")) = (n_receiver_cell)',
            '$lookup(S_caller.ENV,$ptascii("selector")) = (n_selector)',
            'S.STORE[n_receiver_cell] = DEFINED (POBJECT n_receiver)',
            'S.STORE[n_selector] = DEFINED pvalue_selector',
            '$string_bytes(pvalue_selector) = ($ptascii("zero"))',
            '$string_bytes(pvalue_raw) = ($ptascii("0.0"))',
            '$typed_return_task_valid(S,z_return) /\\ $call_task_valid(S,RETURN_VALUE z_return)',
            '~$typed_return_task_valid(S,$(z_return + 1))',
            '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,pvalue_raw,false,false) = TYPEVALUE (PFLOAT 0)',
            '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,pvalue_raw,true,false) = TYPEREJECT',
            '$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PINT 0,true,false) = TYPEVALUE (PFLOAT 0)',
            'S.EVENTS = [OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;")]',
            '$call_descriptors_valid(S) /\\ $class_state_valid(S) /\\ $property_state_valid(S) /\\ $heap_valid($heap_graph(S))',
            'S_verified = $typed_return_value(S,z_return)',
            'S_verified.COMPLETION = NORMAL /\\ S_verified.RESULT = KNOWN (PFLOAT 0)',
            'S_verified.STORE = S.STORE /\\ S_verified.EVENTS = S.EVENTS /\\ S_verified.CURRENT = S.CURRENT',
            'PhpStep: S ~> S_unwind',
            'S_unwind.TODO = (RETURN_UNWIND (KNOWN (PFLOAT 0)) (porigin_return)) :: ptask_return*',
            'S_unwind.RESULT = KNOWN PNULL /\\ S_unwind.BASE = BASE_VALUE (KNOWN PNULL)',
            'S_unwind.STORE = S.STORE /\\ S_unwind.EVENTS = S.EVENTS',
            '$heap_owners($heap_graph(S_unwind),HOBJECT n_receiver) = 2',
            '$call_descriptors_valid(S_unwind) /\\ $property_state_valid(S_unwind) /\\ $heap_valid($heap_graph(S_unwind))',
            'S_zero = $drive_steps(S,0)',
            'S_zero = S[.COMPLETION = BUDGET]',
            'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
            'S_one.COMPLETION = BUDGET /\\ S_one.TODO = S_unwind.TODO',
            'S_one.RESULT = S_unwind.RESULT /\\ S_one.BASE = S_unwind.BASE',
            '$heap_owners($heap_graph(S_one),HOBJECT n_receiver) = 2',
            'S_result_found = $quiet_float_seek_result(S_one[.COMPLETION = NORMAL],2000)',
            'S_result_found.COMPLETION = NORMAL \\/ S_result_found.COMPLETION = BUDGET',
            'S_result = S_result_found[.COMPLETION = NORMAL]',
            'S_result.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_result*',
            'S_result.RESULT = KNOWN (PFLOAT 0) /\\ S_result.CURRENT = eps /\\ S_result.FRAMES = eps',
            '$call_task_valid(S_result,PROPERTY_EMPTY_RESULT ppropertyempty true)',
            '$property_magic_cv_source(S_result,ppropertyempty.SITE,ppropertyempty.LINE)',
            '$property_magic_cv_result_supported(S_result,ppropertyempty.SITE,ppropertyempty.LINE,true,KNOWN (PBOOL false))',
            '$property_magic_cv_result_supported(S_result,ppropertyempty.SITE,ppropertyempty.LINE,false,KNOWN (PBOOL false))',
            '$property_magic_cv_result_supported(S_result,ppropertyempty.SITE,ppropertyempty.LINE,true,KNOWN (PINT 7))',
            '~$property_magic_cv_result_supported(S_result,ppropertyempty.SITE,ppropertyempty.LINE,false,KNOWN (PINT 7))',
            '$property_magic_cv_result_supported(S_result,ppropertyempty.SITE,ppropertyempty.LINE,true,KNOWN PNULL)',
            '$property_magic_cv_result_supported(S_result,ppropertyempty.SITE,ppropertyempty.LINE,true,KNOWN (PFLOAT 0))',
            '~$property_magic_cv_result_supported(S_result,ppropertyempty.SITE,ppropertyempty.LINE,false,KNOWN (PFLOAT 0))',
            '~$property_magic_cv_result_supported(S_result,ppropertyempty.SITE,ppropertyempty.LINE,true,KNOWN (PFLOAT 18446744073709551616))',
            '$property_magic_cv_result_supported(S_result,ppropertyempty.SITE,ppropertyempty.LINE,true,KNOWN (POBJECT n_receiver))',
            '$property_empty_guard(S_result,n_receiver,ppropertyempty.NAME)',
            '$heap_owners($heap_graph(S_result),HOBJECT n_receiver) = 2',
            'S_result.EVENTS = S.EVENTS /\\ S_result.STORE[n_selector] = DEFINED pvalue_selector',
            'PhpStep: S_result ~> S_truth',
            'S_truth.TODO = ptask_result* /\\ S_truth.RESULT = KNOWN (PBOOL true)',
            '$heap_owners($heap_graph(S_truth),HOBJECT n_receiver) = 1',
            'S_truth.STORE[n_receiver_cell] = DEFINED (POBJECT n_receiver) /\\ S_truth.EVENTS = S.EVENTS',
            '~$property_empty_guard(S_truth,n_receiver,ppropertyempty.NAME)',
            '$call_descriptors_valid(S_truth) /\\ $property_state_valid(S_truth) /\\ $heap_valid($heap_graph(S_truth))',
            'S_done = $drive_steps(S_truth,4096)',
            'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ S_done.HELD = eps',
            'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("EMPTY;"),OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;"),OUTPUT $ptascii("ZERO;"),OUTPUT $ptascii("I;"),OUTPUT $ptascii("RHS;"),OUTPUT $ptascii("FALL;"),OUTPUT $ptascii("NAME;"),OUTPUT $ptascii("DONE;")]',
            'S_done.STORE[n_selector] = DEFINED pvalue_selector',
            '$lookup(S_done.ENV,$ptascii("receiver")) = (n_receiver_cell)',
            'S_done.STORE[n_receiver_cell] = DEFINED (POBJECT n_receiver)',
            '$heap_owners($heap_graph(S_done),HOBJECT n_receiver) = 1 /\\ (HOBJECT n_receiver) <- S_done.ALLOCATIONS',
            '~$destructor_operational(S_done) /\\ ~$destructor_ready(S_done)',
            'S_done.DESTRUCTION.PHASE = DESTRUCTION_PENDING /\\ S_done.DESTRUCTION.OPERATIONS = eps /\\ S_done.DESTRUCTION.CALLS = eps',
            '~$property_empty_get_active(S_done,n_receiver,ppropertyempty.NAME) /\\ ~$property_empty_guard(S_done,n_receiver,ppropertyempty.NAME)',
            '$call_descriptors_valid(S_done) /\\ $class_state_valid(S_done) /\\ $property_state_valid(S_done) /\\ $heap_valid($heap_graph(S_done))',
            '$drive_steps(S_unwind,4096) = S_done',
            '$drive_steps(S_one[.COMPLETION = NORMAL],4096) = S_done',
            '$drive_steps(S,4096) = S_done',
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
    protocol.run({name: case for name, case in CASES.items()
                  if not args.case or name in args.case}, (Path(__file__), CATALOGUE),
                 runner_flags=('--sl',), fixture_renderer=render)
