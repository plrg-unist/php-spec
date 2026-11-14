#!/usr/bin/env python3
"""Reach exact singleton-Boolean callable headers and private Notice cells."""
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
import cv_bool_callable_producer_reference_notice_state as prior
import cv_string_callable_producer_reference_notice_state as string_prior

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_literal_bool_callable_producer_reference_notice_cases.json')
PREFIX = prior.PREFIX.replace('88', '89')
branches, raw = string_prior.branches, string_prior.raw
reached, completed = prior.reached, prior.completed


def controls(case):
    lines = [line for line in string_prior.controls(case) if not line.startswith('$typed_conversion_at(')]
    for kind in ('true', 'false'):
        for members in (['callable', kind], [kind, 'callable']):
            normalized = branches(members)
            lines += ['$ptmasks(' + normalized + ') = [' + ', '.join(json.dumps(member) for member in members) + ']']
            for strict in ('false', 'true'):
                accepted = case['value_kind'] == 'callable' or case['bool_value'] == (kind == 'true')
                lines += ['$typed_conversion_at(S_return, ' + normalized + ', pvalue_original, ' + strict + ') = ' + ('TYPEVALUE pvalue_original' if accepted else 'TYPEREJECT'),
                    '$typed_conversion_at(S_return, ' + normalized + ', PBOOL ' + kind + ', ' + strict + ') = TYPEVALUE (PBOOL ' + kind + ')',
                    '$typed_conversion_at(S_return[.CALLABLES = eps][.FUNCTIONS = eps][.CLASSES = eps], ' + normalized + ', PBOOL ' + kind + ', ' + strict + ') = TYPEVALUE (PBOOL ' + kind + ')']
                for value in ('PBOOL ' + ('false' if kind == 'true' else 'true'), 'PNULL', 'PINT 0', 'PINT 17', 'PFLOAT $float_of_int(2)', 'PSTRING ($ptascii("17"))', 'PSTRING ($ptascii("0"))', 'PSTRING eps', 'PSTRING ($ptascii("notRegistered89"))'):
                    lines += ['$typed_conversion_at(S_return, ' + normalized + ', ' + value + ', ' + strict + ') = TYPEREJECT']
                if case['value_kind'] == 'callable':
                    for field in ('CALLABLES', 'FUNCTIONS'):
                        lines += ['$typed_conversion_at(S_return[.' + field + ' = eps], ' + normalized + ', pvalue_original, ' + strict + ') = TYPEREJECT']
            atoms = ', '.join('NIdentifier (BYTES ' + json.dumps(base64.b64encode(member.encode()).decode()) + ') metadata_return_first' for member in members)
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
    paths = [Path(__file__), Path(prior.__file__), Path(string_prior.__file__), Path(prior.prior.__file__), Path(prior.prior.prior.__file__), Path(prior.prior.union_prior.__file__), CATALOGUE, provenance]
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
    print('cv-literal-bool-callable-front' if args.front else 'cv-literal-bool-callable-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
