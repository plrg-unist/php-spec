#!/usr/bin/env python3
"""Check exact FQN stdClass/iterable RETURN members and existing ordinary-CV private cells."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types
import cv_builtin_union_iterable_return_producer_reference_notice_state as prior

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_fqn_stdclass_iterable_return_producer_reference_notice_cases.json')
PREFIX = prior.PREFIX
single, multi = prior.single, prior.multi
old_bool_review, old_string, old_string_review = prior.old_bool_review, prior.old_string, prior.old_string_review
FOLD = '$reference_notice_producer_stdclass_iterable_return_union_members'


def branches(members, name):
    return '[' + ', '.join('(PTBRANCH ([PTCLASS ($ptascii(' + json.dumps(name) + '))]))' if kind == 'class' else '(PTBRANCH ([PTBUILTIN ' + json.dumps(kind) + ']))' for kind in members) + ']'


def nodes(members, name, class_tag='NNameFullyQualified'):
    atoms = []
    for kind in members:
        text = name if kind == 'class' else kind
        atoms.append((class_tag if kind == 'class' else 'NIdentifier') + ' (BYTES ' + json.dumps(base64.b64encode(text.encode()).decode()) + ') metadata_return_union')
    return '[' + ', '.join(atoms) + ']'


def raw(members, name, class_tag='NNameFullyQualified'):
    return 'NUnionType (SEQUENCE (' + nodes(members, name, class_tag) + ')) metadata_return_union'


def normalized(line, case):
    return line.replace('PTBUILTIN "class"', 'PTCLASS ($ptascii(' + json.dumps(case['class_return']) + '))')


def return_proof(case):
    members = case['return_members']
    atoms = [('NNameFullyQualified' if kind == 'class' else 'NIdentifier') + ' (BYTES text_return' + str(index) + ') metadata_return' + str(index) for index, kind in enumerate(members)]
    lines = ['phpType18 = NUnionType (SEQUENCE ([' + ', '.join(atoms) + '])) metadata_return_union']
    for index, kind in enumerate(members):
        if kind == 'class':
            lines.append('$base64(text_return' + str(index) + ') = $ptascii(' + json.dumps(case['class_return']) + ')')
        else:
            lines.append('$ptlc($base64(text_return' + str(index) + ')) = $ptascii(' + json.dumps(kind) + ')')
    for alias, index in (('return', members.index('iterable')), ('return_literal', next(index for index, kind in enumerate(members) if kind != 'iterable'))):
        lines += ['text_' + alias + ' = text_return' + str(index), 'metadata_' + alias + ' = metadata_return' + str(index)]
    return lines


def reached(case, front):
    lines = []
    for line in prior.reached(case, front):
        if line.startswith('phpType18 = NUnionType '):
            lines += return_proof(case)
            continue
        if re.match(r'\$ptlc\(\$base64\(text_return[0-9]+\)\)', line) or re.match(r'(text|metadata)_(return|return_literal) = ', line):
            continue
        lines.append(normalized(line, case))
    return lines


def completed(case):
    return [normalized(line, case) for line in prior.completed(case)]


def controls(case):
    lines = [normalized(line, case) for line in prior.controls(case)]
    if case.get('priority_control'):
        return lines
    header = '$reference_notice_producer_header(phpType6_producer, phpType16, '
    signature = 'pfunction_producer.SIGNATURE'
    name = case['class_return']
    accepted = [['class', 'iterable'], ['iterable', 'class'], ['class', 'iterable', 'int'], ['class', 'int', 'iterable'], ['class', 'iterable', 'null'], ['float', 'class', 'iterable'],
        ['callable', 'null', 'string', 'bool', 'float', 'int', 'iterable', 'class']]
    accepted += [['class', 'iterable', 'int', 'float', boolean, 'string', 'null', 'callable'] for boolean in ('bool', 'false', 'true')]
    for members in accepted:
        lines += [header + raw(members, name) + ', ' + signature + '[.RETURNS = ' + branches(members, name) + '])',
            FOLD + '(' + nodes(members, name) + ', ' + branches(members, name) + ', false, eps)']
    refused = [['iterable', 'int'], ['class', 'int'], ['class', 'class', 'iterable'], ['class', 'iterable', 'iterable'],
        ['class', 'iterable', 'array'], ['object', 'class', 'iterable'], ['class', 'iterable', 'bool', 'true'],
        ['class', 'iterable', 'false', 'true'], ['class', 'iterable', 'int', 'float', 'bool', 'string', 'null', 'callable', 'false']]
    for members in refused:
        lines.append('~' + FOLD + '(' + nodes(members, name) + ', ' + branches(members, name) + ', false, eps)')
        if 'class' in members and 'iterable' in members:
            lines.append('~' + header + raw(members, name) + ', ' + signature + '[.RETURNS = ' + branches(members, name) + '])')
    for members in (list(reversed(case['return_members'])), case['return_members'][:-1], case['return_members'] + ['null']):
        lines.append('~' + header + 'phpType18, ' + signature + '[.RETURNS = ' + branches(members, name) + '])')
    lines += ['~' + header + 'phpType18, ' + signature + '[.RETURNS = ' + branches(case['return_members'], name.swapcase()) + '])',
        '~' + FOLD + '(' + nodes(['class', 'iterable'], name) + ', ' + branches(['class', 'iterable'], name.swapcase()) + ', false, eps)']
    for tag in ('NName', 'NNameRelative', 'NIdentifier'):
        lines.append('~' + header + raw(case['return_members'], name, tag) + ', ' + signature + ')')
    malformed = nodes(case['return_members'], name).replace('NIdentifier', 'NName', 1)
    lines.append('~' + FOLD + '(' + malformed + ', ' + branches(case['return_members'], name) + ', false, eps)')
    duplicate_class = nodes(['class', 'class', 'iterable'], name).replace(json.dumps(base64.b64encode(name.encode()).decode()), json.dumps(base64.b64encode(name.swapcase().encode()).decode()), 1)
    duplicate_normalized = branches(['class', 'class', 'iterable'], name).replace('PTCLASS ($ptascii(' + json.dumps(name) + '))', 'PTCLASS ($ptascii(' + json.dumps(name.swapcase()) + '))', 1)
    lines += ['~' + FOLD + '(' + duplicate_class + ', ' + duplicate_normalized + ', false, eps)',
        '~' + FOLD + '(' + nodes(['class', 'iterable'], 'OtherClass') + ', ' + branches(['class', 'iterable'], 'OtherClass') + ', false, eps)',
        '~$reference_notice_producer_stdclass_union_members(' + nodes(['class', 'iterable'], name) + ', ' + branches(['class', 'iterable'], name) + ', false, eps)',
        '$reference_notice_producer_stdclass_union_members(' + nodes(['class', 'int'], name) + ', ' + branches(['class', 'int'], name) + ', false, eps)',
        header + raw(['class', 'int'], name) + ', ' + signature + '[.RETURNS = ' + branches(['class', 'int'], name) + '])']
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
    paths = [Path(__file__), Path(prior.__file__), Path(single.__file__), Path(single.prior.__file__), Path(multi.__file__), Path(multi.prior.__file__), Path(multi.prior.prior.__file__), Path(multi.prior.prior.prior.__file__), CATALOGUE, provenance]
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
    print('cv-fqn-stdclass-iterable-return-front' if args.front else 'cv-fqn-stdclass-iterable-return-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
