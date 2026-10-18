#!/usr/bin/env python3
"""Reached top-level empty define values and authenticated allocation classes."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import file_compile_notice_sources as inputs
import static_types as types
from dynamic_constant_array_protocol import PREFIX, public
from recorded_worker import Worker
from typed_static_invoke_set_protocol import process

ROOT = Path(__file__).resolve().parents[2]
STAGES = {'literal': ('static-native-v43', 'literal-empty', 'V43_LITERAL'),
    'mutable': ('static-native-v43', 'emptied-array', 'V43_EMPTIED')}
b64 = lambda data: base64.b64encode(data).decode()


def assertions(main, case, constant, stdout, stage):
    immutable = stage == 'literal'
    flag = 'true' if immutable else 'false'
    wrong = 'false' if immutable else 'true'
    checks = ['S_initial = $php_run(' + main + ',0,' + json.dumps(b64(os.fsencode(case / 'main.php'))) + ')',
        'S_found = $test_define_seek(S_initial,1000)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', '$test_define_front(S)',
        'S.FILEINCLUDEPATH = eps', 'S.USERCONSTANTS = eps',
        'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail*',
        '$config_invoke_valid(S,pconfigcall)', '$dynamic_array_call_valid(S,pconfigcall)',
        '$dynamic_define_values(pconfigcall) = ((preqbytes_name,PARRAY n_input))',
        'preqbytes_name = $ptascii(' + json.dumps(constant) + ')',
        'parray_input = S.ARRAYS[n_input]', 'parray_input.ITEMS = eps',
        'n_before = |S.ARRAYS|', *public('S')]
    if immutable:
        checks += ['parray_input = $array_empty()', '$array_immutable(S,n_input)',
            '$dynamic_define_known(S,pconfigcall.SITE,1) = (PARRAY n_known)',
            '$array_immutable(S,n_known)']
    else:
        checks += ['~$array_immutable(S,n_input)', 'parray_input.NEXT = 1',
            'parray_input.SERIAL = 1', 'parray_input.POSITIONS = eps',
            '$dynamic_define_known(S,pconfigcall.SITE,1) = eps']
    checks += ['S_after = $drive_steps(S,1)',
        r'S_after.COMPLETION = NORMAL \/ S_after.COMPLETION = BUDGET',
        'S_row = S_after[.COMPLETION = NORMAL]', 'S_row.USERCONSTANTS = [puserconstant]',
        'puserconstant.ORIGIN = pconfigcall.SITE',
        'puserconstant.NAME = $user_constant_key(preqbytes_name)',
        'puserconstant.VALUE = PARRAY n_value',
        'puserconstant.CLASS = PVARRAY ' + flag + ' eps',
        'puserconstant.READS = eps', 'puserconstant.RECEIVES = eps',
        'S_row.RESULT = KNOWN (PBOOL true)', 'S_row.EVENTS = S.EVENTS',
        'S_row.ARRAYS[0:n_before] = S.ARRAYS', 'S_row.ARRAYS[n_value] = $array_empty()',
        '$dynamic_array_value(S_row,PARRAY n_value,eps,false) = ((S_row,PARRAY n_value,puserconstant.CLASS))',
        '$source_constant_lookup(S_row,preqbytes_name) = (VALUE (PARRAY n_value))',
        '(HARRAY n_value) <- $heap_graph(S_row).ROOTS', *public('S_row')]
    if immutable:
        checks += ['n_value = n_input', 'S_row.ARRAYS = S.ARRAYS',
            'S_row.ALLOCATIONS = S.ALLOCATIONS', '$array_immutable(S_row,n_value)',
            '$dynamic_array_known_matches(S_row,PARRAY n_value,(PARRAY n_known))',
            'S_clone_alloc = $allocate_array(S_row,$array_empty())',
            'S_clone_alloc.RESULT = KNOWN (PARRAY n_clone)',
            'S_clone = S_clone_alloc[.RESULT = S_row.RESULT][.USERCONSTANTS = [puserconstant[.VALUE = PARRAY n_clone][.CLASS = PVARRAY false eps]]]',
            'n_clone =/= n_value', '~$array_immutable(S_clone,n_clone)',
            'S_clone.ARRAYS[n_clone] = S_clone.ARRAYS[n_known]',
            '$dynamic_array_value(S_clone,PARRAY n_clone,eps,false) = ((S_clone,PARRAY n_clone,PVARRAY false eps))',
            '$heap_valid($heap_graph(S_clone))',
            '~$dynamic_array_known_matches(S_clone,PARRAY n_clone,(PARRAY n_known))',
            '~$user_constants_valid(S_clone,S_clone.USERCONSTANTS)',
            '~$call_descriptors_valid(S_clone)']
    else:
        checks += ['n_value = n_before', 'n_value =/= n_input',
            '$(|S_row.ARRAYS| = n_before + 1)', '~$array_immutable(S_row,n_value)']
        for label, field in [('next', 'NEXT'), ('serial', 'SERIAL')]:
            bad = 'S_' + label
            checks += [bad + ' = S_row[.ARRAYS = $array_replace(S_row.ARRAYS,n_value,$array_empty()[.' + field + ' = parray_input.' + field + '])]',
                '$heap_valid($heap_graph(' + bad + '))',
                '$dynamic_array_value(' + bad + ',PARRAY n_value,eps,false) = eps',
                '~$call_descriptors_valid(' + bad + ')']
        checks += ['S_nested = $allocate_array(S_row,$array_insert($array_empty(),KSTRING ($ptascii("child")),DIRECT (PARRAY n_value)))',
            'S_nested.RESULT = KNOWN (PARRAY n_parent)', 'n_parent =/= n_value',
            '$dynamic_array_value(S_nested,PARRAY n_parent,eps,true) =/= eps',
            '$dynamic_array_value(S_nested,PARRAY n_parent,eps,false) = ((S_nested,PARRAY n_parent,PVARRAY false ([(KSTRING ($ptascii("child")),PVARRAY false eps)])))']
    variants = ['[puserconstant[.CLASS = PVARRAY ' + wrong + ' eps]]',
        '[puserconstant[.ORIGIN = PORIGIN 0 eps]]',
        '[puserconstant[.NAME = $ptascii("V43_FORGED")]]', '[puserconstant,puserconstant]']
    if not immutable:
        variants += ['[puserconstant[.VALUE = PARRAY n_input]]']
    checks += ['~$user_constants_valid(S_row[.USERCONSTANTS = ' + value + '],' + value + ')' for value in variants]
    checks += ['~$call_descriptors_valid(S_row[.USERCONSTANTS = ' + value + '])' for value in variants]
    checks += ['S_missing = S_row[.ALLOCATIONS = $call_remove_owner(S_row.ALLOCATIONS,HARRAY n_value)]',
        '$dynamic_array_value(S_missing,PARRAY n_value,eps,false) = eps',
        '~$call_descriptors_valid(S_missing)',
        'S_final = $drive_steps(S_row,2000)', 'S_final.COMPLETION = NORMAL',
        'S_final.TODO = eps', 'S_final.FILEINCLUDEPATH = eps',
        'S_final.USERCONSTANTS = [puserconstant]', 'S_final.ARRAYS[n_value] = $array_empty()',
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
    paths = [Path(__file__), ROOT / 'tests/semantics/recorded_worker.py', ROOT / 'tests/semantics/dynamic_constant_array_protocol.py',
        ROOT / 'tests/semantics/_build/default/numeric_runner.exe', ROOT / 'frontend/target.php', ROOT / 'adapter/wire.ml']
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
