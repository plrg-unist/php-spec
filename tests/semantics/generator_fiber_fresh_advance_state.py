#!/usr/bin/env python3
"""Check source-reached fresh NEXT/SEND phases, real callees, caches and argument roots."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_fiber_fresh_advance_cases.json')
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
def stage(sent):
    return (PARK_STAGE+' -- if pfiber.VM = (pfibervm) '
            '-- if pfibervm.TODO = (FIBER_CONTINUE pfiberapi) :: ptask_saved* '
            '-- if pfiberapi.SENT = (pvalue_sent) '
            f'-- if $string_bytes(pvalue_sent) = ($ptascii("{sent}"))')
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
pgenerator.DELEGATE = eps
pgenerator.PARKED = eps
pgenerator.ACCESS = eps
pgenerator.RETURN = eps
pgenerator.BORROWED = eps
~pgenerator.PENDING_INIT
pfiber.VM = (pfibervm)
~pfibervm.GLOBAL
pfibervm.CURRENT = (pcallcontext_generator)
pfibervm.FRAMES = pframe_generator :: pframe_tail*
pframe_generator.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_generator*
pframe_generator.CONTEXT = (pcallcontext_callback)
pgeneratorop.OBJECT = n_generator
pgeneratorop.LOOP = eps
~pgeneratorop.STARTPACK
~pgeneratorop.BORROWED
pcallcontext_generator.FUNCTION = pgenerator.FUNCTION
S_view = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]
$generator_record_valid(S_view, pgenerator)
$call_current_valid(S_view)
$fiber_vm_valid(S, pfibervm, (n_fiber), eps)
$generator_resume_pairs(S_view, S_view.CURRENT, S_view.FRAMES)
$fiber_generator_callee_valid(S_view, pgenerator, pcallcontext_generator)
$fiber_generator_cached_reference_valid(S_view, pgenerator, pcallcontext_generator)
$fiber_generator_body_id(S_view) = (n_generator)
$fiber_transfer_domain(S_view)
$generator_saved_fiber_ids(S) = [n_generator]
$generator_owners_valid(S)
''')
NAMED = checks(r'''
pcallcontext_generator.TARGET = pgenerator.FUNCTION
pcallcontext_generator.INSTANCE = eps
pcallcontext_generator.RECEIVER = eps
pgenerator.CLOSURE = eps
$lookup(S.ENV, $ptascii("old")) = (n_item)
$lookup(S.ENV, $ptascii("slot")) = (n_input)
S.STORE[n_item] = DEFINED (PINT 7)
S.STORE[n_input] = DEFINED (PINT 9)
n_item =/= n_input
n_item <- S.REFCELLS
$lookup(pfibervm.TABLE.ENV, $ptascii("item")) = (n_item)
pframe_generator.LOCALS = (psymboltable_callback)
$lookup(psymboltable_callback.ENV, $ptascii("old")) = (n_item)
$heap_count(HCELL n_item, $fiber_vm_nodes(pfibervm)) = 2
$generator_reference_producer(S, pgenerator)
''')
SEND = checks(r'''
pgeneratorop.NAME = "send"
pgeneratorop.ARGUMENTS = [POBJECT n_delivered]
$lookup(S.ENV, $ptascii("weakDelivered")) = (n_weak_delivered_cell)
S.STORE[n_weak_delivered_cell] = DEFINED (POBJECT n_weak_delivered)
S.OBJECTS[n_weak_delivered] = WEAKREFERENCE (n_delivered)
$weakref_get(S, n_weak_delivered) = POBJECT n_delivered
$task_nodes(GENERATOR_RESUME pgeneratorop) = [HOBJECT n_generator, HOBJECT n_delivered]
$heap_count(HOBJECT n_delivered, $fiber_vm_nodes(pfibervm)) = 1
''')
FRESH = checks(r'''
pgeneratorop.ADVANCE
pgenerator.FIRST
pgenerator.VALUE = eps
pgenerator.REFCELL = eps
$node_children(S, HOBJECT n_generator) = eps
$lookup(pfibervm.TABLE.ENV, $ptascii("received")) = eps
$heap_owners($heap_graph(S), HCELL n_item) = 3
$heap_owners($heap_graph(S), HOBJECT n_delivered) = 1
$fiber_generator_fresh_advance_valid(S_view, pgeneratorop, pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_advance_valid(S_view, pgeneratorop[.NAME = "current"], pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_advance_valid(S_view, pgeneratorop[.NAME = "throw"], pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_advance_valid(S_view, pgeneratorop[.NAME = "next"], pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_advance_valid(S_view, pgeneratorop[.ARGUMENTS = eps], pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_advance_valid(S_view, pgeneratorop[.ARGUMENTS = [PINT 1, PINT 2]], pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_advance_valid(S_view, pgeneratorop[.ADVANCE = false], pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_advance_valid(S_view, pgeneratorop, pgenerator[.FIRST = false], pcallcontext_generator)
~$fiber_generator_fresh_advance_valid(S_view, pgeneratorop, pgenerator[.VALUE = (PINT 7)], pcallcontext_generator)
~$fiber_generator_fresh_advance_valid(S_view, pgeneratorop, pgenerator[.REFCELL = (n_item)], pcallcontext_generator)
~$fiber_generator_fresh_advance_valid(S_view, pgeneratorop, pgenerator, pcallcontext_callback)
pcallcontext_name = pcallcontext_generator[.NAME = $ptascii("forged74")]
S_name = S_view[.CURRENT = (pcallcontext_name)]
~$call_current_valid(S_name)
~$fiber_generator_fresh_advance_valid(S_name, pgeneratorop, pgenerator, pcallcontext_name)
~$fiber_vm_valid(S, pfibervm[.CURRENT = (pcallcontext_name)], (n_fiber), eps)
$fiber_generator_body_id(S_name) = eps
pcallcontext_receiver = pcallcontext_generator[.RECEIVER = (n_fiber)]
S_receiver = S_view[.CURRENT = (pcallcontext_receiver)]
~$call_current_valid(S_receiver)
~$fiber_generator_fresh_advance_valid(S_receiver, pgeneratorop, pgenerator, pcallcontext_receiver)
~$fiber_vm_valid(S, pfibervm[.CURRENT = (pcallcontext_receiver)], (n_fiber), eps)
$fiber_generator_body_id(S_receiver) = eps
pcallcontext_site = pcallcontext_generator[.CALLSITE = eps]
S_site = S_view[.CURRENT = (pcallcontext_site)]
~$call_current_valid(S_site)
~$fiber_generator_fresh_advance_valid(S_site, pgeneratorop, pgenerator, pcallcontext_site)
~$fiber_vm_valid(S, pfibervm[.CURRENT = (pcallcontext_site)], (n_fiber), eps)
$fiber_generator_body_id(S_site) = eps
~$generator_record_valid(S_view, pgenerator[.FUNCTION = pcallcontext_callback.FUNCTION])
''')
DELIVERED = checks(r'''
~pgeneratorop.ADVANCE
~pgenerator.FIRST
pgenerator.VALUE = eps
pgenerator.REFCELL = (n_item)
$node_children(S, HOBJECT n_generator) = [HCELL n_item]
$lookup(pfibervm.TABLE.ENV, $ptascii("received")) = (n_received)
S.STORE[n_received] = DEFINED (POBJECT n_delivered)
$node_children(S, HCELL n_received) = [HOBJECT n_delivered]
$heap_owners($heap_graph(S), HCELL n_received) = 1
$heap_count(HCELL n_received, $fiber_vm_nodes(pfibervm)) = 1
$heap_owners($heap_graph(S), HOBJECT n_delivered) = 2
~$fiber_generator_fresh_advance_valid(S_view, pgeneratorop, pgenerator, pcallcontext_generator)
S_noarg = S_view[.FRAMES = pframe_generator[.TODO = (GENERATOR_RESUME pgeneratorop[.ARGUMENTS = eps]) :: ptask_generator*] :: pframe_tail*]
$fiber_generator_body_id(S_noarg) = eps
S_twoargs = S_view[.FRAMES = pframe_generator[.TODO = (GENERATOR_RESUME pgeneratorop[.ARGUMENTS = [POBJECT n_delivered, POBJECT n_delivered]]) :: ptask_generator*] :: pframe_tail*]
$fiber_generator_body_id(S_twoargs) = eps
''')
CACHED_AUTH = checks(r'''
$generator_reference_valid(S_view, GENERATOR pgenerator)
$call_reference_operand_valid(S_view, REFERENCE n_item)
S_unmarked = S_view[.REFCELLS = eps]
~$fiber_generator_cached_reference_valid(S_unmarked, pgenerator, pcallcontext_generator)
$fiber_generator_body_id(S_unmarked) = eps
S_line = S_view[.FRAMES = pframe_generator[.TODO = (GENERATOR_RESUME pgeneratorop[.LINE = 0]) :: ptask_generator*] :: pframe_tail*]
$fiber_generator_body_id(S_line) = eps
S_duplicate = S_view[.FRAMES = pframe_generator :: pframe_generator :: pframe_tail*]
$fiber_generator_body_id(S_duplicate) = eps
''')
METHOD = checks(r'''
pgenerator.CLOSURE = eps
pcallcontext_generator.TARGET = METHOD_TARGET n_owner pgenerator.FUNCTION
pcallcontext_generator.RECEIVER = (n_owner)
pcallcontext_generator.INSTANCE = eps
$class_named(S.CLASSNAMES, $ptlc($ptascii("Parent74Self"))) = (porigin_parent)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Leaf74Self"))) = (porigin_leaf)
pcallcontext_generator.LEXICAL_CLASS = (porigin_parent)
pcallcontext_generator.CALLED_CLASS = (porigin_leaf)
$generator_reference_producer(S, pgenerator)
$lookup(pfibervm.TABLE.ENV, $ptascii("item")) = (n_item)
S.STORE[n_item] = DEFINED (POBJECT n_owner)
n_item <- S.REFCELLS
$lookup(S.ENV, $ptascii("owner")) = eps
$lookup(S.ENV, $ptascii("slot")) = eps
$heap_owners($heap_graph(S), HCELL n_item) = 2
$heap_count(HCELL n_item, $fiber_vm_nodes(pfibervm)) = 1
$heap_owners($heap_graph(S), HOBJECT n_owner) = 2
$call_context_roots((pcallcontext_generator)) = [HOBJECT n_owner]
$heap_count(HOBJECT n_owner, $fiber_vm_nodes(pfibervm)) = 1
pcallcontext_receiver = pcallcontext_generator[.RECEIVER = (n_fiber)]
S_receiver = S_view[.CURRENT = (pcallcontext_receiver)]
~$fiber_generator_callee_valid(S_receiver, pgenerator, pcallcontext_receiver)
~$fiber_vm_valid(S, pfibervm[.CURRENT = (pcallcontext_receiver)], (n_fiber), eps)
$fiber_generator_body_id(S_receiver) = eps
pcallcontext_both = pcallcontext_generator[.TARGET = METHOD_TARGET n_fiber pgenerator.FUNCTION][.RECEIVER = (n_fiber)]
S_both = S_view[.CURRENT = (pcallcontext_both)]
~$call_current_valid(S_both)
~$fiber_generator_callee_valid(S_both, pgenerator, pcallcontext_both)
~$fiber_vm_valid(S, pfibervm[.CURRENT = (pcallcontext_both)], (n_fiber), eps)
$fiber_generator_body_id(S_both) = eps
''')
CLOSURE = checks(r'''
pgenerator.CLOSURE = (n_callee)
pcallcontext_generator.TARGET = CLOSURE_TARGET n_callee
pcallcontext_generator.INSTANCE = (n_callee)
pcallcontext_generator.RECEIVER = eps
S.OBJECTS[n_callee] = REALCLOSURE pgenerator.FUNCTION pitem* pstaticcell*
$generator_closure_valid(S_view, pgenerator)
$closure_live_object_valid(S, n_callee)
S_capture = S[.OBJECTS = $object_set(S.OBJECTS, n_callee, REALCLOSURE pgenerator.FUNCTION eps pstaticcell*)]
~$closure_live_object_valid(S_capture, n_callee)
~$fiber_vm_valid(S_capture, pfibervm, (n_fiber), eps)
$heap_owners($heap_graph(S), HOBJECT n_callee) = 1
$call_context_roots((pcallcontext_generator)) = [HOBJECT n_callee]
$lookup(S.ENV, $ptascii("factory")) = eps
$lookup(S.ENV, $ptascii("old")) = (n_item)
$lookup(S.ENV, $ptascii("slot")) = (n_input)
S.STORE[n_item] = DEFINED (PINT 7)
S.STORE[n_input] = DEFINED (PINT 9)
n_item =/= n_input
n_item <- S.REFCELLS
$lookup(pfibervm.TABLE.ENV, $ptascii("slot")) = (n_item)
pframe_generator.LOCALS = (psymboltable_callback)
$lookup(psymboltable_callback.ENV, $ptascii("old")) = (n_item)
~pgeneratorop.ADVANCE
~pgenerator.FIRST
pgenerator.VALUE = eps
pgenerator.REFCELL = (n_item)
$node_children(S, HOBJECT n_generator) = [HCELL n_item]
$heap_owners($heap_graph(S), HCELL n_item) = 5
$heap_count(HCELL n_item, $fiber_vm_nodes(pfibervm)) = 2
pgeneratorop.NAME = "next"
pgeneratorop.ARGUMENTS = eps
$task_nodes(GENERATOR_RESUME pgeneratorop) = [HOBJECT n_generator]
pcallcontext_instance = pcallcontext_generator[.INSTANCE = (n_fiber)]
S_instance = S_view[.CURRENT = (pcallcontext_instance)]
~$fiber_generator_callee_valid(S_instance, pgenerator, pcallcontext_instance)
~$fiber_vm_valid(S, pfibervm[.CURRENT = (pcallcontext_instance)], (n_fiber), eps)
$fiber_generator_body_id(S_instance) = eps
pcallcontext_both = pcallcontext_generator[.TARGET = CLOSURE_TARGET n_fiber][.INSTANCE = (n_fiber)]
S_both = S_view[.CURRENT = (pcallcontext_both)]
~$fiber_generator_callee_valid(S_both, pgenerator, pcallcontext_both)
~$fiber_vm_valid(S, pfibervm[.CURRENT = (pcallcontext_both)], (n_fiber), eps)
$fiber_generator_body_id(S_both) = eps
~$fiber_generator_callee_valid(S_view, pgenerator[.CLOSURE = (n_fiber)], pcallcontext_generator)
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
SEND_END = checks(r'''
n_delivered <- S_done.DESTRUCTION.CALLED
~((HOBJECT n_delivered) <- S_done.ALLOCATIONS)
''')
CASES={
 'i74-advancing-named-send-argument-only':{'source':ROWS['i74-fresh-named-reference-send-buffer']['source'],'stage':stage('before74'),
   'checks':[*COMMON,*NAMED,*SEND,*FRESH,*ENDING,*SEND_END]},
 'i74-delivered-named-send-cache-and-local':{'source':ROWS['i74-fresh-named-reference-send-buffer']['source'],'stage':stage('after74'),
   'checks':[*COMMON,*NAMED,*SEND,*DELIVERED,'$heap_owners($heap_graph(S), HCELL n_item) = 4',*CACHED_AUTH,*ENDING,*SEND_END]},
 'i74-method-self-cache-supplied-abort':{'source':ROWS['i74-fresh-method-reference-send-self-abort']['source'],'stage':THROW_STAGE,
   'checks':[*COMMON,*SEND,*DELIVERED,*METHOD,*CACHED_AUTH,*ENDING,*SEND_END,'n_owner <- S_done.DESTRUCTION.CALLED','~((HOBJECT n_owner) <- S_done.ALLOCATIONS)']},
 'i74-closure-reference-second-stage':{'source':ROWS['i74-fresh-closure-reference-next-two-stage']['source'],'stage':stage('after74'),
   'checks':[*COMMON,*CLOSURE,*CACHED_AUTH,*ENDING,'~((HOBJECT n_callee) <- S_done.ALLOCATIONS)']},
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
