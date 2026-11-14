#!/usr/bin/env python3
"""Independently check FQN class/callable priority, strict errors and class authority."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import cv_fqn_stdclass_callable_union_producer_reference_notice_state as source_fixture
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_fqn_stdclass_callable_union_producer_reference_notice_review_cases.json')
PREFIX = source_fixture.PREFIX
for old, new in (('CallableSingletonByval93', 'FqnStdclassCallablePeer93'),
        ('CallableSingletonByref93', 'FqnStdclassCallableReceivePeer93'),
        ('CallableMulti93', 'FqnStdclassCallableReturnPeer93')):
    PREFIX = PREFIX.replace(old, new)
branches = source_fixture.branches


def atoms(kinds):
    nodes = []
    for kind in kinds:
        tag = 'NNameFullyQualified' if kind.startswith('\\') else 'NIdentifier'
        name = kind[1:] if kind.startswith('\\') else kind
        nodes.append(tag + ' (BYTES ' + json.dumps(base64.b64encode(name.encode()).decode()) + ') metadata_return_first')
    return '[' + ', '.join(nodes) + ']'


def raw(kinds):
    return 'NUnionType (SEQUENCE (' + atoms(kinds) + ')) metadata_union_return'


def reached(case, front):
    if case['outcome'] != 'NOTICE':
        return ['S_initial.COMPLETION = BUDGET',
            'S_negative = $drive(S_initial[.COMPLETION = NORMAL], 10000)',
            r'S_negative.COMPLETION = NORMAL /\ S_negative.TODO = eps /\ S_negative.CURRENT = eps /\ S_negative.FRAMES = eps',
            '$cn_output(S_negative.EVENTS) = $ptascii(' + json.dumps(case['native_stdout']) + ')',
            '$lookup(S_negative.ENV, $ptascii("x")) = (n_x)',
            'S_negative.STORE[n_x] = DEFINED (PINT 17)',
            '$lookup(S_negative.ENV, $ptascii("copy")) = (n_copy)',
            'S_negative.STORE[n_copy] = DEFINED (PINT 17)',
            r'S_negative.PROPREFS = eps /\ S_negative.REFCOERCIONS = eps /\ S_negative.PARAMETERBACKINGS = eps',
            r'$heap_valid($heap_graph(S_negative)) /\ $call_descriptors_valid(S_negative)']
    lines = source_fixture.reached(case, front)
    return [line.replace('pvalue_original = PSTRING_CARRIER INTERNED_STRING ptbytes_name',
        'pvalue_original = PSTRING_CARRIER (REQUEST_STRING n_string) ptbytes_name') for line in lines]


def completed(case):
    return source_fixture.completed(case) if case['outcome'] == 'NOTICE' else []


def controls(case):
    if case['outcome'] != 'NOTICE':
        typeset = case['formal_members'] if case['outcome'] == 'RECEIVE' else case['return_members']
        return ['$typed_conversion_at(S_negative, ' + branches(typeset) + ', PINT 17, true) = TYPEREJECT',
            '$typed_conversion_at(S_negative, ' + branches(typeset) + ', PINT 17, false) = TYPEBOOL (PINT 17)']
    lines = []
    for kinds in (case['formal_members'], case['return_members'], ['bool', 'callable', '\\StDcLaSs']):
        normalized = branches(kinds)
        lines += ['~$typed_exact(' + normalized + ', pvalue_original)',
            '~$typed_object_exact(S_return, ' + normalized + ', pvalue_original)',
            '$typed_conversion_at(S_return, ' + normalized + ', pvalue_original, false) = TYPEVALUE pvalue_original',
            '$typed_conversion_at(S_return, ' + normalized + ', pvalue_original, true) = TYPEVALUE pvalue_original',
            '$typed_conversion_at(S_return[.CALLABLES = eps][.FUNCTIONS = eps], ' + normalized + ', pvalue_original, false) = TYPEBOOL pvalue_original',
            '$typed_conversion_at(S_return[.CALLABLES = eps][.FUNCTIONS = eps], ' + normalized + ', pvalue_original, true) = TYPEREJECT']
    for kinds in (case['formal_members'], case['return_members']):
        masks = [tag for kind in kinds if not kind.startswith('\\') for tag in (('true', 'false') if kind == 'bool' else (kind,))]
        lines += ['$ptmasks(' + branches(kinds) + ') = ' + json.dumps(masks)]
    lines += ['$typed_callable(S_return, pvalue_original) = (true)',
        '~$typed_return_task_valid(S_return, $(z_return + 1))',
        '~$error_call_valid(S_notice, perrorcall[.LINE = $(perrorcall.LINE + 1)])',
        '~$positional_reference_notice_pending(S_pre[.SOURCES = eps])']
    def check(kinds, accepted=True, normalized=None):
        return ('' if accepted else '~') + '$reference_notice_producer_stdclass_union_members(' + atoms(kinds) + ', ' + (branches(kinds) if normalized is None else normalized) + ', false, eps)'
    maximum = ['\\sTdClAsS', 'callable', 'array', 'int', 'float', 'string', 'null', 'false']
    for size in range(2, 9):
        kinds = maximum[:size]
        lines += [check(kinds), check(list(reversed(kinds)))]
    for boolean in ('bool', 'true'):
        lines += [check(maximum[:-1] + [boolean])]
    for kinds in (['callable', 'int', 'bool'], ['\\stdClass', '\\stdClass', 'callable'],
            ['\\stdClass', 'callable', 'callable'], ['\\stdClass', 'callable', 'bool', 'false'],
            ['\\stdClass', 'callable', 'true', 'false'], ['\\stdClass', 'callable', 'object'],
            ['\\stdClass', 'callable', 'mixed'], ['\\stdClass', 'callable', 'void'],
            ['\\stdClass', 'callable', 'never'], ['\\stdClass', 'callable', 'iterable'],
            maximum + ['object'], ['\\Other', 'callable', 'null'],
            ['\\Vendor\\stdClass', 'callable', 'null']):
        lines += [check(kinds, False)]
    kinds = ['\\sTdClAsS', 'callable', 'bool']
    for wrong in (list(reversed(kinds)), kinds[:-1], kinds + ['null'], ['\\stdclass', 'callable', 'bool']):
        lines += [check(kinds, False, branches(wrong))]
    for tag in ('NName', 'NNameRelative', 'NIdentifier'):
        changed = atoms(kinds).replace('NNameFullyQualified', tag, 1)
        lines += ['~$reference_notice_producer_stdclass_union_members(' + changed + ', ' + branches(kinds) + ', false, eps)']
    signature = 'pfunction_producer.SIGNATURE'
    header = '$reference_notice_producer_header(phpType6_producer, phpType16, '
    # The six old selector shapes use only this fresh source state.
    for kinds in (['\\sTdClAsS', 'callable'], ['callable', '\\sTdClAsS'],
            ['\\sTdClAsS', 'int', 'callable'], ['\\sTdClAsS', 'callable', 'int']):
        lines += [header + raw(kinds) + ', ' + signature + '[.RETURNS = ' + branches(kinds) + '])']
    lines += [check(['\\sTdClAsS', 'int', 'callable']), check(['\\stdClass', 'callable', 'null'])]
    for kinds in (['\\sTdClAsS', 'callable'], ['callable', '\\sTdClAsS'], maximum):
        parameter = 'NParam (SEQUENCE eps) (INTEGER 0) (' + raw(kinds) + ') (BOOLEAN false) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter'
        arguments = '$reference_notice_producer_arguments(phpType6_producer, SEQUENCE ([' + parameter + ']), ' + signature + '[.RETURNS = eps][.PARAMETERS = [psparam[.TYPE = ' + branches(kinds) + ']]])'
        lines += [arguments]
        for update in ('.REQUIRED = false', '.BYREF = true', '.VARIADIC = true'):
            lines += ['~' + arguments.replace('psparam[.TYPE', 'psparam[' + update + '][.TYPE')]
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
    paths = [Path(__file__), CATALOGUE, provenance] + [Path(module.__file__) for module in tuple(sys.modules.values()) if getattr(module, '__file__', None) and Path(module.__file__).resolve().parent == Path(__file__).resolve().parent]
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
            specs.append('dec $cn_case' + str(index) + '() : bool\ndef $cn_case' + str(index) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in current + extra))
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
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\n'.join(specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $cn_case' + str(index) + '()\n' for index in range(len(cases))))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths += modules + [runner, fixture] + [ROOT / name for name in ('spec/semantics/modules.json', 'tests/semantics/profile.json', '_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py', 'tests/semantics/static_types.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py', 'tests/validate.py', 'tests/corpus.py')]
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
    print('peer-fqn-stdclass-callable-union-front' if args.front else 'peer-fqn-stdclass-callable-union-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
