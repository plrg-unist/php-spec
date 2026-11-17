#!/usr/bin/env python3
"""Check exact builtin/iterable required formals and existing private Notice cells."""
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
import cv_builtin_union_iterable_return_producer_reference_notice_state as prior

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_builtin_union_iterable_formal_producer_reference_notice_cases.json')
PREFIX, branches, nodes, raw = prior.PREFIX, prior.branches, prior.nodes, prior.raw
single, multi = prior.single, prior.multi
old_bool_review, old_string, old_string_review = prior.old_bool_review, prior.old_string, prior.old_string_review
FOLD = prior.FOLD


def formal_proof(case):
    members = case['formal_members']
    atoms = ['NIdentifier (BYTES text_formal' + str(index) + ') metadata_formal' + str(index) for index in range(len(members))]
    shape = 'NUnionType (SEQUENCE ([' + ', '.join(atoms) + '])) metadata_formal_union'
    lines = ['phpType17 = NParam (SEQUENCE eps) (INTEGER 0) (' + shape + ') (BOOLEAN ' + str(case['formal_byref']).lower() + ') (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter']
    lines += ['$ptlc($base64(text_formal' + str(index) + ')) = $ptascii(' + json.dumps(kind) + ')' for index, kind in enumerate(members)]
    return lines


def reached(case, front):
    lines = []
    for line in prior.reached(case, front):
        if line.startswith('phpType17 = NParam '):
            lines += formal_proof(case)
        elif front and line.startswith('$reference_notice_producer_arguments(') and '.RETURNS = eps' in line:
            lines.append('~' + line)
        elif line.startswith('psparam.TYPE = '):
            lines.append('psparam.TYPE = ' + branches(case['formal_members']))
        elif not line.startswith('$ptlc($base64(text_formal))'):
            lines.append(line)
    return lines


def completed(case):
    return prior.completed(case)


def controls(case):
    lines = prior.controls(case)
    if case.get('priority_control'):
        return lines
    signature = 'pfunction_producer.SIGNATURE'
    ref = str(case['formal_byref']).lower()
    def proof(shape, members, update=''):
        parameter = 'NParam (SEQUENCE eps) (INTEGER 0) (' + shape + ') (BOOLEAN ' + ref + ') (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter'
        selected = 'psparam[.TYPE = ' + branches(members) + ']' + update
        params, raw_params = [selected], [parameter]
        if case['cv_arity'] > 1:
            params.insert(1 - case['formal_index'], 'psparam_other')
            raw_params.insert(1 - case['formal_index'], 'phpType17_other')
        return '$reference_notice_producer_arguments(phpType6_producer, SEQUENCE ([' + ', '.join(raw_params) + ']), ' + signature + '[.PARAMETERS = [' + ', '.join(params) + ']][.RETURNS = eps])'
    valid = [['iterable', 'int'], ['float', 'iterable'], ['iterable', 'bool'], ['string', 'iterable'],
        ['iterable', 'object'], ['object', 'iterable'], ['iterable', 'callable'], ['callable', 'iterable'],
        ['iterable', 'int', 'float'], ['null', 'iterable'], ['iterable', 'null']]
    valid += [['iterable', 'object', 'callable', 'int', 'float', boolean, 'string', 'null'] for boolean in ('bool', 'false', 'true')]
    for members in valid:
        lines += [proof(raw(members), members), FOLD + '(' + nodes(members) + ', ' + branches(members) + ', eps)']
    invalid = [['iterable', 'array'], ['array', 'iterable', 'string'], ['iterable', 'iterable'],
        ['iterable', 'int', 'int'], ['iterable', 'bool', 'false'], ['iterable', 'false', 'true'],
        ['iterable', 'mixed'], ['iterable', 'void'], ['iterable', 'never'], ['iterable', 'class']]
    for members in invalid:
        lines += ['~' + proof(raw(members), members), '~' + FOLD + '(' + nodes(members) + ', ' + branches(members) + ', eps)']
    for members in (['object', 'callable'], ['int', 'float']):
        lines.append('~' + FOLD + '(' + nodes(members) + ', ' + branches(members) + ', eps)')
    lines.append('~' + proof(raw(['iterable']), ['iterable']))
    members = case['formal_members']
    for different in (list(reversed(members)), members[:-1], members + ['null']):
        lines.append('~' + proof(raw(members), different))
    for tag in ('NName', 'NNameRelative', 'NNameFullyQualified'):
        lines.append('~' + proof(raw(members).replace('NIdentifier', tag), members))
    normal = proof(raw(members), members)
    for edit in ('.BYREF = ' + str(not case['formal_byref']).lower(), '.REQUIRED = false', '.VARIADIC = true', '.DEFAULT = PSDEFAULTUNSUPPORTED "forged builtin iterable formal default"'):
        lines.append('~' + proof(raw(members), members, '[' + edit + ']'))
    for before, after in (('NParam (SEQUENCE eps)', 'NParam (SEQUENCE ([NAttributeGroup (SEQUENCE eps) metadata_parameter]))'),
            ('NParam (SEQUENCE eps) (INTEGER 0)', 'NParam (SEQUENCE eps) (INTEGER 1)'),
            ('(BOOLEAN ' + ref + ') (BOOLEAN false) phpType10', '(BOOLEAN ' + str(not case['formal_byref']).lower() + ') (BOOLEAN false) phpType10'),
            ('(BOOLEAN ' + ref + ') (BOOLEAN false) phpType10', '(BOOLEAN ' + ref + ') (BOOLEAN true) phpType10')):
        lines.append('~' + normal.replace(before, after, 1))
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
    paths = [Path(__file__), Path(prior.__file__), Path(prior.prior.__file__), Path(single.__file__), Path(single.prior.__file__), Path(multi.__file__), Path(multi.prior.__file__), Path(multi.prior.prior.__file__), Path(multi.prior.prior.prior.__file__), CATALOGUE, provenance]
    paths += [Path(history.__file__) for history in (old_bool_review, old_string, old_string_review)]
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
    print('cv-builtin-union-iterable-formal-front' if args.front else 'cv-builtin-union-iterable-formal-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
