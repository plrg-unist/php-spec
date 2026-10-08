#!/usr/bin/env python3
"""Reached quiet property borrows and dereferenced coalesce result copies."""
import argparse
import base64
import json
import os
from pathlib import Path
import tempfile

import instance_future_heap_read_protocol as heap

base = heap.base
sources = heap.sources
cross = heap.cross
ROOT = heap.ROOT
CASES = {
    'borrowed': 'review-instance-future-quiet-heap19',
    'coalesce': 'review-instance-future-quiet-coalesce-alias19',
}
PREFIX = heap.PREFIX + r'''
def $heap_read_child(S) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S, n) = $ptascii("FutureQuietAliasFirst359")
def $heap_read_phase(S, 0) = true
  -- if $heap_read_child(S)
  -- if S.TODO = (COALESCE_QUIET expression z z_right) :: ptask*
  -- if S.BASE = BASE_PROPERTY (POBJECT n) ptbytes
  -- if ptbytes = $ptascii("later")
  -- if $instance_storage_for(S, n) = (pinstancestorage)
  -- if $instance_test_output(S.EVENTS) = $ptascii("C|A|")
def $heap_read_phase(S, 1) = true
  -- if $heap_read_child(S)
  -- if $instance_test_output(S.EVENTS) = $ptascii("C|A|FutureQuietAliasLeaf359/fallback|")
  -- if S.RESULT = KNOWN PNULL /\ S.BASE = BASE_VALUE (KNOWN PNULL)
  -- if $destructor_operation_for(S) = eps
def $heap_read_phase(S, 2) = true
  -- if S.CURRENT = eps
  -- if $instance_test_output(S.EVENTS) = $ptascii("C|A|FutureQuietAliasLeaf359/fallback|x=2|")
  -- if S.RESULT = KNOWN PNULL /\ S.BASE = BASE_VALUE (KNOWN PNULL)
  -- if $destructor_operation_for(S) = eps
def $heap_read_phase(S, 10) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S, n) = $ptascii("FutureQuietHeapFirst359")
  -- if S.TODO = (ISSET_RESULT false z) :: ptask*
  -- if S.BASE = BASE_PROPERTY (POBJECT n_parent) ptbytes
  -- if ptbytes = $ptascii("later")
def $heap_read_phase(S, 11) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n porigin
  -- if $object_name(S, n) = $ptascii("FutureQuietHeapFirst359")
  -- if S.TODO = (ISSET_RESULT true z) :: ptask*
  -- if S.BASE = BASE_PROPERTY (POBJECT n_parent) ptbytes
  -- if ptbytes = $ptascii("items")
dec $quiet_replace_class(pclassdesc*, pclassdesc) : pclassdesc*
def $quiet_replace_class(eps, pclassdesc) = eps
def $quiet_replace_class(pclassdesc_old :: pclassdesc_tail*, pclassdesc) = pclassdesc :: pclassdesc_tail*
  -- if pclassdesc_old.ORIGIN = pclassdesc.ORIGIN
def $quiet_replace_class(pclassdesc_old :: pclassdesc_tail*, pclassdesc) = pclassdesc_old :: $quiet_replace_class(pclassdesc_tail*, pclassdesc)
  -- if pclassdesc_old.ORIGIN =/= pclassdesc.ORIGIN
'''


def borrow(before, label, source, result):
    """One genuine terminal boolean probe, then real shared-receiver release."""
    transfer, drop, exit_, after = [f'S_{label}_{suffix}' for suffix in ['transfer', 'drop', 'exit', 'bool']]
    release, operation, tail = [f'{name}_{label}' for name in ['pdestructionrelease', 'pdestructionoperation', 'ptask_tail']]
    unchanged = lambda state: [f'$heap_owners($heap_graph({state}), HOBJECT n_leaf) = 2',
                               f'$heap_owners($heap_graph({state}), HARRAY n_array) = 1']
    step = lambda parent, state: [f'{state}_found = $drive_steps({parent}, 1)',
        f'{state}_found.COMPLETION = BUDGET', f'{state} = {state}_found[.COMPLETION = NORMAL]', *base.valid(state)]
    return [f'{before}.TODO = ({source}) :: {tail}*', *unchanged(before), *step(before, transfer),
        f'{transfer}.TODO = (DESTRUCTOR_RELEASE {release}) :: (DESTRUCTOR_OPERATION_EXIT {operation}) :: {tail}*',
        f'{release}.JOBS = [DESTRUCTION_VALUE (HOBJECT n_parent)]',
        f'{operation}.SOURCE = {source}',
        f'{operation}.VALUE = KNOWN (PBOOL {result})',
        f'{operation}.PENDING = eps',
        f'$task_nodes(DESTRUCTOR_OPERATION_EXIT {operation}) = eps',
        f'{transfer}.RESULT = KNOWN PNULL', f'{transfer}.BASE = BASE_VALUE (KNOWN PNULL)',
        f'$heap_owners($heap_graph({transfer}), HOBJECT n_parent) = 2', *unchanged(transfer),
        *step(transfer, drop),
        f'{drop}.TODO = (DESTRUCTOR_RELEASE {release}[.JOBS = eps]) :: (DESTRUCTOR_OPERATION_EXIT {operation}) :: {tail}*',
        f'$heap_owners($heap_graph({drop}), HOBJECT n_parent) = 1', *unchanged(drop),
        *step(drop, exit_),
        f'{exit_}.TODO = (DESTRUCTOR_OPERATION_EXIT {operation}) :: {tail}*',
        f'$destructor_operation_valid({exit_}, {operation})',
        *step(exit_, after), f'{after}.TODO = {tail}*',
        f'{after}.RESULT = KNOWN (PBOOL {result})', f'{after}.BASE = BASE_VALUE (KNOWN PNULL)',
        f'$operand_nodes({after}.RESULT) = eps',
        f'$heap_owners($heap_graph({after}), HOBJECT n_parent) = 1', *unchanged(after)]


def borrowed_assertions(initial, expected):
    clauses = ['S_initial = '+initial, '~S_initial.COMPILESTOP',
        *heap.seek('S_initial', 'S_object', 10),
        '$instance_storage_all(S_object) = [pinstancestorage]',
        'n_parent = pinstancestorage.OBJECT', 'pinstancestorage.NEXT = 1',
        'pinstancestorage.SLOTS = [ppropertyslot_first, ppropertyslot_later, ppropertyslot_items]',
        'ppropertyslot_first.STATE = PROP_VALUE (DIRECT (POBJECT n_first))',
        'ppropertyslot_later.STATE = PROP_VALUE (DIRECT (POBJECT n_leaf))',
        'ppropertyslot_items.STATE = PROP_VALUE (DIRECT (PARRAY n_array))',
        '$entry_lookup(S_object.ARRAYS[n_array].ITEMS, KINT 0) = (DIRECT (POBJECT n_leaf))',
        '$instance_storage_frames(S_object.FRAMES) = [pinstancestorage]',
        '$instance_storage_tasks(S_object.TODO) = eps',
        '$heap_owners($heap_graph(S_object), HOBJECT n_parent) = 2',
        'S_object.TODO = (ISSET_RESULT false z_object) :: ptask_object_tail*',
        '$instance_storage_quiet_result(S_object, n_parent, $ptascii("later")) = (POBJECT n_leaf)',
        '$isset_simple(S_object, S_object.BASE, false, z_object).RESULT = KNOWN (PBOOL true)',
        # Helper-only boolean states are constructed; the steps below are live.
        'S_zero = $drive_steps(S_object, 0)', 'S_zero = S_object[.COMPLETION = BUDGET]',
        *borrow('S_object', 'object', 'ISSET_RESULT false z_object', 'true'),
        *heap.seek('S_object_bool', 'S_array', 11),
        'S_array.TODO = (ISSET_RESULT true z_array) :: ptask_array_tail*',
        '$instance_storage_for(S_array, n_parent) = (pinstancestorage)',
        '$heap_owners($heap_graph(S_array), HOBJECT n_parent) = 2',
        '$instance_storage_quiet_result(S_array, n_parent, $ptascii("items")) = (PARRAY n_array)',
        '$isset_simple(S_array, S_array.BASE, true, z_array).RESULT = KNOWN (PBOOL false)',
        *borrow('S_array', 'array', 'ISSET_RESULT true z_array', 'false'),
        '$instance_storage_quiet_result(S_object, n_parent, $ptascii("first")) = eps',
        '$instance_storage_quiet_result(S_object, n_parent, $ptascii("missing")) = eps',
        'S_missing = S_object[.FRAMES = $instance_test_without_frames(S_object.FRAMES)]',
        '$instance_storage_quiet_result(S_missing, n_parent, $ptascii("later")) = eps',
        '~$call_descriptors_valid(S_missing)',
        'S_duplicate = S_object[.TODO = (INSTANCE_STORAGE_STEP pinstancestorage) :: S_object.TODO]',
        '~$instance_storage_state_valid(S_duplicate)',
        '$instance_storage_quiet_result(S_duplicate, n_parent, $ptascii("later")) = eps',
        # Guard-only forged magic metadata, never executed or admitted wholesale.
        'S_object.OBJECTS[n_parent] = INSTANCE porigin_parent',
        '$class_at(S_object.CLASSES, porigin_parent) = (pclassdesc_parent)',
        '$destructor_method(S_object, n_first) = (pmethoddesc_first)']
    for name in ['__isset', '__get']:
        label = name[2:]
        state = 'S_magic_'+label
        clauses += [f'pmethoddesc_{label} = pmethoddesc_first[.NAME = $ptascii("{name}")]',
            f'{state} = S_object[.CLASSES = $quiet_replace_class(S_object.CLASSES, pclassdesc_parent[.METHODS = pmethoddesc_{label} :: pclassdesc_parent.METHODS])]',
            f'~$instance_storage_quiet_class({state}, n_parent)',
            f'$instance_storage_quiet_result({state}, n_parent, $ptascii("later")) = eps']
    return [*clauses, *base.finish('S_array_bool', expected), '~((HOBJECT n_parent) <- S_done.ALLOCATIONS)',
            '~((HOBJECT n_leaf) <- S_done.ALLOCATIONS)', '~((HARRAY n_array) <- S_done.ALLOCATIONS)']


def coalesce_assertions(initial, expected):
    clauses = heap.alias_assertions(initial, expected)
    clauses = [clause.replace('S_before.TODO = (DIM_FETCH z) :: ptask_tail*',
        'S_before.TODO = (COALESCE_QUIET expression_right z z_right) :: ptask_tail*').replace(
        'pdestructionoperation.SOURCE = DIM_FETCH z',
        'pdestructionoperation.SOURCE = COALESCE_QUIET expression_right z z_right') for clause in clauses]
    index = clauses.index('S_kept.PROPREFS = S_before.PROPREFS')
    clauses[index:index] = [
        '$instance_storage_quiet_value(S_kept, n_parent, ppropertyslot_later.NAME) = (PNULL)',
        '$instance_storage_quiet_result(S_kept, n_parent, $ptascii("later")) = (PNULL)']
    return clauses


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=list(CASES), required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before = cross.snapshot(None)
    out = Path(tempfile.mkdtemp(prefix='instance-future-quiet-', dir=ROOT/'.tools'))
    report = {'before': before, 'profile': cross.invoke.types.PROFILE, 'passed': False,
              'native_evaluations': 0, 'model_evaluations': 0, 'state_assertions_evaluated': 0,
              'runner_mode': 'SL', 'numeric_cap_seconds': 120, 'case': CASES[args.group], 'jobs': 1}
    print(out, flush=True)
    try:
        original = sources.CASES[CASES[args.group]]
        source = out/'source.php'; source.write_bytes(original)
        sources.prepare(out, source)
        initial = '$php_run(program_source,0,'+json.dumps(base64.b64encode(os.fsencode(source)).decode())+')'
        body = {'borrowed': borrowed_assertions, 'coalesce': coalesce_assertions}[args.group](initial, sources.EXPECTED[CASES[args.group]])
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
