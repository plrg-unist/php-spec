#!/usr/bin/env python3
"""RETURN storage callbacks precede historical CONFIG reception."""
import argparse
import json
import os
import sys
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import config_generator_return_storage_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64
PREFIX = r"""
dec $test_config_storage_front(pstate, nat) : bool
def $test_config_storage_front(S, 0) = true
  -- if S.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_config_storage_front(S, 1) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "finish") :: ptask*
def $test_config_storage_front(S, 2) = true
  -- if S.TODO = (GENERATOR_STORAGE_STEP pgenstorage) :: ptask*
  -- if pgenstorage.NEXT = 0
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $test_config_storage_front(S, 3) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "storage-released") :: ptask*
  -- if ~((HOBJECT pconfiggenerator.OBJECT) <- S.ALLOCATIONS)
  -- if S.CURRENT = eps /\ S.FRAMES = eps /\ S.DESTRUCTION.OPERATIONS = eps
def $test_config_storage_front(S, n) = false -- otherwise
dec $test_config_storage_seek(pstate, nat, nat) : pstate
def $test_config_storage_seek(S, n_stage, 0) = S
def $test_config_storage_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_config_storage_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
def $test_config_storage_seek(S, n_stage, n) = $test_config_storage_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_config_storage_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~(S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
dec $test_config_storage_step(pstate) : pstate
def $test_config_storage_step(S) = S_next
  -- PhpStep: S ~> S_next
"""


def reach(state, start, stage):
    return [state + '_found = $test_config_storage_seek(' + start + ',' + str(stage) + ',4000)',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_config_storage_front(' + state + ',' + str(stage) + ')']


def owners(state, generator, callee):
    return ['$heap_owners($heap_graph(' + state + '),HOBJECT ' + node + ') = ' + str(count)
        for node, count in [('n_generator', generator), ('n_owner', callee)]]


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)',
        state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def setup(program, path):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *reach('S_pre', 'S_initial', 0),
        'S_pre.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*',
        'pconfigcall.OWNER = (n_owner)',
        '$intrinsic_argument(S_pre,pconfigcall.SITE,0) = ((expression,true,eps,porigin_argument,z_argument))',
        'S_pre.RESULT = VARIABLE ' + text('generator') + ' z_argument']
    for variable, cell in [('generator', 'n_generator_cell'), ('watch', 'n_watch_cell'),
            ('call', 'n_call_cell'), ('keep', 'n_keep_cell'), ('result', 'n_result_cell')]:
        values += ['$lookup(S_pre.ENV,' + text(variable) + ') = (' + cell + ')']
    return values + ['S_pre.STORE[n_generator_cell] = DEFINED (POBJECT n_generator)',
        'S_pre.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)']


def checks(program, path, name):
    assert name == 'config-generator-return-destructor-precedes-selected-api'
    values = [*setup(program, path), 'pconfigcall.LINE = 17', 'z_argument = 18',
        'S_pre.OBJECTS[n_watch] = WEAKREFERENCE (n_generator)',
        '$node_children(S_pre,HOBJECT n_watch) = eps',
        'S_pre.STORE[n_result_cell] = DEFINED (PINT 99)',
        '$config_generator_start(S_pre,pconfigcall,S_pre.RESULT,n_generator)',
        *owners('S_pre', 1, 3), *common.public('S_pre'),
        *reach('S_finish', 'S_pre', 1),
        'S_finish.TODO = (CONFIG_GENERATOR pconfiggenerator "finish") :: ptask_tail*',
        'pconfiggenerator.CALL = pconfigcall', 'pconfiggenerator.OBJECT = n_generator',
        'pconfiggenerator.INPUT = S_pre.RESULT', 'pconfiggenerator.PRODUCER = eps',
        'pconfiggenerator.ITEMS = [ENTRY (KINT 3) (DIRECT pvalue_option),ENTRY (KINT 3) (DIRECT pvalue_value)]',
        '$string_bytes(pvalue_option) = (' + text('precision') + ')',
        '$string_bytes(pvalue_value) = (' + text('8') + ')',
        'S_finish.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED', 'pgenerator_closed.FRAME = eps',
        'pgenerator_closed.DELEGATE = eps', 'pgenerator_closed.BORROWED = eps',
        'pgenerator_closed.RETURN = (POBJECT n_payload)',
        '$ref_return_retire_method(S_finish,n_payload) = (pmethoddesc)',
        '$objectprops_at(S_finish.OBJECTPROPS,n_payload) = (eps)',
        '$node_children(S_finish,HOBJECT n_generator) = [HOBJECT n_payload]',
        '$node_children(S_finish,HOBJECT n_payload) = eps',
        'S_finish.STORE[n_generator_cell] = DEFINED (PINT 17)',
        'S_finish.STORE[n_result_cell] = DEFINED (PINT 99)',
        '$test_outputs(S_finish.EVENTS) = ' + text('B|Y0|Y1|F|'),
        '$weakref_get(S_finish,n_watch) = POBJECT n_generator',
        '~$config_generator_quiet_closed(S_finish,pconfiggenerator)',
        '$config_generator_return_history(S_finish,pconfiggenerator)',
        '$config_generator_return_storage(S_finish,pconfiggenerator)',
        '$config_generator_finish_allowed(S_finish,pconfiggenerator)',
        *owners('S_finish', 1, 3), *common.public('S_finish'),
        'ppropertyslot_extra = {DECL eps,NAME ' + text('extra') + ',STATE PROP_VALUE (DIRECT (PINT 7))}',
        'S_extra = $objectprops_mark(S_finish[.OBJECTPROPS = $objectprops_set(S_finish.OBJECTPROPS,n_payload,[ppropertyslot_extra])],n_payload)',
        '$objectprops_at(S_extra.OBJECTPROPS,n_payload) = ([ppropertyslot_extra])',
        '$objectprops_valid(S_extra,S_extra.OBJECTPROPS)',
        '$heap_valid($heap_graph(S_extra))',
        '$config_generator_return_history(S_extra,pconfiggenerator)',
        '~$config_generator_return_storage(S_extra,pconfiggenerator)',
        '$test_config_storage_step(S_extra) = S_extra[.COMPLETION = UNSUPPORTED "CONFIG Generator unpack last DATA or callee owner"]',
        'S_raw_release = $test_config_storage_step(S_finish)',
        'S_raw_release = $config_generator_finish(S_finish,pconfiggenerator,ptask_tail*)',
        *reach('S_pinned', 'S_finish', 2),
        'S_pinned.TODO = (GENERATOR_STORAGE_STEP pgenstorage) :: ptask_storage_tail*',
        'pgenstorage.OBJECT = n_generator', 'pgenstorage.NEXT = 0', 'pgenstorage.USER',
        'pgenstorage.ORIGIN = (porigin_argument)',
        '$generator_storage_valid(S_pinned,pgenstorage)',
        '$destructor_operation_for(S_pinned) = (pdestructionoperation)',
        'pdestructionoperation.SOURCE = CONFIG_GENERATOR pconfiggenerator "storage-released"',
        'pdestructionoperation.PENDING = eps',
        '$eager_operation_source_valid(S_pinned,pdestructionoperation)',
        '$task_nodes(DESTRUCTOR_OPERATION_EXIT pdestructionoperation) = eps',
        '$task_nodes(GENERATOR_STORAGE_STEP pgenstorage) = [HOBJECT n_generator]',
        '$task_nodes(CONFIG_GENERATOR pconfiggenerator "storage-released") = [HOBJECT n_owner]',
        '$node_children(S_pinned,HOBJECT n_generator) = [HOBJECT n_payload]',
        '$weakref_get(S_pinned,n_watch) = POBJECT n_generator',
        *owners('S_pinned', 1, 3), *common.public('S_pinned'),
        *reach('S_storage', 'S_pinned', 3),
        'S_storage.TODO = (CONFIG_GENERATOR pconfiggenerator "storage-released") :: ptask_tail*',
        'S_storage.ORIGIN = (porigin_argument)',
        '~((HOBJECT n_generator) <- S_storage.ALLOCATIONS)',
        '~((HOBJECT n_payload) <- S_storage.ALLOCATIONS)',
        '$weakref_get(S_storage,n_watch) = PNULL',
        'S_storage.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        '$config_generator_return_history(S_storage,pconfiggenerator)',
        '$config_generator_return_history(S_storage[.OBJECTPROPS = eps],pconfiggenerator)',
        '$config_generator_retired_scope(S_storage,pconfiggenerator)',
        '~$config_generator_scope(S_storage,pconfiggenerator)',
        '$config_generator_valid(S_storage,pconfiggenerator,"storage-released")',
        'S_storage.STORE[n_result_cell] = DEFINED (PINT 99)',
        'S_storage.STORE[n_generator_cell] = DEFINED (PINT 17)',
        'S_storage.STORE[n_call_cell] = DEFINED (POBJECT n_getter)',
        'S_storage.OBJECTS[n_getter] = INTRINSICCLOSURE INTRINSIC_INI_GET',
        'n_getter =/= n_owner', 'S_storage.PRECISIONINI = ' + text('6'),
        '$test_outputs(S_storage.EVENTS) = ' + text('B|Y0|Y1|F|D|H|'),
        *owners('S_storage', 0, 2), *common.public('S_storage'),
        'S_last_callee = S_storage[.STORE[n_keep_cell] = DEFINED PNULL]',
        '$heap_owners($heap_graph(S_last_callee),HOBJECT n_owner) = 1',
        '$config_generator_valid(S_last_callee,pconfiggenerator,"storage-released")',
        'S_stopped = $test_config_storage_step(S_last_callee)',
        'S_stopped = S_last_callee[.COMPLETION = UNSUPPORTED "CONFIG Generator unpack last storage callee owner"]',
        '$drive_steps(S_stopped,4) = S_stopped',
        'S_invoke = $test_config_storage_step(S_storage)',
        'S_invoke = $config_generator_storage_finish(S_storage,pconfiggenerator,ptask_tail*)',
        'S_invoke = S_storage[.ORIGIN = (pconfigcall.SITE)][.TODO = (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask_tail*]',
        '$config_generator_valid(S_invoke,pconfiggenerator,"invoke")',
        *budget('S_finish'), *budget('S_storage'),
        *common.step('S_after', 'S_invoke'), 'S_after.TODO = ptask_tail*',
        'S_after.RESULT = KNOWN pvalue_old', '$string_bytes(pvalue_old) = (' + text('6') + ')',
        'S_after.PRECISIONINI = ' + text('8'), *owners('S_after', 0, 1),
        'S_final = $drive_steps(S_after,4000)', 'S_final.COMPLETION = NORMAL',
        'S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        '$weakref_get(S_final,n_watch) = PNULL',
        '$test_outputs(S_final.EVENTS) = ' + text('B|Y0|Y1|F|D|H|A|6|8|17|G|L|8|R|8|9'),
        *common.public('S_final')]
    return values


def partition(values, part):
    cut = values.index('$heap_valid($heap_graph(S_pinned))') + 1
    if part == 'entry':
        return values[:cut]
    end = values.index('S_pre.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)') + 1
    prefix = values[:end]
    prefix += [*reach('S_finish', 'S_pre', 1),
        'S_finish.TODO = (CONFIG_GENERATOR pconfiggenerator "finish") :: ptask_tail*',
        'S_finish.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        'pgenerator_closed.RETURN = (POBJECT n_payload)',
        *reach('S_pinned', 'S_finish', 2)]
    return prefix + values[cut:]


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['prepare', 'check'], required=True)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--part', choices=['entry', 'completion', 'all'], default='all')
    args = parser.parse_args()
    driver.sources, driver.PREFIX = sources, PREFIX
    for part in (['entry', 'completion'] if args.part == 'all' else [args.part]):
        driver.checks = lambda program, path, name: partition(checks(program, path, name), part)
        sys.argv = [sys.argv[0], '--phase', args.phase, '--sources', str(args.sources),
            '--output', str(args.output / part)]
        driver.main()


if __name__ == '__main__':
    main()
