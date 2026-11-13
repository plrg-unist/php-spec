#!/usr/bin/env python3
"""Check owning CV Empty results and the distinct literal/CV coalesce paths."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('magic_property_owning_quiet_empty_get_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

EMPTY = [
    r'S.CURRENT = eps /\ S.FRAMES = eps /\ S.HELD = eps',
    r'n_receiver = ppropertyempty.OBJECT',
    r'$property_get_method(S,n_receiver) = (pmethoddesc)',
    r'pfunction = pmethoddesc.FUNCTION',
    r'pfunction.ORIGIN = ppropertyempty.GET /\ ~pfunction.SIGNATURE.BYREF',
    r'pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "array"]))]',
    r'$property_get_method_source(S,pmethoddesc,true) /\ ~$property_empty_get_source(S,pmethoddesc)',
    r'$property_quiet_get_source(S,pmethoddesc) /\ $property_empty_method_source(S,pmethoddesc,true)',
    r'~$property_quiet_get_source(S[.SOURCES = eps],pmethoddesc)',
    r'~$property_quiet_get_source(S,pmethoddesc[.FUNCTION = pfunction[.ENDLINE = 99]])',
    r'$property_empty_valid(S,ppropertyempty) /\ $call_task_valid(S,PROPERTY_EMPTY_RESULT ppropertyempty true)',
    r'$property_magic_cv_source(S,ppropertyempty.SITE,ppropertyempty.LINE)',
    r'$property_magic_cv_empty_source(S,ppropertyempty.SITE,ppropertyempty.LINE)',
    r'~$property_magic_cv_empty_source(S[.SOURCES = eps],ppropertyempty.SITE,ppropertyempty.LINE)',
    r'ppropertyempty.SITE = PORIGIN n_unit pcpath',
    r'pcpath_empty = pcpath[0:$nabs($(|pcpath| - 1))]',
    r'pcpath = pcpath_empty ++ [PCFIELD 0]',
    r'$origin_node(S.SOURCES,ppropertyempty.SITE) = (expression_property)',
    r'$origin_node(S.SOURCES,PORIGIN n_unit pcpath_empty) = (NExprEmpty expression_property metadata_empty)',
    r'S.RESULT = KNOWN (PARRAY n_array)',
    r'$(n_array < |S.ARRAYS|) /\ (HARRAY n_array) <- S.ALLOCATIONS',
    r'$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,true,S.RESULT)',
    r'~$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,false,S.RESULT)',
    r'~$property_magic_cv_result_supported(S[.ALLOCATIONS = eps],ppropertyempty.SITE,ppropertyempty.LINE,true,S.RESULT)',
    r'~$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,true,KNOWN (PARRAY (|S.ARRAYS|)))',
    r'$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,true,KNOWN (POBJECT n_receiver))',
    r'~$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,true,KNOWN (POBJECT (|S.OBJECTS|)))',
    r'~$property_magic_cv_result_supported(S[.OBJECTS[n_receiver] = WEAKMAP eps],ppropertyempty.SITE,ppropertyempty.LINE,true,KNOWN (POBJECT n_receiver))',
    r'~$property_magic_cv_result_supported(S[.OBJECTS[n_receiver] = REALCLOSURE pfunction.ORIGIN eps eps],ppropertyempty.SITE,ppropertyempty.LINE,true,KNOWN (POBJECT n_receiver))',
    r'$lookup(S.ENV,$ptascii("reader")) = (n_reader)',
    r'$lookup(S.ENV,$ptascii("selector")) = (n_selector)',
    r'S.STORE[n_reader] = DEFINED PNULL',
    r'S.STORE[n_selector] = DEFINED pvalue_selector',
    r'$string_bytes(pvalue_selector) = ($ptascii("changed"))',
    r'$task_nodes(PROPERTY_EMPTY_RESULT ppropertyempty true) = [HOBJECT n_receiver]',
    r'$heap_owners($heap_graph(S),HOBJECT n_receiver) = 1',
    r'$property_empty_guard(S,n_receiver,ppropertyempty.NAME)',
    r'~$property_empty_get_active(S,n_receiver,ppropertyempty.NAME)',
    r'S.EVENTS = [OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;")]',
    r'$call_descriptors_valid(S) /\ $class_state_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_graph(S))',
]

IMMUTABLE = EMPTY + [
    r'ppropertyempty.NAME = $ptascii("empty")',
    r'$array_immutable(S,n_array) /\ S.ARRAYS[n_array].ITEMS = eps',
    r'pfunction.ORIGIN = PORIGIN n_unit pcpath_method',
    r'$pool_value(S.POOLS,PORIGIN n_unit (pfunction.BODY ++ [PCINDEX 4,PCFIELD 0])) = (PARRAY n_array)',
    r'$heap_count(HARRAY n_array,$pools_nodes(S.POOLS)) = 1',
    r'$property_empty_truth(S,PARRAY n_array) = (true) /\ ~$property_empty_rv_ready(S,ppropertyempty)',
    r'$heap_owners($heap_graph(S),HARRAY n_array) = 2',
    r'PhpStep: S ~> S_value',
    r'S_value.TODO = ptask_tail* /\ S_value.RESULT = KNOWN (PBOOL true)',
    r'S_value.BASE = BASE_VALUE (KNOWN PNULL) /\ S_value.EVENTS = S.EVENTS /\ S_value.STORE = S.STORE',
    r'$heap_owners($heap_graph(S_value),HARRAY n_array) = 1',
    r'S_zero = $drive_steps(S,0)',
    r'S_zero = S[.COMPLETION = BUDGET]',
    r'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
    r'S_one.COMPLETION = BUDGET',
    r'S_done = $drive_steps(S,4096)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.HELD = eps',
    r'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("R;"),OUTPUT $ptascii("EMPTY;"),OUTPUT $ptascii("CAPTURE;"),OUTPUT $ptascii("DONE;")]',
    r'S_done.STORE[n_reader] = DEFINED PNULL /\ S_done.STORE[n_selector] = DEFINED pvalue_selector',
    r'~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)',
    r'(HARRAY n_array) <- S_done.ALLOCATIONS /\ $heap_owners($heap_graph(S_done),HARRAY n_array) = 1',
    r'$call_descriptors_valid(S_done) /\ $property_state_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
    r'$drive_steps(S_one[.COMPLETION = NORMAL],4096) = S_done',
]

SHARED = EMPTY + [
    r'ppropertyempty.NAME = $ptascii("shared")',
    r'$property_empty_truth(S,PARRAY n_array) = eps /\ $property_empty_rv_ready(S,ppropertyempty)',
    r'S.ARRAYS[n_array].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_payload))]',
    r'$lookup(S.ENV,$ptascii("items")) = (n_items)',
    r'$lookup(S.ENV,$ptascii("held")) = (n_held)',
    r'S.STORE[n_items] = DEFINED PNULL /\ S.STORE[n_held] = DEFINED (PARRAY n_array)',
    r'$heap_owners($heap_graph(S),HARRAY n_array) = 2 /\ $heap_owners($heap_graph(S),HOBJECT n_payload) = 1',
    r'PhpStep: S ~> S_cached',
    r'S_cached.TODO = (PROPERTY_EMPTY_RV ppropertyemptyrv) :: ptask_tail*',
    r'ppropertyemptyrv.EMPTY = ppropertyempty /\ ppropertyemptyrv.TAIL = ptask_tail*',
    r'S_cached.RESULT = KNOWN (PBOOL false) /\ S_cached.EVENTS = S.EVENTS /\ S_cached.STORE = S.STORE',
    r'$property_empty_rv_valid(S_cached,ppropertyemptyrv) /\ $property_empty_rv_guard(S_cached,n_receiver,ppropertyempty.NAME)',
    r'$heap_owners($heap_graph(S_cached),HARRAY n_array) = 1 /\ $heap_owners($heap_graph(S_cached),HOBJECT n_receiver) = 1',
    r'$task_nodes(PROPERTY_EMPTY_RV ppropertyemptyrv) = [HOBJECT n_receiver]',
    r'S_zero = $drive_steps(S,0)',
    r'S_zero = S[.COMPLETION = BUDGET]',
    r'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
    r'S_one.COMPLETION = BUDGET',
    r'S_done = $drive_steps(S,4096)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.HELD = eps',
    r'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("R;"),OUTPUT $ptascii("ARRAY;"),OUTPUT $ptascii("CAPTURE;"),OUTPUT $ptascii("PAYLOAD;"),OUTPUT $ptascii("DONE;")]',
    r'~((HOBJECT n_receiver) <- S_done.ALLOCATIONS) /\ ~((HOBJECT n_payload) <- S_done.ALLOCATIONS) /\ ~((HARRAY n_array) <- S_done.ALLOCATIONS)',
    r'$call_descriptors_valid(S_done) /\ $property_state_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
    r'$drive_steps(S_one[.COMPLETION = NORMAL],4096) = S_done',
]

LITERAL = [
    r'S.CURRENT = eps /\ S.FRAMES = eps /\ S.HELD = eps',
    r'ppropertycoalesce.NAME = $ptascii("object")',
    r'n_receiver = ppropertycoalesce.OBJECT',
    r'S.RESULT = KNOWN (POBJECT n_value)',
    r'$property_get_method(S,n_receiver) = (pmethoddesc)',
    r'pmethoddesc.FUNCTION.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "object"]))]',
    r'$property_quiet_get_source(S,pmethoddesc) /\ $property_coalesce_method_source(S,pmethoddesc,true)',
    r'$property_coalesce_valid(S,ppropertycoalesce)',
    r'~$property_magic_cv_source(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE)',
    r'~$property_magic_cv_empty_source(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE)',
    r'$property_magic_cv_result_supported(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,S.RESULT)',
    r'$value_nodes(POBJECT n_value) = [HOBJECT n_value]',
    r'$task_nodes(PROPERTY_COALESCE_RESULT ppropertycoalesce true) = [HOBJECT n_receiver]',
    r'$heap_owners($heap_graph(S),HOBJECT n_receiver) = 1 /\ $heap_owners($heap_graph(S),HOBJECT n_value) = 1',
    r'$lookup(S.ENV,$ptascii("reader")) = (n_reader)',
    r'S.STORE[n_reader] = DEFINED PNULL',
    r'S.EVENTS = [OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;")]',
    r'PhpStep: S ~> S_value',
    r'S_value.TODO = (ORIGIN_RETURN (porigin_parent)) :: (COALESCE_RESULT expression_right z_left z_right) :: ptask_tail*',
    r'S_value.RESULT = S.RESULT /\ S_value.EVENTS = S.EVENTS /\ S_value.STORE = S.STORE',
    r'$heap_owners($heap_graph(S_value),HOBJECT n_value) = 1 /\ $heap_owners($heap_graph(S_value),HOBJECT n_receiver) = 0',
    r'S_zero = $drive_steps(S,0)',
    r'S_zero = S[.COMPLETION = BUDGET]',
    r'S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)',
    r'S_one.COMPLETION = BUDGET',
    r'S_done = $drive_steps(S,4096)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.HELD = eps',
    r'S_done.EVENTS = S.EVENTS ++ [OUTPUT $ptascii("R;"),OUTPUT $ptascii("OWNED;"),OUTPUT $ptascii("PAYLOAD;"),OUTPUT $ptascii("DONE;")]',
    r'~((HOBJECT n_receiver) <- S_done.ALLOCATIONS) /\ ~((HOBJECT n_value) <- S_done.ALLOCATIONS)',
    r'$call_descriptors_valid(S_done) /\ $property_state_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
    r'$drive_steps(S_one[.COMPLETION = NORMAL],4096) = S_done',
]

COALESCE_CONTROL = [
    r'S.CURRENT = eps /\ S.FRAMES = eps /\ S.HELD = eps',
    r'S.RESULT = KNOWN (POBJECT n_value) /\ S.OBJECTS[n_value] = STDINSTANCE',
    r'$property_coalesce_valid(S,ppropertycoalesce)',
    r'$property_magic_cv_source(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE)',
    r'~$property_magic_cv_empty_source(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE)',
    r'~$property_magic_cv_result_supported(S,ppropertycoalesce.SITE,ppropertycoalesce.LINE,true,S.RESULT)',
    r'$eager_property_class_valid(S,S.OBJECTS[n_value]) /\ (HOBJECT n_value) <- S.ALLOCATIONS',
    r'$heap_owners($heap_graph(S),HOBJECT n_value) = 1',
    r'PhpStep: S ~> S_refused',
    r'S_refused.COMPLETION = UNSUPPORTED "CV-name magic coalesce callback result"',
    r'S_refused.TODO = S.TODO /\ S_refused.RESULT = S.RESULT /\ S_refused.EVENTS = S.EVENTS /\ S_refused.STORE = S.STORE',
    r'S_zero = $drive_steps(S,0)',
    r'S_zero = S[.COMPLETION = BUDGET]',
    r'S_done = $drive_steps(S_zero[.COMPLETION = NORMAL],64)',
    r'S_done.COMPLETION = S_refused.COMPLETION /\ S_done.TODO = eps',
    r'S_done.EVENTS = [OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;")]',
    r'$call_descriptors_valid(S_done) /\ $property_state_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
]

CASES = {
    'immutable-array-cv-empty-direct-truth': {
        'source': ROWS[0]['source'],
        'stage': 'S.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_tail* -- if S.RESULT = KNOWN (PARRAY n_array)',
        'checks': IMMUTABLE,
    },
    'shared-array-cv-empty-cached-truth': {
        'source': ROWS[1]['source'],
        'stage': 'S.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_tail* -- if S.RESULT = KNOWN (PARRAY n_array)',
        'checks': SHARED,
    },
    'literal-object-coalesce-owning-handoff': {
        'source': ROWS[3]['source'],
        'stage': 'S.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce true) :: (ORIGIN_RETURN (porigin_parent)) :: (COALESCE_QUIET expression_right z_left z_right) :: ptask_tail* -- if S.RESULT = KNOWN (POBJECT n_value)',
        'checks': LITERAL,
    },
    'cv-object-coalesce-result-refusal': {
        'source': ROWS[4]['source'],
        'stage': 'S.TODO = (PROPERTY_COALESCE_RESULT ppropertycoalesce true) :: ptask_tail* -- if S.RESULT = KNOWN (POBJECT n_value)',
        'checks': COALESCE_CONTROL,
    },
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE), runner_flags=('--sl',))
