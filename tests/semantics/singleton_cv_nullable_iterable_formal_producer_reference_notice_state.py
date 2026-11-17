#!/usr/bin/env python3
"""Reach nullable/ordered-null singleton iterable formals before private Notice cells."""
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
import singleton_cv_iterable_formal_producer_reference_notice_state as prior

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('singleton_cv_nullable_iterable_formal_producer_reference_notice_cases.json')
PREFIX = prior.PREFIX
ITERABLE = prior.ITERABLE
branches = prior.prior.branches


def formal_raw(case):
    iterable = '(NIdentifier (BYTES text_formal) metadata_formal)'
    if case['formal_shape'] == 'nullable':
        return '(NNullableType ' + iterable + ' metadata_formal_nullable)'
    nodes = [iterable if kind == 'iterable' else '(NIdentifier (BYTES text_formal_null) metadata_formal_null)' for kind in case['formal_members']]
    return '(NUnionType (SEQUENCE ([' + ', '.join(nodes) + '])) metadata_formal_union)'


def reached(case, front):
    formal = branches(case['formal_members'])
    lines = []
    for line in prior.reached(case, front):
        if line.startswith('phpType17 = NParam '):
            line = line.replace('(NIdentifier (BYTES text_formal) metadata_formal)', formal_raw(case))
            lines.append(line)
            if case['formal_shape'] == 'union':
                lines.append('$ptlc($base64(text_formal_null)) = $ptascii("null")')
            continue
        if line == 'psparam.TYPE = ' + ITERABLE:
            line = 'psparam.TYPE = ' + formal
        line = line.replace('$typed_conversion_at(S_return, ' + ITERABLE + ', ', '$typed_conversion_at(S_return, ' + formal + ', ')
        line = line.replace('$typed_conversion_at(S_pre, ' + ITERABLE + ', ', '$typed_conversion_at(S_pre, ' + formal + ', ')
        lines.append(line)
    if case.get('receive_priority_control'):
        lines += ['$call_target(S_full, $ptascii(' + json.dumps(case['namespace'] + '\\make') + '), eps) = (pfunction_producer)',
            'pfunction_producer.SIGNATURE.PARAMETERS = [psparam]',
            'psparam.TYPE = ' + formal,
            r'psparam.REQUIRED /\ ~psparam.VARIADIC /\ psparam.DEFAULT = PSNONE']
    elif case['caller_kind'] == 'null':
        lines += ['S_return.STORE[n_formal] = DEFINED PNULL',
            '$typed_conversion_at(S_return, ' + formal + ', PNULL, false) = TYPEVALUE PNULL',
            '$typed_conversion_at(S_return, ' + formal + ', PNULL, true) = TYPEVALUE PNULL',
            'S_pre.STORE[n_caller] = DEFINED PNULL',
            '$lookup(S_pre.ENV, $ptascii("copy")) = (n_copy)',
            '$lookup(S_pre.ENV, $ptascii("kept")) = (n_kept)',
            r'S_pre.STORE[n_copy] = DEFINED PNULL /\ S_pre.STORE[n_kept] = DEFINED PNULL',
            '$propref_at(S_pre.PROPREFS, n_caller) = eps',
            '$reference_coercion_at(S_pre.REFCOERCIONS, n_caller) = eps']
    return lines


def completed(case):
    lines = prior.completed(case)
    if case['caller_kind'] == 'null':
        lines += [r'S_full.STORE[n_copy] = DEFINED PNULL /\ S_full.STORE[n_kept] = DEFINED PNULL',
            'S_full.STORE[n_caller] = DEFINED (PINT 23)',
            '$propref_at(S_full.PROPREFS, n_caller) = eps',
            '$reference_coercion_at(S_full.REFCOERCIONS, n_caller) = eps']
    return lines


def controls(case):
    formal = branches(case['formal_members'])
    if case.get('receive_priority_control'):
        return ['$typed_conversion_at(S_full, ' + formal + ', PINT 17, true) = TYPEREJECT',
            '$typed_conversion_at(S_full, ' + formal + ', PINT 17, false) = TYPEREJECT']
    header = '$reference_notice_producer_header(phpType6_producer, '
    raw = '(NIdentifier (BYTES text_formal) metadata_formal)'
    lines = []
    for line in prior.controls(case):
        if case['formal_shape'] == 'union' and line.startswith('$reference_notice_producer_arguments(SEQUENCE ([phpType7_actual, phpType7_actual])'):
            line = '~' + line
        elif line.startswith('~' + header) and '(NNullableType ' + raw + ' metadata_formal)' in line and case['formal_members'] == ['iterable', 'null']:
            line = line[1:]
        lines.append(line)
    if case['formal_shape'] == 'nullable':
        lines += ['text_formal_null = "bnVsbA=="', 'metadata_formal_null = metadata_formal', 'metadata_formal_union = metadata_formal_nullable']
    else:
        lines += ['metadata_formal_nullable = metadata_formal_union']
    signature = 'pfunction_producer.SIGNATURE'
    for shape, members in (('nullable', ['iterable', 'null']), ('union', ['iterable', 'null']), ('union', ['null', 'iterable'])):
        parameter = 'NParam (SEQUENCE eps) (INTEGER 0) ' + formal_raw(dict(formal_shape=shape, formal_members=members)) + ' (BOOLEAN b_ref) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter'
        lines += [header + 'SEQUENCE ([' + parameter + ']), phpType18, ' + signature + '[.PARAMETERS = [psparam[.TYPE = ' + branches(members) + ']]])']
    parameter = 'NParam (SEQUENCE eps) (INTEGER 0) ' + raw + ' (BOOLEAN b_ref) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter'
    lines += ['~' + header + 'SEQUENCE ([' + parameter + ']), phpType18, ' + signature + ')',
        '~' + header + 'phpType16, phpType18, ' + signature + '[.PARAMETERS = [psparam[.TYPE = ' + branches(list(reversed(case['formal_members']))) + ']]])']
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
    paths = [Path(__file__), Path(prior.__file__), Path(prior.prior.__file__), Path(prior.prior.prior.__file__), CATALOGUE, provenance]
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
    print('singleton-cv-nullable-iterable-formal-front' if args.front else 'singleton-cv-nullable-iterable-formal-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
