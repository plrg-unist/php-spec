#!/usr/bin/env python3
"""Reach callable/float verification, strict integer widening and Notice cells."""
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
import cv_int_callable_producer_reference_notice_state as prior
import cv_string_callable_producer_reference_notice_state as string_prior

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_float_callable_producer_reference_notice_cases.json')
PREFIX = prior.PREFIX.replace('86', '87')
branches, raw = string_prior.branches, string_prior.raw


def reached(case, front):
    adapted = dict(case, value_kind='integer' if case['value_kind'] == 'float' else 'callable')
    lines = prior.reached(adapted, front)
    if case['value_kind'] == 'float':
        value = 'PFLOAT $float_of_int(' + str(case['integer']) + ')'
        lines = [line.replace('pvalue_original = PINT ' + str(case['integer']), 'pvalue_original = ' + value) for line in lines]
        lines = [line.replace('$typed_parameter_conversion(S_receive, psparam, pvalue_caller) = ' + ('TYPEINTEGER pvalue_caller' if case['weak_receive'] else 'TYPEVALUE pvalue_caller'),
            '$typed_parameter_conversion(S_receive, psparam, pvalue_caller) = TYPEVALUE pvalue_original') for line in lines]
        if not case['weak_receive']:
            lines = [line.replace('pvalue_caller = pvalue_original', 'pvalue_caller = PINT ' + str(case['integer'])) for line in lines]
            for slot in ('S_return.STORE[n_copy]', 'S_pre.STORE[n_copy]'):
                lines = [line.replace(slot + ' = DEFINED pvalue_original', slot + ' = DEFINED pvalue_caller') for line in lines]
    return lines


def completed(case):
    adapted = dict(case, value_kind='integer' if case['value_kind'] == 'float' else 'callable')
    lines = prior.completed(adapted)
    if case['value_kind'] == 'float' and not case['weak_receive']:
        lines = [line.replace('S_resume.STORE[n_copy] = DEFINED pvalue_original', 'S_resume.STORE[n_copy] = DEFINED pvalue_caller') for line in lines]
    return lines


def controls(case):
    lines = [line for line in string_prior.controls(case) if not line.startswith('$typed_conversion_at(')]
    for normalized in (branches(['callable', 'float']), branches(['float', 'callable'])):
        for strict in ('false', 'true'):
            lines += ['$typed_conversion_at(S_return, ' + normalized + ', pvalue_original, ' + strict + ') = TYPEVALUE pvalue_original',
                '$typed_conversion_at(S_return, ' + normalized + ', PNULL, ' + strict + ') = TYPEREJECT',
                '$typed_conversion_at(S_return, ' + normalized + ', PINT 17, ' + strict + ') = TYPEVALUE (PFLOAT $float_of_int(17))',
                '$typed_conversion_at(S_return, ' + normalized + ', PSTRING ($ptascii("notRegistered87")), ' + strict + ') = TYPEREJECT']
            for field in ('CALLABLES', 'FUNCTIONS', 'CLASSES'):
                lines += ['$typed_conversion_at(S_return[.' + field + ' = eps], ' + normalized + ', PFLOAT $float_of_int(17), ' + strict + ') = TYPEVALUE (PFLOAT $float_of_int(17))']
            if case['value_kind'] == 'callable':
                for field in ('CALLABLES', 'FUNCTIONS'):
                    lines += ['$typed_conversion_at(S_return[.' + field + ' = eps], ' + normalized + ', pvalue_original, ' + strict + ') = TYPEREJECT']
        for value, integer in (('PSTRING ($ptascii("17"))', 17), ('PBOOL true', 1)):
            lines += ['$typed_conversion_at(S_return, ' + normalized + ', ' + value + ', false) = TYPEVALUE (PFLOAT $float_of_int(' + str(integer) + '))',
                '$typed_conversion_at(S_return, ' + normalized + ', ' + value + ', true) = TYPEREJECT']
        members = ['callable', 'float'] if normalized == branches(['callable', 'float']) else ['float', 'callable']
        atoms = ', '.join('NIdentifier (BYTES ' + json.dumps(base64.b64encode(kind.encode()).decode()) + ') metadata_return_first' for kind in members)
        changed = 'NUnionType (SEQUENCE ([' + atoms + '])) metadata_union_return'
        lines += ['$reference_notice_producer_header(phpType6_producer, phpType16, ' + changed + ', pfunction_producer.SIGNATURE[.RETURNS = ' + normalized + '])']
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
    paths = [Path(__file__), Path(prior.__file__), Path(string_prior.__file__), Path(prior.prior.__file__), Path(prior.union_prior.__file__), CATALOGUE, provenance]
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
    print('cv-float-callable-front' if args.front else 'cv-float-callable-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
