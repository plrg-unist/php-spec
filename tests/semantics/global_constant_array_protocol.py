#!/usr/bin/env python3
"""Original-derived global array query roots, tree guards and readonly receives."""
import argparse
import base64
import json
import os
from pathlib import Path
import subprocess

import class_constant_call_protocol as common
import error_handler_run as recorder
import global_constant_array_sources as sources
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
recorder.ROOT = ROOT
b64 = lambda data: base64.b64encode(data).decode()
sha = sources.family.sha
text = lambda value: '$ptascii(' + json.dumps(value) + ')'


def receive(state, start, query, row, index, selected=False):
    call, root, after = 'pconfigcall_' + state, 'n_array_' + state, state + '_value'
    values = [*common.reach(state, start, 0, query),
        state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        '$dynamic_global_constant_call(' + call + ')',
        '$dynamic_global_constant_valid(' + state + ',' + call + ')',
        '~$dynamic_class_constant_valid(' + state + ',' + call + ')',
        call + '.OWNER = eps', call + '.PACKS = eps',
        '$user_constant_at(' + state + '.USERCONSTANTS,' + text(query) + ') = (' + row + ')',
        '$(|' + state + '.USERCONSTANTS| > ' + str(index) + ')',
        state + '.USERCONSTANTS[' + str(index) + '] = ' + row,
        row + '.VALUE = PARRAY ' + root,
        '$dynamic_global_constant_array_tree(' + state + ',' + row + '.VALUE,' + row + '.CLASS)',
        '$dynamic_global_constant_value(' + state + ',' + text(query) + ') = (' + row + '.VALUE)',
        *common.public(state),
        state + '_pause = $drive_steps(' + state + ',0)',
        state + '_pause = ' + state + '[.COMPLETION = BUDGET]',
        state + '_one = $drive_steps(' + state + ',1)',
        state + '_one = $drive_steps(' + state + '_pause[.COMPLETION = NORMAL],1)',
        state + r'_one.COMPLETION = NORMAL \/ ' + state + '_one.COMPLETION = BUDGET',
        after + ' = ' + state + '_one[.COMPLETION = NORMAL]',
        after + '.TODO = ptask_' + state + '*',
        after + '.RESULT = KNOWN (' + row + '.VALUE)',
        after + '.BASE = BASE_VALUE (KNOWN PNULL)', *common.public(after)]
    values += [after + '.' + field + ' = ' + state + '.' + field for field in (
        'ARRAYS', 'ALLOCATIONS', 'STRINGDATA', 'USERCONSTANTS', 'STORE', 'EVENTS',
        'POOLS', 'SOURCES', 'FILES', 'CLASSCONSTANTCACHE', 'SELECTEDCALLS')]
    if selected:
        values += [call + '.SELECTION = (n_selection)',
            '$(n_selection < |' + state + '.SELECTEDCALLS|)',
            state + '.SELECTEDCALLS[n_selection].KIND = INTRINSIC_CONSTANT']
    else:
        values += [call + '.SELECTION = eps']
    return values


def checks(program, path, name):
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET']
    if name == 'immutable-and-mutable-empty-roots':
        values += receive('S_fixed', 'S_initial', 'FixedEmpty23', 'puserconstant_fixed', 0)
        values += ['puserconstant_fixed.CLASS = PVARRAY true eps',
            '$array_immutable(S_fixed,n_array_S_fixed)',
            'S_fixed.ARRAYS[n_array_S_fixed] = $array_empty()',
            '~$dynamic_global_constant_array_tree(S_fixed,puserconstant_fixed.VALUE,PVARRAY false eps)']
        values += receive('S_mutable', 'S_fixed_value', 'MutableEmpty23', 'puserconstant_mutable', 1)
        values += ['puserconstant_mutable.CLASS = PVARRAY false eps',
            '~$array_immutable(S_mutable,n_array_S_mutable)',
            'S_mutable.ARRAYS[n_array_S_mutable] = $array_empty()',
            '~$dynamic_global_constant_array_tree(S_mutable,puserconstant_mutable.VALUE,PVARRAY true eps)',
            'S_clone = $allocate_array(S_fixed,$array_empty())',
            'S_clone.RESULT = KNOWN (PARRAY n_clone)',
            '~$array_immutable(S_clone,n_clone)',
            '~$dynamic_global_constant_array_tree(S_clone,PARRAY n_clone,PVARRAY true eps)',
            '$dynamic_global_constant_array_tree(S_clone,PARRAY n_clone,PVARRAY false eps)']
        return values
    request = name == 'defined-request-tree'
    query = 'DefinedTree23' if request else 'GlobalTree23'
    values += receive('S', 'S_initial', query, 'puserconstant', 0, request)
    empty_class = ', (KSTRING ' + text('empty') + ',PVARRAY true eps)' if not request else ''
    leaf_class = 'PVSTRING false' if request else 'PVSCALAR'
    values += ['puserconstant.CLASS = PVARRAY false [(KSTRING ' + text('n') + ',PVSCALAR), (KSTRING ' + text('child') + ',PVARRAY false [(KINT 0,' + leaf_class + ')])' + empty_class + ']',
        'S.ARRAYS[n_array_S].ITEMS = (ENTRY (KSTRING ' + text('n') + ') (DIRECT (PFLOAT 9221120237041090560))) :: (ENTRY (KSTRING ' + text('child') + ') (DIRECT (PARRAY n_child))) :: pentry_tail*',
        'S.ARRAYS[n_child].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_leaf)]',
        'S.ARRAYS[n_child].NEXT = 1',
        'S_bad_class = S[.USERCONSTANTS[0].CLASS = PVARRAY true eps]',
        '$dynamic_global_constant_value(S_bad_class,' + text(query) + ') = eps',
        '~$call_descriptors_valid(S_bad_class)',
        'S_bad_out = $drive(S_bad_class,0)', 'S_bad_out.COMPLETION = UNSUPPORTED text_bad',
        'S_bad_history = S[.ARRAYS[n_child].NEXT = 2]',
        '$dynamic_global_constant_value(S_bad_history,' + text(query) + ') = eps',
        'S_bad_alias = S[.ARRAYS[n_child].ITEMS = [ENTRY (KINT 0) (ALIAS (|S.STORE|))]]',
        '$dynamic_global_constant_value(S_bad_alias,' + text(query) + ') = eps',
        'S_bad_key = S[.ARRAYS[n_child].ITEMS = [ENTRY (KINT 1) (DIRECT pvalue_leaf)]]',
        '$dynamic_global_constant_value(S_bad_key,' + text(query) + ') = eps']
    if request:
        values += ['pentry_tail* = eps',
            'pvalue_leaf = PSTRING_CARRIER (REQUEST_STRING n_string) ' + text('request-value'),
            '$string_carrier_valid(S,pvalue_leaf)',
            'pvalue_bad = PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ' + text('request-value'),
            'S_bad_string = S[.ARRAYS[n_child].ITEMS = [ENTRY (KINT 0) (DIRECT pvalue_bad)]]',
            '$dynamic_global_constant_value(S_bad_string,' + text(query) + ') = eps',
            '~$call_descriptors_valid(S_bad_string)',
            'S_bad_data = S[.STRINGDATA[n_string] = ' + text('different') + ']',
            '$dynamic_global_constant_value(S_bad_data,' + text(query) + ') = eps']
    else:
        values += ['pvalue_leaf = PINT 1',
            'pentry_tail* = [ENTRY (KSTRING ' + text('empty') + ') (DIRECT (PARRAY n_empty))]',
            '$array_immutable(S,n_empty)',
            '~$dynamic_global_constant_array_tree(S,PARRAY (|S.ARRAYS|),PVARRAY true eps)',
            '~$dynamic_global_constant_array_tree(S[.ALLOCATIONS = eps],puserconstant.VALUE,puserconstant.CLASS)']
    values += receive('S_peer', 'S_value', query, 'puserconstant_peer', 0)
    values += ['puserconstant_peer = puserconstant', 'n_array_S_peer = n_array_S']
    return values


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['prepare', 'check'], required=True)
    parser.add_argument('--sources', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out, originals = args.output.resolve(), args.sources.resolve()
    out.mkdir(parents=True, exist_ok=True)
    report_path = out / (args.phase + '-report.json'); assert not report_path.exists()
    native_path = originals / 'native-report.json'
    native = json.loads(native_path.read_bytes())
    assert native['passed'] and native['inputs_stable'] and native['head_stable']
    names = list(sources.family.CASES)
    paths = {name: originals / name / 'main.php' for name in names}
    for name, path in paths.items():
        assert path.read_bytes() == sources.family.CASES[name]
        row, = [row for row in native['records'] if row['id'] == name]
        assert row['source_sha256'] == sha(path)
    watched = [Path(__file__), Path(common.__file__), ROOT / 'tests/semantics/recorded_worker.py',
        ROOT / 'tests/semantics/static_types.py', ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
        native_path, *paths.values()]
    if args.phase == 'check':
        watched += [out / 'prepare-report.json']
        watched += [out / name / item for name in names for item in ('protocol.watsup', 'assertions.json')]
    pins = lambda: dict(sources.family.fingerprint(), **{str(path): sha(path) for path in watched})
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'phase': args.phase, 'revision': head, 'inputs': pins(), 'records': [], 'passed': False}
    try:
        if args.phase == 'prepare':
            frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *types.FLAGS, '-d',
                'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
            try:
                adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
                try:
                    for name, path in paths.items():
                        parsed = frontend.request({'op': 'parse', 'source': b64(path.read_bytes())}); assert parsed['accepted']
                        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                        values = checks(checked['fixture'], path, name)
                        target = out / name; target.mkdir()
                        fixture = target / 'protocol.watsup'
                        (target / 'assertions.json').write_text(json.dumps(values, indent=2) + '\n')
                        fixture.write_text(common.PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
                            ''.join('  -- if ' + value + '\n' for value in values))
                        report['records'].append({'id': name, 'fixture_sha256': sha(fixture), 'premises': len(values)})
                finally:
                    adapter.close()
            finally:
                frontend.close()
        else:
            prepared = json.loads((out / 'prepare-report.json').read_bytes())
            assert prepared['passed'] and prepared['inputs_stable'] and prepared['head_stable']
            assert all(report['inputs'][key] == value for key, value in prepared['inputs'].items())
            assert [row['id'] for row in prepared['records']] == names
            modules = [str(ROOT / name) for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
            for row in prepared['records']:
                target = out / row['id']; fixture = target / 'protocol.watsup'
                assert sha(fixture) == row['fixture_sha256']
                record = dict(row); report['records'].append(record)
                record['process'] = recorder.recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                    '--sl', *modules, str(fixture)], target / 'check', 90)
                assert record['process']['exit'] == 0 and not record['process']['timeout'] and not record['process']['group_after']
                assert (target / 'check.stdout').read_bytes() == b'true\n' and (target / 'check.stderr').read_bytes() == b''
                assert sha(fixture) == row['fixture_sha256']
                record['passed'] = True
                print(record['id'], record['premises'], 'PASS', flush=True)
        report['passed'] = True
    finally:
        report['inputs_stable'] = report['inputs'] == pins()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['passed'] = report['passed'] and report['inputs_stable'] and report['head_stable']
        report_path.write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']


if __name__ == '__main__':
    main()
