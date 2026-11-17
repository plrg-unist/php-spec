#!/usr/bin/env python3
"""Independently check required one-CV iterable formals and bounded Notice operands."""
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
import singleton_cv_nullable_iterable_return_producer_reference_notice_review_state as prior

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('singleton_cv_iterable_formal_producer_reference_notice_review_cases.json')
PREFIX = prior.PREFIX
ITERABLE = prior.ITERABLE


def reached(case, front):
    if case.get('priority_control'):
        return prior.reached(case, front)
    argument = '$reference_notice_producer_arguments(phpType6_producer, phpType16, pfunction_producer.SIGNATURE[.RETURNS = eps])'
    lines = []
    for line in prior.reached(case, front):
        if line == argument:
            line = ('~' if front else '') + line
        if line == 'S_pre.STORE[n_copy] = DEFINED (PBOOL false)':
            line = 'S_pre.STORE[n_copy] = DEFINED (POBJECT n_generator)' if case['caller_kind'] == 'generator' else 'S_pre.STORE[n_copy] = DEFINED (PARRAY n_copy_root)'
        if line == 'S_pre.STORE[n_caller] = DEFINED (PARRAY n_root)' and case['caller_kind'] == 'generator':
            line = 'S_pre.STORE[n_caller] = DEFINED PNULL'
        lines.append(line)
    lines += ['phpType17 = NParam (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_formal) metadata_formal) (BOOLEAN b_ref) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter',
        '$ptlc($base64(text_formal)) = $ptascii("iterable")',
        'psparam.BYREF = b_ref',
        'psparam.TYPE = ' + ITERABLE]
    if case['caller_kind'] == 'generator':
        lines += ['S_return.STORE[n_formal] = DEFINED PNULL',
            '$generator_object(S_pre, n_generator)',
            '$lookup(S_pre.ENV, $ptascii("kept")) = (n_kept)',
            'S_pre.STORE[n_kept] = DEFINED (POBJECT n_generator)',
            'n_copy =/= n_kept',
            '$typed_conversion_at(S_pre, ' + ITERABLE + ', POBJECT n_generator, false) = TYPEVALUE (POBJECT n_generator)',
            '$typed_conversion_at(S_pre, ' + ITERABLE + ', POBJECT n_generator, true) = TYPEVALUE (POBJECT n_generator)']
    else:
        lines += ['n_copy_root =/= n_root',
            '$entry_lookup(S_pre.ARRAYS[n_copy_root].ITEMS, KSTRING ($ptascii("n"))) = (DIRECT (PINT 3))']
    return lines


def completed(case):
    lines = prior.completed(case)
    if case.get('priority_control'):
        return lines
    lines += ['$propref_at(S_full.PROPREFS, n_caller) = eps',
        '$reference_coercion_at(S_full.REFCOERCIONS, n_caller) = eps']
    if case['caller_kind'] == 'generator':
        lines += ['S_full.STORE[n_copy] = DEFINED (POBJECT n_generator)',
            'S_full.STORE[n_kept] = DEFINED (POBJECT n_generator)',
            '$generator_object(S_full, n_generator)',
            'S_full.STORE[n_caller] = DEFINED (PARRAY n_caller_array)',
            '$entry_lookup(S_full.ARRAYS[n_caller_array].ITEMS, KSTRING ($ptascii("n"))) = (DIRECT (PINT 23))',
            '$lookup(S_full.ENV, $ptascii("alias")) = (n_caller)']
    else:
        lines += ['S_full.STORE[n_copy] = DEFINED (PARRAY n_copy_root)',
            '$entry_lookup(S_full.ARRAYS[n_copy_root].ITEMS, KSTRING ($ptascii("n"))) = (DIRECT (PINT 3))']
    return lines


def controls(case):
    if case.get('priority_control'):
        return ['$typed_conversion_at(S_full, ' + ITERABLE + ', pvalue_copy, false) = TYPEREJECT',
            '$typed_conversion_at(S_full, ' + ITERABLE + ', pvalue_copy, true) = TYPEREJECT']
    lines = []
    for line in prior.controls(case):
        if line.startswith('$reference_notice_producer_arguments(SEQUENCE ([phpType7_actual, phpType7_actual])'):
            line = '~' + line
        lines.append(line)
    header = '$reference_notice_producer_header(phpType6_producer, '
    signature = 'pfunction_producer.SIGNATURE'
    raw = '(NIdentifier (BYTES text_formal) metadata_formal)'
    for replacement in ('(NName (BYTES text_formal) metadata_formal)',
            '(NNameFullyQualified (BYTES text_formal) metadata_formal)',
            '(NNullableType ' + raw + ' metadata_formal)'):
        lines += ['~' + header + 'SEQUENCE ([NParam (SEQUENCE eps) (INTEGER 0) ' + replacement + ' (BOOLEAN b_ref) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter]), phpType18, ' + signature + ')']
    lines += ['~' + header + 'phpType16, phpType18, ' + signature + '[.PARAMETERS = [psparam[.TYPE = ' + prior.branches(['array']) + ']]])',
        header + 'SEQUENCE ([NParam (SEQUENCE eps) (INTEGER 0) (NNullableType ' + raw + ' metadata_formal) (BOOLEAN b_ref) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter]), phpType18, ' + signature + '[.PARAMETERS = [psparam[.TYPE = ' + prior.branches(['iterable', 'null']) + ']]])',
        '~$reference_notice_producer_arguments(phpType6_producer, phpType16, ' + signature + '[.PARAMETERS = eps][.RETURNS = eps])']
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
            specs.append('dec $sr_case' + str(index) + '() : bool\ndef $sr_case' + str(index) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in current + extra))
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
    fixture.write_text(prefix + '\n'.join(specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $sr_case' + str(index) + '()\n' for index in range(len(cases))))
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
