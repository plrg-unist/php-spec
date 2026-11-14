#!/usr/bin/env python3
"""Reach integer/callable reception, retirement and separate Notice cells."""
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
import cv_union_callable_producer_reference_notice_state as union_prior
import cv_string_callable_producer_reference_notice_state as string_prior

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_int_callable_producer_reference_notice_cases.json')
PREFIX = prior.PREFIX.replace('82', '86').replace('N;M:17;H:10:1;', 'N;M:1;H:10:1;')
PREFIX = PREFIX.replace('def $cn_ready(S, n_stage) = false -- otherwise', r'''def $cn_ready(S, 3) = true
  -- if S.TODO = (TYPE_RECEIVE porigin 0) :: eps
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.NAME <- [$ptascii("CallableSingletonByval86\\make"), $ptascii("CallableSingletonByref86\\make"), $ptascii("CallableMulti86\\make")]
def $cn_ready(S, n_stage) = false -- otherwise''')
branches, raw = string_prior.branches, string_prior.raw


def reached(case, front):
    result = []
    for line in prior.reached(case, front):
        if line.startswith(('$ptlc($base64(text_parameter))', '$ptlc($base64(text_return))')):
            continue
        line = line.replace('(NIdentifier (BYTES text_parameter) metadata_type)', '(' + raw('parameter') + ')')
        if line.startswith('psparam.TYPE = '):
            line = line.replace(prior.CALLABLE, branches(case['formal_members']))
        if line.startswith('pfunction_producer.SIGNATURE.RETURNS = '):
            line = line.replace(prior.CALLABLE, branches(case['return_members']))
        if line.startswith('phpType18 = '):
            line = 'phpType18 = ' + raw('return')
        if case['value_kind'] == 'integer':
            if line.startswith(('$string_bytes(pvalue_original)', 'pvalue_original = PSTRING_CARRIER',
                    '$string_carrier_valid(', '~$pfunction_builtin(', '$callable_at(',
                    '$function_at(S_return.FUNCTIONS,', '$typed_registered(', '$typed_callable(')):
                continue
            if case['weak_receive']:
                for slot in ('S_return.STORE[n_copy]', 'S_pre.STORE[n_copy]', 'S_pre.STORE[n_source]'):
                    line = line.replace(slot + ' = DEFINED pvalue_original', slot + ' = DEFINED pvalue_caller')
        result.append(line)
    for which, members in (('parameter', case['formal_members']), ('return', case['return_members'])):
        for role, kind in zip(('first', 'last'), members):
            result += ['$ptlc($base64(text_' + which + '_' + role + ')) = $ptascii(' + json.dumps(kind) + ')']
    if case['value_kind'] == 'integer':
        result += ['pvalue_original = PINT ' + str(case['integer'])]
    result += ['S_receive = $cn_seek(S_initial, 3, 2000)[.COMPLETION = NORMAL]',
        '$cn_ready(S_receive, 3)',
        'S_receive.TODO = (TYPE_RECEIVE porigin_receive 0) :: eps',
        '$typed_receive_valid(S_receive, porigin_receive, 0)',
        '$function_at($all_functions(S_receive), porigin_receive) = (pfunction_receive)',
        'pfunction_receive = pfunction_producer',
        '$lookup(S_receive.ENV, $ptascii("saved")) = (n_saved)',
        'S_receive.STORE[n_saved] = DEFINED pvalue_caller',
        ('$typed_caller_strict(S_receive)' if case['byref'] else '~$typed_caller_strict(S_receive)'),
        '$typed_parameter_conversion(S_receive, psparam, pvalue_caller) = ' + ('TYPEINTEGER pvalue_caller' if case['weak_receive'] else 'TYPEVALUE pvalue_caller'),
        'S_received = $drive(S_receive, 1)[.COMPLETION = NORMAL]',
        'S_received.STORE[n_saved] = DEFINED pvalue_original',
        r'S_received.PROPREFS = eps /\ S_received.REFCOERCIONS = eps /\ S_received.PARAMETERBACKINGS = eps']
    if case['weak_receive']:
        result += ['pvalue_caller = PSTRING_CARRIER (REQUEST_STRING n_string) ($ptascii("17"))',
            '$string_carrier_valid(S_receive, pvalue_caller)',
            '$string_carrier_valid(S_pre, pvalue_caller)',
            'S_received.STRINGDATA = S_receive.STRINGDATA']
    else:
        result += ['pvalue_caller = pvalue_original']
    return result


def completed(case):
    lines = prior.completed(case)
    if case['value_kind'] == 'integer':
        lines = [line for line in lines if not line.startswith('$string_carrier_valid(')]
    if case['weak_receive']:
        lines = [line.replace('S_resume.STORE[n_copy] = DEFINED pvalue_original', 'S_resume.STORE[n_copy] = DEFINED pvalue_caller') for line in lines]
    return lines


def controls(case):
    lines = [line for line in string_prior.controls(case) if not line.startswith('$typed_conversion_at(')]
    adapted = dict(case, return_null_first=False, formal_null_first=False)
    for line in union_prior.controls(adapted):
        if any(branches(order) in line for order in (['callable', 'int'], ['int', 'callable'])):
            lines.append(line.replace(' metadata_return', ' metadata_return_first'))
    for normalized in (branches(['callable', 'int']), branches(['int', 'callable'])):
        for strict in ('false', 'true'):
            lines += ['$typed_conversion_at(S_return, ' + normalized + ', pvalue_original, ' + strict + ') = TYPEVALUE pvalue_original',
                '$typed_conversion_at(S_return, ' + normalized + ', PNULL, ' + strict + ') = TYPEREJECT']
            for field in ('CALLABLES', 'FUNCTIONS', 'CLASSES'):
                lines += ['$typed_conversion_at(S_return[.' + field + ' = eps], ' + normalized + ', PINT 17, ' + strict + ') = TYPEVALUE (PINT 17)']
            for value in ('PSTRING ($ptascii("17"))', 'PBOOL true', 'PFLOAT $float_of_int(2)'):
                lines += ['$typed_conversion_at(S_return, ' + normalized + ', ' + value + ', ' + strict + ') = ' + ('TYPEREJECT' if strict == 'true' else 'TYPEINTEGER (' + value + ')')]
            lines += ['$typed_conversion_at(S_return, ' + normalized + ', PSTRING ($ptascii("notRegistered86")), ' + strict + ') = TYPEREJECT']
            if case['value_kind'] == 'callable':
                for field in ('CALLABLES', 'FUNCTIONS'):
                    lines += ['$typed_conversion_at(S_return[.' + field + ' = eps], ' + normalized + ', pvalue_original, ' + strict + ') = TYPEREJECT']
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
    assert set(rows) == {case['id'] for case in cases} and len(cases) == 3
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    paths = [Path(__file__), Path(prior.__file__), Path(union_prior.__file__), Path(string_prior.__file__), CATALOGUE, provenance]
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
    print('cv-int-callable-front' if args.front else 'cv-int-callable-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
