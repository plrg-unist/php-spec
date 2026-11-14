#!/usr/bin/env python3
"""Ground non-null literal-Boolean unions and exact producer ownership."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import error_handler_run as recorder
from recorded_worker import Worker
import cv_literal_bool_return_producer_reference_notice_state as prior
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_nonnull_literal_bool_producer_reference_notice_cases.json')
single, multi, base = prior.single, prior.multi, prior.prior
PREFIX = prior.PREFIX.replace('SingletonFalseReturn71', 'SingletonNonnullFalse74').replace('MultiCvTrueReturn71', 'MultiCvNonnullTrue74')


def union(kind, partner, reverse=False):
    members = [partner, kind] if reverse else [kind, partner]
    return '[' + ', '.join('(PTBRANCH ([PTBUILTIN "' + member + '"]))' for member in members) + ']'


def raw_union(kind, partner, metadata, reverse=False):
    members = [partner, kind] if reverse else [kind, partner]
    return 'NUnionType (SEQUENCE ([' + ', '.join('NIdentifier (BYTES "' + base64.b64encode(member.encode()).decode() + '") ' + metadata for member in members) + '])) ' + metadata


def front_lines(index, case):
    lines = prior.front_lines(index, case)
    if index == 0:
        replacements = {
            'psparam.TYPE = ' + prior.literal('false'): 'psparam.TYPE = ' + union('false', 'int'),
            'pfunction_producer.SIGNATURE.RETURNS = ' + prior.literal('false'):
                'pfunction_producer.SIGNATURE.RETURNS = ' + union('false', 'int', True),
            'phpType17 = NParam (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_type) metadata_type) (BOOLEAN true) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter':
                'phpType17 = NParam (SEQUENCE eps) (INTEGER 0) (NUnionType (SEQUENCE ([NIdentifier (BYTES text_type) metadata_type, NIdentifier (BYTES "aW50") metadata_int_parameter])) metadata_union_parameter) (BOOLEAN true) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter',
            'phpType18 = NIdentifier (BYTES text_return) metadata_return':
                'phpType18 = NUnionType (SEQUENCE ([NIdentifier (BYTES "aW50") metadata_int_return, NIdentifier (BYTES text_return) metadata_return])) metadata_union_return'}
    else:
        replacements = {
            'S_args.STORE[n_y] = DEFINED (PINT 5)': 'S_args.STORE[n_y] = DEFINED (PBOOL false)',
            'psparam_first.TYPE = eps /\\ psparam_last.TYPE = eps':
                'psparam_first.TYPE = ' + union('true', 'string') + r' /\ psparam_last.TYPE = ' + union('false', 'int'),
            'pfunction_producer.SIGNATURE.RETURNS = ' + prior.literal('true') + r' /\ ~pfunction_producer.SIGNATURE.BYREF':
                'pfunction_producer.SIGNATURE.RETURNS = ' + union('true', 'string', True) + r' /\ ~pfunction_producer.SIGNATURE.BYREF',
            'phpType18_return = NIdentifier (BYTES text_return) metadata_type':
                'phpType18_return = NUnionType (SEQUENCE ([NIdentifier (BYTES "c3RyaW5n") metadata_string_return, NIdentifier (BYTES text_return) metadata_type])) metadata_union_return'}
    for old, new in replacements.items():
        assert lines.count(old) == 1, old
        lines = [new if line == old else line for line in lines]
    if index == 1:
        lines += [
            'phpType17_first = NParam (SEQUENCE eps) (INTEGER 0) (NUnionType (SEQUENCE ([NIdentifier (BYTES text_type_first) metadata_type_first, NIdentifier (BYTES "c3RyaW5n") metadata_string_first])) metadata_union_first) (BOOLEAN false) (BOOLEAN false) phpType10_first ABSENT (SEQUENCE eps) metadata_parameter_first',
            'phpType17_last = NParam (SEQUENCE eps) (INTEGER 0) (NUnionType (SEQUENCE ([NIdentifier (BYTES text_type_last) metadata_type_last, NIdentifier (BYTES "aW50") metadata_int_last])) metadata_union_last) (BOOLEAN true) (BOOLEAN false) phpType10_last ABSENT (SEQUENCE eps) metadata_parameter_last',
            '$ptlc($base64(text_type_first)) = $ptascii("true")',
            '$ptlc($base64(text_type_last)) = $ptascii("false")']
    return [('~' + line) if line.startswith('$reference_notice_producer_arguments(') else line for line in lines]


def full_lines(index, case):
    return prior.full_lines(index, case)


def controls(index, case):
    arguments = ('SEQUENCE ([phpType7]), SEQUENCE ([phpType17]), ' if index == 0 else
        'SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), ')
    raw = 'phpType18' if index == 0 else 'phpType18_return'
    meta = 'metadata_return' if index == 0 else 'metadata_type'
    signature = 'pfunction_producer.SIGNATURE'
    header = '$reference_notice_producer_header(' + arguments
    kind, partner = ('false', 'int') if index == 0 else ('true', 'string')
    lines = ['~$typed_return_task_valid(S_return, $(z_return + 1))',
        '~$error_call_valid(S_notice, perrorcall[.LINE = $(perrorcall.LINE + 1)])',
        '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])',
        '~' + header + raw + ', ' + signature + '[.RETURNS = ' + union(kind, partner) + '])',
        '~' + header + raw + ', ' + signature + '[.RETURNS = ' + prior.literal(kind) + '])',
        '~' + header + 'NIdentifier (BYTES "' + base64.b64encode(kind.encode()).decode() + '") ' + meta + ', ' + signature + ')']
    actuals = '([phpType7])' if index == 0 else '([phpType7_first, phpType7_last])'
    raw_tail = '' if index == 0 else ', phpType17_last'
    slot, tail = ('psparam', '') if index == 0 else ('psparam_first', ', psparam_last')
    variable = 'phpType10' if index == 0 else 'phpType10_first'
    parameter_meta = 'metadata_parameter' if index == 0 else 'metadata_parameter_first'
    byref = 'true' if index == 0 else 'false'
    proof = '$reference_notice_producer_arguments(SEQUENCE ' + actuals + ', SEQUENCE (['
    for literal_kind in ('false', 'true'):
        opposite = 'true' if literal_kind == 'false' else 'false'
        for other, exact in [('array', 'PARRAY 0'), ('int', 'PINT 17'), ('float', 'PFLOAT 0'), ('string', 'PSTRING eps')]:
            weak_opposite = {'array': 'TYPEREJECT', 'int': 'TYPEINTEGER (PBOOL ' + opposite + ')',
                'float': 'TYPEVALUE (PFLOAT ' + ('4607182418800017408' if opposite == 'true' else '0') + ')',
                'string': 'TYPESTRING (PBOOL ' + opposite + ')'}[other]
            for reverse in (False, True):
                normalized = union(literal_kind, other, reverse)
                node = raw_union(literal_kind, other, meta, reverse)
                parameter = 'NParam (SEQUENCE eps) (INTEGER 0) (' + node + ') (BOOLEAN ' + byref + ') (BOOLEAN false) ' + variable + ' ABSENT (SEQUENCE eps) ' + parameter_meta
                lines += [header + node + ', ' + signature + '[.RETURNS = ' + normalized + '])',
                    proof + parameter + raw_tail + ']), ' + signature + '[.RETURNS = eps][.PARAMETERS = [' + slot + '[.TYPE = ' + normalized + ']' + tail + ']])',
                    '~' + header + node + ', ' + signature + '[.RETURNS = ' + union(literal_kind, other, not reverse) + '])']
                for strict in ('false', 'true'):
                    for value in ('PBOOL ' + literal_kind, exact):
                        lines += ['$typed_conversion_at(S_return, ' + normalized + ', ' + value + ', ' + strict + ') = TYPEVALUE (' + value + ')']
                    lines += ['$typed_conversion_at(S_return, ' + normalized + ', PNULL, ' + strict + ') = TYPEREJECT']
                lines += ['$typed_conversion_at(S_return, ' + normalized + ', PBOOL ' + opposite + ', true) = TYPEREJECT',
                    '$typed_conversion_at(S_return, ' + normalized + ', PBOOL ' + opposite + ', false) = ' + weak_opposite]
        for other in ('bool', opposite, literal_kind):
            normalized = union(literal_kind, other)
            node = raw_union(literal_kind, other, meta)
            parameter = 'NParam (SEQUENCE eps) (INTEGER 0) (' + node + ') (BOOLEAN ' + byref + ') (BOOLEAN false) ' + variable + ' ABSENT (SEQUENCE eps) ' + parameter_meta
            lines += ['~' + header + node + ', ' + signature + '[.RETURNS = ' + normalized + '])',
                '~' + proof + parameter + raw_tail + ']), ' + signature + '[.RETURNS = eps][.PARAMETERS = [' + slot + '[.TYPE = ' + normalized + ']' + tail + ']])']
    for name in ('return', 'notice'):
        stage = 'S_' + name
        lines += ['S_zero_' + name + ' = $drive(' + stage + ', 0)',
            'S_zero_' + name + '.COMPLETION = BUDGET /\\ S_zero_' + name + '[.COMPLETION = NORMAL] = ' + stage,
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
    paths += [ROOT / path for path in ('tests/semantics/error_handler_run.py', 'tests/semantics/scalar_return_producer_cv_reference_notice_review_state.py', 'tests/semantics/cv_union_literal_bool_producer_reference_notice_state.py', 'tests/semantics/cv_union_null_literal_bool_producer_reference_notice_review_state.py', 'tests/semantics/cv_nullable_literal_bool_producer_reference_notice_review_state.py', 'tests/semantics/cv_literal_bool_return_producer_reference_notice_state.py', 'tests/semantics/cv_literal_bool_formal_producer_reference_notice_state.py', 'tests/semantics/cv_literal_bool_formal_producer_reference_notice_review_state.py', 'tests/semantics/cv_literal_bool_return_producer_reference_notice_review_state.py', 'tests/semantics/profile.json', 'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py', 'tests/validate.py', 'tests/corpus.py', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py')]
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
    print('cv-nonnull-literal-bool-front' if args.front else 'cv-nonnull-literal-bool-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
