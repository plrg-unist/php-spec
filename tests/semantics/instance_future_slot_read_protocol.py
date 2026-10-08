#!/usr/bin/env python3
"""Reached reads of initialized declared slots not yet visited by free_obj."""
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
    'scalar': 'review-instance-future-scalar19',
    'alias': 'review-instance-future-typed-alias19',
}
PREFIX = base.PREFIX + r'''
dec $future_phase(pstate, nat) : bool
def $future_phase(S, 0) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S, n) = $ptascii("FutureReadLeaf359") \/ $object_name(S, n) = $ptascii("FutureAliasLeaf359")
  -- if $instance_test_output(S.EVENTS) = $ptascii("C|")
def $future_phase(S, 1) = true
  -- if S.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: ptask*
  -- if pinstancestorage.NEXT = 2
  -- if $object_name(S, pinstancestorage.OBJECT) = $ptascii("FutureReadParent359") \/ $object_name(S, pinstancestorage.OBJECT) = $ptascii("FutureAliasParent359")
def $future_phase(S, n) = false -- otherwise
dec $future_seek(pstate, nat, nat) : pstate
def $future_seek(S, n_phase, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $future_seek(S, n_phase, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $future_phase(S, n_phase)
def $future_seek(S, n_phase, 0) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$future_phase(S, n_phase)
def $future_seek(S, n_phase, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$future_phase(S, n_phase)
  -- if $(n > 0) /\ S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps
def $future_seek(S, n_phase, n) = $future_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$future_phase(S, n_phase)
  -- if $(n > 0)
  -- if S.TODO =/= eps \/ S.CURRENT =/= eps \/ S.FRAMES =/= eps
dec $future_replace_stage(ptask*, pinstancestorage) : ptask*
def $future_replace_stage(eps, pinstancestorage) = eps
def $future_replace_stage((INSTANCE_STORAGE_STEP pinstancestorage_old) :: ptask_tail*, pinstancestorage) = (INSTANCE_STORAGE_STEP pinstancestorage) :: $future_replace_stage(ptask_tail*, pinstancestorage)
def $future_replace_stage(ptask :: ptask_tail*, pinstancestorage) = ptask :: $future_replace_stage(ptask_tail*, pinstancestorage)
  -- if $instance_storage_task(ptask) = eps
'''


def seek(parent, state, phase):
    return [f'{state}_found = $future_seek({parent}, {phase}, 2048)',
            fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$future_phase({state}, {phase})', *base.valid(state)]


def start(initial):
    return ['S_initial = '+initial, '~S_initial.COMPILESTOP',
        *seek('S_initial', 'S_child', 0),
        '$instance_storage_all(S_child) = [pinstancestorage]',
        'n_parent = pinstancestorage.OBJECT',
        'pinstancestorage.NEXT = 1',
        'S_child.OBJECTS[n_parent] = INSTANCE porigin_parent',
        '$destructor_method(S_child, n_parent) = eps',
        '$instance_storage_basic(S_child, pinstancestorage)',
        '$instance_storage_state_valid(S_child)',
        '~$instance_storage_valid(S_child, pinstancestorage)',
        '$instance_storage_tasks(S_child.TODO) = eps',
        '$instance_storage_frames(S_child.FRAMES) = [pinstancestorage]',
        'S_child.FRAMES = pframe_owner :: pframe_tail*',
        '$instance_storage_tasks(pframe_owner.TODO) = [pinstancestorage]',
        '$instance_storage_tail(pframe_owner.TODO, pinstancestorage) = (ptask_stage_tail*)',
        '$task_nodes(INSTANCE_STORAGE_STEP pinstancestorage) = [HOBJECT n_parent]',
        '(HOBJECT n_parent) <- S_child.ALLOCATIONS',
        '$heap_owners($heap_graph(S_child), HOBJECT n_parent) = 1',
        '$objectprops_at(S_child.OBJECTPROPS, n_parent) = (ppropertyslot_live*)',
        'S_child.CURRENT = (pcallcontext_child)',
        'pcallcontext_child.TARGET = METHOD_TARGET n_leaf porigin_leaf',
        'S_zero = $drive_steps(S_child, 0)',
        'S_zero = S_child[.COMPLETION = BUDGET]']


def controls():
    return [
        '$instance_storage_read_value(S_child, n_parent, $ptascii("child")) = eps',
        '$property_read(S_child, POBJECT n_parent, $ptascii("child"), 1).COMPLETION = UNSUPPORTED "freeing instance property access"',
        '$instance_storage_read_item(S_child, DIRECT (POBJECT (|S_child.OBJECTS|))) = eps',
        '$instance_storage_read_item(S_child, DIRECT (PARRAY (|S_child.ARRAYS|))) = eps',
        '$instance_storage_read_item(S_child, UNINITIALIZED) = eps',
        '$instance_storage_read_item(S_child, DIRECT PUNDEFINED) = eps',
        'S_missing = S_child[.FRAMES = $instance_test_without_frames(S_child.FRAMES)]',
        '$instance_storage_for(S_missing, n_parent) = eps',
        '$instance_storage_read_value(S_missing, n_parent, $ptascii("number")) = eps',
        '~$call_descriptors_valid(S_missing)',
        'S_duplicate = S_child[.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: S_child.TODO]',
        '~$instance_storage_state_valid(S_duplicate)',
        '$instance_storage_read_value(S_duplicate, n_parent, $ptascii("number")) = eps',
        '~$call_descriptors_valid(S_duplicate)',
        'pinstancestorage_bad = pinstancestorage[.NEXT = 2]',
        'S_bad_next = S_child[.FRAMES = pframe_owner[.TODO = $future_replace_stage(pframe_owner.TODO, pinstancestorage_bad)] :: pframe_tail*]',
        '~$instance_storage_state_valid(S_bad_next)',
        '$instance_storage_read_value(S_bad_next, n_parent, $ptascii("number")) = eps',
        '$property_quiet(S_child, POBJECT n_parent, $ptascii("number"), 1) = S_read_number',
        '$property_store_value(S_child, n_parent, $ptascii("number"), PINT 8, 1).COMPLETION = UNSUPPORTED "freeing instance property access"',
        '$property_reference_fetch_unshared(S_child, n_parent, $ptascii("number"), 1).COMPLETION = UNSUPPORTED "freeing instance property access"']


def read(state, key, value):
    label = 'S_read_'+key
    return [f'$instance_storage_read_value({state}, n_parent, $ptascii("{key}")) = ({value})',
        f'{label} = $property_read({state}, POBJECT n_parent, $ptascii("{key}"), 1)',
        f'{label} = {state}[.RESULT = KNOWN ({value})]',
        f'$property_read_key({state}, POBJECT n_parent, $ptascii("{key}"), 1) = {label}',
        f'$heap_graph({label}) = $heap_graph({state})', *base.valid(label)]


def scalar_assertions(initial, expected):
    clauses = [*start(initial),
        'pinstancestorage.SLOTS = [ppropertyslot_child, ppropertyslot_number, ppropertyslot_text, ppropertyslot_truth, ppropertyslot_nothing]',
        'ppropertyslot_child.STATE = PROP_VALUE (DIRECT (POBJECT n_leaf))',
        '$node_children(S_child, HOBJECT n_parent) = eps']
    for key, value in [('number', 'PINT 7'), ('text', '$ptascii("future")'),
                       ('truth', 'PBOOL true'), ('nothing', 'PNULL')]:
        if key == 'text':
            value = 'PSTRING '+value
        clauses += read('S_child', key, value)
    clauses += controls()
    # A valid unvisited slot still cannot reacquire an already-freeing object.
    clauses += [
        'ppropertyslot_heap = ppropertyslot_nothing[.STATE = PROP_VALUE (DIRECT (POBJECT n_parent))]',
        'pinstancestorage_heap = pinstancestorage[.SLOTS[4] = ppropertyslot_heap]',
        'S_heap = S_child[.OBJECTPROPS = $objectprops_set(S_child.OBJECTPROPS, n_parent, $instance_storage_cleared(pinstancestorage_heap.SLOTS, 0))][.FRAMES = pframe_owner[.TODO = $future_replace_stage(pframe_owner.TODO, pinstancestorage_heap)] :: pframe_tail*]',
        '$instance_storage_state_valid(S_heap)',
        '$instance_storage_freeing(S_heap, n_parent)',
        '$instance_storage_read_value(S_heap, n_parent, $ptascii("nothing")) = eps',
        *seek('S_child', 'S_after_number', 1),
        '$instance_storage_for(S_after_number, n_parent) = (pinstancestorage[.NEXT = 2])',
        '$instance_storage_read_value(S_after_number, n_parent, $ptascii("number")) = eps',
        '$property_read(S_after_number, POBJECT n_parent, $ptascii("number"), 1).COMPLETION = UNSUPPORTED "freeing instance property access"',
        '$instance_storage_read_value(S_after_number, n_parent, $ptascii("text")) = (PSTRING $ptascii("future"))',
        *base.finish('S_after_number', expected),
        '~((HOBJECT n_parent) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_leaf) <- S_done.ALLOCATIONS)']
    return clauses


def alias_assertions(initial, expected):
    return [*start(initial),
        'pinstancestorage.SLOTS = [ppropertyslot_child, ppropertyslot_number]',
        'ppropertyslot_number.STATE = PROP_VALUE (ALIAS n_cell)',
        'ppropertyslot_number.DECL = (ppropertyid)',
        'S_child.STORE[n_cell] = DEFINED (PINT 9)',
        'pproptypesource = OBJECT_PROP_SOURCE n_parent ppropertyslot_number.NAME ppropertyid',
        'S_child.PROPREFS = [{CELL n_cell, SOURCES ([pproptypesource])}]',
        '$propref_source_valid(S_child, n_cell, pproptypesource)',
        '$node_children(S_child, HOBJECT n_parent) = [HCELL n_cell]',
        *read('S_child', 'number', 'PINT 9'),
        *controls(),
        'S_missing_cell = S_child[.ALLOCATIONS = $destruction_node_delete(S_child.ALLOCATIONS, HCELL n_cell)]',
        '$instance_storage_read_item(S_missing_cell, ALIAS n_cell) = eps',
        '$instance_storage_read_value(S_missing_cell, n_parent, $ptascii("number")) = eps',
        '$instance_storage_read_item(S_child, ALIAS (|S_child.STORE|)) = eps',
        'S_bad_type = S_child[.STORE[n_cell] = DEFINED (PSTRING $ptascii("bad"))]',
        '$instance_storage_read_value(S_bad_type, n_parent, $ptascii("number")) = eps',
        *seek('S_child', 'S_detached', 1),
        '$instance_storage_for(S_detached, n_parent) = (pinstancestorage[.NEXT = 2])',
        'S_detached.PROPREFS = eps',
        '$instance_storage_read_value(S_detached, n_parent, $ptascii("number")) = eps',
        '$property_read(S_detached, POBJECT n_parent, $ptascii("number"), 1).COMPLETION = UNSUPPORTED "freeing instance property access"',
        *base.finish('S_detached', expected),
        '~((HOBJECT n_parent) <- S_done.ALLOCATIONS)',
        'S_done.STORE[n_cell] = DEFINED (PSTRING $ptascii("free"))']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=list(CASES), required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = cross.snapshot(None)
    out = Path(tempfile.mkdtemp(prefix='instance-future-slot-', dir=ROOT/'.tools'))
    report = {'before': before, 'profile': cross.invoke.types.PROFILE, 'passed': False,
              'native_evaluations': 0, 'model_evaluations': 0, 'state_assertions_evaluated': 0,
              'runner_mode': 'SL', 'numeric_cap_seconds': 120, 'case': CASES[args.group], 'jobs': 1}
    print(out, flush=True)
    try:
        original = sources.CASES[CASES[args.group]]
        source = out/'source.php'; source.write_bytes(original)
        sources.prepare(out, source)
        initial = '$php_run(program_source,0,'+json.dumps(base64.b64encode(os.fsencode(source)).decode())+')'
        body = {'scalar': scalar_assertions, 'alias': alias_assertions}[args.group](initial, sources.EXPECTED[CASES[args.group]])
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
