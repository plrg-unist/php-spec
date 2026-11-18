#!/usr/bin/env python3
"""Ground case-preserving Relative types through reception, return and Notice cells."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import global_relative_stdclass_formal_producer_reference_notice_state as formal
import global_relative_nullable_ordered_stdclass_formal_producer_reference_notice_state as wrapped
import global_relative_stdclass_return_producer_reference_notice_state as returns
import global_relative_nullable_stdclass_return_producer_reference_notice_state as nullable
import global_relative_ordered_stdclass_return_producer_reference_notice_state as ordered
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('global_relative_case_stdclass_producer_reference_notice_cases.json')
PREFIX = formal.PREFIX + ordered.PREFIX


def normalized(case, name):
    members = (case['formal_members'] if case['side'] == 'formal' else case['return_members']) if case['shape'] == 'union' else ['class'] + (['null'] if case['shape'] == 'nullable' else [])
    return ordered.ordered.normalized(members, name)


def front_lines(case, front):
    if case['side'] == 'formal':
        producer = formal if case['shape'] == 'bare' else wrapped
        lines = producer.front_lines(case['role_index'], case)
        result = []
        for line in lines:
            if 'PTCLASS' in line or line.startswith('$base64(text_formal'):
                line = line.replace('$ptascii("stdClass")', '$ptascii(' + json.dumps(case['relative_class']) + ')')
            if not front and line.startswith('~($reference_notice_producer_scoped_header('):
                continue
            if not front and line == '~$positional_reference_notice_pending(S_pre)':
                line = line.removeprefix('~')
            result.append(line)
        return result
    producer = {'bare': returns, 'nullable': nullable, 'union': ordered}[case['shape']]
    lines = producer.front_lines(case, front)
    # Only the declaration-position assertion was canonical in the old helpers.
    return [line.replace('$ptascii("stdClass")', '$ptascii(' + json.dumps(case['relative_class']) + ')')
        if line.startswith('$ptsingle(') or line.startswith('pfunction_producer.SIGNATURE.RETURNS[') else line for line in lines]


def full_lines(case):
    if case['side'] == 'formal':
        return formal.driver.full_lines(case['role_index'], case)
    return {'bare': returns, 'nullable': nullable, 'union': ordered}[case['shape']].full_lines(case)


def raw_type(case, name=None, tag='NNameRelative'):
    encoded = 'text_formal' if case['side'] == 'formal' else 'text_return'
    if case['shape'] == 'union' and case['side'] == 'return':
        encoded += str(case['return_members'].index('class'))
    encoded = encoded if name is None else json.dumps(base64.b64encode(name.encode()).decode())
    metadata = 'metadata_formal' if case['side'] == 'formal' else 'metadata_return' + (str(case['return_members'].index('class')) if case['shape'] == 'union' else '')
    wrapper = ('metadata_nullable_formal' if case['shape'] == 'nullable' else 'metadata_formal_union') if case['side'] == 'formal' else ('metadata_nullable' if case['shape'] == 'nullable' else 'metadata_union')
    atom = tag + ' (BYTES ' + encoded + ') ' + metadata
    if case['shape'] == 'bare':
        return atom
    if case['shape'] == 'nullable':
        return 'NNullableType (' + atom + ') ' + wrapper
    members = case['formal_members'] if case['side'] == 'formal' else case['return_members']
    nodes = [atom if kind == 'class' else 'NIdentifier (BYTES ' + json.dumps(base64.b64encode(kind.encode()).decode()) + ') ' + metadata for kind in members]
    return 'NUnionType (SEQUENCE ([' + ', '.join(nodes) + '])) ' + wrapper


def controls(case):
    env, signature = 'pfunction_producer.ENV', 'pfunction_producer.SIGNATURE'
    role = case['role_index'] if case['side'] == 'formal' else 0
    parameter = 'psparam' if role == 0 else 'psparam_last'
    def param(typename):
        return 'NParam (SEQUENCE eps) (INTEGER 0) (' + typename + ') (BOOLEAN ' + str(role == 1).lower() + ') (BOOLEAN false) ' + ('phpType10' if role == 0 else 'phpType10_last') + ' ABSENT (SEQUENCE eps) ' + ('metadata_parameter' if role == 0 else 'metadata_parameter_last')
    def proof(typename=None, context=env, spelling=None):
        arguments, result, checked = 'phpType16', 'phpType18', signature
        if typename is not None:
            if case['side'] == 'formal':
                arguments = 'SEQUENCE ([' + ('' if role == 0 else 'phpType17, ') + param(typename) + '])'
            else:
                result = typename
        if spelling is not None:
            checked += ('[.PARAMETERS = [' + ('' if role == 0 else 'psparam, ') + parameter + '[.TYPE = ' + normalized(case, spelling) + ']]]' if case['side'] == 'formal' else '[.RETURNS = ' + normalized(case, spelling) + ']')
        return '$reference_notice_producer_scoped_header(' + context + ', phpType6_producer, ' + arguments + ', ' + result + ', ' + checked + ')'
    raw = raw_type(case)
    lines = [proof(), proof(raw), proof(raw_type(case, tag='NNameFullyQualified')),
        '~' + proof(context=env + '[.NAMESPACE = $ptascii("Other")]'),
        '~$error_call_valid(S_notice, perrorcall[.LINE = ' + str(case['notice_line'] + 1) + '])',
        '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])',
        '~$typed_return_task_valid(S_return, $(z_return + 1))']
    for imports in ('eps', '[($ptascii("stdclass"), $ptascii("Other"))]', '[($ptascii("box"), $ptascii("stdClass"))]'):
        lines.append(proof(raw, context=env + '[.CLASSES = ' + imports + ']'))
    for spelling in ('stdClass', 'STDCLASS', 'sTdClAsS', 'StDcLaSs'):
        changed = raw_type(case, spelling)
        lines += [proof(changed, spelling=spelling), '~' + proof(changed, spelling=spelling.swapcase())]
        if case['side'] == 'formal':
            view = '$reference_notice_producer_scoped_parameter_view(' + env + ', ' + param(changed) + ')'
            lines += [view + ' = (' + param(raw_type(case, spelling, 'NNameFullyQualified')) + ')',
                '$reference_notice_producer_global_parameter_view(' + param(changed) + ') = (' + param(changed) + ')']
        if spelling != case['relative_class']:
            lines.append('~' + proof(changed))
    for name in ('Other', 'Other\\stdClass', '\\stdClass', 'namespace\\stdClass', 'stdClass\x00', '', 'int', 'mixed', 'self', 'parent', 'static'):
        changed = raw_type(case, name)
        lines.append('~' + proof(changed))
        if case['side'] == 'formal':
            lines.append('$reference_notice_producer_scoped_parameter_view(' + env + ', ' + param(changed) + ') = (' + param(changed) + ')')
    metadata = 'metadata_formal' if case['side'] == 'formal' else 'metadata_return'
    if case['shape'] == 'union' and case['side'] == 'return':
        metadata += str(case['return_members'].index('class'))
    lines += ['~' + proof(raw_type(case, tag='NIdentifier')), proof(raw.replace(' ' + metadata, ' eps', 1))]
    for update in ('.BYREF = ' + str(role == 0).lower(), '.VARIADIC = true', '.REQUIRED = false', '.DEFAULT = PSDEFAULTUNSUPPORTED "forged case-preserving formal"'):
        parameters = '[' + ('' if role == 0 else 'psparam, ') + parameter + '[' + update + ']]'
        lines.append('~' + proof().replace(signature + ')', signature + '[.PARAMETERS = ' + parameters + '])'))
    if case['side'] == 'formal':
        viewed = param(raw_type(case, tag='NNameFullyQualified'))
        lines += ['$reference_notice_producer_scoped_parameter_view(' + env + ', ' + param(raw) + ') = (' + viewed + ')',
            '$reference_notice_producer_scoped_parameter_view(' + env + '[.NAMESPACE = $ptascii("Other")], ' + param(raw) + ') = (' + param(raw) + ')',
            '$reference_notice_producer_global_parameter_view(' + param(raw) + ') = (' + param(raw) + ')']
    if case['shape'] == 'union':
        members = case['formal_members'] if case['side'] == 'formal' else case['return_members']
        reverse = dict(case, **{('formal_members' if case['side'] == 'formal' else 'return_members'): members[::-1]})
        lines.append('~' + proof(raw_type(reverse, case['relative_class'])))
    for stage in (('receive', 'return', 'notice') if case['side'] == 'formal' else ('return', 'notice')):
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
    native, cases = json.loads(native_path.read_bytes()), json.loads(CATALOGUE.read_bytes())
    rows = {row['id']: row for row in native['records']}
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    assert native['mode'] == 'native-first' and native['passed'] and native['inputs_stable'] and native['head_stable']
    assert native['profile'] == types.PROFILE and native['runtime_sha256'] == sha(types.PHP)
    assert set(rows) == {case['id'] for case in cases} and len(cases) == 6
    out = args.output.resolve()
    out.mkdir(parents=True)
    paths = [CATALOGUE, native_path] + sorted({Path(module.__file__).absolute() for module in sys.modules.values() if getattr(module, '__file__', None) and Path(module.__file__).absolute().parent == ROOT / 'tests/semantics'})
    frontend = adapter = None
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
    print('global-relative-case-stdclass-front' if args.front else 'global-relative-case-stdclass-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
