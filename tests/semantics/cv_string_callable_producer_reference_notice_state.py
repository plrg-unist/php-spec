#!/usr/bin/env python3
"""Reach string exact fastmatch and weak integer-return string ownership."""
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
import cv_callable_producer_reference_notice_state as prior

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_string_callable_producer_reference_notice_cases.json')
PREFIX = prior.PREFIX.replace('82', '85')


def branches(members):
    return '[' + ', '.join('(PTBRANCH ([PTBUILTIN ' + json.dumps(kind) + ']))' for kind in members) + ']'


def raw(which):
    return 'NUnionType (SEQUENCE ([NIdentifier (BYTES text_' + which + '_first) metadata_' + which + '_first, NIdentifier (BYTES text_' + which + '_last) metadata_' + which + '_last])) metadata_union_' + which


def reached(case, front):
    result = []
    for line in prior.reached(case, front):
        if line.startswith(('~$pfunction_builtin(', '$callable_at(', '$function_at(S_return.FUNCTIONS,', '$typed_registered(', '$typed_callable(')):
            continue
        if line.startswith(('$ptlc($base64(text_parameter))', '$ptlc($base64(text_return))')):
            continue
        annotation = '(' + raw('parameter') + ')' if case['formal_members'] else 'ABSENT'
        line = line.replace('(NIdentifier (BYTES text_parameter) metadata_type)', annotation)
        if line.startswith('psparam.TYPE = '):
            line = line.replace(prior.CALLABLE, branches(case['formal_members']) if case['formal_members'] else 'eps')
        if line.startswith('pfunction_producer.SIGNATURE.RETURNS = '):
            line = line.replace(prior.CALLABLE, branches(case['return_members']))
        if line.startswith('phpType18 = '):
            line = 'phpType18 = ' + raw('return')
        if case['weak_return']:
            if line.startswith(('$string_bytes(', 'pvalue_original = PSTRING_CARRIER', '$string_carrier_valid(S_return,')):
                continue
            if line == 'S_resolved.RESULT = KNOWN pvalue_original':
                line = 'S_resolved.RESULT = KNOWN (PINT 17)'
            if line == '$typed_return_value(S_return, z_return) = S_resolved':
                result += [
                    '$typed_conversion_at(S_resolved, ' + branches(case['return_members']) + ', PINT 17, false) = TYPESTRING (PINT 17)',
                    'S_checked = $typed_return_value(S_return, z_return)',
                    'S_checked = $typed_apply(S_resolved, TYPESTRING (PINT 17), z_return)',
                    'pvalue_original = PSTRING_CARRIER (REQUEST_STRING (|S_return.STRINGDATA|)) ($ptascii("17"))',
                    'S_checked.RESULT = KNOWN pvalue_original',
                    '$string_bytes(pvalue_original) = (ptbytes_name)',
                    'S_checked.STRINGDATA = S_return.STRINGDATA ++ [ptbytes_name]',
                    '$string_carrier_valid(S_checked, pvalue_original)',
                ]
                continue
            for slot in ('S_return.STORE[n_saved]', 'S_return.STORE[n_copy]', 'S_pre.STORE[n_copy]'):
                if line == slot + ' = DEFINED pvalue_original':
                    line = slot + ' = DEFINED (PINT 17)'
        result.append(line)
    for which, members in (('parameter', case['formal_members']), ('return', case['return_members'])):
        if members:
            for role, kind in zip(('first', 'last'), members):
                result += ['$ptlc($base64(text_' + which + '_' + role + ')) = $ptascii(' + json.dumps(kind) + ')']
    result += ['ptbytes_name = $ptascii(' + json.dumps(case['value_bytes']) + ')',
        '~$typed_registered(S_pre, ptbytes_name)',
        '$typed_exact(' + branches(case['return_members']) + ', pvalue_original)',
        '$string_carrier_valid(S_pre, pvalue_original)']
    if case['weak_return']:
        result += ['S_after_return.STRINGDATA = S_checked.STRINGDATA']
    return result


def completed(case):
    lines = prior.completed(case)
    if case['weak_return']:
        lines = [line.replace('S_resume.STORE[n_copy] = DEFINED pvalue_original', 'S_resume.STORE[n_copy] = DEFINED (PINT 17)') for line in lines]
    return lines


def controls(case):
    returns = branches(case['return_members'])
    result = ['~$typed_return_task_valid(S_return, $(z_return + 1))',
        '~$error_call_valid(S_notice, perrorcall[.LINE = $(perrorcall.LINE + 1)])',
        '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])']
    for strict in ('false', 'true'):
        result += ['$typed_conversion_at(S_pre, ' + returns + ', pvalue_original, ' + strict + ') = TYPEVALUE pvalue_original',
            '$typed_conversion_at(S_pre, ' + returns + ', PNULL, ' + strict + ') = TYPEREJECT',
            '$typed_conversion_at(S_pre[.CALLABLES = eps][.FUNCTIONS = eps][.CLASSES = eps], ' + returns + ', pvalue_original, ' + strict + ') = TYPEVALUE pvalue_original']
        for value in ('PINT 17', 'PBOOL true'):
            result += ['$typed_conversion_at(S_pre, ' + returns + ', ' + value + ', ' + strict + ') = ' + ('TYPEREJECT' if strict == 'true' else 'TYPESTRING (' + value + ')')]
    signature = 'pfunction_producer.SIGNATURE'
    header = '$reference_notice_producer_header(phpType6_producer, phpType16, '
    for wrong in (branches(list(reversed(case['return_members']))), branches(['callable']), branches(['string']), returns[:-1] + ', (PTBRANCH ([PTBUILTIN "string"]))]'):
        result += ['~' + header + 'phpType18, ' + signature + '[.RETURNS = ' + wrong + '])']
    params = '[psparam, psparam_last]' if case['multiple'] else '[psparam]'
    for update in ('.TYPE = ' + (branches(list(reversed(case['formal_members']))) if case['formal_members'] else returns),
            '.BYREF = ' + str(not case['byref']).lower(), '.REQUIRED = false', '.VARIADIC = true',
            '.DEFAULT = PSDEFAULTUNSUPPORTED "forged string callable default"'):
        changed = params.replace('psparam', 'psparam[' + update + ']', 1)
        result += ['~' + header + 'phpType18, ' + signature + '[.PARAMETERS = ' + changed + '])']
    raw_parameter = 'NParam (SEQUENCE eps) (INTEGER 0) (__TYPE__) (BOOLEAN ' + str(case['byref']).lower() + ') (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter'
    raw_tail = ', NParam (SEQUENCE eps) (INTEGER 0) ABSENT (BOOLEAN true) (BOOLEAN false) phpType10_last ABSENT (SEQUENCE eps) metadata_last' if case['multiple'] else ''
    for members in (('callable', 'string'), ('string', 'callable'), ('callable', 'null'), ('null', 'callable'),
            ('callable', 'int'), ('int', 'callable'), ('callable', 'bool'), ('bool', 'callable'), ('callable', 'null', 'string'), ('callable', 'callable')):
        atoms = ', '.join('NIdentifier (BYTES ' + json.dumps(base64.b64encode(kind.encode()).decode()) + ') metadata_return_first' for kind in members)
        changed = 'NUnionType (SEQUENCE ([' + atoms + '])) metadata_union_return'
        normalized = branches(members)
        refused = '' if members == ('callable', 'null', 'string') or len(members) == 2 and ('string' in members or 'null' in members or 'int' in members or 'bool' in members) and len(set(members)) == 2 else '~'
        parameters = '[psparam[.TYPE = ' + normalized + ']' + (', psparam_last' if case['multiple'] else '') + ']'
        result += [refused + header + changed + ', ' + signature + '[.RETURNS = ' + normalized + '])',
            refused + '$reference_notice_producer_arguments(phpType6_producer, SEQUENCE ([' + raw_parameter.replace('__TYPE__', changed) + raw_tail + ']), ' + signature + '[.RETURNS = eps][.PARAMETERS = ' + parameters + '])']
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
    print('cv-string-callable-front' if args.front else 'cv-string-callable-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
