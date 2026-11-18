#!/usr/bin/env python3
"""Ground scoped nullable stdClass RETURN aliases and object/NULL private Notice cells."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import global_plain_nullable_stdclass_return_producer_reference_notice_state as prior
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('scoped_nullable_stdclass_return_producer_reference_notice_cases.json')
NAMESPACE = 'ScopedNullableReturn128'


def qualify(line):
    for name in ('make', 'take'):
        line = line.replace('$ptascii(' + json.dumps(name) + ')', '$ptascii(' + json.dumps(NAMESPACE + '\\' + name) + ')')
    return line


PREFIX = qualify(prior.PREFIX)


def front_lines(case, front):
    lines = []
    for line in prior.front_lines(case, front):
        if line == 'pfunction_producer.ENV.NAMESPACE = eps':
            line = 'pfunction_producer.ENV.NAMESPACE = $ptascii(' + json.dumps(NAMESPACE) + ')'
        elif line == 'pfunction_producer.ENV.CLASSES = eps':
            line = 'pfunction_producer.ENV.CLASSES = [($ptascii("box"), $ptascii("stdClass"))]'
        elif line == '$base64(text_return) = $ptascii("stdClass")':
            line = '$base64(text_return) = $ptascii(' + json.dumps(case['return_name']) + ')'
        lines.append(qualify(line))
    lines += ['phpType16 = SEQUENCE phpType17_all*',
        'phpType17_all* = ($reference_notice_producer_scoped_parameter_view(pfunction_producer.ENV, phpType17_all))*',
        '$ptvalidname($base64(text_return), true)',
        '$ptsingle($pltypecontext(pfunction_producer.ENV, PTGLOBAL, PTRETURN, eps, eps, { UNIT 0, PATH eps, FILE eps, LINE 0 }), PTPLAIN, $base64(text_return)) = PTOK (' + prior.objects.prior.class_type('stdClass') + ') eps']
    if front:
        lines.append('~$reference_notice_producer_scoped_header(pfunction_producer.ENV, phpType6_producer, phpType16, phpType18, pfunction_producer.SIGNATURE)')
    return lines


def full_lines(case):
    return [qualify(line) for line in prior.completed(case)]


def controls(case):
    env, signature = 'pfunction_producer.ENV', 'pfunction_producer.SIGNATURE'
    normalized = prior.nullable('stdClass')
    canonical = prior.objects.prior.class_type('stdClass')
    raw = 'NNullableType (NName (BYTES text_return) metadata_return) metadata_nullable'
    fqn = raw.replace('NName (BYTES text_return)', 'NNameFullyQualified (BYTES "c3RkQ2xhc3M=")')
    def proof(expression=raw, context=env, returns=None):
        sig = signature + ('[.RETURNS = ' + returns + ']' if returns is not None else '')
        return '$reference_notice_producer_scoped_header(' + context + ', phpType6_producer, phpType16, ' + expression + ', ' + sig + ')'
    scoped = proof()
    lines = [scoped, proof(fqn),
        '~$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, ' + signature + ')',
        proof(returns='eps'), scoped.replace('phpType6_producer,', 'SEQUENCE eps,', 1),
        proof(context=env + '[.NAMESPACE = eps]'), proof(context=env + '[.NAMESPACE = $ptascii("Elsewhere")]'),
        '~' + proof(context=env + '[.CLASSES = eps]'),
        '~' + proof(context=env + '[.NAMESPACE = eps][.CLASSES = eps]'),
        '~$error_call_valid(S_notice, perrorcall[.LINE = ' + str(case['notice_line'] + 1) + '])',
        '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])',
        '~$typed_return_task_valid(S_return, $(z_return + 1))']
    for alias in ('Box', 'bOx', 'BOX'):
        lines.append(proof(raw.replace('text_return', json.dumps(base64.b64encode(alias.encode()).decode()))))
    for tag in ('NIdentifier', 'NNameRelative', 'NNameFullyQualified'):
        lines.append('~' + proof(raw.replace('NName ', tag + ' ', 1)))
    for name in ('Other', 'Box\\stdClass', '\\Box', 'Box\x00', 'int', 'mixed', 'self', 'array', 'callable'):
        changed = raw.replace('text_return', json.dumps(base64.b64encode(name.encode()).decode()))
        lines.append('~' + proof(changed))
    for name in ('int', 'bool', 'array', 'callable', 'self', 'parent', 'static', 'void', 'never', 'mixed'):
        changed = raw.replace('text_return', json.dumps(base64.b64encode(name.encode()).decode()))
        fake = env + '[.CLASSES = [($ptascii(' + json.dumps(name) + '), $ptascii("stdClass"))]]'
        lines.append('~' + proof(changed, fake))
    for target in ('Other', 'stdclass', 'StDcLaSs'):
        lines.append('~' + proof(context=env + '[.CLASSES = [($ptascii("box"), $ptascii(' + json.dumps(target) + '))]]'))
    for returns in (canonical, prior.nullable('Other'), prior.nullable('STDCLASS'),
            '[(PTBRANCH ([PTBUILTIN "null"]))]',
            '[(PTBRANCH ([PTBUILTIN "null"])), ' + canonical[1:],
            normalized[:-1] + ', (PTBRANCH ([PTBUILTIN "null"]))]',
            normalized[:-1] + ', (PTBRANCH ([PTBUILTIN "int"]))]'):
        lines.append('~' + proof(returns=returns))
    inner = 'NName (BYTES text_return) metadata_return'
    union = 'NUnionType (SEQUENCE ([' + inner + ', NIdentifier (BYTES "bnVsbA==") metadata_return])) metadata_nullable'
    lines += ['~' + proof(inner), proof(union),
        proof(raw.replace('metadata_nullable', 'eps')), proof(raw.replace('metadata_return', 'eps'))]
    imported = env + '[.CLASSES = [($ptascii("stdclass"), $ptascii("stdClass"))]]'
    global_raw = raw.replace('text_return', '"c3RkQ2xhc3M="')
    lines += [proof(global_raw, imported), proof(global_raw, imported + '[.NAMESPACE = eps]')]
    parameter = 'psparam' if case['role_index'] == 0 else 'psparam_tag'
    tail = '' if case['role_index'] == 0 else ', psparam'
    for update in ('.BYREF = true', '.VARIADIC = true', '.REQUIRED = false', '.DEFAULT = PSDEFAULTUNSUPPORTED "forged scoped nullable return formal default"'):
        lines.append('~' + scoped.replace(signature + ')', signature + '[.PARAMETERS = [' + parameter + '[' + update + ']' + tail + ']])'))
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
    print('scoped-nullable-stdclass-return-front' if args.front else 'scoped-nullable-stdclass-return-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
