#!/usr/bin/env python3
"""Reached stdClass storage pins and real property-table ownership transfers."""
import argparse
import base64
import json
import os
from pathlib import Path
import tempfile

import instance_storage_pin_protocol as base

sources = base.sources
cross = sources.cross
ROOT = sources.ROOT
CASES = {
    'table': 'review-stdinstance-storage-table-reinsert-throws19',
    'shared': 'review-stdinstance-storage-shared-table19',
    'generator': 'review-stdinstance-storage-generator-return19',
}
PREFIX = base.PREFIX + r'''
dec $stdstorage_phase(pstate, nat) : bool
def $stdstorage_phase(S, 0) = true
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask*
  -- if pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n)) :: pdestructionjob*
  -- if S.OBJECTS[n] = STDINSTANCE
  -- if $object_table_at(S.OBJECTTABLES, n) =/= eps
  -- if $destructor_operation_for(S) = (pdestructionoperation)
  -- if pdestructionoperation.SOURCE = FOREACH_BIND_RELEASE pforeachbind
  -- if pforeachbind.VALUE = POBJECT n
  -- if $heap_owners($heap_graph(S), HOBJECT n) = 1
def $stdstorage_phase(S, 1) = true
  -- if S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask*
  -- if S.OBJECTS[pinstancestorage.OBJECT] = STDINSTANCE
  -- if $object_table_at(S.OBJECTTABLES, pinstancestorage.OBJECT) =/= eps
  -- if pinstancestorage.NEXT = 0
def $stdstorage_phase(S, 2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S, n) = $ptascii("StdStorageOrderLeaf359")
  -- if $instance_test_output(S.EVENTS) = $ptascii("C|B/stdClass/1|")
def $stdstorage_phase(S, 3) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S, n) = $ptascii("StdStorageOrderLeaf359")
  -- if $instance_test_output(S.EVENTS) = $ptascii("C|B/stdClass/1|A/stdClass/1|")
def $stdstorage_phase(S, 4) = true
  -- if S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask*
  -- if S.OBJECTS[pinstancestorage.OBJECT] = STDINSTANCE
  -- if $object_table_at(S.OBJECTTABLES, pinstancestorage.OBJECT) = eps
  -- if pinstancestorage.NEXT = |pinstancestorage.SLOTS|
def $stdstorage_phase(S, 5) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (FOREACH_BIND_COMMIT pforeachbind) :: ptask*
  -- if pforeachbind.VALUE = POBJECT n
  -- if S.OBJECTS[n] = STDINSTANCE
def $stdstorage_phase(S, 10) = true
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask*
  -- if pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n)) :: pdestructionjob*
  -- if S.OBJECTS[n] = STDINSTANCE
  -- if $object_table_at(S.OBJECTTABLES, n) =/= eps
  -- if $instance_test_output(S.EVENTS) = $ptascii("C|")
def $stdstorage_phase(S, 20) = true
  -- if S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask*
  -- if pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n)) :: pdestructionjob*
  -- if S.OBJECTS[n] = STDINSTANCE
  -- if $instance_test_output(S.EVENTS) = $ptascii("C|")
  -- if $trace_slot(S, S.ENV, $ptascii("wg")) = POBJECT n_weak
  -- if $weakref_get(S, n_weak) = POBJECT n_generator
  -- if $generator_storage_for(S, n_generator) = (pgenstorage)
  -- if pgenstorage.NEXT = 4
  -- if S.OBJECTS[n_generator] = GENERATOR pgenerator
  -- if pgenerator.RETURN = (POBJECT n)
def $stdstorage_phase(S, 21) = true
  -- if S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask*
  -- if S.OBJECTS[pinstancestorage.OBJECT] = STDINSTANCE
  -- if pinstancestorage.NEXT = 0
  -- if $object_table_at(S.OBJECTTABLES, pinstancestorage.OBJECT) = eps
def $stdstorage_phase(S, 22) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S, n) = $ptascii("StdStorageReturnLeaf359")
  -- if $instance_test_output(S.EVENTS) = $ptascii("C|L")
def $stdstorage_phase(S, n) = false -- otherwise
dec $stdstorage_seek(pstate, nat, nat) : pstate
def $stdstorage_seek(S, n_phase, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $stdstorage_seek(S, n_phase, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $stdstorage_phase(S, n_phase)
def $stdstorage_seek(S, n_phase, 0) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$stdstorage_phase(S, n_phase)
def $stdstorage_seek(S, n_phase, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$stdstorage_phase(S, n_phase)
  -- if $(n > 0) /\ S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps
def $stdstorage_seek(S, n_phase, n) = $stdstorage_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$stdstorage_phase(S, n_phase)
  -- if $(n > 0)
  -- if S.TODO =/= eps \/ S.CURRENT =/= eps \/ S.FRAMES =/= eps
'''


def seek(parent, state, phase):
    return [f'{state}_found = $stdstorage_seek({parent}, {phase}, 2048)',
            fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$stdstorage_phase({state}, {phase})', *base.valid(state)]


def one(parent, state):
    return [f'{state}_found = $drive_steps({parent}, 1)',
            f'{state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]', *base.valid(state)]


def pinned_checks():
    return ['S_pinned.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_pin_tail*',
        'pinstancestorage.OBJECT = n_parent',
        '$instance_storage_valid(S_pinned, pinstancestorage)',
        '$object_table_at(S_pinned.OBJECTTABLES, n_parent) = (n_table)',
        '$node_children(S_pinned, HOBJECT n_parent) = [HARRAY n_table]',
        '$task_nodes(INSTANCE_STORAGE_STEP pinstancestorage) = [HOBJECT n_parent]',
        '$heap_owners($heap_graph(S_pinned), HOBJECT n_parent) = 1',
        '$weakref_get(S_pinned, n_weak) = PNULL',
        'S_pinned.OBJECTS[n_weak] = WEAKREFERENCE (n_parent)',
        '$node_children(S_pinned, HOBJECT n_weak) = eps',
        '$destructor_handle(S_pinned, pinstancestorage.HANDLE, 0) = eps',
        'S_zero = $drive_steps(S_pinned, 0)',
        'S_zero.COMPLETION = BUDGET', 'S_zero[.COMPLETION = NORMAL] = S_pinned']


def transfer_checks():
    return [*one('S_pinned', 'S_transfer'),
        'S_transfer.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_table) :: (INSTANCE_STORAGE_STEP pinstancestorage[.NEXT = |pinstancestorage.SLOTS|]) :: ptask_pin_tail*',
        'pdestructionrelease_table.JOBS = [DESTRUCTION_VALUE (HARRAY n_table)]',
        '$object_table_at(S_transfer.OBJECTTABLES, n_parent) = eps',
        '$objectprops_at(S_transfer.OBJECTPROPS, n_parent) = ($instance_storage_unset_all(pinstancestorage.SLOTS))',
        '$node_children(S_transfer, HOBJECT n_parent) = eps',
        'S_transfer.ARRAYS = S_pinned.ARRAYS',
        'S_transfer.PROPREFS = S_pinned.PROPREFS',
        '$heap_owners($heap_graph(S_transfer), HOBJECT n_parent) = 1',
        '(HARRAY n_table) <- S_transfer.ALLOCATIONS']


def table_assertions(initial, expected):
    checks = ['S_initial = '+initial, '~S_initial.COMPILESTOP',
        *seek('S_initial', 'S_release', 0),
        'S_release.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_release_tail*',
        'pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n_parent)) :: pdestructionjob_tail*',
        '$trace_slot(S_release, S_release.ENV, $ptascii("wp")) = POBJECT n_weak',
        '$trace_slot(S_release, S_release.ENV, $ptascii("object")) = POBJECT n_receiver',
        '$weakref_get(S_release, n_weak) = POBJECT n_parent',
        *seek('S_release', 'S_pinned', 1), *pinned_checks(),
        'S_pinned.ARRAYS[n_table].ITEMS = [ENTRY (KSTRING ($ptascii("second"))) (DIRECT (POBJECT n_second)), ENTRY (KSTRING ($ptascii("first"))) (DIRECT (POBJECT n_first))]',
        '$heap_owners($heap_graph(S_pinned), HARRAY n_table) = 1',
        '~$instance_storage_basic(S_pinned, pinstancestorage[.NEXT = 1])',
        'S_missing = S_pinned[.ALLOCATIONS = $destruction_node_delete(S_pinned.ALLOCATIONS, HARRAY n_table)]',
        '~$instance_storage_table_valid(S_missing, pinstancestorage)',
        'S_wrong = S_pinned[.OBJECTTABLES = $object_table_remove(S_pinned.OBJECTTABLES, n_parent) ++ [{OBJECT n_parent, TABLE (|S_pinned.ARRAYS|)}]]',
        '~$instance_storage_table_valid(S_wrong, pinstancestorage)',
        'S_image = S_pinned[.OBJECTPROPS = $objectprops_set(S_pinned.OBJECTPROPS, n_parent, eps)]',
        '~$instance_storage_basic(S_image, pinstancestorage)',
        'S_duplicate = S_pinned[.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: S_pinned.TODO]',
        '~$instance_storage_state_valid(S_duplicate)',
        *transfer_checks(),
        '$heap_owners($heap_graph(S_transfer), HARRAY n_table) = 1',
        *seek('S_transfer', 'S_second', 2),
        '~((HARRAY n_table) <- S_second.ALLOCATIONS)',
        '$instance_storage_for(S_second, n_parent) = (pinstancestorage[.NEXT = |pinstancestorage.SLOTS|])',
        '$heap_owners($heap_graph(S_second), HOBJECT n_parent) = 1',
        '$node_children(S_second, HOBJECT n_parent) = eps',
        '$weakref_get(S_second, n_weak) = PNULL',
        'S_second.CURRENT = (pcallcontext_second)',
        '$destructor_context_call(pcallcontext_second, S_second.CURRENT, S_second.FRAMES) = (pdestructorcall_second)',
        'pdestructorcall_second.OPERATION = (pdestructionoperation_second)',
        'pdestructionoperation_second.SOURCE = FOREACH_BIND_RELEASE pforeachbind',
        '$foreach_released_cell(S_second, pforeachbind.OLD)',
        '$node_children(S_second, HCELL pforeachbind.OLD) = eps',
        '$objectprops_at(S_second.OBJECTPROPS, n_receiver) = (ppropertyslot_receiver*)',
        '$property_slot_at(ppropertyslot_receiver*, $ptascii("x")) = (ppropertyslot_selected)',
        'ppropertyslot_selected.STATE = PROP_VALUE (ALIAS pforeachbind.NEW)',
        '$task_nodes(FOREACH_BIND_COMMIT pforeachbind) = [HCELL pforeachbind.NEW]',
        '$heap_owners($heap_graph(S_second), HCELL pforeachbind.NEW) = 2']
    for call, reason in [
        ('$property_read(S_second, POBJECT n_parent, $ptascii("first"), 1)', 'property access'),
        ('$cast_value(S_second, CASTARRAY, POBJECT n_parent, 1)', 'array cast'),
        ('$object_foreach_reset(S_second, n_parent)', 'foreach'),
        ('$weakref_create(S_second, n_parent)', 'new weak reference'),
    ]:
        checks.append(call+'.COMPLETION = UNSUPPORTED '+json.dumps('freeing instance '+reason))
    checks += [*seek('S_second', 'S_first', 3),
        'S_first.CURRENT = (pcallcontext_first)',
        '$destructor_context_call(pcallcontext_first, S_first.CURRENT, S_first.FRAMES) = (pdestructorcall_first)',
        'pdestructorcall_first.OBJECT = n_first',
        'pdestructorcall_first.PENDING = (n_pending)',
        '$throwable_field(S_first, n_pending, "message") = PSTRING ($ptascii("B"))',
        '$heap_owners($heap_graph(S_first), HOBJECT n_parent) = 1',
        # Borrowed destructor records cannot replace an actual stage carrier.
        'S_absent = S_first[.TODO = $instance_test_without(S_first.TODO)][.FRAMES = $instance_test_without_frames(S_first.FRAMES)]',
        '$instance_storage_for(S_absent, n_parent) = eps',
        '$heap_owners($heap_graph(S_absent), HOBJECT n_parent) = 0',
        '~$gc_retired_valid(S_absent, n_parent)',
        '~$call_descriptors_valid(S_absent)',
        *seek('S_first', 'S_finish', 4),
        '$heap_owners($heap_graph(S_finish), HOBJECT n_parent) = 1',
        '$destructor_operation_for(S_finish) = (pdestructionoperation_finish)',
        'pdestructionoperation_finish.PENDING = (n_final)',
        '$throwable_field(S_finish, n_final, "message") = PSTRING ($ptascii("A"))',
        '$throwable_previous_id(S_finish, n_final) = (n_pending)',
        'S_escaped = S_finish[.HELD = (HOBJECT n_parent) :: S_finish.HELD]',
        '$heap_owners($heap_graph(S_escaped), HOBJECT n_parent) = 2',
        '$drive_steps(S_escaped, 1).COMPLETION = UNSUPPORTED "freeing instance escaped reacquisition"',
        *one('S_finish', 'S_retired'),
        '~((HOBJECT n_parent) <- S_retired.ALLOCATIONS)',
        '$weakref_get(S_retired, n_weak) = PNULL',
        *seek('S_retired', 'S_commit', 5),
        'S_commit.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation_commit) :: (FOREACH_BIND_COMMIT pforeachbind) :: ptask_commit_tail*',
        'pdestructionoperation_commit.PENDING = (n_final)',
        *one('S_commit', 'S_bound'),
        '$lookup(S_bound.ENV, pforeachbind.NAME) = (pforeachbind.NEW)',
        'S_bound.STORE[pforeachbind.NEW] = DEFINED (PINT 2)',
        'S_bound.TODO = (THROW_SEARCH n_final) :: ptask_commit_tail*',
        *base.finish('S_bound', expected)]
    return checks


def shared_assertions(initial, expected):
    return ['S_initial = '+initial, '~S_initial.COMPILESTOP',
        *seek('S_initial', 'S_release', 10),
        'S_release.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_release_tail*',
        'pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n_parent)) :: pdestructionjob_tail*',
        '$trace_slot(S_release, S_release.ENV, $ptascii("wp")) = POBJECT n_weak',
        *seek('S_release', 'S_pinned', 1), *pinned_checks(),
        '$heap_owners($heap_graph(S_pinned), HARRAY n_table) = 2',
        'S_pinned.ARRAYS[n_table].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (DIRECT (POBJECT n_leaf))]',
        *transfer_checks(),
        '$heap_owners($heap_graph(S_transfer), HARRAY n_table) = 2',
        *seek('S_transfer', 'S_finish', 4),
        '(HARRAY n_table) <- S_finish.ALLOCATIONS',
        '(HOBJECT n_leaf) <- S_finish.ALLOCATIONS',
        '$heap_owners($heap_graph(S_finish), HARRAY n_table) = 1',
        '$node_children(S_finish, HARRAY n_table) = [HOBJECT n_leaf]',
        '$instance_test_output(S_finish.EVENTS) = $ptascii("C|")',
        # Constructed empty-table admission must still transfer its table owner.
        'pinstancestorage_empty = pinstancestorage[.SLOTS = eps]',
        'S_empty = S_pinned[.ARRAYS = $array_replace(S_pinned.ARRAYS, n_table, $array_empty())][.OBJECTPROPS = $objectprops_set(S_pinned.OBJECTPROPS, n_parent, eps)][.TODO = (INSTANCE_STORAGE_STEP pinstancestorage_empty) :: ptask_pin_tail*]',
        '$instance_storage_valid(S_empty, pinstancestorage_empty)',
        *one('S_empty', 'S_empty_transfer'),
        'S_empty_transfer.TODO = (DESTRUCTOR_RELEASE pdestructionrelease_empty) :: (INSTANCE_STORAGE_STEP pinstancestorage_empty) :: ptask_pin_tail*',
        'pdestructionrelease_empty.JOBS = [DESTRUCTION_VALUE (HARRAY n_table)]',
        '$object_table_at(S_empty_transfer.OBJECTTABLES, n_parent) = eps',
        '(HOBJECT n_parent) <- S_empty_transfer.ALLOCATIONS',
        *one('S_finish', 'S_retired'),
        '~((HOBJECT n_parent) <- S_retired.ALLOCATIONS)',
        '(HARRAY n_table) <- S_retired.ALLOCATIONS',
        '(HOBJECT n_leaf) <- S_retired.ALLOCATIONS',
        '$heap_owners($heap_graph(S_retired), HARRAY n_table) = 1',
        *base.finish('S_retired', expected),
        '~((HARRAY n_table) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_leaf) <- S_done.ALLOCATIONS)']


def generator_assertions(initial, expected):
    return ['S_initial = '+initial, '~S_initial.COMPILESTOP',
        *seek('S_initial', 'S_release', 20),
        'S_release.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_release_tail*',
        'pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n_parent)) :: pdestructionjob_tail*',
        '$trace_slot(S_release, S_release.ENV, $ptascii("wg")) = POBJECT n_weak_generator',
        '$trace_slot(S_release, S_release.ENV, $ptascii("wp")) = POBJECT n_weak_parent',
        '$weakref_get(S_release, n_weak_generator) = POBJECT n_generator',
        '$weakref_get(S_release, n_weak_parent) = POBJECT n_parent',
        *seek('S_release', 'S_pinned', 21),
        'S_pinned.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask_pin_tail*',
        'pinstancestorage.OBJECT = n_parent',
        '$heap_owners($heap_graph(S_pinned), HOBJECT n_parent) = 1',
        '$heap_owners($heap_graph(S_pinned), HOBJECT n_generator) = 1',
        '$weakref_get(S_pinned, n_weak_parent) = PNULL',
        '$weakref_get(S_pinned, n_weak_generator) = POBJECT n_generator',
        *seek('S_pinned', 'S_leaf', 22),
        '$instance_storage_for(S_leaf, n_parent) = (pinstancestorage[.NEXT = 1])',
        '$node_children(S_leaf, HOBJECT n_parent) = eps',
        '$heap_owners($heap_graph(S_leaf), HOBJECT n_parent) = 1',
        '$heap_owners($heap_graph(S_leaf), HOBJECT n_generator) = 1',
        '$weakref_get(S_leaf, n_weak_parent) = PNULL',
        '$generator_at(S_leaf, n_generator) = (pgenerator)',
        'pgenerator.RETURN = (POBJECT n_parent)',
        '$generator_storage_for(S_leaf, n_generator) = (pgenstorage)',
        'pgenstorage.NEXT = 4',
        *base.finish('S_leaf', expected),
        '~((HOBJECT n_parent) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_generator) <- S_done.ALLOCATIONS)',
        '$weakref_get(S_done, n_weak_parent) = PNULL',
        '$weakref_get(S_done, n_weak_generator) = PNULL']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=list(CASES), required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = cross.snapshot(None)
    out = Path(tempfile.mkdtemp(prefix='stdinstance-storage-pin-', dir=ROOT/'.tools'))
    report = {'before': before, 'profile': cross.invoke.types.PROFILE, 'passed': False,
              'native_evaluations': 0, 'model_evaluations': 0, 'state_assertions_evaluated': 0,
              'runner_mode': 'SL', 'numeric_cap_seconds': 120, 'case': CASES[args.group], 'jobs': 1}
    print(out, flush=True)
    try:
        original = sources.CASES[CASES[args.group]]
        source = out/'source.php'; source.write_bytes(original)
        sources.prepare(out, source)
        initial = '$php_run(program_source,0,'+json.dumps(base64.b64encode(os.fsencode(source)).decode())+')'
        body = {'table': table_assertions, 'shared': shared_assertions,
                'generator': generator_assertions}[args.group](initial, sources.EXPECTED[CASES[args.group]])
        clauses = ['program_source = '+(out/'program.watsup').read_text().strip(), *body]
        fixture = out/'protocol.watsup'
        fixture.write_text(PREFIX+'dec $body() : bool\ndef $body() = true\n'+
                          ''.join('  -- if '+clause+'\n' for clause in clauses)+
                          '\ndec $main() : bool\ndef $main() = $body()\n')
        (out/'assertions.json').write_text(json.dumps(clauses, indent=2)+'\n')
        report.update(source_sha256=cross.invoke.sha(source), fixture_sha256=cross.invoke.sha(fixture),
                      assertions=len(clauses))
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
