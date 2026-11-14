#!/usr/bin/env python3
"""Reach exact FQN stdClass/callable unions, class checks and private Notice cells."""
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
import cv_builtin_callable_union_producer_reference_notice_state as prior

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_fqn_stdclass_callable_union_producer_reference_notice_cases.json')
PREFIX = prior.PREFIX.replace('92', '93')
ROLES = prior.ROLES


def branches(members):
    atoms = ['PTCLASS ($ptascii(' + json.dumps(kind[1:]) + '))' if kind.startswith('\\') else 'PTBUILTIN ' + json.dumps(kind) for kind in members]
    return '[' + ', '.join('(PTBRANCH ([' + atom + ']))' for atom in atoms) + ']'


def raw(which, members):
    atoms = ', '.join(('NNameFullyQualified' if kind.startswith('\\') else 'NIdentifier') + ' (BYTES text_' + which + '_' + role + ') metadata_' + which + '_' + role for role, kind in zip(ROLES, members))
    return 'NUnionType (SEQUENCE ([' + atoms + '])) metadata_union_' + which


def reached(case, front):
    result = []
    for line in prior.reached(case, front):
        if line.startswith(('$ptlc($base64(text_parameter_', '$ptlc($base64(text_return_')):
            continue
        for which, members in (('parameter', case['formal_members']), ('return', case['return_members'])):
            line = line.replace(prior.raw(which, members), raw(which, members))
            line = line.replace(prior.branches(members), branches(members))
        result.append(line)
    for which, members in (('parameter', case['formal_members']), ('return', case['return_members'])):
        for role, kind in zip(ROLES, members):
            if kind.startswith('\\'):
                result += ['$base64(text_' + which + '_' + role + ') = $ptascii(' + json.dumps(kind[1:]) + ')']
            else:
                result += ['$ptlc($base64(text_' + which + '_' + role + ')) = $ptascii(' + json.dumps(kind) + ')']
    return result


def completed(case):
    return prior.completed(case)


def controls(case):
    result = ['~$typed_return_task_valid(S_return, $(z_return + 1))',
        '~$error_call_valid(S_notice, perrorcall[.LINE = $(perrorcall.LINE + 1)])',
        '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])']
    for members in (case['formal_members'], case['return_members']):
        normalized = branches(members)
        masks = [tag for kind in members if not kind.startswith('\\') for tag in (('true', 'false') if kind == 'bool' else (kind,))]
        result += ['$ptmasks(' + normalized + ') = [' + ', '.join(json.dumps(kind) for kind in masks) + ']']
        for strict in ('false', 'true'):
            result += ['$typed_conversion_at(S_return, ' + normalized + ', pvalue_original, ' + strict + ') = TYPEVALUE pvalue_original',
                '$typed_conversion_at(S_return[.CALLABLES = eps][.FUNCTIONS = eps][.CLASSES = eps], ' + normalized + ', pvalue_original, ' + strict + ') = TYPEVALUE pvalue_original']
        if case['value_kind'] == 'object':
            result += ['~$typed_exact(' + normalized + ', pvalue_original)',
                '$typed_object_exact(S_return, ' + normalized + ', pvalue_original)']
    signature = 'pfunction_producer.SIGNATURE'
    header = '$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, '
    returns = case['return_members']
    for members in (list(reversed(returns)), returns[:-1], returns + ['callable'], [kind.lower() if kind.startswith('\\') else kind for kind in returns]):
        result += ['~' + header + signature + '[.RETURNS = ' + branches(members) + '])']
    params = '[psparam, psparam_last]' if case['multiple'] else '[psparam]'
    for update in ('.TYPE = ' + branches(list(reversed(case['formal_members']))),
            '.BYREF = ' + str(not case['byref']).lower(), '.REQUIRED = false', '.VARIADIC = true',
            '.DEFAULT = PSDEFAULTUNSUPPORTED "forged FQN class callable default"'):
        changed = params.replace('psparam', 'psparam[' + update + ']', 1)
        result += ['~' + header + signature + '[.PARAMETERS = ' + changed + '])']
    if case['value_kind'] == 'object':
        result += ['~$named_reference_notice_object(S_pre[.OBJECTPROPS = eps], pvalue_original)',
            '~$named_reference_notice_object(S_pre[.ALLOCATIONS = eps], pvalue_original)',
            '~$named_reference_notice_object(S_pre, POBJECT (|S_pre.OBJECTS|))']
    if case['value_kind'] == 'string':
        result += ['$typed_registered(S_return, ptbytes_name)',
            '~$typed_registered(S_return[.CALLABLES = eps][.FUNCTIONS = eps], ptbytes_name)']
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
    paths = [Path(__file__), Path(prior.__file__), Path(prior.prior.__file__), Path(prior.prior.prior.__file__), Path(prior.prior.union_prior.__file__), Path(prior.object_prior.__file__), Path(prior.string_prior.__file__), CATALOGUE, provenance]
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
    print('cv-fqn-stdclass-callable-union-front' if args.front else 'cv-fqn-stdclass-callable-union-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
