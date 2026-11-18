#!/usr/bin/env python3
"""Ground one-sign FLOAT defaults without changing live signatures or ownership."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types
import supplied_optional_float_default_producer_reference_notice_state as literal

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('supplied_optional_unary_float_default_producer_reference_notice_cases.json')


def namespaces(text):
    return (text.replace('SingletonScalarFormal59', 'UnaryFloatDefault148')
        .replace('UntypedArrayReturnProducer35', 'UnaryFloatArray148'))


PREFIX = namespaces(literal.PREFIX)


def default_parts(case):
    assert case['default'] in ('+7.5', '-7.5')
    operator = 'NExprUnaryMinus' if case['default'] == '-7.5' else 'NExprUnaryPlus'
    return '(' + operator + ' (NScalarFloat (FLOAT "401e000000000000") metadata_default_leaf) metadata_default)'


def replacements(case, lines):
    result = []
    for line in lines:
        line = line.replace(literal.DEFAULT, default_parts(case))
        if case['default'] == '-7.5':
            line = line.replace(literal.FLOAT75, 'PFLOAT 13843502304583483392')
        result.append(namespaces(line))
    return result


def front_lines(case, front):
    if case['kind'] == 'invalid':
        return literal.front_lines(case, front)
    lines = replacements(case, literal.front_lines(case, front))
    if case['kind'] == 'singleton' and front:
        lines += ['~$reference_notice_producer_arguments(phpType6_producer, phpType16_producer, pfunction_producer.SIGNATURE)']
    return lines


def full_lines(case):
    return [] if case['kind'] == 'invalid' else replacements(case, literal.full_lines(case))


def controls(case):
    return [] if case['kind'] == 'invalid' else replacements(case, literal.controls(case))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-report', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--front', action='store_true')
    args = parser.parse_args()
    native_path = args.native_report.resolve()
    native, cases = json.loads(native_path.read_bytes()), json.loads(CATALOGUE.read_bytes())
    rows = {row['id']: row for row in native['records']}
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    assert native['mode'] == 'native-first' and native['passed'] and native['inputs_stable'] and native['head_stable']
    assert native['profile'] == types.PROFILE and native['runtime_sha256'] == sha(types.PHP)
    assert set(rows) == {case['id'] for case in cases} and len(cases) == 4
    out = args.output.resolve()
    out.mkdir(parents=True)
    paths = [CATALOGUE, native_path] + sorted({Path(module.__file__).absolute() for module in sys.modules.values()
        if getattr(module, '__file__', None) and Path(module.__file__).absolute().parent == ROOT / 'tests/semantics'})
    frontend = adapter = None
    specs, reached, derived = [], [], []
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for index, case in enumerate(cases):
            row, source = rows[case['id']], Path(rows[case['id']]['command'][-1])
            assert row['passed'] and row['exit'] == case['native_exit'] and not row['timeout'] and not row['group_after']
            assert source.read_bytes() == case['source'].encode() and sha(source) == case['source_sha256'] == row['source_sha256']
            assert Path(row['stdout']).read_bytes() == row['actual_stdout'].encode() == case['native_stdout'].encode()
            assert Path(row['stderr']).read_bytes() == row['actual_stderr'].encode() == case['native_stderr'].replace('{source}', str(source)).encode()
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted']
            checked_value = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked_value['ok'] and checked_value['fixture']
            current = ['S_initial = $php_run(' + checked_value['fixture'] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'] + front_lines(case, args.front)
            extra = [] if args.front else controls(case)
            if not args.front:
                current += full_lines(case)
            specs.append('dec $unary_float_default_case' + str(index) + '() : bool\ndef $unary_float_default_case' + str(index) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in current + extra))
            reached += current
            derived += extra
            paths += [source, Path(row['stdout']), Path(row['stderr'])]
    finally:
        try:
            if frontend:
                frontend.close()
        finally:
            if adapter:
                adapter.close()
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\n'.join(specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $unary_float_default_case' + str(index) + '()\n' for index in range(len(cases))))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths += modules + [runner, fixture] + [ROOT / name for name in ('spec/semantics/modules.json', 'tests/semantics/profile.json', '_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py')]
    fingerprints = lambda: {str(path): sha(path) for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    recorder.ROOT = ROOT
    print(out, flush=True)
    process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(fixture)], out / 'run', 1200)
    stable = before == fingerprints()
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = process['exit'] == 0 and not process['timeout'] and not process['group_after'] and stable and head_stable and (out / 'run.stdout').read_bytes() == b'true\n' and not (out / 'run.stderr').read_bytes()
    report = dict(revision=revision, inputs=before, inputs_stable=stable, head_stable=head_stable, module_count=len(modules), mode='fixture-SL/cache=false/det=true', front=args.front, selection=[case['id'] for case in cases], conditions=len(reached) + len(derived), reached_conditions=len(reached), derived_conditions=len(derived), source_agreements=0, process=process, passed=passed)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('supplied-optional-unary-float-default-front' if args.front else 'supplied-optional-unary-float-default-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
