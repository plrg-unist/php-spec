#!/usr/bin/env python3
"""Check exact ordered iterable/null multiple-CV formals and private Notice cells."""
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
import multi_cv_nullable_iterable_formal_producer_reference_notice_state as prior

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('multi_cv_union_null_iterable_formal_producer_reference_notice_cases.json')
PREFIX = prior.PREFIX
branches, vector = prior.branches, prior.vector


def raw_union(members, other=False):
    name = 'other_formal' if other else 'formal'
    metadata = 'metadata_other_type' if other else 'metadata_formal'
    nodes = ['NIdentifier (BYTES text_' + name + ('_null' if kind == 'null' else '') + ') ' + (metadata + '_null' if kind == 'null' else metadata) for kind in members]
    return '(NUnionType (SEQUENCE ([' + ', '.join(nodes) + '])) ' + metadata + '_union)'


def reached(case, front):
    formal = branches(case['formal_members'])
    lines = []
    for line in prior.reached(case, front):
        if line.startswith('phpType17 = NParam '):
            line = line.replace(prior.RAW_NULLABLE, raw_union(case['formal_members']))
            lines += [line, '$ptlc($base64(text_formal_null)) = $ptascii("null")']
            continue
        if case['other_kind'] == 'iterable':
            if line.startswith('phpType17_other = NParam '):
                line = line.replace('(NNullableType (NIdentifier (BYTES text_other_formal) metadata_other_type) metadata_other_nullable)', raw_union(case['other_formal_members'], True))
                lines += [line, '$ptlc($base64(text_other_formal_null)) = $ptascii("null")']
                continue
            if line == 'psparam_other.TYPE = ' + prior.NULLABLE:
                lines.append('psparam_other.TYPE = ' + branches(case['other_formal_members']))
                continue
        lines.append(line.replace(prior.NULLABLE, formal))
    return lines


def completed(case):
    return prior.completed(case)


def controls(case):
    formal = branches(case['formal_members'])
    if case.get('receive_priority_control'):
        return ['$typed_conversion_at(S_full, ' + formal + ', PINT 17, ' + strict + ') = TYPEREJECT' for strict in ('false', 'true')]
    lines = prior.prior.controls(case)
    lines.append('metadata_formal_nullable = metadata_formal_union')
    signature = 'pfunction_producer.SIGNATURE'
    arguments = '$reference_notice_producer_arguments(phpType6_producer, '
    def check(raw, members, positive=False):
        parameter = 'NParam (SEQUENCE eps) (INTEGER 0) ' + raw + ' (BOOLEAN b_ref) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter'
        return ('' if positive else '~') + arguments + 'SEQUENCE (' + vector(case, parameter, 'phpType17_other') + '), ' + signature + '[.RETURNS = eps][.PARAMETERS = ' + vector(case, 'psparam[.TYPE = ' + branches(members) + ']', 'psparam_other') + '])'
    for members in (['iterable', 'null'], ['null', 'iterable']):
        lines.append(check(raw_union(members), members, True))
        lines.append(check(raw_union(members), list(reversed(members))))
    lines += [check(prior.RAW, case['formal_members']),
        check(prior.RAW_NULLABLE, ['null', 'iterable'])]
    for partner in ('int', 'array', 'object', 'callable'):
        for members in (['iterable', partner], [partner, 'iterable']):
            nodes = ['NIdentifier (BYTES ' + ('text_formal' if kind == 'iterable' else json.dumps(base64.b64encode(kind.encode()).decode())) + ') metadata_formal' for kind in members]
            raw = '(NUnionType (SEQUENCE ([' + ', '.join(nodes) + '])) metadata_formal)'
            lines.append(check(raw, members))
    lines.append(check(raw_union(['iterable', 'iterable']), ['iterable', 'iterable']))
    lines.append('$reference_notice_producer_arguments(SEQUENCE ([phpType7_actual, phpType7_actual]), SEQUENCE ([phpType17, phpType17]), ' + signature + '[.RETURNS = eps][.PARAMETERS = [psparam, psparam]])')
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
    paths = [Path(__file__), Path(prior.__file__), Path(prior.prior.__file__), Path(prior.prior.prior.__file__), Path(prior.prior.prior.prior.__file__), CATALOGUE, provenance]
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
    print('multi-cv-union-null-iterable-formal-front' if args.front else 'multi-cv-union-null-iterable-formal-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
