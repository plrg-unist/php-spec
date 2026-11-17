#!/usr/bin/env python3
"""Check ordered float/iterable returns, weak/strict widening and private-cell cleanup."""
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
import singleton_cv_union_int_iterable_return_producer_reference_notice_review_state as single
import multi_cv_union_int_iterable_return_producer_reference_notice_review_state as multi

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_union_float_iterable_return_producer_reference_notice_review_cases.json')
PREFIX, branches, raw = single.PREFIX, single.branches, single.raw


def basis(case):
    return single if case['cv_arity'] == 1 else multi


def template(case):
    return dict(case, value_kind='int') if case['value_kind'] == 'float' else case


def reached(case, front):
    lines = basis(case).reached(template(case), front)
    if case['value_kind'] != 'float':
        return lines
    value = '(PFLOAT ' + str(case['return_float_bits']) + ')'
    source = '(PINT 17)' if case['float_input_kind'] == 'int' else 'pvalue_string'
    result = []
    for line in lines:
        if line == 'S_resolved.RESULT = KNOWN pvalue_string':
            line = 'S_resolved.RESULT = KNOWN ' + source
        elif line == '$string_bytes(pvalue_string) = ($ptascii("17"))':
            if case['float_input_kind'] == 'int':
                continue
            line = '$string_bytes(pvalue_string) = ($ptascii("17.5"))'
        elif line.startswith('S_return.STORE[n_formal] = DEFINED pvalue_string') or line.startswith('S_pre.STORE[n_caller] = DEFINED pvalue_string'):
            line = line.replace('pvalue_string', source)
        else:
            line = line.replace('(PINT 17)', value)
        result.append(line)
    result.append('$typed_conversion_at(S_resolved, ' + branches(case['return_members']) + ', ' + source + ', ' + str(bool(case.get('callee_strict'))).lower() + ') = TYPEVALUE ' + value)
    return result


def completed(case):
    lines = basis(case).completed(template(case))
    if case['value_kind'] != 'float':
        return lines
    value = '(PFLOAT ' + str(case['return_float_bits']) + ')'
    lines = [line.replace('(PINT 17)', value) for line in lines]
    if case['float_input_kind'] == 'int':
        lines = [line.replace('S_full.STORE[n_copy] = DEFINED pvalue_string', 'S_full.STORE[n_copy] = DEFINED (PINT 17)') for line in lines]
    return lines


def controls(case):
    lines = basis(case).controls(template(case))
    header = '$reference_notice_producer_header(phpType6_producer, phpType16, '
    signature = 'pfunction_producer.SIGNATURE'
    for members in (['iterable', 'float'], ['float', 'iterable']):
        call = header + raw(members) + ', ' + signature + '[.RETURNS = ' + branches(members) + '])'
        assert lines.count('~' + call) + lines.count(call) == 1
        if '~' + call in lines:
            lines[lines.index('~' + call)] = call
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
    print('cv-union-float-iterable-return-front' if args.front else 'cv-union-float-iterable-return-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
