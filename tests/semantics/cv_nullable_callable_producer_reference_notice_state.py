#!/usr/bin/env python3
"""Reach nullable callable verification, exact NULL values and private Notice cells."""
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

import cv_callable_producer_reference_notice_state as prior

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_nullable_callable_producer_reference_notice_cases.json')
PREFIX = prior.PREFIX.replace('82', '83')
CALLABLE = '[(PTBRANCH ([PTBUILTIN "callable"])), (PTBRANCH ([PTBUILTIN "null"]))]'
prior.CALLABLE = CALLABLE


def reached(case, front):
    lines = prior.reached(case, front)
    result = []
    for line in lines:
        if case['carrier'] == 'PNULL':
            if line.startswith(('$string_bytes(', '$string_carrier_valid(', '~$pfunction_builtin(', '$callable_at(', '$function_at(S_return.FUNCTIONS,', '$typed_registered(', '$typed_callable(', 'pvalue_original = PSTRING_CARRIER')):
                continue
            if line == 'S_return.STORE[n_saved] = DEFINED pvalue_original':
                result += ['pvalue_original = PNULL']
        line = line.replace('(NIdentifier (BYTES text_parameter) metadata_type) (BOOLEAN', '(NNullableType (NIdentifier (BYTES text_parameter) metadata_type) metadata_nullable_type) (BOOLEAN')
        if line.startswith('phpType18 = NIdentifier'):
            line = 'phpType18 = NNullableType (NIdentifier (BYTES text_return) metadata_return) metadata_nullable_return'
        result.append(line)
    return result


def completed(case):
    return [line for line in prior.completed(case) if case['carrier'] != 'PNULL' or not line.startswith('$string_carrier_valid(')]


def controls(case):
    lines = ['~$typed_return_task_valid(S_return, $(z_return + 1))',
        '~$error_call_valid(S_notice, perrorcall[.LINE = $(perrorcall.LINE + 1)])',
        '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])']
    for strict in ('false', 'true'):
        lines += ['$typed_conversion_at(S_return, ' + CALLABLE + ', pvalue_original, ' + strict + ') = TYPEVALUE pvalue_original',
            '$typed_conversion_at(S_return, ' + CALLABLE + ', PNULL, ' + strict + ') = TYPEVALUE PNULL']
        for bad in ('PINT 17', 'PBOOL true', 'PSTRING eps', 'PSTRING ($ptascii("missingNullableCallable83"))'):
            lines += ['$typed_conversion_at(S_return, ' + CALLABLE + ', ' + bad + ', ' + strict + ') = TYPEREJECT']
        for field in ('CALLABLES', 'FUNCTIONS'):
            lines += ['$typed_conversion_at(S_return[.' + field + ' = eps], ' + CALLABLE + ', PNULL, ' + strict + ') = TYPEVALUE PNULL']
            if case['carrier'] != 'PNULL':
                lines += ['$typed_conversion_at(S_return[.' + field + ' = eps], ' + CALLABLE + ', pvalue_original, ' + strict + ') = TYPEREJECT']
    for stage in ('return', 'notice'):
        lines += ['S_zero_' + stage + ' = $drive(S_' + stage + ', 0)',
            'S_zero_' + stage + r'.COMPLETION = BUDGET /\ S_zero_' + stage + '[.COMPLETION = NORMAL] = S_' + stage,
            '$drive($drive(S_zero_' + stage + '[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_' + stage + ', 2)']
    signature = 'pfunction_producer.SIGNATURE'
    header = '$reference_notice_producer_header(phpType6_producer, phpType16, '
    for normalized in ('[(PTBRANCH ([PTBUILTIN "null"])), (PTBRANCH ([PTBUILTIN "callable"]))]',
            '[(PTBRANCH ([PTBUILTIN "callable"]))]',
            CALLABLE[:-1] + ', (PTBRANCH ([PTBUILTIN "null"]))]'):
        lines += ['~' + header + 'phpType18, ' + signature + '[.RETURNS = ' + normalized + '])']
    for raw in ('NIdentifier (BYTES text_return) metadata_return',
            'NNullableType (NNameFullyQualified (BYTES text_return) metadata_return) metadata_nullable_return',
            'NUnionType (SEQUENCE ([NIdentifier (BYTES text_return) metadata_return, NIdentifier (BYTES "bnVsbA==") metadata_return])) metadata_nullable_return'):
        lines += ['~' + header + raw + ', ' + signature + ')']
    params = '[psparam, psparam_last]' if case['multiple'] else '[psparam]'
    for update in ('.TYPE = [(PTBRANCH ([PTBUILTIN "callable"]))]',
            '.TYPE = [(PTBRANCH ([PTBUILTIN "null"])), (PTBRANCH ([PTBUILTIN "callable"]))]',
            '.BYREF = ' + str(not case['byref']).lower(), '.REQUIRED = false', '.VARIADIC = true',
            '.DEFAULT = PSDEFAULTUNSUPPORTED "forged nullable callable default"'):
        changed = params.replace('psparam', 'psparam[' + update + ']', 1)
        lines += ['~' + header + 'phpType18, ' + signature + '[.PARAMETERS = ' + changed + '])']
    return lines


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-report', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--front', action='store_true')
    args = parser.parse_args()
    provenance = args.native_report.resolve()
    native, cases = json.loads(provenance.read_bytes()), json.loads(CATALOGUE.read_bytes())
    rows = {row['id']: row for row in native['records']}
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    assert native['mode'] == 'native-first' and native['passed'] and native['inputs_stable'] and native['head_stable']
    assert native['profile'] == types.PROFILE and native['runtime_sha256'] == sha(types.PHP)
    assert set(rows) == {case['id'] for case in cases} and len(cases) == 3
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    paths = [Path(__file__), Path(prior.__file__), CATALOGUE, provenance]
    specs, reached_lines, derived_lines = [], [], []
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for index, case in enumerate(cases):
            row, source = rows[case['id']], Path(rows[case['id']]['command'][-1])
            assert row['passed'] and row['exit'] == 0 and not row['timeout'] and not row['group_after']
            assert source.read_bytes() == case['source'].encode() and sha(source) == case['source_sha256'] == row['source_sha256']
            assert Path(row['stdout']).read_bytes() == row['actual_stdout'].encode() == case['native_stdout'].encode()
            assert Path(row['stderr']).read_bytes() == row['actual_stderr'].encode() == b''
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'] and checked['fixture']
            initial = 'S_initial = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'
            current = [initial] + reached(case, args.front)
            extra = [] if args.front else controls(case)
            if not args.front:
                current += completed(case)
            specs.append('dec $cn_case' + str(index) + '() : bool\ndef $cn_case' + str(index) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in current + extra))
            reached_lines += current
            derived_lines += extra
            paths += [source, Path(row['stdout']), Path(row['stderr'])]
    finally:
        try:
            if frontend:
                frontend.close()
        finally:
            if adapter:
                adapter.close()
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\n'.join(specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $cn_case' + str(index) + '()\n' for index in range(len(cases))))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths += modules + [runner, fixture] + [ROOT / name for name in ('spec/semantics/modules.json', 'tests/semantics/profile.json', '_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py', 'tests/semantics/static_types.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py', 'tests/validate.py', 'tests/corpus.py')]
    fingerprints = lambda: {str(path): sha(path) for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    recorder.ROOT = ROOT
    print(out, flush=True)
    process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(fixture)], out / 'run', 1200)
    stable = before == fingerprints()
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = process['exit'] == 0 and not process['timeout'] and not process['group_after'] and stable and head_stable and (out / 'run.stdout').read_bytes() == b'true\n' and not (out / 'run.stderr').read_bytes()
    report = dict(revision=revision, inputs=before, inputs_stable=stable, head_stable=head_stable, module_count=len(modules), mode='fixture-SL/cache=false/det=true', front=args.front, selection=[case['id'] for case in cases], conditions=len(reached_lines) + len(derived_lines), reached_conditions=len(reached_lines), derived_conditions=len(derived_lines), source_agreements=0, process=process, passed=passed)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('cv-nullable-callable-front' if args.front else 'cv-nullable-callable-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
