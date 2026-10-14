#!/usr/bin/env python3
"""Reached class-constant array sharing, COW and reference acquisition."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import file_compile_notice_sources as inputs
import static_types as types
from recorded_worker import Worker
from typed_static_invoke_set_protocol import process

ROOT = Path(__file__).resolve().parents[2]
STAGES = {'loaded': ('static-native-v46', 'loaded-inherited-array', 'V46Child::DATA'),
    'autoload': ('static-native-v46', 'selected-autoload-array', 'V46Loaded::DATA')}
b64 = lambda data: base64.b64encode(data).decode()

PREFIX = r"""
dec $test_output_item(pevent) : nat*
def $test_output_item(OUTPUT n*) = n*
def $test_output_item(pevent) = eps -- otherwise
dec $test_outputs(pevent*) : nat*
def $test_outputs(eps) = eps
def $test_outputs(pevent :: pevent_tail*) = $test_output_item(pevent) ++ $test_outputs(pevent_tail*)
dec $test_running(pstate) : pstate
def $test_running(S) = S[.COMPLETION = NORMAL] -- if S.COMPLETION = BUDGET
def $test_running(S) = S -- otherwise
dec $test_constant_front(pstate, int, preqbytes) : bool
def $test_constant_front(S, 0, preqbytes) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_CONSTANT
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue)]
  -- if $string_bytes(pvalue) = (preqbytes)
def $test_constant_front(S, 1, preqbytes) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $autoload_context_call(pcallcontext,S.CURRENT,S.FRAMES) = ((pautoloadcall,pautoloadentry,poperand))
  -- if pautoloadcall.MODE = AUTO_EXPLICIT pconfigcall
  -- if pconfigcall.KIND = INTRINSIC_CONSTANT
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue)]
  -- if $string_bytes(pvalue) = (preqbytes)
  -- if $lookup(S.ENV,$ptascii("name")) = (n_cell)
  -- if $(n_cell < |S.STORE|)
  -- if S.STORE[n_cell] = DEFINED pvalue_argument
  -- if $string_bytes(pvalue_argument) = (pautoloadcall.NAME)
def $test_constant_front(S, 2, preqbytes) = true
  -- if S.TODO = (DYNAMIC_CLASS_CONSTANT_RESUME pconfigcall) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_CONSTANT
  -- if pconfigcall.SENT = [NAMED_SENT (KNOWN pvalue)]
  -- if $string_bytes(pvalue) = (preqbytes)
def $test_constant_front(S, z_stage, preqbytes) = true
  -- if $(z_stage > 2)
  -- if S.TODO = (STMT (NStmtExpression expression metadata)) :: ptask_tail*
  -- if $source_line(metadata) = z_stage
def $test_constant_front(S, z_stage, preqbytes) = false -- otherwise
dec $test_constant_seek(pstate, int, preqbytes, nat) : pstate
def $test_constant_seek(S, z_stage, preqbytes, 0) = S
def $test_constant_seek(S, z_stage, preqbytes, n) = S
  -- if $(n > 0)
  -- if $test_constant_front(S,z_stage,preqbytes) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_constant_seek(S, z_stage, preqbytes, n) = $test_constant_seek($drive_steps($test_running(S),1),z_stage,preqbytes,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_constant_front(S,z_stage,preqbytes)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
"""


def public(state):
    return ['$call_descriptors_valid(' + state + ')',
        '$declaration_entry_check(' + state + ') = ' + state,
        '$heap_valid($heap_graph(' + state + '))']


def reach(state, source, stage, query):
    found = state + '_found'
    return [found + ' = $test_constant_seek(' + source + ',' + str(stage) + ',$ptascii(' + json.dumps(query) + '),3000)',
        found + '.COMPLETION = NORMAL \\/ ' + found + '.COMPLETION = BUDGET',
        state + ' = ' + found + '[.COMPLETION = NORMAL]',
        '$test_constant_front(' + state + ',' + str(stage) + ',$ptascii(' + json.dumps(query) + '))']


def step(state, source, array=False):
    found = state + '_found'
    checks = [found + ' = $drive_steps(' + source + ',1)',
        found + '.COMPLETION = NORMAL \\/ ' + found + '.COMPLETION = BUDGET',
        state + ' = ' + found + '[.COMPLETION = NORMAL]']
    if array:
        checks += [state + '.RESULT = KNOWN (PARRAY n_pool)']
        checks += [state + '.' + field + ' = ' + source + '.' + field for field in
            ('ARRAYS', 'ALLOCATIONS', 'STORE', 'POOLS', 'EVENTS', 'CLASSCONSTANTCACHE', 'CLASSNAMES')]
        checks += public(state)
    return checks


def cv(state, name, cell, value):
    return ['$lookup(' + state + '.ENV,$ptascii(' + json.dumps(name) + ')) = (' + cell + ')',
        state + '.STORE[' + cell + '] = DEFINED (' + value + ')']


def bad_tree(state, label, index, table, call):
    bad = 'S_bad_' + label
    return [bad + ' = ' + state + '[.ARRAYS = $array_replace(' + state + '.ARRAYS,' + index + ',' + table + ')]',
        '~$dynamic_class_constant_array_tree(' + bad + ',PARRAY n_pool,pvalueclass_root)',
        bad + '_finish = $dynamic_class_constant_finish(' + bad + ',' + call + ')',
        bad + '_finish.COMPLETION = UNSUPPORTED "class constant value query"']


def tree(state, loaded):
    first, child = (2, 4) if loaded else (9, 6)
    leaf_class = 'PVSTRING false' if loaded else 'PVSCALAR'
    nested = 'KSTRING ($ptascii("nested"))'
    classes = '[(KINT ' + str(first) + ',' + leaf_class + '),(' + nested + ',pvalueclass_child)]' if loaded else \
        '[(' + nested + ',pvalueclass_child),(KINT ' + str(first) + ',' + leaf_class + ')]'
    entries = '[ENTRY (KINT 2) (DIRECT (PSTRING ($ptascii("root")))),ENTRY (' + nested + ') (DIRECT (PARRAY n_child))]' if loaded else \
        '[ENTRY (' + nested + ') (DIRECT (PARRAY n_child)),ENTRY (KINT 9) (DIRECT (PINT 29))]'
    leaf = 'PSTRING ($ptascii("kept"))' if loaded else 'PINT 17'
    checks = ['pclassconstantdesc.FOLDED', '$class_constant_visible(' + state + ',pclassconstantdesc)',
        '$origin_node(' + state + '.SOURCES,pclassconstantdesc.INITIALIZER) = (NExprArray (SEQUENCE phpType13*) metadata_initializer)',
        '$compiled_read(' + state + ',pclassconstantdesc.INITIALIZER) = (PARRAY n_pool)',
        '$pool_class(' + state + '.POOLS,pclassconstantdesc.INITIALIZER) = (pvalueclass_root)',
        'pvalueclass_child = PVARRAY false ([(KINT ' + str(child) + ',' + leaf_class + ')])',
        'pvalueclass_root = PVARRAY false (' + classes + ')',
        'parray_pool = ' + state + '.ARRAYS[n_pool]', 'parray_pool.ITEMS = ' + entries,
        'parray_pool.NEXT = ' + str(first + 1), 'parray_pool.SERIAL = 2',
        'parray_child = ' + state + '.ARRAYS[n_child]',
        'parray_child.ITEMS = [ENTRY (KINT ' + str(child) + ') (DIRECT (' + leaf + '))]',
        'parray_child.NEXT = ' + str(child + 1), 'parray_child.SERIAL = 1',
        '(HARRAY n_pool) <- ' + state + '.ALLOCATIONS', '(HARRAY n_child) <- ' + state + '.ALLOCATIONS',
        '$dynamic_class_constant_array_tree(' + state + ',PARRAY n_pool,pvalueclass_root)',
        '~$dynamic_class_constant_array_tree(' + state + ',PARRAY n_pool,PVARRAY true (' + classes + '))',
        '~$dynamic_class_constant_array_tree(' + state + ',PARRAY n_pool,PVSCALAR)',
        '~$dynamic_class_constant_array_tree(' + state + ',PARRAY (|' + state + '.ARRAYS|),pvalueclass_root)',
        '~$dynamic_class_constant_array_tree(' + state + '[.ALLOCATIONS = eps],PARRAY n_pool,pvalueclass_root)',
        '~$dynamic_class_constant_array_tree(' + state + ',POBJECT 0,PVOBJECT)']
    for label, index, record, change in [('next', 'n_pool', 'parray_pool', '[.NEXT = $(parray_pool.NEXT + 1)]'),
            ('serial', 'n_pool', 'parray_pool', '[.SERIAL = $(parray_pool.SERIAL + 1)]'),
            ('positions', 'n_pool', 'parray_pool', '[.POSITIONS = eps]'),
            ('child_next', 'n_child', 'parray_child', '[.NEXT = $(parray_child.NEXT + 1)]')]:
        checks += bad_tree(state, label, index, record + change, 'pconfigcall')
    checks += bad_tree(state, 'nested_empty', 'n_child', '$array_empty()', 'pconfigcall')
    checks += ['S_empty = ' + state + '[.ARRAYS = $array_replace(' + state + '.ARRAYS,n_pool,$array_empty())]',
        '~$dynamic_class_constant_array_tree(S_empty,PARRAY n_pool,PVARRAY false eps)']
    return checks


def assertions(main, case, query, stdout, stage):
    loaded = stage == 'loaded'
    checks = ['S_initial = $php_run(' + main + ',0,' + json.dumps(b64(os.fsencode(case / 'main.php'))) + ')',
        *reach('S', 'S_initial', 0, query), 'S.FILEINCLUDEPATH = eps',
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        '$config_invoke_valid(S,pconfigcall)', '$dynamic_class_constant_valid(S,pconfigcall)', *public('S')]
    if loaded:
        checks += ['pconfigcall.SELECTION = eps',
            '$class_named(S.CLASSNAMES,$ptascii("v46child")) = (porigin_child)',
            '$class_named(S.CLASSNAMES,$ptascii("v46base")) = (porigin_base)',
            'porigin_child =/= porigin_base',
            '$class_constant_lookup(S,porigin_child,$ptascii("DATA"),|S.CLASSES|) = (pclassconstantdesc)',
            'pclassconstantdesc.OWNER = porigin_base']
        checks += tree('S', True) + step('S_value', 'S', True)
        checks += reach('S_root', 'S_value', 9, query)
        checks += cv('S_root', 'copy', 'n_copy_cell', 'PARRAY n_copy')
        checks += cv('S_root', 'peer', 'n_peer_cell', 'PARRAY n_pool')
        checks += ['n_copy =/= n_pool',
            '$entry_lookup(S_root.ARRAYS[n_copy].ITEMS,KSTRING ($ptascii("nested"))) = (DIRECT (PARRAY n_child))',
            '$entry_lookup(S_root.ARRAYS[n_copy].ITEMS,KINT 2) = (DIRECT pvalue_changed)',
            '$string_bytes(pvalue_changed) = ($ptascii("changed"))',
            '$entry_lookup(S_root.ARRAYS[n_copy].ITEMS,KINT 3) = (DIRECT (PINT 73))',
            'S_root.ARRAYS[n_copy].NEXT = 4', 'S_root.ARRAYS[n_pool] = parray_pool',
            'S_root.ARRAYS[n_child] = parray_child', 'S_root.POOLS = S.POOLS', *public('S_root')]
        checks += reach('S_child', 'S_root', 10, query)
        checks += cv('S_child', 'copy', 'n_copy_cell', 'PARRAY n_copy')
        checks += ['$entry_lookup(S_child.ARRAYS[n_copy].ITEMS,KSTRING ($ptascii("nested"))) = (DIRECT (PARRAY n_child_copy))',
            'n_child_copy =/= n_child',
            '$entry_lookup(S_child.ARRAYS[n_child_copy].ITEMS,KINT 4) = (DIRECT pvalue_child_changed)',
            '$string_bytes(pvalue_child_changed) = ($ptascii("changed-child"))',
            'S_child.ARRAYS[n_child_copy].NEXT = 5', 'S_child.ARRAYS[n_pool] = parray_pool',
            'S_child.ARRAYS[n_child] = parray_child', 'S_child.POOLS = S.POOLS', *public('S_child')]
        continuation, again_query = 'S_child', 'V46Base::DATA'
    else:
        checks += ['pconfigcall.SELECTION = (n_selection)',
            'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_CONSTANT',
            '$class_named(S.CLASSNAMES,$ptascii("v46loaded")) = eps']
        checks += step('S_next', 'S')
        checks += ['S_next.TODO = (AUTO_NEXT pautoloadcall) :: ptask_next*',
            'pautoloadcall.MODE = AUTO_EXPLICIT pconfigcall',
            'pautoloadcall.RESUME = DYNAMIC_CLASS_CONSTANT_RESUME pconfigcall',
            '$dynamic_class_constant_autoload_valid(S_next,pautoloadcall)', *public('S_next')]
        checks += reach('S_loader', 'S_next', 1, query)
        checks += ['S_loader.CURRENT = (pcallcontext_loader)',
            '$autoload_context_valid(S_loader,pcallcontext_loader)', *public('S_loader')]
        checks += reach('S_resume', 'S_loader', 2, query)
        checks += ['S_resume.TODO = (DYNAMIC_CLASS_CONSTANT_RESUME pconfigcall) :: ptask_resume*',
            '$class_named(S_resume.CLASSNAMES,$ptascii("v46loaded")) = (porigin_loaded)',
            '$class_constant_lookup(S_resume,porigin_loaded,$ptascii("DATA"),|S_resume.CLASSES|) = (pclassconstantdesc)',
            'pclassconstantdesc.OWNER = porigin_loaded', *public('S_resume')]
        checks += tree('S_resume', False) + step('S_value', 'S_resume', True)
        checks += reach('S_ref', 'S_value', 15, query)
        checks += cv('S_ref', 'copy', 'n_copy_cell', 'PARRAY n_copy')
        checks += cv('S_ref', 'peer', 'n_peer_cell', 'PARRAY n_pool')
        checks += cv('S_ref', 'leaf', 'n_cell', 'PINT 17')
        checks += ['n_copy =/= n_pool',
            '$entry_lookup(S_ref.ARRAYS[n_copy].ITEMS,KSTRING ($ptascii("nested"))) = (DIRECT (PARRAY n_child_copy))',
            'n_child_copy =/= n_child',
            '$entry_lookup(S_ref.ARRAYS[n_child_copy].ITEMS,KINT 6) = (ALIAS n_cell)',
            'S_ref.ARRAYS[n_pool] = parray_pool', 'S_ref.ARRAYS[n_child] = parray_child',
            'S_ref.POOLS = S_resume.POOLS', *public('S_ref'),
            'S_alias = S_ref[.ARRAYS = $array_replace(S_ref.ARRAYS,n_child,parray_child[.ITEMS = [ENTRY (KINT 6) (ALIAS n_cell)]])]',
            '$constant_value_class_valid(S_alias,PARRAY n_pool,pvalueclass_root)',
            '~$dynamic_class_constant_array_tree(S_alias,PARRAY n_pool,pvalueclass_root)']
        checks += reach('S_write', 'S_ref', 16, query)
        checks += ['S_write.STORE[n_cell] = DEFINED (PINT 31)',
            'S_write.ARRAYS[n_pool] = parray_pool', 'S_write.ARRAYS[n_child] = parray_child',
            '$entry_lookup(S_write.ARRAYS[n_child_copy].ITEMS,KINT 6) = (ALIAS n_cell)', *public('S_write')]
        continuation, again_query = 'S_write', query
    checks += reach('S_again', continuation, 0, again_query)
    checks += ['S_again.TODO = (CONFIG_INVOKE pconfigcall_again) :: ptask_again*',
        '$dynamic_class_constant_valid(S_again,pconfigcall_again)',
        'S_again.ARRAYS[n_pool] = parray_pool', 'S_again.ARRAYS[n_child] = parray_child',
        '$dynamic_class_constant_array_tree(S_again,PARRAY n_pool,pvalueclass_root)', *public('S_again')]
    checks += step('S_again_value', 'S_again', True)
    checks += ['S_final = $drive_steps(S_again_value,3000)', 'S_final.COMPLETION = NORMAL',
        'S_final.TODO = eps', 'S_final.FILEINCLUDEPATH = eps', 'S_final.USERCONSTANTS = eps',
        'S_final.ARRAYS[n_pool] = parray_pool', 'S_final.ARRAYS[n_child] = parray_child',
        '$test_outputs(S_final.EVENTS) = $ptascii(' + json.dumps(stdout) + ')', *public('S_final')]
    return checks


def prepare(out, sources, names):
    out.mkdir()
    frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d',
        'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = None
    try:
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for stage in names:
            suite, case_name, constant = STAGES[stage]
            case = sources / suite / case_name
            native = json.loads((case.parent / 'report.json').read_text())
            row, = [item for item in native['records'] if item['id'] == case_name]
            assert native['result'] == 'native_observation' and native['stable_inputs']
            assert native['target'] == types.PROFILE and row['exit'] == 0 and not row['stderr']
            assert hashlib.sha256((case / 'main.php').read_bytes()).hexdigest() == row['originals']['main.php']
            parsed = frontend.request({'op': 'parse', 'source': b64((case / 'main.php').read_bytes())})
            assert parsed['accepted'], parsed
            main = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})['fixture']
            checks = assertions(main, case, constant, row['stdout'], stage)
            target = out / stage
            target.mkdir()
            (target / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
            (target / 'protocol.watsup').write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
                ''.join('  -- if ' + item + '\n' for item in checks))
    finally:
        if adapter:
            adapter.close()
        frontend.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['fixtures', 'check'], required=True)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--stage', action='append', default=[])
    parser.add_argument('--attempt', type=int, default=1)
    args = parser.parse_args()
    names, out, sources = args.stage or list(STAGES), args.output.resolve(), args.sources.resolve()
    assert args.attempt > 0 and names and len(set(names)) == len(names) and set(names) <= STAGES.keys()
    paths = [Path(__file__), ROOT / 'tests/semantics/recorded_worker.py', ROOT / 'tests/semantics/_build/default/numeric_runner.exe', ROOT / 'frontend/target.php', ROOT / 'adapter/wire.ml']
    for name in names:
        suite, case, _ = STAGES[name]
        paths += [sources / suite / 'report.json', sources / suite / 'run.py', sources / suite / case / 'main.php']
        paths += [sources / suite / case / 'native' / item for item in ['stdout', 'stderr', 'process.json', 'command.json']]
        if args.phase == 'check':
            paths += [out / name / 'protocol.watsup', out / name / 'assertions.json']
    pins = lambda: dict(inputs.inputs(), **{str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths})
    before = pins()
    label = args.phase if args.attempt == 1 else args.phase + '-' + str(args.attempt)
    assert not (out / (label + '-report.json')).exists()
    report = {'phase': args.phase, 'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'module_count': len(json.loads((ROOT / 'spec/semantics/modules.json').read_text())), 'inputs': before,
        'implementation_diff_sha256': hashlib.sha256(subprocess.check_output(['git', 'diff', 'HEAD', '--', 'spec/semantics'], cwd=ROOT)).hexdigest(),
        'records': [], 'agreement_credit': 0, 'result': 'fail'}
    try:
        if args.phase == 'fixtures':
            prepare(out, sources, names)
        else:
            mods = [str(ROOT / item) for item in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
            for name in names:
                target = out / name
                runner = process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *mods,
                    str(target / 'protocol.watsup')], target / label, 90, ROOT)
                passed = runner.returncode == 0 and runner.stdout == b'true\n' and not runner.stderr
                report['records'].append({'id': name, 'pass': passed, 'runner_exit': runner.returncode,
                    'premises': len(json.loads((target / 'assertions.json').read_text())) if passed else 0})
                print(json.dumps(report['records'][-1]), flush=True)
                if not passed:
                    break
        report['result'] = 'pass' if args.phase == 'fixtures' or len(report['records']) == len(names) and all(row['pass'] for row in report['records']) else 'fail'
    finally:
        report['stable_inputs'] = before == pins()
        if not report['stable_inputs']:
            report['result'] = 'fail'
            for record in report['records']:
                record['pass'], record['premises'] = False, 0
        (out / (label + '-report.json')).write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if report['result'] == 'pass' else 1)


if __name__ == '__main__':
    main()
