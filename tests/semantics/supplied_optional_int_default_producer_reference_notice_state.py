#!/usr/bin/env python3
"""Ground supplied optional defaults without changing live signatures or omitted calls."""
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
import singleton_cv_typed_formal_producer_reference_notice_state as single
import untyped_array_return_producer_cv_reference_notice_state as arrays
import multi_cv_scalar_formal_producer_reference_notice_state as multiple

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('supplied_optional_int_default_producer_reference_notice_cases.json')
DEFAULT = '(NScalarInt (INTEGER 7) metadata_default)'
ARRAY_STAGES = r'''
def $rsn_stage(S, 0) = true
  -- if S.TODO = (CALL_SEND pcalltarget phpType7* n poperand* porigin? z) :: ptask_tail*
  -- if S.RESULT = KNOWN (PARRAY n_root)
  -- if $target_function(S, pcalltarget) = (pfunction)
  -- if pfunction.NAME = $ptascii("UntypedArrayReturnProducer35\\take")
def $rsn_stage(S, 1) = true
  -- if S.TODO = (CALL_ARGS pcalltarget eps 1 poperand* porigin? z) :: ptask_tail*
  -- if $rsn_outputs(S.EVENTS) = $ptascii("U;V:3;M:17;H;")
def $rsn_stage(S, 2) = true
  -- if S.TODO = (RETURN_VALUE z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if $function_at($all_functions(S), pcallcontext.FUNCTION) = (pfunction)
  -- if pfunction.NAME = $ptascii("UntypedArrayReturnProducer35\\make")
def $rsn_stage(S, 3) = true
  -- if $rsn_outputs(S.EVENTS) = $ptascii("U;V:3;M:17;H;F;7:7:23:23:9;11:11;")
  -- if $lookup(S.ENV, $ptascii("copy")) = eps /\ $lookup(S.ENV, $ptascii("leaf")) = eps
def $rsn_stage(S, 4) = true
  -- if $rsn_outputs(S.EVENTS) = $ptascii("U;V:3;M:17;H;F;7:7:23:23:9;11:11;11:17:9:13;")
def $rsn_stage(S, n_stage) = false -- otherwise
'''
PREFIX = single.PREFIX + multiple.PREFIX + arrays.PREFIX + ARRAY_STAGES


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
            'psparam_default.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]',
            'psparam_default.DEFAULT = PSDEFAULT (NScalarInt (INTEGER 7) metadata_default) "int"',
            '$heap_valid($heap_graph(S_full)) /\\ $call_descriptors_valid(S_full)']
    if kind == 'invalid':
        return ['S_initial.COMPLETION = STATICBYTES ($ptascii("Cannot use int as default value for parameter $input of type array")) 2',
            'S_initial.EVENTS = eps']
    if kind == 'singleton':
        lines = single.front_lines(0, case)
    elif kind == 'array':
        lines = arrays.RETURN + arrays.COMMON
    else:
        lines = multiple.front_lines(0, case)
    result = []
    for line in lines:
        if kind == 'multiple':
            if line.startswith('phpType17_last = NParam'):
                line = line.replace('phpType10_last ABSENT', 'phpType10_last ' + DEFAULT)
            line = line.replace('psparam_first.REQUIRED /\\ psparam_last.REQUIRED', 'psparam_first.REQUIRED /\\ ~psparam_last.REQUIRED')
            line = line.replace('pvalue_received_last = PBOOL false', 'pvalue_received_last = PINT 0')
            line = line.replace('= TYPEBOOL pvalue_y_original', '= TYPEINTEGER pvalue_y_original')
        else:
            if line.startswith(('phpType17 = NParam', 'phpType16 = SEQUENCE')):
                line = line.replace('phpType10 ABSENT', 'phpType10 ' + DEFAULT)
            line = line.replace('psparam.REQUIRED /\\ psparam.DEFAULT = PSNONE', '~psparam.REQUIRED /\\ psparam.DEFAULT = PSDEFAULT ' + DEFAULT + ' "int"')
        if kind == 'array':
            line = line.replace('U;M:17;', 'U;V:3;M:17;')
            if line.startswith('$reference_notice_producer_arguments(') and '.RETURNS = eps' in line and front:
                line = '~' + line
        if not front and (line.startswith('~$reference_notice_producer_header(')
                or (line.startswith('~$reference_notice_producer_arguments(') and '.RETURNS = eps' in line)
                or line == '~$positional_reference_notice_pending(S_pre)'):
            line = line.removeprefix('~')
        default_clause = 'psparam.DEFAULT = PSDEFAULT ' + DEFAULT + ' "int"'
        if ' /\\ ' + default_clause in line:
            result += [line.replace(' /\\ ' + default_clause, ''), default_clause]
            continue
        result.append(line)
    if kind == 'multiple':
        result += ['psparam_first.DEFAULT = PSNONE',
            'psparam_last.DEFAULT = PSDEFAULT ' + DEFAULT + ' "int"']
    if kind == 'array' and front:
        result += ['~$reference_notice_producer_header(phpType6_producer, phpType16, phpType18, pssignature)',
            '~$positional_reference_notice_pending(S_pre)']
    arguments, raw, returns, _ = header_parts(case)
    if kind != 'array':
        result.append('phpType6_producer = ' + arguments)
    result += ['phpType16_producer = ' + ('phpType16' if kind == 'array' else 'SEQUENCE (' + raw + ')'),
        'phpType18_producer = ' + returns]
    return result


def full_lines(case):
    if case['kind'] == 'singleton':
        return single.full_lines(0, case)
    if case['kind'] == 'multiple':
        return multiple.full_lines(0, case)
    if case['kind'] == 'array':
        return [line.replace('U;M:17;H;F;7:7:23:23:9;11:11;11:17:9:13;R:29:23:23;', case['native_stdout'])
            for line in arrays.PRIMARY]
    return []


def header_parts(case):
    if case['kind'] == 'singleton':
        return 'SEQUENCE ([phpType7])', '[phpType17]', 'phpType18', '[psparam]'
    if case['kind'] == 'multiple':
        return 'SEQUENCE ([phpType7_first, phpType7_last])', '[phpType17_first, phpType17_last]', 'phpType18_return', '[psparam_first, psparam_last]'
    return 'phpType6_producer', '[phpType17]', 'phpType18', '[psparam]'


def controls(case):
    if case['kind'] in ('omitted', 'invalid'):
        return []
    arguments, raw, returns, parameters = header_parts(case)
    signature = 'pfunction_producer.SIGNATURE'
    parameter = 'psparam_last' if case['kind'] == 'multiple' else 'psparam'
    if case['kind'] == 'array':
        raw_bind = 'phpType16 = SEQUENCE ([phpType17])'
    else:
        raw_bind = None

    def checked(update):
        return signature + '[.PARAMETERS = ' + parameters.replace(parameter + ']', parameter + '[' + update + ']]') + ']'

    def proof(checked_signature=signature, raw_parameters=raw, actuals=arguments):
        return '$reference_notice_producer_header(' + actuals + ', SEQUENCE (' + raw_parameters + '), ' + returns + ', ' + checked_signature + ')'

    lines = ([raw_bind] if raw_bind else []) + [proof(),
        '$reference_notice_producer_supplied_defaults(' + raw + ', ' + parameters + ', false) = ((phpType17_view*, psparam_view*))',
        '$reference_notice_producer_arguments(' + arguments + ', SEQUENCE phpType17_view*, ' + signature + '[.PARAMETERS = psparam_view*][.RETURNS = eps])',
        '$reference_notice_producer_header(' + arguments + ', SEQUENCE phpType17_view*, ' + returns + ', ' + signature + '[.PARAMETERS = psparam_view*])',
        parameter + '.DEFAULT = PSDEFAULT ' + DEFAULT + ' "int"',
        '~' + parameter + '.REQUIRED',
        '~' + proof(checked('.DEFAULT = PSNONE')),
        '~' + proof(checked('.DEFAULT = PSDEFAULT (NScalarInt (INTEGER 9) metadata_default) "int"')),
        '~' + proof(checked('.DEFAULT = PSDEFAULT ' + DEFAULT + ' "float"')),
        '~' + proof(checked('.REQUIRED = true')),
        '~' + proof(checked('.VARIADIC = true')),
        '~' + proof(checked('.BYREF = ' + ('false' if case['kind'] != 'singleton' else 'true'))),
        '~' + proof(actuals='SEQUENCE ([NArg ABSENT (NScalarInt (INTEGER 7) eps) (BOOLEAN false) (BOOLEAN false) eps])'),
        '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])',
        '~$error_call_valid(S_notice, perrorcall[.LINE = $(perrorcall.LINE + 1)])']
    # The reached signature/default stays genuine after the pure proof query.
    lines += [parameter + '.DEFAULT = PSDEFAULT ' + DEFAULT + ' "int"',
        'pfunction_producer.SIGNATURE.PARAMETERS = ' + parameters]
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
    assert set(rows) == {case['id'] for case in cases} and len(cases) == 5
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
            specs.append('dec $optional_case' + str(index) + '() : bool\ndef $optional_case' + str(index) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in current + extra))
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
    fixture.write_text(PREFIX + '\n'.join(specs) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if $optional_case' + str(index) + '()\n' for index in range(len(cases))))
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
    print('supplied-optional-int-default-front' if args.front else 'supplied-optional-int-default-notice', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
