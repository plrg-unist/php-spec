#!/usr/bin/env python3
"""Ground standalone mixed identity, frame retirement and private Notice cells."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import error_handler_run as recorder
from recorded_worker import Worker
import cv_primitive_union_return_producer_reference_notice_state as primitive
import multi_cv_nullable_array_return_producer_reference_notice_state as multi
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_mixed_return_producer_reference_notice_cases.json')
PREFIX = (primitive.PREFIX.replace('PrimitiveUnionStringIdentityReturn65', 'MixedStringIdentityReturn67')
    + multi.PREFIX.replace('MultiCvNullableArray52', 'MultiCvMixedArrayReturn67'))
MIXED = '[(PTBRANCH ([PTBUILTIN "mixed"]))]'


def front_lines(index, case):
    if index == 0:
        lines = primitive.front_lines(0, dict(case, return_members=['float', 'int', 'string']))
        lines = [line for line in lines if not line.startswith(('|phpType69_return*|', 'phpType69_return*[', '$ptlc($base64(text_return_'))]
        replacements = {
            'pfunction_producer.SIGNATURE.RETURNS = ' + primitive.branches(['float', 'int', 'string']):
                'pfunction_producer.SIGNATURE.RETURNS = ' + MIXED,
            'phpType18_return = NUnionType (SEQUENCE phpType69_return*) metadata_union':
                'phpType18_return = NIdentifier (BYTES text_return) metadata_type'}
    else:
        lines = list(multi.BASE + multi.VERIFY + multi.CONTINUE + multi.COPY)
        replacements = {
            'pfunction_producer.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "array"])), (PTBRANCH ([PTBUILTIN "null"]))] /\\ ~pfunction_producer.SIGNATURE.BYREF':
                'pfunction_producer.SIGNATURE.RETURNS = ' + MIXED + r' /\ ~pfunction_producer.SIGNATURE.BYREF',
            'phpType18_return = NNullableType (NIdentifier (BYTES text_return) metadata_type) metadata_return':
                'phpType18_return = NIdentifier (BYTES text_return) metadata_type',
            '$ptlc($base64(text_return)) = $ptascii("array")':
                '$ptlc($base64(text_return)) = $ptascii("mixed")'}
        lines += ['$mcn_output(S_pre.EVENTS) = $ptascii("A;M:17:23:0;")',
            r'psparam_first.DEFAULT = PSNONE /\ psparam_last.DEFAULT = PSNONE']
    for old, new in replacements.items():
        assert lines.count(old) == 1
        lines = [new if line == old else line for line in lines]
    if index == 0:
        lines += ['$ptlc($base64(text_return)) = $ptascii("mixed")']
    for old, new in {'ARG_OWNERS': '3', 'FORMAL_OWNERS': '2', 'RETURN_OWNERS': '3', 'PRE_OWNERS': '2'}.items():
        lines = [line.replace(old, new) for line in lines]
    return lines


def full_lines(index, case):
    if index == 0:
        return primitive.full_lines(0, case)
    lines = ['~((HCELL n_original_x) <- S_pre.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_pre), HCELL n_original_x) = 0'] + multi.PRIVATE + multi.NORMAL + [
        '~$named_reference_notice_array(S_written, PARRAY n_current)',
        '$mcn_output(S_full.EVENTS) = $ptascii(' + json.dumps(case['native_stdout']) + ')']
    return [line.replace('PRE_OWNERS', '2') for line in lines]


def controls(index):
    arguments = ('SEQUENCE phpType7*, phpType16_parameters, ' if index == 0 else
        'SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), ')
    signature = 'pfunction_producer.SIGNATURE'
    header = '$reference_notice_producer_header(' + arguments
    raw = 'phpType18_return'
    metadata = 'metadata_type'
    lines = ['~$typed_return_task_valid(S_return, $(z_return + 1))',
        '~$error_call_valid(S_notice, perrorcall[.LINE = $(perrorcall.LINE + 1)])',
        '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])',
        '~' + header + 'ABSENT, ' + signature + ')',
        header + 'NIdentifier (BYTES "bUlYZUQ=") ' + metadata + ', ' + signature + ')',
        '~' + header + 'NNullableType (NIdentifier (BYTES "bWl4ZWQ=") ' + metadata + ') ' + metadata + ', ' + signature + ')',
        '$reference_notice_producer_header(SEQUENCE eps, SEQUENCE eps, ' + raw + ', ' + signature + '[.PARAMETERS = eps])',
        'S_zero = $drive(S_notice, 0)',
        r'S_zero.COMPLETION = BUDGET /\ S_zero[.COMPLETION = NORMAL] = S_notice',
        '$drive($drive(S_zero[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_notice, 2)']
    for kind in ('array', 'int', 'float', 'bool', 'string', 'null', 'object', 'void', 'never'):
        encoded = base64.b64encode(kind.encode()).decode()
        lines += ['~' + header + raw + ', ' + signature + '[.RETURNS = [(PTBRANCH ([PTBUILTIN "' + kind + '"]))]])',
            '~' + header + 'NIdentifier (BYTES "' + encoded + '") ' + metadata + ', ' + signature + ')']
    for members in (('mixed', 'null'), ('array', 'mixed'), ('mixed', 'array', 'null')):
        raw_union = 'NUnionType (SEQUENCE ([' + ', '.join('NIdentifier (BYTES "' + base64.b64encode(kind.encode()).decode() + '") ' + metadata for kind in members) + '])) ' + metadata
        normalized = primitive.branches(members)
        lines += ['~' + header + raw_union + ', ' + signature + '[.RETURNS = ' + normalized + '])',
            '~' + header + raw_union + ', ' + signature + ')',
            '~' + header + raw + ', ' + signature + '[.RETURNS = ' + normalized + '])']
    for strict in ('false', 'true'):
        for value in ('PNULL', 'PBOOL false', 'PINT 17', 'PFLOAT 0', 'PSTRING eps'):
            lines += ['$typed_conversion(' + signature + '.RETURNS, ' + value + ', ' + strict + ') = TYPEVALUE (' + value + ')']
        value = 'pvalue_original' if index == 0 else 'PARRAY n_root'
        lines += ['$typed_conversion_at(S_return, ' + signature + '.RETURNS, ' + value + ', ' + strict + ') = TYPEVALUE (' + value + ')']
    parameters = ['psparam*[0]'] if index == 0 else ['psparam_first', 'psparam_last']
    for update in ('.TYPE = ' + MIXED, '.BYREF = true' if index == 0 else '.BYREF = false', '.VARIADIC = true', '.REQUIRED = false'):
        altered = parameters.copy()
        position = 0 if index == 0 else 1
        altered[position] += '[' + update + ']'
        lines += ['~' + header + raw + ', ' + signature + '[.PARAMETERS = [' + ', '.join(altered) + ']])']
    if index == 1:
        lines += ['S_zero_retired = $drive(S_retired, 0)',
            r'S_zero_retired.COMPLETION = BUDGET /\ S_zero_retired[.COMPLETION = NORMAL] = S_retired',
            '$drive($drive(S_zero_retired[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_retired, 2)']
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
            conditions = [line.removeprefix('~') if line.startswith('~$reference_notice_producer_header(') or line == '~$positional_reference_notice_pending(S_pre)' else line for line in conditions]
            conditions += full_lines(i, case)
            extra = controls(i)
        specs.append('dec $cmr_case' + str(i) + '() : bool\ndef $cmr_case' + str(i) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in conditions + extra))
        reached += conditions
        derived += extra
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\n'.join(specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $cmr_case' + str(i) + '()\n' for i in range(len(cases))))
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, Path(__file__), Path(primitive.__file__), Path(multi.__file__), CATALOGUE, fixture, native_path, ROOT / 'spec/semantics/modules.json', ROOT / '_build/default/adapter/main.exe', types.PHP, ROOT / '.tools/php-file.so']
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
    print('cv-mixed-return-front' if args.front else 'cv-mixed-return-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
