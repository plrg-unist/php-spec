#!/usr/bin/env python3
"""Check direct SEND body-throw argv release and the real receiver pin."""
import hashlib
import json
from pathlib import Path
import fiber_state_review as review

ROW = json.loads(Path(__file__).with_name(
    'generator_send_body_throw_review_cases.json').read_bytes())[0]
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']
assert ROW['source_sha256'] == 'ad8c685514225876aa731929a6a8bc6be8665c8f74cfca781476e4c2eaf30d4a'
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
pfunction_caller.NAME = $ptascii("run117R")
S.ACTIVEFIBER = eps
S.SOURCEPENDING = eps
S.DESTRUCTION.RELEASES = eps
S.DESTRUCTION.CALLS = eps
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
pfunction_generator.NAME = $ptascii("flow117R")
$function_generator(S, pfunction_generator)
$node_children(S, HOBJECT n_target) = eps
$object_name(S, n_argument) = $ptascii("Argument117R")
S_global = $global_table_view(S)
$lookup(S_global.ENV, $ptascii("target")) = (n_target_cv)
S.STORE[n_target_cv] = DEFINED PNULL
$lookup(S_global.ENV, $ptascii("bodyStop")) = (n_body_cv)
S.STORE[n_body_cv] = DEFINED (POBJECT n_body)
$lookup(S_global.ENV, $ptascii("weakTarget")) = (n_weak_target_cv)
S.STORE[n_weak_target_cv] = DEFINED (POBJECT n_weak_target)
$weakref_get(S, n_weak_target) = POBJECT n_target
$lookup(S_global.ENV, $ptascii("weakArgument")) = (n_weak_argument_cv)
S.STORE[n_weak_argument_cv] = DEFINED (POBJECT n_weak_argument)
$weakref_get(S, n_weak_argument) = POBJECT n_argument
$task_nodes(GENERATOR_RESUME pgeneratorop) = [HOBJECT n_target, HOBJECT n_argument]
$task_nodes(THROW_SEARCH n_body) = [HOBJECT n_body]
$heap_owners($heap_graph(S), HOBJECT n_target) = 1
$heap_owners($heap_graph(S), HOBJECT n_argument) = 1
$heap_owners($heap_graph(S), HOBJECT n_body) = 2
$generator_api_body_throw(S, pgeneratorop)
~$generator_api_body_throw(S[.TODO = ptask_tail*], pgeneratorop)
~$generator_api_body_throw(S[.TODO = (THROW_SEARCH n_argument) :: ptask_tail*], pgeneratorop)
~$generator_api_body_throw(S[.COMPLETION = THROWING n_body], pgeneratorop)
~$generator_api_body_throw(S, pgeneratorop[.NAME = "throw"])
~$generator_api_body_throw(S, pgeneratorop[.ADVANCE = true])
~$generator_api_body_throw(S, pgeneratorop[.BORROWED = true])
~$generator_api_body_throw(S, pgeneratorop[.STARTPACK = true])
~$generator_api_body_throw(S, pgeneratorop[.ARGUMENTS = eps])
~$generator_api_body_throw(S[.OBJECTS[n_target] = GENERATOR pgenerator[.PENDING_INIT = true]], pgeneratorop)
S_no_target = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HOBJECT n_target)]
~$generator_api_body_throw(S_no_target, pgeneratorop)
S_no_argument = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HOBJECT n_argument)]
~$generator_api_body_throw(S_no_argument, pgeneratorop)
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
S_pause = $drive(S, 0)
S_pause.COMPLETION = BUDGET
S_pause[.COMPLETION = NORMAL] = S
PhpStep: S ~> S_release
S_release.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (THROW_SEARCH n_body) :: (GENERATOR_API_RESULT pgeneratorop PNULL) :: ptask_tail*
pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_argument)]
S_release.DESTRUCTION.RELEASES = pdestructionrelease :: S.DESTRUCTION.RELEASES
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
$heap_owners($heap_graph(S_release), HOBJECT n_argument) = 1
$heap_owners($heap_graph(S_release), HOBJECT n_body) = 2
$call_task_valid(S_release, DESTRUCTOR_RELEASE pdestructionrelease)
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

review.CASES = {'i117-peer-body-throw-argv-release-pin': {
    'source': ROW['source'], 'stage': STAGE, 'checks': CHECKS}}

if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=600) else 1)
