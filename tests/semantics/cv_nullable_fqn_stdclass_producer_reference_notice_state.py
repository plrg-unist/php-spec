#!/usr/bin/env python3
"""Ground exact nullable fully qualified stdClass types on the existing quiet object path."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import cv_object_producer_reference_notice_state as prior
import cv_fqn_stdclass_producer_reference_notice_state as compatibility
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_nullable_fqn_stdclass_producer_reference_notice_cases.json')
PREFIX = prior.PREFIX.replace('SingletonObject76', 'SingletonNullableFqnStdClass78').replace('MultiObject76', 'MultiNullableFqnStdClass78')


def class_type(name):
    if '\x00' in name:
        return '[(PTBRANCH ([PTCLASS ([' + ', '.join(map(str, name.encode())) + '])]))]'
    return '[(PTBRANCH ([PTCLASS ($ptascii(' + json.dumps(name) + '))]))]'


def raw_class(name, tag='NNameFullyQualified'):
    return tag + ' (BYTES "' + base64.b64encode(name.encode()).decode() + '") metadata_function'


def nullable_type(name):
    return class_type(name)[:-1] + ', (PTBRANCH ([PTBUILTIN "null"]))]'


def raw_nullable(name, tag='NNameFullyQualified'):
    return 'NNullableType (' + raw_class(name, tag) + ') metadata_function'


def front_lines(index, case):
    compatibility = {'formal_members': [['object']] if index == 0 else [[], ['object']], 'return_members': ['object']}
    lines = prior.front_lines(index, compatibility)
    result = []
    for line in lines:
        line = line.replace('SingletonObject76', 'SingletonNullableFqnStdClass78').replace('MultiObject76', 'MultiNullableFqnStdClass78')
        if line.startswith('pfunction_producer.SIGNATURE.RETURNS = '):
            line = 'pfunction_producer.SIGNATURE.RETURNS = ' + nullable_type(case['class_return'])
        if line.startswith('~psparam.BYREF /\\ psparam.TYPE = '):
            line = r'~psparam.BYREF /\ psparam.TYPE = ' + (nullable_type(case['class_formals'][0]) if index == 0 else 'eps')
        if line.startswith('psparam_last.BYREF /\\ psparam_last.TYPE = '):
            line = r'psparam_last.BYREF /\ psparam_last.TYPE = ' + nullable_type(case['class_formals'][1])
        result.append(line)
    return result


def full_lines(index, case):
    return prior.full_lines(index, case)


def controls(index, case):
    signature = 'pfunction_producer.SIGNATURE'
    header = '$reference_notice_producer_header(phpType6_producer, phpType16, '
    actuals = '([phpType7_first])' if index == 0 else '([phpType7_first, phpType7_last])'
    raw_tail, tail = ('', '') if index == 0 else (', phpType17_last', ', psparam_last')
    lines = ['~$error_call_valid(S_notice, perrorcall[.LINE = 9])',
        '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])',
        '~$typed_return_task_valid(S_return, $(z_return + 1))']
    for spelling in ('stdClass', 'sTdClAsS', 'STDCLASS'):
        normalized, raw = nullable_type(spelling), raw_nullable(spelling)
        parameter = 'NParam (SEQUENCE eps) (INTEGER 0) (' + raw + ') (BOOLEAN false) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter'
        proof = '$reference_notice_producer_arguments(SEQUENCE ' + actuals + ', SEQUENCE ([' + parameter + raw_tail + ']), ' + signature + '[.RETURNS = eps][.PARAMETERS = [psparam[.TYPE = ' + normalized + ']' + tail + ']])'
        lines += [header + raw + ', ' + signature + '[.RETURNS = ' + normalized + '])', proof]
        for strict in ('false', 'true'):
            for value in ('POBJECT n_object', 'PNULL'):
                lines += ['$typed_conversion_at(S_return, ' + normalized + ', ' + value + ', ' + strict + ') = TYPEVALUE (' + value + ')']
            for value in ('PBOOL false', 'PINT 0', 'PSTRING eps'):
                lines += ['$typed_conversion_at(S_return, ' + normalized + ', ' + value + ', ' + strict + ') = TYPEREJECT']
        different_case = 'STDCLASS' if spelling != 'STDCLASS' else 'stdClass'
        bad_types = [class_type(spelling), nullable_type(different_case),
            '[(PTBRANCH ([PTBUILTIN "null"])), ' + class_type(spelling)[1:],
            normalized[:-1] + ', (PTBRANCH ([PTBUILTIN "null"]))]',
            normalized[:-1] + ', (PTBRANCH ([PTBUILTIN "int"]))]']
        for bad in bad_types:
            lines += ['~' + header + raw + ', ' + signature + '[.RETURNS = ' + bad + '])',
                '~' + proof.replace('.TYPE = ' + normalized, '.TYPE = ' + bad)]
        for tag in ('NName', 'NIdentifier'):
            lines += ['~' + header + raw_nullable(spelling, tag) + ', ' + signature + '[.RETURNS = ' + normalized + '])']
        union = 'NUnionType (SEQUENCE ([' + raw_class(spelling) + ', NIdentifier (BYTES "bnVsbA==") metadata_function])) metadata_function'
        lines += ['~' + header + union + ', ' + signature + '[.RETURNS = ' + normalized + '])',
            '~' + header + raw_class(spelling) + ', ' + signature + '[.RETURNS = ' + normalized + '])']
    for name in ('Other', 'Namespace\\stdClass', '\\stdClass', 'stdClass\x00'):
        lines += ['~' + header + raw_nullable(name) + ', ' + signature + '[.RETURNS = ' + nullable_type(name) + '])']
    for update in ('.BYREF = true', '.VARIADIC = true', '.REQUIRED = false', '.DEFAULT = PSDEFAULTUNSUPPORTED "forged nullable FQN stdClass default"'):
        lines += ['~$reference_notice_producer_arguments(phpType6_producer, phpType16, ' + signature + '[.RETURNS = eps][.PARAMETERS = [psparam[' + update + ']' + tail + ']])']
    for stage in ('return', 'notice'):
        lines += ['S_zero_' + stage + ' = $drive(S_' + stage + ', 0)',
            'S_zero_' + stage + r'.COMPLETION = BUDGET /\ S_zero_' + stage + '[.COMPLETION = NORMAL] = S_' + stage,
            '$drive($drive(S_zero_' + stage + '[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_' + stage + ', 2)']
    lines += [line for line in compatibility.controls(index, case) if line.startswith(header + 'NNullableType ')]
    return lines


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-report', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--front', action='store_true')
    args = parser.parse_args()
    native_path = args.native_report.resolve()
    native = json.loads(native_path.read_bytes())
    cases = json.loads(CATALOGUE.read_bytes())
    records = {row['id']: row for row in native['records']}
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    assert native['mode'] == 'native-first' and native['passed'] and native['inputs_stable'] and native['head_stable']
    assert native['profile'] == json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    assert native['runtime_sha256'] == sha(types.PHP) == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    sources = {}
    for i, case in enumerate(cases):
        row = records[case['id']]
        sources[i] = Path(row['command'][-1])
        assert row['passed'] and row['exit'] == 0 and not row['timeout'] and not row['group_after']
        assert sources[i].read_bytes() == case['source'].encode() and sha(sources[i]) == case['source_sha256'] == row['source_sha256']
        assert Path(row['stdout']).read_bytes() == row['actual_stdout'].encode() == case['native_stdout'].encode()
        assert Path(row['stderr']).read_bytes() == row['actual_stderr'].encode() == case['native_stderr'].encode()
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    fixtures = {}
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for i in sources:
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
    reached, derived, specs = [], [], []
    for i, case in enumerate(cases):
        initial = 'S_initial = $php_run(' + fixtures[i] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(sources[i])).decode()) + ')'
        conditions = [initial] + front_lines(i, case)
        extra = []
        if not args.front:
            conditions = [line.removeprefix('~') if line.startswith('~$reference_notice_producer_header(') or (line.startswith('~$reference_notice_producer_arguments(') and '.RETURNS = eps' in line) or line == '~$positional_reference_notice_pending(S_pre)' else line for line in conditions]
            conditions += full_lines(i, case)
            extra = controls(i, case)
        specs.append('dec $scnr_case' + str(i) + '() : bool\ndef $scnr_case' + str(i) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in conditions + extra))
        reached += conditions
        derived += extra
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\n'.join(specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $scnr_case' + str(i) + '()\n' for i in range(len(cases))))
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, Path(__file__), Path(prior.__file__), Path(compatibility.__file__), CATALOGUE, fixture, native_path,
        ROOT / 'spec/semantics/modules.json', ROOT / '_build/default/adapter/main.exe', types.PHP, ROOT / '.tools/php-file.so']
    paths += [ROOT / path for path in ('tests/semantics/error_handler_run.py', 'tests/semantics/profile.json',
        'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py', 'tests/validate.py',
        'tests/corpus.py', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py')]
    for case in cases:
        row = records[case['id']]
        paths += [Path(row['command'][-1]), Path(row['stdout']), Path(row['stderr'])]
    fingerprints = lambda: {str(path): sha(path) for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    recorder.ROOT = ROOT
    print(out, flush=True)
    process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(fixture)], out / 'run', 1200)
    stable = before == fingerprints()
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = (process['exit'] == 0 and not process['timeout'] and not process['group_after'] and stable and head_stable and (out / 'run.stdout').read_bytes() == b'true\n' and not (out / 'run.stderr').read_bytes())
    report = {'revision': revision, 'inputs': before, 'inputs_stable': stable, 'head_stable': head_stable, 'fixture_sha256': sha(fixture), 'conditions': len(reached) + len(derived), 'reached_conditions': len(reached), 'derived_conditions': len(derived), 'module_count': len(modules), 'mode': 'fixture-SL/cache=false/det=true', 'process': process, 'source_agreements': 0, 'passed': passed}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('cv-nullable-fqn-stdclass-front' if args.front else 'cv-nullable-fqn-stdclass-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
