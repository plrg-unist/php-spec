#!/usr/bin/env python3
"""Ground optional literal Boolean formals without widening weak coercion."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types
import cv_literal_bool_formal_producer_reference_notice_state as primary
import cv_literal_bool_formal_producer_reference_notice_review_state as reviewed

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('supplied_optional_literal_bool_default_producer_reference_notice_cases.json')


def namespaces(text):
    return (text.replace('FalseFormalAlias70', 'OptionalFalseFormalAlias143')
        .replace('MultiCvLiteralBoolFormal70', 'OptionalMultiLiteralBool143')
        .replace('ReviewNotice70', 'OptionalLiteralNotice143'))


PREFIX = namespaces(primary.PREFIX + reviewed.PREFIX.replace('$scfr_', '$literal_review_'))


def default_parts(case, index=0):
    spelling = case['defaults'][index] if case['kind'] == 'multiple' else case['default']
    suffix = ('_first' if index == 0 else '_last') if case['kind'] == 'multiple' else ''
    encoded = json.dumps(base64.b64encode(spelling.encode()).decode())
    return ('(NExprConstFetch (NName (BYTES ' + encoded + ') metadata_default_name' + suffix
        + ') metadata_default' + suffix + ')'), spelling.lower()


def front_lines(case, front):
    kind = case['kind']
    if kind == 'invalid':
        return ['S_initial.COMPLETION = STATICBYTES ($ptascii("Cannot use bool as default value for parameter $input of type false")) 2',
            'S_initial.EVENTS = eps']
    if kind in ('false_byref', 'multiple'):
        lines, _ = primary.normal('', case, 0 if kind == 'false_byref' else 1, front)
    elif kind == 'true_byval':
        lines, _ = reviewed.normal('', case, front)
        lines = [line.replace('$scfr_', '$literal_review_') for line in lines]
    else:
        lines, _ = reviewed.priority('', 1 if kind == 'false_priority' else 2)
        lines = [line.replace('$scfr_', '$literal_review_') for line in lines]
    assert lines[0] == ''
    slots = [('psparam_first', 'phpType10_saved', 0), ('psparam_last', 'phpType10_changed', 1)] if kind == 'multiple' else [('psparam', 'phpType10', 0)]
    result = []
    for line in lines[1:]:
        for slot, variable, index in slots:
            default, literal = default_parts(case, index)
            line = line.replace(variable + ' ABSENT', variable + ' ' + default)
            line = line.replace(slot + '.REQUIRED', '~' + slot + '.REQUIRED')
            line = line.replace(slot + '.DEFAULT = PSNONE', slot + '.DEFAULT = PSDEFAULT ' + default + ' "' + literal + '"')
        if line.removeprefix('~').startswith(('$reference_notice_producer_arguments(', '$reference_notice_producer_header(', '$positional_reference_notice_pending(')):
            live_return_denial = kind == 'multiple' and line.removeprefix('~').startswith('$reference_notice_producer_arguments(') and '.RETURNS = eps' not in line
            line = ('~' if front or live_return_denial else '') + line.removeprefix('~')
        clauses = line.split(r' /\ ')
        defaults = [clause for clause in clauses if '.DEFAULT = PSDEFAULT ' in clause]
        if defaults:
            flags = [clause for clause in clauses if clause not in defaults]
            if flags:
                result.append(namespaces(r' /\ '.join(flags)))
            result += [namespaces(clause) for clause in defaults]
        else:
            result.append(namespaces(line))
    for slot, _, index in slots:
        default, literal = default_parts(case, index)
        result += [slot + '.DEFAULT = PSDEFAULT ' + default + ' "' + literal + '"',
            '$typed_stored_default(' + slot + '.DEFAULT, PBOOL ' + literal + ') = PBOOL ' + literal]
    return result


def full_lines(case):
    return []


def controls(case):
    if case['kind'] not in ('false_byref', 'multiple', 'true_byval'):
        return []
    multiple = case['kind'] == 'multiple'
    arguments = 'SEQUENCE ([phpType7_first, phpType7_last])' if multiple else 'SEQUENCE ([phpType7])'
    raw = 'SEQUENCE ([phpType17_first, phpType17_last])' if multiple else 'SEQUENCE ([phpType17])'
    returns = 'phpType18_return' if multiple else 'phpType18'
    default, _ = default_parts(case)
    slot = 'psparam_first' if multiple else 'psparam'
    parameters = '[' + slot + '[.DEFAULT = PSDEFAULT ' + default + ' "bool"]' + (', psparam_last' if multiple else '') + ']'
    lines = ['~$reference_notice_producer_header(' + arguments + ', ' + raw + ', ' + returns + ', pfunction_producer.SIGNATURE[.PARAMETERS = ' + parameters + '])',
        '$call_target(S_full, pfunction_producer.NAME, eps) = (pfunction_survived)',
        'pfunction_survived.SIGNATURE = pfunction_producer.SIGNATURE']
    for stage in ('receive', 'return', 'notice'):
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
    native_path = args.native_report.resolve()
    native, cases = json.loads(native_path.read_bytes()), json.loads(CATALOGUE.read_bytes())
    rows = {row['id']: row for row in native['records']}
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    assert native['mode'] == 'native-first' and native['passed'] and native['inputs_stable'] and native['head_stable']
    assert native['profile'] == types.PROFILE and native['runtime_sha256'] == sha(types.PHP)
    assert set(rows) == {case['id'] for case in cases} and len(cases) == 6
    out = args.output.resolve()
    out.mkdir(parents=True)
    paths = [CATALOGUE, native_path] + sorted({Path(module.__file__).absolute() for module in sys.modules.values()
        if getattr(module, '__file__', None) and Path(module.__file__).absolute().parent == ROOT / 'tests/semantics'})
    frontend = adapter = None
    specs, reached, derived = [], [], []
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for index, case in enumerate(cases):
            row, source = rows[case['id']], Path(rows[case['id']]['command'][-1])
            assert row['passed'] and row['exit'] == case['native_exit'] and not row['timeout'] and not row['group_after']
            assert source.read_bytes() == case['source'].encode() and sha(source) == case['source_sha256'] == row['source_sha256']
            assert Path(row['stdout']).read_bytes() == row['actual_stdout'].encode() == case['native_stdout'].encode()
            assert Path(row['stderr']).read_bytes() == row['actual_stderr'].encode() == case['native_stderr'].replace('{source}', str(source)).encode()
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted']
            checked_value = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked_value['ok'] and checked_value['fixture']
            current = ['S_initial = $php_run(' + checked_value['fixture'] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'] + front_lines(case, args.front)
            extra = [] if args.front else controls(case)
            if not args.front:
                current += full_lines(case)
            specs.append('dec $literal_bool_default_case' + str(index) + '() : bool\ndef $literal_bool_default_case' + str(index) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in current + extra))
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
    fixture.write_text(PREFIX + '\n'.join(specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $literal_bool_default_case' + str(index) + '()\n' for index in range(len(cases))))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths += modules + [runner, fixture] + [ROOT / name for name in ('spec/semantics/modules.json', 'tests/semantics/profile.json', '_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py')]
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
    print('supplied-optional-literal-bool-default-front' if args.front else 'supplied-optional-literal-bool-default-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
