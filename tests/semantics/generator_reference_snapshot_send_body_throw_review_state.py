#!/usr/bin/env python3
"""Check closed VALUE owners and the authentic aborted-Notice cursor front."""
import hashlib
import json
from pathlib import Path
import fiber_state_review as review

ROWS = json.loads(Path(__file__).with_name(
    'generator_reference_snapshot_send_body_throw_review_cases.json').read_bytes())
EXPECTED = {
    'i121-completed-notice-value-cache-send-unwind':
        '18a967dd165f398e9c1108f9968809373e8f304b491bde4bbea75a454990e2db',
    'i121-post-init-throwing-notice-value-cache-send-unwind':
        'fb5d879772915774f718ccf481cea941e3cea4d779405481bf4f4e7064ed9a9c',
}
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
    assert row['source_sha256'] == EXPECTED[row['id']]

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
pfunction_caller.NAME = $ptascii("run121R")
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
pfunction_generator.NAME = $ptascii("flow121R")
pfunction_generator.SIGNATURE.BYREF
$function_generator(S, pfunction_generator)
$ppgenerator_reference_owner($origin_node(S.SOURCES, pfunction_generator.ORIGIN)) = (true)
pgenerator.VALUE = (POBJECT n_cache)
pgenerator.REFCELL = eps
$object_name(S, n_cache) = $ptascii("Cache121R")
$object_name(S, n_argument) = $ptascii("Argument121R")
$generator_reference_producer(S, pgenerator)
$generator_reference_valid(S, GENERATOR pgenerator)
~$generator_api_body_reference(S, pgenerator)
~$generator_storage_active(S, n_target)
$generator_api_body_snapshot(S, n_target)
$node_children(S, HOBJECT n_target) = [HOBJECT n_cache]
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
$lookup(S.ENV, $ptascii("result")) = (n_result_cv)
S.STORE[n_result_cv] = DEFINED pvalue_result
$string_bytes(pvalue_result) = ($ptascii("sentinel"))
$task_nodes(GENERATOR_RESUME pgeneratorop) = [HOBJECT n_target, HOBJECT n_argument]
$heap_owners($heap_graph(S), HOBJECT n_target) = 1
$heap_owners($heap_graph(S), HOBJECT n_cache) = 1
$heap_owners($heap_graph(S), HOBJECT n_argument) = 1
$heap_owners($heap_graph(S), HOBJECT n_body) = 2
$generator_api_body_throw(S, pgeneratorop)
~$generator_api_body_snapshot(S, n_cache)
~$generator_api_body_snapshot(S, n_argument)
~$generator_api_body_snapshot(S, |S.OBJECTS|)
S_no_target = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HOBJECT n_target)]
~$generator_api_body_snapshot(S_no_target, n_target)
~$generator_api_body_throw(S_no_target, pgeneratorop)
S_no_cache = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HOBJECT n_cache)]
~$generator_api_body_snapshot(S_no_cache, n_target)
~$generator_api_body_throw(S_no_cache, pgeneratorop)
S_no_value = S[.OBJECTS[n_target] = GENERATOR pgenerator[.VALUE = eps]]
~$generator_api_body_snapshot(S_no_value, n_target)
~$generator_api_body_throw(S_no_value, pgeneratorop)
~$generator_api_body_snapshot(S[.OBJECTS[n_target] = GENERATOR pgenerator[.REFCELL = (|S.STORE|)]], n_target)
~$generator_api_body_snapshot(S[.OBJECTS[n_target] = GENERATOR pgenerator[.VALUE = (PINT 17)]], n_target)
~$generator_api_body_snapshot(S[.OBJECTS[n_target] = GENERATOR pgenerator[.FUNCTION = pcallcontext.FUNCTION]], n_target)
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
$heap_owners($heap_graph(S_release), HOBJECT n_cache) = 1
$heap_owners($heap_graph(S_release), HOBJECT n_argument) = 1
$heap_owners($heap_graph(S_release), HOBJECT n_body) = 2
$generator_api_body_snapshot(S_release, n_target)
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

NOTICE_STAGE = (
    'S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail* '
    '-- if perrorcall.RESUME = GENERATOR_YIELD_REF_NOTICE n_target porigin eps (POBJECT n_cache) z')
NOTICE_CHECKS = [line.strip() for line in r'''
S.COMPLETION = NORMAL
S.CURRENT = (pcallcontext)
$function_at($all_functions(S), pcallcontext.FUNCTION) = (pfunction_generator)
pfunction_generator.NAME = $ptascii("flow121C")
pfunction_generator.SIGNATURE.BYREF
$ppgenerator_reference_owner($origin_node(S.SOURCES, pfunction_generator.ORIGIN)) = (true)
S.FRAMES = pframe :: pframe_tail*
pframe.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_resumer*
pgeneratorop.NAME = "send"
pgeneratorop.OBJECT = n_target
pgeneratorop.ARGUMENTS = [POBJECT n_argument]
~pgeneratorop.ADVANCE
S.OBJECTS[n_target] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_RUNNING
pgenerator.FUNCTION = pfunction_generator.ORIGIN
pgenerator.FRAME = eps
pgenerator.VALUE = eps
pgenerator.REFCELL = eps
pgenerator.KEY = eps
$generator_borrowed_value(pgenerator) = (REFERENCE n_old)
~((HCELL n_old) <- S.ALLOCATIONS)
~$call_reference_operand_valid(S, REFERENCE n_old)
$node_children(S, HOBJECT n_target) = eps
$object_name(S, n_cache) = $ptascii("Cache121C")
$object_name(S, n_argument) = $ptascii("Argument121C")
perrorcall.SITE = porigin
perrorcall.LEVEL = 8
perrorcall.LINE = z
perrorcall.MESSAGE = $generator_reference_message()
perrorcall.TARGET = eps
$string_bytes(perrorcall.CALLBACK) = ($ptascii("notice121C"))
S.ERRORHANDLER.CALLBACK = (perrorcall.CALLBACK)
$generator_reference_notice_ids(ERROR_HANDLER_INVOKE perrorcall) = [n_target]
$generator_reference_notice_valid(S, n_target, porigin, eps, POBJECT n_cache, z)
$generator_borrowed_scope(S, n_target)
$heap_owners($heap_graph(S), HOBJECT n_target) = 1
$heap_owners($heap_graph(S), HOBJECT n_cache) = 1
$heap_owners($heap_graph(S), HOBJECT n_argument) = 1
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
S_pause = $drive(S, 0)
S_pause.COMPLETION = BUDGET
S_pause[.COMPLETION = NORMAL] = S
PhpStep: S ~> S_cursor
S_cursor.COMPLETION = NORMAL
S_cursor.TODO = (API_CALLBACK_SEND papiargcursor) :: ptask_tail*
papiargcursor.CALL = API_ERROR perrorcall
papiargcursor.SITE = porigin
papiargcursor.LINE = z
papiargcursor.SENT = eps
papiargcursor.INDEX = 0
papiargcursor.VALUES = $error_handler_values(S_cursor, perrorcall)
$target_function(S_cursor, papiargcursor.TARGET) = (pfunction_handler)
pfunction_handler.NAME = $ptascii("notice121C")
papiargcursor.PRODUCER.TARGET = papiargcursor.TARGET
papiargcursor.PRODUCER.SITE = (porigin)
S_cursor.ERRORHANDLER = S.ERRORHANDLER[.CALLBACK = eps]
S_cursor.CURRENT = S.CURRENT
S_cursor.FRAMES = S.FRAMES
S_cursor.OBJECTS = S.OBJECTS
S_cursor.ALLOCATIONS = S.ALLOCATIONS
S_cursor.STORE = S.STORE
S_cursor.EVENTS = S.EVENTS
$task_nodes(API_CALLBACK_SEND papiargcursor) = [HOBJECT n_cache]
$generator_reference_notice_ids(API_CALLBACK_SEND papiargcursor) = [n_target]
$generator_reference_notice_ids(API_CALLBACK_REF papiargcursor) = [n_target]
$generator_reference_notice_valid(S_cursor, n_target, porigin, eps, POBJECT n_cache, z)
$call_task_valid(S_cursor, API_CALLBACK_SEND papiargcursor)
$generator_borrowed_task(S_cursor, n_target, API_CALLBACK_SEND papiargcursor)
$generator_borrowed_scope(S_cursor, n_target)
$generator_reference_valid(S_cursor, GENERATOR pgenerator)
$heap_owners($heap_graph(S_cursor), HCELL n_old) = 0
$heap_owners($heap_graph(S_cursor), HOBJECT n_target) = 1
$heap_owners($heap_graph(S_cursor), HOBJECT n_cache) = 1
$heap_owners($heap_graph(S_cursor), HOBJECT n_argument) = 1
$call_descriptors_valid(S_cursor)
$heap_valid($heap_graph(S_cursor))
~$call_task_valid(S_cursor, API_CALLBACK_REF papiargcursor)
~$generator_borrowed_task(S_cursor, n_target, API_CALLBACK_REF papiargcursor)
papiargcursor_bad = papiargcursor[.INDEX = 1]
S_bad = S_cursor[.TODO = (API_CALLBACK_SEND papiargcursor_bad) :: ptask_tail*]
~$call_task_valid(S_bad, API_CALLBACK_SEND papiargcursor_bad)
~$generator_borrowed_task(S_bad, n_target, API_CALLBACK_SEND papiargcursor_bad)
~$call_descriptors_valid(S_bad)
papiargcursor_site = papiargcursor[.SITE = pfunction_handler.ORIGIN]
S_site = S_cursor[.TODO = (API_CALLBACK_SEND papiargcursor_site) :: ptask_tail*]
~$call_task_valid(S_site, API_CALLBACK_SEND papiargcursor_site)
~$generator_borrowed_task(S_site, n_target, API_CALLBACK_SEND papiargcursor_site)
papiargcursor_empty = papiargcursor[.CALL = API_ERROR perrorcall[.RESUME = DISCARD]]
S_empty = S_cursor[.TODO = (API_CALLBACK_SEND papiargcursor_empty) :: ptask_tail*]
$generator_reference_notice_ids(API_CALLBACK_SEND papiargcursor_empty) = eps
~$call_task_valid(S_empty, API_CALLBACK_SEND papiargcursor_empty)
~$generator_borrowed_task(S_empty, n_target, API_CALLBACK_SEND papiargcursor_empty)
S_duplicate = S_cursor[.TODO = (API_CALLBACK_SEND papiargcursor) :: (API_CALLBACK_SEND papiargcursor) :: ptask_tail*]
$generator_reference_notice_tasks(S_duplicate.TODO) = [n_target, n_target]
~$call_task_valid(S_duplicate, API_CALLBACK_SEND papiargcursor)
~$generator_borrowed_task(S_duplicate, n_target, API_CALLBACK_SEND papiargcursor)
~$call_descriptors_valid(S_duplicate)
S_budget = $drive(S, 1)
S_budget.COMPLETION = BUDGET
S_budget[.COMPLETION = NORMAL] = S_cursor
$drive(S_pause[.COMPLETION = NORMAL], 1) = S_budget
$call_descriptors_valid(S_budget)
$heap_valid($heap_graph(S_budget))
PhpStep: S_cursor ~> S_sent
S_sent.TODO = (API_CALLBACK_SEND papiargcursor_sent) :: ptask_tail*
papiargcursor_sent = papiargcursor[.SENT = [KNOWN (PINT 8)]][.INDEX = 1]
$generator_reference_notice_ids(API_CALLBACK_SEND papiargcursor_sent) = [n_target]
$generator_borrowed_task(S_sent, n_target, API_CALLBACK_SEND papiargcursor_sent)
$heap_owners($heap_graph(S_sent), HOBJECT n_cache) = 1
$call_descriptors_valid(S_sent)
$heap_valid($heap_graph(S_sent))
'''.splitlines() if line.strip()]

review.CASES = {
    ROWS[0]['id']: {'source': ROWS[0]['source'], 'stage': STAGE, 'checks': CHECKS},
    ROWS[1]['id']: {'source': ROWS[1]['source'], 'stage': NOTICE_STAGE,
                    'checks': NOTICE_CHECKS},
}

if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=600) else 1)
