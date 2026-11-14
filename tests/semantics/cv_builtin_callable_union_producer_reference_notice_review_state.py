#!/usr/bin/env python3
"""Independently check callable precedence, strict errors and ordered union fences."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import cv_builtin_callable_union_producer_reference_notice_state as source_fixture
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_builtin_callable_union_producer_reference_notice_review_cases.json')
PREFIX = source_fixture.PREFIX
for old, new in (('CallableSingletonByval92', 'CallableBuiltinPeer92'),
        ('CallableSingletonByref92', 'CallableBuiltinReceivePeer92'),
        ('CallableMulti92', 'CallableBuiltinReturnPeer92')):
    PREFIX = PREFIX.replace(old, new)
branches = source_fixture.branches


def atoms(kinds):
    return '[' + ', '.join('NIdentifier (BYTES ' + json.dumps(base64.b64encode(kind.encode()).decode()) + ') metadata_return_first' for kind in kinds) + ']'


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
    for kinds in (case['formal_members'], case['return_members'], ['bool', 'callable', 'null']):
        normalized = branches(kinds)
        lines += ['~$typed_exact(' + normalized + ', pvalue_original)',
            '$typed_conversion_at(S_return, ' + normalized + ', pvalue_original, false) = TYPEVALUE pvalue_original',
            '$typed_conversion_at(S_return, ' + normalized + ', pvalue_original, true) = TYPEVALUE pvalue_original',
            '$typed_conversion_at(S_return[.CALLABLES = eps][.FUNCTIONS = eps], ' + normalized + ', pvalue_original, false) = TYPEBOOL pvalue_original',
            '$typed_conversion_at(S_return[.CALLABLES = eps][.FUNCTIONS = eps], ' + normalized + ', pvalue_original, true) = TYPEREJECT']
    lines += ['$typed_callable(S_return, pvalue_original) = (true)',
        '~$typed_return_task_valid(S_return, $(z_return + 1))',
        '~$error_call_valid(S_notice, perrorcall[.LINE = $(perrorcall.LINE + 1)])',
        '~$positional_reference_notice_pending(S_pre[.SOURCES = eps])']
    # Exercise the legal widths and both endpoint orders on this fresh source state.
    maximum = ['callable', 'array', 'int', 'float', 'string', 'null', 'false', 'object']
    for size in range(3, 9):
        kinds = maximum[:size]
        for ordered in (kinds, list(reversed(kinds))):
            lines += ['$reference_notice_producer_union_members(' + atoms(ordered) + ', ' + branches(ordered) + ', eps)']
    for boolean in ('bool', 'true'):
        kinds = ['callable', 'array', 'int', 'float', 'string', 'null', boolean, 'object']
        lines += ['$reference_notice_producer_union_members(' + atoms(kinds) + ', ' + branches(kinds) + ', eps)']
    for kinds in (['callable', 'callable', 'null'], ['callable', 'bool', 'false'],
            ['callable', 'true', 'false'], ['callable', 'bool', 'true'],
            ['callable', 'void', 'null'], ['callable', 'never', 'null'],
            ['callable', 'mixed', 'null'], maximum + ['callable']):
        lines += ['~$reference_notice_producer_union_members(' + atoms(kinds) + ', ' + branches(kinds) + ', eps)']
    kinds = ['callable', 'bool', 'null']
    for wrong in (list(reversed(kinds)), kinds[:-1], kinds + ['string']):
        lines += ['~$reference_notice_producer_union_members(' + atoms(kinds) + ', ' + branches(wrong) + ', eps)']
    for tag in ('NName', 'NNameFullyQualified', 'NNameRelative'):
        changed = atoms(kinds).replace('NIdentifier', tag, 1)
        lines += ['~$reference_notice_producer_union_members(' + changed + ', ' + branches(kinds) + ', eps)']
    class_raw = atoms(['stdClass', 'callable', 'null']).replace('NIdentifier', 'NNameFullyQualified', 1)
    class_types = '[(PTBRANCH ([PTCLASS ($ptascii("stdClass"))])), (PTBRANCH ([PTBUILTIN "callable"])), (PTBRANCH ([PTBUILTIN "null"]))]'
    lines += ['~$reference_notice_producer_stdclass_union_members(' + class_raw + ', ' + class_types + ', false, eps)']
    # All affected old selectors are checked here, without replaying their campaigns.
    promoted = [('callable', 'int', 'string')] * 2
    promoted += [('callable', 'null', 'int'), ('callable', 'int', 'string')] * 3
    promoted += [('callable', 'null', 'string'), ('callable', 'int', 'string')]
    promoted += [('callable', 'null', 'bool'), ('callable', 'bool', 'string')]
    promoted += [('callable', 'null', 'int'), ('callable', 'null', 'string')]
    for index, kinds in enumerate(promoted):
        header = '$reference_notice_producer_header(phpType6_producer, phpType16, ' + raw(kinds) + ', pfunction_producer.SIGNATURE[.RETURNS = ' + branches(kinds) + '])'
        parameter = 'NParam (SEQUENCE eps) (INTEGER 0) (' + raw(kinds) + ') (BOOLEAN false) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter'
        formal = '$reference_notice_producer_arguments(phpType6_producer, SEQUENCE ([' + parameter + ']), pfunction_producer.SIGNATURE[.RETURNS = eps][.PARAMETERS = [psparam[.TYPE = ' + branches(kinds) + ']]])'
        lines += [header]
        if index >= 2:
            lines += [formal]
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
    print('peer-builtin-callable-union-front' if args.front else 'peer-builtin-callable-union-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
