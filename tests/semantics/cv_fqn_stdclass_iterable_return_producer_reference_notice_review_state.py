#!/usr/bin/env python3
"""Check exact FQN stdClass/iterable returns, coercion priority and private-cell ownership."""
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
import cv_builtin_union_iterable_return_producer_reference_notice_review_state as prior

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_fqn_stdclass_iterable_return_producer_reference_notice_review_cases.json')
PREFIX, single, multi, floating = prior.PREFIX, prior.single, prior.multi, prior.floating
FOLD = '$reference_notice_producer_stdclass_iterable_return_union_members'


def branches(members, class_name):
    return prior.branches(members).replace('PTBUILTIN "class"', 'PTCLASS ($ptascii(' + json.dumps(class_name) + '))')


def nodes(members, class_name, class_tag='NNameFullyQualified', builtin_tag='NIdentifier'):
    atoms = []
    for kind in members:
        tag, name = (class_tag, class_name) if kind == 'class' else (builtin_tag, kind)
        atoms.append(tag + ' (BYTES ' + json.dumps(base64.b64encode(name.encode()).decode()) + ') metadata_union')
    return '[' + ', '.join(atoms) + ']'


def raw(members, class_name, class_tag='NNameFullyQualified', builtin_tag='NIdentifier'):
    return 'NUnionType (SEQUENCE (' + nodes(members, class_name, class_tag, builtin_tag) + ')) metadata_union'


def indexed_return(lines, case):
    result = []
    for line in lines:
        if line.startswith('phpType18 = NUnionType '):
            atoms, facts = [], []
            for index, kind in enumerate(case['return_members']):
                tag = 'NNameFullyQualified' if kind == 'class' else 'NIdentifier'
                field = 'text_return_' + str(index)
                atoms.append(tag + ' (BYTES ' + field + ') metadata_return_' + str(index))
                facts.append(('$base64(' + field + ') = $ptascii(' + json.dumps(case['class_return']) + ')') if kind == 'class' else
                    '$ptlc($base64(' + field + ')) = $ptascii(' + json.dumps(kind) + ')')
            result += ['phpType18 = NUnionType (SEQUENCE ([' + ', '.join(atoms) + '])) metadata_union'] + facts
        elif not line.startswith(('$ptlc($base64(text_first))', '$ptlc($base64(text_second))', '$ptlc($base64(text_return_')):
            result.append(line)
    return result


def reached(case, front):
    if case.get('priority_control'):
        lines = single.reached(case, front)
        lines = [line.replace('$ptascii("17")', '$ptascii("17.5")') for line in lines]
        lines += ['S_return.STORE[n_formal] = DEFINED pvalue_string', 'n_formal = n_caller']
    else:
        lines = prior.reached(case, front)
    return [line.replace('PTBUILTIN "class"', 'PTCLASS ($ptascii(' + json.dumps(case['class_return']) + '))')
        for line in indexed_return(lines, case)]


def completed(case):
    return [] if case.get('priority_control') else prior.completed(case)


def controls(case):
    if case.get('priority_control'):
        return ['$typed_conversion_at(S_resolved, ' + branches(case['return_members'], case['class_return']) +
            ', pvalue_string, false) = TYPEVALUE (PFLOAT 4625619029774565376)']
    lines = prior.controls(case)
    lines = [line.replace('PTBUILTIN "class"', 'PTCLASS ($ptascii(' + json.dumps(case['class_return']) + '))') for line in lines]
    if case['value_kind'] != 'object':
        return lines
    name = case['class_return']
    header = '$reference_notice_producer_header(phpType6_producer, phpType16, '
    signature = 'pfunction_producer.SIGNATURE'
    valid = [['class', 'iterable'], ['iterable', 'class'], ['iterable', 'float', 'class', 'int'],
        ['null', 'class', 'string', 'iterable', 'int', 'float', 'callable', 'true']]
    valid += [['callable', 'int', 'class', 'iterable', 'float', boolean, 'string', 'null'] for boolean in ('bool', 'false', 'true')]
    invalid = [['class', 'iterable', 'array'], ['object', 'class', 'iterable'], ['class', 'class', 'iterable'],
        ['class', 'iterable', 'iterable'], ['class', 'iterable', 'int', 'int'],
        ['class', 'iterable', 'bool', 'false'], ['class', 'iterable', 'false', 'true'],
        ['class', 'iterable', 'null', 'null'], ['class', 'iterable', 'mixed'], ['class', 'iterable', 'void'],
        ['class', 'iterable', 'never'], ['class', 'iterable', 'resource'],
        ['class', 'iterable', 'int', 'float', 'bool', 'string', 'null', 'callable', 'true']]
    for members in valid + invalid:
        mark = '' if members in valid else '~'
        raw_members, normalized = nodes(members, name), branches(members, name)
        lines += [mark + FOLD + '(' + raw_members + ', ' + normalized + ', false, eps)',
            mark + header + raw(members, name) + ', ' + signature + '[.RETURNS = ' + normalized + '])']
    for members in (['iterable', 'int'], ['class', 'int'], ['class'], ['iterable']):
        lines.append('~' + FOLD + '(' + nodes(members, name) + ', ' + branches(members, name) + ', false, eps)')
    members = ['class', 'iterable']
    lines += ['~' + FOLD + '(eps, eps, false, eps)',
        '~' + FOLD + '(' + nodes(members, name) + ', ' + branches(members, name.upper()) + ', false, eps)',
        '~' + FOLD + '(' + nodes(['class', 'iterable', 'int'], name) + ', ' + branches(members, name) + ', false, eps)',
        '~' + FOLD + '(' + nodes(members, name) + ', ' + branches(['class', 'iterable', 'int'], name) + ', false, eps)',
        '~' + FOLD + '(' + nodes(members, name) + ', ' + branches(members[::-1], name) + ', false, eps)']
    for tag in ('NName', 'NNameRelative', 'NIdentifier'):
        lines.append('~' + header + raw(members, name, class_tag=tag) + ', ' + signature + '[.RETURNS = ' + branches(members, name) + '])')
    for tag in ('NName', 'NNameFullyQualified'):
        lines.append('~' + header + raw(members, name, builtin_tag=tag) + ', ' + signature + '[.RETURNS = ' + branches(members, name) + '])')
    lines += ['~' + header + raw(members, name) + ', ' + signature + '[.RETURNS = ' + branches(members, name.upper()) + '])',
        '~' + header + raw(members, 'OtherClass') + ', ' + signature + '[.RETURNS = ' + branches(members, 'OtherClass') + '])']
    formal = 'NParam (SEQUENCE eps) (INTEGER 0) (' + raw(members, name) + ') (BOOLEAN false) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter'
    lines.append('$reference_notice_producer_arguments(phpType6_producer, SEQUENCE ([' + formal + ']), ' + signature +
        '[.RETURNS = eps][.PARAMETERS = [psparam[.TYPE = ' + branches(members, name) + ']]])')
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
    paths = [Path(__file__), Path(prior.__file__), Path(single.__file__), Path(multi.__file__), Path(single.base.__file__), Path(floating.__file__), CATALOGUE, provenance]
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
    print('cv-fqn-stdclass-iterable-return-front' if args.front else 'cv-fqn-stdclass-iterable-return-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
