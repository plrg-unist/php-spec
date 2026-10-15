#!/usr/bin/env python3
"""Reached certified-instance queries, shared properties and RESULT ownership."""
import argparse
import base64
import json
import os
from pathlib import Path
import subprocess

import class_constant_call_protocol as common
import error_handler_run as recorder
import global_constant_instance_sources as sources
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
recorder.ROOT = ROOT
b64 = lambda data: base64.b64encode(data).decode()
sha = sources.family.sha
text = lambda value: '$ptascii(' + json.dumps(value) + ')'


def receive(state, start, query, value):
    call, row, obj = 'pconfigcall_' + state, 'puserconstant_' + state, 'pconstantobject_' + state
    values = [*common.reach(state, start, 0, query),
        state + '.TODO = (CONFIG_INVOKE ' + call + ') :: ptask_' + state + '*',
        '$dynamic_global_constant_call(' + call + ')',
        '$dynamic_global_constant_valid(' + state + ',' + call + ')',
        call + '.OWNER = eps', call + '.PACKS = eps',
        state + '.USERCONSTANTS = [' + row + ']', row + '.NAME = ' + text(query),
        row + '.VALUE = POBJECT n_object', row + '.CLASS = PVINSTANCE n_object porigin_site',
        '$global_new_record(' + state + '.CONSTANTOBJECTS,n_object) = (' + obj + ')',
        state + '.CONSTANTOBJECTS = [' + obj + ']',
        obj + '.OBJECT = n_object', obj + '.SITE = porigin_site', obj + '.DECL = ' + row + '.ORIGIN',
        '$global_new_completed(' + state + ',' + obj + ')',
        state + '.OBJECTS[n_object] = INSTANCE ' + obj + '.CLASS',
        '$constant_value_class_valid(' + state + ',' + row + '.VALUE,' + row + '.CLASS)',
        '$dynamic_global_constant_value(' + state + ',' + text(query) + ') = (' + row + '.VALUE)',
        '$objectprops_at(' + state + '.OBJECTPROPS,n_object) = (ppropertyslot_all_' + state + '*)',
        '$property_slot_at(ppropertyslot_all_' + state + '*,' + text('value') + ') = (ppropertyslot_' + state + ')',
        'ppropertyslot_' + state + '.STATE = PROP_VALUE (DIRECT (PINT ' + str(value) + '))',
        '$user_constant_roots(' + state + '.USERCONSTANTS) = [HOBJECT n_object]',
        'H_' + state + ' = $heap_graph(' + state + ')',
        'n_owners_' + state + ' = $heap_owners(H_' + state + ',HOBJECT n_object)',
        '$(n_owners_' + state + ' > 0)', *common.public(state)]
    after = state + '_value'
    values += common.step(after, state, 'POBJECT n_object')
    values += [after + '.TODO = ptask_' + state + '*', after + '.BASE = BASE_VALUE (KNOWN PNULL)',
        'H_' + after + ' = $heap_graph(' + after + ')',
        'H_' + after + '.NODES = H_' + state + '.NODES', 'H_' + after + '.EDGES = H_' + state + '.EDGES',
        '$heap_owners(H_' + after + ',HOBJECT n_object) = $(n_owners_' + state + ' + 1)']
    values += [after + '.' + field + ' = ' + state + '.' + field for field in (
        'OBJECTS', 'OBJECTPROPS', 'OBJECTTABLES', 'PROPREFS', 'ALLOCATIONS', 'CONSTANTOBJECTS',
        'USERCONSTANTS', 'ARRAYS', 'STRINGDATA', 'STORE', 'POOLS', 'SOURCES', 'FILES', 'SELECTEDCALLS')]
    return values


def checks(program, path, name):
    plain = name == 'plain-instance-identity-and-mutation'
    query, initial, mutated = ('GlobalPlain24', 3, 9) if plain else ('GlobalBuilt24', 5, 12)
    values = ['S_initial = $php_run(' + program + ',0,' + json.dumps(b64(os.fsencode(path))) + ')',
        'S_initial.COMPLETION = BUDGET', *receive('S', 'S_initial', query, initial),
        'n_owners_S = 1',
        'S_pause = $drive_steps(S,0)', 'S_pause = S[.COMPLETION = BUDGET]',
        'S_one = $drive_steps(S,1)', 'S_one = $drive_steps(S_pause[.COMPLETION = NORMAL],1)',
        'S_one[.COMPLETION = NORMAL] = S_value']
    if plain:
        values += ['pconfigcall_S.SELECTION = eps', *receive('S_peer', 'S_value', query, initial),
            'puserconstant_S_peer = puserconstant_S']
        start = 'S_peer_value'
    else:
        values += ['pconfigcall_S.SELECTION = (n_selection)', '$(n_selection < |S.SELECTEDCALLS|)',
            'S.SELECTEDCALLS[n_selection].KIND = INTRINSIC_CONSTANT']
        start = 'S_value'
    values += receive('S_again', start, query, mutated)
    values += ['puserconstant_S_again = puserconstant_S',
        'n_owners_S_again = 1',
        'pconstantobject_S_again = pconstantobject_S',
        'S_bad_id = S[.USERCONSTANTS[0].VALUE = POBJECT (|S.OBJECTS|)]',
        'S_bad_site = S[.USERCONSTANTS[0].CLASS = PVINSTANCE n_object pconfigcall_S.SITE]',
        'S_bad_complete = S[.CONSTANTOBJECTS[0].COMPLETE = false]',
        'S_bad_generic = S[.USERCONSTANTS[0].CLASS = PVOBJECT]',
        'S_bad_live = S[.ALLOCATIONS = eps]']
    for bad in ('id', 'site', 'complete', 'generic', 'live'):
        values += ['$dynamic_global_constant_value(S_bad_' + bad + ',' + text(query) + ') = eps',
            '~$call_descriptors_valid(S_bad_' + bad + ')']
    values += ['S_bad_out = $drive(S_bad_generic,0)', 'S_bad_out.COMPLETION = UNSUPPORTED text_bad',
        '$constant_value_class_valid(S,POBJECT n_object,PVOBJECT)',
        '~$global_constant_class_supported(PVOBJECT)']
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
