#!/usr/bin/env python3
"""Ground both ordered import-independent relative class/null RETURNs in the empty namespace."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import global_relative_nullable_stdclass_return_producer_reference_notice_state as prior
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('global_relative_union_null_stdclass_return_producer_reference_notice_cases.json')
PREFIX = prior.PREFIX


CLASS = prior.prior.objects.prior.class_type('stdClass')
NULL = '(PTBRANCH ([PTBUILTIN "null"]))'


def normalized(case):
    return CLASS[:-1] + ', ' + NULL + ']' if case['class_first'] else '[' + NULL + ', ' + CLASS[1:]


def raw_return(case, name='text_return', tag='NNameRelative'):
    nominal = tag + ' (BYTES ' + name + ') metadata_return'
    null = 'NIdentifier (BYTES "bnVsbA==") metadata_null'
    members = [nominal, null] if case['class_first'] else [null, nominal]
    return 'NUnionType (SEQUENCE ([' + ', '.join(members) + '])) metadata_union'


def front_lines(case, front):
    lines = []
    for line in prior.front_lines(case, front):
        if line.startswith('pfunction_producer.SIGNATURE.RETURNS = '):
            line = 'pfunction_producer.SIGNATURE.RETURNS = ' + normalized(case)
        elif line.startswith('phpType18 = NNullableType '):
            line = 'phpType18 = ' + raw_return(case)
        lines.append(line)
    return lines


def full_lines(case):
    return prior.full_lines(case)


def controls(case):
    env, signature = 'pfunction_producer.ENV', 'pfunction_producer.SIGNATURE'
    raw = raw_return(case)
    def proof(expression=raw, context=env, returns=None):
        sig = signature + ('[.RETURNS = ' + returns + ']' if returns is not None else '')
        return '$reference_notice_producer_scoped_header(' + context + ', phpType6_producer, phpType16, ' + expression + ', ' + sig + ')'
    scoped = proof()
    lines = [scoped, proof(raw_return(case, tag='NNameFullyQualified')),
        proof(raw.replace('"bnVsbA=="', '"TnVMbA=="')),
        proof(raw.replace('metadata_null', 'metadata_return').replace('metadata_union', 'metadata_return')),
        '~$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, ' + signature + ')',
        proof(returns='eps'), scoped.replace('phpType6_producer,', 'SEQUENCE eps,', 1),
        proof(context=env + '[.CLASSES = eps]'),
        '~' + proof(context=env + '[.NAMESPACE = $ptascii("Elsewhere")]'),
        '~$error_call_valid(S_notice, perrorcall[.LINE = ' + str(case['notice_line'] + 1) + '])',
        '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])',
        '~$typed_return_task_valid(S_return, $(z_return + 1))']
    for target in ('Other', 'stdclass', 'StDcLaSs', 'stdClass'):
        context = env + '[.CLASSES = [($ptascii("stdclass"), $ptascii(' + json.dumps(target) + '))]]'
        lines += [proof(context=context),
            ('' if target == 'stdClass' else '~') + proof(raw_return(case, tag='NName'), context)]
    for name in ('Other', 'Box\\stdClass', '\\stdClass', 'stdClass\x00', 'STDCLASS', 'sTdClAsS', 'int', 'mixed', 'self', 'array', 'callable'):
        changed = raw_return(case, json.dumps(base64.b64encode(name.encode()).decode()))
        lines.append('~' + proof(changed))
    opposite = normalized(dict(case, class_first=not case['class_first']))
    for wrong in (CLASS, opposite, '[' + NULL + ']', normalized(case)[:-1] + ', ' + NULL + ']',
            normalized(case)[:-1] + ', (PTBRANCH ([PTBUILTIN "int"]))]'):
        lines.append('~' + proof(returns=wrong))
    inner = 'NNameRelative (BYTES text_return) metadata_return'
    nullable = 'NNullableType (' + inner + ') metadata_union'
    lines += [('' if case['class_first'] else '~') + proof(nullable),
        '~' + proof(inner), '~' + proof(raw_return(case, tag='NIdentifier')),
        proof(raw.replace('metadata_return', 'eps')), proof(raw.replace('metadata_null', 'eps')),
        proof(raw.replace('metadata_union', 'eps')),
        '~' + proof(raw.replace('"bnVsbA=="', '"aW50"')),
        '~' + proof(raw.replace('])) metadata_union', ', NIdentifier (BYTES "aW50") metadata_null])) metadata_union'))]
    for update in ('.BYREF = ' + str(case['kind'] != 'null').lower(), '.VARIADIC = true', '.REQUIRED = false', '.DEFAULT = PSDEFAULTUNSUPPORTED "forged ordered relative return formal default"'):
        parameters = '[psparam[' + update + ']]' if case['kind'] == 'object' else '[psparam_tag, psparam[' + update + ']]'
        lines.append('~' + scoped.replace(signature + ')', signature + '[.PARAMETERS = ' + parameters + '])'))
    for strict in ('true', 'false'):
        lines += ['$typed_conversion_at(S_return, ' + signature + '.RETURNS, PNULL, ' + strict + ') = TYPEVALUE PNULL',
            '$typed_conversion_at(S_return, ' + signature + '.RETURNS, PINT 19, ' + strict + ') = TYPEREJECT']
        if case['kind'] == 'object':
            lines.append('$typed_conversion_at(S_return, ' + signature + '.RETURNS, POBJECT n_object, ' + strict + ') = TYPEVALUE (POBJECT n_object)')
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
                current += full_lines(case)
            specs.append('dec $src_case' + str(index) + '() : bool\ndef $src_case' + str(index) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in current + extra))
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
    fixture.write_text(PREFIX + '\n'.join(specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $src_case' + str(index) + '()\n' for index in range(len(cases))))
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
    print('global-relative-union-null-stdclass-return-front' if args.front else 'global-relative-union-null-stdclass-return-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
