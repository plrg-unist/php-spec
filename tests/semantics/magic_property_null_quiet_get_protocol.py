#!/usr/bin/env python3
"""Check canonical NULL Get and the private coalesce-assignment handoff."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol


CATALOGUE = Path(__file__).with_name('magic_property_null_quiet_get_cases.json')
ROW = json.loads(CATALOGUE.read_text())['cases'][0]
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']

HELPERS = r'''
dec $quiet_null_stage(pstate,nat) : bool
def $quiet_null_stage(S,0) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_tail*
  -- if S.RESULT = KNOWN PNULL
def $quiet_null_stage(S,1) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce true) :: ptask_tail*
  -- if ppropertycoalesce.PROPERTY = (porigin_property)
  -- if S.RESULT = KNOWN PNULL
def $quiet_null_stage(S,2) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (PROPERTY_COALESCE_ASSIGN_VALUE porigin pbase n pcallcontext?) :: ptask_tail*
def $quiet_null_stage(S,n) = false -- otherwise
dec $quiet_null_seek(pstate,nat,nat) : pstate
def $quiet_null_seek(S,n_stage,n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $quiet_null_seek(S,n_stage,n) = S -- if $quiet_null_stage(S,n_stage) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $quiet_null_seek(S,n_stage,0) = S -- if ~$quiet_null_stage(S,n_stage) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $quiet_null_seek(S,n_stage,n) = $quiet_null_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$quiet_null_stage(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''

CASES = {
    'null-get-canonical-and-private-assignment-handoff': {
        'source': ROW['source'],
        'stage': ('S.CURRENT = (pcallcontext) '
                  '-- if pcallcontext.TARGET = PROPERTY_EMPTY_TARGET ppropertyempty true '
                  '-- if S.TODO = (RETURN_VALUE z_return) :: ptask_return* '
                  '-- if S.RESULT = KNOWN PNULL'),
        'checks': [
            r'S.ORIGIN = (porigin_return)',
            r'z_return = 5',
            r'n_receiver = ppropertyempty.OBJECT',
            r'ppropertyempty.PROPERTY = eps /\ ppropertyempty.NAME = $ptascii("missing")',
            r'$property_get_method(S,n_receiver) = (pmethoddesc)',
            r'pfunction = pmethoddesc.FUNCTION',
            r'pfunction.ORIGIN = pcallcontext.FUNCTION /\ pfunction.ORIGIN = ppropertyempty.GET',
            r'pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "null"]))] /\ ~pfunction.SIGNATURE.BYREF /\ ~pfunction.CODE.STRICT',
            r'$class_at(S.CLASSES,pmethoddesc.OWNER) = (pclassdesc)',
            r'pclassdesc.NAME = $ptascii("QuietNullRead") /\ pclassdesc.PARENT = eps',
            r'pfunction.ORIGIN = PORIGIN n_unit pcpath_method',
            r'$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_method ++ [PCFIELD 5])) = (NIdentifier (BYTES text_return) metadata_return)',
            r'$ptlc($base64(text_return)) = $ptascii("null")',
            r'ptcontext = {NAMESPACE pfunction.ENV.NAMESPACE, IMPORTS pfunction.ENV.CLASSES, SCOPE PTKNOWN pclassdesc.NAME eps, POSITION PTRETURN, OWNER pclassdesc.NAME, MEMBER pmethoddesc.NAME, FILE $call_sourcefile(S.FILES,pfunction.ORIGIN), LINE pfunction.LINE}',
            r'$ptype_normalize(NIdentifier (BYTES text_return) metadata_return,ptcontext) = PTOK pfunction.SIGNATURE.RETURNS eps',
            r'$property_get_return_type_source(NIdentifier (BYTES text_return) metadata_return,pfunction.SIGNATURE.RETURNS,ptcontext,true)',
            r'~$property_get_return_type_source(NIdentifier (BYTES text_return) metadata_return,pfunction.SIGNATURE.RETURNS,ptcontext,false)',
            r'$property_quiet_get_source(S,pmethoddesc) /\ ~$property_empty_get_source(S,pmethoddesc)',
            r'$property_empty_method_source(S,pmethoddesc,true) /\ $property_coalesce_method_source(S,pmethoddesc,true)',
            r'~$property_quiet_get_source(S[.SOURCES = eps],pmethoddesc)',
            r'~$property_quiet_get_source(S,pmethoddesc[.FUNCTION = pfunction[.ENDLINE = 99]])',
            r'$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PNULL,false,false) = TYPEVALUE PNULL',
            r'$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PNULL,true,false) = TYPEVALUE PNULL',
            r'$typed_reference_conversion(S,pfunction.SIGNATURE.RETURNS,PINT 0,false,false) = TYPEREJECT',
            r'$return_function_name(S,pfunction) = $ptascii("QuietNullRead::__get")',
            r'S.FRAMES = [pframe]',
            r'pframe.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_caller*',
            r'$property_empty_context(S,pcallcontext) /\ $property_empty_get_active(S,n_receiver,ppropertyempty.NAME)',
            r'S_caller = $constant_frame_scope(S,pframe,eps)',
            r'$lookup(S_caller.ENV,$ptascii("receiver")) = (n_receiver_cell)',
            r'$lookup(S_caller.ENV,$ptascii("selector")) = (n_selector)',
            r'$lookup(S_caller.ENV,$ptascii("written")) = (n_written)',
            r'S.STORE[n_receiver_cell] = DEFINED (POBJECT n_receiver) /\ S.STORE[n_written] = DEFINED (PINT 42)',
            r'S.STORE[n_selector] = DEFINED pvalue_selector',
            r'$string_bytes(pvalue_selector) = ($ptascii("missing"))',
            r'$heap_owners($heap_graph(S),HOBJECT n_receiver) = 2 /\ $value_nodes(PNULL) = eps',
            r'$typed_return_task_valid(S,z_return) /\ ~$typed_return_task_valid(S,$(z_return + 1))',
            r'S.EVENTS = [OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;")]',
            r'PhpStep: S ~> S_unwind',
            r'S_unwind.TODO = (RETURN_UNWIND (KNOWN PNULL) (porigin_return)) :: ptask_return*',
            r'S_unwind.STORE = S.STORE /\ S_unwind.EVENTS = S.EVENTS',
            r'S_zero = $drive_steps(S,0)',
            r'S_zero = S[.COMPLETION = BUDGET]',
            r'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
            r'S_one.COMPLETION = BUDGET /\ S_one.TODO = S_unwind.TODO /\ S_one.RESULT = S_unwind.RESULT',
            r'S_result_found = $quiet_null_seek(S_one[.COMPLETION = NORMAL],0,2000)',
            r'S_result_found.COMPLETION = NORMAL \/ S_result_found.COMPLETION = BUDGET',
            r'S_result = S_result_found[.COMPLETION = NORMAL]',
            r'S_result.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_result*',
            r'S_result.RESULT = KNOWN PNULL /\ S_result.CURRENT = eps /\ S_result.FRAMES = eps',
            r'$property_magic_cv_source(S_result,ppropertyempty.SITE,ppropertyempty.LINE)',
            r'$property_magic_cv_result_supported(S_result,ppropertyempty.SITE,ppropertyempty.LINE,true,KNOWN PNULL)',
            r'~$property_magic_cv_result_supported(S_result,ppropertyempty.SITE,ppropertyempty.LINE,false,KNOWN PNULL)',
            r'~$property_magic_cv_source(S_result,ppropertyempty.SITE,$(ppropertyempty.LINE + 1))',
            r'~$property_empty_valid(S_result[.SOURCES = eps],ppropertyempty)',
            r'$property_empty_truth(S_result,PNULL) = (true)',
            r'$heap_owners($heap_graph(S_result),HOBJECT n_receiver) = 2 /\ $property_empty_guard(S_result,n_receiver,ppropertyempty.NAME)',
            r'PhpStep: S_result ~> S_truth',
            r'S_truth.TODO = ptask_result* /\ S_truth.RESULT = KNOWN (PBOOL true)',
            r'$heap_owners($heap_graph(S_truth),HOBJECT n_receiver) = 1 /\ ~$property_empty_guard(S_truth,n_receiver,ppropertyempty.NAME)',
            r'S_private_found = $quiet_null_seek(S_result,1,4000)',
            r'S_private_found.COMPLETION = NORMAL \/ S_private_found.COMPLETION = BUDGET',
            r'S_private = S_private_found[.COMPLETION = NORMAL]',
            r'S_private.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce true) :: (ORIGIN_RETURN (porigin_parent)) :: (PROPERTY_COALESCE_ASSIGN_VALUE porigin_parent pbase_pending 0 eps) :: ptask_private*',
            r'ppropertycoalesce.OBJECT = n_receiver /\ ppropertycoalesce.NAME = $ptascii("value")',
            r'ppropertycoalesce.PROPERTY = (porigin_property)',
            r'$property_effective_desc(S_private,n_receiver,ppropertycoalesce.NAME) = (ppropertydesc)',
            r'ppropertydesc.ORIGIN = porigin_property /\ ppropertydesc.VISIBILITY = PROPERTY_PRIVATE',
            r'S_private.RESULT = KNOWN PNULL /\ S_private.STORE[n_written] = DEFINED (PINT 42)',
            r'S_private.STORE[n_receiver_cell] = DEFINED (POBJECT n_receiver) /\ S_private.STORE[n_selector] = DEFINED pvalue_selector',
            r'$property_coalesce_valid(S_private,ppropertycoalesce) /\ $call_task_valid(S_private,PROPERTY_COALESCE_RESULT ppropertycoalesce true)',
            r'~$property_magic_cv_source(S_private,ppropertycoalesce.SITE,ppropertycoalesce.LINE)',
            r'$task_nodes(PROPERTY_COALESCE_RESULT ppropertycoalesce true) = [HOBJECT n_receiver]',
            r'$task_nodes(PROPERTY_COALESCE_ASSIGN_VALUE porigin_parent pbase_pending 0 eps) = eps',
            r'$base_nodes(pbase_pending) = eps /\ $heap_owners($heap_graph(S_private),HOBJECT n_receiver) = 2',
            r'~$property_empty_get_active(S_private,n_receiver,ppropertycoalesce.NAME)',
            r'S_private.EVENTS = [OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;"),OUTPUT $ptascii("EMPTY;"),OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;"),OUTPUT $ptascii("RHS;"),OUTPUT $ptascii("FALL;"),OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;")]',
            r'PhpStep: S_private ~> S_release',
            r'S_release.TODO = (ORIGIN_RETURN (porigin_parent)) :: (PROPERTY_COALESCE_ASSIGN_VALUE porigin_parent pbase_pending 0 eps) :: ptask_private*',
            r'S_release.RESULT = KNOWN PNULL /\ S_release.BASE = BASE_VALUE (KNOWN PNULL)',
            r'$heap_owners($heap_graph(S_release),HOBJECT n_receiver) = 1 /\ S_release.EVENTS = S_private.EVENTS',
            r'S_decide_found = $quiet_null_seek(S_private,2,2000)',
            r'S_decide_found.COMPLETION = NORMAL \/ S_decide_found.COMPLETION = BUDGET',
            r'S_decide = S_decide_found[.COMPLETION = NORMAL]',
            r'S_decide.TODO = (PROPERTY_COALESCE_ASSIGN_VALUE porigin_parent pbase_pending 0 eps) :: ptask_private*',
            r'S_decide.RESULT = KNOWN PNULL /\ S_decide.ORIGIN = (porigin_parent)',
            r'$property_coalesce_assign_value_valid(S_decide,porigin_parent,pbase_pending,0,eps)',
            r'$call_task_valid(S_decide,PROPERTY_COALESCE_ASSIGN_VALUE porigin_parent pbase_pending 0 eps)',
            r'$heap_owners($heap_graph(S_decide),HOBJECT n_receiver) = 1 /\ S_decide.EVENTS = S_private.EVENTS',
            r'S_done = $drive_steps(S_decide,4096)',
            r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.HELD = eps',
            r'S_done.STORE[n_receiver_cell] = DEFINED (POBJECT n_receiver) /\ S_done.STORE[n_written] = DEFINED (PINT 9) /\ S_done.STORE[n_selector] = DEFINED pvalue_selector',
            r'S_done.EVENTS = S_private.EVENTS ++ [OUTPUT $ptascii("RHS;"),OUTPUT $ptascii("S;"),OUTPUT $ptascii("ASSIGN;"),OUTPUT $ptascii("SET;"),OUTPUT $ptascii("I;"),OUTPUT $ptascii("RHS;"),OUTPUT $ptascii("SKIP;"),OUTPUT $ptascii("NAME_KEEP;"),OUTPUT $ptascii("DONE;")]',
            r'$heap_owners($heap_graph(S_done),HOBJECT n_receiver) = 1 /\ (HOBJECT n_receiver) <- S_done.ALLOCATIONS',
            r'S_done.DESTRUCTION.OPERATIONS = eps /\ S_done.DESTRUCTION.CALLS = eps',
            r'$call_descriptors_valid(S_done) /\ $class_state_valid(S_done) /\ $property_state_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
            r'$drive_steps(S_private,4096) = S_done',
            r'$drive_steps(S_one[.COMPLETION = NORMAL],4096) = S_done',
            r'$drive_steps(S,4096) = S_done',
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
