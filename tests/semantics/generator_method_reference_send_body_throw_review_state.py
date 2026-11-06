#!/usr/bin/env python3
"""Check real method reference caches, This and pending SEND ownership."""
import hashlib
import json
from pathlib import Path
import fiber_state_review as review

ROWS = json.loads(Path(__file__).with_name(
    'generator_method_reference_send_body_throw_review_cases.json').read_bytes())
EXPECTED = [
    'b4aaf07152778810e5250aa6d9fefa4ae5094a43f1a700f9273687a7d2a1a651',
    '097bc76a9d0e18de91d3d11e9c743baef52270065f72b7fc2f0f2b89547256db',
]
assert [row['source_sha256'] for row in ROWS] == EXPECTED
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def checks(text, suffix):
    return [line.strip().replace('@X@', suffix)
            for line in text.splitlines() if line.strip()]


INITIAL = r'''
S.COMPLETION = NORMAL
S.CURRENT = (pcallcontext_caller)
S.TODO = (GENERATOR_RESUME pgeneratorop_current) :: ptask_current*
n_target = pgeneratorop_current.OBJECT
pgeneratorop_current.NAME = "current"
pgeneratorop_current.ARGUMENTS = eps
S.OBJECTS[n_target] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_PAUSED
pgenerator.VALUE = eps
pgenerator.REFCELL = (n_cell)
pgenerator.CLOSURE = eps
pgenerator.CREATION = eps
pgenerator.ACCESS = eps
pgenerator.DELEGATE = eps
pgenerator.FRAME = (pframe_generator)
pframe_generator.CONTEXT = (pcallcontext_generator)
pframe_generator.LOCALS = (psymboltable_generator)
pcallcontext_generator.INSTANCE = eps
pcallcontext_generator.FUNCTION = pgenerator.FUNCTION
pcallcontext_generator.ARGC = 0
pcallcontext_generator.EXTRA = eps
pcallcontext_generator.NAMED = eps
pcallcontext_generator.WRAPPER = eps
$class_method_origin(S.CLASSES, pgenerator.FUNCTION) = (pmethoddesc)
pmethoddesc.VISIBILITY = PROPERTY_PUBLIC
~pmethoddesc.ABSTRACT
pmethoddesc.FUNCTION.SIGNATURE.BYREF
b_static = pmethoddesc.STATIC
pmethoddesc.NAME = $ptascii("flow")
$ppgenerator_reference_owner($origin_node(S.SOURCES, pgenerator.FUNCTION)) = (true)
$function_generator(S, pmethoddesc.FUNCTION)
$class_at(S.CLASSES, pmethoddesc.OWNER) = (pclassdesc_owner)
pclassdesc_owner.KIND = "class"
pclassdesc_owner.NAME = $ptascii("Factory124@X@")
pcallcontext_generator.LEXICAL_CLASS = (pmethoddesc.OWNER)
pcallcontext_generator.CALLED_CLASS = (porigin_called)
$class_at(S.CLASSES, porigin_called) = (pclassdesc_called)
pclassdesc_called.NAME = $ptascii("ChildFactory124@X@")
porigin_called =/= pmethoddesc.OWNER
S_global = $global_table_view(S)
$lookup(S_global.ENV, $ptascii("weakFactory")) = (n_weak_factory_cv)
S.STORE[n_weak_factory_cv] = DEFINED (POBJECT n_weak_factory)
S.OBJECTS[n_weak_factory] = WEAKREFERENCE (n_factory)
S.OBJECTS[n_factory] = INSTANCE porigin_called
$lookup(psymboltable_generator.ENV, $ptascii("cache")) = (n_cell)
n_cell <- S.REFCELLS
(HCELL n_cell) <- S.ALLOCATIONS
S.STORE[n_cell] = DEFINED (POBJECT n_cache)
$object_name(S, n_cache) = $ptascii("Cache124@X@")
$ordinary_reference_value(S, n_cell) = (POBJECT n_cache)
$generator_reference_producer(S, pgenerator)
$generator_reference_valid(S, GENERATOR pgenerator)
$generator_api_body_reference(S, pgenerator)
$generator_api_body_method_reference(S, n_target)
$generator_api_body_producer(S, n_target)
$node_children(S, HCELL n_cell) = [HOBJECT n_cache]
$heap_owners($heap_graph(S), HCELL n_cell) = 2
$heap_owners($heap_graph(S), HOBJECT n_cache) = 1
$heap_owners($heap_graph(S), HOBJECT n_target) = 2
$generator_frame_valid(S, pgenerator, pframe_generator)
S_frame_view = $generator_frame_scope(S, pframe_generator)
$generator_creation_context_valid(S_frame_view, pgenerator, pcallcontext_generator)
$call_current_valid(S_frame_view)
S_lexical = S_frame_view[.CURRENT = (pcallcontext_generator[.LEXICAL_CLASS = (porigin_called)])]
~$call_current_valid(S_lexical)
S_called = S_frame_view[.CURRENT = (pcallcontext_generator[.CALLED_CLASS = (pmethoddesc.OWNER)])]
~$call_current_valid(S_called)
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
'''

INSTANCE = r'''
~pmethoddesc.STATIC
pcallcontext_generator.TARGET = METHOD_TARGET n_factory pgenerator.FUNCTION
pcallcontext_generator.RECEIVER = (n_factory)
$this_receiver(S_frame_view) = (n_factory)
$call_context_roots((pcallcontext_generator)) = [HOBJECT n_factory]
$heap_owners($heap_graph(S), HOBJECT n_factory) = 1
S_receiver = S_frame_view[.CURRENT = (pcallcontext_generator[.RECEIVER = eps])]
~$call_current_valid(S_receiver)
S_continue = $drive_steps(S, 1)
S_reached_factory = $seek(S_continue[.COMPLETION = NORMAL], 4000)
S_reached_factory.COMPLETION = NORMAL \/ S_reached_factory.COMPLETION = BUDGET
S_factory = S_reached_factory[.COMPLETION = NORMAL]
S_factory.CURRENT = (pcallcontext_factory)
pcallcontext_factory.NAME = $ptascii("Factory124I::__destruct")
pcallcontext_factory.RECEIVER = (n_factory)
pcallcontext_factory.CALLSITE = eps
S_factory.FRAMES = pframe_factory :: pframe_factory_tail*
pframe_factory.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: (DESTRUCTOR_RELEASE pdestructionrelease_empty) :: (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (GENERATOR_RESUME pgeneratorop) :: ptask_tail*
pdestructorcall.OBJECT = n_factory
pdestructorcall.FRAME = (pdestructionframe)
pdestructionframe.FUNCTION = pgenerator.FUNCTION
pdestructionframe.PENDING = (n_body)
pdestructionrelease_empty.JOBS = eps
pgeneratorop.OBJECT = n_target
pgeneratorop.NAME = "send"
pgeneratorop.ARGUMENTS = [POBJECT n_argument]
S_factory.OBJECTS[n_target] = GENERATOR pgenerator_closed
pgenerator_closed.REFCELL = (n_cell)
pgenerator_closed.VALUE = eps
$generator_api_body_method_reference(S_factory, n_target)
$generator_api_body_producer(S_factory, n_target)
$node_children(S_factory, HOBJECT n_target) = [HCELL n_cell]
$heap_owners($heap_graph(S_factory), HOBJECT n_factory) = 2
$heap_owners($heap_graph(S_factory), HOBJECT n_target) = 1
$heap_owners($heap_graph(S_factory), HCELL n_cell) = 1
$heap_owners($heap_graph(S_factory), HOBJECT n_cache) = 1
$heap_owners($heap_graph(S_factory), HOBJECT n_argument) = 1
$heap_owners($heap_graph(S_factory), HOBJECT n_body) = 2
S_boundary = $destructor_boundary_scope(S_factory, pdestructorcall, S_factory.FRAMES)
$generator_api_body_cleanup(S_boundary, S_boundary.TODO) = ((pgeneratorop, ptask_projected*))
S_projection = $generator_descriptor_view(S_factory)
S_projection = S_factory[.FRAMES = pframe_factory[.TODO = ptask_projected*] :: pframe_factory_tail*]
$destructor_trace_suffix(S_factory, pcallcontext_factory) = [ptraceframe_api]
ptraceframe_api.FUNCTION = $ptascii("send")
ptraceframe_api.CLASS = ($ptascii("Generator"))
ptraceframe_api.ARGS = $trace_indexed_args([POBJECT n_argument], 0)
$call_descriptors_valid(S_factory)
$heap_valid($heap_graph(S_factory))
S_factory_pause = $drive(S_factory, 0)
S_factory_pause.COMPLETION = BUDGET
S_factory_pause[.COMPLETION = NORMAL] = S_factory
$generator_descriptor_view(S_factory_pause) = S_projection[.COMPLETION = BUDGET]
$call_descriptors_valid(S_factory_pause)
S_factory_next = $drive_steps(S_factory, 1)
S_factory_next.COMPLETION = BUDGET
$call_descriptors_valid(S_factory_next)
$drive_steps(S_factory_pause[.COMPLETION = NORMAL], 1) = S_factory_next
S_reached_closed = $seek(S_factory_next[.COMPLETION = NORMAL], 4000)
S_reached_closed.COMPLETION = NORMAL \/ S_reached_closed.COMPLETION = BUDGET
S_closed = S_reached_closed[.COMPLETION = NORMAL]
'''

STATIC = r'''
pmethoddesc.STATIC
pcallcontext_generator.TARGET = STATIC_METHOD_TARGET porigin_called pgenerator.FUNCTION
pcallcontext_generator.RECEIVER = eps
$this_receiver(S_frame_view) = eps
$call_context_roots((pcallcontext_generator)) = eps
$target_nodes(pcallcontext_generator.TARGET) = eps
$weakref_get(S, n_weak_factory) = PNULL
~((HOBJECT n_factory) <- S.ALLOCATIONS)
$heap_owners($heap_graph(S), HOBJECT n_factory) = 0
S_receiver = S_frame_view[.CURRENT = (pcallcontext_generator[.RECEIVER = (n_cache)])]
~$call_current_valid(S_receiver)
S_continue = $drive_steps(S, 1)
S_reached_cleanup = $seek(S_continue[.COMPLETION = NORMAL], 4000)
S_reached_cleanup.COMPLETION = NORMAL \/ S_reached_cleanup.COMPLETION = BUDGET
S_cleanup = S_reached_cleanup[.COMPLETION = NORMAL]
S_cleanup.CURRENT = (pcallcontext_caller)
S_cleanup.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_empty) :: (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (GENERATOR_RESUME pgeneratorop) :: ptask_tail*
pdestructionrelease_empty.JOBS = eps
pdestructionframe.FUNCTION = pgenerator.FUNCTION
pdestructionframe.PENDING = (n_body)
pgeneratorop.OBJECT = n_target
pgeneratorop.NAME = "send"
pgeneratorop.ARGUMENTS = [POBJECT n_argument]
$generator_api_body_method_reference(S_cleanup, n_target)
$generator_api_body_cleanup(S_cleanup, S_cleanup.TODO) = ((pgeneratorop, ptask_projected*))
S_projection = $generator_descriptor_view(S_cleanup)
S_projection = S_cleanup[.TODO = ptask_projected*]
$heap_owners($heap_graph(S_cleanup), HOBJECT n_factory) = 0
$heap_owners($heap_graph(S_cleanup), HOBJECT n_target) = 1
$heap_owners($heap_graph(S_cleanup), HCELL n_cell) = 1
$heap_owners($heap_graph(S_cleanup), HOBJECT n_cache) = 1
$heap_owners($heap_graph(S_cleanup), HOBJECT n_argument) = 1
$heap_owners($heap_graph(S_cleanup), HOBJECT n_body) = 2
$call_descriptors_valid(S_cleanup)
$heap_valid($heap_graph(S_cleanup))
S_pause = $drive(S_cleanup, 0)
S_pause.COMPLETION = BUDGET
S_pause[.COMPLETION = NORMAL] = S_cleanup
$generator_descriptor_view(S_pause) = S_projection[.COMPLETION = BUDGET]
$call_descriptors_valid(S_pause)
PhpStep: S_cleanup ~> S_frame_exit
S_frame_exit.TODO = (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (GENERATOR_RESUME pgeneratorop) :: ptask_tail*
$call_descriptors_valid(S_frame_exit)
$heap_valid($heap_graph(S_frame_exit))
S_budget = $drive(S_cleanup, 1)
S_budget.COMPLETION = BUDGET
S_budget[.COMPLETION = NORMAL] = S_frame_exit
$drive(S_pause[.COMPLETION = NORMAL], 1) = S_budget
$call_descriptors_valid(S_budget)
PhpStep: S_frame_exit ~> S_closed
S_closed.OBJECTS[n_target] = GENERATOR pgenerator_closed
'''

CLOSED = r'''
S_closed.COMPLETION = NORMAL
S_closed.TODO = (THROW_SEARCH n_body) :: (GENERATOR_RESUME pgeneratorop) :: ptask_tail*
S_closed.CURRENT = (pcallcontext_caller)
pgenerator_closed.FUNCTION = pgenerator.FUNCTION
pgenerator_closed.PHASE = GENERATOR_CLOSED
pgenerator_closed.FRAME = eps
pgenerator_closed.RETURN = eps
pgenerator_closed.VALUE = eps
pgenerator_closed.REFCELL = (n_cell)
~pgenerator_closed.PENDING_INIT
$ordinary_reference_value(S_closed, n_cell) = (POBJECT n_cache)
$generator_api_body_reference(S_closed, pgenerator_closed)
$generator_api_body_method_reference(S_closed, n_target)
$generator_api_body_producer(S_closed, n_target)
$generator_api_body_throw(S_closed, pgeneratorop)
~$generator_storage_active(S_closed, n_target)
$node_children(S_closed, HOBJECT n_target) = [HCELL n_cell]
$node_children(S_closed, HCELL n_cell) = [HOBJECT n_cache]
$weakref_get(S_closed, n_weak_factory) = PNULL
$heap_owners($heap_graph(S_closed), HOBJECT n_factory) = 0
$heap_owners($heap_graph(S_closed), HOBJECT n_target) = 1
$heap_owners($heap_graph(S_closed), HCELL n_cell) = 1
$heap_owners($heap_graph(S_closed), HOBJECT n_cache) = 1
$heap_owners($heap_graph(S_closed), HOBJECT n_argument) = 1
$heap_owners($heap_graph(S_closed), HOBJECT n_body) = 2
$lookup(S_closed.ENV, $ptascii("result")) = (n_result_cv)
S_closed.STORE[n_result_cv] = DEFINED pvalue_result
$string_bytes(pvalue_result) = ($ptascii("sentinel"))
S_no_cell = S_closed[.ALLOCATIONS = $destruction_node_delete(S_closed.ALLOCATIONS, HCELL n_cell)]
~$generator_api_body_method_reference(S_no_cell, n_target)
~$generator_api_body_throw(S_no_cell, pgeneratorop)
~$generator_api_body_method_reference(S_closed[.REFCELLS = eps], n_target)
~$generator_api_body_method_reference(S_closed[.STORE[n_cell] = UNDEFINED], n_target)
S_snapshot = S_closed[.OBJECTS[n_target] = GENERATOR pgenerator_closed[.REFCELL = eps][.VALUE = (POBJECT n_cache)]]
~$generator_api_body_method_reference(S_snapshot, n_target)
~$generator_api_body_producer(S_snapshot, n_target)
S_metadata = S_closed[.PROPREFS = {CELL n_cell, SOURCES eps} :: S_closed.PROPREFS]
$generator_api_body_reference(S_metadata, pgenerator_closed)
$ordinary_reference_value(S_metadata, n_cell) = eps
~$generator_api_body_method_reference(S_metadata, n_target)
~$generator_api_body_producer(S_metadata, n_target)
pgenstorage = {OBJECT n_target, HANDLE S_closed.DESTRUCTION.HANDLES[n_target], NEXT 2, CALLER S_closed.CURRENT, ORIGIN S_closed.ORIGIN, CONSTCONTEXT S_closed.CONSTCONTEXT, USER $destructor_user_source(S_closed)}
S_consumed = S_closed[.TODO = (GENERATOR_STORAGE_STEP pgenstorage) :: S_closed.TODO]
$generator_storage_active(S_consumed, n_target)
$generator_api_body_reference(S_consumed, pgenerator_closed)
~$generator_api_body_method_reference(S_consumed, n_target)
~$generator_api_body_producer(S_consumed, n_target)
pclassdesc_owner.METHODS = pmethoddesc :: pmethoddesc_tail*
S_signature = S_closed[.CLASSES = $trait_class_set(S_closed.CLASSES, pclassdesc_owner[.METHODS = pmethoddesc[.FUNCTION = pmethoddesc.FUNCTION[.SIGNATURE = pmethoddesc.FUNCTION.SIGNATURE[.BYREF = false]]] :: pmethoddesc_tail*])]
~$generator_api_body_producer(S_signature, n_target)
S_flag = S_closed[.CLASSES = $trait_class_set(S_closed.CLASSES, pclassdesc_owner[.METHODS = pmethoddesc[.STATIC = (~b_static)] :: pmethoddesc_tail*])]
~$generator_api_body_producer(S_flag, n_target)
S_private = S_closed[.CLASSES = $trait_class_set(S_closed.CLASSES, pclassdesc_owner[.METHODS = pmethoddesc[.VISIBILITY = PROPERTY_PRIVATE] :: pmethoddesc_tail*])]
~$generator_api_body_producer(S_private, n_target)
~$generator_api_body_producer(S_closed[.CLASSNAMES = eps], n_target)
~$generator_api_body_throw(S_closed, pgeneratorop[.NAME = "throw"])
$call_descriptors_valid(S_closed)
$heap_valid($heap_graph(S_closed))
PhpStep: S_closed ~> S_release
S_release.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_argument) :: (THROW_SEARCH n_body) :: (GENERATOR_API_RESULT pgeneratorop PNULL) :: ptask_tail*
pdestructionrelease_argument.JOBS = [DESTRUCTION_VALUE (HOBJECT n_argument)]
$task_nodes(DESTRUCTOR_RELEASE pdestructionrelease_argument) = [HOBJECT n_argument]
$task_nodes(GENERATOR_API_RESULT pgeneratorop PNULL) = [HOBJECT n_target]
$destructor_tail_pending(S_release.TODO) = (n_body)
$heap_owners($heap_graph(S_release), HOBJECT n_factory) = 0
$heap_owners($heap_graph(S_release), HOBJECT n_target) = 1
$heap_owners($heap_graph(S_release), HCELL n_cell) = 1
$heap_owners($heap_graph(S_release), HOBJECT n_cache) = 1
$heap_owners($heap_graph(S_release), HOBJECT n_argument) = 1
$heap_owners($heap_graph(S_release), HOBJECT n_body) = 2
$call_descriptors_valid(S_release)
$heap_valid($heap_graph(S_release))
'''


def case(row, static):
    suffix = 'S' if static else 'I'
    stage = (r'S.CURRENT = (pcallcontext_stage) '
             r'-- if pcallcontext_stage.NAME = $ptascii("run124@X@") '
             r'-- if $generator_resume_head(S.TODO) \/ '
             + (r'$generator_api_body_cleanup(S, S.TODO) =/= eps \/ '
                if static else '')
             + r'$destructor_leaving_exception(S.TODO) =/= eps')
    if not static:
        stage = (
            r'S.CURRENT = (pcallcontext_stage) '
            r'-- if $target_function(S, pcallcontext_stage.TARGET) = (pfunction_stage) '
            r'-- if (pcallcontext_stage.NAME = $ptascii("run124I") /\ '
            r'($generator_resume_head(S.TODO) \/ $destructor_leaving_exception(S.TODO) =/= eps)) \/ '
            r'(pcallcontext_stage.NAME = $ptascii("Factory124I::__destruct") /\ '
            r'S.TODO = $call_receive_body(S, pfunction_stage))')
    return {'source': row['source'], 'stage': stage.replace('@X@', suffix),
            'checks': checks(INITIAL + (STATIC if static else INSTANCE) + CLOSED,
                             suffix)}


review.CASES = {row['id']: case(row, bool(index))
                for index, row in enumerate(ROWS)}

if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=600) else 1)
