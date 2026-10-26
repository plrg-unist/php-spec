#!/usr/bin/env python3
"""Real call-result INPUT survives DATA retirement and dies before CONFIG entry."""
import argparse
import json
import os
import sys
from pathlib import Path

import global_constant_scalar_name_protocol as driver
import config_generator_call_result_sources as sources

common, text, b64 = driver.common, driver.text, driver.b64
PREFIX = r"""
dec $test_config_call_front(pstate, nat) : bool
def $test_config_call_front(S, 0) = true
  -- if S.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_INI_SET
def $test_config_call_front(S, 1) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "finish") :: ptask*
def $test_config_call_front(S, 2) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "input-release") :: ptask*
  -- if S.DESTRUCTION.OPERATIONS = eps
  -- if $heap_owners($heap_graph(S),HOBJECT pconfiggenerator.OBJECT) = 1
def $test_config_call_front(S, 3) = true
  -- if S.TODO = (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask*
  -- if ~((HOBJECT pconfiggenerator.OBJECT) <- S.ALLOCATIONS)
def $test_config_call_front(S, n) = false -- otherwise
dec $test_config_call_seek(pstate, nat, nat) : pstate
def $test_config_call_seek(S, n_stage, 0) = S
def $test_config_call_seek(S, n_stage, n) = S
  -- if $(n > 0)
  -- if $test_config_call_front(S,n_stage) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
def $test_config_call_seek(S, n_stage, n) = $test_config_call_seek($drive_steps($test_running(S),1),n_stage,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_config_call_front(S,n_stage)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~(S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
dec $test_config_call_step(pstate) : pstate
def $test_config_call_step(S) = S_next
  -- PhpStep: S ~> S_next
"""


def reach(state, start, stage):
    return [state + '_found = $test_config_call_seek(' + start + ',' + str(stage) + ',3000)',
        state + r'_found.COMPLETION = NORMAL \/ ' + state + '_found.COMPLETION = BUDGET',
        state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
        '$test_config_call_front(' + state + ',' + str(stage) + ')']


def budget(state):
    return [state + '_pause = $drive_steps(' + state + ',0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)',
        state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)']


def checks(program, path, name):
    owned = name == 'retained-config-factory-generator-input-retires-before-api'
    assert owned or name == 'fixed-config-temporary-generator-call-drains-before-api'
    callee = ',HOBJECT n_owner' if owned else ''
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *reach('S_pre', 'S_initial', 0),
        'S_pre.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*',
        '$intrinsic_argument(S_pre,pconfigcall.SITE,0) = ((expression,true,eps,PORIGIN n_source pcpath_argument,z_argument))',
        'S_pre.RESULT = KNOWN (POBJECT n_generator)',
        '$lookup(S_pre.ENV,' + text('result') + ') = (n_result_cell)',
        'S_pre.STORE[n_result_cell] = DEFINED (PINT 99)',
        '$lookup(S_pre.ENV,' + text('local') + ') = eps',
        '$source_emission_noarg_call(S_pre,n_source,pcpath_argument,expression) = (z_call)',
        '$code_at(S_pre.CODE,n_source) = (pcode)',
        '$source_unit(S_pre.SOURCES,n_source) = (pcunit)',
        '$ppunpack_class(pcode,pcunit,pcpath_argument) = (UNPACK_VAR)',
        '$code_name(pcode.NAMES,pcpath_argument) = ((ptbytes_factory,eps))',
        '$call_target(S_pre,ptbytes_factory,eps) = (pfunction_factory)',
        'S_pre.OBJECTS[n_generator] = GENERATOR pgenerator_initial',
        'pgenerator_initial.PHASE = GENERATOR_FRESH',
        '$heap_owners($heap_graph(S_pre),HOBJECT n_generator) = 1',
        'pconfiggenerator_initial = {CALL pconfigcall,OBJECT n_generator,INPUT S_pre.RESULT,ITEMS eps,PRODUCER eps}',
        '$config_generator_input(S_pre,pconfiggenerator_initial)',
        '$config_generator_start(S_pre,pconfigcall,S_pre.RESULT,n_generator)',
        '$config_generator_owning_input(pconfiggenerator_initial)',
        '$config_generator_input_nodes(pconfiggenerator_initial) = [HOBJECT n_generator]',
        '~$config_generator_start(S_pre[.ORIGIN = (PORIGIN n_source pcpath_argument)],pconfigcall,S_pre.RESULT,n_generator)',
        *common.public('S_pre'),
        'S_data = $test_config_call_step(S_pre)',
        'S_data = S_pre[.ORIGIN = (PORIGIN n_source pcpath_argument)][.TODO = (CONFIG_GENERATOR pconfiggenerator_initial "rewind") :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$task_nodes(CONFIG_GENERATOR pconfiggenerator_initial "rewind") = [HOBJECT n_generator,HOBJECT n_generator' + callee + ']',
        'pconfigcall.OWNER = (n_owner)' if owned else 'pconfigcall.OWNER = eps',
        '$heap_owners($heap_graph(S_data),HOBJECT n_generator) = 2',
        '$config_generator_valid(S_data,pconfiggenerator_initial,"rewind")',
        'S_data.OBJECTS = S_pre.OBJECTS', 'S_data.STORE = S_pre.STORE',
        'S_data.ARRAYS = S_pre.ARRAYS',
        'S_data.ITERATORS = S_pre.ITERATORS', 'S_data.NEXTITER = S_pre.NEXTITER',
        '$test_outputs(S_data.EVENTS) = ' + text('B|P|' if owned else 'B|'),
        *common.public('S_data')]
    if owned:
        values += ['~(pgenerator_initial.FUNCTION = pfunction_factory.ORIGIN)',
            '~$function_generator(S_pre,pfunction_factory)',
            '$lookup(S_pre.ENV,' + text('watch') + ') = (n_watch_cell)',
            'S_pre.STORE[n_watch_cell] = DEFINED (POBJECT n_watch)',
            'S_pre.OBJECTS[n_watch] = WEAKREFERENCE (n_generator)',
            '$node_children(S_pre,HOBJECT n_watch) = eps',
            '$weakref_get(S_pre,n_watch) = POBJECT n_generator']
    else:
        values += ['pgenerator_initial.FUNCTION = pfunction_factory.ORIGIN',
            '$function_generator(S_pre,pfunction_factory)']
    values += ['pconfiggenerator_cv = pconfiggenerator_initial[.INPUT = VARIABLE ' + text('invented') + ' z_argument]',
        'S_cv = S_data[.TODO = (CONFIG_GENERATOR pconfiggenerator_cv "rewind") :: ptask_tail*]',
        '~$config_generator_history(S_cv,pconfiggenerator_cv)',
        '~$config_generator_input(S_data,pconfiggenerator_initial[.INPUT = KNOWN PNULL])',
        '~$config_generator_input(S_data[.CODE = eps],pconfiggenerator_initial)',
        *reach('S_finish', 'S_data', 1),
        'S_finish.TODO = (CONFIG_GENERATOR pconfiggenerator "finish") :: ptask_tail*',
        'pconfiggenerator.ITEMS = [ENTRY (KINT 3) (DIRECT pvalue_option),ENTRY (KINT 3) (DIRECT pvalue_value)]',
        'pconfiggenerator = pconfiggenerator_initial[.ITEMS = pconfiggenerator.ITEMS]',
        '$string_bytes(pvalue_option) = (' + text('precision') + ')',
        '$string_bytes(pvalue_value) = (' + text('11' if owned else '8') + ')',
        'S_finish.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED', 'pgenerator_closed.FRAME = eps',
        '$heap_owners($heap_graph(S_finish),HOBJECT n_generator) = 2',
        '$config_generator_finish_allowed(S_finish,pconfiggenerator)',
        'S_finish.PRECISIONINI = ' + text('8' if owned else '14'),
        'S_finish.STORE[n_result_cell] = DEFINED (PINT 99)',
        '$test_outputs(S_finish.EVENTS) = ' + text('B|P|Y0|H|Y1|F|' if owned else 'B|Y0|Y1|F|'),
        *common.public('S_finish'),
        'S_raw_data = $test_config_call_step(S_finish)',
        'S_raw_data = $config_generator_finish(S_finish,pconfiggenerator,ptask_tail*)',
        *reach('S_input', 'S_finish', 2),
        'S_input.TODO = (CONFIG_GENERATOR pconfiggenerator "input-release") :: ptask_tail*',
        'S_input.ORIGIN = (pconfigcall.SITE)',
        '$task_nodes(CONFIG_GENERATOR pconfiggenerator "input-release") = [HOBJECT n_generator' + callee + ']',
        '$heap_owners($heap_graph(S_input),HOBJECT n_generator) = 1',
        '(HOBJECT n_generator) <- S_input.ALLOCATIONS',
        '$config_generator_valid(S_input,pconfiggenerator,"input-release")',
        'S_input.EVENTS = S_finish.EVENTS', 'S_input.ARRAYS = S_finish.ARRAYS',
        *common.public('S_input'),
        'S_raw_input = $test_config_call_step(S_input)',
        'S_raw_input = $config_generator_release_input(S_input,pconfiggenerator,ptask_tail*)',
        *reach('S_invoke', 'S_input', 3),
        'S_invoke.TODO = (CONFIG_GENERATOR pconfiggenerator "invoke") :: ptask_tail*',
        '$heap_owners($heap_graph(S_invoke),HOBJECT n_generator) = 0',
        '$task_nodes(CONFIG_GENERATOR pconfiggenerator "invoke") = ' + ('[HOBJECT n_owner]' if owned else 'eps'),
        '$config_generator_retired_scope(S_invoke,pconfiggenerator)',
        '~$config_generator_scope(S_invoke,pconfiggenerator)',
        '$config_generator_valid(S_invoke,pconfiggenerator,"invoke")',
        'S_invoke.EVENTS = S_finish.EVENTS', *common.public('S_invoke')]
    if owned:
        values += ['$weakref_get(S_finish,n_watch) = POBJECT n_generator',
            '$weakref_get(S_input,n_watch) = POBJECT n_generator',
            '$weakref_get(S_invoke,n_watch) = PNULL',
            '$lookup(S_pre.ENV,' + text('keep') + ') = (n_keep_cell)',
            '$heap_owners($heap_graph(S_input),HOBJECT n_owner) = 2',
            'S_last_callee = S_input[.STORE[n_keep_cell] = DEFINED PNULL]',
            '$heap_owners($heap_graph(S_last_callee),HOBJECT n_owner) = 1',
            '$test_config_call_step(S_last_callee) = S_last_callee[.COMPLETION = UNSUPPORTED "CONFIG Generator unpack last INPUT or callee owner"]',
            'S_owning = S_input[.OBJECTS[n_generator] = GENERATOR pgenerator_closed[.RETURN = (POBJECT n_watch)]]',
            '$heap_valid($heap_graph(S_owning))',
            '~$config_generator_quiet_closed(S_owning,pconfiggenerator)',
            '$test_config_call_step(S_owning) = S_owning[.COMPLETION = UNSUPPORTED "CONFIG Generator unpack last INPUT or callee owner"]']
    values += [*common.step('S_after', 'S_invoke'),
        'S_after.TODO = ptask_tail*', 'S_after.RESULT = KNOWN pvalue_old',
        '$string_bytes(pvalue_old) = (' + text('8' if owned else '14') + ')',
        'S_after.PRECISIONINI = ' + text('11' if owned else '8'),
        'S_after.STORE[n_result_cell] = DEFINED (PINT 99)',
        *budget('S_pre'), *budget('S_input'),
        'S_final = $drive_steps(S_after,3000)', 'S_final.COMPLETION = NORMAL',
        'S_final.TODO = eps', 'S_final.CURRENT = eps', 'S_final.FRAMES = eps',
        '~((HOBJECT n_generator) <- S_final.ALLOCATIONS)',
        '$test_outputs(S_final.EVENTS) = ' + text('B|P|Y0|H|Y1|F|A|8|11|D|L|11|R|11|9' if owned else 'B|Y0|Y1|F|A|14|8|E'),
        *common.public('S_final')]
    return values


def partition(values, part, owned):
    cut = values.index('$heap_valid($heap_graph(S_data))') + 1
    if part == 'entry':
        return values[:cut]
    setup = [values[0], values[1], *reach('S_pre', 'S_initial', 0),
        'S_pre.TODO = (CONFIG_UNPACK_PREP pconfigcall) :: ptask_tail*',
        '$intrinsic_argument(S_pre,pconfigcall.SITE,0) = ((expression,true,eps,PORIGIN n_source pcpath_argument,z_argument))',
        'S_pre.RESULT = KNOWN (POBJECT n_generator)',
        '$lookup(S_pre.ENV,' + text('result') + ') = (n_result_cell)',
        '$code_at(S_pre.CODE,n_source) = (pcode)',
        '$code_name(pcode.NAMES,pcpath_argument) = ((ptbytes_factory,eps))',
        '$call_target(S_pre,ptbytes_factory,eps) = (pfunction_factory)',
        'S_pre.OBJECTS[n_generator] = GENERATOR pgenerator_initial',
        'pconfiggenerator_initial = {CALL pconfigcall,OBJECT n_generator,INPUT S_pre.RESULT,ITEMS eps,PRODUCER eps}',
        'S_data = $test_config_call_step(S_pre)']
    if owned:
        setup += ['pconfigcall.OWNER = (n_owner)']
    return setup + values[cut:]


def main():
    fingerprint = sources.family.fingerprint
    sources.family.fingerprint = lambda: dict(fingerprint(), **{
        str(Path(__file__).relative_to(driver.ROOT)): sources.family.sha(__file__)})
    cases = dict(sources.family.CASES)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['prepare', 'check'], required=True)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--part', choices=['entry', 'completion', 'all'], default='all')
    parser.add_argument('--case', action='append', default=[])
    args = parser.parse_args()
    selected = args.case or list(cases)
    assert len(selected) == len(set(selected)) and set(selected) <= cases.keys()
    driver.sources, driver.PREFIX = sources, PREFIX
    for name in selected:
        case = cases[name]
        sources.family.CASES = {name: case}
        for part in (['entry', 'completion'] if args.part == 'all' else [args.part]):
            driver.checks = lambda program, path, name: partition(checks(program, path, name), part,
                name == 'retained-config-factory-generator-input-retires-before-api')
            sys.argv = [sys.argv[0], '--phase', args.phase, '--sources', str(args.sources),
                '--output', str(args.output / name / part)]
            driver.main()


if __name__ == '__main__':
    main()
