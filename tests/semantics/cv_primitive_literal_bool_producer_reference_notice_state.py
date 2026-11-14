#!/usr/bin/env python3
"""Ground primitive literal-Boolean union folds and existing producer ownership."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import error_handler_run as recorder
from recorded_worker import Worker
import cv_nonnull_literal_bool_producer_reference_notice_state as prior
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_primitive_literal_bool_producer_reference_notice_cases.json')
single, multi, base = prior.single, prior.multi, prior.base
PREFIX = prior.PREFIX.replace('SingletonNonnullFalse74', 'SingletonPrimitiveFalse75').replace('MultiCvNonnullTrue74', 'MultiCvPrimitiveTrue75')


def normalized(members):
    return '[' + ', '.join('(PTBRANCH ([PTBUILTIN "' + member + '"]))' for member in members) + ']'


def raw_union(members, metadata, variable=None):
    nodes = []
    for i, member in enumerate(members):
        if variable and member == variable[0]:
            nodes.append('NIdentifier (BYTES ' + variable[1] + ') ' + variable[2])
        else:
            nodes.append('NIdentifier (BYTES "' + base64.b64encode(member.encode()).decode() + '") ' + metadata + ('_' + str(i) if variable else ''))
    return 'NUnionType (SEQUENCE ([' + ', '.join(nodes) + '])) ' + metadata


def front_lines(index, case):
    lines = prior.front_lines(index, case)
    if index == 0:
        changes = {
            'psparam.TYPE = ': 'psparam.TYPE = ' + normalized(case['formal_members']),
            'pfunction_producer.SIGNATURE.RETURNS = ': 'pfunction_producer.SIGNATURE.RETURNS = ' + normalized(case['return_members']),
            'phpType17 = NParam (SEQUENCE eps) (INTEGER 0) (NUnionType':
                'phpType17 = NParam (SEQUENCE eps) (INTEGER 0) (' + raw_union(case['formal_members'], 'metadata_union_parameter', ('false', 'text_type', 'metadata_type')) + ') (BOOLEAN true) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter',
            'phpType18 = NUnionType': 'phpType18 = ' + raw_union(case['return_members'], 'metadata_union_return', ('false', 'text_return', 'metadata_return'))}
    else:
        changes = {
            'psparam_first.TYPE = ': 'psparam_first.TYPE = ' + normalized(case['formal_members'][0]) + r' /\ psparam_last.TYPE = ' + normalized(case['formal_members'][1]),
            'pfunction_producer.SIGNATURE.RETURNS = ': 'pfunction_producer.SIGNATURE.RETURNS = ' + normalized(case['return_members']) + r' /\ ~pfunction_producer.SIGNATURE.BYREF',
            'phpType18_return = NUnionType': 'phpType18_return = ' + raw_union(case['return_members'], 'metadata_union_return', ('true', 'text_return', 'metadata_type')),
            'phpType17_first = NParam': 'phpType17_first = NParam (SEQUENCE eps) (INTEGER 0) (' + raw_union(case['formal_members'][0], 'metadata_union_first', ('true', 'text_type_first', 'metadata_type_first')) + ') (BOOLEAN false) (BOOLEAN false) phpType10_first ABSENT (SEQUENCE eps) metadata_parameter_first',
            'phpType17_last = NParam': 'phpType17_last = NParam (SEQUENCE eps) (INTEGER 0) (' + raw_union(case['formal_members'][1], 'metadata_union_last', ('false', 'text_type_last', 'metadata_type_last')) + ') (BOOLEAN true) (BOOLEAN false) phpType10_last ABSENT (SEQUENCE eps) metadata_parameter_last'}
    for prefix, new in changes.items():
        old, = [line for line in lines if line.startswith(prefix)]
        lines = [new if line == old else line for line in lines]
    return lines


def full_lines(index, case):
    return prior.full_lines(index, case)


def controls(index, case):
    actuals = '([phpType7])' if index == 0 else '([phpType7_first, phpType7_last])'
    raw_parameters = '([phpType17])' if index == 0 else '([phpType17_first, phpType17_last])'
    header = '$reference_notice_producer_header(SEQUENCE ' + actuals + ', SEQUENCE ' + raw_parameters + ', '
    signature = 'pfunction_producer.SIGNATURE'
    raw = 'phpType18' if index == 0 else 'phpType18_return'
    meta = 'metadata_return' if index == 0 else 'metadata_type'
    slot, tail = ('psparam', '') if index == 0 else ('psparam_first', ', psparam_last')
    raw_tail = '' if index == 0 else ', phpType17_last'
    byref = 'true' if index == 0 else 'false'
    variable = 'phpType10' if index == 0 else 'phpType10_first'
    parameter_meta = 'metadata_parameter' if index == 0 else 'metadata_parameter_first'
    proof = '$reference_notice_producer_arguments(SEQUENCE ' + actuals + ', SEQUENCE (['
    lines = ['~$typed_return_task_valid(S_return, $(z_return + 1))',
        '~$error_call_valid(S_notice, perrorcall[.LINE = $(perrorcall.LINE + 1)])',
        '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])',
        '~' + header + raw + ', ' + signature + '[.RETURNS = ' + normalized(list(reversed(case['return_members']))) + '])']
    for literal in ('false', 'true'):
        for count in range(3, 7):
            original = [literal, 'int', 'float', 'string', 'null', 'array'][:count]
            for reverse in (False, True):
                members = list(reversed(original)) if reverse else original
                norm = normalized(members)
                node = raw_union(members, meta)
                parameter = 'NParam (SEQUENCE eps) (INTEGER 0) (' + node + ') (BOOLEAN ' + byref + ') (BOOLEAN false) ' + variable + ' ABSENT (SEQUENCE eps) ' + parameter_meta
                lines += [header + node + ', ' + signature + '[.RETURNS = ' + norm + '])',
                    proof + parameter + raw_tail + ']), ' + signature + '[.RETURNS = eps][.PARAMETERS = [' + slot + '[.TYPE = ' + norm + ']' + tail + ']])',
                    '~' + header + node + ', ' + signature + '[.RETURNS = ' + normalized(list(reversed(members))) + '])',
                    '~' + header + node + ', ' + signature + '[.RETURNS = ' + normalized(members[:-1]) + '])']
                for strict in ('false', 'true'):
                    lines += ['$typed_conversion_at(S_return, ' + norm + ', PBOOL ' + literal + ', ' + strict + ') = TYPEVALUE (PBOOL ' + literal + ')']
        for members in ([literal, 'null', 'int'], [literal, 'int', 'string']):
            norm, node = normalized(members), raw_union(members, meta)
            parameter = 'NParam (SEQUENCE eps) (INTEGER 0) (' + node + ') (BOOLEAN ' + byref + ') (BOOLEAN false) ' + variable + ' ABSENT (SEQUENCE eps) ' + parameter_meta
            lines += [header + node + ', ' + signature + '[.RETURNS = ' + norm + '])',
                proof + parameter + raw_tail + ']), ' + signature + '[.RETURNS = eps][.PARAMETERS = [' + slot + '[.TYPE = ' + norm + ']' + tail + ']])']
        for bad in ('bool', 'true' if literal == 'false' else 'false', literal, 'object', 'mixed', 'callable', 'void', 'never'):
            for members in ([literal, 'int', bad], [bad, 'int', literal]):
                norm = normalized(members)
                node = raw_union(members, meta)
                parameter = 'NParam (SEQUENCE eps) (INTEGER 0) (' + node + ') (BOOLEAN ' + byref + ') (BOOLEAN false) ' + variable + ' ABSENT (SEQUENCE eps) ' + parameter_meta
                lines += ['~' + header + node + ', ' + signature + '[.RETURNS = ' + norm + '])',
                    '~' + proof + parameter + raw_tail + ']), ' + signature + '[.RETURNS = eps][.PARAMETERS = [' + slot + '[.TYPE = ' + norm + ']' + tail + ']])']
    for name in ('return', 'notice'):
        stage = 'S_' + name
        lines += ['S_zero_' + name + ' = $drive(' + stage + ', 0)',
            'S_zero_' + name + r'.COMPLETION = BUDGET /\ S_zero_' + name + '[.COMPLETION = NORMAL] = ' + stage,
            '$drive($drive(S_zero_' + name + '[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(' + stage + ', 2)']
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
    paths = modules + [runner, Path(__file__), Path(prior.__file__), Path(prior.prior.__file__), Path(base.__file__), Path(single.__file__), Path(multi.__file__), CATALOGUE, fixture, native_path, ROOT / 'spec/semantics/modules.json', ROOT / '_build/default/adapter/main.exe', types.PHP, ROOT / '.tools/php-file.so']
    paths += [ROOT / path for path in ('tests/semantics/cv_nonnull_literal_bool_producer_reference_notice_state.py', 'tests/semantics/error_handler_run.py', 'tests/semantics/scalar_return_producer_cv_reference_notice_review_state.py', 'tests/semantics/cv_union_literal_bool_producer_reference_notice_state.py', 'tests/semantics/cv_union_null_literal_bool_producer_reference_notice_review_state.py', 'tests/semantics/cv_nullable_literal_bool_producer_reference_notice_review_state.py', 'tests/semantics/cv_literal_bool_return_producer_reference_notice_state.py', 'tests/semantics/cv_literal_bool_formal_producer_reference_notice_state.py', 'tests/semantics/cv_literal_bool_formal_producer_reference_notice_review_state.py', 'tests/semantics/cv_literal_bool_return_producer_reference_notice_review_state.py', 'tests/semantics/profile.json', 'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py', 'tests/validate.py', 'tests/corpus.py', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py')]
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
    print('cv-primitive-literal-bool-front' if args.front else 'cv-primitive-literal-bool-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
