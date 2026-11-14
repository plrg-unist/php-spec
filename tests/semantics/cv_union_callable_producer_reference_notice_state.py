#!/usr/bin/env python3
"""Reach ordered callable/null headers, captured names and private Notice cells."""
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
import cv_nullable_callable_producer_reference_notice_state as prior

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_union_callable_producer_reference_notice_cases.json')
PREFIX = prior.PREFIX.replace('83', '84')


def branches(reverse):
    members = ['(PTBRANCH ([PTBUILTIN "callable"]))', '(PTBRANCH ([PTBUILTIN "null"]))']
    return '[' + ', '.join(reversed(members) if reverse else members) + ']'


def raw(which, reverse):
    metadata = 'metadata_type' if which == 'parameter' else 'metadata_return'
    members = ['NIdentifier (BYTES text_' + which + ') ' + metadata,
        'NIdentifier (BYTES text_null_' + which + ') metadata_null_' + which]
    return 'NUnionType (SEQUENCE ([' + ', '.join(reversed(members) if reverse else members) + '])) metadata_union_' + which


def reached(case, front):
    result = []
    for line in prior.reached(case, front):
        line = line.replace('(NNullableType (NIdentifier (BYTES text_parameter) metadata_type) metadata_nullable_type)', '(' + raw('parameter', case['formal_null_first']) + ')')
        if line.startswith('psparam.TYPE = '):
            line = line.replace(prior.CALLABLE, branches(case['formal_null_first']))
        if line.startswith('pfunction_producer.SIGNATURE.RETURNS = '):
            line = line.replace(prior.CALLABLE, branches(case['return_null_first']))
        if line.startswith('phpType18 = '):
            line = 'phpType18 = ' + raw('return', case['return_null_first'])
        result.append(line)
    result += ['$ptlc($base64(text_null_parameter)) = $ptascii("null")',
        '$ptlc($base64(text_null_return)) = $ptascii("null")']
    return result


def completed(case):
    return prior.completed(case)


def controls(case):
    result = ['~$typed_return_task_valid(S_return, $(z_return + 1))',
        '~$error_call_valid(S_notice, perrorcall[.LINE = $(perrorcall.LINE + 1)])',
        '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])']
    returns = branches(case['return_null_first'])
    for strict in ('false', 'true'):
        for value in ('pvalue_original', 'PNULL'):
            result += ['$typed_conversion_at(S_return, ' + returns + ', ' + value + ', ' + strict + ') = TYPEVALUE ' + value]
        for bad in ('PINT 17', 'PBOOL true', 'PSTRING eps', 'PSTRING ($ptascii("missingUnionCallable84"))'):
            result += ['$typed_conversion_at(S_return, ' + returns + ', ' + bad + ', ' + strict + ') = TYPEREJECT']
        for field in ('CALLABLES', 'FUNCTIONS'):
            result += ['$typed_conversion_at(S_return[.' + field + ' = eps], ' + returns + ', PNULL, ' + strict + ') = TYPEVALUE PNULL']
            if case['carrier'] != 'PNULL':
                result += ['$typed_conversion_at(S_return[.' + field + ' = eps], ' + returns + ', pvalue_original, ' + strict + ') = TYPEREJECT']
    signature = 'pfunction_producer.SIGNATURE'
    header = '$reference_notice_producer_header(phpType6_producer, phpType16, '
    for wrong in (branches(not case['return_null_first']), '[(PTBRANCH ([PTBUILTIN "callable"]))]',
            '[(PTBRANCH ([PTBUILTIN "null"]))]', returns[:-1] + ', (PTBRANCH ([PTBUILTIN "null"]))]'):
        result += ['~' + header + 'phpType18, ' + signature + '[.RETURNS = ' + wrong + '])']
    for tag in ('NName', 'NNameFullyQualified'):
        changed = raw('return', case['return_null_first']).replace('NIdentifier (BYTES text_return)', tag + ' (BYTES text_return)')
        result += ['~' + header + changed + ', ' + signature + ')']
    raw_parameter = 'NParam (SEQUENCE eps) (INTEGER 0) (__TYPE__) (BOOLEAN ' + str(case['byref']).lower() + ') (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter'
    raw_tail = ', NParam (SEQUENCE eps) (INTEGER 0) ABSENT (BOOLEAN true) (BOOLEAN false) phpType10_last ABSENT (SEQUENCE eps) metadata_last' if case['multiple'] else ''
    for members in (('callable', 'int'), ('int', 'callable'), ('callable', 'string'), ('string', 'callable'), ('callable', 'null', 'int')):
        atoms = ', '.join('NIdentifier (BYTES ' + json.dumps(base64.b64encode(kind.encode()).decode()) + ') metadata_return' for kind in members)
        changed = 'NUnionType (SEQUENCE ([' + atoms + '])) metadata_union_return'
        normalized = '[' + ', '.join('(PTBRANCH ([PTBUILTIN ' + json.dumps(kind) + ']))' for kind in members) + ']'
        parameters = '[psparam[.TYPE = ' + normalized + ']' + (', psparam_last' if case['multiple'] else '') + ']'
        refused = '' if len(members) == 2 and ('string' in members or 'int' in members) or members == ('callable', 'null', 'int') else '~'
        result += [refused + '$reference_notice_producer_arguments(phpType6_producer, SEQUENCE ([' + raw_parameter.replace('__TYPE__', changed) + raw_tail + ']), ' + signature + '[.RETURNS = eps][.PARAMETERS = ' + parameters + '])']
        result += [refused + header + changed + ', ' + signature + '[.RETURNS = ' + normalized + '])']
    old_nullable = 'NNullableType (NIdentifier (BYTES text_return) metadata_return) metadata_union_return'
    result += [('~' if case['return_null_first'] else '') + header + old_nullable + ', ' + signature + ')']
    old_ordered = 'NUnionType (SEQUENCE ([NIdentifier (BYTES text_return) metadata_return, NIdentifier (BYTES "bnVsbA==") metadata_return])) metadata_union_return'
    result += [header + old_ordered + ', ' + signature + '[.RETURNS = ' + prior.CALLABLE + '])']
    params = '[psparam, psparam_last]' if case['multiple'] else '[psparam]'
    for update in ('.TYPE = ' + branches(not case['formal_null_first']),
            '.TYPE = [(PTBRANCH ([PTBUILTIN "callable"]))]', '.BYREF = ' + str(not case['byref']).lower(),
            '.REQUIRED = false', '.VARIADIC = true', '.DEFAULT = PSDEFAULTUNSUPPORTED "forged union callable default"'):
        changed = params.replace('psparam', 'psparam[' + update + ']', 1)
        result += ['~' + header + 'phpType18, ' + signature + '[.PARAMETERS = ' + changed + '])']
    for stage in ('return', 'notice'):
        result += ['S_zero_' + stage + ' = $drive(S_' + stage + ', 0)',
            'S_zero_' + stage + r'.COMPLETION = BUDGET /\ S_zero_' + stage + '[.COMPLETION = NORMAL] = S_' + stage,
            '$drive($drive(S_zero_' + stage + '[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_' + stage + ', 2)']
    return result

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
    assert set(rows) == {case['id'] for case in cases} and len(cases) == 3
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    paths = [Path(__file__), Path(prior.__file__), Path(prior.prior.__file__), CATALOGUE, provenance]
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
            specs.append('dec $cn_case' + str(index) + '() : bool\ndef $cn_case' + str(index) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in current + extra))
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
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\n'.join(specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $cn_case' + str(index) + '()\n' for index in range(len(cases))))
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
    report = dict(revision=revision, inputs=before, inputs_stable=stable, head_stable=head_stable, module_count=len(modules), mode='fixture-SL/cache=false/det=true', front=args.front, selection=[case['id'] for case in cases], conditions=len(reached_lines) + len(derived_lines), reached_conditions=len(reached_lines), derived_conditions=len(derived_lines), source_agreements=0, process=process, passed=passed)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('cv-union-callable-front' if args.front else 'cv-union-callable-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
