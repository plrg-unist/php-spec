#!/usr/bin/env python3
"""Check actual magic Gen initialization owners and original/supplied exception order."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import fiber_state_review as review

CATALOG = Path(__file__).with_name('generator_direct_magic_throw_cases.json')
INPUT_BYTES = {path: path.read_bytes() for path in (Path(__file__), CATALOG, Path(review.__file__))}
ROW = next(row for row in json.loads(INPUT_BYTES[CATALOG])
           if row['id'] == 'i90-magic-fresh-throw-abort-retarget-independent')
assert hashlib.sha256(ROW['source'].encode()).hexdigest() == ROW['source_sha256']


def checks(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


COMMON = checks(r'''
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
pgenerator.FRAME = eps
pgenerator.CLOSURE = eps
pgenerator.VALUE = eps
pgenerator.REFCELL = eps
pgenerator.RETURN = eps
pgenerator.CREATION = (pgeneratorcreation)
pgeneratorcreation.CLOSURE = eps
pgeneratorcreation.ANCESTORS = eps
pgeneratorcreation.CALLEE = MAGIC_METHOD_TARGET pmagicmethodcall n_arguments ([POBJECT n_token])
pgeneratorcreation.CREATOR_TARGET = pgeneratorcreation.CALLEE
pgeneratorcreation.SITE = pmagicmethodcall.SITE
pgeneratorcreation.CREATOR.FUNCTION = pgenerator.FUNCTION
pgeneratorcreation.CREATOR.FUNCTION = pmagicmethodcall.METHOD
pgeneratorcreation.CREATOR.CALLSITE = (pmagicmethodcall.SITE)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Base90R"))) = (porigin_base)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Leaf90R"))) = (porigin_leaf)
$class_named(S.CLASSNAMES, $ptlc($ptascii("Token90R"))) = (porigin_token)
pgeneratorcreation.CREATOR.LEXICAL_CLASS = (porigin_base)
pgeneratorcreation.CREATOR.CALLED_CLASS = (porigin_leaf)
$target_receiver(S, pgeneratorcreation.CALLEE) = (n_maker)
pmagicmethodcall.CLASS = porigin_leaf
pmagicmethodcall.OBJECT = n_maker
pmagicmethodcall.NAME = $ptascii("missing90R")
pmagicmethodcall.CALLER = eps
pmagicmethodcall.OWNER = 0
|pmagicmethodcall.ARGUMENTS| = 1
S.OBJECTS[n_maker] = INSTANCE porigin_leaf
S.OBJECTS[n_token] = INSTANCE porigin_token
$(n_arguments < |S.ARRAYS|)
$magic_method_descriptor(S, pmagicmethodcall)
$class_method_origin(S.CLASSES, pgenerator.FUNCTION) = (pmethoddesc)
pmethoddesc.OWNER = porigin_base
pmethoddesc.NAME = $ptascii("__call")
~pmethoddesc.STATIC
~pmethoddesc.FUNCTION.SIGNATURE.BYREF
$function_generator(S, pmethoddesc.FUNCTION)
~$generator_reference_producer(S, pgenerator)
$generator_creation_record_valid(S, pgenerator)
$lookup(S.ENV, $ptascii("maker")) = eps
$lookup(S.ENV, $ptascii("weakMaker")) = (n_weak_maker_cell)
S.STORE[n_weak_maker_cell] = DEFINED (POBJECT n_weak_maker)
$lookup(S.ENV, $ptascii("weakToken")) = (n_weak_token_cell)
S.STORE[n_weak_token_cell] = DEFINED (POBJECT n_weak_token)
$lookup(S.ENV, $ptascii("weakOther")) = (n_weak_other_cell)
S.STORE[n_weak_other_cell] = DEFINED (POBJECT n_weak_other)
$weakref_get(S, n_weak_other) = PNULL
$node_children(S, HOBJECT n_generator) = eps
H = $heap_graph(S)
$call_descriptors_valid(S)
$heap_valid(H)
''')

PARK_STAGE = (
    'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
    '-- if pconfigcall.KIND = INTRINSIC_FIBER_THROW '
    '-- if pconfigcall.OWNER = (n_fiber) '
    '-- if S.ACTIVEFIBER = eps '
    '-- if S.OBJECTS[n_fiber] = FIBER pfiber '
    '-- if pfiber.STATUS = FIBER_SUSPENDED')

PARK = COMMON + checks(r'''
pgenerator.PHASE = GENERATOR_RUNNING
pgenerator.FIRST
(HOBJECT n_maker) <- S.ALLOCATIONS
(HARRAY n_arguments) <- S.ALLOCATIONS
S.ARRAYS[n_arguments].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_token))]
$weakref_get(S, n_weak_maker) = POBJECT n_maker
$weakref_get(S, n_weak_token) = POBJECT n_token
pfiber.VM = (pfibervm)
~pfibervm.GLOBAL
pfibervm.CURRENT = (pcallcontext_generator)
pfibervm.FRAMES = pframe_throw :: pframe_tail*
pframe_throw.TODO = (GENERATOR_RESUME pgeneratorop) :: ptask_throw*
pgeneratorop.OBJECT = n_generator
pgeneratorop.NAME = "throw"
pgeneratorop.ARGUMENTS = [POBJECT n_input]
pgeneratorop.LOOP = eps
pgeneratorop.ADVANCE
~pgeneratorop.STARTPACK
~pgeneratorop.BORROWED
$throwable_member(S, n_input)
$lookup(S.ENV, $ptascii("weakFirst")) = (n_weak_input_cell)
S.STORE[n_weak_input_cell] = DEFINED (POBJECT n_weak_input)
$weakref_get(S, n_weak_input) = POBJECT n_input
$throwable_previous_id(S, n_input) = eps
pcallcontext_generator.TARGET = pgeneratorcreation.CALLEE
pcallcontext_generator.FUNCTION = pgenerator.FUNCTION
pcallcontext_generator.CALLSITE = (pmagicmethodcall.SITE)
pcallcontext_generator.LINE = pmagicmethodcall.LINE
pcallcontext_generator.LEXICAL_CLASS = (porigin_base)
pcallcontext_generator.CALLED_CLASS = (porigin_leaf)
pcallcontext_generator.RECEIVER = (n_maker)
pcallcontext_generator.INSTANCE = eps
pcallcontext_generator.WRAPPER = eps
pcallcontext_generator.ARGC = 2
pcallcontext_generator.EXTRA = eps
pcallcontext_generator.HOLES = eps
$lookup(pfibervm.TABLE.ENV, $ptascii("arguments")) = (n_arguments_cell)
S.STORE[n_arguments_cell] = DEFINED (PARRAY n_arguments)
$lookup(pfibervm.TABLE.ENV, $ptascii("name")) = (n_name_cell)
S.STORE[n_name_cell] = DEFINED pvalue_name
$string_bytes(pvalue_name) = ($ptascii("missing90R"))
$node_children(S, HCELL n_arguments_cell) = [HARRAY n_arguments]
$node_children(S, HARRAY n_arguments) = [HOBJECT n_token]
$call_context_roots((pcallcontext_generator)) = [HOBJECT n_maker]
$heap_owners(H, HOBJECT n_maker) = 1
$heap_owners(H, HOBJECT n_token) = 1
$heap_owners(H, HARRAY n_arguments) = 1
$heap_owners(H, HCELL n_arguments_cell) = 1
$heap_owners(H, HOBJECT n_input) = 2
$heap_count(HOBJECT n_maker, $fiber_vm_nodes(pfibervm)) = 1
$heap_count(HOBJECT n_token, $fiber_vm_nodes(pfibervm)) = 0
$heap_count(HOBJECT n_input, $fiber_vm_nodes(pfibervm)) = 2
$generator_pending_exception_nodes(pgeneratorop) = [HOBJECT n_input]
$task_nodes(GENERATOR_RESUME pgeneratorop) = [HOBJECT n_generator, HOBJECT n_input, HOBJECT n_input]
S_live = $fiber_vm_restore(S, pfibervm)[.ACTIVEFIBER = (n_fiber)][.COMPLETION = NORMAL]
$generator_creation_resume_owner(S_live) = (n_generator)
$generator_creation_owner(S_live) = (n_generator)
$generator_creation_selected(S_live, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
$generator_creation_context_valid(S_live, pgenerator, pcallcontext_generator)
$generator_magic_context_valid(S_live, pcallcontext_generator)
$fiber_generator_magic_valid(S_live, pgenerator, pcallcontext_generator)
$magic_method_entered(S_live, S_live.CURRENT, S_live.FRAMES, pmagicmethodcall, n_arguments, [POBJECT n_token])
$fiber_generator_callee_valid(S_live, pgenerator, pcallcontext_generator)
$fiber_generator_fresh_throw_valid(S_live, pgeneratorop, pgenerator, pcallcontext_generator)
~$fiber_generator_throw_valid(S_live, pgeneratorop, pgenerator, pcallcontext_generator)
$fiber_generator_body_id(S_live) = (n_generator)
$fiber_generator_transfer(S_live)
$call_current_valid(S_live)
pgenerator_missing = pgenerator[.CREATION = eps]
S_missing = $generator_set(S_live, n_generator, pgenerator_missing)
~$generator_creation_selected(S_missing, pgeneratorcreation.CALLEE, pgeneratorcreation.SITE)
~$fiber_generator_magic_valid(S_missing, pgenerator_missing, pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_missing, pgeneratorop, pgenerator_missing, pcallcontext_generator)
S_dead = S_live[.ALLOCATIONS = $destruction_node_delete(S_live.ALLOCATIONS, HOBJECT n_maker)]
~$fiber_generator_magic_valid(S_dead, pgenerator, pcallcontext_generator)
pcallcontext_bad_receiver = pcallcontext_generator[.RECEIVER = eps]
S_bad_receiver = S_live[.CURRENT = (pcallcontext_bad_receiver)]
~$fiber_generator_fresh_throw_valid(S_bad_receiver, pgeneratorop, pgenerator, pcallcontext_bad_receiver)
S_no_owner = S_live[.FRAMES = eps]
~$fiber_generator_magic_valid(S_no_owner, pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_no_owner, pgeneratorop, pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_live, pgeneratorop[.ADVANCE = false], pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_live, pgeneratorop[.ARGUMENTS = eps], pgenerator, pcallcontext_generator)
~$fiber_generator_fresh_throw_valid(S_live, pgeneratorop[.ARGUMENTS = [PINT 90]], pgenerator, pcallcontext_generator)
S_zero = $drive_steps(S, 0)
S_zero.COMPLETION = BUDGET
S_one = $drive_steps(S, 1)
S_one.COMPLETION = BUDGET
S_done = $drive_steps(S, 4200)
$drive_steps(S_one[.COMPLETION = NORMAL], 4200) = S_done
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.CURRENT = eps
S_done.FRAMES = eps
S_done.ACTIVEFIBER = eps
~((HOBJECT n_maker) <- S_done.ALLOCATIONS)
~((HOBJECT n_token) <- S_done.ALLOCATIONS)
~((HOBJECT n_input) <- S_done.ALLOCATIONS)
~((HARRAY n_arguments) <- S_done.ALLOCATIONS)
n_maker <- S_done.DESTRUCTION.CALLED
n_token <- S_done.DESTRUCTION.CALLED
$heap_valid($heap_graph(S_done))
''')

CLOSED_STAGE = (
    'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
    '-- if pconfigcall.KIND = INTRINSIC_WEAKREF_GET '
    '-- if $lookup(S.ENV, $ptascii("weakToken")) = (n_weak_token_cell) '
    '-- if S.STORE[n_weak_token_cell] = DEFINED (POBJECT n_weak_token) '
    '-- if pconfigcall.OWNER = (n_weak_token) '
    '-- if $lookup(S.ENV, $ptascii("g")) = (n_generator_cell) '
    '-- if S.STORE[n_generator_cell] = DEFINED (POBJECT n_generator) '
    '-- if S.OBJECTS[n_generator] = GENERATOR pgenerator '
    '-- if pgenerator.PHASE = GENERATOR_CLOSED')

CLOSED = COMMON + checks(r'''
S.ACTIVEFIBER = eps
pgenerator.PHASE = GENERATOR_CLOSED
~((HOBJECT n_maker) <- S.ALLOCATIONS)
~((HOBJECT n_token) <- S.ALLOCATIONS)
~((HARRAY n_arguments) <- S.ALLOCATIONS)
$weakref_get(S, n_weak_maker) = PNULL
$weakref_get(S, n_weak_token) = PNULL
$heap_owners(H, HOBJECT n_maker) = 0
$heap_owners(H, HOBJECT n_token) = 0
$heap_owners(H, HARRAY n_arguments) = 0
n_maker <- S.DESTRUCTION.CALLED
n_token <- S.DESTRUCTION.CALLED
$generator_close_children(S, HOBJECT n_generator) = eps
$lookup(S.ENV, $ptascii("e")) = (n_exception_cell)
S.STORE[n_exception_cell] = DEFINED (POBJECT n_input)
$lookup(S.ENV, $ptascii("weakFirst")) = (n_weak_input_cell)
S.STORE[n_weak_input_cell] = DEFINED (POBJECT n_weak_input)
$weakref_get(S, n_weak_input) = POBJECT n_input
$lookup(S.ENV, $ptascii("supplied")) = (n_supplied_cell)
S.STORE[n_supplied_cell] = DEFINED (POBJECT n_supplied)
n_input =/= n_supplied
$throwable_previous_id(S, n_input) = (n_supplied)
$throwable_previous_id(S, n_supplied) = eps
$lookup(S.ENV, $ptascii("fiber")) = (n_fiber_cell)
S.STORE[n_fiber_cell] = DEFINED (POBJECT n_fiber)
S.OBJECTS[n_fiber] = FIBER pfiber
pfiber.STATUS = FIBER_TERMINATED
pfiber.VM = eps
S_done = $drive_steps(S, 1600)
S_done.COMPLETION = NORMAL
S_done.TODO = eps
S_done.CURRENT = eps
S_done.FRAMES = eps
S_done.ACTIVEFIBER = eps
~((HOBJECT n_input) <- S_done.ALLOCATIONS)
~((HOBJECT n_supplied) <- S_done.ALLOCATIONS)
$heap_valid($heap_graph(S_done))
''')

CASES = {
    'i90-magic-fresh-throw-parked-independent': {'source': ROW['source'], 'stage': PARK_STAGE, 'checks': PARK},
    'i90-magic-fresh-throw-closed-independent': {'source': ROW['source'], 'stage': CLOSED_STAGE, 'checks': CLOSED},
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
