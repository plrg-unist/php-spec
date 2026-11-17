#!/usr/bin/env python3
"""Check multiple CV formals, exact ordered-null iterable returns and private cells."""
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
import multi_cv_nullable_iterable_return_producer_reference_notice_state as prior

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('multi_cv_union_null_iterable_return_producer_reference_notice_cases.json')
PREFIX, ITERABLE = prior.PREFIX, prior.ITERABLE


def branches(members):
    return '[' + ', '.join('(PTBRANCH ([PTBUILTIN ' + json.dumps(kind) + ']))' for kind in members) + ']'


def raw_union(members):
    nodes = [prior.RAW if kind == 'iterable' else 'NIdentifier (BYTES text_return_null) metadata_return_null' for kind in members]
    return 'NUnionType (SEQUENCE ([' + ', '.join(nodes) + '])) metadata_return_union'


def reached(case, front):
    lines = []
    for line in prior.reached(case, front):
        if line == 'phpType18 = ' + prior.RAW_NULLABLE:
            lines += ['phpType18 = ' + raw_union(case['return_members']),
                '$ptlc($base64(text_return_null)) = $ptascii("null")']
        else:
            lines.append(line.replace(prior.NULLABLE, branches(case['return_members'])))
    return lines


def completed(case):
    return prior.completed(case)


def controls(case):
    lines = prior.controls(case)
    if case.get('priority_control'):
        return lines
    lines.insert(0, 'metadata_return_nullable = metadata_return_union')
    header = '$reference_notice_producer_header(phpType6_producer, phpType16, '
    signature = 'pfunction_producer.SIGNATURE'
    nullable_upper = header + 'NNullableType (NIdentifier (BYTES "SVRFUkFCTEU=") metadata_return) metadata_return_nullable, ' + signature + ')'
    assert nullable_upper in lines
    lines[lines.index(nullable_upper)] = nullable_upper[:-1] + '[.RETURNS = ' + prior.NULLABLE + '])'
    lines += ['~' + header + 'phpType18, ' + signature + '[.RETURNS = ' + branches(list(reversed(case['return_members']))) + '])',
        '~' + header + 'phpType18, ' + signature + '[.RETURNS = ' + ITERABLE + '])']
    for members in (['iterable', 'int'], ['int', 'iterable'], ['iterable', 'false'], ['false', 'iterable'],
            ['iterable', 'array'], ['array', 'iterable'], ['iterable', 'null', 'int']):
        nodes = [prior.RAW if kind == 'iterable' else 'NIdentifier (BYTES ' + json.dumps(base64.b64encode(kind.encode()).decode()) + ') metadata_return_null' for kind in members]
        raw = 'NUnionType (SEQUENCE ([' + ', '.join(nodes) + '])) metadata_return_union'
        polarity = '' if members in (['iterable', 'int'], ['int', 'iterable'], ['iterable', 'false'], ['false', 'iterable']) else '~'
        lines.append(polarity + header + raw + ', ' + signature + '[.RETURNS = ' + branches(members) + '])')
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
    assert set(rows) == {case['id'] for case in cases} and len(cases) == 4
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    paths = [Path(__file__), Path(prior.__file__), Path(prior.prior.__file__), Path(prior.prior.prior.__file__), CATALOGUE, provenance]
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
            specs.append('dec $ir_case' + str(index) + '() : bool\ndef $ir_case' + str(index) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in current + extra))
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
    prefix = PREFIX
    for marker, name in (('NAMES_MAKE', 'make'), ('NAMES_TAKE', 'take')):
        prefix = prefix.replace(marker, '[' + ', '.join('$ptascii(' + json.dumps(case['namespace'] + '\\' + name) + ')' for case in cases) + ']')
    fixture = out / 'state.watsup'
    fixture.write_text(prefix + '\n'.join(specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $ir_case' + str(index) + '()\n' for index in range(len(cases))))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths += modules + [runner, fixture] + [ROOT / name for name in ('spec/semantics/modules.json', 'tests/semantics/profile.json', '_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py', 'tests/semantics/static_types.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py')]
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
    print('multi-cv-union-null-iterable-return-front' if args.front else 'multi-cv-union-null-iterable-return-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
