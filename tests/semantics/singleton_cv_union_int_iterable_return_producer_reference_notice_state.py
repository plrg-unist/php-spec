#!/usr/bin/env python3
"""Check one required ordinary CV, exact ordered-int iterable returns and private cells."""
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
CATALOGUE = Path(__file__).with_name('singleton_cv_union_int_iterable_return_producer_reference_notice_cases.json')
PREFIX, ITERABLE = prior.PREFIX, prior.ITERABLE
RAW = 'NIdentifier (BYTES text_return) metadata_return'


def branches(members):
    return '[' + ', '.join('(PTBRANCH ([PTBUILTIN ' + json.dumps(kind) + ']))' for kind in members) + ']'


def raw_union(members):
    nodes = [RAW if kind == 'iterable' else 'NIdentifier (BYTES text_return_int) metadata_return_int' for kind in members]
    return 'NUnionType (SEQUENCE ([' + ', '.join(nodes) + '])) metadata_return_union'


def return_proof(case):
    return ['phpType18 = ' + raw_union(case['return_members']),
        '$ptlc($base64(text_return)) = $ptascii("iterable")',
        '$ptlc($base64(text_return_int)) = $ptascii("int")']


def reached(case, front):
    lines = []
    for line in prior.reached(case, front):
        line = line.replace(ITERABLE, branches(case['return_members']))
        if line == 'phpType18 = ' + RAW:
            lines += return_proof(case)
            continue
        if line == '$ptlc($base64(text_return)) = $ptascii("iterable")':
            continue
        if case.get('priority_bad_return'):
            if line == 'S_resolved.RESULT = KNOWN (PINT 17)':
                lines += ['S_resolved.RESULT = KNOWN pvalue_bad_return',
                    '$string_bytes(pvalue_bad_return) = ($ptascii("bad"))']
                continue
            if line.startswith('$typed_conversion_at(S_return, '):
                line = line.replace('PINT 17', 'pvalue_bad_return')
        lines.append(line)
    if case.get('priority_control'):
        lines += ['$origin_node(S_return.SOURCES, pfunction_producer.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) phpType11 phpType16 phpType18 phpType23 metadata_function)',
            'phpType16 = SEQUENCE ([phpType17])'] + return_proof(case)
    raw = 'ABSENT' if case['formal_kind'] is None else '(NIdentifier (BYTES text_formal) metadata_formal)'
    ref = str(case['formal_byref']).lower()
    lines += ['phpType17 = NParam (SEQUENCE eps) (INTEGER 0) ' + raw + ' (BOOLEAN ' + ref + ') (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter',
        'psparam.NAME = $ptascii(' + json.dumps(case['formal_name']) + ')',
        'psparam.TYPE = ' + ('eps' if case['formal_kind'] is None else branches([case['formal_kind']])),
        'psparam.BYREF = ' + ref + r' /\ psparam.REQUIRED /\ ~psparam.VARIADIC /\ psparam.DEFAULT = PSNONE']
    if case['formal_kind'] is not None:
        lines.append('$ptlc($base64(text_formal)) = $ptascii(' + json.dumps(case['formal_kind']) + ')')
    return lines


def completed(case):
    return prior.completed(case)


def controls(case):
    lines = prior.controls(case)
    if case.get('priority_control'):
        return lines
    header = '$reference_notice_producer_header(phpType6_producer, phpType16, '
    signature = 'pfunction_producer.SIGNATURE'
    bare_upper = header + 'NIdentifier (BYTES "SVRFUkFCTEU=") metadata_return, ' + signature + ')'
    assert lines.count(bare_upper) == 1
    lines[lines.index(bare_upper)] = bare_upper[:-1] + '[.RETURNS = ' + ITERABLE + '])'
    lines += ['~' + header + 'phpType18, ' + signature + '[.RETURNS = ' + branches(list(reversed(case['return_members']))) + '])',
        '~' + header + 'phpType18, ' + signature + '[.RETURNS = ' + ITERABLE + '])',
        '~' + header + 'phpType18, ' + signature + '[.PARAMETERS = [psparam[.DEFAULT = PSDEFAULTUNSUPPORTED "forged singleton iterable return default"]]])']
    for leaf in ('NName', 'NNameFullyQualified'):
        nodes = [(leaf if kind == 'iterable' else 'NIdentifier') + ' (BYTES ' + json.dumps(base64.b64encode(kind.encode()).decode()) + ') metadata_return_int' for kind in case['return_members']]
        lines.append('~' + header + 'NUnionType (SEQUENCE ([' + ', '.join(nodes) + '])) metadata_return_union, ' + signature + ')')
    for members in (['iterable', 'int'], ['int', 'iterable'], ['iterable', 'float'], ['float', 'iterable'],
            ['iterable', 'bool'], ['bool', 'iterable'], ['iterable', 'array'], ['array', 'iterable'],
            ['iterable', 'iterable'], ['int', 'int'], ['iterable', 'int', 'null']):
        nodes = ['NIdentifier (BYTES ' + json.dumps(base64.b64encode(kind.encode()).decode()) + ') metadata_return_int' for kind in members]
        raw = 'NUnionType (SEQUENCE ([' + ', '.join(nodes) + '])) metadata_return_union'
        polarity = '' if members in (['iterable', 'int'], ['int', 'iterable']) else '~'
        lines.append(polarity + header + raw + ', ' + signature + '[.RETURNS = ' + branches(members) + '])')
    if case['formal_kind'] == 'array':
        iterable = 'NIdentifier (BYTES "aXRlcmFibGU=") metadata_parameter'
        null = 'NIdentifier (BYTES "bnVsbA==") metadata_parameter'
        forms = [(iterable, ['iterable']),
            ('NNullableType (' + iterable + ') metadata_parameter', ['iterable', 'null']),
            ('NUnionType (SEQUENCE ([' + iterable + ', ' + null + '])) metadata_parameter', ['iterable', 'null']),
            ('NUnionType (SEQUENCE ([' + null + ', ' + iterable + '])) metadata_parameter', ['null', 'iterable'])]
        for raw_type, members in forms:
            parameter = 'NParam (SEQUENCE eps) (INTEGER 0) (' + raw_type + ') (BOOLEAN true) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter'
            lines.append('$reference_notice_producer_arguments(phpType6_producer, SEQUENCE ([' + parameter + ']), ' + signature + '[.PARAMETERS = [psparam[.TYPE = ' + branches(members) + ']]][.RETURNS = eps])')
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
    print('singleton-cv-union-int-iterable-return-front' if args.front else 'singleton-cv-union-int-iterable-return-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
