#!/usr/bin/env python3
"""Ground bare global stdClass RETURN authority and existing private Notice cells."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import cv_fqn_stdclass_producer_reference_notice_state as prior
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('global_plain_stdclass_return_producer_reference_notice_cases.json')
PREFIX = prior.PREFIX.replace('SingletonFqnStdClass77\\\\make', 'make').replace('MultiFqnStdClass77\\\\make', 'make').replace('SingletonFqnStdClass77\\\\take', 'take').replace('MultiFqnStdClass77\\\\take', 'take')


def front_lines(case, front):
    role = case['role_index']
    lines = []
    compatibility = dict(case, class_formals=[name or 'sTdClAsS' for name in case['class_formals']])
    for line in prior.front_lines(role, compatibility):
        line = line.replace('SingletonFqnStdClass77\\\\make', 'make').replace('MultiFqnStdClass77\\\\make', 'make')
        if line.startswith('~$reference_notice_producer_arguments('):
            line = line.removeprefix('~')
        if line == ('pfunction_producer.CODE.STRICT' if role == 0 else '~pfunction_producer.CODE.STRICT'):
            line = ('' if case['callee_strict'] else '~') + 'pfunction_producer.CODE.STRICT'
        if line.startswith('~psparam.BYREF /\\ psparam.TYPE = '):
            normalized = prior.class_type(case['class_formals'][0]) if case['class_formals'][0] else ('[(PTBRANCH ([PTBUILTIN "int"]))]' if case['first_builtin'] else 'eps')
            line = r'~psparam.BYREF /\ psparam.TYPE = ' + normalized
        line = line.replace('= ((8, b_last))', '= ((' + str(case['notice_line']) + ', b_last))')
        if line.startswith('$reference_notice_producer_line('):
            line = line.removesuffix('= 8') + '= ' + str(case['notice_line'])
        lines.append(line)
    lines += ['pfunction_producer.ENV.NAMESPACE = eps', 'pfunction_producer.ENV.CLASSES = eps',
        'phpType18 = NName (BYTES text_return) metadata_return',
        '$base64(text_return) = $ptascii(' + json.dumps(case['class_return']) + ')']
    if not front:
        lines = [line.removeprefix('~') if line == '~$positional_reference_notice_pending(S_pre)' else line for line in lines]
        lines += ['$reference_notice_producer_scoped_header(pfunction_producer.ENV, phpType6_producer, phpType16, phpType18, pfunction_producer.SIGNATURE)']
    return lines


def controls(case):
    signature = 'pfunction_producer.SIGNATURE'
    environment = 'pfunction_producer.ENV'
    header = '$reference_notice_producer_scoped_header(' + environment + ', phpType6_producer, phpType16, '
    lines = ['~$error_call_valid(S_notice, perrorcall[.LINE = ' + str(case['notice_line'] + 1) + '])', '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])',
        '~$typed_return_task_valid(S_return, $(z_return + 1))']
    for spelling in ('stdClass', 'sTdClAsS', 'STDCLASS'):
        normalized, raw = prior.class_type(spelling), prior.raw_class(spelling, 'NName')
        proof = header + raw + ', ' + signature + '[.RETURNS = ' + normalized + '])'
        lines += [proof, '~' + proof.replace(environment + ',', environment + '[.NAMESPACE = $ptascii("Other")],', 1),
            '~' + proof.replace(environment + ',', environment + '[.CLASSES = [($ptascii("stdclass"), $ptascii("Other"))]],', 1),
            '~' + proof.replace(normalized, prior.class_type(spelling.swapcase())),
            '~$reference_notice_producer_header(phpType6_producer, phpType16, ' + raw + ', ' + signature + '[.RETURNS = ' + normalized + '])']
        for tag in ('NIdentifier', 'NNameRelative'):
            lines.append(('' if tag == 'NNameRelative' and spelling == 'stdClass' else '~') + proof.replace(raw, prior.raw_class(spelling, tag)))
        lines += ['~' + proof.replace(raw, 'NNullableType (' + raw + ') metadata_return'),
            '~' + proof.replace(raw, 'NUnionType (SEQUENCE ([' + raw + ', NIdentifier (BYTES "bnVsbA==") metadata_return])) metadata_return')]
        fully = prior.raw_class(spelling)
        lines += [header + fully + ', ' + signature + '[.RETURNS = ' + normalized + '])']
    for spelling in ('Other', 'Other\\stdClass', '\\stdClass', 'stdClass\x00'):
        lines.append('~' + header + prior.raw_class(spelling, 'NName') + ', ' + signature + '[.RETURNS = ' + prior.class_type(spelling) + '])')
    for update in ('.VARIADIC = true', '.REQUIRED = false', '.DEFAULT = PSDEFAULTUNSUPPORTED "forged plain class default"'):
        tail = '' if case['role_index'] == 0 else ', psparam_last'
        lines.append('~$reference_notice_producer_scoped_header(' + environment + ', phpType6_producer, phpType16, phpType18, ' + signature + '[.PARAMETERS = [psparam[' + update + ']' + tail + ']])')
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
    assert set(rows) == {case['id'] for case in cases} and len(cases) == 4
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    paths = [Path(__file__), Path(prior.__file__), Path(prior.prior.__file__), CATALOGUE, provenance]
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
                current += [line.replace('perrorcall.LINE = 8', 'perrorcall.LINE = ' + str(case['notice_line'])) for line in prior.full_lines(case['role_index'], case)]
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
    report = dict(revision=revision, inputs=before, inputs_stable=stable, head_stable=head_stable, module_count=len(modules), mode='fixture-SL/cache=false/det=true', front=args.front, selection=[case['id'] for case in cases], conditions=len(reached) + len(derived), reached_conditions=len(reached), derived_conditions=len(derived), source_agreements=0, process=process, passed=passed)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('global-plain-stdclass-return-front' if args.front else 'global-plain-stdclass-return-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
