#!/usr/bin/env python3
"""Check private CV coalesce-assignment owning results and cleanup."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('magic_property_owning_quiet_coalesce_assignment_get_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

HELPERS = r'''
dec $coalesce_get_after_cow(pstate) : bool
def $coalesce_get_after_cow(S) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.EVENTS = [OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;"),OUTPUT $ptascii("RECEIVER;"),OUTPUT $ptascii("COW;")]
def $coalesce_get_after_cow(S) = false -- otherwise
dec $coalesce_get_seek_cow(pstate,nat) : pstate
def $coalesce_get_seek_cow(S,n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $coalesce_get_seek_cow(S,n) = S -- if $coalesce_get_after_cow(S) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $coalesce_get_seek_cow(S,0) = S -- if ~$coalesce_get_after_cow(S) -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $coalesce_get_seek_cow(S,n) = $coalesce_get_seek_cow($drive_steps(S[.COMPLETION = NORMAL],1),$nabs($(n - 1)))
  -- if $(n > 0) /\ ~$coalesce_get_after_cow(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''

COMMON = [
    r'S.CURRENT = eps /\ S.FRAMES = eps /\ S.HELD = eps /\ S.SOURCEPENDING = eps',
    r'S.BASE = BASE_VALUE (KNOWN PNULL)',
    r'n_receiver = ppropertycoalesce.OBJECT',
    r'$property_get_method(S,n_receiver) = (pmethoddesc)',
    r'pfunction = pmethoddesc.FUNCTION',
    r'ppropertycoalesce.GET = (pfunction.ORIGIN) /\ ~pfunction.SIGNATURE.BYREF',
    r'$property_get_method_source(S,pmethoddesc,true) /\ $property_quiet_get_source(S,pmethoddesc)',
    r'$property_coalesce_valid(S,ppropertycoalesce) /\ $call_task_valid(S,PROPERTY_COALESCE_RESULT ppropertycoalesce true)',
    r'$property_magic_cv_source(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE)',
    r'$property_magic_cv_coalesce_assign_source(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE)',
    r'~$property_magic_cv_coalesce_source(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE)',
    r'~$property_magic_cv_empty_source(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE)',
    r'~$property_magic_cv_coalesce_assign_source(S[.SOURCES = eps],ppropertycoalesce.SITE,ppropertycoalesce.LINE)',
    r'~$property_magic_cv_coalesce_assign_source(S,ppropertycoalesce.SITE,$(ppropertycoalesce.LINE + 1))',
    r'$property_hook_coalesce_parent(S,ppropertycoalesce.SITE) = eps',
    r'$property_coalesce_assign_source(S,porigin_parent) /\ $property_coalesce_assign_base(S,porigin_parent,pbase)',
    r'ppropertycoalesce.PROPERTY = (porigin_property)',
    r'~$property_coalesce_descriptor(S,ppropertycoalesce[.PROPERTY = eps])',
    r'$task_nodes(PROPERTY_COALESCE_ASSIGN_VALUE porigin_parent pbase n_owner pcallcontext_caller?) = eps',
    r'$origin_node(S.SOURCES,ppropertycoalesce.SITE) = (expression_left)',
    r'$origin_node(S.SOURCES,porigin_parent) = (NExprAssignOpCoalesce expression_left expression_right metadata_parent)',
    r'porigin_parent = PORIGIN n_unit pcpath_parent',
    r'S.SOURCES = [pcunit]',
    r'S_swapped = S[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_parent (NExprAssignOpCoalesce expression_right expression_left metadata_parent)) :: pcunit.OCCURRENCES]]]',
    r'$property_magic_cv_source(S_swapped,ppropertycoalesce.SITE,ppropertycoalesce.LINE)',
    r'~$property_magic_cv_coalesce_assign_source(S_swapped,ppropertycoalesce.SITE,ppropertycoalesce.LINE)',
    r'~$property_magic_cv_result_supported(S_swapped,ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,S.RESULT)',
    r'S_literal_rhs = S[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_parent (NExprAssignOpCoalesce expression_left (NScalarInt (INTEGER 9) metadata_parent) metadata_parent)) :: pcunit.OCCURRENCES]]]',
    r'$property_magic_cv_source(S_literal_rhs,ppropertycoalesce.SITE,ppropertycoalesce.LINE)',
    r'~$property_magic_cv_coalesce_assign_source(S_literal_rhs,ppropertycoalesce.SITE,ppropertycoalesce.LINE)',
    r'~$property_magic_cv_result_supported(S_literal_rhs,ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,S.RESULT)',
    r'$property_magic_cv_result_supported(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,S.RESULT)',
    r'~$property_magic_cv_result_supported(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE,false,S.RESULT)',
    r'S.RESULT = KNOWN (PARRAY n_array)',
    r'$(n_array < |S.ARRAYS|) /\ (HARRAY n_array) <- S.ALLOCATIONS',
    r'~$property_magic_cv_result_supported(S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HARRAY n_array)],ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,S.RESULT)',
    r'~$property_magic_cv_result_supported(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,KNOWN (PARRAY (|S.ARRAYS|)))',
    r'$property_magic_cv_result_supported(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,KNOWN (POBJECT n_receiver))',
    r'~$property_magic_cv_result_supported(S[.OBJECTS[n_receiver] = WEAKMAPENTRIES eps],ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,KNOWN (POBJECT n_receiver))',
    r'~$property_magic_cv_result_supported(S[.OBJECTS[n_receiver] = REALCLOSURE pfunction.ORIGIN eps eps],ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,KNOWN (POBJECT n_receiver))',
    r'$lookup(S.ENV,$ptascii("reader")) = (n_reader)',
    r'$lookup(S.ENV,$ptascii("selector")) = (n_selector)',
    r'S.STORE[n_reader] = DEFINED PNULL',
    r'S.STORE[n_selector] = DEFINED pvalue_selector',
    r'$task_nodes(PROPERTY_COALESCE_RESULT ppropertycoalesce true) = [HOBJECT n_receiver]',
    r'$heap_owners($heap_graph(S),HOBJECT n_receiver) = 1',
    r'~$property_empty_get_active(S,n_receiver,ppropertycoalesce.NAME) /\ ~$property_empty_guard(S,n_receiver,ppropertycoalesce.NAME)',
    r'S.EVENTS = [OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;")]',
    r'$call_descriptors_valid(S) /\ $class_state_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_graph(S))',
]

IMMUTABLE = COMMON + [
    r'ppropertycoalesce.NAME = $ptascii("value")',
    r'pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "array"]))]',
    r'$string_bytes(pvalue_selector) = ($ptascii("changed"))',
    r'~$property_magic_name_capture(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE,ppropertycoalesce.NAME)',
    r'$array_immutable(S,n_array) /\ S.ARRAYS[n_array].ITEMS = eps',
    r'pfunction.ORIGIN = PORIGIN n_unit pcpath_method',
    r'$pool_value(S.POOLS,PORIGIN n_unit (pfunction.BODY ++ [PCINDEX 4,PCFIELD 0])) = (PARRAY n_array)',
    r'n_pool = $heap_count(HARRAY n_array,$pools_nodes(S.POOLS))',
    r'$(n_pool > 0) /\ $heap_owners($heap_graph(S),HARRAY n_array) = $(n_pool + 1)',
    r'PhpStep: S ~> S_value',
    r'S_value.TODO = (ORIGIN_RETURN (porigin_parent)) :: (PROPERTY_COALESCE_ASSIGN_VALUE porigin_parent pbase n_owner pcallcontext_caller?) :: ptask_tail*',
    r'S_value.RESULT = S.RESULT /\ S_value.BASE = BASE_VALUE (KNOWN PNULL)',
    r'S_value.STORE = S.STORE /\ S_value.EVENTS = S.EVENTS',
    r'$heap_owners($heap_graph(S_value),HOBJECT n_receiver) = 0 /\ $heap_owners($heap_graph(S_value),HARRAY n_array) = $(n_pool + 1)',
    r'S_zero = $drive_steps(S,0)',
    r'S_zero = S[.COMPLETION = BUDGET]',
    r'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
    r'S_one.COMPLETION = BUDGET',
    r'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: S_value.TODO',
    r'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_receiver)]',
    r'pdestructionoperation.SOURCE = PROPERTY_COALESCE_RESULT ppropertycoalesce true',
    r'pdestructionoperation.VALUE = KNOWN (PARRAY n_array) /\ pdestructionoperation.PENDING = eps',
    r'$heap_owners($heap_graph(S_one),HARRAY n_array) = $(n_pool + 1) /\ S_one.EVENTS = S.EVENTS',
    r'S_done = $drive_steps(S,4096)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.HELD = eps',
    r'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("RECEIVER;"),OUTPUT $ptascii("EMPTY_ARRAY;"),OUTPUT $ptascii("CAPTURE;"),OUTPUT $ptascii("I;"),OUTPUT $ptascii("RHS;"),OUTPUT $ptascii("SET;"),OUTPUT $ptascii("FALLBACK;"),OUTPUT $ptascii("RECEIVER;"),OUTPUT $ptascii("DONE;")]',
    r'$lookup(S_done.ENV,$ptascii("answer")) = (n_answer)',
    r'S_done.STORE[n_answer] = DEFINED (PINT 9) /\ S_done.STORE[n_reader] = DEFINED PNULL',
    r'$heap_owners($heap_graph(S_done),HARRAY n_array) = n_pool /\ ~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
    r'$call_descriptors_valid(S_done) /\ $property_state_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
    r'$drive_steps(S_one[.COMPLETION = NORMAL],4096) = S_done',
]

COW = COMMON + [
    r'ppropertycoalesce.NAME = $ptascii("value")',
    r'pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "mixed"]))]',
    r'$string_bytes(pvalue_selector) = ($ptascii("changed"))',
    r'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7)),ENTRY (KINT 1) (DIRECT (POBJECT n_payload))]',
    r'$lookup(S.ENV,$ptascii("held")) = (n_held)',
    r'$lookup(S.ENV,$ptascii("items")) = (n_items)',
    r'S.STORE[n_held] = DEFINED (PARRAY n_array) /\ S.STORE[n_items] = DEFINED PNULL',
    r'$heap_owners($heap_graph(S),HARRAY n_array) = 2 /\ $heap_owners($heap_graph(S),HOBJECT n_payload) = 1',
    r'PhpStep: S ~> S_value',
    r'S_value.TODO = (ORIGIN_RETURN (porigin_parent)) :: (PROPERTY_COALESCE_ASSIGN_VALUE porigin_parent pbase n_owner pcallcontext_caller?) :: ptask_tail*',
    r'S_value.RESULT = S.RESULT /\ S_value.EVENTS = S.EVENTS /\ S_value.STORE = S.STORE',
    r'$heap_owners($heap_graph(S_value),HARRAY n_array) = 2 /\ $heap_owners($heap_graph(S_value),HOBJECT n_receiver) = 0',
    r'S_copy_found = $coalesce_get_seek_cow(S,2000)',
    r'S_copy_found.COMPLETION = NORMAL \/ S_copy_found.COMPLETION = BUDGET',
    r'S_copy = S_copy_found[.COMPLETION = NORMAL]',
    r'$coalesce_get_after_cow(S_copy)',
    r'$lookup(S_copy.ENV,$ptascii("answer")) = (n_answer)',
    r'S_copy.STORE[n_answer] = DEFINED (PARRAY n_copy)',
    r'S_copy.STORE[n_held] = DEFINED (PARRAY n_array)',
    r'n_copy =/= n_array',
    r'S_copy.ARRAYS[n_copy].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 99)),ENTRY (KINT 1) (DIRECT (POBJECT n_payload))]',
    r'S_copy.ARRAYS[n_array].ITEMS = S.ARRAYS[n_array].ITEMS',
    r'$heap_owners($heap_graph(S_copy),HARRAY n_array) = 1 /\ $heap_owners($heap_graph(S_copy),HARRAY n_copy) = 1 /\ $heap_owners($heap_graph(S_copy),HOBJECT n_payload) = 2',
    r'~((HOBJECT n_receiver) <- S_copy.ALLOCATIONS)',
    r'$call_descriptors_valid(S_copy) /\ $property_state_valid(S_copy) /\ $heap_valid($heap_graph(S_copy))',
    r'S_zero = $drive_steps(S,0)',
    r'S_zero = S[.COMPLETION = BUDGET]',
    r'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
    r'S_one.COMPLETION = BUDGET',
    r'S_done = $drive_steps(S_copy,4096)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.HELD = eps',
    r'S_done.EVENTS = S_copy.EVENTS ++ [OUTPUT $ptascii("AFTER_FIRST;"),OUTPUT $ptascii("PAYLOAD;"),OUTPUT $ptascii("DONE;")]',
    r'~((HOBJECT n_payload) <- S_done.ALLOCATIONS) /\ ~((HARRAY n_array) <- S_done.ALLOCATIONS) /\ ~((HARRAY n_copy) <- S_done.ALLOCATIONS)',
    r'$call_descriptors_valid(S_done) /\ $property_state_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
    r'$drive_steps(S,4096) = S_done /\ $drive_steps(S_one[.COMPLETION = NORMAL],4096) = S_done',
]

ASSIGN_STAGE = ('S.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce true) :: '
                '(ORIGIN_RETURN (porigin_parent)) :: (PROPERTY_COALESCE_ASSIGN_VALUE porigin_parent pbase n_owner pcallcontext_caller?) :: ptask_tail* '
                '-- if S.RESULT = KNOWN (PARRAY n_array)')
CASES = {
    'immutable-array-cv-coalesce-assignment-retained-value': {'source': ROWS[1]['source'], 'stage': ASSIGN_STAGE, 'checks': IMMUTABLE},
    'mixed-array-cv-coalesce-assignment-cow-and-payload-retirement': {'source': ROWS[2]['source'], 'stage': ASSIGN_STAGE, 'checks': COW},
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
    text += ''.join('  -- ' + ('' if check.startswith('PhpStep:') else 'if ') + check + '\n' for check in case['checks'])
    return text, len(case['checks']) + 6

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE), fixture_renderer=render, runner_flags=('--sl',))
