#!/usr/bin/env python3
"""Reached Error transitions from unvisited uninitialized typed slots."""
import argparse
import base64
import json
import os
from pathlib import Path
import tempfile

import instance_storage_pin_protocol as base

sources = base.sources
cross = base.cross
ROOT = base.ROOT
CASES = {
    'inherited': 'review-instance-future-initial-inherited19',
    'pending': 'review-instance-future-initial-pending19',
}
PREFIX = base.PREFIX + r'''
dec $initial_read_first(pstate) : bool
def $initial_read_first(S) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S, n) = $ptascii("FutureInitialFirst359") \/ $object_name(S, n) = $ptascii("FutureInitialPendingFirst359")
def $initial_read_first(S) = false -- otherwise
dec $initial_read_phase(pstate, nat) : bool
def $initial_read_phase(S, 0) = true
  -- if $initial_read_first(S)
  -- if S.TODO = (DIM_FETCH z) :: ptask*
  -- if S.BASE = BASE_PROPERTY (POBJECT n) ptbytes
  -- if ptbytes = $ptascii("number")
  -- if $instance_storage_for(S, n) = (pinstancestorage)
def $initial_read_phase(S, 1) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S, n) = $ptascii("FutureInitialPendingSecond359")
  -- if $instance_test_output(S.EVENTS) = $ptascii("C|A|")
def $initial_read_phase(S, 2) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (FOREACH_BIND_COMMIT pforeachbind) :: ptask*
  -- if pforeachbind.VALUE = POBJECT n
  -- if $object_name(S, n) = $ptascii("FutureInitialPendingParent359")
def $initial_read_phase(S, n) = false -- otherwise
dec $initial_read_seek(pstate, nat, nat) : pstate
def $initial_read_seek(S, n_phase, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $initial_read_seek(S, n_phase, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $initial_read_phase(S, n_phase)
def $initial_read_seek(S, n_phase, 0) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$initial_read_phase(S, n_phase)
def $initial_read_seek(S, n_phase, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$initial_read_phase(S, n_phase)
  -- if $(n > 0) /\ S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps
def $initial_read_seek(S, n_phase, n) = $initial_read_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$initial_read_phase(S, n_phase)
  -- if $(n > 0)
  -- if S.TODO =/= eps \/ S.CURRENT =/= eps \/ S.FRAMES =/= eps
dec $initial_replace_stage(ptask*, pinstancestorage) : ptask*
def $initial_replace_stage(eps, pinstancestorage) = eps
def $initial_replace_stage((INSTANCE_STORAGE_STEP pinstancestorage_old) :: ptask_tail*, pinstancestorage) = (INSTANCE_STORAGE_STEP pinstancestorage) :: $initial_replace_stage(ptask_tail*, pinstancestorage)
def $initial_replace_stage(ptask :: ptask_tail*, pinstancestorage) = ptask :: $initial_replace_stage(ptask_tail*, pinstancestorage)
  -- if $instance_storage_task(ptask) = eps
'''


def seek(parent, state, phase):
    return [f'{state}_found = $initial_read_seek({parent}, {phase}, 2048)',
            fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$initial_read_phase({state}, {phase})', *base.valid(state)]


def step(parent, state):
    return [f'{state}_found = $drive_steps({parent}, 1)',
            f'{state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]', *base.valid(state)]


def start(initial, declaring):
    message = f'Typed property {declaring}::$number must not be accessed before initialization'
    return ['S_initial = '+initial, '~S_initial.COMPILESTOP',
        *seek('S_initial', 'S_before', 0),
        '$instance_storage_all(S_before) = [pinstancestorage]',
        'n_parent = pinstancestorage.OBJECT',
        'pinstancestorage.NEXT = 1',
        '$instance_storage_basic(S_before, pinstancestorage)',
        '$instance_storage_state_valid(S_before)',
        '~$instance_storage_valid(S_before, pinstancestorage)',
        '$instance_storage_tasks(S_before.TODO) = eps',
        '$instance_storage_frames(S_before.FRAMES) = [pinstancestorage]',
        'S_before.FRAMES = pframe_owner :: pframe_tail*',
        '$instance_storage_tasks(pframe_owner.TODO) = [pinstancestorage]',
        '$task_nodes(INSTANCE_STORAGE_STEP pinstancestorage) = [HOBJECT n_parent]',
        '$heap_owners($heap_graph(S_before), HOBJECT n_parent) = 2',
        'S_before.TODO = (DIM_FETCH z) :: ptask_tail*',
        '$(z > 0)',
        'S_before.BASE = BASE_PROPERTY (POBJECT n_parent) ptbytes_key',
        'ptbytes_key = $ptascii("number")',
        'S_before.ORIGIN = (porigin_read)',
        '$property_slot_at(pinstancestorage.SLOTS, ptbytes_key) = (ppropertyslot_number)',
        'ppropertyslot_number.STATE = PROP_INITIAL',
        '$objectprops_at(S_before.OBJECTPROPS, n_parent) = (ppropertyslot_live*)',
        '$property_slot_at(ppropertyslot_live*, ptbytes_key) = (ppropertyslot_number)',
        '$instance_storage_initial_desc(S_before, n_parent, ptbytes_key) = (ppropertydesc)',
        'ppropertydesc.TYPE =/= eps',
        'ppropertydesc.DEFAULT = PROP_UNINITIALIZED',
        f'$property_declaring_name(S_before.CLASSES, ppropertydesc.ORIGIN) = $ptascii("{declaring}")',
        '$instance_storage_read_value(S_before, n_parent, ptbytes_key) = eps',
        f'ptbytes_message = $ptascii("{message}")',
        # This helper-only result checks the producer; ownership below is reached.
        'S_probe = $property_read(S_before, POBJECT n_parent, ptbytes_key, z)',
        'S_probe = S_before[.COMPLETION = THROWN "Error" ptbytes_message z]',
        '$property_read_key(S_before, POBJECT n_parent, ptbytes_key, z) = S_probe',
        '$heap_graph(S_probe) = $heap_graph(S_before)',
        '$property_read(S_before, POBJECT n_parent, ptbytes_key, 0).COMPLETION = UNSUPPORTED "missing source line"',
        'S_zero = $drive_steps(S_before, 0)',
        'S_zero = S_before[.COMPLETION = BUDGET]',
        *step('S_before', 'S_transfer'),
        'S_transfer.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
        'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_parent)]',
        'pdestructionoperation.SOURCE = DIM_FETCH z',
        'pdestructionoperation.PENDING = (n_error)',
        'pdestructionoperation.COMPLETION = THROWING n_error',
        'pdestructionoperation.VALUE = KNOWN PNULL',
        'S_transfer.RESULT = KNOWN PNULL',
        'S_transfer.BASE = BASE_VALUE (KNOWN PNULL)',
        'S_transfer.OBJECTS[n_error] = THROWABLE pthrowable',
        'pthrowable.KIND = "Error"',
        'pthrowable.ORIGIN = (porigin_read)',
        '$throwable_field(S_transfer, n_error, "message") = PSTRING ptbytes_message',
        '$throwable_field(S_transfer, n_error, "line") = PINT z',
        '$throwable_field(S_transfer, n_error, "file") = PSTRING $call_sourcefile(S_transfer.FILES, porigin_read)',
        '$throwable_previous_id(S_transfer, n_error) = eps',
        '$heap_owners($heap_graph(S_transfer), HOBJECT n_error) = 1',
        '$heap_owners($heap_graph(S_transfer), HOBJECT n_parent) = 2',
        '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = [HOBJECT n_error]',
        *step('S_transfer', 'S_shared'),
        'S_shared.TODO = (DESTRUCTOR_RELEASE pdestructionrelease[.JOBS = eps]) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
        '$heap_owners($heap_graph(S_shared), HOBJECT n_parent) = 1',
        '$heap_owners($heap_graph(S_shared), HOBJECT n_error) = 1',
        *step('S_shared', 'S_exit'),
        'S_exit.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
        '$destructor_operation_valid(S_exit, pdestructionoperation)',
        *step('S_exit', 'S_throw'),
        'S_throw.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
        'S_throw.RESULT = KNOWN PNULL',
        'S_throw.BASE = BASE_VALUE (KNOWN PNULL)',
        '$heap_owners($heap_graph(S_throw), HOBJECT n_error) = 1',
        '$heap_owners($heap_graph(S_throw), HOBJECT n_parent) = 1',
        '$instance_storage_for(S_throw, n_parent) = (pinstancestorage)']


def controls():
    return [
        'S_missing = S_before[.FRAMES = $instance_test_without_frames(S_before.FRAMES)]',
        '$instance_storage_for(S_missing, n_parent) = eps',
        '$instance_storage_initial_desc(S_missing, n_parent, ptbytes_key) = eps',
        '~$call_descriptors_valid(S_missing)',
        'S_duplicate = S_before[.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: S_before.TODO]',
        '~$instance_storage_state_valid(S_duplicate)',
        '$instance_storage_initial_desc(S_duplicate, n_parent, ptbytes_key) = eps',
        '~$call_descriptors_valid(S_duplicate)',
        'pinstancestorage_bad = pinstancestorage[.NEXT = 2]',
        'S_bad_next = S_before[.FRAMES = pframe_owner[.TODO = $initial_replace_stage(pframe_owner.TODO, pinstancestorage_bad)] :: pframe_tail*]',
        '~$instance_storage_state_valid(S_bad_next)',
        '$instance_storage_initial_desc(S_bad_next, n_parent, ptbytes_key) = eps',
        '~$property_slot_valid(S_before, ppropertydesc[.DEFAULT = PROP_LITERAL (PINT 7)], ppropertyslot_number)',
        'ppropertyslot_unset = ppropertyslot_number[.STATE = PROP_UNSET]',
        'pinstancestorage_unset = pinstancestorage[.SLOTS[1] = ppropertyslot_unset]',
        'S_unset = S_before[.OBJECTPROPS = $objectprops_set(S_before.OBJECTPROPS, n_parent, $instance_storage_cleared(pinstancestorage_unset.SLOTS, 0))][.FRAMES = pframe_owner[.TODO = $initial_replace_stage(pframe_owner.TODO, pinstancestorage_unset)] :: pframe_tail*]',
        '$instance_storage_state_valid(S_unset)',
        '$instance_storage_initial_desc(S_unset, n_parent, ptbytes_key) = eps',
        '$property_read(S_unset, POBJECT n_parent, ptbytes_key, z).COMPLETION = UNSUPPORTED "freeing instance property access"',
        '$instance_storage_initial_desc(S_before, n_parent, $ptascii("first")) = eps',
        '$property_read(S_before, POBJECT n_parent, $ptascii("first"), z).COMPLETION = UNSUPPORTED "freeing instance property access"',
        '$property_quiet(S_before, POBJECT n_parent, ptbytes_key, z).COMPLETION = UNSUPPORTED "freeing instance property access"',
        '$property_reference_fetch_unshared(S_before, n_parent, ptbytes_key, z).COMPLETION = UNSUPPORTED "freeing instance property access"']


def inherited_assertions(initial, expected):
    return [*start(initial, 'FutureInitialBase359'),
        '$object_name(S_before, n_parent) = $ptascii("FutureInitialDerived359")',
        'pinstancestorage.SLOTS = [ppropertyslot_first, ppropertyslot_number]',
        *controls(), *base.finish('S_throw', expected),
        '~((HOBJECT n_parent) <- S_done.ALLOCATIONS)']


def pending_assertions(initial, expected):
    return [*start(initial, 'FutureInitialPendingParent359'),
        'pinstancestorage.SLOTS = [ppropertyslot_first, ppropertyslot_number, ppropertyslot_second]',
        'ppropertyslot_second.STATE = PROP_VALUE (DIRECT (POBJECT n_second))',
        *seek('S_throw', 'S_second', 1),
        '$instance_storage_for(S_second, n_parent) = (pinstancestorage[.NEXT = 3])',
        '$heap_owners($heap_graph(S_second), HOBJECT n_parent) = 1',
        '$node_children(S_second, HOBJECT n_parent) = eps',
        '$objectprops_at(S_second.OBJECTPROPS, n_parent) = (ppropertyslot_after*)',
        '$property_slot_at(ppropertyslot_after*, ptbytes_key) = (ppropertyslot_number[.STATE = PROP_UNSET])',
        '$instance_storage_initial_desc(S_second, n_parent, ptbytes_key) = eps',
        '$property_read(S_second, POBJECT n_parent, ptbytes_key, z).COMPLETION = UNSUPPORTED "freeing instance property access"',
        'S_second.CURRENT = (pcallcontext_second)',
        'pcallcontext_second.TARGET = METHOD_TARGET n_second porigin_second',
        'S_second.DESTRUCTION.CALLS = pdestructorcall_second :: pdestructorcall_tail*',
        'pdestructorcall_second.OBJECT = n_second',
        'pdestructorcall_second.PENDING = (n_error)',
        '$heap_owners($heap_graph(S_second), HOBJECT n_error) = 1',
        *seek('S_second', 'S_commit', 2),
        'S_commit.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_commit) :: (FOREACH_BIND_COMMIT pforeachbind) :: ptask_commit_tail*',
        'pdestructionoperation_commit.PENDING = (n_final)',
        '$throwable_previous_id(S_commit, n_final) = (n_error)',
        '$throwable_field(S_commit, n_final, "message") = PSTRING $ptascii("B")',
        '$throwable_field(S_commit, n_error, "message") = PSTRING ptbytes_message',
        '~((HOBJECT n_parent) <- S_commit.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_commit), HCELL pforeachbind.NEW) = 2',
        '$task_nodes(FOREACH_BIND_COMMIT pforeachbind) = [HCELL pforeachbind.NEW]',
        '$lookup(S_commit.ENV, pforeachbind.NAME) = (pforeachbind.OLD)',
        *step('S_commit', 'S_bound'),
        '$lookup(S_bound.ENV, pforeachbind.NAME) = (pforeachbind.NEW)',
        'S_bound.STORE[pforeachbind.NEW] = DEFINED (PINT 2)',
        'S_bound.TODO = (THROW_SEARCH n_final) :: ptask_commit_tail*',
        *base.finish('S_bound', expected)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=list(CASES), required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = cross.snapshot(None)
    out = Path(tempfile.mkdtemp(prefix='instance-future-initial-', dir=ROOT/'.tools'))
    report = {'before': before, 'profile': cross.invoke.types.PROFILE, 'passed': False,
              'native_evaluations': 0, 'model_evaluations': 0, 'state_assertions_evaluated': 0,
              'runner_mode': 'SL', 'numeric_cap_seconds': 120, 'case': CASES[args.group], 'jobs': 1}
    print(out, flush=True)
    try:
        original = sources.CASES[CASES[args.group]]
        source = out/'source.php'; source.write_bytes(original)
        sources.prepare(out, source)
        initial = '$php_run(program_source,0,'+json.dumps(base64.b64encode(os.fsencode(source)).decode())+')'
        body = {'inherited': inherited_assertions, 'pending': pending_assertions}[args.group](initial, sources.EXPECTED[CASES[args.group]])
        clauses = ['program_source = '+(out/'program.watsup').read_text().strip(), *body]
        fixture = out/'protocol.watsup'
        fixture.write_text(PREFIX+'dec $body() : bool\ndef $body() = true\n'+
                          ''.join('  -- if '+clause+'\n' for clause in clauses)+
                          '\ndec $main() : bool\ndef $main() = $body()\n')
        (out/'assertions.json').write_text(json.dumps(clauses, indent=2)+'\n')
        report.update(source_sha256=cross.invoke.sha(source), fixture_sha256=cross.invoke.sha(fixture), assertions=len(clauses))
        if not args.prepare_only:
            modules = json.loads((ROOT/'spec/semantics/modules.json').read_text())
            result = cross.invoke.process([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                *[str(ROOT/module) for module in modules], str(fixture)], out/'numeric', 120, ROOT)
            assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
            report['state_assertions_evaluated'] = len(clauses)
        assert source.read_bytes() == original and cross.snapshot(None) == before
        report['passed'] = True
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        report['after'] = cross.snapshot(None)
        (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
        print(out/'report.json', report['passed'], flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
