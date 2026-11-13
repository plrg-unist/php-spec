#!/usr/bin/env python3
"""Check enum-case cache roots through quiet Get value and receiver handoff."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('magic_property_enum_quiet_get_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

COMMON = [
    r'S.CURRENT = eps /\ S.FRAMES = eps /\ S.HELD = eps /\ S.SOURCEPENDING = eps',
    r'S.RESULT = KNOWN (POBJECT n_case)',
    r'S.BASE = BASE_VALUE (KNOWN PNULL)',
    r'n_receiver = ppropertycoalesce.OBJECT',
    r'n_case =/= n_receiver',
    r'$property_get_method(S,n_receiver) = (pmethoddesc)',
    r'pfunction = pmethoddesc.FUNCTION',
    r'ppropertycoalesce.GET = (pfunction.ORIGIN) /\ ~pfunction.SIGNATURE.BYREF',
    r'pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "object"]))]',
    r'$property_get_method_source(S,pmethoddesc,true) /\ $property_quiet_get_source(S,pmethoddesc)',
    r'$property_coalesce_valid(S,ppropertycoalesce) /\ $call_task_valid(S,PROPERTY_COALESCE_RESULT ppropertycoalesce true)',
    r'$property_magic_cv_source(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE)',
    r'~$property_magic_cv_empty_source(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE)',
    r'$property_magic_cv_result_supported(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,S.RESULT)',
    r'~$property_magic_cv_result_supported(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE,false,S.RESULT)',
    r'S.OBJECTS[n_case] = ENUMCASE porigin_case',
    r'(HOBJECT n_case) <- S.ALLOCATIONS',
    r'$enum_case_object(S,n_case) = (pclassconstantdesc)',
    r'pclassconstantdesc.ORIGIN = porigin_case',
    r'$default_cache_at(S.CLASSCONSTANTCACHE,porigin_case) = (pdefaultcache)',
    r'pdefaultcache.VALUE = POBJECT n_case /\ pdefaultcache.CLASS = PVENUMCASE n_case porigin_case',
    r'$constant_value_class_valid(S,POBJECT n_case,PVENUMCASE n_case porigin_case)',
    r'(HOBJECT n_case) <- $class_constant_roots(S.CLASSCONSTANTCACHE)',
    r'$heap_count(HOBJECT n_case,$class_constant_roots(S.CLASSCONSTANTCACHE)) = 1',
    r'$heap_owners($heap_graph(S),HOBJECT n_case) = 2',
    r'~$eager_property_class_valid(S,S.OBJECTS[n_case])',
    r'~$property_magic_cv_result_supported(S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_case)],ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,S.RESULT)',
    r'~$property_magic_cv_result_supported(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,KNOWN (POBJECT (|S.OBJECTS|)))',
    r'S_wrong = S[.OBJECTS[n_case] = ENUMCASE pfunction.ORIGIN]',
    r'$enum_case_object(S_wrong,n_case) = eps',
    r'~$property_magic_cv_result_supported(S_wrong,ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,S_wrong.RESULT)',
    r'S_duplicate = S[.OBJECTS = S.OBJECTS ++ [ENUMCASE porigin_case]][.ALLOCATIONS = S.ALLOCATIONS ++ [HOBJECT (|S.OBJECTS|)]]',
    r'$enum_case_object(S_duplicate,n_case) = eps',
    r'~$property_magic_cv_result_supported(S_duplicate,ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,S_duplicate.RESULT)',
    r'~$property_magic_cv_result_supported(S[.OBJECTS[n_case] = WEAKMAP eps],ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,S.RESULT)',
    r'$lookup(S.ENV,$ptascii("reader")) = (n_reader)',
    r'$lookup(S.ENV,$ptascii("selector")) = (n_selector)',
    r'S.STORE[n_reader] = DEFINED PNULL',
    r'S.STORE[n_selector] = DEFINED pvalue_selector',
    r'$string_bytes(pvalue_selector) = ($ptascii("changed"))',
    r'~$property_magic_name_capture(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE,ppropertycoalesce.NAME)',
    r'$task_nodes(PROPERTY_COALESCE_RESULT ppropertycoalesce true) = [HOBJECT n_receiver]',
    r'$heap_owners($heap_graph(S),HOBJECT n_receiver) = 1',
    r'S.EVENTS = [OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;")]',
    r'$call_descriptors_valid(S) /\ $class_state_valid(S) /\ $property_state_valid(S) /\ $class_constant_state_valid(S) /\ $heap_valid($heap_graph(S))',
    r'PhpStep: S ~> S_value',
    r'S_value.RESULT = S.RESULT /\ S_value.EVENTS = S.EVENTS /\ S_value.STORE = S.STORE',
    r'$heap_owners($heap_graph(S_value),HOBJECT n_receiver) = 0',
    r'$heap_owners($heap_graph(S_value),HOBJECT n_case) = 2',
    r'S_value.CLASSCONSTANTCACHE = S.CLASSCONSTANTCACHE',
    r'S_zero = $drive_steps(S,0)',
    r'S_zero = S[.COMPLETION = BUDGET]',
    r'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
    r'S_one.COMPLETION = BUDGET',
    r'S_one.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: S_value.TODO',
    r'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_receiver)]',
    r'pdestructionoperation.SOURCE = PROPERTY_COALESCE_RESULT ppropertycoalesce true',
    r'pdestructionoperation.VALUE = KNOWN (POBJECT n_case) /\ pdestructionoperation.PENDING = eps',
    r'$heap_owners($heap_graph(S_one),HOBJECT n_case) = 2',
    r'S_one.CLASSCONSTANTCACHE = S.CLASSCONSTANTCACHE /\ S_one.EVENTS = S.EVENTS',
    r'S_done = $drive_steps(S,4096)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.HELD = eps',
    r'S_done.CLASSCONSTANTCACHE = S.CLASSCONSTANTCACHE',
    r'(HOBJECT n_case) <- S_done.ALLOCATIONS /\ ~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
    r'$enum_case_object(S_done,n_case) = (pclassconstantdesc)',
    r'$lookup(S_done.ENV,$ptascii("answer")) = eps',
    r'$call_descriptors_valid(S_done) /\ $property_state_valid(S_done) /\ $class_constant_state_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
    r'$drive_steps(S_one[.COMPLETION = NORMAL],4096) = S_done',
]

BINARY = COMMON + [
    r'ppropertycoalesce.PROPERTY = eps',
    r'$property_magic_cv_coalesce_source(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE)',
    r'~$property_magic_cv_coalesce_assign_source(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE)',
    r'S_value.TODO = (ORIGIN_RETURN (porigin_parent)) :: (COALESCE_RESULT expression_right z_left z_right) :: ptask_tail*',
    r'$enum_backing(S,pclassconstantdesc.OWNER) = ""',
    r'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("RECEIVER;"),OUTPUT $ptascii("SAME;"),OUTPUT $ptascii("CAPTURE;"),OUTPUT $ptascii("DONE;")]',
    r'$heap_owners($heap_graph(S_done),HOBJECT n_case) = 1',
]

ASSIGN = COMMON + [
    r'ppropertycoalesce.PROPERTY = (porigin_property)',
    r'$property_magic_cv_coalesce_assign_source(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE)',
    r'~$property_magic_cv_coalesce_source(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE)',
    r'$property_coalesce_assign_source(S,porigin_parent) /\ $property_coalesce_assign_base(S,porigin_parent,pbase)',
    r'$task_nodes(PROPERTY_COALESCE_ASSIGN_VALUE porigin_parent pbase n_owner pcallcontext_caller?) = eps',
    r'S_value.TODO = (ORIGIN_RETURN (porigin_parent)) :: (PROPERTY_COALESCE_ASSIGN_VALUE porigin_parent pbase n_owner pcallcontext_caller?) :: ptask_tail*',
    r'$enum_backing(S,pclassconstantdesc.OWNER) = "int"',
    r'$lookup(S.ENV,$ptascii("held")) = (n_held)',
    r'S.STORE[n_held] = DEFINED PNULL',
    r'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("RECEIVER;"),OUTPUT $ptascii("SAME;"),OUTPUT $ptascii("CLEARED;"),OUTPUT $ptascii("AFTER_FIRST;"),OUTPUT $ptascii("SAME_AGAIN;"),OUTPUT $ptascii("DONE;")]',
    r'$lookup(S_done.ENV,$ptascii("again")) = (n_again)',
    r'S_done.STORE[n_again] = DEFINED (POBJECT n_case)',
    r'$heap_owners($heap_graph(S_done),HOBJECT n_case) = 2',
]

CASES = {
    'enum-binary-coalesce-cache-and-result-owners': {
        'source': ROWS[0]['source'],
        'stage': 'S.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce true) :: (ORIGIN_RETURN (porigin_parent)) :: (COALESCE_QUIET expression_right z_left z_right) :: ptask_tail*',
        'checks': BINARY,
    },
    'enum-private-coalesce-assignment-cache-and-result-owners': {
        'source': ROWS[1]['source'],
        'stage': 'S.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce true) :: (ORIGIN_RETURN (porigin_parent)) :: (PROPERTY_COALESCE_ASSIGN_VALUE porigin_parent pbase n_owner pcallcontext_caller?) :: ptask_tail*',
        'checks': ASSIGN,
    },
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE), runner_flags=('--sl',))
