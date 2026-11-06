#!/usr/bin/env python3
"""Check genuine reference-cache authority and SEND body-throw owners."""
import hashlib
import json
from pathlib import Path
import fiber_state_review as review

ROW = json.loads(Path(__file__).with_name(
    'generator_reference_send_body_throw_review_cases.json').read_bytes())[0]
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']
assert ROW['source_sha256'] == '8d3f9c94c83a2843686360c17fa9a73fce4847e123aac44aef47502e36186830'
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
pfunction_caller.NAME = $ptascii("run120R")
pgeneratorop.OBJECT = n_target
pgeneratorop.SELECTION = eps
pgeneratorop.LOOP = eps
~pgeneratorop.STARTPACK
~pgeneratorop.BORROWED
~pgeneratorop.ADVANCE
pgenerator.FRAME = eps
pgenerator.RETURN = eps
~pgenerator.PENDING_INIT
pgenerator.CLOSURE = eps
pgenerator.DELEGATE = eps
pgenerator.ACCESS = eps
pgenerator.CREATION = eps
$function_at(S.FUNCTIONS, pgenerator.FUNCTION) = (pfunction_generator)
pfunction_generator.NAME = $ptascii("flow120R")
pfunction_generator.SIGNATURE.BYREF
$function_generator(S, pfunction_generator)
$ppgenerator_reference_owner($origin_node(S.SOURCES, pfunction_generator.ORIGIN)) = (true)
pgenerator.VALUE = eps
pgenerator.REFCELL = (n_cell)
n_cell <- S.REFCELLS
(HCELL n_cell) <- S.ALLOCATIONS
S.STORE[n_cell] = DEFINED (POBJECT n_cache)
$object_name(S, n_cache) = $ptascii("Cache120R")
$object_name(S, n_argument) = $ptascii("Argument120R")
$generator_reference_producer(S, pgenerator)
$generator_reference_valid(S, GENERATOR pgenerator)
$call_reference_operand_valid(S, REFERENCE n_cell)
$generator_api_body_reference(S, pgenerator)
$node_children(S, HOBJECT n_target) = [HCELL n_cell]
$node_children(S, HCELL n_cell) = [HOBJECT n_cache]
$node_children(S, HOBJECT n_cache) = eps
S_global = $global_table_view(S)
$lookup(S_global.ENV, $ptascii("target")) = (n_target_cv)
S.STORE[n_target_cv] = DEFINED PNULL
$lookup(S_global.ENV, $ptascii("bodyStop")) = (n_body_cv)
S.STORE[n_body_cv] = DEFINED (POBJECT n_body)
$lookup(S_global.ENV, $ptascii("weakTarget")) = (n_weak_target_cv)
S.STORE[n_weak_target_cv] = DEFINED (POBJECT n_weak_target)
$weakref_get(S, n_weak_target) = POBJECT n_target
$lookup(S_global.ENV, $ptascii("weakCache")) = (n_weak_cache_cv)
S.STORE[n_weak_cache_cv] = DEFINED (POBJECT n_weak_cache)
$weakref_get(S, n_weak_cache) = POBJECT n_cache
$task_nodes(GENERATOR_RESUME pgeneratorop) = [HOBJECT n_target, HOBJECT n_argument]
$heap_owners($heap_graph(S), HOBJECT n_target) = 1
$heap_owners($heap_graph(S), HCELL n_cell) = 1
$heap_owners($heap_graph(S), HOBJECT n_cache) = 1
$heap_owners($heap_graph(S), HOBJECT n_argument) = 1
$heap_owners($heap_graph(S), HOBJECT n_body) = 2
$generator_api_body_throw(S, pgeneratorop)
~$generator_api_body_reference(S, pgenerator[.REFCELL = eps])
~$generator_api_body_reference(S, pgenerator[.REFCELL = (|S.STORE|)])
~$generator_api_body_reference(S, pgenerator[.VALUE = (POBJECT n_cache)])
~$generator_api_body_reference(S, pgenerator[.FUNCTION = pcallcontext.FUNCTION])
~$generator_api_body_reference(S[.REFCELLS = eps], pgenerator)
S_no_cell = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HCELL n_cell)]
~$generator_api_body_reference(S_no_cell, pgenerator)
~$generator_api_body_throw(S_no_cell, pgeneratorop)
~$generator_api_body_throw(S[.REFCELLS = eps], pgeneratorop)
~$generator_api_body_reference(S[.STORE[n_cell] = UNDEFINED], pgenerator)
~$generator_api_body_throw(S, pgeneratorop[.ADVANCE = true])
~$generator_api_body_throw(S[.TODO = ptask_tail*], pgeneratorop)
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
$heap_owners($heap_graph(S_release), HCELL n_cell) = 1
$heap_owners($heap_graph(S_release), HOBJECT n_cache) = 1
$heap_owners($heap_graph(S_release), HOBJECT n_argument) = 1
$heap_owners($heap_graph(S_release), HOBJECT n_body) = 2
$generator_api_body_reference(S_release, pgenerator)
$call_task_valid(S_release, GENERATOR_API_RESULT pgeneratorop PNULL)
$call_descriptors_valid(S_release)
$heap_valid($heap_graph(S_release))
S_budget = $drive(S, 1)
S_budget.COMPLETION = BUDGET
S_budget[.COMPLETION = NORMAL] = S_release
$drive(S_pause[.COMPLETION = NORMAL], 1) = S_budget
$call_descriptors_valid(S_budget)
$heap_valid($heap_graph(S_budget))
'''.splitlines() if line.strip()]

review.CASES = {'i120-reference-cache-body-throw-owner-pin': {
    'source': ROW['source'], 'stage': STAGE, 'checks': CHECKS}}

if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=600) else 1)
