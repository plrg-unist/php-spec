#!/usr/bin/env python3
"""Check genuine inherited method authority through closed SEND cleanup."""
import hashlib
import json
from pathlib import Path
import fiber_state_review as review

ROW = json.loads(Path(__file__).with_name(
    'generator_instance_send_body_throw_review_cases.json').read_bytes())[0]
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']
assert ROW['source_sha256'] == 'a6a386c7bdef87efb172a50b5351a93fd05f12fc609253cad17bed12d0416dc0'

# Stop at the initial getter, the factory destructor's actual entry, then the
# closed SEND. Matching the complete entry body keeps the middle stop unique.
STAGE = (
    'S.CURRENT = (pcallcontext_stage) '
    '-- if $target_function(S, pcallcontext_stage.TARGET) = (pfunction_stage) '
    '-- if (pcallcontext_stage.NAME = $ptascii("run122M") /\\ '
    '($generator_resume_head(S.TODO) \\/ $destructor_leaving_exception(S.TODO) =/= eps)) \\/ '
    '(pcallcontext_stage.NAME = $ptascii("Factory122M::__destruct") /\\ '
    'S.TODO = $call_receive_body(S, pfunction_stage))')
CHECKS = [line.strip() for line in r'''
S.COMPLETION = NORMAL
S.CURRENT = (pcallcontext_caller)
S.TODO = (GENERATOR_RESUME pgeneratorop_current) :: ptask_current*
n_target = pgeneratorop_current.OBJECT
S.OBJECTS[n_target] = GENERATOR pgenerator
pgeneratorop_current.OBJECT = n_target
pgeneratorop_current.NAME = "current"
pgeneratorop_current.ARGUMENTS = eps
pgenerator.PHASE = GENERATOR_PAUSED
pgenerator.CLOSURE = eps
pgenerator.CREATION = eps
pgenerator.ACCESS = eps
pgenerator.DELEGATE = eps
pgenerator.REFCELL = eps
pgenerator.VALUE = (POBJECT n_cache)
pgenerator.FRAME = (pframe_generator)
pframe_generator.CONTEXT = (pcallcontext_generator)
pframe_generator.LOCALS = (psymboltable_generator)
pcallcontext_generator.TARGET = METHOD_TARGET n_factory pgenerator.FUNCTION
pcallcontext_generator.FUNCTION = pgenerator.FUNCTION
pcallcontext_generator.RECEIVER = (n_factory)
pcallcontext_generator.INSTANCE = eps
pcallcontext_generator.ARGC = 0
pcallcontext_generator.EXTRA = eps
pcallcontext_generator.NAMED = eps
pcallcontext_generator.WRAPPER = eps
S.OBJECTS[n_factory] = INSTANCE porigin_called
$class_method_origin(S.CLASSES, pgenerator.FUNCTION) = (pmethoddesc)
pmethoddesc.VISIBILITY = PROPERTY_PUBLIC
~pmethoddesc.STATIC
~pmethoddesc.ABSTRACT
~pmethoddesc.FUNCTION.SIGNATURE.BYREF
pmethoddesc.NAME = $ptascii("flow")
$class_at(S.CLASSES, pmethoddesc.OWNER) = (pclassdesc_owner)
pclassdesc_owner.KIND = "class"
pclassdesc_owner.NAME = $ptascii("Factory122M")
$class_at(S.CLASSES, porigin_called) = (pclassdesc_called)
pclassdesc_called.NAME = $ptascii("ChildFactory122M")
porigin_called =/= pmethoddesc.OWNER
pcallcontext_generator.LEXICAL_CLASS = (pmethoddesc.OWNER)
pcallcontext_generator.CALLED_CLASS = (porigin_called)
$function_generator(S, pmethoddesc.FUNCTION)
$ppgenerator_reference_owner($origin_node(S.SOURCES, pgenerator.FUNCTION)) = (false)
$generator_frame_valid(S, pgenerator, pframe_generator)
S_view = $generator_frame_scope(S, pframe_generator)
$generator_creation_context_valid(S_view, pgenerator, pcallcontext_generator)
$call_current_valid(S_view)
$this_receiver(S_view) = (n_factory)
$scoped_receiver_valid(S_view, porigin_called, pmethoddesc, (n_factory))
$call_context_roots((pcallcontext_generator)) = [HOBJECT n_factory]
$lookup(psymboltable_generator.ENV, $ptascii("cache")) = (n_cache_cv)
S.STORE[n_cache_cv] = DEFINED (POBJECT n_cache)
$object_name(S, n_cache) = $ptascii("Cache122M")
$node_children(S, HOBJECT n_factory) = eps
$node_children(S, HOBJECT n_cache) = eps
$heap_owners($heap_graph(S), HOBJECT n_factory) = 1
$heap_owners($heap_graph(S), HOBJECT n_cache) = 2
$heap_owners($heap_graph(S), HOBJECT n_target) = 2
$generator_api_body_producer(S, n_target)
S_receiver = S_view[.CURRENT = (pcallcontext_generator[.RECEIVER = eps])]
~$call_current_valid(S_receiver)
S_target = S_view[.CURRENT = (pcallcontext_generator[.TARGET = METHOD_TARGET n_target pgenerator.FUNCTION])]
~$call_current_valid(S_target)
S_lexical = S_view[.CURRENT = (pcallcontext_generator[.LEXICAL_CLASS = eps])]
~$call_current_valid(S_lexical)
S_called = S_view[.CURRENT = (pcallcontext_generator[.CALLED_CLASS = (pmethoddesc.OWNER)])]
~$call_current_valid(S_called)
S_line = S_view[.CURRENT = (pcallcontext_generator[.LINE = $(pcallcontext_generator.LINE + 1)])]
~$call_current_valid(S_line)
S_site = S_view[.CURRENT = (pcallcontext_generator[.CALLSITE = (pgenerator.FUNCTION)])]
~$call_current_valid(S_site)
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
S_continue = $drive_steps(S, 1)
S_reached_factory = $seek(S_continue[.COMPLETION = NORMAL], 4000)
S_reached_factory.COMPLETION = NORMAL \/ S_reached_factory.COMPLETION = BUDGET
S_factory = S_reached_factory[.COMPLETION = NORMAL]
S_factory.CURRENT = (pcallcontext_factory)
pcallcontext_factory.NAME = $ptascii("Factory122M::__destruct")
pcallcontext_factory.RECEIVER = (n_factory)
pcallcontext_factory.LEXICAL_CLASS = (pmethoddesc.OWNER)
pcallcontext_factory.CALLED_CLASS = (porigin_called)
pcallcontext_factory.CALLSITE = eps
pcallcontext_factory.LINE = $(-1)
S_factory.FRAMES = pframe_factory :: pframe_factory_tail*
pframe_factory.CONTEXT = (pcallcontext_caller)
pframe_factory.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: (DESTRUCTOR_RELEASE pdestructionrelease_empty) :: (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (GENERATOR_RESUME pgeneratorop) :: ptask_tail*
pdestructorcall.OBJECT = n_factory
pdestructorcall.TARGET = METHOD_TARGET n_factory pcallcontext_factory.FUNCTION
pdestructorcall.CALLER = (pcallcontext_caller)
pdestructorcall.FRAME = (pdestructionframe)
pdestructorcall.OPERATION = eps
pdestructorcall.PENDING = (n_body)
pdestructionrelease_empty.JOBS = eps
pdestructionrelease_empty.CALLER = (pcallcontext_caller)
pdestructionrelease_empty.ORIGIN = (pgeneratorop.SITE)
S_factory.DESTRUCTION.FRAMES = pdestructionframe :: pdestructionframe_tail*
pdestructionframe.CALLER = (pcallcontext_caller)
pdestructionframe.FUNCTION = pgenerator.FUNCTION
pdestructionframe.PENDING = (n_body)
pdestructionframe.VALUE = KNOWN PNULL
pdestructionframe.ORIGIN = (pgeneratorop.SITE)
$destructor_context_call(pcallcontext_factory, S_factory.CURRENT, S_factory.FRAMES) = (pdestructorcall)
$destructor_context_valid(S_factory, pcallcontext_factory)
$destructor_call_pending_valid(S_factory, pdestructorcall)
$destructor_call_pending_tail(S_factory, pdestructorcall) = ((DESTRUCTOR_RELEASE pdestructionrelease_empty) :: (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (GENERATOR_RESUME pgeneratorop) :: ptask_tail*)
S_boundary = $destructor_boundary_scope(S_factory, pdestructorcall, S_factory.FRAMES)
S_boundary.TODO = pframe_factory.TODO
$generator_api_body_cleanup(S_boundary, S_boundary.TODO) = ((pgeneratorop, ptask_projected*))
ptask_projected* = (DESTRUCTOR_RESULT pdestructorcall) :: (DESTRUCTOR_RELEASE pdestructionrelease_empty) :: (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: ptask_tail*
S_factory.OBJECTS[n_target] = GENERATOR pgenerator_closed
pgenerator_closed.PHASE = GENERATOR_CLOSED
pgenerator_closed.FRAME = eps
$generator_api_body_producer(S_factory, n_target)
$heap_owners($heap_graph(S_factory), HOBJECT n_factory) = 2
$heap_owners($heap_graph(S_factory), HOBJECT n_target) = 1
$heap_owners($heap_graph(S_factory), HOBJECT n_cache) = 1
$heap_owners($heap_graph(S_factory), HOBJECT n_body) = 2
pgeneratorop.ARGUMENTS = [POBJECT n_argument]
$heap_owners($heap_graph(S_factory), HOBJECT n_argument) = 1
$task_nodes(GENERATOR_RESUME pgeneratorop) = [HOBJECT n_target, HOBJECT n_argument]
$node_children(S_factory, HOBJECT n_target) = [HOBJECT n_cache]
$destructor_trace_suffix(S_factory, pcallcontext_factory) = [ptraceframe_api]
ptraceframe_api.FILE = $call_sourcefile(S_factory.FILES, pgeneratorop.SITE)
ptraceframe_api.LINE = pgeneratorop.LINE
ptraceframe_api.FUNCTION = $ptascii("send")
ptraceframe_api.CLASS = ($ptascii("Generator"))
ptraceframe_api.TYPE = ($ptascii("->"))
ptraceframe_api.ARGS = $trace_indexed_args([POBJECT n_argument], 0)
ptraceframe_api.HASARGS
$trace_context(S_factory, S_factory.ENV, (pcallcontext_factory)) = [ptraceframe_destructor, ptraceframe_api]
ptraceframe_destructor.FUNCTION = $ptascii("__destruct")
ptraceframe_destructor.CLASS = ($ptascii("Factory122M"))
ptraceframe_destructor.FILE = eps
ptraceframe_destructor.LINE = $(-1)
$generator_api_body_cleanup(S_boundary, (DESTRUCTOR_FRAME_EXIT pdestructionframe[.PENDING = eps]) :: (GENERATOR_RESUME pgeneratorop) :: ptask_tail*) = eps
$generator_api_body_cleanup(S_boundary, (DESTRUCTOR_FRAME_EXIT pdestructionframe[.CALLER = eps]) :: (GENERATOR_RESUME pgeneratorop) :: ptask_tail*) = eps
$generator_api_body_cleanup(S_boundary, (DESTRUCTOR_FRAME_EXIT pdestructionframe[.FUNCTION = pcallcontext_caller.FUNCTION]) :: (GENERATOR_RESUME pgeneratorop) :: ptask_tail*) = eps
$generator_api_body_cleanup(S_boundary, (DESTRUCTOR_RELEASE pdestructionrelease_empty[.JOBS = [DESTRUCTION_VALUE (HOBJECT n_argument)]]) :: (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (GENERATOR_RESUME pgeneratorop) :: ptask_tail*) = eps
$generator_api_body_cleanup(S_boundary, (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: DISCARD :: (GENERATOR_RESUME pgeneratorop) :: ptask_tail*) = eps
$generator_api_body_cleanup(S_boundary, (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (GENERATOR_RESUME pgeneratorop[.NAME = "throw"]) :: ptask_tail*) = eps
$generator_api_body_cleanup(S_boundary, (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (GENERATOR_RESUME pgeneratorop[.OBJECT = n_factory]) :: ptask_tail*) = eps
S_projection = $generator_descriptor_view(S_factory)
S_projection.OBJECTS = S_factory.OBJECTS
S_projection.ALLOCATIONS = S_factory.ALLOCATIONS
S_projection.STORE = S_factory.STORE
S_projection.DESTRUCTION = S_factory.DESTRUCTION
S_projection.CURRENT = S_factory.CURRENT
S_projection.TODO = S_factory.TODO
|S_projection.FRAMES| = |S_factory.FRAMES|
S_moved = S_factory[.FRAMES = pframe_factory[.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: (DESTRUCTOR_RELEASE pdestructionrelease_empty) :: (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: DISCARD :: (GENERATOR_RESUME pgeneratorop) :: ptask_tail*] :: pframe_factory_tail*]
$generator_descriptor_view(S_moved) = S_moved
~$call_descriptors_valid(S_moved)
$destructor_trace_suffix(S_moved, pcallcontext_factory) = eps
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
S_closed.TODO = (THROW_SEARCH n_body) :: (GENERATOR_RESUME pgeneratorop) :: ptask_tail*
S_closed.CURRENT = (pcallcontext_after)
pcallcontext_after.NAME = $ptascii("run122M")
pgeneratorop.OBJECT = n_target
pgeneratorop.NAME = "send"
pgeneratorop.ARGUMENTS = [POBJECT n_argument]
pgeneratorop.SELECTION = eps
pgeneratorop.LOOP = eps
~pgeneratorop.STARTPACK
~pgeneratorop.BORROWED
~pgeneratorop.ADVANCE
S_closed.OBJECTS[n_target] = GENERATOR pgenerator_closed
pgenerator_closed.PHASE = GENERATOR_CLOSED
pgenerator_closed.FUNCTION = pgenerator.FUNCTION
pgenerator_closed.FRAME = eps
pgenerator_closed.RETURN = eps
pgenerator_closed.CLOSURE = eps
pgenerator_closed.CREATION = eps
pgenerator_closed.ACCESS = eps
pgenerator_closed.DELEGATE = eps
pgenerator_closed.REFCELL = eps
pgenerator_closed.VALUE = (POBJECT n_cache)
~pgenerator_closed.PENDING_INIT
~((HOBJECT n_factory) <- S_closed.ALLOCATIONS)
S_closed.OBJECTS[n_factory] = INSTANCE porigin_called
$heap_owners($heap_graph(S_closed), HOBJECT n_factory) = 0
$node_children(S_closed, HOBJECT n_target) = [HOBJECT n_cache]
$object_name(S_closed, n_argument) = $ptascii("Argument122M")
S_global = $global_table_view(S_closed)
$lookup(S_global.ENV, $ptascii("weakFactory")) = (n_weak_factory_cv)
S_closed.STORE[n_weak_factory_cv] = DEFINED (POBJECT n_weak_factory)
$weakref_get(S_closed, n_weak_factory) = PNULL
$lookup(S_global.ENV, $ptascii("weakTarget")) = (n_weak_target_cv)
S_closed.STORE[n_weak_target_cv] = DEFINED (POBJECT n_weak_target)
$weakref_get(S_closed, n_weak_target) = POBJECT n_target
$lookup(S_global.ENV, $ptascii("weakCache")) = (n_weak_cache_cv)
S_closed.STORE[n_weak_cache_cv] = DEFINED (POBJECT n_weak_cache)
$weakref_get(S_closed, n_weak_cache) = POBJECT n_cache
$lookup(S_global.ENV, $ptascii("bodyStop")) = (n_body_cv)
S_closed.STORE[n_body_cv] = DEFINED (POBJECT n_body)
$lookup(S_global.ENV, $ptascii("target")) = (n_target_cv)
S_closed.STORE[n_target_cv] = DEFINED PNULL
$lookup(S_closed.ENV, $ptascii("result")) = (n_result_cv)
S_closed.STORE[n_result_cv] = DEFINED pvalue_result
$string_bytes(pvalue_result) = ($ptascii("sentinel"))
$task_nodes(GENERATOR_RESUME pgeneratorop) = [HOBJECT n_target, HOBJECT n_argument]
$heap_owners($heap_graph(S_closed), HOBJECT n_target) = 1
$heap_owners($heap_graph(S_closed), HOBJECT n_cache) = 1
$heap_owners($heap_graph(S_closed), HOBJECT n_argument) = 1
$heap_owners($heap_graph(S_closed), HOBJECT n_body) = 2
$generator_api_body_producer(S_closed, n_target)
$generator_api_body_throw(S_closed, pgeneratorop)
pclassdesc_owner.METHODS = pmethoddesc :: pmethoddesc_tail*
S_static = S_closed[.CLASSES = $trait_class_set(S_closed.CLASSES, pclassdesc_owner[.METHODS = pmethoddesc[.STATIC = true] :: pmethoddesc_tail*])]
~$generator_api_body_producer(S_static, n_target)
S_private = S_closed[.CLASSES = $trait_class_set(S_closed.CLASSES, pclassdesc_owner[.METHODS = pmethoddesc[.VISIBILITY = PROPERTY_PRIVATE] :: pmethoddesc_tail*])]
~$generator_api_body_producer(S_private, n_target)
S_abstract = S_closed[.CLASSES = $trait_class_set(S_closed.CLASSES, pclassdesc_owner[.METHODS = pmethoddesc[.ABSTRACT = true] :: pmethoddesc_tail*])]
~$generator_api_body_producer(S_abstract, n_target)
S_byref = S_closed[.CLASSES = $trait_class_set(S_closed.CLASSES, pclassdesc_owner[.METHODS = pmethoddesc[.FUNCTION = pmethoddesc.FUNCTION[.SIGNATURE = pmethoddesc.FUNCTION.SIGNATURE[.BYREF = true]]] :: pmethoddesc_tail*])]
~$generator_api_body_producer(S_byref, n_target)
S_kind = S_closed[.CLASSES = $trait_class_set(S_closed.CLASSES, pclassdesc_owner[.KIND = "trait"])]
~$generator_api_body_producer(S_kind, n_target)
S_member = S_closed[.CLASSES = $trait_class_set(S_closed.CLASSES, pclassdesc_owner[.METHODS = eps])]
~$generator_api_body_producer(S_member, n_target)
~$generator_api_body_producer(S_closed[.CLASSNAMES = eps], n_target)
S_wrong_function = S_closed[.OBJECTS[n_target] = GENERATOR pgenerator_closed[.FUNCTION = pcallcontext_factory.FUNCTION]]
~$generator_api_body_producer(S_wrong_function, n_target)
~$generator_api_body_throw(S_wrong_function, pgeneratorop)
S_no_target = S_closed[.ALLOCATIONS = $destruction_node_delete(S_closed.ALLOCATIONS, HOBJECT n_target)]
~$generator_api_body_throw(S_no_target, pgeneratorop)
~$generator_api_body_throw(S_closed, pgeneratorop[.ADVANCE = true])
~$generator_api_body_throw(S_closed, pgeneratorop[.NAME = "throw"])
~$generator_api_body_throw(S_closed[.TODO = ptask_tail*], pgeneratorop)
$call_descriptors_valid(S_closed)
$heap_valid($heap_graph(S_closed))
S_pause = $drive(S_closed, 0)
S_pause.COMPLETION = BUDGET
S_pause[.COMPLETION = NORMAL] = S_closed
PhpStep: S_closed ~> S_release
S_release.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (THROW_SEARCH n_body) :: (GENERATOR_API_RESULT pgeneratorop PNULL) :: ptask_tail*
pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_argument)]
S_release.ORIGIN = (pgeneratorop.SITE)
S_release.RESULT = KNOWN PNULL
S_release.BASE = BASE_VALUE (KNOWN PNULL)
S_release.OBJECTS = S_closed.OBJECTS
S_release.ALLOCATIONS = S_closed.ALLOCATIONS
S_release.STORE = S_closed.STORE
S_release.EVENTS = S_closed.EVENTS
$task_nodes(DESTRUCTOR_RELEASE pdestructionrelease) = [HOBJECT n_argument]
$task_nodes(GENERATOR_API_RESULT pgeneratorop PNULL) = [HOBJECT n_target]
$destructor_tail_pending(S_release.TODO) = (n_body)
$heap_owners($heap_graph(S_release), HOBJECT n_factory) = 0
$heap_owners($heap_graph(S_release), HOBJECT n_target) = 1
$heap_owners($heap_graph(S_release), HOBJECT n_cache) = 1
$heap_owners($heap_graph(S_release), HOBJECT n_argument) = 1
$heap_owners($heap_graph(S_release), HOBJECT n_body) = 2
$call_descriptors_valid(S_release)
$heap_valid($heap_graph(S_release))
S_budget = $drive(S_closed, 1)
S_budget.COMPLETION = BUDGET
S_budget[.COMPLETION = NORMAL] = S_release
$drive(S_pause[.COMPLETION = NORMAL], 1) = S_budget
$call_descriptors_valid(S_budget)
$heap_valid($heap_graph(S_budget))
'''.splitlines() if line.strip()]

review.CASES = {ROW['id']: {'source': ROW['source'], 'stage': STAGE,
                          'checks': CHECKS}}

if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=600) else 1)
