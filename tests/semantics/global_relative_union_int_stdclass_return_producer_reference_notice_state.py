#!/usr/bin/env python3
"""Ground import-independent relative class/int RETURN unions through object and INT Notice cells."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import global_plain_union_null_stdclass_return_producer_reference_notice_state as previous
import cv_builtin_fqn_stdclass_producer_reference_notice_state as scalar
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('global_relative_union_int_stdclass_return_producer_reference_notice_cases.json')
PREFIX = previous.PREFIX + scalar.scalar.PREFIX.replace('MultiCvScalarFormalString57\\\\make', 'make').replace('MultiCvScalarFormalString57\\\\take', 'take').replace('H:8:', 'H:9:')


def union_type(name, int_first=False):
    nominal = previous.previous.objects.prior.class_type(name)[1:-1]
    integer = '(PTBRANCH ([PTBUILTIN "int"]))'
    return '[' + ', '.join((integer, nominal) if int_first else (nominal, integer)) + ']'


def raw_union(name, int_first=False, tag='NName'):
    return scalar.raw_union('int', not int_first, name).replace('NNameFullyQualified', tag)


def context(case):
    if case['kind'] == 'object':
        return 'phpType6_producer', 'phpType16', 'phpType18'
    return 'SEQUENCE ([phpType7_first, phpType7_last])', 'SEQUENCE ([phpType17_first, phpType17_last])', 'phpType18_return'


def front_lines(case, front):
    if case['kind'] == 'object':
        original = previous.front_lines(dict(case, null_first=case['int_first']), front)
        result = []
        for line in original:
            if line.startswith('pfunction_producer.SIGNATURE.RETURNS = '):
                line = 'pfunction_producer.SIGNATURE.RETURNS = ' + union_type('stdClass', case['int_first'])
            if line.startswith('phpType18 = '):
                line = line.replace('NName ', 'NNameRelative ', 1).replace('text_null', 'text_int')
            if line.startswith('$ptlc($base64(text_null))'):
                line = '$ptlc($base64(text_int)) = $ptascii("int")'
            if line == 'pfunction_producer.ENV.CLASSES = eps':
                line = 'pfunction_producer.ENV.CLASSES = [($ptascii("stdclass"), $ptascii(' + json.dumps(case['import_target']) + '))]'
            if not front and line == '~$positional_reference_notice_pending(S_pre)':
                line = line.removeprefix('~')
            result.append(line)
        return result
    result = []
    for line in scalar.scalar_front(case):
        if line.startswith('pfunction_producer.SIGNATURE.RETURNS = '):
            line = 'pfunction_producer.SIGNATURE.RETURNS = ' + union_type('stdClass', case['int_first']) + r' /\ ~pfunction_producer.SIGNATURE.BYREF'
        if line.startswith('phpType18_return = '):
            line = 'phpType18_return = ' + scalar.raw_union('int', not case['int_first'], field='return').replace('NNameFullyQualified', 'NNameRelative')
        if line.startswith('~$reference_notice_producer_arguments('):
            line = line.removeprefix('~')
        line = line.replace('= ((8, b_last))', '= ((' + str(case['notice_line']) + ', b_last))')
        if line.startswith(('$reference_notice_producer_line(', '$runtime_line(')) and line.endswith('= 8'):
            line = line.removesuffix('= 8') + '= ' + str(case['notice_line'])
        if not front and line == '~$positional_reference_notice_pending(S_pre)':
            line = line.removeprefix('~')
        result.append(line)
    actuals, parameters, returns = context(case)
    return result + ['pfunction_producer.ENV.NAMESPACE = eps',
        'pfunction_producer.ENV.CLASSES = [($ptascii("stdclass"), $ptascii(' + json.dumps(case['import_target']) + '))]',
        ('~' if front else '') + '$reference_notice_producer_scoped_header(pfunction_producer.ENV, ' + actuals + ', ' + parameters + ', ' + returns + ', pfunction_producer.SIGNATURE)']


def completed(case):
    if case['kind'] == 'object':
        return previous.completed(case)
    return [line.replace('perrorcall.LINE = 8', 'perrorcall.LINE = ' + str(case['notice_line']))
        for line in scalar.scalar.full_lines(1, case)]


def controls(case):
    actuals, parameters, returns = context(case)
    signature, env = 'pfunction_producer.SIGNATURE', 'pfunction_producer.ENV'
    normalized = union_type('stdClass', case['int_first'])
    raw = raw_union('stdClass', case['int_first'], 'NNameRelative')
    def proof(expression=raw, environment=env, checked=normalized):
        return '$reference_notice_producer_scoped_header(' + environment + ', ' + actuals + ', ' + parameters + ', ' + expression + ', ' + signature + '[.RETURNS = ' + checked + '])'
    lines = [proof(), proof(raw.replace('NNameRelative', 'NNameFullyQualified')),
        proof(raw.replace('"aW50"', '"SW5U"')),
        proof(raw.replace('metadata_function', 'eps').replace('metadata_return', 'eps')),
        '~$reference_notice_producer_header(' + actuals + ', ' + parameters + ', ' + raw + ', ' + signature + '[.RETURNS = ' + normalized + '])',
        '~' + proof(environment=env + '[.NAMESPACE = $ptascii("Other")]'),
        proof(environment=env + '[.CLASSES = eps]'),
        '~$error_call_valid(S_notice, perrorcall[.LINE = ' + str(case['notice_line'] + 1) + '])',
        '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])', '~$typed_return_task_valid(S_return, $(z_return + 1))']
    for target in ('Other', 'stdclass', 'StDcLaSs', 'stdClass'):
        environment = env + '[.CLASSES = [($ptascii("stdclass"), $ptascii(' + json.dumps(target) + '))]]'
        lines += [proof(environment=environment),
            ('' if target == 'stdClass' else '~') + proof(raw.replace('NNameRelative', 'NName'), environment)]
    for spelling in ('Other', 'Other\\stdClass', '\\stdClass', 'stdClass\x00', 'STDCLASS', 'sTdClAsS', 'int', 'mixed', 'self', 'array', 'callable'):
        lines.append('~' + proof(raw_union(spelling, case['int_first'], 'NNameRelative')))
    opposite = union_type('stdClass', not case['int_first'])
    lines += ['~' + proof(checked=opposite),
        '~' + proof(raw_union('stdClass', not case['int_first'], 'NNameRelative')),
        proof(raw_union('stdClass', not case['int_first'], 'NNameRelative'), checked=opposite),
        '~' + proof(raw.replace('NNameRelative', 'NIdentifier')),
        '~' + proof(checked=previous.previous.objects.prior.class_type('stdClass')),
        '~' + proof(checked=normalized[:-1] + ', (PTBRANCH ([PTBUILTIN "null"]))]')]
    for kind in ('float', 'string', 'bool', 'array', 'callable', 'false', 'true', 'iterable'):
        changed_raw = raw.replace('"aW50"', json.dumps(base64.b64encode(kind.encode()).decode()))
        changed_type = normalized.replace('"int"', json.dumps(kind))
        lines.append(proof(changed_raw, checked=changed_type))
    lines.append(proof(raw.replace('"aW50"', '"bnVsbA=="'), checked=normalized.replace('"int"', '"null"')))
    for strict in ('true', 'false'):
        lines += ['$typed_conversion_at(S_return, ' + normalized + ', PINT 37, ' + strict + ') = TYPEVALUE (PINT 37)',
            '$typed_conversion_at(S_return, ' + normalized + ', PNULL, ' + strict + ') = TYPEREJECT']
        if case['kind'] == 'object':
            lines.append('$typed_conversion_at(S_return, ' + normalized + ', POBJECT n_object, ' + strict + ') = TYPEVALUE (POBJECT n_object)')
    for stage in ('return', 'notice'):
        lines += ['S_zero_' + stage + ' = $drive(S_' + stage + ', 0)',
            'S_zero_' + stage + r'.COMPLETION = BUDGET /\ S_zero_' + stage + '[.COMPLETION = NORMAL] = S_' + stage,
            '$drive($drive(S_zero_' + stage + '[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_' + stage + ', 2)']
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
    assert set(rows) == {case['id'] for case in cases} and len(cases) == 2
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    paths = [Path(__file__), CATALOGUE, provenance]
    paths += sorted({Path(module.__file__).absolute() for module in sys.modules.values() if getattr(module, '__file__', None) and Path(module.__file__).absolute().parent == ROOT / 'tests/semantics'})
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
    print('global-relative-union-int-stdclass-return-front' if args.front else 'global-relative-union-int-stdclass-return-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
