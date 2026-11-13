#!/usr/bin/env python3
"""Check enum Empty truth, cache ownership and receiver cleanup from source."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_owning_quiet_empty_get_review_protocol as owning

CATALOGUE = Path(__file__).with_name('magic_property_enum_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

COMMON = r'''
S.CURRENT = eps /\ S.FRAMES = eps /\ S.HELD = eps /\ S.SOURCEPENDING = eps
S.BASE = BASE_VALUE (KNOWN PNULL) /\ S.RESULT = KNOWN (POBJECT n_case)
n_receiver = ppropertyempty.OBJECT
n_receiver =/= n_case
$property_get_method(S,n_receiver) = (pmethoddesc)
pfunction = pmethoddesc.FUNCTION
ppropertyempty.GET = pfunction.ORIGIN /\ ~pfunction.SIGNATURE.BYREF
pfunction.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "object"]))]
$property_get_method_source(S,pmethoddesc,true) /\ $property_quiet_get_source(S,pmethoddesc)
~$property_quiet_get_source(S[.SOURCES = eps],pmethoddesc)
~$property_quiet_get_source(S,pmethoddesc[.FUNCTION = pfunction[.ENDLINE = 99]])
$property_empty_valid(S,ppropertyempty) /\ $call_task_valid(S,PROPERTY_EMPTY_RESULT ppropertyempty true)
$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,true,S.RESULT)
$property_empty_rv_ready(S,ppropertyempty)
~$property_empty_rv_ready(S[.SOURCES = eps],ppropertyempty)
~$property_empty_rv_ready(S,ppropertyempty[.LINE = $(ppropertyempty.LINE + 1)])
S.OBJECTS[n_case] = ENUMCASE porigin_case
(HOBJECT n_case) <- S.ALLOCATIONS
$enum_case_object(S,n_case) = (pclassconstantdesc)
pclassconstantdesc.ORIGIN = porigin_case
$enum_case_descriptor(S,porigin_case) = (pclassconstantdesc)
$class_at(S.CLASSES,pclassconstantdesc.OWNER) = (pclassdesc_enum)
pclassdesc_enum.KIND = "enum" /\ pclassconstantdesc.OWNERNAME = pclassdesc_enum.NAME
$default_cache_at(S.CLASSCONSTANTCACHE,porigin_case) = (pdefaultcache)
pdefaultcache.VALUE = POBJECT n_case /\ pdefaultcache.CLASS = PVENUMCASE n_case porigin_case
$constant_value_class_valid(S,POBJECT n_case,PVENUMCASE n_case porigin_case)
$heap_count(HOBJECT n_case,$class_constant_roots(S.CLASSCONSTANTCACHE)) = 1
$heap_owners($heap_graph(S),HOBJECT n_case) = 2
$heap_owners($heap_graph(S),HOBJECT n_receiver) = 1
$truth(S,POBJECT n_case) /\ $property_empty_truth(S,POBJECT n_case) = eps
~$eager_property_class_valid(S,S.OBJECTS[n_case])
~$property_empty_rv_ready(S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HOBJECT n_case)],ppropertyempty)
~$property_empty_rv_ready(S[.RESULT = KNOWN (POBJECT (|S.OBJECTS|))],ppropertyempty)
S_wrong = S[.OBJECTS[n_case] = ENUMCASE pfunction.ORIGIN]
$enum_case_object(S_wrong,n_case) = eps /\ ~$property_empty_rv_ready(S_wrong,ppropertyempty)
S_duplicate = S[.OBJECTS = S.OBJECTS ++ [ENUMCASE porigin_case]][.ALLOCATIONS = S.ALLOCATIONS ++ [HOBJECT (|S.OBJECTS|)]]
$enum_case_object(S_duplicate,n_case) = eps /\ ~$property_empty_rv_ready(S_duplicate,ppropertyempty)
$lookup(S.ENV,$ptascii("reader")) = (n_reader)
S.STORE[n_reader] = DEFINED PNULL
ppropertyempty.NAME = $ptascii("value")
$property_empty_guard(S,n_receiver,ppropertyempty.NAME) /\ ~$property_empty_get_active(S,n_receiver,ppropertyempty.NAME)
$task_nodes(PROPERTY_EMPTY_RESULT ppropertyempty true) = [HOBJECT n_receiver]
S.EVENTS = [OUTPUT $ptascii("I;"),OUTPUT $ptascii("G;")]
$call_descriptors_valid(S) /\ $property_state_valid(S) /\ $class_constant_state_valid(S) /\ $heap_valid($heap_graph(S))
PhpStep: S ~> S_cached_raw
S_cached_raw.TODO = (PROPERTY_EMPTY_RV ppropertyemptyrv) :: ptask_tail*
ppropertyemptyrv.EMPTY = ppropertyempty /\ ppropertyemptyrv.OWNER = 0 /\ ppropertyemptyrv.CALLER = eps /\ ppropertyemptyrv.TAIL = ptask_tail*
S_cached_raw.RESULT = KNOWN (PBOOL false) /\ S_cached_raw.BASE = BASE_VALUE (KNOWN PNULL)
S_cached_raw.EVENTS = S.EVENTS /\ S_cached_raw.STORE = S.STORE /\ S_cached_raw.CLASSCONSTANTCACHE = S.CLASSCONSTANTCACHE
$task_nodes(PROPERTY_EMPTY_RV ppropertyemptyrv) = [HOBJECT n_receiver]
$heap_owners($heap_graph(S_cached_raw),HOBJECT n_case) = 1 /\ $heap_owners($heap_graph(S_cached_raw),HOBJECT n_receiver) = 1
(HOBJECT n_case) <- S_cached_raw.ALLOCATIONS /\ $enum_case_object(S_cached_raw,n_case) = (pclassconstantdesc)
$property_empty_rv_valid(S_cached_raw,ppropertyemptyrv) /\ $property_empty_guard(S_cached_raw,n_receiver,ppropertyempty.NAME)
~$property_empty_rv_valid(S_cached_raw,ppropertyemptyrv[.OWNER = 1])
~$property_empty_rv_valid(S_cached_raw,ppropertyemptyrv[.EMPTY = ppropertyempty[.NAME = $ptascii("wrong")]])
S_zero = $drive_steps(S,0)
S_zero = S[.COMPLETION = BUDGET]
S_one = $drive_steps(S_zero[.COMPLETION = NORMAL],1)
S_one.COMPLETION = BUDGET /\ S_one[.COMPLETION = NORMAL] = $owning_review_after(S,S_cached_raw)
S_receiver_found = $owning_review_seek(S_one[.COMPLETION = NORMAL],OW_DTOR n_receiver,2000)
S_receiver_found.COMPLETION = NORMAL \/ S_receiver_found.COMPLETION = BUDGET
S_receiver = S_receiver_found[.COMPLETION = NORMAL]
S_receiver.CURRENT = (pcallcontext_receiver)
$destructor_context_call(pcallcontext_receiver,S_receiver.CURRENT,S_receiver.FRAMES) = (pdestructorcall_receiver)
pdestructorcall_receiver.OPERATION = (pdestructionoperation_receiver)
pdestructionoperation_receiver.SOURCE = PROPERTY_EMPTY_RV ppropertyemptyrv
pdestructionoperation_receiver.VALUE = KNOWN (PBOOL false) /\ pdestructionoperation_receiver.PENDING = eps
~$property_empty_guard(S_receiver,n_receiver,ppropertyempty.NAME)
S_receiver.EVENTS = S.EVENTS /\ S_receiver.CLASSCONSTANTCACHE = S.CLASSCONSTANTCACHE
(HOBJECT n_case) <- S_receiver.ALLOCATIONS /\ $heap_owners($heap_graph(S_receiver),HOBJECT n_case) = 1
$enum_case_object(S_receiver,n_case) = (pclassconstantdesc)
S_done = $drive_steps(S,4096)
S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.HELD = eps
S_done.CLASSCONSTANTCACHE = S.CLASSCONSTANTCACHE
(HOBJECT n_case) <- S_done.ALLOCATIONS /\ ~((HOBJECT n_receiver) <- S_done.ALLOCATIONS)
$heap_owners($heap_graph(S_done),HOBJECT n_case) = 1
$enum_case_object(S_done,n_case) = (pclassconstantdesc)
$lookup(S_done.ENV,$ptascii("again")) = eps
$call_descriptors_valid(S_done) /\ $property_state_valid(S_done) /\ $class_constant_state_valid(S_done) /\ $heap_valid($heap_graph(S_done))
$drive_steps(S_one[.COMPLETION = NORMAL],4096) = S_done
$drive_steps(S_receiver,4096) = S_done
'''.strip().splitlines()

CV = COMMON + r'''
$enum_backing(S,pclassconstantdesc.OWNER) = "string"
$property_magic_cv_source(S,ppropertyempty.SITE,ppropertyempty.LINE)
$property_magic_cv_empty_source(S,ppropertyempty.SITE,ppropertyempty.LINE)
~$property_magic_cv_coalesce_source(S,ppropertyempty.SITE,ppropertyempty.LINE)
~$property_magic_cv_coalesce_assign_source(S,ppropertyempty.SITE,ppropertyempty.LINE)
~$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,false,S.RESULT)
~$property_magic_cv_result_supported(S_wrong,ppropertyempty.SITE,ppropertyempty.LINE,true,S_wrong.RESULT)
~$property_magic_cv_result_supported(S_duplicate,ppropertyempty.SITE,ppropertyempty.LINE,true,S_duplicate.RESULT)
~$property_magic_cv_result_supported(S[.OBJECTS[n_case] = WEAKMAPENTRIES eps],ppropertyempty.SITE,ppropertyempty.LINE,true,S.RESULT)
$lookup(S.ENV,$ptascii("selector")) = (n_selector)
S.STORE[n_selector] = DEFINED pvalue_selector
$string_bytes(pvalue_selector) = ($ptascii("changed"))
~$property_magic_name_capture(S,ppropertyempty.SITE,ppropertyempty.LINE,ppropertyempty.NAME)
$lookup(S_done.ENV,$ptascii("answer")) = (n_answer)
S_done.STORE[n_answer] = DEFINED (PBOOL false)
S_done.STORE[n_reader] = DEFINED PNULL /\ S_done.STORE[n_selector] = DEFINED pvalue_selector
$owning_review_output(S_done.EVENTS) = $ptascii("I;G;RECEIVER;FALSE;CAPTURE;SAME;DONE;")
'''.strip().splitlines()

LITERAL = COMMON + r'''
$enum_backing(S,pclassconstantdesc.OWNER) = ""
~$property_magic_cv_source(S,ppropertyempty.SITE,ppropertyempty.LINE)
$lookup(S.ENV,$ptascii("held")) = (n_held)
S.STORE[n_held] = DEFINED PNULL
$lookup(S.ENV,$ptascii("destination")) = (n_destination)
S.STORE[n_destination] = DEFINED (PINT 42)
S_catch_found = $owning_review_seek(S_receiver,OW_CATCH,2000)
S_catch_found.COMPLETION = NORMAL \/ S_catch_found.COMPLETION = BUDGET
S_catch = S_catch_found[.COMPLETION = NORMAL]
S_catch.TODO = (CATCH_BIND porigin_try n_index n_error) :: ptask_catch*
$call_task_valid(S_catch,CATCH_BIND porigin_try n_index n_error)
$throwable_live(S_catch,n_error) /\ $throwable_field(S_catch,n_error,"previous") = PNULL
$string_bytes($throwable_field(S_catch,n_error,"message")) = ($ptascii("receiver"))
$throwable_field(S_catch,n_error,"line") = PINT 7
S_catch.STORE[n_destination] = DEFINED (PINT 42)
(HOBJECT n_case) <- S_catch.ALLOCATIONS /\ $heap_owners($heap_graph(S_catch),HOBJECT n_case) = 1
S_catch.CLASSCONSTANTCACHE = S.CLASSCONSTANTCACHE
$owning_review_output(S_catch.EVENTS) = $ptascii("I;G;RECEIVER;")
PhpStep: S_catch ~> S_bound_raw
S_bound = $owning_review_after(S_catch,S_bound_raw)
$lookup(S_bound.ENV,$ptascii("failure")) = (n_failure)
S_bound.STORE[n_failure] = DEFINED (POBJECT n_error)
(HOBJECT n_error) <- S_bound.ALLOCATIONS
S_done.STORE[n_destination] = DEFINED (PINT 42) /\ S_done.STORE[n_reader] = DEFINED PNULL /\ S_done.STORE[n_held] = DEFINED PNULL
$lookup(S_done.ENV,$ptascii("failure")) = eps
$owning_review_output(S_done.EVENTS) = $ptascii("I;G;RECEIVER;CAUGHT;KEEP;CLEARED;SAME;DONE;")
$drive_steps(S_catch,4096) = S_done
$drive_steps(S_bound,4096) = S_done
'''.strip().splitlines()

STAGE = ('S.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_tail* '
         '-- if S.RESULT = KNOWN (POBJECT n_case)')
CASES = {
    'enum-cv-empty-truth-and-permanent-cache-owner': {
        'source': ROWS[0]['source'], 'stage': STAGE, 'checks': CV,
    },
    'enum-literal-empty-cache-survives-receiver-throw': {
        'source': ROWS[1]['source'], 'stage': STAGE, 'checks': LITERAL,
    },
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, Path(owning.__file__), owning.CATALOGUE),
                 runner_flags=('--sl',), fixture_renderer=owning.render)
