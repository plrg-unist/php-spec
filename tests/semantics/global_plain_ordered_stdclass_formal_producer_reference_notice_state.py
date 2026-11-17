#!/usr/bin/env python3
"""Ground flat ordered bare stdClass FORMAL unions before private Notice admission."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import global_plain_stdclass_formal_producer_reference_notice_state as prior
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('global_plain_ordered_stdclass_formal_producer_reference_notice_cases.json')
PREFIX = prior.PREFIX


def branches(members, name='sTdClAsS'):
    return '[' + ', '.join(prior.prior.class_type(name)[1:-1] if kind == 'class' else
        '(PTBRANCH ([PTBUILTIN ' + json.dumps(kind) + ']))' for kind in members) + ']'


def raw_type(members, name=None, tag='NName', indexed=True):
    encoded = 'text_formal' if name is None else json.dumps(base64.b64encode(name.encode()).decode())
    atoms = [(tag + ' (BYTES ' + encoded + ') metadata_formal') if kind == 'class' else
        'NIdentifier (BYTES ' + json.dumps(base64.b64encode(kind.encode()).decode()) + ') ' + ('metadata_formal_' + str(index) if indexed else 'metadata_formal')
        for index, kind in enumerate(members)]
    return 'NUnionType (SEQUENCE ([' + ', '.join(atoms) + '])) metadata_formal_union'


def front_lines(index, case):
    result = []
    normalized = branches(case['formal_members'])
    raw = raw_type(case['formal_members'])
    for line in prior.front_lines(index, case):
        line = line.replace(prior.prior.class_type('sTdClAsS'), normalized)
        if line.startswith('phpType18_parameter = NName '):
            line = 'phpType18_parameter = ' + raw
        if line.startswith('phpType17_last = '):
            line = line.replace('(NName (BYTES text_formal) metadata_formal)', '(' + raw + ')', 1)
        result.append(line)
    return result


def full_lines(index, case):
    return prior.full_lines(index, case)


def controls(index, case):
    raw = 'phpType17' if index == 0 else 'phpType17_last'
    byref = 'false' if index == 0 else 'true'
    variable = 'phpType10' if index == 0 else 'phpType10_last'
    metadata = 'metadata_parameter' if index == 0 else 'metadata_parameter_last'
    parameter = 'psparam' if index == 0 else 'psparam_last'
    typename = raw_type(case['formal_members'])
    shape = 'NParam (SEQUENCE eps) (INTEGER 0) (' + typename + ') (BOOLEAN ' + byref + ') (BOOLEAN false) ' + variable + ' ABSENT (SEQUENCE eps) ' + metadata
    view = shape.replace('NName ', 'NNameFullyQualified ', 1)
    sequence = 'SEQUENCE ([phpType17])' if index == 0 else 'SEQUENCE ([phpType17, phpType17_last])'
    signature = 'pfunction_producer.SIGNATURE'
    scoped = '$reference_notice_producer_scoped_header(pfunction_producer.ENV, phpType6_producer, ' + sequence + ', phpType18, ' + signature + ')'
    proof = lambda changed: scoped.replace(sequence, sequence.replace(raw, '(' + changed + ')'), 1)
    params = lambda normalized: '[' + ('' if index == 0 else 'psparam, ') + parameter + '[.TYPE = ' + normalized + ']]'
    typed = lambda changed, normalized: proof(changed).replace(signature + ')', signature + '[.PARAMETERS = ' + params(normalized) + '])')
    lines = ['$reference_notice_producer_global_parameter_view(' + raw + ') = (' + view + ')',
        '$reference_notice_producer_global_parameter_view(' + view + ') = (' + view + ')', proof(view),
        '~' + scoped.replace('pfunction_producer.ENV,', 'pfunction_producer.ENV[.NAMESPACE = $ptascii("Other")],', 1),
        '~' + scoped.replace('pfunction_producer.ENV,', 'pfunction_producer.ENV[.CLASSES = [($ptascii("stdclass"), $ptascii("Other"))]],', 1),
        '~$error_call_valid(S_notice, perrorcall[.LINE = ' + str(case['notice_line'] + 1) + '])',
        '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])',
        '~$typed_return_task_valid(S_return, $(z_return + 1))',
        '~' + typed(shape, branches(case['formal_members'][::-1])),
        '~' + typed(shape, branches(case['formal_members'], 'StDcLaSs'))]
    null_shape = shape.replace(typename, raw_type(['class', 'null'], indexed=False))
    lines += ['$reference_notice_producer_global_parameter_view(' + null_shape + ') = (' + null_shape.replace('NName ', 'NNameFullyQualified ', 1) + ')',
        typed(null_shape, branches(['class', 'null'])),
        '~' + typed(null_shape, prior.prior.class_type('sTdClAsS'))]
    for companion in ('array', 'iterable'):
        for boolean in ('bool', 'false', 'true'):
            kinds = [companion, 'int', 'float', boolean, 'string', 'null', 'callable']
            for position in (0, 3, 7):
                members = kinds[:position] + ['class'] + kinds[position:]
                changed = shape.replace(typename, raw_type(members, indexed=False))
                lines.append(typed(changed, branches(members)))
    builtin_shape = shape.replace(typename, raw_type(['int', 'string'], indexed=False))
    lines += ['$reference_notice_producer_global_parameter_view(' + builtin_shape + ') = (' + builtin_shape + ')',
        typed(builtin_shape, branches(['int', 'string']))]
    invalid = (['class', 'class'], ['class', 'array', 'iterable'],
        ['class', 'object'], ['class', 'mixed'], ['class', 'void'], ['class', 'never'],
        ['class', 'bool', 'false'], ['class', 'bool', 'true'], ['class', 'true', 'false'], ['class', 'int', 'int'])
    for members in invalid:
        lines.append('~' + typed(shape.replace(typename, raw_type(members, indexed=False)), branches(members)))
    for tag in ('NNameRelative', 'NIdentifier'):
        changed = shape.replace(typename, raw_type(case['formal_members'], tag=tag, indexed=False))
        lines += ['$reference_notice_producer_global_parameter_view(' + changed + ') = (' + changed + ')', '~' + proof(changed)]
    for name in ('Other', 'Namespace\\stdClass', '\\stdClass', 'stdClass\x00'):
        changed = shape.replace(typename, raw_type(case['formal_members'], name=name, indexed=False))
        lines += ['$reference_notice_producer_global_parameter_view(' + changed + ') = (' + changed + ')', '~' + typed(changed, branches(case['formal_members'], name))]
    for before, after in (('metadata_formal_union', 'eps'), ('metadata_formal)', 'eps)'), (metadata, 'eps')):
        lines.append('$reference_notice_producer_global_parameter_view(' + shape.replace(before, after) + ') = (' + view.replace(before, after) + ')')
    for before, after in (('(INTEGER 0)', '(INTEGER 1)'),
                          ('(BOOLEAN ' + byref + ') (BOOLEAN false)', '(BOOLEAN ' + byref + ') (BOOLEAN true)'),
                          (' ABSENT (SEQUENCE eps) ', ' (NExprConstFetch (NName (BYTES "bnVsbA==") eps) eps) (SEQUENCE eps) '),
                          ('NParam (SEQUENCE eps)', 'NParam (SEQUENCE ([NAttributeGroup (SEQUENCE eps) metadata_formal]))')):
        changed = shape.replace(before, after, 1)
        lines += ['$reference_notice_producer_global_parameter_view(' + changed + ') = (' + view.replace(before, after, 1) + ')', '~' + proof(changed)]
    for update in ('.BYREF = ' + ('true' if index == 0 else 'false'), '.VARIADIC = true', '.REQUIRED = false', '.DEFAULT = PSDEFAULTUNSUPPORTED "forged bare class union formal default"'):
        parameters = '[' + ('' if index == 0 else 'psparam, ') + parameter + '[' + update + ']]'
        lines.append('~' + scoped.replace(signature + ')', signature + '[.PARAMETERS = ' + parameters + '])'))
    for strict in ('true', 'false'):
        lines.append('$typed_conversion_at(S_receive, ' + branches(case['formal_members']) + ', POBJECT n_object_receive, ' + strict + ') = TYPEVALUE (POBJECT n_object_receive)')
    lines.append('$typed_conversion_at(S_receive, ' + branches(case['formal_members']) + ', PINT 19, true) = TYPEREJECT')
    if index == 0:
        lines.append('$typed_conversion_at(S_receive, ' + branches(case['formal_members']) + ', PINT 19, false) = TYPESTRING (PINT 19)')
    else:
        lines += ['$typed_conversion_at(S_receive, ' + branches(case['formal_members']) + ', PNULL, true) = TYPEVALUE PNULL',
            '$typed_conversion_at(S_receive, ' + branches(case['formal_members']) + ', PINT 19, false) = TYPEREJECT']
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
    paths = modules + [runner, Path(__file__), Path(prior.__file__), Path(prior.prior.__file__), Path(prior.prior.prior.__file__), CATALOGUE, fixture, native_path,
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
    print('global-plain-ordered-stdclass-formal-front' if args.front else 'global-plain-ordered-stdclass-formal-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
