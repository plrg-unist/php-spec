#!/usr/bin/env python3
"""Reach nullable/ordered-null iterable returns before private Notice-cell creation."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types
import singleton_cv_iterable_return_producer_reference_notice_state as prior

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('singleton_cv_nullable_iterable_return_producer_reference_notice_cases.json')
PREFIX = prior.PREFIX.replace('S.RESULT = KNOWN (PARRAY n_root)', 'S.RESULT = KNOWN pvalue\n  -- if $typed_tag(pvalue) <- ["array", "null"]')


def branches(members):
    return '[' + ', '.join('(PTBRANCH ([PTBUILTIN ' + json.dumps(kind) + ']))' for kind in members) + ']'


def raw(shape, members):
    iterable = '(NIdentifier (BYTES text_return) metadata_return)'
    if shape == 'nullable':
        return 'NNullableType ' + iterable + ' metadata_nullable'
    nodes = [iterable if kind == 'iterable' else '(NIdentifier (BYTES text_null) metadata_null)' for kind in members]
    return 'NUnionType (SEQUENCE ([' + ', '.join(nodes) + '])) metadata_union'


def reached(case, front):
    lines = []
    for line in prior.reached(case, front):
        line = line.replace(prior.ITERABLE, branches(case['return_members']))
        if line == 'phpType18 = NIdentifier (BYTES text_return) metadata_return':
            lines += ['phpType18 = ' + raw(case['return_shape'], case['return_members'])]
            if case['return_shape'] == 'union':
                lines += ['$ptlc($base64(text_null)) = $ptascii("null")']
        else:
            if case['value_kind'] == 'null':
                line = line.replace('(PARRAY n_root)', 'PNULL').replace('PARRAY n_root', 'PNULL')
                line = line.replace('$named_reference_notice_array(S_pre, PNULL)', '$named_reference_notice_root_value(S_pre, PNULL)')
            lines.append(line)
    return lines


def completed(case):
    lines = prior.completed(case)
    if case['value_kind'] == 'null':
        lines = [line.replace('(PARRAY n_root)', 'PNULL').replace('[HARRAY n_root]', 'eps') for line in lines]
    return lines


def controls(case):
    lines = ['~$typed_return_task_valid(S_return, $(z_return + 1))',
        'S_zero = $drive(S_return, 0)',
        r'S_zero.COMPLETION = BUDGET /\ S_zero[.COMPLETION = NORMAL] = S_return',
        '$drive($drive(S_zero[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_return, 2)']
    if case.get('priority_control'):
        return lines
    signature = 'pfunction_producer.SIGNATURE'
    header = '$reference_notice_producer_header(phpType6_producer, phpType16, '
    if case['return_shape'] == 'nullable':
        # Supply the literal null metadata used by the derived ordered headers.
        lines += ['text_null = "bnVsbA=="', 'metadata_null = metadata_return', 'metadata_union = metadata_nullable']
    else:
        lines += ['metadata_nullable = metadata_union']
    promoted = [line for line in prior.controls(case)
        if line.startswith(header + 'NNullableType ') or line.startswith(header + 'NUnionType ')]
    assert len(promoted) == 3
    lines += promoted
    lines += [header + 'NIdentifier (BYTES text_return) metadata_return, ' + signature + '[.RETURNS = ' + prior.ITERABLE + '])',
        '~' + header + raw('nullable', ['iterable', 'null']) + ', ' + signature + '[.RETURNS = ' + branches(['null', 'iterable']) + '])',
        '~' + header + raw('nullable', ['iterable', 'null']) + ', ' + signature + '[.RETURNS = ' + prior.ITERABLE + '])',
        '~' + header + 'NName (BYTES text_return) metadata_return, ' + signature + ')',
        '~' + header + 'NNameFullyQualified (BYTES text_return) metadata_return, ' + signature + ')',
        '$reference_notice_producer_arguments(SEQUENCE ([phpType7_actual, phpType7_actual]), SEQUENCE ([phpType17, phpType17]), ' + signature + '[.PARAMETERS = [psparam, psparam]][.RETURNS = eps])',
        '$reference_notice_producer_header(SEQUENCE ([phpType7_actual, phpType7_actual]), SEQUENCE ([phpType17, phpType17]), phpType18, ' + signature + '[.PARAMETERS = [psparam, psparam]])']
    for members in (['iterable', 'null'], ['null', 'iterable']):
        reversed_members = list(reversed(members))
        lines += ['~' + header + raw('union', members) + ', ' + signature + '[.RETURNS = ' + branches(reversed_members) + '])']
    for members in (['iterable', 'false'], ['false', 'iterable']):
        false_node = '(NIdentifier (BYTES "ZmFsc2U=") metadata_return)'
        iterable_node = '(NIdentifier (BYTES text_return) metadata_return)'
        nodes = [iterable_node if kind == 'iterable' else false_node for kind in members]
        lines += ['~' + header + 'NUnionType (SEQUENCE ([' + ', '.join(nodes) + '])) metadata_union, ' + signature + '[.RETURNS = ' + branches(members) + '])']
    for edit in ('REQUIRED = false', 'VARIADIC = true', 'BYREF = ' + str(not case['formal_byref']).lower(),
                 'TYPE = [(PTBRANCH ([PTBUILTIN "bool"]))]'):
        lines += ['~' + header + 'phpType18, ' + signature + '[.PARAMETERS = [psparam[.' + edit + ']]])']
    lines += ['phpType17 = NParam (SEQUENCE eps) (INTEGER 0) phpType18_formal (BOOLEAN b_ref) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter',
        '~$reference_notice_producer_header(phpType6_producer, SEQUENCE ([NParam (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES "aXRlcmFibGU=") metadata_return) (BOOLEAN b_ref) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter]), phpType18, ' + signature + '[.PARAMETERS = [psparam[.TYPE = ' + prior.ITERABLE + ']]])',
        '~$reference_notice_producer_header(SEQUENCE ([NArg ABSENT (NExprVariable (BYTES "aHR0cF9yZXNwb25zZV9oZWFkZXI=") metadata_variable) (BOOLEAN false) (BOOLEAN false) metadata_actual]), phpType16, phpType18, ' + signature + ')']
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
    paths = [Path(__file__), Path(prior.__file__), CATALOGUE, provenance]
    specs, reached_lines, derived_lines = [], [], []
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
            initial = 'S_initial = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'
            current = [initial] + reached(case, args.front)
            extra = [] if args.front else controls(case)
            if not args.front:
                current += completed(case)
            specs.append('dec $ir_case' + str(index) + '() : bool\ndef $ir_case' + str(index) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in current + extra))
            reached_lines += current
            derived_lines += extra
            paths += [source, Path(row['stdout']), Path(row['stderr'])]
    finally:
        try:
            if frontend:
                frontend.close()
        finally:
            if adapter:
                adapter.close()
    prefix = PREFIX
    for marker, name in (('NAMES_MAKE', 'make'), ('NAMES_TAKE', 'take')):
        prefix = prefix.replace(marker, '[' + ', '.join('$ptascii(' + json.dumps(case['namespace'] + '\\' + name) + ')' for case in cases) + ']')
    fixture = out / 'state.watsup'
    fixture.write_text(prefix + '\n'.join(specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $ir_case' + str(index) + '()\n' for index in range(len(cases))))
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
    report = dict(revision=revision, inputs=before, inputs_stable=stable, head_stable=head_stable, module_count=len(modules), mode='fixture-SL/cache=false/det=true', front=args.front, selection=[case['id'] for case in cases], conditions=len(reached_lines) + len(derived_lines), reached_conditions=len(reached_lines), derived_conditions=len(derived_lines), source_agreements=0, process=process, passed=passed)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('singleton-cv-nullable-iterable-return-front' if args.front else 'singleton-cv-nullable-iterable-return-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
