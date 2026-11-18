#!/usr/bin/env python3
"""Ground raw INT defaults on supplied plain FLOAT formals without changing live signatures."""
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
import supplied_optional_int_default_producer_reference_notice_state as integer

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('supplied_optional_float_int_default_producer_reference_notice_cases.json')
DEFAULT = integer.DEFAULT
PREFIX = integer.PREFIX
FLOAT17 = 'PFLOAT 4625478292286210048'
FLOAT7 = 'PFLOAT 4619567317775286272'


def front_lines(case, front):
    kind = case['kind']
    if kind == 'omitted':
        return ['S_initial.COMPLETION = BUDGET',
            'S_full = $drive(S_initial[.COMPLETION = NORMAL], 100000)',
            'S_full.COMPLETION = NORMAL /\\ S_full.TODO = eps',
            '$rsn_outputs(S_full.EVENTS) = $ptascii(' + json.dumps(case['native_stdout']) + ')',
            '$call_target(S_full, $ptascii("make"), eps) = (pfunction_default)',
            'pfunction_default.SIGNATURE.PARAMETERS = [psparam_default]',
            '~psparam_default.REQUIRED /\\ ~psparam_default.VARIADIC',
            'psparam_default.TYPE = [(PTBRANCH ([PTBUILTIN "float"]))]',
            'psparam_default.DEFAULT = PSDEFAULT ' + DEFAULT + ' "float"',
            '$typed_stored_default(psparam_default.DEFAULT, PINT 7) = ' + FLOAT7,
            '$heap_valid($heap_graph(S_full)) /\\ $call_descriptors_valid(S_full)']
    if kind == 'invalid':
        return ['S_initial.COMPLETION = STATICBYTES ($ptascii("Cannot use string as default value for parameter $input of type float")) 2',
            'S_initial.EVENTS = eps']
    lines = integer.front_lines(case, front)
    result = []
    for line in lines:
        if kind == 'singleton':
            line = line.replace('PTBUILTIN "int"', 'PTBUILTIN "float"')
            line = line.replace('$ptascii("int")', '$ptascii("float")')
            line = line.replace('TYPEINTEGER pvalue_original', 'TYPEVALUE (' + FLOAT17 + ')')
            line = line.replace('(PINT 17)', '(' + FLOAT17 + ')')
        else:
            line = line.replace('pvalue_received_last = PINT 0', 'pvalue_received_last = PFLOAT 0')
            line = line.replace('TYPEINTEGER pvalue_y_original', 'TYPEVALUE (PFLOAT 0)')
        line = line.replace('PSDEFAULT ' + DEFAULT + ' "int"', 'PSDEFAULT ' + DEFAULT + ' "float"')
        result.append(line)
    parameter = 'psparam_last' if kind == 'multiple' else 'psparam'
    result += ['$psconvertdefault(' + parameter + '.TYPE, PSDEFAULT ' + DEFAULT + ' "int") = ' + parameter + '.DEFAULT',
        '$typed_stored_default(' + parameter + '.DEFAULT, PINT 7) = ' + FLOAT7]
    return result


def full_lines(case):
    lines = integer.full_lines(case)
    if case['kind'] == 'singleton':
        return [line.replace('(PINT 17)', '(' + FLOAT17 + ')') for line in lines]
    return lines


def controls(case):
    if case['kind'] in ('omitted', 'invalid'):
        return []
    arguments, raw, returns, parameters = integer.header_parts(case)
    parameter = 'psparam_last' if case['kind'] == 'multiple' else 'psparam'
    signature = 'pfunction_producer.SIGNATURE'

    def proof(update='', actuals=arguments):
        checked = signature if not update else signature + '[.PARAMETERS = ' + parameters.replace(parameter + ']', parameter + '[' + update + ']]') + ']'
        return '$reference_notice_producer_header(' + actuals + ', SEQUENCE (' + raw + '), ' + returns + ', ' + checked + ')'

    lines = [proof(),
        '~' + proof('.DEFAULT = PSNONE'),
        '~' + proof('.DEFAULT = PSDEFAULT ' + DEFAULT + ' "int"'),
        '~' + proof('.DEFAULT = PSDEFAULT (NScalarFloat (FLOAT "401c000000000000") metadata_default) "float"'),
        '~' + proof('.DEFAULT = PSDEFAULT (NScalarInt (INTEGER 8) metadata_default) "float"'),
        '~' + proof('.REQUIRED = true'),
        '~' + proof('.VARIADIC = true'),
        '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])',
        '~$error_call_valid(S_notice, perrorcall[.LINE = $(perrorcall.LINE + 1)])',
        '$call_target(S_full, pfunction_producer.NAME, eps) = (pfunction_survived)',
        'pfunction_survived.SIGNATURE = pfunction_producer.SIGNATURE',
        parameter + '.DEFAULT = PSDEFAULT ' + DEFAULT + ' "float"']
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
    native_path = args.native_report.resolve()
    native, cases = json.loads(native_path.read_bytes()), json.loads(CATALOGUE.read_bytes())
    rows = {row['id']: row for row in native['records']}
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    assert native['mode'] == 'native-first' and native['passed'] and native['inputs_stable'] and native['head_stable']
    assert native['profile'] == types.PROFILE and native['runtime_sha256'] == sha(types.PHP)
    assert set(rows) == {case['id'] for case in cases} and len(cases) == 4
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
            specs.append('dec $float_default_case' + str(index) + '() : bool\ndef $float_default_case' + str(index) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in current + extra))
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
    fixture.write_text(PREFIX + '\n'.join(specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $float_default_case' + str(index) + '()\n' for index in range(len(cases))))
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
    print('supplied-optional-float-int-default-front' if args.front else 'supplied-optional-float-int-default-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
