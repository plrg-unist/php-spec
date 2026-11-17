#!/usr/bin/env python3
"""Ground strict INT-to-FLOAT return widening before private Notice cells."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import global_plain_union_int_stdclass_return_producer_reference_notice_state as previous
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('global_plain_union_float_stdclass_return_producer_reference_notice_cases.json')
PREFIX = previous.PREFIX
scalar = previous.scalar
objects = previous.previous.previous.objects
FLOAT37 = '(PFLOAT 4630404104378646528)'


def compatibility(case):
    return dict(case, kind='int' if case['kind'] == 'float' else 'object',
        int_first=case['float_first'], return_kind='int')


def union_type(name, float_first=False):
    nominal = objects.prior.class_type(name)[1:-1]
    floating = '(PTBRANCH ([PTBUILTIN "float"]))'
    return '[' + ', '.join((floating, nominal) if float_first else (nominal, floating)) + ']'


def raw_union(name, float_first=False, tag='NName'):
    return scalar.raw_union('float', not float_first, name).replace('NNameFullyQualified', tag)


def context(case):
    return previous.context(compatibility(case))


def front_lines(case, front):
    result = []
    for line in previous.front_lines(compatibility(case), front):
        if line.startswith('pfunction_producer.SIGNATURE.RETURNS = '):
            line = 'pfunction_producer.SIGNATURE.RETURNS = ' + union_type(case['class_return'], case['float_first']) + (r' /\ ~pfunction_producer.SIGNATURE.BYREF' if case['kind'] == 'float' else '')
        if line.startswith('phpType18 = '):
            line = line.replace('text_int', 'text_float')
        if line.startswith('$ptlc($base64(text_int))'):
            line = '$ptlc($base64(text_float)) = $ptascii("float")'
        if line.startswith('phpType18_return = '):
            line = 'phpType18_return = ' + scalar.raw_union('float', not case['float_first'], field='return').replace('NNameFullyQualified', 'NName')
        if line.startswith('$ptlc($base64(text_return_builtin))'):
            line = '$ptlc($base64(text_return_builtin)) = $ptascii("float")'
        if case['kind'] == 'float' and line.startswith(('S_checked.COMPLETION', 'S_after_return.TODO', 'S_pre.RESULT')):
            line = line.replace('(PINT 37)', FLOAT37)
        result.append(line)
    if case['kind'] == 'float':
        result.append('$typed_conversion_at(S_return, pfunction_producer.SIGNATURE.RETURNS, PINT 37, true) = TYPEVALUE ' + FLOAT37)
    return result


def completed(case):
    result = []
    for line in previous.completed(compatibility(case)):
        if case['kind'] == 'float' and line.startswith(('S_notice.STORE[n_private]', 'S_resume.STORE[n_private]')):
            line = line.replace('(PINT 37)', FLOAT37)
        result.append(line)
    return result


def controls(case):
    lines = previous.controls(compatibility(case))
    actuals, parameters, returns = context(case)
    signature, env = 'pfunction_producer.SIGNATURE', 'pfunction_producer.ENV'
    header = '$reference_notice_producer_scoped_header(' + env + ', ' + actuals + ', ' + parameters + ', '
    for spelling in ('stdClass', 'sTdClAsS', 'STDCLASS'):
        for float_first in (False, True):
            normalized, raw = union_type(spelling, float_first), raw_union(spelling, float_first)
            proof = header + raw + ', ' + signature + '[.RETURNS = ' + normalized + '])'
            lines += [proof, proof.replace('"ZmxvYXQ="', '"RkxPQVQ="'),
                '~' + proof.replace(env + ',', env + '[.NAMESPACE = $ptascii("Other")],', 1),
                '~' + proof.replace(env + ',', env + '[.CLASSES = [($ptascii("stdclass"), $ptascii("stdClass"))]],', 1),
                proof.replace(actuals + ',', 'SEQUENCE eps,', 1),
                '~' + proof.replace(normalized, union_type(spelling.swapcase(), float_first)),
                '~' + proof.replace(normalized, union_type(spelling, not float_first)),
                '~' + proof.replace(raw, raw_union(spelling, not float_first)),
                '~' + proof.replace(raw, raw.replace('"ZmxvYXQ="', '"aW50"')),
                '~$reference_notice_producer_header(' + actuals + ', ' + parameters + ', ' + raw + ', ' + signature + '[.RETURNS = ' + normalized + '])',
                proof.replace(raw, raw_union(spelling, float_first, 'NNameFullyQualified'))]
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
    paths = [Path(__file__), Path(previous.__file__), Path(previous.previous.__file__), Path(previous.previous.previous.__file__), Path(objects.__file__), Path(objects.prior.__file__), Path(objects.prior.prior.__file__), Path(scalar.__file__), Path(scalar.scalar.__file__), Path(scalar.objects.__file__), Path(scalar.objects.prior.__file__), Path(scalar.objects.compatibility.__file__), CATALOGUE, provenance]
    specs, reached, derived = [], [], []
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
            current = ['S_initial = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'] + front_lines(case, args.front)
            extra = [] if args.front else controls(case)
            if not args.front:
                current += completed(case)
            specs.append('dec $plc_case' + str(index) + '() : bool\ndef $plc_case' + str(index) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in current + extra))
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
    fixture.write_text(PREFIX + '\n'.join(specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $plc_case' + str(index) + '()\n' for index in range(len(cases))))
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
    report = dict(revision=revision, inputs=before, inputs_stable=stable, head_stable=head_stable, module_count=len(modules), mode='fixture-SL/cache=false/det=true', front=args.front, selection=[case['id'] for case in cases], conditions=len(reached) + len(derived), reached_conditions=len(reached), derived_conditions=len(derived), source_agreements=0, process=process, passed=passed)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('global-plain-union-float-stdclass-return-front' if args.front else 'global-plain-union-float-stdclass-return-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
