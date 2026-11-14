#!/usr/bin/env python3
"""Ground ordered kind/null formals, caller snapshots and private Notice cells."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types
import multi_cv_scalar_formal_producer_reference_notice_state as prior

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_union_null_formal_producer_reference_notice_cases.json')
PREFIX = prior.PREFIX.replace('MultiCvScalarFormalString57', 'CvUnionNullFormalString61').replace('MultiCvScalarFormal57', 'CvUnionNullFormal61')


def union_raw(kind, metadata, reverse):
    members = ['NIdentifier (BYTES ' + kind + ') ' + metadata + '_type',
               'NIdentifier (BYTES "bnVsbA==") ' + metadata + '_null']
    if reverse:
        members.reverse()
    return '(NUnionType (SEQUENCE ([' + ', '.join(members) + '])) ' + metadata + '_union)'


def union_type(kind, reverse):
    members = ['(PTBRANCH ([PTBUILTIN "' + kind + '"]))', '(PTBRANCH ([PTBUILTIN "null"]))']
    if reverse:
        members.reverse()
    return '[' + ', '.join(members) + ']'


def front_lines(index, case):
    lines = prior.front_lines(index, case)
    for which, kind, reverse in zip(('first', 'last'), case['formal_kinds'], case['formal_null_first']):
        raw = '(NIdentifier (BYTES text_' + which + '_type) metadata_' + which + '_type)'
        replacement = union_raw('text_' + which + '_type', 'metadata_' + which, reverse)
        lines = [line.replace(raw, replacement) if line.startswith('phpType17_' + which + ' = NParam') else line for line in lines]
        lines = ['psparam_' + which + '.TYPE = ' + union_type(kind, reverse) if line.startswith('psparam_' + which + '.TYPE =') else line for line in lines]
    if index == 0:
        changes = {
            'pvalue_y_original = PSTRING_CARRIER INTERNED_STRING ($ptascii("0"))': 'pvalue_y_original = PINT 17',
            'pvalue_received_last = PBOOL false': 'pvalue_received_last = PFLOAT 4625478292286210048',
            '$typed_parameter_conversion(S_receive_last, psparam_last, pvalue_y_original) = TYPEBOOL pvalue_y_original': '$typed_parameter_conversion(S_receive_last, psparam_last, pvalue_y_original) = TYPEVALUE (PFLOAT 4625478292286210048)',
        }
    else:
        changes = {
            'pvalue_y_original = PINT 17': 'pvalue_y_original = PNULL',
            'pvalue_received_last = PFLOAT 4625478292286210048': 'pvalue_received_last = PNULL',
            '$typed_parameter_conversion(S_receive_last, psparam_last, pvalue_y_original) = TYPEVALUE (PFLOAT 4625478292286210048)': '$typed_parameter_conversion(S_receive_last, psparam_last, pvalue_y_original) = TYPEVALUE PNULL',
        }
    return [changes.get(line, line) for line in lines]


def full_lines(index, case):
    return prior.full_lines(index, case)


def controls(index):
    lines = [line for line in prior.controls(index) if not line.startswith('phpType17_nullable = ') and 'SEQUENCE ([phpType17_nullable, phpType17_last])' not in line]
    arguments = '$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), '
    signature = 'pfunction_producer.SIGNATURE[.RETURNS = eps]'
    lines += [
        '~' + arguments + signature + '[.PARAMETERS = [psparam_first[.TYPE = [psparam_first.TYPE[1], psparam_first.TYPE[0]]], psparam_last]])',
        '~' + arguments + signature + '[.PARAMETERS = [psparam_first[.REQUIRED = false], psparam_last]])',
        '~' + arguments + signature + '[.PARAMETERS = [psparam_first[.VARIADIC = true], psparam_last]])',
        'phpType17_nullable_int_last = NParam (SEQUENCE eps) (INTEGER 0) (NNullableType (NIdentifier (BYTES "aW50") metadata_last_type) metadata_last_union) (BOOLEAN true) (BOOLEAN false) phpType10_last ABSENT (SEQUENCE eps) metadata_last_parameter',
    ]
    for kind in ('array', 'int', 'float', 'bool', 'string'):
        encoded = '"' + base64.b64encode(kind.encode()).decode() + '"'
        for reverse in (False, True):
            name = 'phpType17_' + kind + ('_null_first' if reverse else '_null_last')
            raw = union_raw(encoded, 'metadata_first', reverse)
            lines += [name + ' = NParam (SEQUENCE eps) (INTEGER 0) ' + raw + ' (BOOLEAN false) (BOOLEAN false) phpType10_first ABSENT (SEQUENCE eps) metadata_first_parameter',
                arguments.replace('phpType17_first,', name + ',') + signature + '[.PARAMETERS = [psparam_first[.TYPE = ' + union_type(kind, reverse) + '], psparam_last]])']
            if kind in ('array', 'bool') and not reverse:
                lines += [arguments.replace('phpType17_first, phpType17_last', name + ', phpType17_nullable_int_last') + signature + '[.PARAMETERS = [psparam_first[.TYPE = ' + union_type(kind, False) + '], psparam_last[.TYPE = ' + union_type('int', False) + ']]])']
    for members in (('int', 'float'), ('null', 'null'), ('int', 'null', 'bool')):
        name = 'phpType17_bad_' + '_'.join(members)
        raw = ['NIdentifier (BYTES "' + base64.b64encode(kind.encode()).decode() + '") metadata_first_type' for kind in members]
        normalized = '[' + ', '.join('(PTBRANCH ([PTBUILTIN "' + kind + '"]))' for kind in members) + ']'
        lines += [name + ' = NParam (SEQUENCE eps) (INTEGER 0) (NUnionType (SEQUENCE ([' + ', '.join(raw) + '])) metadata_first_union) (BOOLEAN false) (BOOLEAN false) phpType10_first ABSENT (SEQUENCE eps) metadata_first_parameter',
            ('' if members == ('int', 'float') else '~') + arguments.replace('phpType17_first,', name + ',') + signature + '[.PARAMETERS = [psparam_first[.TYPE = ' + normalized + '], psparam_last]])']
    return lines


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-report', required=True, type=Path, action='append')
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--front', action='store_true')
    args = parser.parse_args()
    native_paths = [path.resolve() for path in args.native_report]
    natives = [json.loads(path.read_bytes()) for path in native_paths]
    cases = json.loads(CATALOGUE.read_bytes())
    records = {}
    for native in natives:
        for row in native['records']:
            assert row['id'] not in records
            records[row['id']] = row
    selected = [0, 1]
    sources = {i: Path(records[cases[i]['id']]['command'][-1]) for i in selected}
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    for native in natives:
        assert native['mode'] == 'native-first' and native['passed'] and native['inputs_stable'] and native['head_stable']
        assert native['profile'] == json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
        assert native['runtime_sha256'] == sha(types.PHP) == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    for i in selected:
        case, record = cases[i], records[cases[i]['id']]
        assert record['passed'] and record['exit'] == 0 and not record['timeout'] and not record['group_after']
        assert sources[i].read_bytes() == case['source'].encode() and sha(sources[i]) == case['source_sha256'] == record['source_sha256']
        assert Path(record['stdout']).read_bytes() == record['actual_stdout'].encode() == case['native_stdout'].encode()
        assert Path(record['stderr']).read_bytes() == record['actual_stderr'].encode() == case['native_stderr'].encode()
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    fixtures = {}
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for i in selected:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(sources[i].read_bytes()).decode()})
            assert parsed['accepted']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'] and checked['fixture']
            fixtures[i] = checked['fixture']
    finally:
        try:
            if frontend:
                frontend.close()
        finally:
            if adapter:
                adapter.close()
    def initial(name, i):
        return name + ' = $php_run(' + fixtures[i] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(sources[i])).decode()) + ')'
    case_specs = []
    reached = []
    derived = []
    for i in selected:
        conditions = [initial('S_initial', i)] + front_lines(i, cases[i])
        current_derived = []
        if not args.front:
            conditions = [line.removeprefix('~') if line.startswith('~$reference_notice_producer_header(') or line.startswith('~$reference_notice_producer_arguments(') or line == '~$positional_reference_notice_pending(S_pre)' else line for line in conditions]
            conditions += full_lines(i, cases[i])
            current_derived = controls(i)
        case_specs.append('dec $mcsf_case' + str(i) + '() : bool\ndef $mcsf_case' + str(i) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in conditions + current_derived))
        reached += conditions
        derived += current_derived
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\n' + '\n'.join(case_specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $mcsf_case' + str(i) + '()\n' for i in selected))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, Path(__file__), Path(prior.__file__), CATALOGUE, fixture, *native_paths, ROOT / 'spec/semantics/modules.json', ROOT / '_build/default/adapter/main.exe', types.PHP, ROOT / '.tools/php-file.so', ROOT / 'tests/semantics/error_handler_run.py']
    paths += [ROOT / path for path in ('tests/semantics/profile.json', 'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py')]
    for i in selected:
        paths += [sources[i], Path(records[cases[i]['id']]['stdout']), Path(records[cases[i]['id']]['stderr'])]
    fingerprints = lambda: {str(path): sha(path) for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    recorder.ROOT = ROOT
    print(out, flush=True)
    process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(fixture)], out / 'run', 1200)
    stable = before == fingerprints()
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = (process['exit'] == 0 and not process['timeout'] and not process['group_after'] and stable and head_stable
        and (out / 'run.stdout').read_bytes() == b'true\n' and not (out / 'run.stderr').read_bytes())
    report = {'revision': revision, 'inputs': before, 'inputs_stable': stable, 'head_stable': head_stable, 'fixture_sha256': sha(fixture), 'part': 'cv-union-null-formal-producer-front' if args.front else 'cv-union-null-formal-producer-notice', 'conditions': len(reached) + len(derived), 'reached_conditions': len(reached), 'derived_conditions': len(derived), 'heap_bindings': sum(line.startswith('H_') and ' = $heap_graph(' in line for line in reached), 'module_count': len(modules), 'mode': 'SL/cache=false/det=true', 'process': process, 'source_agreements': 0, 'passed': passed}
    report['selected_sources'] = {cases[i]['id']: sha(sources[i]) for i in selected}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(report['part'], passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
