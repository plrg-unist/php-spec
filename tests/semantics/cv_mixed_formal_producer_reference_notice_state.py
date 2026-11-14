#!/usr/bin/env python3
"""Ground required mixed formal identity and the ordinary CV Notice argument proof."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import error_handler_run as recorder
from recorded_worker import Worker
import cv_mixed_return_producer_reference_notice_state as prior
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_mixed_formal_producer_reference_notice_cases.json')
PREFIX = prior.PREFIX.replace('MixedStringIdentityReturn67', 'MixedFormalStringIdentity68').replace('MultiCvMixedArrayReturn67', 'MultiCvMixedFormalArray68')
MIXED = prior.MIXED
primitive, multi = prior.primitive, prior.multi


def front_lines(index, case):
    lines = prior.front_lines(index, case)
    if index == 0:
        lines += ['phpType16_parameters = SEQUENCE ([phpType17_mixed])',
            'phpType17_mixed = NParam (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_formal) metadata_formal_type) (BOOLEAN false) (BOOLEAN false) phpType10_saved ABSENT (SEQUENCE eps) metadata_formal',
            '$ptlc($base64(text_formal)) = $ptascii("mixed")']
    else:
        old = 'psparam_first.TYPE = eps /\\ psparam_last.TYPE = eps'
        assert lines.count(old) == 1
        lines = ['psparam_first.TYPE = ' + MIXED + r' /\ psparam_last.TYPE = ' + MIXED if line == old else line for line in lines]
        lines += ['phpType17_first = NParam (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_formal_first) metadata_first_type) (BOOLEAN false) (BOOLEAN false) phpType10_saved ABSENT (SEQUENCE eps) metadata_first_formal',
            'phpType17_last = NParam (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_formal_last) metadata_last_type) (BOOLEAN true) (BOOLEAN false) phpType10_changed ABSENT (SEQUENCE eps) metadata_last_formal',
            '$ptlc($base64(text_formal_first)) = $ptascii("mixed")',
            '$ptlc($base64(text_formal_last)) = $ptascii("mixed")']
    return ['~' + line if line.startswith('$reference_notice_producer_arguments(') else line for line in lines]


def full_lines(index, case):
    return prior.full_lines(index, case)


def controls(index):
    lines = prior.controls(index)
    lines = [line.removeprefix('~') if line.startswith('~$reference_notice_producer_header(') and '.PARAMETERS = ' in line and '.TYPE = ' + MIXED in line else line for line in lines]
    signature = 'pfunction_producer.SIGNATURE'
    actuals = 'phpType7*' if index == 0 else '([phpType7_first, phpType7_last])'
    parameters = '([phpType17_mixed])' if index == 0 else '([phpType17_first, phpType17_last])'
    args = '$reference_notice_producer_arguments(SEQUENCE ' + actuals + ', SEQUENCE '
    normalized = signature + '[.RETURNS = eps]'
    raw = 'NIdentifier (BYTES "bWl4ZWQ=") metadata_type'
    raw_parameter = 'NParam (SEQUENCE eps) (INTEGER 0) __TYPE__ (BOOLEAN __BYREF__) (BOOLEAN false) phpType10_saved ABSENT (SEQUENCE eps) metadata_type'
    slot = 'psparam*[0]' if index == 0 else 'psparam_first'
    tail_raw = '' if index == 0 else ', phpType17_last'
    tail_normalized = '' if index == 0 else ', psparam_last'
    for kind in ('array', 'int', 'float', 'bool', 'string', 'null', 'object'):
        lines += ['~' + args + parameters + ', ' + normalized + '[.PARAMETERS = [' + slot + '[.TYPE = [(PTBRANCH ([PTBUILTIN "' + kind + '"]))]]' + tail_normalized + ']])']
    for typ in ('NNullableType (' + raw + ') metadata_type',
            'NUnionType (SEQUENCE ([' + raw + ', NIdentifier (BYTES "bnVsbA==") metadata_type])) metadata_type',
            'NName (BYTES "bWl4ZWQ=") metadata_type'):
        parameter = raw_parameter.replace('__TYPE__', '(' + typ + ')').replace('__BYREF__', 'false')
        lines += ['~' + args + '([' + parameter + tail_raw + ']), ' + normalized + ')']
    for strict in ('false', 'true'):
        lines += ['$typed_conversion_at(S_args, ' + MIXED + ', PNULL, ' + strict + ') = TYPEVALUE PNULL',
            '$typed_conversion_at(S_args, ' + MIXED + ', pvalue_original, ' + strict + ') = TYPEVALUE pvalue_original']
    lines += [args + parameters + ', ' + normalized + ')']
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
            conditions = [line.removeprefix('~') if line.startswith('~$reference_notice_producer_header(') or line == '~$positional_reference_notice_pending(S_pre)' or (line.startswith('~$reference_notice_producer_arguments(') and '.RETURNS = eps' in line) else line for line in conditions]
            conditions += full_lines(i, case)
            extra = controls(i)
        specs.append('dec $cmf_case' + str(i) + '() : bool\ndef $cmf_case' + str(i) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in conditions + extra))
        reached += conditions
        derived += extra
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\n'.join(specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $cmf_case' + str(i) + '()\n' for i in range(len(cases))))
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, Path(__file__), Path(prior.__file__), Path(primitive.__file__), Path(multi.__file__), CATALOGUE, fixture, native_path, ROOT / 'spec/semantics/modules.json', ROOT / '_build/default/adapter/main.exe', types.PHP, ROOT / '.tools/php-file.so']
    paths += [ROOT / path for path in ('tests/semantics/error_handler_run.py', 'tests/semantics/profile.json', 'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py', 'tests/validate.py', 'tests/corpus.py', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py')]
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
    print('cv-mixed-formal-front' if args.front else 'cv-mixed-formal-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
