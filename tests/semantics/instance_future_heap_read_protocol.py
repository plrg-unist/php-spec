#!/usr/bin/env python3
"""Reached payload copies from live, unvisited declared property slots."""
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
    'alias': 'review-instance-future-heap-alias19',
    'array': 'review-instance-future-heap-array-cow19',
}
PREFIX = base.PREFIX + r'''
dec $heap_read_child(pstate) : bool
def $heap_read_child(S) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S, n) = $ptascii("FutureAliasHeapFirst359") \/ $object_name(S, n) = $ptascii("FutureCowHeapFirst359")
def $heap_read_child(S) = false -- otherwise
dec $heap_read_phase(pstate, nat) : bool
def $heap_read_phase(S, 0) = true
  -- if $heap_read_child(S)
  -- if S.TODO = (DIM_FETCH z) :: ptask*
  -- if S.BASE = BASE_PROPERTY (POBJECT n) ptbytes
  -- if ptbytes = $ptascii("later")
  -- if $instance_storage_for(S, n) = (pinstancestorage)
  -- if $instance_test_output(S.EVENTS) = $ptascii("C|A|")
def $heap_read_phase(S, 1) = true
  -- if $heap_read_child(S)
  -- if $instance_test_output(S.EVENTS) = $ptascii("C|A|FutureAliasHeapLeaf359/1|") \/ $instance_test_output(S.EVENTS) = $ptascii("C|A|old/new|")
  -- if S.RESULT = KNOWN PNULL /\ S.BASE = BASE_VALUE (KNOWN PNULL)
  -- if $destructor_operation_for(S) = eps
def $heap_read_phase(S, 2) = true
  -- if S.CURRENT = eps
  -- if $instance_test_output(S.EVENTS) = $ptascii("C|A|FutureAliasHeapLeaf359/1|x=2|") \/ $instance_test_output(S.EVENTS) = $ptascii("C|A|old/new|x=2|")
  -- if S.RESULT = KNOWN PNULL /\ S.BASE = BASE_VALUE (KNOWN PNULL)
  -- if $destructor_operation_for(S) = eps
def $heap_read_phase(S, n) = false -- otherwise
dec $heap_read_seek(pstate, nat, nat) : pstate
def $heap_read_seek(S, n_phase, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $heap_read_seek(S, n_phase, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $heap_read_phase(S, n_phase)
def $heap_read_seek(S, n_phase, 0) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$heap_read_phase(S, n_phase)
def $heap_read_seek(S, n_phase, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$heap_read_phase(S, n_phase)
  -- if $(n > 0) /\ S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps
def $heap_read_seek(S, n_phase, n) = $heap_read_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$heap_read_phase(S, n_phase)
  -- if $(n > 0)
  -- if S.TODO =/= eps \/ S.CURRENT =/= eps \/ S.FRAMES =/= eps
'''


def seek(parent, state, phase):
    return [f'{state}_found = $heap_read_seek({parent}, {phase}, 2048)',
            fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$heap_read_phase({state}, {phase})', *base.valid(state)]


def start(initial):
    return ['S_initial = '+initial, '~S_initial.COMPILESTOP',
        *seek('S_initial', 'S_before', 0),
        '$instance_storage_all(S_before) = [pinstancestorage]',
        'n_parent = pinstancestorage.OBJECT',
        'pinstancestorage.NEXT = 1',
        'pinstancestorage.SLOTS = [ppropertyslot_first, ppropertyslot_later]',
        '$instance_storage_basic(S_before, pinstancestorage)',
        '$instance_storage_state_valid(S_before)',
        '$instance_storage_tasks(S_before.TODO) = eps',
        '$instance_storage_frames(S_before.FRAMES) = [pinstancestorage]',
        '$task_nodes(INSTANCE_STORAGE_STEP pinstancestorage) = [HOBJECT n_parent]',
        '$heap_owners($heap_graph(S_before), HOBJECT n_parent) = 2',
        'S_before.TODO = (DIM_FETCH z) :: ptask_tail*',
        'S_before.BASE = BASE_PROPERTY (POBJECT n_parent) ppropertyslot_later.NAME',
        'S_before.RESULT = KNOWN PNULL',
        'S_global = $global_table_view(S_before)',
        '$trace_slot(S_global, S_global.ENV, $ptascii("wp")) = POBJECT n_weak_parent',
        '$weakref_get(S_before, n_weak_parent) = PNULL',
        '$trace_slot(S_global, S_global.ENV, $ptascii("wl")) = POBJECT n_weak_leaf',
        'S_zero = $drive_steps(S_before, 0)',
        'S_zero = S_before[.COMPLETION = BUDGET]']


def copy(value, node):
    return [
        f'$instance_storage_read_value(S_before, n_parent, ppropertyslot_later.NAME) = ({value})',
        f'$heap_owners($heap_graph(S_before), {node}) = 1',
        'S_transfer_found = $drive_steps(S_before, 1)',
        'S_transfer_found.COMPLETION = BUDGET',
        'S_transfer = S_transfer_found[.COMPLETION = NORMAL]',
        'S_transfer.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
        'pdestructionrelease.JOBS = [DESTRUCTION_VALUE (HOBJECT n_parent)]',
        'pdestructionoperation.SOURCE = DIM_FETCH z',
        f'pdestructionoperation.VALUE = KNOWN ({value})',
        'pdestructionoperation.BASE = BASE_VALUE (KNOWN PNULL)',
        'pdestructionoperation.PENDING = eps',
        'S_transfer.RESULT = KNOWN PNULL /\\ S_transfer.BASE = BASE_VALUE (KNOWN PNULL)',
        f'$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = [{node}]',
        f'$heap_owners($heap_graph(S_transfer), {node}) = 2',
        '$heap_owners($heap_graph(S_transfer), HOBJECT n_parent) = 2',
        *base.valid('S_transfer'),
        'S_drop_found = $drive_steps(S_transfer, 1)',
        'S_drop_found.COMPLETION = BUDGET',
        'S_drop = S_drop_found[.COMPLETION = NORMAL]',
        'S_drop.TODO = (DESTRUCTOR_RELEASE pdestructionrelease[.JOBS = eps]) :: (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
        '$heap_owners($heap_graph(S_drop), HOBJECT n_parent) = 1',
        f'$heap_owners($heap_graph(S_drop), {node}) = 2',
        *base.valid('S_drop'),
        'S_exit_found = $drive_steps(S_drop, 1)',
        'S_exit_found.COMPLETION = BUDGET',
        'S_exit = S_exit_found[.COMPLETION = NORMAL]',
        'S_exit.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*',
        '$destructor_operation_valid(S_exit, pdestructionoperation)',
        *base.valid('S_exit'),
        'S_copy_found = $drive_steps(S_exit, 1)',
        'S_copy_found.COMPLETION = BUDGET',
        'S_copy = S_copy_found[.COMPLETION = NORMAL]',
        'S_copy.TODO = ptask_tail*',
        'S_copy.BASE = BASE_VALUE (KNOWN PNULL)',
        f'S_copy.RESULT = KNOWN ({value})',
        f'$operand_nodes(S_copy.RESULT) = [{node}]',
        f'$heap_owners($heap_graph(S_copy), {node}) = 2',
        '$heap_owners($heap_graph(S_copy), HOBJECT n_parent) = 1',
        'S_copy.OBJECTPROPS = S_before.OBJECTPROPS',
        'S_copy.PROPREFS = S_before.PROPREFS', *base.valid('S_copy')]


def controls():
    return [
        '$instance_storage_read_item(S_before, DIRECT (POBJECT (|S_before.OBJECTS|))) = eps',
        '$instance_storage_read_item(S_before, DIRECT (PARRAY (|S_before.ARRAYS|))) = eps',
        '$instance_storage_read_item(S_before, DIRECT (POBJECT n_parent)) = eps',
        '$instance_storage_read_value(S_before, n_parent, $ptascii("first")) = eps',
        'S_missing = S_before[.FRAMES = $instance_test_without_frames(S_before.FRAMES)]',
        '$instance_storage_read_value(S_missing, n_parent, ppropertyslot_later.NAME) = eps',
        '~$call_descriptors_valid(S_missing)',
        'S_duplicate = S_before[.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: S_before.TODO]',
        '~$instance_storage_state_valid(S_duplicate)',
        '$instance_storage_read_value(S_duplicate, n_parent, ppropertyslot_later.NAME) = eps',
        '$property_quiet(S_before, POBJECT n_parent, ppropertyslot_later.NAME, z) = S_before[.RESULT = pdestructionoperation.VALUE]',
        '$property_reference_fetch_unshared(S_before, n_parent, ppropertyslot_later.NAME, z).COMPLETION = UNSUPPORTED "freeing instance property access"']


def retire():
    return [*seek('S_kept', 'S_retired', 2),
        '~((HOBJECT n_parent) <- S_retired.ALLOCATIONS)',
        '$instance_storage_for(S_retired, n_parent) = eps',
        '$weakref_get(S_retired, n_weak_parent) = PNULL',
        '$weakref_get(S_retired, n_weak_leaf) = POBJECT n_leaf',
        'S_retired.STORE[n_kept] = S_kept.STORE[n_kept]']


def alias_assertions(initial, expected):
    return [*start(initial),
        'ppropertyslot_later.STATE = PROP_VALUE (ALIAS n_cell)',
        'ppropertyslot_later.DECL = (ppropertyid)',
        'S_before.STORE[n_cell] = DEFINED (POBJECT n_leaf)',
        '$weakref_get(S_before, n_weak_leaf) = POBJECT n_leaf',
        '$node_children(S_before, HOBJECT n_parent) = [HCELL n_cell]',
        '$node_children(S_before, HCELL n_cell) = [HOBJECT n_leaf]',
        '$heap_owners($heap_graph(S_before), HCELL n_cell) = 2',
        'pproptypesource = OBJECT_PROP_SOURCE n_parent ppropertyslot_later.NAME ppropertyid',
        'S_before.PROPREFS = [{CELL n_cell, SOURCES ([pproptypesource])}]',
        *copy('POBJECT n_leaf', 'HOBJECT n_leaf'),
        '$heap_owners($heap_graph(S_copy), HCELL n_cell) = 2',
        '$instance_storage_read_item(S_before, DIRECT (POBJECT n_leaf)) = (POBJECT n_leaf)',
        'S_absent = S_before[.ALLOCATIONS = $destruction_node_delete(S_before.ALLOCATIONS, HOBJECT n_leaf)]',
        '$instance_storage_read_value(S_absent, n_parent, ppropertyslot_later.NAME) = eps',
        *controls(), *seek('S_copy', 'S_kept', 1),
        'S_kept_global = $global_table_view(S_kept)',
        '$lookup(S_kept_global.ENV, $ptascii("kept")) = (n_kept)',
        'S_kept.STORE[n_kept] = DEFINED (POBJECT n_leaf)',
        '$node_children(S_kept, HCELL n_kept) = [HOBJECT n_leaf]',
        'S_kept.STORE[n_cell] = DEFINED PNULL',
        '$node_children(S_kept, HCELL n_cell) = eps',
        '$instance_storage_read_value(S_kept, n_parent, ppropertyslot_later.NAME) = (PNULL)',
        '$heap_owners($heap_graph(S_kept), HOBJECT n_leaf) = 1',
        'S_kept.PROPREFS = S_before.PROPREFS',
        '$propref_source_valid(S_kept, n_cell, pproptypesource)',
        *retire(),
        '$heap_owners($heap_graph(S_retired), HOBJECT n_leaf) = 1',
        'S_retired.PROPREFS = eps',
        'S_retired.STORE[n_cell] = DEFINED PNULL',
        *base.finish('S_retired', expected),
        'S_done.STORE[n_cell] = DEFINED (PSTRING $ptascii("free"))',
        '~((HOBJECT n_leaf) <- S_done.ALLOCATIONS)',
        '$weakref_get(S_done, n_weak_leaf) = PNULL']


def array_assertions(initial, expected):
    return [*start(initial),
        'ppropertyslot_later.STATE = PROP_VALUE (DIRECT (PARRAY n_array))',
        '$node_children(S_before, HOBJECT n_parent) = [HARRAY n_array]',
        '$entry_lookup(S_before.ARRAYS[n_array].ITEMS, KSTRING $ptascii("leaf")) = (DIRECT (POBJECT n_leaf))',
        '$weakref_get(S_before, n_weak_leaf) = POBJECT n_leaf',
        '$heap_owners($heap_graph(S_before), HOBJECT n_leaf) = 1',
        *copy('PARRAY n_array', 'HARRAY n_array'),
        '$heap_owners($heap_graph(S_copy), HOBJECT n_leaf) = 1',
        'S_absent = S_before[.ALLOCATIONS = $destruction_node_delete(S_before.ALLOCATIONS, HARRAY n_array)]',
        '$instance_storage_read_value(S_absent, n_parent, ppropertyslot_later.NAME) = eps',
        *controls(), *seek('S_copy', 'S_kept', 1),
        'S_kept_global = $global_table_view(S_kept)',
        '$lookup(S_kept_global.ENV, $ptascii("kept")) = (n_kept)',
        'S_kept.STORE[n_kept] = DEFINED (PARRAY n_array_copy)',
        'n_array_copy =/= n_array',
        '$node_children(S_kept, HOBJECT n_parent) = [HARRAY n_array]',
        '$node_children(S_kept, HCELL n_kept) = [HARRAY n_array_copy]',
        '$entry_lookup(S_kept.ARRAYS[n_array].ITEMS, KSTRING $ptascii("tag")) = (DIRECT (PSTRING $ptascii("old")))',
        '$entry_lookup(S_kept.ARRAYS[n_array_copy].ITEMS, KSTRING $ptascii("tag")) = (DIRECT (PSTRING $ptascii("new")))',
        '$entry_lookup(S_kept.ARRAYS[n_array_copy].ITEMS, KSTRING $ptascii("leaf")) = (DIRECT (POBJECT n_leaf))',
        '$heap_owners($heap_graph(S_kept), HARRAY n_array) = 1',
        '$heap_owners($heap_graph(S_kept), HARRAY n_array_copy) = 1',
        '$heap_owners($heap_graph(S_kept), HOBJECT n_leaf) = 2',
        *retire(),
        '~((HARRAY n_array) <- S_retired.ALLOCATIONS)',
        '(HARRAY n_array_copy) <- S_retired.ALLOCATIONS',
        '$heap_owners($heap_graph(S_retired), HARRAY n_array_copy) = 1',
        '$heap_owners($heap_graph(S_retired), HOBJECT n_leaf) = 1',
        *base.finish('S_retired', expected),
        '~((HARRAY n_array_copy) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_leaf) <- S_done.ALLOCATIONS)',
        '$weakref_get(S_done, n_weak_leaf) = PNULL']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=list(CASES), required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = cross.snapshot(None)
    out = Path(tempfile.mkdtemp(prefix='instance-future-heap-', dir=ROOT/'.tools'))
    report = {'before': before, 'profile': cross.invoke.types.PROFILE, 'passed': False,
              'native_evaluations': 0, 'model_evaluations': 0, 'state_assertions_evaluated': 0,
              'runner_mode': 'SL', 'numeric_cap_seconds': 120, 'case': CASES[args.group], 'jobs': 1}
    print(out, flush=True)
    try:
        original = sources.CASES[CASES[args.group]]
        source = out/'source.php'; source.write_bytes(original)
        sources.prepare(out, source)
        initial = '$php_run(program_source,0,'+json.dumps(base64.b64encode(os.fsencode(source)).decode())+')'
        body = {'alias': alias_assertions, 'array': array_assertions}[args.group](initial, sources.EXPECTED[CASES[args.group]])
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
