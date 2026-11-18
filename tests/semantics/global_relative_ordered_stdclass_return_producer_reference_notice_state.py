#!/usr/bin/env python3
"""Ground flat relative RETURN unions, ordered coercion and private Notice ownership."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import global_plain_ordered_stdclass_return_producer_reference_notice_state as ordered
import global_relative_union_int_stdclass_return_producer_reference_notice_state as relative_int
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('global_relative_ordered_stdclass_return_producer_reference_notice_cases.json')
PREFIX = ordered.PREFIX


def front_lines(case, front):
    lines = []
    for line in ordered.reached(case, front):
        line = line.replace('pfunction_producer.ENV.CLASSES = eps', 'pfunction_producer.ENV.CLASSES = [($ptascii("stdclass"), $ptascii(' + json.dumps(case['import_target']) + '))]')
        if line.startswith('phpType18 = '):
            line = line.replace('NName ', 'NNameRelative ')
        lines.append(line)
    lines += ['phpType16 = SEQUENCE phpType17_all*',
        'phpType17_all* = ($reference_notice_producer_scoped_parameter_view(pfunction_producer.ENV, phpType17_all))*',
        'phpType18 = NUnionType (SEQUENCE phpType69_members*) metadata_union']
    for index, kind in enumerate(case['return_members']):
        text = 'text_return' + str(index)
        position = 'PTRELATIVE' if kind == 'class' else 'PTPLAIN'
        member = ordered.normalized([kind], 'stdClass')
        lines += ['$ptvalidname($base64(' + text + '), true)',
            '$ptsingle($pltypecontext(pfunction_producer.ENV, PTGLOBAL, PTRETURN, eps, eps, { UNIT 0, PATH eps, FILE eps, LINE 0 }), ' + position + ', $base64(' + text + ')) = PTOK (' + member + ') eps',
            'pfunction_producer.SIGNATURE.RETURNS[' + str(index) + '] = ' + member[1:-1]]
    return lines


def full_lines(case):
    return ordered.completed(case)


def controls(case):
    if case['kind'] == 'object':
        return relative_int.controls(dict(case, int_first=False))
    lines = ['~$error_call_valid(S_notice, perrorcall[.LINE = 9])',
        '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])',
        '~$typed_return_task_valid(S_return, $(z_return + 1))']
    for stage in ('return', 'notice'):
        lines += ['S_zero_' + stage + ' = $drive(S_' + stage + ', 0)',
            'S_zero_' + stage + r'.COMPLETION = BUDGET /\ S_zero_' + stage + '[.COMPLETION = NORMAL] = S_' + stage,
            '$drive($drive(S_zero_' + stage + '[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_' + stage + ', 2)']
    if case['kind'] != 'bool':
        return lines
    env, signature = 'pfunction_producer.ENV', 'pfunction_producer.SIGNATURE'
    raw = lambda members, name='stdClass', tag='NNameRelative': ordered.raw(members, name, tag)
    normalized = lambda members, name='stdClass': ordered.normalized(members, name)
    def proof(expression='phpType18', context=env, returns=None):
        checked = signature + ('[.RETURNS = ' + returns + ']' if returns is not None else '')
        return '$reference_notice_producer_scoped_header(' + context + ', phpType6_producer, phpType16, ' + expression + ', ' + checked + ')'
    def members(expression):
        return expression.removeprefix('NUnionType (SEQUENCE (').removesuffix(')) metadata_function')
    view = '$reference_notice_producer_relative_return_union_view('
    kinds = case['return_members']
    source = members(raw(kinds))
    canonical = members(raw(kinds, tag='NNameFullyQualified'))
    lines += [view + env + ', ' + source + ', false) = (' + canonical + ')',
        view + env + ', ' + source + ', true) = eps',
        proof(context=env + '[.CLASSES = eps]'),
        '~' + proof(context=env + '[.NAMESPACE = $ptascii("Other")]'),
        proof(raw(kinds).replace('metadata_function', 'eps')),
        proof(raw(kinds).replace('"Ym9vbA=="', '"Qm9PbA=="')),
        '$reference_notice_producer_global_union_view(' + source + ', false) = eps',
        '$reference_notice_producer_scoped_return_union_view(' + env + ', ' + source + ', false) = eps']
    for tag in ('NName', 'NNameFullyQualified', 'NIdentifier'):
        lines.append(view + env + ', ' + members(raw(kinds, tag=tag)) + ', false) = eps')
    accepted = [['class', kind] for kind in ('array', 'int', 'float', 'bool', 'string', 'null', 'false', 'true', 'callable', 'iterable')]
    accepted += [items[::-1] for items in accepted]
    accepted += [['float', 'int', 'class'], ['bool', 'class', 'string']]
    for items in accepted:
        lines += [proof(raw(items), returns=normalized(items)),
            '~' + proof(raw(items), returns=normalized(items[::-1])),
            '~' + proof(raw(items), returns=normalized(items, 'STDCLASS'))]
    for items in (['class'], ['class', 'class'], ['class', 'int', 'int'],
            ['class', 'bool', 'true'], ['class', 'false', 'true'], ['class', 'array', 'iterable'],
            ['class', 'object'], ['class', 'mixed'], ['class', 'void'], ['class', 'never']):
        lines.append('~' + proof(raw(items), returns=normalized(items)))
    for name in ('Other', 'Other\\stdClass', '\\stdClass', 'namespace\\stdClass', 'stdClass\x00',
            'STDCLASS', 'sTdClAsS', '', 'int', 'mixed', 'self', 'array', 'callable'):
        lines.append('~' + proof(raw(kinds, name), returns=normalized(kinds)))
    nested = raw(kinds).replace('NIdentifier (BYTES "Ym9vbA==") metadata_function',
        'NIntersectionType (SEQUENCE ([NNameRelative (BYTES "c3RkQ2xhc3M=") metadata_function])) metadata_function')
    lines += ['~' + proof(nested), '~' + proof(raw([])),
        view + env + ', eps, false) = eps', view + env + ', eps, true) = (eps)',
        view + env + ', ' + members(raw(['int', 'float'])) + ', false) = eps',
        view + env + ', ' + members(nested) + ', false) = eps']
    for update in ('.BYREF = true', '.VARIADIC = true', '.REQUIRED = false',
            '.DEFAULT = PSDEFAULTUNSUPPORTED "forged relative ordered return formal"'):
        lines.append('~' + proof().replace(signature + ')', signature + '[.PARAMETERS = [psparam[' + update + ']]])'))
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
    assert set(rows) == {case['id'] for case in cases} and len(cases) == 5
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    paths = [Path(__file__), CATALOGUE, provenance]
    paths += sorted({Path(module.__file__).absolute() for module in sys.modules.values() if getattr(module, '__file__', None) and Path(module.__file__).absolute().parent == ROOT / 'tests/semantics'})
    specs, reached, derived = [], [], []
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
            current = ['S_initial = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'] + front_lines(case, args.front)
            extra = [] if args.front else controls(case)
            if not args.front:
                current += full_lines(case)
            specs.append('dec $src_case' + str(index) + '() : bool\ndef $src_case' + str(index) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in current + extra))
            reached += current
            derived += extra
            paths += [source, Path(row['stdout']), Path(row['stderr'])]
    finally:
        try:
            if frontend:
                frontend.close()
        finally:
            if adapter:
                adapter.close()
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\n'.join(specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $src_case' + str(index) + '()\n' for index in range(len(cases))))
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
    report = dict(revision=revision, inputs=before, inputs_stable=stable, head_stable=head_stable, module_count=len(modules), mode='fixture-SL/cache=false/det=true', front=args.front, selection=[case['id'] for case in cases], conditions=len(reached) + len(derived), reached_conditions=len(reached), derived_conditions=len(derived), source_agreements=0, process=process, passed=passed)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('global-relative-ordered-stdclass-return-front' if args.front else 'global-relative-ordered-stdclass-return-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
