#!/usr/bin/env python3
"""Check ordered builtin/iterable RETURN members and existing ordinary-CV private cells."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types
import cv_union_literal_bool_iterable_return_producer_reference_notice_state as prior

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_builtin_union_iterable_return_producer_reference_notice_cases.json')
PREFIX, branches = prior.PREFIX, prior.branches
single, multi = prior.single, prior.multi
old_bool_review, old_string, old_string_review = prior.old_bool_review, prior.old_string, prior.old_string_review
FOLD = '$reference_notice_producer_iterable_return_union_members'


def nodes(members, leaf='NIdentifier'):
    return '[' + ', '.join(leaf + ' (BYTES ' + json.dumps(base64.b64encode(kind.encode()).decode()) + ') metadata_return_union' for kind in members) + ']'


def raw(members, leaf='NIdentifier'):
    return 'NUnionType (SEQUENCE (' + nodes(members, leaf) + ')) metadata_return_union'


def return_proof(case):
    members = case['return_members']
    nodes = ['NIdentifier (BYTES text_return' + str(index) + ') metadata_return' + str(index) for index in range(len(members))]
    lines = ['phpType18 = NUnionType (SEQUENCE ([' + ', '.join(nodes) + '])) metadata_return_union']
    lines += ['$ptlc($base64(text_return' + str(index) + ')) = $ptascii(' + json.dumps(kind) + ')' for index, kind in enumerate(members)]
    iterable = members.index('iterable')
    other = next(index for index, kind in enumerate(members) if kind != 'iterable')
    for alias, index in (('return', iterable), ('return_literal', other)):
        lines += ['text_' + alias + ' = text_return' + str(index), 'metadata_' + alias + ' = metadata_return' + str(index)]
    return lines


def reached(case, front):
    lines = []
    for line in prior.reached(case, front):
        if line.startswith('phpType18 = NUnionType '):
            lines += return_proof(case)
            continue
        if line.startswith('$ptlc($base64(text_return))') or line.startswith('$ptlc($base64(text_return_literal))'):
            continue
        if case.get('priority_control'):
            line = line.replace('KNOWN (PINT 17)', 'KNOWN PNULL')
            if line.startswith('$typed_conversion_at(S_return, '):
                line = line.replace('PINT 17', 'PNULL')
        lines.append(line)
    return lines


def completed(case):
    return prior.completed(case)


def controls(case):
    lines = prior.controls(case)
    if case.get('priority_control'):
        return lines
    header = '$reference_notice_producer_header(phpType6_producer, phpType16, '
    signature = 'pfunction_producer.SIGNATURE'
    for members in (['iterable', 'object'], ['object', 'iterable'], ['iterable', 'callable'], ['callable', 'iterable'],
            ['iterable', 'int', 'null'], ['null', 'int', 'iterable'], ['iterable', 'null', 'int'],
            ['iterable', 'bool', 'int'], ['iterable', 'float', 'int'], ['iterable', 'string', 'int'],
            ['iterable', 'int', 'float', 'bool', 'string', 'null', 'object', 'callable'],
            ['callable', 'object', 'null', 'string', 'false', 'float', 'int', 'iterable'],
            ['true', 'iterable', 'float', 'object', 'callable', 'null', 'int', 'string']):
        lines += [header + raw(members) + ', ' + signature + '[.RETURNS = ' + branches(members) + '])',
            FOLD + '(' + nodes(members) + ', ' + branches(members) + ', eps)']
    for members in (['object', 'callable'], ['iterable', 'array', 'int'], ['int', 'iterable', 'iterable'],
            ['iterable', 'bool', 'true'], ['iterable', 'false', 'true'], ['false', 'iterable', 'bool'],
            ['iterable', 'null', 'mixed'], ['iterable', 'never', 'object'], ['void', 'iterable', 'int']):
        lines.append('~' + FOLD + '(' + nodes(members) + ', ' + branches(members) + ', eps)')
        if 'iterable' in members:
            lines.append('~' + header + raw(members) + ', ' + signature + '[.RETURNS = ' + branches(members) + '])')
    for returns in (list(reversed(case['return_members'])), case['return_members'][:-1], case['return_members'] + ['null']):
        lines.append('~' + header + 'phpType18, ' + signature + '[.RETURNS = ' + branches(returns) + '])')
    for leaf in ('NName', 'NNameFullyQualified'):
        lines.append('~' + header + raw(case['return_members'], leaf) + ', ' + signature + ')')
    lines += ['~' + header + 'phpType18, ' + signature + '[.RETURNS = [(PTBRANCH ([PTBUILTIN "iterable", PTBUILTIN "object"]))]])',
        '~' + header + 'phpType18, ' + signature + '[.PARAMETERS = eps])']
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
    paths = [Path(__file__), Path(prior.__file__), Path(single.__file__), Path(single.prior.__file__), Path(multi.__file__), Path(multi.prior.__file__), Path(multi.prior.prior.__file__), Path(multi.prior.prior.prior.__file__), CATALOGUE, provenance]
    paths += [Path(history.__file__) for history in (old_bool_review, old_string, old_string_review)]
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
    print('cv-builtin-union-iterable-return-front' if args.front else 'cv-builtin-union-iterable-return-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
