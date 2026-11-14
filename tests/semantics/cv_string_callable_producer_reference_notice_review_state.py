"""Ground string-arm exact matches before callable service admission."""
import argparse
import base64
import hashlib
import json
import os
import subprocess
from pathlib import Path

import cv_union_callable_producer_reference_notice_review_state as prior
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('cv_string_callable_producer_reference_notice_review_cases.json')
FORWARD = '[(PTBRANCH ([PTBUILTIN "callable"])), (PTBRANCH ([PTBUILTIN "string"]))]'
REVERSE = '[(PTBRANCH ([PTBUILTIN "string"])), (PTBRANCH ([PTBUILTIN "callable"]))]'


def prefix(case):
    return prior.prefix(case).replace('ReviewUnionCallable84', 'ReviewCallableString85')


def controls(case):
    args = 'SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([phpType17_first, phpType17_last]), '
    signature = 'pfunction_producer.SIGNATURE'
    header = '$reference_notice_producer_header(' + args + 'phpType18_return, '
    lines = ['~$typed_return_task_valid(S_return, $(z_return + 1))',
        '~$error_call_valid(S_notice, perrorcall[.LINE = 9])',
        '~$error_call_valid(S_notice, perrorcall[.LEVEL = 2])',
        '~$positional_reference_notice_pending(S_pre[.SOURCES = eps])',
        '~$positional_reference_notice_pending(S_pre[.RESULT = KNOWN (PSTRING_CARRIER (REQUEST_STRING (|S_pre.STRINGDATA|)) ($ptascii("forged85")))])',
        '~$named_reference_notice_operand(S_pre[.REFCELLS = eps], REFERENCE n_y)',
        '~$error_call_valid(S_notice[.REFCELLS = eps], perrorcall)']
    for role, opposite in (('first', REVERSE), ('last', FORWARD)):
        for wrong in ('eps', '[(PTBRANCH ([PTBUILTIN "callable"]))]', opposite,
                FORWARD[:-1] + ', (PTBRANCH ([PTBUILTIN "string"]))]'):
            params = '[psparam_first[.TYPE = ' + wrong + '], psparam_last]' if role == 'first' else '[psparam_first, psparam_last[.TYPE = ' + wrong + ']]'
            lines += ['~$reference_notice_producer_arguments(' + args + signature + '[.RETURNS = eps][.PARAMETERS = ' + params + '])']
    for wrong in (FORWARD, '[(PTBRANCH ([PTBUILTIN "callable"]))]', REVERSE[:-1] + ', (PTBRANCH ([PTBUILTIN "string"]))]'):
        lines += ['~' + header + signature + '[.RETURNS = ' + wrong + '])']
    for kinds in (('callable', 'string'), ('string', 'callable'), ('callable', 'null'), ('null', 'callable')):
        raw, normalized = prior.union(kinds)
        lines += ['$reference_notice_producer_header(' + args + raw + ', ' + signature + '[.RETURNS = ' + normalized + '])']
    for kinds in (('callable', 'int'), ('int', 'callable'), ('callable', 'bool'), ('array', 'callable'), ('callable', 'object'), ('callable', 'null', 'string'), ('callable', 'int', 'string'), ('callable', 'callable')):
        raw, normalized = prior.union(kinds)
        refused = '' if len(kinds) == 2 and ('int' in kinds or 'bool' in kinds) else '~'
        lines += [refused + '$reference_notice_producer_header(' + args + raw + ', ' + signature + '[.RETURNS = ' + normalized + '])']
        raw_param = 'NParam (SEQUENCE eps) (INTEGER 0) (' + raw + ') (BOOLEAN false) (BOOLEAN false) phpType10_first ABSENT (SEQUENCE eps) metadata_first_parameter'
        lines += [refused + '$reference_notice_producer_arguments(SEQUENCE ([phpType7_first, phpType7_last]), SEQUENCE ([' + raw_param + ', phpType17_last]), ' + signature + '[.RETURNS = eps][.PARAMETERS = [psparam_first[.TYPE = ' + normalized + '], psparam_last]])']
    for update in ('.BYREF = true', '.REQUIRED = false', '.VARIADIC = true', '.DEFAULT = PSDEFAULTUNSUPPORTED "forged callable string default"'):
        lines += ['~$reference_notice_producer_arguments(' + args + signature + '[.RETURNS = eps][.PARAMETERS = [psparam_first[' + update + '], psparam_last]])']
    for normalized in (FORWARD, REVERSE):
        for strict in ('false', 'true'):
            for value in ('pvalue_saved', 'pvalue_y_original', 'PSTRING eps'):
                lines += ['$typed_exact(' + normalized + ', ' + value + ')',
                    '$typed_conversion_at(S_return, ' + normalized + ', ' + value + ', ' + strict + ') = TYPEVALUE (' + value + ')']
                for field in ('CALLABLES', 'FUNCTIONS', 'CLASSES'):
                    lines += ['$typed_conversion_at(S_return[.' + field + ' = eps], ' + normalized + ', ' + value + ', ' + strict + ') = TYPEVALUE (' + value + ')']
            lines += ['$typed_conversion_at(S_return, ' + normalized + ', PNULL, ' + strict + ') = TYPEREJECT']
        for value in ('PINT 17', 'PBOOL true'):
            lines += ['$typed_conversion_at(S_return, ' + normalized + ', ' + value + ', false) = TYPESTRING (' + value + ')',
                '$typed_conversion_at(S_return, ' + normalized + ', ' + value + ', true) = TYPEREJECT']
    lines += ['S_zero = $drive(S_notice, 0)',
        'S_zero.COMPLETION = BUDGET /\\ S_zero[.COMPLETION = NORMAL] = S_notice',
        '$drive($drive(S_zero[.COMPLETION = NORMAL], 1)[.COMPLETION = NORMAL], 1) = $drive(S_notice, 2)']
    return lines


def normal(initial, case, index, front):
    reached, _ = prior.normal(initial, case, index, front)
    result = []
    for line in reached:
        if line == '$typed_callable(S_args, pvalue_original) = (true)':
            continue
        line = line.replace(prior.FORWARD, FORWARD).replace(prior.REVERSE, REVERSE)
        line = line.replace('_null', '_string').replace('$ptascii("null")', '$ptascii("string")')
        if line == 'pvalue_y_original = PNULL':
            line = 'pvalue_y_original = PSTRING_CARRIER (REQUEST_STRING n_y_string) ($ptascii(' + json.dumps(case['changed_name']) + '))'
        if line == 'pvalue_received_last = PNULL':
            line = 'pvalue_received_last = pvalue_y_original'
        if line == '$typed_parameter_conversion(S_receive_last, psparam_last, pvalue_y_original) = TYPEVALUE PNULL':
            line = '$typed_parameter_conversion(S_receive_last, psparam_last, pvalue_y_original) = TYPEVALUE pvalue_y_original'
        result.append(line)
    result += ['$string_carrier_valid(S_args, pvalue_y_original)', '$string_carrier_valid(S_pre, pvalue_y_original)',
        '~$typed_registered(S_args, $ptascii(' + json.dumps(case['value_name']) + '))',
        '~$typed_registered(S_args, $ptascii(' + json.dumps(case['changed_name']) + '))',
        '$typed_exact(' + FORWARD + ', pvalue_original)', '$typed_exact(' + REVERSE + ', pvalue_y_original)']
    if not front:
        result += ['$string_carrier_valid(S_full, pvalue_y_original)']
    return result, [] if front else controls(case)


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
    assert set(rows) == {row['id'] for row in cases} and len(cases) == 3
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    case_specs, reached, derived = [], [], []
    paths = [Path(__file__), Path(prior.__file__), Path(prior.prior.__file__), Path(prior.prior.prior.__file__), CATALOGUE, provenance]
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        for index, case in enumerate(cases[:1]):
            row = rows[case['id']]
            source = Path(row['command'][-1])
            assert row['passed'] and row['exit'] == 0 and not row['timeout'] and not row['group_after']
            assert source.read_bytes() == case['source'].encode() and sha(source) == case['source_sha256'] == row['source_sha256']
            assert Path(row['stdout']).read_bytes() == row['actual_stdout'].encode() == case['native_stdout'].encode()
            assert Path(row['stderr']).read_bytes() == row['actual_stderr'].encode() == b''
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'] and checked['fixture']
            initial = 'S_initial = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'
            conditions, current_derived = normal(initial, case, index, args.front)
            case_specs.append('dec $scfr_case' + str(index) + '() : bool\ndef $scfr_case' + str(index) + '() = true\n' + ''.join('  -- if ' + line + '\n' for line in conditions + current_derived))
            reached += conditions
            derived += current_derived
            paths += [source, Path(row['stdout']), Path(row['stderr'])]
    finally:
        try:
            if frontend:
                frontend.close()
        finally:
            if adapter:
                adapter.close()
    fixture = out / 'state.watsup'
    fixture.write_text(prefix(cases[0]) + '\n' + '\n'.join(case_specs) + '\ndec $main() : bool\ndef $main() = true\n  -- if $scfr_case0()\n')
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
    report = dict(revision=revision, inputs=before, input_count=len(before), inputs_stable=stable, head_stable=head_stable, module_count=len(modules), mode='fixture-SL/cache=false/det=true', front=args.front, selection=[row['id'] for row in cases[:1]], conditions=len(reached) + len(derived), reached_conditions=len(reached), derived_conditions=len(derived), source_agreements=0, process=process, passed=passed)
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('cv-string-callable-producer-reference-review', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
