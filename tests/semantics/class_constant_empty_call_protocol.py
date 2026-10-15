#!/usr/bin/env python3
"""Reached immutable empty class constants, mutable history and bucket references."""
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
STAGES = {'root': ('static-native-v47', 'loaded-empty-root', 'V47Root::DATA'),
    'nested': ('static-native-v47', 'selected-nested-empty-reference', 'V47Nested::DATA')}
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
def $test_constant_front(S, z_stage, preqbytes) = true
  -- if $(z_stage > 0)
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



def empty_authority(state, index):
    return [state + '.ARRAYS[' + index + '] = $array_empty()',
        '(HARRAY ' + index + ') <- ' + state + '.ALLOCATIONS',
        '$gc_literal_empty_pools(' + state + ',' + state + '.POOLS,' + index + ')',
        '$array_immutable(' + state + ',' + index + ')',
        '$dynamic_class_constant_array_tree(' + state + ',PARRAY ' + index + ',PVARRAY true eps)',
        '~$dynamic_class_constant_array_tree(' + state + ',PARRAY ' + index + ',PVARRAY false eps)']


def assertions(main, case, query, stdout, stage):
    root = stage == 'root'
    class_name = 'v47root' if root else 'v47nested'
    checks = ['S_initial = $php_run(' + main + ',0,' + json.dumps(b64(os.fsencode(case / 'main.php'))) + ')',
        *reach('S', 'S_initial', 0, query), 'S.FILEINCLUDEPATH = eps',
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        '$config_invoke_valid(S,pconfigcall)', '$dynamic_class_constant_valid(S,pconfigcall)',
        '$class_named(S.CLASSNAMES,$ptascii(' + json.dumps(class_name) + ')) = (porigin_class)',
        '$class_constant_lookup(S,porigin_class,$ptascii("DATA"),|S.CLASSES|) = (pclassconstantdesc)',
        'pclassconstantdesc.OWNER = porigin_class', 'pclassconstantdesc.FOLDED',
        '$origin_node(S.SOURCES,pclassconstantdesc.INITIALIZER) = (NExprArray (SEQUENCE phpType13*) metadata_initializer)',
        '$compiled_read(S,pclassconstantdesc.INITIALIZER) = (PARRAY n_pool)',
        '$pool_class(S.POOLS,pclassconstantdesc.INITIALIZER) = (pvalueclass_root)',
        'parray_pool = S.ARRAYS[n_pool]', *public('S')]
    if root:
        checks += ['pconfigcall.SELECTION = eps', 'pvalueclass_root = PVARRAY true eps']
        checks += empty_authority('S', 'n_pool')
    else:
        checks += ['pconfigcall.SELECTION = (n_selection)',
            'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_CONSTANT',
            'pvalueclass_root = PVARRAY false ([(KSTRING ($ptascii("nested")),PVARRAY true eps),(KINT 4,PVSCALAR)])',
            'parray_pool.ITEMS = [ENTRY (KSTRING ($ptascii("nested"))) (DIRECT (PARRAY n_child)),ENTRY (KINT 4) (DIRECT (PINT 17))]',
            'parray_pool.NEXT = 5', 'parray_pool.SERIAL = 2',
            '~$array_immutable(S,n_pool)', '$dynamic_class_constant_array_tree(S,PARRAY n_pool,pvalueclass_root)']
        checks += empty_authority('S', 'n_child')
    checks += step('S_value', 'S', True)
    if root:
        checks += reach('S_empty', 'S_value', 8, query)
        checks += cv('S_empty', 'copy', 'n_copy_cell', 'PARRAY n_copy')
        checks += cv('S_empty', 'peer', 'n_peer_cell', 'PARRAY n_pool')
        checks += ['n_copy =/= n_pool', 'parray_empty = S_empty.ARRAYS[n_copy]',
            'parray_empty.ITEMS = eps', 'parray_empty.NEXT = 1',
            'parray_empty.SERIAL = 1', 'parray_empty.POSITIONS = eps',
            '~$array_immutable(S_empty,n_copy)',
            '~$dynamic_class_constant_array_tree(S_empty,PARRAY n_copy,PVARRAY true eps)',
            '~$dynamic_class_constant_array_tree(S_empty,PARRAY n_copy,PVARRAY false eps)',
            'S_empty.ARRAYS[n_pool] = parray_pool', *public('S_empty'),
            'S_clone = $allocate_array(S_empty,$array_empty())',
            'S_clone.RESULT = KNOWN (PARRAY n_clone)', 'n_clone = |S_empty.ARRAYS|',
            'S_clone.ARRAYS[n_clone] = parray_pool', '$heap_valid($heap_graph(S_clone))',
            '~$array_immutable(S_clone,n_clone)',
            '~$dynamic_class_constant_array_tree(S_clone,PARRAY n_clone,PVARRAY true eps)',
            '~$dynamic_class_constant_array_tree(S_clone,PARRAY n_clone,PVARRAY false eps)',
            '$dynamic_class_constant_array_tree(S_clone,PARRAY n_pool,PVARRAY true eps)',
            'S_history = S[.ARRAYS = $array_replace(S.ARRAYS,n_pool,parray_empty)]',
            '~$array_immutable(S_history,n_pool)',
            '~$dynamic_class_constant_array_tree(S_history,PARRAY n_pool,pvalueclass_root)',
            'S_history_finish = $dynamic_class_constant_finish(S_history,pconfigcall)',
            'S_history_finish.COMPLETION = UNSUPPORTED "class constant value query"']
        continuation = 'S_empty'
    else:
        checks += reach('S_ref', 'S_value', 10, query)
        checks += cv('S_ref', 'copy', 'n_copy_cell', 'PARRAY n_copy')
        checks += cv('S_ref', 'peer', 'n_peer_cell', 'PARRAY n_pool')
        checks += cv('S_ref', 'bucket', 'n_bucket', 'PARRAY n_child')
        checks += ['n_copy =/= n_pool',
            '$entry_lookup(S_ref.ARRAYS[n_copy].ITEMS,KSTRING ($ptascii("nested"))) = (ALIAS n_bucket)',
            'S_ref.ARRAYS[n_pool] = parray_pool',
            '$array_immutable(S_ref,n_child)', 'S_ref.ARRAYS[n_child] = $array_empty()',
            '$constant_value_class_valid(S_ref,PARRAY n_copy,pvalueclass_root)',
            '~$dynamic_class_constant_array_tree(S_ref,PARRAY n_copy,pvalueclass_root)',
            '$dynamic_class_constant_array_tree(S_ref,PARRAY n_pool,pvalueclass_root)', *public('S_ref')]
        continuation = 'S_ref'
    checks += reach('S_again', continuation, 0, query)
    checks += ['S_again.TODO = (CONFIG_INVOKE pconfigcall_again) :: ptask_again*',
        '$dynamic_class_constant_valid(S_again,pconfigcall_again)',
        'S_again.ARRAYS[n_pool] = parray_pool',
        '$dynamic_class_constant_array_tree(S_again,PARRAY n_pool,pvalueclass_root)']
    checks += cv('S_again', 'copy', 'n_copy_cell', 'PARRAY n_copy')
    checks += cv('S_again', 'peer', 'n_peer_cell', 'PARRAY n_pool')
    if root:
        checks += ['S_again.ARRAYS[n_copy].ITEMS = [ENTRY (KINT 1) (DIRECT (PINT 29))]',
            'S_again.ARRAYS[n_copy].NEXT = 2', 'S_again.ARRAYS[n_copy].SERIAL = 2',
            'S_again.ARRAYS[n_copy].POSITIONS = [POSITION (KINT 1) 1]']
    else:
        checks += cv('S_again', 'bucket', 'n_bucket', 'PARRAY n_child_copy')
        checks += ['n_child_copy =/= n_child',
            '$entry_lookup(S_again.ARRAYS[n_copy].ITEMS,KSTRING ($ptascii("nested"))) = (ALIAS n_bucket)',
            'S_again.ARRAYS[n_child_copy].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 29))]',
            'S_again.ARRAYS[n_child_copy].NEXT = 1', 'S_again.ARRAYS[n_child_copy].SERIAL = 1',
            'S_again.ARRAYS[n_child] = $array_empty()', '$array_immutable(S_again,n_child)',
            '~$array_immutable(S_again,n_child_copy)']
    checks += public('S_again') + step('S_again_value', 'S_again', True)
    checks += ['S_final = $drive_steps(S_again_value,3000)', 'S_final.COMPLETION = NORMAL',
        'S_final.TODO = eps', 'S_final.FILEINCLUDEPATH = eps', 'S_final.USERCONSTANTS = eps',
        'S_final.ARRAYS[n_pool] = parray_pool', 'S_final.POOLS = S.POOLS',
        '$test_outputs(S_final.EVENTS) = $ptascii(' + json.dumps(stdout) + ')', *public('S_final')]
    checks += cv('S_final', 'again', 'n_again_cell', 'PARRAY n_pool')
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
