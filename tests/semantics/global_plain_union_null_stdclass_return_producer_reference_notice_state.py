#!/usr/bin/env python3
"""Ground exact ordered global stdClass/null RETURN unions at private Notices."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import global_plain_nullable_stdclass_return_producer_reference_notice_state as previous
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('global_plain_union_null_stdclass_return_producer_reference_notice_cases.json')
PREFIX = previous.PREFIX
completed = previous.completed


def union_type(name, null_first=False):
    nominal = previous.objects.prior.class_type(name)[1:-1]
    null = '(PTBRANCH ([PTBUILTIN "null"]))'
    return '[' + ', '.join((null, nominal) if null_first else (nominal, null)) + ']'


def raw_union(name, null_first=False, tag='NName'):
    nominal = previous.objects.prior.raw_class(name, tag).replace('metadata_function', 'metadata_return')
    null = 'NIdentifier (BYTES "bnVsbA==") metadata_null'
    return 'NUnionType (SEQUENCE ([' + ', '.join((null, nominal) if null_first else (nominal, null)) + '])) metadata_union'


def front_lines(case, front):
    lines = previous.front_lines(case, front)
    result = []
    for line in lines:
        if line.startswith('pfunction_producer.SIGNATURE.RETURNS = '):
            line = 'pfunction_producer.SIGNATURE.RETURNS = ' + union_type(case['class_return'], case['null_first'])
        if line.startswith('phpType18 = '):
            nominal = 'NName (BYTES text_return) metadata_return'
            null = 'NIdentifier (BYTES text_null) metadata_null'
            line = 'phpType18 = NUnionType (SEQUENCE ([' + ', '.join((null, nominal) if case['null_first'] else (nominal, null)) + '])) metadata_union'
        result.append(line)
    result.append('$ptlc($base64(text_null)) = $ptascii("null")')
    if front:
        result.append('~$reference_notice_producer_scoped_header(pfunction_producer.ENV, phpType6_producer, phpType16, phpType18, pfunction_producer.SIGNATURE)')
    return result


def controls(case):
    signature, env = 'pfunction_producer.SIGNATURE', 'pfunction_producer.ENV'
    header = '$reference_notice_producer_scoped_header(' + env + ', phpType6_producer, phpType16, '
    lines = ['~$error_call_valid(S_notice, perrorcall[.LINE = ' + str(case['notice_line'] + 1) + '])',
        '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])', '~$typed_return_task_valid(S_return, $(z_return + 1))']
    for spelling in ('stdClass', 'sTdClAsS', 'STDCLASS'):
        for null_first in (False, True):
            normalized, raw = union_type(spelling, null_first), raw_union(spelling, null_first)
            proof = header + raw + ', ' + signature + '[.RETURNS = ' + normalized + '])'
            lines += [proof, proof.replace('"bnVsbA=="', '"TnVMbA=="'),
                '~' + proof.replace(env + ',', env + '[.NAMESPACE = $ptascii("Other")],', 1),
                ('' if spelling == 'stdClass' else '~') + proof.replace(env + ',', env + '[.CLASSES = [($ptascii("stdclass"), $ptascii("stdClass"))]],', 1),
                proof.replace('phpType6_producer', 'SEQUENCE eps'),
                '~' + proof.replace(normalized, union_type(spelling.swapcase(), null_first)),
                '~' + proof.replace(normalized, union_type(spelling, not null_first)),
                '~' + proof.replace(raw, raw_union(spelling, not null_first)),
                '~' + proof.replace(raw, raw.replace('"bnVsbA=="', '"aW50"')),
                '~$reference_notice_producer_header(phpType6_producer, phpType16, ' + raw + ', ' + signature + '[.RETURNS = ' + normalized + '])',
                proof.replace(raw, raw_union(spelling, null_first, 'NNameFullyQualified'))]
            for tag in ('NIdentifier', 'NNameRelative'):
                lines.append('~' + proof.replace(raw, raw_union(spelling, null_first, tag)))
            for wrong in (previous.objects.prior.class_type(spelling), normalized[:-1] + ', (PTBRANCH ([PTBUILTIN "null"]))]'):
                lines.append('~' + proof.replace(normalized, wrong))
    for spelling in ('Other', 'Other\\stdClass', '\\stdClass', 'stdClass\x00'):
        lines.append('~' + header + raw_union(spelling) + ', ' + signature + '[.RETURNS = ' + union_type(spelling) + '])')
    lines += [line.replace('metadata_nullable', 'metadata_union') for line in previous.controls(case)
        if line.startswith('$reference_notice_producer_scoped_header(') and 'NUnionType (SEQUENCE ([NName' in line]
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
    paths = [Path(__file__), Path(previous.__file__), Path(previous.objects.__file__), Path(previous.objects.prior.__file__), Path(previous.objects.prior.prior.__file__), CATALOGUE, provenance]
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
    print('global-plain-union-null-stdclass-return-front' if args.front else 'global-plain-union-null-stdclass-return-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
