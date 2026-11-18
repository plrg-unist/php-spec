#!/usr/bin/env python3
"""Ground supplied literal FLOAT defaults under the existing checked-source encoding contract."""
import argparse
import base64
import copy
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
import supplied_optional_float_int_default_producer_reference_notice_state as promoted

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('supplied_optional_float_default_producer_reference_notice_cases.json')
DEFAULT = '(NScalarFloat (FLOAT "401e000000000000") metadata_default)'
FLOAT75 = 'PFLOAT 4620130267728707584'
PREFIX = integer.PREFIX.replace('U;V:3;M:17;', 'U;V:3:0;M:17;')


def front_lines(case, front):
    kind = case['kind']
    if kind == 'invalid':
        return ['S_initial.COMPLETION = STATICBYTES ($ptascii("Cannot use float as default value for parameter $input of type int")) 2',
            'S_initial.EVENTS = eps']
    lines = promoted.front_lines(case, front) if kind in ('singleton', 'omitted') else integer.front_lines(case, front)
    result = []
    for line in lines:
        if line.startswith(('$psconvertdefault(', '$typed_stored_default(')):
            continue
        line = line.replace(integer.DEFAULT, DEFAULT)
        line = line.replace('PSDEFAULT ' + DEFAULT + ' "int"', 'PSDEFAULT ' + DEFAULT + ' "float"')
        line = line.replace('U;V:3;M:17;', 'U;V:3:0;M:17;')
        if kind == 'omitted':
            line = line.replace('psparam_default.TYPE = [(PTBRANCH ([PTBUILTIN "float"]))]', 'psparam_default.TYPE = eps')
        result.append(line)
    if kind == 'array':
        result.append('phpType16 = SEQUENCE ([phpType17])')
    parameter = 'psparam_default' if kind == 'omitted' else 'psparam'
    result.append('$typed_stored_default(' + parameter + '.DEFAULT, ' + FLOAT75 + ') = ' + FLOAT75)
    return result


def full_lines(case):
    return promoted.full_lines(case) if case['kind'] == 'singleton' else integer.full_lines(case)


def controls(case):
    if case['kind'] in ('omitted', 'invalid'):
        return []
    arguments, raw, returns, parameters = integer.header_parts(case)
    signature = 'pfunction_producer.SIGNATURE'

    def proof(update=''):
        checked = signature if not update else signature + '[.PARAMETERS = [psparam[' + update + ']]]'
        return '$reference_notice_producer_header(' + arguments + ', SEQUENCE (' + raw + '), ' + returns + ', ' + checked + ')'

    lines = [proof(),
        '~' + proof('.DEFAULT = PSNONE'),
        '~' + proof('.DEFAULT = PSDEFAULT ' + DEFAULT + ' "int"'),
        '~' + proof('.DEFAULT = PSDEFAULT (NScalarInt (INTEGER 7) metadata_default) "float"'),
        '~' + proof('.DEFAULT = PSDEFAULT (NScalarFloat (FLOAT "401c000000000000") metadata_default) "float"'),
        '~' + proof('.REQUIRED = true'),
        '~' + proof('.VARIADIC = true'),
        '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])',
        '~$error_call_valid(S_notice, perrorcall[.LINE = $(perrorcall.LINE + 1)])',
        '$call_target(S_full, pfunction_producer.NAME, eps) = (pfunction_survived)',
        'pfunction_survived.SIGNATURE = pfunction_producer.SIGNATURE',
        'psparam.DEFAULT = PSDEFAULT ' + DEFAULT + ' "float"']
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
    adapter_float_boundary_negatives = 0
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
            if args.front and case['kind'] == 'singleton':
                for payload in ('401e00000000000', '401e0000000000000', '401E000000000000', '401g000000000000'):
                    bad = copy.deepcopy(parsed['ast'])

                    def replace_float(value):
                        if isinstance(value, dict):
                            if 'float' in value:
                                value['float'] = payload
                                return True
                            return any(replace_float(child) for child in value.values())
                        return isinstance(value, list) and any(replace_float(child) for child in value)

                    assert replace_float(bad)
                    try:
                        adapter.request({'op': 'check', 'ast': bad, 'fixture': True})
                    except AssertionError as error:
                        rejection = error.args[0]
                        assert rejection['ok'] is False and rejection['category'] == 'adapter_rejection' and 'invalid float bits' in rejection['message']
                        adapter_float_boundary_negatives += 1
                    else:
                        raise AssertionError('malformed FLOAT transport reached the semantic fixture')
            checked_value = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked_value['ok'] and checked_value['fixture']
            current = ['S_initial = $php_run(' + checked_value['fixture'] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'] + front_lines(case, args.front)
            extra = [] if args.front else controls(case)
            if not args.front:
                current += full_lines(case)
            specs.append('dec $literal_float_default_case' + str(index) + '() : bool\ndef $literal_float_default_case' + str(index) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in current + extra))
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
    fixture.write_text(PREFIX + '\n'.join(specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $literal_float_default_case' + str(index) + '()\n' for index in range(len(cases))))
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
    report = dict(revision=revision, inputs=before, inputs_stable=stable, head_stable=head_stable, module_count=len(modules), mode='fixture-SL/cache=false/det=true', front=args.front, selection=[case['id'] for case in cases], conditions=len(reached) + len(derived), reached_conditions=len(reached), derived_conditions=len(derived), source_agreements=0, adapter_float_boundary_negatives=adapter_float_boundary_negatives, process=process, passed=passed)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('supplied-optional-float-default-front' if args.front else 'supplied-optional-float-default-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
