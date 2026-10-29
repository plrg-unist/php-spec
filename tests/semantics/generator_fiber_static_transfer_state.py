#!/usr/bin/env python3
"""Check source-reached static CURRENT/NEXT/SEND frames, caches and argument roots."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_fiber_static_transfer_cases.json')
INPUT_BYTES = {p:p.read_bytes() for p in (Path(__file__),CATALOG,Path(review.__file__))}
ROWS = {r['id']:r for r in json.loads(INPUT_BYTES[CATALOG])}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest()==row['source_sha256']

def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]

PARK_STAGE = (
    'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
    '-- if pconfigcall.KIND = INTRINSIC_FIBER_RESUME '
    '-- if pconfigcall.OWNER = (n_fiber) '
    '-- if S.OBJECTS[n_fiber] = FIBER pfiber '
    '-- if pfiber.STATUS = FIBER_SUSPENDED')
THROW_STAGE = PARK_STAGE.replace('INTRINSIC_FIBER_RESUME','INTRINSIC_FIBER_THROW')
COMMON = checks(r'''
S.COMPLETION = NORMAL
S.ACTIVEFIBER = eps
S.CURRENT = eps
S.FRAMES = eps
S.FIBERCALLERS = eps
S.FIBERCLOSERS = eps
$lookup(S.ENV, $ptascii("g")) = (n_generator_cell)
S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)
S.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_RUNNING
pgenerator.FRAME = eps
pgenerator.CLOSURE = eps
pgenerator.DELEGATE = eps
pgenerator.PARKED = eps
pgenerator.ACCESS = eps
pgenerator.RETURN = eps
pgenerator.BORROWED = eps
~pgenerator.PENDING_INIT
$class_method_origin(S.CLASSES, pgenerator.FUNCTION) = (pmethoddesc)
pmethoddesc.STATIC
pmethoddesc.OWNER = porigin_parent
pfunction = pmethoddesc.FUNCTION
pfiber.VM = (pfibervm)
~pfibervm.GLOBAL
pfibervm.CURRENT = (pcallcontext_generator)
pfibervm.FRAMES = pframe_generator :: pframe_tail*
pframe_generator.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_generator*
pframe_generator.CONTEXT = (pcallcontext_callback)
pgeneratorop.OBJECT = n_generator
pgeneratorop.LOOP = eps
~pgeneratorop.ADVANCE
~pgeneratorop.STARTPACK
~pgeneratorop.BORROWED
pcallcontext_generator.FUNCTION = pgenerator.FUNCTION
pcallcontext_generator.INSTANCE = eps
pcallcontext_generator.RECEIVER = eps
pcallcontext_generator.LEXICAL_CLASS = (porigin_parent)
pcallcontext_generator.CALLED_CLASS = (porigin_leaf)
$target_nodes(pcallcontext_generator.TARGET) = eps
$call_context_roots((pcallcontext_generator)) = eps
S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]
$generator_record_valid(S_view, pgenerator)
$call_current_valid(S_view)
$fiber_vm_valid(S, pfibervm, (n_fiber), eps)
$generator_resume_pairs(S_view, S_view.CURRENT, S_view.FRAMES)
$fiber_generator_static_target(pcallcontext_generator.TARGET, pgenerator.FUNCTION)
$fiber_generator_callee_valid(S_view, pgenerator, pcallcontext_generator)
$fiber_generator_cached_reference_valid(S_view, pgenerator, pcallcontext_generator)
$fiber_generator_body_id(S_view) = (n_generator)
$fiber_transfer_domain(S_view)
$generator_saved_fiber_ids(S) = [n_generator]
$generator_owners_valid(S)
''')
STATIC = checks(r'''
pcallcontext_generator.TARGET = STATIC_METHOD_TARGET porigin_leaf pgenerator.FUNCTION
$lookup(S.ENV, $ptascii("weakSelector")) = (n_weak_selector_cell)
S.STORE[n_weak_selector_cell] = DEFINED (POBJECT n_weak_selector)
S.OBJECTS[n_weak_selector] = WEAKREFERENCE (n_selector)
$weakref_get(S, n_weak_selector) = PNULL
~((HOBJECT n_selector) <- S.ALLOCATIONS)
n_selector <- S.DESTRUCTION.CALLED
$heap_owners($heap_graph(S), HOBJECT n_selector) = 0
$heap_count(HOBJECT n_selector, $fiber_vm_nodes(pfibervm)) = 0
''')
SCOPED = checks(r'''
pcallcontext_generator.TARGET = SCOPED_TARGET porigin_leaf pgenerator.FUNCTION porigin_leaf eps poperand_selector
$operand_nodes(poperand_selector) = eps
''')
AUTHENTICATION = checks(r'''
pcallcontext_name = pcallcontext_generator[.NAME = $ptascii("forged73")]
S_name = S_view[.CURRENT = (pcallcontext_name)]
~$call_current_valid(S_name)
~$fiber_vm_valid(S, pfibervm[.CURRENT = (pcallcontext_name)], (n_fiber), eps)
$fiber_generator_body_id(S_name) = eps
pcallcontext_receiver = pcallcontext_generator[.RECEIVER = (n_fiber)]
S_receiver = S_view[.CURRENT = (pcallcontext_receiver)]
~$fiber_generator_callee_valid(S_receiver, pgenerator, pcallcontext_receiver)
~$fiber_vm_valid(S, pfibervm[.CURRENT = (pcallcontext_receiver)], (n_fiber), eps)
$fiber_generator_body_id(S_receiver) = eps
pcallcontext_called = pcallcontext_generator[.CALLED_CLASS = (porigin_parent)]
S_called = S_view[.CURRENT = (pcallcontext_called)]
~$call_current_valid(S_called)
~$fiber_vm_valid(S, pfibervm[.CURRENT = (pcallcontext_called)], (n_fiber), eps)
$fiber_generator_body_id(S_called) = eps
S_line = S_view[.FRAMES = pframe_generator[.TODO = (GENERATOR_RESUME pgeneratorop[.LINE = 0]) :: ptask_generator*] :: pframe_tail*]
$fiber_generator_body_id(S_line) = eps
S_duplicate = S_view[.FRAMES = pframe_generator :: pframe_generator :: pframe_tail*]
$fiber_generator_body_id(S_duplicate) = eps
''')
FRESH_REFERENCE = checks(r'''
pfunction.SIGNATURE.BYREF
$generator_reference_producer(S, pgenerator)
pgenerator.FIRST
pgenerator.VALUE = eps
pgenerator.REFCELL = eps
pgeneratorop.NAME = "current"
pgeneratorop.ARGUMENTS = eps
$task_nodes(GENERATOR_RESUME pgeneratorop) = [HOBJECT n_generator]
$node_children(S, HOBJECT n_generator) = eps
$lookup(S.ENV, $ptascii("old")) = (n_item)
$lookup(S.ENV, $ptascii("slot")) = (n_input)
S.STORE[n_item] = DEFINED (PINT 7)
S.STORE[n_input] = DEFINED (PINT 9)
n_item =/= n_input
n_item <- S.REFCELLS
$lookup(pfibervm.TABLE.ENV, $ptascii("item")) = (n_item)
pframe_generator.LOCALS = (psymboltable_callback)
$lookup(psymboltable_callback.ENV, $ptascii("old")) = (n_item)
$heap_owners($heap_graph(S), HCELL n_item) = 3
$heap_count(HCELL n_item, $fiber_vm_nodes(pfibervm)) = 2
S_arg = S_view[.FRAMES = pframe_generator[.TODO = (GENERATOR_RESUME pgeneratorop[.ARGUMENTS = [PINT 3]]) :: ptask_generator*] :: pframe_tail*]
$fiber_generator_body_id(S_arg) = eps
''')
SCOPED_SOURCE_AUTH = checks(r'''
pcallcontext_parent = pcallcontext_generator[.TARGET = SCOPED_TARGET porigin_parent pgenerator.FUNCTION porigin_parent eps (KNOWN (PSTRING ($ptascii("Parent73CurrentRef"))))][.CALLED_CLASS = (porigin_parent)]
S_parent = S_view[.CURRENT = (pcallcontext_parent)]
$target_function(S_parent, pcallcontext_parent.TARGET) = (pfunction)
$fiber_generator_static_target(pcallcontext_parent.TARGET, pgenerator.FUNCTION)
~$call_current_valid(S_parent)
~$fiber_vm_valid(S, pfibervm[.CURRENT = (pcallcontext_parent)], (n_fiber), eps)
$fiber_generator_body_id(S_parent) = eps
''')
NEXT_VALUE = checks(r'''
~pfunction.SIGNATURE.BYREF
~pgenerator.FIRST
pgenerator.REFCELL = eps
pgeneratorop.NAME = "next"
pgeneratorop.ARGUMENTS = eps
$task_nodes(GENERATOR_RESUME pgeneratorop) = [HOBJECT n_generator]
$lookup(S.ENV, $ptascii("weakCache")) = (n_weak_cache_cell)
S.STORE[n_weak_cache_cell] = DEFINED (POBJECT n_weak_cache)
S.OBJECTS[n_weak_cache] = WEAKREFERENCE (n_cache)
pgenerator.VALUE = (POBJECT n_cache)
$weakref_get(S, n_weak_cache) = POBJECT n_cache
$node_children(S, HOBJECT n_generator) = [HOBJECT n_cache]
$heap_owners($heap_graph(S), HOBJECT n_cache) = 1
$lookup(pfibervm.TABLE.ENV, $ptascii("item")) = eps
$heap_count(HOBJECT n_cache, $fiber_vm_nodes(pfibervm)) = 0
''')
NEXT_SOURCE=ROWS['i73-scoped-next-byval-sole-cache']['source']
CURRENT_LINE=next(i for i,line in enumerate(NEXT_SOURCE.splitlines(),1) if line=='$g->current();')
CURRENT_COMPATIBILITY=checks(r'''
porigin_current = PORIGIN 0 ([PCINDEX 5, PCFIELD 0])
$generator_source_method(S_view, porigin_current, $ptascii("current"))
''')+[f'pgeneratorop_current = pgeneratorop[.NAME = "current"][.SITE = porigin_current][.LINE = {CURRENT_LINE}]']+checks(r'''
S_current = S_view[.FRAMES = pframe_generator[.TODO = (GENERATOR_RESUME pgeneratorop_current) :: ptask_generator*][.ORIGIN = (porigin_current)] :: pframe_tail*]
$generator_resumption_valid(S_current, pgeneratorop_current)
$generator_resume_pairs(S_current, S_current.CURRENT, S_current.FRAMES)
$call_current_valid(S_current)
$fiber_generator_callee_valid(S_current, pgenerator, pcallcontext_generator)
$fiber_generator_cached_reference_valid(S_current, pgenerator, pcallcontext_generator)
$fiber_generator_body_id(S_current) = (n_generator)
''')
NEXT_REFERENCE = checks(r'''
pfunction.SIGNATURE.BYREF
$generator_reference_producer(S, pgenerator)
~pgenerator.FIRST
pgenerator.VALUE = eps
pgenerator.REFCELL = (n_item)
pgeneratorop.NAME = "next"
pgeneratorop.ARGUMENTS = eps
$task_nodes(GENERATOR_RESUME pgeneratorop) = [HOBJECT n_generator]
$node_children(S, HOBJECT n_generator) = [HCELL n_item]
$lookup(S.ENV, $ptascii("old")) = (n_item)
$lookup(S.ENV, $ptascii("slot")) = (n_input)
S.STORE[n_input] = DEFINED (PINT 9)
n_item =/= n_input
n_item <- S.REFCELLS
$lookup(pfibervm.TABLE.ENV, $ptascii("item")) = (n_item)
S.STORE[n_item] = DEFINED (PARRAY n_live)
$lookup(S.ENV, $ptascii("copy")) = (n_copy_cell)
S.STORE[n_copy_cell] = DEFINED (PARRAY n_copy)
n_copy =/= n_live
$entry_lookup(S.ARRAYS[n_copy].ITEMS, KINT 0) = (DIRECT (POBJECT n_old))
$entry_lookup(S.ARRAYS[n_live].ITEMS, KINT 0) = (DIRECT (POBJECT n_next))
n_old =/= n_next
$object_name(S, n_old) = $ptascii("Old73NextRef")
$object_name(S, n_next) = $ptascii("Next73NextRef")
$heap_owners($heap_graph(S), HCELL n_item) = 3
$heap_count(HCELL n_item, $fiber_vm_nodes(pfibervm)) = 1
$heap_owners($heap_graph(S), HARRAY n_copy) = 1
$heap_owners($heap_graph(S), HARRAY n_live) = 1
$heap_owners($heap_graph(S), HOBJECT n_old) = 1
$heap_owners($heap_graph(S), HOBJECT n_next) = 1
$node_children(S, HCELL n_item) = [HARRAY n_live]
$generator_reference_valid(S_view, GENERATOR pgenerator)
$call_reference_operand_valid(S_view, REFERENCE n_item)
S_unmarked = S_view[.REFCELLS = eps]
~$fiber_generator_cached_reference_valid(S_unmarked, pgenerator, pcallcontext_generator)
$fiber_generator_body_id(S_unmarked) = eps
''')
SEND_VALUE = checks(r'''
~pfunction.SIGNATURE.BYREF
~pgenerator.FIRST
pgenerator.REFCELL = eps
pgeneratorop.NAME = "send"
pgeneratorop.ARGUMENTS = [POBJECT n_delivered]
$lookup(S.ENV, $ptascii("weakCache")) = (n_weak_cache_cell)
S.STORE[n_weak_cache_cell] = DEFINED (POBJECT n_weak_cache)
S.OBJECTS[n_weak_cache] = WEAKREFERENCE (n_cache)
pgenerator.VALUE = (POBJECT n_cache)
$lookup(S.ENV, $ptascii("weakDelivered")) = (n_weak_delivered_cell)
S.STORE[n_weak_delivered_cell] = DEFINED (POBJECT n_weak_delivered)
S.OBJECTS[n_weak_delivered] = WEAKREFERENCE (n_delivered)
$weakref_get(S, n_weak_delivered) = POBJECT n_delivered
$weakref_get(S, n_weak_cache) = POBJECT n_cache
$lookup(pfibervm.TABLE.ENV, $ptascii("received")) = (n_received)
S.STORE[n_received] = DEFINED (POBJECT n_delivered)
$node_children(S, HCELL n_received) = [HOBJECT n_delivered]
$heap_owners($heap_graph(S), HCELL n_received) = 1
$heap_owners($heap_graph(S), HOBJECT n_delivered) = 2
$heap_owners($heap_graph(S), HOBJECT n_cache) = 1
$node_children(S, HOBJECT n_generator) = [HOBJECT n_cache]
$task_nodes(GENERATOR_RESUME pgeneratorop) = [HOBJECT n_generator, HOBJECT n_delivered]
$heap_count(HOBJECT n_delivered, $fiber_vm_nodes(pfibervm)) = 1
$heap_count(HCELL n_received, $fiber_vm_nodes(pfibervm)) = 1
S_noarg = S_view[.FRAMES = pframe_generator[.TODO = (GENERATOR_RESUME pgeneratorop[.ARGUMENTS = eps]) :: ptask_generator*] :: pframe_tail*]
$fiber_generator_body_id(S_noarg) = eps
S_twoargs = S_view[.FRAMES = pframe_generator[.TODO = (GENERATOR_RESUME pgeneratorop[.ARGUMENTS = [POBJECT n_delivered, POBJECT n_delivered]]) :: ptask_generator*] :: pframe_tail*]
$fiber_generator_body_id(S_twoargs) = eps
''')
ENDING = checks(r'''
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
S_zero = $drive_steps(S, 0)
S_zero.COMPLETION = BUDGET
S_zero[.COMPLETION = NORMAL] = S
S_one_budget = $drive_steps(S, 1)
S_one_budget.COMPLETION = BUDGET
S_one = S_one_budget[.COMPLETION = NORMAL]
$drive_steps(S, 2) = $drive_steps(S_one, 1)
S_done = $drive_steps(S_one, 4000)
$drive_steps(S, 4000) = S_done
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.FRAMES = eps
S_done.CURRENT = eps
S_done.ACTIVEFIBER = eps
S_done.FIBERCALLERS = eps
S_done.FIBERCLOSERS = eps
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
''')
CACHE_END = checks(r'''
n_cache <- S_done.DESTRUCTION.CALLED
~((HOBJECT n_cache) <- S_done.ALLOCATIONS)
''')
ARRAY_END = checks(r'''
n_old <- S_done.DESTRUCTION.CALLED
n_next <- S_done.DESTRUCTION.CALLED
~((HOBJECT n_old) <- S_done.ALLOCATIONS)
~((HOBJECT n_next) <- S_done.ALLOCATIONS)
''')
SEND_END = checks(r'''
n_delivered <- S_done.DESTRUCTION.CALLED
~((HOBJECT n_delivered) <- S_done.ALLOCATIONS)
''')

def scope(parent,leaf):
    return [f'$class_named(S.CLASSNAMES, $ptlc($ptascii("{parent}"))) = (porigin_parent)',
            f'$class_named(S.CLASSNAMES, $ptlc($ptascii("{leaf}"))) = (porigin_leaf)']

CASES={
 'i73-fresh-current-shared-reference':{'source':ROWS['i73-scoped-current-byref-snapshot']['source'],'stage':PARK_STAGE,
   'checks':[*scope('Parent73CurrentRef','Leaf73CurrentRef'),*COMMON,*SCOPED,*FRESH_REFERENCE,*SCOPED_SOURCE_AUTH,*AUTHENTICATION,*ENDING]},
 'i73-cached-next-sole-value':{'source':NEXT_SOURCE,'stage':PARK_STAGE,
   'checks':[*scope('Parent73NextValue','Leaf73NextValue'),*COMMON,*SCOPED,*NEXT_VALUE,*CURRENT_COMPATIBILITY,*AUTHENTICATION,*ENDING,*CACHE_END]},
 'i73-cached-next-reference-array-cow':{'source':ROWS['i73-static-next-byref-array-copy']['source'],'stage':PARK_STAGE,
   'checks':[*scope('Parent73NextRef','Leaf73NextRef'),*COMMON,*STATIC,*NEXT_REFERENCE,*AUTHENTICATION,*ENDING,*ARRAY_END]},
 'i73-send-value-buffer-and-local':{'source':ROWS['i73-static-send-byval-buffer-abort']['source'],'stage':THROW_STAGE,
   'checks':[*scope('Parent73SendValue','Leaf73SendValue'),*COMMON,*STATIC,*SEND_VALUE,*AUTHENTICATION,*ENDING,*CACHE_END,*SEND_END]},
}

def run(selected):
    revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=review.ROOT,text=True).strip()
    review.CASES=CASES;original=review.recorded;raw=None
    def recorded(command,directory,stem,environment,cap):
        nonlocal raw
        raw=directory.parent
        return original(command,directory,stem,environment,cap)
    review.recorded=recorded
    try:passed=review.run(selected,process_seconds=300)
    finally:review.recorded=original
    stable=INPUT_BYTES=={path:path.read_bytes() for path in INPUT_BYTES}
    head_stable=revision==subprocess.check_output(['git','rev-parse','HEAD'],cwd=review.ROOT,text=True).strip()
    p=raw/'report.json';r=json.loads(p.read_bytes())
    r.update(author_inputs={str(path):hashlib.sha256(data).hexdigest() for path,data in INPUT_BYTES.items()},author_inputs_stable=stable,head_stable=head_stable,passed=passed and stable and head_stable)
    p.write_text(json.dumps(r,indent=2)+'\n')
    return r['passed']

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--case',action='append')
    raise SystemExit(0 if run(parser.parse_args().case) else 1)
