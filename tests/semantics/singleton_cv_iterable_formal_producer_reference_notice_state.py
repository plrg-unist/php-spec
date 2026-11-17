#!/usr/bin/env python3
"""Reach required singleton iterable formals before private Notice-cell creation."""
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
import singleton_cv_nullable_iterable_return_producer_reference_notice_state as prior

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('singleton_cv_iterable_formal_producer_reference_notice_cases.json')
PREFIX = prior.PREFIX
ITERABLE = prior.prior.ITERABLE


def reached(case, front):
    if case.get('receive_priority_control'):
        return ['S_initial.COMPLETION = BUDGET',
            'S_full = $drive(S_initial[.COMPLETION = NORMAL], 10000)',
            r'S_full.COMPLETION = NORMAL /\ S_full.TODO = eps /\ S_full.CURRENT = eps /\ S_full.FRAMES = eps',
            '$ir_output(S_full.EVENTS) = $ptascii(' + json.dumps(case['native_stdout']) + ')',
            '$ir_quiet(S_full.EVENTS)',
            '$lookup(S_full.ENV, $ptascii("source")) = (n_source)',
            '$lookup(S_full.ENV, $ptascii("sourceAlias")) = (n_source)',
            'S_full.STORE[n_source] = DEFINED (PINT 19)',
            '$lookup(S_full.ENV, $ptascii("r")) = (n_r)',
            'S_full.STORE[n_r] = DEFINED pvalue_old',
            '$string_bytes(pvalue_old) = ($ptascii("old"))',
            'S_full.PARAMETERBACKINGS = eps',
            r'$heap_valid($heap_graph(S_full)) /\ $call_descriptors_valid(S_full)']
    argument = '$reference_notice_producer_arguments(phpType6_producer, phpType16, pfunction_producer.SIGNATURE[.RETURNS = eps])'
    lines = []
    for line in prior.reached(case, front):
        if line == argument:
            line = ('~' if front else '') + line
        line = line.replace('$lookup(S_return.ENV, $ptascii("saved"))', '$lookup(S_return.ENV, $ptascii(' + json.dumps(case['formal_name']) + '))')
        lines.append(line)
    lines += ['phpType17 = NParam (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_formal) metadata_formal) (BOOLEAN b_ref) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter',
        '$ptlc($base64(text_formal)) = $ptascii("iterable")',
        'psparam.NAME = $ptascii(' + json.dumps(case['formal_name']) + ')',
        'psparam.TYPE = ' + ITERABLE,
        ('psparam.BYREF' if case['formal_byref'] else '~psparam.BYREF'),
        r'psparam.BYREF = b_ref /\ psparam.REQUIRED /\ ~psparam.VARIADIC /\ psparam.DEFAULT = PSNONE']
    if case['caller_kind'] == 'generator':
        lines += ['S_return.STORE[n_formal] = DEFINED (POBJECT n_generator)',
            '$generator_object(S_return, n_generator)',
            '$typed_conversion_at(S_return, ' + ITERABLE + ', POBJECT n_generator, false) = TYPEVALUE (POBJECT n_generator)',
            '$typed_conversion_at(S_return, ' + ITERABLE + ', POBJECT n_generator, true) = TYPEVALUE (POBJECT n_generator)',
            'S_pre.STORE[n_caller] = DEFINED (POBJECT n_generator)',
            '$lookup(S_pre.ENV, $ptascii("copy")) = (n_copy)',
            '$lookup(S_pre.ENV, $ptascii("kept")) = (n_kept)',
            r'S_pre.STORE[n_copy] = DEFINED (POBJECT n_generator) /\ S_pre.STORE[n_kept] = DEFINED (POBJECT n_generator)',
            '$generator_object(S_pre, n_generator)']
    return lines


def completed(case):
    if case.get('receive_priority_control'):
        return []
    lines = prior.completed(case)
    if case['caller_kind'] == 'generator':
        lines += [r'S_full.STORE[n_copy] = DEFINED (POBJECT n_generator) /\ S_full.STORE[n_kept] = DEFINED (POBJECT n_generator)',
            '$generator_object(S_full, n_generator)',
            'S_full.STORE[n_caller] = DEFINED (PINT 23)']
    return lines


def controls(case):
    if case.get('receive_priority_control'):
        return ['$typed_conversion_at(S_full, ' + ITERABLE + ', PINT 17, true) = TYPEREJECT',
            '$typed_conversion_at(S_full, ' + ITERABLE + ', PINT 17, false) = TYPEREJECT']
    header = '$reference_notice_producer_header(phpType6_producer, '
    signature = 'pfunction_producer.SIGNATURE'
    lines = ['~$typed_return_task_valid(S_return, $(z_return + 1))',
        '~$error_call_valid(S_notice, perrorcall[.LINE = $(perrorcall.LINE + 1)])',
        '~$positional_reference_notice_pending(S_pre[.SOURCES = eps])']
    for stage in ('return', 'notice'):
        lines += ['S_zero_' + stage + ' = $drive(S_' + stage + ', 0)',
            'S_zero_' + stage + r'.COMPLETION = BUDGET /\ S_zero_' + stage + '[.COMPLETION = NORMAL] = S_' + stage,
            '$drive($drive(S_zero_' + stage + '[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_' + stage + ', 2)']
    for edit in ('REQUIRED = false', 'VARIADIC = true', 'BYREF = ' + str(not case['formal_byref']).lower(),
            'DEFAULT = PSDEFAULTUNSUPPORTED "forged iterable formal default"', 'TYPE = [(PTBRANCH ([PTBUILTIN "array"]))]'):
        lines += ['~' + header + 'phpType16, phpType18, ' + signature + '[.PARAMETERS = [psparam[.' + edit + ']]])']
    raw = '(NIdentifier (BYTES text_formal) metadata_formal)'
    for replacement in ('(NName (BYTES text_formal) metadata_formal)',
            '(NNameFullyQualified (BYTES text_formal) metadata_formal)',
            '(NNullableType ' + raw + ' metadata_formal)'):
        lines += ['~' + header + 'SEQUENCE ([NParam (SEQUENCE eps) (INTEGER 0) ' + replacement + ' (BOOLEAN b_ref) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter]), phpType18, ' + signature + ')']
    lines += ['~$reference_notice_producer_arguments(SEQUENCE ([phpType7_actual, phpType7_actual]), SEQUENCE ([phpType17, phpType17]), ' + signature + '[.PARAMETERS = [psparam, psparam]][.RETURNS = eps])',
        '~$reference_notice_producer_header(SEQUENCE ([phpType7_actual, phpType7_actual]), SEQUENCE ([phpType17, phpType17]), phpType18, ' + signature + '[.PARAMETERS = [psparam, psparam]])',
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
    print('singleton-cv-iterable-formal-front' if args.front else 'singleton-cv-iterable-formal-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
