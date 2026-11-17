#!/usr/bin/env python3
"""Check Literal-Boolean/iterable returns, exact tags and weak noncoercion and private-cell cleanup."""
import argparse
import base64
import hashlib
import json
import os
import re
from pathlib import Path
import subprocess

import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types
import singleton_cv_union_int_iterable_return_producer_reference_notice_review_state as single
import multi_cv_union_int_iterable_return_producer_reference_notice_review_state as multi
import singleton_cv_nullable_iterable_return_producer_reference_notice_state as old_nullable_author
import singleton_cv_nullable_iterable_return_producer_reference_notice_review_state as old_nullable_peer
import multi_cv_union_null_iterable_return_producer_reference_notice_review_state as old_union_null_peer

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_union_literal_bool_iterable_return_producer_reference_notice_review_cases.json')
PREFIX, branches, raw = single.PREFIX, single.branches, single.raw


def basis(case):
    return single if case['cv_arity'] == 1 else multi


def template(case):
    return dict(case, value_kind='int') if case['value_kind'] == 'bool' else case


def result(case):
    return 'PBOOL ' + str(case['bool_result']).lower()


def reached(case, front):
    lines = basis(case).reached(template(case), front)
    if case['value_kind'] != 'bool':
        return lines
    lines = [line.replace('(PINT 17)', '(' + result(case) + ')').replace('pvalue_string', 'pvalue_input') for line in lines]
    lines = ['pvalue_input = (' + case['input_value'] + ')' if line == '$string_bytes(pvalue_input) = ($ptascii("17"))' else line for line in lines]
    for strict in ('false', 'true'):
        lines.append('$typed_conversion_at(S_resolved, ' + branches(case['return_members']) + ', pvalue_input, ' + strict + ') = TYPEVALUE pvalue_input')
    return lines


def completed(case):
    lines = basis(case).completed(template(case))
    if case['value_kind'] != 'bool':
        return lines
    return [line.replace('(PINT 17)', '(' + result(case) + ')').replace('pvalue_string', 'pvalue_input') for line in lines]


def controls(case):
    lines = basis(case).controls(template(case))
    header = '$reference_notice_producer_header(phpType6_producer, phpType16, '
    signature = 'pfunction_producer.SIGNATURE'
    for members in (['iterable', 'false'], ['false', 'iterable'], ['iterable', 'true'], ['true', 'iterable']):
        lines.append(header + raw(members) + ', ' + signature + '[.RETURNS = ' + branches(members) + '])')
    for members in (['false', 'false'], ['true', 'true'], ['false', 'true'], ['true', 'false'], ['iterable', 'false', 'true']):
        lines.append('~' + header + raw(members) + ', ' + signature + '[.RETURNS = ' + branches(members) + '])')
    for value in ('PINT 0', 'PINT 17', 'PSTRING_CARRIER INTERNED_STRING ($ptascii("0"))'):
        for strict in ('false', 'true'):
            lines.append('$typed_conversion_at(S_resolved, ' + branches(case['return_members']) + ', ' + value + ', ' + strict + ') = TYPEREJECT')
    if case['value_kind'] == 'bool':
        lines.append('$typed_conversion_at(S_resolved, ' + branches(case['return_members']) + ', PBOOL ' + str(not case['bool_result']).lower() + ', false) = TYPEREJECT')
    if case['value_kind'] == 'array':
        for history in (old_nullable_author, old_nullable_peer, old_union_null_peer):
            previous = history.controls(case)
            for members in (['iterable', 'false'], ['false', 'iterable']):
                promoted = [line for line in previous if line.startswith(header + 'NUnionType')
                    and '(BYTES "ZmFsc2U=")' in line
                    and line.endswith(signature + '[.RETURNS = ' + history.branches(members) + '])')]
                expected = 2 if history is old_union_null_peer else 1
                assert len(promoted) == expected and len(set(promoted)) == 1
                line = re.sub(r'\btext_return\b', 'text_first', promoted[-1])
                lines.append(re.sub(r'\bmetadata_return\b', 'metadata_union', line))
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
    paths = [Path(__file__), Path(single.__file__), Path(multi.__file__), Path(single.base.__file__), CATALOGUE, provenance]
    paths += [Path(history.__file__) for history in (old_nullable_author, old_nullable_peer, old_union_null_peer)]
    paths += [Path(old_nullable_author.prior.__file__)]
    paths += [Path(old_union_null_peer.prior.__file__), Path(old_union_null_peer.prior.prior.__file__), Path(old_union_null_peer.prior.prior.prior.__file__), Path(old_union_null_peer.prior.prior.prior.prior.__file__), Path(old_union_null_peer.prior.prior.prior.prior.prior.__file__)]
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
            specs.append('dec $sr_case' + str(index) + '() : bool\ndef $sr_case' + str(index) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in current + extra))
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
    fixture.write_text(prefix + '\n'.join(specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $sr_case' + str(index) + '()\n' for index in range(len(cases))))
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
    print('cv-union-literal-bool-iterable-return-front' if args.front else 'cv-union-literal-bool-iterable-return-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
