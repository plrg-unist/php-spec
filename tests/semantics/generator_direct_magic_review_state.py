#!/usr/bin/env python3
"""Check direct magic Gen owners through alias retirement, abort and siblings."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_direct_magic_cases.json')
INPUT_BYTES = {path: path.read_bytes() for path in (Path(__file__), CATALOG, Path(review.__file__))}
ROWS = {row['id']: row for row in json.loads(INPUT_BYTES[CATALOG])}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


PARK_STAGE = (
    'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
    '-- if pconfigcall.KIND = INTRINSIC_FIBER_THROW '
    '-- if pconfigcall.OWNER = (n_fiber) '
    '-- if S.ACTIVEFIBER = eps '
    '-- if S.OBJECTS[n_fiber] = FIBER pfiber '
    '-- if pfiber.STATUS = FIBER_SUSPENDED')

PARK = checks(r'''
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
S.FIBERCALLERS = eps
S.FIBERCLOSERS = eps
S.GC.ACTIVE = eps
S.GENERATORINPUTS = eps
$lookup(S.ENV, $ptascii("g")) = (n_generator_cell)
S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)
S.OBJECTS[n_generator] = GENERATOR pgenerator
pgenerator.PHASE = GENERATOR_RUNNING
pgenerator.FRAME = eps
pgenerator.CLOSURE = eps
pgenerator.VALUE = (POBJECT n_token)
pgenerator.REFCELL = eps
pgenerator.CREATION = (pgeneratorcreation)
pgeneratorcreation.CLOSURE = eps
pgeneratorcreation.ANCESTORS = eps
pgeneratorcreation.CALLEE = MAGIC_METHOD_TARGET pmagicmethodcall n_arguments ([POBJECT n_token])
pgeneratorcreation.CREATOR_TARGET = pgeneratorcreation.CALLEE
pgeneratorcreation.SITE = pmagicmethodcall.SITE
pgeneratorcreation.CREATOR.FUNCTION = pmagicmethodcall.METHOD
pgeneratorcreation.CREATOR.CALLSITE = (pmagicmethodcall.SITE)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base85R"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Leaf85R"))) = (porigin_leaf)
pgeneratorcreation.CREATOR.LEXICAL_CLASS = (porigin_base)
pgeneratorcreation.CREATOR.CALLED_CLASS = (porigin_leaf)
pmagicmethodcall.CLASS = porigin_leaf
pmagicmethodcall.OBJECT = n_maker
pmagicmethodcall.NAME = $ptascii("open")
pmagicmethodcall.CALLER = eps
pmagicmethodcall.OWNER = 0
|pmagicmethodcall.ARGUMENTS| = 1
S.OBJECTS[n_maker] = INSTANCE porigin_leaf
(HOBJECT n_maker) <- S.ALLOCATIONS
$lookup(S.ENV, $ptascii("maker")) = eps
$(n_arguments < |S.ARRAYS|)
~((HARRAY n_arguments) <- S.ALLOCATIONS)
S.ARRAYS[n_arguments].ITEMS = [ENTRY (KINT 0) (ALIAS n_alias)]
~((HCELL n_alias) <- S.ALLOCATIONS)
S.ARRAYS[n_arguments] =/= $magic_method_array([POBJECT n_token], 0)
$magic_method_descriptor(S, pmagicmethodcall)
~$magic_method_pending(S, pmagicmethodcall, n_arguments, [POBJECT n_token])
~$magic_method_entered(S, S.CURRENT, S.FRAMES, pmagicmethodcall, n_arguments, [POBJECT n_token])
$target_function(S, pgeneratorcreation.CALLEE) = eps
$class_method_origin(S.CLASSES, pmagicmethodcall.METHOD) = (pmethoddesc)
pmethoddesc.OWNER = porigin_base
pmethoddesc.NAME = $ptascii("__call")
~pmethoddesc.STATIC
~pmethoddesc.FUNCTION.SIGNATURE.BYREF
$function_generator(S, pmethoddesc.FUNCTION)
$target_function(S, METHOD_TARGET n_maker pmagicmethodcall.METHOD) = (pmethoddesc.FUNCTION)
$generator_creation_record_valid(S, pgenerator)
S_bad_links = S[.LINKEDPARENTS = S.LINKEDPARENTS ++ S.LINKEDPARENTS]
$magic_method_descriptor(S_bad_links, pmagicmethodcall)
~$class_links_valid(S_bad_links)
~$generator_creation_record_valid(S_bad_links, pgenerator)
$lookup(S.ENV, $ptascii("weakMaker")) = (n_weak_maker_cell)
S.STORE[n_weak_maker_cell] = DEFINED (POBJECT n_weak_maker)
$weakref_get(S, n_weak_maker) = POBJECT n_maker
pfiber.VM = (pfibervm)
~pfibervm.GLOBAL
pfibervm.CURRENT = (pcallcontext_generator)
pfibervm.FRAMES = pframe_send :: pframe_tail*
pframe_send.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_send*
pgeneratorop.OBJECT = n_generator
pgeneratorop.NAME = "send"
pgeneratorop.ARGUMENTS = [POBJECT n_input]
pgeneratorop.LOOP = eps
~pgeneratorop.ADVANCE
~pgeneratorop.STARTPACK
~pgeneratorop.BORROWED
$task_nodes(GENERATOR_RESUME pgeneratorop) = [HOBJECT n_generator, HOBJECT n_input]
pcallcontext_generator.TARGET = pgeneratorcreation.CALLEE
pcallcontext_generator.FUNCTION = pgenerator.FUNCTION
pcallcontext_generator.CALLSITE = (pmagicmethodcall.SITE)
pcallcontext_generator.LINE = pmagicmethodcall.LINE
pcallcontext_generator.LEXICAL_CLASS = (porigin_base)
pcallcontext_generator.CALLED_CLASS = (porigin_leaf)
pcallcontext_generator.RECEIVER = (n_maker)
pcallcontext_generator.INSTANCE = eps
pcallcontext_generator.ARGC = 2
pcallcontext_generator.EXTRA = eps
pcallcontext_generator.NAMED = eps
pcallcontext_generator.WRAPPER = eps
pcallcontext_generator.HOLES = eps
$lookup(pfibervm.TABLE.ENV, $ptascii("arguments")) = eps
$lookup(pfibervm.TABLE.ENV, $ptascii("alias")) = eps
$lookup(pfibervm.TABLE.ENV, $ptascii("received")) = eps
$object_name(S, n_token) = $ptascii("Token85R")
$object_name(S, n_input) = $ptascii("Input85R")
$node_children(S, HOBJECT n_generator) = [HOBJECT n_token]
H = $heap_graph(S)
$heap_owners(H, HOBJECT n_maker) = 1
$heap_owners(H, HOBJECT n_token) = 1
$heap_owners(H, HOBJECT n_input) = 1
$heap_owners(H, HARRAY n_arguments) = 0
$heap_owners(H, HCELL n_alias) = 0
$heap_count(HOBJECT n_maker, $fiber_vm_nodes(pfibervm)) = 1
$heap_count(HOBJECT n_input, $fiber_vm_nodes(pfibervm)) = 1
$heap_count(HARRAY n_arguments, $fiber_vm_nodes(pfibervm)) = 0
$heap_count(HCELL n_alias, $fiber_vm_nodes(pfibervm)) = 0
S_live = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]
$generator_creation_required(S_live, pcallcontext_generator)
$generator_creation_owner(S_live) = (n_generator)
$generator_creation_selected(S_live, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
$generator_creation_context_valid(S_live, pgenerator, pcallcontext_generator)
$fiber_generator_callee_valid(S_live, pgenerator, pcallcontext_generator)
~$magic_method_frame(S_live, pcallcontext_generator, pframe_send, pframe_tail*, pmagicmethodcall, n_arguments, [POBJECT n_token])
$magic_method_entered(S_live, S_live.CURRENT, S_live.FRAMES, pmagicmethodcall, n_arguments, [POBJECT n_token])
$target_function(S_live, pgeneratorcreation.CALLEE) = (pmethoddesc.FUNCTION)
$fiber_generator_body_id(S_live) = (n_generator)
$fiber_generator_transfer(S_live)
$call_current_valid(S_live)
$generator_owners_valid(S)
$call_descriptors_valid(S)
$heap_valid(H)
pgenerator_missing = pgenerator[.CREATION = eps]
S_missing = $generator_set(S_live, n_generator, pgenerator_missing)
$generator_creation_owner(S_missing) = (n_generator)
~$generator_creation_selected(S_missing, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
~$magic_method_entered(S_missing, S_missing.CURRENT, S_missing.FRAMES, pmagicmethodcall, n_arguments, [POBJECT n_token])
$target_function(S_missing, pgeneratorcreation.CALLEE) = eps
~$fiber_generator_callee_valid(S_missing, pgenerator_missing, pcallcontext_generator)
~$call_current_valid(S_missing)
pcallcontext_bad_count = pcallcontext_generator[.ARGC = 1]
S_bad_count = S_live[.CURRENT = (pcallcontext_bad_count)]
~$magic_method_entered(S_bad_count, S_bad_count.CURRENT, S_bad_count.FRAMES, pmagicmethodcall, n_arguments, [POBJECT n_token])
~$fiber_generator_callee_valid(S_bad_count, pgenerator, pcallcontext_bad_count)
pcallcontext_bad_receiver = pcallcontext_generator[.RECEIVER = (n_input)]
S_bad_receiver = S_live[.CURRENT = (pcallcontext_bad_receiver)]
~$magic_method_entered(S_bad_receiver, S_bad_receiver.CURRENT, S_bad_receiver.FRAMES, pmagicmethodcall, n_arguments, [POBJECT n_token])
pcallcontext_bad_called = pcallcontext_generator[.CALLED_CLASS = (porigin_base)]
S_bad_called = S_live[.CURRENT = (pcallcontext_bad_called)]
~$magic_method_entered(S_bad_called, S_bad_called.CURRENT, S_bad_called.FRAMES, pmagicmethodcall, n_arguments, [POBJECT n_token])
S_no_owner = S_live[.FRAMES = eps]
$generator_creation_owner(S_no_owner) = eps
~$magic_method_entered(S_no_owner, S_no_owner.CURRENT, S_no_owner.FRAMES, pmagicmethodcall, n_arguments, [POBJECT n_token])
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
S_done.CURRENT = eps
S_done.FRAMES = eps
S_done.ACTIVEFIBER = eps
S_done.FIBERCALLERS = eps
$call_descriptors_valid(S_done)
$heap_valid($heap_graph(S_done))
~((HOBJECT n_maker) <- S_done.ALLOCATIONS)
~((HOBJECT n_token) <- S_done.ALLOCATIONS)
~((HOBJECT n_input) <- S_done.ALLOCATIONS)
n_maker <- S_done.DESTRUCTION.CALLED
n_token <- S_done.DESTRUCTION.CALLED
n_input <- S_done.DESTRUCTION.CALLED
''')

CLOSE_STAGE = (
    'S.TODO = (GENERATOR_CLOSE_ENTER pgenclose) :: ptask_tail* '
    '-- if S.OBJECTS[pgenclose.OBJECT] = GENERATOR pgenerator_a '
    '-- if pgenerator_a.CREATION = (pgeneratorcreation_a)')

SIBLING = checks(r'''
S.COMPLETION = NORMAL
S.CURRENT = eps
S.FRAMES = eps
pgenclose.FRAME = (pframe_a)
pgenclose.CONTEXT = pcallcontext_a
pframe_a.CONTEXT = (pcallcontext_a)
pgenerator_a.PHASE = GENERATOR_CLOSING
pgenerator_a.FRAME = eps
pgeneratorcreation_a.CALLEE = MAGIC_METHOD_TARGET pmagicmethodcall_a n_arguments_a ([PINT 85])
pgeneratorcreation_a.CREATOR_TARGET = pgeneratorcreation_a.CALLEE
pgeneratorcreation_a.SITE = pmagicmethodcall_a.SITE
pmagicmethodcall_a.NAME = $ptascii("first")
pcallcontext_a.TARGET = pgeneratorcreation_a.CALLEE
pcallcontext_a.CALLSITE = (pmagicmethodcall_a.SITE)
pcallcontext_a.RECEIVER = (pmagicmethodcall_a.OBJECT)
$lookup(S.ENV, $ptascii("gb")) = (n_gb_cell)
S.STORE[n_gb_cell] = DEFINED (POBJECT n_gb)
n_gb =/= pgenclose.OBJECT
S.OBJECTS[n_gb] = GENERATOR pgenerator_b
pgenerator_b.PHASE = GENERATOR_FRESH
pgenerator_b.FRAME = (pframe_b)
pframe_b.CONTEXT = (pcallcontext_b)
pgenerator_b.CREATION = (pgeneratorcreation_b)
pgeneratorcreation_b.CALLEE = MAGIC_METHOD_TARGET pmagicmethodcall_b n_arguments_b ([PINT 86])
pgeneratorcreation_b.CREATOR_TARGET = pgeneratorcreation_b.CALLEE
pgeneratorcreation_b.SITE = pmagicmethodcall_b.SITE
pmagicmethodcall_b.NAME = $ptascii("second")
pcallcontext_b.TARGET = pgeneratorcreation_b.CALLEE
pcallcontext_b.CALLSITE = (pmagicmethodcall_b.SITE)
pcallcontext_b.RECEIVER = (pmagicmethodcall_b.OBJECT)
pgenerator_a.FUNCTION = pgenerator_b.FUNCTION
pcallcontext_a.FUNCTION = pcallcontext_b.FUNCTION
pmagicmethodcall_a.METHOD = pmagicmethodcall_b.METHOD
pmagicmethodcall_a.CLASS = pmagicmethodcall_b.CLASS
pmagicmethodcall_a.OBJECT =/= pmagicmethodcall_b.OBJECT
pmagicmethodcall_a.SITE =/= pmagicmethodcall_b.SITE
pgeneratorcreation_a.CALLEE =/= pgeneratorcreation_b.CALLEE
$magic_method_descriptor(S, pmagicmethodcall_a)
$magic_method_descriptor(S, pmagicmethodcall_b)
$generator_creation_record_valid(S, pgenerator_a)
$generator_creation_record_valid(S, pgenerator_b)
S_view = $generator_close_frame_scope(S, pframe_a)
$generator_creation_owner(S_view) = (pgenclose.OBJECT)
$generator_creation_selected(S_view, pgeneratorcreation_a.CALLEE, pgeneratorcreation_a.SITE)
$magic_method_entered(S_view, S_view.CURRENT, S_view.FRAMES, pmagicmethodcall_a, n_arguments_a, [PINT 85])
$generator_close_enter_valid(S, pgenclose)
$call_current_valid(S_view)
$generator_retained_nodes(S_view, S_view.ALLOCATIONS, pcallcontext_b)
S_sibling = S_view[.CURRENT = (pcallcontext_b)]
$generator_context_retained(S_sibling, pcallcontext_b)
$generator_creation_owner(S_sibling) = (pgenclose.OBJECT)
~$generator_creation_selected(S_sibling, pgeneratorcreation_b.CALLEE, pgeneratorcreation_b.SITE)
~$magic_method_entered(S_sibling, S_sibling.CURRENT, S_sibling.FRAMES, pmagicmethodcall_b, n_arguments_b, [PINT 86])
$target_function(S_sibling, pgeneratorcreation_b.CALLEE) = eps
pgenerator_missing = pgenerator_a[.CREATION = eps]
S_missing = $generator_set(S_view, pgenclose.OBJECT, pgenerator_missing)
$generator_creation_owner(S_missing) = (pgenclose.OBJECT)
~$generator_creation_selected(S_missing, pgeneratorcreation_a.CALLEE, pgeneratorcreation_a.SITE)
~$magic_method_entered(S_missing, S_missing.CURRENT, S_missing.FRAMES, pmagicmethodcall_a, n_arguments_a, [PINT 85])
$target_function(S_missing, pgeneratorcreation_a.CALLEE) = eps
pgenerator_wrong_receipt = pgenerator_a[.CREATION = (pgeneratorcreation_b)]
S_wrong_receipt = $generator_set(S_view, pgenclose.OBJECT, pgenerator_wrong_receipt)
~$generator_creation_selected(S_wrong_receipt, pgeneratorcreation_a.CALLEE, pgeneratorcreation_a.SITE)
~$magic_method_entered(S_wrong_receipt, S_wrong_receipt.CURRENT, S_wrong_receipt.FRAMES, pmagicmethodcall_a, n_arguments_a, [PINT 85])
$call_descriptors_valid(S)
$heap_valid($heap_graph(S))
''')

CASES = {
    'i85-direct-magic-alias-parked-send-independent': {
        'source': ROWS['i85-direct-magic-alias-abort-independent']['source'],
        'stage': PARK_STAGE, 'checks': PARK},
    'i85-direct-magic-sibling-close-independent': {
        'source': ROWS['i85-direct-magic-sibling-owner-independent']['source'],
        'stage': CLOSE_STAGE, 'checks': SIBLING},
}


def run(selected):
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=review.ROOT, text=True).strip()
    review.CASES = CASES
    original = review.recorded
    raw = None

    def recorded(command, directory, stem, environment, cap):
        nonlocal raw
        raw = directory.parent
        return original(command, directory, stem, environment, cap)

    review.recorded = recorded
    try:
        passed = review.run(selected, process_seconds=600)
    finally:
        review.recorded = original
    stable = INPUT_BYTES == {path: path.read_bytes() for path in INPUT_BYTES}
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=review.ROOT, text=True).strip()
    path = raw / 'report.json'
    report = json.loads(path.read_bytes())
    report.update(independent_inputs={str(p): hashlib.sha256(data).hexdigest() for p, data in INPUT_BYTES.items()},
                  independent_inputs_stable=stable, head_stable=head_stable,
                  passed=passed and stable and head_stable)
    path.write_text(json.dumps(report, indent=2) + '\n')
    return report['passed']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    raise SystemExit(0 if run(parser.parse_args().case) else 1)
