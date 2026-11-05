#!/usr/bin/env python3
"""Check frozen computed SEND authority and body-throw receiver ownership."""
import hashlib
import json
from pathlib import Path
import fiber_state_review as review

ROW = json.loads(Path(__file__).with_name(
    'generator_computed_send_body_throw_review_cases.json').read_bytes())[0]
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']
assert ROW['source_sha256'] == '09097076fce1f3e598cd7046eb146da220f9d287835d40d12c46bb3ccf5d50df'
STAGE = (
    'S.TODO = (THROW_SEARCH n_body) :: (GENERATOR_RESUME pgeneratorop) :: ptask_tail* '
    '-- if pgeneratorop.NAME = "send" '
    '-- if pgeneratorop.ARGUMENTS = [POBJECT n_argument] '
    '-- if S.OBJECTS[pgeneratorop.OBJECT] = GENERATOR pgenerator '
    '-- if pgenerator.PHASE = GENERATOR_CLOSED')
CHECKS = [line.strip() for line in r'''
S.COMPLETION = NORMAL
S.CURRENT = (pcallcontext)
$function_at($all_functions(S), pcallcontext.FUNCTION) = (pfunction_caller)
pfunction_caller.NAME = $ptascii("run118R")
pgeneratorop.OBJECT = n_target
pgeneratorop.SELECTION = (pgeneratormethodselection)
pgeneratormethodselection.SITE = pgeneratorop.SITE
pgeneratormethodselection.OBJECT = n_target
pgeneratormethodselection.LINE = pgeneratorop.LINE
pgeneratormethodselection.NAME = $ptascii("SeNd")
pgeneratormethodselection.CAPTURE = eps
~pgeneratormethodselection.TEMPORARY
pgeneratorop.LOOP = eps
~pgeneratorop.STARTPACK
~pgeneratorop.BORROWED
~pgeneratorop.ADVANCE
pgenerator.FRAME = eps
pgenerator.RETURN = eps
~pgenerator.PENDING_INIT
pgenerator.DELEGATE = eps
$function_at(S.FUNCTIONS, pgenerator.FUNCTION) = (pfunction_generator)
pfunction_generator.NAME = $ptascii("flow118R")
$object_name(S, n_argument) = $ptascii("Argument118R")
S_global = $global_table_view(S)
$lookup(S_global.ENV, $ptascii("target")) = (n_target_cv)
S.STORE[n_target_cv] = DEFINED (POBJECT n_other)
n_other =/= n_target
S.OBJECTS[n_other] = GENERATOR pgenerator_other
pgenerator_other.PHASE = GENERATOR_FRESH
$lookup(S_global.ENV, $ptascii("method")) = (n_method_cv)
S.STORE[n_method_cv] = DEFINED pvalue_method
$string_bytes(pvalue_method) = ($ptascii("throw"))
$lookup(S_global.ENV, $ptascii("replacement")) = (n_replacement_cv)
S.STORE[n_replacement_cv] = DEFINED PNULL
$lookup(S.ENV, $ptascii("result")) = (n_result_cv)
S.STORE[n_result_cv] = DEFINED pvalue_result
$string_bytes(pvalue_result) = ($ptascii("sentinel"))
$lookup(S_global.ENV, $ptascii("bodyStop")) = (n_body_cv)
S.STORE[n_body_cv] = DEFINED (POBJECT n_body)
$lookup(S_global.ENV, $ptascii("weakTarget")) = (n_weak_target_cv)
S.STORE[n_weak_target_cv] = DEFINED (POBJECT n_weak_target)
$weakref_get(S, n_weak_target) = POBJECT n_target
$task_nodes(GENERATOR_RESUME pgeneratorop) = [HOBJECT n_target, HOBJECT n_argument]
$task_nodes(GENERATOR_RESUME pgeneratorop[.SELECTION = eps]) = [HOBJECT n_target, HOBJECT n_argument]
$heap_owners($heap_graph(S), HOBJECT n_target) = 1
$heap_owners($heap_graph(S), HOBJECT n_other) = 1
$heap_owners($heap_graph(S), HOBJECT n_argument) = 1
$heap_owners($heap_graph(S), HOBJECT n_body) = 2
$generator_computed_method_node($origin_node(S.SOURCES, pgeneratorop.SITE))
~$generator_source_method(S, pgeneratorop.SITE, $ptascii("send"))
$generator_operation_site(S, pgeneratorop)
$generator_api_body_throw(S, pgeneratorop)
~$generator_api_body_throw(S, pgeneratorop[.SELECTION = eps])
~$generator_api_body_throw(S, pgeneratorop[.SELECTION = (pgeneratormethodselection[.NAME = $ptascii("throw")])])
~$generator_api_body_throw(S, pgeneratorop[.SELECTION = (pgeneratormethodselection[.OBJECT = n_other])])
~$generator_api_body_throw(S, pgeneratorop[.SELECTION = (pgeneratormethodselection[.SITE = pgenerator.FUNCTION])])
~$generator_api_body_throw(S, pgeneratorop[.SELECTION = (pgeneratormethodselection[.LINE = $(-1)])])
~$generator_api_body_throw(S, pgeneratorop[.SELECTION = (pgeneratormethodselection[.CAPTURE = (n_argument)])])
~$generator_api_body_throw(S, pgeneratorop[.SELECTION = (pgeneratormethodselection[.TEMPORARY = true])])
~$generator_api_body_throw(S, pgeneratorop[.ADVANCE = true])
~$generator_api_body_throw(S[.TODO = ptask_tail*], pgeneratorop)
S_no_target = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HOBJECT n_target)]
~$generator_api_body_throw(S_no_target, pgeneratorop)
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
S_pause = $drive(S, 0)
S_pause.COMPLETION = BUDGET
S_pause[.COMPLETION = NORMAL] = S
PhpStep: S ~> S_release
S_release.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (THROW_SEARCH n_body) :: (GENERATOR_API_RESULT pgeneratorop PNULL) :: ptask_tail*
pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_argument)]
S_release.ORIGIN = (pgeneratorop.SITE)
S_release.RESULT = KNOWN PNULL
S_release.BASE = BASE_VALUE (KNOWN PNULL)
S_release.OBJECTS = S.OBJECTS
S_release.ALLOCATIONS = S.ALLOCATIONS
S_release.STORE = S.STORE
S_release.EVENTS = S.EVENTS
$task_nodes(DESTRUCTOR_RELEASE pdestructionrelease) = [HOBJECT n_argument]
$task_nodes(GENERATOR_API_RESULT pgeneratorop PNULL) = [HOBJECT n_target]
$destructor_tail_pending(S_release.TODO) = (n_body)
$heap_owners($heap_graph(S_release), HOBJECT n_target) = 1
$heap_owners($heap_graph(S_release), HOBJECT n_other) = 1
$heap_owners($heap_graph(S_release), HOBJECT n_argument) = 1
$heap_owners($heap_graph(S_release), HOBJECT n_body) = 2
$call_descriptors_valid(S_release)
$heap_valid($heap_graph(S_release))
S_budget = $drive(S, 1)
S_budget.COMPLETION = BUDGET
S_budget[.COMPLETION = NORMAL] = S_release
$drive(S_pause[.COMPLETION = NORMAL], 1) = S_budget
$call_descriptors_valid(S_budget)
$heap_valid($heap_graph(S_budget))
'''.splitlines() if line.strip()]

review.CASES = {'i118-computed-body-throw-receipt-and-owner-pin': {
    'source': ROW['source'], 'stage': STAGE, 'checks': CHECKS}}

if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=600) else 1)
