#!/usr/bin/env python3
"""Ground declaration-resolved nullable stdClass FORMALs before private Notices."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import scoped_stdclass_formal_producer_reference_notice_state as prior
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('scoped_nullable_stdclass_formal_producer_reference_notice_cases.json')
PREFIX = prior.PREFIX.replace('ScopedFormal124', 'ScopedNullableFormal125')


def nullable_type(name):
    return prior.prior.prior.class_type(name)[:-1] + ', (PTBRANCH ([PTBUILTIN "null"]))]'


def front_lines(index, case):
    lines = []
    for line in prior.front_lines(index, case):
        for name in ('stdClass', case['class_return']):
            line = line.replace(prior.prior.prior.class_type(name), nullable_type(name))
        line = line.replace('ScopedFormal124', 'ScopedNullableFormal125')
        if line.startswith('phpType18 = NNameFullyQualified '):
            line = 'phpType18 = NNullableType (NNameFullyQualified (BYTES text_return) metadata_return) metadata_nullable_return'
        if line.startswith('phpType18_parameter = NName '):
            line = 'phpType18_parameter = NNullableType (NName (BYTES text_formal) metadata_formal) metadata_nullable_formal'
        if line.startswith('phpType17_last = '):
            line = line.replace('(NName (BYTES text_formal) metadata_formal)', '(NNullableType (NName (BYTES text_formal) metadata_formal) metadata_nullable_formal)', 1)
        lines.append(line)
    return lines


def full_lines(index, case):
    return prior.full_lines(index, case)


def controls(index, case):
    raw = 'phpType17' if index == 0 else 'phpType17_last'
    byref = 'false' if index == 0 else 'true'
    variable = 'phpType10' if index == 0 else 'phpType10_last'
    metadata = 'metadata_parameter' if index == 0 else 'metadata_parameter_last'
    parameter = 'psparam' if index == 0 else 'psparam_last'
    shape = 'NParam (SEQUENCE eps) (INTEGER 0) (NNullableType (NName (BYTES text_formal) metadata_formal) metadata_nullable_formal) (BOOLEAN ' + byref + ') (BOOLEAN false) ' + variable + ' ABSENT (SEQUENCE eps) ' + metadata
    view = shape.replace('NName (BYTES text_formal)', 'NNameFullyQualified (BYTES "c3RkQ2xhc3M=")', 1)
    env = 'pfunction_producer.ENV'
    helper = '$reference_notice_producer_scoped_parameter_view('
    sequence = 'SEQUENCE ([phpType17])' if index == 0 else 'SEQUENCE ([phpType17, phpType17_last])'
    signature = 'pfunction_producer.SIGNATURE'
    scoped = '$reference_notice_producer_scoped_header(' + env + ', phpType6_producer, ' + sequence + ', phpType18, ' + signature + ')'
    proof = lambda value: scoped.replace(sequence, sequence.replace(raw, '(' + value + ')'), 1)
    converted = lambda value, context=env: helper + context + ', ' + value + ')'
    lines = [converted(raw) + ' = (' + view + ')', converted(view) + ' = (' + view + ')',
        '$reference_notice_producer_global_parameter_view(' + raw + ') = ' + raw,
        proof(view),
        scoped.replace(env + ',', env + '[.NAMESPACE = $ptascii("Elsewhere")],', 1),
        '~' + scoped.replace(env + ',', env + '[.CLASSES = eps],', 1),
        '~' + scoped.replace(env + ',', env + '[.CLASSES = [($ptascii("box"), $ptascii("Other"))]],', 1),
        '~' + scoped.replace(signature + ')', signature + '[.PARAMETERS = [' + ('' if index == 0 else 'psparam, ') + parameter + '[.TYPE = ' + nullable_type('StDcLaSs') + ']]])'),
        scoped.replace('phpType6_producer,', 'SEQUENCE eps,', 1),
        '~$error_call_valid(S_notice, perrorcall[.LINE = ' + str(case['notice_line'] + 1) + '])',
        '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])',
        '~$typed_return_task_valid(S_return, $(z_return + 1))']
    for alias in ('Box', 'bOx', 'BOX'):
        changed = shape.replace('BYTES text_formal', 'BYTES ' + json.dumps(base64.b64encode(alias.encode()).decode()))
        lines += [converted(changed) + ' = (' + view + ')', proof(changed)]
    for tag in ('NNameRelative', 'NIdentifier'):
        changed = shape.replace('NName ', tag + ' ', 1)
        lines += [converted(changed) + ' = (' + changed + ')', '~' + proof(changed)]
    for name in ('Other', 'Box\\stdClass', '\\Box', 'Box\x00'):
        changed = shape.replace('BYTES text_formal', 'BYTES ' + json.dumps(base64.b64encode(name.encode()).decode()))
        lines += [converted(changed) + ' = (' + changed + ')', '~' + proof(changed)]
    for name in ('int', 'bool', 'array', 'callable', 'self', 'parent', 'static'):
        changed = shape.replace('BYTES text_formal', 'BYTES ' + json.dumps(base64.b64encode(name.encode()).decode()))
        fake_env = env + '[.CLASSES = [($ptascii(' + json.dumps(name) + '), $ptascii("stdClass"))]]'
        lines += [converted(changed, fake_env) + ' = (' + changed + ')', '~' + proof(changed).replace(env + ',', fake_env + ',', 1)]
    for target in ('stdclass', 'StDcLaSs', 'Other'):
        context = env + '[.CLASSES = [($ptascii("box"), $ptascii(' + json.dumps(target) + '))]]'
        lines += [converted(raw, context) + ' = ' + raw, '~' + scoped.replace(env + ',', context + ',', 1)]
    wrapper = 'NNullableType (NName (BYTES text_formal) metadata_formal) metadata_nullable_formal'
    union = 'NUnionType (SEQUENCE ([NName (BYTES text_formal) metadata_formal, NIdentifier (BYTES "bnVsbA==") metadata_formal])) metadata_nullable_formal'
    changed = shape.replace(wrapper, union, 1)
    lines += [converted(changed) + ' = (' + changed + ')', '~' + proof(changed)]
    for normalized in (prior.prior.prior.class_type('stdClass'),
            '[(PTBRANCH ([PTBUILTIN "null"])), (PTBRANCH ([PTCLASS ($ptascii("stdClass"))]))]',
            nullable_type('stdClass')[:-1] + ', (PTBRANCH ([PTBUILTIN "null"]))]'):
        parameters = '[' + ('' if index == 0 else 'psparam, ') + parameter + '[.TYPE = ' + normalized + ']]'
        lines.append('~' + scoped.replace(signature + ')', signature + '[.PARAMETERS = ' + parameters + '])'))
    for before, after in (('metadata_nullable_formal', 'eps'), ('metadata_formal)', 'eps)'), (metadata, 'eps')):
        lines.append(converted(shape.replace(before, after)) + ' = (' + view.replace(before, after) + ')')
    for before, after in (('(INTEGER 0)', '(INTEGER 1)'),
                          ('(BOOLEAN ' + byref + ') (BOOLEAN false)', '(BOOLEAN ' + byref + ') (BOOLEAN true)'),
                          (' ABSENT (SEQUENCE eps) ', ' (NExprConstFetch (NName (BYTES "bnVsbA==") eps) eps) (SEQUENCE eps) '),
                          ('NParam (SEQUENCE eps)', 'NParam (SEQUENCE ([NAttributeGroup (SEQUENCE eps) metadata_formal]))')):
        changed = shape.replace(before, after, 1)
        lines += [converted(changed) + ' = (' + view.replace(before, after, 1) + ')', '~' + proof(changed)]
    for update in ('.BYREF = ' + ('true' if index == 0 else 'false'), '.VARIADIC = true', '.REQUIRED = false', '.DEFAULT = PSDEFAULTUNSUPPORTED "forged imported formal default"'):
        parameters = '[' + ('' if index == 0 else 'psparam, ') + parameter + '[' + update + ']]'
        lines.append('~' + scoped.replace(signature + ')', signature + '[.PARAMETERS = ' + parameters + '])'))
    for strict in ('true', 'false'):
        lines.append('$typed_conversion_at(S_receive, ' + nullable_type('stdClass') + ', POBJECT n_object_receive, ' + strict + ') = TYPEVALUE (POBJECT n_object_receive)')
        lines.append('$typed_conversion_at(S_receive, ' + nullable_type('stdClass') + ', PNULL, ' + strict + ') = TYPEVALUE PNULL')
        for value in ('PINT 19', 'PBOOL false'):
            lines.append('$typed_conversion_at(S_receive, ' + nullable_type('stdClass') + ', ' + value + ', ' + strict + ') = TYPEREJECT')
    for stage in ('receive', 'return', 'notice'):
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
    native_path = args.native_report.resolve()
    native = json.loads(native_path.read_bytes())
    cases = json.loads(CATALOGUE.read_bytes())
    records = {row['id']: row for row in native['records']}
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    assert native['mode'] == 'native-first' and native['passed'] and native['inputs_stable'] and native['head_stable']
    assert native['profile'] == json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    assert native['runtime_sha256'] == sha(types.PHP) == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    sources = {}
    for i, case in enumerate(cases):
        row = records[case['id']]
        sources[i] = Path(row['command'][-1])
        assert row['passed'] and row['exit'] == 0 and not row['timeout'] and not row['group_after']
        assert sources[i].read_bytes() == case['source'].encode() and sha(sources[i]) == case['source_sha256'] == row['source_sha256']
        assert Path(row['stdout']).read_bytes() == row['actual_stdout'].encode() == case['native_stdout'].encode()
        assert Path(row['stderr']).read_bytes() == row['actual_stderr'].encode() == case['native_stderr'].encode()
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    fixtures = {}
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for i in sources:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(sources[i].read_bytes()).decode()})
            assert parsed['accepted']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'] and checked['fixture']
            fixtures[i] = checked['fixture']
    finally:
        try:
            if frontend:
                frontend.close()
        finally:
            if adapter:
                adapter.close()
    reached, derived, specs = [], [], []
    for i, case in enumerate(cases):
        initial = 'S_initial = $php_run(' + fixtures[i] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(sources[i])).decode()) + ')'
        conditions = [initial] + front_lines(i, case)
        extra = []
        if not args.front:
            conditions = [line for line in conditions if not line.startswith('~($reference_notice_producer_scoped_header(')]
            conditions = [line.removeprefix('~') if line.startswith('~$reference_notice_producer_header(') or (line.startswith('~$reference_notice_producer_arguments(') and '.RETURNS = eps' in line) or line == '~$positional_reference_notice_pending(S_pre)' else line for line in conditions]
            conditions += full_lines(i, case)
            extra = controls(i, case)
        specs.append('dec $scnr_case' + str(i) + '() : bool\ndef $scnr_case' + str(i) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in conditions + extra))
        reached += conditions
        derived += extra
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\n'.join(specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $scnr_case' + str(i) + '()\n' for i in range(len(cases))))
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, Path(__file__), Path(prior.__file__), Path(prior.prior.__file__), Path(prior.prior.prior.__file__), Path(prior.prior.prior.prior.__file__), CATALOGUE, fixture, native_path,
        ROOT / 'spec/semantics/modules.json', ROOT / '_build/default/adapter/main.exe', types.PHP, ROOT / '.tools/php-file.so']
    paths += [ROOT / path for path in ('tests/semantics/error_handler_run.py', 'tests/semantics/profile.json',
        'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py', 'tests/validate.py',
        'tests/corpus.py', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py')]
    for case in cases:
        row = records[case['id']]
        paths += [Path(row['command'][-1]), Path(row['stdout']), Path(row['stderr'])]
    fingerprints = lambda: {str(path): sha(path) for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    recorder.ROOT = ROOT
    print(out, flush=True)
    process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(fixture)], out / 'run', 1200)
    stable = before == fingerprints()
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = (process['exit'] == 0 and not process['timeout'] and not process['group_after'] and stable and head_stable and (out / 'run.stdout').read_bytes() == b'true\n' and not (out / 'run.stderr').read_bytes())
    report = {'revision': revision, 'inputs': before, 'inputs_stable': stable, 'head_stable': head_stable, 'fixture_sha256': sha(fixture), 'conditions': len(reached) + len(derived), 'reached_conditions': len(reached), 'derived_conditions': len(derived), 'module_count': len(modules), 'mode': 'fixture-SL/cache=false/det=true', 'process': process, 'source_agreements': 0, 'passed': passed}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('scoped-nullable-stdclass-formal-front' if args.front else 'scoped-nullable-stdclass-formal-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
