#!/usr/bin/env python3
"""Ground declaration-resolved ordered RETURN unions and unchanged private Notice cells."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import global_plain_union_null_stdclass_return_producer_reference_notice_state as nulls
import global_plain_ordered_stdclass_return_producer_reference_notice_state as ordered
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('scoped_ordered_stdclass_return_producer_reference_notice_cases.json')
NAMESPACE = 'ScopedOrderedReturn129'


def qualify(line):
    for name in ('make', 'take'):
        line = line.replace('$ptascii(' + json.dumps(name) + ')', '$ptascii(' + json.dumps(NAMESPACE + '\\' + name) + ')')
    return line


PREFIX = qualify(nulls.PREFIX + ordered.PREFIX)


def front_lines(case, front):
    previous = nulls.front_lines(case, front) if case['route'] == 'null' else ordered.reached(case, front)
    lines = []
    alias_variable = 'text_return' if case['route'] == 'null' else 'text_return' + str(case['return_members'].index('class'))
    for line in previous:
        line = line.replace('pfunction_producer.ENV.NAMESPACE = eps', 'pfunction_producer.ENV.NAMESPACE = $ptascii(' + json.dumps(NAMESPACE) + ')')
        line = line.replace('pfunction_producer.ENV.CLASSES = eps', 'pfunction_producer.ENV.CLASSES = [($ptascii("box"), $ptascii("stdClass"))]')
        if line == '$base64(' + alias_variable + ') = $ptascii("stdClass")':
            line = '$base64(' + alias_variable + ') = $ptascii(' + json.dumps(case['return_name']) + ')'
        lines.append(qualify(line))
    lines += ['phpType16 = SEQUENCE phpType17_all*',
        'phpType17_all* = ($reference_notice_producer_scoped_parameter_view(pfunction_producer.ENV, phpType17_all))*',
        'phpType18 = NUnionType (SEQUENCE phpType69_members*) metadata_union',
        '$ptvalidname($base64(' + alias_variable + '), true)',
        '$ptsingle($pltypecontext(pfunction_producer.ENV, PTGLOBAL, PTRETURN, eps, eps, { UNIT 0, PATH eps, FILE eps, LINE 0 }), PTPLAIN, $base64(' + alias_variable + ')) = PTOK (' + nulls.previous.objects.prior.class_type('stdClass') + ') eps']
    return lines


def full_lines(case):
    previous = nulls.completed(case) if case['route'] == 'null' else ordered.completed(case)
    return [qualify(line) for line in previous]


def controls(case):
    env, signature = 'pfunction_producer.ENV', 'pfunction_producer.SIGNATURE'
    members = case['return_members']
    normalized = lambda kinds, name='stdClass': ordered.normalized(kinds, name)
    raw = lambda kinds, name='Box', tag='NName': ordered.raw(kinds, name, tag)
    def proof(expression='phpType18', context=env, returns=None):
        sig = signature + ('[.RETURNS = ' + returns + ']' if returns is not None else '')
        return '$reference_notice_producer_scoped_header(' + context + ', phpType6_producer, phpType16, ' + expression + ', ' + sig + ')'
    scoped = proof()
    view = '$reference_notice_producer_scoped_return_union_view('
    source = raw(members).removeprefix('NUnionType (SEQUENCE (').removesuffix(')) metadata_function')
    canonical = raw(members, 'stdClass', 'NNameFullyQualified').removeprefix('NUnionType (SEQUENCE (').removesuffix(')) metadata_function')
    lines = [scoped, proof(raw(members, 'stdClass', 'NNameFullyQualified')),
        view + env + ', ' + source + ', false) = (' + canonical + ')',
        '~$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, ' + signature + ')',
        proof(returns='eps'), scoped.replace('phpType6_producer,', 'SEQUENCE eps,', 1),
        proof(context=env + '[.NAMESPACE = eps]'), proof(context=env + '[.NAMESPACE = $ptascii("Elsewhere")]'),
        '~' + proof(context=env + '[.CLASSES = eps]'),
        '~' + proof(context=env + '[.NAMESPACE = eps][.CLASSES = eps]'),
        '~$error_call_valid(S_notice, perrorcall[.LINE = 9])', '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])',
        '~$typed_return_task_valid(S_return, $(z_return + 1))']
    accepted = [['class', kind] for kind in ('array', 'int', 'float', 'bool', 'string', 'null', 'false', 'true', 'callable', 'iterable')]
    accepted += [kinds[::-1] for kinds in accepted]
    accepted += [['null', 'string', 'class'], ['float', 'int', 'class'], ['bool', 'class', 'string'],
        ['class', 'array', 'int', 'float', 'bool', 'string', 'null', 'callable'],
        ['callable', 'null', 'string', 'true', 'float', 'int', 'iterable', 'class']]
    for kinds in accepted:
        lines += [proof(raw(kinds), returns=normalized(kinds)),
            '~' + proof(raw(kinds), returns=normalized(kinds[::-1])),
            '~' + proof(raw(kinds), returns=normalized(kinds, 'STDCLASS'))]
    for kinds in (['class'], ['class', 'class'], ['class', 'int', 'int'], ['class', 'bool', 'true'],
            ['class', 'false', 'true'], ['class', 'array', 'iterable'], ['class', 'object'], ['class', 'mixed'], ['class', 'void']):
        lines.append('~' + proof(raw(kinds), returns=normalized(kinds)))
    for name in ('Box', 'bOx', 'BOX'):
        lines.append(proof(raw(members, name)))
    for tag in ('NIdentifier', 'NNameRelative', 'NNameFullyQualified'):
        lines.append('~' + proof(raw(members, 'Box', tag)))
    for name in ('Other', 'Box\\stdClass', '\\Box', 'Box\x00', 'int', 'mixed', 'self', 'array', 'callable'):
        lines.append('~' + proof(raw(members, name)))
    for name in ('int', 'bool', 'array', 'callable', 'self', 'parent', 'static', 'void', 'never', 'mixed'):
        fake = env + '[.CLASSES = [($ptascii(' + json.dumps(name) + '), $ptascii("stdClass"))]]'
        lines.append('~' + proof(raw(members, name), fake))
    for target in ('Other', 'stdclass', 'StDcLaSs'):
        lines.append('~' + proof(context=env + '[.CLASSES = [($ptascii("box"), $ptascii(' + json.dumps(target) + '))]]'))
    for context in (env, env + '[.NAMESPACE = eps]'):
        fake = context + '[.CLASSES = [($ptascii("stdclass"), $ptascii("stdClass"))]]'
        lines.append(proof(raw(members, 'stdClass'), fake))
    for flag in ('true', 'false'):
        lines += [view + env + ', eps, ' + flag + ') = ' + ('(eps)' if flag == 'true' else 'eps'),
            view + env + ', [NIdentifier (BYTES "aW50") metadata_function], ' + flag + ') = ' + ('([NIdentifier (BYTES "aW50") metadata_function])' if flag == 'true' else 'eps')]
    lines += [proof(raw(members).replace('metadata_function', 'eps')),
        '~' + proof(raw(members).replace('NUnionType ', 'NIntersectionType ', 1))]
    for stage in ('return', 'notice'):
        lines += ['S_zero_' + stage + ' = $drive(S_' + stage + ', 0)',
            'S_zero_' + stage + r'.COMPLETION = BUDGET /\ S_zero_' + stage + '[.COMPLETION = NORMAL] = S_' + stage,
            '$drive($drive(S_zero_' + stage + '[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_' + stage + ', 2)']
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
    print('scoped-ordered-stdclass-return-front' if args.front else 'scoped-ordered-stdclass-return-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
