#!/usr/bin/env python3
"""Check genuine inherited static Generator scope and pending SEND owners."""
import hashlib
import json
from pathlib import Path
import fiber_state_review as review

ROW = json.loads(Path(__file__).with_name(
    'generator_static_send_body_throw_review_cases.json').read_bytes())[0]
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']
assert ROW['source_sha256'] == 'dcf319206322428a1c2d5945a5c948040cbc417542410aa26481f3a96d5516f3'

# The first CURRENT handoff exposes the saved static frame. The next stop is
# its real pending empty release, before FRAME_EXIT restores THROW_SEARCH.
STAGE = (
    r'S.CURRENT = (pcallcontext_stage) '
    r'-- if pcallcontext_stage.NAME = $ptascii("run123S") '
    r'-- if $generator_resume_head(S.TODO) \/ '
    r'$generator_api_body_cleanup(S, S.TODO) =/= eps \/ '
    r'$destructor_leaving_exception(S.TODO) =/= eps')
CHECKS = [line.strip() for line in r'''
S.COMPLETION = NORMAL
S.CURRENT = (pcallcontext_caller)
S.TODO = (GENERATOR_RESUME pgeneratorop_current) :: ptask_current*
n_target = pgeneratorop_current.OBJECT
pgeneratorop_current.NAME = "current"
pgeneratorop_current.ARGUMENTS = eps
S.OBJECTS[n_target] = GENERATOR pgenerator
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
pcallcontext_generator.TARGET = STATIC_METHOD_TARGET porigin_called pgenerator.FUNCTION
pcallcontext_generator.FUNCTION = pgenerator.FUNCTION
pcallcontext_generator.RECEIVER = eps
pcallcontext_generator.INSTANCE = eps
pcallcontext_generator.ARGC = 0
pcallcontext_generator.PARAMS = eps
pcallcontext_generator.HOLES = eps
pcallcontext_generator.EXTRA = eps
pcallcontext_generator.NAMED = eps
pcallcontext_generator.WRAPPER = eps
$class_method_origin(S.CLASSES, pgenerator.FUNCTION) = (pmethoddesc)
pmethoddesc.VISIBILITY = PROPERTY_PUBLIC
pmethoddesc.STATIC
~pmethoddesc.ABSTRACT
~pmethoddesc.FUNCTION.SIGNATURE.BYREF
~$ppmethod_magic(pmethoddesc.NAME)
pmethoddesc.NAME = $ptascii("flow")
pcallcontext_generator.NAME = pmethoddesc.FUNCTION.NAME
$class_at(S.CLASSES, pmethoddesc.OWNER) = (pclassdesc_owner)
pclassdesc_owner.KIND = "class"
pclassdesc_owner.NAME = $ptascii("Factory123S")
$class_at(S.CLASSES, porigin_called) = (pclassdesc_called)
pclassdesc_called.NAME = $ptascii("ChildFactory123S")
porigin_called =/= pmethoddesc.OWNER
pcallcontext_generator.LEXICAL_CLASS = (pmethoddesc.OWNER)
pcallcontext_generator.CALLED_CLASS = (porigin_called)
$function_generator(S, pmethoddesc.FUNCTION)
$ppgenerator_reference_owner($origin_node(S.SOURCES, pgenerator.FUNCTION)) = (false)
$generator_frame_valid(S, pgenerator, pframe_generator)
S_frame_view = $generator_frame_scope(S, pframe_generator)
$generator_creation_context_valid(S_frame_view, pgenerator, pcallcontext_generator)
$call_current_valid(S_frame_view)
$this_receiver(S_frame_view) = eps
$scoped_receiver_valid(S_frame_view, porigin_called, pmethoddesc, eps)
~$scoped_receiver_valid(S_frame_view, porigin_called, pmethoddesc, (n_cache))
$call_context_roots((pcallcontext_generator)) = eps
$target_nodes(pcallcontext_generator.TARGET) = eps
$lookup(psymboltable_generator.ENV, $ptascii("cache")) = (n_cache_cv)
S.STORE[n_cache_cv] = DEFINED (POBJECT n_cache)
$object_name(S, n_cache) = $ptascii("Cache123S")
S_global = $global_table_view(S)
$lookup(S_global.ENV, $ptascii("weakFactory")) = (n_weak_factory_cv)
S.STORE[n_weak_factory_cv] = DEFINED (POBJECT n_weak_factory)
S.OBJECTS[n_weak_factory] = WEAKREFERENCE (n_factory)
S.OBJECTS[n_factory] = INSTANCE porigin_called
$weakref_get(S, n_weak_factory) = PNULL
~((HOBJECT n_factory) <- S.ALLOCATIONS)
n_factory <- S.DESTRUCTION.CALLED
$heap_owners($heap_graph(S), HOBJECT n_factory) = 0
$heap_owners($heap_graph(S), HOBJECT n_cache) = 2
$heap_owners($heap_graph(S), HOBJECT n_target) = 2
$generator_api_body_producer(S, n_target)
S_receiver = S_frame_view[.CURRENT = (pcallcontext_generator[.RECEIVER = (n_cache)])]
~$call_current_valid(S_receiver)
S_instance = S_frame_view[.CURRENT = (pcallcontext_generator[.INSTANCE = (n_cache)])]
~$call_current_valid(S_instance)
S_target = S_frame_view[.CURRENT = (pcallcontext_generator[.TARGET = METHOD_TARGET n_factory pgenerator.FUNCTION])]
~$call_current_valid(S_target)
S_lexical = S_frame_view[.CURRENT = (pcallcontext_generator[.LEXICAL_CLASS = (porigin_called)])]
~$call_current_valid(S_lexical)
S_called = S_frame_view[.CURRENT = (pcallcontext_generator[.CALLED_CLASS = (pmethoddesc.OWNER)])]
~$call_current_valid(S_called)
S_line = S_frame_view[.CURRENT = (pcallcontext_generator[.LINE = $(pcallcontext_generator.LINE + 1)])]
~$call_current_valid(S_line)
S_site = S_frame_view[.CURRENT = (pcallcontext_generator[.CALLSITE = (pgenerator.FUNCTION)])]
~$call_current_valid(S_site)
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
S_continue = $drive_steps(S, 1)
S_reached_cleanup = $seek(S_continue[.COMPLETION = NORMAL], 4000)
S_reached_cleanup.COMPLETION = NORMAL \/ S_reached_cleanup.COMPLETION = BUDGET
S_cleanup = S_reached_cleanup[.COMPLETION = NORMAL]
S_cleanup.CURRENT = (pcallcontext_caller)
S_cleanup.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_empty) :: (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (GENERATOR_RESUME pgeneratorop) :: ptask_tail*
pgeneratorop.OBJECT = n_target
pgeneratorop.NAME = "send"
pgeneratorop.ARGUMENTS = [POBJECT n_argument]
pgeneratorop.SELECTION = eps
pgeneratorop.LOOP = eps
~pgeneratorop.STARTPACK
~pgeneratorop.BORROWED
~pgeneratorop.ADVANCE
pdestructionrelease_empty.JOBS = eps
pdestructionrelease_empty.CALLER = (pcallcontext_caller)
pdestructionrelease_empty.ORIGIN = (pgeneratorop.SITE)
S_cleanup.DESTRUCTION.RELEASES = pdestructionrelease_empty :: pdestructionrelease_tail*
S_cleanup.DESTRUCTION.FRAMES = pdestructionframe :: pdestructionframe_tail*
pdestructionframe.FUNCTION = pgenerator.FUNCTION
pdestructionframe.CALLER = (pcallcontext_caller)
pdestructionframe.PENDING = (n_body)
pdestructionframe.VALUE = KNOWN PNULL
pdestructionframe.ORIGIN = (pgeneratorop.SITE)
S_cleanup.OBJECTS[n_target] = GENERATOR pgenerator_closed
pgenerator_closed.FUNCTION = pgenerator.FUNCTION
pgenerator_closed.PHASE = GENERATOR_CLOSED
pgenerator_closed.FRAME = eps
pgenerator_closed.RETURN = eps
pgenerator_closed.VALUE = (POBJECT n_cache)
pgenerator_closed.REFCELL = eps
pgenerator_closed.CLOSURE = eps
pgenerator_closed.CREATION = eps
pgenerator_closed.ACCESS = eps
pgenerator_closed.DELEGATE = eps
~pgenerator_closed.PENDING_INIT
$generator_api_body_producer(S_cleanup, n_target)
$generator_api_body_cleanup(S_cleanup, S_cleanup.TODO) = ((pgeneratorop, ptask_projected*))
ptask_projected* = (DESTRUCTOR_RELEASE pdestructionrelease_empty) :: (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: ptask_tail*
S_projection = $generator_descriptor_view(S_cleanup)
S_projection = S_cleanup[.TODO = ptask_projected*]
$destructor_frame_internal_site(S_cleanup)
$task_nodes(GENERATOR_RESUME pgeneratorop) = [HOBJECT n_target, HOBJECT n_argument]
$node_children(S_cleanup, HOBJECT n_target) = [HOBJECT n_cache]
$weakref_get(S_cleanup, n_weak_factory) = PNULL
$heap_owners($heap_graph(S_cleanup), HOBJECT n_factory) = 0
$heap_owners($heap_graph(S_cleanup), HOBJECT n_target) = 1
$heap_owners($heap_graph(S_cleanup), HOBJECT n_cache) = 1
$heap_owners($heap_graph(S_cleanup), HOBJECT n_argument) = 1
$heap_owners($heap_graph(S_cleanup), HOBJECT n_body) = 2
pclassdesc_owner.METHODS = pmethoddesc :: pmethoddesc_tail*
S_flag = S_cleanup[.CLASSES = $trait_class_set(S_cleanup.CLASSES, pclassdesc_owner[.METHODS = pmethoddesc[.STATIC = false] :: pmethoddesc_tail*])]
~$generator_api_body_producer(S_flag, n_target)
$generator_api_body_cleanup(S_flag, S_flag.TODO) = eps
S_private = S_cleanup[.CLASSES = $trait_class_set(S_cleanup.CLASSES, pclassdesc_owner[.METHODS = pmethoddesc[.VISIBILITY = PROPERTY_PRIVATE] :: pmethoddesc_tail*])]
~$generator_api_body_producer(S_private, n_target)
S_abstract = S_cleanup[.CLASSES = $trait_class_set(S_cleanup.CLASSES, pclassdesc_owner[.METHODS = pmethoddesc[.ABSTRACT = true] :: pmethoddesc_tail*])]
~$generator_api_body_producer(S_abstract, n_target)
S_byref = S_cleanup[.CLASSES = $trait_class_set(S_cleanup.CLASSES, pclassdesc_owner[.METHODS = pmethoddesc[.FUNCTION = pmethoddesc.FUNCTION[.SIGNATURE = pmethoddesc.FUNCTION.SIGNATURE[.BYREF = true]]] :: pmethoddesc_tail*])]
~$generator_api_body_producer(S_byref, n_target)
~$generator_api_body_producer(S_cleanup[.CLASSNAMES = eps], n_target)
$destructor_method(S_cleanup, n_cache) = (pmethoddesc_cache)
S_function = S_cleanup[.OBJECTS[n_target] = GENERATOR pgenerator_closed[.FUNCTION = pmethoddesc_cache.FUNCTION.ORIGIN]]
~$generator_api_body_producer(S_function, n_target)
$generator_api_body_cleanup(S_cleanup, (DESTRUCTOR_FRAME_EXIT pdestructionframe[.PENDING = eps]) :: (GENERATOR_RESUME pgeneratorop) :: ptask_tail*) = eps
$generator_api_body_cleanup(S_cleanup, (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (GENERATOR_RESUME pgeneratorop[.NAME = "throw"]) :: ptask_tail*) = eps
$generator_api_body_cleanup(S_cleanup, (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (GENERATOR_RESUME pgeneratorop[.ARGUMENTS = eps]) :: ptask_tail*) = eps
$generator_api_body_cleanup(S_cleanup[.COMPLETION = UNSUPPORTED "not a public pause"], S_cleanup.TODO) = eps
S_moved = S_cleanup[.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_empty) :: (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: DISCARD :: (GENERATOR_RESUME pgeneratorop) :: ptask_tail*]
$generator_descriptor_view(S_moved) = S_moved
~$call_descriptors_valid(S_moved)
$call_descriptors_valid(S_cleanup)
$heap_valid($heap_graph(S_cleanup))
S_pause = $drive(S_cleanup, 0)
S_pause.COMPLETION = BUDGET
S_pause[.COMPLETION = NORMAL] = S_cleanup
$generator_descriptor_view(S_pause) = S_projection[.COMPLETION = BUDGET]
$call_descriptors_valid(S_pause)
$heap_owners($heap_graph(S_pause), HOBJECT n_factory) = 0
$heap_owners($heap_graph(S_pause), HOBJECT n_target) = 1
$heap_owners($heap_graph(S_pause), HOBJECT n_cache) = 1
$heap_owners($heap_graph(S_pause), HOBJECT n_argument) = 1
$heap_owners($heap_graph(S_pause), HOBJECT n_body) = 2
PhpStep: S_cleanup ~> S_frame_exit
S_frame_exit.TODO = (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (GENERATOR_RESUME pgeneratorop) :: ptask_tail*
S_frame_exit.DESTRUCTION.RELEASES = pdestructionrelease_tail*
S_frame_exit.DESTRUCTION.FRAMES = S_cleanup.DESTRUCTION.FRAMES
S_frame_exit.OBJECTS = S_cleanup.OBJECTS
S_frame_exit.ALLOCATIONS = S_cleanup.ALLOCATIONS
S_frame_exit.STORE = S_cleanup.STORE
S_frame_exit.EVENTS = S_cleanup.EVENTS
$generator_descriptor_view(S_frame_exit) = S_frame_exit[.TODO = (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: ptask_tail*]
$call_descriptors_valid(S_frame_exit)
$heap_valid($heap_graph(S_frame_exit))
S_budget = $drive(S_cleanup, 1)
S_budget.COMPLETION = BUDGET
S_budget[.COMPLETION = NORMAL] = S_frame_exit
$drive(S_pause[.COMPLETION = NORMAL], 1) = S_budget
$call_descriptors_valid(S_budget)
$heap_owners($heap_graph(S_budget), HOBJECT n_factory) = 0
$heap_owners($heap_graph(S_budget), HOBJECT n_target) = 1
$heap_owners($heap_graph(S_budget), HOBJECT n_cache) = 1
$heap_owners($heap_graph(S_budget), HOBJECT n_argument) = 1
$heap_owners($heap_graph(S_budget), HOBJECT n_body) = 2
PhpStep: S_frame_exit ~> S_closed
S_closed.TODO = (THROW_SEARCH n_body) :: (GENERATOR_RESUME pgeneratorop) :: ptask_tail*
S_closed.CURRENT = (pcallcontext_caller)
S_closed.DESTRUCTION.FRAMES = pdestructionframe_tail*
S_closed.OBJECTS = S_cleanup.OBJECTS
S_closed.ALLOCATIONS = S_cleanup.ALLOCATIONS
$lookup(S_closed.ENV, $ptascii("result")) = (n_result_cv)
S_closed.STORE[n_result_cv] = DEFINED pvalue_result
$string_bytes(pvalue_result) = ($ptascii("sentinel"))
$lookup(S_global.ENV, $ptascii("bodyStop")) = (n_body_cv)
S_closed.STORE[n_body_cv] = DEFINED (POBJECT n_body)
$lookup(S_global.ENV, $ptascii("target")) = (n_target_cv)
S_closed.STORE[n_target_cv] = DEFINED PNULL
$generator_api_body_throw(S_closed, pgeneratorop)
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
$heap_owners($heap_graph(S_release), HOBJECT n_cache) = 1
$heap_owners($heap_graph(S_release), HOBJECT n_argument) = 1
$heap_owners($heap_graph(S_release), HOBJECT n_body) = 2
$call_descriptors_valid(S_release)
$heap_valid($heap_graph(S_release))
'''.splitlines() if line.strip()]

review.CASES = {ROW['id']: {'source': ROW['source'], 'stage': STAGE,
                          'checks': CHECKS}}

if __name__ == '__main__':
    raise SystemExit(0 if review.run(None, process_seconds=600) else 1)
